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
            "args": {
                "file_path": csv_path
            }
        },
        {
            "step": 2,
            "tool_name": "classify_column",
            "args": "for each column_info from analyze_csv result"
        },
        {
            "step": 3,
            "tool_name": "generate_report",
            "args": {
                "output_path": "reports/classification_report.md"
            }
        }
    ]

    return plan

def run_agent(user_task):
    agent_name = "DataClassificationAgent"

    print(f"\nAgent: {agent_name}")
    print("Agent is reading the user task...")

    task_type = detect_task_type(user_task)

    if task_type != "csv_data_classification":
        return {
            "agent_name": agent_name,
            "task_type": task_type,
            "status": "error",
            "message": "This agent can only handle CSV data classification tasks for now."
        }

    csv_path = extract_csv_path(user_task)
    plan = create_plan(csv_path)

    print("\nAgent created a plan:")
    for step in plan:
        print(step)

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

    final_result = {
        "agent_name": agent_name,
        "task_type": task_type,
        "status": "success",
        "csv_path": csv_path,
        "tools_used": [
            "analyze_csv",
            "classify_column",
            "generate_report"
        ],
        "field_count": len(classification_results),
        "report_path": "reports/classification_report.md",
        "results": classification_results
    }

    return final_result

if __name__ == "__main__":
    import json

    user_task = get_user_task()
    final_result = run_agent(user_task)

    print("\nFinal Agent Result:")
    print(json.dumps(final_result, indent=2, ensure_ascii=False))