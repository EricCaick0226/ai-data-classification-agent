# src/rules.py

FIELD_RULES = [
    {
        "keywords": ["password", "passwd", "pwd"],
        "category": "Sensitive / 身份认证数据",
        "risk_level": "Critical",
        "reason": "字段名可能表示密码或登录凭证，泄露后可能导致账号被盗。",
        "recommendation": "必须严格保护，不能明文存储或公开展示。",
        "needs_review": False,
    },
    {
        "keywords": ["id_card", "passport", "ssn"],
        "category": "Sensitive / 身份识别数据",
        "risk_level": "Critical",
        "reason": "字段名可能表示身份证、护照或社会安全号码等强身份识别信息。",
        "recommendation": "应加密存储，限制访问，并避免在报告或导出文件中直接显示。",
        "needs_review": False,
    },
    {
        "keywords": ["email", "mail"],
        "category": "PII / 联系方式数据",
        "risk_level": "Medium",
        "reason": "字段名可能表示邮箱地址，可以识别或联系到个人。",
        "recommendation": "应避免公开展示，导出或共享时需要注意保护。",
        "needs_review": False,
    },
    {
        "keywords": ["phone", "mobile", "tel"],
        "category": "PII / 联系方式数据",
        "risk_level": "Medium",
        "reason": "字段名可能表示电话号码或手机号码，可以联系到个人。",
        "recommendation": "应避免公开展示，必要时进行脱敏处理。",
        "needs_review": False,
    },
    {
        "keywords": ["username"],
        "category": "PII / 用户标识数据",
        "risk_level": "Medium",
        "reason": "字段名 username 可能表示用户账号名，能够间接识别用户。",
        "recommendation": "应根据业务场景判断是否需要脱敏或限制展示。",
        "needs_review": True,
    },
    {
        "keywords": ["user_id"],
        "category": "PII / 用户标识数据",
        "risk_level": "Medium",
        "reason": "字段名 user_id 可能是用户唯一编号，可能与个人身份或行为记录关联。",
        "recommendation": "应结合样例值和业务含义判断是否属于敏感标识符。",
        "needs_review": True,
    },
    {
        "keywords": ["name"],
        "category": "PII / 个人信息",
        "risk_level": "Medium",
        "reason": "字段名包含 name，可能表示个人姓名，也可能表示商品名、项目名等非个人信息。",
        "recommendation": "应结合样例值判断是否为真实个人姓名，必要时进行脱敏。",
        "needs_review": True,
    },
    {
        "keywords": ["address", "location"],
        "category": "Location / 位置或地址数据",
        "risk_level": "High",
        "reason": "字段名可能表示地址、位置或地理信息，具体风险取决于精确程度。",
        "recommendation": "需要查看样例值判断是城市、地址、GPS 坐标还是实时位置。",
        "needs_review": True,
    },
    {
        "keywords": ["birth_date", "birthday", "date_of_birth", "dob"],
        "category": "PII / 出生日期",
        "risk_level": "High",
        "reason": "字段名可能表示出生日期，可用于身份识别或身份验证。",
        "recommendation": "应谨慎处理，必要时只保留年份或年龄段。",
        "needs_review": True,
    },
    {
        "keywords": ["salary", "income", "wage"],
        "category": "Confidential / 财务或薪酬数据",
        "risk_level": "High",
        "reason": "字段名可能表示薪资、收入或工资，属于敏感财务信息。",
        "recommendation": "应限制访问，避免在公开报告中展示个人级别薪酬数据。",
        "needs_review": False,
    },
    {
        "keywords": ["login_time", "last_login"],
        "category": "Behavioral / 行为数据",
        "risk_level": "Medium",
        "reason": "字段名可能表示用户登录时间，属于行为或活动记录。",
        "recommendation": "应结合具体使用场景判断是否涉及用户行为追踪。",
        "needs_review": True,
    },
    {
        "keywords": ["device_id", "device"],
        "category": "Device / 设备数据",
        "risk_level": "Medium",
        "reason": "字段名可能表示设备编号或设备信息，可能与用户行为或身份关联。",
        "recommendation": "应检查是否为唯一设备标识符，必要时进行脱敏。",
        "needs_review": True,
    },
    {
        "keywords": ["created_at", "updated_at"],
        "category": "Internal / 系统时间字段",
        "risk_level": "Low",
        "reason": "字段名表示创建或更新时间，通常是系统内部时间记录。",
        "recommendation": "一般可以保留，但仍需注意是否与敏感事件关联。",
        "needs_review": False,
    },
    {
        "keywords": ["favorite_color", "preference"],
        "category": "Public / 普通偏好数据",
        "risk_level": "Low",
        "reason": "字段名可能表示普通偏好信息，通常敏感性较低。",
        "recommendation": "一般风险较低，但仍需结合具体内容判断。",
        "needs_review": False,
    },
    {
        "keywords": ["notes", "note", "comment"],
        "category": "Unknown / 自由文本字段",
        "risk_level": "Unknown",
        "reason": "字段名表示自由文本内容，无法仅凭字段名判断是否包含敏感信息。",
        "recommendation": "必须查看样例值或进行人工复核。",
        "needs_review": True,
    },
]


def classify_field(field_name):
    normalized_name = field_name.lower()

    for rule in FIELD_RULES:
        for keyword in rule["keywords"]:
            if keyword in normalized_name:
                return {
                    "field_name": field_name,
                    "category": rule["category"],
                    "risk_level": rule["risk_level"],
                    "reason": rule["reason"],
                    "recommendation": rule["recommendation"],
                    "needs_review": rule["needs_review"],
                }

    return {
        "field_name": field_name,
        "category": "Unknown / 未知字段",
        "risk_level": "Unknown",
        "reason": "没有匹配到已知关键词，无法仅凭字段名判断数据类型。",
        "recommendation": "需要查看样例值或进行人工复核。",
        "needs_review": True,
    }


if __name__ == "__main__":
    test_fields = [
        "email",
        "phone_number",
        "password",
        "id_card",
        "ssn",
        "name",
        "username",
        "user_id",
        "address",
        "birth_date",
        "created_at",
        "updated_at",
        "notes",
        "comment",
        "salary",
        "favorite_color",
        "last_login_time",
        "device_id",
        "user_location",
        "random_note",
        "random_field",
    ]

    for field in test_fields:
        result = classify_field(field)

        print("字段名:", result["field_name"])
        print("分类:", result["category"])
        print("等级:", result["risk_level"])
        print("原因:", result["reason"])
        print("建议:", result["recommendation"])
        print("是否需要人工复核:", result["needs_review"])
        print("-" * 50)