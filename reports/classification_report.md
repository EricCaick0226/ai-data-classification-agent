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
| medical_settlement | created_at | LLM result is missing classification_path. |  |

## Column 分类分级明细

| Table | Column | Type | Description | Classification Path | Security Level | Level Name | Sharing Policy | Open Policy | Basis | Confidence | Review Required |
|---|---|---|---|---|---|---|---|---|---|---:|---|
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | column_name='patient_name'且column_description明确指向医疗服务中的身份确认，属于患者基本身份信息，与候选规则中'患者信息'定义完全一致；该路径层级（3级）低于'患者主索引'（4级），但语义更精准匹配通用患者身份字段而非唯一主索引场景。 | 0.95 | False |
| patient | id_card_no | varchar | 患者身份证件号码 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | id_card_no 是患者身份的唯一法定标识，属于患者基本信息的核心字段，直接关联患者主体，符合‘患者信息’分类定义中‘身份识别’和‘基本隐私保护’的描述。 | 0.95 | False |
| patient | diagnosis_result | text | 患者诊断结果 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | diagnosis_result 直接表征患者健康状况的核心私密信息，属于病历核心内容，符合‘患者敏感信息’定义中‘诊断结果’的明确列举，且需严格保密，匹配4级不予开放要求 | 0.98 | False |
| patient | treatment_plan | text | 患者治疗方案 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | column_name='treatment_plan'且column_description='患者治疗方案'，明确指向患者个体化、高度私密的临床决策内容，符合'患者敏感信息'定义中'治疗方案等高度私密数据'的描述，且该路径推荐等级为4级 | 0.95 | False |
| medical_settlement | insurance_amount | decimal | 医保结算金额 | 主题资源 / 其他数据库 / 互联网+医疗健康 / 互联网+医疗保障结算服务 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为insurance_amount，描述为'医保结算金额'，直接对应互联网+医疗健康场景下的医疗保障结算服务数据 | 0.95 | False |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
