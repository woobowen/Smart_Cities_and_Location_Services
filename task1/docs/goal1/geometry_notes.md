# Goal 1 平面几何与独立审核器

本页说明平面几何内核、独立审核以及历史构造测试。当前真实 pilot 通过另行登记的局部 ENU 适配器进入相同内核；source CRS 仍为 UNVERIFIED，D2 一次标记同时删除已获用户批准。条件化分析的合同、有效运行和限制见 [CONTRACTS](CONTRACTS.md) 与 [当前审阅入口](../../evidence/goal1/REVIEW_PACKET.md)，不能把构造测试当成真实结果。

## 来源、复用与保留

- 教师基础 Notebook 的工作顺序为分段→去噪→简化；原文件及保存输出不改动。完整可读提取见 [Notebook source/outputs](../../evidence/goal1/materials/notebook_02_source_outputs.md)。
- Notebook Cell 1 是 `65 / 5 / 30 / 400 / 35 / 5` 的初始化出处；本内核不预填任何研究参数。Cell 2 生成的是 `[timestamps, coordinates, velocities, directions]`，而后续 TODO 注释把后两字段写反。因此新工作模块使用具名字段和边的原始索引。
- [starter simplify.py](../../作业/作业/traj_agent/core/simplify.py) 的迭代栈思路、首尾保留和零容差保留全部点行为被最小复用；不直接 import 其默认投影，不使用其自报误差作为独立真值。旧源文件完整保留。
- [教师 PPT 文字提取](../../evidence/goal1/materials/pptx_05_text_and_notes.md) 的第 20 页及主线程的图示核查支持三条相邻出边方向的双比较关系。该支持不自动补全删除顺序、迭代、末端方向或零位移规则。

## 接口与数学口径

[geometry.py](../../workflow/geometry.py) 接受单记录 `record_id / indices / timestamps / xy`。`indices` 是唯一严格递增的原始点编号，`xy` 必须是显式平面二维输入。`timestamps` 可以含 `None`，但依赖时间的操作会拦截或报告不可计算。

| 接口 | 已固定的工程行为 |
|---|---|
| `point_segment_distance(p, a, b)` | 投影距离钳到有限线段；退化线段退化为点到端点距离。反例 `(2,1)` 到 `(0,0)–(1,0)` 是 `sqrt(2)`。单位只是输入平面单位。 |
| `angular_difference(a,b)` | `abs(((a mod 360) - (b mod 360) + 180) mod 360 - 180)`；范围 `[0,180]`，支持负角与多圈角。 |
| `recompute_features(record,time_reliable=...)` | 从当前相邻点重算 `dt/distance/speed/direction_degrees`，按 `from_index/to_index` 对齐。方向是以 `+y` 为零、顺时针的平面方向，不能冒充已核实地理方位。 |
| `select_indices(record,indices,...)` | 按原始编号取有序子序列，保持时间和坐标原值，独立复制坐标，再重算依赖字段，不从浮点坐标反查。 |
| `split_trajectory(record,dt_threshold,dist_threshold,...)` | 阈值严格 `>` 切分，等号保留同段；负 `dt` 独立记录；边界右点是新段首点；每个输入点恰归属一段。`None` 可以显式停用一种边界条件。 |
| `filter_segments(segments,min_points,min_length,...)` | 分段之后独立过滤；点数或段内累计欧氏长度严格小于阈值时过滤，等号保留。两个原因分别保存，不把断点跳跃距离计入段长。 |
| `douglas_peucker_indices(points,tolerance,indices=...)` | 有限线段 DP，保留首尾，最大偏差严格大于阈值才继续细分；相等可压缩。返回原始索引，不用坐标相等映射重复点。零容差沿用 starter 身份输出。 |
| `direction_candidates(record,threshold)` | 同时计算候选诊断；不删除点、不改值，不代表完整教师去噪实现。 |
| `denoise_trajectory(...)` | 仅显式登记的 `single_pass_simultaneous_keep_undefined` 执行一次标记、同时删除并重算特征；其他或缺失 method 抛 `MethodUnresolved`。真实输入还须通过注册合同。 |

零 `dt` 的速度是 `None / ZERO_TIME_DIFFERENCE`，负 `dt` 是 `None / NEGATIVE_TIME_DIFFERENCE`；没有时间是 `MISSING_TIMESTAMP`，尚未明确可靠时是 `UNRELIABLE_TIME`。默认 `time_reliable=False`，可靠性由调用方显式传入。原始数值时间差仍可作为结构事实读取。零位移的方向为 `None / ZERO_DISPLACEMENT`；零位移且正 `dt` 的速度可以是 0。首点不伪造一条零速度边。

### 去噪关系与已批准调度

定义 `d_i = direction(p_i → p_(i+1))`。只对 `i = 1,...,n−3` 的三条出边方向均可计算的窗口诊断：

`angle_diff(d_i,d_(i−1)) > threshold AND angle_diff(d_i,d_(i+1)) > threshold`。

第一/最后点、缺少后续出边的倒数第二点、三边窗口有零位移的点，输出明确不可评估原因；不假造方向，不据此自动保留为“正常”或删除为“噪声”。

最小构造反例 `[(0,0),(0,1),(0,2),(1,2),(1,3)]`，阈值 35°：同时候选只有原始点 2；如果在构造测试中删除点 2、重算方向，原始点 1 又成为候选。因此同时一次删除和迭代删除会产生不同结果。该历史构造例用于暴露原始方法歧义；本轮用户已明确选定一次标记同时删除，生产实现不迭代。该批准不等于教师原文明确了全部细节。

## 独立评价及可支持结论

[evaluation.py](../../workflow/evaluation.py) 不导入生产距离函数或 DP。它用独立点积端点分类和叉积距离逐点检查，点 `p_i` 只能匹配覆盖其原始索引的相邻保留端点区间，不能任意匹配到输出中的另一段。

`verify_simplification` 先检查 schema、同一记录、可选父哈希、索引有序子序列、首尾及原值未改，再计算误差。返回 `VERIFIED` 只说明这些工程条件通过；`quality_status` 始终是 `PENDING_RESEARCH_REVIEW`。候选自报的 `status/max_error` 不影响结论。错误输出返回 `REJECTED`，超界点保留原始编号及实测误差。

| 指标 | 对象、定义及方向 | 单位、分母与不可用原因 | 支持范围 |
|---|---|---|---|
| `reference_points / simplified_points` | 同一简化前后输入的点数；描述量，无质量好坏方向 | 点数，无分母 | 简化规模 |
| `saving` | `1 − N_output/N_reference`；越大代表压缩更多 | 无量纲；分母是相同简化前输入；空输入为 `EMPTY_REFERENCE_DENOMINATOR` | 不能把去噪/过滤损失混入简化收益；也不能单独证明质量 |
| `max_error` | 每个原始索引区间对应有限线段距离的最大值；越小表示对此参考更保真 | 输入平面单位；空输入 `EMPTY_REFERENCE`；单点正确保留时为 0 | 相对于当前简化前输入的保真，不能解释之前的删点是否正确 |
| `reference_length / simplified_length` | 各自相邻点欧氏距离和 | 输入平面单位；空输入分别为 `EMPTY_REFERENCE/EMPTY_OUTPUT`；真实零长度可为 0 | 描述几何长度，不是准确率 |
| `length_change` | `L_output − L_reference`，保留符号 | 输入平面单位；空输入不可用 | 长度变化 |
| `relative_length_change` | `L_output/L_reference − 1`，保留符号 | 无量纲；零长度 `ZERO_REFERENCE_LENGTH`，空输入 `EMPTY_REFERENCE` | 长度相对变化，不能单独判定清洗质量 |
| feature `coverage` | 可计算速度/方向边数，分母是全部当前相邻边 | 边数；无边为 `NO_EDGES`，未计算边不从分母消失 | 可计算性覆盖 |

数值核验误差在查看输出前按固定公式计算：`64 × binary64_epsilon × max(1, coordinate_extent, absolute_coordinate, tolerance)`。坐标绝对尺度用于覆盖平移后坐标相减的舍入，范围用于向量运算尺度，64 是固定保守浮点预算，不是研究质量门槛；每次核验输出其值。DP 使用原始算法阈值，不加该核验预算。超出浮点可表达范围的计算拒绝，不能由 NaN 比较漏洞获得通过。

`audit_point_accounting` 对每个 `(record_id, original_index)` 检查一个且仅一个最终去向：`filtered / denoised / simplified / retained`，同时核对原始坐标和时间。它不以总数量相等代替点级守恒，不把不同记录同坐标点合并；空记录仍计入输入记录数。完整基线审核另以候选之外的可信原始输入和固定合同重建点终态，核对实际 clean/final 数值及全体汇总；当前条件化真实处理使用这条入口。

`assess_improvement` 只实现已批准的布尔逻辑。正式收益门槛、保护项和有效性证据缺失时返回 `PENDING_RESEARCH_REVIEW`，硬条件明确失败时拒绝。测试里的显式数值门槛只属于 `CONSTRUCTED_FIXTURE`，不是项目质量合同，不可直接用于真实候选准入。

## 实际验证与范围

命令：

```bash
.venv/bin/python -m pytest task1/tests/test_geometry.py task1/tests/test_evaluation.py -q
```

首次实现后实际输出：`54 passed in 0.08s`；没有新增依赖。最终运行日志由主线程统一归档并绑定代码版本，本页首次结果不能代替最终版本复算。

| 测试组 | 有效检查 |
|---|---|
| `test_finite_segment_known_answers`, `test_geo05_*` | 有限线段 `sqrt(2)`、退化、垂直、端点外、环形角差 |
| `test_geo06_*` 至 `test_geo12_*` | 具名速度/方向、缺失/负/零时间、邻接重算、严格等号、右边界、分段/过滤分离、点归属、短/空记录 |
| `test_geo13_*` 至 `test_geo15_*` | 空/短/重复/闭合/回头/垂直 DP、原始索引、平面平移旋转及坐标与阈值同比缩放 |
| `test_geo16_*` 至 `test_geo19_*` | 去噪歧义反例、未定义方向、阈值/对齐/索引拒绝 |
| `test_eval01_*` 至 `test_eval05_*` | 真正错误简化拒绝、索引区间反例、独立参考、模拟破坏生产距离后仍拦错、父版本/原值/缺失输出/伪造状态拒绝 |
| `test_eval06_*` 至 `test_eval11_*` | 空分母、零长度、简化分母、全体去向、跨记录错误、舍入界、实际重算一致、平面不变性 |
| `test_eval12_*` 至 `test_eval14_*` | 未冻结阈值拦截、正例可通过/保护项失败可拒绝、非有限计算拒绝 |

以上54项结果属于首次构造数学验证，不是本轮重跑数量。当前完整测试、真实条件化处理、自然运行失败及修复证据均由 [当前审阅入口](../../evidence/goal1/REVIEW_PACKET.md) 定位。构造审核器挑战不作为人机争论证据；方法未被宣称最优，未知来源datum与真实地面精度仍未证明。
