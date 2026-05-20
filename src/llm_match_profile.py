import json
import os
import re


API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://mc-llm-api.dev.mchz.com.cn/v1")
MODEL = os.getenv("MODEL", "qwen-plus")
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "30"))
PROMPT_VERSION = "llm-match-profile-v1"

GENERIC_PROFILE_TERMS = {
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
}


def get_match_profile_status():
    if not _is_enabled():
        return {
            "enabled": False,
            "source": "disabled",
            "updated_rules": 0,
        }

    if not API_KEY:
        return {
            "enabled": True,
            "source": "missing_api_key",
            "updated_rules": 0,
        }

    return {
        "enabled": True,
        "source": "candidate_level",
        "updated_rules": 0,
    }


def enrich_candidate_rules_for_column(column_info, candidate_rules):
    if not _is_enabled() or not API_KEY or not candidate_rules:
        return {
            "enabled": _is_enabled(),
            "source": "missing_api_key" if _is_enabled() and not API_KEY else "disabled",
            "updated_rules": 0,
        }

    profile_payload = _generate_column_profile(column_info, candidate_rules)
    updated_rules = _merge_profile_into_rules(candidate_rules, profile_payload)
    return {
        "enabled": True,
        "source": "candidate_level_llm",
        "updated_rules": updated_rules,
    }


def _is_enabled():
    value = os.getenv("ENABLE_LLM_MATCH_PROFILE", "1")
    return value.lower() not in {"0", "false", "no", "off"}


def _generate_column_profile(column_info, candidate_rules):
    client = _build_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=_build_column_messages(column_info, candidate_rules),
        temperature=0,
    )
    content = response.choices[0].message.content or ""
    parsed = _parse_json_object(content)
    if parsed is None:
        return {
            "prompt_version": PROMPT_VERSION,
            "model": MODEL,
            "profiles": [],
        }

    return {
        "prompt_version": PROMPT_VERSION,
        "model": MODEL,
        "profiles": _normalize_profiles(parsed.get("profiles", [])),
    }


def _build_client():
    try:
        import httpx
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI API dependencies are not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    base_url = BASE_URL.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    return OpenAI(
        api_key=API_KEY,
        base_url=base_url,
        http_client=httpx.Client(timeout=httpx.Timeout(TIMEOUT_SECONDS, connect=5)),
    )


def _build_column_messages(column_info, candidate_rules):
    candidate_payload = [
        {
            "classification_path": rule["classification_path"],
            "recommended_level": rule["recommended_level"],
            "classification_description": rule["classification_description"],
            "existing_match_terms": [
                term["value"] for term in rule.get("match_terms", [])[:10]
            ],
        }
        for rule in candidate_rules
    ]

    system_prompt = (
        "你负责为当前数据库字段生成候选召回辅助词。"
        "输入里已有程序宽召回得到的候选标准分类。"
        "你的任务不是最终分类，而是帮助程序判断这些候选中哪些更可能匹配当前字段。"
        "只允许为输入候选中的 classification_path 生成 match profile，不能创造新路径。"
        "生成的词将用于匹配 table_name.column_name、column_description。"
        "避免输出泛词，例如'信息''数据''记录''管理''服务''系统''业务'。"
        "只返回一个 JSON 对象，不要输出 Markdown 或解释性前后缀。"
    )
    user_prompt = {
        "column": column_info,
        "candidate_rules": candidate_payload,
        "task": (
            "针对当前 column，为每条确实相关的候选规则补充 match profile。"
            "优先生成数据库字段名中可能出现的英文、缩写、snake_case，以及字段描述中可能出现的中文同义表达。"
            "如果候选规则与当前字段明显无关，可以只返回 negative_terms 或不返回该候选。"
            "例如字段 diagnosis_result 与'诊断明细信息'相关时，应考虑 diagnosis、diagnosis_result、clinical_diagnosis、诊断结果、疾病诊断 等表达。"
        ),
        "required_output_schema": {
            "profiles": [
                {
                    "classification_path": "必须与 candidate_rules 中某条完全一致",
                    "core_terms": ["当前字段和该规则之间最关键的中文业务词，最多 6 个"],
                    "synonyms": ["当前字段描述中可能出现的中文同义表达，最多 6 个"],
                    "column_name_hints": ["当前字段名或相似字段名可能出现的英文/snake_case，最多 8 个"],
                    "negative_terms": ["当前字段容易误召回但不应匹配该规则的词，最多 4 个"],
                }
            ]
        },
    }

    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps(user_prompt, ensure_ascii=False),
        },
    ]


def _normalize_profiles(profiles):
    normalized_profiles = []
    for profile in profiles:
        classification_path = str(profile.get("classification_path", "")).strip()
        if not classification_path:
            continue

        normalized_profiles.append(
            {
                "classification_path": classification_path,
                "core_terms": _clean_term_list(profile.get("core_terms", []), 6),
                "synonyms": _clean_term_list(profile.get("synonyms", []), 6),
                "column_name_hints": _clean_term_list(
                    profile.get("column_name_hints", []),
                    8,
                ),
                "negative_terms": _clean_term_list(profile.get("negative_terms", []), 4),
            }
        )

    return normalized_profiles


def _clean_term_list(values, limit):
    if not isinstance(values, list):
        return []

    terms = []
    seen = set()
    for value in values:
        normalized_value = _normalize_for_match(value)
        if not _is_useful_profile_term(normalized_value):
            continue
        if normalized_value in seen:
            continue

        seen.add(normalized_value)
        terms.append(normalized_value)
        if len(terms) >= limit:
            break

    return terms


def _merge_profile_into_rules(rules, payload):
    profiles_by_path = {
        profile["classification_path"]: profile
        for profile in payload.get("profiles", [])
    }

    updated_rules = 0
    for rule in rules:
        profile = profiles_by_path.get(rule["classification_path"])
        if not profile:
            continue

        before_count = len(rule.get("match_terms", []))
        for term in profile.get("core_terms", []):
            _merge_match_term(rule, term, 5)
        for term in profile.get("synonyms", []):
            _merge_match_term(rule, term, 4)
        for term in profile.get("column_name_hints", []):
            _merge_match_term(rule, term, 5)

        negative_terms = [
            term for term in profile.get("negative_terms", [])
            if _is_useful_profile_term(term)
        ]
        if negative_terms:
            rule["negative_terms"] = sorted(set(negative_terms))

        if len(rule.get("match_terms", [])) > before_count or negative_terms:
            updated_rules += 1

    return updated_rules


def _merge_match_term(rule, value, score):
    normalized_value = _normalize_for_match(value)
    if not _is_useful_profile_term(normalized_value):
        return

    terms = {
        term["value"]: term["score"]
        for term in rule.get("match_terms", [])
    }
    terms[normalized_value] = max(terms.get(normalized_value, 0), score)
    rule["match_terms"] = [
        {"value": term_value, "score": term_score}
        for term_value, term_score in sorted(
            terms.items(),
            key=lambda item: (item[1], len(item[0]), item[0]),
            reverse=True,
        )
    ]


def _is_useful_profile_term(value):
    if not value or value in GENERIC_PROFILE_TERMS:
        return False

    if len(value) > 40:
        return False

    if re.fullmatch(r"[a-zA-Z0-9_]+", value):
        return len(value) >= 2

    return len(value) >= 2


def _parse_json_object(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _normalize_for_match(value):
    return re.sub(r"\s+", "", str(value or "").strip().lower())
