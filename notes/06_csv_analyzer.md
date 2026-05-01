# Day 6 笔记：CSV Analyzer 核心逻辑

## 1. 今天目标

今天完成 `src/csv_analyzer.py`。

核心函数是：

`analyze_csv(file_path)`

它负责读取 CSV 文件，并提取每一列的基础字段信息。

## 2. csv_analyzer.py 的职责

`csv_analyzer.py` 只负责看清楚 CSV 里有什么。

它不负责：

- 判断字段风险
- 判断字段分类
- 生成报告
- 调用 Agent
- 调用 LLM API

它负责：

- 读取 CSV
- 遍历每一列
- 提取字段名
- 提取数据类型
- 统计缺失值数量
- 提取少量非空样例值
- 返回字段信息 list

## 3. analyze_csv 的输出结构

`analyze_csv(file_path)` 返回一个 list。

list 里的每个元素是一个 dictionary，例如：

```python
{
    "field_name": "email",
    "data_type": "str",
    "missing_count": 0,
    "sample_values": ["alice.fake@example.com", "bob.fake@example.com", "carol.fake@example.com"]
}