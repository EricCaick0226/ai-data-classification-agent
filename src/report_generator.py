def generate_report(results, output_path="reports/classification_report.md"):
    total_fields = len(results)

    needs_review_count = sum(
        1 for item in results
        if item.get("needs_review") is True
    )

    high_risk_count = sum(
        1 for item in results
        if item.get("risk_level") in ["High", "Critical"]
    )

    markdown_lines = []

    markdown_lines.append("# Data Classification Report")
    markdown_lines.append("")
    markdown_lines.append("This report summarizes the classification and risk level of each field in the dataset.")
    markdown_lines.append("")
    markdown_lines.append("## Summary")
    markdown_lines.append("")
    markdown_lines.append(f"- Total fields: {total_fields}")
    markdown_lines.append(f"- Fields needing manual review: {needs_review_count}")
    markdown_lines.append(f"- High or Critical risk fields: {high_risk_count}")
    markdown_lines.append("")
    markdown_lines.append("## Field Classification Details")
    markdown_lines.append("")
    markdown_lines.append("| Field Name | Data Type | Missing Count | Category | Risk Level | Reason | Recommendation | Needs Review |")
    markdown_lines.append("|---|---|---|---|---|---|---|---|")

    for item in results:
        markdown_lines.append(
            f"| {item.get('field_name')} "
            f"| {item.get('data_type')} "
            f"| {item.get('missing_count')} "
            f"| {item.get('category')} "
            f"| {item.get('risk_level')} "
            f"| {item.get('reason')} "
            f"| {item.get('recommendation')} "
            f"| {item.get('needs_review')} |"
        )

    markdown_lines.append("")

    markdown_content = "\n".join(markdown_lines)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(markdown_content)

    return output_path

if __name__ == "__main__":
    fake_results = [
        {
            "field_name": "email",
            "data_type": "object",
            "missing_count": 0,
            "sample_values": ["eric@example.com", "student@nyu.edu"],
            "category": "PII",
            "risk_level": "Medium",
            "reason": "Email can identify or contact a person.",
            "recommendation": "Protect this field and avoid unnecessary exposure.",
            "needs_review": False
        },
        {
            "field_name": "notes",
            "data_type": "object",
            "missing_count": 1,
            "sample_values": ["prefers email contact", "needs follow-up"],
            "category": "Unknown",
            "risk_level": "Unknown",
            "reason": "Free-text fields may contain unpredictable information.",
            "recommendation": "Review this field manually before sharing.",
            "needs_review": True
        },
        {
            "field_name": "password",
            "data_type": "object",
            "missing_count": 0,
            "sample_values": ["fake_password_1", "fake_password_2"],
            "category": "Authentication",
            "risk_level": "Critical",
            "reason": "Passwords are sensitive authentication data.",
            "recommendation": "Never expose passwords in plain text.",
            "needs_review": False
        }
    ]

    report_path = generate_report(fake_results)
    print(f"Report generated: {report_path}")