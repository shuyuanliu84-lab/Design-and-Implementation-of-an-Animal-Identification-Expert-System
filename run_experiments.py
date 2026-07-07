#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""统一运行性能、准确率、消融和鲁棒性实验。"""

import csv
import json
import math
import sqlite3
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from modules.knowledge_base import KnowledgeBase
from modules.conflict_resolver import ConflictResolver
from modules.rule_validator import RuleValidator


DB_PATH = "large_expert_system.db"
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
CASE_PATH = DATA_DIR / "generated_test_cases.json"
UCI_CASE_PATH = DATA_DIR / "uci_zoo_cases.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summary_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "std": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
        }
    mean = statistics.mean(values)
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    margin = 1.96 * std / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return {
        "count": len(values),
        "mean": mean,
        "std": std,
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "ci95_low": mean - margin,
        "ci95_high": mean + margin,
    }


class SilentInferenceRunner:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.rules = kb.get_all_rules()
        self.rule_map = {rule["id"]: rule for rule in self.rules}
        self.alpha_memory = self._build_alpha_index()
        self.conflict_resolver = ConflictResolver()

    def _build_alpha_index(self) -> Dict[str, set]:
        alpha = {}
        for rule in self.rules:
            for condition in rule["conditions"]:
                alpha.setdefault(condition, set()).add(rule["id"])
        return alpha

    def _candidate_rules(self, facts: Dict[str, bool], use_alpha_index: bool) -> List[Dict[str, Any]]:
        if not use_alpha_index:
            return self.rules
        candidate_ids = set()
        for fact in facts:
            candidate_ids.update(self.alpha_memory.get(fact, set()))
        if not candidate_ids:
            return self.rules
        rules = [self.rule_map[rule_id] for rule_id in candidate_ids if rule_id in self.rule_map]
        rules.sort(key=lambda rule: (-rule["priority"], rule["id"]))
        return rules

    @staticmethod
    def _satisfied(rule: Dict[str, Any], facts: Dict[str, bool]) -> bool:
        return all(facts.get(key) == value for key, value in rule["conditions"].items())

    @staticmethod
    def _check_rule_conditions(rule: Dict[str, Any], facts: Dict[str, bool], beta_memory: Dict[int, Dict[str, Any]] = None) -> Tuple[bool, int]:
        if beta_memory is None:
            checks = 0
            for key, value in rule["conditions"].items():
                checks += 1
                if facts.get(key) != value:
                    return False, checks
            return True, checks

        rule_id = rule["id"]
        cache = beta_memory.get(rule_id, {
            "matched": set(),
            "unmatched": set(rule["conditions"].keys()),
            "fact_snapshot": {},
        })
        matched = set(cache["matched"])
        unmatched = set(cache["unmatched"])
        snapshot = dict(cache.get("fact_snapshot", {}))
        checks = 0

        for key, value in rule["conditions"].items():
            current_value = facts.get(key)
            if snapshot.get(key) == current_value and key in matched.union(unmatched):
                continue
            checks += 1
            snapshot[key] = current_value
            if current_value == value:
                matched.add(key)
                unmatched.discard(key)
            else:
                matched.discard(key)
                unmatched.add(key)

        beta_memory[rule_id] = {
            "matched": matched,
            "unmatched": unmatched,
            "fact_snapshot": snapshot,
            "progress": len(matched) / len(rule["conditions"]) if rule["conditions"] else 1.0,
        }
        return len(unmatched) == 0, checks

    def infer(
        self,
        initial_facts: Dict[str, bool],
        use_alpha_index: bool = True,
        use_beta_memory: bool = False,
        max_cycles: int = 10,
    ) -> Dict[str, Any]:
        facts = dict(initial_facts)
        inferred = []
        checked_rules = 0
        condition_checks = 0
        candidate_counts = []
        beta_memory = {} if use_beta_memory else None
        fired_rules = []
        start = time.perf_counter()

        for cycle in range(1, max_cycles + 1):
            changed = False
            candidates = self._candidate_rules(facts, use_alpha_index)
            candidate_counts.append(len(candidates))
            for rule in candidates:
                checked_rules += 1
                conclusion = rule["conclusion"]
                if facts.get(conclusion) is True:
                    continue
                satisfied, checks = self._check_rule_conditions(rule, facts, beta_memory)
                condition_checks += checks
                if satisfied:
                    facts[conclusion] = True
                    inferred.append(conclusion)
                    fired_rules.append(rule)
                    changed = True
            if not changed:
                break

        elapsed = time.perf_counter() - start
        conflict = self.conflict_resolver.detect_runtime_conflict(fired_rules, initial_facts)
        if conflict and conflict["resolution"] == "priority_winner":
            selected = set(conflict["selected_conclusions"])
            for conclusion in conflict["conflict_conclusions"]:
                if conclusion not in selected:
                    facts.pop(conclusion, None)
                    if conclusion in inferred:
                        inferred.remove(conclusion)
        return {
            "elapsed_seconds": elapsed,
            "inferred": inferred,
            "all_true_facts": [fact for fact, value in facts.items() if value],
            "checked_rules": checked_rules,
            "condition_checks": condition_checks,
            "cycles": len(candidate_counts),
            "avg_candidate_rules": statistics.mean(candidate_counts) if candidate_counts else 0,
            "beta_memory_entries": len(beta_memory) if beta_memory is not None else 0,
            "runtime_conflict": conflict,
        }


def classify_case(result: Dict[str, Any], expected: List[str]) -> Tuple[bool, str]:
    true_facts = set(result["all_true_facts"])
    expected_set = set(expected)
    if expected_set.issubset(true_facts):
        return True, "exact_or_contains_expected"
    if true_facts.intersection(expected_set):
        return True, "partial_expected"
    if result["inferred"]:
        return False, "wrong_conclusion"
    return False, "no_conclusion"


def run_accuracy(cases: List[Dict[str, Any]], runner: SilentInferenceRunner) -> List[Dict[str, Any]]:
    rows = []
    for case in cases:
        result = runner.infer(case["input_facts"], use_alpha_index=True)
        ok, error_type = classify_case(result, case["expected_conclusions"])
        rows.append({
            "case_id": case["case_id"],
            "case_type": case.get("case_type", "uci_zoo"),
            "expected": json.dumps(case["expected_conclusions"], ensure_ascii=False),
            "inferred": json.dumps(result["inferred"], ensure_ascii=False),
            "correct": int(ok),
            "error_type": error_type,
            "elapsed_ms": result["elapsed_seconds"] * 1000,
            "checked_rules": result["checked_rules"],
            "condition_checks": result["condition_checks"],
            "avg_candidate_rules": result["avg_candidate_rules"],
        })
    return rows


def aggregate_accuracy(rows: List[Dict[str, Any]], group_field: str) -> List[Dict[str, Any]]:
    groups = sorted({row[group_field] for row in rows})
    summary = []
    for group in groups:
        group_rows = [row for row in rows if row[group_field] == group]
        correct = sum(int(row["correct"]) for row in group_rows)
        summary.append({
            group_field: group,
            "case_count": len(group_rows),
            "correct_count": correct,
            "accuracy": correct / len(group_rows) if group_rows else 0,
            "mean_elapsed_ms": summary_stats([float(row["elapsed_ms"]) for row in group_rows])["mean"],
            "mean_candidate_rules": summary_stats([float(row["avg_candidate_rules"]) for row in group_rows])["mean"],
        })
    return summary


def run_performance(cases: List[Dict[str, Any]], runner: SilentInferenceRunner) -> List[Dict[str, Any]]:
    rows = []
    for case in cases[:100]:
        alpha_result = runner.infer(case["input_facts"], use_alpha_index=True)
        baseline_result = runner.infer(case["input_facts"], use_alpha_index=False)
        rows.append({
            "case_id": case["case_id"],
            "case_type": case["case_type"],
            "alpha_elapsed_ms": alpha_result["elapsed_seconds"] * 1000,
            "baseline_elapsed_ms": baseline_result["elapsed_seconds"] * 1000,
            "speedup": baseline_result["elapsed_seconds"] / alpha_result["elapsed_seconds"] if alpha_result["elapsed_seconds"] else 0,
            "alpha_candidate_rules": alpha_result["avg_candidate_rules"],
            "baseline_candidate_rules": baseline_result["avg_candidate_rules"],
            "filter_ratio": alpha_result["avg_candidate_rules"] / len(runner.rules) if runner.rules else 0,
        })
    return rows


def run_ablation(cases: List[Dict[str, Any]], runner: SilentInferenceRunner) -> List[Dict[str, Any]]:
    rows = []
    selected = cases[:100]
    modes = [
        ("baseline_no_index", False, False),
        ("alpha_index_only", True, False),
        ("full_optimized", True, True),
    ]
    for mode_name, use_alpha, use_beta in modes:
        elapsed = []
        candidates = []
        checked = []
        condition_checks = []
        for case in selected:
            result = runner.infer(case["input_facts"], use_alpha_index=use_alpha, use_beta_memory=use_beta)
            elapsed.append(result["elapsed_seconds"] * 1000)
            candidates.append(result["avg_candidate_rules"])
            checked.append(result["checked_rules"])
            condition_checks.append(result["condition_checks"])
        stats = summary_stats(elapsed)
        rows.append({
            "mode": mode_name,
            "case_count": len(selected),
            "mean_elapsed_ms": stats["mean"],
            "std_elapsed_ms": stats["std"],
            "median_elapsed_ms": stats["median"],
            "ci95_low_ms": stats["ci95_low"],
            "ci95_high_ms": stats["ci95_high"],
            "mean_candidate_rules": statistics.mean(candidates),
            "mean_checked_rules": statistics.mean(checked),
            "mean_condition_checks": statistics.mean(condition_checks),
            "speedup_vs_no_index": "",
        })

    sqlite_rows = sqlite_index_probe()
    rows.append(sqlite_rows)
    return rows


def sqlite_index_probe(iterations: int = 200) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT condition_key FROM rule_conditions GROUP BY condition_key ORDER BY COUNT(*) ASC LIMIT 100")
    conditions = [row[0] for row in cursor.fetchall()]

    cursor.execute("DROP INDEX IF EXISTS idx_conditions_key")
    conn.commit()
    start = time.perf_counter()
    for _ in range(iterations):
        for condition in conditions:
            cursor.execute("SELECT rule_id FROM rule_conditions WHERE condition_key = ?", (condition,))
            cursor.fetchall()
    no_index = (time.perf_counter() - start) / (iterations * len(conditions))

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conditions_key ON rule_conditions(condition_key)")
    conn.commit()
    start = time.perf_counter()
    for _ in range(iterations):
        for condition in conditions:
            cursor.execute("SELECT rule_id FROM rule_conditions WHERE condition_key = ?", (condition,))
            cursor.fetchall()
    with_index = (time.perf_counter() - start) / (iterations * len(conditions))
    conn.close()

    return {
        "mode": "sqlite_condition_index",
        "case_count": len(conditions),
        "mean_elapsed_ms": with_index * 1000,
        "std_elapsed_ms": 0,
        "median_elapsed_ms": with_index * 1000,
        "ci95_low_ms": with_index * 1000,
        "ci95_high_ms": with_index * 1000,
        "mean_candidate_rules": 0,
        "mean_checked_rules": 0,
        "mean_condition_checks": 0,
        "speedup_vs_no_index": no_index / with_index if with_index else 0,
    }


def run_beta_ablation(cases: List[Dict[str, Any]], runner: SilentInferenceRunner) -> List[Dict[str, Any]]:
    selected = cases[:100]
    rows = []
    results_by_mode = {}
    for mode_name, use_beta in [("alpha_only", False), ("alpha_beta", True)]:
        elapsed = []
        condition_checks = []
        checked_rules = []
        beta_entries = []
        for case in selected:
            result = runner.infer(case["input_facts"], use_alpha_index=True, use_beta_memory=use_beta)
            elapsed.append(result["elapsed_seconds"] * 1000)
            condition_checks.append(result["condition_checks"])
            checked_rules.append(result["checked_rules"])
            beta_entries.append(result["beta_memory_entries"])
        stats = summary_stats(elapsed)
        results_by_mode[mode_name] = {
            "elapsed": elapsed,
            "condition_checks": condition_checks,
        }
        rows.append({
            "mode": mode_name,
            "case_count": len(selected),
            "mean_elapsed_ms": stats["mean"],
            "std_elapsed_ms": stats["std"],
            "median_elapsed_ms": stats["median"],
            "ci95_low_ms": stats["ci95_low"],
            "ci95_high_ms": stats["ci95_high"],
            "mean_checked_rules": statistics.mean(checked_rules),
            "mean_condition_checks": statistics.mean(condition_checks),
            "mean_beta_memory_entries": statistics.mean(beta_entries),
            "speedup_vs_alpha_only": "",
            "condition_check_reduction": "",
        })

    alpha_mean = statistics.mean(results_by_mode["alpha_only"]["elapsed"])
    beta_mean = statistics.mean(results_by_mode["alpha_beta"]["elapsed"])
    alpha_checks = statistics.mean(results_by_mode["alpha_only"]["condition_checks"])
    beta_checks = statistics.mean(results_by_mode["alpha_beta"]["condition_checks"])
    for row in rows:
        if row["mode"] == "alpha_beta":
            row["speedup_vs_alpha_only"] = alpha_mean / beta_mean if beta_mean else 0
            row["condition_check_reduction"] = 1 - beta_checks / alpha_checks if alpha_checks else 0
    return rows


def run_runtime_conflict_log(cases: List[Dict[str, Any]], runner: SilentInferenceRunner) -> List[Dict[str, Any]]:
    rows = []
    for case in cases:
        result = runner.infer(case["input_facts"], use_alpha_index=True, use_beta_memory=True)
        conflict = result.get("runtime_conflict") or {}
        if not conflict:
            continue
        rows.append({
            "case_id": case["case_id"],
            "case_type": case.get("case_type", ""),
            "input_facts": json.dumps(conflict["input_facts"], ensure_ascii=False, sort_keys=True),
            "conflict_conclusions": json.dumps(conflict["conflict_conclusions"], ensure_ascii=False),
            "triggered_rule_ids": json.dumps(conflict["triggered_rule_ids"], ensure_ascii=False),
            "triggered_priorities": json.dumps(conflict["triggered_priorities"], ensure_ascii=False, sort_keys=True),
            "selected_conclusions": json.dumps(conflict["selected_conclusions"], ensure_ascii=False),
            "resolution": conflict["resolution"],
        })
    return rows


def rule_conflict_rows(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for item in report["sample_conflicts"]:
        rows.append({
            "condition_signature": json.dumps(item["condition_signature"], ensure_ascii=False, sort_keys=True),
            "rule_ids": json.dumps(item["rule_ids"], ensure_ascii=False),
            "conclusions": json.dumps(item["conclusions"], ensure_ascii=False),
            "priorities": json.dumps(item["priorities"], ensure_ascii=False, sort_keys=True),
        })
    if not rows:
        rows.append({
            "condition_signature": "",
            "rule_ids": "[]",
            "conclusions": "[]",
            "priorities": "{}",
        })
    return rows


def run_robustness(cases: List[Dict[str, Any]], runner: SilentInferenceRunner) -> List[Dict[str, Any]]:
    robust_rows = run_accuracy(cases, runner)
    return aggregate_accuracy(robust_rows, "case_type")


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    if not CASE_PATH.exists() or not UCI_CASE_PATH.exists():
        raise SystemExit("请先运行 python3 generate_test_cases.py")

    kb = KnowledgeBase(DB_PATH)
    runner = SilentInferenceRunner(kb)
    cases = load_json(CASE_PATH)
    uci_cases = load_json(UCI_CASE_PATH)

    performance_rows = run_performance(cases, runner)
    accuracy_rows = run_accuracy(cases, runner)
    uci_rows = run_accuracy(uci_cases, runner)
    ablation_rows = run_ablation(cases, runner)
    beta_ablation_rows = run_beta_ablation(cases, runner)
    robustness_rows = run_robustness(cases, runner)
    runtime_conflict_rows = run_runtime_conflict_log(cases, runner)
    validator = RuleValidator(kb.get_all_rules())
    consistency_report = validator.health_report()
    conflict_rows = rule_conflict_rows(consistency_report)

    write_csv(RESULTS_DIR / "performance_summary.csv", performance_rows, [
        "case_id", "case_type", "alpha_elapsed_ms", "baseline_elapsed_ms", "speedup",
        "alpha_candidate_rules", "baseline_candidate_rules", "filter_ratio",
    ])
    write_csv(RESULTS_DIR / "accuracy_details.csv", accuracy_rows, [
        "case_id", "case_type", "expected", "inferred", "correct", "error_type",
        "elapsed_ms", "checked_rules", "condition_checks", "avg_candidate_rules",
    ])
    write_csv(RESULTS_DIR / "uci_zoo_validation.csv", uci_rows, [
        "case_id", "case_type", "expected", "inferred", "correct", "error_type",
        "elapsed_ms", "checked_rules", "condition_checks", "avg_candidate_rules",
    ])
    write_csv(RESULTS_DIR / "ablation_summary.csv", ablation_rows, [
        "mode", "case_count", "mean_elapsed_ms", "std_elapsed_ms", "median_elapsed_ms",
        "ci95_low_ms", "ci95_high_ms", "mean_candidate_rules", "mean_checked_rules",
        "mean_condition_checks", "speedup_vs_no_index",
    ])
    write_csv(RESULTS_DIR / "beta_ablation_summary.csv", beta_ablation_rows, [
        "mode", "case_count", "mean_elapsed_ms", "std_elapsed_ms", "median_elapsed_ms",
        "ci95_low_ms", "ci95_high_ms", "mean_checked_rules", "mean_condition_checks",
        "mean_beta_memory_entries", "speedup_vs_alpha_only", "condition_check_reduction",
    ])
    write_csv(RESULTS_DIR / "robustness_summary.csv", robustness_rows, [
        "case_type", "case_count", "correct_count", "accuracy", "mean_elapsed_ms",
        "mean_candidate_rules",
    ])
    write_csv(RESULTS_DIR / "runtime_conflict_log.csv", runtime_conflict_rows, [
        "case_id", "case_type", "input_facts", "conflict_conclusions", "triggered_rule_ids",
        "triggered_priorities", "selected_conclusions", "resolution",
    ])
    write_csv(RESULTS_DIR / "conflict_report.csv", conflict_rows, [
        "condition_signature", "rule_ids", "conclusions", "priorities",
    ])
    write_json(RESULTS_DIR / "rule_consistency_report.json", consistency_report)

    perf_speedups = [float(row["speedup"]) for row in performance_rows]
    alpha_times = [float(row["alpha_elapsed_ms"]) for row in performance_rows]
    baseline_times = [float(row["baseline_elapsed_ms"]) for row in performance_rows]
    overview = {
        "rule_count": kb.get_rule_count(),
        "generated_case_count": len(cases),
        "performance_case_count": len(performance_rows),
        "uci_zoo_case_count": len(uci_cases),
        "generated_accuracy": sum(int(row["correct"]) for row in accuracy_rows) / len(accuracy_rows),
        "uci_zoo_accuracy": sum(int(row["correct"]) for row in uci_rows) / len(uci_rows),
        "alpha_elapsed_ms_stats": summary_stats(alpha_times),
        "baseline_elapsed_ms_stats": summary_stats(baseline_times),
        "speedup_stats": summary_stats(perf_speedups),
        "runtime_conflict_count": len(runtime_conflict_rows),
        "rule_health_score": consistency_report["health_score"],
        "offline_conflict_count": consistency_report["offline_conflict_count"],
        "cycle_count": consistency_report["cycle_count"],
        "weak_redundancy_count": consistency_report["weak_redundancy_count"],
    }
    write_json(RESULTS_DIR / "experiment_overview.json", overview)

    print("实验完成")
    print(f"- 自建测试集: {len(cases)} 组")
    print(f"- 性能测试: {len(performance_rows)} 组")
    print(f"- UCI Zoo验证: {len(uci_cases)} 组")
    print(f"- 结果目录: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
