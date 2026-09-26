# Goal 1 数据、方法、评价与权限合同

机器版本：[goal1.json](../../config/goal1.json)。每项语义保留 value/status/source/verification/affected_operations；CURRENT PROMPT 明确许可的规则标已批准，来源事实标 SOURCE_DECLARED/VERIFIED，研究草案绝不改标 USER_APPROVED。

## 1. 数据与未决项

顶层键作为原始记录标识；补充学生讲义第4页把相同 JSON 样例声明为车辆 ID、Unix 秒、(经度,纬度) 度数。结构事实可以核实，车辆身份/采样机制的外部真实性并无独立证明。时间顺序按原样读取；时区未知只阻断本地钟点解释，不阻断相对时间差。

**U01_CRS_DISTANCE：BLOCKED。** 教师 PPT 第13页正文泛述 WGS84，备注泛述 GCJ02，均未绑定这份数据；Notebook 函数名不能消除冲突。Notebook 分段/DP 使用 Mercator，而旧 traj_agent 使用31.23°N局部椭球平面。这两者也不是同一距离。真实距离、速度、空间分段、长度过滤、方向去噪和米制 DP 均不运行；不以构造数据冒充真实验收，不叠加底图。需先确认数据 CRS 与允许的距离口径。

**U02_DIRECTION_EXECUTION：BLOCKED。** 教师 PPT20 能确认 d_i=bearing(p_i,p_(i+1))，内部点满足 circular_difference(d_i,d_(i-1))>θ 且 circular_difference(d_i,d_(i+1))>θ 才为候选。无法据此确定同时标记、边删边算、还是重算迭代；最后方向与零位移邻域也未明确。两组真实执行的构造反例见 [direction_ambiguity_fixtures.json](../../evidence/goal1/materials/direction_ambiguity_fixtures.json)。`direction_candidates` 仅检查可算窗口并报告候选，不删除；`denoise_trajectory` 缺少明确注册方法时抛出 MethodUnresolved；本次新增单次同时删除候选只在构造平面链中验证，生产入口仍需独立批准。规则核实不等于删除调度已批准。

没有独立标签/参考轨迹。重复位置不自动等于噪声；零时间差速度不可计算，零位移方向不可计算。原始数值、顺序和点索引不得改写。禁止平滑、插值、折叠停留时间、地图匹配。历史案例352的“170点3秒4时间值”与当前数据不符，不能继续作为事实；本轮结构检查为170点、54时间值、跨度543原始秒。

## 2. 基线与参数

参考顺序沿基础 Notebook Cell10：分段→短片段过滤→方向去噪→DP。它不是最优顺序结论。当前正式链阻断；明确数学原语在平面构造输入上验证。

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
| 最大误差/超界点 | 每个输入点只对其原始索引区间的相邻保留线段测距，最大值与逐点超界 | 平面单位/误差越小/所有reference点 | 空reference不可用，真实米制阻断；不得全轨迹最近段掩盖回头误差 | 独立几何保真；evaluation._direct_distance/verify_simplification |
| 长度变化 | L_output-L_reference及 L_output/L_reference-1；各段内部求和 | 平面单位/无单独优劣/reference长度 | 零长度相对值=null+ZERO_REFERENCE_LENGTH | 描述性，不代表真值恢复；verify_simplification |
| 时间/位置诊断 | 原始相邻边 dt符号、>30、同时间不同位置、精确重复位置 | 秒、边数/描述性/全部原始边 | 无可靠单位仅报raw；非有限单列不从分母消失 | 原始结构，非物理质量；diagnostics.profile/aggregate |
| 可计算性 | 可算速度/方向边数 / 全部输入边数，附不可算原因 | 计数与分母/覆盖更高不代表更正确 | 零dt、负dt、缺失/不可靠时间与零位移分别记录 | 使用范围；geometry.recompute_features |
| 耗时 | 控制器perf_counter工具/模型实际耗时 | 秒/描述性/该调用 | 非性能基准 | 当前执行成本；controller/provider receipts |
| 模型/工具/状态 | 实际call/session/tool ID、用量（可见时）、执行/拒绝/升级/恢复 | 次/无单独优劣/所有尝试含失败 | 缺快照/请求ID记unavailable | 执行真实性与反馈能力；events.jsonl/checkpoint |

旧综合目标函数和 regret 不参与新审核。无标签不得输出检测准确率、误删率或恢复真值。搜索未在本轮执行；未来预算内参照不得称全球最优。

## 4. 三层裁决与下一阶段

工程层：已知答案、硬条件、独立重算决定 VERIFIED/REJECTED。任务质量层：真实三步处理仍BLOCKED。改进层：硬条件 AND 主要收益达预先门槛 AND 保护项无不可接受退化 AND 比较有效/证据足够；目前收益门槛、退化额度、选择数据未冻结，统一 PENDING_RESEARCH_REVIEW。

现有 `assess_improvement` 只执行上述逻辑；其构造测试中出现的数字是 ENGINEERING_TEST，不会写回批准合同。运行时 Agent 无权修改合同、方法、输入、审核代码、历史结果或留出集。新算法、参数扫描、组合、全量清洗、最终选择和正式报告均保持Goal2/3边界。

## SC-LAB1-G1-REPAIR-001 工程补充

完整提交列表先检查字段、唯一性和精确集合，再允许重排。新 `contract_snapshot` 仅说明保存合同；`source_check` 核读白名单来源的真实片段，不能确认未知 datum。反馈要求当前审核 call 与其 VERIFIED 工具回执，检查文件hash、run和原始父版本。

`pipeline.py` 连接分段→独立过滤→注册方向方法→DP→独立审核→逐点账本。真实入口从教师JSON出发，只有研究批准后登记的 REAL_CONTRACTS/坐标适配器可执行；目前为空，D1/D2与参数均未冻结。

旧预算和历史 live_stop 原样保留。新批次只按修复 Prompt 与最终离线测试授权6次外层派发（1探针＋最多5角色）、12工具、180秒、串行且无自动重提。CLI0.157.1内置openai不能通过同名provider覆盖重试值；实时观察首个异常即杀进程组，底层请求数仍unknown。详见修复审阅入口。
