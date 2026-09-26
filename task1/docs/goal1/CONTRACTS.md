# Goal 1 数据、方法、评价与权限合同

机器版本：[goal1.json](../../config/goal1.json)。每项语义保留 value/status/source/verification/affected_operations；CURRENT PROMPT 明确许可的规则标已批准，来源事实标 SOURCE_DECLARED/VERIFIED，研究草案绝不改标 USER_APPROVED。

## 1. 数据与未决项

顶层键作为原始记录标识；补充学生讲义第4页把相同 JSON 样例声明为车辆 ID、Unix 秒、(经度,纬度) 度数。结构事实可以核实，车辆身份/采样机制的外部真实性并无独立证明。时间顺序按原样读取；时区未知只阻断本地钟点解释，不阻断相对时间差。

**U01_CRS_DISTANCE：来源事实 UNVERIFIED；条件化分析已授权。** 教师 PPT13 的一般 WGS84/GCJ02 说明不绑定这份JSON。用户本轮明确允许在有来源支持的 (lon,lat) 度和结构事实基础上，固定局部数学模型完成开发性处理；该授权不是 datum 证明。唯一登记模型为 [conditional_planar.json](../../config/conditional_planar.json)：数学椭球 a=6378137m、1/f=298.257223563、假设h=0，原始角坐标→ECEF→固定中心(121.343555°,31.3561015°)的East/North切平面。中心取固定pilot包围盒中点，在计算结果之前确定；不贴源EPSG、不做加偏转换。原始值和派生坐标、适配器版本、raw→working关系分别保存。PROJ独立核对公式，同数学椭球测地距离及AEQD只用于近似误差/阈值敏感性，不能证明来源或地面精度。

**U02_DIRECTION_EXECUTION：USER_APPROVED。** [用户补充原文](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)明确批准：分段输入一次计算教师双侧环形方向差谓词，完整标记后同时删除；首尾、缺必要方向和零位移窗口保留并标记，不迭代，下游重算。它是本次教学参考实现，不是教师明确过所有细节或最优性结论。旧调度歧义反例保留为历史；构造approval不能解锁真实输入。

没有独立标签/参考轨迹。重复位置不自动等于噪声；零时间差速度不可计算，零位移方向不可计算。原始数值、顺序和点索引不得改写。禁止平滑、插值、折叠停留时间、地图匹配。历史案例352的“170点3秒4时间值”与当前数据不符，不能继续作为事实；本轮结构检查为170点、54时间值、跨度543原始秒。

## 2. 基线与参数

参考顺序沿基础 Notebook Cell10：分段→短片段过滤→方向去噪→DP。它不是最优顺序结论。固定七条的条件化链已获授权，最终实际状态以当前运行与独立审核回执为准。

分段：dt>阈值 或距离>阈值在该边右点前切开；负dt独立记原因；等号不切。右点属于新段，不复制边界点，不跨记录连线。短段过滤另行判点数<5、段内累计长度<65，分别保留原因，切断边不计入任何片段长度。`time_boundaries` 是允许的真实时间诊断，列索引分区而不做空间切分或删点，不能称完整教学分段。

DP：有限线段距离，保留首尾，返回原始索引有序子序列；阈值相等不递归；零容差沿已有栈实现保留所有点（合法但不声称最简）。退化线段用到端点距离。邻接关系变化后时间差/距离/速度/方向全部由新索引重算。几何平面坐标不能直接传入未确认经纬度作为米。

65/5/30/400/35/5 均来自基础 Notebook Cell1，分别为长度/点数/秒/意图米/度/意图米，标 STARTER_REFERENCE，不是已批准最优或冻结参数。PPT24 的95m是25 km/h骑行、12秒采样示例，不能与400混为同一配置。

浮点审核固定为 `64 * binary64_epsilon * max(1, coordinate_extent, absolute_coordinate, tolerance)`；考虑减法和向量运算舍入，测试前固定，记录实际值，不加到算法阈值上。极端范围不可表示时拒绝，不扩大容差补救。

## 3. 指标登记

| 指标 | 对象/参考/定义 | 单位/方向/分母 | 适用与不可用 | 可支持结论/位置 |
|---|---|---|---|---|
| 输入与去向 | 所有原始(record,index)恰好归入过滤/去噪/简化/保留之一；阻断另计未处理 | 点/无优劣/全部输入 | 原始对齐，缺失亦保留问题 | 守恒与改值检查；evaluation.audit_point_accounting |
| 片段与过滤 | 切分边右归，过滤理由逐段，段内长度 | 条、点、平面单位/描述性/全部片段 | 真实长度须U01解决 | 结构保留与损失；geometry.split_trajectory/filter_segments |
| 删除/改值 | 按原始索引计各阶段损失与数值差异；本轮改值必须0 | 点/改值硬约束0/全体输入 | 不推断误删率 | 修改范围与追踪；audit_point_accounting |
| saving | 1-N_simplified/N_reference，reference为相同简化前输入 | 无量纲/越高只代表压缩/简化前点数 | 空reference=null+EMPTY_REFERENCE_DENOMINATOR | 压缩，不代表准确率；verify_simplification |
| 最大误差/超界点 | 每个输入点只对其原始索引区间的相邻保留线段测距，最大值与逐点超界 | 平面单位/误差越小/所有reference点 | 空reference不可用，真实结果仅限条件化工作平面；不得全轨迹最近段掩盖回头误差 | 独立几何保真；evaluation._direct_distance/verify_simplification |
| 长度变化 | L_output-L_reference及 L_output/L_reference-1；各段内部求和 | 平面单位/无单独优劣/reference长度 | 零长度相对值=null+ZERO_REFERENCE_LENGTH | 描述性，不代表真值恢复；verify_simplification |
| 时间/位置诊断 | 原始相邻边 dt符号、>30、同时间不同位置、精确重复位置 | 秒、边数/描述性/全部原始边 | 无可靠单位仅报raw；非有限单列不从分母消失 | 原始结构，非物理质量；diagnostics.profile/aggregate |
| 可计算性 | 可算速度/方向边数 / 全部输入边数，附不可算原因 | 计数与分母/覆盖更高不代表更正确 | 零dt、负dt、缺失/不可靠时间与零位移分别记录 | 使用范围；geometry.recompute_features |
| 耗时 | 控制器perf_counter工具/模型实际耗时 | 秒/描述性/该调用 | 非性能基准 | 当前执行成本；controller/provider receipts |
| 模型/工具/状态 | 实际call/session/tool ID、用量（可见时）、执行/拒绝/升级/恢复 | 次/无单独优劣/所有尝试含失败 | 缺快照/请求ID记unavailable | 执行真实性与反馈能力；events.jsonl/checkpoint |

旧综合目标函数和 regret 不参与新审核。无标签不得输出检测准确率、误删率或恢复真值。搜索未在本轮执行；未来预算内参照不得称全球最优。

## 4. 三层裁决与下一阶段

工程层：已知答案、硬条件、独立重算决定 VERIFIED/REJECTED。任务质量层：条件化真实三步处理按当前产物审核，源datum仍未证实。改进层：硬条件 AND 主要收益达预先门槛 AND 保护项无不可接受退化 AND 比较有效/证据足够；目前收益门槛、退化额度、选择数据未冻结，统一 PENDING_RESEARCH_REVIEW。

现有 `assess_improvement` 只执行上述逻辑；其构造测试中出现的数字是 ENGINEERING_TEST，不会写回批准合同。运行时 Agent 无权修改合同、方法、输入、审核代码、历史结果或留出集。新算法、参数扫描、组合、全量清洗、最终选择和正式报告均保持Goal2/3边界。

## 历史 SC-LAB1-G1-REPAIR-001 工程补充（旧批次范围，不控制新授权）

完整提交列表先检查字段、唯一性和精确集合，再允许重排。新 `contract_snapshot` 仅说明保存合同；`source_check` 核读白名单来源的真实片段，不能确认未知 datum。反馈要求当前审核 call 与其 VERIFIED 工具回执，检查文件hash、run和原始父版本。

`pipeline.py` 连接分段→独立过滤→注册方向方法→DP→独立审核→逐点账本。真实入口从教师JSON出发，只有研究批准后登记的 REAL_CONTRACTS/坐标适配器可执行；目前为空，D1/D2与参数均未冻结。

旧预算和历史 live_stop 原样保留。新批次只按修复 Prompt 与最终离线测试授权6次外层派发（1探针＋最多5角色）、12工具、180秒、串行且无自动重提。CLI0.157.1内置openai不能通过同名provider覆盖重试值；实时观察首个异常即杀进程组，底层请求数仍unknown。详见修复审阅入口。

## 当前 COMPLETE 工程合同

唯一当前任务由 COMPLETE 初始指令与补充授权共同确定。[用户决定](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json)绑定原文hash；固定条件合同由代码allowlist和文件hash绑定，不接受模型修改状态字符串自批。`review_baseline(candidate, trusted_complete_inputs, approved_contract, trusted_provenance)`缺可信参数即拒绝。C核对实际源记录、参数/单位/顺序、边界与过滤、方向窗口、实际clean/final值、区间DP误差、逐点终态及全部汇总。

审核回执绑定控制器解析的artifact ID/文件hash/output hash、raw来源、完整record scope、合同版本与checked/unchecked。`recompute_check`按登记的具体目标核验，不把profiles通过充当其他产物的审核。缺覆盖、旧run、变更源码或未闭合问题不能关闭父任务。

[GoalJournal](../../workflow/goal.py)维护同一Goal的依赖/问题/修复/恢复，B实际消费修复，C独立复验后恢复父任务。历史五阶段仅为受限调度片段。新执行通过原生Codex角色协作，原4次与后续6次CLI批次预算和失败完整保留，新增资源在本轮resources.json累计，不伪造精确内部请求数。当前Run All默认RECOMPUTE，不调用模型。
