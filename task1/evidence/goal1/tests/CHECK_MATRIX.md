# 测试证据索引

现状测试先于代码修改。第一次系统pytest缺失，创建项目venv后运行原starter测试，仓库根cwd得到 **289 passed / 3 failed / 1 skipped**，详见 [原日志](starter_baseline.txt)、[JUnit](starter_baseline.xml)、[命令](starter_baseline_command.json)。3个失败属于test_tools相对vault_stub路径：切到starter实际cwd，仅重跑这3项，结果 **3 passed**，见 [修正cwd日志](starter_cwd_fix.txt)。未修改教师测试或实现；没有把这3项复测伪称完整292项重跑。旧测试中的历史样本/Mock输出不算本轮正式实验。

当前工作实现 **108 passed / 0 failed / 0 skipped**：[实际JUnit](final_bound.xml)、[逐case结果与代码hash](case_results.json)。测试调用为 `.venv/bin/python -m pytest task1/tests -q --junitxml=task1/evidence/goal1/tests/final_bound.xml`。绑定0b7914df；随后只修改制图/归档复算脚本，workflow与tests内容hash未变。早期 `final.txt/final.xml` 是82项开发阶段记录，不能代表修复后的最终套件。

| 承诺 | 测试ID/输入来源 | 预期与实际证据 |
|---|---|---|
| 分段、过滤与归属 | test_geo09/10/11、test_eval08/09；CONSTRUCTED_FIXTURE | 严格阈值等号、右端归属、过滤独立、无跨记录连接、全点去向；正例通过，漏点/改值反例拒绝 |
| 方向/速度与邻接 | test_geo05/06/07/08/16/17 | 359/1循环差、零位移无方向、零dt无速度、命名字段不交换、新邻接重算；调度歧义阻断，未伪实现去噪 |
| 有限线段/退化/DP | test_finite_segment_known_answers、test_geo12/13/14 | (2,1)到[(0,0),(1,0)]为sqrt(2)，退化为端点距离；短轨迹/重复/闭合/回头/有序原始索引 |
| 独立误差审核 | test_eval01/02/03/04 | 故意超阈值输出被拒；按索引区间而非全局最近段；改变production距离函数仍由独立oracle发现错误 |
| 指标与不变量 | test_eval06/07/10/11、test_geo15 | 空分母/零长度结构化null，saving分母不掺入去噪过滤，固定数值容忍、平移/旋转/同尺度缩放；未把平面规律套到经纬度 |
| 改进准入 | test_eval12/13/14 | null门槛PENDING_RESEARCH_REVIEW；构造正收益/退化反例按同逻辑判定；非有限值拒绝 |
| 请求/权限 | test_scope_and_schema_denials、test_unapproved_metric_and_goal_denied、test_illegal_paths、test_symlink_escape_denied、test_contract_protected、test_raw_hash_mismatch_denied | 越方法/参数/版本/路径/holdout、未知语义或修改保护文件均拒绝；正确fixture诊断并非全拒 |
| 缓存/伪成功 | test_output_tampering_is_rejected、test_cached_output_self_hash_cannot_replace_registered_hash、test_bad_tool_does_not_advance_or_upgrade | 文件hash、父版本、输入、缺失、状态伪造、REJECTED/BLOCKED结果均不被升级 |
| 恢复 | test_preplanted_live_response_is_rejected_without_model、test_recovery_requires_bound_visible_call_evidence、test_valid_recovery_executes_once_without_new_model、test_failure_preserves_old_artifacts_and_resume_does_not_repeat_effect | 预置response/空receipt不能LIVE；缺事件、不同input/response、非法工具事件被拒；完整构造恢复只执行一次且新模型调用0 |
| Provider | test_jsonl_and_schema_are_strict_and_reasoning_not_saved、test_unexpected_cli_tools_cannot_pass、test_tool_start_event_is_a_violation_even_with_valid_final、test_intentionally_disabled_code_host_requires_completed_valid_turn | 严格JSONL/schema；非法工具start/completed即拒；隐藏reasoning不保存；只有精确已知禁用提示可与合法完成事件共存 |
| 中断/预算/模式 | test_timeout_kills_child_process_group、test_budget_cannot_reset_by_new_run_id、test_budget_freeze_cannot_be_reset_with_new_run_id、test_final_policy_disables_all_new_live_calls、test_search_only_no_llm_and_mock_not_live、test_unavailable_provider_never_succeeds | 子进程被回收、预算共享且冻结；SEARCH_ONLY不得LLM，Mock/无provider不能假LIVE；不把构造恢复记录发布为LIVE |
| 数值诊断审核 | test_known_raw_fixture_counts_and_time_partition、test_recompute_accepts_same_record_set_in_different_order、test_mock_time_partitions_keep_mock_classification、test_independent_profile_review_checks_all_reported_numeric_fields | 手算计数/时间边界正确，合法顺序变化不误拒，MOCK标签不变REAL，篡改多个统计字段被独立核验拒绝 |
| 原始材料保护 | [原始117文件最终hash](../validation/original_integrity.json) | 教师、raw、starter、治理、模板与installed plotting Skill字节未变 |
| 实际可复算入口 | [Notebook新内核记录](../validation/notebooks.json)、[旧CODE真实复算](../validation/replay_result.json) | 每Notebook 6个code cell运行成功；重新读取raw计算，不只打印旧CSV；旧run仅source_evidence可复算 |

[独立控制器审查](INDEPENDENT_CONTROL_REVIEW.md)另保留9项修复前反例、修复后108pass和中断/保存事件的独立复验。这些全部是ENGINEERING_TEST；其价值在发现原测试遗漏，不是自然多Agent反馈链。真实网络重试没有修复后复验，不能因这些PASS将G1-A13写PASS。
