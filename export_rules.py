#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""导出公开规则库和规则统计。"""

import csv
import json
from pathlib import Path

from modules.knowledge_base import KnowledgeBase


DB_PATH = "large_expert_system.db"
RULES_DIR = Path("rules")


def main() -> None:
    RULES_DIR.mkdir(exist_ok=True)

    kb = KnowledgeBase(DB_PATH)
    rules = sorted(kb.get_all_rules(), key=lambda rule: rule["id"])

    json_path = RULES_DIR / "rules.json"
    csv_path = RULES_DIR / "rules.csv"
    stats_path = RULES_DIR / "rule_stats.json"

    json_path.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "conditions", "conclusion", "priority", "category"])
        writer.writeheader()
        for rule in rules:
            writer.writerow({
                "id": rule["id"],
                "conditions": json.dumps(rule["conditions"], ensure_ascii=False, sort_keys=True),
                "conclusion": rule["conclusion"],
                "priority": rule["priority"],
                "category": rule["category"],
            })

    category_counts = {}
    condition_keys = set()
    condition_records = 0
    for rule in rules:
        category_counts[rule["category"]] = category_counts.get(rule["category"], 0) + 1
        condition_keys.update(rule["conditions"].keys())
        condition_records += len(rule["conditions"])

    stats = {
        "rule_count": len(rules),
        "category_counts": dict(sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))),
        "distinct_condition_count": len(condition_keys),
        "condition_record_count": condition_records,
        "public_files": [str(json_path), str(csv_path)],
    }
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"导出完成: {len(rules)} 条规则")
    print(f"- {json_path}")
    print(f"- {csv_path}")
    print(f"- {stats_path}")


if __name__ == "__main__":
    main()
