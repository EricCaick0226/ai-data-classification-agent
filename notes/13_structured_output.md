# Day 13 笔记：Structured Output

## 1. 今天目标

今天的目标是升级 `src/agent_demo.py` 的最终输出格式。

之前 Agent Demo 已经可以接收用户任务、判断任务类型、调用工具，并生成报告。

今天的重点不是增加新功能，而是把最终结果整理成稳定的 JSON-style dictionary。

也就是说，运行：

```bash
python src/agent_demo.py