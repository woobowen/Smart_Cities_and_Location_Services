"""A's actual development-only readiness record; no model/processing dispatches.

Reuses the fixed analysis reader, checks the independent C targets, and consumes
all current development proposals. It neither selects new parameters nor reads
holdout method outcomes. The previous partial A followup is retained unchanged.
"""
from collections import Counter, defaultdict
from pathlib import Path
from time import perf_counter

from task1.scripts.build_goal2_analysis import (
    EVIDENCE, Inputs, actual_ai_critique, memory_analysis, mode_analysis,
    mode_statistics, relative, resource_accounting,
)
from task1.workflow.io import ROOT, digest, now, object_hash, read_json, write_json


def binding(path):
    return {"path": relative(path), "sha256": digest(path)}


def main():
    started, timer = now(), perf_counter()
    directory = Path(__file__).resolve().parent
    output = directory / "A_EVALUATION_READINESS.json"
    if output.exists():
        raise ValueError("READINESS_ALREADY_EXISTS_PRESERVE_ORIGINAL")
    observed_path = directory / "live_development_observations/summary.json"
    observed = read_json(observed_path)
    # The root may register holdout work while A is writing its development-only
    # followup. Reconstruct the exact already-consumed registry snapshot, whose
    # original byte hash was saved before that concurrent registration.
    current = {"counterexamples": "task1/evidence/goal2/counterexamples/formal-02",
        "parameter_development": "g2-development-parameters-02",
        "order_development": "g2-development-orders-02",
        "memory": "g2-demo-memory-02", "mode_development": "g2-development-modes-02"}
    current_path = EVIDENCE / "a_epoch02_development_registry_snapshot.json"
    if not current_path.exists():
        write_json(current_path, current, exclusive=True)
    if (read_json(current_path) != current or digest(current_path) !=
            observed["input_hashes"]["task1/evidence/goal2/current_runs.json"]):
        raise ValueError("A_DEVELOPMENT_SNAPSHOT_DIFFERS_FROM_ALREADY_READ_REGISTRY")
    inputs = Inputs(current_path)
    if current["mode_development"] != "g2-development-modes-02" or inputs.freeze is None:
        raise ValueError("EXPECTED_COMPLETED_EPOCH02_AND_ACTUAL_FREEZE")
    analysis_path = ROOT / "task1/scripts/build_goal2_analysis.py"
    analysis_hash = digest(analysis_path)
    if analysis_hash != "0a7ad0743e8f4fe0344ba1d0b97bb2fd6acf54f1c059e0a6224ab9c00d88281d":
        raise ValueError("ANALYSIS_VERSION_CHANGED_SINCE_DEVELOPMENT_FACTS")
    prior_path = directory / "A_FOLLOWUP_DEVELOPMENT_EPOCH02.json"
    prior = read_json(prior_path)
    if (prior["candidate_lock"]["sha256"] != inputs.freeze["candidate_lock_sha256"] or
            prior["contract_sha256"] != inputs.contract_hash or
            prior["split_sha256"] != inputs.split_hash):
        raise ValueError("PRE_LIVE_A_FOLLOWUP_CHANGED_PARENT")
    receipts = {}
    for label, filename in (
            ("complete_development_modes", "development_modes_epoch02_receipt.json"),
            ("candidate_lock", "candidate_lock_epoch02_receipt.json"),
            ("evaluation_freeze", "evaluation_freeze_epoch02_receipt.json")):
        path = EVIDENCE / "c_contract" / filename
        receipt = read_json(path)
        if receipt["status"] != "VERIFIED" or receipt["errors"] or receipt["role_context"] != "/root/c_contract":
            raise ValueError("INDEPENDENT_C_RECEIPT_NOT_VERIFIED")
        for target in receipt["targets"]:
            if digest(ROOT / target["path"]) != target["sha256"]:
                raise ValueError("INDEPENDENT_C_TARGET_MISMATCH")
        for source, sha256 in receipt["source_hashes"].items():
            if digest(ROOT / source) != sha256:
                raise ValueError("INDEPENDENT_C_SOURCE_MISMATCH")
        audit = receipt["audit_program"]
        if digest(ROOT / audit["path"]) != audit["sha256"]:
            raise ValueError("INDEPENDENT_C_AUDIT_SOURCE_MISMATCH")
        receipts[label] = {**binding(path), "status": receipt["status"],
            "classification": receipt["classification"], "targets": receipt["targets"],
            "checks": receipt.get("check_count", receipt.get("checks")),
            "checked_components": receipt["checked_components"],
            "unchecked_components": receipt["unchecked_components"]}
    for role, sha256 in inputs.freeze["development_manifest_hashes"].items():
        if digest(inputs.manifests[role][0] / "manifest.json") != sha256:
            raise ValueError("FREEZE_DEVELOPMENT_MANIFEST_MISMATCH")
    for source, sha256 in inputs.freeze["processing_source_hashes"].items():
        if digest(ROOT / source) != sha256:
            raise ValueError("FREEZE_PROCESSING_SOURCE_MISMATCH")
    tables = defaultdict(list)
    memory = memory_analysis(inputs, tables)
    records = mode_analysis(inputs, tables)
    mode_statistics(tables, records)
    critique = actual_ai_critique(tables)
    costs = resource_accounting(inputs, tables)
    for table in observed["table_registry"].values():
        if digest(ROOT / table["path"]) != table["sha256"]:
            raise ValueError("A_DEVELOPMENT_OBSERVATION_TABLE_CHANGED")
    for key, value in (("mode_summary", tables["mode_summary"]), ("memory", memory),
                       ("actual_ai_critique", critique), ("costs", costs)):
        if observed[key] != value:
            raise ValueError("A_DEVELOPMENT_OBSERVATIONS_NOT_REPRODUCED:" + key)
    common_model = inputs.contract["modes"]["common_model"]
    for call in tables["model_calls"]:
        actual_receipt = read_json(ROOT / call["receipt_path"])
        if (call["requested_model"] != common_model["model"] or
                call["reasoning_effort"] != common_model["reasoning_effort"] or
                call["seed"] != common_model["seed"] or actual_receipt["model_tools"] or
                call["status"] != "VERIFIED_STRUCTURE_ONLY"):
            raise ValueError("CURRENT_LIVE_MODEL_CONFIGURATION_MISMATCH")
    candidate_index = {(row["episode_id"], row["record_id"], row["config_id"]): row
                       for row in tables["mode_candidates"]}
    negative_proposals = []
    proposal_statuses = Counter()
    for proposal in tables["mode_proposals"]:
        candidate = candidate_index.get((proposal["episode_id"], proposal["record_id"],
                                         proposal["executed_config_id"]))
        if candidate is None:
            continue
        proposal_statuses[candidate["status"]] += 1
        if candidate["status"] in ("REJECTED_BY_CONSTRAINT", "TRADEOFF"):
            negative_proposals.append({"proposal": proposal, "actual_comparison": candidate,
                "A_action": "Retain the real negative candidate and observed protection failure; do not promote it or relax the guard. Continue the already frozen comparison without a new method."})
    negative_proposals.sort(key=lambda row: (row["proposal"]["mode"], row["proposal"]["record_id"],
        row["proposal"]["round"], row["proposal"]["proposal_number"]))
    result = {
        "goal_id": inputs.contract["goal_id"], "role": "A", "role_context": "/root/a_contract",
        "version": "EPOCH02_POST_LIVE_READINESS_V1", "status": "READY_FOR_FROZEN_G2_EVAL",
        "classification": "ACTUAL_GOVERNANCE_FOLLOWUP_NOT_HUMAN_APPROVAL",
        "started_at": started, "ended_at": now(), "elapsed_seconds": perf_counter() - timer,
        "supplements": {**binding(prior_path), "prior_original_preserved": True,
            "meaning": "The earlier record's LIVE/C readiness dependency is now satisfied. Its frozen choices and future-task definitions are unchanged."},
        "read_scope": ["DEVELOPMENT current run evidence", "DEMO_MEMORY frozen admissions", "fixed split/evaluation plan metadata", "historical request cost receipts only"],
        "read_scope_snapshot": {**binding(current_path), "original_observation_at": observed["at"],
            "original_current_registry_byte_hash_reproduced": True,
            "concurrent_root_progress": "Root registered evaluation after the development observations were collected; A finalization uses only this exact prior development registry snapshot. No evaluation manifest or method result is opened."},
        "evaluation_method_results_read": False, "new_model_calls": 0,
        "new_candidate_processing_runs": 0, "new_memory_writes": 0,
        "source_hashes": {relative(analysis_path): analysis_hash, relative(Path(__file__)): digest(Path(__file__))},
        "code_sha": inputs.manifests["mode_development"][1]["code_head_at_start"],
        "raw_sha256": inputs.split["raw_sha256"], "contract_sha256": inputs.contract_hash,
        "split_sha256": inputs.split_hash, "source_crs": "UNVERIFIED",
        "evaluation_freeze": binding(EVIDENCE / "evaluation_freeze.json"),
        "candidate_lock": binding(EVIDENCE / "candidate_lock.json"),
        "independent_C_receipts_consumed": receipts,
        "A_scope": "Full 12 episode artifact hashes, all96 record-episode trace/proposal/receipt bindings, registered budgets, saved assessments, same24 IDs per mode, all60 memory admissions, retrieval parents and before/after hashes. No independent raw-DP rerun is claimed by A; C's checked/unchecked scopes remain explicit.",
        "input_hashes": inputs.lineage, "observations": binding(observed_path),
        "mode_summaries": tables["mode_summary"], "locked_outcomes": observed["mode_locked_statuses"],
        "all_candidate_outcomes": dict(Counter(row["status"] for row in tables["mode_candidates"])),
        "actual_model_proposal_outcomes": dict(proposal_statuses),
        "actual_negative_model_proposals": negative_proposals,
        "actual_AI_critique": critique,
        "memory_snapshot": memory, "memory_retrieval": observed["memory_retrieval"],
        "memory_consumption": observed["memory_consumption"],
        "memory_independent_comparison": observed["memory_independent_comparison"],
        "costs": costs,
        "model_configuration_observed": {"requested_models": sorted({row["requested_model"] for row in tables["model_calls"]}),
            "reasoning_efforts": sorted({row["reasoning_effort"] for row in tables["model_calls"]}),
            "cli_versions": sorted({row["cli_version"] for row in tables["model_calls"]}),
            "seed": "unavailable", "exact_provider_request_count": "unknown"},
        "A_followup_decisions": [
            {"id": "KEEP_FROZEN_SCOPE", "evidence": "All development structures/budgets/provenance and actual freeze independently VERIFIED.",
             "action": "Proceed with fixed120-record parameter/order evaluation and four modes on the fixed24-record subset for three episodes. No setting, model, template, memory, metric, selector or candidate changes."},
            {"id": "CONSUME_NEGATIVE_PROPOSALS", "evidence": "Four actual LLM proposals produced TRADEOFF;148 were legal/executed, no illegal proposal or fallback and no evaluable prediction mismatch occurred.",
             "action": "Preserve all4 negative proposals and all search rejections; do not invent model errors, retune the guards or treat legal execution as improvement."},
            {"id": "KEEP_MEMORY_SNAPSHOT", "evidence": "24/24 nonempty eligible DEMO-only retrievals;17/60 rounds validly cited memory and13/60 contained a parameter-consistent citation/proposal pair; unchanged snapshot.",
             "action": "No memory starvation repair is justified. Keep exact60-record snapshot read-only; record nonconsumption and independent suggestion differences without claiming causal benefit."},
            {"id": "NO_EXTRA_STRUCTURAL_CANDIDATES", "evidence": prior["structural_candidates"],
             "action": "Retain the pre-implementation NOT_ADMITTED decisions; current mode outputs do not authorize additional layered or combined methods."},
            {"id": "PRESERVE_REPAIR_HISTORY", "evidence": "The epoch01 context-binding defect and interrupted attempt costs remain separately archived; current epoch02 was rebuilt and independently reviewed.",
             "action": "Count current21 completed experimental dispatches separately from historical15 attempts. Source changes invalidate affected decision paths; negative method outcomes do not trigger repair."}],
        "next_TaskPlan": [task for task in prior["tasks"] if task["task_id"] in (
            "A02-EVALUATE-SINGLE-PARAMETERS", "A02-EVALUATE-FEASIBLE-ORDERS", "A02-EVALUATE-FOUR-MODES")],
        "readiness_end_condition": "Complete development-mode C and evaluation-freeze C targets still match their actual artifacts, all protocol checks above succeed, and locked choices remain unchanged.",
        "remaining_goal_end_condition": "The planned holdout experiments, independent final Goal2 acceptance, required deliverables and publication are still required; this readiness record completes none of those future tasks.",
        "limits": ["One development episode is not three-episode confirmation", "Stratified24 records are not a population-weighted sample", "70/70 evaluable predictions exclude78 unevaluable proposals; no global AI accuracy claim", "Memory citations/action consistency and changed suggestions are not causal quality evidence", "No hidden provider request count or exact currency cost is observable", "No Human Approval, GPT_SECOND_REVIEW pass, final-method freeze or G3 execution"]}
    for task in result["next_TaskPlan"]:
        task["status"] = "READY_DEPENDENCIES_SATISFIED"
    if digest(analysis_path) != analysis_hash:
        raise ValueError("ANALYSIS_CHANGED_DURING_A_READINESS")
    write_json(output, result, exclusive=True)
    lines = ["# A：开发四模式完成后的评测就绪检查", "",
        "状态：**READY_FOR_FROZEN_G2_EVAL**。这是已授权范围内的治理 A Followup，不是 Human Approval、Goal 2 全验收或最终方法接受。未读取 G2_EVAL 方法结果，未修改合同、选择标准、提示、源码或记忆。", "",
        "此前 A 的开发参数／顺序检查原件保留；本记录仅闭合其 LIVE 开发与独立 C 的依赖。当前冻结文件已生成并经独立 C 核验，后续按固定计划执行。", "",
        f"- 计算代码：`{result['code_sha']}`。",
        f"- 冻结文件 SHA256：`{result['evaluation_freeze']['sha256']}`。",
        f"- 记忆 SHA256：`{memory['snapshot_sha256']}`。", "",
        "| 模式 | 原始记录 × episode | 真实派发 | 唯一候选计算 | 合法并执行提议 | 可评价预测一致 | 保护内增益 / 无增益 |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    for mode in ("llm-only", "search-only", "llm+search", "llm+memory+search"):
        row = next(row for row in tables["mode_summary"] if row["mode"] == mode)
        counts = result["locked_outcomes"][mode]
        lines.append(f"| {mode} | 24 × 1 | {row['experiment_model_dispatches']} | {row['candidate_evaluations']} | {row['raw_legal_proposals']}/{row['valid_raw_proposal_denominator']} | {row['matching_predictions']}/{row['evaluable_prediction_denominator']} | {counts.get('SUPPORTED_WITHIN_SCOPE',0)} / {counts.get('NO_DEMONSTRATED_GAIN',0)} |")
    lines += ["", "search-only 的提议和预测为不适用（0 条分母），不能将表中的 0/0 读成比例。llm-only 只有一次锁定建议；36 次唯一计算包含共同参考，24 次参考评分不向模型反馈，12 条建议与参考重合形成缓存复用。三种搜索模式共同上限为每条20候选；实际使用480、372、330，不将其伪称相同计算量。", "",
        "148 条原始提议全部合法执行，0 回退，0 可评价预测不符。70 条预测可评价且一致；78 条因未承诺、变化近零或覆盖变化不可评价，不能把148都当作准确率分母。1218 个已执行候选包含116个约束拒绝及159个权衡，选择器没有将这些失败隐藏。", "",
        "4 条实际 LLM 提议为 TRADEOFF，全部保留。按固定模式／记录／轮次排序的首例为 memory 模式记录7764的 `7764-r2-a`：模型提议额外距离分段及较松过滤，并明确仍需检验覆盖和保真；实际共同覆盖122/122未变，但基线覆盖集合最大误差从40.214764升至69.145351工作米，触发共同几何保护退化，因此未被最终选中。它自身 DP 最大误差仍为4.826420工作米，正说明自身DP合格不能证明整体几何改善。这是实际负结果，不是非法模型动作或虚构预测错误。原始提议、响应路径、哈希和对比指标见 JSON 的 `actual_negative_model_proposals`。", "",
        "记忆60条（26条范围内支持、34条无已证增益）均经准入。开发检索24/24非空，共72次 query-entry 返回；60个 record-round 共呈现180条记忆。21次有效引用分布于17轮，15个参数一致的 citation-proposal 对分布于13轮，0无效引用，前后快照哈希完全相同。与独立无记忆模式相比，初始建议16/24不同、锁定参数11/24不同；这不是记忆因果增益证明。覆盖充分，无需扩展示范集或改索引。", "",
        "当前21次派发均完成，可见 input_tokens=822007、output_tokens=18869；缓存与 reasoning token 字段单独保留，不能重复相加。历史15次派发（14完成、1人为中断）仅计历史成本，其1次 token 缺失为 unknown，不能混作当前有效实验。底层 provider 请求数与费用不可观察。", "",
        "下一动作保持原计划：120条固定评测记录运行14个预锁代表／单项配置，以及 S-D-P、S-P-D 两个可行顺序；同一24条模式评测记录运行4模式×3独立episode。C-S仍是点数2、长度0，其余参考；C-D和C-P保留参考。两类额外结构候选继续 NOT_ADMITTED，不组合单项。负结果只按既定保护判定登记，不触发评测后调参。", "",
        "全部模式／候选／记忆／冻结回执的目标与源码哈希均已核对。独立 C 覆盖12批完整模式，5,528,516项检查；候选选择及评测冻结亦分别通过。未检查的真实 CRS、真实噪声标签、因果记忆收益、底层请求及最终 Goal 2 验收仍明确保留。", "",
        "可复核入口：`A_EVALUATION_READINESS.json`、`live_development_observations/summary.json`及其带哈希的逐记录／逐提议／逐调用表。此 A 检查只进行读取和确定性汇总，新增模型调用与候选处理均为0。", ""]
    (directory / "A_EVALUATION_READINESS.md").write_text("\n".join(lines), encoding="utf-8")
    print({"status": result["status"], "path": relative(output), "sha256": digest(output),
           "records": len(records), "model_dispatches": len(tables["model_calls"]),
           "negative_actual_model_proposals": len(negative_proposals),
           "elapsed_seconds": result["elapsed_seconds"]})


if __name__ == "__main__":
    main()
