import json
import os
import re


API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://mc-llm-api.dev.mchz.com.cn/v1")
MODEL = os.getenv("MODEL", "qwen-plus")
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "30"))
PROMPT_VERSION = "llm-match-profile-v1"
DEFAULT_BATCH_SIZE = 8

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


def enrich_rules_with_llm_match_profile(excel_path, rules):
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

    profile_payload = _generate_profile(rules)

    updated_rules = _merge_profile_into_rules(rules, profile_payload)
    return {
        "enabled": True,
        "source": "llm",
        "updated_rules": updated_rules,
    }


def _is_enabled():
    value = os.getenv("ENABLE_LLM_MATCH_PROFILE", "1")
    return value.lower() not in {"0", "false", "no", "off"}


def _generate_profile(rules):
    selected_rules = _limited_rules(rules)
    batches = [
        selected_rules[index : index + DEFAULT_BATCH_SIZE]
        for index in range(0, len(selected_rules), DEFAULT_BATCH_SIZE)
    ]

    profiles = []
    client = _build_client()
    for batch in batches:
        response = client.chat.completions.create(
            model=MODEL,
            messages=_build_messages(batch),
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        parsed = _parse_json_object(content)
        if parsed is None:
            continue

        profiles.extend(_normalize_profiles(parsed.get("profiles", [])))

    return {
        "prompt_version": PROMPT_VERSION,
        "model": MODEL,
        "profiles": profiles,
    }


def _limited_rules(rules):
    limit = os.getenv("LLM_MATCH_PROFILE_LIMIT")
    if not limit:
        return rules

    try:
        limit_value = int(limit)
    except ValueError:
        return rules

    if limit_value <= 0:
        return rules

    return rules[:limit_value]


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


def _build_messages(rules):
    rule_payload = [
        {
            "classification_path": rule["classification_path"],
            "recommended_level": rule["recommended_level"],
            "classification_description": rule["classification_description"],
        }
        for rule in rules
    ]

    system_prompt = (
        "你负责为数据分类规则生成候选召回辅助词。"
        "这些词只用于帮助程序召回候选分类，不用于直接决定最终分类。"
        "不要创造新的 classification_path，不要输出 Markdown。"
        "避免'信息''数据''管理''服务'这类泛词。"
    )
    user_prompt = {
        "rules": rule_payload,
        "task": (
            "为每条规则生成更准确的 match profile。"
            "重点补充字段名可能出现的英文、拼音或 snake_case 表达。"
        ),
        "required_output_schema": {
            "profiles": [
                {
                    "classification_path": "必须与输入完全一致",
                    "core_terms": ["规则原文中的核心业务词，最多 6 个"],
                    "synonyms": ["常见中文同义表达，最多 6 个"],
                    "column_name_hints": ["常见英文字段名或 snake_case，最多 8 个"],
                    "negative_terms": ["容易误召回但不应匹配的词，最多 4 个"],
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
