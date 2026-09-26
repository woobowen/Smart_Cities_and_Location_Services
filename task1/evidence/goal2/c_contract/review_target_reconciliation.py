"""C-only supplemental review of execution metadata and exact target handoff.

Preserves previous numerical receipts. The isolated journal is an explicitly
labelled engineering test; it never writes the actual Goal controller.
"""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import G2Journal, task_sources
from review_development_runs import Audit, read_compressed

OUT = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"
ISSUE = "G2-C-RECEIPT-TARGET-001"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def review():
    audit = Audit()
    reconciliation_path = EV / "review_target_reconciliation.json"
    reconciliation = read_json(reconciliation_path)
    state_snapshot = read_json(EV / "goal_state.json")
    issue = state_snapshot["issues"][ISSUE]
    audit.check("issue:repair_registered", issue["status"] == "REGRESSION_PENDING")
    for target in issue["repair_evidence"]:
        audit.check("repair:actual_target_bytes", digest(ROOT / target["path"]) == target["sha256"])
    outputs = []
    for row in reconciliation["task_rows"]:
        task = row["task"]
        original_path = ROOT / row["original_c_receipt"]
        original = read_json(original_path)
        audit.check(task + ":prior_independent_math_verified", original["status"] == "VERIFIED" and not original["errors"]
                    and original["role_context"] == "/root/c_contract")
        audit.same(task + ":original_targets_retained", original["targets"], row["c_targets"])
        for target in original["targets"] + row["submitted_targets"]:
            audit.check(task + ":unchanged_bytes", digest(ROOT / target["path"]) == target["sha256"])
        run_id = original["run_id"]
        directory = EV / "runs" / run_id
        manifest = read_json(directory / "manifest.json")
        execution_path = EV / "logs" / (run_id + "_execution.json")
        checks_path = EV / "logs" / (run_id + "_artifact_checks.json")
        execution, checks = read_json(execution_path), read_json(checks_path)
        log_path = ROOT / execution["log"]
        log = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
        command = [str(ROOT / ".venv/bin/python"), "-m", "task1.scripts.goal2", task.replace("_", "-"), "--run-id", run_id]
        audit.same(task + ":actual_logged_command", execution["command"], command)
        audit.same(task + ":log_start", log[0]["command"], command)
        audit.check(task + ":log_classification", log[0]["classification"] == "FROZEN_G2_EVAL")
        audit.check(task + ":run_identity_exit", execution["run_id"] == checks["run_id"] == manifest["run_id"] == run_id
                    and execution["phase"] == task.replace("_", "-") and execution["exit_code"] == 0 and manifest["status"] == "REVIEW_PENDING")
        audit.check(task + ":chronology", log[0]["started_at"] == execution["started_at"] <= manifest["started_at"]
                    <= manifest["ended_at"] <= execution["ended_at"] <= checks["checked_at"])
        utc_duration = (datetime.fromisoformat(execution["ended_at"]) - datetime.fromisoformat(execution["started_at"])).total_seconds()
        audit.check(task + ":elapsed_readings", abs(utc_duration - execution["elapsed_utc_seconds"]) < 1e-6
                    and 0 < execution["elapsed_monotonic_seconds"] <= utc_duration)
        frozen_hash = digest(EV / "evaluation_freeze.json")
        audit.check(task + ":freeze_parent", execution["evaluation_freeze_sha256"] == checks["evaluation_freeze_sha256"]
                    == log[0]["evaluation_freeze_sha256"] == frozen_hash)
        audit.check(task + ":code_parent", execution["code_sha"] == checks["code_sha"] == manifest["code_head_at_start"])
        sources = {path: digest(ROOT / path) for path in manifest["source_hashes"]}
        audit.same(task + ":current_exact_sources", sources, manifest["source_hashes"])
        audit.same(task + ":previous_review_source_epoch", original["source_hashes"], {path: digest(ROOT / path) for path in task_sources(task)})
        audit.check(task + ":source_tree", object_hash(sources) == manifest["source_tree_sha256"]
                    == execution["processing_source_tree_sha256"] == checks["processing_source_tree_sha256"])
        audit.check(task + ":source_unchanged_metadata", execution["source_unchanged_at_end"] is True)
        audit.check(task + ":self_check_scope_label", checks["classification"] == "B_SELF_CHECK_NOT_INDEPENDENT_C" and checks["status"] == "PASSED"
                    and checks["manifest_sha256"] == digest(directory / "manifest.json")
                    and "independent_alternate_numeric_recomputation" in checks["unchecked_components"])
        artifacts = {entry["file"]: entry for entry in manifest["artifacts"].values()}
        audit.check(task + ":artifact_metadata_exact_set", len(checks["artifacts"]) == len(artifacts)
                    and {item["file"] for item in checks["artifacts"]} == set(artifacts))
        for item in checks["artifacts"]:
            entry = artifacts[item["file"]]
            trace = read_compressed(directory / item["file"])
            audit.check(task + ":metadata_actual_artifact", item["config_id"] == entry["config_id"] and item["sha256"] == entry["sha256"]
                        == digest(directory / item["file"]))
            audit.check(task + ":metadata_scope_denominator", item["records"] == 120 == len(trace["records"])
                        and item["input_points"] == sum(len(r["source_record"]["timestamps"]) for r in trace["records"]))
            audit.check(task + ":metadata_production_review", item["production_review"] == entry["engineering_status"] == "VERIFIED"
                        and item["full_scope_and_ledger_counts"] == item["summary_reaggregation"] == "PASSED")
            if task == "evaluation_orders":
                audit.check(task + ":metadata_order", item["order"] == entry["order"])
                for metric in ("raw_break_crossings", "direction_windows_across_raw_breaks"):
                    audit.check(task + ":metadata_" + metric, item[metric] == entry["summary"][metric])
        audit.same(task + ":actual_resources", checks["resources"], {key: manifest[key] for key in checks["resources"]})
        if task == "evaluation_parameters":
            audit.check(task + ":actual_log_progress", len(log[1:]) == len(artifacts)
                        and {item["evaluation_config"] for item in log[1:]} == {item["config_id"] for item in artifacts.values()}
                        and all(item["records"] == 120 for item in log[1:]))
        else:
            audit.check(task + ":order_command_log", len(log) == 1)
        audit.check(task + ":original_missing_exact_two", {item["path"] for item in row["missing_target_bindings"]}
                    == {str(checks_path.relative_to(ROOT)), str(execution_path.relative_to(ROOT))})
        if audit.errors:
            raise AssertionError(audit.errors)
        complete = deepcopy(original)
        complete.update(at=now(), classification="C_NUMERIC_REVIEW_WITH_COMPLETE_EXECUTION_TARGET_BINDINGS",
                        original_numerical_review=bound(original_path), supplemental_audit_program=bound(Path(__file__)),
                        supplemental_metadata_checks=audit.check_count,
                        supplemental_limits=["Exit code and monotonic duration are contemporaneous B process observations; C verifies cross-file consistency, not an independent historical process replay."])
        complete["targets"] += [bound(path) for path in (checks_path, execution_path, log_path, original_path)]
        complete["checked_components"] += ["actual_execution_metadata", "all_submitted_target_bindings", "unchanged_numerical_evidence"]
        complete_path = OUT / (task + "_bound_receipt.json")
        write_json(complete_path, complete, exclusive=True)
        outputs.append((task, original_path, complete_path, row["submitted_targets"]))
    # Isolated test context supplies prerequisite status only. It is not a
    # second production acceptance and does not assert unexecuted prerequisites.
    test_directory = OUT / "receipt_target_engineering_test"
    if test_directory.exists():
        raise ValueError("ENGINEERING_TEST_ALREADY_EXISTS")
    journal = G2Journal(test_directory)
    journal.dispatch_role("C", "/root/c_contract", "metadata_target_test", "ENGINEERING_TEST")
    journal.state["tasks"]["evaluation_freeze"]["status"] = "VERIFIED"
    results = []
    for task, original_path, complete_path, targets in outputs:
        journal.submit(task, [ROOT / item["path"] for item in targets])
        observed = None
        try:
            journal.accept(task, original_path, "C:/root/c_contract")
        except ValueError as error:
            observed = str(error)
        audit.check(task + ":old_missing_targets_rejected", observed == "C_TARGET_MISMATCH")
        journal.accept(task, complete_path, "C:/root/c_contract")
        audit.check(task + ":complete_target_receipt_accepted", journal.state["tasks"][task]["status"] == "VERIFIED")
        results.append({"task": task, "original_receipt_rejection": observed,
                        "complete_receipt_accepted": True, "complete_receipt": bound(complete_path)})
    closure = {"issue_id": ISSUE, "status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "at": now(),
               "classification": "ACTUAL_HANDOFF_GAP_CLOSED_WITH_ISOLATED_REGRESSION",
               "targets": deepcopy(issue["repair_evidence"]), "source_hashes": deepcopy(issue["repair_source_hashes"]),
               "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch", "metadata_actual_manifest_and_logs", "prior_numerical_receipts_preserved"],
               "unchecked_components": ["independent_replay_of_historical_process_exit", "full_Goal2_acceptance"],
               "check_count": audit.check_count, "errors": audit.errors, "regression_results": results,
               "engineering_test_journal": bound(test_directory / "goal_state.json"), "audit_program": bound(Path(__file__)),
               "numerical_reruns": 0, "processing_mutations": 0, "new_model_calls": 0,
               "parent_resume": "Root must close issue, resubmit original targets, and accept complete receipts in production journal."}
    output = OUT / "receipt_target_closure_receipt.json"
    write_json(output, closure, exclusive=True)
    print({key: closure[key] for key in ("status", "check_count", "errors")})


if __name__ == "__main__":
    review()
