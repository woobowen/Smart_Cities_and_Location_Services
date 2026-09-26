# 实验一 Goal 1：三个角色与确定性控制

主线程对整个Goal负责。当前真实使用原生Codex子角色：A核对教师来源和剩余任务；
B-Repair修改可信baseline审核，主线程兼B-Repair实现目标审核与Goal控制；
C在独立上下文复现外部GPT缺陷、补反例并复验。最终另由独立C上下文总审。
每次真实分派、可见输出和工具产物单独记录，不把一次回复拆成三名Agent。

| 角色 | 输入与实际动作 | 输出与边界 |
|---|---|---|
| A | 教师原文/hash、合同、真实诊断、未完成要求 | 有依赖和关闭标准的TaskPlan；不虚构datum，不开展G2候选搜索 |
| B-Run | 固定原始句柄、登记合同、CODE_SHA | 实际诊断/条件化基线/账本/复算/必要图；不能改原始值或评价尺度 |
| B-Repair | C的缺陷与反例、批准定义 | 最小实现修复、专项回归和影响产物重建；不能自行关闭缺陷 |
| C | 候选之外的原始输入/合同、实际版本产物 | 独立数值检查、完整覆盖回执、反例和关闭证据；不改核心待审文件 |

`goal.py`是确定性Python任务/问题队列，不是第四个模型。原生会话分派由主线程执行，
控制器消费实际回执并约束恢复/结束；独立脚本不会虚构自动模型通信。
原生C的只读范围由任务指令、实际文件diff和hash检查落实，未声称它具有与旧CLI相同的OS沙盒。
旧`provider.py`仍有真实只读CLI隔离/可见事件校验，用于历史和显式授权LIVE入口。

`NEEDS_REPAIR → REPAIRING → AWAITING_REGRESSION → C VERIFIED → parent PENDING`
是实际工程路径。C拒绝继续修复，有问题不结束父Goal。任务还区分PENDING/RUNNING/
AWAITING_REVIEW/BLOCKED_EXTERNAL/VERIFIED；Goal为IMPLEMENTING、
ENGINEERING_READY_FOR_GPT_REVIEW、BLOCKED_EXTERNAL或INTERRUPTED_CHECKPOINT。
历史五阶段`Controller`只可结束一个调度片段；它的phase不能决定Goal完成。

目标审核覆盖profiles、完整重复事件、时间分区和baseline。控制器解析已登记ID与文件hash，
回执列出可信raw/contract、record scope、checked/unchecked。必须审同一版本的实际目标，
不能把旧profiles通过用于新time或baseline。baseline自报的审核不能代替C的候选外核验。

baseline以可信完整输入、批准合同和实际candidate为参数，独立检查原始集合、切分/过滤、
方向窗口、actual clean/final坐标与时间、DP原始索引区间、终态账本和分记录/全局统计。
条件化模型仅改变工作坐标域；source_crs保持UNVERIFIED，raw→working关系和adapter版本保留。

源码变化暂停旧run，重新固定版本；受影响结果/审核失效，依赖任务回到待执行。
无关可靠产物保留。结束关口再次检查当前run必需产物和覆盖，不相信单个文本PASS。
原始值、合同、输出和审核文件hash均验证；模型无法执行任意字符串/shell或修改评分。

本轮资源见 `revisions/SC-LAB1-G1-COMPLETE-001/resources.json`。
主会话/原生子角色/已完成turn/CLI/确定性工具分别统计，底层请求及精确剩余额度unknown。
旧4次、后续6次CLI调用和live_stop永久保留；它们是历史批次，不阻断用户新授权的正常协作。
无额外付费API、无新供应商、无无界递归派发。

中断前记录inflight。未知执行状态不能自动重复写或模型调用；恢复先核对可见回执和文件。
SEARCH_ONLY不得发起LLM；未来留出/记忆只读边界保留，四模式效果实验属于G2。
Notebook默认离线重算，历史调用、当前原生协作、构造ENGINEERING_TEST和真实条件化数据分开。

两份正式报告及Evidence Master截图/标注/LOCK均不在本轮定稿。工程就绪只供GPT读取真实远程二重审核，
不等于最终Deliverable PASS、用户理解完成或教师Submission完成。
