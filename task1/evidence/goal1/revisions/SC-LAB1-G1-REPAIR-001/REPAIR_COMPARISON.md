# R1-F01—F05 修复对照

| 项 | 旧问题与最小修复 | 代码 | before / after 与限制 |
|---|---|---|---|
| F01 | 去重/过滤掩盖错误 → 整份原列表字段、唯一性、数量和集合先检查，合法后才重排 | diagnostics.profile_list_errors；tools.execute_tool | probes_before.json → probes_after_adapted.json；两入口9类回归，不授权子集 |
| F02 | 缺失时间、null item、启动和工具异常逃逸；timeout丢日志 → 可计算性分离、结构校验、失败receipt/checkpoint/manifest，保留安全部分日志，杀整个进程组 | diagnostics.duplicate_details；provider.visible_events/run_limited/call；controller.terminate_failure | 真实PermissionError和坏数据见actual_failure_probes；超时/重试父子进程后续文件写入未发生；写盘失败报告EVIDENCE_MISSING，不伪称已保存 |
| F03 | denoise与baseline恒阻断、阶段单一 → 明确方法注册/真实合同核对与实际runner分离，连接完整平面链、独立评价及账本 | pipeline.py；geometry.denoise_trajectory；evaluation.review_baseline；controller.available_actions | 构造8点：2过滤、1方向删除、3简化、2保留；真实7条783点仍BLOCKED。真实坐标适配器未获批准，没有默认投影；不是只改配置便可跑 |
| F04 | 引用非空即可、任意交集充当反馈、合同回显称核源 → 小型source registry、真实页/片段和hash、当前审核与对应VERIFIED工具均须引用 | sources.py；controller.context/required_feedback；contract_snapshot/source_check | 来源未知/伪路径/错父版本/错run/非审核/缺数值反馈均拒绝；正常真实链通过。C05文本覆盖范围大于recompute_check实际的profile范围；时间分区与重复明细另由audit_live.py独立离线核对，不伪称C工具覆盖了这些字段 |
| F05 | 内部重试漏计、communicate末尾才发现 → 固定wrapper/native版本hash，按0.157.1源码识别内置provider覆盖无效，移除三项无效参数；实时事件观察首错终止；固定新批ledger绑定批准与测试 | provider.py；budget.py；repair_goal1.py | 离线停止/超时/预算测试 + 1探针/5角色实际成功。默认内部重试4/5仍在，不声称已禁用；本批可见重试0，底层请求unknown。历史9重连/1fallback/10sampling retry不相加，原FAIL保留 |

测试适配而非删反例：旧恢复fixture改用当前动作schema与来源ID；旧“随便存在的review字符串应通过”改为应拒绝；异常现在要求FAILED终态。交接原探针保留，新存在性检查所需唯一可执行路径适配见PROBE_ADAPTATION.md。早期开发失败日志全部保留。
