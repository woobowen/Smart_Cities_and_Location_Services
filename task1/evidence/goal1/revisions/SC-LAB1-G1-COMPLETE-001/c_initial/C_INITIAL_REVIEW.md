# C 初始缺陷复现与 B-Repair 交接

主 Goal：SC-LAB1-G1-FOUNDATION-001；执行标签：SC-LAB1-G1-COMPLETE-001。

本记录是独立 C 角色在修复前的有界核查，状态为 `REPRODUCED_REPAIR_REQUIRED`，不是父 Goal 完成声明。两项问题来源均为外部 GPT 第二轮审核；C 本轮核查确认其仍存在，没有把历史发现冒称为自主新发现。主线程已收到结果并安排实际工程修复。

## 范围与版本

- 第一条实际命令为 `ls -la`。目录有 `.venv`、`task1/`、`AGENTS.md` 和本轮 handoff；复用 `.venv`，没有安装依赖。
- 初始 `git status --short --branch`：`main...origin/main`；未跟踪项为两个用户 handoff ZIP 及本轮 revision 目录。C 没有修改、删除或提交这些原有 ZIP。
- 已读 active `AGENTS.md`、当前批准 Prompt、`task1/docs/goal1/CONTRACTS.md`、原探针源码、待审实现与旧 C03/C05 原始响应。
- 原探针实测 `diagnostics.py`、`evaluation.py`、`tools.py`、`io.py` 的 Git blob 均精确匹配历史审核锚点 `7e6cd4082c2cdad2452fa5a1006e99dcfb050d17`；各 SHA256 及运行时间见 [本轮 JSON](initial_reference_probes.json)。这项结论限定于执行探针时的代码，后续 B 修复应使用新的版本绑定。
- 核心代码、合同、教师数据、历史结果只读。C 仅新增本目录证据。D1/D2 仍是研究／事实门槛，不由本核查批准；没有执行真实空间 baseline、完整旧六调用、额外 Provider 或网络请求。

## 实际执行命令

工作目录为仓库根目录。执行前读过脚本，确认它仅使用构造输入和临时文件，输出路径由参数明确指定；调用时拒绝覆盖本目录已有结果。

```bash
.venv/bin/python -B task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/handoff/reference_only/probes/verify_round2_findings.py --repo . --output task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/c_initial/initial_reference_probes.json
```

进程退出码为 0；它是输出实测结果的探针，并不以“发现误放行”返回非零，不能用退出码 0 宣称审核正确。[完整输出日志](initial_reference_probes.log) 保留命令、cwd、退出码、stdout/stderr。全部反例均为 `ENGINEERING_TEST` / `CONSTRUCTED_FIXTURE`；程序内模型／网络调用为 0。本 C 会话本身是主线程实际派发的角色工作，不计作该探针的模型调用。

## C2-F01：审核目标与实际覆盖错配

**实测／读取依据：** 当前 `tools.execute_tool()` 对 `verify_profiles`、`recompute_check` 都只调用 `independent_profile_review(subset, previous_profiles)`。后者另比较重算 profile 的 hash。函数没有时间分区／重复详情待审参数；`Controller._dispatch()` 只传 `self.profiles()` 与 `self.baseline_output()`。原 `PHASE_ACTIONS` 的 C 阶段也没有时间／重复详情专用核查，`Controller.run()` 以 `phase == 5` 决定终态。

旧真实 C03 明确请求“交叉核对重复事件详情”；旧真实 C05 请求“严格大于30秒、等值不切分、分区索引无遗漏无重复”。本轮读取的是历史原始响应，没有重发模型请求。原文件为：

- `task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/runs/g1-repair-roles-01/calls/g1-repair-roles-01-03-review/response.json`
- 同目录 `g1-repair-roles-01-05-review/response.json`

本轮探针中 normal 与 legally_reordered 各经 `verify_profiles`、`recompute_check`，4 项均 VERIFIED；duplicate_id、missing_id、foreign_id 各经两工具，6 项均 REJECTED。此结果证明已修好的完整 profile 列表校验仍有效，**不证明时间分区或重复详情已审**。探针字段 `previous_F01_regression` 指更早的 profile 列表问题，不是本轮 C2-F01 的覆盖完成证明。C 本轮没有伪称已执行时间分区／重复详情的错误候选拒绝测试；现有接口缺少可提交目标。

**根因：** 工具名称与泛化 VERIFIED 未绑定实际审核目标；反馈 ID 引用不能补足缺失的审核能力，固定阶段耗尽也不能证明全部产物覆盖。

**最低接口与关闭条件：**

1. 对 profiles、time_boundaries、duplicate_details、baseline 有明确可调用的核查入口；核心独立检查接入运行时，而非仅放在离线发布脚本。
2. 控制器从已登记产物解析 `target_artifact_id`、实际 hash、记录范围、合同版本；模型自填 hash／ID 不成为可信事实。回执给出可信参考、checked/unchecked 组件及原因。
3. 缺目标、目标类型错配、请求超出能力、旧 profile 审核用于关闭新时间／重复目标、目标 hash 改变均不能返回足够覆盖的 VERIFIED 或关闭父任务。
4. 时间审核从可信原始时间逐边核对：负 dt、严格 `>30`、等号不切、右点归新段、切点与分区一致、原始索引顺序、完整且不重复覆盖。分别拒绝漏边界、错误等号切分、错索引；合法完整分区通过。
5. 重复详情审核全部事件：拒绝漏事件、重复事件、错边、错误原因及错误类型；缺失时间／无效位置保持真实不可计算原因。不能只审核 preview。
6. 既有 profile 正常重排通过、重复／缺失／多余 ID 拒绝的 10 项回归不退化。
7. Goal 控制器只有当前要求覆盖闭合才能结束；工程 issue 经过 B 修复、C 复验、关闭证据与父任务恢复，不因旧固定五阶段自动完成。

## C2-F02：baseline 候选自证

本轮原探针的实际输出：

| 用例 | 应有结果 | 实测 | 实测要点 |
|---|---|---|---|
| 正常四点线段 | VERIFIED | VERIFIED | 输入4，简化2，保留2 |
| 仅 final 第一点 x 改为999 | REJECTED | REJECTED | VALUE_MODIFIED，index=0 |
| clean 与 final 同时平移(+1000,+1000)，input／账本不变 | REJECTED | VERIFIED | 错报 modified_point_count=0 |
| records 与 point_actions 清空，原汇总仍输入4 | REJECTED | VERIFIED | 审核改按0记录／0点守恒 |
| 汇总 input／retained 改为999 | REJECTED | VERIFIED | 独立实际计数仍4／2却未比对 |
| 工具 raw 为 fixture:a、fixture:b（5点），候选为 fixture:review（4点）且同移 | REJECTED | VERIFIED | 工具读取可信 raw 却未传给 baseline 审核 |

5 个应拒绝反例中 4 个误放行；正常对照通过。它们是构造错误产物，不说明真实七条 pilot 被改过值。

**根因：** `evaluation.review_baseline(output)` 从候选的 `segment.input` 收集审核输入，以候选 `parameters.direction/dp` 决定方法阈值。DP 只比候选 clean 与 final；随后分组账本又取 original 中的值，绕过 actual clean 与可信源值的关系。整个候选 records 可共同漏空；`stage_counts` 没有逐项核算比较。实际切分／过滤、完整可信记录范围和父版本也未独立核验。`tools.verify_baseline` 仅传 `previous_baseline`，丢弃已读取的可信 subset 与 policy。

**最低接口：** 语义上应为 `review_baseline(candidate, trusted_complete_inputs, approved_contract, trusted_provenance)`；具体形参由实现方决定。参考必须从候选之外提供，包含 raw hash、完整 record scope、索引和值、raw→working 关系、父版本与适配器版本；不能把候选自身字段拷贝成 trusted 参数。

**关闭条件：**

1. 精确核对可信记录集合、全部原始索引、raw hash、父版本、适配器版本；候选双侧改值、漏记录／点、外来记录不得共同逃逸。
2. 参数、处理顺序、单位、方向方法、DP 容差来自可信合同，拒绝参数偷换；未知真实 CRS／未批 D2 保持门控，不能改字符串解锁。
3. 从可信段独立核对切边条件、边界点归属、顺序／覆盖及过滤点数、长度和完整理由，不再次调用整个生产 runner 作答案。
4. actual input、actual clean、actual final 的 record/index/time/working 坐标逐点对可信父输入；方向删除的 ID、同时调度及不可计算窗口符合批准方法。
5. final 是正确父 clean 的有序索引子序列；独立有限线段与原始索引区间核验 DP，使用事前固定浮点余量；不能使用全轨迹最近段或候选自选容差。
6. 实际 point_actions、逐记录统计、全局 stage_counts 与可信全部输入严格一致。`modified_values` 等声明也须与实际检查对应。
7. 原四项误放行与仅 final 改值均拒绝；另验证错父版本、账本漏项、错误过滤理由和参数偷换。正常完整结果、合法空输入、合法全过滤有合理通过与无输出／质量不可用说明；非空任务无理由丢空拒绝。
8. 审核结果标明范围，不因工程正确宣称真实恢复准确率或处理质量提升；源代码变化后重建受影响结果并由独立 C 复验。

## 交接状态

两项 issue 均保持 OPEN / REPAIR_REQUIRED；本记录不得直接将其关闭。来源为 [外部 GPT 第二轮审核](../handoff/reference_only/GPT_SECOND_REVIEW_ROUND2.md)，本轮 before 证据为本目录 JSON／日志。

主线程已接收根因，并明确接手 C2-F01／控制器，B-Repair 接手可信 baseline 审核及相应接口／测试。修复后 C 应从可信输入独立核验实际 after 产物，保留原反例语义；接口变化要记录适配，不能删掉反例求通过。

C 本次不修改生产代码／测试／合同，不负责整体 GC 关闭，不宣称 Goal1 或最终 Deliverable 通过。Experiment Report、Process Report、正式图和真实 baseline 均未在本 C 子任务中生成或更改。无新增系统包、语言包、工具链或配置变更；无 commit／push。
