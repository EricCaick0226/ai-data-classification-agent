import json
import os
import re

from llm_metrics import increment_metric


API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://mc-llm-api.dev.mchz.com.cn/v1")
MODEL = os.getenv("MODEL", "qwen-plus")
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "30"))


def classify_column_with_llm(column_info, candidate_rules, level_rules):
    if not API_KEY:
        return {
            "status": "error",
            "error": "DASHSCOPE_API_KEY is not set.",
        }

    client = _build_client()
    messages = _build_messages(column_info, candidate_rules, level_rules)

    try:
        increment_metric("classifier_llm_calls")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
        )
    except Exception as exc:
        return {
            "status": "error",
            "error": f"LLM request failed: {exc}",
        }

    content = response.choices[0].message.content or ""
    parsed = _parse_json_object(content)
    if parsed is None:
        return {
            "status": "error",
            "error": "LLM response is not valid JSON.",
            "raw_response": content,
        }

    parsed["status"] = "success"
    parsed["raw_response"] = content
    return parsed


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


def _build_messages(column_info, candidate_rules, level_rules):
    candidate_payload = [
        {
            "candidate_rank": rule.get("candidate_rank"),
            "program_match_score": rule.get("program_match_score"),
            "classification_path": rule["classification_path"],
            "recommended_level": rule["recommended_level"],
            "classification_description": rule["classification_description"],
            "match_profile": rule.get("llm_match_profile", {}),
        }
        for rule in candidate_rules
    ]

    level_payload = list(level_rules.values())

    system_prompt = (
        "你是一个数据库字段分类分级 Agent。"
        "分类分级标准 Excel 是唯一权威来源。"
        "你只能从候选 classification_path 中选择最匹配的一条，不能创造新的分类路径或等级。"
        "请根据 table_name、column_name、column_type、column_description 判断 column 语义。"
        "候选规则中的 match_profile 是上一阶段 LLM 基于当前字段生成的匹配辅助信息，"
        "只用于理解字段与候选分类的语义关系，不能替代规则 Excel。"
        "candidate_rank 和 program_match_score 来自程序宽召回，分数越高、排名越靠前，"
        "表示字段文本与规则文本的字面匹配越强；当语义证据充分时，应优先考虑高排名候选。"
        "选择分类时必须同时匹配字段语义和分类路径上下文，"
        "不能只因为某个关键词命中就选择更具体的业务场景路径。"
        "如果某个具体候选的分类说明直接覆盖字段的核心语义，"
        "且不需要额外假设字段所属业务场景，则可以优先选择该具体候选。"
        "如果具体候选只是因为宽泛关键词命中，"
        "但字段元数据没有体现该候选路径中的具体场景，"
        "应选择语义更稳妥的上位或通用候选。"
        "只返回一个 JSON 对象，不要输出 Markdown 或解释性前后缀。"
    )

    user_prompt = {
        "column": column_info,
        "candidate_rules": candidate_payload,
        "level_rules": level_payload,
        "required_output_schema": {
            "classification_path": "必须来自 candidate_rules",
            "security_level": "优先使用候选规则 recommended_level",
            "basis": "简短说明匹配依据",
            "confidence": "0 到 1 的数字",
            "review_required": "布尔值",
        },
    }

    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps(user_prompt, ensure_ascii=False),
        },
    ]


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
