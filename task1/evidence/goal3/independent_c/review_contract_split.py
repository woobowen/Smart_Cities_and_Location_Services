"""Independent C checker: original JSON, PROJ descriptions, and split reconstruction.

Imports no task1 production module and executes no cleaning algorithm. Future
FINAL_CONFIRM raw identities/descriptors are checked, never method effects.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pyproj

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def canonical_hash(value):
    value = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(value.encode()).hexdigest()


def rank(group, salt):
    return hashlib.sha256(f"42|{salt}|{group}".encode()).hexdigest()


def reconstruct_selection(groups, strata, target, salt):
    buckets = defaultdict(list)
    for group, ids in groups.items():
        assert len({strata[rid] for rid in ids}) == 1
        buckets[strata[ids[0]]].append(group)
    names = sorted(buckets)
    ranked_buckets = {name: sorted(buckets[name], key=lambda x: (rank(x, salt), x)) for name in names}
    quota = {name: target // len(names) + int(i < target % len(names)) for i, name in enumerate(names)}
    selected, realized = [], Counter()
    cursor = dict.fromkeys(names, 0)
    for name in names:
        while cursor[name] < len(ranked_buckets[name]) and realized[name] < quota[name]:
            group = ranked_buckets[name][cursor[name]]
            selected += groups[group]
            realized[name] += len(groups[group])
            cursor[name] += 1
    while len(selected) < target:
        before = len(selected)
        for name in names:
            if cursor[name] < len(ranked_buckets[name]):
                group = ranked_buckets[name][cursor[name]]
                selected += groups[group]
                realized[name] += len(groups[group])
                cursor[name] += 1
            if len(selected) >= target:
                break
        assert len(selected) > before
    return selected, quota, dict(realized)


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else ""
    paths = {"contract": "task1/config/goal3/contract.json",
             "split": "task1/evidence/goal3/split_manifest.json",
             "generator": "task1/goal3/data.py",
             "raw": "task1/作业/作业/traj_dict.json",
             "g2_contract": "task1/config/goal2/contract.json",
             "g2_split": "task1/evidence/goal2/data/split_manifest.json",
             "g2_diagnostics": "task1/evidence/goal2/data/raw_diagnostics.json",
             "candidate_plan": "task1/evidence/goal3/a_candidate_plan.json"}
    hashes = {key: sha(ROOT / path) for key, path in paths.items()}
    contract, split = load(paths["contract"]), load(paths["split"])
    old, old_split, cards = load(paths["g2_contract"]), load(paths["g2_split"]), load(paths["g2_diagnostics"])
    raw = load(paths["raw"])
    errors, checked = [], []

    def check(name, condition, detail=None):
        checked.append(name)
        if not condition:
            errors.append({"check": name, "detail": detail})

    check("raw_hash", hashes["raw"] == "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3")
    check("raw_counts", len(raw) == 11386 and sum(len(r[0]) for r in raw.values()) == 1173410)
    check("target_split_binding", contract["split_sha256"] == hashes["split"])
    check("generator_binding", split["source_sha256"] == hashes["generator"])
    check("G2_contract_binding", contract["inherited_contract"]["sha256"] == hashes["g2_contract"])
    check("G2_split_binding", split["g2_split_sha256"] == hashes["g2_split"])
    check("G2_diagnostics_binding", split["g2_diagnostics_sha256"] == hashes["g2_diagnostics"] == old_split["diagnostics_sha256"])
    check("authority_binding", sha(ROOT / contract["authority"]["path"]) == contract["authority"]["sha256"])
    check("memory_binding", sha(ROOT / contract["mode"]["memory_path"]) == contract["mode"]["memory_sha256"])
    for key in ("model", "units", "source_crs", "direction_method", "stage_rules", "parameter_grids",
                "numeric_audit", "common_reference", "metrics"):
        check("inherited_definition:" + key, contract[key] == old[key])
    expected_r0 = {"dt": 30, "distance": 400, "min_points": 5, "min_length": 65, "direction": 35, "dp": 5}
    check("R0_exact", contract["references"]["R0"] == expected_r0)
    check("S0_exact", contract["references"]["S0"] == {**expected_r0, "min_points": 2, "min_length": 0})
    check("candidate_budgets", all(contract["budget"][k] == v for k, v in {
        "new_single_definitions_max": 8, "combination_definitions_max": 12,
        "enhancement_depth_max": 3, "selection_shortlist_max": 4, "final_comparison_max": 4}.items()))
    check("SD_guards_exact", contract["selection"]["SD_guards"] == old["selection"]["CS_CD"]["per_record_guards"])
    check("P_budget_and_parent", contract["selection"]["P_shared_actual_error_budget_work_m"] == 5
          and contract["selection"]["P_same_upstream_dp5_parent_required"]
          and contract["selection"]["P_complete_input_equality_required"])
    check("fixed_and_incumbent_protection", contract["selection"]["fixed_and_incumbent_protection"]
          and contract["selection"]["all_records_must_pass"])
    check("no_weighted_score", contract["selection"]["weighted_quality_score"] is None)
    check("confirmation_gate", contract["release_gate"]["on_no_support_or_tradeoff"] == "R0"
          and not contract["release_gate"]["retune_on_confirmation"]
          and contract["release_gate"]["all_fixed_guards_pass"]
          and contract["release_gate"]["strict_predeclared_gain_required"])
    check("record_model_default", contract["mode"]["new_record_level_model_dispatches"] == 0
          and not contract["mode"]["new_mode_gain_claim"])

    groups = defaultdict(list)
    membership = {}
    for rid, record in raw.items():
        membership[rid] = canonical_hash(record)
        groups[membership[rid]].append(rid)
    check("group_membership_recomputed", split["group_for_record"] == membership)
    check("group_count", split["group_count"] == len(groups))
    check("duplicates_recomputed", split["duplicate_groups"] == [ids for ids in groups.values() if len(ids) > 1])
    check("diagnostic_raw_identities", set(cards) == set(raw) and all(
        cards[rid]["record_content_sha256"] == membership[rid] for rid in raw))

    model = contract["model"]
    transform = pyproj.Transformer.from_pipeline(
        '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    spans, flags = {}, {}
    maximum_span_difference = 0.0
    for rid, (times, angular) in raw.items():
        a = np.asarray(angular, dtype=float)
        x, y, _ = transform.transform(a[:, 0], a[:, 1], np.zeros(len(a)))
        spans[rid] = float(np.hypot(np.ptp(x), np.ptp(y)))
        delta = np.diff(times)
        flags[rid] = (bool(np.any((delta <= 0) | (delta > 30))),
                      any(left == right for left, right in zip(angular, angular[1:])))
        maximum_span_difference = max(maximum_span_difference, abs(spans[rid] - cards[rid]["span_work_m"]))
    quantiles = np.quantile(list(spans.values()), [1 / 3, 2 / 3], method="linear")
    strata = {rid: ("LOW" if span <= quantiles[0] else "MID" if span <= quantiles[1] else "HIGH")
              + f"_T{int(flags[rid][0])}_D{int(flags[rid][1])}" for rid, span in spans.items()}
    check("independent_raw_span_PROJ", maximum_span_difference <= 1e-6, maximum_span_difference)
    check("independent_raw_tertiles", np.max(np.abs(quantiles - old_split["quantiles"])) <= 1e-6)
    check("independent_descriptive_strata", all(cards[rid]["stratum"] == strata[rid] for rid in raw))

    reserved = set(old_split["splits"]["G3_RESERVED"])
    available = {g: ids for g, ids in groups.items() if set(ids) <= reserved}
    selected, quotas, realized = reconstruct_selection(available, strata, 240, "SC_LAB1_G3_SELECTION_V1")
    remaining_groups = {g: ids for g, ids in available.items() if not set(ids) & set(selected)}
    final = []
    for group in sorted(remaining_groups, key=lambda g: (rank(g, "SC_LAB1_FINAL_CONFIRM_V1"), g)):
        final.extend(remaining_groups[group])
        if len(final) >= 600:
            break
    remainder = sorted(reserved - set(selected) - set(final), key=lambda rid: (rank(membership[rid], "PRODUCTION"), rid))
    expected_parts = {
        "PILOT_REGRESSION": old_split["splits"]["PILOT_REGRESSION"],
        "DEMO_MEMORY": old_split["splits"]["DEMO_MEMORY"],
        "G3_DEVELOPMENT": old_split["splits"]["DEVELOPMENT"] + old_split["splits"]["G2_EVAL"],
        "G3_SELECTION": selected, "FINAL_CONFIRM": final, "PRODUCTION_REMAINDER": remainder}
    check("exact_partition_ordered_reconstruction", split["partitions"] == expected_parts)
    all_ids = sum(split["partitions"].values(), [])
    check("exact_complete_unique_scope", len(all_ids) == len(set(all_ids)) == len(raw) and set(all_ids) == set(raw))
    part_of = {rid: name for name, ids in split["partitions"].items() for rid in ids}
    check("atomic_groups", all(len({part_of[rid] for rid in ids}) == 1 for ids in groups.values()))
    check("selection_allocation", split["allocation"]["G3_SELECTION"]["quota"] == quotas
          and split["allocation"]["G3_SELECTION"]["realized"] == realized)
    check("final_equal_group_pool", split["allocation"]["FINAL_CONFIRM"]["quota"] == {"ALL": 600}
          and split["allocation"]["FINAL_CONFIRM"]["actual_records"] == len(final))
    distributions = {name: dict(Counter(strata[rid] for rid in ids)) for name, ids in expected_parts.items()}
    check("stratum_distributions", split["stratum_distributions"] == distributions)
    check("exposure_honesty", "KNOWN_EXPOSED" in split["development_exposure"]
          and "NO_DOCUMENTED_METHOD_EXPOSURE" in split["reserved_exposure"])

    # These are checks of required pre-experiment bounds, not implementation of
    # the eventual task controller or strategy.
    limits = contract.get("exploration_constraints", {})
    check("explicit_exploration_constraints", limits.get("raw_diagnostic_rule_max") == 1
          and limits.get("raw_diagnostic_groups_max") == 3
          and limits.get("conservative_direction_protection_max") == 1
          and limits.get("group_boundaries_and_parameters_fixed_on") == "G3_DEVELOPMENT only"
          and bool(limits.get("unknown_group_fallback"))
          and "record_id answer routing" in limits.get("forbidden", []))
    check("explicit_final_information_boundary", set(limits.get("final_pre_freeze_forbidden_contexts", []))
          >= {"A", "memory", "parameter_selection", "mode_feedback", "figure_preview"}
          and limits.get("full_candidate_execution_requires_confirmation_completed") is True)
    sample = contract["full_audit"]["independent_math_sample"]
    check("independent_sample_preregistered", bool(sample.get("random_algorithm"))
          and set(sample["categories"]) == set(sample.get("category_selection", {})))

    plan = load(paths["candidate_plan"])
    for path, expected in plan["evidence_sha256"].items():
        check("candidate_evidence_binding:" + path, sha(ROOT / path) == expected)
    candidates = {row["candidate_id"]: row for row in plan["candidate_definitions"]}
    check("candidate_identity_unique", len(candidates) == len(plan["candidate_definitions"]) == 11)
    for cid, candidate in candidates.items():
        check("candidate_grid:" + cid, set(candidate["parameters"]) == set(expected_r0)
              and all(value in contract["parameter_grids"][name]
                      for name, value in candidate["parameters"].items()))
        check("candidate_order_model_scope:" + cid, candidate["order"] == "S-D-P"
              and candidate["extra_online_model_calls"] == 0
              and "G3_DEVELOPMENT" in candidate["scope"])
        check("candidate_parent_scope:" + cid, all(parent in candidates for parent in candidate["parent_ids"]))
    check("candidate_count_budgets", sum(row["new_single_definition_count"] for row in candidates.values()) == 1
          and sum(row["new_combination_definition_count"] for row in candidates.values()) == 3
          and plan["record_processing_budget_upper_bound"] == 11 * 240)
    check("reference_candidate_definitions", candidates["R0"]["parameters"] == expected_r0
          and candidates["S0"]["parameters"] == contract["references"]["S0"])
    for cid in ("G0", "S0_G0"):
        rule = candidates[cid]["conditional_rule"]
        check("conditional_rule:" + cid, rule["rule_id"] == "TIME_REGULAR_DIRECTION60_V1"
              and rule["group_count"] == len(rule["groups"]) == 2
              and rule["raw_record_id_in_predicate"] is False
              and rule["method_result_or_final_feedback_in_predicate"] is False
              and {x["direction"] for x in rule["groups"]} == {35, 60}
              and "fallback" in rule["empty_or_singleton"])
    check("P_combinations_diagnostic_scope", all(candidates[cid]["kind"] == "NEW_COMBINATION_DIAGNOSTIC"
          for cid in ("S0_P2", "S0_P10")))
    check("factorial_parent_sets", plan["task_sequence"][2]["required_control_sets"] == [
        ["R0", "S0", "G0", "S0_G0"], ["R0", "S0", "P2", "S0_P2"],
        ["R0", "S0", "P10", "S0_P10"]])
    check("G0_gate_before_combination", "otherwise reject and do not run S0_G0" in plan["task_sequence"][1]["adjudication"])
    with (ROOT / "task1/evidence/goal2/tables/parameter_record_pairs.csv").open() as handle:
        pairs = list(csv.DictReader(handle))
    for description in plan["historical_direction_diagnosis"]:
        selected_rows = [r for r in pairs if r["partition"] == description["partition"]
                         and all(float(r[k]) == v for k, v in {**expected_r0, "direction": description["direction"]}.items())]
        regular = [r for r in selected_rows if "_T0_" in r["stratum"]]
        failed = [r for r in selected_rows if json.loads(r["protection_failures"])]
        check("A_historical_direction:" + description["partition"] + ":" + str(description["direction"]),
              len(selected_rows) == description["n_records"]
              and dict(Counter(r["status"] for r in selected_rows)) == description["statuses"]
              and len(regular) == description["time_regular"]["n_records"]
              and sum(r["strict_gain"] == "True" for r in regular) == description["time_regular"]["strict_gain_records"]
              and [r["record_id"] for r in regular if json.loads(r["protection_failures"])] == description["time_regular"]["failure_records"]
              and {r["record_id"] for r in failed} == {r["record_id"] for r in description["failures"]})

    for key, path in paths.items():
        check("unchanged_during_review:" + key, sha(ROOT / path) == hashes[key])
    receipt = {
        "reviewer": "native Codex independent C /root/c_protocol",
        "core_or_contract_authorship": False,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "VERIFIED" if not errors else "REJECTED",
        "target_paths": paths, "target_hashes": hashes,
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_contract_split.py" + (" " + suffix if suffix else ""),
        "checked": checked, "errors": errors,
        "observations": {"counts": {k: len(v) for k, v in expected_parts.items()},
                         "independent_PROJ_span_max_difference_work_m": maximum_span_difference,
                         "independent_raw_span_tertiles": quantiles.tolist(),
                         "selection_quota": quotas, "selection_realized": realized,
                         "all_groups_singletons": all(len(ids) == 1 for ids in groups.values()),
                         "final_sampling": "one remaining atomic-group pool; hash rank; 600 actual singleton groups",
                         "candidate_processing_executed_by_reviewer": False,
                         "candidate_scope": {"complete_definitions": 11, "new_singles": 1, "new_combinations": 3,
                                             "P_combinations": "DIAGNOSTIC_ONLY; no deployment revival of harmful variants"}},
        "unchecked": ["future strategy and controller correctness", "actual experiments",
                      "source datum or independent person identity", "production/postfreeze data use",
                      "full coordinate approximation sensitivity", "reports/package/publication"],
        "not_human_approval": True,
    }
    output = OUT / ("contract_split" + ("_" + suffix if suffix else "") + "_receipt.json")
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "target_hashes": hashes,
                      "observations": receipt["observations"], "errors": errors}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
