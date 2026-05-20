import json
import os
import re


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


def classify_columns_with_llm(batch_items, level_rules):
    if not API_KEY:
        return {
            "status": "error",
            "error": "DASHSCOPE_API_KEY is not set.",
        }

    client = _build_client()
    messages = _build_batch_messages(batch_items, level_rules)

    try:
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

    results = parsed.get("results") if isinstance(parsed, dict) else None
    if not isinstance(results, list):
        return {
            "status": "error",
            "error": "LLM batch response must contain a results list.",
            "raw_response": content,
        }

    return {
        "status": "success",
        "results": results,
        "raw_response": content,
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


def _build_messages(column_info, candidate_rules, level_rules):
    candidate_payload = [
        {
            "classification_path": rule["classification_path"],
            "recommended_level": rule["recommended_level"],
            "classification_description": rule["classification_description"],
        }
        for rule in candidate_rules
    ]

    level_payload = list(level_rules.values())

    system_prompt = (
        "你是一个数据库字段分类分级 Agent。"
        "分类分级标准 Excel 是唯一权威来源。"
        "你只能从候选 classification_path 中选择最匹配的一条，不能创造新的分类路径或等级。"
        "请根据 table_name、column_name、column_type、column_description 判断 column 语义。"
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


def _build_batch_messages(batch_items, level_rules):
    item_payload = []
    for item in batch_items:
        item_payload.append(
            {
                "column_index": item["column_index"],
                "column": item["column_info"],
                "candidate_rules": [
                    {
                        "classification_path": rule["classification_path"],
                        "recommended_level": rule["recommended_level"],
                        "classification_description": rule["classification_description"],
                    }
                    for rule in item["candidate_rules"]
                ],
            }
        )

    system_prompt = (
        "你是一个数据库字段分类分级 Agent。"
        "分类分级标准 Excel 是唯一权威来源。"
        "你必须分别处理每个 item，只能从该 item 自己的 candidate_rules 中选择 classification_path。"
        "不能把一个 item 的候选分类路径用于另一个 item。"
        "必须使用原始 column_index 返回结果，不能遗漏、重复或重排含义。"
        "只返回一个 JSON 对象，不要输出 Markdown 或解释性前后缀。"
    )

    user_prompt = {
        "items": item_payload,
        "level_rules": list(level_rules.values()),
        "required_output_schema": {
            "results": [
                {
                    "column_index": "必须等于输入 item 的 column_index",
                    "classification_path": "必须来自该 item 的 candidate_rules",
                    "security_level": "优先使用所选候选规则 recommended_level",
                    "basis": "简短说明匹配依据",
                    "confidence": "0 到 1 的数字",
                    "review_required": "布尔值",
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
