# Data Classification Report

This report summarizes the classification and risk level of each field in the dataset.

## Summary

- Total fields: 16
- Fields needing manual review: 8
- High or Critical risk fields: 6

## Field Classification Details

| Field Name | Data Type | Missing Count | Category | Risk Level | Confidence | Reason | Recommendation | Needs Review |
|---|---|---|---|---|---|---|---|---|
| user_id | str | 0 | PII / 用户标识数据 | Medium | 0.6 | 字段名 user_id 可能是用户唯一编号，可能与个人身份或行为记录关联。 | 应结合样例值和业务含义判断是否属于敏感标识符。 | True 
| username | str | 0 | PII / 用户标识数据 | Medium | 0.6 | 字段名 username 可能表示用户账号名，能够间接识别用户。 | 应根据业务场景判断是否需要脱敏或限制展示。 | True 
| full_name | str | 0 | PII / 个人信息 | Medium | 0.6 | 字段名包含 name，可能表示个人姓名，也可能表示商品名、项目名等非个人信息。 | 应结合样例值判断是否为真实个人姓名，必要时进行脱敏。 | True 
| email | str | 0 | PII / 联系方式数据 | Medium | 0.75 | 字段名可能表示邮箱地址，可以识别或联系到个人。 | 应避免公开展示，导出或共享时需要注意保护。 | False 
| phone_number | str | 2 | PII / 联系方式数据 | Medium | 0.75 | 字段名可能表示电话号码或手机号码，可以联系到个人。 | 应避免公开展示，必要时进行脱敏处理。 | False 
| password | str | 0 | Sensitive / 身份认证数据 | Critical | 0.95 | 字段名可能表示密码或登录凭证，泄露后可能导致账号被盗。 | 必须严格保护，不能明文存储或公开展示。 | False 
| id_card | str | 0 | Sensitive / 身份识别数据 | Critical | 0.95 | 字段名可能表示身份证、护照或社会安全号码等强身份识别信息。 | 应加密存储，限制访问，并避免在报告或导出文件中直接显示。 | False 
| ssn | str | 0 | Sensitive / 身份识别数据 | Critical | 0.95 | 字段名可能表示身份证、护照或社会安全号码等强身份识别信息。 | 应加密存储，限制访问，并避免在报告或导出文件中直接显示。 | False 
| address | str | 2 | Location / 位置或地址数据 | High | 0.7 | 字段名可能表示地址、位置或地理信息，具体风险取决于精确程度。 | 需要查看样例值判断是城市、地址、GPS 坐标还是实时位置。 | True 
| birth_date | str | 0 | PII / 出生日期 | High | 0.7 | 字段名可能表示出生日期，可用于身份识别或身份验证。 | 应谨慎处理，必要时只保留年份或年龄段。 | True 
| user_location | str | 0 | Location / 位置或地址数据 | High | 0.7 | 字段名可能表示地址、位置或地理信息，具体风险取决于精确程度。 | 需要查看样例值判断是城市、地址、GPS 坐标还是实时位置。 | True 
| device_id | str | 0 | Device / 设备数据 | Medium | 0.6 | 字段名可能表示设备编号或设备信息，可能与用户行为或身份关联。 | 应检查是否为唯一设备标识符，必要时进行脱敏。 | True 
| favorite_color | str | 1 | Public / 普通偏好数据 | Low | 0.65 | 字段名可能表示普通偏好信息，通常敏感性较低。 | 一般风险较低，但仍需结合具体内容判断。 | False 
| notes | str | 1 | Unknown / 自由文本字段 | Unknown | 0.35 | 字段名表示自由文本内容，无法仅凭字段名判断是否包含敏感信息。 | 必须查看样例值或进行人工复核。 | True 
| created_at | str | 0 | Internal / 系统时间字段 | Low | 0.65 | 字段名表示创建或更新时间，通常是系统内部时间记录。 | 一般可以保留，但仍需注意是否与敏感事件关联。 | False 
| updated_at | str | 0 | Internal / 系统时间字段 | Low | 0.65 | 字段名表示创建或更新时间，通常是系统内部时间记录。 | 一般可以保留，但仍需注意是否与敏感事件关联。 | False 
