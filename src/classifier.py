from rules import classify_field

def calculate_confidence(classification_result):
    risk_level = classification_result.get("risk_level", "Unknown")
    needs_review = classification_result.get("needs_review", True)

    base_confidence = {
        "Critical": 0.95,
        "High": 0.85,
        "Medium": 0.75,
        "Low": 0.65,
        "Unknown": 0.35
    }.get(risk_level, 0.35)

    if needs_review and base_confidence > 0.45:
        base_confidence -= 0.15

    return round(base_confidence, 2)


def classify_column(column_info):
    """
    Classify one column based on column information.
    """

    field_name = column_info["field_name"]
    data_type = column_info["data_type"]
    missing_count = column_info["missing_count"]
    sample_values = column_info["sample_values"]

    rule_result = classify_field(field_name)

    result = {
        "field_name": field_name,
        "data_type": data_type,
        "missing_count": missing_count,
        "sample_values": sample_values,
        "category": rule_result["category"],
        "risk_level": rule_result["risk_level"],
        "reason": rule_result["reason"],
        "recommendation": rule_result["recommendation"],
        "confidence": calculate_confidence(rule_result),
        "needs_review": rule_result["needs_review"],
    }

    return result
if __name__ == "__main__":
    test_columns = [
        {
            "field_name": "email",
            "data_type": "object",
            "missing_count": 0,
            "sample_values": ["a@gmail.com", "b@nyu.edu"],
        },
        {
            "field_name": "user_location",
            "data_type": "object",
            "missing_count": 2,
            "sample_values": ["New York", "Los Angeles"],
        },
        {
            "field_name": "notes",
            "data_type": "object",
            "missing_count": 5,
            "sample_values": ["student asked for help", "personal comment"],
        },
    ]

    for column in test_columns:
        result = classify_column(column)

        print("字段名:", result["field_name"])
        print("数据类型:", result["data_type"])
        print("缺失值数量:", result["missing_count"])
        print("样例值:", result["sample_values"])
        print("分类:", result["category"])
        print("等级:", result["risk_level"])
        print("原因:", result["reason"])
        print("建议:", result["recommendation"])
        print("置信度:", result["confidence"])
        print("是否需要人工复核:", result["needs_review"])
        print("-" * 50)