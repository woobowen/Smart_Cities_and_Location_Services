"""Actual governance A: epoch02 development-only diagnosis and next TaskPlan.

This is evidence-generation code, not an experiment decision path. It reads no
G2_EVAL result, changes no candidate or contract, and makes no model requests.
"""
from collections import defaultdict
from pathlib import Path
from time import perf_counter

from task1.scripts.build_goal2_analysis import (
    Inputs, EVIDENCE, parameter_analysis, pareto_analysis, order_analysis,
    memory_analysis, relative,
)
from task1.workflow.io import ROOT, read_json, write_json, digest, now


def main():
    started, timer = now(), perf_counter()
    directory = Path(__file__).resolve().parent
    output = directory / "A_FOLLOWUP_DEVELOPMENT_EPOCH02.json"
    if output.exists():
        raise ValueError("A_FOLLOWUP_ALREADY_EXISTS_PRESERVE_PRIOR_VERSION")
    current = read_json(EVIDENCE / "current_runs.json")
    if any(key.startswith("evaluation_") or key == "mode_evaluation" for key in current):
        raise ValueError("THIS_A_PLANNING_CHECK_MUST_PRECEDE_EVALUATION")
    expected_runs = {"parameter_development": "g2-development-parameters-02",
                     "order_development": "g2-development-orders-02",
                     "memory": "g2-demo-memory-02"}
    if any(current.get(role) != run_id for role, run_id in expected_runs.items()):
        raise ValueError("EXPECTED_EPOCH02_DEVELOPMENT_RUNS_REQUIRED")
    analysis_path = ROOT / "task1/scripts/build_goal2_analysis.py"
    analysis_hash = digest(analysis_path)
    inputs = Inputs(EVIDENCE / "current_runs.json")
    c_receipts = {}
    for role, filename in (
            ("parameter_development", "development_parameters_epoch02_receipt.json"),
            ("order_development", "development_orders_epoch02_receipt.json"),
            ("memory", "memory_epoch02_receipt.json")):
        path = EVIDENCE / "c_contract" / filename
        receipt = read_json(path)
        if (receipt["status"] != "VERIFIED" or receipt["run_id"] != expected_runs[role] or
                receipt["contract_sha256"] != inputs.contract_hash or
                receipt["split_sha256"] != inputs.split_hash or
                receipt["raw_sha256"] != inputs.split["raw_sha256"]):
            raise ValueError("C_DEVELOPMENT_RECEIPT_PARENT_MISMATCH")
        for target in receipt["targets"]:
            if digest(ROOT / target["path"]) != target["sha256"]:
                raise ValueError("C_RECEIPT_TARGET_CHANGED")
        for source, sha256 in receipt["source_hashes"].items():
            if digest(ROOT / source) != sha256:
                raise ValueError("C_REVIEWED_SOURCE_CHANGED")
        c_receipts[role] = {"path": relative(path), "sha256": digest(path),
            "status": receipt["status"], "targets": receipt["targets"],
            "checked_components": receipt["checked_components"],
            "unchecked_components": receipt["unchecked_components"]}
    tables, catalogs = defaultdict(list), {}
    parameter_analysis(inputs, tables, catalogs)
    pareto_analysis(inputs, tables, catalogs)
    order_analysis(inputs, tables)
    memory = memory_analysis(inputs, tables)
    catalog = catalogs["parameter_development"]
    lock_path = EVIDENCE / "candidate_lock.json"
    if not lock_path.is_file():
        write_json(directory / "LOCK_BINDING_PENDING.json", {
            "status": "DEVELOPMENT_EVIDENCE_READ_LOCK_BINDING_PENDING", "at": now(),
            "parameters_read": len(catalog), "orders_read": len(tables["order_configurations"]),
            "analysis_source_sha256": analysis_hash, "evaluation_readiness": "PENDING"})
        raise ValueError("WAIT_FOR_ROOT_CANDIDATE_LOCK_NO_EVALUATION_ALLOWED")
    lock = read_json(lock_path)
    if (lock["parameter_run_id"] != expected_runs["parameter_development"] or
            lock["order_run_id"] != expected_runs["order_development"] or
            lock["source_partition"] != "DEVELOPMENT" or lock["g2_eval_observed_for_selection"]):
        raise ValueError("CANDIDATE_LOCK_NOT_FROM_CURRENT_DEVELOPMENT")
    reference_id = next(cid for cid, row in catalog.items()
                        if row["parameters"] == inputs.contract["reference_parameters"])
    families = {}
    for name in ("C-S", "C-D", "C-P"):
        rows = [row for row in tables["feasible_pareto"] if row["family"] == name]
        gains = [row["config_id"] for row in rows if row["research_status"] == "SUPPORTED_WITHIN_SCOPE"]
        frontier = [row["config_id"] for row in rows if row["on_feasible_frontier"] and row["config_id"] in gains]
        if name == "C-P" and gains:
            selected = min(gains, key=lambda cid: (catalog[cid]["summary"]["n_dp_output"],
                catalog[cid]["summary"]["dp_max_error"] or 0, catalog[cid]["parameters"]["dp"], cid))
        elif name != "C-P" and len(frontier) == 1:
            selected = frontier[0]
        else:
            selected = reference_id
        frozen = lock["selected_single_candidates"][name]
        if (frozen["config_id"] != selected or frozen["parameters"] != catalog[selected]["parameters"] or
                set(frozen["eligible_gain_ids"]) != set(gains) or
                set(frozen["domain_ids"]) != {row["config_id"] for row in rows}):
            raise ValueError("LOCKED_SINGLE_CANDIDATE_DISAGREES_WITH_A_DEVELOPMENT_EVIDENCE:" + name)
        chosen = catalog[selected]
        families[name] = {"config_id": selected, "parameters": frozen["parameters"],
            "domain_size": len(rows), "feasible_config_ids": [row["config_id"] for row in rows if row["feasible_all_records"]],
            "protected_gain_ids": gains, "descriptive_feasible_frontier": [row["config_id"] for row in rows if row["on_feasible_frontier"]],
            "selection_reason": frozen["selection_reason"], "research_status": chosen["research_status"],
            "reference_retained": selected == reference_id, "development_summary": chosen["summary"],
            "strict_gain_records": sum(row["comparison"]["strict_gain"] for row in chosen["records"].values()),
            "records_protected": sum(row["comparison"]["feasible"] for row in chosen["records"].values()),
            "raw_or_true_quality_acceptance": False, "final_method_frozen": False}
    orders = [{key: row[key] for key in ("order", "n_records", "safety_failure_records",
        "raw_break_crossings", "direction_windows_across_raw_breaks", "p_removed_raw_break_trigger_points",
        "research_status", "geometric_guard_failures")} for row in tables["order_configurations"]]
    safe_orders = [row["order"] for row in orders if row["safety_failure_records"] == 0]
    if lock["feasible_orders"] != safe_orders:
        raise ValueError("LOCKED_ORDER_SET_DISAGREES_WITH_ACTUAL_SAFETY_CHECKS")
    c_order = read_json(ROOT / c_receipts["order_development"]["path"])
    if any(c_order["order_safety"][row["order"]]["failing_record_count"] != row["safety_failure_records"] for row in orders):
        raise ValueError("A_ORDER_SAFETY_DISAGREES_WITH_INDEPENDENT_C")
    requested = sorted(set(lock["eval_representatives"]) |
                       {value["config_id"] for value in lock["selected_single_candidates"].values()})
    prior_path = EVIDENCE / "a_followup_development.json"
    result = {"goal_id": inputs.contract["goal_id"], "role": "A", "version": "EPOCH02_PRE_LIVE_READINESS_V1",
        "classification": "ACTUAL_GOVERNANCE_FOLLOWUP_AND_TASKPLAN_NOT_HUMAN_APPROVAL",
        "started_at": started, "ended_at": now(), "elapsed_seconds": perf_counter() - timer,
        "status": "DEVELOPMENT_SELECTION_CHECKED_NEXT_TASKS_DEFINED",
        "evaluation_readiness": "PENDING_LIVE_DEVELOPMENT_AND_INDEPENDENT_C_MODE_REVIEW",
        "evaluation_readiness_reason": "This record verifies deterministic development/DEMO evidence and the candidate lock. It has not consumed completed epoch02 LIVE-mode evidence, actual memory consumption or C's LIVE-mode receipt.",
        "new_model_calls": 0, "new_candidate_processing_runs": 0, "evaluation_method_results_read": False,
        "source_hashes": {relative(analysis_path): analysis_hash, relative(Path(__file__)): digest(Path(__file__))},
        "code_sha": inputs.manifests["parameter_development"][1]["code_head_at_start"],
        "processing_source_tree_sha256": inputs.manifests["parameter_development"][1]["source_tree_sha256"],
        "raw_sha256": inputs.split["raw_sha256"], "contract_sha256": inputs.contract_hash,
        "split_sha256": inputs.split_hash, "source_crs": "UNVERIFIED",
        "supersedes": {"path": relative(prior_path), "sha256": digest(prior_path),
            "reason": "Prior followup remains historical evidence for source epoch01; source-epoch repair required complete epoch02 rebuilding. This is a new diagnosis of the new manifests, not a relabelled old run.",
            "old_original_and_source_archives_preserved": True},
        "independent_C_receipts_consumed": c_receipts,
        "A_verification_scope": "All 59 parameter and six order artifacts: hash/provenance/review target/scope/summary checks; regenerate record-level comparisons and family feasibility/Pareto; verify 60 selected memory admissions. A does not claim a separate raw full-DP rerun; C coverage is reported by its receipts.",
        "input_hashes": inputs.lineage,
        "candidate_lock": {"path": relative(lock_path), "sha256": digest(lock_path), "frozen_at": lock["frozen_at"]},
        "parameter_configurations": len(catalog), "development_records": len(inputs.split["splits"]["DEVELOPMENT"]),
        "candidate_families": families, "order_evidence": orders, "frozen_feasible_orders": safe_orders,
        "memory_snapshot": memory, "structural_candidates": inputs.contract["structural_candidates"],
        "tasks": [
            {"task_id": "A02-CONSUME-DEVELOPMENT-LIVE", "parent_requirements": ["R03", "R04", "R09"],
             "status": "RUNNING_OUTSIDE_THIS_A_CHECK", "question": "Do actual decision paths and memory consumption obey the frozen four-mode protocol?",
             "hypothesis": "The corrected context binding preserves exact historical feedback, and the frozen demonstration memory may or may not be applicable or consumed.",
             "scope": {"partition": "DEVELOPMENT", "record_ids": inputs.split["llm_subsets"]["DEVELOPMENT"], "modes": ["llm-only", "search-only", "llm+search", "llm+memory+search"], "episodes_per_mode": 1},
             "baseline": "Same fixed record reference; compare independent modes only after episode lock.",
             "what_may_change": "Only proposed parameters/actions in registered grids; no protocol, memory or source changes within a run.",
             "budget": "At most8 cards per batch; llm-only1 locked proposal/no feedback; each search mode≤20 unique candidates including reference; model search≤3 decisions; transient faults≤2 retries with actual receipts.",
             "checks": ["exact cards and same24 IDs", "actual provider prompts/responses/receipt hashes", "search-only zero model sentinel", "context snapshots cannot mutate with later proposal lists", "own candidate feedback only", "raw legality before execution and no hidden clamp", "delivered/cited/parameter-consistent memory use separately", "snapshot hash unchanged and no own/cross-episode leakage", "actual counters and missing provider usage"],
             "allowed_followup": "Consume real negative/no-memory-use results without inventing benefit. Reproducible engineering defects go through repair/regression/invalidation/rebuild. Only protocol-permitted DEMO index fixes before EVAL may be considered; no EVAL feedback is available.",
             "end_condition": "All4×24 development record episodes complete with valid episode evidence and an independent C LIVE-mode receipt. Then A records actual memory/use/legality/feedback findings in a separate readiness record."},
            {"task_id": "A02-FREEZE-EVALUATION", "parent_requirements": ["R03", "R04", "R05", "R09"],
             "status": "PENDING_DEPENDENCIES", "depends_on": ["A02-CONSUME-DEVELOPMENT-LIVE"],
             "question": "Are protocol, candidates, memory and evaluators fixed before holdout results?",
             "hypothesis": "The current validated epoch can support one common holdout comparison with no post-holdout selection.",
             "scope": "Freeze metadata only; no G2_EVAL processing before the freeze.",
             "action": ".venv/bin/python -m task1.scripts.goal2 freeze-evaluation",
             "guards": ["bind this candidate_lock hash", "same verified memory snapshot", "same prompt/model/provider/source tree", "fixed metrics and conservative selection", "exact split IDs and24 LLM IDs", "no unresolved blocking issues"],
             "budget": "One deterministic freeze operation; no model call.",
             "end_condition": "evaluation_freeze.json is LOCKED_BEFORE_G2_EVAL with all actual hashes, after completed LIVE-mode review. This A planning record alone is not readiness or Human Approval."},
            {"task_id": "A02-EVALUATE-SINGLE-PARAMETERS", "parent_requirements": ["R01", "R05", "R06"],
             "status": "PENDING_FREEZE", "depends_on": ["A02-FREEZE-EVALUATION"],
             "question": "Do the locked single candidates retain their registered protections on common holdout records?",
             "hypothesis": "C-S may add original-point coverage without losing baseline coverage/geometric protection; C-D/P retain the reference because development did not establish protected gain.",
             "baseline": inputs.contract["reference_parameters"], "what_changes": "C-S only segmentation/filter parameter group; C-D direction only; C-P tolerance only. No candidate combination.",
             "scope": {"partition": "G2_EVAL", "record_ids": inputs.split["splits"]["G2_EVAL"], "configuration_ids": requested},
             "command_template": ".venv/bin/python -m task1.scripts.goal2 evaluation-parameters --run-id <new-evaluation-parameters-run>",
             "budget": {"unique_configurations": len(requested), "record_candidate_evaluations": len(requested) * len(inputs.split["splits"]["G2_EVAL"]), "new_model_calls": 0},
             "metrics_and_guards": ["complete input/terminal point ledger", "raw-window breakpoint crossing=0", "baseline covered original-index set retained", "record/window coverage protected", "S/D common geometry on baseline-covered mask", "P complete immediate reference and5-work-metre common budget", "null+reason with original denominators"],
             "allowed_followup": "Report SUPPORTED/NO_GAIN/TRADEOFF/REJECTED/INSUFFICIENT by the existing rule. Negative results do not trigger retuning. Reference reuse for C-D/P remains shared evidence, not independent extra runs.",
             "end_condition": "All fixed representative and locked single-candidate entries cover120 records, independent audit succeeds, and per-record/stratum tradeoffs plus KEEP/REJECT/TRADEOFF/INSUFFICIENT reasons are registered."},
            {"task_id": "A02-EVALUATE-FEASIBLE-ORDERS", "parent_requirements": ["R02", "R06"],
             "status": "PENDING_FREEZE", "depends_on": ["A02-FREEZE-EVALUATION"],
             "question": "How does the already safe S-P-D order trade geometry against S-D-P on common holdout records?",
             "hypothesis": "Safety in development does not imply equal neighbourhoods or no geometric degradation.",
             "baseline": "S-D-P", "what_changes": "Only the registered S/D/P order; no hidden pre-segmentation or added repair.",
             "scope": {"partition": "G2_EVAL", "record_ids": inputs.split["splits"]["G2_EVAL"], "orders": safe_orders},
             "command_template": ".venv/bin/python -m task1.scripts.goal2 evaluation-orders --run-id <new-evaluation-orders-run>",
             "budget": {"record_order_evaluations": len(safe_orders) * len(inputs.split["splits"]["G2_EVAL"]), "new_model_calls": 0},
             "metrics_and_guards": ["actual-stage recomputation", "immediate P denominator separate from later deletion", "original breakpoint crossings and removed triggers", "baseline covered identities", "D neighbourhood changes", "same common-reference geometric comparisons"],
             "allowed_followup": "Keep the four rejected development orders and their full failure evidence; do not expand or repair them merely to pass.",
             "end_condition": "Both frozen safe orders have120-record holdout outputs, actual protection verdicts and independent audit; any new failure remains visible without reselecting order."},
            {"task_id": "A02-EVALUATE-FOUR-MODES", "parent_requirements": ["R03", "R04", "R06", "R07"],
             "status": "PENDING_FREEZE", "depends_on": ["A02-FREEZE-EVALUATION"],
             "question": "How do the four actual decision structures compare under their registered budgets and frozen memory?",
             "hypothesis": "Memory/proposals may change actions, but changed suggestions, citations or extra calls do not establish quality benefit.",
             "baseline": "Per-record reference plus matched search-only finite-budget comparator; no global-optimum claim.",
             "what_changes": "Only LLM/search/memory availability, with the registered shared tool/model/batch/domain/selection conditions.",
             "scope": {"partition": "G2_EVAL", "record_ids": inputs.split["llm_subsets"]["G2_EVAL"], "modes": ["llm-only", "search-only", "llm+search", "llm+memory+search"], "independent_episodes_per_mode": 3},
             "command_template": ".venv/bin/python -m task1.scripts.goal2 evaluation-modes --run-id <new-evaluation-modes-run> --enable-live",
             "budget": {"record_episode_observations": 4 * 24 * 3, "search_mode_candidates_per_record_episode": 20, "LLM_search_decisions_per_episode": 3, "LLM_only_proposals_per_record_episode": 1, "maximum_cards_per_batch": 8, "maximum_successful_batch_decision_calls_before_transient_retries": 63},
             "metrics_and_guards": ["raw legal/executed/rejected proposal counts", "pre-execution metric/reference/sign predictions", "actual own-feedback decisions", "candidate/reference/fallback separately", "record-paired differences and three-episode distributions", "frozen memory delivered/cited/action-consistent counts and no writes", "zero experimental LLM calls for search-only", "actual visible tokens/time/request provenance with unknown underlying counts"],
             "allowed_followup": "No evaluation-driven tuning, DEMO expansion or cross-episode learning. Engineering repair invalidates affected outputs and downstream proposals, with fresh LIVE rebuilding where feedback changed.",
             "end_condition": "All288 record-episode observations are complete and independently audited, or an actual external blocker is recorded with unaffected work complete. No mocked/replayed responses count as new LIVE."}],
        "limits": ["conditional working-plane geometry, source datum remains unverified", "coverage/compression are not true cleaning accuracy", "no final method or combination selected", "no G3_RESERVED method results consumed", "no new Human Approval or external GPT acceptance asserted"]}
    if digest(analysis_path) != analysis_hash:
        raise ValueError("ANALYSIS_GENERATOR_CHANGED_DURING_A_CHECK")
    write_json(output, result, exclusive=True)
    lines = ["# A：epoch02 开发证据与后续执行", "", "这是一份真实治理 A 的 Followup/TaskPlan，不是 Human Approval。旧版本及原始源码继续保留。", "",
        "参数与顺序的选择检查已完成；**EVAL readiness=PENDING_LIVE_DEVELOPMENT_AND_INDEPENDENT_C_MODE_REVIEW**。"
        "本记录未消费已完成的 epoch02 LIVE 开发证据和模式 C 回执，不能据此提前开启评测。", "",
        f"代码 {result['code_sha']}；合同 {result['contract_sha256']}；candidate_lock {result['candidate_lock']['sha256']}。", "",
        "| 单项 | 锁定参数 | 开发判定 | 保护通过/记录 | 严格增益记录 |", "|---|---|---|---:|---:|"]
    for name, row in families.items():
        lines.append(f"| {name} | {row['parameters']} | {row['research_status']} | {row['records_protected']}/120 | {row['strict_gain_records']} |")
    lines.extend(["", "C-D/C-P 保留参考是按规则回退，不表示最优，也不省略其留出登记。C-S 的增益只指共同参考覆盖/几何条件，"
        "新覆盖区域误差单列，不能称为真实噪声清洗质量提升。", "", "S-D-P 和 S-P-D 进入冻结的阶段顺序评测。"
        "S-P-D 虽通过安全条件，仍有几何保护权衡；其余四种顺序保留实际约束失败，不加隐藏分段修复。", ""])
    for row in inputs.contract["structural_candidates"]:
        lines.append(f"- {row['id']}：{row['status']}。{row['reason']}")
    lines.extend(["", "后续步骤、问题/假设、数据范围、预算、保护项、允许修复与结束条件见同目录 JSON 的 tasks。"
        f"正式参数评测计划 {len(requested)} 个唯一配置×120 记录；顺序 {len(safe_orders)}×120；模式 4×24×3。"
        "这些是计划预算，尚不是已执行评测。完成 LIVE 开发与独立 C 模式检查后，A 需另写实际 readiness，随后才能冻结并开启 G2_EVAL。", "",
        "旧 A 记录：[epoch01 followup](../a_followup_development.json)；其被本版本替代的原因是代码版本修复后的全量重建，"
        "不倒写历史，不将旧 LIVE 重标为新 LIVE。", ""])
    (directory / "A_FOLLOWUP_DEVELOPMENT_EPOCH02.md").write_text("\n".join(lines), encoding="utf-8")
    print({"status": result["status"], "evaluation_readiness": result["evaluation_readiness"],
           "candidate_lock_sha256": result["candidate_lock"]["sha256"], "planned_evaluation_unique_configs": len(requested),
           "candidate_choices": {name: value["parameters"] for name, value in families.items()},
           "output": relative(output), "elapsed_seconds": result["elapsed_seconds"]})


if __name__ == "__main__":
    main()
