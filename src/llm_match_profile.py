import json
import os
import re

from llm_metrics import increment_metric


API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://mc-llm-api.dev.mchz.com.cn/v1")
MODEL = os.getenv("MODEL", "qwen-plus")
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "30"))
PROMPT_VERSION = "llm-match-profile-v1"
MATCH_PROFILE_MODES = {"off", "always", "auto"}

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
            "mode": _match_profile_mode(),
            "updated_rules": 0,
        }

    if not API_KEY:
        return {
            "enabled": True,
            "source": "missing_api_key",
            "mode": _match_profile_mode(),
            "updated_rules": 0,
        }

    return {
        "enabled": True,
        "source": "candidate_level",
        "mode": _match_profile_mode(),
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
    if _match_profile_mode() == "off":
        return False

    value = os.getenv("ENABLE_LLM_MATCH_PROFILE", "1")
    return value.lower() not in {"0", "false", "no", "off"}


def _match_profile_mode():
    mode = os.getenv("LLM_MATCH_PROFILE_MODE", "auto").strip().lower()
    if mode not in MATCH_PROFILE_MODES:
        return "auto"

    return mode


def _generate_column_profile(column_info, candidate_rules):
    client = _build_client()
    increment_metric("match_profile_llm_calls")
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
        "你负责为当前数据库字段生成可验证的候选匹配线索。"
        "输入里已有程序宽召回得到的候选标准分类。"
        "你的任务不是最终分类、不是候选重排，也不是为每个候选寻找理由。"
        "你只能为与当前字段有直接证据关系的候选生成短 match profile。"
        "只允许为输入候选中的 classification_path 生成 match profile，不能创造新路径。"
        "positive terms 必须能被 table_name、column_name、column_description 或候选规则文本直接支持。"
        "如果字段元数据不支持候选路径中的具体上下文，不要生成 positive terms；可以生成 negative_terms。"
        "避免输出泛词，例如'信息''数据''记录''管理''服务''系统''业务'。"
        "只返回一个 JSON 对象，不要输出 Markdown 或解释性前后缀。"
    )
    user_prompt = {
        "column": column_info,
        "candidate_rules": candidate_payload,
        "task": (
            "只为少数有直接证据的候选生成 profile。"
            "如果候选只是因为宽泛关键词被召回，或者候选路径比字段上下文更具体但字段没有支持该上下文，不要返回该候选的 positive profile。"
            "column_name_hints 只能包含当前字段名、当前字段名的合理拆分或直接等价表达。"
            "negative_terms 应描述候选路径中存在但当前字段元数据没有体现的具体上下文。"
        ),
        "required_output_schema": {
            "profiles": [
                {
                    "classification_path": "必须与 candidate_rules 中某条完全一致",
                    "positive_terms": ["当前字段与该候选之间可直接验证的匹配词，最多 4 个"],
                    "column_name_hints": ["当前字段名或直接等价字段名表达，最多 4 个"],
                    "negative_terms": ["候选路径中当前字段元数据不支持的具体上下文，最多 3 个"],
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
                "positive_terms": _clean_term_list(
                    profile.get("positive_terms", []),
                    4,
                ),
                "core_terms": _clean_term_list(profile.get("core_terms", []), 4),
                "synonyms": _clean_term_list(profile.get("synonyms", []), 4),
                "column_name_hints": _clean_term_list(
                    profile.get("column_name_hints", []),
                    4,
                ),
                "negative_terms": _clean_term_list(profile.get("negative_terms", []), 3),
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

        rule["llm_match_profile"] = {
            "positive_terms": profile.get("positive_terms", []),
            "core_terms": profile.get("core_terms", []),
            "synonyms": profile.get("synonyms", []),
            "column_name_hints": profile.get("column_name_hints", []),
            "negative_terms": profile.get("negative_terms", []),
        }

        before_count = len(rule.get("match_terms", []))
        for term in profile.get("positive_terms", []):
            _merge_match_term(rule, term, 5)
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
