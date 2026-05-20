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
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为 patient_name，类型为 varchar，描述明确指向‘患者姓名用于医疗服务中的身份确认’，与该分类路径下‘患者信息包括患者的身份识别……用于身份确认和沟通’的定义完全一致，语义匹配度高且不依赖特定业务子场景。 | 0.95 | False |
| patient | id_card_no | varchar | 患者身份证件号码 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为id_card_no，描述为'患者身份证件号码'，属于患者身份识别类基本资料，直接对应'患者信息'分类中关于身份识别的核心语义；该路径层级合理（3级），覆盖通用患者身份管理场景，不依赖特定业务子系统（如就诊卡、医保登记等），匹配最稳健。 | 0.95 | False |
| patient | diagnosis_result | text | 患者诊断结果 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段名为diagnosis_result，描述为'患者诊断结果'，直接对应分类说明中'患者的病历、诊断结果、治疗方案等高度私密数据'，且match_profile中positive_terms明确包含'诊断结果''患者诊断结果''高度私密数据''需严格保密以防止泄露'，语义完全匹配，无需依赖具体业务场景假设。 | 0.98 | False |
| patient | treatment_plan | text | 患者治疗方案 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段语义为'患者治疗方案'，直接对应分类描述中明确列举的'治疗方案'，且该路径专指涵盖病历、诊断结果、治疗方案等高度私密数据的患者敏感信息，强调保密性与伦理合规，语义覆盖最精准、层级最适配。 | 0.95 | False |
| medical_settlement | insurance_amount | decimal | 医保结算金额 | 主题资源 / 其他数据库 / 互联网+医疗健康 / 互联网+医疗保障结算服务 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为insurance_amount，描述为'医保结算金额'，语义明确指向医疗保障结算场景下的金额数据，与'互联网+医疗保障结算服务'分类中'记录在线支付和医保结算信息'高度契合；相较之下，'医保接口管理'侧重系统对接与政策交互，不直接对应结算金额这一业务结果数据。 | 0.95 | False |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
