# G1/G2 报告正文与 Notebook 源文件独立预审

审查角色：`C-Documents:/root/c_documents`。没有编写或修改报告、Notebook、图源或处理实现。本次只写 `independent_documents/`，不读取 G3 选择/最终效果，不作候选决定。

状态：**REPAIR_REQUIRED（两项文档问题）；历史数字与引用核对 VERIFIED_WITHIN_SCOPE**。这不是 G3 报告最终验收，也不闭合外部互动证据依赖。

待审原版本：

| 对象 | SHA256 |
|---|---|
| `task1/reports/experiment1/experiment1.tex` | `ca9c37cff21750ce0442ad5178de321b262672d2da0c3641f679fe52111a04ba` |
| `task1/reports/process1/process1.tex` | `bc95533d182da8e5b17fe04d3109ee472cf64b810f624c7974aa8428d84ee78c` |
| 基础完成版 Notebook | `6d85188656634a2f93a8b4a3954d847346a3fa6ca19c3c61714fc3f41ffc9b6d` |
| 系统完成版 Notebook | `89aa0605a51be9409e875da7d307998f7756de7a31461958b696b2d1c3e1c7d6` |

## 必要修复

### G3-DOC-01：Process Report 两层归属

现有 Part I 的“坐标来源缺失没有被假标签补齐”和“方向规则的计算顺序先确认，再执行”包含具体 CRS/D1、D2 技术语义及 7 条 pilot 数值。Interaction Evidence Protocol §18.2 明确把 CRS、投影与具体实验方法归入 Part II。Part I 可以保留不确定事实、用户授权与角色边界的治理说明，但当前具体实验段落跨越了两层职责。

关闭标准：将两个具体技术小节整体移至 Part II，Part I 保留有来源的治理原则和交叉引用；原话、数值、历史身份不改变。重新编译，并由 C 对新目标哈希复核。这是报告结构修复，不需要新方法授权。

### G3-DOC-02：Experiment Report 方向参数组呈现不足

“三组参数实验”列出方向取值，但实际图只有 S 网格和 P 压缩误差图；方向组仅有定性一句与 C-D 最终保留 R0 的说明。基础 Notebook 已包含方向参数图，报告本身仍缺少能看出该组实际结果的读数。用户要求完整实验解释与独立技术报告，不能靠参数域清单代替结果。

关闭标准：在报告加入现成的真实 G2 方向阈值结果图或等价小表，配简短结果解释，明确开发样本、局部删除/几何读数及未证明统一收益的边界；数字核对真实历史记录，不新增实验或重定指标。现成图为 `task1/figures/goal2/direction_threshold_and_neighborhood.pdf`。

附带数值校正：正文 PROJ 最大坐标差写为 `4.83e-10`，原回执是 `4.823281158894599e-10`；可按三位有效数字写“约 `4.82e-10`”。这属于轻微显示舍入，不作为单独阻断项。

## 实际检查及通过范围

独立执行：

```bash
.venv/bin/python task1/evidence/goal3/independent_documents/review_history.py
```

当前输出 **833 项检查全部通过**；15 个源目标、36 个真实依赖文件逐一绑定，完整观察值见 `historical_checks.json`。

- 实际回读教师 PPTX 原件第 5、6、18、20、22、24、26、37、42 页，并核对基础/系统 starter 的任务单元。确认需要处理代码、评价逻辑、参数/顺序讨论、结构不同的四模式、AI 反例与两份报告；提交命名和日期未被虚构为精确时刻。
- 从原始 JSON 重新统计 11,386 条、1,173,410 点、1,162,024 条相邻边，以及零时间差、同刻异位置、连续重复位置、超过 30 秒边数。这里只读结构，不运行 G3 方法。
- 独立核对 23 个历史数值宏、生成表文件哈希；从 G2 逐记录配对表重聚合 C-S/C-D/C-P 的分母、严格改善、终态与覆盖。覆盖与实际保留点区分正确。
- 从模式逐记录表与模型回执目录表核对四模式观察分母、支持计数、84 次有效与 15 次历史可见调用；Search only 的记录级调用为 0。没有将隐藏底层费用填为 0。
- 记忆送达为 96 个记录观察；消费表共 241 个回合，其中 60 回合引用、49 回合动作一致。报告没有把这些分母混用或声称因果质量收益。
- 六条 AI 引用全部核对原始 response 哈希与真实原话，再从对应候选 trace 核对参数和所有所引指标。合法权衡、不确定预测、正确局部预测分别表达；没有把缺失共同误差当作零或可比增减。
- 六组构造/19 条处理链/25 个已知答案记录与报告对应。报告明示构造标签只在合成例内有效，未冒充真实噪声标签。本次未重跑历史数学；独立数学复验属于既有 C 及当前 C-Protocol 范围。
- G1 D1/D2 两条引语与保存的 `USER_DECISIONS.json` 完全匹配；pilot 阶段计数匹配原结果。Process Report 中 context 绑定、回执目标、null 叙述、Notebook/图形与中断分类修复，在真实 `PROCESS_RECORD.md` 中有对应记录；未发现伪造用户逐项裁决。
- 两份完成版 Notebook 共 20 个代码单元 AST 通过，默认 FULL_RECOMPUTE、相对根路径、两处 Provider 哨兵、记忆前后哈希、拒绝覆盖已有复算目录等边界在源码中存在。当前 execution_count 全为 null；不能把本次静态检查写成 full 路径通过。
- 两份报告采用共同 P2 文件，无引用模板 demo-assets。当前保留清楚的姓名/学号、真实截图、Evidence Master 规格/LOCK 依赖，没有假造证据或宣称提交。

## 引用支持范围

独立 C 使用网页工具实际打开三个原始官方页面，均成功返回正文：

- [PROJ cart](https://proj.org/en/stable/operations/conversions/cart.html)：支持经纬度/椭球高到地心直角坐标的语义。
- [PROJ topocentric](https://proj.org/en/stable/operations/conversions/topocentric.html)：支持固定原点 ENU、地理输入先 cart 再 topocentric 的语义。
- [Cawley–Talbot 官方摘要与元数据](https://www.jmlr.org/papers/v11/cawley10a.html)：支持有限样本选择准则可能过拟合、评价可能产生选择偏差的一般提醒。

B 的 `SOURCE_READ_SCOPE.md` 和 HTTP 回执明确其实际读取范围。报告没有把这些来源用于证明数据 datum、样本量、阈值最优或真实精度；没有声称读过 Cawley–Talbot 全文或复现其算法。本次 C 只核对网页可见内容与引用关系，不伪称已复验 B 下载时原始 HTTP 字节。

## 未检查与外部依赖

G3 最终内容、最终生产数值、图与完整报告的全页 200 dpi 视觉审核、两份 Notebook 新内核 full 执行、ZIP 独立解压复算、完整源码依赖闭包仍待最终真实产物。原报告 `generated.tex` 待填接口没有被当作已完成内容。

姓名/学号及 Evidence Master 输入属于已登记的外部依赖，保持 `BLOCKED_EXTERNAL`；它们不阻止其他技术文档、实验、复现工作继续。证据未 LOCK、网页 GPT 第二审核未发生、用户 Understanding 未判断，均不能改成 PASS。

审查程序第一次把 PPT XML 文本中的空格当作缺失“零调用”句子，产生了一项检查器误报；原输出保存在 `historical_checks_first_attempt.json`。仅修正检查器的空白归一化后复验通过，未改教师材料或报告。这不是生产方法失败。
