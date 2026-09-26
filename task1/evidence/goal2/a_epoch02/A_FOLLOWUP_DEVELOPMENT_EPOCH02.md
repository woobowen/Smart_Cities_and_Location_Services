# A：epoch02 开发证据与后续执行

这是一份真实治理 A 的 Followup/TaskPlan，不是 Human Approval。旧版本及原始源码继续保留。

参数与顺序的选择检查已完成；**EVAL readiness=PENDING_LIVE_DEVELOPMENT_AND_INDEPENDENT_C_MODE_REVIEW**。本记录未消费已完成的 epoch02 LIVE 开发证据和模式 C 回执，不能据此提前开启评测。

代码 c1c6272606716f9f59aa785d48bfeadb09c7a30e；合同 db758c097509139596fbc52b4c3f65e921eb1f12d9fb4c239e308abdb57f31f8；candidate_lock a5ed67a3e28a6591063be28df3fb70b0698915b212b010acee7fa580e1aadef8。

| 单项 | 锁定参数 | 开发判定 | 保护通过/记录 | 严格增益记录 |
|---|---|---|---:|---:|
| C-S | {'dt': 30, 'distance': 400, 'min_points': 2, 'min_length': 0, 'direction': 35, 'dp': 5} | SUPPORTED_WITHIN_SCOPE | 120/120 | 54 |
| C-D | {'dt': 30, 'distance': 400, 'min_points': 5, 'min_length': 65, 'direction': 35, 'dp': 5} | NO_DEMONSTRATED_GAIN | 120/120 | 0 |
| C-P | {'dt': 30, 'distance': 400, 'min_points': 5, 'min_length': 65, 'direction': 35, 'dp': 5} | NO_DEMONSTRATED_GAIN | 120/120 | 0 |

C-D/C-P 保留参考是按规则回退，不表示最优，也不省略其留出登记。C-S 的增益只指共同参考覆盖/几何条件，新覆盖区域误差单列，不能称为真实噪声清洗质量提升。

S-D-P 和 S-P-D 进入冻结的阶段顺序评测。S-P-D 虽通过安全条件，仍有几何保护权衡；其余四种顺序保留实际约束失败，不加隐藏分段修复。

- C-STRATIFIED：NOT_ADMITTED_WITH_REASON。No independently justified conditional parameter policy beyond the required controlled parameter experiments; optional scope not filled by invented motion labels.
- C-DIRECTION-GUARD：NOT_ADMITTED_WITH_REASON。No independently justified displacement reliability threshold frozen; no arbitrary low-displacement cutoff introduced.

后续步骤、问题/假设、数据范围、预算、保护项、允许修复与结束条件见同目录 JSON 的 tasks。正式参数评测计划 14 个唯一配置×120 记录；顺序 2×120；模式 4×24×3。这些是计划预算，尚不是已执行评测。完成 LIVE 开发与独立 C 模式检查后，A 需另写实际 readiness，随后才能冻结并开启 G2_EVAL。

旧 A 记录：[epoch01 followup](../a_followup_development.json)；其被本版本替代的原因是代码版本修复后的全量重建，不倒写历史，不将旧 LIVE 重标为新 LIVE。
