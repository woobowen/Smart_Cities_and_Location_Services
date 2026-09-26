"""ENGINEERING_TEST / CONSTRUCTED_FIXTURE; independent oracle and challenge tests."""
from copy import deepcopy
import math

import pytest

from task1.workflow.evaluation import (
    assess_improvement, audit_point_accounting, floating_allowance, verify_simplification,
)
from task1.workflow.geometry import douglas_peucker_indices, filter_segments, select_indices, split_trajectory


def record(points, indices=None, record_id="CONSTRUCTED_FIXTURE"):
    return {"record_id": record_id, "xy": [list(p) for p in points],
            "timestamps": list(range(len(points))),
            "indices": list(range(len(points))) if indices is None else indices}


def codes(result):
    return {item["code"] for item in result["errors"]}


def test_eval01_finite_segment_oracle_rejects_plausible_wrong_simplification():
    source = record([(0, 0), (2, 1), (1, 0)])
    wrong = select_indices(source, [0, 2])
    result = verify_simplification(source, wrong, 1.1)
    assert result["status"] == "REJECTED"
    assert result["metrics"]["max_error"]["value"] == pytest.approx(math.sqrt(2))
    assert result["exceeding_points"][0]["index"] == 1
    correct = select_indices(source, douglas_peucker_indices(source["xy"], 1.1))
    assert verify_simplification(source, correct, 1.1)["status"] == "VERIFIED"


def test_eval02_index_interval_not_global_nearest_segment():
    source = record([(0, 0), (1, 1), (2, 0), (1, 1)])
    candidate = select_indices(source, [0, 2, 3])
    result = verify_simplification(source, candidate, .5)
    # Omitted point 1 equals later retained point 3. Global nearest would hide it.
    assert result["metrics"]["max_error"]["value"] == 1
    assert result["status"] == "REJECTED"


def test_eval03_degenerate_segment_and_original_index_mapping():
    source = record([(0, 0), (3, 4), (0, 0)], [10, 20, 30])
    result = verify_simplification(source, select_indices(source, [10, 30]), 4)
    assert result["metrics"]["max_error"]["value"] == 5
    assert result["exceeding_points"] == [{"index": 20, "error": 5}]


def test_eval04_independence_from_production_distance_and_self_report(monkeypatch):
    import task1.workflow.geometry as geometry
    monkeypatch.setattr(geometry, "point_segment_distance", lambda *_: 0)
    source = record([(0, 0), (1, 2), (2, 0)])
    candidate = select_indices(source, geometry.douglas_peucker_indices(source["xy"], .5))
    candidate["max_error"] = 0
    candidate["status"] = "QUALITY_ACCEPTED"
    result = verify_simplification(source, candidate, .5)
    assert result["status"] == "REJECTED"
    assert result["metrics"]["max_error"]["value"] == 2


@pytest.mark.parametrize("mutation,expected", [
    (lambda c: c.update(record_id="OTHER_RECORD"), "WRONG_RECORD"),
    (lambda c: c.update(parent_hash="WRONG"), "WRONG_PARENT_HASH"),
    (lambda c: c.update(indices=[0, 99]), "INDEX_NOT_IN_PARENT"),
    (lambda c: c["xy"][0].__setitem__(0, .01), "VALUE_MODIFIED"),
    (lambda c: c["timestamps"].__setitem__(0, 10), "VALUE_MODIFIED"),
    (lambda c: c.update(indices=[2, 0]), "INVALID_INDEX_ORDER"),
    (lambda c: c.pop("xy"), "MISSING_OUTPUT_OR_FIELDS"),
], ids=["wrong-record", "wrong-hash", "wrong-parent-index", "coordinate-modified",
        "time-modified", "unordered", "missing-output"])
def test_eval05_corruption_and_forged_success_rejected(mutation, expected):
    source = record([(0, 0), (1, 0), (2, 0)])
    candidate = select_indices(source, [0, 2])
    candidate["parent_hash"] = "EXPECTED"
    candidate["status"] = "VERIFIED"
    mutation(candidate)
    result = verify_simplification(source, candidate, 1, expected_parent_hash="EXPECTED")
    assert result["status"] == "REJECTED"
    assert expected in codes(result)


def test_eval06_empty_single_zero_length_metrics_have_explicit_reasons():
    empty = record([])
    result = verify_simplification(empty, deepcopy(empty), 1)
    assert result["status"] == "VERIFIED"
    assert result["metrics"]["saving"] == {"value": None, "reason": "EMPTY_REFERENCE_DENOMINATOR"}
    assert result["metrics"]["max_error"] == {"value": None, "reason": "EMPTY_REFERENCE"}
    point = record([(0, 0)])
    one = verify_simplification(point, deepcopy(point), 1)
    assert one["metrics"]["max_error"]["value"] == 0
    assert one["metrics"]["relative_length_change"] == {"value": None, "reason": "ZERO_REFERENCE_LENGTH"}
    duplicate = record([(0, 0), (0, 0), (0, 0)])
    same = verify_simplification(duplicate, select_indices(duplicate, [0, 2]), 1)
    assert same["status"] == "VERIFIED" and same["metrics"]["reference_length"]["value"] == 0
    assert same["metrics"]["relative_length_change"]["reason"] == "ZERO_REFERENCE_LENGTH"


def test_eval07_saving_uses_same_pre_simplification_input_not_raw_count():
    raw = record([(i, 0) for i in range(10)])
    before_dp = select_indices(raw, [1, 3, 6, 9])
    after_dp = select_indices(before_dp, [1, 9])
    result = verify_simplification(before_dp, after_dp, 1)
    assert result["metrics"]["saving"]["value"] == .5
    assert result["metrics"]["reference_points"]["value"] == 4
    assert result["quality_status"] == "PENDING_RESEARCH_REVIEW"
    assert "accuracy" not in result["metrics"]


def test_eval08_all_input_terminal_fates_and_record_boundaries():
    a = record([(0, 0), (1, 0), (2, 0), (50, 0)], record_id="A")
    b = record([(0, 0), (1, 1), (2, 2)], record_id="B")
    split = split_trajectory(a, None, 10)
    filtered = filter_segments(split["segments"], 2, 0)
    groups = {"filtered": filtered["dropped"], "denoised": [select_indices(b, [1])],
              "simplified": [select_indices(a, [1])],
              "retained": [select_indices(a, [0, 2]), select_indices(b, [0, 2])]}
    result = audit_point_accounting([a, b], groups)
    assert result["status"] == "VERIFIED"
    assert result["stage_points"] == {"filtered": 1, "denoised": 1, "simplified": 1, "retained": 4}
    assert result["input_points"] == 7 and result["modified_point_count"] == 0
    groups["retained"][1]["record_id"] = "A"
    bad = audit_point_accounting([a, b], groups)
    assert bad["status"] == "REJECTED"
    assert {"DUPLICATED_POINT", "MISSING_POINT"}.issubset(codes(bad))
    assert bad["count_conserved"]  # Equal aggregate counts alone cannot prove conservation.


def test_eval09_accounting_detects_undisclosed_loss_and_alteration():
    source = record([(0, 0), (1, 1)])
    kept = select_indices(source, [0])
    kept["timestamps"][0] = 999
    result = audit_point_accounting([source], {"filtered": [], "denoised": [], "simplified": [], "retained": [kept]})
    assert result["status"] == "REJECTED"
    assert codes(result) == {"VALUE_MODIFIED", "MISSING_POINT"}
    with pytest.raises(ValueError, match="all four"):
        audit_point_accounting([source], {"retained": [source]})


def test_eval10_fixed_rounding_allowance_is_separate_from_algorithm_threshold():
    source = record([(0, 0), (1, .25), (2, 0)])
    candidate = select_indices(source, [0, 2])
    expected_allowance = 64 * math.ulp(1.0) * 2
    assert floating_allowance(source["xy"], .25) == expected_allowance
    assert verify_simplification(source, candidate, .25)["status"] == "VERIFIED"
    candidate["max_error"] = 0
    rejected = verify_simplification(source, candidate, .25 - 2 * expected_allowance)
    assert rejected["status"] == "REJECTED"
    assert rejected["floating_allowance"] == expected_allowance


def test_eval11_recomputation_consistent_and_rigid_scaled_geometry():
    source = record([(0, 0), (1, .2), (2, 1), (3, .1), (4, 0)])
    indices = douglas_peucker_indices(source["xy"], .3)
    expected = verify_simplification(source, select_indices(source, indices), .3)
    assert verify_simplification(source, select_indices(source, indices), .3) == expected
    moved = deepcopy(source)
    moved["xy"] = [[10 - y, x - 4] for x, y in source["xy"]]
    rotated = verify_simplification(moved, select_indices(moved, indices), .3)
    assert rotated["status"] == expected["status"] == "VERIFIED"
    assert rotated["metrics"]["max_error"]["value"] == pytest.approx(expected["metrics"]["max_error"]["value"])
    scaled = deepcopy(source)
    scaled["xy"] = [[x * 7, y * 7] for x, y in source["xy"]]
    result = verify_simplification(scaled, select_indices(scaled, indices), 2.1)
    assert result["status"] == "VERIFIED"
    assert result["metrics"]["max_error"]["value"] == pytest.approx(expected["metrics"]["max_error"]["value"] * 7)


def test_eval12_unfrozen_improvement_contract_cannot_auto_accept():
    result = assess_improvement(hard_conditions=True)
    assert result["status"] == "PENDING_RESEARCH_REVIEW"
    assert "minimum_gain" in result["missing"]
    assert assess_improvement(hard_conditions=False)["status"] == "REJECTED"


def test_eval13_engineering_fixture_acceptance_logic_positive_and_protection_failure():
    # Artificial thresholds exercise logic only; they do not become research values.
    arguments = dict(hard_conditions=True, measured_gain=2, minimum_gain=1,
                     protection_changes={"error": .1}, allowed_degradations={"error": .2},
                     comparison_valid=True, evidence_sufficient=True)
    assert assess_improvement(**arguments)["status"] == "QUALITY_ACCEPTED"
    arguments["protection_changes"] = {"error": .3}
    assert assess_improvement(**arguments)["status"] == "REJECTED"
    arguments["allowed_degradations"] = {}
    assert assess_improvement(**arguments)["status"] == "PENDING_RESEARCH_REVIEW"


def test_eval14_nonfinite_metrics_cannot_be_verified():
    source = record([(-1e308, 0), (0, 1), (1e308, 0)])
    candidate = {"record_id": source["record_id"], "xy": [source["xy"][0], source["xy"][-1]],
                 "indices": [0, 2], "timestamps": [0, 2]}
    result = verify_simplification(source, candidate, 1)
    assert result["status"] == "REJECTED"
    assert "NUMERIC_RANGE_EXCEEDED" in codes(result)
