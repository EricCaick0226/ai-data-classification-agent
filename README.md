# AI Data Classification Agent

A small Agent-style demo for CSV data classification and risk-level analysis.

This project was built as part of my AI / data internship preparation. The goal is not to build a production-level data governance system, but to understand how an Agent-style workflow can be organized with an Agent, tools, an executor, structured output, and a human-readable report.

## Project Overview

AI Data Classification Agent takes a user task, checks whether the task is about CSV data classification, analyzes the CSV file, classifies each column, assigns a risk level, and generates a Markdown report.

The current version is mainly rule-based. It does not use LangChain, LangGraph, RAG, vector databases, multi-agent systems, Docker, deployment, or a frontend.

The focus of this project is the basic structure:

```text
User task
→ Agent
→ Tool-calling plan
→ Executor
→ Tools
→ Structured result
→ Markdown report
```

## Problem It Solves

In real data work, a team may need to quickly understand what kinds of fields exist in a dataset.

For example, a CSV file may contain:

- personal identifiers
- contact information
- authentication data
- location data
- device identifiers
- free-text fields that may need manual review

This project gives a simple way to inspect a CSV file, classify its columns, assign risk levels, and produce a readable report.

## Demo Command

Run the final Agent demo with:

```bash
python src/agent_demo.py
```

Example user input:

```text
请分析 data/sample_users.csv，并对每个字段做数据分类分级。
```

## Expected Output

After running the demo, the project should output:

- Agent execution logs
- a structured JSON-style result
- a Markdown report at `reports/classification_report.md`

The logs are for showing the execution process.

The JSON-style result is for structured program output and debugging.

The Markdown report is for human readers who want to understand the classification results without reading the code.

## Project Structure

```text
ai-data-classification-agent/
├── data/
│   └── sample_users.csv
├── notes/
│   └── 09_final_summary.md
├── reports/
│   └── classification_report.md
├── src/
│   ├── rules.py
│   ├── classifier.py
│   ├── csv_analyzer.py
│   ├── report_generator.py
│   ├── tools.py
│   ├── agent_executor.py
│   ├── agent_demo.py
│   ├── main.py
│   └── llm_classifier.py
└── README.md
```

## File Responsibilities

- `src/rules.py`  
  Stores the rule-based classification logic and risk-level rules.

- `src/classifier.py`  
  Contains the core `classify_column()` logic for classifying one column.

- `src/csv_analyzer.py`  
  Contains `analyze_csv(file_path)`, which reads a CSV file and extracts column information.

- `src/report_generator.py`  
  Contains `generate_report(results)`, which creates the Markdown classification report.

- `src/tools.py`  
  Wraps normal Python functions into Agent-callable tools, such as `analyze_csv_tool`, `classify_column_tool`, and `generate_report_tool`.

- `src/agent_executor.py`  
  Contains `execute_tool()`, which runs tools based on their tool names.

- `src/agent_demo.py`  
  The final Agent-style demo entry point.

- `src/main.py`  
  A normal pipeline testing entry point. It is useful for development, but it is not the final demo.

- `src/llm_classifier.py`  
  Optional LLM or mock LLM interface for future extension.

- `reports/classification_report.md`  
  The generated human-readable report.

## Agent / Tool / Executor Mapping

In this project, the Agent-style structure is mapped like this:

| Concept | Project Mapping |
|---|---|
| Agent | Logic in `src/agent_demo.py` |
| Executor | `execute_tool()` in `src/agent_executor.py` |
| Tools | Tool wrappers in `src/tools.py` |
| Structured Output | Final JSON-style dictionary from `src/agent_demo.py` |
| Markdown Report | `reports/classification_report.md` |

The Agent receives the user task, detects the task type, extracts the CSV path, creates a tool-calling plan, and summarizes the final result.

The Executor receives a tool name and arguments, then runs the correct tool.

The Tools perform the actual work, such as analyzing the CSV, classifying columns, and generating the report.

## Why This Is an Agent-Style Demo

This project is not only a fixed pandas script.

A normal pipeline would directly run the same functions in the same order.

This demo starts from a user task, detects the task type, creates a plan, calls tools through an executor, and returns a structured result.

The current version is still simple and mainly rule-based, but it follows the basic Agent / Tool / Executor pattern.

## Current Limitations

This project is intentionally small.

Current limitations:

- It is mainly rule-based.
- It focuses only on CSV data classification.
- It does not use a real LLM API by default.
- It is not a general-purpose AI Agent.
- Ambiguous fields still need manual review.
- The classification quality depends on the current rule library.
- It is not a production-level data governance system.

## About the LLM Part

The current version may include an optional or mock LLM interface, but the main demo does not depend on a real LLM API by default.

This is intentional.

The goal at this stage is to understand the Agent-style structure first:

```text
Agent decides what to do
Executor runs the selected tool
Tool performs the actual task
Structured output records the result
Report explains the result to humans
```

A real LLM API can be added later to help with ambiguous fields, but the project does not need to pretend to be more complex than it is.

## Future Improvements

Possible next steps:

- Add a real LLM API for ambiguous field classification.
- Expand the rule library.
- Improve analysis based on sample values, not only column names.
- Add a stricter JSON schema for structured output.
- Support more file types besides CSV.
- Add more test datasets.

## Internship Relevance

This project helped me understand the basic structure behind Agent-style systems before jumping into larger frameworks.

Through this project, I practiced:

- breaking a workflow into tools
- using an executor to call tools
- separating human-readable output from structured program output
- explaining how an Agent-style workflow works
- connecting data classification with privacy and risk review

The project is small, but it gives me a clearer foundation for understanding more advanced AI Agent frameworks later.