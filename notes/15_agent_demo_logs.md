# Day 15: Agent Demo Interaction and Logs

## 1. 今日目标

今天的目标是优化 `src/agent_demo.py`，让它的运行过程更像一个真正的 Agent Demo。

重点不是增加复杂功能，而是让 Demo 在运行时清楚展示：

用户任务  
↓  
Agent 判断任务类型  
↓  
Agent 生成工具调用计划  
↓  
Executor 调用 Tool  
↓  
Tool 返回结果  
↓  
Agent 汇总并输出 Structured Output  

---

## 2. 为什么今天重要

一个好的 Demo 不只是“能跑”，还要让别人看懂它在干什么。

如果只在最后输出一个 JSON，别人可能看不出来这是 Agent Demo，可能会以为这只是一个普通的 `main.py` 脚本。

所以今天加入运行日志，让整个过程更透明：

- Agent 收到了什么任务
- Agent 判断这个任务属于什么类型
- Agent 准备调用哪些工具
- Executor 正在调用哪个 Tool
- 每个 Tool 是否调用成功
- 最终报告生成在哪里
- 最终结构化结果是什么

这能让面试官、mentor 或实习 supervisor 更容易理解项目结构。

---

## 3. 今天学到什么

今天学到的核心概念是：

> Demo log 是给人看的，Structured Output 是给程序看的。

例如：

```text
[Agent] 收到任务：请分析 data/sample_users.csv，并对每个字段做数据分类分级。
[Agent] 判断任务类型：csv_data_classification
[Executor] Calling tool: analyze_csv
[Executor] Tool analyze_csv finished successfully.