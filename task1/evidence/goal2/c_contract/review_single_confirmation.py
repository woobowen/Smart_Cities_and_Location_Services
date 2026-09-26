"""Independent frozen single-candidate confirmation, without production compare.

All 360 labelled record pairs and null/stratum denominators are reconstructed
from previously independently verified trace bytes. No candidate selection,
new numerical experiment, or model invocation occurs here.
"""
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import Audit, read_compressed, summary_expected
from review_live_modes_epoch02 import assessment, compact
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS

OUT = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"
DIRECTORY = EV / "a_epoch02/heldout_single_confirmation"
PAIR_METRICS = ("n_final", "n_filtered", "n_direction_removed", "n_dp_output", "point_retention", "common_covered_points",
                "common_coverage", "raw_break_crossings", "raw_windows_covered", "dp_saving", "dp_max_error", "common_max_error")


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def paired(candidate, reference):
    comparison = assessment(candidate, reference)
    masks = [{x["index"] for x in record["metrics"]["common_point_errors"] if x["error"] is not None} for record in (candidate, reference)]
    same_p = next(s["input"] for s in candidate["stages"] if s["name"] == "P") == next(s["input"] for s in reference["stages"] if s["name"] == "P")
    comparison.update(same_common_covered_mask=masks[0] == masks[1], same_dp_input_reference=same_p)
    for metric in PAIR_METRICS:
        a, b = candidate["metrics"][metric], reference["metrics"][metric]
        reason = None
        if a is None or b is None:
            reason = "UNAVAILABLE_IN_AT_LEAST_ONE_ARM"
        elif metric in ("n_dp_output", "dp_saving", "dp_max_error") and not same_p:
            reason = "DIFFERENT_DP_INPUT_REFERENCE"
        elif metric == "common_max_error" and masks[0] != masks[1]:
            reason = "DIFFERENT_COMMON_COVERED_MASK_USE_BASELINE_MASK_READING"
        comparison.update({"reference_" + metric: b, "candidate_" + metric: a,
                           "delta_" + metric: None if reason else a - b, "delta_" + metric + "_reason": reason})
    return comparison


def outcomes(rows):
    return {"n_records": len(rows), "feasible_records": sum(r["feasible"] for r in rows),
            "strict_gain_records": sum(r["strict_gain"] for r in rows),
            "feasible_all_records": bool(rows) and all(r["feasible"] for r in rows),
            "strict_gain_any_record": any(r["strict_gain"] for r in rows),
            "statuses": dict(Counter(r["status"] for r in rows)),
            "protection_failures": dict(Counter(reason for r in rows for reason in r["protection_failures"])),
            "quality_accepted": False}


def status(rows):
    if any(r["status"] == "REJECTED_BY_CONSTRAINT" for r in rows):
        return "REJECTED_BY_CONSTRAINT"
    if not all(r["feasible"] for r in rows):
        return "TRADEOFF"
    return "SUPPORTED_WITHIN_SCOPE" if any(r["strict_gain"] for r in rows) else "NO_DEMONSTRATED_GAIN"


def check_csv(audit, row, expected, label):
    for key, value in expected.items():
        actual = row.get(key)
        if isinstance(value, (dict, list)):
            audit.same(label + ":" + key, json.loads(actual), value, 1e-10)
        elif value is None:
            audit.check(label + ":" + key, actual == "")
        elif isinstance(value, bool):
            audit.check(label + ":" + key, actual == str(value))
        elif isinstance(value, (int, float)):
            audit.check(label + ":" + key, actual is not None and actual != "" and math.isclose(float(actual), value, rel_tol=0, abs_tol=1e-10))
        else:
            audit.check(label + ":" + key, actual == value)


def case_ids(selected, baseline, pairs, cards):
    expected = {}
    indexed = {p["record_id"]: p for p in pairs}
    layers = defaultdict(list)
    for rid in selected:
        layers[cards[rid]["stratum"].split("_")[0]].append(rid)
    for layer, ids in layers.items():
        median = statistics.median(cards[rid]["span_work_m"] for rid in ids)
        expected["representative_" + layer] = min(ids, key=lambda rid: (abs(cards[rid]["span_work_m"] - median), rid))
    losses = [(baseline[rid]["metrics"]["common_covered_points"] - row["metrics"]["common_covered_points"], rid) for rid, row in selected.items()]
    losses = [item for item in losses if item[0] > 0]
    expected["worst_coverage"] = min(losses, key=lambda row: (-row[0], row[1]))[1] if losses else None
    errors = [(p["candidate_max_on_baseline_covered"], p["record_id"]) for p in pairs if p["candidate_max_on_baseline_covered"] is not None]
    expected["worst_comparable_common_error"] = min(errors, key=lambda row: (-row[0], row[1]))[1] if errors else None
    boundary, changed = [], []
    for rid, row in selected.items():
        for stage in row["stages"]:
            if stage["name"] == "P":
                for op in stage["operations"]:
                    for point in op["runtime_dp_check"]["error_by_original_index"]:
                        gap = abs(point["error"] - op["tolerance"])
                        if point["error"] > 0 and gap > 0:
                            boundary.append((gap, rid, point["index"], op["input_segment_id"]))
            if stage["name"] == "D":
                for before, after in zip(stage["input"], stage["output"]):
                    prior = set(zip(before["indices"], before["indices"][1:]))
                    changed.extend((rid, a, b) for a, b in zip(after["indices"], after["indices"][1:]) if (a, b) not in prior)
    expected["near_DP_boundary"] = min(boundary)[1] if boundary else None
    expected["actual_D_neighborhood_change"] = min(changed)[0] if changed else None
    failed = sorted(rid for rid, p in indexed.items() if not p["feasible"])
    gain = sorted(rid for rid, p in indexed.items() if p["strict_gain"])
    unavailable = sorted(rid for rid in selected if any(row["metrics"][key] is None for row in (selected[rid], baseline[rid]) for key in ("common_max_error", "dp_max_error")))
    for name, rows in (("first_protection_failure", failed), ("first_strict_gain", gain), ("first_unavailable_error", unavailable)):
        expected[name] = rows[0] if rows else None
    return expected, min(boundary) if boundary else None, min(changed) if changed else None


def main():
    audit = Audit()
    path = DIRECTORY / "single_candidate_confirmation.json"
    result = read_json(path)
    expected_targets = [path, DIRECTORY / "SINGLE_CANDIDATE_CONFIRMATION.md"]
    for field in ("source", "analysis_source", "comparison_definition_source", "candidate_lock", "evaluation_freeze",
                  "development_A_selection_evidence", "read_scope_registry", "case_rules"):
        target = result[field]
        audit.check("bound_input:" + field, digest(ROOT / target["path"]) == target["sha256"])
        expected_targets.append(ROOT / target["path"])
    for target_path, sha in result["input_hashes"].items():
        audit.check("all_input_bytes", digest(ROOT / target_path) == sha)
    for name, info in result["independent_input_reviews"].items():
        receipt = read_json(ROOT / info["path"])
        audit.check("independent_parent:" + name, receipt["status"] == "VERIFIED" and digest(ROOT / info["path"]) == info["sha256"])
        for target in receipt["targets"]:
            audit.check("independent_parent_unchanged_target", digest(ROOT / target["path"]) == target["sha256"])
    lock, freeze = read_json(EV / "candidate_lock.json"), read_json(EV / "evaluation_freeze.json")
    contract = read_json(ROOT / "task1/config/goal2/contract.json")
    cards = read_json(EV / "data/raw_diagnostics.json")
    audit.check("frozen_before_evaluation", lock["g2_eval_observed_for_selection"] is False and freeze["evaluation_previously_observed"] is False)
    audit.same("locked_candidates_unchanged", lock["selected_single_candidates"], freeze["selected_single_candidates"])
    audit.same("full_scope", result["input_scope"]["record_ids"], freeze["eval_ids"])
    scope = read_json(ROOT / result["read_scope_registry"]["path"])
    audit.check("no_model_results_read", set(scope) == {"parameter_development", "order_development", "evaluation_parameters", "evaluation_orders"})
    directory = EV / "runs" / scope["evaluation_parameters"]
    manifest = read_json(directory / "manifest.json")
    parent = read_json(OUT / "evaluation_parameters_bound_receipt.json")
    audit.check("verified_heldout_manifest", any(t["path"] == str((directory / "manifest.json").relative_to(ROOT)) and t["sha256"] == digest(directory / "manifest.json") for t in parent["targets"]))
    entries = {r["config_id"]: r for r in manifest["artifacts"].values()}
    refid = "cfg-b15b8281b73592fb"
    fixed = lock["selected_single_candidates"]
    records = {}
    for cid in {refid} | {r["config_id"] for r in fixed.values()}:
        audit.check("trace_hash", digest(directory / entries[cid]["file"]) == entries[cid]["sha256"])
        records[cid] = {r["record_id"]: r for r in read_compressed(directory / entries[cid]["file"])["records"]}
        audit.same("exact120_record_order", list(records[cid]), freeze["eval_ids"])
    baseline = records[refid]
    tables = {}
    for name, info in result["tables"].items():
        target = ROOT / info["path"]
        audit.check("table_hash:" + name, digest(target) == info["sha256"])
        with target.open(newline="") as stream:
            tables[name] = list(csv.DictReader(stream))
        audit.check("table_rows:" + name, len(tables[name]) == info["rows"])
        expected_targets.append(target)
    audit.check("three_single_candidates", {r["candidate"] for r in result["candidate_results"]} == {"C-S", "C-D", "C-P"} and len(result["candidate_results"]) == 3)
    indexed_pairs = {(r["candidate"], r["record_id"]): r for r in tables["candidate_record_pairs"]}
    indexed_metrics = {(r["candidate"], r["record_id"], r["arm"]): r for r in tables["candidate_record_metrics"]}
    audit.check("complete360_pairs_and720_arms", len(indexed_pairs) == len(tables["candidate_record_pairs"]) == 360 and len(indexed_metrics) == len(tables["candidate_record_metrics"]) == 720)
    expected_nulls = []
    actual_results = []
    for name in ("C-S", "C-D", "C-P"):
        cid = fixed[name]["config_id"]
        selected = records[cid]
        saved = next(row for row in result["candidate_results"] if row["candidate"] == name)
        audit.check(name + ":single_parameter_family", all(fixed[name]["parameters"][k] == contract["reference_parameters"][k] for k in contract["reference_parameters"]
                    if k not in ({"dt", "distance", "min_points", "min_length"} if name == "C-S" else {"direction"} if name == "C-D" else {"dp"})))
        audit.check(name + ":frozen_parameter_identity", cid == saved["config_id"] and all(saved[k] == v for k, v in fixed[name]["parameters"].items()))
        pairs, strata = [], defaultdict(list)
        for rid, candidate in selected.items():
            pair = paired(candidate, baseline[rid])
            pairs.append(pair)
            strata[cards[rid]["stratum"]].append(rid)
            check_csv(audit, indexed_pairs[(name, rid)], {"candidate": name, "config_id": cid, "stratum": cards[rid]["stratum"], **pair,
                "raw_point_denominator": len(candidate["source_record"]["timestamps"]), "reference_record_trace_hash": object_hash(baseline[rid]),
                "candidate_record_trace_hash": object_hash(candidate), "shared_experiment_key": entries[cid]["experiment_key"]}, name + ":pair:" + rid)
            for arm, record in (("reference", baseline[rid]), ("candidate", candidate)):
                metric = record["metrics"]
                check_csv(audit, indexed_metrics[(name, rid, arm)], compact(metric), name + ":metrics:" + rid + ":" + arm)
                for key, reason, denominator in (("dp_saving", "dp_saving_reason", "n_dp_input"), ("dp_max_error", "dp_error_reason", "dp_error_denominator"),
                      ("common_max_error", "common_error_reason", "common_error_denominator"), ("common_coverage", "common_coverage_reason", "common_raw_points"),
                      ("final_length", "final_length_reason", "n_final"), ("raw_length", "raw_length_reason", "n_input")):
                    if metric[key] is None:
                        expected_nulls.append({"candidate": name, "record_id": rid, "arm": arm, "metric": key, "value": None, "reason": metric[reason],
                            "metric_denominator": metric[denominator], "raw_point_denominator": metric["n_input"], "original_record_denominator": 120})
        expected_status = status(pairs)
        retained = cid == refid
        recommendation = "KEEP" if retained or expected_status == "SUPPORTED_WITHIN_SCOPE" else "TRADEOFF" if expected_status == "TRADEOFF" else "REJECT"
        expected = {**outcomes(pairs), **summary_expected([r["metrics"] for r in selected.values()]), "evaluation_status": expected_status, "recommendation": recommendation,
                    "reference_retained": retained, "automatic_new_goal3_candidate": expected_status == "SUPPORTED_WITHIN_SCOPE" and not retained,
                    "quality_accepted": False, "final_method_frozen": False, "development_selection_locked_before_evaluation": True, "evaluation_used_for_reselection": False}
        for key, value in expected.items():
            audit.same(name + ":summary:" + key, saved[key], value, 1e-10)
        check_csv(audit, next(r for r in tables["candidate_evaluation"] if r["candidate"] == name),
                  {k: v for k, v in expected.items() if k not in ("development_selection_locked_before_evaluation", "evaluation_used_for_reselection")}, name + ":evaluation_csv")
        check_csv(audit, next(r for r in tables["candidate_development"] if r["candidate"] == name),
                  {"candidate": name, **fixed[name], "evaluation_was_used_for_selection": False, "source_run_id": lock["parameter_run_id"]}, name + ":development_csv")
        audit.check(name + ":no_new_calculation", saved["computation"]["count_as_new_independent_calculation"] is False and saved["computation"]["batch"]["sha256"] == entries[cid]["sha256"])
        check_csv(audit, next(r for r in tables["candidate_shared_calculations"] if r["candidate"] == name),
                  {"candidate": name, **saved["computation"], "records": 120, "raw_points": 12173,
                   "actual_existing_batch_elapsed_seconds": entries[cid]["elapsed_seconds"]}, name + ":shared_calculations")
        for stratum, rids in strata.items():
            group = [p for p in pairs if p["record_id"] in rids]
            row = next(r for r in tables["candidate_by_stratum"] if r["candidate"] == name and r["stratum"] == stratum)
            check_csv(audit, row, {**outcomes(group), "research_status": status(group)}, name + ":stratum")
            for arm, source in (("reference", baseline), ("candidate", selected)):
                row = next(r for r in tables["candidate_stratum_metrics"] if r["candidate"] == name and r["stratum"] == stratum and r["arm"] == arm)
                check_csv(audit, row, {**summary_expected([source[rid]["metrics"] for rid in rids]), "statistical_unit": "original_record", "population_weighted": False}, name + ":stratum_metrics")
        expected_cases, boundary, changed = case_ids(selected, baseline, pairs, cards)
        actual_cases = [row for row in result["candidate_cases"] if row["candidate"] == name]
        audit.check(name + ":complete_cases", len(actual_cases) == len(expected_cases) and {row["case_kind"] for row in actual_cases} == set(expected_cases))
        for case in actual_cases:
            audit.check(name + ":independent_case_rule:" + case["case_kind"], case["record_id"] == expected_cases[case["case_kind"]])
            if case["case_kind"] == "near_DP_boundary" and boundary:
                audit.check(name + ":near_case_index_segment", case["selection_details"]["original_index"] == boundary[2]
                            and case["selection_details"]["segment_id"] == boundary[3] and case["selection_details"]["absolute_gap_work_m"] == boundary[0])
            if case["case_kind"] == "actual_D_neighborhood_change" and changed:
                audit.check(name + ":D_case_actual_indices", case["selection_details"]["from_index"] == changed[1] and case["selection_details"]["to_index"] == changed[2])
        actual_results.append({"candidate": name, "config_id": cid, "independent_status": expected_status, "recommendation": recommendation,
                               "protected_records": sum(r["feasible"] for r in pairs), "strict_gain_records": sum(r["strict_gain"] for r in pairs),
                               "raw_points": saved["n_input"], "common_covered_points": saved["common_covered_points"], "final_points": saved["n_final"]})
    audit.check("null_denominator_complete", len(expected_nulls) == len(tables["candidate_unavailable_metrics"]) == result["nulls"]["unavailable_reading_rows"])
    for actual, expected in zip(tables["candidate_unavailable_metrics"], expected_nulls):
        check_csv(audit, actual, expected, "unavailable")
    audit.check("shared_reference_not_three_experiments", fixed["C-D"]["config_id"] == fixed["C-P"]["config_id"] == refid and len(records) == 2
                and result["resources"]["single_confirmation_unique_existing_record_configurations"] == 240
                and result["resources"]["named_family_record_comparisons"] == 360
                and result["resources"]["analysis_new_candidate_processing_calls"] == result["resources"]["analysis_new_model_dispatches"] == 0)
    for case in result["candidate_cases"]:
        case_csv = next(r for r in tables["candidate_case_selection"] if r["candidate"] == case["candidate"] and r["case_kind"] == case["case_kind"])
        check_csv(audit, case_csv, case, "case_table")
        if case["record_id"] is None:
            audit.check("explicit_missing_case", case["status"] == "NO_AVAILABLE_CASE" and bool(case["unavailable_reason"]))
            continue
        rid, name = case["record_id"], case["candidate"]
        row = records[fixed[name]["config_id"]][rid]
        audit.same("case:independent_pair", case["comparison"], paired(row, baseline[rid]), 1e-10)
        audit.same("case:actual_candidate_metrics", case["candidate_metrics"], compact(row["metrics"]))
        audit.check("case:record_hashes", case["candidate_record_trace_hash"] == object_hash(row) and case["reference_record_trace_hash"] == object_hash(baseline[rid]))
    targets = {str(p.relative_to(ROOT)): bound(p) for p in expected_targets}
    controller = read_json(EV / "goal_state.json")
    for target in controller["tasks"]["candidates"].get("evidence", []):
        audit.check("exact_submitted_target_covered", target["path"] in targets and targets.get(target["path"]) == target)
    receipt = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": "candidates", "at": now(),
               "targets": list(targets.values()), "source_hashes": {p: digest(ROOT / p) for p in task_sources("candidates")},
               "checked_components": REQUIRED_COMPONENTS["candidates"] + ["all360_independent_pairs", "all_null_reasons_denominators", "stratum_summaries", "shared_evidence_costs", "all_case_ranking_identity_and_metrics"],
               "unchecked_components": ["ground_truth_cleaning_accuracy", "formal_final_adoption", "full_Goal2_acceptance"],
               "check_count": audit.check_count, "errors": audit.errors, "independent_results": actual_results, "audit_program": bound(Path(__file__)),
               "numerical_review_reused": bound(OUT / "evaluation_parameters_bound_receipt.json"), "new_model_calls": 0, "new_processing_experiments": 0,
               "scope_limit": "Fixed single candidates only; independent assessment and all denominators, with pre-existing exact raw-trace numerical review. No selection after holdout or candidate combination."}
    write_json(OUT / "single_candidate_confirmation_receipt.json", receipt, exclusive=True)
    print({key: receipt[key] for key in ("status", "check_count", "errors", "independent_results")})


if __name__ == "__main__":
    main()
