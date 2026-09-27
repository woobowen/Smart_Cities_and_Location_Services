"""Independent C challenges, all SYNTHETIC_ENGINEERING_TEST inputs.

No reserved, selection, or final record method effects are read by these tests.
Core implementation authors must repair implementation rather than relax checks.
"""
from copy import deepcopy
from pathlib import Path

import pytest

from task1.goal3 import runtime, selection
from task1.workflow.g2_pipeline import run_record


CONTRACT = "a" * 64
P = {"dt": 30, "distance": 400, "min_points": 2, "min_length": 0, "direction": 35, "dp": 5}


def trace(dp=5, rid="C_SYNTHETIC", y=3, min_points=2):
    record = {"record_id": rid, "indices": list(range(5)), "timestamps": [0, 10, 20, 30, 40],
              "xy": [[0., 0.], [10., 0.], [20., float(y)], [30., 0.], [40., 0.]]}
    return run_record(record, {**P, "dp": dp, "min_points": min_points}, "S-D-P", contract_hash=CONTRACT,
                      provenance={"source_kind": "ENGINEERING_TEST"})


def reject_or_infeasible(call):
    try:
        result = call()
    except (ValueError, KeyError):
        return
    assert not result["feasible"], "mismatched trusted comparison was accepted"


def test_identical_reference_is_not_gain():
    t = trace()
    comparison = selection.paired(t, deepcopy(t))
    assert comparison["feasible"] and not comparison["strict_gain"]


def test_P_finer_geometry_is_not_compression_gain():
    coarse, finer = trace(5), trace(2)
    assert finer["metrics"]["n_dp_output"] > coarse["metrics"]["n_dp_output"]
    general = selection.paired(finer, coarse)
    specialized = selection.paired(finer, coarse, p_only=True)
    assert general["strict_gain"]
    assert specialized["feasible"] and not specialized["strict_gain"]


def test_P_parent_complete_input_mismatch_rejected():
    reference, candidate = trace(), trace()
    candidate["stages"][2]["input"][0]["indices"] = [0, 2, 4]
    result = selection.paired(candidate, reference, p_only=True)
    assert not result["feasible"] and "DP_REFERENCE_CHANGED" in result["protection_failures"]


def test_common_geometry_degradation_rejected_even_when_point_count_benefit():
    reference, candidate = trace(2), trace(5)
    result = selection.paired(candidate, reference)
    assert not result["feasible"]
    assert "COMMON_GEOMETRIC_PROTECTION_DEGRADED" in result["protection_failures"]


def test_null_reference_does_not_become_geometric_gain():
    reference, candidate = trace(), trace()
    for t in (reference, candidate):
        for row in t["metrics"]["common_point_errors"]:
            row["error"] = None
        t["metrics"]["record_covered"] = False
        t["metrics"]["raw_windows_covered"] = 0
    result = selection.paired(candidate, reference)
    assert not result["strict_gain"]
    assert result["baseline_common_max"] is None
    assert result["candidate_max_on_baseline_covered"] is None


def test_coverage_identity_loss_not_hidden_by_equal_cardinality():
    reference, candidate = trace(), trace()
    reference["metrics"]["common_point_errors"][0]["error"] = None
    candidate["metrics"]["common_point_errors"][-1]["error"] = None
    result = selection.paired(candidate, reference)
    assert result["coverage_delta"] == 0 and not result["feasible"]
    assert "COMMON_COVERED_IDENTITIES_LOST" in result["protection_failures"]


def test_different_raw_record_comparison_rejected():
    reject_or_infeasible(lambda: selection.paired(trace(2, rid="OTHER", min_points=3), trace(5)))


def test_different_raw_values_same_record_comparison_rejected():
    reject_or_infeasible(lambda: selection.paired(trace(2, y=1, min_points=3), trace(5, y=3)))


def test_wrong_contract_comparison_rejected():
    reference, candidate = trace(), trace(2)
    candidate["contract_hash"] = "b" * 64
    reject_or_infeasible(lambda: selection.paired(candidate, reference))


def rule_strategy():
    # Actual frozen definition is an input to the routing implementation test.
    import json
    root = Path(__file__).resolve().parents[4]
    plan = json.loads((root / "task1/evidence/goal3/a_candidate_plan.json").read_text())
    return next(deepcopy(c) for c in plan["candidate_definitions"] if c["candidate_id"] == "G0")


@pytest.mark.parametrize("times,expected", [
    ([0, 10, 20, 30], 60), ([0, 30, 60], 60),
    ([], 35), ([0], 35), ([0, 0], 35), ([1, 0], 35),
    ([0, 31], 35), ([0, None], 35), ([0, float("nan")], 35), ([False, 10], 35),
])
def test_raw_time_rule_and_undefined_fallback(times, expected):
    params, group = runtime.resolve_parameters(rule_strategy(), [times, [[0, 0]] * len(times)])
    assert params["direction"] == expected
    assert group == ("TIME_REGULAR" if expected == 60 else "TIME_FLAGGED_OR_UNAVAILABLE")


def test_development_gate_rejects_final_identity(monkeypatch):
    fixtures = {
        "contract_freeze.json": {"status": "INDEPENDENT_C_VERIFIED", "bindings": {}},
        "split_manifest.json": {"partitions": {"G3_DEVELOPMENT": ["DEV"], "G3_SELECTION": ["SELECT"],
                                                "FINAL_CONFIRM": ["FINAL"]}},
    }
    monkeypatch.setattr(runtime, "read_json", lambda p: deepcopy(fixtures[Path(p).name]))
    monkeypatch.setattr(runtime, "assert_binding", lambda x: None)
    with pytest.raises((ValueError, KeyError)):
        runtime.execution_gate("G3_DEVELOPMENT", ["FINAL"], ["R0"])


def test_final_gate_requires_real_freeze(monkeypatch):
    fixtures = {
        "contract_freeze.json": {"status": "INDEPENDENT_C_VERIFIED", "bindings": {}},
        "split_manifest.json": {"partitions": {"FINAL_CONFIRM": ["FINAL"]}},
    }
    def read_fixture(path):
        if Path(path).name not in fixtures:
            raise FileNotFoundError("SYNTHETIC_ABSENT_FINAL_FREEZE")
        return deepcopy(fixtures[Path(path).name])
    monkeypatch.setattr(runtime, "read_json", read_fixture)
    monkeypatch.setattr(runtime, "definitions", lambda: {"R0": {}})
    monkeypatch.setattr(runtime, "assert_binding", lambda x: None)
    with pytest.raises(FileNotFoundError, match="SYNTHETIC_ABSENT_FINAL_FREEZE"):
        runtime.execution_gate("FINAL_CONFIRM", ["FINAL"], ["R0"])


def test_final_gate_rejects_strategy_added_after_freeze(monkeypatch):
    fixtures = {
        "contract_freeze.json": {"status": "INDEPENDENT_C_VERIFIED", "bindings": {}},
        "split_manifest.json": {"partitions": {"FINAL_CONFIRM": ["FINAL"]}},
        "final_freeze.json": {"bindings": {}, "input_ids": ["FINAL"], "strategy_ids": ["R0"]},
    }
    monkeypatch.setattr(runtime, "read_json", lambda p: deepcopy(fixtures[Path(p).name]))
    monkeypatch.setattr(runtime, "definitions", lambda: {"R0": {}, "NEW": {}})
    monkeypatch.setattr(runtime, "assert_binding", lambda x: None)
    with pytest.raises(ValueError, match="FROZEN_SCOPE_OR_STRATEGY_MISMATCH"):
        runtime.execution_gate("FINAL_CONFIRM", ["FINAL"], ["R0", "NEW"])


def test_aggregate_does_not_hide_one_failing_record():
    good = selection.paired(trace(2), trace(5))
    bad = selection.paired(trace(5), trace(2))
    result = selection.aggregate_pairs([good, bad])
    assert not result["all_guards_pass"] and not result["replacement_supported"]
    assert result["protected_records"] == 1 and len(result["failure_records"]) == 1


def test_choose_requires_fixed_R0_and_incumbent():
    yes = {"all_guards_pass": True, "replacement_supported": True}
    no = {"all_guards_pass": False, "replacement_supported": False}
    equal = {"all_guards_pass": True, "replacement_supported": False}
    comparisons = {a + "|" + b: deepcopy(equal) for a in ("R0", "S0", "G0") for b in ("R0", "S0", "G0")}
    comparisons["S0|R0"] = yes
    comparisons["G0|R0"] = yes
    comparisons["G0|S0"] = no
    result = selection.choose(["R0", "S0", "G0"], comparisons)
    assert result["incumbent"] == "S0"


def test_equivalent_simpler_candidate_replaces_complex_incumbent():
    same = {"all_guards_pass": True, "replacement_supported": False, "all_equivalent_readings": True}
    comps = {a + "|" + b: deepcopy(same) for a in ("R0", "A_SIMPLE", "Z_COMPLEX")
             for b in ("R0", "A_SIMPLE", "Z_COMPLEX")}
    metadata = {"A_SIMPLE": {"enhancement_modules": 1, "online_model_dependency": False, "measured_seconds": 10},
                "Z_COMPLEX": {"enhancement_modules": 2, "online_model_dependency": False, "measured_seconds": 1}}
    result = selection.choose(["Z_COMPLEX", "A_SIMPLE"], comps, initial="Z_COMPLEX", tie_metadata=metadata)
    assert result["incumbent"] == "A_SIMPLE"
    assert result["events"][0]["decision"] == "EQUIVALENT_SIMPLER_REPRESENTATIVE"


def test_equal_max_error_does_not_hide_different_pointwise_readings():
    reference, candidate = trace(), trace()
    candidate["metrics"]["common_point_errors"][1]["error"] += 0.5
    result = selection.paired(candidate, reference)
    assert result["baseline_common_max"] == result["candidate_max_on_baseline_covered"]
    assert not result["equivalent_readings"]


@pytest.fixture
def synthetic_runtime(tmp_path, monkeypatch):
    """Isolate runtime artifact behavior; no real partition or model is used."""
    import json
    from task1.workflow.io import object_hash
    ev = tmp_path / "task1/evidence/goal3"
    cfg = tmp_path / "task1/config/goal3"
    ev.mkdir(parents=True)
    cfg.mkdir(parents=True)
    raw = {"TEST_A": [[0, 10, 20, 30, 40], [[121.34 + i / 10000, 31.35] for i in range(5)]],
           "TEST_B": [[0, 10, 20, 30, 40], [[121.35 + i / 10000, 31.35] for i in range(5)]]}
    split = {"partitions": {"G3_DEVELOPMENT": list(raw)}, "raw_sha256": object_hash(raw),
             "g2_diagnostics_path": "cards.json"}
    (ev / "split_manifest.json").write_text(json.dumps(split))
    (cfg / "contract.json").write_text('{"test": "SYNTHETIC_ENGINEERING_TEST"}')
    (ev / "a_candidate_plan.json").write_text('{}')
    (tmp_path / "cards.json").write_text(json.dumps({rid: {"stratum": "SYNTHETIC"} for rid in raw}))
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    monkeypatch.setattr(runtime, "EV", ev)
    monkeypatch.setattr(runtime, "CFG", cfg)
    monkeypatch.setattr(runtime, "definitions", lambda: {"R0": {"parameters": P, "order": "S-D-P", "conditional_rule": None}})
    monkeypatch.setattr(runtime, "execution_gate", lambda *args: None)
    monkeypatch.setattr(runtime, "source_snapshot", lambda: {})
    monkeypatch.setattr(runtime, "raw_data", lambda: deepcopy(raw))
    monkeypatch.setattr(runtime.subprocess, "check_output", lambda *a, **kw: "SYNTHETIC_TEST_CODE\n")
    return ev


def test_full_scope_shard_and_summary_agree_on_synthetic_data(synthetic_runtime):
    output = synthetic_runtime / "original"
    manifest = runtime.evaluate("C_TEST", "G3_DEVELOPMENT", ["R0"], output=output)
    rows = list(runtime.read_rows(output))
    assert [row["record_id"] for row in rows] == ["TEST_A", "TEST_B"]
    assert manifest["completed_record_ids"] == manifest["input_ids"]
    assert manifest["record_metrics"]["R0"]["n_input"] == 10
    assert manifest["processing_evaluations"] == 2
    replay = runtime.evaluate("C_TEST_CACHE", "G3_DEVELOPMENT", ["R0"],
        output=synthetic_runtime / "replay", parent=output)
    assert replay["processing_evaluations"] == 0 and replay["cached_trace_rechecks"] == 2


def test_parent_cache_rejects_wrong_provenance(synthetic_runtime):
    import json
    output = synthetic_runtime / "original"
    manifest = runtime.evaluate("C_TEST", "G3_DEVELOPMENT", ["R0"], output=output)
    manifest["provenance"]["raw_sha256"] = "wrong"
    (output / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="PARENT_CACHE_SCOPE_OR_EPOCH_MISMATCH"):
        runtime.evaluate("C_TEST_CACHE", "G3_DEVELOPMENT", ["R0"],
            output=synthetic_runtime / "replay", parent=output)


def test_parent_cache_rejects_extra_record_even_if_manifest_scope_claim_unchanged(synthetic_runtime):
    import gzip
    import json
    from task1.workflow.io import digest
    output = synthetic_runtime / "original"
    manifest = runtime.evaluate("C_TEST", "G3_DEVELOPMENT", ["R0"], output=output)
    rows = list(runtime.read_rows(output))
    extra = deepcopy(rows[0])
    extra["record_id"] = "EXTRA_TEST_RECORD"
    shard = output / manifest["shards"][0]["path"]
    with gzip.open(shard, "wt", encoding="utf8") as handle:
        for row in rows + [extra]:
            handle.write(json.dumps(row) + "\n")
    manifest["shards"][0]["sha256"] = digest(shard)
    manifest["shards"][0]["records"] = 3
    manifest["shards"][0]["input_ids"].append("EXTRA_TEST_RECORD")
    (output / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises((ValueError, StopIteration)):
        runtime.evaluate("C_TEST_CACHE", "G3_DEVELOPMENT", ["R0"],
            output=synthetic_runtime / "replay", parent=output)


def test_reviewed_artifact_mutation_invalidates_descendants(tmp_path, monkeypatch):
    from task1.goal3 import control
    from task1.workflow.io import digest
    monkeypatch.setattr(control, "ROOT", tmp_path)
    target = tmp_path / "verified.json"
    target.write_text('{"value": 1}')
    journal = control.Journal(tmp_path / "journal")
    journal.state["tasks"]["handoff"].update(status="VERIFIED", source_hashes={},
        targets=[{"path": "verified.json", "sha256": digest(target)}])
    journal.state["tasks"]["contract_split"].update(status="VERIFIED", source_hashes={}, targets=[])
    target.write_text('{"value": 2}')
    changed = journal.invalidate_changed()
    assert "handoff" in changed and "contract_split" in changed
    assert journal.state["tasks"]["handoff"]["status"] == "STALE_REBUILD_REQUIRED"


def test_reviewed_receipt_mutation_invalidates_parent(tmp_path, monkeypatch):
    from task1.goal3 import control
    from task1.workflow.io import digest
    monkeypatch.setattr(control, "ROOT", tmp_path)
    target = tmp_path / "receipt.json"
    target.write_text('{"status": "VERIFIED"}')
    journal = control.Journal(tmp_path / "journal")
    journal.state["tasks"]["handoff"].update(status="VERIFIED", source_hashes={}, targets=[],
        receipt={"path": "receipt.json", "sha256": digest(target)})
    target.write_text('{"status": "REJECTED"}')
    assert "handoff" in journal.invalidate_changed()


def test_one_issue_close_does_not_resume_parent_with_another_open_issue(tmp_path, monkeypatch):
    import json
    from task1.goal3 import control
    monkeypatch.setattr(control, "ROOT", tmp_path)
    target = tmp_path / "repair.py"
    target.write_text("# SYNTHETIC_ENGINEERING_TEST patch\n")
    journal = control.Journal(tmp_path / "journal")
    journal.register_role("C", "C:independent_test", "synthetic", "test fixture")
    journal.issue("FIRST", "implementation", "fixture failure one", ["repair.py"])
    journal.issue("SECOND", "implementation", "fixture failure two", ["repair.py"])
    journal.repair("FIRST", [target])
    receipt = tmp_path / "closure.json"
    receipt.write_text(json.dumps({"role_context": "C:independent_test", "issue_id": "FIRST", "status": "VERIFIED",
        "targets": [journal.attach(target)], "checked_components": ["fixture actual repair and regression"]}))
    journal.close_issue("FIRST", receipt, "C:independent_test")
    assert journal.state["issues"]["FIRST"]["status"] == "VERIFIED"
    assert journal.state["tasks"]["implementation"]["status"] == "NEEDS_REPAIR"
