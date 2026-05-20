# Column 分类分级报告

## 汇总

- Total columns: 6
- Classified columns: 0
- Review required columns: 6

## 需要人工复核

| Table | Column | Reason | Candidate Paths |
|---|---|---|---|
| patient | patient_name | DASHSCOPE_API_KEY is not set. | 基础资源 / 服务范围与对象 / 患者 / 患者信息; 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息; 业务资源 / 医疗服务(医院) / 医疗管理 / 就诊卡管理; 业务资源 / 医疗服务(医院) / 临床服务 / 门诊合理用药; 业务资源 / 医疗服务(医院) / 临床服务 / 住院病历书写 |
| patient | id_card_no | DASHSCOPE_API_KEY is not set. | 基础资源 / 服务范围与对象 / 患者 / 患者信息; 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 |
| patient | diagnosis_result | DASHSCOPE_API_KEY is not set. | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息; 基础资源 / 服务范围与对象 / 患者 / 患者信息 |
| patient | treatment_plan | DASHSCOPE_API_KEY is not set. | 基础资源 / 服务范围与对象 / 患者 / 患者信息; 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息; 业务资源 / 医疗服务 (基层) / 基本医疗服务 / 住院管理 |
| medical_settlement | insurance_amount | DASHSCOPE_API_KEY is not set. | 业务资源 / 医疗服务(医院) / 医疗管理 / 医保接口管理 |
| medical_settlement | created_at | DASHSCOPE_API_KEY is not set. | 主题资源 / 电子健康档案数据库 / 儿童保健 / 5岁以下儿童死亡报告 |

## Column 分类分级明细

| Table | Column | Type | Description | Classification Path | Security Level | Level Name | Sharing Policy | Open Policy | Basis | Confidence | Review Required |
|---|---|---|---|---|---|---|---|---|---|---:|---|
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
| patient | id_card_no | varchar | 患者身份证件号码 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
| patient | diagnosis_result | text | 患者诊断结果 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
| patient | treatment_plan | text | 患者治疗方案 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
| medical_settlement | insurance_amount | decimal | 医保结算金额 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
