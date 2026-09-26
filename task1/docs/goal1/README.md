# Goal 1 工作入口

任务 SC-LAB1-G1-FOUNDATION-001 是已批准的一次性阶段执行。完整边界见 [本轮用户原文](../../evidence/goal1/APPROVED_PROMPT.md)，不改长期治理文件。当前实现只允许原始结构、时间与重复诊断；真实米制三步链受 CRS/距离口径及方向删除调度阻断。

教师源仍在 `task1/作业/作业/`，保持逐字节原样。新增 `task1/workflow/` 是工作版唯一执行实现：复用 starter 迭代 DP 的索引栈思路；不加载会隐式投影、排序时间、折叠重复、平滑或写入历史记忆的入口。既有 starter 保留为教学/历史来源，不与新工作版共同充当 active 算法。

在仓库根目录执行：

```bash
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r task1/config/requirements-goal1.txt
.venv/bin/python -m pytest -q task1/tests
.venv/bin/python -m task1.workflow inventory
.venv/bin/python -m task1.workflow live --enable-live --run-id g1-live-20260926-01 --stop-after 3
.venv/bin/python -m task1.workflow live --enable-live --run-id g1-live-20260926-01
.venv/bin/python -m task1.workflow recompute --run-id g1-live-20260926-01
```

LIVE 显式启用，复用当前 ChatGPT 登录；不读取认证文件、不换供应商、不启用付费 API。已有相同 run_id 会恢复；新 run_id 仍使用同一个 LIVE 调用预算。预算耗尽必须交研究审核，不能改 run_id 绕过。表中的示例 run_id 是本轮实际计划 ID，重复运行会恢复而不构成新模型实验。

默认 Notebook 仅离线重新执行工具并与真实记录逐对象比较；不只是打印旧结果。需要重新调用模型时显式设 LIVE 与新 ID，并受剩余预算和语义合同约束。

[合同](CONTRACTS.md) · [角色/控制器](ARCHITECTURE.md) · [审核包](../../evidence/goal1/REVIEW_PACKET.md)
