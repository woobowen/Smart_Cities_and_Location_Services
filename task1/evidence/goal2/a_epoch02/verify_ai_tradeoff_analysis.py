"""Development-only regression for the presentation of actual model tradeoffs."""
import ast
from collections import defaultdict
from pathlib import Path
from time import perf_counter

from task1.scripts.build_goal2_analysis import (
    EVIDENCE, Inputs, actual_ai_critique, memory_analysis, mode_analysis,
    mode_statistics, relative, render_document, resource_accounting, write_tables,
)
from task1.workflow.io import ROOT, digest, now, read_json, write_json


def main():
    started, timer = now(), perf_counter()
    directory = Path(__file__).resolve().parent
    output = directory / "ai_tradeoff_analysis_regression"
    analysis = ROOT / "task1/scripts/build_goal2_analysis.py"
    archive = EVIDENCE / "a_followup_archive/0a7ad0743e8f4fe0"
    old_binding = read_json(archive / "archive_binding.json")
    assert digest(archive / "build_goal2_analysis.py") == old_binding["source_sha256"]
    for consumer in old_binding["immutable_consumers"]:
        assert digest(ROOT / consumer["path"]) == consumer["sha256"]
    def function_asts(path):
        return {node.name: ast.dump(node) for node in ast.parse(path.read_text()).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    before = function_asts(archive / "build_goal2_analysis.py")
    after = function_asts(analysis)
    changed = [name for name in before if before[name] != after[name]]
    assert set(before) == set(after)
    assert set(changed) == {"actual_ai_critique", "render_document"}
    snapshot_path = EVIDENCE / "a_epoch02_development_registry_snapshot.json"
    snapshot = read_json(snapshot_path)
    assert not any(key.startswith("evaluation_") or key == "mode_evaluation" for key in snapshot)
    previous = read_json(directory / "A_EVALUATION_READINESS.json")
    assert digest(snapshot_path) == previous["read_scope_snapshot"]["sha256"]
    inputs = Inputs(snapshot_path)
    tables = defaultdict(list)
    memory = memory_analysis(inputs, tables)
    records = mode_analysis(inputs, tables)
    mode_statistics(tables, records)
    critique = actual_ai_critique(tables)
    actual = tables["ai_legal_proposal_tradeoffs"]
    assert len(actual) == 4
    expected = previous["actual_negative_model_proposals"]
    def key(row):
        return row["episode_id"], row["record_id"], row["candidate_id"]
    assert {key(row) for row in actual} == {key(row["proposal"]) for row in expected}
    for row in actual:
        saved = next(item for item in expected if key(item["proposal"]) == key(row))
        assert row["original_proposal"] == saved["proposal"]["original_proposal"]
        assert row["legal"] and row["executed"] and not row["proposal_is_selected_output"]
        comparison = row["actual_execution_comparison"]
        assert comparison["research_status"] == "TRADEOFF"
        assert comparison["true_quality_claim"] is False
        for name, value in comparison["registered_protection_readings"].items():
            assert value == saved["actual_comparison"][name]
        for source in row["raw_response_sources"]:
            assert digest(ROOT / source["path"]) == source["sha256"]
            response = read_json(ROOT / source["path"])
            assert any(action["record_id"] == row["record_id"] and
                       row["original_proposal"] in action["proposals"]
                       for action in response["records"])
    example = next(row for row in critique["examples"] if row["kind"] == "LEGAL_PROPOSAL_TRADEOFF")
    assert example["record_id"] == "7764" and example["candidate_id"] == "7764-r2-a"
    reversed_tables = defaultdict(list, {name: list(reversed(rows)) for name, rows in tables.items()})
    assert actual_ai_critique(reversed_tables) == critique
    assert reversed_tables["ai_legal_proposal_tradeoffs"] == actual
    costs = resource_accounting(inputs, tables)
    observations = read_json(directory / "live_development_observations/summary.json")
    assert costs == observations["costs"]
    old_cost_regression = read_json(EVIDENCE / "analysis_resource_accounting_regression.json")
    assert costs["historical_model_costs"] == old_cost_regression["historical_provider_calls"]
    for role, run_id in (("memory_registered_calls", "g2-demo-memory-01"),
                         ("orders_registered_calls", "g2-development-orders-01")):
        row = next(row for row in tables["resource_totals"] if row["run_id"] == run_id)
        for name, value in old_cost_regression[role].items():
            assert row[name] == value
    preview = output / "DEVELOPMENT_PRESENTATION_REGRESSION.md"
    summary = {"analysis_status": "DEVELOPMENT_PRESENTATION_REGRESSION_ONLY_NOT_FINAL_ANALYSIS",
        "missing_requirements": ["G2_EVAL results deliberately excluded from this regression"],
        "data": {"partition_records": {name: len(ids) for name, ids in inputs.split["splits"].items()}},
        "resource_accounting": costs, "memory": memory, "ai_critique": critique}
    render_document(summary, tables, preview)
    rendered = preview.read_text()
    for text in ("LEGAL_PROPOSAL_TRADEOFF", "40.214764", "69.145351", "ai_legal_proposal_tradeoffs.csv",
                 "是否成为锁定输出=False", "不能称为非法动作"):
        assert text in rendered, text
    exported = write_tables(output, {"ai_legal_proposal_tradeoffs": actual,
        "ai_critique_examples": critique["examples"]})
    result = {"status": "VERIFIED", "classification": "ACTUAL_DEVELOPMENT_ANALYSIS_PRESENTATION_REGRESSION",
        "started_at": started, "ended_at": now(), "elapsed_seconds": perf_counter() - timer,
        "actual_command": ".venv/bin/python -m task1.evidence.goal2.a_epoch02.verify_ai_tradeoff_analysis",
        "analysis_source": {"path": relative(analysis), "sha256": digest(analysis)},
        "verification_source": {"path": relative(Path(__file__)), "sha256": digest(Path(__file__))},
        "source_archive": old_binding, "old_A_and_cost_consumers_unchanged": True,
        "changed_functions": changed, "processing_and_contract_sources_unchanged": True,
        "development_registry_snapshot": {"path": relative(snapshot_path), "sha256": digest(snapshot_path)},
        "development_record_episodes_checked": len(records), "actual_tradeoff_proposals": len(actual),
        "all_four_match_original_responses_and_previous_bound_A_evidence": True,
        "representative": {"record_id": example["record_id"], "candidate_id": example["candidate_id"],
            "raw_response_sources": example["raw_response_sources"],
            "actual_execution_comparison": example["actual_execution_comparison"]},
        "stable_order_after_input_reversal_verified": True,
        "prior_five_critique_categories": {key: value for key, value in critique["category_coverage"].items()
            if key != "LEGAL_PROPOSAL_TRADEOFF"},
        "new_critique_category": critique["category_coverage"]["LEGAL_PROPOSAL_TRADEOFF"],
        "resource_accounting_regression": {"current_and_historical_costs_identical_to_prior_actual_observation": True,
            "historical15_14_complete1_interrupted_unknown_usage_preserved": True,
            "memory40_plus60_admission_equals100": True,
            "orders12_plus1_cache_verifier_equals13": True,
            "resource_function_ASTs_unchanged": True},
        "tables": exported, "presentation_preview": {"path": relative(preview), "sha256": digest(preview)},
        "input_hashes": inputs.lineage, "evaluation_results_read": False,
        "new_model_calls": 0, "new_candidate_processing_runs": 0,
        "final_analysis_executed": False, "selection_or_parameters_changed": False}
    failure_path = output / "initial_test_failure.json"
    if failure_path.exists():
        result["closed_test_assertion_failure"] = {"path": relative(failure_path),
            "sha256": digest(failure_path), "closure": "The corrected display assertion and all original proposal/resource checks passed in this actual rerun."}
    write_json(output / "receipt.json", result, exclusive=True)
    print({"status": result["status"], "path": relative(output / "receipt.json"),
           "sha256": digest(output / "receipt.json"), "analysis_sha256": digest(analysis),
           "actual_tradeoff_proposals": len(actual), "changed_functions": changed})


if __name__ == "__main__":
    main()
