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
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为 patient_name，类型为 varchar，描述明确指向‘患者姓名用于医疗服务中的身份确认’，与该分类路径下‘患者信息包括患者的身份识别……用于医疗服务中的身份确认和沟通’语义完全匹配，且不依赖特定业务系统（如电子病历、就诊卡等）或细分场景（如儿童保健、医保登记），属最通用且准确的上位归类。 | 0.98 | False |
| patient | id_card_no | varchar | 患者身份证件号码 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为id_card_no，类型为varchar，描述为'患者身份证件号码'，明确属于患者身份识别类基本资料，与'患者信息'分类中'身份识别'语义完全匹配；该路径覆盖通用患者身份管理场景，不依赖特定业务（如就诊卡、医保登记）假设，比更具体的业务路径（如就诊卡管理、参保登记）更稳妥。 | 0.95 | False |
| patient | diagnosis_result | text | 患者诊断结果 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段语义为'患者诊断结果'，属于高度私密的临床健康信息，直接匹配'患者敏感信息'定义中明确列举的'诊断结果'，且该路径强调严格保密和伦理合规，安全等级要求最高。 | 0.95 | False |
| patient | treatment_plan | text | 患者治疗方案 | 基础资源 / 服务范围与对象 / 患者 / 患者敏感信息 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段语义为'患者治疗方案'，属于电子病历中高度私密的临床数据，直接关联患者个体健康权益，符合'患者敏感信息'对病历、诊断、治疗方案等需严格保密数据的定义；虽其他候选路径（如临床路径管理、门急诊处方等）也含'治疗方案'关键词，但均附加特定业务场景约束（如标准化流程、门急诊、处方等），而本字段无表名或描述佐证其归属具体业务环节，故选择覆盖语义最广且安全等级匹配的通用敏感信息分类。 | 0.92 | False |
| medical_settlement | insurance_amount | decimal | 医保结算金额 | 主题资源 / 其他数据库 / 互联网+医疗健康 / 互联网+医疗保障结算服务 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为insurance_amount，描述为'医保结算金额'，直接对应'互联网+医疗保障结算服务'中记录医保结算信息的核心语义；相比'医保接口管理'（偏重系统对接与政策交互），该字段属于结算结果数据本身，更契合结算服务主题资源分类。 | 0.92 | False |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
