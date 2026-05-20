import argparse
import json
from pathlib import Path

from agent_executor import execute_tool


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sample_column_metadata.csv"
DEFAULT_RULES = Path("/Users/ericcai/Desktop/internfiles/分类分级标准.xlsx")
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "classification_report.md"


def create_plan(input_path, rules_path, output_path):
    return [
        {
            "step": 1,
            "tool_name": "read_column_metadata",
            "purpose": "Read database column metadata from CSV or Excel.",
            "args": {"file_path": input_path},
        },
        {
            "step": 2,
            "tool_name": "load_rule_catalog",
            "purpose": "Load classification and level rules from rule Excel.",
            "args": {"excel_path": rules_path},
        },
        {
            "step": 3,
            "tool_name": "classify_column",
            "purpose": "Use LLM semantic matching against rule candidates for each column.",
            "args": "for each column_info from read_column_metadata result",
        },
        {
            "step": 4,
            "tool_name": "generate_report",
            "purpose": "Generate standardized Markdown classification report.",
            "args": {"output_path": output_path},
        },
    ]


def build_summary(classification_results, report_path):
    total_columns = len(classification_results)
    review_required_columns = sum(
        1 for result in classification_results
        if result.get("review_required") is True
    )
    classified_columns = sum(
        1 for result in classification_results
        if result.get("classification_path")
    )

    return {
        "total_columns": total_columns,
        "classified_columns": classified_columns,
        "review_required_columns": review_required_columns,
        "report_path": report_path,
    }


def run_agent(input_path, rules_path, output_path):
    agent_name = "ColumnClassificationAgent"

    print(f"\nAgent: {agent_name}")
    print("[Agent] Building a single-task column classification plan...")

    plan = create_plan(input_path, rules_path, output_path)
    for step in plan:
        print(f"[Agent] {step['step']}. {step['tool_name']}: {step['purpose']}")

    print("\n[Executor] Calling tool: read_column_metadata")
    metadata_result = execute_tool("read_column_metadata", file_path=input_path)
    if metadata_result["status"] != "success":
        return _error_result(agent_name, "Failed to read column metadata.", metadata_result)

    column_infos = metadata_result["result"]
    print(f"[Executor] Loaded {len(column_infos)} columns.")

    print("\n[Executor] Calling tool: load_rule_catalog")
    rules_result = execute_tool("load_rule_catalog", excel_path=rules_path)
    if rules_result["status"] != "success":
        return _error_result(agent_name, "Failed to load rule Excel.", rules_result)

    rule_catalog = rules_result["result"]
    print(
        "[Executor] Loaded "
        f"{len(rule_catalog.classification_rules)} classification rules and "
        f"{len(rule_catalog.level_rules)} level rules."
    )

    print("\n[Executor] Calling tool: classify_column for each column")
    classification_results = []
    for column_info in column_infos:
        classify_result = execute_tool(
            "classify_column",
            column_info=column_info,
            rule_catalog=rule_catalog,
        )

        if classify_result["status"] == "success":
            classification_results.append(classify_result["result"])
        else:
            classification_results.append(
                {
                    "table_name": column_info.get("table_name", ""),
                    "column_name": column_info.get("column_name", ""),
                    "column_type": column_info.get("column_type", ""),
                    "column_description": column_info.get("column_description", ""),
                    "classification_path": "",
                    "security_level": "",
                    "level_name": "",
                    "sharing_policy": "",
                    "open_policy": "",
                    "basis": "分类工具调用失败，需要人工复核。",
                    "confidence": 0,
                    "review_required": True,
                    "failure_reason": classify_result.get("message", "Classification failed."),
                    "candidate_paths": [],
                }
            )

    print(f"[Executor] Processed {len(classification_results)} columns.")

    print("\n[Executor] Calling tool: generate_report")
    report_result = execute_tool(
        "generate_report",
        results=classification_results,
        output_path=output_path,
    )
    if report_result["status"] != "success":
        return _error_result(agent_name, "Failed to generate report.", report_result)

    report_path = report_result["result"]
    summary = build_summary(classification_results, report_path)

    print("\n[Agent] Task completed.")
    print(f"Total columns: {summary['total_columns']}")
    print(f"Classified columns: {summary['classified_columns']}")
    print(f"Review required columns: {summary['review_required_columns']}")
    print(f"Report path: {summary['report_path']}")

    return {
        "agent_name": agent_name,
        "status": "success",
        "input": {
            "column_metadata_path": input_path,
            "rule_excel_path": rules_path,
        },
        "plan": plan,
        "tools_used": [
            "read_column_metadata",
            "load_rule_catalog",
            "classify_column",
            "generate_report",
        ],
        "summary": summary,
        "results": classification_results,
        "message": "Column classification completed.",
    }


def _error_result(agent_name, message, details):
    return {
        "agent_name": agent_name,
        "status": "error",
        "message": message,
        "details": details,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Excel-rule-driven column classification agent."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="CSV or Excel file containing database column metadata.",
    )
    parser.add_argument(
        "--rules",
        default=str(DEFAULT_RULES),
        help="Excel file containing classification and level rules.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Markdown report output path.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    final_result = run_agent(
        input_path=args.input,
        rules_path=args.rules,
        output_path=args.output,
    )

    print("\nFinal Agent Result:")
    print(json.dumps(final_result, indent=2, ensure_ascii=False, default=str))
