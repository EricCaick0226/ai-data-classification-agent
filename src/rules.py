from dataclasses import dataclass
import math
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


@dataclass
class RuleCatalog:
    classification_rules: list[dict]
    level_rules: dict[str, dict]

    def get_rule_by_path(self, classification_path):
        for rule in self.classification_rules:
            if rule["classification_path"] == classification_path:
                return rule
        return None

    def get_level_rule(self, security_level):
        return self.level_rules.get(str(security_level).strip())

    def get_candidate_rules(self, column_info, limit=12):
        scored_rules = []
        source_text = _build_column_search_text(column_info)

        for rule in self.classification_rules:
            score = _score_rule(source_text, rule)
            scored_rules.append((score, rule))

        scored_rules.sort(
            key=lambda item: (
                item[0],
                len(item[1]["classification_description"]),
                item[1]["classification_path"],
            ),
            reverse=True,
        )

        candidates = [rule for score, rule in scored_rules if score > 0][:limit]
        if candidates:
            return candidates

        return [rule for _, rule in scored_rules[:limit]]


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
    level_rules = _build_level_rules(level_df)

    if not classification_rules:
        raise ValueError("No classification rules found in the rule Excel file.")

    if not level_rules:
        raise ValueError("No level rules found in the rule Excel file.")

    return RuleCatalog(
        classification_rules=classification_rules,
        level_rules=level_rules,
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
            }
        )

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
    searchable_values = [
        rule["classification_path"],
        rule["classification_description"],
        *rule["classification_parts"],
    ]

    for value in searchable_values:
        normalized_value = _normalize_for_match(value)
        if not normalized_value:
            continue

        if normalized_value in source_text:
            score += 5

        for token in _tokenize(normalized_value):
            if token and token in source_text:
                score += 1

    return score


def _build_column_search_text(column_info):
    values = [
        column_info.get("table_name", ""),
        column_info.get("column_name", ""),
        column_info.get("column_type", ""),
        column_info.get("column_description", ""),
    ]
    return _normalize_for_match(" ".join(str(value) for value in values))


def _tokenize(value):
    ascii_tokens = re.findall(r"[a-zA-Z0-9]+", value)
    chinese_tokens = re.findall(r"[\u4e00-\u9fff]{2,}", value)
    return ascii_tokens + chinese_tokens


def _normalize_for_match(value):
    value = _normalize_cell(value).lower()
    return re.sub(r"\s+", "", value)


def _normalize_cell(value):
    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    return str(value).strip()
