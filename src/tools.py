from csv_analyzer import analyze_csv
from classifier import classify_column
from report_generator import generate_report

def analyze_csv_tool(file_path):
    result = analyze_csv(file_path)

    return {
        "tool_name": "analyze_csv_tool",
        "status": "success",
        "result": result
    }

def classify_column_tool(column_info):
    result = classify_column(column_info)

    return {
        "tool_name": "classify_column_tool",
        "status": "success",
        "result": result
    }
def generate_report_tool(results, output_path="reports/classification_report.md"):
    generate_report(results, output_path)

    return {
        "tool_name": "generate_report_tool",
        "status": "success",
        "result": output_path
    }


if __name__ == "__main__":
    csv_result = analyze_csv_tool("data/sample_users.csv")
    print(csv_result)

    classified_results = []
    for column_info in csv_result["result"]:
        classified = classify_column_tool(column_info)
        classified_results.append(classified["result"])

    report_result = generate_report_tool(classified_results)
    print(report_result)