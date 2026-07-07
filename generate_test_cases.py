#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""生成自建测试集和UCI Zoo外部验证集。"""

import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Any

from modules.knowledge_base import KnowledgeBase


DATA_DIR = Path("data")
RANDOM_SEED = 20260706
DB_PATH = "large_expert_system.db"

UCI_ZOO_COLUMNS = [
    "animal_name", "hair", "feathers", "eggs", "milk", "airborne", "aquatic",
    "predator", "toothed", "backbone", "breathes", "venomous", "fins", "legs",
    "tail", "domestic", "catsize", "type",
]

# UCI Zoo official data mirrored locally for reproducible offline experiments.
UCI_ZOO_DATA = """aardvark,1,0,0,1,0,0,1,1,1,1,0,0,4,0,0,1,1
antelope,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,1
bass,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,4
bear,1,0,0,1,0,0,1,1,1,1,0,0,4,0,0,1,1
boar,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
buffalo,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,1
calf,1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,1
carp,0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,4
catfish,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,4
cavy,1,0,0,1,0,0,0,1,1,1,0,0,4,0,1,0,1
cheetah,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
chicken,0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,2
chub,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,4
clam,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,7
crab,0,0,1,0,0,1,1,0,0,0,0,0,4,0,0,0,7
crayfish,0,0,1,0,0,1,1,0,0,0,0,0,6,0,0,0,7
crow,0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,2
deer,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,1
dogfish,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,4
dolphin,0,0,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1
dove,0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,2
duck,0,1,1,0,1,1,0,0,1,1,0,0,2,1,0,0,2
elephant,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,1
flamingo,0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,1,2
flea,0,0,1,0,0,0,0,0,0,1,0,0,6,0,0,0,6
frog,0,0,1,0,0,1,1,1,1,1,0,0,4,0,0,0,5
frog,0,0,1,0,0,1,1,1,1,1,1,0,4,0,0,0,5
fruitbat,1,0,0,1,1,0,0,1,1,1,0,0,2,1,0,0,1
giraffe,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,1
girl,1,0,0,1,0,0,1,1,1,1,0,0,2,0,1,1,1
gnat,0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0,6
goat,1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,1
gorilla,1,0,0,1,0,0,0,1,1,1,0,0,2,0,0,1,1
gull,0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,0,2
haddock,0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,4
hamster,1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,0,1
hare,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,0,1
hawk,0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,2
herring,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,4
honeybee,1,0,1,0,1,0,0,0,0,1,1,0,6,0,1,0,6
housefly,1,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0,6
kiwi,0,1,1,0,0,0,1,0,1,1,0,0,2,1,0,0,2
ladybird,0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0,6
lark,0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,2
leopard,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
lion,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
lobster,0,0,1,0,0,1,1,0,0,0,0,0,6,0,0,0,7
lynx,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
mink,1,0,0,1,0,1,1,1,1,1,0,0,4,1,0,1,1
mole,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,1
mongoose,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
moth,1,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0,6
newt,0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,0,5
octopus,0,0,1,0,0,1,1,0,0,0,0,0,8,0,0,1,7
opossum,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,1
oryx,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,1
ostrich,0,1,1,0,0,0,0,0,1,1,0,0,2,1,0,1,2
parakeet,0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,2
penguin,0,1,1,0,0,1,1,0,1,1,0,0,2,1,0,1,2
pheasant,0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,2
pike,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,4
piranha,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,4
pitviper,0,0,1,0,0,0,1,1,1,1,1,0,0,1,0,0,3
platypus,1,0,1,1,0,1,1,0,1,1,0,0,4,1,0,1,1
polecat,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
pony,1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,1
porpoise,0,0,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1
puma,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
pussycat,1,0,0,1,0,0,1,1,1,1,0,0,4,1,1,1,1
raccoon,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
reindeer,1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,1
rhea,0,1,1,0,0,0,1,0,1,1,0,0,2,1,0,1,2
scorpion,0,0,0,0,0,0,1,0,0,1,1,0,8,1,0,0,7
seahorse,0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,4
seal,1,0,0,1,0,1,1,1,1,1,0,1,0,0,0,1,1
sealion,1,0,0,1,0,1,1,1,1,1,0,1,2,1,0,1,1
seasnake,0,0,0,0,0,1,1,1,1,0,1,0,0,1,0,0,3
seawasp,0,0,1,0,0,1,1,0,0,0,1,0,0,0,0,0,7
skimmer,0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,0,2
skua,0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,0,2
slowworm,0,0,1,0,0,0,1,1,1,1,0,0,0,1,0,0,3
slug,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,7
sole,0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,4
sparrow,0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,2
squirrel,1,0,0,1,0,0,0,1,1,1,0,0,2,1,0,0,1
starfish,0,0,1,0,0,1,1,0,0,0,0,0,5,0,0,0,7
stingray,0,0,1,0,0,1,1,1,1,0,1,1,0,1,0,1,4
swan,0,1,1,0,1,1,0,0,1,1,0,0,2,1,0,1,2
termite,0,0,1,0,0,0,0,0,0,1,0,0,6,0,0,0,6
toad,0,0,1,0,0,1,0,1,1,1,0,0,4,0,0,0,5
tortoise,0,0,1,0,0,0,0,0,1,1,0,0,4,1,0,1,3
tuatara,0,0,1,0,0,0,1,1,1,1,0,0,4,1,0,0,3
tuna,0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,4
vampire,1,0,0,1,1,0,0,1,1,1,0,0,2,1,0,0,1
vole,1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,0,1
vulture,0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,1,2
wallaby,1,0,0,1,0,0,0,1,1,1,0,0,2,1,0,1,1
wasp,1,0,1,0,1,0,0,0,0,1,1,0,6,0,0,0,6
wolf,1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,1
worm,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,7
wren,0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,2"""

UCI_MAPPING = {
    "hair": "有毛发",
    "feathers": "有羽毛",
    "eggs": "会下蛋",
    "milk": "有奶",
    "airborne": "会飞",
    "aquatic": "生活在水中",
    "predator": "吃肉",
    "toothed": "有牙齿",
    "backbone": "有脊椎",
    "breathes": "呼吸空气",
    "venomous": "有毒",
    "fins": "有鳍",
    "tail": "有尾巴",
    "domestic": "家养",
    "catsize": "猫大小",
}

UCI_TYPE_LABELS = {
    "1": "哺乳动物",
    "2": "鸟类",
    "3": "爬行动物",
    "4": "鱼类",
    "5": "两栖动物",
    "6": "昆虫",
    "7": "无脊椎动物",
}


def facts_for_rule(rule: Dict[str, Any]) -> Dict[str, bool]:
    return dict(rule["conditions"])


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_generated_cases(total: int = 550) -> List[Dict[str, Any]]:
    random.seed(RANDOM_SEED)
    kb = KnowledgeBase(DB_PATH)
    rules = [rule for rule in kb.get_all_rules() if rule["conditions"]]
    rules.sort(key=lambda rule: (rule["category"] == "general", rule["id"]))

    complete_rules = [rule for rule in rules if rule["category"] != "general"]
    generated_rules = [rule for rule in rules if rule["category"] == "general"]
    condition_pool = sorted({cond for rule in rules for cond in rule["conditions"]})
    category_conclusions = {"哺乳动物", "鸟类", "鱼类", "爬行动物", "昆虫", "两栖动物", "食肉动物", "有蹄类动物"}
    cases = []

    def add_case(case_type: str, rule: Dict[str, Any], input_facts: Dict[str, bool], difficulty: str) -> None:
        expected = [rule["conclusion"]]
        for fact in input_facts:
            if fact in category_conclusions and fact not in expected:
                expected.insert(0, fact)
        cases.append({
            "case_id": f"{case_type}_{len(cases) + 1:04d}",
            "case_type": case_type,
            "difficulty": difficulty,
            "source_rule_id": rule["id"],
            "input_facts": input_facts,
            "expected_conclusions": expected,
        })

    for rule in (complete_rules * 3)[:200]:
        add_case("complete", rule, facts_for_rule(rule), "medium")

    for rule in (complete_rules * 3)[:100]:
        facts = facts_for_rule(rule)
        if len(facts) > 1:
            facts.pop(random.choice(list(facts.keys())))
        add_case("missing", rule, facts, "hard")

    for rule in (complete_rules * 3)[:100]:
        facts = facts_for_rule(rule)
        facts[random.choice(["有毛发", "有羽毛", "有鳃", "有鳞片", "有六条腿"])] = True
        add_case("conflict", rule, facts, "hard")

    for rule in (complete_rules * 3)[:100]:
        facts = facts_for_rule(rule)
        for noise in random.sample(condition_pool, 2):
            facts.setdefault(noise, True)
        add_case("noise", rule, facts, "medium")

    for rule in generated_rules[: max(50, total - len(cases))]:
        add_case("boundary", rule, facts_for_rule(rule), "easy")

    return cases[:total]


def write_generated_cases(cases: List[Dict[str, Any]]) -> None:
    write_json(DATA_DIR / "generated_test_cases.json", cases)
    with (DATA_DIR / "generated_test_cases.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["case_id", "case_type", "difficulty", "source_rule_id", "input_facts", "expected_conclusions"],
        )
        writer.writeheader()
        for case in cases:
            writer.writerow({
                **case,
                "input_facts": json.dumps(case["input_facts"], ensure_ascii=False, sort_keys=True),
                "expected_conclusions": json.dumps(case["expected_conclusions"], ensure_ascii=False),
            })


def write_uci_zoo() -> List[Dict[str, Any]]:
    rows = []
    for raw_line in UCI_ZOO_DATA.strip().splitlines():
        values = raw_line.split(",")
        row = dict(zip(UCI_ZOO_COLUMNS, values))
        rows.append(row)

    with (DATA_DIR / "uci_zoo.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=UCI_ZOO_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    write_json(DATA_DIR / "uci_zoo_mapping.json", {
        "feature_mapping": UCI_MAPPING,
        "type_labels": UCI_TYPE_LABELS,
        "usage": "外部大类验证，不替代自建规则库",
    })

    converted = []
    for index, row in enumerate(rows, 1):
        facts = {}
        for english, chinese in UCI_MAPPING.items():
            if row[english] == "1":
                facts[chinese] = True
        legs = int(row["legs"])
        if legs == 0:
            facts["无四肢"] = True
        elif legs == 2:
            facts["两条腿"] = True
        elif legs == 4:
            facts["四条腿"] = True
        elif legs == 6:
            facts["有六条腿"] = True
        elif legs == 8:
            facts["八条腿"] = True
        converted.append({
            "case_id": f"uci_zoo_{index:03d}",
            "animal_name": row["animal_name"],
            "input_facts": facts,
            "expected_conclusions": [UCI_TYPE_LABELS[row["type"]]],
            "uci_type": row["type"],
        })
    write_json(DATA_DIR / "uci_zoo_cases.json", converted)
    return converted


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    cases = build_generated_cases()
    write_generated_cases(cases)
    uci_cases = write_uci_zoo()
    summary = {
        "random_seed": RANDOM_SEED,
        "generated_case_count": len(cases),
        "generated_case_type_counts": {
            case_type: sum(1 for case in cases if case["case_type"] == case_type)
            for case_type in sorted({case["case_type"] for case in cases})
        },
        "uci_zoo_case_count": len(uci_cases),
    }
    write_json(DATA_DIR / "dataset_summary.json", summary)
    print(f"自建测试集: {len(cases)} 组")
    print(f"UCI Zoo验证集: {len(uci_cases)} 组")
    print(f"输出目录: {DATA_DIR}")


if __name__ == "__main__":
    main()
