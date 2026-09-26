# Goal 1 完整要求—阶段—当前证据对应

Task ID：`SC-LAB1-G1-FOUNDATION-001`。机器可读版本：[requirements.json](requirements.json)。教师 Slide 为一起始页码；Notebook Cell 为零起始 JSON 索引。

本表不构成最终验收。真实完整基线受 U01/U02 阻断；run03 仅研究角色 A 与来源工具成功，B 路由失败，C 未调用，反馈回路未完成。内部 9 条重连通知和 1 条 transport fallback 未被原外层预算完整约束，新 LIVE 已持久冻结。108 项离线工程测试与两 Notebook 新内核复算通过，不能补足这些核心真实证据。GPT_SECOND_REVIEW 为 PENDING，Submission 为 NOT_READY。

全量工作仅为 11,386 条记录、1,173,410 点的原始结构盘点。事前 pilot 为 `0,1,2,246,256,306,352`，783 点；真实时间诊断给出 12 个索引分区，0 删除、0 改值，不是完整空间分段/过滤/去噪/简化。全部已暴露为开发数据，不宣称独立确认集。

状态只用 NOT_STARTED / IN_PROGRESS / VERIFIED_FOR_CURRENT_SCOPE / BLOCKED。VERIFIED_FOR_CURRENT_SCOPE 仅覆盖行内明确列出的本轮工程证据；G2/G3 尚未执行不单独构成 G1 失败，必要 G1 项受阻则必须保留。

| ID | 要求 | Goal 归属 | 本轮状态 | 当前事实与限制 |
|---|---|---|---|---|
| R01 | 数据字段、时空语义、采样与质量盘点 | G1：全量只读结构盘点、来源语义与权限合同；关键语义需补证；G2：批准距离口径后补充真实物理诊断与方法实验；G3：独立确认及总体边界复核 | BLOCKED | 原始结构和权限边界已核验；数据专属 CRS 与距离口径未确认，不能将语义核查整体标为完成 |
| R02 | 时间/空间异常处分段，短片段处理 | G1：分段/过滤原语、归属和原因核验；小规模真实完整分段基线；G2：完整三组参数实验中的分段组；G3：冻结参数后的全量产出 | BLOCKED | 时间诊断实际完成；空间切分和长度过滤受阻，12个时间分区不能称完整教学分段 |
| R03 | 基于教师方向关系的去噪及验证 | G1：核实教师谓词，验证环形角差/可计算性并暴露定义歧义；G2：明确删除调度后实际基线和去噪参数优化；G3：冻结方法的独立确认和正式处理 | BLOCKED | outgoing方向谓词明确；删除调度、端点/不可算邻域尚未批准，真实删点未执行 |
| R04 | Douglas–Peucker 简化及验证 | G1：有限线段和索引实现、独立误差审核及小规模真实链；G2：简化参数实验；G3：冻结后独立确认/全量结果 | BLOCKED | 有限平面数学与索引原语通过构造核验；真实米制DP及完整链没有运行 |
| R05 | 自行设计指标，解释逻辑与结果 | G1：结构/保真/不可用值合同及可运行独立审核器；G2：预先冻结收益门槛与保护项；有效比较结果；G3：独立确认并解释正式结果 | VERIFIED_FOR_CURRENT_SCOPE | 仅G1已明确的描述性/硬检查和待审核准入逻辑；不等于已证明质量改善 |
| R06 | 分段、去噪、简化三组参数实验 | G1：核实来源与六值角色，不执行扫描；G2：分段/去噪/简化三组完整参数实验；G3：保留参数的独立确认 | NOT_STARTED | 属于后续效果实验；G1材料与STARTER_REFERENCE登记不算已做参数实验 |
| R07 | 三步能否换序的讨论与必要实验 | G1：登记参考顺序，未作优劣结论；G2：批准的顺序讨论及必要实验；G3：采用顺序的独立复核 | NOT_STARTED | 没有正式顺序对照；记录Notebook顺序不算完成讨论/实验 |
| R08 | 基于助教系统的 LLM 质量提升工作流 | G1：三个真实角色、确定性工具和最小反馈闭环起步；G2：单项候选/模式作用验证；G3：组合及独立确认中的持续复核 | BLOCKED | 三个角色代码已实现，只有A成功接入当前控制器；B实际失败，C和反馈未完成 |
| R09 | LLM / 搜索 / 记忆的实际作用验证 | G1：基础权限隔离测试，不做完整效果消融；G2：批准四模式及记忆/搜索效果实验；G3：最终独立确认 | NOT_STARTED | 模式权限测试存在，但完整真实四模式效果实验未执行 |
| R10 | AI准确性与隐含假设批判，至少一组反例及前后指标、拒绝原因 | G1：保留真实工程错误/反例、拒绝与修复证据；G2：形成实际方法候选的反例、前后指标与拒绝原因；G3：汇总为真实AI批判与过程报告 | IN_PROGRESS | 已形成工程反例和真实失败，尚无完整方法效果前后比较；不伪造Human–AI争论 |
| R11 | 实验程序、Notebook、实验报告、含AI批判的过程报告 | G1：工作版程序/两Notebook/阶段技术说明和证据；G2：补充有效实验结果及报告素材；G3：完整实验报告、过程报告及正式交付 | IN_PROGRESS | 两工作Notebook新内核复算通过；正式报告未开始定稿，真实处理和闭环缺项显式展示 |
| R12 | 实验一专用真实执行、审核与持续优化循环 | G1：真实反馈至少触发一次有依据后续工具或有证据越界升级；G2：单项候选反馈/复验；G3：组合、接受/回退、独立确认反馈 | BLOCKED | 控制器具备反馈阶段，但真实执行在B失败停止，feedback→plan→tool→review没有完成 |
| R13 | 先单项后组合、少量论文、同标准比较、负结果保留 | G1：合同/权限边界及负结果记录验证；G2：共同基线上的少量单项候选；G3：独立验证后再研究兼容性/组合、接受或回退 | VERIFIED_FOR_CURRENT_SCOPE | 仅本Goal遵守范围与准入规则；未来执行仍需按同合同审查 |
| R14 | 原生可复现图、draw.io结构源文件、P2 / XeLaTeX | G1：必要诊断图、真实状态架构图及源文件/重建命令；G2：实验对照可复现图；G3：正式图表与P2/XeLaTeX报告 | VERIFIED_FOR_CURRENT_SCOPE | G1必要诊断/架构图已生成和视觉核查；真实完整基线前后图因U01/U02受阻，不声称存在 |
| R15 | Codex自检、推送、GPT实际远程二重验收 | G1：自检、完整审核包、安全commit/push与远程核对；GPT第二重验收；G2：同一阶段出口流程；G3：全量成果最终远程验收 | IN_PROGRESS | 自检证据已有；发布在主线程进行，本文不预报远程一致或GPT通过 |
| R16 | 教师最终ZIP与GitHub完整工程分开 | G1：核实截止/命名/邮箱及工程镜像边界；不提交老师；G2：继续完整工程与证据同步；G3：最终教师包、提交前验收与单独发布确认 | NOT_STARTED | 最终教师提交包/邮件属于G3，尚未制作或发送；要求已核实不等于已交付 |

## 逐项来源、证据和未来验收

### R01 · 数据字段、时空语义、采样与质量盘点

性质：正确执行前提。状态：**BLOCKED**。原始结构和权限边界已核验；数据专属 CRS 与距离口径未确认，不能将语义核查整体标为完成。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第10–15页；第13页正文和备注）；[task1/作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx](../../作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx)（第4页 JSON 样例与字段/Unix秒声明）；[task1/作业/作业/作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb)（Cell 1/2/11）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§5.1/7.1）。

**本轮实际内容**：

- 全量只读核对11386条记录、1173410点；无全量正式清洗或方法选择。
- 原始数组顺序和数值保留；同时间异位置/重复位置/时间差分项统计。
- Unix秒和(lon,lat)度为SOURCE_DECLARED；CRS为UNKNOWN，距离口径待批准；原始哈希前后一致。

**证据**：[task1/evidence/goal1/inventory/structure_summary.json](inventory/structure_summary.json)（全量原始结构实测）；[task1/evidence/goal1/inventory/raw_integrity.json](inventory/raw_integrity.json)（输入不变）；[task1/docs/goal1/CONTRACTS.md](../../docs/goal1/CONTRACTS.md)（数据合同/U01）；[task1/config/goal1.json](../../config/goal1.json)（可程序检查的语义及影响操作）。

**未来验收**：

- 取得绑定该JSON的数据基准可靠来源，并明确米制距离/投影口径。
- 不因时区未知阻断可靠相对时间差；仅在批准范围补做受影响真实运算。

受阻项：`U01_CRS_DISTANCE`。

对应 G1 验收 ID：G1-A02, G1-A03, G1-A04, G1-A11；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R02 · 时间/空间异常处分段，短片段处理

性质：教师基础任务 T1。状态：**BLOCKED**。时间诊断实际完成；空间切分和长度过滤受阻，12个时间分区不能称完整教学分段。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第17–18页；18页异常边p2→p3及两侧点归属）；[task1/作业/作业/作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb)（Cell 1/4/10/12–13）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§5.2/7.2/8.1）。

**本轮实际内容**：

- 分段和短片段过滤分别实现，边界右点归新段、等号不切、过滤原因独立。
- 七条pilot 0/1/2/246/256/306/352共783点，以>30来源秒得到12个索引分区，0删除、0改值。
- 构造测试验证守恒/不跨记录/短片段原因；真实空间部分未运行。

**证据**：[task1/workflow/geometry.py](../../workflow/geometry.py)（split_trajectory/filter_segments）；[task1/tests/test_geometry.py](../../tests/test_geometry.py)（已知答案与边界测试）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（当前108项离线工程测试JUnit）；[task1/results/goal1/pilot_diagnostics.json](../../results/goal1/pilot_diagnostics.json)（真实时间诊断及TIME_ONLY限制）；[task1/results/goal1/point_actions.jsonl](../../results/goal1/point_actions.jsonl)（逐点保留及阻断去向）。

**未来验收**：

- U01解除后在事前pilot上实际执行时间+空间分段和独立短段过滤。
- G2批准参数范围后比较分段参数；保留失败与全输入分母。

受阻项：`U01_CRS_DISTANCE`。

对应 G1 验收 ID：G1-A05, G1-A11；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R03 · 基于教师方向关系的去噪及验证

性质：教师基础任务 T1。状态：**BLOCKED**。outgoing方向谓词明确；删除调度、端点/不可算邻域尚未批准，真实删点未执行。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第19–20页；20页明确p3方向=p3→p4）；[task1/作业/作业/作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb)（Cell 2/6/10/14–15）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§5.1/5.2/8.1）。

**本轮实际内容**：

- 明确d_i与d_(i-1)、d_(i+1)两个环形角差均>35°的参考关系。
- direction_candidates仅报告可算窗口候选；实际denoise入口对未决方法抛MethodUnresolved。
- 两个CONSTRUCTED_FIXTURE真实验证一次/迭代/即时重算删除集合不同；没有自选一种作为教师实现。

**证据**：[task1/evidence/goal1/materials/findings.md](materials/findings.md)（教师图与字段错配核查）；[task1/evidence/goal1/materials/direction_ambiguity_fixtures.json](materials/direction_ambiguity_fixtures.json)（两个调度反例和逐步结果）；[task1/workflow/geometry.py](../../workflow/geometry.py)（角差/方向候选/拒绝未决去噪）；[task1/docs/goal1/CONTRACTS.md](../../docs/goal1/CONTRACTS.md)（U02定义和不准改值）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（构造角差/不可计算方向/特征对齐测试）。

**未来验收**：

- GPT/用户确认同时或在线、一次或迭代，以及端点和不可计算方向行为。
- U01/U02解除后进行真实删点、原因记录、特征重算和复核；随后G2单项参数实验。

受阻项：`U01_CRS_DISTANCE`, `U02_DIRECTION_EXECUTION`。

对应 G1 验收 ID：G1-A06, G1-A11；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R04 · Douglas–Peucker 简化及验证

性质：教师基础任务 T1。状态：**BLOCKED**。有限平面数学与索引原语通过构造核验；真实米制DP及完整链没有运行。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第21–23页；22页线段距离及严格大于阈值；23页16帧演示）；[task1/作业/作业/作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb)（Cell 1/2/8/10/16–18）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§5.2/5.3/8.1–8.2）。

**本轮实际内容**：

- 有序原始索引DP、有限线段/退化距离实现，避免浮点坐标相等反查。
- 独立直接距离按原始索引区间审查，含p=(2,1),a=(0,0),b=(1,0)距离sqrt(2)反例。
- 构造端点、闭合、重复、回头及几何不变性等测试；真实米制运算被U01门控，完整链另受U02影响。

**证据**：[task1/workflow/geometry.py](../../workflow/geometry.py)（DP和有限线段原语）；[task1/workflow/evaluation.py](../../workflow/evaluation.py)（独立区间对应误差）；[task1/tests/test_geometry.py](../../tests/test_geometry.py)（几何已知答案）；[task1/tests/test_evaluation.py](../../tests/test_evaluation.py)（错误结果拒绝）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（108项离线测试结果）。

**未来验收**：

- U01批准后在相同简化前输入上实际执行并验证米制误差/索引。
- 与前序基线串联须同时解决U02；G2实验只按共同指标比较。

受阻项：`U01_CRS_DISTANCE`, `U02_DIRECTION_EXECUTION`。

对应 G1 验收 ID：G1-A07, G1-A08, G1-A11；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R05 · 自行设计指标，解释逻辑与结果

性质：教师基础任务 T1。状态：**VERIFIED_FOR_CURRENT_SCOPE**。仅G1已明确的描述性/硬检查和待审核准入逻辑；不等于已证明质量改善。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第26页必做第2项；第24–25页示例保留比例）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§5.3/5.4/8.2）。

**本轮实际内容**：

- 指标注明对象、参考、单位、分母、适用条件、不可用原因和可支持结论。
- 实现全输入去向、简化前同参考saving、索引区间最大误差、长度变化、可计算性与调用状态。
- 缺收益门槛、退化额度或选择集返回PENDING_RESEARCH_REVIEW；不沿用旧综合目标/regret，不称真值恢复。

**证据**：[task1/docs/goal1/CONTRACTS.md](../../docs/goal1/CONTRACTS.md)（§3指标登记及§4三层裁决）；[task1/config/goal1.json](../../config/goal1.json)（improvement门槛为null并标草案）；[task1/workflow/evaluation.py](../../workflow/evaluation.py)（独立检查与assess_improvement）；[task1/tests/test_evaluation.py](../../tests/test_evaluation.py)（空分母/错误指标/反例/拒绝正例）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（数值和控制器离线测试）。

**未来验收**：

- G2前批准主要收益阈值、保护项退化额度、选择数据/预算。
- 真实结果仅支持保真和约束变化；无标签不升级为准确率。

对应 G1 验收 ID：G1-A08, G1-A10, G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R06 · 分段、去噪、简化三组参数实验

性质：Notebook选做，已纳入项目T2。状态：**NOT_STARTED**。属于后续效果实验；G1材料与STARTER_REFERENCE登记不算已做参数实验。

**准确来源**：[task1/作业/作业/作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb)（Cell 12/14/16题目；13/15/17为空代码单元）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§0.1/4/R06/9）。

**本轮实际内容**：

- 65/5/30/400/35/5明确标STARTER_REFERENCE_NOT_FROZEN；95m另列TEACHING_EXAMPLE。
- 没有参数扫描、候选评分或正式最优值选择。

**证据**：[task1/evidence/goal1/materials/requirements_sources.md](materials/requirements_sources.md)（选做题与页/单元映射）；[task1/config/goal1.json](../../config/goal1.json)（starter_reference、teacher_95m及allow_search=false）。

**未来验收**：

- G2先批准范围、公共基线、指标/分母、有效样本、运行预算。
- 每组保留全部结果/失败/负结果；不能把搜索预算最优称全局真值。

对应 G1 验收 ID：G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R07 · 三步能否换序的讨论与必要实验

性质：教师思考讨论，已纳入项目T2。状态：**NOT_STARTED**。没有正式顺序对照；记录Notebook顺序不算完成讨论/实验。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第42页问题）；[task1/作业/作业/作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb)（Cell 10 split→denoise→simplify）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§0.1/4/R07/5.2）。

**本轮实际内容**：

- 分段→短片段过滤→方向去噪→DP只标参考顺序。
- 未开展换序效果比较，也未宣称参考顺序最优。

**证据**：[task1/docs/goal1/CONTRACTS.md](../../docs/goal1/CONTRACTS.md)（§2参考顺序与依赖特征重算）；[task1/config/goal1.json](../../config/goal1.json)（method.order/order_status）。

**未来验收**：

- G2明确合法换序语义、阶段参考和不可比较情况。
- 每次改变邻接后重算特征；用共同指标记录结果与代价。

对应 G1 验收 ID：G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R08 · 基于助教系统的 LLM 质量提升工作流

性质：教师拓展T2与用户真实执行要求。状态：**BLOCKED**。三个角色代码已实现，只有A成功接入当前控制器；B实际失败，C和反馈未完成。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第26页选做；第28–40页助教系统）；[task1/作业/作业/任务3_LLM辅助评估清洗.ipynb](../../作业/作业/任务3_LLM辅助评估清洗.ipynb)（Cell 6/21显式Mock；Cell 30环境切换说明）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§6/7.3）。

**本轮实际内容**：

- 三角色11项职责、独立调用schema、实际权限/沙盒与工具白名单已实现。
- run03 A真实返回结构化请求并触发source_evidence；B workspace routing discovery failed；C未调用。
- run01/02失败和run03成功/失败保留；没有Mock回退冒充LIVE，亦未后补虚假交接。

**证据**：[task1/docs/goal1/ARCHITECTURE.md](../../docs/goal1/ARCHITECTURE.md)（角色职责/交接/实际覆盖）；[task1/workflow/controller.py](../../workflow/controller.py)（白名单/阶段/状态/工具派发）；[task1/workflow/provider.py](../../workflow/provider.py)（CLI/JSONL严格解析与失败）；[task1/evidence/goal1/runs/g1-live-20260926-03/manifest.json](runs/g1-live-20260926-03/manifest.json)（run03实际调用和工具）；[task1/evidence/goal1/runs/budget_live.json](runs/budget_live.json)（跨run预算及LIVE冻结）。

**未来验收**：

- 先审查合法provider路径和可验证内部重试预算；不得未批准自动解冻。
- 在当前可恢复代码状态真实完成A→B→数值审核+C→A反馈后动作→最终复核。

受阻项：`LIVE_PROVIDER_ROUTING`, `LIVE_TRANSPORT_BUDGET_FROZEN`。

对应 G1 验收 ID：G1-A09, G1-A10, G1-A12, G1-A13, G1-A14；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R09 · LLM / 搜索 / 记忆的实际作用验证

性质：教学方案37页及项目验证范围。状态：**NOT_STARTED**。模式权限测试存在，但完整真实四模式效果实验未执行。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第37页四模式、search-only不调LLM、示范/留出隔离；38页历史结果）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§0.3/4/R09/8.3）。

**本轮实际内容**：

- ENGINEERING_TEST验证search-only不能调用LLM、留出不进入pilot和参数选择。
- 未开展LLM/search/memory四模式效果比较；历史Mock演示和旧ablation不纳入当前结果。

**证据**：[task1/tests/test_control.py](../../tests/test_control.py)（模式/留出/无模型伪成功护栏）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（离线测试真实结果）；[task1/evidence/goal1/materials/findings.md](materials/findings.md)（M15/M16历史消融口径限制）。

**未来验收**：

- G2先冻结共同评分、数据划分、示范/留出边界、失败分母和预算。
- 真实模型、搜索、记忆须结构性不同并保留实际调用；G3独立确认。

对应 G1 验收 ID：G1-A14, G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R10 · AI准确性与隐含假设批判，至少一组反例及前后指标、拒绝原因

性质：教师基础任务及过程报告要求。状态：**IN_PROGRESS**。已形成工程反例和真实失败，尚无完整方法效果前后比较；不伪造Human–AI争论。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第6页单位/经纬度/插值示例及反例、前后指标、拒绝原因要求）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§8/9/10）；[docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md)（真实互动证据及Evidence Master边界）。

**本轮实际内容**：

- 材料审计纠正352历史事实、字段错配和指标范围；保留构造去噪调度反例。
- 独立控制器挑战暴露CR-01至CR-09并保留修复前后真实离线结果。
- 真实B路由失败、内部重试预算失守和冻结原因保留；工程测试不计为自然Agent争论或质量改善。

**证据**：[task1/evidence/goal1/materials/findings.md](materials/findings.md)（材料问题与真实原始结构复核）；[task1/evidence/goal1/tests/INDEPENDENT_CONTROL_REVIEW.md](tests/INDEPENDENT_CONTROL_REVIEW.md)（独立工程反例、修复前后、真实run审查）；[task1/evidence/goal1/runs/budget_live.json](runs/budget_live.json)（真实预算失败及拒绝继续LIVE）。

**未来验收**：

- G2/G3用实际候选和共同指标形成至少一组真实方法反例及前后量值/拒绝理由。
- 正式过程报告只引用真实互动，需Evidence Master批准后再制作/Lock。

对应 G1 验收 ID：G1-A08, G1-A13, G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R11 · 实验程序、Notebook、实验报告、含AI批判的过程报告

性质：教师基础交付与项目报告规则。状态：**IN_PROGRESS**。两工作Notebook新内核复算通过；正式报告未开始定稿，真实处理和闭环缺项显式展示。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第5页实验一产出；第26页作业细则）；[AGENTS.md](../../../AGENTS.md)（§§10/12/16/18）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§10/11）。

**本轮实际内容**：

- 创建基础处理审核与Agent闭环复算工作Notebook，保留教师源映射，调用共有实现。
- 两Notebook各6个code cells以独立新内核执行PASS，模式RECOMPUTE，new_model_calls=0。
- Notebook从原始输入实际重算；旧LIVE来源只复算已有source_evidence，不称新完整模型实验。
- 只形成阶段说明；未完成正式Experiment Report、未伪造Process Report或Evidence Lock。

**证据**：[task1/notebooks/01_baseline_and_audit.ipynb](../../notebooks/01_baseline_and_audit.ipynb)（基础诊断/受阻链/独立审核）；[task1/notebooks/02_agent_loop_recompute.ipynb](../../notebooks/02_agent_loop_recompute.ipynb)（已存LIVE工具复算及当前离线诊断）；[task1/evidence/goal1/validation/notebooks.json](validation/notebooks.json)（两新内核6+6 cells/零新模型调用）；[task1/docs/goal1/README.md](../../docs/goal1/README.md)（工作入口与阶段说明）。

**未来验收**：

- G2补齐有效实验，G3冻结后完成正式Notebook、两报告及可复現工程。
- 两报告分别经GPT审核，不从代码测试自动推断用户理解或正式交付通过。

对应 G1 验收 ID：G1-A15, G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R12 · 实验一专用真实执行、审核与持续优化循环

性质：用户明确要求。状态：**BLOCKED**。控制器具备反馈阶段，但真实执行在B失败停止，feedback→plan→tool→review没有完成。

**准确来源**：[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§0.2/6.2/7.3）；[task1/实验课1.pptx](../../实验课1.pptx)（第30/35/37页工具与核验思想；当前三角色为用户要求）。

**本轮实际内容**：

- 固定A来源→B诊断→C独立核查→反馈A→批准补查→C裁决阶段。
- 恢复/拒绝/缓存/状态/内部重试问题经独立反例修复；108项离线工程测试通过。
- 真实run03只有A和source_evidence，不能以恢复fixture或离线RECOMPUTE替代闭环。

**证据**：[task1/docs/goal1/ARCHITECTURE.md](../../docs/goal1/ARCHITECTURE.md)（固定阶段与实际未完成分支）；[task1/evidence/goal1/runs/g1-live-20260926-03/manifest.json](runs/g1-live-20260926-03/manifest.json)（实际run边界）；[task1/evidence/goal1/tests/INDEPENDENT_CONTROL_REVIEW.md](tests/INDEPENDENT_CONTROL_REVIEW.md)（控制器正反例及修复后结论）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（离线工程验证）；[task1/evidence/goal1/runs/budget_live.json](runs/budget_live.json)（停止条件持久化）。

**未来验收**：

- 先审查并解除真实调用阻断；按预算在最终代码完成真实反馈链。
- 后续动作必须引用真实审核反馈，不能无理由重跑或越权调参。

受阻项：`LIVE_PROVIDER_ROUTING`, `LIVE_TRANSPORT_BUDGET_FROZEN`。

对应 G1 验收 ID：G1-A09, G1-A12, G1-A13, G1-A14；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R13 · 先单项后组合、少量论文、同标准比较、负结果保留

性质：用户最终确认规则。状态：**VERIFIED_FOR_CURRENT_SCOPE**。仅本Goal遵守范围与准入规则；未来执行仍需按同合同审查。

**准确来源**：[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§0.1–0.3/5.4/9）；[docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md](../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md)（§§E–F及来源/UNRESOLVED规则）。

**本轮实际内容**：

- 未实现论文增强批量算法，未做候选大扫描、组合或最终留出选择。
- 同一结构/保真审核与硬条件固定；未冻结收益参数时不升级候选。
- 原始失败/拒绝/历史材料保留，缺失研究原件如实登记，没有重写冒充或凑论文采用数。

**证据**：[task1/config/goal1.json](../../config/goal1.json)（权限、统一指标版本、改进草案）；[task1/docs/goal1/CONTRACTS.md](../../docs/goal1/CONTRACTS.md)（三层裁决与阶段边界）；[task1/tests/test_control.py](../../tests/test_control.py)（越界方法/版本/留出拒绝）；[task1/evidence/goal1/tests/INDEPENDENT_CONTROL_REVIEW.md](tests/INDEPENDENT_CONTROL_REVIEW.md)（负例及修复前后均保留）。

**未来验收**：

- G2按共同认可基线先验证单项，保留负结果；只阅读/借鉴少量有明确任务缺口的来源。
- G3组合前需单项证据、兼容性假设和事前保护项；无额外价值优先简单方案。

对应 G1 验收 ID：G1-A17；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R14 · 原生可复现图、draw.io结构源文件、P2 / XeLaTeX

性质：用户及项目视觉规则。状态：**VERIFIED_FOR_CURRENT_SCOPE**。G1必要诊断/架构图已生成和视觉核查；真实完整基线前后图因U01/U02受阻，不声称存在。

**准确来源**：[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§10/4/R14）；[docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md](../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)（§§11–14及P2规则）；[tools/skills/publication-plots/SKILL.md](../../../tools/skills/publication-plots/SKILL.md)（科研制图及相关references）；[templates/latex/common/p2_cloud_sorbet_colors.tex](../../../templates/latex/common/p2_cloud_sorbet_colors.tex)（P2颜色源）。

**本轮实际内容**：

- 七条开发诊断图及由当前实现/真实run状态生成的架构图，保留SVG/PDF/PNG和.drawio。
- 最终生成命令与输入/代码/配色hash保存；主线程实际view_image检查中文、数据值与图状态。
- 架构图标明A成功、B失败、C未调/反馈未完成；不叠未确认基准底图。
- 没有完整基线前后输出，figure manifest明确BLOCKED；尚未制作正式报告。

**证据**：[task1/figures/goal1/figure_manifest.json](../../figures/goal1/figure_manifest.json)（图源/输入/代码绑定和baseline_before_after_figure阻断）；[task1/figures/goal1/goal1_loop.drawio](../../figures/goal1/goal1_loop.drawio)（可编辑结构源）；[task1/scripts/build_goal1_figures.py](../../scripts/build_goal1_figures.py)（原生重建入口）；[task1/evidence/goal1/validation/figures_command.json](validation/figures_command.json)（最终实际生成命令）；[task1/evidence/goal1/validation/figures.txt](validation/figures.txt)（最终生成输出）；[task1/results/goal1/pilot_diagnostics.json](../../results/goal1/pilot_diagnostics.json)（图所用真实结构数据）。

**未来验收**：

- U01/U02解除后再补真实完整基线输入—动作—输出图，不能用合成图补齐。
- G3报告按P2/XeLaTeX正式编译/渲染核查；本轮不冻结最终报告。

对应 G1 验收 ID：G1-A16；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R15 · Codex自检、推送、GPT实际远程二重验收

性质：用户及AGENTS工程规则。状态：**IN_PROGRESS**。自检证据已有；发布在主线程进行，本文不预报远程一致或GPT通过。

**准确来源**：[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§11–13/15）；[AGENTS.md](../../../AGENTS.md)（§§18/20）。

**本轮实际内容**：

- 保存初始环境/工作区、材料、现状基线、最终108项测试、独立控制器审查和Notebook复算。
- 已授权main提交/推送；最终ARTIFACT_SHA、remote SHA和clean状态由最终发布证据确认。
- GPT_SECOND_REVIEW保持PENDING，核心受阻不能由其他PASS抵消。

**证据**：[task1/evidence/goal1/environment/initial_commands.json](environment/initial_commands.json)（初始工作区/命令事实）；[task1/evidence/goal1/tests/starter_baseline.txt](tests/starter_baseline.txt)（修改前测试）；[task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)（最终离线JUnit）；[task1/evidence/goal1/tests/INDEPENDENT_CONTROL_REVIEW.md](tests/INDEPENDENT_CONTROL_REVIEW.md)（独立工程审查）；[task1/evidence/goal1/validation/notebooks.json](validation/notebooks.json)（新内核复算）。

**未来验收**：

- 主线程完成完整审核包和安全发布检查，实际push后核对最终本地/远程SHA。
- GPT读取真实远程代码/数据/图/日志进行二重验收；在此之前不得宣布项目最终PASS。

对应 G1 验收 ID：G1-A01, G1-A18；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

### R16 · 教师最终ZIP与GitHub完整工程分开

性质：教师提交要求与项目发布规则。状态：**NOT_STARTED**。最终教师提交包/邮件属于G3，尚未制作或发送；要求已核实不等于已交付。

**准确来源**：[task1/实验课1.pptx](../../实验课1.pptx)（第26页压缩包、邮箱、命名、10月5日前；第43页联系邮箱）；[AGENTS.md](../../../AGENTS.md)（§18 GitHub与Submission Package分工）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（§4/R16/13）。

**本轮实际内容**：

- 保留源码、材料、数据和内部证据的GitHub工程范围；没有把证据整批排除。
- 登记原截止文字、邮箱和命名，未改教师日期、未发邮件。
- 未制作正式教师ZIP，也未把本轮结果加入11-file ChatGPT上传集合。

**证据**：[task1/evidence/goal1/materials/requirements_sources.md](materials/requirements_sources.md)（教师提交细则与课程设计适用边界）；[task1/evidence/goal1/materials/pptx_05_text_and_notes.md](materials/pptx_05_text_and_notes.md)（第26/43页原文）；[task1/evidence/goal1/APPROVED_PROMPT.md](APPROVED_PROMPT.md)（本轮发布授权和禁止正式提交）。

**未来验收**：

- G3按老师最后有效要求单独整理学号_姓名_实验一提交包。
- 正式提交须满足最终验收/发布授权；GitHub工程仍保留可复核完整证据。

对应 G1 验收 ID：G1-A17, G1-A18；这些 ID 的最终 PASS/FAIL/BLOCKED/NOT_RUN 由 acceptance.json 单独裁决。

## 教师提交与课程设计适用范围

教师第 26 页写 **10 月 5 日前**，具体时刻未说明，提交页未单独写年份；封面日期为 20260917。本轮保留原日期，不推断 23:59，不擅自延期，也不发邮件。邮箱 `52285903012@stu.ecnu.edu.cn`；命名 `学号_姓名_实验一`，页面列出 `.zip/.ipynb/.docx/.pdf`。G3 再按老师最后有效要求单独整理教师 ZIP，GitHub 持续保留完整工程与证据。

教师第 26 页的 `Trajectory_preprocessing.ipynb` 按三项 TODO 和任务内容对应仓库的 `task1/作业/作业/作业1轨迹数据预处理.ipynb`；不新建同名文件替代原材料。第 3 页四人分组与第 7 页分组/开题/中期/答辩属于课程设计页面，未据此增加实验一交付。安排原文为 9 月 24 日、10 月 22 日、11 月 16 日、12 月 31 日 / 1 月 8 日（最终答辩待定）。

第 8 页 DeepSeek 是教师工具建议；本项目 GPT＋Codex 是用户明确选择，不能写成教师单独批准。

## 缺失研究文件与证据类别

没有提供或找到下列原件，不补写摘要冒充；不依赖它们的 G1 基础工程继续，未重启广泛论文检索。

- `Task1_Literature_Review_2025_2026_Merged.md`。
- `Task1_Source_Audit_2025_2026_Merged.json`。
- `Task1_Stage01_Readonly_Audit.md`。

本轮区分 CURRENT_RUN_REAL_DATA_DIAGNOSTIC_RECOMPUTE、真实 LIVE 已发生调用、CONSTRUCTED_FIXTURE / ENGINEERING_TEST、MOCK_TEST、REPLAY/RECOMPUTE 和 HISTORICAL。教师示例图、Notebook 旧 output、旧 demo/ablation 均不是本轮结果。两工作 Notebook 的新内核结果为 RECOMPUTE，`new_model_calls=0`；只有保存的实际 CLI 调用可计入 LIVE。

## 本表核对

已检查 R01–R16 共 16 项且无重复 ID，状态全部属于指定枚举，44 个引用文件实际存在。该核对只证明本表结构/路径，不证明算法、真实处理或最终项目验收。最新 108 项测试依据为 [task1/evidence/goal1/tests/final_bound.xml](tests/final_bound.xml)，两 Notebook 新内核证据为 [task1/evidence/goal1/validation/notebooks.json](validation/notebooks.json)，独立控制器复查为 [task1/evidence/goal1/tests/INDEPENDENT_CONTROL_REVIEW.md](tests/INDEPENDENT_CONTROL_REVIEW.md)。

Git 最终发布、远程 SHA 和 GPT 二重验收由主审核包的最终结果提供；本表不提前声称已同步或已验收。
