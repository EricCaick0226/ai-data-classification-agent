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
MIN_CANDIDATE_SCORE = 2

GENERIC_MATCH_TERMS = {
    "患者",
    "信息",
    "数据",
    "记录",
    "时间",
    "管理",
    "服务",
    "医疗",
    "医疗服务",
    "系统",
    "业务",
    "内容",
    "结果",
    "编号",
    "名称",
    "类型",
}

TERM_WEIGHTS = {
    "身份证": 8,
    "身份证件": 8,
    "证件号码": 8,
    "患者信息": 5,
    "患者敏感信息": 8,
    "高度私密": 5,
    "身份识别": 5,
    "身份确认": 5,
    "唯一标识": 4,
    "基本资料": 4,
    "手机号": 7,
    "联系电话": 7,
    "联系方式": 5,
    "居住地址": 7,
    "地址": 6,
    "姓名": 5,
    "监护人": 5,
    "紧急联系人": 5,
    "出生日期": 5,
    "就诊": 4,
    "科室": 4,
    "诊断结果": 10,
    "诊断": 7,
    "治疗方案": 10,
    "病历": 8,
    "主诉": 7,
    "处方": 8,
    "医嘱": 8,
    "用药": 6,
    "检验结果": 9,
    "检验": 6,
    "检查": 5,
    "影像": 7,
    "手术": 8,
    "输血": 8,
    "过敏史": 8,
    "护理记录": 7,
    "医保": 6,
    "结算": 5,
    "费用": 5,
    "金额": 4,
    "支付": 4,
    "公共卫生": 6,
    "随访": 6,
    "慢病": 6,
    "血压": 7,
    "血糖": 7,
    "心理健康": 8,
    "医务人员": 6,
    "医生": 5,
    "执业资格": 7,
    "绩效": 6,
    "日志": 6,
    "审计": 6,
    "操作": 4,
    "ip": 6,
    "设备": 4,
    "互联网": 6,
    "问诊": 8,
    "远程会诊": 8,
    "药品配送": 7,
    "科研": 6,
    "基因": 10,
    "临床试验": 8,
    "生物样本": 8,
}

SOURCE_SYNONYMS = {
    "id_card": ["身份证", "身份证件", "证件号码", "身份识别", "身份确认", "基本资料", "患者信息"],
    "idcard": ["身份证", "身份证件", "证件号码", "身份识别", "身份确认"],
    "身份证": ["身份识别", "身份确认", "基本资料", "患者信息"],
    "身份证件": ["身份识别", "身份确认", "基本资料", "患者信息"],
    "card_no": ["证件号码", "编号"],
    "patient_id": ["患者信息", "身份识别", "唯一标识"],
    "patient_name": ["姓名", "身份识别", "身份确认", "基本资料", "患者信息"],
    "guardian_name": ["监护人", "姓名", "基本资料", "患者信息"],
    "emergency_contact": ["紧急联系人", "联系方式", "基本资料", "患者信息"],
    "phone": ["手机号", "联系电话", "联系方式", "基本资料"],
    "mobile": ["手机号", "联系电话"],
    "address": ["地址", "居住地址", "联系方式", "基本资料", "患者信息"],
    "birth": ["出生日期", "基本资料", "患者信息"],
    "doctor_name": ["医生", "医务人员", "姓名"],
    "staff_name": ["医务人员", "姓名"],
    "department": ["科室"],
    "diagnosis": ["诊断", "诊断结果", "病历", "患者敏感信息", "高度私密"],
    "treatment_plan": ["治疗方案", "患者敏感信息", "高度私密"],
    "chief_complaint": ["主诉", "病历", "患者敏感信息", "高度私密"],
    "visit": ["就诊"],
    "prescription": ["处方"],
    "medical_order": ["医嘱"],
    "drug": ["药品", "用药"],
    "dosage": ["用药剂量"],
    "lab_result": ["检验结果"],
    "abnormal": ["异常"],
    "imaging": ["影像", "影像检查"],
    "surgery": ["手术"],
    "transfusion": ["输血"],
    "allergy": ["过敏史"],
    "nursing": ["护理记录"],
    "insurance": ["医保"],
    "settlement": ["结算"],
    "amount": ["金额", "费用", "支付"],
    "followup": ["随访"],
    "blood_pressure": ["血压"],
    "blood_glucose": ["血糖"],
    "mental_health": ["心理健康"],
    "staff": ["医务人员"],
    "doctor": ["医生", "医务人员"],
    "certificate": ["执业资格", "证书"],
    "performance": ["绩效"],
    "audit": ["审计", "日志"],
    "log": ["日志"],
    "operator": ["操作人"],
    "operation": ["操作"],
    "ip_address": ["ip", "访问地址"],
    "device": ["设备"],
    "consultation": ["问诊"],
    "remote_diagnosis": ["远程会诊", "诊断"],
    "payment": ["支付"],
    "research": ["科研"],
    "gene": ["基因"],
    "trial": ["临床试验"],
    "sample": ["生物样本", "样本"],
}


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
        if _is_low_semantic_technical_field(column_info):
            return []

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

        return [
            rule for score, rule in scored_rules
            if score >= MIN_CANDIDATE_SCORE
        ][:limit]


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

        if normalized_value in source_text and normalized_value not in GENERIC_MATCH_TERMS:
            score += 5

        for token in _tokenize(normalized_value):
            if token and token in source_text and token not in GENERIC_MATCH_TERMS:
                score += TERM_WEIGHTS.get(token, 1)

    return score


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

    raw_text = " ".join(str(value) for value in values)
    normalized_text = _normalize_for_match(raw_text)
    expansions = []
    for trigger, synonyms in SOURCE_SYNONYMS.items():
        if trigger in normalized_text:
            expansions.extend(synonyms)

    return _normalize_for_match(" ".join([raw_text, *expansions]))


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


def _tokenize(value):
    ascii_tokens = [
        token for token in re.findall(r"[a-zA-Z0-9]+", value)
        if token not in GENERIC_MATCH_TERMS
    ]
    chinese_terms = [
        term for term in TERM_WEIGHTS
        if term in value and term not in GENERIC_MATCH_TERMS
    ]
    return ascii_tokens + chinese_terms


def _normalize_for_match(value):
    value = _normalize_cell(value).lower()
    return re.sub(r"\s+", "", value)


def _normalize_cell(value):
    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    return str(value).strip()
