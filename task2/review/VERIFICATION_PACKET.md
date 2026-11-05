# 验证包

作者测试与独立核验分别读。测试只验证定义和回归，不证明实际业务改进。

|层面|实际证据|
|---|---|
|最终语法/单测|`../evidence/final_syntax.json`、`../evidence/final_tests.txt`：47个Python实现/脚本、90项测试；专项CLI回归另列|
|CLI工程保护|`../evidence/rl/launcher_guard_01/validation_receipt.json`、`../evidence/evolution/basic_cli_guard/`：帮助不加载实验、既存输出/悬空symlink拒写、数学主体等值；独立入口复验与作者测试分开|
|在线独立|`../evidence/independent_rl_on_online/result.json` 与 `verify_online.py`：独立sum LP、瓶颈枚举/增广、小图及真实1045结果|
|MOO独立|`../evidence/independent_research_on_evolution/REVIEW.md`；`result.json`、`canonical_result.json`、`basic_result.json`、`batch_provenance_result.json`|
|RL独立|`../evidence/independent_ea_on_rl/REVIEW.md`、`result.json`、`policy_result.json`；375rollout、双Q/LT；两条beta1轨迹逐时刻边权及局部精确最大权匹配核对，另含融合与paired统计；不是RL policy最优性证明|
|RL误重放追加|`../evidence/independent_ea_on_rl/replay_review/REVIEW.md`、`result.json`、`recovered_front_result.json`、`cli_guard_independent.json`；旧审原件保留，不把无法恢复runtime伪造回旧身份|
|输入获取/来源|`../evidence/research_data/public_fetch_exact_network_verified.json`；`source_entry_exact_regression.json`；`../evidence/independent_package/exact_public_data_review.json`|
|公开投影与反解边界|`../evidence/independent_package/public_projection_review.json`、`content_probe.json`、`sensitive_classification.json`；最终Git集合另审|
|实际Git内容|`../evidence/independent_package/staged_semantic_review.json`与`PACKAGE_REVIEW_HANDOFF.md`；逐blob审查发现的KM计时membership已精确排除；结构检查与最终有界delta复核另列|
|KM计时元数据修复|`../evidence/evolution/km_runtime_scope_fix/result.json`；5条scope不再错标EA-only；125记录/375组精度指标及所有数值不变，旧原件保留；图表仅来源继承|
|无逐条数据重画|`../evidence/evolution/public_only_figure_build.json`；`../evidence/independent_package/public_rl_render_review.json`|
|Notebook|`../evidence/notebook_execution/`基础attempt3、进阶attempt2返回0；`../evidence/independent_package/notebook_fallback_review.json`与`public_notebook_generator_review.json`|
|报告数字与页面|`../evidence/independent_report_review/`真实320数字、26+8页200dpi检查；末轮3页修订追加；`../evidence/report_build/build_receipt.json`是编译/渲染回执，本身不自动声称视觉通过|
|修复总账|[REVIEW_LOG](../docs/REVIEW_LOG.md)，每项原证据范围与后续继承条件均区分|

CLI与最后元数据的真正独立追加检查在 `../evidence/independent_cli_guard/` 和 `../evidence/independent_final_metadata/`；原source snapshots与旧审查结论仍按各自版本保留。源包当前来源哈希更新只触及sources.json及包内manifest，真正编译资产保持与独立编译时相同；不冒称所有后续版本二进制PDF相等。最终实际集合有界增量结论见 `../evidence/independent_package/final_delta_review.json`。

关键已知答案反例在 `../tests/`：sum不等于bottleneck、丢单平台、零分母与不同基数、非法重复匹配、规范HV、不可行Q动作与WAIT、终止和跨步折扣、Double两个更新分支、物理移动成本、非支持Pareto点。独立程序不调用作者同一个评价器来制造第二个PASS。

未覆盖：真实平台可用性/营收、确认datum的地理精度、跨任意软件环境随机产物bit一致、外部GPT审查、用户理解确认、教师提交及本轮Process UI Evidence Lock。源包只证明报告可编译，公开重画只证明图可重画，两者不替代完整实验复算。
