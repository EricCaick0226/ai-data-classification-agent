import re
from agent_executor import execute_tool

def get_user_task():
    user_task = input("请输入你的任务：")
    return user_task


def detect_task_type(user_task):
    keywords = ["CSV", "csv", "分析", "分类", "分级"]

    for keyword in keywords:
        if keyword in user_task:
            return "csv_data_classification"

    return "unknown"


def extract_csv_path(user_task):
    match = re.search(r"[\w./-]+\.csv", user_task)

    if match:
        return match.group(0)

    return "data/sample_users.csv"

def create_plan(csv_path):
    plan = [
        {
            "step": 1,
            "tool_name": "analyze_csv",
            "purpose": "Extract column metadata from CSV",
            "args": {
                "file_path": csv_path
            }
        },
        {
            "step": 2,
            "tool_name": "classify_column",
            "purpose": "Classify each column and assign risk level",
            "args": "for each column_info from analyze_csv result"
        },
        {
            "step": 3,
            "tool_name": "generate_report",
            "purpose": "Generate Markdown classification report",
            "args": {
                "output_path": "reports/classification_report.md"
            }
        }
    ]

    return plan

def build_summary(classification_results, report_path):
    total_fields = len(classification_results)

    fields_needing_review = sum(
        1 for result in classification_results
        if result.get("needs_review") == True
    )

    high_or_critical_risk_fields = sum(
        1 for result in classification_results
        if result.get("risk_level") in ["High", "Critical"]
    )

    summary = {
        "total_fields": total_fields,
        "fields_needing_review": fields_needing_review,
        "high_or_critical_risk_fields": high_or_critical_risk_fields,
        "report_path": report_path
    }

    return summary


def run_agent(user_task):
    agent_name = "DataClassificationAgent"

    print(f"\nAgent: {agent_name}")
    print("Agent is reading the user task...")

    task_type = detect_task_type(user_task)
    print(f"[Agent] 判断任务类型：{task_type}")

    if task_type != "csv_data_classification":
        return {
            "agent_name": agent_name,
            "task_type": task_type,
            "status": "error",
            "message": "This agent can only handle CSV data classification tasks for now."
        }

    csv_path = extract_csv_path(user_task)
    print(f"[Agent] 识别 CSV 路径：{csv_path}")
    plan = create_plan(csv_path)

    print("\n[Agent] 生成工具调用计划：")
    for step in plan:
         print(f"{step['step']}. {step['tool_name']}：{step['purpose']}")

    print("\nExecutor is running tools...")

    analyze_result = execute_tool(
        "analyze_csv",
        file_path=csv_path
    )

    if analyze_result["status"] != "success":
        return {
            "agent_name": agent_name,
            "task_type": task_type,
            "status": "error",
            "message": "Failed to analyze CSV.",
            "details": analyze_result
        }

    column_infos = analyze_result["result"]

    classification_results = []

    for column_info in column_infos:
        classify_result = execute_tool(
            "classify_column",
            column_info=column_info
        )

        if classify_result["status"] == "success":
            classification_results.append(classify_result["result"])
        else:
            classification_results.append({
                "field_name": column_info.get("field_name", "unknown"),
                "status": "error",
                "message": classify_result.get("message", "Classification failed.")
            })

    report_result = execute_tool(
        "generate_report",
        results=classification_results,
        output_path="reports/classification_report.md"
    )

    if report_result["status"] != "success":
        return {
            "agent_name": agent_name,
            "task_type": task_type,
            "status": "error",
            "message": "Failed to generate report.",
            "details": report_result
        }

    report_path = "reports/classification_report.md"
    summary = build_summary(classification_results, report_path)

    final_result = {
        "agent_name": agent_name,
        "task_type": task_type,
        "status": "success",
        "input": {
            "user_task": user_task,
            "csv_path": csv_path
        },
        "plan": plan,
        "tools_used": [
            "analyze_csv",
            "classify_column",
            "generate_report"
        ],
        "summary": summary,
        "results": classification_results,
        "message": "CSV data classification completed successfully."
}

    return final_result

if __name__ == "__main__":
    import json

    user_task = get_user_task()
    print(f"[Agent] 收到任务：{user_task}")
    final_result = run_agent(user_task)

    print("\nFinal Agent Result:")
    print(json.dumps(final_result, indent=2, ensure_ascii=False))