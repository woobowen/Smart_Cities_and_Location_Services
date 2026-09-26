# Goal 1 工作入口

任务 SC-LAB1-G1-FOUNDATION-001 是已批准的一次性阶段执行。完整边界见 [本轮用户原文](../../evidence/goal1/APPROVED_PROMPT.md)，不改长期治理文件。当前实现只允许原始结构、时间与重复诊断；真实米制三步链受 CRS/距离口径及方向删除调度阻断。

教师源仍在 `task1/作业/作业/`，保持逐字节原样。新增 `task1/workflow/` 是工作版唯一执行实现：复用 starter 迭代 DP 的索引栈思路；不加载会隐式投影、排序时间、折叠重复、平滑或写入历史记忆的入口。既有 starter 保留为教学/历史来源，不与新工作版共同充当 active 算法。

在仓库根目录执行：

```bash
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r task1/config/requirements-goal1.txt
.venv/bin/python -m pytest -q task1/tests
.venv/bin/python task1/scripts/recompute_archived_run.py g1-live-20260926-03
.venv/bin/python task1/scripts/build_goal1_figures.py
```

本轮LIVE已冻结：A成功一次，B网络失败，C/反馈未发生，且发现CLI内部重试未纳入原预算。不得直接再运行模型或改run_id绕过。已修复控制器漏洞，真实网络重试控制还需审核后复验。访问方式仍为现有ChatGPT登录，不读取认证文件、不换供应商、不启用付费API。

默认 Notebook 仅离线重新执行工具并与真实记录逐对象比较。旧LIVE源码可按其CODE_SHA恢复到临时目录复算，当前工作区不切换版本；它只验证已实际执行的source_evidence，不等于完整Agent闭环。全量inventory已保存在审核包，重新调用inventory会重建同名派生文件，需另存原证据后再进行。

[合同](CONTRACTS.md) · [角色/控制器](ARCHITECTURE.md) · [审核包](../../evidence/goal1/REVIEW_PACKET.md)
