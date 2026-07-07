# 公开规则库说明

本目录保存动物识别专家系统的公开规则库导出文件。

## 文件说明

- `rules.json`: JSON 格式规则库，适合程序读取；
- `rules.csv`: CSV 格式规则库，适合表格查看和论文附录引用；
- `rule_stats.json`: 规则数量、类别分布、条件数量等统计信息。

## 字段说明

| 字段 | 含义 |
| --- | --- |
| `id` | 规则编号 |
| `conditions` | 前置条件集合 |
| `conclusion` | 推理结论 |
| `priority` | 规则优先级，用于冲突解决 |
| `category` | 规则类别 |

## 重新导出

在项目根目录运行：

```bash
python3 export_rules.py
```

导出脚本会从 `large_expert_system.db` 读取规则，并覆盖生成本目录下的 JSON、CSV 和统计文件。
