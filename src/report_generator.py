from pathlib import Path


def generate_report(results, output_path="reports/classification_report.md"):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    total_columns = len(results)
    review_count = sum(1 for item in results if item.get("review_required") is True)
    classified_count = sum(1 for item in results if item.get("classification_path"))
    security_level_counts = _count_by(results, "security_level")

    markdown_lines = []
    markdown_lines.append("# Column 分类分级报告")
    markdown_lines.append("")
    markdown_lines.append("## 汇总")
    markdown_lines.append("")
    markdown_lines.append(f"- Total columns: {total_columns}")
    markdown_lines.append(f"- Classified columns: {classified_count}")
    markdown_lines.append(f"- Review required columns: {review_count}")
    markdown_lines.append("")

    if security_level_counts:
        markdown_lines.append("## 等级统计")
        markdown_lines.append("")
        markdown_lines.append("| Security Level | Count |")
        markdown_lines.append("|---|---:|")
        for level, count in security_level_counts.items():
            markdown_lines.append(f"| {_escape(level)} | {count} |")
        markdown_lines.append("")

    review_items = [
        item for item in results
        if item.get("review_required") is True
    ]
    if review_items:
        markdown_lines.append("## 需要人工复核")
        markdown_lines.append("")
        markdown_lines.append("| Table | Column | Reason | Candidate Paths |")
        markdown_lines.append("|---|---|---|---|")
        for item in review_items:
            markdown_lines.append(
                "| {table_name} | {column_name} | {failure_reason} | {candidate_paths} |".format(
                    table_name=_escape(item.get("table_name")),
                    column_name=_escape(item.get("column_name")),
                    failure_reason=_escape(item.get("failure_reason") or item.get("basis")),
                    candidate_paths=_escape("; ".join(item.get("candidate_paths", []))),
                )
            )
        markdown_lines.append("")

    markdown_lines.append("## Column 分类分级明细")
    markdown_lines.append("")
    markdown_lines.append(
        "| Table | Column | Type | Description | Classification Path | "
        "Security Level | Level Name | Sharing Policy | Open Policy | Basis | Confidence | Review Required |"
    )
    markdown_lines.append("|---|---|---|---|---|---|---|---|---|---|---:|---|")

    for item in results:
        markdown_lines.append(
            "| {table_name} | {column_name} | {column_type} | {column_description} | "
            "{classification_path} | {security_level} | {level_name} | {sharing_policy} | "
            "{open_policy} | {basis} | {confidence} | {review_required} |".format(
                table_name=_escape(item.get("table_name")),
                column_name=_escape(item.get("column_name")),
                column_type=_escape(item.get("column_type")),
                column_description=_escape(item.get("column_description")),
                classification_path=_escape(item.get("classification_path")),
                security_level=_escape(item.get("security_level")),
                level_name=_escape(item.get("level_name")),
                sharing_policy=_escape(item.get("sharing_policy")),
                open_policy=_escape(item.get("open_policy")),
                basis=_escape(item.get("basis")),
                confidence=item.get("confidence", ""),
                review_required=item.get("review_required"),
            )
        )

    output.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    return str(output)


def _count_by(results, key):
    counts = {}
    for item in results:
        value = item.get(key)
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def _escape(value):
    if value is None:
        return ""

    return str(value).replace("\n", " ").replace("|", "\\|")


if __name__ == "__main__":
    fake_results = [
        {
            "table_name": "patient",
            "column_name": "patient_name",
            "column_type": "varchar",
            "column_description": "患者姓名",
            "classification_path": "基础资源 / 服务范围与对象 / 患者 / 患者信息",
            "security_level": "3级",
            "level_name": "一般数据3级",
            "sharing_policy": "有条件共享",
            "open_policy": "有条件开放",
            "basis": "column_description 与患者信息匹配。",
            "confidence": 0.86,
            "review_required": False,
        }
    ]
    print(generate_report(fake_results))
