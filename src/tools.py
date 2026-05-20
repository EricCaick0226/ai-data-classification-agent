from classifier import classify_column
from csv_analyzer import read_column_metadata
from report_generator import generate_report
from rules import load_rule_catalog


def read_column_metadata_tool(file_path, sheet_name=None):
    result = read_column_metadata(file_path, sheet_name=sheet_name)

    return {
        "tool_name": "read_column_metadata_tool",
        "status": "success",
        "result": result,
    }


def load_rule_catalog_tool(excel_path):
    result = load_rule_catalog(excel_path)

    return {
        "tool_name": "load_rule_catalog_tool",
        "status": "success",
        "result": result,
    }


def classify_column_tool(column_info, rule_catalog):
    result = classify_column(column_info, rule_catalog)

    return {
        "tool_name": "classify_column_tool",
        "status": "success",
        "result": result,
    }


def generate_report_tool(results, output_path="reports/classification_report.md"):
    report_path = generate_report(results, output_path)

    return {
        "tool_name": "generate_report_tool",
        "status": "success",
        "result": report_path,
    }
