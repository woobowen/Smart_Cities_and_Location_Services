"""Independent G2 coordinate checks and actual-trace threshold sensitivity.

The alternate projections are diagnostics under the same mathematical ellipsoid.
They neither identify the source datum nor replace the frozen ENU processing.
No candidate, model episode, or memory write is performed by this program.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pyproj

from task1.workflow.coordinates import working_xy
from task1.workflow.io import ROOT, digest, now, object_hash, read_json, write_json
from task1.workflow.g2_selection import config_id


EV = ROOT / "task1/evidence/goal2"
PARTITIONS = ("PILOT_REGRESSION", "DEMO_MEMORY", "DEVELOPMENT", "G2_EVAL")


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _distribution(values, empty_reason="EMPTY_DENOMINATOR"):
    values = np.asarray(values, dtype=float)
    _require(bool(np.isfinite(values).all()), "NONFINITE_COMPARISON_VALUE")
    if not len(values):
        return {"count": 0, "min": None, "mean": None, "q50": None,
                "q90": None, "q95": None, "q99": None, "max": None,
                "reason": empty_reason}
    qs = np.quantile(values, [0, .5, .9, .95, .99, 1], method="linear")
    return dict(count=len(values), min=float(qs[0]), mean=float(values.mean()),
                q50=float(qs[1]), q90=float(qs[2]), q95=float(qs[3]),
                q99=float(qs[4]), max=float(qs[5]), reason=None)


def _combined_distribution(blocks, empty_reason="EMPTY_DENOMINATOR"):
    return _distribution(np.concatenate(blocks) if blocks else [], empty_reason)


def _distance(point, start, end):
    """Independent finite-segment distance; endpoint distance when degenerate."""
    px, py = point
    ax, ay = start
    dx, dy = end[0] - ax, end[1] - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return math.hypot(px - ax, py - ay)
    along = ((px - ax) * dx + (py - ay) * dy) / (length * length)
    along = min(1.0, max(0.0, along))
    return math.hypot(px - ax - along * dx, py - ay - along * dy)


def _allowance(points, tolerance):
    values = np.asarray(points, dtype=float)
    absolute = float(np.max(np.abs(values))) if values.size else 0.0
    extent = float(np.ptp(values, axis=0).max()) if len(values) else 0.0
    return 64 * np.finfo(float).eps * max(1.0, absolute, extent, tolerance)


def _headings(points, indices, threshold):
    bearings = []
    for i, j in zip(indices, indices[1:]):
        dx, dy = points[j][0] - points[i][0], points[j][1] - points[i][1]
        bearings.append(None if dx == dy == 0 else math.degrees(math.atan2(dx, dy)) % 360)
    rows = []
    for position, index in enumerate(indices):
        reason = None
        if position == 0 or position == len(indices) - 1:
            reason = "ENDPOINT"
        elif position + 1 >= len(bearings):
            reason = "MISSING_FOLLOWING_OUTGOING_EDGE"
        elif any(v is None for v in bearings[position - 1:position + 2]):
            reason = "UNCOMPUTABLE_DIRECTION_IN_WINDOW"
        angles = None
        if reason is None:
            angles = [abs((bearings[position] - bearings[k] + 180) % 360 - 180)
                      for k in (position - 1, position + 1)]
        rows.append({"index": index, "reason": reason, "angles": angles,
                     "delete": None if reason else all(v > threshold for v in angles)})
    return rows


def _dp_indices(points, indices, tolerance):
    if len(indices) <= 2 or tolerance == 0:
        return list(indices)
    kept, pending = {0, len(indices) - 1}, [(0, len(indices) - 1)]
    while pending:
        first, last = pending.pop()
        if last - first <= 1:
            continue
        distances = [(_distance(points[indices[k]], points[indices[first]], points[indices[last]]), k)
                     for k in range(first + 1, last)]
        maximum = max(d for d, _ in distances)
        chosen = next(k for d, k in distances if d == maximum)
        if maximum > tolerance:
            kept.add(chosen)
            pending.extend(((first, chosen), (chosen, last)))
    return [indices[k] for k in sorted(kept)]


def _interval_errors(points, indices, kept):
    if not indices:
        _require(not kept, "NONEMPTY_OUTPUT_OF_EMPTY_DP_INPUT")
        return []
    _require(bool(kept) and kept[0] == indices[0] and kept[-1] == indices[-1],
             "DP_ENDPOINTS_OR_OUTPUT_MISSING")
    positions = {index: position for position, index in enumerate(indices)}
    _require(kept == sorted(set(kept)) and all(i in positions for i in kept),
             "INVALID_DP_ORIGINAL_INDICES")
    values = {index: {"index": index, "left_index": index, "right_index": index, "error": 0.0}
              for index in kept}
    for first, last in zip(kept, kept[1:]):
        for index in indices[positions[first] + 1:positions[last]]:
            values[index] = {"index": index, "left_index": first, "right_index": last,
                             "error": _distance(points[index], points[first], points[last])}
    _require(set(values) == set(indices), "DP_ERROR_COVERAGE_INCOMPLETE")
    return [values[index] for index in indices]


def coordinate_context(raw_scope, model, distance_thresholds=(), working_records=None):
    """Read-only complete scope: independent PROJ, all within-record Geod pairs.

    `working_records` permits explicit known-answer corruption tests. Production
    derives the same frozen ENU formula from raw coordinates and model parameters.
    """
    a, rf = model["semi_major_m"], model["inverse_flattening"]
    lon0, lat0 = model["origin_lon_degrees"], model["origin_lat_degrees"]
    transformer = pyproj.Transformer.from_pipeline(
        f"+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad "
        f"+step +proj=cart +a={a} +rf={rf} "
        f"+step +proj=topocentric +a={a} +rf={rf} +lon_0={lon0} +lat_0={lat0} +h_0=0")
    alternate = pyproj.Proj(proj="aeqd", a=a, rf=rf, lon_0=lon0, lat_0=lat0, units="m")
    geod = pyproj.Geod(a=a, rf=rf)
    records, enu, aeqd, rows, edges, problems = {}, {}, {}, [], [], []
    coordinate_errors, aeqd_offsets, pair_absolute, pair_relative = [], [], [], []
    pair_enu_distances, pair_geod_distances = [], []
    maxima = {"coordinate_error_m": None, "pair_absolute_difference_m": None,
              "pair_relative_difference": None, "aeqd_coordinate_offset_m": None}
    zero_pairs = 0

    def extreme(key, value, witness):
        if maxima[key] is None or value > maxima[key]["value"]:
            maxima[key] = {"value": float(value), **witness}

    for rid, (times, coordinates) in raw_scope.items():
        _require(len(times) == len(coordinates), "RAW_TIME_COORDINATE_ALIGNMENT")
        record = (deepcopy(working_records[rid]) if working_records is not None else
                  {"record_id": rid, "indices": list(range(len(times))),
                   "timestamps": deepcopy(times), "xy": working_xy(coordinates, model)})
        _require(record["indices"] == list(range(len(times))) and record["timestamps"] == times,
                 "WORKING_RECORD_RAW_IDENTITY_MISMATCH")
        records[rid] = record
        xy = np.asarray(record["xy"], dtype=float).reshape((-1, 2))
        lonlat = np.asarray(coordinates, dtype=float).reshape((-1, 2))
        if len(coordinates):
            east, north, _ = transformer.transform(lonlat[:, 0], lonlat[:, 1],
                                                   np.zeros(len(lonlat)), errcheck=True)
            projected = np.column_stack((east, north))
            ax, ay = alternate(lonlat[:, 0], lonlat[:, 1], errcheck=True)
            alt = np.column_stack((ax, ay))
        else:
            projected, alt = np.empty((0, 2)), np.empty((0, 2))
        enu[rid], aeqd[rid] = record["xy"], alt.tolist()
        error = np.linalg.norm(xy - projected, axis=1)
        offset = np.linalg.norm(xy - alt, axis=1)
        radii = np.linalg.norm(xy, axis=1)
        coordinate_errors.extend(error.tolist()); aeqd_offsets.extend(offset.tolist())
        for i in range(len(times)):
            extreme("coordinate_error_m", error[i], {"record_id": rid, "index": i})
            extreme("aeqd_coordinate_offset_m", offset[i], {"record_id": rid, "index": i})
            if error[i] > model["coordinate_crosscheck_absolute_tolerance_m"]:
                problems.append({"code": "PROJ_IMPLEMENTATION_MISMATCH", "record_id": rid,
                                 "index": i, "error_m": float(error[i])})
            if radii[i] > model["domain_max_radius_m"]:
                problems.append({"code": "OUTSIDE_FROZEN_G2_DOMAIN", "record_id": rid,
                                 "index": i, "radius_m": float(radii[i])})
        left, right = np.triu_indices(len(times), 1)
        if len(left):
            _, _, ground = geod.inv(lonlat[left, 0].tolist(), lonlat[left, 1].tolist(),
                                    lonlat[right, 0].tolist(), lonlat[right, 1].tolist())
            ground = np.asarray(ground)
            planar = np.linalg.norm(xy[right] - xy[left], axis=1)
            absolute = np.abs(planar - ground)
            positive = ground > 0
            relative = absolute[positive] / ground[positive]
            zero_pairs += int((~positive).sum())
            pair_absolute.append(absolute); pair_relative.append(relative)
            pair_enu_distances.append(planar); pair_geod_distances.append(ground)
            k = int(np.argmax(absolute))
            extreme("pair_absolute_difference_m", absolute[k],
                    {"record_id": rid, "left_index": int(left[k]), "right_index": int(right[k]),
                     "enu_m": float(planar[k]), "geod_m": float(ground[k])})
            if len(relative):
                k = np.flatnonzero(positive)[int(np.argmax(relative))]
                extreme("pair_relative_difference", absolute[k] / ground[k],
                        {"record_id": rid, "left_index": int(left[k]), "right_index": int(right[k]),
                         "enu_m": float(planar[k]), "geod_m": float(ground[k])})
            adjacent = np.flatnonzero(right == left + 1)
            for k in adjacent:
                i, j = int(left[k]), int(right[k])
                alt_distance = math.dist(alt[i], alt[j])
                edges.append({"record_id": rid, "left_index": i, "right_index": j,
                              "enu_m": float(planar[k]), "geod_m": float(ground[k]),
                              "aeqd_m": alt_distance, "absolute_difference_m": float(absolute[k]),
                              "relative_difference": None if ground[k] == 0 else float(absolute[k] / ground[k]),
                              "relative_reason": "ZERO_GEOD_REFERENCE" if ground[k] == 0 else None,
                              "threshold_differences": [
                                  {"threshold_m": t, "enu_cut": bool(planar[k] > t),
                                   "geod_cut": bool(ground[k] > t), "aeqd_cut": alt_distance > t}
                                  for t in distance_thresholds
                                  if not (bool(planar[k] > t) == bool(ground[k] > t) == (alt_distance > t))]})
        else:
            absolute, relative = np.array([]), np.array([])
            planar, ground = np.array([]), np.array([])
        rows.append({"record_id": rid, "point_count": len(times),
                     "pair_count": len(left), "raw_edge_count": max(0, len(times) - 1),
                     "max_enu_radius_m": float(radii.max()) if len(radii) else None,
                     "coordinate_error_m": _distribution(error),
                     "aeqd_coordinate_offset_m": _distribution(offset),
                     "pair_enu_distance_m": _distribution(planar),
                     "pair_geod_distance_m": _distribution(ground),
                     "pair_absolute_difference_m": _distribution(absolute),
                     "pair_relative_difference": _distribution(relative, "NO_POSITIVE_GEOD_DISTANCES")})
    summary = {"classification": "CONDITIONAL_MODEL_IMPLEMENTATION_AND_APPROXIMATION_CHECK",
               "source_crs": "UNVERIFIED", "source_datum_proven": False,
               "implementation_status": "REJECTED" if problems else "VERIFIED",
               "implementation_failures": problems, "record_ids": list(raw_scope),
               "records_checked": len(raw_scope), "points_checked": len(coordinate_errors),
               "within_record_pairs_checked": sum(len(v) for v in pair_absolute), "raw_edges_checked": len(edges),
               "coordinate_error_m": _distribution(coordinate_errors),
               "aeqd_coordinate_offset_m": _distribution(aeqd_offsets),
               "pair_enu_distance_m": _combined_distribution(pair_enu_distances),
               "pair_geod_distance_m": _combined_distribution(pair_geod_distances),
               "pair_absolute_difference_m": _combined_distribution(pair_absolute),
               "pair_relative_difference": _combined_distribution(pair_relative, "NO_POSITIVE_GEOD_DISTANCES"),
               "raw_edge_enu_distance_m": _distribution([e["enu_m"] for e in edges]),
               "raw_edge_geod_distance_m": _distribution([e["geod_m"] for e in edges]),
               "raw_edge_absolute_difference_m": _distribution([e["absolute_difference_m"] for e in edges]),
               "zero_geod_pair_denominator": zero_pairs,
               "zero_geod_pair_relative_value": None,
               "zero_geod_pair_reason": "ZERO_GEOD_REFERENCE",
               "extrema_witnesses": maxima, "per_record": rows,
               "raw_edge_grid_threshold_differences": sum(len(e["threshold_differences"]) for e in edges),
               "independent_library": {"pyproj": pyproj.__version__, "PROJ": pyproj.proj_version_str},
               "interpretation": "Approximation differences do not fail the ENU implementation check; no G1 approximation bound is reused."}
    return {"raw": raw_scope, "model": model, "records": records, "enu": enu,
            "aeqd": aeqd, "geod": geod, "summary": summary, "raw_edge_rows": edges}


def inspect_trace(candidate, context):
    """Inspect actual stage indices. Returns all differences, never a new output."""
    rid, p = candidate["record_id"], candidate["parameters"]
    enu, alt = context["enu"][rid], context["aeqd"][rid]
    times, lonlat = context["raw"][rid]
    counts, differences = Counter(), []
    maxima = {}
    _require([s["name"] for s in candidate["stages"]] == candidate["order"].split("-"),
             "TRACE_ORDER_MISMATCH")

    def report(kind, stage, **details):
        differences.append({"kind": kind, "record_id": rid, "config_id": config_id(p),
                            "parameters": p, "order": candidate["order"],
                            "stage_position": stage["position"], **details})

    def extreme(name, value, stage, **witness):
        if name not in maxima or value > maxima[name]["value"]:
            maxima[name] = {"value": value, "record_id": rid,
                            "stage_position": stage["position"], **witness}

    for stage in candidate["stages"]:
        _require(len(stage["input"]) == len(stage["operations"]), "TRACE_OPERATION_SCOPE_MISMATCH")
        if stage["name"] == "P":
            _require(len(stage["input"]) == len(stage["output"]), "P_INPUT_OUTPUT_SEGMENTS_MISMATCH")
        for j, (segment, operation) in enumerate(zip(stage["input"], stage["operations"])):
            ids = segment["indices"]
            _require(operation["parent_hash"] == object_hash(segment), "TRACE_PARENT_HASH_MISMATCH")
            _require(segment["xy"] == [enu[i] for i in ids] and segment["timestamps"] == [times[i] for i in ids],
                     "TRACE_RAW_VALUES_OR_COORDINATES_MISMATCH")
            common = {"input_segment_id": segment["segment_id"], "input_indices": ids}
            if stage["name"] == "S":
                for a, b in zip(ids, ids[1:]):
                    values = {"enu": math.dist(enu[a], enu[b]), "aeqd": math.dist(alt[a], alt[b]),
                              "geod": context["geod"].inv(*lonlat[a], *lonlat[b])[2]}
                    flags = {key: value > p["distance"] for key, value in values.items()}
                    counts["S_distance_edges"] += 1
                    extreme("S_max_abs_aeqd_distance_change_m", abs(values["aeqd"] - values["enu"]), stage,
                            left_index=a, right_index=b, threshold_m=p["distance"])
                    extreme("S_max_abs_geod_distance_change_m", abs(values["geod"] - values["enu"]), stage,
                            left_index=a, right_index=b, threshold_m=p["distance"])
                    if len(set(flags.values())) > 1:
                        temporal = times[b] - times[a] > p["dt"] or times[b] - times[a] < 0
                        report("S_DISTANCE_THRESHOLD", stage, **common, left_index=a, right_index=b,
                               threshold_m=p["distance"], distances_m=values, strict_greater=flags,
                               temporal_cut=temporal, full_cut={k: temporal or v for k, v in flags.items()})
                for part in operation["segments"]:
                    original = part["indices"]
                    values = {key: math.fsum(math.dist(points[a], points[b]) for a, b in zip(original, original[1:]))
                              for key, points in (("enu", enu), ("aeqd", alt))}
                    values["geod"] = math.fsum(context["geod"].inv(*lonlat[a], *lonlat[b])[2]
                                                for a, b in zip(original, original[1:]))
                    flags = {k: v < p["min_length"] for k, v in values.items()}
                    counts["S_actual_segments_length"] += 1
                    extreme("S_max_abs_geod_length_change_m", abs(values["geod"] - values["enu"]), stage,
                            segment_indices=original, threshold_m=p["min_length"])
                    if len(set(flags.values())) > 1:
                        report("S_LENGTH_THRESHOLD", stage, **common, segment_indices=original,
                               threshold_m=p["min_length"], lengths_m=values, strict_less=flags,
                               too_few_points=len(original) < p["min_points"])
            elif stage["name"] == "D":
                left, right = _headings(enu, ids, p["direction"]), _headings(alt, ids, p["direction"])
                _require([v["index"] for v in operation["decisions"]] == ids, "D_DECISION_SCOPE_MISMATCH")
                for en, ae, actual in zip(left, right, operation["decisions"]):
                    _require(actual["candidate"] == en["delete"] and actual["reason"] == en["reason"],
                             "ACTUAL_D_PREDICATE_MISMATCH")
                    counts["D_windows"] += 1
                    counts["D_undefined_windows"] += en["reason"] is not None
                    if en["angles"] is not None and ae["angles"] is not None:
                        extreme("D_max_abs_aeqd_angle_change_degrees",
                                max(abs(a - b) for a, b in zip(en["angles"], ae["angles"])), stage,
                                original_index=en["index"], threshold_degrees=p["direction"])
                    if en["delete"] != ae["delete"] or en["reason"] != ae["reason"]:
                        report("D_DIRECTION_THRESHOLD_OR_UNDEFINED", stage, **common,
                               original_index=en["index"], threshold_degrees=p["direction"],
                               enu=en, aeqd=ae, actual_deleted=en["index"] in operation["deleted_indices"])
            else:
                output = stage["output"][j]
                kept = output["indices"]
                _require(operation["tolerance"] == p["dp"] and operation["dp_output_hash"] == object_hash(output),
                         "P_PARAMETER_OR_OUTPUT_BINDING_MISMATCH")
                left, right = _interval_errors(enu, ids, kept), _interval_errors(alt, ids, kept)
                eps_en = _allowance([enu[i] for i in ids], p["dp"])
                eps_ae = _allowance([alt[i] for i in ids], p["dp"])
                counts["P_complete_input_points"] += len(ids)
                counts["P_immediate_output_points"] += len(kept)
                counts["P_segments"] += 1
                for en, ae in zip(left, right):
                    _require(en["error"] <= p["dp"] + eps_en, "ACTUAL_ENU_DP_GUARANTEE_FAILED")
                    extreme("P_max_aeqd_error_of_actual_output_m", ae["error"], stage,
                            original_index=en["index"], threshold_m=p["dp"])
                    extreme("P_max_abs_aeqd_error_change_m", abs(ae["error"] - en["error"]), stage,
                            original_index=en["index"], threshold_m=p["dp"])
                    strict_en, strict_ae = en["error"] > p["dp"], ae["error"] > p["dp"]
                    audit_en, audit_ae = en["error"] > p["dp"] + eps_en, ae["error"] > p["dp"] + eps_ae
                    if strict_en != strict_ae or audit_en != audit_ae:
                        report("P_FIXED_OUTPUT_INTERVAL_THRESHOLD", stage, **common,
                               original_index=en["index"], left_index=en["left_index"], right_index=en["right_index"],
                               threshold_m=p["dp"], enu_error_m=en["error"], aeqd_error_m=ae["error"],
                               enu_audit_allowance_m=eps_en, aeqd_audit_allowance_m=eps_ae,
                               strict_exceeds={"enu": strict_en, "aeqd": strict_ae},
                               audit_exceeds={"enu": audit_en, "aeqd": audit_ae})
                alt_kept = _dp_indices(alt, ids, p["dp"])
                if alt_kept != kept:
                    report("P_KEEP_SET_SENSITIVITY", stage, **common, threshold_m=p["dp"],
                           enu_immediate_output_indices=kept, aeqd_diagnostic_output_indices=alt_kept,
                           enu_max_error_m=max((e["error"] for e in left), default=None),
                           aeqd_error_of_actual_output_m=max((e["error"] for e in right), default=None))
    return {"counts": dict(counts), "differences": differences, "extrema": maxima,
            "difference_counts": dict(Counter(d["kind"] for d in differences))}


def _bound_file(directory, name, expected_hash):
    path = (directory / name).resolve()
    _require(path.is_relative_to(directory.resolve()) and path.is_file(), "OUTSIDE_OR_MISSING_ARTIFACT")
    _require(isinstance(expected_hash, str) and digest(path) == expected_hash, "ARTIFACT_HASH_MISMATCH:" + name)
    return path


def _read_gzip(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def inspect_run(run_dir, context, contract, contract_hash, split, split_hash, emit):
    """Bind manifest -> actual batch/mode trace -> trusted raw before inspection."""
    run_dir = Path(run_dir).resolve()
    manifest_path = run_dir / "manifest.json"
    manifest = read_json(manifest_path)
    manifest_hash = digest(manifest_path)
    _require(manifest["status"] in {"REVIEW_PENDING", "VERIFIED"}, "INCOMPLETE_OR_INVALIDATED_RUN")
    partition = manifest["partition"]
    _require(partition in PARTITIONS, "UNAUTHORIZED_OR_RESERVED_RUN_PARTITION")
    _require(manifest["raw_sha256"] == contract["raw_sha256"] == split["raw_sha256"], "RUN_RAW_MISMATCH")
    _require(manifest["contract_sha256"] == contract_hash and manifest["split_sha256"] == split_hash,
             "RUN_CONTRACT_OR_SPLIT_MISMATCH")
    _require(manifest["input_ids"] == split["splits"][partition], "RUN_COMPLETE_SCOPE_MISMATCH")
    _require(bool(manifest["source_hashes"]), "SOURCE_BINDINGS_REQUIRED")
    _require(manifest["source_tree_sha256"] == object_hash(manifest["source_hashes"]), "SOURCE_TREE_HASH_MISMATCH")
    for name, expected in manifest["source_hashes"].items():
        _bound_file(ROOT, name, expected)
    counts, difference_counts, checked_ids, bindings = Counter(), Counter(), set(), []
    maxima = {}
    thresholds = {key: set() for key in ("distance", "min_length", "direction", "dp")}
    trace_count = 0

    def consume(candidate, parameters, order, source_binding, expected_provenance, review=None):
        nonlocal trace_count
        rid = candidate["record_id"]
        _require(rid in manifest["input_ids"] and rid in context["records"], "TRACE_OUT_OF_SCOPE")
        _require(candidate["parameters"] == parameters and candidate["order"] == order,
                 "TRACE_PARAMETERS_OR_ORDER_MISMATCH")
        _require(set(parameters) == set(contract["parameter_grids"])
                 and all(value in contract["parameter_grids"][key] for key, value in parameters.items()),
                 "TRACE_OUTSIDE_PARAMETER_DOMAIN")
        _require(candidate["contract_hash"] == contract_hash, "TRACE_CONTRACT_MISMATCH")
        _require(candidate["source_record"] == context["records"][rid]
                 and candidate["source_record_hash"] == object_hash(context["records"][rid]),
                 "TRACE_TRUSTED_RAW_MISMATCH")
        _require(candidate["provenance"] == expected_provenance, "TRACE_PROVENANCE_MISMATCH")
        if review is not None:
            _require(review["status"] == "VERIFIED" and review["target_hash"] == object_hash(candidate),
                     "REVIEW_TARGET_OR_STATUS_MISMATCH")
        inspected = inspect_trace(candidate, context)
        trace_count += 1; checked_ids.add(rid)
        counts.update(inspected["counts"]); difference_counts.update(inspected["difference_counts"])
        for name, value in inspected["extrema"].items():
            if name not in maxima or value["value"] > maxima[name]["value"]:
                maxima[name] = {**value, "config_id": config_id(parameters), "order": order,
                                "source_binding": source_binding}
        for name in thresholds:
            thresholds[name].add(parameters[name])
        for difference in inspected["differences"]:
            emit({"run_id": manifest["run_id"], "partition": partition,
                  "source_binding": source_binding, "candidate_hash": object_hash(candidate), **difference})

    def provenance(ids):
        return {"goal_id": manifest["goal_id"], "run_id": manifest["run_id"],
                "raw_sha256": manifest["raw_sha256"], "partition": partition,
                "scope_sha256": object_hash(ids), "source_tree_sha256": manifest["source_tree_sha256"],
                "contract_sha256": contract_hash, "split_sha256": split_hash,
                "adapter_version": contract["model"]["adapter_version"]}

    for entry in manifest["artifacts"].values():
        path = _bound_file(run_dir, entry["file"], entry["sha256"])
        review_path = _bound_file(run_dir, entry["review_file"], entry["review_sha256"])
        batch, review = _read_gzip(path), read_json(review_path)
        ids = entry["input_ids"]
        _require(ids == batch["record_scope"] == [r["record_id"] for r in batch["records"]]
                 and len(ids) == len(set(ids)) and set(ids) <= set(manifest["input_ids"]), "BATCH_EXACT_SCOPE_MISMATCH")
        _require(entry["config_id"] == config_id(entry["parameters"]), "BATCH_CONFIG_ID_MISMATCH")
        _require(review["status"] == "VERIFIED" and review["target_hash"] == object_hash(batch), "BATCH_REVIEW_TARGET_MISMATCH")
        _require(batch["parameters"] == entry["parameters"] and batch["order"] == entry["order"]
                 and batch["contract_hash"] == contract_hash and batch["provenance"] == provenance(ids), "BATCH_BINDING_MISMATCH")
        row_reviews = {r["record_id"]: r for r in review["record_receipts"]}
        _require(set(row_reviews) == set(ids), "BATCH_REVIEW_SCOPE_MISMATCH")
        binding = {"file": entry["file"], "sha256": entry["sha256"],
                   "config_id": entry["config_id"], "order": entry["order"], "input_ids": ids}
        bindings.append(binding)
        for candidate in batch["records"]:
            consume(candidate, entry["parameters"], entry["order"], binding,
                    provenance(ids), row_reviews[candidate["record_id"]])
    for registered in manifest.get("mode_episodes", []):
        episode_path = _bound_file(run_dir, registered["path"], registered["sha256"])
        episode = read_json(episode_path)
        _require(episode["contract_sha256"] == contract_hash
                 and episode["source_tree_sha256"] == manifest["source_tree_sha256"], "EPISODE_VERSION_MISMATCH")
        _require(episode["input_ids"] == registered["input_ids"] == [r["record_id"] for r in episode["records"]],
                 "EPISODE_EXACT_SCOPE_MISMATCH")
        _require(len(episode["input_ids"]) == len(set(episode["input_ids"])), "DUPLICATE_EPISODE_RECORD")
        _require(episode["mode"] == registered["mode"] and episode["episode"] == registered["episode"],
                 "EPISODE_REGISTRATION_MISMATCH")
        for row in episode["records"]:
            rid = row["record_id"]
            filename = f"{rid}_candidate_traces.json.gz"
            path = _bound_file(episode_path.parent, filename, episode.get("artifact_hashes", {}).get(filename))
            payload = _read_gzip(path)
            _require(set(payload["results"]) == set(row["candidate_ids"]) == set(payload["reviews"]),
                     "MODE_CANDIDATE_SET_MISMATCH")
            for cid, candidate in payload["results"].items():
                _require(cid == config_id(candidate["parameters"]) and candidate["record_id"] == rid,
                         "MODE_CONFIG_OR_RECORD_MISMATCH")
                binding = {"episode_file": registered["path"], "episode_sha256": registered["sha256"],
                           "trace_file": str(path.relative_to(run_dir)), "trace_sha256": digest(path),
                           "episode_id": episode["episode_id"], "mode": episode["mode"], "config_id": cid}
                expected = {**provenance([rid]), "episode_id": episode["episode_id"]}
                consume(candidate, candidate["parameters"], "S-D-P", binding, expected, payload["reviews"][cid])
            bindings.append({"episode_file": registered["path"], "record_id": rid,
                             "trace_file": str(path.relative_to(run_dir)), "trace_sha256": digest(path),
                             "candidate_ids": row["candidate_ids"]})
    _require(digest(manifest_path) == manifest_hash, "MANIFEST_CHANGED_DURING_SENSITIVITY_CHECK")
    return {"run_id": manifest["run_id"], "manifest_sha256": manifest_hash,
            "partition": partition, "run_source_tree_sha256": manifest["source_tree_sha256"],
            "record_scope": manifest["input_ids"], "actual_trace_record_ids": sorted(checked_ids),
            "unchecked_record_ids": sorted(set(manifest["input_ids"]) - checked_ids),
            "actual_traces_checked": trace_count, "stage_check_counts": dict(counts),
            "actual_threshold_values": {k: sorted(v) for k, v in thresholds.items()},
            "sensitivity_difference_counts": dict(difference_counts), "artifact_bindings": bindings,
            "measured_extrema": maxima,
            "run_status_at_read": manifest["status"]}


def _gzip_jsonl(path):
    raw = Path(path).open("xb")
    stream = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
    return raw, stream


def generate_report(run_dirs, output_dir, *, contract_path=ROOT / "task1/config/goal2/contract.json",
                    split_path=EV / "data/split_manifest.json", coordinates_only=False):
    started, clock = now(), time.perf_counter()
    contract, split = read_json(contract_path), read_json(split_path)
    contract_hash, split_hash = digest(contract_path), digest(split_path)
    _require(bool(run_dirs) or coordinates_only, "ACTUAL_RUN_REQUIRED_OR_EXPLICIT_COORDINATES_ONLY")
    ids = [rid for name in PARTITIONS for rid in split["splits"][name]]
    _require({name: len(split["splits"][name]) for name in PARTITIONS}
             == {"PILOT_REGRESSION": 7, "DEMO_MEMORY": 60, "DEVELOPMENT": 120, "G2_EVAL": 120},
             "REGISTERED_PARTITION_SIZES_REQUIRED")
    _require(len(ids) == len(set(ids)) == 307, "EXACT_307_SELECTED_RECORDS_REQUIRED")
    _require(not (set(ids) & set(split["splits"]["G3_RESERVED"])), "RESERVED_SCOPE_LEAKAGE")
    raw_path = ROOT / contract["raw_path"]
    _require(digest(raw_path) == contract["raw_sha256"] == split["raw_sha256"], "RAW_HASH_MISMATCH")
    complete_raw = read_json(raw_path)
    scope = {rid: complete_raw[rid] for rid in ids}
    del complete_raw
    context = coordinate_context(scope, contract["model"], contract["parameter_grids"]["distance"])
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    write_json(output_dir / "coordinate_checks.json", context["summary"], exclusive=True)
    raw_stream, edge_stream = _gzip_jsonl(output_dir / "raw_edges.jsonl.gz")
    try:
        for edge in context["raw_edge_rows"]:
            edge_stream.write((json.dumps(edge, ensure_ascii=False, allow_nan=False) + "\n").encode())
    finally:
        edge_stream.close(); raw_stream.close()
    raw_stream, diff_stream = _gzip_jsonl(output_dir / "all_threshold_differences.jsonl.gz")
    reports = []
    try:
        for directory in run_dirs:
            report = inspect_run(directory, context, contract, contract_hash, split, split_hash,
                                 lambda row: diff_stream.write((json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n").encode()))
            reports.append(report)
            print(json.dumps({"run_id": report["run_id"], "traces": report["actual_traces_checked"],
                              "differences": report["sensitivity_difference_counts"]}), flush=True)
    except Exception as exc:
        write_json(output_dir / "failure.json", {"status": "REJECTED", "started_at": started,
                   "failed_at": now(), "reason": str(exc), "completed_run_checks": reports}, exclusive=True)
        raise
    finally:
        diff_stream.close(); raw_stream.close()
    _require(digest(contract_path) == contract_hash and digest(split_path) == split_hash,
             "PARENT_VERSION_CHANGED_DURING_CHECK")
    summary = {"goal_id": contract["goal_id"], "classification": "CURRENT_RUN_CONDITIONAL_ANALYSIS",
               "status": context["summary"]["implementation_status"], "started_at": started,
               "ended_at": now(), "elapsed_seconds": time.perf_counter() - clock,
               "command": list(sys.argv), "raw_sha256": contract["raw_sha256"],
               "contract_sha256": contract_hash, "split_sha256": split_hash,
               "source_sha256": digest(__file__), "source_crs": "UNVERIFIED",
               "source_datum_proven": False, "new_candidate_evaluations": 0,
               "new_model_calls": 0, "memory_writes": 0, "selected_record_count": len(ids),
               "raw_scope_hash": object_hash(scope), "runs": reports,
               "processing_sensitivity_status": "NOT_RUN_COORDINATES_ONLY" if coordinates_only and not reports else "CHECKED_REGISTERED_TRACES",
               "checked_components": ["all307_selected_coordinates", "independent_PROJ", "all_selected_within_record_Geod_pairs",
                                      "raw_edge_grid_thresholds", "actual_trace_S_lengths_distances", "actual_trace_D_windows", "actual_trace_P_immediate_intervals"],
               "unchecked_components": ["source_datum", "ground_truth_accuracy", "unprovided_run_traces", "independent_final_C_acceptance"],
               "limitations": ["Geod and AEQD use the same assumed ellipsoid and center; agreement cannot establish source datum.",
                               "All actual stage indices are frozen ENU-chain inputs. Alternate predicates and DP index sets are sensitivity diagnostics, not alternate cleaning results or selection feedback.",
                               "Approximation threshold differences are retained and limit robustness claims, not a reason to replace records or change the coordinate model.",
                               "Only listed manifests/configurations/episodes were checked; omitted runs are not certified."],
               "artifacts": {name: {"path": name, "sha256": digest(output_dir / name)}
                             for name in ("coordinate_checks.json", "raw_edges.jsonl.gz", "all_threshold_differences.jsonl.gz")}}
    if coordinates_only and not reports:
        summary["checked_components"] = summary["checked_components"][:4]
        summary["unchecked_components"].append("all_processing_threshold_sensitivity")
    write_json(output_dir / "summary.json", summary, exclusive=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, action="append", default=[], help="Actual G2 run; may repeat")
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory, normally under goal2/coordinate_sensitivity")
    parser.add_argument("--coordinates-only", action="store_true", help="Explicit raw preflight, not processing-threshold verification")
    args = parser.parse_args()
    result = generate_report(args.run_dir, args.output_dir, coordinates_only=args.coordinates_only)
    print(json.dumps({"status": result["status"], "output_dir": str(args.output_dir),
                      "selected_records": result["selected_record_count"], "runs_checked": len(result["runs"])}))
    return 0 if result["status"] == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
