# A 当前交接：按新增授权完成条件化真实 pilot

[用户补充授权](../AUTHORIZATION_SUPPLEMENT.md)及 [USER_DECISIONS](../USER_DECISIONS.json)已经覆盖初始 Prompt 的 D1/D2 等待安排：**D2 已批准；source datum 仍 UNVERIFIED，但固定、可追踪的局部模型假设允许真实 pilot 条件化分析。** 不再询问技术批准，也不能继续把未知 datum 当成所有真实处理的停止条件。

当前 [TaskPlan.json](TaskPlan.json) 是供主线程消费的执行交接；原 `requirements.json` 仍是唯一 requirements 表。该 JSON 完整保留 R01–R16 引用、15项执行任务、GC01–GC16 关闭标准和 G1-A01–A18 对应。本文件及 TaskPlan 不代替 C 的内部总验收。

## 当前直接执行顺序

1. **A-T02–T06**：在原 requirements/active 入口同步当前授权；完成两项审核缺口、Goal队列/真实修复消费/父任务恢复、资源与恢复记录。完成两个 patch 仍不等于 Goal 完成。
2. **A-T11**：按主线程已固定模型登记候选外合同与原始→工作坐标适配器；不需要另一次研究批准。具体定义和逐阈值审核见 [local_model_contract.json](local_model_contract.json)。
3. **A-T07**：固定有效 CODE_SHA，执行完整 `task1/tests`、相关回归和 C 独立复验；改代码后重建受影响旧产物，不在原 run 热换代码。
4. **A-T08、T12**：重建当前真实诊断，实际执行固定七条/783点条件化链；审核器从可信 raw＋固定合同核查实际输出及全部账本。
5. **A-T13**：实际 C 审核驱动有意义的后续局部检查或修复；执行后再次审核对应新产物，不以历史诊断链代替真实处理反馈。
6. **A-T09、T10**：两本工作 Notebook 新内核 RECOMPUTE；必要图与实际返回路径一致，保存原生可编辑源和检查结果。
7. **A-T14、T15**：独立 C 总审查、唯一当前 REVIEW_PACKET、安全检查与实际 push/remote 核对。GPT 二重验收仍 PENDING，Goal2/3不启动。

真实地理语义确认继续 UNVERIFIED。工程完成、条件化实验有效、真实地理事实三项分开登记；前两项可依据真实执行通过，不能用它们推导第三项。只有影响某个结论的实际障碍才阻断该结论。

## 固定工作模型

主线程依据原始空间范围、在清洗评分前固定：数学椭球 `a=6378137m`、`1/f=298.257223563`，所有点 `h=0`；ECEF 转冻结中心 `(121.343555°,31.3561015°)` 的 ENU，使用 East/North 平面坐标，单位为**条件模型米**。中心来自完整七条原始 bbox，不随过滤重算。

这些参数定义计算模型，不把数据认定为 WGS84，不赋予源 EPSG，不做加偏转换。Up 可作为曲率诊断，不能当实际高程。参考参数仍为 `65/5/30/400/35/5`，没有调参或模型效果筛选。

[本次只读模型诊断](local_model_diagnostics.json)已实际执行：

| 项目 | 实测 |
|---|---|
| 原始范围 | lon `[121.214715,121.472395]`；lat `[31.097935,31.614268]` |
| 最大水平半径 | 31,131.193530 条件模型米 |
| East / North 范围 | 约 `[-12225.18,12264.18]` / `[-28623.29,28631.99]` m |
| 原始邻边 | 776条；453非零位移、323零位移 |
| 同一数学椭球的邻边距离核查 | ENU与测地距离最大绝对差0.00217928m；最大相对差约11.826ppm |
| 400m布尔敏感性 | 776条距离阈值及时间OR后判定均0差异；最接近边距阈值3.418026m |
| 时间边界 | 记录1原始边0→1恰30秒；严格大于规则下时间分支不切 |
| 局部微分比例 | 原始bbox内奇异值范围约 `[0.999987999906,1]`，最多12ppm局部收缩 |

这不是 baseline 结果。A 没有分段、过滤、去噪或DP。局部微分比例不是有限DP弦距离的误差定理，更不是未知datum误差界。独立计算方案一致也不能确认原始地理语义。

## B/C 需完成的实际数值核验

[技术交接](local_model_contract.json)给出完整公式、参数和 MODEL-V01–V08：

- 每点手工公式/生产适配器对独立 PROJ cart→topocentric；核查有限值、原始ID/索引/坐标精确保护。建议事前固定1微米适配器交叉核算误差，不能加到处理阈值或替代既有DP数值余量。
- 30秒直接由 raw 时间计算；400m检查原始邻边的严格等号、距离单独布尔与时间OR后布尔。
- 65m用**实际分段结果**内部的边累加，同椭球测地长度仅作敏感性；断边不计入任何段。5点过滤条件单独核对。
- 35°核对实际去噪输入的 outgoing grid heading、双侧环形差、零位移/不可算窗口、同时删点与下游重算；不得加噪声地板或改为迭代。
- 5m对每个实际 clean 参考点核对其相邻保留原始索引区间的有限线段，不能找全轨迹最近段。保留DP同输入分母、独立误差及原值检查。
- 为量化方向与有限弦的投影敏感性，可将**同一批点/同一窗口/同一保留索引**映射到同椭球同中心AEQD做一次几何复算；不再跑另一条清洗链，不选更高分模型，不据此改变ENU合同。若跨阈值，明确限制跨模型结论。
- 实际 baseline 审核后，依据最大DP残差或最小阈值裕量安排一项有意义局部复验，并记录新产物的C审核；不存在错误就不编造错误。

## 原表需要同步的实质旧状态

- R03原G2字段中的“调度明确后实际基线”移到G1条件化执行责任；G2保留参数/效果研究。
- snapshot/R08/R12仍写旧run03只有A成功、B失败、C未调用，须区分旧失败、REPAIR真实诊断链、本轮实际工程修复与条件化处理链。
- 三个研究附件已在 `task1/docs/research/`，原 missing 标记应更新，不重复索取或广搜。
- R05/G1-A08受C2影响的评价器范围重开并用当前C证据关闭；有效历史profile/数学验证仅继承其实际范围。
- 当前README/CONTRACTS附录/架构及source注册不再以旧6-call耗尽或“只等待”控制本轮；历史ledger/失败必须保留。
- 当前合同/requirements/acceptance分别记录源datum未知、D2已批准、工作模型假设已授权、真实条件化执行状态。原“未运行”不能被字符串改成已运行。

## 来源、快照与 A 边界

[source_audit.json](source_audit.json)已核对新增授权归档及其hash，同时保留6个原始来源hash一致、3个PPT关键摘录逐字一致、raw hash与7条783点核查。变更前 [TaskPlan.initial.json](TaskPlan.initial.json)、[TaskPlan.initial.md](TaskPlan.initial.md)、[source_audit.initial.json](source_audit.initial.json)仅为补充授权到达前的历史快照，不再控制当前执行。

可重跑命令：

```bash
.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/a_scope/verify_sources.py
.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/a_scope/local_model_diagnostics.py
```

A 仅写本目录，未改生产代码/合同/治理/原始数据/旧证据，未调用外部 Provider、未新增代理、未安装包。共享 `.venv` 中的 pyproj 安装由主线程记录。G1工程是否完成仍由最终真实产物和独立C总验收决定。
