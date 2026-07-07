# 动物识别专家系统实验复现说明

## 数据角色

- `large_expert_system.db`: 当前自建规则库，共 5121 条规则。
- `rules/rules.json` 和 `rules/rules.csv`: 从 SQLite 导出的公开规则库。
- `data/generated_test_cases.*`: 固定随机种子生成的 500+ 自建测试样本。
- `data/uci_zoo.csv`: UCI Zoo 原始表格副本，101 个动物样本。
- `data/uci_zoo_cases.json`: 将 UCI Zoo 特征映射为本系统中文事实后的外部验证集。

## 运行顺序

```bash
python3 export_rules.py
python3 generate_test_cases.py
python3 run_experiments.py
```

## 主要输出

- `results/performance_summary.csv`: 100 组性能测试，包含无索引和 Alpha 索引耗时。
- `results/accuracy_details.csv`: 自建测试集逐样本准确性结果。
- `results/uci_zoo_validation.csv`: UCI Zoo 外部验证结果。
- `results/ablation_summary.csv`: 无索引、Alpha 索引、SQLite 条件索引、完整优化对比。
- `results/robustness_summary.csv`: 完整、缺失、矛盾、噪声、边界样本鲁棒性统计。
- `results/experiment_overview.json`: 论文可引用的总体统计。
- `results/beta_ablation_summary.csv`: Alpha-only 与 Alpha+Beta 记忆机制对比。
- `results/conflict_report.csv`: 离线规则冲突检测报告。
- `results/runtime_conflict_log.csv`: 运行时互斥类别冲突日志。
- `results/rule_consistency_report.json`: 规则一致性、冗余、循环依赖和健康度报告。

## 技术实现补充

- Beta 记忆机制用于记录规则的已满足/未满足条件，减少重复条件检查。当前实验显示其降低了条件检查次数，但 Python 缓存维护存在额外开销，论文中应如实描述速度/内存权衡。
- 冲突解决默认使用优先级最高者胜；若互斥类别结论优先级相同，则保留多个结论并标记为 `manual_review_required`。
- 规则一致性验证把规则库视为条件到结论的有向图，报告离线冲突、冗余规则、循环依赖和健康度分数。
