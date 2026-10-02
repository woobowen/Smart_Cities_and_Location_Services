# Experiment 1 Technical Handoff

## 2026-10-02 当前 Process 接管

用户已验收77页完整Process；本轮接入真实工作源、两条报告构建及当前PDF/打包路径。新增工程核验与范围见 [SC-LAB1-PROCESS-INTEGRATION-SYNC-001](../../../evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/REVIEW_PACKET.md)。网页GPT本轮二审=PENDING，Submission=NOT_READY；不升级逐条Evidence Lock或Understanding。Experiment成品及科学结果保持此前验收范围。

当前 [Process PDF](../../reports/process1/process1.pdf) / [唯一工作源](../../reports/process1/source/main.tex)；[旧12页稿](../../reports/process1/history/technical-draft-12p/process1.pdf)及PreTask均保留历史身份。新的审阅包以本轮REVIEW_PACKET列出的具名文件为准，旧包不覆盖。

以下为原版本交接全文，保留其当时的“当前”、委派状态和旧路径；历史路径应结合对应固定提交读取，不代表本轮检查或未完成项。

---

## 当前技术基点与指定交接

本次`SC-LAB1-NONPROCESS-CLOSEOUT-001`是非Process范围收尾；[当前验收入口](../../../evidence/infrastructure/SC-LAB1-NONPROCESS-CLOSEOUT-001/REVIEW_PACKET.md)登记NC结果。技术处理、规定实验、有限候选比较、最终确认与全量结果维持此前范围验收，不新开研究或宣称全局最优。

- 原数值CODE_SHA：`e12f8a27944210adb452730be92a0674dfc6b84b`。冻结[方法/坐标合同](../../config/goal3/contract.json)、[分区](../../evidence/goal3/split_manifest.json)、[当前运行索引](../../evidence/goal3/current_runs.json)与[结果摘要](../../evidence/goal3/result_summary.json)保持；原始数据、指标、记忆、失败记录、teacher/starter和完成版Notebook不改。§3—7保留具体历史研究事实。
- 用户已确认本对话复盘及25页Experiment。当前[PDF](../../reports/experiment1/experiment1.pdf)、[章节源](../../reports/experiment1/Experiment_Report.tex)及[批准PDF/ZIP](../../../reports/experiment-report/experiment1-reconstructed/)保持原字节；[构建说明](../../reports/README.md)继续接管正常REPORT_BUILD。已验收工程ARTIFACT=`87fc7db1ced9fd394d0cdda2113c5608205dce03`；[网页GPT二审承接](../../../evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review/REVIEW_RECEIPT.md)只对应被审`89371f6597f92f7dac9abf61f6f6b18e29ed76cc`，当前按用户转交记录，原审核附件尚未入库。本轮新提交仍待网页GPT核查。
- 已有构建/复算命令在[task1 README](../../README.md)中，分别为`REPORT_BUILD --output <新ZIP>`与`FULL_RECOMPUTE --output <新目录>`；本轮不执行，继承具体旧run/源hash/报告构建和包核验范围。placeins、needspace保留于`.venv/texmf`，不安装或清理依赖。
- Process由用户指定的另一对话接续，`PROCESS_REPORT=DELEGATED_NOT_COMPLETED`。现有[Interaction Handoff](INTERACTION_HANDOFF.md)及[原件/spec/Lock盘点](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/b_handoff/evidence_inventory.md)只作已有事实入口，原话、条目、截图、框选、caption和Evidence Plan均未修改。[前期31页源复现PARTIAL](../../../evidence/infrastructure/SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md)是已交接限制，不改为PASS。
- 非Process任务可在本轮NC通过后单独关闭；完整[当前审阅ZIP](../../submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip)保持`REVIEW_ONLY` / `NOT_READY`。Process完成后再合并、核验并取得用户提交确认，本轮不制新包。整体Deliverable=`FINAL_REVIEW`；Understanding保留原`LEARNING`，不新增Understanding/VIVA通过。

原始CRS/源datum仍未知，无噪声真值，共同覆盖不等于清洗准确率；Process完成不会消除这些技术限制。本轮实验模型调用和研究数值运行均为0。以下旧文保留当时版本身份，其中“本次”、22页/旧包/四次FULL和旧PENDING不代表当前新执行或新的未审声明。

## 历史正文：SC-LAB1-G3-CLOSEOUT-001及冻结研究事实

Parent Goal：`SC-LAB1-G3-FINAL-001`；本次收尾 Task：`SC-LAB1-G3-CLOSEOUT-001`，仍属实验一，不新增 Goal 4。当前审阅入口为 [REVIEW_PACKET.md](../../evidence/goal3/REVIEW_PACKET.md)，原要求登记保留在 [requirements.json](../../evidence/goal3/requirements.json)。本次 [MASTER_REQUIREMENTS_REVIEW](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md) 将教师 T1/T2、用户 U01—U44 与原 G1/G2/G3、TD 项交叉定位，不创建第二套研究通过结论。完整实验一入口为 [task1/README.md](../../README.md)，随后讲解入口为 [REVIEW_GUIDE.md](REVIEW_GUIDE.md)。

姓名“吴博闻”、学号字符串“10245102410”来自本次用户直接授权，唯一任务身份源为 [assignment.json](../../config/assignment.json)。Identity 已为 `VERIFIED`；报告修订日期为 2026-09-28，旧实验与冻结时间不改。Process 正式互动证据仍有外部依赖，用户理解验收与新网页文档/包验收尚未完成。本文 §3–7 记录冻结的研究事实；本次文档、复现与包的工程状态见 §8–9。

## 1. 承接、输入和研究范围

G1/G2 的阶段验收按用户转交记录保存为 `USER_RELAYED_GPT_STAGE_ACCEPTANCE`，没有补造网页审查日志。承接锚点为 `6fad8420b09ba123fe0658a5cd805cb7b7b9e67b`；G2 实际处理代码为 `c1c6272606716f9f59aa785d48bfeadb09c7a30e`，结果提交为 `1ac203c1c60b3c64490150cbd473d3091eac8564`。旧结果保留历史身份。

原始 JSON 实测 **11,386 条记录、1,173,410 点**，SHA256 为 `c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3`。原始值、教师 PPTX 和两个 starter 没有覆盖；完成版 Notebook 单独交付。完整相同记录按原值哈希分组，没有发现重复组，也没有证实记录键代表独立用户或完整行程。

既有研究范围为教师的分段、去噪、DP 简化、三组参数、顺序、评价、四模式、记忆与 AI 批判，加上原 Goal 3 批准的有限选择、确认、全量生产和交付。本次收尾只处理身份、报告表达、要求对账、复现兼容性、待审包与发布；不重新搜索候选或调参。没有新增训练、道路匹配、外部数据、坐标加偏、实验二停留点或热点任务。

## 2. 实际架构、权限和恢复接口

以下是**原 Goal 3 研究与交付阶段**的真实角色，保留原上下文身份：

| 角色/层 | 实际上下文或入口 | 责任与边界 |
|---|---|---|
| A | `/root/a_candidates` | 从真实开发证据提出有限 TaskPlan，消费单项、组合与移除结果；没有读最终集来开发新候选 |
| B-Run / B-Repair | 主线程 `/root` | 运行冻结处理、接收真实问题、修正实现、测试、新 run 重建、恢复父任务 |
| B 文档工程 | `/root/b_delivery_inventory` | 教师入口、Notebook、离线复算、图与报告生成、依赖闭包及待审包 |
| 独立 C 数值/协议 | `/root/c_protocol` | 原始范围、实际产物、独立数学、保护、选择与冻结核验；没有编写待审核心实现 |
| 独立 C 文档/交付 | `/root/c_documents` | 历史事实与引用、文档结构、可移植复现、视觉和包核验 |
| 确定性控制器 | [control.py](../../goal3/control.py) | 任务依赖、问题队列、来源/产物 hash、独立关闭、失效传播和检查点；不是第四个 LLM |

本次 `SC-LAB1-G3-CLOSEOUT-001` 复用 A/B/C 职责，实际分工为：

| 本轮角色 | 实际上下文 | 已授权的工作与边界 |
|---|---|---|
| A 要求与证据诊断 | `/root/a_requirements` | 核对教师要求、授权、教学差异和文献使用，形成派生总账；不提新算法或补写历史 |
| B 执行与修复 / 主线程 | `/root` | 同步身份和生成器，修改报告，真实构建、Notebook 复算、待审包与修复后重建，持续负责父任务 |
| B 文档子任务 | `/root/b_review_guide` | 四块复盘指南、互动来源盘点、Handoff 当前状态与导航；不代 Evidence Master 选句、定关系或 Lock |
| 独立 C | `/root/c_independent` | 从冻结来源和实际当前产物检查身份、内容、视觉、复现和包；对待审正文与数值只读，审核范围以本次 [C 目录](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/) 的回执为准 |

[goal_state.json](../../evidence/goal3/goal_state.json) 保存真实任务与问题状态；本次证据集中在 [closeout 目录](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/)。主要接口是 `submit → accept` 和 `issue → repair → close_issue`；实际产物、独立 C 上下文和当前来源必须匹配，旧回执不能关闭新产物。运行入口拒绝已有 run 目录；中断保留明确检查点和失败原因，不静默重发不确定任务。

原阶段主要工程问题及真实修复包括：等价简化条件缺失、开发输入范围检查、错误父原始对象/合同比较、产物或源码变化后的旧回执复用、父缓存范围及异常处理、无 `.git` 的冻结复算身份、相对父缓存路径，以及阶段决策消费前的实际分片新鲜度。G3-C06/C07 改变处理源码时期后重建了受影响开发 run；旧失败和旧结果没有删除或冒充当前版本。G3-C08 只修尚未用于正式运行的阶段辅助程序，不改变数值处理时期。文档的两层归属与方向参数呈现问题也经原阶段独立复验关闭。

原交付实跑还发现 Matplotlib 与 Notebook inline 接口不兼容。首个修复被独立 C 的新内核测试拒绝；第二次改用原生 `Figure`/`FigureCanvasAgg`，通过专项检查后重新执行两个完整 Notebook。原基本本失败和明确中断的系统本均保留，未计为完整复算。图例、外部依赖文字及开发阶段 C→控制器→A 反馈路径也经修正与独立检查；这些是工程问题，不是方法效果退化或质量收益。本次新增工程问题和复验见 [C 问题记录](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/ISSUES.md)；本轮 Notebook 中断与重试单独登记，见 §8。

原阶段 [治理事件索引](../../evidence/goal3/governance_tool_events.json) 的可读范围限于真实时间、工具、call ID、可得角色元数据和存储载荷哈希；索引说明当时 native 消息正文为平台加密字段，不等于已恢复逐字对话。本轮没有读取账号/其他会话日志来补历史。可读研究决定来自真实 TaskPlan、裁决和核验文件。底层模型请求及费用不可见，保持 `unknown`；本轮治理调用、历史 84 次实验模型调用与当前记录级 RECOMPUTE 分账。

## 3. 最终部署策略和坐标合同

最终策略 **S0**，统一确定性 **S-D-P**：`dt=30、distance=400、min_points=2、min_length=0、direction=35、dp=5`。教学参考 R0 仅将 `min_points/min_length` 分别设为 `5/65`，其余相同。最终记录级处理不调用 LLM，不搜索，不使用记忆，不包含逐记录候选→R0 回退。一次性确认未支持时回退 R0 的发布门控在打开最终集前已登记，原最终确认未触发该回退。

方向规则沿用批准的 D2：一次计算与完整标记、同时删除；首尾及必要方向不可计算窗口保留并标记，不迭代至收敛，下游重算特征。DP 使用有限线段距离和已固定的索引/阈值约定；阈值为 0 的检查保留全部点，不能把它称作压缩进步。

`source_crs=UNVERIFIED`。固定工作模型为椭球 `a=6378137、rf=298.257223563`，`h=0`，ENU 原点 `(121.343555°,31.3561015°)`。这是一项有说明的条件化数学分析，不是数据源 datum 认证。距离、累计长度和 DP 误差的单位均为工作米。坐标公式、域与浮点余量见 [合同](../../config/goal3/contract.json)；不得改 EPSG 标签或按处理得分选择坐标模型。

## 4. 指标、接受条件和结果解释

共同参考由固定 raw 窗口构成。S/D 及组合的替换逐记录检查原始点覆盖集合包含关系、参考已覆盖集合上的 max 几何非退化、原有非空记录与窗口身份、零原始断点跨越，以及实际 P 预算。既比较 R0，也比较该轮 incumbent；任一记录退化不能被其他记录的平均收益抵消。至少一项主要读数严格改善才替换，无法比较的 `null` 不算几何改善。

P 专项只比较完全相同的完整 P 输入，统一实际误差预算为 5 工作米；只有输出点数更少且全部保护通过才构成压缩改进。上游不同的自身 clean 压缩率仅作描述，不能把 S/D 的覆盖增益归给 P。

共同覆盖不是最终存储点数，几何保护不是噪声识别准确率。新增覆盖的误差、短段与零位移相邻信息单列；这些诊断不提供真实噪声标签。工程 `VERIFIED` 与研究 `SUPPORTED_WITHIN_SCOPE / TRADEOFF / NO_DEMONSTRATED_GAIN / REJECTED_BY_CONSTRAINT` 分开。

## 5. 数据隔离、有限候选与实际选择

| 分区 | 记录数 | 身份 |
|---|---:|---|
| PILOT_REGRESSION | 7 | 既有暴露样本 |
| DEMO_MEMORY | 60 | 冻结示范记忆来源 |
| G3_DEVELOPMENT | 240 | 已有 DEVELOPMENT 与已暴露 G2_EVAL |
| G3_SELECTION | 240 | 预先描述性分层、稳定哈希抽取；选择后已暴露 |
| FINAL_CONFIRM | 600 | 预先按完整记录组稳定等概率抽取，一次确认 |
| PRODUCTION_REMAINDER | 10,239 | 其余记录 |

分区 hash 为 `c20747b7e2869b5e3ce755601764336dcd5e42ed4643e99d5e56be7a0ebba2f0`；完整算法、独立 salt 与各层分布见 [split manifest](../../evidence/goal3/split_manifest.json)。先前已做原始结构盘点，诚实标为 `NO_DOCUMENTED_METHOD_EXPOSURE`，没有宣称绝对盲测。最终集没有进入 A、记忆或参数反馈。全量生产随后包含全部分区。

原 Goal 3 研究阶段只有 1 个新结构单项和 3 个新组合定义；既有参数证据复算与新候选分账，没有耗尽配额或扩大连续搜索。另一个删除保护没有可信定义，记为不准入；已危险顺序没有新修复机制，未重复六排列；没有为增加调用量重跑四模式。本次收尾不新增候选、组合或实验记录级 LIVE 调用。

开发真实结果：S0 相对 R0 在 107/240 条记录增加覆盖，合计 6,704 点。时间规则 G0 只有原始所有相邻时间差均满足 `0<dt<=30` 秒时才用 direction=60，其余用 35。G0 独立有条件价值但不能替代 S0；S0_G0 后来相对 S0 全保护并有 41 条几何改善，成为开发 incumbent。移除其两个父组件均有损失。

P2 及 S0_P2 在同上游下分别多保留 1,946/2,010 个点，无压缩收益，并存在整链几何退化；P10 及 S0_P10 分别有 173/178 条超过共同预算。完整四项父对照和负结果保存在 [A3 裁决](../../evidence/goal3/A3_DECISION.json)、[收敛复盘](../../evidence/goal3/CONVERGENCE_REVIEW.md) 及逐记录表中。

选择短名单冻结为 `R0→S0→G0→S0_G0`。按固定规则在新选择分区从 R0 开始：S0 全 240 保护、103 条覆盖改善，共增加 6,625 点；G0 和 S0_G0 在同样三条记录 `3017、9311、9534` 上退化。独立额外数学重算证明这是方向输出改变后 DP 选点替换造成的真实权衡，非实现错误。最终选择 S0；没有事先指定 S0 必胜，也没有把更复杂组合自动保留。

## 6. 一次性最终确认

冻结时间 `2026-09-27T05:23:51.350095+00:00`，冻结 hash `d64869cc4623b3751d365d54d2cc70305a188891c41b8c6de17b58f3fadb1e6e`，处理 CODE_SHA `e12f8a27944210adb452730be92a0674dfc6b84b`。只比较 R0 与 S0，未根据最终效果改参数、记忆或方法。

600 条记录、62,284 点全部实际执行；S0 全部保护通过，349 条严格覆盖改善。共同覆盖 `35,868→62,220`，实际存储点 `10,991→12,114`，无输出记录 `255→0`。两者即时 P 最大误差均为 `4.9971311138733405` 工作米；共同 raw 最大误差均为 `280.69670439064976` 工作米。新增覆盖点最大误差为 `6.087101997252068` 工作米，这不违反不同参考对象下的 P 即时预算，也不证明新增点干净。

[确认闭合回执](../../evidence/goal3/independent_c/confirmation_closure_receipt.json) 绑定完整 600 条、1,200 份 trace 和 2,400 行配对；另有预登记 40 条记录的 80 份 Decimal/PROJ 独立数学核验。发布规则支持 S0，预设 R0 回退未触发；这不是在最终集上选出新的赢家。

## 7. 全量生产与扩大坐标核验

全量运行 `g3-full-production-01` 已实际结束并通过[独立生产闭合审核](../../evidence/goal3/independent_c/production_closure_receipt.json)，范围为所有 11,386 条记录、1,173,410 点。R0/S0 共 22,772 次处理，0 个处理失败，新增记录级模型调用 0，运行器计时 1,763.65 秒。策略保持统一 S0，没有逐记录回退。全部处理轨迹与原始范围、点账本、配对及汇总已核验；独立 Decimal/PROJ 数学重算覆盖预登记 40 条随机记录及各实际类别代表，合并为 50 条、100 份轨迹，不将分层独立重算称作全记录数学重算。

| 全量读数 | R0 | S0 |
|---|---:|---:|
| S 过滤点 | 501,511 | 1,199 |
| D 删除点 | 36,056 | 39,732 |
| P 简化点 | 435,373 | 911,330 |
| 显式保留点 | 200,470 | 221,149 |
| 共同 raw 覆盖点 | 671,899 | 1,172,211 |
| 无输出记录 | 4,859 | 0 |
| 覆盖的原始窗口 | 15,205 | 24,764 |
| 原始断点跨越 | 0 | 0 |

每列前四项合计 1,173,410，全部原始记录和点有终态。机器配对结果为 11,386 条保护通过、6,522 条严格覆盖改善；共同覆盖增加 500,312，显式存储增加 20,679。共同 raw 最大误差两者均为 368.707060 工作米，P 即时最大误差两者均为 4.999964 工作米。这是包含开发记录的生产描述，不是新独立测试。

[新增覆盖边界独立回执](../../evidence/goal3/independent_c/new_coverage_boundary_receipt.json) 已枚举全部记录并用 Decimal/PROJ 重算最差点：record 352、原索引 105，偏差 266.016754 工作米。原窗口 `[104,105,106,107]` 被 R0 因点数不足过滤；S0 保留该窗口后，D 删除 105，P 的输入和输出均为 `[104,106,107]`，局部没有再精简。不能把此误差归给 P，不能说新增覆盖点已经干净，也不能把它归为长度不足的片段。

旧分析字段 `from_segments_shorter_than_R0_filter` 的实际定义一直是 **点数不足 5 或长度不足 65 工作米的并集**。[全量原因分解](../../evidence/goal3/full_filter_attribution.json) 从 R0 实际点账本按互斥原因重新列示：仅长度不足 492,513、仅点数不足 5,434、两者同时 2,365。新增覆盖的点终态为保留 20,679、P 简化 475,957、D 删除 3,676；[独立原因核验](../../evidence/goal3/independent_c/full_filter_attribution_receipt.json) 已从全部原始记录和最终边重新得到相同结果，没有倒写旧实验文件。

坐标程序已实际检查全部 1,173,410 点、1,162,024 条原始相邻边和 22,772 份实际 trace。PROJ 坐标最大残差 `8.148098e-10` 工作米；最远 ENU 半径约 111,906.20 工作米，位于批准域内；实际相邻工作距离与同椭球测地距离最大差约 0.452041 工作米。对实际 S 距离/长度、D 窗口及固定 P 输入的 AEQD 检查未报告阈值/保留集合差异。[独立坐标审核](../../evidence/goal3/independent_c/g3-full-production-01_coordinates_receipt.json) 核了全部点、原始邻边与实际阶段计数，并对随机、类别、极值合并的 56 条记录、112 份轨迹独立重算阶段敏感性和全部已报告阶段极值见证。未对其余每条记录再独立重算 AEQD 敏感性；该检查不等于换坐标后重跑整条链，也不能认证源 datum。

## 8. 历史SC-LAB1-G3-CLOSEOUT-001： 可复现交付与状态边界

- [基础完成版 Notebook](../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) 对应基础 starter：参数、六种顺序、评价、真实 AI 批判、构造例和全量生产。
- [系统完成版 Notebook](../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) 对应 LLM starter：真实工作流、四模式、记忆边界与保存提议的离线重算。
- [Experiment Report 源](../../reports/experiment1/experiment1.tex) / [PDF](../../reports/experiment1/experiment1.pdf)；[Process Report 源](../../reports/process1/process1.tex) / [PDF](../../reports/process1/process1.pdf)。本次已构建为 22/12 个 PDF 物理页，当前字节、页数、提取和渲染入口见 [build_receipt.json](../../evidence/goal3/report_build/build_receipt.json)。模板原件不覆盖，正式数字与图从核验产物绑定生成；新页的实际视觉审核按本次 C 回执范围判断。
- [Experiment 分页文本](../../evidence/goal3/report_build/experiment1_pages.txt)、[Process 分页文本](../../evidence/goal3/report_build/process1_pages.txt) 和 [200 dpi 逐页图](../../evidence/goal3/report_build/render200/) 供网页 GPT 直接检查；实际 cell/source hash/PDF 物理页定位见 [教师作业导航](../../evidence/goal3/teacher_delivery_mapping.md)。提取成功或 hash 一致本身不构成逐页目视通过。
- [图源](../../goal3/figures.py) 与 [正式图目录](../../figures/goal3/) 保留 SVG/PDF/PNG、数据与实际工作流 `.drawio`；没有底图或生成式数据图。
- [Interaction Handoff](INTERACTION_HANDOFF.md) 和 [本次原件/spec/Lock 盘点](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/b_handoff/evidence_inventory.md) 保存可得事实与真正缺项，不代替 Evidence Master 的 Tier、caption、裁切、箭头或 LOCK。
- [四块复盘指南](REVIEW_GUIDE.md)、[运行与答辩说明](DEFENSE_NOTES.md)、[要求总账](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md)、[教学差异](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/TEACHING_DIFFERENCES.md) 和 [文献使用表](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/literature_use_map.md) 用于随后讲解；不把用户 Understanding 自动设为 PASS。

默认 `FULL_RECOMPUTE` 实际重算历史参数/顺序 9,720 次、模式候选 6,001 次及 384 个原有 record–episode 选择，然后从全部原始数据重算冻结生产策略并重新画图。历史提议按 `RECOMPUTE` 身份重放，不冒充新 LIVE。`LIVE` 必须显式开启、使用新 run 和原有合法认证；默认不调用。`REPORT_BUILD` 先核验完整生产闭合和实际来源，再构建数值摘要、图、报告与新 REVIEW_ONLY ZIP；它拒绝覆盖已有包，新包仍须全页视觉检查和隔离 FULL 复算。详细入口与依赖见主 README。

**原阶段的四次 FULL 与旧 ZIP 是历史证据。** 原仓库[基础本](../../evidence/goal3/independent_c/repository_basic_full_02_receipt.json) 12 个代码单元、9,720 次历史参数/顺序处理、19 条构造处理链、1 条已暴露 pilot、22,772 次全量生产处理；原仓库[系统本](../../evidence/goal3/independent_c/repository_system_full_02_current_receipt.json) 8 个代码单元、6,001 次历史候选处理、384 个历史 episode 选择核对。两者当时的 Provider 哨兵观测新增调用均为 0，raw 与冻结记忆字节不变。原基础复算 Git 身份为 `0b20be8e4142e8e62246e9357993e83951833e4f`，32 个数值源码与正式生产的 `e12f8a2` 完全相同；这不是本次身份更新后的新执行回执。

历史 [REVIEW_ONLY_实验一.zip](../../submission/REVIEW_ONLY_实验一.zip) 保留原样：113 个成员（含 manifest）、21,418,989 字节、SHA256 `97d5dbe2d7a5c87d09bcb21ae5798fa0b76374fabdd03f25447fb87c4f27c447`。该旧包的[基础本 FULL](../../evidence/goal3/notebook_verification/isolated_basic_full_01/execution_receipt.json) 为 12/12 单元、2,811.70 秒，[系统本 FULL](../../evidence/goal3/notebook_verification/isolated_system_full_01/execution_receipt.json) 为 8/8 单元、534.86 秒；当时两者均实际完成且 Provider attempts=0。原包使用同一项目依赖环境，源码/配置/输入来自真实解压目录，没有 `.git` 时采用 `FROZEN_SOURCE_BUNDLE`。这些旧字节与旧审核不自动适用于本次新包。

<!-- CLOSEOUT_CURRENT_EXECUTION_STATUS -->
**本次四次新内核 FULL 均已实际完成。** 两个 Notebook 分别在仓库和同一 ZIP 的实际解压目录运行，完整回执与单元输出保存在 [closeout/notebooks](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/)。其独立核查以本次 C 的[四次 FULL 回执](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/notebook_runs_receipt.json)为准，不用旧四次 FULL 或静态 probe 代替。

| 位置与 Notebook | 实际新内核执行 | FULL 范围 | 本轮执行证据 |
|---|---|---|---|
| 仓库基础本 | 12/12；3260.13秒；新增记录级调用0 | 9,720次参数/顺序；19条构造链、1条已暴露pilot；11,386条/1,173,410点，R0/S0共22,772次全量处理 | [新内核执行](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/repository_basic_retry/execution_receipt.json) / [计算规模](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/repository_basic_retry/artifacts/notebook_receipt.json) |
| 仓库系统本 | 8/8；712.26秒；新增记录级调用0 | 6,001次历史候选处理；384个原有record–episode选择 | [新内核执行](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/repository_system/execution_receipt.json) / [计算规模](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/repository_system/artifacts/notebook_receipt.json) |
| 同一实际 ZIP 解压基础本 | 12/12；3357.02秒；新增记录级调用0 | 9,720次参数/顺序；19条构造链、1条已暴露pilot；11,386条/1,173,410点，R0/S0共22,772次全量处理 | [新内核执行](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/isolated_basic/execution_receipt.json) / [计算规模](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/isolated_basic/artifacts/notebook_receipt.json) |
| 同一实际 ZIP 解压系统本 | 8/8；628.04秒；新增记录级调用0 | 6,001次历史候选处理；384个原有record–episode选择 | [新内核执行](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/isolated_system_retry/execution_receipt.json) / [计算规模](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/isolated_system_retry/artifacts/notebook_receipt.json) |

原仓库基础本和原解压系统本分别在10/12、2/8代码单元后观测SIGTERM/143，没有完整执行回执，不计FULL成功。两次中断的触发来源仍未确认；本次未将它们解释成数学缺陷。保留[中断与部分产物](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/notebook_interruptions.json)，对相同Notebook、数值源码和输入使用新内核、新目录重试，以上两份成功重试均实际exit0。未切换Mock、缩小样本或把历史输出当作重跑。独立C另核对真实分片、逐点终态、原始记录范围、历史注册表、只读记忆和Provider观察；本轮观察到的新增记录级模型调用为0。
<!-- END_CLOSEOUT_CURRENT_EXECUTION_STATUS -->

本次具名待审文件为 [REVIEW_ONLY_10245102410_吴博闻_实验一.zip](../../submission/REVIEW_ONLY_10245102410_吴博闻_实验一.zip)，116 个成员、15,776,719 字节，SHA256 `efa6d259a45cf5c89725c4ebe3d2f02f5b3e1c6ca82c4672de2a6fd4ae78ecc0`。当前包已真实构建与解压完成静态检查；[PACKAGE_VALIDATION](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/PACKAGE_VALIDATION.json)登记当前内容、身份和 PDF，独立 C 的[成员检查](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/package_receipt.json)与[执行输入等价检查](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/package_execution_equivalence.json)分别保留。

实际 FULL 解压输入包已原样保存在本次 `executed_package/`，其 SHA256 为 `61fee89775b751233e1aa5f969f957c8278aebd07e390f592fe58043a8b3e8b6`。当前包只改 Experiment PDF 和 manifest：113 个非 PDF payload 成员与其完全相同，Process PDF 也未变。因此可按当前授权绑定同字节 Notebook/完整依赖/输入的实际执行证据；不能把这次报告修订称为又一次 FULL 执行。完整 FULL 与 C 复验仍以本节实际回执为准。正式目标名 `10245102410_吴博闻_实验一.zip` 仅供用户最终确认后使用，本轮仍为 `REVIEW_ONLY / NOT_READY`。

源码、完整 trace、失败记录、报告 LaTeX、图源与独立审核继续留在 GitHub；教师最小包保留 PDF、完成版 Notebook 和必需运行闭包，两者职责分开。本次身份生成与冻结核验见 [独立 C 回执](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/frozen_identity_receipt.json)。身份输入依赖已关闭；Process 正式互动原件/spec/Lock 仍缺，不能将完整正式过程报告宣布完成。

当前状态分别保持：Identity=`VERIFIED`；Process Evidence=`BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK`；Deliverable=`FINAL_REVIEW`；Understanding=`LEARNING`；Submission=`NOT_READY`；新的 GPT_SECOND_REVIEW=`PENDING`。工程验收与发布进度由本次收尾回执登记，不由本 Handoff 自立“全部 PASS”。没有发送邮件或上传教学平台；本次截至该编辑节点未新增系统包、语言包、工具链、字体或持久环境配置。

## 9. 历史SC-LAB1-G3-CLOSEOUT-001： 审核版本入口

`NUMERIC_CODE_SHA=e12f8a27944210adb452730be92a0674dfc6b84b` 仍指原选择、确认及生产的真实代码；冻结继续绑定原件、合同、分区、源码和只读记忆。本次 C 对冻结来源的检查和数值摘要等价核对分别保存在 [冻结/身份回执](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/frozen_identity_receipt.json) 与 [摘要等价回执](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/result_summary_equivalence.json)，不把文档提交 HEAD 改称原数值代码。

原结果 `ARTIFACT_SHA=fd559e451291b9d424682853ef0909aa5eb94b32` 与原交付锚点 `1a5e26b43189aef64a46f8986b3cc442fa50d2c5` 属于历史版本；原 [PUBLICATION_RECORD.json](../../evidence/goal3/PUBLICATION_RECORD.json) 只证明其登记范围内的真实发布。新报告、新具名包与本次四次复现不直接继承旧发布或网页验收结论。

本次 `DOCUMENT_BUILD_CODE_SHA`、`PACKAGE_CONTENT_ID`、最终交付提交、Local HEAD/origin/main/Remote SHA 及固定 SHA 回读，以 [本次收尾目录](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/) 中最终发布记录和 `FINAL_RESPONSE.md` 为准；包的当前内容绑定见 `PACKAGE_VALIDATION.json`。报告 PDF、分页文本/页图和当前 teacher_delivery_mapping 分别通过 [build_receipt](../../evidence/goal3/report_build/build_receipt.json) 及其实际 hash 绑定，不预填尚未产生的自身提交 SHA。新的网页 GPT 文档/包二重验收始终 `PENDING`，直到它实际读取远程成果并完成审核。
