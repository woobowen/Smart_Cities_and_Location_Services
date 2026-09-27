# 实验一 Goal 3 审阅入口

Goal：`SC-LAB1-G3-FINAL-001`。本轮是实验一的第三个工程阶段，不是课程实验三。

当前数值研究、一次性最终确认、全量生产、仓库与同一解压 ZIP 共四次 FULL Notebook、七张正式图和两报告可用工程已通过独立内部审核。Handoff 与包工程父任务也已独立闭合；[总验收](independent_c/internal_acceptance_receipt.json) 已核验全部 15 个前置任务、1,131 个目标和 222 个来源，获准发布 PARTIAL_BLOCKED 审查检查点。实际发布正在进行，此入口不代表实验一最终 PASS。可信姓名/学号、真实互动原图及 Evidence Master 批准呈现与 LOCK 仍属外部缺项。`GPT_SECOND_REVIEW=PENDING`，`Submission=NOT_READY`，没有代发邮件或提交平台。

## 1. 建议阅读顺序

1. [实验一总入口](../../README.md)：教师任务对应、完成版 Notebook、报告和离线运行命令。
   [教师任务定位](teacher_delivery_mapping.md) 列出 90 个具体单元引用及 45 处实际报告页码。
2. [Technical Handoff](../../docs/goal3/TECHNICAL_HANDOFF.md)：完整方法、共同指标、选择、确认、全量读数、版本和限制。
3. [Interaction Handoff](../../docs/goal3/INTERACTION_HANDOFF.md)：真实事实候选索引，不代 Evidence Master 选择、注释或 LOCK。
4. [唯一要求登记](requirements.json)、[实际任务/修复状态](goal_state.json)：逐项动作、证据和未完成项。
5. [Experiment Report PDF](../../reports/experiment1/experiment1.pdf) / [LaTeX](../../reports/experiment1/experiment1.tex)；[Process Report PDF](../../reports/process1/process1.pdf) / [LaTeX](../../reports/process1/process1.tex)。Process 仍为明确待补送审稿。

## 2. 当前有效实验与结果

[current_runs.json](current_runs.json) 只指向有效的开发、选择、最终确认和全量生产。[result_summary.json](result_summary.json) 按实际原件/合同/分区/源码/独立回执哈希生成；完整原始点终态在全量 run 的 285 个确定性压缩分片内，可由完成版 Notebook 从 raw 重算。

| 阶段 | 实际范围与身份 | 核心结果 | 独立闭合 |
|---|---|---|---|
| 开发 | 240 条已暴露记录 | S0 增加 6,704 点覆盖；S0_G0 相对 S0 有 41 条几何改善，父项/移除/负结果保留 | [开发](independent_c/development_closure_receipt.json) |
| 选择 | 240 条预登记选择记录 | S0 全保护、103 条覆盖改善；G0/组合在同样 3 条记录退化，选择 S0 | [选择](independent_c/selection_closure_receipt.json) |
| 最终确认 | 冻结后一次运行 600 条、62,284 点 | S0 全保护、349 条覆盖改善；共同覆盖 35,868→62,220，存储点 10,991→12,114 | [确认](independent_c/confirmation_closure_receipt.json) |
| 全量生产 | 全部 11,386 条、1,173,410 点，包含开发记录 | R0/S0 22,772 次真实处理；共同覆盖 671,899→1,172,211，存储点 200,470→221,149；0 处理失败/0 逐记录回退 | [全量](independent_c/production_closure_receipt.json) |

最终策略为统一确定性 **S-D-P：30 / 400 / 2 / 0 / 35 / 5**，参数顺序为 `dt / distance / min_points / min_length / direction / dp`。R0 的 `min_points/min_length=5/65`，其余相同。最终记录级处理新增模型调用为 0；治理 A/B/C 的实际调用另计，隐藏后端请求与费用保持 unknown。

选择、确认与生产数值 CODE_SHA：`e12f8a27944210adb452730be92a0674dfc6b84b`。后续报告、图和 Notebook 兼容性修复没有改写这些数值运行的代码身份。结果提交与发布 HEAD 待实际发布核对后登记，不能预先声称自身 SHA。

## 3. 不能省略的限制与负结果

- `source_crs=UNVERIFIED`。固定椭球/h=0/ENU 是批准的条件化数学模型；PROJ 一致与敏感性检查不认证源 datum。
- 共同覆盖不是最终存储点数；没有噪声真值，不能声称清洗准确率提高。全量统计是本数据集产出描述，不是第二次独立测试。
- 最差新增覆盖点为 record 352 / index 105，偏差 **266.016754 工作米**。其四点原窗口被 R0 因点数不足过滤；S0 经过 D 后删除该点，局部 P 没有再删点。[独立边界核验](independent_c/new_coverage_boundary_receipt.json) 与[全量过滤原因](independent_c/full_filter_attribution_receipt.json) 单列此限制。
- D60、P2/P10、条件方向组合的失败及不采用原因均保留。[收敛复盘](CONVERGENCE_REVIEW.md) 解释有限预算下停止；没有预定最复杂方案或 S0 必胜。
- 全量 22,772 份实际轨迹通过外部 raw oracle；独立 Decimal/PROJ 重算为随机/类别合并 50 条记录、100 份轨迹。独立阶段坐标敏感性覆盖 56 条、112 份，不冒称全部记录的第二次数学实现重算。

## 4. 工程与外部边界

[本轮原始授权](USER_PROMPT.md) 保留用户实际文字；G1/G2 的网页审核承接为 `USER_RELAYED_GPT_STAGE_ACCEPTANCE`，没有补造工具日志。[治理工具事件](governance_tool_events.json) 仅导出本次会话可得的真实事件元数据；加密载荷只留哈希，不冒称逐字消息。

失败、补丁、独立复验和恢复保存在 `repairs/`、`independent_c/`、`independent_documents/`、`notebook_verification/`。旧失效开发 run、原有教师/starter、原始数据与用户既有 ZIP 均保留。

仓库两份 Notebook 新内核 FULL 和独立复验已完成：[基础本回执](independent_c/repository_basic_full_02_receipt.json)、[系统本回执](independent_c/repository_system_full_02_current_receipt.json)。两报告全部 33 页已实际目视；统一 REPORT_BUILD 后独立重渲染与已看版本逐页字节一致，[当前重建复核](independent_documents/report_entry_delta_receipt.json) 按新产物绑定，未把旧 hash 说成当前 hash。

[实际 REVIEW_ONLY ZIP](../../submission/REVIEW_ONLY_实验一.zip) 已构建并真实解压，113 个成员（含 manifest）、21,418,989 字节，SHA256 `97d5dbe2d7a5c87d09bcb21ae5798fa0b76374fabdd03f25447fb87c4f27c447`。包内两个 FULL 均已独立通过：[基础本](independent_c/isolated_package_basic_full_receipt.json)、[系统本](independent_c/isolated_package_system_full_receipt.json)。两者均从包内 raw/源码执行，新分片与正式结果一致，Provider attempts=0；静态依赖检查不替代这些全量运行。总验收已通过；实际远程核对将按真实结果补入[最终回复](FINAL_RESPONSE.md)，不预写通过。
