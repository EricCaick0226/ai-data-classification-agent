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
| patient | patient_name | varchar | 患者姓名用于医疗服务中的身份确认 | 基础资源 / 服务范围与对象 / 患者 / 患者信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为 patient_name，类型为 varchar，描述明确指向‘患者姓名用于医疗服务中的身份确认’，与该分类路径下‘患者的身份识别、联系方式等基本资料，用于医疗服务中的身份确认和沟通’高度一致；match_profile 中 core_terms 包含‘患者姓名’‘身份确认’‘基本信息’‘患者识别’，column_name_hints 包含 patient_name，且 negative_terms 不匹配（无身份证号、住址等敏感扩展信息），排除更高级别敏感类或索引类路径。 | 0.98 | False |
| patient | id_card_no | varchar | 患者身份证件号码 | 主题资源 / 电子病历数据库 / 基础字典 / 患者主索引 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段语义为患者唯一身份标识（身份证件号码），匹配‘患者主索引’核心场景，强调唯一性、主索引属性及身份核验功能，且 match_profile 中 core_terms 和 column_name_hints 高度吻合。 | 0.98 | False |
| patient | diagnosis_result | text | 患者诊断结果 | 主题资源 / 电子病历数据库 / 临床诊疗 / 诊断明细信息 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为diagnosis_result，类型为text，描述为'患者诊断结果'，与'诊断明细信息'类目下核心语义（诊断结果、诊断明细、疾病诊断）及同义词（详细诊断、主/其他诊断）、列名提示（diagnosis_result、diagnosis_detail等）高度匹配；该字段属于电子病历中结构化或半结构化临床诊疗数据，强调诊断内容本身而非摘要、处方依据或特定专科场景。 | 0.96 | False |
| patient | treatment_plan | text | 患者治疗方案 | 业务资源 / 医疗服务(医院) / 临床服务 / 门急诊电子病历 | 4级 | 一般数据4级 | 有条件共享 | 不予开放 | 字段语义为患者治疗方案，属于门急诊电子病历中记录的核心诊疗内容，且该分类明确包含'治疗方案'，匹配度最高；其recommended_level为4级，符合敏感性和管控要求。 | 0.95 | False |
| medical_settlement | insurance_amount | decimal | 医保结算金额 | 业务资源 / 医疗服务(医院) / 医疗管理 / 医保接口管理 | 3级 | 一般数据3级 | 有条件共享 | 有条件开放 | 字段名为insurance_amount，描述为'医保结算金额'，与候选规则1的核心术语'医保结算'、'结算金额'及列名提示'insurance_amount'高度匹配；无互联网/线上相关语义线索，排除规则2。 | 0.95 | False |
| medical_settlement | created_at | datetime | 记录创建时间 |  |  |  |  |  | 未形成可信分类结论，需要人工复核。 | 0 | True |
