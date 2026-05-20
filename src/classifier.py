from llm_classifier import classify_column_with_llm


CONFIDENCE_THRESHOLD = 0.7


def classify_column(column_info, rule_catalog, confidence_threshold=CONFIDENCE_THRESHOLD):
    candidate_rules = rule_catalog.get_candidate_rules(column_info)
    llm_result = classify_column_with_llm(
        column_info=column_info,
        candidate_rules=candidate_rules,
        level_rules=rule_catalog.level_rules,
    )

    validation = _validate_llm_result(llm_result, rule_catalog, confidence_threshold)
    if validation["is_valid"]:
        return _build_valid_result(
            column_info=column_info,
            llm_result=llm_result,
            matched_rule=validation["matched_rule"],
            level_rule=validation["level_rule"],
            candidate_rules=candidate_rules,
        )

    return _build_review_result(
        column_info=column_info,
        candidate_rules=candidate_rules,
        failure_reason=validation["failure_reason"],
        llm_result=llm_result,
    )


def _validate_llm_result(llm_result, rule_catalog, confidence_threshold):
    if llm_result.get("status") != "success":
        return {
            "is_valid": False,
            "failure_reason": llm_result.get("error", "LLM classification failed."),
        }

    classification_path = str(llm_result.get("classification_path", "")).strip()
    security_level = str(llm_result.get("security_level", "")).strip()
    confidence = _to_float(llm_result.get("confidence"))

    if not classification_path:
        return {
            "is_valid": False,
            "failure_reason": "LLM result is missing classification_path.",
        }

    matched_rule = rule_catalog.get_rule_by_path(classification_path)
    if matched_rule is None:
        return {
            "is_valid": False,
            "failure_reason": "LLM returned a classification_path outside the rule Excel.",
        }

    recommended_level = matched_rule.get("recommended_level", "")
    if recommended_level and security_level and security_level != recommended_level:
        return {
            "is_valid": False,
            "failure_reason": "LLM security_level does not match the rule Excel recommended level.",
        }

    if recommended_level:
        security_level = recommended_level
        llm_result["security_level"] = security_level
    elif not security_level:
        return {
            "is_valid": False,
            "failure_reason": "Matched rule has no recommended level and LLM did not return security_level.",
        }

    level_rule = rule_catalog.get_level_rule(security_level)
    if level_rule is None:
        return {
            "is_valid": False,
            "failure_reason": "LLM returned a security_level outside the level rules.",
        }

    if confidence is None:
        return {
            "is_valid": False,
            "failure_reason": "LLM result is missing a numeric confidence value.",
        }

    if confidence < confidence_threshold:
        return {
            "is_valid": False,
            "failure_reason": "LLM confidence is below threshold.",
        }

    return {
        "is_valid": True,
        "matched_rule": matched_rule,
        "level_rule": level_rule,
    }


def _build_valid_result(column_info, llm_result, matched_rule, level_rule, candidate_rules):
    confidence = round(_to_float(llm_result.get("confidence")) or 0, 2)
    review_required = bool(llm_result.get("review_required", False))

    return {
        **_column_result_base(column_info),
        "classification_path": matched_rule["classification_path"],
        "security_level": level_rule["security_level"],
        "level_name": level_rule["level_name"],
        "sharing_policy": level_rule["sharing_policy"],
        "open_policy": level_rule["open_policy"],
        "basis": str(llm_result.get("basis", "")).strip(),
        "confidence": confidence,
        "review_required": review_required,
        "failure_reason": "",
        "candidate_paths": _candidate_paths(candidate_rules),
    }


def _build_review_result(column_info, candidate_rules, failure_reason, llm_result):
    return {
        **_column_result_base(column_info),
        "classification_path": "",
        "security_level": "",
        "level_name": "",
        "sharing_policy": "",
        "open_policy": "",
        "basis": "未形成可信分类结论，需要人工复核。",
        "confidence": 0,
        "review_required": True,
        "failure_reason": failure_reason,
        "candidate_paths": _candidate_paths(candidate_rules),
        "llm_raw_response": llm_result.get("raw_response", ""),
    }


def _column_result_base(column_info):
    return {
        "table_name": column_info.get("table_name", ""),
        "column_name": column_info.get("column_name", ""),
        "column_type": column_info.get("column_type", ""),
        "column_description": column_info.get("column_description", ""),
    }


def _candidate_paths(candidate_rules):
    return [
        rule["classification_path"]
        for rule in candidate_rules[:5]
    ]


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
