"""Read-only C reconstruction of analytic fixtures and already exposed pilot cases."""
import argparse
from collections import Counter
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from independent_numeric import (audit_record, directions, dp, finite_distance, partition,
                                 length, common_reference, allowance)
from review_development_runs import Audit
from task1.workflow.io import read_json, write_json, digest, object_hash, now

OUT = Path(__file__).parent
FIXTURES = {
    "normal_right_angle": [[0, 0], [10, 0], [20, 0], [20, 10], [20, 20]],
    "legitimate_zigzag": [[0, 0], [10, 0], [10, 10], [20, 10], [20, 20]],
    "injected_spike": [[-20, 0], [-10, 0], [0, 30], [10, 0], [20, 0]],
    "zero_and_time_conflict": [[0, 0], [0, 0], [5, 0], [5, 5], [10, 5]],
    "time_gap": [[0, 0], [10, 0], [20, 0], [30, 0], [40, 0]],
    "hidden_distance_break": [[0, 0], [401, 0], [399, 0]],
    "finite_segment": [[0, 0], [2, 1], [1, 0]],
    "threshold_equality": [[0, 0], [1, 1], [2, 0]],
    "own_clean_reference": [[0, 0], [0, 1], [0, 2], [1, 3], [1, 4]],
}
TIMES = {"zero_and_time_conflict": [0, 0, 0, 1, 2], "time_gap": [0, 10, 100, 110, 120]}
REFERENCE = {"dt": 30, "distance": 400, "min_points": 5, "min_length": 65, "direction": 35, "dp": 5}


def planar(audit, result, name, expected_parameters, expected_order, contract_hash):
    xy = FIXTURES[name]
    times = TIMES.get(name, list(range(len(xy))))
    source = {"record_id": "fixture:" + name, "indices": list(range(len(xy))), "timestamps": times, "xy": xy}
    audit.same(name + ":analytic_raw", result["source_record"], source)
    audit.same(name + ":parameters", result["parameters"], expected_parameters)
    audit.check(name + ":order_contract_label", result["order"] == expected_order and result["contract_hash"] == contract_hash
                and result["classification"] == result["provenance"]["source_kind"] == "SYNTHETIC_COUNTEREXAMPLE")
    audit.check(name + ":no_real_truth_claim", result["provenance"]["claims_population_accuracy"] is False and result["modified_values"] == 0)
    current, fates, p_before, p_after, residuals = [list(range(len(xy)))], {}, [], [], []
    for position, (stage, step) in enumerate(zip(result["stages"], expected_order.split("-")), 1):
        audit.same(name + ":stage_input", [s["indices"] for s in stage["input"]], current)
        audit.check(name + ":stage_identity", stage["name"] == step and stage["position"] == position)
        out = []
        for group in current:
            if step == "S":
                segments, _ = partition(times, xy, group, expected_parameters["dt"], expected_parameters["distance"])
                for indices in segments:
                    reasons = (["TOO_FEW_POINTS"] if len(indices) < expected_parameters["min_points"] else [])
                    if length(xy, indices) < expected_parameters["min_length"]:
                        reasons.append("TOO_SHORT_LENGTH")
                    if reasons:
                        fates.update((i, ("filtered", position, reasons)) for i in indices)
                    else:
                        out.append(indices)
            elif step == "D":
                decisions = directions(xy, group, expected_parameters["direction"])
                removed = {row["index"] for row in decisions if row["candidate"] is True}
                out.append([i for i in group if i not in removed])
                fates.update((i, ("denoised", position, ["DIRECTION_RULE"])) for i in removed)
            else:
                kept = dp(xy, group, expected_parameters["dp"])
                out.append(kept)
                p_before.extend(group)
                p_after.extend(kept)
                errors = {i: 0.0 for i in kept}
                for a, b in zip(kept, kept[1:]):
                    errors.update((i, finite_distance(xy[i], xy[a], xy[b])) for i in group if a < i < b)
                residuals.extend(errors.values())
                fates.update((i, ("simplified", position, ["DP_WITHIN_TOLERANCE"])) for i in group if i not in kept)
        audit.same(name + ":stage_output", [s["indices"] for s in stage["output"]], out)
        for group in stage["input"] + stage["output"]:
            audit.same(name + ":unchanged_times", group["timestamps"], [times[i] for i in group["indices"]])
            audit.same(name + ":unchanged_xy", group["xy"], [xy[i] for i in group["indices"]])
            audit.same(name + ":stage_length", group["features"]["length"], length(xy, group["indices"]), 1e-12)
        current = out
    retained = [i for group in current for i in group]
    fates.update((i, ("retained", 4, ["FINAL_OUTPUT"])) for i in retained)
    audit.same(name + ":final_groups", [r["indices"] for r in result["final_segments"]], current)
    audit.same(name + ":ledger_complete", [r["original_index"] for r in result["point_actions"]], list(range(len(xy))))
    for row in result["point_actions"]:
        i = row["original_index"]
        audit.check(name + ":ledger_fate", (row["action"], row["stage_position"], row["reasons"]) == fates[i]
                    and row["timestamp"] == times[i] and row["xy"] == xy[i])
    ref = common_reference(times, xy, current)
    counts = Counter(x[0] for x in fates.values())
    expected = {"n_input": len(xy), "n_final": len(retained), "n_filtered": counts["filtered"],
                "n_direction_removed": counts["denoised"], "n_dp_removed": counts["simplified"],
                "n_dp_input": len(p_before), "n_dp_output": len(p_after),
                "dp_saving": 1 - len(p_after) / len(p_before) if p_before else None,
                "dp_max_error": max(residuals, default=None), "common_raw_points": len(xy),
                "common_coverage": len(ref["covered_indices"]) / len(xy), "common_max_error": ref["max_error"],
                "raw_break_count": len(ref["breaks"]), "raw_break_crossings": len(ref["crossed_edges"]),
                "all_filtered": len(xy) == counts["filtered"], "no_output": len(retained) == 0}
    for key, value in expected.items():
        audit.same(name + ":metric:" + key, result["metrics"][key], value, allowance(xy, expected_parameters["dp"]))
    return {"final_groups": current, "fates": fates, "metrics": expected, "common_reference": ref}


def main(directory, output_name):
    started = time.perf_counter()
    directory = ROOT / directory
    manifest = read_json(directory / "manifest.json")
    synthetic = read_json(directory / "synthetic_cases.json")
    pilot = read_json(directory / "exposed_pilot_cases.json")
    contract = read_json(ROOT / "task1/config/goal2/contract.json")
    raw = read_json(ROOT / contract["raw_path"])
    audit, reconstructions = Audit(), {}
    for p, value in manifest["artifacts"].items():
        audit.check("artifact_hash:" + p, digest(directory / p) == value)
    for p, value in manifest["source_files"].items():
        audit.check("source_hash:" + p, digest(ROOT / p) == value)
    audit.check("source_tree", object_hash(manifest["source_files"]) == manifest["source_tree_hash"])
    audit.check("fixture_contract", object_hash(synthetic["fixture_contract"]) == synthetic["fixture_contract_hash"] == manifest["fixture_contract_hash"])
    audit.check("raw_contract", digest(ROOT / contract["raw_path"]) == manifest["raw_sha256"] and digest(ROOT / "task1/config/goal2/contract.json") == manifest["g2_parent_contract_hash"])
    audit.check("synthetic_boundary", synthetic["classification"] == "SYNTHETIC_COUNTEREXAMPLE" and synthetic["real_data_accuracy_claim"] is False)
    for name, points in FIXTURES.items():
        audit.same("independent_analytic_definition:" + name, synthetic["fixture_contract"]["definitions"][name]["xy"], points)
    cases = {case["case_id"]: case for case in synthetic["cases"]}
    audit.check("six_families", len(cases) == 6)
    for case in synthetic["cases"]:
        for key, entry in case["executions"].items():
            result = entry["output"]
            name = result["record_id"].split(":", 1)[1]
            params = {**REFERENCE, "min_points": 2, "min_length": 0}
            if case["case_id"].startswith(("CE01", "CE02", "CE06")):
                params["dp"] = 0
            if key.startswith("dp="):
                params["dp"] = float(key[3:])
            if key == "finite":
                params["dp"] = 1.1
            if key == "covered":
                params["dp"] = 1
            if key == "all_filtered":
                params = dict(REFERENCE)
            if key.startswith("direction="):
                params["direction"] = int(key.split("=")[1])
            order = key.split(":")[1] if ":" in key else "S-D-P"
            reconstruction = planar(audit, result, name, params, order, synthetic["fixture_contract_hash"])
            reconstructions[(case["case_id"], key)] = reconstruction
            audit.check("receipt_binding", entry["review"]["status"] == "VERIFIED" and entry["review"]["target_hash"] == object_hash(result)
                        and entry["review"]["trusted_reference_hash"] == object_hash(result["source_record"]))
    audit.check("19_actual_synthetic_runs", len(reconstructions) == manifest["synthetic_pipeline_executions"] == 19)
    expected = {
        "normal_right_angle: direction deletion identities": [], "legitimate_zigzag: direction deletion identities": [1, 2],
        "injected_spike: direction deletion identities": [1, 2], "zero-dt edges remain unavailable": 2,
        "same-time different-position count": 1, "zero-displacement direction unavailable": 1,
        "point 1 undefined window retained": "UNCOMPUTABLE_DIRECTION_IN_WINDOW",
        "time reference keeps record coverage": True, "P-before-S time fixture loses all output": True,
        "not every raw point was filtered by S": False, "distance breakpoint hidden by P": 1,
        "P removed triggering point": [1], "finite distance rejects infinite-line shortcut": "REJECTED",
        "finite distance is sqrt(2)": math.sqrt(2), "correct finite DP retains middle point": 3,
        "zero tolerance preserves all points": 3, "below equality retains point": 3, "equality does not recurse": 2,
        "all raw points remain denominator": 3, "empty output coverage": 0.0, "empty error is null": None,
        "empty DP saving is null": None, "both own-P errors are zero": [0.0, 0.0],
        "fixed-raw errors distinguish the methods": True, "candidate clean deletion retains coverage denominator": 5}
    observed = {row["name"]: row for case in synthetic["cases"] for row in case["known_answer_checks"]}
    audit.same("known_answer_exact_scope", sorted(observed), sorted(expected))
    for label, value in expected.items():
        audit.same("known_answer:" + label, observed[label]["observed"], value, 1e-12)
        audit.same("declared_known_answer:" + label, observed[label]["expected"], value, 1e-12)
    for name in ("normal_right_angle", "legitimate_zigzag", "injected_spike"):
        entry = cases["CE01_DIRECTION_AMBIGUITY"]["executions"][name]
        removed = {i for i, fate in reconstructions[("CE01_DIRECTION_AMBIGUITY", name)]["fates"].items() if fate[0] == "denoised"}
        truth = {2} if name == "injected_spike" else set()
        expected_detection = {"known_noise_points": len(truth), "known_normal_points": 5 - len(truth),
                              "true_positive": len(removed & truth), "false_positive": len(removed - truth),
                              "false_negative": len(truth - removed), "only_authored_fixture_truth": True}
        audit.same("synthetic_truth_counts:" + name, entry["synthetic_detection_counts"], expected_detection)
    zero = cases["CE02_UNDEFINED_IS_NOT_ZERO"]["executions"]["zero_and_time_conflict"]["output"]
    edges = zero["stages"][0]["input"][0]["features"]["edges"]
    audit.check("zero_time_not_zero_speed", edges[0]["speed"] is None and edges[1]["speed"] is None and edges[0]["direction_degrees"] is None)
    audit.check("finite_distance_independent", finite_distance([2, 1], [0, 0], [1, 0]) > 1.1 and abs(finite_distance([2, 1], [0, 0], [1, 0]) - math.sqrt(2)) < 1e-14)
    pilot_rows = []
    audit.same("pilot_exact_scope", pilot["record_ids"], ["0", "1", "2", "246", "256", "306", "352"])
    audit.check("pilot_exposure_label", pilot["exposure"] == "KNOWN_EXPOSED" and pilot["fresh_holdout_claim"] is False and pilot["source_crs"] == "UNVERIFIED")
    executions = [(rid, entry) for rid, entry in pilot["executions"].items()]
    executions += [(pilot["near_threshold_case"]["record_id"], entry) for entry in pilot["near_threshold_case"]["same_upstream_threshold_runs"].values()]
    for rid, entry in executions:
        target = entry["output"]
        result = audit_record(target, raw[rid], target["parameters"], "S-D-P", contract["model"], manifest["g2_parent_contract_hash"])
        audit.check("pilot_full_independent_reconstruction", result["status"] == "VERIFIED", result["errors"])
        pilot_rows.append({"record_id": rid, "parameters": target["parameters"], "checks": result["checks"], "status": result["status"]})
    audit.check("pilot10_runs", len(executions) == manifest["pilot_pipeline_executions"] == 10)
    for row in pilot["all_filtered_records_0_1_2"]:
        rid = row["record_id"]
        for part in row["segments"]:
            xy = pilot["executions"][rid]["output"]["source_record"]["xy"]
            distance = length(xy, part["indices"])
            reasons = (["TOO_FEW_POINTS"] if len(part["indices"]) < 5 else []) + (["TOO_SHORT_LENGTH"] if distance < 65 else [])
            audit.same("pilot_filter_reasons:" + rid, part["filter_reasons"], reasons)
            audit.same("pilot_filter_length:" + rid, part["within_segment_length_working_m"], distance, 1e-9)
    near = pilot["near_threshold_case"]
    candidates = []
    for rid, entry in pilot["executions"].items():
        stage = next(s for s in entry["output"]["stages"] if s["name"] == "P")
        xy = entry["output"]["source_record"]["xy"]
        for before, after in zip(stage["input"], stage["output"]):
            for a, b in zip(after["indices"], after["indices"][1:]):
                for i in before["indices"]:
                    if a < i < b:
                        distance = finite_distance(xy[i], xy[a], xy[b])
                        if distance > 0:
                            candidates.append((abs(5 - distance), int(rid), i, [a, b], distance))
    selected = min(candidates)
    audit.check("pilot_near_threshold_selection", [int(near["record_id"]), near["original_index"], near["reference_bracketing_indices"]] == list(selected[1:4]))
    audit.same("pilot_near_threshold_error", near["actual_error_working_m"], selected[4], 1e-9)
    receipt = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": None,
               "classification": "PARTIAL_C_COUNTEREXAMPLE_AND_EXPOSED_PILOT_REVIEW_NOT_FULL_R07_ACCEPTANCE",
               "at": now(), "run_id": manifest["run_id"], "targets": [{"path": str((directory / "manifest.json").relative_to(ROOT)), "sha256": digest(directory / "manifest.json")}],
               "checked_components": ["known_answers", "real_execution", "synthetic_labels", "pilot_explanations"],
               "unchecked_components": ["actual_current_model_citations_and_AI_critique", "full_goal_acceptance"],
               "synthetic_executions": 19, "pilot_executions": 10, "known_answers": 25, "checks": audit.check_count,
               "pilot_independent_checks": sum(x["checks"] for x in pilot_rows), "pilot_reconstructions": pilot_rows,
               "errors": audit.errors, "real_model_calls_in_review": 0, "elapsed_seconds": time.perf_counter() - started,
               "audit_program": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))}}
    write_json(OUT / output_name, receipt, exclusive=True)
    print({key: receipt[key] for key in ("status", "synthetic_executions", "pilot_executions", "known_answers", "checks", "pilot_independent_checks", "errors")})
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("output_name")
    args = parser.parse_args()
    result = main(args.directory, args.output_name)
    raise SystemExit(result["status"] != "VERIFIED")
