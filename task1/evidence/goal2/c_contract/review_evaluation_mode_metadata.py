"""Bind complete C mode review to the actual process metadata and 36-line log."""
from collections import Counter
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, now
from task1.workflow.g2_journal import task_sources
from review_development_runs import Audit

OUT = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def main():
    audit = Audit()
    original_path = OUT / "evaluation_modes_numeric_receipt.json"
    original = read_json(original_path)
    audit.check("independent_full_review", original["status"] == "VERIFIED" and original["errors"] == [] and len(original["episode_reports"]) == 36)
    for target in original["targets"]:
        audit.check("numeric_target_unchanged", digest(ROOT / target["path"]) == target["sha256"])
    run_id = original["run_id"]
    run_dir = EV / "runs" / run_id
    manifest = read_json(run_dir / "manifest.json")
    execution_path = EV / "logs" / (run_id + "_execution.json")
    log_path = EV / "logs" / (run_id + ".log")
    execution = read_json(execution_path)
    logs = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    audit.same("actual_command", execution["command"], [".venv/bin/python", "-m", "task1.scripts.goal2", "evaluation-modes", "--run-id", run_id, "--enable-live"])
    audit.check("manifest_command_matches_module_entry", manifest["command"] == str(ROOT / "task1/scripts/goal2.py") + " evaluation-modes --run-id " + run_id + " --enable-live")
    audit.check("successful_contemporaneous_exit", execution["exit_code"] == 0 and isinstance(execution["pid"], int) and execution["pid"] > 0)
    audit.check("UTC_ordering", execution["started_at"] <= manifest["started_at"] <= manifest["ended_at"] <= execution["ended_at"])
    utc_elapsed = (datetime.fromisoformat(execution["ended_at"]) - datetime.fromisoformat(execution["started_at"])).total_seconds()
    audit.check("two_duration_readings_retained", utc_elapsed > 0 and execution["elapsed_monotonic_seconds"] > 0)
    registered = {Path(item["path"]).parent.name: item for item in manifest["mode_episodes"]}
    audit.check("exact36_log_episodes", len(logs) == len({r["episode"] for r in logs}) == 36 and {r["episode"] for r in logs} == set(registered))
    counts = {}
    for row in logs:
        episode = read_json(run_dir / registered[row["episode"]]["path"])
        resources = episode["resources"]
        audit.check("log_actual_episode_resources", row["model_dispatches"] == resources["experiment_model_dispatches"] and row["candidate_evaluations"] == resources["candidate_evaluations"])
        audit.check("log_actual_elapsed_rounding", row["seconds"] == round(episode["elapsed_seconds"], 2))
        mode = episode["mode"]
        counts.setdefault(mode, Counter())
        counts[mode].update(calls=row["model_dispatches"], candidates=row["candidate_evaluations"], batches=1, record_episode_observations=len(episode["records"]))
    audit.check("mode_counts", {m: dict(v) for m, v in counts.items()} == {
        "llm-only": {"calls": 9, "candidates": 109, "batches": 9, "record_episode_observations": 72},
        "search-only": {"calls": 0, "candidates": 1440, "batches": 9, "record_episode_observations": 72},
        "llm+search": {"calls": 27, "candidates": 1080, "batches": 9, "record_episode_observations": 72},
        "llm+memory+search": {"calls": 27, "candidates": 954, "batches": 9, "record_episode_observations": 72}})
    audit.check("run_counts", sum(r["model_dispatches"] for r in logs) == manifest["experiment_model_dispatches"] == 63
                and sum(r["candidate_evaluations"] for r in logs) == manifest["candidate_evaluations"] == 3583)
    source_now = {p: digest(ROOT / p) for p in task_sources("evaluation_modes")}
    audit.same("unchanged_source_epoch", original["source_hashes"], source_now)
    state = read_json(EV / "goal_state.json")
    submitted = state["tasks"]["evaluation_modes"]["evidence"]
    expected_paths = {str((run_dir / "manifest.json").relative_to(ROOT)), str(execution_path.relative_to(ROOT)), str(log_path.relative_to(ROOT))}
    audit.check("exact_submitted_target_paths", {r["path"] for r in submitted} == expected_paths)
    for target in submitted:
        audit.check("submitted_target_current_hash", digest(ROOT / target["path"]) == target["sha256"])
    result = deepcopy(original)
    target_map = {r["path"]: r for r in original["targets"] + submitted + [bound(original_path)]}
    result.update(status="VERIFIED" if not audit.errors else "REJECTED", at=now(), targets=list(target_map.values()),
                  classification="COMPLETE_C_HELDOUT_MODES_AND_EXECUTION_METADATA_REVIEW",
                  original_numeric_review=bound(original_path), supplemental_audit_program=bound(Path(__file__)),
                  supplemental_check_count=audit.check_count, supplemental_errors=audit.errors,
                  mode_counts={m: dict(v) for m, v in counts.items()},
                  actual_process_duration={"utc_difference_seconds": utc_elapsed, "recorded_monotonic_seconds": execution["elapsed_monotonic_seconds"],
                                           "utc_minus_monotonic_seconds": utc_elapsed - execution["elapsed_monotonic_seconds"],
                                           "interpretation": "Both actual readings preserved; no retrospective replacement or invented equality. C checks metadata consistency, not historical process reexecution."})
    result["checked_components"] += ["all_submitted_target_bindings", "actual_execution_log_and_exit", "duration_readings_preserved"]
    result["errors"] += audit.errors
    write_json(OUT / "evaluation_modes_complete_receipt.json", result, exclusive=True)
    print({"status": result["status"], "numerical_checks": original["check_count"], "metadata_checks": audit.check_count, "errors": audit.errors})


if __name__ == "__main__":
    main()
