from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple


def canonical_conditions(conditions: Dict[str, Any]) -> Tuple[Tuple[str, str], ...]:
    return tuple(sorted((key, str(value)) for key, value in conditions.items()))


class RuleValidator:
    """Offline consistency checks for the rule base."""

    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = sorted(rules, key=lambda rule: rule["id"])
        self.rule_count = len(self.rules)

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        grouped = defaultdict(list)
        for rule in self.rules:
            grouped[canonical_conditions(rule["conditions"])].append(rule)

        conflicts = []
        for condition_key, group in grouped.items():
            conclusions = sorted({rule["conclusion"] for rule in group})
            if len(conclusions) <= 1:
                continue
            conflicts.append({
                "condition_signature": dict(condition_key),
                "rule_ids": [rule["id"] for rule in group],
                "conclusions": conclusions,
                "priorities": {str(rule["id"]): rule.get("priority", 1) for rule in group},
            })
        return conflicts

    def detect_redundant_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        exact_groups = defaultdict(list)
        by_conclusion = defaultdict(list)
        for rule in self.rules:
            exact_groups[(canonical_conditions(rule["conditions"]), rule["conclusion"])].append(rule)
            by_conclusion[rule["conclusion"]].append(rule)

        exact_duplicates = []
        for (_, conclusion), group in exact_groups.items():
            if len(group) > 1:
                exact_duplicates.append({
                    "type": "exact_duplicate",
                    "conclusion": conclusion,
                    "rule_ids": [rule["id"] for rule in group],
                })

        weak_redundancies = []
        for conclusion, group in by_conclusion.items():
            condition_sets = [(rule, set(rule["conditions"].items())) for rule in group]
            for i, (base_rule, base_conditions) in enumerate(condition_sets):
                for other_rule, other_conditions in condition_sets[i + 1:]:
                    if base_conditions < other_conditions:
                        weak_redundancies.append({
                            "type": "weak_redundancy",
                            "general_rule_id": base_rule["id"],
                            "specific_rule_id": other_rule["id"],
                            "conclusion": conclusion,
                        })
                    elif other_conditions < base_conditions:
                        weak_redundancies.append({
                            "type": "weak_redundancy",
                            "general_rule_id": other_rule["id"],
                            "specific_rule_id": base_rule["id"],
                            "conclusion": conclusion,
                        })

        return {
            "exact_duplicates": exact_duplicates,
            "weak_redundancies": weak_redundancies,
        }

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        graph = defaultdict(set)
        for rule in self.rules:
            conclusion = rule["conclusion"]
            for condition in rule["conditions"]:
                graph[condition].add(conclusion)
        return graph

    def detect_cycles(self, max_cycles: int = 200) -> List[List[str]]:
        graph = self.build_dependency_graph()
        cycles = []
        seen = set()

        def dfs(node: str, path: List[str], visiting: Set[str]) -> None:
            if len(cycles) >= max_cycles:
                return
            visiting.add(node)
            path.append(node)
            for next_node in graph.get(node, set()):
                if next_node in visiting:
                    index = path.index(next_node)
                    cycle = path[index:] + [next_node]
                    key = tuple(cycle)
                    if key not in seen:
                        seen.add(key)
                        cycles.append(cycle)
                elif next_node not in path:
                    dfs(next_node, path, visiting)
            path.pop()
            visiting.discard(node)

        for node in list(graph):
            dfs(node, [], set())
            if len(cycles) >= max_cycles:
                break
        return cycles

    def health_report(self) -> Dict[str, Any]:
        conflicts = self.detect_conflicts()
        redundancies = self.detect_redundant_rules()
        cycles = self.detect_cycles()
        exact_count = len(redundancies["exact_duplicates"])
        weak_count = len(redundancies["weak_redundancies"])
        conflict_count = len(conflicts)
        cycle_count = len(cycles)

        denominator = max(self.rule_count, 1)
        conflict_penalty = min(30.0, conflict_count / denominator * 100)
        redundancy_penalty = min(30.0, (exact_count + weak_count) / denominator * 100)
        cycle_penalty = min(40.0, cycle_count / denominator * 100)
        health_score = max(0.0, 100.0 - conflict_penalty - redundancy_penalty - cycle_penalty)

        return {
            "rule_count": self.rule_count,
            "offline_conflict_count": conflict_count,
            "exact_duplicate_count": exact_count,
            "weak_redundancy_count": weak_count,
            "cycle_count": cycle_count,
            "health_score": health_score,
            "penalties": {
                "conflict_penalty": conflict_penalty,
                "redundancy_penalty": redundancy_penalty,
                "cycle_penalty": cycle_penalty,
            },
            "sample_conflicts": conflicts[:100],
            "sample_exact_duplicates": redundancies["exact_duplicates"][:100],
            "sample_weak_redundancies": redundancies["weak_redundancies"][:100],
            "sample_cycles": cycles[:100],
        }
