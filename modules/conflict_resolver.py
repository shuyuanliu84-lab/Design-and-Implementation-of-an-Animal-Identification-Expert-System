from typing import Any, Dict, List


MUTUALLY_EXCLUSIVE_CATEGORIES = {"哺乳动物", "鸟类", "鱼类", "爬行动物", "昆虫", "两栖动物"}


class ConflictResolver:
    """Detect and resolve mutually exclusive category conclusions."""

    def __init__(self, mutually_exclusive_categories=None):
        self.mutually_exclusive_categories = set(mutually_exclusive_categories or MUTUALLY_EXCLUSIVE_CATEGORIES)

    def detect_runtime_conflict(self, fired_rules: List[Dict[str, Any]], input_facts: Dict[str, bool]) -> Dict[str, Any]:
        category_rules = [
            rule for rule in fired_rules
            if rule["conclusion"] in self.mutually_exclusive_categories
        ]
        conclusions = sorted({rule["conclusion"] for rule in category_rules})
        if len(conclusions) <= 1:
            return {}

        max_priority = max(rule.get("priority", 1) for rule in category_rules)
        winners = [rule for rule in category_rules if rule.get("priority", 1) == max_priority]
        winning_conclusions = sorted({rule["conclusion"] for rule in winners})
        resolution = "priority_winner" if len(winning_conclusions) == 1 else "manual_review_required"

        return {
            "input_facts": dict(input_facts),
            "conflict_conclusions": conclusions,
            "triggered_rule_ids": [rule["id"] for rule in category_rules],
            "triggered_priorities": {str(rule["id"]): rule.get("priority", 1) for rule in category_rules},
            "selected_conclusions": winning_conclusions,
            "resolution": resolution,
        }

    def should_keep_conclusion(self, conclusion: str, conflict: Dict[str, Any]) -> bool:
        if not conflict or conclusion not in self.mutually_exclusive_categories:
            return True
        if conflict["resolution"] == "priority_winner":
            return conclusion in set(conflict["selected_conclusions"])
        return True
