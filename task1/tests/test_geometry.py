"""ENGINEERING_TEST; every input is a CONSTRUCTED_FIXTURE, never teacher data."""
from copy import deepcopy
import math

import pytest

from task1.workflow.geometry import (
    MethodUnresolved, angular_difference, denoise_trajectory, direction_candidates,
    douglas_peucker_indices, filter_segments, point_segment_distance,
    recompute_features, select_indices, split_trajectory,
)


def record(points, times=None, indices=None, record_id="CONSTRUCTED_FIXTURE"):
    return {"record_id": record_id, "xy": [list(p) for p in points],
            "timestamps": list(range(len(points))) if times is None else times,
            "indices": list(range(len(points))) if indices is None else indices}


@pytest.mark.parametrize("point,start,end,expected", [
    ((2, 1), (0, 0), (1, 0), math.sqrt(2)),
    ((3, 4), (0, 0), (0, 0), 5),
    ((2, 1), (0, 0), (0, 3), 2),
    ((-1, -1), (0, 0), (1, 0), math.sqrt(2)),
], ids=["GEO-01-finite-endpoint", "GEO-02-degenerate", "GEO-03-vertical", "GEO-04-before-start"])
def test_finite_segment_known_answers(point, start, end, expected):
    assert point_segment_distance(point, start, end) == pytest.approx(expected)


@pytest.mark.parametrize("a,b,expected", [(350, 10, 20), (10, 350, 20), (0, 180, 180),
                                         (720 + 350, -350, 20), (-10, 350, 0)],
                         ids=["wrap", "symmetric", "half-turn", "multiple-turns", "negative"])
def test_geo05_circular_difference(a, b, expected):
    assert angular_difference(a, b) == expected


def test_geo06_named_features_zero_and_negative_time():
    sample = record([(0, 0), (0, 4), (0, 4), (3, 4), (3, 0)], [0, 2, 2, 1, None])
    original = deepcopy(sample)
    features = recompute_features(sample, time_reliable=True)
    a, b, c, d = features["edges"]
    assert a["speed"] == 2 and a["direction_degrees"] == 0
    assert b["speed"] is None and b["speed_reason"] == "ZERO_TIME_DIFFERENCE"
    assert b["direction_degrees"] is None and b["direction_reason"] == "ZERO_DISPLACEMENT"
    assert c["speed"] is None and c["speed_reason"] == "NEGATIVE_TIME_DIFFERENCE"
    assert c["direction_degrees"] == 90
    assert d["speed"] is None and d["speed_reason"] == "MISSING_TIMESTAMP"
    assert features["coverage"] == {"edge_denominator": 4, "speed_computable": 1,
                                     "direction_computable": 3, "reason": None}
    assert sample == original


def test_geo07_unreliable_time_is_not_zero_speed():
    output = recompute_features(record([(0, 0), (3, 4)], [0, 5]))
    assert output["edges"][0]["dt"] == 5
    assert output["edges"][0]["speed"] is None
    assert output["edges"][0]["speed_reason"] == "UNRELIABLE_TIME"


def test_geo08_select_recomputes_adjacency_and_preserves_index_values():
    source = record([(0, 0), (3, 4), (0, 8)], [0, 1, 4], [10, 20, 30])
    source["features"] = {"edges": [{"speed": "STALE"}]}
    selected = select_indices(source, [10, 30], time_reliable=True)
    edge = selected["features"]["edges"][0]
    assert edge["dt"] == 4 and edge["distance"] == 8 and edge["speed"] == 2
    assert edge["from_index"] == 10 and edge["to_index"] == 30
    selected["xy"][0][0] = 100
    assert source["xy"][0][0] == 0
    with pytest.raises(ValueError, match="subsequence"):
        select_indices(source, [30, 10])


def test_geo09_segmentation_right_boundary_and_equal_threshold():
    sample = record([(0, 0), (3, 4), (6, 8), (20, 8), (20, 9), (20, 10)],
                    [0, 5, 10, 16, 15, 15])
    original = deepcopy(sample)
    split = split_trajectory(sample, 5, 5, time_reliable=True)
    assert [s["indices"] for s in split["segments"]] == [[0, 1, 2], [3], [4, 5]]
    assert split["boundaries"][0]["reasons"] == ["TIME_GAP", "DISTANCE_GAP"]
    assert split["boundaries"][1]["reasons"] == ["NEGATIVE_TIME_DIFFERENCE"]
    assert [i for s in split["segments"] for i in s["indices"]] == sample["indices"]
    assert split["segments"][2]["features"]["edges"][0]["speed"] is None
    assert sample == original


def test_geo10_filter_is_separate_length_is_within_each_segment():
    sample = record([(0, 0), (3, 4), (6, 8), (100, 100), (101, 100)], [0, 1, 2, 10, 11])
    split = split_trajectory(sample, 5, 20, time_reliable=True)
    filtered = filter_segments(split["segments"], 3, 10)
    assert [s["indices"] for s in filtered["kept"]] == [[0, 1, 2]]
    assert filtered["kept"][0]["features"]["length"] == 10
    assert filtered["dropped"][0]["filter_reasons"] == ["TOO_FEW_POINTS", "TOO_SHORT_LENGTH"]
    assert [s["indices"] for s in split["segments"]] == [[0, 1, 2], [3, 4]]
    assert "filter_reasons" not in split["segments"][0]


def test_geo11_time_gate_allows_independent_distance_only():
    sample = record([(0, 0), (10, 0)], [None, None])
    with pytest.raises(ValueError, match="UNRELIABLE_TIME"):
        split_trajectory(sample, 5, 5)
    with pytest.raises(ValueError, match="MISSING_TIMESTAMP"):
        split_trajectory(sample, 5, 5, time_reliable=True)
    assert len(split_trajectory(sample, None, 5)["segments"]) == 2


def test_geo12_empty_and_single_point_do_not_invent_edges():
    assert split_trajectory(record([]), 5, 5, time_reliable=True)["segments"] == []
    one = split_trajectory(record([(2, 3)]), 5, 5, time_reliable=True)["segments"]
    assert len(one) == 1 and one[0]["features"]["edges"] == []
    assert filter_segments(one, 2, 0)["dropped"][0]["filter_reasons"] == ["TOO_FEW_POINTS"]


@pytest.mark.parametrize("points,tolerance,expected", [
    ([], 1, []), ([(1, 1)], 1, [0]), ([(1, 1), (1, 1)], 1, [0, 1]),
    ([(0, 0), (0, 1), (0, 2)], .1, [0, 2]),
    ([(0, 0), (1, 0), (0, 0)], .1, [0, 1, 2]),
    ([(0, 0), (2, 1), (1, 0)], 1.1, [0, 1, 2]),
    ([(0, 0), (0, 0), (1, 0), (1, 0)], .1, [0, 3]),
    ([(0, 0), (1, 0), (2, 0)], 0, [0, 1, 2]),
    ([(0, 0), (1, 1), (2, 0)], 1, [0, 2]),
], ids=["empty", "single", "two-duplicates", "vertical-collinear", "closed-return",
        "finite-segment-counterexample", "duplicate-coordinates", "zero-identity", "threshold-equality"])
def test_geo13_dp_short_closed_duplicate_and_return_cases(points, tolerance, expected):
    assert douglas_peucker_indices(points, tolerance) == expected


def test_geo14_dp_uses_original_ids_not_coordinate_equality():
    points = [(0, 0), (0, 0), (1, 0), (1, 0)]
    assert douglas_peucker_indices(points, .1, [10, 11, 40, 80]) == [10, 80]


def test_geo15_planar_rigid_motion_and_simultaneous_scale():
    points = [(0, 0), (1, .2), (2, 2), (3, -.5), (4, 0)]
    angle = .731
    transformed = [(math.cos(angle) * x - math.sin(angle) * y + 11,
                    math.sin(angle) * x + math.cos(angle) * y - 13) for x, y in points]
    expected = douglas_peucker_indices(points, .4)
    assert douglas_peucker_indices(transformed, .4) == expected
    assert douglas_peucker_indices([(x * 13, y * 13) for x, y in points], .4 * 13) == expected
    assert point_segment_distance(transformed[1], transformed[0], transformed[-1]) == pytest.approx(
        point_segment_distance(points[1], points[0], points[-1]))


def test_geo16_direction_candidate_iteration_changes_answer_without_permitting_delete():
    sample = record([(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)])
    original = deepcopy(sample)
    simultaneous = direction_candidates(sample, 35)
    assert simultaneous["candidate_indices"] == [2]
    assert simultaneous["deleted_indices"] == []
    after_constructed_deletion = select_indices(sample, [0, 1, 3, 4])
    assert direction_candidates(after_constructed_deletion, 35)["candidate_indices"] == [1]
    assert sample == original
    with pytest.raises(MethodUnresolved, match="TEACHER_DIRECTION_RULE_UNRESOLVED"):
        denoise_trajectory(sample, 35)


def test_geo17_direction_unknown_window_and_endpoints_are_not_normal_bearings():
    sample = record([(0, 0), (0, 1), (0, 1), (1, 1), (1, 2)])
    diagnostic = direction_candidates(sample, 35)
    assert diagnostic["candidate_indices"] == []
    assert [row["reason"] for row in diagnostic["rows"]] == [
        "ENDPOINT", "UNCOMPUTABLE_DIRECTION_IN_WINDOW", "UNCOMPUTABLE_DIRECTION_IN_WINDOW",
        "MISSING_FOLLOWING_OUTGOING_EDGE", "ENDPOINT"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1, True])
def test_geo18_invalid_thresholds_rejected(bad):
    with pytest.raises(ValueError):
        douglas_peucker_indices([(0, 0), (1, 1)], bad)


def test_geo19_alignment_and_index_corruption_rejected():
    bad = record([(0, 0), (1, 1)], [0])
    with pytest.raises(ValueError, match="aligned"):
        recompute_features(bad)
    with pytest.raises(ValueError, match="original indices"):
        recompute_features(record([(0, 0), (1, 1)], indices=[0, 0]))
