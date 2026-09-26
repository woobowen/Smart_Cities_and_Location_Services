"""C definition review; does not run or select candidate outcomes."""
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def key(parameters):
    return tuple((name, float(parameters[name])) for name in sorted(parameters))


def main():
    contract_path = "task1/config/goal2/contract.json"
    matrix_path = "task1/config/goal2/experiment_matrix.json"
    document_path = "task1/docs/goal2/CONTRACT.md"
    requirements_path = "task1/evidence/goal2/requirements.json"
    contract, matrix, requirements = read(contract_path), read(matrix_path), read(requirements_path)
    checks = []
    def check(name, condition, detail=None):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
    expected_grids = {"dt": [15, 20, 30, 45, 60], "distance": [95, 200, 400, 600, 800],
                      "min_points": [2, 3, 5, 7, 10], "min_length": [0, 32.5, 65, 97.5, 130],
                      "direction": [15, 25, 35, 45, 60], "dp": [0, .5, 1, 2, 5, 10, 20]}
    reference = {"dt": 30, "distance": 400, "min_points": 5, "min_length": 65, "direction": 35, "dp": 5}
    check("user_parameter_grids_exact", contract["parameter_grids"] == expected_grids)
    check("reference_parameters_exact", contract["reference_parameters"] == reference)
    expected = set()
    for name, values in expected_grids.items():
        expected.update(key({**reference, name: value}) for value in values)
    for first, second in (("dt", "distance"), ("min_points", "min_length")):
        expected.update(key({**reference, first: a, second: b})
                        for a, b in itertools.product(expected_grids[first], expected_grids[second]))
    rows = matrix["parameter_configurations"]
    by_id = {row["config_id"]: row for row in rows}
    observed = {key(row["parameters"]) for row in rows}
    check("all_59_unique_configs_exact", expected == observed and len(expected) == len(rows) == len(by_id) == 59)
    for experiment in matrix["experiments"]:
        if experiment["experiment_id"].startswith("G2-PARAM"):
            fields = experiment["changes_only"]
            if len(fields) == 1:
                expected_set = {key({**reference, fields[0]: value}) for value in expected_grids[fields[0]]}
            else:
                expected_set = {key({**reference, fields[0]: a, fields[1]: b})
                                for a, b in itertools.product(expected_grids[fields[0]], expected_grids[fields[1]])}
            actual_set = {key(by_id[identifier]["parameters"]) for identifier in experiment["config_ids"]}
            check("grid_membership:" + experiment["experiment_id"], actual_set == expected_set)
    expected_representatives = {key({**reference, name: value}) for name, grid in expected_grids.items()
                                for value in (grid[0], reference[name], grid[-1])}
    check("fixed_13_eval_representatives", expected_representatives ==
          {key(by_id[identifier]["parameters"]) for identifier in matrix["fixed_eval_representative_config_ids"]}
          and len(expected_representatives) == 13)
    check("six_exact_orders", set(contract["orders"]) == {"S-D-P", "S-P-D", "D-S-P", "D-P-S", "P-S-D", "P-D-S"})
    check("no_preS_segmentation", contract["stage_rules"]["before_S"] == "raw record boundaries only; no implicit time/distance segmentation")
    check("order_feasibility_preregistered", bool(contract["order_feasibility"]["safety_guards_per_record"])
          and contract["order_feasibility"]["violation_status"] == "REJECTED_BY_CONSTRAINT")
    sequence = contract["search"]["sequence"]
    check("search_20_unique_configs_reference_first", len(sequence) == len({key(x["parameters"]) for x in sequence}) == 20
          and sequence[0]["parameters"] == reference)
    check("search_sequence_in_domain", all(all(v in expected_grids[k] for k, v in row["parameters"].items()) for row in sequence))
    modes = contract["modes"]
    check("mode_sizes_and_round_budgets", modes["development_records"] == modes["evaluation_records"] == 24
          and modes["development_episodes"] == 1 and modes["evaluation_episodes"] == 3
          and modes["batch_size_max"] == 8 and modes["max_decision_rounds"] == 3
          and modes["search_round_cumulative_budgets"] == [8, 14, 20])
    check("strict_zero_search_model", modes["search_only"]["experiment_model_dispatches"] == 0
          and modes["search_only"]["callable_provider_instantiated"] is False and modes["search_only"]["sentinel_required"] is True)
    check("llmonly_no_feedback", modes["llm_only"]["max_locked_proposals"] == 1 and
          all(modes["llm_only"][name] is False for name in ("feedback", "search", "memory")))
    check("memory_demo_60_readonly", contract["memory"]["source_records"] == 60
          and contract["memory"]["source_partition"] == "DEMO_MEMORY" and contract["memory"]["eval_read_only"] is True
          and contract["memory"]["snapshot_frozen_before_eval"] is True)
    split = contract["split"]
    check("record_partition_sizes", split["seed"] == 42 and split["partition_sizes"] ==
          {"PILOT_REGRESSION": 7, "DEMO_MEMORY": 60, "DEVELOPMENT": 120, "G2_EVAL": 120, "G3_RESERVED": "all remainder"})
    old_model = read("task1/config/conditional_planar.json")["analysis_model"]
    check("same_coordinate_mathematics", all(contract["model"][name] == old_model[name] for name in
          ("semi_major_m", "inverse_flattening", "assumed_height_m", "origin_lon_degrees", "origin_lat_degrees")))
    check("expanded_guard_separate_from_precision", contract["model"]["domain_max_radius_m"] == 200000
          and contract["model"]["guard_is_accuracy_guarantee"] is False and old_model["domain_max_radius_m"] == 40000)
    common = contract["common_reference"]
    check("common_raw_independent_reference", common["candidate_dependent"] is False and common["short_segment_filter"] is False
          and common["coverage_identity_set_required"] is True and common["crossing_limit"] == 0 and common["uncovered_value"] is None)
    check("no_own_clean_quality_claim", contract["selection"]["allow_quality_accepted"] is False
          and contract["selection"]["CP"]["common_dp_error_budget_m"] == 5
          and contract["selection"]["regret"]["scalar_objective"] is None)
    check("three_required_singles_no_combinations", set(contract["required_single_candidates"]) == {"C-S", "C-D", "C-P"}
          and "joint_CS_CD_CP_enhancement" in contract["forbidden"])
    check("source_snapshots_match", all(sha(item["path"]) == item["sha256"] for item in contract["source_snapshot"]))
    check("actual_prompt_bound", sha(contract["authority"]["path"]) == contract["authority"]["sha256"]
          and contract["authority"]["internal_A_C_is_human_approval"] is False)
    check("single_R01_R10_registry", [row["id"] for row in requirements["requirements"]] == [f"R{i:02}" for i in range(1, 11)])
    check("all_A01_A17_pending_not_fabricated", [row["id"] for row in requirements["acceptance_items"]] == [f"A{i:02}" for i in range(1, 18)]
          and all(row["status"] == "PENDING" for row in requirements["acceptance_items"]))
    check("default_recompute_zero_models", contract["notebooks"]["default_new_model_dispatches"] == 0)
    check("internal_before_publication", contract["publication"]["normal_push_before_internal_acceptance"] is False
          and contract["publication"]["force_push"] is False)
    target_paths = [contract_path, matrix_path, document_path]
    receipt = {"role_context": "/root/c_contract", "status": "VERIFIED" if all(c["passed"] for c in checks) else "REJECTED",
               "at_utc": datetime.now(timezone.utc).isoformat(), "classification": "INDEPENDENT_C_DEFINITION_REVIEW_NOT_HUMAN_APPROVAL",
               "targets": [{"path": path, "sha256": sha(path)} for path in target_paths],
               "source_hashes": {path: sha(path) for path in target_paths},
               "requirements_reference_at_preparation": {"path": requirements_path, "sha256": sha(requirements_path)},
               "checked_components": ["teacher_requirements", "comparison_definitions", "selection_rules", "data_partition_rules",
                                      "mode_budgets", "scope_boundaries", "source_bindings", "unique_exact_grid", "same_coordinate_model"],
               "unchecked_components": ["actual_split_ids", "production_split_recompute", "full_G2_coordinate_sensitivity",
                                        "actual_parameter_experiments", "real_mode_episodes", "memory_consumption", "final_acceptance"],
               "checks": checks, "human_approval": False,
               "manual_review": ["Teacher original PPT 18/20/22/24/26/37/42 and both starter notebooks agree with limited G2 scope.",
                                 "G1 40km guard stays frozen; explicit G2 200km guard is an input-domain extension of unchanged mathematics, not accuracy proof.",
                                 "Baseline covered point identities prevent difficulty substitution; missing output is not zero error.",
                                 "P immediate guarantee and final geometry after later D/S are separate.",
                                 "Order safety versus geometric tradeoff is fixed before G2 development results.",
                                 "Memory retrieval and cited consumption are observables, not causal quality-gain proof.",
                                 "No G3 composition/final processing/report or human-understanding pass is authorized by this receipt."],
               "open_contract_issues": [], "new_model_calls": 0}
    (OUT / "contract_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "checks": len(checks), "failed": [c for c in checks if not c["passed"]],
                      "targets": receipt["targets"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
