"""Independently verify development-only candidate selection and later evaluation lock."""
import argparse
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import Audit, read_compressed, config_id
from review_live_modes_epoch02 import assessment, PROMPT_TEMPLATE
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS

HERE = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"
CFG = ROOT / "task1/config/goal2"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def review(output, include_freeze=False):
    start = time.perf_counter()
    audit = Audit()
    lock_path = EV / "candidate_lock.json"
    lock = read_json(lock_path)
    contract, matrix, split = [read_json(p) for p in (CFG / "contract.json", CFG / "experiment_matrix.json", EV / "data/split_manifest.json")]
    scope = split["splits"]["DEVELOPMENT"]
    root = EV / "runs" / lock["parameter_run_id"]
    order_root = EV / "runs" / lock["order_run_id"]
    manifest, order_manifest = read_json(root / "manifest.json"), read_json(order_root / "manifest.json")
    audit.check("development_only_parent", lock["source_partition"] == manifest["partition"] == order_manifest["partition"] == "DEVELOPMENT"
                and lock["g2_eval_observed_for_selection"] is False)
    audit.same("exact_full_development_scope", manifest["input_ids"], scope)
    audit.same("structural_candidates_not_combined", lock["structural_candidates"], contract["structural_candidates"])
    entries = {e["config_id"]: e for e in manifest["artifacts"].values()}
    expected_configs = {r["config_id"]: r["parameters"] for r in matrix["parameter_configurations"]}
    audit.check("complete_parameter_grid", set(entries) == set(expected_configs) == set(lock["all_config_assessments"]))
    refid = config_id(contract["reference_parameters"])
    baseline_path = root / entries[refid]["file"]
    audit.check("reference_hash", digest(baseline_path) == entries[refid]["sha256"])
    baseline = {r["record_id"]: r for r in read_compressed(baseline_path)["records"]}
    all_assessments = {}
    for cid, entry in entries.items():
        path = root / entry["file"]
        audit.check("candidate_hash", digest(path) == entry["sha256"])
        batch = read_compressed(path)
        audit.same("candidate_fixed_parameters", batch["parameters"], expected_configs[cid])
        audit.same("candidate_full_scope", [r["record_id"] for r in batch["records"]], scope)
        comparisons = [assessment(row, baseline[row["record_id"]]) for row in batch["records"]]
        feasible, gain = all(r["feasible"] for r in comparisons), any(r["strict_gain"] for r in comparisons)
        status = ("SUPPORTED_WITHIN_SCOPE" if feasible and gain else "NO_DEMONSTRATED_GAIN" if feasible else
                  "REJECTED_BY_CONSTRAINT" if any(r["status"] == "REJECTED_BY_CONSTRAINT" for r in comparisons) else "TRADEOFF")
        expected = {"config_id": cid, "parameters": batch["parameters"], "engineering_status": "VERIFIED",
                    "feasible_all_records": feasible, "strict_gain_any_record": gain, "record_comparisons": comparisons,
                    "summary": batch["summary"], "status": status}
        audit.same("candidate_independent_selection_evidence", lock["all_config_assessments"][cid], expected)
        all_assessments[cid] = expected
    audit.same("complete_feasible_set", lock["feasible_set"], [cid for cid, row in all_assessments.items() if row["feasible_all_records"]])
    chosen = {}
    for name, allowed in (("C-S", {"dt", "distance", "min_points", "min_length"}), ("C-D", {"direction"}), ("C-P", {"dp"})):
        domain = [cid for cid, row in entries.items() if all(row["parameters"][key] == contract["reference_parameters"][key] for key in contract["reference_parameters"] if key not in allowed)]
        gains = [cid for cid in domain if all_assessments[cid]["feasible_all_records"] and all_assessments[cid]["strict_gain_any_record"]]
        def dominates(left, right):
            strict = False
            for a, b in zip(all_assessments[left]["record_comparisons"], all_assessments[right]["record_comparisons"]):
                if not set(b["candidate_covered_indices"]) <= set(a["candidate_covered_indices"]):
                    return False
                strict = strict or a["candidate_covered_count"] > b["candidate_covered_count"]
                x, y = a["candidate_max_on_baseline_covered"], b["candidate_max_on_baseline_covered"]
                eps = max(a["numerical_allowance"], b["numerical_allowance"])
                if y is not None and (x is None or x > y + eps):
                    return False
                strict = strict or x is not None and y is not None and x < y - eps
            return strict
        frontier = [cid for cid in gains if not any(dominates(other, cid) for other in gains if cid != other)]
        if name == "C-P" and gains:
            selected = min(gains, key=lambda cid: (entries[cid]["summary"]["n_dp_output"], entries[cid]["summary"]["dp_max_error"] or 0, entries[cid]["parameters"]["dp"], cid))
            reason = "COMPRESSION_WITHIN_COMMON_5_WORK_METRE_BUDGET"
        elif len(frontier) == 1:
            selected, reason = frontier[0], "UNIQUE_PROTECTED_PARETO_GAIN"
        else:
            selected, reason = refid, "NO_UNIQUE_COMPARABLE_GAIN_KEEP_REFERENCE"
        expected = {"config_id": selected, "parameters": entries[selected]["parameters"], "selection_reason": reason,
                    "eligible_gain_ids": gains, "pareto_frontier": frontier, "domain_ids": domain,
                    "research_status": all_assessments[selected]["status"], "final_method_frozen": False}
        audit.same("single_candidate:" + name, lock["selected_single_candidates"][name], expected)
        chosen[name] = expected
    order_table_path = order_root / "order_table.json"
    audit.check("order_table_hash", digest(order_table_path) == order_manifest["tables"]["order_table.json"])
    order_table = read_json(order_table_path)
    safe = [r["order"] for r in order_table if not r["safety_failures"]]
    audit.same("safe_order_lock", lock["feasible_orders"], safe)
    audit.same("fixed_representatives", lock["eval_representatives"], matrix["fixed_eval_representative_config_ids"])
    targets = [lock_path, root / "manifest.json", order_root / "manifest.json"]
    components = ["development_selection_only", "candidate_lock", "three_separate_candidate_families", "all_config_comparisons", "safe_orders", "fixed_representatives"]
    if include_freeze:
        freeze_path = EV / "evaluation_freeze.json"
        freeze = read_json(freeze_path)
        current = read_json(EV / "current_runs.json")
        targets.append(freeze_path)
        audit.check("freeze_status", freeze["status"] == "LOCKED_BEFORE_G2_EVAL" and freeze["evaluation_previously_observed"] is False)
        audit.check("freeze_contract_split", freeze["contract_sha256"] == digest(CFG / "contract.json") and freeze["split_sha256"] == digest(EV / "data/split_manifest.json"))
        audit.check("freeze_candidate_hash", freeze["candidate_lock_sha256"] == digest(lock_path))
        audit.same("freeze_candidates", freeze["selected_single_candidates"], chosen)
        audit.same("freeze_orders", freeze["orders"], safe)
        audit.same("freeze_representatives", freeze["representative_config_ids"], matrix["fixed_eval_representative_config_ids"])
        audit.same("freeze_eval120", freeze["eval_ids"], split["splits"]["G2_EVAL"])
        audit.same("freeze_eval24", freeze["eval_llm_ids"], split["llm_subsets"]["G2_EVAL"])
        audit.check("freeze_three_episodes", freeze["evaluation_episodes"] == 3)
        audit.check("freeze_prompt_hash", freeze["prompt_template_sha256"] == object_hash(PROMPT_TEMPLATE))
        for path, key in ((ROOT / "task1/workflow/g2_modes.py", "mode_implementation_sha256"), (ROOT / "task1/workflow/g2_provider.py", "provider_implementation_sha256"), (ROOT / freeze["memory_path"], "memory_sha256")):
            audit.check("freeze_dependency:" + key, digest(path) == freeze[key])
        current_sources = {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / "task1/workflow").glob("*.py")}
        current_sources["task1/scripts/goal2.py"] = digest(ROOT / "task1/scripts/goal2.py")
        audit.same("freeze_exact_source_epoch", freeze["processing_source_hashes"], current_sources)
        for key, value in freeze["development_manifest_hashes"].items():
            path = EV / "runs" / current[key] / "manifest.json"
            row = read_json(path)
            audit.check("freeze_development_manifest:" + key, digest(path) == value and row["status"] == "REVIEW_PENDING" and row["ended_at"] <= freeze["frozen_at"])
        for path in (EV / "runs").glob("*/manifest.json"):
            row = read_json(path)
            if row["partition"] == "G2_EVAL":
                audit.check("evaluation_started_after_freeze", row["started_at"] >= freeze["frozen_at"])
        components = REQUIRED_COMPONENTS["evaluation_freeze"] + components
    result = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": "evaluation_freeze" if include_freeze else None,
              "classification": "COMPLETE_C_EVALUATION_FREEZE_REVIEW" if include_freeze else "PARTIAL_C_DEVELOPMENT_SELECTION_REVIEW",
              "at": now(), "targets": [bound(p) for p in targets],
              "source_hashes": {p: digest(ROOT / p) for p in task_sources("evaluation_freeze")},
              "checked_components": components, "unchecked_components": ["future_G2_EVAL_method_outcomes", "final_Goal2_acceptance"],
              "checks": audit.check_count, "errors": audit.errors, "single_candidates": chosen,
              "new_model_calls": 0, "elapsed_seconds": time.perf_counter() - start,
              "audit_program": bound(Path(__file__))}
    write_json(HERE / output, result, exclusive=True)
    print({k: result[k] for k in ("status", "classification", "checks", "errors", "elapsed_seconds")}, flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--include-freeze", action="store_true")
    args = parser.parse_args()
    result = review(args.output, args.include_freeze)
    raise SystemExit(result["status"] != "VERIFIED")
