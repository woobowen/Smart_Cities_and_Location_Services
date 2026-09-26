# Goal 1 工作入口

当前任务为 SC-LAB1-G1-REPAIR-001，修复前审核结论为 REVISE / NOT_PASS。工程总状态仍 PARTIAL_BLOCKED；新增真实诊断闭环已完成，D1/D2阻断真实空间baseline。完整入口见 [REVIEW_PACKET](../../evidence/goal1/REVIEW_PACKET.md)。

沿用现有 .venv 和恢复的临时 Codex CLI0.157.1，不需要重新安装环境。教师源位于 task1/作业/作业/，保持原样。task1/workflow 是工作版执行实现；它不加载会自动投影/平滑/改时间的历史入口。

可离线复核：

```bash
.venv/bin/python -m pytest task1/tests -q
.venv/bin/python task1/scripts/recompute_archived_run.py g1-live-20260926-03
.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/audit_live.py
```

当前记录：6次外层派发（1探针＋5角色）、5次真实工具、无可见重试；底层请求数unknown。旧ledger/live_stop保持冻结，新修复批次模型预算已耗尽。不要重发模型、清空ledger或换run_id/base绕过；Notebook默认离线，无模型请求。

完整平面构造链已实现并独立验证；真实生产合同与坐标适配器等待批准，不把构造approval接到教师JSON。历史source_evidence仍按旧CODE复算；新工具contract_snapshot只读合同说明，source_check读取精确白名单来源，不替未知CRS背书。

[合同](CONTRACTS.md) · [角色/控制器](ARCHITECTURE.md) · [修复对照](../../evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/REPAIR_COMPARISON.md)
