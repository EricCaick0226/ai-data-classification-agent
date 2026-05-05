from tools import (
    analyze_csv_tool,
    classify_column_tool,
    generate_report_tool,
)


TOOL_REGISTRY = {
    "analyze_csv": analyze_csv_tool,
    "classify_column": classify_column_tool,
    "generate_report": generate_report_tool,
}

def execute_tool(tool_name, **kwargs):
    if tool_name not in TOOL_REGISTRY:
        return {
            "status": "error",
            "tool_name": tool_name,
            "message": f"Tool '{tool_name}' not found."
        }

    tool_function = TOOL_REGISTRY[tool_name]
    result = tool_function(**kwargs)

    return result

if __name__ == "__main__":
    result = execute_tool(
        "analyze_csv",
        file_path="data/sample_users.csv"
    )
    print(result)