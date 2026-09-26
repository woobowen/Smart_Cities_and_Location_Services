"""Confirm fixed single candidates from completed holdout traces, without tuning.

The existing parameter_analysis/candidate_analysis functions own all comparison
and recommendation definitions. This wrapper binds the specific A handoff,
exports complete record/stratum denominators, and applies frozen case rules.
It never loads the concurrently running LIVE mode run or dispatches processing.
"""
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from time import perf_counter

from task1.scripts.build_goal2_analysis import (
    EVIDENCE, Inputs, candidate_analysis, compact_metrics, parameter_analysis,
    pair_reading, relative, summarize, write_tables,
)
from task1.workflow.io import ROOT, digest, now, object_hash, read_json, write_json
from task1.workflow.g2_selection import REFERENCE, config_id


def binding(path):
    return {"path": relative(path), "sha256": digest(path)}


def neighbors(record):
    stage = next(row for row in record["stages"] if row["name"] == "D")
    changes = []
    for before, after in zip(stage["input"], stage["output"]):
        original_pairs = set(zip(before["indices"], before["indices"][1:]))
        for left, right in zip(after["indices"], after["indices"][1:]):
            if (left, right) not in original_pairs:
                changes.append({"from_index": left, "to_index": right,
                    "removed_between": [index for index in before["indices"] if left < index < right],
                    "segment_id": after["segment_id"]})
    return changes


def cases_for_candidate(name, selected, baseline, catalog, cards, trace_binding):
    rows = []
    def add(kind, rid, reason=None, details=None):
        result = {"candidate": name, "case_kind": kind, "record_id": rid,
            "status": "AVAILABLE" if rid is not None else "NO_AVAILABLE_CASE",
            "unavailable_reason": reason, "selection_details": details,
            "source": trace_binding, "true_quality_claim": False}
        if rid is not None:
            after, before = selected[rid], baseline[rid]
            result.update({"stratum": cards[rid]["stratum"],
                "reference_metrics": compact_metrics(before["metrics"]),
                "candidate_metrics": compact_metrics(after["metrics"]),
                "comparison": catalog[rid]["comparison"],
                "reference_record_trace_hash": object_hash(before),
                "candidate_record_trace_hash": object_hash(after)})
        rows.append(result)
    layers = defaultdict(list)
    for rid in selected:
        layers[cards[rid]["stratum"].split("_")[0]].append(rid)
    for layer, ids in sorted(layers.items()):
        center = median(cards[rid]["span_work_m"] for rid in ids)
        rid = min(ids, key=lambda rid: (abs(cards[rid]["span_work_m"] - center), rid))
        add("representative_" + layer, rid, details={"layer_records": len(ids),
            "raw_span_median_work_m": center, "selected_raw_span_work_m": cards[rid]["span_work_m"]})
    loss = [(baseline[rid]["metrics"]["common_covered_points"] - record["metrics"]["common_covered_points"], rid)
            for rid, record in selected.items()]
    positive_loss = [row for row in loss if row[0] > 0]
    if positive_loss:
        count, rid = min(positive_loss, key=lambda row: (-row[0], row[1]))
        add("worst_coverage", rid, details={"covered_point_loss": count})
    else:
        add("worst_coverage", None, "NO_OBSERVED_COVERAGE_LOSS", {"largest_loss": max(row[0] for row in loss)})
    comparable = [(row["comparison"]["candidate_max_on_baseline_covered"], rid)
                  for rid, row in catalog.items() if row["comparison"]["candidate_max_on_baseline_covered"] is not None]
    if comparable:
        value, rid = min(comparable, key=lambda row: (-row[0], row[1]))
        add("worst_comparable_common_error", rid, details={"candidate_error_on_baseline_mask_work_m": value,
            "guard_failed": not catalog[rid]["comparison"]["feasible"]})
    else:
        add("worst_comparable_common_error", None, "NO_NONEMPTY_BASELINE_COVERAGE_REFERENCE")
    boundary = []
    direction = []
    for rid, record in selected.items():
        stage = next(row for row in record["stages"] if row["name"] == "P")
        for operation in stage["operations"]:
            check = operation["runtime_dp_check"]
            assert check["status"] == "VERIFIED"
            for point in check["error_by_original_index"]:
                gap = abs(point["error"] - operation["tolerance"])
                if point["error"] > 0 and gap > 0:
                    boundary.append((gap, rid, point["index"], operation["input_segment_id"], {
                        "actual_residual_work_m": point["error"], "tolerance_work_m": operation["tolerance"],
                        "absolute_gap_work_m": gap, "floating_allowance": check["floating_allowance"],
                        "dp_input_hash": operation["dp_reference_hash"], "dp_output_hash": operation["dp_output_hash"]}))
        for change in neighbors(record):
            direction.append((rid, change["from_index"], change["to_index"], change))
    if boundary:
        gap, rid, index, segment, detail = min(boundary, key=lambda row: row[:4])
        add("near_DP_boundary", rid, details={"original_index": index, "segment_id": segment, **detail})
    else:
        add("near_DP_boundary", None, "NO_NONZERO_DP_RESIDUAL_WITH_POSITIVE_THRESHOLD_GAP")
    if direction:
        rid, _, _, change = min(direction, key=lambda row: row[:3])
        add("actual_D_neighborhood_change", rid, details={**change,
            "reference_has_same_stage_change": change in neighbors(baseline[rid]),
            "meaning": "Within-pipeline D removal changes adjacency; not automatically a candidate-versus-reference change."})
    else:
        add("actual_D_neighborhood_change", None, "NO_ACTUAL_D_OUTPUT_NEW_ADJACENCY")
    for kind, eligible, reason in (
            ("first_protection_failure", [rid for rid, row in catalog.items() if not row["comparison"]["feasible"]], "NO_FROZEN_PROTECTION_FAILURE"),
            ("first_strict_gain", [rid for rid, row in catalog.items() if row["comparison"]["strict_gain"]], "NO_STRICT_REGISTERED_GAIN"),
            ("first_unavailable_error", [rid for rid in selected if any(record["metrics"][metric] is None
                for record in (selected[rid], baseline[rid]) for metric in ("common_max_error", "dp_max_error"))], "NO_UNAVAILABLE_COMMON_OR_DP_ERROR")):
        add(kind, min(eligible) if eligible else None, None if eligible else reason)
    return rows


def main():
    started, timer = now(), perf_counter()
    directory = Path(__file__).resolve().parent
    output = directory / "single_candidate_confirmation.json"
    if output.exists():
        raise ValueError("CONFIRMATION_EXISTS_PRESERVE_ORIGINAL")
    snapshot = EVIDENCE / "a_epoch02_single_confirmation_registry_snapshot.json"
    scope = read_json(snapshot)
    if set(scope) != {"parameter_development", "order_development", "evaluation_parameters", "evaluation_orders"}:
        raise ValueError("SINGLE_CONFIRMATION_SCOPE_MUST_EXCLUDE_ALL_LIVE_MODES")
    inputs = Inputs(snapshot)
    assert inputs.freeze["evaluation_previously_observed"] is False
    analysis = ROOT / "task1/scripts/build_goal2_analysis.py"
    analysis_hash = digest(analysis)
    contract_path = ROOT / "task1/config/goal2/contract.json"
    rules_path = directory / "case_selection_rules.json"
    rules = read_json(rules_path)
    assert rules["contract_sha256"] == inputs.contract_hash
    assert rules["original_frozen_case_rules"] == inputs.contract["case_selection"]
    receipts = {}
    for name in ("evaluation_parameters_bound_receipt.json", "evaluation_orders_bound_receipt.json",
                 "candidate_lock_epoch02_receipt.json", "evaluation_freeze_epoch02_receipt.json"):
        path = EVIDENCE / "c_contract" / name
        receipt = read_json(path)
        assert receipt["status"] == "VERIFIED" and not receipt["errors"]
        for target in receipt["targets"]:
            assert digest(ROOT / target["path"]) == target["sha256"]
        for source, sha256 in receipt["source_hashes"].items():
            assert digest(ROOT / source) == sha256
        assert digest(ROOT / receipt["audit_program"]["path"]) == receipt["audit_program"]["sha256"]
        receipts[name] = {**binding(path), "status": receipt["status"], "targets": receipt["targets"],
            "checked_components": receipt["checked_components"], "unchecked_components": receipt["unchecked_components"]}
    tables, catalogs = defaultdict(list), {}
    parameter_analysis(inputs, tables, catalogs)
    candidate_analysis(inputs, tables, catalogs)
    evaluation_dir, manifest = inputs.manifests["evaluation_parameters"]
    entries = {row["config_id"]: row for row in manifest["artifacts"].values()}
    locked = inputs.lock["selected_single_candidates"]
    reference_id = config_id(REFERENCE)
    selected_ids = {row["config_id"] for row in locked.values()} | {reference_id}
    actual = {cid: {row["record_id"]: row for row in inputs.load_batch("evaluation_parameters", entries[cid])["records"]}
              for cid in sorted(selected_ids)}
    baseline = actual[reference_id]
    ids = inputs.split["splits"]["G2_EVAL"]
    assert len(ids) == 120 and all(list(rows) == ids for rows in actual.values())
    raw_points = sum(row["metrics"]["n_input"] for row in baseline.values())
    case_rows, calculations, summaries = [], [], []
    for candidate in ("C-S", "C-D", "C-P"):
        cid = locked[candidate]["config_id"]
        entry = entries[cid]
        shared = [name for name, item in locked.items() if item["config_id"] == cid]
        if cid == reference_id:
            shared.append("COMMON_REFERENCE")
        trace_binding = {"run_id": manifest["run_id"], "experiment_key": entry["experiment_key"],
            "config_id": cid, "batch": binding(evaluation_dir / entry["file"]),
            "batch_review": binding(evaluation_dir / entry["review_file"]),
            "shared_evidence_for": shared, "count_as_new_independent_calculation": False}
        calculations.append({"candidate": candidate, **trace_binding,
            "actual_existing_batch_elapsed_seconds": entry["elapsed_seconds"],
            "records": len(ids), "raw_points": raw_points})
        catalog = catalogs["evaluation_parameters"][cid]["records"]
        outcome = next(row for row in tables["candidate_evaluation"] if row["candidate"] == candidate)
        summaries.append({**outcome, "computation": trace_binding,
            "development_source": catalogs["parameter_development"][cid]["context"],
            "development_selection_locked_before_evaluation": True,
            "evaluation_used_for_reselection": False,
            "interpretation": ("Operational reference retained; C-D/C-P and reference share this exact batch, not independent confirmation replicates. No new-method superiority demonstrated."
                if cid == reference_id else "Apply frozen single-candidate protections only; any support is conditional geometry/coverage, not real cleaning accuracy or final adoption.")})
        selected = actual[cid]
        assert sum(row["metrics"]["n_input"] for row in selected.values()) == raw_points
        strata = defaultdict(list)
        for rid, record in selected.items():
            pair = pair_reading(record, baseline[rid])
            assert pair == catalog[rid]["comparison"]
            pairs = [row for row in tables["candidate_record_pairs"] if row["candidate"] == candidate and row["record_id"] == rid]
            assert len(pairs) == 1
            pairs[0].update({"raw_point_denominator": record["metrics"]["n_input"],
                "reference_record_trace_hash": object_hash(baseline[rid]),
                "candidate_record_trace_hash": object_hash(record), "shared_experiment_key": entry["experiment_key"]})
            strata[inputs.cards[rid]["stratum"]].append(rid)
            for arm, item in (("reference", baseline[rid]), ("candidate", record)):
                metrics = item["metrics"]
                tables["candidate_record_metrics"].append({"candidate": candidate, "config_id": cid,
                    "record_id": rid, "stratum": inputs.cards[rid]["stratum"], "arm": arm,
                    "experiment_key": entries[reference_id]["experiment_key"] if arm == "reference" else entry["experiment_key"],
                    **compact_metrics(metrics)})
                for metric, reason, denominator in (
                        ("dp_saving", "dp_saving_reason", "n_dp_input"),
                        ("dp_max_error", "dp_error_reason", "dp_error_denominator"),
                        ("common_max_error", "common_error_reason", "common_error_denominator"),
                        ("common_coverage", "common_coverage_reason", "common_raw_points"),
                        ("final_length", "final_length_reason", "n_final"),
                        ("raw_length", "raw_length_reason", "n_input")):
                    if metrics[metric] is None:
                        tables["candidate_unavailable_metrics"].append({"candidate": candidate, "record_id": rid,
                            "arm": arm, "metric": metric, "value": None, "reason": metrics[reason],
                            "metric_denominator": metrics[denominator], "raw_point_denominator": metrics["n_input"],
                            "original_record_denominator": 120})
        for stratum, records in sorted(strata.items()):
            for arm, source in (("reference", baseline), ("candidate", selected)):
                tables["candidate_stratum_metrics"].append({"candidate": candidate, "stratum": stratum,
                    "arm": arm, **summarize([source[rid] for rid in records]),
                    "statistical_unit": "original_record", "population_weighted": False})
        case_rows.extend(cases_for_candidate(candidate, selected, baseline, catalog, inputs.cards, trace_binding))
    export_names = ("candidate_development", "candidate_evaluation", "candidate_record_pairs",
                    "candidate_by_stratum", "candidate_record_metrics", "candidate_stratum_metrics",
                    "candidate_unavailable_metrics")
    exported_tables = {name: tables[name] for name in export_names}
    exported_tables["candidate_case_selection"] = case_rows
    exported_tables["candidate_shared_calculations"] = calculations
    table_registry = write_tables(directory, exported_tables)
    prior_A = EVIDENCE / "a_epoch02/A_FOLLOWUP_DEVELOPMENT_EPOCH02.json"
    result = {"goal_id": inputs.contract["goal_id"], "classification": "LOCKED_SINGLE_CANDIDATE_HELDOUT_CONFIRMATION",
        "status": "REVIEW_PENDING", "derivation_status": "ACTUAL_A_BINDING_AND_COMPARISON_CHECKS_VERIFIED",
        "independent_candidate_confirmation_review": "PENDING",
        "started_at": started, "ended_at": now(), "elapsed_seconds": perf_counter() - timer,
        "actual_command": ".venv/bin/python -m task1.evidence.goal2.a_epoch02.heldout_single_confirmation.build_confirmation",
        "source": binding(Path(__file__)), "analysis_source": binding(analysis),
        "comparison_definition_source": binding(ROOT / "task1/workflow/g2_selection.py"),
        "candidate_lock": binding(EVIDENCE / "candidate_lock.json"),
        "evaluation_freeze": binding(EVIDENCE / "evaluation_freeze.json"),
        "development_A_selection_evidence": binding(prior_A), "read_scope_registry": binding(snapshot),
        "independent_input_reviews": receipts, "case_rules": binding(rules_path),
        "code_sha": manifest["code_head_at_start"], "source_tree_sha256": manifest["source_tree_sha256"],
        "raw_sha256": inputs.split["raw_sha256"], "contract_sha256": inputs.contract_hash,
        "split_sha256": inputs.split_hash, "source_crs": "UNVERIFIED", "unit": "working_metre",
        "input_scope": {"partition": "G2_EVAL", "record_ids": ids, "records": len(ids),
            "raw_points": raw_points, "parent_group_unit": "original_record", "population_weighted": False},
        "reference_parameters": REFERENCE, "reference_summary": catalogs["evaluation_parameters"][reference_id]["summary"],
        "candidate_results": summaries, "candidate_cases": case_rows,
        "shared_calculation_statement": "C-D and C-P retain reference parameters and use exactly the common reference batch file, hash, experiment key and120 records; three named families are not three independently new computations.",
        "resources": {"parameter_run_id": manifest["run_id"], "all_fixed_parameter_configs": len(entries),
            "parameter_run_candidate_evaluations": manifest["candidate_evaluations"],
            "parameter_run_registered_new_processing_verifier_calls": manifest["deterministic_tool_calls"],
            "parameter_run_cache_hit_verifier_calls": manifest["cache_reads"],
            "parameter_run_model_dispatches": manifest["experiment_model_dispatches"],
            "single_confirmation_unique_existing_configs_including_reference": len(selected_ids),
            "single_confirmation_unique_existing_record_configurations": len(selected_ids) * len(ids),
            "named_family_record_comparisons": 3 * len(ids),
            "each_existing_config_binding_and_elapsed": calculations,
            "analysis_elapsed_seconds": perf_counter() - timer,
            "analysis_new_candidate_processing_calls": 0, "analysis_new_model_dispatches": 0,
            "unit_limit": "Actual registered processing/verifier dispatches and existing batch elapsed time; not all Python helpers, no fabricated allocation of shared evidence costs."},
        "nulls": {"representation": "null with reason and original denominator; no fill-zero or record exclusion",
            "unavailable_reading_rows": len(tables["candidate_unavailable_metrics"]),
            "same_output_counts_do_not_prove_same_true_quality": True},
        "tables": table_registry, "input_hashes": inputs.lineage,
        "checks": {"three_locked_candidates": True, "each_contains_exact120_original_records": True,
            "each_preserves_complete_raw_denominator": True, "existing_candidate_analysis_and_compare_reused": True,
            "C_D_C_P_and_reference_share_one_artifact": locked["C-D"]["config_id"] == locked["C-P"]["config_id"] == reference_id,
            "case_choice_follows_registered_rules": True, "no_new_config_or_reselection": True,
            "no_mode_run_or_prompt_read_or_modified": True},
        "limits": ["Conditional working geometry and coverage only; source CRS unverified and real noise truth unavailable", "Prior development choices remain unchanged even if holdout effect is negative", "KEEP for retained reference is operational fallback, not new gain or proven optimality", "No candidate combination, final adoption, whole-data cleaning or G3 work", "Full stage analysis and Goal2 final acceptance remain outstanding"]}
    assert digest(analysis) == analysis_hash and digest(contract_path) == inputs.contract_hash
    assert len(tables["candidate_record_pairs"]) == 360
    assert all(sum(row["n_records"] for row in tables["candidate_by_stratum"] if row["candidate"] == candidate) == 120
               for candidate in ("C-S", "C-D", "C-P"))
    write_json(output, result, exclusive=True)
    lines = ["# 固定单项候选的留出确认", "",
        "本记录只对已冻结候选应用已有比较规则。输入参数和顺序产物已经独立 C 验证；本派生确认等待独立 candidates 回执。没有新候选处理或模型调用，未接触并行 LIVE 模式。", "",
        f"G2_EVAL 保持原120条记录、{raw_points}原始点；source_crs=UNVERIFIED，所有距离均为工作米。记录分组、原始分母与空值保留，分层结果不解释成总体均值。", "",
        "| 单项 | 固定配置 | 留出判定 | 建议 | 保护通过/记录 | 严格增益记录 | 共同覆盖点 | 最终点数 | 最终无输出记录 |",
        "|---|---|---|---|---:|---:|---:|---:|---:|"]
    for row in summaries:
        lines.append(f"| {row['candidate']} | {row['config_id']} | {row['evaluation_status']} | {row['recommendation']} | "
            f"{row['feasible_records']}/120 | {row['strict_gain_records']} | {row['common_covered_points']}/{raw_points} | {row['n_final']} | {row['n_no_output_records']} |")
    lines += ["", "C-S仅改变分段/过滤参数组；C-D方向35和C-P容差5均保留参考。C-D、C-P和共同参考是同一个既有batch/hash/experiment key，不能把共享读数称为三个独立新实验。KEEP参考不代表新收益或参考最优。", "",
        "已有参数评测共14个唯一配置、1680个记录配置计算；本确认涉及含参考的2个唯一配置、240个既有记录配置，输出360条按候选标签展开的配对行。展开不会增加实际实验次数。", "",
        "逐记录表包含相同共同覆盖与相同DP输入的可比性、保护失败、各差值及不可用原因；分层表给原始记录分母、pooled点数和明确分母。DP省点率只针对本次完整DP输入，不能跨不同上游直接称整体改善。", "",
        "案例依据原冻结规则：各原始跨度层中位数代表、实际覆盖损失、共同参考最差误差、DP近边界、方向邻接变化；缺类明确标无可用，不用其他记录替代。案例及原始索引、batch和record trace哈希见 JSON 与 candidate_case_selection.csv。", "",
        "这些是阶段单项证据。是否组合、如何处理权衡及最终采用留给 Goal 3 与用户／网页 GPT；本记录不冻结最终方法、不宣称真实噪声准确率、全量清洗或最终报告完成。", ""]
    (directory / "SINGLE_CANDIDATE_CONFIRMATION.md").write_text("\n".join(lines), encoding="utf-8")
    print({"status": result["status"], "path": relative(output), "sha256": digest(output),
        "raw_points": raw_points, "candidates": [{key: row[key] for key in (
            "candidate", "evaluation_status", "recommendation", "feasible_records", "strict_gain_records",
            "common_covered_points", "n_final", "n_no_output_records")} for row in summaries],
        "elapsed_seconds": result["elapsed_seconds"]})


if __name__ == "__main__":
    main()
