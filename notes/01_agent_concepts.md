# Day 1 笔记：AI Agent 与数据分类分级基础概念

## 1. 项目目标

本项目叫：

`ai-data-classification-agent`

最终目标是：

输入一个 CSV 文件，系统能够读取字段信息，判断字段类型，对字段进行分类分级，并生成一份 Markdown 报告。

第一阶段不使用 LLM，不调用 OpenAI API。

第一阶段只用 Python、pandas 和规则分类器完成最小闭环。

## 2. 数据分类分级是什么？

数据分类分级，就是判断一个字段属于什么类型、风险有多高、是否需要保护。

例如：

| 字段名 | 分类 | 风险等级 | 理由 | 是否需要人工复核 |
|---|---|---|---|---|
| email | 个人信息 PII | 中 | 邮箱可以识别或联系到个人 | 否 |
| phone_number | 个人信息 PII | 中 | 电话号码属于个人联系方式 | 否 |
| password | 敏感信息 Sensitive | 高 | 密码可以用于登录账号 | 否 |
| id_card | 机密信息 Confidential | 高 | 身份证件属于强身份识别信息 | 否 |
| username | 内部信息 Internal | 低或中 | 用户名可能与个人账号有关 | 是 |

## 3. LLM 是什么？

LLM 的英文是 Large Language Model，中文是大语言模型。

可以先把 LLM 理解成一个很会读文字、写文字、总结规则、解释原因的 AI 助手。

在本项目中，LLM 以后可以帮助判断一些模糊字段。

例如：

字段名：

`contact`

样例值：

`["eric@gmail.com", "212-555-1234"]`

LLM 可能会判断：

这个字段包含联系方式，可能包括邮箱和电话，因此属于个人信息 PII，需要中等级别保护，并建议人工复核。

但是 Day 1 不使用 LLM。

## 4. Prompt 是什么？

Prompt 就是给 LLM 的任务说明。

也可以理解成：你怎么跟 AI 说话。

例如：

请判断下面这个字段是否包含敏感信息：

字段名：`email`

样例值：`["a@gmail.com", "b@nyu.edu"]`

请输出：

- 字段分类
- 风险等级
- 判断理由
- 是否需要人工复核

这段话就是一个 Prompt。

## 5. Token 是什么？

Token 是 LLM 处理文字时的基本单位。

你可以粗略理解成：模型不是直接按完整句子理解文字，而是把文字切成很多小块。

例如：

`phone_number`

可能会被模型拆成类似：

- `phone`
- `_`
- `number`

Token 很重要，因为以后调用 LLM API 时，输入和输出通常都会按照 token 计算成本和长度限制。

Day 1 只需要记住：

Token = 模型读写文本的小单位。

## 6. API 是什么？

API 的英文是 Application Programming Interface，中文可以理解成“应用程序接口”。

简单说，API 就是让你的代码和外部服务沟通的方式。

例如，以后 Python 代码可能通过 API 问 LLM：

请判断 `password` 这个字段的风险等级。

LLM 可能返回：

```json
{
  "field_name": "password",
  "category": "Sensitive",
  "risk_level": "High",
  "reason": "Password can be used to access user accounts.",
  "needs_review": false
}
```md
```

## 7. Tool 是什么？

Tool 中文可以理解成“工具”。

在 AI Agent 项目里，Tool 通常是一个可以被 AI 调用的函数。

比如在本项目中，未来可能会有一个工具叫：

`analyze_csv_tool(csv_path)`

它的作用是读取 CSV 文件，并返回字段信息，例如：

- 字段名
- 数据类型
- 缺失值数量
- 样例值

例如输入：

`data/sample_users.csv`

可能输出：

| 字段名 | 数据类型 | 缺失值数量 | 样例值 |
|---|---|---|---|
| email | string | 0 | eric@gmail.com |
| phone_number | string | 1 | 212-555-1234 |
| password | string | 0 | abc123456 |

在本项目中，未来可能会有这些工具：

1. CSV 分析工具
2. 字段分类工具
3. 风险分级工具
4. Markdown 报告生成工具

Day 1 只需要记住：

Tool = 一个可以被调用的函数。

---

## 8. Tool Calling 是什么？

Tool Calling 中文可以理解成“工具调用”。

它的意思是：LLM 不只是回答问题，而是可以判断自己需要调用哪个工具。

例如用户说：

请帮我分析这个 CSV 里有哪些敏感字段。

LLM 自己不能直接读取本地 CSV 文件，所以它需要调用工具。

可能的过程是：

用户提出任务  
↓  
LLM 判断需要读取 CSV  
↓  
调用 CSV 分析工具  
↓  
工具返回字段名、数据类型、缺失值、样例值  
↓  
LLM 或规则分类器继续判断字段分类和风险等级  
↓  
生成结果  

在本项目中，未来的 Tool Calling 可能是：

`analyze_csv_tool` 负责分析 CSV  
`classify_field_tool` 负责分类字段  
`generate_report_tool` 负责生成报告  

Day 1 只需要记住：

Tool Calling = AI 根据任务选择并调用工具。

---

## 9. Chain 是什么？

Chain 中文可以理解成“链条”或“流程链”。

它指的是把多个步骤按顺序串起来。

本项目第一阶段就是一个很简单的 Chain：

1. 读取 CSV 文件
2. 分析字段信息
3. 根据规则判断字段类型
4. 判断风险等级
5. 判断是否需要人工复核
6. 生成 Markdown 报告

这个流程可以写成：

CSV 文件  
↓  
字段分析  
↓  
规则分类  
↓  
风险分级  
↓  
报告生成  

注意：

Chain 不一定必须使用 LangChain。

我们自己用 Python 函数一个接一个执行，也是一种 Chain 的思想。

Day 1 只需要记住：

Chain = 多个步骤按顺序串起来。

---

## 10. Agent 是什么？

Agent 中文可以理解成“智能体”。

但 Day 1 不要把 Agent 想得太玄学。

Agent 可以先理解成：

一个有目标、能选择工具、能决定下一步做什么的 AI 系统。

普通程序通常是写死流程：

先读取 CSV  
↓  
再分析字段  
↓  
再分类  
↓  
再生成报告  

Agent 更像是根据目标自己判断：

目标：帮用户分析 CSV 中的敏感字段。

它可能会决定：

1. 我需要先读取 CSV
2. 我需要分析字段名和样例值
3. 我需要判断哪些字段是个人信息
4. 我需要判断哪些字段风险较高
5. 我需要把不确定的字段标记为人工复核
6. 我需要生成 Markdown 报告

在本项目中，未来的 Agent 不需要很复杂。

它只要能围绕一个任务选择合适工具并完成流程就够了。

Day 1 只需要记住：

Agent = 目标 + 工具 + 决策 + 执行。

---

## 11. Agent Executor 是什么？

Agent Executor 中文可以理解成“Agent 执行器”。

它负责真正执行 Agent 做出的决定。

可以这样理解：

- Agent = 决策者
- Executor = 执行者
- Tool = 被调用的工具

例如：

Agent 判断：

我需要分析 CSV 文件。

Executor 执行：

调用 `analyze_csv_tool("data/sample_users.csv")`

Tool 返回：

字段名、数据类型、缺失值、样例值。

然后 Agent 再决定下一步：

我需要调用分类工具。

Executor 再执行：

调用 `classify_field_tool(...)`

Day 1 只需要记住：

Agent Executor = 负责执行 Agent 决策的部分。

---

## 12. Structured Output / JSON Output 是什么？

Structured Output 中文是“结构化输出”。

JSON Output 是一种常见的结构化输出。

普通自然语言输出可能是：

这个 email 字段应该属于个人信息，风险中等，因为邮箱可以识别或联系到个人。

结构化输出则是：

```json
{
  "field_name": "email",
  "category": "PII",
  "risk_level": "Medium",
  "reason": "Email can identify or contact a person.",
  "needs_review": false
}