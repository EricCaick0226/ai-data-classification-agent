# Day 5 笔记：Sample User Dataset

## 1. 今天目标

今天的目标是创建一个假的样例 CSV 文件：

`data/sample_users.csv`

这个文件后面会作为 AI Agent Demo 的测试输入，用来测试字段分析、数据分类分级、缺失值统计和报告生成。

今天不写 Agent、不写 Tool Calling、不写 CSV analyzer，也不安装 OpenAI 或 LangChain。

---

## 2. 为什么需要 sample_users.csv？

`sample_users.csv` 不是随便造数据。

它的作用是测试我们前几天写好的规则系统：

- `src/rules.py`
- `src/classifier.py`

后面的项目流程会是：

```text
data/sample_users.csv
        ↓
analyze_csv
        ↓
classify_column
        ↓
generate_report
        ↓
agent_demo.py