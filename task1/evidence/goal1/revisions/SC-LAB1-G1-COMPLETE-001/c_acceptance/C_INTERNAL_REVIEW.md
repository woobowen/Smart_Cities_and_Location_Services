# C 独立内部总验收

Goal：`SC-LAB1-G1-FOUNDATION-001`；执行：`SC-LAB1-G1-COMPLETE-001`；审核者：`C:/root/c_acceptance`。

**内部工程验收通过，范围为用户批准的固定真实 pilot 条件化分析。** 有效运行仅为 `g1-complete-pilot-03`，处理核心 CODE 为 `f229d9a4113bcc0dd763e1b410f1f5fb73903a62`。当前具备登记九项内部任务和进行正常发布的工程证据。此结论不表示已经 push，不替代 GPT 远程二重审核、用户理解确认或教师提交。

`source_crs=UNVERIFIED`、`source_datum_proven=false`。D2 的一次标记、同时删除已获用户批准；固定局部模型是分析假设，不是源 datum 证明。G2/G3 `NOT_RUN`，`GPT_SECOND_REVIEW=PENDING`，`Submission=NOT_READY`。两份正式报告仍为工作材料，未宣称正式定稿。

## 审核方法与职责

C 先查看目录，读取当前授权补充、USER_DECISIONS、原 COMPLETE 指令、AGENTS、合同、A TaskPlan 与真实老师来源。C 仅在本目录写自己的 probe、固定快照和回执，没有改动原始数据、合同、受审核心或候选产物。原生角色的只读约束来自任务授权与文件差异检查，不宣称存在独立 OS 沙盒。

`independent_probe.py` 不导入生产 workflow。它从实际 raw JSON 和已批准合同出发，逐记录核对783点原值、派生工作坐标、时间与空间切分、过滤原因、方向窗口与实际同时删除、父版本、清洗后相邻关系、递归 DP 实际保留索引；另以 Decimal 55 位有限线段计算检查461个 clean 点对应的实际保留索引区间。完整逐点账本、外部 JSONL 和全局/逐记录汇总一起比较。老师 PPT 摘录从原 ZIP/XML 的普通文本及 Office Math 文本重新提取核对。

`remaining_probe.py` 从 raw 独立核对 profile、完整重复事件和严格时间切分；检查四个实际 artifact/review 的目标、文件与对象 hash、可信参考、scope、checked/unchecked、源文件及处理 commit 的对应字节。后续敏感性逐行与 C 自己的坐标、距离、方向及 DP 结果比较。

既有 C 缺陷角色的37项手工反例与控制器拒绝/恢复检查用于对应工程接口，不冒充本 C 独立数学计算。该早期回执涉及后来修正的三个源码 hash，因此同时绑定本 C 的数值舍入、同轴方向和时间范围修复回执、最终核心测试与实际 run03 复核，未将旧回执整体当作最终源码 hash。

## 实际数值与局限

完整 raw 文件结构读取到11386条记录、1173410点；实际处理范围始终为固定七条记录 `0,1,2,246,256,306,352`，共783点。不存在全量清洗声明。

| 记录 | 输入 | 切分段 | 过滤 | 方向删除 | DP参考 | DP省略 | 最终保留 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 99 | 1 | 99 | 0 | 0 | 0 | 0 |
| 1 | 97 | 1 | 97 | 0 | 0 | 0 | 0 |
| 2 | 99 | 1 | 99 | 0 | 0 | 0 | 0 |
| 246 | 108 | 1 | 0 | 3 | 105 | 69 | 36 |
| 256 | 99 | 9 | 0 | 0 | 99 | 45 | 54 |
| 306 | 111 | 11 | 4 | 2 | 105 | 36 | 69 |
| 352 | 170 | 6 | 10 | 8 | 152 | 123 | 29 |
| 合计 | 783 | 30 | 309 | 13 | 461 | 273 | 188 |

30段中7段过滤、23段处理；所有783点恰有一个终态。实际原值修改0、未处理0。记录0/1/2真实全过滤，其 DP 质量指标明确不可计算。DP 省点率为 `1-188/461=0.5921908893709328`；raw 到 final 总点数减少 `1-188/783=0.7598978288633461`，没有混入 DP 收益。

最大片段索引区间误差在 record306/segment0/original_index2，C Decimal 核对为4.938319812632412工作米，生产二进制浮点报告4.938319812632411米；距5米阈值约0.0616801874米。固定数值余量随尺度为约8.10e-11至4.07e-10米，没有放松5米参数。不得用去点数量或该条件几何误差推断真实恢复准确率或质量提升。

独立 PROJ cart/topocentric 核对全部783坐标，最大实现差3.637978807091713e-12米。固定椭球上45457个记录内点对，ENU 与椭球距离最大相对差1.1826369614622246e-5，最大绝对差0.036456552836170886米，实际最大模型半径31131.317939847395米。776条原始相邻边、30段、474个方向窗口（194个不可计算）、23个实际 DP 段均纳入敏感性检查。400米、65米、35度、不可计算窗口与5米实际区间判定差异均为0。

方向敏感性使用同中心 AEQD 的 grid heading；DP 在相同实际保留索引区间上核对，未运行另一种去噪策略或重新挑参。两模型共享数学椭球假设，有限 pilot 一致性不能证明 datum、offset、绝对定位或地面真值。

## 实际闭环与失败保留

五个实际问题均有问题登记、修复执行者消费、修复回执、C 独立复验及父任务恢复事件：C2-F01、C2-F02、NUMERIC:g1-complete-pilot-01:baseline、C3-COORDINATE-DIRECTION、C3-TIME-SCOPE。79条审核时 journal 事件的 hash 链已核对。旧run01运行审核拒绝保留；run02数值通过但范围文案被新版本替代，旧字节未热替换。有效run03重新执行全部四目标。

圆周角派生数值的修复仅允许两个报告角差的固定 `64*epsilon*360` 舍入余量，候选布尔值、索引、原因、35度严格阈值、实际删留和 DP 几何仍严格核验。本 C 另做14项实际候选专项检查，未引入相对候选自报数值的容差。

C 实际发现近5米余量后提出 run03 专属 follow-up request。主线程实际消费并执行 `coordinate_sensitivity`，其 parent、trigger_review、request、处理 code 和结果 hash 完整绑定。`followup_review.json` 对全部九个 required components 有实质核对且 unchecked 为空，不能用 profile 或其他审核的通过关闭该任务。

本 C 自身在最初提取 PPT 时漏取 Office Math 节点，第一次 probe 的拒绝原件保留为 `probe_development_extraction_issue.json`；修正自己的提取器后重新核对。它不是生产算法缺陷，也没有删除失败证据。

## 测试、Notebook 与图

主线程在最终处理 CODE 实际执行 `pytest task1/tests`：261 passed、0 failure/error/skip。C 核对 JUnit、实际源码 hash，并 AST 解析当前 workflow/scripts；没有把重复运行同一套生产单测当作独立数学证据。starter 292 passed/1 skipped 是依赖未变情况下保留的历史记录，未称本轮新跑。

C 实际执行：

```text
.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/c_acceptance/independent_probe.py g1-complete-pilot-03
→ VERIFIED，383项真实处理检查
.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/c_acceptance/remaining_probe.py g1-complete-pilot-03
→ VERIFIED，64项诊断/绑定检查；1322项后续敏感性检查
.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/c_acceptance/final_evidence_probe.py
→ VERIFIED，45项摘要、22项Notebook、6项最终入口检查
.venv/bin/python evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
→ EXACTLY 11，active bytes/hash 与 manifest 一致
```

上述项目是不同范围的工程检查，不累计成统计样本量或算法准确率。

B 实际以临时 kernelspec 启动两个新内核，Notebook 各8个代码单元按1–8执行，无error；C核对实际日志、全部源代码、执行输出及文件hash。Notebook01由raw重新计算 baseline 并独立审核，Notebook02四目标 fresh recompute 全部精确匹配。默认 RECOMPUTE、LIVE 显式关闭、无新增模型调用；Notebook02末尾IMPLEMENTING明确为执行时快照，后续验收登记不要求改写其历史输出。

三图的10个主文件、三个200dpi PDF渲染以及原生 SVG/PDF/draw.io源均已核对；C实际查看了三个200dpi渲染。轨迹图逐实际段连接、不跨时间/空间断点、过滤段或记录；原始点只散点显示。计数图四类互斥且总和783；架构图区分真实角色和确定性journal，并保留实际修复回路。没有生成式图、地图底图或准确率视觉暗示。Notebook嵌入的三张PNG与当前图文件字节完全一致。

图/Notebook生成器在处理CODE之后只有已审查的显示与快照说明改动，实际产物已重建/执行；生成器及输出分别按最终文件hash绑定。该 ARTIFACT 来源不假称已包含在较早 processing CODE 中。

## GC01–GC16 实际验收范围

每项的输入、命令/核验方法、预期、实际结果与文件hash详见 `acceptance_matrix.json`；该文件是本次内部审核记录，不建立第二份 active requirements 表。

| 项 | 内部结论 | 实际范围 |
|---|---|---|
| GC01 | VERIFIED | main、初始工作区、原始/历史保护、用户ZIP保留；最后push后SHA核对另记 |
| GC02 | VERIFIED | 唯一R01–R16、最新授权、受限治理diff、11-file同步 |
| GC03 | VERIFIED | A/B/C真实独立上下文和主线程实际接手执行，非单次回复改名 |
| GC04 | VERIFIED | 必需任务、依赖、问题恢复及额外follow-up控制Goal，不以第五阶段结束 |
| GC05 | VERIFIED | 五问题真实repair→C regression→重建→父任务恢复 |
| GC06 | VERIFIED | run03三诊断与baseline均有本目标hash/scope完整审核 |
| GC07 | VERIFIED | 候选外raw/固定合同、反例和当前实际baseline独立核验 |
| GC08 | VERIFIED | 未改raw、已获D2/条件化权限、datum仍UNVERIFIED |
| GC09 | VERIFIED | 真实split/filter/direction/邻接/DP区间、严格阈值和固定数值余量 |
| GC10 | VERIFIED | 固定7条783点完整真实处理，0未处理，完整ledger |
| GC11 | VERIFIED | C近阈值反馈被实际消费，九组件后续产物独立验收 |
| GC12 | VERIFIED | 累计资源、明确mode、失败/不确定状态拒绝重派与可恢复机制 |
| GC13 | VERIFIED | 最终261测试、两个新内核Notebook、真实图与独立数学复核 |
| GC14 | VERIFIED | LIVE/native、确定性复算、历史、fixture、未做范围分别标明 |
| GC15 | VERIFIED | 授权内普通工程问题已闭环；无研究层面新增方案待确认 |
| GC16 | INTERNAL_VERIFIED / PUBLICATION_NOT_RUN | 内部结果、来源版本、审查和可发布内容通过；实际push、remote等值及固定远程链接由发布后回执核对 |

## 原 G1-A01–G1-A18 对应

| 项 | 本轮实际范围/结论 |
|---|---|
| G1-A01 | VERIFIED：正确仓库main、用户工作与原始历史文件保护 |
| G1-A02 | VERIFIED：保留来源读取记录并核对本轮相关老师材料、合同和授权 |
| G1-A03 | VERIFIED：原始、历史、当前真实条件化、fixture清楚分离 |
| G1-A04 | VERIFIED：批准条件化计算权限；源datum事实仍未知，不虚构地理语义通过 |
| G1-A05 | VERIFIED：当前实际分段、过滤及逐点来源 |
| G1-A06 | VERIFIED：老师方向定义＋用户批准同时删除日程，未混用direction字段 |
| G1-A07 | VERIFIED：当前实际保留索引、有限线段DP、clean参考与容差 |
| G1-A08 | VERIFIED：重开的C2缺陷修复及当前外部可信审核；旧profile只保留旧scope |
| G1-A09 | VERIFIED：当前A/B/C实际角色及真实repair/processing职责 |
| G1-A10 | VERIFIED：权限、任务、target、source epoch和完整覆盖门控 |
| G1-A11 | VERIFIED：当前固定7条783点完整条件化baseline，非fixture替代 |
| G1-A12 | VERIFIED：近DP阈值请求、真实follow-up及完整目标验收 |
| G1-A13 | VERIFIED：拒绝/恢复/资源记录；隐含provider请求与余量unknown |
| G1-A14 | VERIFIED：RECOMPUTE、历史CLI、native协作、ENGINEERING_TEST区分 |
| G1-A15 | VERIFIED：当前两Notebook新内核实际运行并从raw复算 |
| G1-A16 | VERIFIED：三真实图、可编辑源、生成器hash与视觉检查 |
| G1-A17 | VERIFIED：未做G2/G3、参数扫描、新算法或正式报告/提交 |
| G1-A18 | INTERNAL_VERIFIED / PUBLICATION_NOT_RUN：内部审核包具备，最后同步必须另取真实远程证据 |

## 保护、资源与发布边界

A 的初始273项保护核对与初始Git blob另150项比对均已读取：teacher/raw/starter、templates、installed publication-plots、旧结果和用户两ZIP字节未变；后续当前requirements/REVIEW_PACKET更新有明确授权，旧版本原件保留。AGENTS仅+23行、Research Protocol仅+13行；Evidence Protocol和Visual System未改，11-file bundle只分发同步，不声称ChatGPT UI上传。

资源快照记录1个主会话、4个命名子角色上下文、13次显式spawn/followup派发。本轮CLI新派发0、额外付费API0；历史4+6独立保留，隐藏provider请求/精确剩余额度unknown。C本身未安装包；整个执行只新增`.venv`中的pyproj==3.7.2，安装回执存在，无系统包或持久配置修改。

最终入口A–H已全文读过，并保存只读审核快照。历史review的一处相对链接由用户已有ZIP原字节恢复，C独立比较ZIP member与恢复文件一致；没有改历史review文字或伪造新实验。

`review_receipt.json`只绑定稳定的源码、合同、raw、run、review、Notebook、图、静态授权和C快照。活动goal_state/resources、requirements/acceptance/最终入口不作为闭合任务的可变hash依赖。主线程应消费回执后登记实际任务状态，保留运行时快照；最后正常commit/push并另核验remote，不得将本回执当作已经发布的证明。
