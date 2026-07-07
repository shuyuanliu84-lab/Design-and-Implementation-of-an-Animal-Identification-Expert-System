# 数据与测试集说明

本项目不包含机器学习训练集。数据文件仅用于规则系统的测试、验证和复现。

## 自建测试集

- `generated_test_cases.json`
- `generated_test_cases.csv`

自建测试集由 `generate_test_cases.py` 使用固定随机种子生成，覆盖以下类型：

- 完整特征样本；
- 缺失特征样本；
- 矛盾特征样本；
- 噪声特征样本；
- 边界样本。

## UCI Zoo 外部验证集

- `uci_zoo.csv`: UCI Zoo 原始数据副本；
- `uci_zoo_mapping.json`: UCI 英文字段到系统中文事实的映射；
- `uci_zoo_cases.json`: 转换后的系统推理输入。

UCI Zoo 仅用于外部验证和可复现对照，不作为本项目规则库来源。

## 重新生成

在项目根目录运行：

```bash
python3 generate_test_cases.py
```
