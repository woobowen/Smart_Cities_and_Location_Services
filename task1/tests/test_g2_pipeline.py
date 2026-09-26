"""Goal 2 known-answer semantics and artifact-corruption fault injection.

All coordinates in this module are SYNTHETIC_COUNTEREXAMPLE / ENGINEERING_TEST.
They are not discoveries in the teacher data or injected production failures.
"""
from copy import deepcopy
import math

import pytest

from task1.workflow.g2_pipeline import ORDERS, REFERENCE_PARAMETERS, run_batch, run_record
from task1.workflow.g2_metrics import common_reference_metrics, review_batch, review_record
from task1.workflow.io import object_hash


CONTRACT_HASH = object_hash({"purpose": "G2_ENGINEERING_TEST"})
PROVENANCE = {"source_kind": "SYNTHETIC_COUNTEREXAMPLE", "code_tree_hash": "fixture"}


def fixture(points, times=None, record_id="fixture:g2", indices=None):
    return {"record_id": record_id, "indices": list(range(len(points))) if indices is None else indices,
            "timestamps": list(range(len(points))) if times is None else times,
            "xy": [list(point) for point in points]}


def parameters(**changes):
    return {**REFERENCE_PARAMETERS, "min_points": 2, "min_length": 0, **changes}


def execute(raw, p=None, order="S-D-P"):
    return run_record(raw, p or parameters(), order, contract_hash=CONTRACT_HASH, provenance=PROVENANCE)


def review(output, raw, p=None, order="S-D-P"):
    return review_record(output, raw, expected_parameters=p or parameters(), expected_order=order,
                         contract_hash=CONTRACT_HASH, trusted_provenance=PROVENANCE)


@pytest.mark.parametrize("order", ORDERS)
def test_all_six_orders_actual_stage_execution_and_conservation(order):
    raw = fixture([(0, 0), (0, 10), (0, 20), (10, 20), (10, 30), (800, 0), (800, 10)],
                  times=[0, 10, 20, 30, 40, 200, 210])
    before = deepcopy(raw)
    output = execute(raw, order=order)
    assert output["classification"] == "SYNTHETIC_COUNTEREXAMPLE"
    assert raw == before
    assert [stage["name"] for stage in output["stages"]] == order.split("-")
    assert output["stages"][0]["input"][0]["indices"] == raw["indices"]
    assert [row["original_index"] for row in output["point_actions"]] == raw["indices"]
    metric = output["metrics"]
    assert metric["n_input"] == sum(metric[key] for key in
                                    ("n_final", "n_filtered", "n_direction_removed", "n_dp_removed"))
    assert review(output, raw, order=order)["status"] == "VERIFIED"


def test_p_before_s_really_loses_trigger_and_crosses_fixed_raw_boundary():
    raw = fixture([(0, 0), (401, 0), (399, 0)])
    p = parameters(direction=180, dp=5)
    baseline = execute(raw, p)
    changed = execute(raw, p, "P-S-D")
    assert baseline["metrics"]["raw_break_crossings"] == 0
    assert changed["metrics"]["raw_break_crossings"] == 1
    assert changed["metrics"]["constraint_status"] == "REJECTED_BY_CONSTRAINT"
    assert changed["stages"][0]["output"][0]["indices"] == [0, 2]
    assert changed["metrics"]["breakpoint_crossing_edges"][0]["crossed_boundary_right_indices"] == [1]
    assert changed["metrics"]["p_removed_raw_break_trigger_indices"] == [1]
    # Unsafe outcome is a validly executed negative experiment, not a broken run.
    assert review(changed, raw, p, "P-S-D")["status"] == "VERIFIED"


def test_p_immediate_denominator_is_separate_from_later_direction_deletion():
    raw = fixture([(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)])
    p = parameters(dp=.1)
    output = execute(raw, p, "S-P-D")
    metric = output["metrics"]
    assert metric["n_dp_input"] == 5
    assert metric["n_dp_output"] == 4
    assert metric["n_final"] == 3
    assert metric["dp_saving"] == pytest.approx(.2)
    assert metric["point_retention"] == pytest.approx(.6)
    assert metric["dp_max_error"] == 0
    assert metric["common_max_error"] > p["dp"]
    assert review(output, raw, p, "S-P-D")["status"] == "VERIFIED"


def test_all_filtered_remains_in_scope_and_cannot_earn_zero_error():
    raw = fixture([(0, 0), (0, 0), (0, 0)])
    p = dict(REFERENCE_PARAMETERS)
    output = execute(raw, p)
    metric = output["metrics"]
    assert output["terminal_status"] == "ALL_FILTERED"
    assert metric["n_filtered"] == 3
    assert metric["filter_reason_points"] == {"TOO_FEW_POINTS": 3, "TOO_SHORT_LENGTH": 3}
    assert metric["dp_saving"] is None
    assert metric["common_coverage"] == 0
    assert metric["common_max_error"] is None
    assert metric["common_error_reason"] == "NO_COVERED_RAW_POINTS"
    assert len(metric["common_point_errors"]) == 3
    assert all(row["error"] is None for row in metric["common_point_errors"])
    assert review(output, raw, p)["status"] == "VERIFIED"


def test_empty_input_and_singleton_have_explicit_denominators():
    empty = execute(fixture([]))
    assert empty["metrics"]["point_retention"] is None
    assert empty["metrics"]["common_coverage"] is None
    assert empty["point_actions"] == []
    assert review(empty, fixture([]))["status"] == "VERIFIED"
    one = fixture([(3, 4)])
    p = parameters(min_points=1)
    singleton = execute(one, p)
    assert singleton["metrics"]["common_coverage"] == 1
    assert singleton["metrics"]["common_max_error"] == 0
    assert singleton["metrics"]["final_length"] == 0
    assert review(singleton, one, p)["status"] == "VERIFIED"


def test_no_output_after_p_then_s_is_distinct_from_all_raw_points_filtered():
    raw = fixture([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])
    p = parameters(min_points=5)
    output = execute(raw, p, "P-S-D")
    assert output["metrics"]["n_dp_removed"] == 3
    assert output["metrics"]["n_filtered"] == 2
    assert output["metrics"]["no_output"] is True
    assert output["metrics"]["all_filtered"] is False
    assert output["terminal_status"] == "NO_OUTPUT_AFTER_STAGE_FILTERING"
    assert review(output, raw, p, "P-S-D")["status"] == "VERIFIED"


def test_finite_segment_and_no_global_nearest_shortcuts():
    raw = fixture([(0, 0), (2, 1), (1, 0)], indices=[10, 20, 30])
    final = [{"record_id": raw["record_id"], "segment_id": "known",
              "indices": [10, 30], "timestamps": [0, 2], "xy": [[0, 0], [1, 0]]}]
    metric = common_reference_metrics(raw, final)
    assert metric["common_point_errors"][1]["error"] == pytest.approx(math.sqrt(2))
    returning = fixture([(0, 0), (1, 1), (2, 0), (1, 1)])
    final[0].update(indices=[0, 2, 3], timestamps=[0, 2, 3], xy=[[0, 0], [2, 0], [1, 1]])
    metric = common_reference_metrics(returning, final)
    assert metric["common_point_errors"][1]["error"] == 1


def test_zero_dt_and_undefined_direction_are_preserved_as_reasons():
    raw = fixture([(0, 0), (0, 0), (1, 0), (1, 1), (2, 1)], [0, 0, 0, 1, 2])
    p = parameters(dp=0)
    output = execute(raw, p)
    raw_reading = output["metrics"]["stage_readings"]["raw"]
    assert raw_reading["speed_unavailable_reasons"]["ZERO_TIME_DIFFERENCE"] == 2
    assert raw_reading["same_time_different_position_edges"] == 1
    assert raw_reading["direction_unavailable_reasons"]["ZERO_DISPLACEMENT"] == 1
    assert output["metrics"]["direction_undefined_reasons"]["UNCOMPUTABLE_DIRECTION_IN_WINDOW"] >= 1
    assert review(output, raw, p)["status"] == "VERIFIED"


def test_direction_before_s_records_unprotected_cross_break_windows():
    raw = fixture([(0, 0), (0, 10), (10, 10), (10, 20), (20, 20)], [0, 1, 100, 101, 102])
    changed = execute(raw, order="D-S-P")
    baseline = execute(raw)
    assert changed["metrics"]["direction_windows_across_raw_breaks"] > 0
    assert baseline["metrics"]["direction_windows_across_raw_breaks"] == 0


@pytest.mark.parametrize("mutation", [
    lambda output: output["source_record"]["xy"][0].__setitem__(0, 99),
    lambda output: output["parameters"].__setitem__("dp", 20),
    lambda output: output.__setitem__("contract_hash", "f" * 64),
    lambda output: output["provenance"].__setitem__("code_tree_hash", "changed"),
    lambda output: output["point_actions"].pop(),
    lambda output: output["metrics"].__setitem__("common_max_error", 0),
    lambda output: output["stages"][1]["operations"][0].__setitem__("parent_hash", "wrong"),
    lambda output: output["final_segments"][0]["xy"][0].__setitem__(0, 99),
], ids=["raw-altered", "loosened-tolerance", "wrong-contract", "wrong-code-parent", "deleted-ledger",
        "forged-metric", "wrong-stage-parent", "actual-final-altered"])
def test_corrupted_actual_artifact_rejected(mutation):
    raw = fixture([(0, 0), (1, .5), (2, 0), (3, .2), (4, 0)])
    output = execute(raw)
    mutation(output)
    assert review(output, raw)["status"] == "REJECTED"


def test_simultaneous_clean_final_tampering_and_missing_reference_fail_closed():
    raw = fixture([(0, 0), (1, .5), (2, 0), (3, .2), (4, 0)])
    output = execute(raw)
    output["stages"][1]["output"][0]["xy"][1][1] = 0
    output["stages"][2]["input"][0]["xy"][1][1] = 0
    output["metrics"]["common_max_error"] = 0
    assert review(output, raw)["status"] == "REJECTED"
    assert review_record(output)["status"] == "REJECTED"


@pytest.mark.parametrize("mutation", [
    lambda output: output["records"].pop(),
    lambda output: output["records"].append(deepcopy(output["records"][0])),
    lambda output: output["summary"].__setitem__("n_input", 0),
    lambda output: output.__setitem__("input_hash", "wrong"),
], ids=["deleted-record", "extra-duplicate-record", "fake-summary", "wrong-batch-target"])
def test_complete_scope_and_batch_summary_tampering_rejected(mutation):
    raw = [fixture([(0, 0), (1, 0), (2, 0)], record_id="fixture:a"),
           fixture([(0, 0)], record_id="fixture:b")]
    p = parameters()
    output = run_batch(raw, p, contract_hash=CONTRACT_HASH, provenance=PROVENANCE)
    kwargs = {"expected_parameters": p, "expected_order": "S-D-P", "contract_hash": CONTRACT_HASH,
              "trusted_provenance": PROVENANCE}
    assert review_batch(output, raw, **kwargs)["status"] == "VERIFIED"
    mutation(output)
    assert review_batch(output, raw, **kwargs)["status"] == "REJECTED"


def test_invalid_parameters_and_duplicate_inputs_do_not_run():
    raw = fixture([(0, 0)])
    with pytest.raises(ValueError, match="SIX_PARAMETERS"):
        execute(raw, {"dp": 5})
    with pytest.raises(ValueError, match="INVALID_G2_PARAMETER"):
        execute(raw, parameters(dp=True))
    with pytest.raises(ValueError, match="DUPLICATE_INPUT_RECORD"):
        run_batch([raw, raw], parameters(), contract_hash=CONTRACT_HASH)


def test_float_allowance_cannot_silently_loosen_a_registered_parameter():
    raw = fixture([(0, 0), (1, .5), (2, 0)])
    p = parameters(dp=.5)
    output = execute(raw, p)
    output["parameters"]["dp"] += 1e-15
    assert review(output, raw, p)["status"] == "REJECTED"


@pytest.mark.parametrize("bad", [None, [], {"not_a_result": True}])
def test_malformed_review_target_is_rejected_without_crashing(bad):
    assert review_record(bad)["status"] == "REJECTED"
    assert review_batch(bad)["status"] == "REJECTED"
