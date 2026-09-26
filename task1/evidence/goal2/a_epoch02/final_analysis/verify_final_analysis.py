"""Arithmetic and artifact readback for completed stage-analysis derivation."""
from collections import Counter
from pathlib import Path
import csv

from task1.workflow.io import ROOT, digest, now, read_json, relative, write_json


def main():
    directory = Path(__file__).resolve().parent
    evidence = ROOT / "task1/evidence/goal2"
    summary_path = evidence / "result_summary.json"
    summary = read_json(summary_path)
    execution = read_json(directory / "build_execution.json")
    independent = read_json(directory / "mode_totals_independent_readback.json")
    assert execution["exit_code"] == 0 and execution["status"] == "COMPLETED"
    assert summary["analysis_status"] == "COMPLETE_DERIVATION_FROM_VERIFIED_TRACES"
    assert not summary["missing_requirements"]
    assert summary["analysis_source_sha256"] == "2ccf9fb06b8e7633fc118b0798fce348661c07eed8a3cfa4d08a9e08559c2e38"
    assert digest(ROOT / "task1/scripts/build_goal2_analysis.py") == summary["analysis_source_sha256"]
    tables = {}
    for name, entry in summary["tables"].items():
        path = ROOT / entry["path"]
        assert digest(path) == entry["sha256"]
        with path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == entry["rows"]
        tables[name] = rows
    for key, sha256 in independent["input_bindings"].items():
        assert digest(ROOT / key) == sha256
    assert len(independent["groups"]) == 16
    assert len([key for key in independent["groups"] if key.startswith("G2_EVAL:")]) == 12
    for row in summary["mode_summary"]:
        groups = [value for key, value in independent["groups"].items()
                  if key.startswith(row["partition"] + ":" + row["mode"] + ":")]
        assert len(groups) == row["episodes"]
        assert row["original_records"] == 24
        assert row["record_episode_observations"] == sum(len(group["records"]) for group in groups)
        for field, raw_field in (("candidate_evaluations", "candidate_evaluations"),
                ("experiment_model_dispatches", "model_dispatches"),
                ("valid_raw_proposal_denominator", "raw_proposals"),
                ("raw_legal_proposals", "legal_proposals"), ("executed_proposals", "executed_proposals"),
                ("fallback_records_episodes", "fallbacks"),
                ("evaluable_prediction_denominator", "evaluable_predictions"),
                ("matching_predictions", "matching_predictions"),
                ("input_tokens_observed_sum", "input_tokens"),
                ("output_tokens_observed_sum", "output_tokens")):
            assert row[field] == sum(group[raw_field] for group in groups), (row["mode"], field)
        assert row["protected_gain_records_episodes"] == sum(
            group["research_outcomes"].get("SUPPORTED_WITHIN_SCOPE", 0) for group in groups)
    single_path = evidence / "a_epoch02/heldout_single_confirmation/single_candidate_confirmation.json"
    singles = read_json(single_path)
    assert len(summary["single_candidates"]) == 3
    for actual in summary["single_candidates"]:
        previous = next(row for row in singles["candidate_results"] if row["candidate"] == actual["candidate"])
        for key, value in actual.items():
            assert previous[key] == value, (actual["candidate"], key)
    assert len(tables["candidate_record_pairs"]) == 360
    assert len(tables["mode_record_results"]) == 384
    assert len(tables["model_calls"]) == 84 and len(tables["historical_model_calls"]) == 15
    assert summary["parameters"]["unique_development_configs"] == 59
    assert summary["parameters"]["unique_evaluation_configs"] == 14
    costs = summary["resource_accounting"]
    current, historical = costs["current_valid_model_costs"], costs["historical_model_costs"]
    assert current["visible_experiment_model_dispatches"] == current["completed_calls"] == 84
    assert historical["visible_experiment_model_dispatches"] == 15
    assert historical["completed_calls"] == 14 and historical["interrupted_or_failed_calls"] == 1
    assert historical["input_tokens_unknown_dispatches"] == 1
    assert historical["input_tokens_all_dispatch_total"] == "unknown"
    assert costs["all_visible_experiment_model_dispatches"] == 99
    assert current["provider_request_count"] == historical["provider_request_count"] == "unknown"
    assert current["currency_cost"] == historical["currency_cost"] == "unavailable"
    assert costs["historical_costs_are_current_effectiveness_results"] is False
    assert current["input_tokens_known_sum"] == sum(row["input_tokens"] for row in independent["groups"].values())
    assert current["output_tokens_known_sum"] == sum(row["output_tokens"] for row in independent["groups"].values())
    memory = {}
    for partition in ("DEVELOPMENT", "G2_EVAL"):
        retrievals = [row for row in tables["memory_retrieval"] if row["partition"] == partition]
        uses = [row for row in tables["memory_consumption"] if row["partition"] == partition]
        assert all(row["hash_unchanged"] == "True" and row["snapshot_before"] == row["snapshot_after"] for row in retrievals)
        memory[partition] = {"retrieval_opportunities": len(retrievals),
            "nonempty_retrievals": sum(int(row["delivered_count"]) > 0 for row in retrievals),
            "record_rounds": len(uses), "rounds_with_valid_citation": sum(int(row["valid_citation_count"]) > 0 for row in uses),
            "rounds_with_parameter_consistent_citation": sum(int(row["action_consistent_count"]) > 0 for row in uses),
            "valid_citation_occurrences": sum(int(row["valid_citation_count"]) for row in uses),
            "parameter_consistent_citation_proposal_pairs": sum(int(row["action_consistent_count"]) for row in uses)}
    assert memory["DEVELOPMENT"]["retrieval_opportunities"] == 24
    assert memory["G2_EVAL"]["retrieval_opportunities"] == 72
    assert not summary["quality_accepted"] and not summary["final_method_frozen"]
    assert not summary["selection_after_evaluation"]
    result = {"status": "VERIFIED", "classification": "A_FINAL_ANALYSIS_ARITHMETIC_AND_HASH_READBACK_NOT_C_FULL_ACCEPTANCE",
        "at": now(), "actual_command": ".venv/bin/python -m task1.evidence.goal2.a_epoch02.final_analysis.verify_final_analysis",
        "source": {"path": relative(Path(__file__)), "sha256": digest(Path(__file__))},
        "summary": {"path": relative(summary_path), "sha256": digest(summary_path)},
        "checked_table_count": len(tables), "checked_table_rows": sum(len(rows) for rows in tables.values()),
        "actual_episode_readback": {"path": relative(directory / "mode_totals_independent_readback.json"),
            "sha256": digest(directory / "mode_totals_independent_readback.json")},
        "heldout_single_confirmation": {"path": relative(single_path), "sha256": digest(single_path)},
        "evaluation_group_count": 12, "original_records_per_group": 24, "evaluation_record_episodes": 288,
        "evaluation_single_candidates_match_prior_independent_C_reviewed_artifact": True,
        "current_model_dispatches": 84, "historical_model_dispatches": 15,
        "historical_unknown_usage_preserved": True, "unavailable_currency_cost_preserved": True,
        "memory_readings": memory,
        "new_model_calls": 0, "new_candidate_processing_runs": 0,
        "independent_C_full_acceptance": "PENDING_OUTSIDE_THIS_ARITHMETIC_CHECK"}
    receipt = directory / "verification_receipt.json"
    write_json(receipt, result, exclusive=True)
    paths = [summary_path, ROOT / summary["stage_analysis"]["path"], ROOT / "task1/scripts/build_goal2_analysis.py",
        directory / "build_execution.json", directory / "build.log", directory / "mode_totals_independent_readback.json",
        receipt, Path(__file__).resolve()]
    paths.extend(ROOT / entry["path"] for entry in summary["tables"].values())
    targets = [{"path": relative(path), "sha256": digest(path)} for path in paths]
    write_json(directory / "review_targets.json", {"status": "REVIEW_PENDING",
        "classification": "FINAL_ANALYSIS_EXACT_TARGETS", "targets": targets,
        "self_not_in_targets_to_avoid_hash_self_reference": True}, exclusive=True)
    print({"status": result["status"], "targets": len(targets), "tables": len(tables),
        "table_rows": result["checked_table_rows"], "memory": memory,
        "targets_sha256": digest(directory / "review_targets.json")})


if __name__ == "__main__":
    main()
