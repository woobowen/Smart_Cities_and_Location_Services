"""C-only verification of actual development quotations and counterexample links."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS
from review_development_runs import Audit, read_compressed
from review_live_modes_epoch02 import assessment, prediction, compact, legality

OUT = Path(__file__).resolve().parent
EV = ROOT / "task1/evidence/goal2"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def main():
    started = time.perf_counter()
    audit = Audit()
    directory = EV / "a_epoch02/actual_ai_critique"
    archive = EV / "a_epoch02/actual_ai_critique_v1"
    artifact = read_json(directory / "actual_ai_critique.json")
    old = read_json(archive / "actual_ai_critique.json")
    markdown = (directory / "ACTUAL_AI_CRITIQUE.md").read_text()
    old_markdown = (archive / "ACTUAL_AI_CRITIQUE.md").read_text()
    state = read_json(EV / "goal_state.json")
    issue = state["issues"]["G2-C-AI-NULL-001"]
    for entry in issue["repair_evidence"]:
        audit.check("repair_target_hash", digest(ROOT / entry["path"]) == entry["sha256"])
    for path, sha in issue["repair_source_hashes"].items():
        audit.check("repair_source_epoch", digest(ROOT / path) == sha)
    for key in ("generator", "analysis_source", "read_scope_registry"):
        entry = artifact[key]
        audit.check("AI_binding:" + key, digest(ROOT / entry["path"]) == entry["sha256"])
    registry = read_json(ROOT / artifact["read_scope_registry"]["path"])
    audit.check("read_scope_excludes_evaluation", not any("evaluation" in key or "G2_EVAL" in str(v) for key, v in registry.items()))
    audit.check("no_new_experiments", artifact["new_model_calls"] == artifact["new_candidate_processing_runs"] == artifact["new_counterexample_runs"] == 0)
    audit.check("conditional_no_human_claim", artifact["source_crs"] == "UNVERIFIED" and artifact["frozen_sources_or_selection_changed"] is False)
    for receipt_binding in artifact["independent_input_reviews"].values():
        receipt_path = ROOT / receipt_binding["path"]
        audit.check("independent_review_hash", digest(receipt_path) == receipt_binding["sha256"])
        receipt = read_json(receipt_path)
        audit.check("independent_review_status", receipt["status"] == "VERIFIED" and receipt["errors"] == [])
        for target in receipt["targets"]:
            audit.check("independent_review_target_still_current", digest(ROOT / target["path"]) == target["sha256"])
    for path in task_sources("counterexamples"):
        sha = digest(ROOT / path)
        audit.check("current_counterexample_source", state["tasks"]["counterexamples"]["source_hashes"].get(path) == sha)
    run = EV / "runs" / registry["mode_development"]
    manifest = read_json(run / "manifest.json")
    grids = read_json(ROOT / "task1/config/goal2/contract.json")["parameter_grids"]
    proposals, lookup = [], {}
    cases, calls = 0, 0
    for entry in manifest["mode_episodes"]:
        ep_path = run / entry["path"]
        audit.check("registered_episode_hash", digest(ep_path) == entry["sha256"])
        episode = read_json(ep_path)
        calls += episode["resources"]["experiment_model_dispatches"]
        for record in episode["records"]:
            cases += 1
            trace_path = ep_path.parent / (record["record_id"] + "_candidate_traces.json.gz")
            audit.check("registered_trace_hash", digest(trace_path) == episode["artifact_hashes"][trace_path.name])
            traces = read_compressed(trace_path)["results"]
            reference = traces[record["reference_config_id"]]
            for number, proposal in enumerate(record["proposal_records"]):
                if proposal.get("original") is None:
                    continue
                original = proposal["original"]
                valid, _ = legality(original["parameters"], grids)
                audit.check("raw_legal_not_clamped", valid == proposal["legal"])
                candidate = traces[proposal["executed_config_id"]]
                expected_prediction = prediction(original, candidate, reference)
                audit.same("independent_prediction", proposal["prediction"], expected_prediction)
                pair = assessment(candidate, reference)
                key = (record["partition"], record["mode"], record["episode"], record["record_id"], proposal["round"], number)
                row = {"key": key, "record": record, "proposal": proposal, "candidate": candidate,
                       "reference": reference, "prediction": expected_prediction, "comparison": pair,
                       "episode_path": ep_path, "trace_path": trace_path}
                proposals.append(row)
                lookup[(record["episode_id"], record["record_id"], proposal["round"], original["candidate_id"])] = row
    proposals.sort(key=lambda r: r["key"])
    tradeoffs = [r for r in proposals if r["comparison"]["status"] == "TRADEOFF"]
    evaluable = [r for r in proposals if r["prediction"]["evaluable"]]
    unevaluable = [r for r in proposals if not r["prediction"]["evaluable"]]
    correct = [r for r in evaluable if r["prediction"].get("prediction_matches") is True]
    expected_examples = tradeoffs + correct[:1] + unevaluable[:1]
    audit.check("complete_development_categories", (cases, calls, len(proposals), len(tradeoffs), len(evaluable), len(correct), len(unevaluable)) == (96, 21, 148, 4, 70, 70, 78))
    audit.check("six_citations", len(artifact["actual_ai_citations"]) == len(expected_examples) == 6)
    scope_counts = artifact["actual_scope"]
    audit.check("reported_scope_denominators", scope_counts["record_episode_observations"] == cases and scope_counts["visible_experiment_model_dispatches"] == calls
                and scope_counts["preserved_original_proposals"] == len(proposals) and scope_counts["evaluable_prediction_denominator"] == len(evaluable))
    for item, expected, prior in zip(artifact["actual_ai_citations"], expected_examples, old["actual_ai_citations"]):
        record, prop = expected["record"], expected["proposal"]
        before, after, pair = expected["reference"], expected["candidate"], expected["comparison"]
        audit.check("stable_case_selection", item["episode_id"] == record["episode_id"] and item["record_id"] == record["record_id"]
                    and item["round"] == prop["round"] and item["candidate_id"] == prop["original"]["candidate_id"])
        audit.same("original_proposal", item["original_proposal"], prop["original"])
        for field in ("raw_response", "episode_artifact", "candidate_trace_file"):
            binding = item[field]
            audit.check("citation_binding:" + field, digest(ROOT / binding["path"]) == binding["sha256"])
        response = read_json(ROOT / item["raw_response"]["path"])
        matching = next(r for r in response["records"] if r["record_id"] == record["record_id"])
        audit.check("verbatim_original_response", item["original_proposal"] in matching["proposals"] and item["verbatim_model_reason"] == prop["original"]["reason"]
                    and "> " + item["verbatim_model_reason"] in markdown)
        audit.same("before_metrics", item["reference_metrics"], compact(before["metrics"]))
        audit.same("after_metrics", item["candidate_metrics"], compact(after["metrics"]))
        audit.same("before_parameters", item["reference_parameters"], before["parameters"])
        audit.same("after_parameters", item["candidate_parameters"], after["parameters"])
        predicted = expected["prediction"]
        reported = item["actual_metric_check"]
        audit.check("prediction_trace_binding", reported["prediction_reference_trace_hash"] == object_hash(before) and reported["prediction_candidate_trace_hash"] == object_hash(after))
        for output_field, source_field in (("prediction_status", "status"), ("prediction_evaluable", "evaluable"), ("prediction_matches", "prediction_matches"), ("observed_sign", "observed_sign"), ("delta", "delta")):
            audit.same("prediction:" + output_field, reported[output_field], predicted.get(source_field))
        audit.check("preexecution_handle", item["pre_execution_prediction"]["reference_handle_locked_before_execution"] == prop["reference_handle_locked_before_execution"])
        bm = {r["index"] for r in before["metrics"]["common_point_errors"] if r["error"] is not None}
        am = {r["index"] for r in after["metrics"]["common_point_errors"] if r["error"] is not None}
        missing = sorted(bm - am)
        expected_scope = {"baseline_covered_denominator": len(bm), "candidate_covered_denominator": len(am),
                          "lost_baseline_covered_indices": missing, "lost_baseline_covered_count": len(missing),
                          "own_coverage_maxima_are_paired_comparable": bm == am,
                          "baseline_mask_error_unavailable_reason": "BASELINE_COVERED_IDENTITIES_LOST" if missing else "EMPTY_BASELINE_COVERAGE" if not bm else None}
        audit.same("explicit_common_mask", item["comparison_scope"], expected_scope)
        if item["registered_comparison"]:
            guards = item["registered_comparison"]["registered_protection_readings"]
            audit.same("frozen_guard_result", guards, {k: pair[k] for k in guards})
        audit.check("locked_output_flags", item["proposal_became_locked_output"] == (record["selected_config_id"] == prop["executed_config_id"])
                    and item["actual_locked_config_id"] == record["selected_config_id"] and item["fallback"] == record["fallback"])
        for key in prior:
            if key not in ("A_adjudication", "synthetic_connection"):
                audit.same("repair_preserves_original:" + key, item[key], prior[key])
        audit.check("no_truth_or_human_invention", item["real_noise_truth_available"] is False and item["human_approval_claimed"] is False)
        audit.check("distinct_constructed_link", not item["synthetic_connection"].get("synthetic_truth_transferred_to_real_data", False))
    def clear_null_semantics(data, text):
        item = next(x for x in data["actual_ai_citations"] if x["citation_id"] == "AI-DEV-02")
        scope = item.get("comparison_scope", {})
        section = text.split("## AI-DEV-02", 1)[1].split("## AI-DEV-03", 1)[0]
        return (scope.get("lost_baseline_covered_count") == 11 and scope.get("baseline_covered_denominator") == 122
                and scope.get("candidate_covered_denominator") == 111 and scope.get("own_coverage_maxima_are_paired_comparable") is False
                and scope.get("baseline_mask_error_unavailable_reason") == "BASELINE_COVERED_IDENTITIES_LOST"
                and item["registered_comparison"]["registered_protection_readings"]["candidate_max_on_baseline_covered"] is None
                and "baseline-mask error is unavailable" in item["A_adjudication"] and "not observed paired geometric worsening" in item["synthetic_connection"]["reason"]
                and "不作配对数值增减判断" in section and "`null`" in section and "BASELINE_COVERED_IDENTITIES_LOST" in section and "→ None 工作米" not in section)
    audit.check("old_fault_rejected", not clear_null_semantics(old, old_markdown))
    audit.check("new_valid_narrative_accepted", clear_null_semantics(artifact, markdown))
    tampered = deepcopy(artifact)
    tampered["actual_ai_citations"][1]["comparison_scope"]["lost_baseline_covered_count"] = 0
    audit.check("engineering_null_fault_injection_rejected", not clear_null_semantics(tampered, markdown))
    synthetic = read_json(EV / "counterexamples/formal-02/synthetic_cases.json")
    audit.same("synthetic_originals_unchanged", artifact["synthetic_counterexamples"], old["synthetic_counterexamples"])
    execution_count = 0
    for item, source in zip(artifact["synthetic_counterexamples"], synthetic["cases"]):
        audit.check("synthetic_exact_case", item["case_id"] == source["case_id"] and item["case_object_hash"] == object_hash(source))
        audit.same("known_answers", item["known_answer_checks"], source["known_answer_checks"])
        audit.same("before_after", item["before_after"], source["before_after"])
        audit.check("not_invented_model_error", item["classification"] == "SYNTHETIC_COUNTEREXAMPLE" and item["attributed_as_actual_model_error"] is False)
        for execution in item["actual_executions"]:
            source_execution = source["executions"][execution["execution"]]
            audit.check("actual_synthetic_result_binding", execution["result_hash"] == object_hash(source_execution["output"]) == source_execution["review"]["target_hash"])
            audit.same("synthetic_metrics", execution["metrics"], compact(source_execution["output"]["metrics"]))
            execution_count += 1
    audit.check("constructed_denominators", len(synthetic["cases"]) == 6 and synthetic["known_answer_check_count"] == 25 and execution_count == 19)
    ex = read_json(directory / "root_rebuild_execution.json")
    audit.check("actual_rebuild_success", ex["exit_code"] == 0 and ex["log_sha256"] == digest(directory / "root_rebuild.log") and ex["actual_command"] == [".venv/bin/python", "-m", "task1.evidence.goal2.a_epoch02.actual_ai_critique.build_actual_ai_critique"])
    closure = {"status": "VERIFIED" if not audit.errors else "REJECTED", "issue_id": issue["issue_id"], "role_context": "/root/c_contract", "at": now(),
               "targets": deepcopy(issue["repair_evidence"]), "source_hashes": deepcopy(issue["repair_source_hashes"]),
               "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch", "actual_raw_quotes", "complete_legal_tradeoff_set", "explicit_null_reason_and_coverage", "original_numbers_and_machine_flags_preserved"],
               "unchecked_components": ["source_datum_truth", "real_noise_truth", "full_goal_acceptance"], "check_count": audit.check_count, "errors": audit.errors,
               "audit_program": bound(Path(__file__)), "engineering_fault_injection": "C-owned deep copy only; real artifacts untouched", "elapsed_seconds": time.perf_counter() - started}
    write_json(OUT / "ai_null_closure_receipt.json", closure, exclusive=True)
    partial_path = OUT / "counterexamples_epoch02_receipt.json"
    partial = read_json(partial_path)
    task_targets = [bound(ROOT / entry["path"]) for entry in state["tasks"]["counterexamples"]["evidence"]]
    receipt = {"status": closure["status"], "role_context": "/root/c_contract", "task": "counterexamples", "at": now(), "targets": task_targets,
               "source_hashes": {p: digest(ROOT / p) for p in task_sources("counterexamples")}, "checked_components": sorted(REQUIRED_COMPONENTS["counterexamples"]),
               "unchecked_components": ["ground_truth_real_noise", "full_goal_acceptance"], "errors": audit.errors,
               "known_answers": 25, "synthetic_executions": 19, "exposed_pilot_executions": 10, "actual_ai_citations": 6, "complete_actual_legal_tradeoffs": 4,
               "partial_numeric_review_reused": bound(partial_path), "partial_numeric_checked_components": partial["checked_components"],
               "AI_null_issue_closure": bound(OUT / "ai_null_closure_receipt.json"), "new_model_calls": 0, "new_candidate_experiments": 0,
               "check_count": audit.check_count, "audit_program": bound(Path(__file__)), "elapsed_seconds": time.perf_counter() - started}
    write_json(OUT / "counterexamples_complete_receipt.json", receipt, exclusive=True)
    print({k: closure[k] for k in ("status", "check_count", "errors")})
    return receipt


if __name__ == "__main__":
    result = main()
    raise SystemExit(result["status"] != "VERIFIED")
