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
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为 patient_name，类型为 varchar，描述明确指向‘患者姓名用于医疗服务中的身份确认’，与该分类路径下‘患者基本信息、身份识别、隐私保护’的语义完全一致；match_profile 中 core_terms（如身份确认、患者识别）、synonyms（如患者姓名、就诊人姓名）及 column_name_hints（如 patient_name、name）均高度匹配，且 negative_terms（如联系方式、身份证号）未被触发，排除更窄场景（如就诊卡、主索引、敏感信息）。 | 0.98 | False |
| patient | id_card_no | varchar | 患者身份证件号码 | 主题资源 / 电子病历数据库 / 基础字典 / 患者主索引 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段语义为患者唯一身份标识（身份证件号码），且 column_description 明确指向‘患者身份证件号码’，匹配该路径中‘患者基本身份信息和唯一标识’‘患者主索引’的核心定义；match_profile 中 core_terms 和 column_name_hints 高度吻合，且该路径强调数据唯一性与安全性，符合身份证号作为主索引的强管控要求。 | 0.97 | False |
| patient | diagnosis_result | text | 患者诊断结果 | 主题资源 / 电子健康档案数据库 / 健康档案基本数据集 / 门诊摘要 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段属于患者表，名称为diagnosis_result，类型为text，描述为'患者诊断结果'，语义上属于患者健康档案中结构化门诊记录的核心内容，符合'健康档案基本数据集/门诊摘要'对诊断结果的归集定位；相比'电子病历数据库/门诊就诊信息'，该字段未体现具体就诊行为（如时间、科室、医生等），更契合摘要类、归档类数据集；'远程影像诊断'明显不相关；'其他数据库/门诊记录摘要'层级归属模糊且非标准主库路径。 | 0.92 | False |
| patient | treatment_plan | text | 患者治疗方案 | 业务资源 / 医疗服务(医院) / 临床服务 / 门急诊电子病历 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段名为'treatment_plan'，表为'patient'，描述为'患者治疗方案'，属于门急诊诊疗过程中生成的核心临床文书内容，符合'门急诊电子病历'分类中'包括病史、检查结果和治疗方案等'的定义；且该字段直接关联患者个体诊疗行为，敏感性高，匹配推荐的4级安全等级。 | 0.95 | False |
| medical_settlement | insurance_amount | decimal | 医保结算金额 | 业务资源 / 医疗服务(医院) / 医疗管理 / 医保接口管理 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为insurance_amount，描述为'医保结算金额'，语义明确指向医院端医保结算环节的应付/实结金额，与候选规则1中core_terms（如'医保结算'、'结算金额'）、synonyms（如'医保结算款'、'医保实结金额'）及column_name_hints（如'insurance_amount'、'insurance_settlement_amount'）高度匹配；无任何互联网+、线上、移动等关键词，排除规则2。 | 0.98 | False |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
