# Experiment 1 Interaction Handoff

**真实事实候选索引；供 Evidence Master 检索与进一步审核。** 本稿不决定任何条目进入正式报告，不分配Tier、截图、裁切、高亮、箭头、caption、呈现顺序或LOCK。稳定ID只用于定位，不代表历史/报告顺序。

资料范围：已实际读取的G1授权、G2真实模型响应和阶段证据、当前G3用户Prompt、A计划、旧epoch A1裁决、C06/C07真实修复、当前epoch A1重算及A2/A3裁决。此前 A 撰写部分没有读取选择集或 FINAL_CONFIRM 效果；下方主线程追加部分只在对应冻结之后依据实际产物整理，不向 A 研究上下文传回最终效果。完整结构化字段与源哈希见 [interaction_candidates.json](../../evidence/goal3/interaction_candidates.json)。

当前Prompt只证明当前预先授权。下列系统自主裁决均明确区别于Human Judgment；缺少用户原话、原始消息ID或时间时写NOT_AVAILABLE。C06前A1仍是真实历史决定，但其源码epoch已经失效，不能作为当前有效结果。

## IH-AUTH-D2 · 一次标记、同时删除的明确授权

**真实Trigger：** 已存授权补充明确覆盖先前D1/D2重复审批安排；缺少该补充前后的完整原始网页对话。

**User原话：** AVAILABLE_ARCHIVED_VERBATIM

> 在分段后的输入片段上一次计算教师双侧方向差谓词，
> 完整标记后同时删除；首尾、缺少必要方向或零位移导致
> 无法计算的窗口保留并标记；不迭代删除至收敛；
> 删除后重算相关特征。

来源：[AUTHORIZATION_SUPPLEMENT.md](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)，lines 17-20。原始网页消息ID/日期：NOT_AVAILABLE。

**GPT/Agent提议：** {"status": "PROPOSAL_DETAILS_ONLY_AS_REFERRED_TO_BY_USER", "text": "用户原文说“采用你提出的教学参考删除调度”；在本索引可定位的独立更早GPT原句为NOT_AVAILABLE。不得反向补写那一轮GPT回答。"}

**真实Human Judgment：** AVAILABLE_CURRENT_OR_ARCHIVED_AUTHORIZATION。用户明确批准一次标记同时删除、保留端点与不可计算窗口、不迭代、下游重算。

**实际决定：** {"type": "USER_AUTHORIZATION", "text": "G1/G2/G3沿用同一D2调度；不能写成教师已经给出全部删除调度细节。"}

**可得消息范围：** {"archive_span": "lines 17-20", "original_turn_range": "NOT_AVAILABLE", "neighboring_context": "same authorization supplement §一"}

**为什么可能重要：** 可说明关键算法歧义怎样通过真实用户补充形成明确边界；需要完整原始消息与呈现规格才能制作正式互动证据。

资料/实验：

- [AUTHORIZATION_SUPPLEMENT.md](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)
- [USER_DECISIONS.json](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json)
- [local_model_contract.json](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/a_scope/local_model_contract.json)；定位：fixed_reference_pipeline

## IH-AUTH-CRS · 未知datum的事实状态与条件化工作分开

**真实Trigger：** 已有文件未确认源datum；用户明确允许在固定说明的数学工作坐标中继续被授权分析。

**User原话：** AVAILABLE_ARCHIVED_VERBATIM

> 若无法确认原始 datum，但已有证据支持坐标顺序、
> 角度单位和数据结构，则允许在明确、可追踪的分析假设下，
> 完成固定 pilot 的开发性处理、几何计算、工具验证和闭环。

来源：[AUTHORIZATION_SUPPLEMENT.md](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)，lines 40-42。原始网页消息ID/日期：NOT_AVAILABLE。

> 1. source_crs 的事实状态继续保持 UNVERIFIED。

来源：[AUTHORIZATION_SUPPLEMENT.md](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)，lines 46-46。原始网页消息ID/日期：NOT_AVAILABLE。

**GPT/Agent提议：** {"status": "SOURCED_IMPLEMENTED_MODEL_NOT_ORIGINAL_DIALOGUE", "text": "已登记数学椭球a=6378137、1/f=298.257223563、h=0、固定中心的ECEF→ENU；这是工程分析假设，独立早期GPT逐字提议未在本索引恢复。"}

**真实Human Judgment：** AVAILABLE_CURRENT_OR_ARCHIVED_AUTHORIZATION。允许条件化开发，未确认源WGS84/GCJ02/EPSG；原值不改，不按清洗分数选择坐标模型。

**实际决定：** {"type": "USER_AUTHORIZATION_AND_FIXED_MODEL", "text": "source_crs仍UNVERIFIED；几何正确性与源地理事实分开。后续范围扩大依当前Prompt，不倒写为此条旧消息原已授权全量。"}

**可得消息范围：** {"archive_span": "lines 40-42", "original_turn_range": "NOT_AVAILABLE"}

**为什么可能重要：** 可说明不确定事实不被伪填，且用户明确划定了可继续工程的范围。

资料/实验：

- [AUTHORIZATION_SUPPLEMENT.md](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md)；定位：§二
- [local_model_contract.json](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/a_scope/local_model_contract.json)

## IH-G2-CALIBRATION · 真实模型先保留未知、再给可核验方向预测

**真实Trigger：** G2 DEVELOPMENT的llm+memory+search记录10232，第一轮方向单项后获得该episode允许的实测反馈。

**User原话：** NOT_AVAILABLE

**GPT/Agent提议：** {"status": "RAW_MODEL_RESPONSE_AVAILABLE", "round1": {"candidate_id": "10232-r1", "parameters": {"dt": 30, "distance": 400, "min_points": 5, "min_length": 65, "direction": 60, "dp": 5}, "metric_id": "common_max_error", "predicted_sign": "not_predicted", "reason": "Isolate the direction threshold's effect on protected fidelity; the card cannot establish an error change."}, "round2": {"candidate_id": "10232-r2-a", "parameters": {"dt": 30, "distance": 400, "min_points": 5, "min_length": 65, "direction": 60, "dp": 2}, "metric_id": "n_direction_removed", "predicted_sign": "decrease", "reason": "Direction 60 improved common maximum error and removed 10 versus reference 32. Test tighter DP while preserving that verified direction stage."}, "source_refs": [{"path": "task1/evidence/goal2/runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round1_call/attempt01/response.json", "sha256": "6207cfd3ccfe3cee4b0cf7f12c807cf63a8f0175c9c77bcf3b1dc22c7059ce66", "locator": "records[record_id=10232].proposals[candidate_id=10232-r1]"}, {"path": "task1/evidence/goal2/runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json", "sha256": "fe36cab28325d549ba8118e21e59d53363b7147f4da77b45346d36404e58db98", "locator": "records[record_id=10232].proposals[candidate_id=10232-r2-a]"}], "model": "gpt-6-astra", "reasoning_effort": "medium", "source_kind": "G2_LIVE_EXPERIMENT_NOT_G3_CALL"}

**真实Human Judgment：** NOT_AVAILABLE。没有此项逐次用户判断原文；当前预先授权不替代这一字段。

**实际决定：** {"type": "HISTORICAL_SYSTEM_EVALUATION_NOT_HUMAN_JUDGMENT", "text": "第一轮common_max_error为not_predicted，不强行评分；第二轮预测方向删除量下降，实测-22且预测匹配。该提议未成为锁定输出，不能据此宣称质量改善。", "selected_output": false, "metric_id": "n_direction_removed", "observed_delta": -22.0}

**可得消息范围：** {"run_id": "g2-development-modes-02", "episode_id": "DEVELOPMENT-llm+memory+search-e1-b2", "record_id": "10232", "rounds": [1, 2], "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可用于区分真实可校准预测、不可评价预测与最终方法收益，展示模型原文和真实核验而不制造用户质疑。

资料/实验：

- [receipt.json](../../evidence/goal2/runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/receipt.json)
- [ai_critique_examples.csv](../../evidence/goal2/tables/ai_critique_examples.csv)；定位：candidate_id=10232-r2-a
- [STAGE_ANALYSIS.md](../goal2/STAGE_ANALYSIS.md)；定位：AI 建议与反例核验

## IH-G2-TRADEOFF · 合法建议与自身DP合格仍不能证明共同原始几何更好

**真实Trigger：** G2真实模型在记录7764提出distance200、min_points2、min_length0、direction60、dp5的参数组合。

**User原话：** NOT_AVAILABLE

**GPT/Agent提议：** {"status": "RAW_MODEL_RESPONSE_AVAILABLE", "proposal": {"candidate_id": "7764-r2-a", "parameters": {"dt": 30, "distance": 200, "min_points": 2, "min_length": 0, "direction": 60, "dp": 5}, "metric_id": "raw_break_crossings", "predicted_sign": "unchanged", "reason": "Direction 60 alone left common maximum error unchanged. Test additional spatial splits with relaxed segment filters; existing raw breaks remain separated, while coverage and fidelity require evaluation."}, "source_ref": {"path": "task1/evidence/goal2/runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json", "sha256": "fe36cab28325d549ba8118e21e59d53363b7147f4da77b45346d36404e58db98", "locator": "records[record_id=7764].proposals[candidate_id=7764-r2-a]"}, "source_kind": "G2_LIVE_EXPERIMENT_NOT_G3_CALL"}

**真实Human Judgment：** NOT_AVAILABLE。没有此项逐次用户判断原文；当前预先授权不替代这一字段。

**实际决定：** {"type": "HISTORICAL_SYSTEM_DECISION", "text": "建议合法并真实执行；共同覆盖保持122/122，最大共同误差40.214764→69.145351工作米，触发COMMON_GEOMETRIC_PROTECTION_DEGRADED。自身DP最大4.826420且0超界不能消除共同几何退化；未被锁定采用。", "research_status": "TRADEOFF", "registered_readings": {"status": "TRADEOFF", "feasible": false, "strict_gain": false, "protection_failures": ["COMMON_GEOMETRIC_PROTECTION_DEGRADED"], "baseline_covered_count": 122, "candidate_covered_count": 122, "coverage_delta": 0, "baseline_common_max": 40.214764334442535, "candidate_max_on_baseline_covered": 69.14535092142388, "newly_covered_max_error": null, "numerical_allowance": 2.7017536949079056e-10}, "own_dp_max": 4.826419900439255, "selected_output": false}

**可得消息范围：** {"run_id": "g2-development-modes-02", "episode_id": "DEVELOPMENT-llm+memory+search-e1-b2", "record_id": "7764", "round": 2, "candidate_id": "7764-r2-a", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可支持有来源的AI技术批判：合法性、局部压缩保证和整体共同参考是不同问题；不能把自主审核写成用户现场否决。

资料/实验：

- [receipt.json](../../evidence/goal2/runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/receipt.json)
- [ai_legal_proposal_tradeoffs.csv](../../evidence/goal2/tables/ai_legal_proposal_tradeoffs.csv)；定位：candidate_id=7764-r2-a
- [STAGE_ANALYSIS.md](../goal2/STAGE_ANALYSIS.md)；定位：LEGAL_PROPOSAL_TRADEOFF

## IH-G2-MEMORY · 记忆送达、引用、动作一致与因果收益分开

**真实Trigger：** 已有G2四模式和只读记忆实验形成真实检索/提议回执；指标层级不同。

**User原话：** NOT_AVAILABLE

**GPT/Agent提议：** {"status": "STAGE_ANALYSIS_AVAILABLE_NOT_A_VERBATIM_CHAT_TURN", "text": "既有阶段分析区分retrieved→eligible→delivered→model_cited→action_consistent，未把记忆命中当质量改善。"}

**真实Human Judgment：** NOT_AVAILABLE。没有此项逐次用户判断原文；当前预先授权不替代这一字段。

**实际决定：** {"type": "HISTORICAL_RESEARCH_LIMIT", "text": "96/96有送达，60/241实际决策回合引用有效条目，49/241同时引用且参数一致。这是可观察消费；未证实记忆的因果质量收益。现有G2有效模型派发84次，不能重新命名为G3新调用。"}

**可得消息范围：** {"source_scope": "G2当前有效阶段分析及原始表，非一条完整用户对话", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可解释为什么最终处理策略不必逐条调用模型；没有个人现场判断原话，不能为人机互动叙事补写。

资料/实验：

- [STAGE_ANALYSIS.md](../goal2/STAGE_ANALYSIS.md)；定位：四种模式、预算与记忆
- [memory_consumption.csv](../../evidence/goal2/tables/memory_consumption.csv)
- [memory_independent_mode_comparison.csv](../../evidence/goal2/tables/memory_independent_mode_comparison.csv)
- [current_runs.json](../../evidence/goal2/current_runs.json)

## IH-G3-STAGE-RELAY · 承接阶段验收的证据身份

**真实Trigger：** 本轮Prompt转交G1/G2阶段验收并提供G2交付、代码和结果锚点。

**User原话：** AVAILABLE_ARCHIVED_VERBATIM

> 网页 GPT 已对 Goal 1、Goal 2 完成范围明确的二重验收，用户已确认并要求进入 Goal 3。这是本 Prompt 转交的阶段验收记录；归档为 USER\_RELAYED\_GPT\_STAGE\_ACCEPTANCE，不伪造缺失的网页工具日志、截图或验收附件。

来源：[USER_PROMPT.md](../../evidence/goal3/USER_PROMPT.md)，lines 33-33。原始网页消息ID/日期：NOT_AVAILABLE。

**GPT/Agent提议：** {"status": "NOT_AVAILABLE", "text": "未恢复网页GPT原验收全文、工具日志或截图；不制造对应回复。"}

**真实Human Judgment：** AVAILABLE_CURRENT_OR_ARCHIVED_AUTHORIZATION。这是用户转交的阶段验收记录，不是本地工具重新完成网页二重验收。

**实际决定：** {"type": "USER_RELAYED_GPT_STAGE_ACCEPTANCE", "text": "作为阶段接管事实归档；G3自己的GPT_SECOND_REVIEW仍PENDING。"}

**可得消息范围：** {"source_span": "lines 33-33", "web_review_turn_ids": "NOT_AVAILABLE"}

**为什么可能重要：** 可区分真实转交状态和未提供的原始验收附件，避免伪造网页证据。

资料/实验：

- [USER_PROMPT.md](../../evidence/goal3/USER_PROMPT.md)；定位：§1.1

## IH-G3-AUTONOMY · 当前用户预先批准有限结果驱动决策

**真实Trigger：** G3需要在同一Goal内完成选择、修复、确认、生产和文档；Prompt明确不预定赢家。

**User原话：** AVAILABLE_ARCHIVED_VERBATIM

> 用户已经确认：不提前主观指定最终赢家，由 Codex 在批准范围内依据真实结果形成候选、完成比较、必要组合、接受或拒绝、回退、收敛和工程方案冻结；随后实际完成最终确认、全量处理、正式成果、内部验收和 GitHub 发布。

来源：[USER_PROMPT.md](../../evidence/goal3/USER_PROMPT.md)，lines 15-15。原始网页消息ID/日期：NOT_AVAILABLE。

**GPT/Agent提议：** {"status": "ACTUAL_GOVERNANCE_ARTIFACTS", "text": "A整理有限TaskPlan，C核对合同/分区/候选范围，主线程按规则编排真实B计算；A/C不同真实上下文。", "refs": [{"path": "task1/evidence/goal3/a_candidate_plan.json", "sha256": "ccc11b8efadb3dbce8e6b6d69ccd8e484aa317d655422da2bfb9d8af59ed3f82", "locator": null}, {"path": "task1/evidence/goal3/independent_c/contract_split_receipt.json", "sha256": "a994261cbc5ae03414e29dfa315106dfd9c562ab6c9837fa76d0e6f60919e39c", "locator": null}]}

**真实Human Judgment：** AVAILABLE_CURRENT_OR_ARCHIVED_AUTHORIZATION。用户批准的是范围、预算和接受规则下的自治，不是逐条选出某个参数，也不转移Evidence Master职责。

**实际决定：** {"type": "CURRENT_USER_PREAUTHORIZATION", "text": "后续A裁决均标为“在用户预先批准规则内的系统决定”；不标新增Human Judgment。"}

**可得消息范围：** {"current_prompt_span": "lines 15-15", "earlier_per_trial_user_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可解释研究决策权与工程自治如何由当前明确授权划分；不能据此重构过去具体对话。

资料/实验：

- [USER_PROMPT.md](../../evidence/goal3/USER_PROMPT.md)；定位：§0–1.2
- [a_candidate_plan.json](../../evidence/goal3/a_candidate_plan.json)
- [A_DECISION_INTERFACE.md](../../evidence/goal3/A_DECISION_INTERFACE.md)

## IH-G3-CANDIDATES · 从方向局部收益和退化形成有限G0候选

**真实Trigger：** G2已暴露逐记录证据中D60的3条退化都处于TIME_FLAG层；时间正常组出现局部改善。

**User原话：** NOT_AVAILABLE

**GPT/Agent提议：** {"status": "REAL_A_PROPOSAL", "text": "提出2组TIME_REGULAR_DIRECTION60_V1：原始所有0<dt<=30用60，否则35；保留R0/S0、S消融和一次性P诊断，不扩连续网格。", "source": {"path": "task1/evidence/goal3/a_candidate_plan.json", "sha256": "ccc11b8efadb3dbce8e6b6d69ccd8e484aa317d655422da2bfb9d8af59ed3f82", "locator": null}}

**真实Human Judgment：** NOT_AVAILABLE。没有此项逐次用户判断原文；当前预先授权不替代这一字段。

**实际决定：** {"type": "SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES", "text": "C通过范围一致性检查后准入有限开发；这不是已证G0有效或用户逐条选出G0。", "candidate_status": "PROPOSED_AND_SCOPE_VERIFIED_NOT_RESULT_ACCEPTANCE"}

**可得消息范围：** {"A_artifact_time": "2026-09-27T03:43:36.803823+00:00", "raw_human_turns": "NOT_AVAILABLE", "agent_context": "/root/a_candidates", "C_context": "/root/c_protocol"}

**为什么可能重要：** 可说明候选从真实局部证据与失败产生，且分组属于有限开发假设，不被包装成总体保证。

资料/实验：

- [a_candidate_plan.json](../../evidence/goal3/a_candidate_plan.json)
- [A_CANDIDATE_RATIONALE.md](../../evidence/goal3/A_CANDIDATE_RATIONALE.md)
- [parameter_record_pairs.csv](../../evidence/goal2/tables/parameter_record_pairs.csv)
- [contract_split_receipt.json](../../evidence/goal3/independent_c/contract_split_receipt.json)

## IH-G3-A1-EPOCH01 · 旧源码epoch的A1真实接受与后续失效

**真实Trigger：** 旧run g3-development-parents-01完成240记录/7策略，C按目标哈希核验后，A消费配对结果。

**User原话：** NOT_AVAILABLE

**GPT/Agent提议：** {"status": "REAL_A_DECISION_ARTIFACT", "text": "A按固定保护接受S0为开发incumbent；保留D60退化、P2无压缩收益、P10超预算；继续G0单项。", "source": {"path": "task1/evidence/goal3/A1_DECISION.json", "sha256": "9757d712e52990e286eb3276676675c77ca151ff7b9965c650b6258fc2e8b8cd", "locator": null}}

**真实Human Judgment：** NOT_AVAILABLE。没有此项逐次用户判断原文；当前预先授权不替代这一字段。

**实际决定：** {"type": "SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES", "at_decision": "R0→S0，107条覆盖改善、240/240保护通过；D60有3条退化；P10有173条超共同预算。", "current_validity": "SUPERSEDED_SOURCE_EPOCH_RECOMPUTE_REQUIRED", "old_code_sha": "4d513633065a876520edb0bdfead20c498fac7ac", "old_runtime_sha256": "82a32bc11e21097d4bf5f771ba63de3acdf0877dfb70e63815632ec75f82396a", "explanation": "决定当时真实发生。C06元数据实现修复改变源码epoch，保留旧决定但不能当作当前有效研究产物；需要新run+C后明确RECOMPUTE再确认。"}

**可得消息范围：** {"A_artifact_time": "2026-09-27T04:15:12.840142+00:00", "run_id": "g3-development-parents-01", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可说明真实决策与当前有效版本分离，以及源码依赖改变后不是只改一个汇总CSV；不能将其画成数据质量先升后降。

资料/实验：

- [A1_DECISION.json](../../evidence/goal3/A1_DECISION.json)
- [A1_DECISION.md](../../evidence/goal3/A1_DECISION.md)
- [manifest.json](../../evidence/goal3/runs/g3-development-parents-01/manifest.json)
- [g3-development-parents-01_receipt.json](../../evidence/goal3/independent_c/g3-development-parents-01_receipt.json)
- [C06_impact.json](../../evidence/goal3/C06_impact.json)

## IH-G3-C06 · 不依赖.git的离线复算修复与独立关闭

**真实Trigger：** C真实构造非Git解压根目录，原入口git rev-parse HEAD返回128，在处理前失败。

**User原话：** NOT_AVAILABLE

**GPT/Agent提议：** {"status": "REAL_C_FAILURE_AND_B_REPAIR", "text": "C要求绑定源文件的可移植代码身份；B修复身份元数据读取，拒绝缺失/失配冻结源，保留正常仓库真实HEAD。数学/参数/指标未变。", "failure_source": {"path": "task1/evidence/goal3/independent_c/G3-C06_failure.json", "sha256": "43db3377af498b35f350108543bce3be2a92d2d292d324e599034ac99a20de9c", "locator": null}, "impact_source": {"path": "task1/evidence/goal3/C06_impact.json", "sha256": "dd8ed1709d8f36f204313c38800ec13cc69b7c390caf2fb2a98c5b0a956b0954", "locator": null}}

**真实Human Judgment：** NOT_AVAILABLE。没有此项逐次用户判断原文；当前预先授权不替代这一字段。

**实际决定：** {"type": "SYSTEM_ENGINEERING_REPAIR_WITHIN_PREAUTHORIZATION", "engineering_status": "VERIFIED", "text": "独立C已核验可移植源码身份修复与450项当前epoch回归；旧A1/A2保留为历史并要求重建。实际全量ZIP复算与新epoch研究产物仍是未覆盖闭合要求。", "actual_test_result": {"tests": 450, "failures": 0, "errors": 0, "skipped": 0}, "unchecked": ["Actual full production ZIP recomputation; remains required before package acceptance", "Current-epoch development outputs; parent must rebuild before research continuation"]}

**可得消息范围：** {"issue_id": "G3-C06", "C_context": "/root/c_protocol", "B_owner": "root", "C_closure_time": "2026-09-27T04:21:11.217528+00:00", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可说明部署/复算工程问题怎样进入真实修复闭环。它本身不是用户观点或清洗质量改善，也不自动满足正式Process Report入选条件。

资料/实验：

- [G3-C06_failure.json](../../evidence/goal3/independent_c/G3-C06_failure.json)
- [C06_impact.json](../../evidence/goal3/C06_impact.json)
- [G3-C06_closure.json](../../evidence/goal3/independent_c/G3-C06_closure.json)
- [core_after_C06_receipt.json](../../evidence/goal3/independent_c/core_after_C06_receipt.json)

## IH-G3-EVIDENCE-BOUNDARY · 过程事实索引与Evidence Master正式呈现权限分开

**真实Trigger：** 当前交付需要Process Report，但本地现有原文、截图与批准呈现规格并不等同。

**User原话：** AVAILABLE_ARCHIVED_VERBATIM

> 用户新的当前授权可以准确作为本轮授权保存，但不能倒写成过去各次具体实验由用户逐项决定。无真实原话/日期就保持字段空并解释，不填想象中的对话。

来源：[USER_PROMPT.md](../../evidence/goal3/USER_PROMPT.md)，lines 374-374。原始网页消息ID/日期：NOT_AVAILABLE。

**GPT/Agent提议：** {"status": "CURRENT_INDEX_ARTIFACT_ONLY", "text": "本角色建立带真实源定位的Interaction Handoff，系统裁决与Human Judgment分开；未生成截图、裁切、高亮、箭头或LOCK。"}

**真实Human Judgment：** AVAILABLE_CURRENT_OR_ARCHIVED_AUTHORIZATION。当前用户明确禁止把授权倒写成历史逐次判断。

**实际决定：** {"type": "CURRENT_USER_AUTHORITY_BOUNDARY", "text": "有来源的候选索引可先交付；正式入选、Tier、截图呈现、annotation、caption、顺序和LOCK留给Evidence Master。元数据/原始Evidence缺项不编造。"}

**可得消息范围：** {"current_prompt_span": "lines 374-374", "historical_annotation_approval_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可防止自治技术决策被误写为每一次都由用户现场指导，也说明送审稿哪些部分仍依赖外部原始证据。

资料/实验：

- [USER_PROMPT.md](../../evidence/goal3/USER_PROMPT.md)；定位：§14–15
- [WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md)；定位：§3–4、10–18
- [DELIVERY_INPUT_INVENTORY.md](../../evidence/goal3/DELIVERY_INPUT_INVENTORY.md)；定位：§4

## 后续补齐边界

已存模型JSON、工程文件和当前Prompt不是原生ChatGPT网页截图。完整历史相邻消息、实际用户判断、Evidence Master批准规格与LOCK缺项按[输入盘点](../../evidence/goal3/DELIVERY_INPUT_INVENTORY.md)处理；本稿不补写对话。C06/C07实现修复后的当前epoch开发重建已由独立C核验，见本次增补的A1重算、A2与A3条目。上文旧事件中的未覆盖事项均保留为当时回执范围，不被倒写；最终ZIP全量复算不在本索引作者已查范围。后续新实验由主线程提供后另行增补，不将RECOMPUTE记为新LIVE模型提议。

## 本次增补的开发事实

以下稳定ID仍仅用于检索，不构成Evidence Master选定顺序。四项均没有可定位的逐次用户判断原话，Human Judgment为NOT_AVAILABLE；实际决定属于用户预先批准规则内的系统决定。

### IH-G3-C07 · 相对路径缓存失败、源码失效与父任务恢复

**真实Trigger：** 真实routing-02在处理任何记录前失败；C另用相对parent路径构造两项失败，确认Path(parent)未先规范为绝对路径就调用relative_to(absolute_ROOT)。

**User原话及来源：** NOT_AVAILABLE。当前Prompt仅证明当前预先授权。

**GPT/Agent提议：** B只规范parent路径，保留源码epoch拒绝旧缓存的约束；C核验相对路径成功、旧epoch拒绝、新run重建后缓存恢复。

**真实Human Judgment：** NOT_AVAILABLE；没有将系统裁决冒写成用户逐次选择。

**实际决定：** 452项当前epoch回归通过；源码改变使parents-02/routing-02保留为失效历史。C07关闭回执当时不覆盖新开发重建；后续parents-03/routing-03另有独立回执和A裁决。

**可得消息范围：** {"issue_id": "G3-C07", "C_context": "/root/c_protocol", "B_owner": "root", "C_closure_time": "2026-09-27T04:31:39.761313+00:00", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可核查修复并非修改研究规则；旧结果失效后有实际重建与恢复，不把技术回归通过画成数据质量提升。

资料/实验：

- [G3-C07_failure.json](../../evidence/goal3/independent_c/G3-C07_failure.json)
- [C07_impact.json](../../evidence/goal3/C07_impact.json)
- [G3-C07_closure.json](../../evidence/goal3/independent_c/G3-C07_closure.json)
- [core_after_C07_receipt.json](../../evidence/goal3/independent_c/core_after_C07_receipt.json)
- [A1_RECOMPUTE03_DECISION.json](../../evidence/goal3/A1_RECOMPUTE03_DECISION.json)
- [A2_DECISION.json](../../evidence/goal3/A2_DECISION.json)


### IH-G3-A1-RECOMPUTE03 · 修复后重算旧提议并重建当前有效裁决

**真实Trigger：** C06/C07改变元数据与路径接口；旧epoch A1决定真实存在，但不能沿用作当前有效运行。

**User原话及来源：** NOT_AVAILABLE。当前Prompt仅证明当前预先授权。

**GPT/Agent提议：** 使用此前真实登记的原策略，在CODE6ab1091固定后重算parents-03；数学、参数、比较规则不变，不声称新的LIVE被测模型提议。

**真实Human Judgment：** NOT_AVAILABLE；没有将系统裁决冒写成用户逐次选择。

**实际决定：** 当前240条上S0相对R0全保护，107条严格覆盖改善；保留D60的3条退化、P2无压缩收益和P10的173条超预算。开发incumbent恢复为S0，允许按旧计划继续G0。

**可得消息范围：** {"run_id": "g3-development-parents-03", "A_context": "/root/a_candidates", "decision_artifact_time": "2026-09-27T04:42:48.006878+00:00", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可区分真实历史提议、当前代码下RECOMPUTE和新增模型调用；源版本修复没有伪造新研究发现。

资料/实验：

- [A1_DECISION.json](../../evidence/goal3/A1_DECISION.json)
- [A1_RECOMPUTE03_DECISION.json](../../evidence/goal3/A1_RECOMPUTE03_DECISION.json)
- [manifest.json](../../evidence/goal3/runs/g3-development-parents-03/manifest.json)
- [g3-development-parents-03_receipt.json](../../evidence/goal3/independent_c/g3-development-parents-03_receipt.json)
- [g3-development-parents-03_pairs_receipt.json](../../evidence/goal3/independent_c/g3-development-parents-03_pairs_receipt.json)


### IH-G3-A2 · 单项G0有独立价值但不能替代已有覆盖增益

**真实Trigger：** G0在已暴露240条原始时间诊断上执行，父项trace逐一重验；独立C核验后A消费完整配对。

**User原话及来源：** NOT_AVAILABLE。当前Prompt仅证明当前预先授权。

**GPT/Agent提议：** 使用固定两个原始时间组，无record_id路由：全部相邻差满足0<dt<=30秒时direction60，其余direction35。规则从旧开发证据提出，不读取选择或最终反馈。

**真实Human Judgment：** NOT_AVAILABLE；没有将系统裁决冒写成用户逐次选择。

**实际决定：** G0相对R0全240保护、41条几何严格改善；相对S0会丢6704覆盖点，107条失败，因此保留incumbent S0。S0/G0两个父项已各自受支持，准入既有S0_G0组合，不预判组合结果。

**可得消息范围：** {"run_id": "g3-development-routing-03", "A_context": "/root/a_candidates", "decision_artifact_time": "2026-09-27T04:42:48.006878+00:00", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可呈现“相对最初参考有收益”与“可以替换当前方案”不同；必须保护已获得覆盖，不能用语言评分抵消。

资料/实验：

- [a_candidate_plan.json](../../evidence/goal3/a_candidate_plan.json)
- [A2_DECISION.json](../../evidence/goal3/A2_DECISION.json)
- [manifest.json](../../evidence/goal3/runs/g3-development-routing-03/manifest.json)
- [record_pairs.csv](../../evidence/goal3/runs/g3-development-routing-03/analysis/record_pairs.csv)
- [g3-development-routing-03_receipt.json](../../evidence/goal3/independent_c/g3-development-routing-03_receipt.json)
- [g3-development-routing-03_pairs_receipt.json](../../evidence/goal3/independent_c/g3-development-routing-03_pairs_receipt.json)


### IH-G3-A3 · 真实组合与去除对照后收敛，P负结果保留

**真实Trigger：** A2两个父项均支持后，B按既有11策略定义运行interactions-01；C的全trace、数学抽样、配对和执行计数回执均VERIFIED。

**User原话及来源：** NOT_AVAILABLE。当前Prompt仅证明当前预先授权。

**GPT/Agent提议：** 顺序消费S0_G0、S0_P2、S0_P10，分别保留R0、父项、当前incumbent和去除组件比较；不事后增候选。

**真实Human Judgment：** NOT_AVAILABLE；没有将系统裁决冒写成用户逐次选择。

**实际决定：** S0_G0相对S0全240保护、41条几何严格改善，相对R0新增6704覆盖点且142条严格改善，更新开发incumbent。移除G0损失41条几何性质，移除S损失6704覆盖点。P2组合无P压缩收益且相对S0退化9条、相对更新incumbent退化43条；P10组合178条超预算。收敛并固定最多4个选择前短名单R0→S0→G0→S0_G0。

**可得消息范围：** {"run_id": "g3-development-interactions-01", "A_context": "/root/a_candidates", "decision_artifact_time": "2026-09-27T04:58:57.952042+00:00", "original_human_chat_turns": "NOT_AVAILABLE"}

**为什么可能重要：** 可核查为什么采用该开发组合以及为何拒绝P变体，区分有限收敛、实际收益与未获证明的质量解释。这个系统决定不是虚构用户逐次选择。

资料/实验：

- [A3_DECISION.json](../../evidence/goal3/A3_DECISION.json)
- [CONVERGENCE_REVIEW.json](../../evidence/goal3/CONVERGENCE_REVIEW.json)
- [CONVERGENCE_REVIEW.md](../../evidence/goal3/CONVERGENCE_REVIEW.md)
- [manifest.json](../../evidence/goal3/runs/g3-development-interactions-01/manifest.json)
- [summary.json](../../evidence/goal3/runs/g3-development-interactions-01/analysis/summary.json)
- [g3-development-interactions-01_receipt.json](../../evidence/goal3/independent_c/g3-development-interactions-01_receipt.json)
- [g3-development-interactions-01_pairs_receipt.json](../../evidence/goal3/independent_c/g3-development-interactions-01_pairs_receipt.json)
- [g3-development-interactions-01_accounting_receipt.json](../../evidence/goal3/independent_c/g3-development-interactions-01_accounting_receipt.json)

<!-- ROOT_POSTFREEZE_APPEND -->

以下由主线程按真实产物追加。治理工具事件只保存可得元数据；平台加密载荷的哈希不表示已恢复消息原文。

## IH-G3-C08 · 审核必须指向当前分片和源码，不能只相信旧通过回执

**真实 Trigger：** 独立 C 在首次选择冻结前构造真实执行的篡改夹具，发现辅助门控接受已改变分片、错源码版本和缺失审核目标。

**User 原话与真实 Human Judgment：** NOT_AVAILABLE。当前预先授权不替代逐次判断。

**GPT/Agent 提议：** 主线程修复 verified_run，逐一核对真实分片、C 回执全部目标、回执/运行/当前源码三方身份；独立 C 重跑五项夹具及三次既有开发运行。

**实际决定：** 初次 1 项通过、4 项失败；修复后 5 项通过，18 个真实开发分片通过当前性核对。数值实现未改变；这是工程修复，不是数据质量收益。修复关闭后才固定选择阶段。

**可得范围：** 实际产物时间 2026-09-27T05:12:10.788136+00:00；主线程 /root、独立 C /root/c_protocol。原始 Human 聊天消息范围 NOT_AVAILABLE。

**为什么可能重要：** 可说明实际问题、最小修复、独立关闭与父任务恢复，避免把一份旧 PASS 回执用于新产物。

资料/实验：

- [G3-C08_failure.json](../../evidence/goal3/independent_c/G3-C08_failure.json)
- [C08_impact.json](../../evidence/goal3/repairs/C08_impact.json)
- [G3-C08_closure.json](../../evidence/goal3/independent_c/G3-C08_closure.json)
- [selection_freeze.json](../../evidence/goal3/selection_freeze.json)

## IH-G3-SELECTION · 开发支持的方向组合在选择集出现退化，发布候选回到 S0

**真实 Trigger：** 四个完整策略和规则已冻结后，实际处理 240 条 G3_SELECTION；G0 和 S0_G0 在 3017、9311、9534 三条共同参考几何退化。

**User 原话与真实 Human Judgment：** NOT_AVAILABLE。当前预先授权不替代逐次判断。

**GPT/Agent 提议：** 确定性选择器依预登记 R0→S0→G0→S0_G0 顺序消费完整配对；C 独立重算全部三条失败的四个策略，定位为方向保留集合改变后的 DP 交互。

**实际决定：** S0 相对 R0 全 240 条保护通过，103 条严格覆盖增加，共新增 6,625 点。G0/S0_G0 即时 P 误差仍低于 5 工作米，但不能抵消三条共同几何退化；保持 S0，未修改分组或阈值。开发 incumbent S0_G0 的支持只属于开发范围。

**可得范围：** 实际产物时间 2026-09-27T05:20:08.103086+00:00；主线程 /root、独立 C /root/c_protocol。原始 Human 聊天消息范围 NOT_AVAILABLE。

**为什么可能重要：** 可展示组合未被预设为最终赢家，局部保证与共同参考保护不同；负结果被保留而非反复调到获胜。

资料/实验：

- [selection_freeze.json](../../evidence/goal3/selection_freeze.json)
- [selection_decision.json](../../evidence/goal3/selection_decision.json)
- [selection_failure_receipt.json](../../evidence/goal3/independent_c/selection_failure_receipt.json)
- [selection_closure_receipt.json](../../evidence/goal3/independent_c/selection_closure_receipt.json)

## IH-G3-FINAL-CONFIRM · 一次性最终确认支持冻结 S0，未在最终集选择新方案

**真实 Trigger：** S0 主候选、R0 预设回退、600 条完整记录、代码和保护规则在打开最终结果前冻结。

**User 原话与真实 Human Judgment：** NOT_AVAILABLE。当前预先授权不替代逐次判断。

**GPT/Agent 提议：** B 按冻结参数运行 R0/S0；C 核查 1,200 份实际 trace、完整配对及 40 条记录的 80 份独立数学重算，再由预登记发布门控裁决。

**实际决定：** 600 条全部保护通过，349 条严格覆盖增加；共同覆盖 35,868→62,220，显式保留 10,991→12,114。采用 S0，未触发 R0 回退；没有最终集调参或新赢家选择。新增覆盖最大原始偏差 6.087102 工作米，不是噪声准确率。

**可得范围：** 实际产物时间 2026-09-27T05:31:20.009683+00:00；主线程 /root、独立 C /root/c_protocol。原始 Human 聊天消息范围 NOT_AVAILABLE。

**为什么可能重要：** 可说明开发、选择、最终确认的边界，以及系统遵守用户预先规则而非伪造逐次 Human Judgment。

资料/实验：

- [final_freeze.json](../../evidence/goal3/final_freeze.json)
- [manifest.json](../../evidence/goal3/runs/g3-final-confirm-01/manifest.json)
- [release_decision.json](../../evidence/goal3/release_decision.json)
- [confirmation_closure_receipt.json](../../evidence/goal3/independent_c/confirmation_closure_receipt.json)

## IH-G3-FULL-BOUNDARY · 扩大覆盖后仍公开原始几何偏差很大的边界案例

**真实 Trigger：** 冻结后全量处理的新增覆盖最大偏差远大于 5 工作米；主线程要求 C 定位并从原始值独立核查，不改变方法。

**User 原话与真实 Human Judgment：** NOT_AVAILABLE。当前预先授权不替代逐次判断。

**GPT/Agent 提议：** C 枚举所有 11,386 条记录的新增覆盖集合，并用 Decimal/PROJ 重算最差 record 352/index 105 的参考和最终轨迹，区分 S 过滤、D 删除与 P 即时输入。

**实际决定：** 新增覆盖共 500,312 点；最差点偏差 266.01675442514176 工作米。原窗口 [104,105,106,107] 被 R0 因点数不足过滤；S0 的 D 删除 105，P 输入/输出均 [104,106,107]。这是实际方法局限，局部 P 没有删点；保留冻结 S0 和负面案例，不把覆盖增长称为噪声识别准确率。此专项回执不代替另行的全量总审。

**可得范围：** 实际产物时间 2026-09-27T06:15:12.849250+00:00；主线程 /root、独立 C /root/c_protocol。原始 Human 聊天消息范围 NOT_AVAILABLE。

**为什么可能重要：** 可呈现扩大真实范围后仍保留限制、准确追溯阶段责任的过程事实；这不是虚构用户质疑，也不是看过全量后重新调参。

资料/实验：

- [production_freeze.json](../../evidence/goal3/production_freeze.json)
- [manifest.json](../../evidence/goal3/runs/g3-full-production-01/manifest.json)
- [new_coverage_boundary_receipt.json](../../evidence/goal3/independent_c/new_coverage_boundary_receipt.json)
