from tools import (
    classify_column_tool,
    generate_report_tool,
    load_rule_catalog_tool,
    read_column_metadata_tool,
)


TOOL_REGISTRY = {
    "read_column_metadata": read_column_metadata_tool,
    "load_rule_catalog": load_rule_catalog_tool,
    "classify_column": classify_column_tool,
    "generate_report": generate_report_tool,
}


def execute_tool(tool_name, **kwargs):
    if tool_name not in TOOL_REGISTRY:
        return {
            "status": "error",
            "tool_name": tool_name,
            "message": f"Tool '{tool_name}' not found.",
        }

    tool_function = TOOL_REGISTRY[tool_name]
    try:
        result = tool_function(**kwargs)
    except Exception as exc:
        return {
            "status": "error",
            "tool_name": tool_name,
            "message": str(exc),
        }

    return result
