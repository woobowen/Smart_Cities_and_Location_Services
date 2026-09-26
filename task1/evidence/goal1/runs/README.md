# 本轮真实调用与失败

[call_summary.json](call_summary.json)按实际可见事件汇总4次CLI派发、2个完成的模型turn、1个被控制器接受的结构化请求、1个真实工具动作。底层网络请求数 unavailable。没有Mock fallback，没有完整A→B→C→A反馈闭环。

| run | 已存在的CODE_SHA | 实际结果 | 证据 |
|---|---|---|---|
| g1-live-20260926-01 | 41523a05a346b7e7940c77278000190d1793c9c4 | CLI0.147.0被服务拒绝，模型要求新CLI；0工具 | [manifest](g1-live-20260926-01/manifest.json) / [receipt](g1-live-20260926-01/calls/g1-live-20260926-01-01-research/receipt.json) |
| g1-live-20260926-02 | 348d789ad6dd45c2ad9b0c6cc1981196f8a1674b | CLI0.157.1 A返回完整JSON，但工程解析器误判已主动禁用code host的诊断；保持失败、0工具 | [manifest](g1-live-20260926-02/manifest.json) / [events](g1-live-20260926-02/calls/g1-live-20260926-02-01-research/visible_events.jsonl) |
| g1-live-20260926-03 | d1444eb07035ef651a36a3e89269f004186581df | A成功并调用source_evidence；B workspace routing discovery failed；C未调用 | [manifest](g1-live-20260926-03/manifest.json) / [checkpoint](g1-live-20260926-03/checkpoint.json) |

run03 A的 [输入](g1-live-20260926-03/calls/g1-live-20260926-03-01-research/input.json)、[模型可见事件](g1-live-20260926-03/calls/g1-live-20260926-03-01-research/visible_events.jsonl)、[结构化结果](g1-live-20260926-03/calls/g1-live-20260926-03-01-research/response.json)和[回执](g1-live-20260926-03/calls/g1-live-20260926-03-01-research/receipt.json)相互关联。[唯一实际工具产物](g1-live-20260926-03/tools/0ad49e824507fb5f5ee9e1d042b423f1cee074df1d78283b5385d277638fa15c.json)从固定pilot/raw和合同读取来源信息。A请求保留CRS/方法未决，没有授权猜测或清洗。

B的 [输入](g1-live-20260926-03/calls/g1-live-20260926-03-02-execution/input.json)已包含A和真实tool交接，但 [可见事件](g1-live-20260926-03/calls/g1-live-20260926-03-02-execution/visible_events.jsonl)显示9次重连通知、1次WebSocket→HTTPS切换及最终路由失败。没有合法B response，没有B数值工具执行，没有C ReviewCard。

旧控制器事件名 FEEDBACK_HANDOFF 也用于A初始计划交接；phase=1的这条事件**不是**C审核→A反馈循环。不得仅凭这个名称声称G1-A12通过。工程source_audit/geometry_engineering子代理负责材料和代码审查，身份与runtime三角色分开，不补算为C。

[budget_live.json](budget_live.json)保留4次外层尝试和1次工具计数，同时明确内部请求不可计清、真实护栏FAIL并冻结所有新LIVE。CODE修复后只执行离线ENGINEERING_TEST，未偷偷换run继续模型。

## 当前真实数据工程诊断

[pilot_diagnostics.json](../../../results/goal1/pilot_diagnostics.json)绑定最终诊断CODE、raw与源码hash；[pilot_summary.csv](../../../results/goal1/pilot_summary.csv)含每记录计数；[point_actions.jsonl](../../../results/goal1/point_actions.jsonl)覆盖783点，每点均PRESERVE_UNPROCESSED，changed_values=0，附边界/重复原因。

这些是 CURRENT_RUN_REAL_DATA 的工程诊断，由主线程/Notebook调用当前共同工具；不是B/C完成的模型行动。七例0/1/2/246/256/306/352，783点、776边、122零dt、62同时间不同位置、323相邻重复位置、5个dt>30秒边界，时间诊断12分区。完整分段/过滤/去噪/简化数量为null，783点not_processed，不将未运行写成“删除0且质量优秀”。

## 离线复算

命令：`.venv/bin/python task1/scripts/recompute_archived_run.py g1-live-20260926-03`。从Git恢复已记录CODE到临时目录，校验原始与源码hash，实际重跑唯一已完成source_evidence，输出hash一致，见[复算记录](../validation/replay_result.json)。没有新模型调用，也没有补齐未发生的数值/审核动作。

第二份Notebook另从raw真实执行profile、independent review和recompute_check，明确标为工程离线复算。[新内核运行记录](../validation/notebooks.json)。CONSTRUCTED_FIXTURE/MOCK_TEST只在工程测试中，HISTORICAL只作来源。保留这些类别不会自动证明全量质量或模型确定性。
