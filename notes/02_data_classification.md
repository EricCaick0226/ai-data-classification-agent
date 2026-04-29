# Day 2 笔记：数据分类分级基础

## 1. 今天目标

本项目叫：

`ai-data-classification-agent`

最终目标是：

输入一个 CSV 文件，系统能够读取字段信息，判断字段类型，对字段进行分类分级，并生成一份 Markdown 报告。

Day 2 的主题是：

数据分类分级基础。

今天的目标是：

1. 理解“数据分类”和“数据分级”的区别
2. 理解为什么企业需要做数据分类分级
3. 建立一个最小可用的数据分类表
4. 建立一个最小可用的风险等级表
5. 为后面 Day 3 写 `rules.py` 做准备
6. 完成 `notes/02_data_classification.md`

Day 2 不安装 `openai`。

Day 2 不使用 LLM API。

Day 2 不使用 LangChain。

Day 2 不进入 Tool Calling。

Day 2 不写复杂 Agent。

第一阶段仍然只用 Python、pandas 和规则库完成无 AI 小闭环。

---

## 2. 数据分类分级是什么？

数据分类分级，就是判断一个字段属于什么类型、风险有多高、是否需要保护。

简单来说：

数据分类是在问：

这个字段是什么数据？

数据分级是在问：

这个字段泄露后会造成多严重的影响？

例如：

| 字段名 | 分类 | 风险等级 | 理由 | 是否需要人工复核 |
|---|---|---|---|---|
| email | 个人信息 PII | 中 | 邮箱可以识别或联系到个人 | 否 |
| phone_number | 个人信息 PII | 中 | 电话号码属于个人联系方式 | 否 |
| password | 身份认证数据 Authentication Data | 极高 | 密码可以用于登录账号，泄露后可能导致账号被盗 | 否 |
| id_card | 敏感个人信息 / 身份识别数据 | 极高 | 身份证件可以证明一个人的身份，泄露后可能导致身份冒用 | 否 |
| salary | 财务数据 / 薪酬数据 | 中 | 薪水会暴露个人收入和经济隐私 | 否 |
| favorite_color | 偏好数据 | 低 | 单独泄露通常影响很小 | 否 |
| last_login_time | 行为数据 | 低或中 | 单独看风险较低，但和账号、设备、IP 结合后可能暴露行为习惯 | 是 |
| device_id | 设备数据 | 中 | 设备 ID 可以长期绑定一台设备，可能用于追踪用户行为 | 是 |

---

## 3. 数据分类是什么？

数据分类关注的是：

这个字段是什么类型的数据？

例如：

`phone_number`

它表面上是手机号码。

但在企业的数据分类里，它更准确属于：

个人信息 / 联系方式数据。

因为它可以联系到一个具体的人。

再比如：

`email`

它表面上是邮箱地址。

但在数据分类里，它也属于：

个人信息 / 联系方式数据。

因为它可以识别或联系到某个人，也可能和账号绑定。

再比如：

`password`

它不是联系方式，也不是普通个人信息。

它属于：

身份认证数据。

因为它可以用来验证用户是否有权限进入账号或系统。

---

## 4. 数据分级是什么？

数据分级关注的是：

这个数据泄露后有多严重？

例如：

`favorite_color`

如果最喜欢的颜色泄露了，通常影响不大。

所以它通常是：

低敏感数据。

但是：

`password`

如果密码泄露了，别人可能直接登录用户账号。

所以它通常是：

极高敏感数据。

再比如：

`home_address`

如果家庭住址泄露了，可能带来骚扰、跟踪、人身安全等风险。

所以它通常是：

高敏感数据。

再比如：

`real_time_gps_location`

如果实时 GPS 位置泄露了，别人可能知道一个人现在在哪里，甚至追踪行动轨迹。

所以它可能是：

高敏感或极高敏感数据。

---

## 5. 数据分类和数据分级的区别

数据分类和数据分级不是一回事。

数据分类问的是：

这个字段是什么数据？

数据分级问的是：

这个字段泄露后有多严重？

例如：

| 字段名 | 分类 | 等级 |
|---|---|---|
| email | 个人信息 / 联系方式数据 | 中 |
| password | 身份认证数据 | 极高 |
| id_card | 敏感个人信息 / 身份识别数据 | 极高 |
| salary | 财务数据 / 薪酬数据 | 中 |
| favorite_color | 偏好数据 | 低 |
| device_id | 设备数据 | 中 |

一个字段的分类和等级要分开判断。

例如：

`password` 和 `id_card` 都可能是极高敏感数据。

但是它们的分类不一样。

`password` 属于身份认证数据，因为它用来验证用户能不能进入账号。

`id_card` 属于身份识别数据，因为它用来证明一个人是谁。

所以：

等级一样，不代表分类一样。

分类一样，也不代表等级一定一样。

---

## 6. 企业为什么要做数据分类分级？

企业不能把所有数据都当成一样的数据来管理。

因为不同数据的用途、敏感程度和泄露后果不一样。

例如：

`favorite_color` 泄露后，通常影响很小。

`email` 泄露后，可能导致骚扰、垃圾邮件、钓鱼攻击或账号关联。

`salary` 泄露后，可能暴露个人收入和经济隐私。

`password` 泄露后，可能导致账号被盗。

`id_card` 泄露后，可能导致身份冒用、金融诈骗等严重后果。

所以企业需要先做分类分级，再决定：

- 谁可以访问这些数据
- 是否需要加密
- 是否需要脱敏
- 是否需要记录访问日志
- 是否需要人工复核
- 数据泄露后是否需要上报
- 后续代码应该如何自动判断字段风险

如果不先做分类分级，后面写 `rules.py` 就会很乱。

程序不知道 `email`、`password`、`salary`、`device_id` 分别应该按照什么标准判断，也无法稳定输出分类、等级、原因和是否需要人工复核。

---

## 7. 常见数据分类表

| 分类 | 含义 | 例子 |
|---|---|---|
| 个人信息 PII | 能识别、联系或关联到某个人的数据 | email, phone_number, name |
| 敏感个人信息 Sensitive PII | 泄露后可能对个人造成较大伤害的数据 | id_card, home_address, precise_location |
| 身份识别数据 Identity Data | 用来证明“你是谁”的数据 | id_card, passport_number, student_id |
| 身份认证数据 Authentication Data | 用来验证“你能不能进入账号或系统”的数据 | password, verification_code, login_token |
| 财务数据 Financial Data | 和收入、资产、付款、财务状况有关的数据 | salary, bank_account |
| 交易数据 Transaction Data | 和交易过程有关的数据 | transaction_amount, order_id, payment_time |
| 行为数据 Behavioral Data | 记录用户做过什么的数据 | last_login_time, click_history, search_history |
| 设备数据 Device Data | 和用户设备有关的数据 | device_id, IP address, device_model |
| 位置数据 Location Data | 和用户或设备位置有关的数据 | gps_location, city, home_address |
| 业务运营数据 Business Data | 公司业务运行中的数据 | order_count, inventory_status |
| 内部管理数据 Internal Management Data | 公司内部管理相关数据 | company_department, employee_performance_score |
| 公开数据 Public Data | 本来就可以对外公开的数据 | public_product_name, public_website_url |

---

## 8. 常见敏感等级表

| 等级 | 含义 | 例子 |
|---|---|---|
| 公开 Public | 本来就可以公开，泄露风险很低 | public_product_name |
| 低 Low | 单独泄露影响较小 | favorite_color, general_preference |
| 中 Medium | 可以识别、联系、关联个人，或暴露一定隐私 | email, phone_number, salary, device_id |
| 高 High | 泄露后可能造成明显隐私、安全或经济风险 | home_address, employee_performance_score, precise_location |
| 极高 Critical | 泄露后可能导致账号接管、身份盗用、严重安全风险 | password, id_card, verification_code, real_time_gps_location |

---

## 9. 字段例子分析

| 字段名 | 分类 | 等级 | 原因 | 是否需要人工复核 |
|---|---|---|---|---|
| email | 个人信息 / 联系方式数据 | 中 | 邮箱可以识别或联系到个人，也可能用于钓鱼和账号关联 | 否 |
| phone_number | 个人信息 / 联系方式数据 | 中 | 电话号码可以联系到个人，也可能用于诈骗或账号验证 | 否 |
| password | 身份认证数据 | 极高 | 密码可以用于登录账号，泄露后可能导致账号被盗 | 否 |
| id_card | 敏感个人信息 / 身份识别数据 | 极高 | 身份证件可以证明身份，泄露后可能导致身份冒用 | 否 |
| salary | 财务数据 / 薪酬数据 | 中 | 薪水会暴露个人收入和经济隐私 | 否 |
| favorite_color | 偏好数据 | 低 | 单独泄露通常影响很小 | 否 |
| last_login_time | 行为数据 | 低或中 | 单独看只是登录时间，但和账号、设备、IP 结合后可能暴露行为习惯 | 是 |
| device_id | 设备数据 | 中 | 设备 ID 可以长期绑定一台设备，可能用于追踪用户行为 | 是 |
| home_address | 敏感个人信息 / 地址信息 | 高 | 家庭住址泄露后可能带来骚扰、跟踪和线下安全风险 | 否 |
| gps_location | 位置数据 | 高或极高 | 如果是实时 GPS 坐标，可能暴露用户当前位置和行动轨迹 | 是 |
| company_department | 内部管理数据 | 低或中 | 部门信息本身风险不一定高，但和姓名、薪资、绩效结合后风险会上升 | 是 |
| employee_performance_score | 内部管理数据 / HR 数据 | 中或高 | 绩效分数会影响员工评价、晋升和薪酬，泄露后可能造成内部管理风险 | 是 |
| public_product_name | 公开数据 | 公开 | 产品名称本来就是对外展示的信息 | 否 |

---

## 10. 为什么有些字段需要人工复核？

有些字段需要人工复核，因为字段名本身不一定能说明真实内容。

例如：

`user_location`

它可能表示：

`city = New York`

这种情况范围很大，不能精确定位一个人，风险可能只是低或中。

但它也可能表示：

`real-time GPS coordinates`

这种情况可以精确定位一个人的当前位置和行动轨迹，风险可能达到高或极高。

所以字段名只是线索，不是最终答案。

如果字段含义模糊、范围不清楚、可能有多种解释，就需要人工复核。

例如：

| 字段名 | 为什么需要复核 |
|---|---|
| user_location | 可能只是城市，也可能是实时 GPS |
| contact | 可能是邮箱、电话，也可能只是普通联系人备注 |
| id | 可能是普通数据库 ID，也可能是身份证号 |
| token | 可能是普通标识符，也可能是登录 token |
| address | 可能是家庭住址，也可能是公司地址或收货地址 |

---

## 11. 和后续 rules.py 的关系

Day 2 的目标不是写复杂代码，而是先建立人的判断标准。

Day 3 才会把这些判断标准写成 `rules.py`。

例如：

如果字段名包含 `email` 或 `mail`，可以初步判断为：

| 分类 | 等级 | 是否需要人工复核 |
|---|---|---|
| 个人信息 / 联系方式数据 | 中 | 否 |

如果字段名包含 `password`、`passwd` 或 `pwd`，可以初步判断为：

| 分类 | 等级 | 是否需要人工复核 |
|---|---|---|
| 身份认证数据 | 极高 | 否 |

如果字段名包含 `salary`，可以初步判断为：

| 分类 | 等级 | 是否需要人工复核 |
|---|---|---|
| 财务数据 / 薪酬数据 | 中 | 否 |

如果字段名包含 `location`，可以初步判断为：

| 分类 | 等级 | 是否需要人工复核 |
|---|---|---|
| 位置数据 | 低 / 中 / 高 / 极高，取决于具体内容 | 是 |

所以 `rules.py` 不是让程序真正像人一样理解世界，而是让程序按照我们提前写好的规则进行初步判断。

Day 2 是标准。

Day 3 是把标准翻译成代码。

---

## 12. Day 2 小总结

今天我理解了：

数据分类是在问：

这个字段是什么数据？

数据分级是在问：

这个字段泄露后有什么影响？

我也理解了：

`email` 是个人信息，但通常不是极高敏感。

`phone_number` 是个人信息 / 联系方式数据，通常是中敏感。

`password` 是身份认证数据，通常是极高敏感。

`id_card` 是敏感个人信息 / 身份识别数据，通常是极高敏感。

`salary` 是财务数据 / 薪酬数据，通常是中敏感。

`favorite_color` 是偏好数据，通常是低敏感。

`last_login_time` 是行为数据，单独看风险较低，但和其他字段结合后风险可能上升。

`device_id` 是设备数据，通常是中敏感。

`user_location` 要看具体内容，可能需要人工复核。

今天的重点不是写代码，而是把判断标准想清楚。

下一步 Day 3 才会把这些判断标准写成 `rules.py`。

---

## 13. Day 2 检查标准

我今天应该能做到：

- 能用自己的话解释“分类”和“分级”的区别
- 能判断 `email`、`phone_number`、`password`、`id_card`、`salary`、`favorite_color` 的分类和等级
- 能理解为什么 `password` 和 `id_card` 都是极高敏感，但分类不同
- 能理解为什么 `user_location` 需要人工复核
- 完成 `notes/02_data_classification.md`
- 没有安装 `openai`
- 没有进入 LangChain
- 没有进入 Agent
- 没有进入 Tool Calling

---

## 14. Git 提交信息

完成 Day 2 笔记后，在项目根目录执行：

`git add .`

然后执行：

`git commit -m "Day 2: add data classification and sensitivity notes"`

---

## 15. Day 2 小作业

请判断下面字段的分类、等级、原因、是否需要人工复核：

- email
- phone_number
- password
- id_card
- salary
- favorite_color
- last_login_time
- device_id

格式如下：

字段名：

分类：

等级：

原因：

是否需要人工复核：