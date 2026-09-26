"""Inventory visible Goal 2 provider attempts, including engineering qualification.

This ledger separates effectiveness experiments, superseded attempts and smoke
costs. It does not infer hidden requests, billing, or all Python function calls.
"""
from collections import Counter
from pathlib import Path

from task1.workflow.io import ROOT, digest, now, read_json, write_json


def main():
    evidence = ROOT / "task1/evidence/goal2"
    current = read_json(evidence / "current_runs.json")
    current_roles = {value: key for key, value in current.items() if key != "counterexamples"}
    old = read_json(evidence / "superseded_runs.json")
    historical_statuses = {row["run_id"]: row["status"] for row in old["runs"]}
    historical_ids = set(historical_statuses)
    assert not set(current_roles) & historical_ids
    attempts = []
    for path in sorted(evidence.rglob("receipt.json")):
        receipt = read_json(path)
        if "requested_model" not in receipt:
            continue
        relative = path.relative_to(evidence)
        if relative.parts[0] == "runs":
            run_id = relative.parts[1]
            if run_id in current_roles:
                scope = "CURRENT_VALID_EXPERIMENT"
            elif run_id in historical_ids:
                scope = "HISTORICAL_SUPERSEDED_OR_INTERRUPTED_EXPERIMENT"
            else:
                raise ValueError("UNCLASSIFIED_PROVIDER_RUN:" + run_id)
        elif relative.parts[0] == "provider_smoke":
            scope, run_id = "ENGINEERING_PROVIDER_QUALIFICATION", None
        else:
            raise ValueError("UNCLASSIFIED_PROVIDER_ATTEMPT:" + str(relative))
        dispatch = path.with_name("dispatch.json")
        assert dispatch.is_file()
        usage = receipt.get("usage")
        attempts.append({"scope": scope, "run_id": run_id,
            "receipt": str(path.relative_to(ROOT)), "sha256": digest(path),
            "dispatch_sha256": digest(dispatch), "status": receipt["status"],
            "logical_request_id": receipt.get("request_id"),
            "logical_request_id_is_provider_request_id": False,
            "thread_id": receipt.get("thread_id"), "requested_model": receipt["requested_model"],
            "provider_request_ids": receipt.get("provider_request_ids", "unavailable"),
            "underlying_requests": receipt.get("underlying_requests", "unknown"),
            "usage": usage if isinstance(usage, dict) else None,
            "usage_reason": None if isinstance(usage, dict) else "NOT_OBSERVED",
            "started_at": receipt.get("started_at"), "ended_at": receipt.get("ended_at"),
            "elapsed_seconds": receipt.get("elapsed_seconds"),
            "included_in_current_effectiveness": scope == "CURRENT_VALID_EXPERIMENT"})
    summaries = []
    for scope in sorted({row["scope"] for row in attempts}):
        rows = [row for row in attempts if row["scope"] == scope]
        known = [row["usage"] for row in rows if row["usage"] is not None]
        keys = sorted({key for usage in known for key in usage})
        summaries.append({"scope": scope, "visible_dispatches": len(rows),
            "statuses": dict(Counter(row["status"] for row in rows)),
            "usage_observed_dispatches": len(known), "usage_unavailable_dispatches": len(rows) - len(known),
            "observed_usage_sums": {key: sum(usage.get(key, 0) for usage in known) for key in keys},
            "complete_usage_total_available": len(known) == len(rows),
            "visible_elapsed_seconds_sum": sum(row["elapsed_seconds"] for row in rows if row["elapsed_seconds"] is not None),
            "elapsed_seconds_unavailable_dispatches": sum(row["elapsed_seconds"] is None for row in rows),
            "cost_currency": "unavailable", "underlying_request_total": "unknown"})
    runs = []
    for path in sorted((evidence / "runs").glob("*/manifest.json")):
        manifest = read_json(path)
        run_id = manifest["run_id"]
        scope = ("CURRENT_VALID_EXPERIMENT" if run_id in current_roles else
                 "HISTORICAL_SUPERSEDED_OR_INTERRUPTED_EXPERIMENT" if run_id in historical_ids else
                 "ENGINEERING_PROCESSING_SMOKE" if manifest["classification"] == "ENGINEERING_SMOKE_TEST" else None)
        assert scope is not None, run_id
        runs.append({"scope": scope, "run_id": run_id, "manifest": str(path.relative_to(ROOT)),
            "sha256": digest(path), "candidate_evaluations": manifest["candidate_evaluations"],
            "instrumented_processing_tool_calls": manifest["deterministic_tool_calls"],
            "cache_reads": manifest["cache_reads"],
            "scope_complete": manifest["status"] in ("REVIEW_PENDING", "VERIFIED") and
                historical_statuses.get(run_id) != "INTERRUPTED_CHECKPOINT_SUPERSEDED",
            "historical_registry_status": historical_statuses.get(run_id),
            "limitation": "Manifest counters exclude independent governance audits, counterexamples, coordinate checks and RECOMPUTE. Historical interrupted manifests may exclude in-flight work."})
    current_summary = read_json(evidence / "result_summary.json")
    actual_current = sum(row["scope"] == "CURRENT_VALID_EXPERIMENT" for row in attempts)
    actual_history = sum(row["scope"] == "HISTORICAL_SUPERSEDED_OR_INTERRUPTED_EXPERIMENT" for row in attempts)
    assert actual_current == current_summary["resource_accounting"]["current_valid_model_costs"]["visible_experiment_model_dispatches"]
    assert actual_history == current_summary["resource_accounting"]["historical_model_costs"]["visible_experiment_model_dispatches"]
    result = {"at": now(), "classification": "OBSERVED_RESOURCE_LEDGER_WITH_EXPLICIT_SCOPES",
        "generator_sha256": digest(__file__), "analysis_summary_sha256": digest(evidence / "result_summary.json"),
        "current_runs_sha256": digest(evidence / "current_runs.json"),
        "visible_cli_provider_attempts_all_scopes": len(attempts), "provider_scope_summaries": summaries,
        "attempts": attempts, "registered_run_counters": runs,
        "analysis_registered_run_resource_accounting": current_summary["resource_accounting"],
        "governance_role_dispatches": {"source": "task1/evidence/goal2/governance_dispatches.json",
            "meaning": "Separate timestamped native role-dispatch observation; never equated with provider requests or experiment calls."},
        "excluded_from_effectiveness": ["provider qualification smoke", "engineering processing/counterexample smoke", "superseded/interrupted attempts", "independent audits", "Notebook RECOMPUTE"],
        "unknowns": ["hidden underlying provider requests", "billing/currency costs", "unobserved interrupted token usage", "all helper and operating-system calls"]}
    write_json(evidence / "resource_ledger.json", result)
    print({"visible_cli_provider_attempts_all_scopes": len(attempts),
           "scopes": {row["scope"]: row["visible_dispatches"] for row in summaries}})


if __name__ == "__main__":
    main()
