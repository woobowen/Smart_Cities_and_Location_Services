"""Known-answer sensitivity and binding tests; no teacher candidates are run."""
from copy import deepcopy
import gzip
import json
import math

import pyproj
import pytest

from task1.scripts.goal2_coordinate_sensitivity import (
    _distance, _headings, _interval_errors, coordinate_context, inspect_run, inspect_trace)
from task1.workflow.g2_pipeline import REFERENCE_PARAMETERS, run_batch, run_record
from task1.workflow.g2_metrics import review_batch, review_record
from task1.workflow.g2_selection import config_id
from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json


def planar_fixture(points, *, alternate=None, order="S-D-P", **changes):
    """Explicit synthetic planes to isolate threshold semantics, not projection accuracy."""
    rid = "fixture:coordinate-sensitivity"
    record = {"record_id": rid, "indices": list(range(len(points))),
              "timestamps": [i * 10 for i in range(len(points))], "xy": [list(p) for p in points]}
    parameters = {**REFERENCE_PARAMETERS, "min_points": 2, "min_length": 0, **changes}
    candidate = run_record(record, parameters, order, contract_hash="a" * 64,
                           provenance={"source_kind": "SYNTHETIC_COUNTEREXAMPLE"})
    context = {"enu": {rid: record["xy"]}, "aeqd": {rid: alternate or record["xy"]},
               "raw": {rid: [record["timestamps"], [[x / 111320, y / 111320] for x, y in points]]},
               "geod": pyproj.Geod(a=6378137, rf=298.257223563)}
    return candidate, context


def test_independent_coordinate_formula_expands_domain_without_claiming_accuracy():
    model = read_json(ROOT / "task1/config/goal2/contract.json")["model"]
    raw = {"fixture:wide": [[0, 1, 2], [[121.8, 31.7], [121.8, 31.7], [121.801, 31.701]]]}
    context = coordinate_context(raw, model, [95, 400])
    summary = context["summary"]
    assert summary["implementation_status"] == "VERIFIED"
    assert summary["records_checked"] == 1
    assert summary["points_checked"] == 3
    assert summary["within_record_pairs_checked"] == 3
    assert summary["raw_edges_checked"] == 2
    assert summary["coordinate_error_m"]["max"] < 1e-6
    assert summary["per_record"][0]["max_enu_radius_m"] > 40000
    assert summary["zero_geod_pair_denominator"] == 1
    assert summary["pair_relative_difference"]["count"] == 2
    assert summary["source_datum_proven"] is False
    assert summary["aeqd_coordinate_offset_m"]["max"] > 0


def test_coordinate_formula_corruption_is_not_dismissed_as_model_sensitivity():
    model = read_json(ROOT / "task1/config/goal2/contract.json")["model"]
    raw = {"fixture:bad": [[0, 1], [[121.34, 31.35], [121.341, 31.351]]]}
    context = coordinate_context(raw, model)
    changed = deepcopy(context["records"])
    changed["fixture:bad"]["xy"][1][0] += .001
    checked = coordinate_context(raw, model, working_records=changed)["summary"]
    assert checked["implementation_status"] == "REJECTED"
    assert checked["implementation_failures"][0]["code"] == "PROJ_IMPLEMENTATION_MISMATCH"
    assert checked["implementation_failures"][0]["index"] == 1


def test_empty_coordinate_scope_has_null_distributions_and_no_division_by_zero():
    model = read_json(ROOT / "task1/config/goal2/contract.json")["model"]
    summary = coordinate_context({"fixture:empty": [[], []]}, model)["summary"]
    assert summary["within_record_pairs_checked"] == 0
    assert summary["pair_relative_difference"]["max"] is None
    assert summary["pair_relative_difference"]["reason"] == "NO_POSITIVE_GEOD_DISTANCES"


def test_finite_segment_rejects_infinite_line_shortcut_and_covers_original_indices():
    points = [[0, 0], [2, 1], [1, 0]]
    assert _distance(points[1], points[0], points[2]) == pytest.approx(math.sqrt(2))
    assert _distance([3, 4], [0, 0], [0, 0]) == 5
    errors = _interval_errors(points, [0, 1, 2], [0, 2])
    assert len(errors) == 3 and errors[1]["error"] == pytest.approx(math.sqrt(2))
    with pytest.raises(ValueError, match="DP_ENDPOINTS"):
        _interval_errors(points, [0, 1, 2], [0, 1])


def test_dp_equality_and_near_threshold_difference_is_saved_not_rejected():
    candidate, context = planar_fixture([(0, 0), (1, 1), (2, 0)], dp=1,
                                        alternate=[[0, 0], [1, 1.01], [2, 0]])
    inspected = inspect_trace(candidate, context)
    kinds = {r["kind"] for r in inspected["differences"]}
    assert "P_FIXED_OUTPUT_INTERVAL_THRESHOLD" in kinds
    assert "P_KEEP_SET_SENSITIVITY" in kinds
    row = next(r for r in inspected["differences"] if r["kind"] == "P_FIXED_OUTPUT_INTERVAL_THRESHOLD")
    assert row["original_index"] == 1
    assert row["threshold_m"] == 1
    assert row["strict_exceeds"] == {"enu": False, "aeqd": True}
    assert candidate["stages"][-1]["output"][0]["indices"] == [0, 2]


def test_sensitivity_uses_p_immediate_output_before_later_d_deletion():
    candidate, context = planar_fixture([(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)],
                                        order="S-P-D", dp=.1)
    inspected = inspect_trace(candidate, context)
    assert candidate["metrics"]["n_final"] == 3
    assert inspected["counts"]["P_complete_input_points"] == 5
    assert inspected["counts"]["P_immediate_output_points"] == 4
    assert not any(r["kind"].startswith("P_") for r in inspected["differences"])


def test_s_distance_and_length_strict_threshold_differences_keep_actual_ids():
    candidate, context = planar_fixture([(0, 0), (400, 0)], dp=0,
                                        alternate=[[0, 0], [401, 0]])
    inspected = inspect_trace(candidate, context)
    row = next(r for r in inspected["differences"] if r["kind"] == "S_DISTANCE_THRESHOLD")
    assert row["left_index"] == 0 and row["right_index"] == 1
    assert row["strict_greater"]["enu"] is False
    assert row["strict_greater"]["aeqd"] is True
    candidate, context = planar_fixture([(0, 0), (65, 0)], dp=0, min_length=65,
                                        alternate=[[0, 0], [64.9, 0]])
    inspected = inspect_trace(candidate, context)
    row = next(r for r in inspected["differences"] if r["kind"] == "S_LENGTH_THRESHOLD")
    assert row["segment_indices"] == [0, 1]
    assert row["strict_less"]["enu"] is False and row["strict_less"]["aeqd"] is True


def test_d_direction_threshold_and_undefined_windows_are_distinguished():
    def turn(angle):
        x, y = 10 * math.sin(math.radians(angle)), 10 + 10 * math.cos(math.radians(angle))
        return [[0, 0], [0, 10], [x, y], [x, y + 10]]
    candidate, context = planar_fixture(turn(40), alternate=turn(30), dp=0)
    inspected = inspect_trace(candidate, context)
    row = next(r for r in inspected["differences"] if r["kind"] == "D_DIRECTION_THRESHOLD_OR_UNDEFINED")
    assert row["original_index"] == 1
    assert row["enu"]["delete"] is True and row["aeqd"]["delete"] is False
    assert row["actual_deleted"] is True
    windows = _headings([[0, 0], [0, 0], [1, 0], [1, 1]], [0, 1, 2, 3], 35)
    assert windows[1]["reason"] == "UNCOMPUTABLE_DIRECTION_IN_WINDOW"
    assert windows[2]["reason"] == "MISSING_FOLLOWING_OUTGOING_EDGE"


def _write_compressed(path, value):
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False)


def bound_fixture(tmp_path, *, mode=False):
    contract = read_json(ROOT / "task1/config/goal2/contract.json")
    rid = "fixture:bound"
    raw = {rid: [[0, 10, 20, 30, 40], [[121.34 + i * .0001, 31.35 + (i % 2) * .00005] for i in range(5)]]}
    context = coordinate_context(raw, contract["model"])
    contract["raw_sha256"] = object_hash(raw)
    contract_hash = object_hash(contract)
    split = {"raw_sha256": object_hash(raw), "splits": {"DEVELOPMENT": [rid]}}
    split_hash = object_hash(split)
    sources = {"task1/workflow/g2_pipeline.py": digest(ROOT / "task1/workflow/g2_pipeline.py")}
    source_tree = object_hash(sources)
    manifest = {"goal_id": contract["goal_id"], "run_id": "ENGINEERING_TEST",
                "partition": "DEVELOPMENT", "input_ids": [rid], "status": "REVIEW_PENDING",
                "raw_sha256": object_hash(raw), "contract_sha256": contract_hash,
                "split_sha256": split_hash, "source_hashes": sources, "source_tree_sha256": source_tree,
                "artifacts": {}}
    provenance = {"goal_id": contract["goal_id"], "run_id": "ENGINEERING_TEST",
                  "raw_sha256": object_hash(raw), "partition": "DEVELOPMENT", "scope_sha256": object_hash([rid]),
                  "source_tree_sha256": source_tree, "contract_sha256": contract_hash,
                  "split_sha256": split_hash, "adapter_version": contract["model"]["adapter_version"]}
    parameters = {**REFERENCE_PARAMETERS, "min_length": 0}
    cid = config_id(parameters)
    records = [context["records"][rid]]
    if not mode:
        batch = run_batch(records, parameters, contract_hash=contract_hash, provenance=provenance)
        review = review_batch(batch, records, expected_parameters=parameters, expected_order="S-D-P",
                              contract_hash=contract_hash, trusted_provenance=provenance)
        assert review["status"] == "VERIFIED"
        _write_compressed(tmp_path / "batch.json.gz", batch)
        write_json(tmp_path / "review.json", review)
        entry = {"file": "batch.json.gz", "sha256": digest(tmp_path / "batch.json.gz"),
                 "review_file": "review.json", "review_sha256": digest(tmp_path / "review.json"),
                 "input_ids": [rid], "config_id": cid, "parameters": parameters, "order": "S-D-P"}
        manifest["artifacts"] = {"fixture": entry}
    else:
        provenance["episode_id"] = "fixture:episode"
        candidate = run_record(records[0], parameters, contract_hash=contract_hash, provenance=provenance)
        review = review_record(candidate, records[0], expected_parameters=parameters, expected_order="S-D-P",
                               contract_hash=contract_hash, trusted_provenance=provenance)
        filename = f"{rid}_candidate_traces.json.gz"
        _write_compressed(tmp_path / filename, {"results": {cid: candidate}, "reviews": {cid: review}})
        episode = {"mode": "search-only", "episode": 1, "episode_id": "fixture:episode",
                   "contract_sha256": contract_hash, "source_tree_sha256": source_tree,
                   "input_ids": [rid], "records": [{"record_id": rid, "candidate_ids": [cid]}],
                   "artifact_hashes": {filename: digest(tmp_path / filename)}}
        write_json(tmp_path / "episode.json", episode)
        manifest["mode_episodes"] = [{"path": "episode.json", "sha256": digest(tmp_path / "episode.json"),
                                      "input_ids": [rid], "mode": "search-only", "episode": 1}]
    write_json(tmp_path / "manifest.json", manifest)
    return context, contract, contract_hash, split, split_hash


def test_actual_manifest_batch_trace_and_review_binding(tmp_path):
    args = bound_fixture(tmp_path)
    emitted = []
    report = inspect_run(tmp_path, *args, emitted.append)
    assert report["actual_traces_checked"] == 1
    assert report["actual_trace_record_ids"] == ["fixture:bound"]
    assert report["unchecked_record_ids"] == []
    assert report["actual_threshold_values"]["min_length"] == [0]
    manifest = read_json(tmp_path / "manifest.json")
    manifest["artifacts"]["fixture"]["parameters"]["dp"] = 20
    write_json(tmp_path / "manifest.json", manifest)
    with pytest.raises(ValueError, match="CONFIG_ID_MISMATCH"):
        inspect_run(tmp_path, *args, emitted.append)


def test_manifest_hash_and_reserved_partition_cannot_be_bypassed(tmp_path):
    args = bound_fixture(tmp_path)
    manifest = read_json(tmp_path / "manifest.json")
    manifest["partition"] = "G3_RESERVED"
    write_json(tmp_path / "manifest.json", manifest)
    with pytest.raises(ValueError, match="RESERVED_RUN_PARTITION"):
        inspect_run(tmp_path, *args, lambda _: None)
    manifest["partition"] = "DEVELOPMENT"
    manifest["artifacts"]["fixture"]["sha256"] = "f" * 64
    write_json(tmp_path / "manifest.json", manifest)
    with pytest.raises(ValueError, match="ARTIFACT_HASH_MISMATCH"):
        inspect_run(tmp_path, *args, lambda _: None)


def test_mode_trace_requires_controller_registered_file_hash(tmp_path):
    args = bound_fixture(tmp_path, mode=True)
    report = inspect_run(tmp_path, *args, lambda _: None)
    assert report["actual_traces_checked"] == 1
    episode = read_json(tmp_path / "episode.json")
    episode["artifact_hashes"] = {}
    write_json(tmp_path / "episode.json", episode)
    manifest = read_json(tmp_path / "manifest.json")
    manifest["mode_episodes"][0]["sha256"] = digest(tmp_path / "episode.json")
    write_json(tmp_path / "manifest.json", manifest)
    with pytest.raises(ValueError, match="ARTIFACT_HASH_MISMATCH"):
        inspect_run(tmp_path, *args, lambda _: None)


def test_changed_stage_parent_is_rejected_before_sensitivity_interpretation():
    candidate, context = planar_fixture([(0, 0), (1, 1), (2, 0)], dp=1)
    candidate["stages"][0]["operations"][0]["parent_hash"] = "b" * 64
    with pytest.raises(ValueError, match="TRACE_PARENT_HASH_MISMATCH"):
        inspect_trace(candidate, context)
