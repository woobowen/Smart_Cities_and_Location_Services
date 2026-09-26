# Goal 1 当前工作入口

当前执行 `SC-LAB1-G1-COMPLETE-001`，继续同一 `SC-LAB1-G1-FOUNDATION-001`。
完整结果与状态见 [REVIEW_PACKET](../../evidence/goal1/REVIEW_PACKET.md)。
执行授权为 [COMPLETE](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/handoff/SC-LAB1-G1-COMPLETE-001_CODEX_PROMPT.md)
及最新[补充决定](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)。

D2一次标记同时删除已明确批准；原始 datum 仍 `UNVERIFIED`。
固定七条 pilot 在冻结局部 ENU 模型下做真实条件化分析，原始经纬度和时间不变。
模型尺度的米不是已确认地面精度。G2/G3与正式两报告/教师提交仍不执行。

复用 `.venv`，本轮新增独立核验依赖 `pyproj==3.7.2`。从仓库根目录执行：

```bash
.venv/bin/python -m pytest task1/tests -q
.venv/bin/python -m task1.scripts.complete_goal1 status
.venv/bin/python -m task1.scripts.complete_goal1 verify --run-id g1-complete-pilot-01
```

`verify`真正重读原始JSON并重算，不调用模型。新运行使用新ID：

```bash
.venv/bin/python -m task1.scripts.complete_goal1 recompute --run-id YOUR_NEW_RUN_ID
```

入口要求先提交处理源码，并登记新run；不能在旧run热替换代码或覆盖产物。
若执行/写操作结果未知，保留检查点并人工核对，不自动重发。
两工作 Notebook 默认RECOMPUTE，新内核Run All无模型调用。

原生A/B/C实际协作由当前授权主会话分派，`GoalJournal`记录任务和真实回执。
它不假装在独立Python进程中自动启动不存在的原生会话。旧CLI Provider仍保留，
旧4次及修复6次调用、冻结ledger和失败不重置；旧批次授权不用于绕过新硬限制。

[合同](CONTRACTS.md) · [实际角色与控制器](ARCHITECTURE.md) · [条件化坐标合同](../../config/conditional_planar.json)
