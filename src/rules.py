from dataclasses import dataclass
import math
import os
import re

import pandas as pd


CLASSIFICATION_COLUMNS = [
    "一级分类",
    "二级分类",
    "三级分类",
    "四级分类",
    "五级分类",
    "推荐分级",
    "分类说明",
]

LEVEL_COLUMNS = [
    "安全等级",
    "等级名称",
    "共享属性",
    "开放属性",
]

CLASSIFICATION_SHEET_NAME = "分类"
LEVEL_SHEET_NAME = "分级"
MIN_CANDIDATE_SCORE = 2
WIDE_MIN_CANDIDATE_SCORE = 1
DEFAULT_CANDIDATE_LIMIT = 20
WIDE_CANDIDATE_LIMIT = 40
CLEAR_SCORE_GAP = 5
CLOSE_SCORE_GAP = 4
CLEAR_DIRECT_MATCH_LENGTH = 3
CLEAR_STRONG_DIRECT_MATCH_LENGTH = 5
MATCH_PROFILE_MODES = {"off", "always", "auto"}
AMBIGUOUS_FIELD_TOKENS = {
    "amount",
    "result",
    "status",
    "type",
    "record",
    "plan",
    "value",
    "code",
    "金额",
    "结果",
    "状态",
    "类型",
    "记录",
    "方案",
    "数值",
    "代码",
}
LOW_INFORMATION_FIELD_TOKENS = AMBIGUOUS_FIELD_TOKENS | {
    "name",
    "姓名",
}
GENERIC_TABLE_TOKENS = {
    "generic",
    "generic_table",
    "table",
    "data",
    "record",
    "info",
    "通用",
    "表",
    "数据",
    "记录",
    "信息",
}

GENERIC_MATCH_TERMS = {
    "信息",
    "数据",
    "记录",
    "时间",
    "管理",
    "服务",
    "系统",
    "业务",
    "内容",
    "结果",
    "编号",
    "名称",
    "类型",
    "相关",
    "包括",
    "以及",
    "等",
    "和",
    "与",
    "或",
}


@dataclass
class RuleCatalog:
    classification_rules: list[dict]
    level_rules: dict[str, dict]
    match_profile_status: dict | None = None

    def get_rule_by_path(self, classification_path):
        for rule in self.classification_rules:
            if rule["classification_path"] == classification_path:
                return rule
        return None

    def get_level_rule(self, security_level):
        return self.level_rules.get(str(security_level).strip())

    def get_candidate_rules(self, column_info, limit=DEFAULT_CANDIDATE_LIMIT):
        if (
            _is_low_semantic_technical_field(column_info)
            or _is_low_information_generic_field(column_info)
        ):
            return []

        source_text = _build_column_search_text(column_info)
        scored_rules = _score_rules(source_text, self.classification_rules)
        wide_scored_candidates = [
            (score, rule) for score, rule in scored_rules
            if score >= WIDE_MIN_CANDIDATE_SCORE
        ][:max(limit, WIDE_CANDIDATE_LIMIT)]
        wide_candidates = [rule for _, rule in wide_scored_candidates]

        if not wide_candidates:
            return []

        if _should_enrich_with_llm_profile(
            column_info=column_info,
            source_text=source_text,
            scored_candidates=wide_scored_candidates,
            limit=limit,
        ):
            _enrich_candidate_rules(column_info, wide_candidates)

        rescored_candidates = _score_rules(source_text, wide_candidates)

        candidate_rules = [
            _with_candidate_score(rule, score, rank)
            for rank, (score, rule) in enumerate(rescored_candidates, start=1)
            if score >= MIN_CANDIDATE_SCORE
        ][:limit]

        return candidate_rules


def load_rule_catalog(excel_path):
    classification_df = _read_template_sheet(
        excel_path,
        preferred_sheet_name=CLASSIFICATION_SHEET_NAME,
        required_columns=CLASSIFICATION_COLUMNS,
    )
    level_df = _read_template_sheet(
        excel_path,
        preferred_sheet_name=LEVEL_SHEET_NAME,
        required_columns=LEVEL_COLUMNS,
    )

    classification_rules = _build_classification_rules(classification_df)
    match_profile_status = _match_profile_status()
    level_rules = _build_level_rules(level_df)

    if not classification_rules:
        raise ValueError("No classification rules found in the rule Excel file.")

    if not level_rules:
        raise ValueError("No level rules found in the rule Excel file.")

    return RuleCatalog(
        classification_rules=classification_rules,
        level_rules=level_rules,
        match_profile_status=match_profile_status,
    )


def _read_template_sheet(excel_path, preferred_sheet_name, required_columns):
    try:
        xls = pd.ExcelFile(excel_path)
    except ImportError as exc:
        raise RuntimeError(
            "Reading rule Excel files requires openpyxl. "
            "Use the project virtual environment: "
            "source .venv/bin/activate, or run with .venv/bin/python."
        ) from exc

    sheet_names = list(xls.sheet_names)

    candidate_sheets = []
    if preferred_sheet_name in sheet_names:
        candidate_sheets.append(preferred_sheet_name)
    candidate_sheets.extend(name for name in sheet_names if name not in candidate_sheets)

    for sheet_name in candidate_sheets:
        try:
            raw_df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
        except ImportError as exc:
            raise RuntimeError(
                "Reading rule Excel files requires openpyxl. "
                "Use the project virtual environment: "
                "source .venv/bin/activate, or run with .venv/bin/python."
            ) from exc

        header_index = _find_header_index(raw_df, required_columns)
        if header_index is None:
            continue

        headers = [_normalize_cell(value) for value in raw_df.iloc[header_index].tolist()]
        df = raw_df.iloc[header_index + 1 :].copy()
        df.columns = headers
        df = df.loc[:, [column for column in df.columns if column]]
        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]
        if missing_columns:
            continue

        return df[required_columns].copy()

    raise ValueError(
        "Could not find a sheet with required columns: "
        + ", ".join(required_columns)
    )


def _find_header_index(raw_df, required_columns):
    required_set = set(required_columns)

    for index, row in raw_df.iterrows():
        values = {_normalize_cell(value) for value in row.tolist()}
        if required_set.issubset(values):
            return index

    return None


def _build_classification_rules(df):
    rules = []

    for _, row in df.iterrows():
        parts = [
            _normalize_cell(row.get(column))
            for column in CLASSIFICATION_COLUMNS[:5]
        ]
        classification_parts = [part for part in parts if part]
        if not classification_parts:
            continue

        recommended_level = _normalize_cell(row.get("推荐分级"))
        description = _normalize_cell(row.get("分类说明"))

        rules.append(
            {
                "classification_path": " / ".join(classification_parts),
                "classification_parts": classification_parts,
                "recommended_level": recommended_level,
                "classification_description": description,
                "match_terms": _build_rule_match_terms(
                    classification_parts=classification_parts,
                    description=description,
                ),
            }
        )

    _prune_common_match_terms(rules)
    return rules


def _build_level_rules(df):
    level_rules = {}

    for _, row in df.iterrows():
        security_level = _normalize_cell(row.get("安全等级"))
        if not security_level:
            continue

        level_rules[security_level] = {
            "security_level": security_level,
            "level_name": _normalize_cell(row.get("等级名称")),
            "sharing_policy": _normalize_cell(row.get("共享属性")),
            "open_policy": _normalize_cell(row.get("开放属性")),
        }

    return level_rules


def _score_rule(source_text, rule):
    score = 0

    for term in rule.get("negative_terms", []):
        if term in source_text:
            score -= 4

    for term in rule.get("match_terms", []):
        value = term["value"]
        if value not in source_text:
            continue

        score += term["score"]

    return score


def _score_rules(source_text, rules):
    scored_rules = [
        (_score_rule(source_text, rule), rule)
        for rule in rules
    ]
    scored_rules.sort(
        key=lambda item: (
            item[0],
            len(item[1].get("match_terms", [])),
            len(item[1]["classification_description"]),
            item[1]["classification_path"],
        ),
        reverse=True,
    )
    return scored_rules


def _should_enrich_with_llm_profile(
    column_info,
    source_text,
    scored_candidates,
    limit,
):
    mode = _match_profile_mode()
    if mode == "off":
        return False

    if mode == "always":
        return bool(scored_candidates)

    if not scored_candidates:
        return False

    narrow_candidates = [
        (score, rule) for score, rule in scored_candidates
        if score >= MIN_CANDIDATE_SCORE
    ][:limit]
    if len(narrow_candidates) <= 2:
        return False

    top_score, top_rule = scored_candidates[0]
    second_score = scored_candidates[1][0] if len(scored_candidates) > 1 else 0
    direct_match_length = _direct_literal_match_length(column_info, top_rule)
    is_ambiguous_column = _is_ambiguous_column(column_info)

    if is_ambiguous_column and second_score >= top_score - CLOSE_SCORE_GAP:
        return True

    if (
        direct_match_length >= CLEAR_DIRECT_MATCH_LENGTH
        and (
            not is_ambiguous_column
            or direct_match_length >= CLEAR_STRONG_DIRECT_MATCH_LENGTH
        )
    ):
        return False

    if (
        top_score >= second_score + CLEAR_SCORE_GAP
        and _has_high_quality_term_match(source_text, top_rule)
        and not is_ambiguous_column
    ):
        return False

    return True


def _with_candidate_score(rule, score, rank):
    rule["program_match_score"] = score
    rule["candidate_rank"] = rank
    return rule


def _match_profile_mode():
    if os.getenv("ENABLE_LLM_MATCH_PROFILE", "1").lower() in {"0", "false", "no", "off"}:
        return "off"

    mode = os.getenv("LLM_MATCH_PROFILE_MODE", "auto").strip().lower()
    if mode not in MATCH_PROFILE_MODES:
        return "auto"

    return mode


def _has_high_quality_term_match(source_text, rule):
    for term in rule.get("match_terms", []):
        value = term["value"]
        if value not in source_text:
            continue

        if term["score"] >= 6:
            return True

        if _has_strong_token(value):
            return True

    return False


def _direct_literal_match_length(column_info, rule):
    column_text = _normalize_for_match(
        " ".join(
            str(column_info.get(key, ""))
            for key in ("table_name", "column_name", "column_description")
        )
    )
    rule_text = _normalize_for_match(
        " ".join(
            [
                rule.get("classification_path", ""),
                rule.get("classification_description", ""),
            ]
        )
    )

    return _longest_common_token_length(column_text, rule_text)


def _is_ambiguous_column(column_info):
    values = [
        str(column_info.get("column_name", "")),
        str(column_info.get("column_description", "")),
    ]
    tokens = []
    for value in values:
        tokens.extend(_extract_terms(value))
        tokens.extend(_literal_match_tokens(_normalize_for_match(value)))

    return any(token in AMBIGUOUS_FIELD_TOKENS for token in tokens)


def _is_low_information_generic_field(column_info):
    column_tokens = _field_tokens(column_info.get("column_name", ""))
    description_tokens = _field_tokens(column_info.get("column_description", ""))
    table_tokens = _field_tokens(column_info.get("table_name", ""))

    if not column_tokens:
        return False

    if not all(token in LOW_INFORMATION_FIELD_TOKENS for token in column_tokens):
        return False

    if description_tokens and not all(
        token in LOW_INFORMATION_FIELD_TOKENS
        for token in description_tokens
    ):
        return False

    return not table_tokens or all(token in GENERIC_TABLE_TOKENS for token in table_tokens)


def _field_tokens(value):
    tokens = []
    normalized_value = _normalize_for_match(value)
    tokens.extend(_extract_terms(value))
    tokens.extend(_literal_match_tokens(normalized_value))
    return [token for token in dict.fromkeys(tokens) if token]


def _longest_common_token_length(left, right):
    left_tokens = _literal_match_tokens(left)
    right_tokens = _literal_match_tokens(right)
    longest = 0

    for left_token in left_tokens:
        for right_token in right_tokens:
            longest = max(longest, _longest_common_substring_length(left_token, right_token))
            if longest >= CLEAR_STRONG_DIRECT_MATCH_LENGTH:
                return longest

    return longest


def _literal_match_tokens(value):
    return re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", value)


def _longest_common_substring_length(left, right):
    if not left or not right:
        return 0

    previous = [0] * (len(right) + 1)
    longest = 0
    for left_index in range(1, len(left) + 1):
        current = [0] * (len(right) + 1)
        for right_index in range(1, len(right) + 1):
            if left[left_index - 1] != right[right_index - 1]:
                continue

            current[right_index] = previous[right_index - 1] + 1
            longest = max(longest, current[right_index])

        previous = current

    return longest


def _has_strong_token(value):
    if re.fullmatch(r"[a-zA-Z0-9_]+", value):
        return len(value) >= 4

    return len(value) >= 3


def _enrich_candidate_rules(column_info, candidate_rules):
    try:
        from llm_match_profile import enrich_candidate_rules_for_column
    except ImportError:
        return {
            "source": "import_error",
            "updated_rules": 0,
        }

    try:
        return enrich_candidate_rules_for_column(column_info, candidate_rules)
    except Exception as exc:
        return {
            "source": "error",
            "updated_rules": 0,
            "error": str(exc),
        }


def _match_profile_status():
    try:
        from llm_match_profile import get_match_profile_status
    except ImportError:
        return {
            "enabled": False,
            "source": "import_error",
            "updated_rules": 0,
        }

    return get_match_profile_status()


def _build_column_search_text(column_info):
    values = []
    for key in [
        "table_name",
        "column_name",
        "column_type",
        "column_description",
        "remarks",
    ]:
        value = column_info.get(key)
        if value:
            values.append(value)

    return _normalize_for_match(" ".join(str(value) for value in values))


def _is_low_semantic_technical_field(column_info):
    column_name = _normalize_for_match(column_info.get("column_name", ""))
    description = _normalize_for_match(column_info.get("column_description", ""))
    technical_names = {
        "created_at",
        "create_time",
        "created_time",
        "updated_at",
        "update_time",
        "updated_time",
        "deleted_at",
        "delete_time",
    }
    technical_descriptions = {
        "记录创建时间",
        "创建时间",
        "记录更新时间",
        "更新时间",
        "删除时间",
    }

    if column_name not in technical_names:
        return False

    return not description or description in technical_descriptions


def _build_rule_match_terms(classification_parts, description):
    terms = {}
    last_part_index = len(classification_parts) - 1

    for index, part in enumerate(classification_parts):
        base_score = 6 if index == last_part_index else 3
        _add_match_term(terms, part, base_score)
        for token in _extract_terms(part):
            _add_match_term(terms, token, min(base_score, 3))

    for token in _extract_terms(description):
        _add_match_term(terms, token, 2)

    return [
        {"value": value, "score": score}
        for value, score in sorted(
            terms.items(),
            key=lambda item: (item[1], len(item[0]), item[0]),
            reverse=True,
        )
    ]


def _prune_common_match_terms(rules):
    term_counts = {}
    for rule in rules:
        for value in {term["value"] for term in rule.get("match_terms", [])}:
            term_counts[value] = term_counts.get(value, 0) + 1

    max_common_count = max(5, len(rules) // 20)
    for rule in rules:
        pruned_terms = []
        for term in rule.get("match_terms", []):
            if _is_context_fragment(term["value"]):
                continue

            if (
                term["score"] < 6
                and term_counts.get(term["value"], 0) > max_common_count
            ):
                term = {**term, "score": 1}

            pruned_terms.append(term)

        rule["match_terms"] = pruned_terms


def _add_match_term(terms, value, score):
    normalized_value = _normalize_for_match(value)
    if not _is_useful_match_term(normalized_value):
        return

    terms[normalized_value] = max(terms.get(normalized_value, 0), score)


def _extract_terms(value):
    normalized_value = _normalize_cell(value).lower()
    chunks = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", normalized_value)
    terms = []

    for chunk in chunks:
        if re.fullmatch(r"[a-zA-Z0-9_]+", chunk):
            terms.extend(_split_ascii_terms(chunk))
            continue

        terms.extend(_split_chinese_terms(chunk))

    return terms


def _split_ascii_terms(value):
    ascii_tokens = [
        token for token in re.split(r"[_\W]+", value)
        if _is_useful_match_term(token)
    ]
    return ascii_tokens


def _split_chinese_terms(value):
    delimiters = (
        "包括",
        "包含",
        "用于",
        "涉及",
        "相关",
        "以及",
        "或者",
        "及",
        "或",
        "和",
        "与",
        "等",
        "的",
    )
    pattern = "|".join(re.escape(delimiter) for delimiter in delimiters)
    parts = re.split(pattern, value)
    terms = []
    for part in parts:
        if not _is_useful_match_term(part):
            continue

        terms.append(part)
        terms.extend(_build_chinese_term_variants(part))

    return list(dict.fromkeys(terms))


def _build_chinese_term_variants(value):
    variants = []

    for suffix in ("信息", "数据", "记录", "内容", "管理"):
        if value.endswith(suffix) and len(value) > len(suffix) + 1:
            variants.append(value[: -len(suffix)])

    if len(value) >= 4:
        variants.append(value[:4])
        variants.append(value[:2])

    return [
        variant for variant in variants
        if _is_useful_match_term(variant)
    ]


def _is_useful_match_term(value):
    if not value or value in GENERIC_MATCH_TERMS:
        return False

    if re.fullmatch(r"[a-zA-Z0-9_]+", value):
        return len(value) >= 2

    return len(value) >= 2


def _is_context_fragment(value):
    return value.endswith(("中", "内", "过程中"))


def _normalize_for_match(value):
    value = _normalize_cell(value).lower()
    return re.sub(r"\s+", "", value)


def _normalize_cell(value):
    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    return str(value).strip()
