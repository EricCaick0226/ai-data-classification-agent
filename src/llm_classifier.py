def should_use_llm(classification_result):
    category = classification_result.get("category")
    risk_level = classification_result.get("risk_level")
    needs_review = classification_result.get("needs_review")
    confidence = classification_result.get("confidence", 1.0)

    if category == "Unknown":
        return True

    if risk_level == "Unknown":
        return True

    if needs_review is True:
        return True

    if confidence < 0.6:
        return True

    return False

def mock_llm_classify(column_info):
    field_name = column_info.get("field_name", "unknown_field")
    sample_values = column_info.get("sample_values", [])

    return {
        "source": "mock_llm",
        "field_name": field_name,
        "category_suggestion": "Unknown",
        "risk_level_suggestion": "Unknown",
        "reason": (
            f"The field '{field_name}' is ambiguous. "
            "Based on the field name and sample values, it should be reviewed more carefully."
        ),
        "recommendation": (
            "Use a real LLM API later to inspect sample values and provide a deeper semantic judgment."
        ),
        "needs_review": True,
        "confidence": 0.4,
        "sample_values_checked": sample_values
    }

if __name__ == "__main__":
    test_result = {
        "category": "Unknown",
        "risk_level": "Unknown",
        "needs_review": True,
        "confidence": 0.35
    }

    print("Should use LLM?")
    print(should_use_llm(test_result))

    test_column = {
        "field_name": "notes",
        "data_type": "str",
        "missing_count": 1,
        "sample_values": ["prefers email contact", "needs follow-up"]
    }

    print("\nMock LLM result:")
    print(mock_llm_classify(test_column))