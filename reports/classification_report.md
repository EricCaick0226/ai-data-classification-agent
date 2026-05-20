# Column 分类分级报告

## 汇总

- Total columns: 6
- Classified columns: 5
- Review required columns: 1

## 等级统计

| Security Level | Count |
|---|---:|
| 3级 | 3 |
| 4级 | 2 |

## 需要人工复核

| Table | Column | Reason | Candidate Paths |
|---|---|---|---|
| medical_settlement | created_at | LLM confidence is below threshold. | 主题资源 / 电子健康档案数据库 / 儿童保健 / 5岁以下儿童死亡报告 |

## Column 分类分级明细

| Table | Column | Type | Description | Classification Path | Security Level | Level Name | Sharing Policy | Open Policy | Basis | Confidence | Review Required |
|---|---|---|---|---|---|---|---|---|---|---:|---|
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | patient_name 是患者身份识别的基本字段，用于医疗服务中的身份确认，符合‘患者信息’定义中‘身份识别、基本资料’和‘确保身份确认和沟通’的核心语义，且不涉及病历、诊断等敏感内容，故不属4级敏感信息。 | 0.98 | False |
| patient | id_card_no | varchar | 患者身份证件号码 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 身份证件号码属于患者身份识别类基本资料，用于身份确认，符合'患者信息'定义；虽具敏感性，但未达到病历、诊断等高度私密程度，故不适用4级敏感信息分类 | 0.95 | False |
| patient | diagnosis_result | text | 患者诊断结果 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | diagnosis_result 字段明确表示患者诊断结果，属于病历类高度私密数据，符合候选规则中'患者敏感信息'定义 | 0.98 | False |
| patient | treatment_plan | text | 患者治疗方案 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | treatment_plan（治疗方案）属于患者高度私密的医疗数据，直接关联诊疗决策与健康状况，符合‘患者敏感信息’定义中‘诊断结果、治疗方案等高度私密数据’的描述。 | 0.98 | False |
| medical_settlement | insurance_amount | decimal | 医保结算金额 | 业务资源 / 医疗服务(医院) / 医疗管理 / 医保接口管理 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为insurance_amount，描述为'医保结算金额'，直接关联医保结算业务，属于医保接口管理范畴 | 0.95 | False |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
