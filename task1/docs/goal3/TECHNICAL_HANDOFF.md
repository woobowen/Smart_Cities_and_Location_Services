# Experiment 1 Technical Handoff

Goal：`SC-LAB1-G3-FINAL-001`。本轮仍是实验一。唯一剩余要求登记为 [requirements.json](../../evidence/goal3/requirements.json)，当前审阅入口为 [REVIEW_PACKET.md](../../evidence/goal3/REVIEW_PACKET.md)。完整实验一入口为 [task1/README.md](../../README.md)。

## 1. 承接、输入和研究范围

G1/G2 的阶段验收按用户转交记录保存为 `USER_RELAYED_GPT_STAGE_ACCEPTANCE`，没有补造网页审查日志。承接锚点为 `6fad8420b09ba123fe0658a5cd805cb7b7b9e67b`；G2 实际处理代码为 `c1c6272606716f9f59aa785d48bfeadb09c7a30e`，结果提交为 `1ac203c1c60b3c64490150cbd473d3091eac8564`。旧结果保留历史身份。

原始 JSON 实测 **11,386 条记录、1,173,410 点**，SHA256 为 `c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3`。原始值、教师 PPTX 和两个 starter 没有覆盖；完成版 Notebook 单独交付。完整相同记录按原值哈希分组，没有发现重复组，也没有证实记录键代表独立用户或完整行程。

范围为教师的分段、去噪、DP 简化、三组参数、顺序、评价、四模式、记忆与 AI 批判，加上本 Prompt 批准的有限选择、确认、全量生产和交付。没有新增训练、道路匹配、外部数据、坐标加偏、实验二停留点或热点任务。

## 2. 实际架构、权限和恢复接口

| 角色/层 | 实际上下文或入口 | 责任与边界 |
|---|---|---|
| A | `/root/a_candidates` | 从真实开发证据提出有限 TaskPlan，消费单项、组合与移除结果；没有读最终集来开发新候选 |
| B-Run / B-Repair | 主线程 `/root` | 运行冻结处理、接收真实问题、修正实现、测试、新 run 重建、恢复父任务 |
| B 文档工程 | `/root/b_delivery_inventory` | 教师入口、Notebook、离线复算、图与报告生成、依赖闭包及待审包 |
| 独立 C 数值/协议 | `/root/c_protocol` | 原始范围、实际产物、独立数学、保护、选择与冻结核验；没有编写待审核心实现 |
| 独立 C 文档/交付 | `/root/c_documents` | 历史事实与引用、文档结构、可移植复现、视觉和包核验 |
| 确定性控制器 | [control.py](../../goal3/control.py) | 任务依赖、问题队列、来源/产物 hash、独立关闭、失效传播和检查点；不是第四个 LLM |

[goal_state.json](../../evidence/goal3/goal_state.json) 保存真实任务与问题状态。主要接口是 `submit → accept` 和 `issue → repair → close_issue`；实际产物、独立 C 上下文和当前来源必须匹配，旧回执不能关闭新产物。运行入口拒绝已有 run 目录；中断保留明确检查点和失败原因，不静默重发不确定任务。

主要工程问题及真实修复包括：等价简化条件缺失、开发输入范围检查、错误父原始对象/合同比较、产物或源码变化后的旧回执复用、父缓存范围及异常处理、无 `.git` 的冻结复算身份、相对父缓存路径，以及阶段决策消费前的实际分片新鲜度。G3-C06/C07 改变处理源码时期后重建了受影响开发 run；旧失败和旧结果没有删除或冒充当前版本。G3-C08 只修尚未用于正式运行的阶段辅助程序，不改变数值处理时期。文档的两层归属与方向参数呈现问题也经独立复验关闭。

交付实跑还发现 Matplotlib 与 Notebook inline 接口不兼容。首个修复被独立 C 的新内核测试拒绝；第二次改用原生 `Figure`/`FigureCanvasAgg`，通过专项检查后重新执行两个完整 Notebook。原基本本失败和明确中断的系统本均保留，未计为完整复算。图例、外部依赖文字及开发阶段 C→控制器→A 反馈路径也经修正与独立检查；这些是工程问题，不是方法效果退化或质量收益。

本地 native 工具消息正文在平台日志中以加密字段保存。[治理事件索引](../../evidence/goal3/governance_tool_events.json) 只导出真实时间、工具、call ID、可得角色元数据和存储载荷哈希；不解密、不补写逐字对话。可读研究决定来自真实 TaskPlan、裁决和核验文件。底层模型请求及费用不可见，保持 `unknown`；治理调用与记录级处理分账。

## 3. 最终部署策略和坐标合同

最终策略 **S0**，统一确定性 **S-D-P**：`dt=30、distance=400、min_points=2、min_length=0、direction=35、dp=5`。教学参考 R0 仅将 `min_points/min_length` 分别设为 `5/65`，其余相同。最终记录级处理不调用 LLM，不搜索，不使用记忆，不包含逐记录候选→R0 回退。一次性确认未支持时回退 R0 的发布门控在打开最终集前已登记，本轮未触发。

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

本轮只有 1 个新结构单项和 3 个新组合定义；既有参数证据复算与新候选分账，没有耗尽配额或扩大连续搜索。另一个删除保护没有可信定义，记为不准入；已危险顺序没有新修复机制，未重复六排列；没有为增加调用量重跑四模式。

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

## 8. 可复现交付与状态边界

- [基础完成版 Notebook](../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) 对应基础 starter：参数、六种顺序、评价、真实 AI 批判、构造例和全量生产。
- [系统完成版 Notebook](../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) 对应 LLM starter：真实工作流、四模式、记忆边界与保存提议的离线重算。
- [Experiment Report 源](../../reports/experiment1/experiment1.tex) / [PDF](../../reports/experiment1/experiment1.pdf)；[Process Report 源](../../reports/process1/process1.tex) / [PDF](../../reports/process1/process1.pdf)。模板原件不覆盖，正式数字与图从核验产物绑定生成。
- [图源](../../goal3/figures.py) 与 [正式图目录](../../figures/goal3/) 保留 SVG/PDF/PNG、数据与实际工作流 `.drawio`；没有底图或生成式数据图。
- [Interaction Handoff](INTERACTION_HANDOFF.md) 是 Evidence Master 候选索引，不代替 Tier、caption、裁切、箭头或 LOCK。
- [运行与答辩说明](DEFENSE_NOTES.md) 解释方法与常见指标误读，不把用户 Understanding 自动设为 PASS。

默认 `FULL_RECOMPUTE` 实际重算历史参数/顺序 9,720 次、模式候选 6,001 次及 384 个原有 record–episode 选择，然后从全部原始数据重算冻结生产策略并重新画图。历史提议按 `RECOMPUTE` 身份重放，不冒充新 LIVE。`LIVE` 必须显式开启、使用新 run 和原有合法认证；默认不调用。`REPORT_BUILD` 先核验完整生产闭合和实际来源，再构建数值摘要、图、报告与新 REVIEW_ONLY ZIP；它拒绝覆盖已有包，新包仍须全页视觉检查和隔离 FULL 复算。详细入口与依赖见主 README。

仓库两个 Notebook 已用新内核完整执行并通过独立审核：[基础本](../../evidence/goal3/independent_c/repository_basic_full_02_receipt.json) 12 个代码单元、9,720 次历史参数/顺序处理、19 条构造处理链、1 条已暴露 pilot、22,772 次全量生产处理；[系统本](../../evidence/goal3/independent_c/repository_system_full_02_current_receipt.json) 8 个代码单元、6,001 次历史候选处理、384 个历史 episode 选择核对。两个 Provider 哨兵观测新增调用均为 0，raw 与冻结记忆字节不变。基础复算实际 Git 代码身份为 `0b20be8e4142e8e62246e9357993e83951833e4f`；32 个数值源码与正式生产的 `e12f8a2` 完全相同，不倒写成同一次运行。

源码、完整 trace、失败记录、报告 LaTeX 源、图源和独立审核留在 GitHub；教师包只含 PDF、完成版 Notebook 及实际运行所需闭包。统一 `REPORT_BUILD` 已实际成功，输出 [REVIEW_ONLY ZIP](../../submission/REVIEW_ONLY_实验一.zip)，113 个成员（含 manifest）、21,418,989 字节，SHA256 `97d5dbe2d7a5c87d09bcb21ae5798fa0b76374fabdd03f25447fb87c4f27c447`。包已在新目录真实解压并通过全部成员字节检查。包内[基础本 FULL](../../evidence/goal3/notebook_verification/isolated_basic_full_01/execution_receipt.json) 12/12 单元、2,811.70 秒，[系统本 FULL](../../evidence/goal3/notebook_verification/isolated_system_full_01/execution_receipt.json) 8/8 单元、534.86 秒，均实际完成；处理规模与对应仓库运行相同，Provider attempts=0、raw/记忆字节不变。使用同一项目依赖环境，但任务源码、配置与输入来自真实解压目录，工作目录和绘图/Jupyter 缓存均另设；没有借用原工作区的处理模块或历史汇总替代复算。无 `.git` 的包明确使用 `FROZEN_SOURCE_BUNDLE` 身份。执行回执与独立审核分别保留，不能用静态检查或进程退出码单独代替后者。

身份元数据与 Evidence Master 原图/呈现规格/LOCK 未提供，保持外部依赖。Process Report 只能是明确待补的可编译送审稿；包保持 `REVIEW_ONLY / NOT_READY`。网页 `GPT_SECOND_REVIEW=PENDING`，用户 Understanding 由用户决定，没有发送邮件或上传教学平台。本次未新增系统包、语言包、工具链或持久环境配置。

## 9. 审核版本入口

数值处理 CODE_SHA 如第 6 节；选择、确认及生产冻结均绑定原件、合同、分区、源码和只读记忆。处理代码、结果提交与最终包含发布记录的 HEAD 是不同身份。实际 ARTIFACT_SHA、远程核对与固定版本入口由 [发布记录](../../evidence/goal3/PUBLICATION_RECORD.json) 和最终回复给出，避免文件预称尚不存在的自身 SHA。
