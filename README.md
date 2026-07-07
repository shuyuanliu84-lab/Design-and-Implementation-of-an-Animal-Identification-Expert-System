# 动物识别专家系统

这是一个面向动物识别任务的规则驱动专家系统。项目使用 SQLite 存储规则库，使用 Python 实现正向推理、反向推理、Alpha 条件索引、轻量化 Beta 记忆、冲突检测和规则一致性验证。

本项目不是机器学习分类模型，不训练参数，因此没有训练集。规则库是系统知识来源，测试集和 UCI Zoo 数据仅用于验证推理效果、性能、鲁棒性和可复现性。

## 目录结构

```text
.
├── main.py                         # Tkinter GUI 主程序
├── large_expert_system.db           # SQLite 规则数据库
├── export_rules.py                  # 导出公开规则库
├── generate_test_cases.py           # 生成自建测试集与 UCI Zoo 转换样本
├── run_experiments.py               # 一键运行实验
├── modules/                         # 核心模块
├── rules/                           # 公开规则库 JSON/CSV 与统计
├── data/                            # 自建测试集、UCI Zoo 数据与映射
├── results/                         # 实验结果
├── README_EXPERIMENTS.md            # 实验复现说明
└── 项目总览与数据说明.md             # 项目与数据说明
```

## 规则库

规则库文件位于：

- `large_expert_system.db`: SQLite 原始规则库；
- `rules/rules.json`: JSON 格式公开规则库；
- `rules/rules.csv`: CSV 格式公开规则库；
- `rules/rule_stats.json`: 规则统计信息。

当前规则库包含 5121 条规则。每条规则包含：

- `id`: 规则编号；
- `conditions`: 前置条件集合；
- `conclusion`: 推理结论；
- `priority`: 冲突解决优先级；
- `category`: 规则类别。

可使用以下命令重新导出规则库：

```bash
python3 export_rules.py
```

## 数据集与测试集

项目包含三类数据：

- 自建规则库：系统推理的知识来源；
- 自建测试集：固定随机种子生成的 550 组测试样本；
- UCI Zoo 外部验证集：101 组公开动物数据转换后的验证样本。

自建测试集位于：

- `data/generated_test_cases.json`
- `data/generated_test_cases.csv`

UCI Zoo 相关文件位于：

- `data/uci_zoo.csv`
- `data/uci_zoo_mapping.json`
- `data/uci_zoo_cases.json`

重新生成测试数据：

```bash
python3 generate_test_cases.py
```

## 运行实验

运行完整实验：

```bash
python3 export_rules.py
python3 generate_test_cases.py
python3 run_experiments.py
```

主要结果会输出到 `results/`：

- `performance_summary.csv`: 性能测试；
- `accuracy_details.csv`: 自建测试集准确率明细；
- `uci_zoo_validation.csv`: UCI Zoo 外部验证结果；
- `ablation_summary.csv`: 索引消融实验；
- `beta_ablation_summary.csv`: Beta 记忆机制消融实验；
- `robustness_summary.csv`: 鲁棒性测试；
- `conflict_report.csv`: 离线冲突检测；
- `runtime_conflict_log.csv`: 运行时冲突日志；
- `rule_consistency_report.json`: 规则一致性与健康度报告；
- `experiment_overview.json`: 总体实验摘要。

## 启动 GUI

```bash
python3 main.py
```

## 环境要求

- Python 3.11 或更高版本；
- SQLite；
- Tkinter。

本项目核心脚本仅使用 Python 标准库，无需安装额外 Python 包。

## 复现说明

为保证结果可复现，测试集生成脚本使用固定随机种子。若需要核对规则库是否与公开文件一致，可先运行 `export_rules.py`，再比较 `rules/rules.json` 的规则数量与 `large_expert_system.db` 中的规则数量。

## License

本项目使用 MIT License 开源。详见 `LICENSE`。
