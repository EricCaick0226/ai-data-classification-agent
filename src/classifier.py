from llm_classifier import classify_column_with_llm, classify_columns_with_llm


CONFIDENCE_THRESHOLD = 0.7


def classify_column(column_info, rule_catalog, confidence_threshold=CONFIDENCE_THRESHOLD):
    candidate_rules = rule_catalog.get_candidate_rules(column_info)
    llm_result = classify_column_with_llm(
        column_info=column_info,
        candidate_rules=candidate_rules,
        level_rules=rule_catalog.level_rules,
    )

    validation = _validate_llm_result(
        llm_result=llm_result,
        rule_catalog=rule_catalog,
        confidence_threshold=confidence_threshold,
        candidate_rules=candidate_rules,
    )
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


def classify_columns(
    column_infos,
    rule_catalog,
    batch_size=10,
    confidence_threshold=CONFIDENCE_THRESHOLD,
):
    results = []

    for start in range(0, len(column_infos), batch_size):
        batch_column_infos = column_infos[start : start + batch_size]
        batch_items = []
        candidate_rules_by_index = {}
        column_info_by_index = {}

        for offset, column_info in enumerate(batch_column_infos):
            column_index = start + offset
            candidate_rules = rule_catalog.get_candidate_rules(column_info)
            batch_items.append(
                {
                    "column_index": column_index,
                    "column_info": column_info,
                    "candidate_rules": candidate_rules,
                }
            )
            candidate_rules_by_index[column_index] = candidate_rules
            column_info_by_index[column_index] = column_info

        batch_result = classify_columns_with_llm(
            batch_items=batch_items,
            level_rules=rule_catalog.level_rules,
        )

        if batch_result.get("status") != "success":
            results.extend(
                _fallback_batch_to_single(
                    batch_items=batch_items,
                    rule_catalog=rule_catalog,
                    confidence_threshold=confidence_threshold,
                )
            )
            continue

        batch_results_by_index = _index_batch_results(batch_result.get("results", []))

        for item in batch_items:
            column_index = item["column_index"]
            column_info = column_info_by_index[column_index]
            candidate_rules = candidate_rules_by_index[column_index]
            item_result = batch_results_by_index.get(column_index)

            if item_result is None:
                results.append(
                    _fallback_single_column(
                        column_info=column_info,
                        rule_catalog=rule_catalog,
                        confidence_threshold=confidence_threshold,
                    )
                )
                continue

            item_result = {
                **item_result,
                "status": "success",
                "raw_response": batch_result.get("raw_response", ""),
            }
            validation = _validate_llm_result(
                llm_result=item_result,
                rule_catalog=rule_catalog,
                confidence_threshold=confidence_threshold,
                candidate_rules=candidate_rules,
            )
            if validation["is_valid"]:
                results.append(
                    _build_valid_result(
                        column_info=column_info,
                        llm_result=item_result,
                        matched_rule=validation["matched_rule"],
                        level_rule=validation["level_rule"],
                        candidate_rules=candidate_rules,
                    )
                )
            else:
                results.append(
                    _fallback_single_column(
                        column_info=column_info,
                        rule_catalog=rule_catalog,
                        confidence_threshold=confidence_threshold,
                    )
                )

    return results


def _validate_llm_result(llm_result, rule_catalog, confidence_threshold, candidate_rules):
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

    candidate_paths = {
        rule["classification_path"]
        for rule in candidate_rules
    }
    if classification_path not in candidate_paths:
        return {
            "is_valid": False,
            "failure_reason": "LLM returned a classification_path outside this column's candidates.",
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


def _index_batch_results(batch_results):
    indexed_results = {}
    for item in batch_results:
        column_index = _to_int(item.get("column_index"))
        if column_index is None:
            continue
        indexed_results[column_index] = item
    return indexed_results


def _fallback_batch_to_single(batch_items, rule_catalog, confidence_threshold):
    return [
        _fallback_single_column(
            column_info=item["column_info"],
            rule_catalog=rule_catalog,
            confidence_threshold=confidence_threshold,
        )
        for item in batch_items
    ]


def _fallback_single_column(column_info, rule_catalog, confidence_threshold):
    return classify_column(
        column_info=column_info,
        rule_catalog=rule_catalog,
        confidence_threshold=confidence_threshold,
    )


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
