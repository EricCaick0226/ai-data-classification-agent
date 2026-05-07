# Day 12 笔记：Confidence 与 Needs Review 判断信号

## 1. 今日目标

今天的目标是给数据分类分级结果增加更清楚的判断信号：

- `confidence`：系统对当前分类判断有多确定
- `needs_review`：这个字段是否建议人工复核

今天不改 Agent 架构，不接入 LLM API，不使用 LangChain / LangGraph，也不提前做复杂 Structured Output。

今天主要升级：

- `src/classifier.py`
- `src/report_generator.py`

最终重新生成：

- `reports/classification_report.md`

---

## 2. 为什么今天重要

真实的数据分类分级项目里，系统不能只输出“这个字段是什么类别”。

它还需要告诉使用者：

- 这个判断有多可靠？
- 哪些字段需要人工再看？
- 哪些字段虽然可以初步分类，但仍然存在不确定性？

例如：

| 字段名 | 判断 |
|---|---|
| password | 字段名非常明确，系统很确定，通常不需要人工复核 |
| email | 字段名比较明确，可以较稳定地判断为联系方式类 PII |
| user_location | 可以判断为位置类数据，但不知道是城市还是精确地址，所以需要人工复核 |
| notes | 自由文本字段，内容不可预测，必须人工复核 |

---

## 3. 核心概念

### 3.1 confidence 是什么？

`confidence` 表示系统对自己分类判断的确定程度。

例如：

```python
"confidence": 0.95