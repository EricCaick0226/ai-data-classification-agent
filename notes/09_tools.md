# Day 9 笔记：Tool 包装层

## 1. 今天目标

今天的目标是创建：

`src/tools.py`

把前面已经写好的普通函数包装成未来 Agent / Executor 可以调用的 Tool。

今天不是写真正的 Agent，也不是写 LLM Tool Calling。

今天只是先完成工具包装层。

---

## 2. 为什么需要 tools.py？

之前的 `main.py` 已经可以直接调用：

- `analyze_csv(file_path)`
- `classify_column(column_info)`
- `generate_report(results)`

但是 `main.py` 更像是给人类开发者测试普通流程的入口。

它的作用是：

> 测试我们之前写的普通函数能不能连起来工作。

而 `tools.py` 的作用不一样。

`tools.py` 是未来给 Agent / Executor 调用的标准工具层。

它的作用是：

> 把普通 Python 函数包装成稳定、清楚、可被调用的 Tool。

---

## 3. main.py 和 tools.py 的区别

`main.py` 是人类开发者用来测试 pipeline 的入口。

它负责把流程直接写死：

```text
analyze_csv → classify_column → generate_report