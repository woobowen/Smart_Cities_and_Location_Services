# C2-F02 独立复验

结论：`VERIFIED`，范围为完整可信输入、合同、候选产物审核及其本轮反例。不是真实 pilot 处理验收，不是坐标来源事实确认，也不是 Goal1 总验收。

外部 GPT 最初发现的 C2-F02 反例语义保留：正常四点、仅 final 改值、clean/final 同时平移、records/ledger 清空、汇总伪造以及工具 raw 作用域不符。接口适配为先从构造原输入建立 detached trusted handle，再创建候选；不再调用已废弃的无可信参考签名求正常通过。

候选由 C 手工按正 x 方向匀速直线的已知答案建立，未调用生产 runner、生产几何工具或审核器内部 helper 构造答案。审核期间对生产处理入口设置调用哨兵；两次实测调用数均为 0。

第一轮：37 项中 35 项符合预期。新发现处理片段外层 `segment_index=0` 被 `false`／`0.0` 替代仍误放行。该问题由 C 本轮独立发现；原因是外层段索引列表仍用普通 Python 等值比较。首次 [REJECTED 回执](../initial_review.json) 与 [原始结果](../initial_results.json) 保持原样。

主线程接手最小修复后，第二轮重用同一 `probe_f02.py`，只改变输出目录；全部 37 项符合预期，source hash 前后稳定，可信 handle 未被候选修改。正常四点、空任务、空记录、合法全过滤、完整多记录及合法重排均通过；改值、参数／合同偷换、父版本／raw scope、账本／汇总与类型错误均拒绝。

命令（仓库根目录）：

```bash
.venv/bin/python -B task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/c_f02_review/probe_f02.py
.venv/bin/python -B task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/c_f02_review/recheck_f02.py
```

两次退出码均为 0；原探针把误放行写入结果，不用非零退出码表示发现缺陷，验收依据为 JSON 中逐项实际状态。

[第二轮机器回执](review_receipt.json) 包含 `issues.C2-F02.status`、37 项 checked、实际 11 项源码／配置／批准来源 SHA256，可供 GoalJournal 消费。[完整结果](initial_results.json) 记录各用例实际错误与数字。

另做了 [登记参考读取检查](../registered_reference_check.json)：合法注册 `G1_CONDITIONAL_ENU_V1` 的 preflight 为空，读取固定 7 条／783 点；原始时间和值、教师 JSON SHA256 保持不变。来源 `source_crs=UNVERIFIED` 与 `CURRENT_RUN_CONDITIONAL_ANALYSIS` 分类同时保留。该检查只读可信输入／派生工作坐标，不调用 baseline 生产链。

用例命名勘误：`source_clean_final_and_ledger_shifted_together` 的名称多写了 ledger；脚本实际修改的是 source_record、input、clean、final 的首点 x，未改账本。该项只证明这些实际输入／输出改值被拒绝；账本的缺项、重复、理由、原索引检查由单独用例提供。原证据不改名覆盖，本说明明确其实际范围。

全套候选检查为 ENGINEERING_TEST。没有修改生产代码、合同、教师数据或历史证据；无依赖安装、网络／程序内模型调用、commit 或 push。
