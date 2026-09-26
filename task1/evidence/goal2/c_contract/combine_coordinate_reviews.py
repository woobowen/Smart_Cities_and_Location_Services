"""Bind completed C coordinate reviews and actual evaluation diagnostic metadata."""
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, now
from review_development_runs import Audit

OUT = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def main():
    audit = Audit()
    inputs = [OUT / "coordinate_sensitivity_receipt_v2.json", OUT / "evaluation_coordinate_sensitivity_receipt.json"]
    reviews = [read_json(p) for p in inputs]
    targets, runs = {}, []
    for path, review in zip(inputs, reviews):
        audit.check("independent_review_passed", review["status"] == "VERIFIED" and review["errors"] == [] and review["role_context"] == "/root/c_contract")
        for target in review["targets"] + [review["audit_program"], review["numeric_oracle"], bound(path)]:
            audit.check("all_reviewed_targets_current", digest(ROOT / target["path"]) == target["sha256"])
            targets[target["path"]] = target
        for run in review["runs"]:
            audit.check("actual_run_manifest_current", digest(ROOT / run["manifest"]["path"]) == run["manifest"]["sha256"])
            runs.append(run)
    audit.check("all7_disjoint_run_ids", len(runs) == len({r["run_id"] for r in runs}) == 7)
    audit.check("full_current_trace_denominator", sum(r["traces"] for r in runs) == 15721)
    ep = EV / "logs/coordinate_evaluation_01_execution.json"
    lp = EV / "logs/coordinate_evaluation_01.log"
    sp = EV / "coordinate_sensitivity/evaluation-01/summary.json"
    execution, summary = read_json(ep), read_json(sp)
    logs = [json.loads(line) for line in lp.read_text().splitlines() if line.strip()]
    audit.check("actual_diagnostic_command", execution["actual_command"] == [".venv/bin/python", "-m", "task1.scripts.goal2_coordinate_sensitivity"] + summary["command"][1:])
    audit.check("actual_diagnostic_log", execution["exit_code"] == 0 and execution["log_sha256"] == digest(lp)
                and [(r["run_id"], r["traces"], r["differences"]) for r in logs[:-1]] == [(r["run_id"], r["actual_traces_checked"], r["sensitivity_difference_counts"]) for r in summary["runs"]])
    audit.check("complete_diagnostic_log", logs[-1] == {"status": "VERIFIED", "output_dir": "task1/evidence/goal2/coordinate_sensitivity/evaluation-01", "selected_records": 307, "runs_checked": 3})
    audit.check("actual_time_order", execution["started_at"] <= summary["started_at"] <= summary["ended_at"] <= execution["ended_at"] and execution["elapsed_monotonic_seconds"] > 0)
    for p in (ep, lp, sp):
        targets[str(p.relative_to(ROOT))] = bound(p)
    result = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": None, "at": now(),
              "classification": "COMPLETE_C_CURRENT_COORDINATE_DIAGNOSTICS_REVIEW", "targets": list(targets.values()),
              "checked_components": ["307_selected_raw_records_30992_points", "all1594527_within_record_Geod_pairs", "all30685_raw_edges", "all15721_registered_current_traces", "complete_S_D_P_alternate_predicates_and_DP_index_sets", "version_and_input_hashes", "actual_diagnostic_execution_metadata"],
              "unchecked_components": ["source_datum", "ground_truth_location_accuracy", "G3_RESERVED_processing", "statistical_population_representativeness", "full_goal_acceptance"],
              "runs": runs, "check_count": audit.check_count, "prior_independent_checks": sum(r["check_count"] for r in reviews), "errors": audit.errors,
              "scope": {"records": 307, "points": 30992, "within_record_pairs": 1594527, "zero_geod_pairs": 55362, "current_stage_traces": 15721},
              "new_model_calls": 0, "new_candidate_experiments": 0, "memory_writes": 0,
              "interpretation": "Fixed-ellipsoid ENU implementation agrees with independent PROJ within 1e-6 m. Geod and AEQD are alternate conditional-model diagnostics. No S/D/P threshold difference was found on these exact registered stage inputs; this does not prove the unknown source datum or real geographic accuracy.",
              "audit_program": bound(Path(__file__))}
    write_json(OUT / "coordinate_complete_receipt.json", result, exclusive=True)
    print({k: result[k] for k in ("status", "check_count", "prior_independent_checks", "errors")})


if __name__ == "__main__":
    main()
