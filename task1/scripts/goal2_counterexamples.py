"""Execute analytic Goal 2 counterexamples and exposed G1 case explanations.

Run from the repository root with the existing .venv, for example:
  .venv/bin/python -m task1.scripts.goal2_counterexamples --output <new-directory>

This command makes no model requests. Analytic fixture thresholds are part of
an ENGINEERING_TEST subprotocol, not additions to the real candidate grid.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import math
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from task1.workflow.coordinates import conditional_adapter
from task1.workflow.evaluation import verify_simplification
from task1.workflow.g2_metrics import review_record
from task1.workflow.g2_pipeline import REFERENCE_PARAMETERS, run_record
from task1.workflow.io import DATA, ROOT, digest, now, object_hash, read_json, relative, write_json


GOAL_ID = "SC-LAB1-G2-EXPERIMENTS-001"
PILOT_IDS = ["0", "1", "2", "246", "256", "306", "352"]
RAW_SHA256 = "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3"
DEFINITIONS = {
    "classification": "SYNTHETIC_COUNTEREXAMPLE / ENGINEERING_TEST",
    "coordinate_model": "analytic Cartesian working-metre fixture; no geographic source claim",
    "randomness": "none; every coordinate and time is an exact listed analytic input",
    "normal_right_angle": {"xy": [[0, 0], [10, 0], [20, 0], [20, 10], [20, 20]],
                           "known_noise_indices": [], "expected_D_removed": []},
    "legitimate_zigzag": {"xy": [[0, 0], [10, 0], [10, 10], [20, 10], [20, 20]],
                         "known_noise_indices": [], "expected_D_removed": [1, 2]},
    "injected_spike": {"xy": [[-20, 0], [-10, 0], [0, 30], [10, 0], [20, 0]],
                       "known_noise_indices": [2], "expected_D_removed": [1, 2],
                       "latent_clean_xy": [[-20, 0], [-10, 0], [0, 0], [10, 0], [20, 0]]},
    "zero_and_time_conflict": {"xy": [[0, 0], [0, 0], [5, 0], [5, 5], [10, 5]],
                               "timestamps": [0, 0, 0, 1, 2]},
    "time_gap": {"xy": [[0, 0], [10, 0], [20, 0], [30, 0], [40, 0]],
                 "timestamps": [0, 10, 100, 110, 120]},
    "hidden_distance_break": {"xy": [[0, 0], [401, 0], [399, 0]],
                              "analytic_property": "P tolerance 5 removes overshoot 2; final edge 399 hides original edge 401 > 400"},
    "finite_segment": {"xy": [[0, 0], [2, 1], [1, 0]],
                       "tolerance": 1.1, "finite_error": math.sqrt(2), "infinite_line_error": 1.0},
    "threshold_equality": {"xy": [[0, 0], [1, 1], [2, 0]], "exact_middle_error": 1.0,
                           "tolerances": [0, 1 - 1e-8, 1, 1 + 1e-8]},
    "own_clean_reference": {"xy": [[0, 0], [0, 1], [0, 2], [1, 3], [1, 4]],
                            "direction_thresholds": [35, 60], "dp": 0},
    "claim_boundary": "Known synthetic noise labels support only these authored examples; never real-data detection accuracy or population rates.",
}


def _fixture(name):
    definition = DEFINITIONS[name]
    points = definition["xy"]
    return {"record_id": "fixture:" + name, "indices": list(range(len(points))),
            "timestamps": list(definition.get("timestamps", range(len(points)))), "xy": deepcopy(points)}


def _parameters(**changes):
    return {**REFERENCE_PARAMETERS, "min_points": 2, "min_length": 0, **changes}


def _execute(raw, parameters, order, contract_hash, provenance):
    output = run_record(raw, parameters, order, contract_hash=contract_hash, provenance=provenance)
    receipt = review_record(output, raw, expected_parameters=parameters, expected_order=order,
                            contract_hash=contract_hash, trusted_provenance=provenance)
    if receipt["status"] != "VERIFIED":
        raise AssertionError({"record_id": raw["record_id"], "review": receipt})
    return {"output": output, "review": receipt}


def _D_removed(execution):
    return [row["original_index"] for row in execution["output"]["point_actions"] if row["action"] == "denoised"]


def _check(name, observed, expected):
    passed = (math.isclose(observed, expected, rel_tol=1e-12, abs_tol=1e-12)
              if isinstance(expected, float) else observed == expected)
    return {"name": name, "observed": observed, "expected": expected, "passed": passed}


def synthetic_suite(parent_contract_hash):
    fixture_contract = {"definitions": DEFINITIONS, "scope": "CONSTRUCTED_PLANAR_ONLY",
                        "approval": "ENGINEERING_TEST_ONLY", "g2_parent_contract_hash": parent_contract_hash}
    contract_hash = object_hash(fixture_contract)
    provenance = {"source_kind": "SYNTHETIC_COUNTEREXAMPLE", "fixture_contract_hash": contract_hash,
                  "g2_parent_contract_hash": parent_contract_hash, "claims_population_accuracy": False}
    cases = []

    turns = {}
    checks = []
    for name in ("normal_right_angle", "legitimate_zigzag", "injected_spike"):
        execution = _execute(_fixture(name), _parameters(dp=0), "S-D-P", contract_hash, provenance)
        removed = set(_D_removed(execution))
        truth = set(DEFINITIONS[name]["known_noise_indices"])
        execution["synthetic_detection_counts"] = {
            "known_noise_points": len(truth), "known_normal_points": len(_fixture(name)["indices"]) - len(truth),
            "true_positive": len(removed & truth), "false_positive": len(removed - truth),
            "false_negative": len(truth - removed), "only_authored_fixture_truth": True}
        checks.append(_check(name + ": direction deletion identities", sorted(removed),
                             DEFINITIONS[name]["expected_D_removed"]))
        turns[name] = execution
    cases.append({"case_id": "CE01_DIRECTION_AMBIGUITY", "family": "normal sharp turn versus spike",
                  "executions": turns, "known_answer_checks": checks,
                  "before_after": {name: {"raw_points": execution["output"]["metrics"]["n_input"],
                                                  "final_points": execution["output"]["metrics"]["n_final"],
                                                  "D_deleted": _D_removed(execution),
                                                  "synthetic_detection": execution["synthetic_detection_counts"]}
                                   for name, execution in turns.items()},
                  "interpretation": "A single right-angle turn is retained here, but legitimate zigzag vertices satisfy the same deletion predicate. In the authored spike example the method deletes one normal neighbor together with the injected spike. Geometry alone is not a noise truth label.",
                  "action": "Retain approved predicate as the teaching reference; do not claim real-data detection accuracy or alter the method from this example alone."})

    name = "zero_and_time_conflict"
    zero = _execute(_fixture(name), _parameters(dp=0), "S-D-P", contract_hash, provenance)
    raw_reading = zero["output"]["metrics"]["stage_readings"]["raw"]
    rows = next(stage for stage in zero["output"]["stages"] if stage["name"] == "D")["operations"][0]["decisions"]
    checks = [_check("zero-dt edges remain unavailable", raw_reading["speed_unavailable_reasons"].get("ZERO_TIME_DIFFERENCE"), 2),
              _check("same-time different-position count", raw_reading["same_time_different_position_edges"], 1),
              _check("zero-displacement direction unavailable", raw_reading["direction_unavailable_reasons"].get("ZERO_DISPLACEMENT"), 1),
              _check("point 1 undefined window retained", rows[1]["reason"], "UNCOMPUTABLE_DIRECTION_IN_WINDOW")]
    cases.append({"case_id": "CE02_UNDEFINED_IS_NOT_ZERO", "family": "zero displacement and same time different position",
                  "executions": {name: zero}, "known_answer_checks": checks,
                  "before_after": zero["output"]["metrics"]["stage_readings"],
                  "interpretation": "Zero displacement has undefined direction; zero dt has undefined speed, including the moving same-time edge. These are explicit reasons, not fabricated zero velocities or a physical speed limit.",
                  "action": "Keep undefined direction windows according to the approved one-pass schedule and report their denominator."})

    order_executions, checks = {}, []
    for name in ("time_gap", "hidden_distance_break"):
        raw = _fixture(name)
        for order in ("S-D-P", "P-S-D", "D-S-P"):
            order_executions[name + ":" + order] = _execute(raw, _parameters(), order, contract_hash, provenance)
    time_ref = order_executions["time_gap:S-D-P"]["output"]["metrics"]
    time_p = order_executions["time_gap:P-S-D"]["output"]["metrics"]
    distance_p = order_executions["hidden_distance_break:P-S-D"]["output"]["metrics"]
    checks.extend([_check("time reference keeps record coverage", time_ref["record_covered"], True),
                   _check("P-before-S time fixture loses all output", time_p["no_output"], True),
                   _check("not every raw point was filtered by S", time_p["all_filtered"], False),
                   _check("distance breakpoint hidden by P", distance_p["raw_break_crossings"], 1),
                   _check("P removed triggering point", distance_p["p_removed_raw_break_trigger_indices"], [1])])
    cases.append({"case_id": "CE03_ORDER_AND_BREAK_INFORMATION", "family": "time/distance break and P removes trigger",
                  "executions": order_executions, "known_answer_checks": checks,
                  "before_after": {key: {name: execution["output"]["metrics"][name]
                                           for name in ("n_input", "n_final", "raw_break_count", "raw_break_crossings",
                                                        "common_coverage", "all_filtered", "no_output", "dp_saving")}
                                   for key, execution in order_executions.items()},
                  "interpretation": "P preserves its own geometric tolerance but can remove breakpoint trigger information. On the time fixture later S filters the two remaining singleton segments; on the distance fixture a 399-metre final edge crosses the original 401-metre break.",
                  "action": "Keep actual unsafe order results as constraint-rejected experiments; no hidden segmentation or repair is added."})

    finite_raw = _fixture("finite_segment")
    finite = _execute(finite_raw, _parameters(dp=1.1), "S-D-P", contract_hash, provenance)
    wrong = {"record_id": finite_raw["record_id"], "indices": [0, 2], "timestamps": [0, 2],
             "xy": [finite_raw["xy"][0], finite_raw["xy"][2]]}
    wrong_check = verify_simplification(finite_raw, wrong, 1.1)
    threshold_executions = {}
    for tolerance in DEFINITIONS["threshold_equality"]["tolerances"]:
        key = "dp=" + str(tolerance)
        threshold_executions[key] = _execute(_fixture("threshold_equality"), _parameters(dp=tolerance),
                                              "S-D-P", contract_hash, provenance)
    checks = [_check("finite distance rejects infinite-line shortcut", wrong_check["status"], "REJECTED"),
              _check("finite distance is sqrt(2)", wrong_check["metrics"]["max_error"]["value"], math.sqrt(2)),
              _check("correct finite DP retains middle point", finite["output"]["metrics"]["n_final"], 3),
              _check("zero tolerance preserves all points", threshold_executions["dp=0"]["output"]["metrics"]["n_final"], 3),
              _check("below equality retains point", threshold_executions["dp=0.99999999"]["output"]["metrics"]["n_final"], 3),
              _check("equality does not recurse", threshold_executions["dp=1"]["output"]["metrics"]["n_final"], 2)]
    cases.append({"case_id": "CE04_FINITE_DISTANCE_AND_EQUALITY", "family": "finite segment versus infinite line and threshold equality",
                  "executions": {"finite": finite, **threshold_executions}, "known_answer_checks": checks,
                  "intentionally_wrong_output": {"classification": "ENGINEERING_TEST_FAULT_INJECTION",
                                                 "candidate": wrong, "independent_rejection": wrong_check},
                  "before_after": {key: {"n_input": execution["output"]["metrics"]["n_input"],
                                          "n_final": execution["output"]["metrics"]["n_final"],
                                          "dp_error": execution["output"]["metrics"]["dp_max_error"]}
                                   for key, execution in {"finite": finite, **threshold_executions}.items()},
                  "interpretation": "The middle point projects beyond the finite endpoint, so its finite distance is sqrt(2), not the infinite-line distance 1. A separate exact-height example verifies strict recursion and dp=0 identity.",
                  "action": "Reject the constructed infinite-line shortcut. Audit tolerance remains separate from the algorithm threshold."})

    raw = _fixture("threshold_equality")
    retained = _execute(raw, _parameters(dp=1), "S-D-P", contract_hash, provenance)
    removed = _execute(raw, dict(REFERENCE_PARAMETERS), "S-D-P", contract_hash, provenance)
    no_output = removed["output"]["metrics"]
    cases.append({"case_id": "CE05_EMPTY_OUTPUT_IS_NOT_SUCCESS", "family": "delete-all scoring loophole",
                  "executions": {"covered": retained, "all_filtered": removed},
                  "known_answer_checks": [_check("all raw points remain denominator", no_output["common_raw_points"], 3),
                                          _check("empty output coverage", no_output["common_coverage"], 0.0),
                                          _check("empty error is null", no_output["common_max_error"], None),
                                          _check("empty DP saving is null", no_output["dp_saving"], None)],
                  "before_after": {"covered": retained["output"]["metrics"], "all_filtered": no_output},
                  "interpretation": "An empty output contains no observed anomaly but also no covered raw points. Error and DP saving are unavailable, not perfect zeros; complete input membership remains visible.",
                  "action": "Use coverage guards and null+reason rather than rewarding absence of output."})

    raw = _fixture("own_clean_reference")
    own_clean = {"direction=" + str(threshold): _execute(raw, _parameters(direction=threshold, dp=0),
                                                         "S-D-P", contract_hash, provenance)
                 for threshold in (35, 60)}
    a = own_clean["direction=35"]["output"]["metrics"]
    b = own_clean["direction=60"]["output"]["metrics"]
    checks = [_check("both own-P errors are zero", [a["dp_max_error"], b["dp_max_error"]], [0.0, 0.0]),
              _check("fixed-raw errors distinguish the methods", a["common_max_error"] > b["common_max_error"], True),
              _check("candidate clean deletion retains coverage denominator", a["common_raw_points"], 5)]
    cases.append({"case_id": "CE06_OWN_CLEAN_IS_NOT_COMMON_TRUTH", "family": "different clean references cannot certify overall improvement",
                  "executions": own_clean, "known_answer_checks": checks,
                  "before_after": {key: {"dp_error": execution["output"]["metrics"]["dp_max_error"],
                                          "common_raw_error": execution["output"]["metrics"]["common_max_error"],
                                          "common_raw_coverage": execution["output"]["metrics"]["common_coverage"],
                                          "n_direction_removed": execution["output"]["metrics"]["n_direction_removed"]}
                                   for key, execution in own_clean.items()},
                  "interpretation": "Both P stages copy their own inputs exactly and report error zero; the direction=35 path has already removed a point. Its common raw-reference error is positive while direction=60 remains zero. Separate DP certificates therefore cannot establish cross-method quality.",
                  "action": "Compare the pre-fixed raw reference and covered point identities; keep DP guarantees as stage-local facts."})
    failed = [{"case_id": case["case_id"], **check} for case in cases
              for check in case["known_answer_checks"] if not check["passed"]]
    if failed:
        raise AssertionError({"counterexample_known_answer_failures": failed})
    return {"classification": "SYNTHETIC_COUNTEREXAMPLE", "fixture_contract": fixture_contract,
            "fixture_contract_hash": contract_hash, "cases": cases,
            "known_answer_check_count": sum(len(case["known_answer_checks"]) for case in cases),
            "status": "ENGINEERING_VERIFIED", "real_data_accuracy_claim": False}


def exposed_pilot_cases(parent_contract_hash):
    if digest(DATA) != RAW_SHA256:
        raise ValueError("RAW_HASH_MISMATCH")
    raw = read_json(DATA)
    provenance = {"source_kind": "CURRENT_RUN_CONDITIONAL_ANALYSIS", "raw_sha256": RAW_SHA256,
                  "partition": "PILOT_REGRESSION", "exposure": "KNOWN_EXPOSED",
                  "purpose": "G1 regression and case explanation; not new holdout discovery"}
    executions = {rid: _execute(conditional_adapter(rid, raw[rid]), REFERENCE_PARAMETERS,
                                "S-D-P", parent_contract_hash, provenance) for rid in PILOT_IDS}
    filtering = []
    for rid in ("0", "1", "2"):
        output = executions[rid]["output"]
        s_stage = next(stage for stage in output["stages"] if stage["name"] == "S")
        parts = [part for op in s_stage["operations"] for part in op["segments"]]
        filtering.append({"record_id": rid, "raw_points": len(output["source_record"]["indices"]),
                          "final_points": output["metrics"]["n_final"], "terminal_status": output["terminal_status"],
                          "segments": [{"indices": part["indices"], "n_points": len(part["indices"]),
                                        "within_segment_length_working_m": part["features"]["length"],
                                        "min_points": 5, "min_length": 65,
                                        "filter_reasons": part["filter_reasons"]} for part in parts],
                          "interpretation": "Reasons are evaluated independently on each S-created segment; cut edges do not contribute to its cumulative length."})
    direction_cases = []
    for rid in PILOT_IDS:
        stage = next(stage for stage in executions[rid]["output"]["stages"] if stage["name"] == "D")
        for before, after, operation in zip(stage["input"], stage["output"], stage["operations"]):
            if not operation["deleted_indices"]:
                continue
            index = operation["deleted_indices"][0]
            position = before["indices"].index(index)
            window = before["indices"][max(0, position - 1):position + 3]
            after_edges = [edge for edge in after["features"]["edges"] if edge["from_index"] < index < edge["to_index"]]
            direction_cases.append({"record_id": rid, "selection": "first deleted original index in each exposed pilot with deletion",
                                    "deleted_index": index, "original_current_window": window,
                                    "decision": next(row for row in operation["decisions"] if row["index"] == index),
                                    "all_simultaneous_deleted_indices": operation["deleted_indices"],
                                    "post_delete_bracketing_edges_recomputed": after_edges,
                                    "interpretation": "The window decides deletion once on D input. New adjacency is recomputed after simultaneous deletion and is not a second denoising pass."})
            break
    distances = []
    for rid, execution in executions.items():
        p_stage = next(stage for stage in execution["output"]["stages"] if stage["name"] == "P")
        for before, after, op in zip(p_stage["input"], p_stage["output"], p_stage["operations"]):
            for row in op["runtime_dp_check"]["error_by_original_index"]:
                if row["error"] > 0:
                    distances.append((abs(5 - row["error"]), rid, row["index"], before, after, row["error"]))
    nearest = min(distances, key=lambda item: (item[0], int(item[1]), item[2]))
    _, rid, index, before, after, error = nearest
    edge = next((a, b) for a, b in zip(after["indices"], after["indices"][1:]) if a < index < b)
    sweeps = {str(tolerance): _execute(conditional_adapter(rid, raw[rid]), {**REFERENCE_PARAMETERS, "dp": tolerance},
                                      "S-D-P", parent_contract_hash, provenance) for tolerance in (2, 5, 10)}
    nearby = {"selection": "smallest positive |5 - actual P interval residual| among seven exposed reference pilots",
              "record_id": rid, "original_index": index, "reference_bracketing_indices": list(edge),
              "actual_error_working_m": error, "distance_below_5_working_m": 5 - error,
              "same_upstream_threshold_runs": sweeps,
              "before_after": {threshold: {key: execution["output"]["metrics"][key]
                                             for key in ("n_dp_input", "n_dp_output", "dp_saving", "dp_max_error", "common_max_error")}
                               for threshold, execution in sweeps.items()},
              "interpretation": "The point error belongs to its actual retained original-index interval. Changing dp can change endpoints and all interval errors; this exposed case is not evidence for selecting a holdout threshold."}
    return {"classification": "CURRENT_RUN_CONDITIONAL_ANALYSIS", "partition": "PILOT_REGRESSION",
            "exposure": "KNOWN_EXPOSED", "raw_sha256": RAW_SHA256, "record_ids": PILOT_IDS,
            "executions": executions, "all_filtered_records_0_1_2": filtering,
            "direction_adjacency_cases": direction_cases, "near_threshold_case": nearby,
            "source_crs": "UNVERIFIED", "fresh_holdout_claim": False,
            "status": "ENGINEERING_VERIFIED"}


def run(output_directory, *, include_pilot=True, run_id="g2-counterexamples"):
    output_directory = Path(output_directory)
    if output_directory.exists() and any(output_directory.iterdir()):
        raise ValueError("OUTPUT_DIRECTORY_NOT_EMPTY: preserve previous counterexample evidence")
    started, timer = now(), perf_counter()
    contract_path = ROOT / "task1/config/goal2/contract.json"
    parent_contract_hash = digest(contract_path)
    source_paths = [Path(__file__), ROOT / "task1/workflow/g2_pipeline.py", ROOT / "task1/workflow/g2_metrics.py",
                    ROOT / "task1/workflow/geometry.py", ROOT / "task1/workflow/evaluation.py",
                    ROOT / "task1/workflow/coordinates.py", ROOT / "task1/workflow/io.py"]
    source_hashes = {relative(path): digest(path) for path in source_paths}
    synthetic = synthetic_suite(parent_contract_hash)
    pilot = exposed_pilot_cases(parent_contract_hash) if include_pilot else None
    output_directory.mkdir(parents=True, exist_ok=True)
    write_json(output_directory / "synthetic_cases.json", synthetic)
    if pilot is not None:
        write_json(output_directory / "exposed_pilot_cases.json", pilot)
    notes = ["# Goal 2 反例与已暴露案例", "",
             "构造反例具有解析定义和已知答案；其误删计数只适用于这些人工定义的坐标，不能外推真实轨迹准确率。", "",
             "所有条目实际执行 S/D/P，并用候选之外的可信输入审核。没有新模型调用；下面是风险检验，不声称模型犯过这些错误。", ""]
    for case in synthetic["cases"]:
        notes.extend(["## " + case["case_id"], "", case["interpretation"], "", case["action"], ""])
    if pilot:
        notes.extend(["## 七条已暴露 pilot", "", "记录 0、1、2 的真实过滤分段与理由：", ""])
        for row in pilot["all_filtered_records_0_1_2"]:
            reasons = "; ".join(
                f"{part['n_points']} 点、段内 {part['within_segment_length_working_m']:.9f} 工作米、原因 {','.join(part['filter_reasons'])}"
                for part in row["segments"])
            notes.append(f"- 记录 {row['record_id']}：{row['raw_points']} 原始点，{row['final_points']} 最终点；{reasons}。")
        near = pilot["near_threshold_case"]
        notes.extend(["", f"按预登记距离规则选中的近阈值点为记录 {near['record_id']} / 原始索引 {near['original_index']}，"
                      f"参考索引区间 {near['reference_bracketing_indices']}，误差 {near['actual_error_working_m']:.12f} 工作米。",
                      "方向案例保留一次标记的输入窗口和同时删除后的新邻接边。DP=2/5/10 的局部重算共享 S/D，"
                      "仅解释已有 pilot；不作为未观察的评测发现或最终参数选择。", ""])
    notes.extend(["## 来源与边界", "", "教师方向谓词和有限线段定义的来源沿用冻结合同的原件定位。"
                  "本文件不引用不存在的模型原话、用户质疑、Human Approval 或 Evidence Lock。", ""])
    (output_directory / "CASE_ANALYSIS.md").write_text("\n".join(notes), encoding="utf-8")
    artifacts = {path.name: digest(path) for path in sorted(output_directory.iterdir()) if path.is_file()}
    synthetic_count = sum(len(case["executions"]) for case in synthetic["cases"])
    manifest = {"goal_id": GOAL_ID, "experiment_id": "G2-R07-COUNTEREXAMPLES", "run_id": run_id,
                "classification": "ENGINEERING_COUNTEREXAMPLE_RUN", "started_at": started, "ended_at": now(),
                "elapsed_seconds": perf_counter() - timer, "actual_command": list(sys.argv),
                "code_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_tree_hash": object_hash(source_hashes), "source_files": source_hashes,
                "g2_parent_contract_hash": parent_contract_hash, "fixture_contract_hash": synthetic["fixture_contract_hash"],
                "raw_sha256": RAW_SHA256 if pilot else None, "pilot_scope": PILOT_IDS if pilot else [],
                "synthetic_pipeline_executions": synthetic_count, "pilot_pipeline_executions": 10 if pilot else 0,
                "experiment_model_dispatches": 0, "known_answer_checks": synthetic["known_answer_check_count"],
                "status": "ENGINEERING_VERIFIED", "artifacts": artifacts,
                "limitations": ["synthetic truth applies only to authored fixtures", "pilot cases are already exposed",
                                "conditional work-plane results do not establish source datum", "no final method selected"]}
    write_json(output_directory / "manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", default="g2-counterexamples")
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args()
    manifest = run(args.output, include_pilot=not args.synthetic_only, run_id=args.run_id)
    print({key: manifest[key] for key in ("status", "synthetic_pipeline_executions", "pilot_pipeline_executions",
                                         "known_answer_checks", "experiment_model_dispatches", "elapsed_seconds")})


if __name__ == "__main__":
    main()
