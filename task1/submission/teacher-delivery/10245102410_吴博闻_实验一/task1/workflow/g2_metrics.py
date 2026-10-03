"""Goal 2 common-reference readings and candidate-external processing review.

The oracle below imports no production G2 or geometry operation. It uses the
independent Goal 1 numeric primitives and reconstructs each actual stage from
trusted input. Common raw-window fidelity is distinct from a P-stage guarantee.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import math
import sys

from .evaluation import (_direct_distance, _inspect, _reference_features,
                         _reference_selection, _reference_direction,
                         floating_allowance, verify_simplification)
from .io import object_hash


REFERENCE_DT = 30
REFERENCE_DISTANCE = 400
COMMON_ERROR_BUDGET = 5
_ORDERS = ("S-D-P", "S-P-D", "D-S-P", "D-P-S", "P-S-D", "P-D-S")
_PARAMETERS = {"dt", "distance", "min_points", "min_length", "direction", "dp"}
_FLOAT = 64 * sys.float_info.epsilon


def _quantile(values, q):
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * q
    a, b = math.floor(position), math.ceil(position)
    return values[a] + (values[b] - values[a]) * (position - a)


def _select(record, indices, segment_id):
    selected = _reference_selection(record, indices, True)
    selected["segment_id"] = segment_id
    return selected


def _partition(record, dt, distance):
    features = _reference_features(record, True)
    starts, boundaries = [0], []
    for position, edge in enumerate(features["edges"], 1):
        reasons = []
        if edge["dt"] is None:
            raise ValueError("TRUSTED_TEMPORAL_INPUT_MISSING_TIME")
        if edge["dt"] < 0:
            reasons.append("NEGATIVE_TIME_DIFFERENCE")
        elif edge["dt"] > dt:
            reasons.append("TIME_GAP")
        if edge["distance"] > distance:
            reasons.append("DISTANCE_GAP")
        if reasons:
            boundaries.append({**edge, "reasons": reasons, "right_point_starts_segment": True})
            starts.append(position)
    starts.append(len(record["indices"]))
    intervals = [(a, b) for a, b in zip(starts, starts[1:]) if b > a]
    return boundaries, intervals


def common_reference_metrics(raw, final_segments):
    """Fixed raw 30/400 windows, no filtering and no candidate-derived reference.

Every raw point remains in the denominator. A point is represented only by an
identically retained point or an original-index enclosing final edge entirely
inside the same fixed raw window. No nearest-line matching or extrapolation is
allowed. Unsafe final edges are recorded independently, never used for fidelity.
    """
    boundaries, intervals = _partition(raw, REFERENCE_DT, REFERENCE_DISTANCE)
    indices = raw["indices"]
    positions = {index: pos for pos, index in enumerate(indices)}
    window_for = {indices[pos]: window for window, (a, b) in enumerate(intervals)
                  for pos in range(a, b)}
    retained, errors, crossings = set(), {}, []
    for segment in final_segments:
        retained.update(segment["indices"])
        for index in segment["indices"]:
            if index not in positions:
                raise ValueError("FINAL_INDEX_NOT_IN_COMMON_REFERENCE")
            errors[index] = 0.0
        for left, right in zip(segment["indices"], segment["indices"][1:]):
            if window_for[left] != window_for[right]:
                crossed = [edge["to_index"] for edge in boundaries if left < edge["to_index"] <= right]
                crossings.append({"segment_id": segment["segment_id"], "from_index": left,
                                  "to_index": right, "crossed_boundary_right_indices": crossed})
                continue
            a, b = positions[left], positions[right]
            for pos in range(a + 1, b):
                index = indices[pos]
                error = _direct_distance(raw["xy"][pos], raw["xy"][a], raw["xy"][b])
                # Input subsequences are disjoint; a second value would indicate
                # a malformed segment structure, not another available reference.
                if index in errors and index not in retained:
                    raise ValueError("OVERLAPPING_COMMON_REFERENCE_INTERVALS")
                errors[index] = error
    losses = [{"from_index": edge["from_index"], "to_index": edge["to_index"],
               "missing_trigger_indices": [i for i in (edge["from_index"], edge["to_index"])
                                           if i not in retained]}
              for edge in boundaries]
    values = list(errors.values())
    allowance = floating_allowance(raw["xy"], COMMON_ERROR_BUDGET)
    covered_windows = len({window_for[index] for index in errors})
    return {"common_reference_id": "RAW_WINDOWS_DT30_DISTANCE400_V1",
            "common_raw_points": len(indices), "common_covered_points": len(errors),
            "common_uncovered_points": len(indices) - len(errors),
            "common_coverage": len(errors) / len(indices) if indices else None,
            "common_coverage_reason": None if indices else "EMPTY_RAW_DENOMINATOR",
            "common_error_denominator": len(values),
            "common_max_error": max(values) if values else None,
            "common_mean_error": math.fsum(values) / len(values) if values else None,
            "common_p95_error": _quantile(values, .95),
            "common_error_reason": None if values else "NO_COVERED_RAW_POINTS",
            "common_over_5_points": sum(value > COMMON_ERROR_BUDGET + allowance for value in values),
            "common_error_budget": COMMON_ERROR_BUDGET, "common_floating_allowance": allowance,
            "common_point_errors": [{"index": index, "error": errors.get(index),
                                     "reason": None if index in errors else "UNCOVERED_OR_NO_BRACKETING_EDGE",
                                     "reference_window": window_for[index]} for index in indices],
            "raw_break_count": len(boundaries), "raw_break_crossings": len(crossings),
            "raw_breaks_crossed": len({i for edge in crossings
                                       for i in edge["crossed_boundary_right_indices"]}),
            "raw_boundaries": boundaries, "breakpoint_crossing_edges": crossings,
            "raw_break_trigger_points_removed": len({i for row in losses for i in row["missing_trigger_indices"]}),
            "boundary_trigger_losses": losses,
            "raw_windows": len(intervals), "raw_windows_covered": covered_windows,
            "reference_window_length": math.fsum(
                _reference_features(_reference_selection(raw, indices[a:b], True), True)["length"]
                for a, b in intervals)}


def _stage_reading(segments):
    features = [_reference_features(segment, True) for segment in segments]
    n_points = sum(len(segment["indices"]) for segment in segments)
    edges = [edge for feature in features for edge in feature["edges"]]
    return {"segments": len(segments), "points": n_points,
            "length": math.fsum(feature["length"] for feature in features) if n_points else None,
            "length_reason": None if n_points else "EMPTY_OUTPUT",
            "edge_denominator": len(edges),
            "speed_computable": sum(edge["speed"] is not None for edge in edges),
            "direction_computable": sum(edge["direction_degrees"] is not None for edge in edges),
            "speed_unavailable_reasons": dict(Counter(edge["speed_reason"] for edge in edges
                                                        if edge["speed_reason"] is not None)),
            "direction_unavailable_reasons": dict(Counter(edge["direction_reason"] for edge in edges
                                                            if edge["direction_reason"] is not None)),
            "negative_dt_edges": sum(edge["dt"] is not None and edge["dt"] < 0 for edge in edges),
            "zero_dt_edges": sum(edge["dt"] == 0 for edge in edges),
            "same_time_different_position_edges": sum(edge["dt"] == 0 and edge["distance"] > 0 for edge in edges),
            "zero_displacement_edges": sum(edge["distance"] == 0 for edge in edges)}


def record_metrics(trusted_record, result):
    """Describe an executed trace; this alone is not an independent acceptance."""
    raw, final = trusted_record, result["final_segments"]
    counts = Counter(row["action"] for row in result["point_actions"])
    stages = {stage["name"]: stage for stage in result["stages"]}
    p_stage = stages["P"]
    p_checks = [verify_simplification(before, after, result["parameters"]["dp"])
                for before, after in zip(p_stage["input"], p_stage["output"])]
    dp_values = [row["error"] for check in p_checks for row in check.get("error_by_original_index", [])]
    n_p_in = sum(len(segment["indices"]) for segment in p_stage["input"])
    n_p_out = sum(len(segment["indices"]) for segment in p_stage["output"])
    parts = [part for op in stages["S"]["operations"] for part in op["segments"]]
    filter_reasons = Counter(reason for part in parts for reason in part["filter_reasons"])
    filter_points = Counter()
    for part in parts:
        for reason in part["filter_reasons"]:
            filter_points[reason] += len(part["indices"])
    direction_rows = [row for op in stages["D"]["operations"] for row in op["decisions"]]
    direction_window_crossings = []
    raw_boundaries, _ = _partition(raw, REFERENCE_DT, REFERENCE_DISTANCE)
    raw_cut_ids = [edge["to_index"] for edge in raw_boundaries]
    for segment in stages["D"]["input"]:
        for pos in range(1, max(1, len(segment["indices"]) - 2)):
            window = segment["indices"][pos - 1:pos + 3]
            crossed = [cut for cut in raw_cut_ids if window[0] < cut <= window[-1]]
            if crossed:
                direction_window_crossings.append({"index": segment["indices"][pos],
                                                   "window_indices": window,
                                                   "boundary_right_indices": crossed})
    p_retained = {index for segment in p_stage["output"] for index in segment["indices"]}
    p_input = {index for segment in p_stage["input"] for index in segment["indices"]}
    p_lost_triggers = {index for edge in raw_boundaries for index in (edge["from_index"], edge["to_index"])
                       if index in p_input and index not in p_retained}
    stage_values = {"raw": _stage_reading([raw] if raw["indices"] else [])}
    for stage in result["stages"]:
        before, after = _stage_reading(stage["input"]), _stage_reading(stage["output"])
        after["length_change"] = (after["length"] - before["length"]
                                  if before["length"] is not None and after["length"] is not None else None)
        after["length_change_reason"] = (None if after["length_change"] is not None else
                                         "EMPTY_STAGE_INPUT_OR_OUTPUT")
        after["relative_length_change"] = (after["length"] / before["length"] - 1
                                           if before["length"] and after["length"] is not None else None)
        after["relative_length_change_reason"] = (None if after["relative_length_change"] is not None else
                                                  "ZERO_OR_EMPTY_STAGE_INPUT_LENGTH" if not before["length"]
                                                  else "EMPTY_STAGE_OUTPUT")
        stage_values["after_" + stage["name"]] = after
    common = common_reference_metrics(raw, final)
    n_input, n_final = len(raw["indices"]), sum(len(segment["indices"]) for segment in final)
    metrics = {"record_id": raw["record_id"], "n_input": n_input, "n_final": n_final,
               "point_retention": n_final / n_input if n_input else None,
               "point_retention_reason": None if n_input else "EMPTY_RAW_DENOMINATOR",
               "record_covered": n_final > 0,
               "all_filtered": bool(n_input and counts["filtered"] == n_input),
               "no_output": bool(n_input and not n_final),
               "n_filtered": counts["filtered"], "n_direction_removed": counts["denoised"],
               "n_dp_removed": counts["simplified"], "n_dp_input": n_p_in, "n_dp_output": n_p_out,
               "dp_saving": 1 - n_p_out / n_p_in if n_p_in else None,
               "dp_saving_reason": None if n_p_in else "EMPTY_DP_REFERENCE_DENOMINATOR",
               "dp_max_error": max(dp_values) if dp_values else None,
               "dp_mean_error": math.fsum(dp_values) / len(dp_values) if dp_values else None,
               "dp_p50_error": _quantile(dp_values, .5),
               "dp_p90_error": _quantile(dp_values, .9),
               "dp_p95_error": _quantile(dp_values, .95),
               "dp_p99_error": _quantile(dp_values, .99),
               "dp_error_reason": None if dp_values else "EMPTY_DP_REFERENCE",
               "dp_error_denominator": len(dp_values),
               "n_dp_exceedances": sum(len(check.get("exceeding_points", [])) for check in p_checks),
               "dp_checks_passed": all(check["status"] == "VERIFIED" for check in p_checks),
               "n_s_segments": len(parts), "n_filtered_segments": sum(bool(part["filter_reasons"]) for part in parts),
               "filter_reason_segments": dict(filter_reasons), "filter_reason_points": dict(filter_points),
               "direction_candidate_points": sum(row["candidate"] is True for row in direction_rows),
               "direction_undefined_points": sum(row["reason"] is not None for row in direction_rows),
               "direction_undefined_reasons": dict(Counter(row["reason"] for row in direction_rows
                                                            if row["reason"] is not None)),
               "direction_windows_across_raw_breaks": len(direction_window_crossings),
               "direction_window_crossing_details": direction_window_crossings,
               "p_removed_raw_break_trigger_points": len(p_lost_triggers),
               "p_removed_raw_break_trigger_indices": sorted(p_lost_triggers),
               "raw_length": stage_values["raw"]["length"],
               "raw_length_reason": stage_values["raw"]["length_reason"],
               "final_length": _stage_reading(final)["length"],
               "final_length_reason": _stage_reading(final)["length_reason"], "stage_readings": stage_values,
               **common}
    metrics["constraint_status"] = ("REJECTED_BY_CONSTRAINT" if metrics["raw_break_crossings"]
                                    else "NO_RAW_BREAK_CROSSING")
    return metrics


def summarize(records):
    """Point-pooled totals plus explicitly record-weighted descriptive means."""
    rows = [record["metrics"] for record in records]
    counts = ("n_input", "n_final", "n_filtered", "n_direction_removed", "n_dp_removed",
              "n_dp_input", "n_dp_output", "n_dp_exceedances", "n_s_segments", "n_filtered_segments",
              "common_raw_points", "common_covered_points", "common_uncovered_points", "common_over_5_points",
              "raw_break_count", "raw_break_crossings", "raw_breaks_crossed", "raw_break_trigger_points_removed",
              "raw_windows", "raw_windows_covered", "direction_candidate_points", "direction_undefined_points",
              "direction_windows_across_raw_breaks", "p_removed_raw_break_trigger_points")
    summary = {name: sum(row[name] for row in rows) for name in counts}
    summary.update(n_records=len(rows), n_records_covered=sum(row["record_covered"] for row in rows),
                   n_all_filtered_records=sum(row["all_filtered"] for row in rows),
                   n_no_output_records=sum(row["no_output"] for row in rows))
    for name, numerator, denominator in (
            ("point_retention", summary["n_final"], summary["n_input"]),
            ("record_coverage", summary["n_records_covered"], len(rows)),
            ("all_filtered_record_fraction", summary["n_all_filtered_records"], len(rows)),
            ("no_output_record_fraction", summary["n_no_output_records"], len(rows)),
            ("common_coverage", summary["common_covered_points"], summary["common_raw_points"])):
        summary[name] = numerator / denominator if denominator else None
        summary[name + "_reason"] = None if denominator else "EMPTY_DENOMINATOR"
    summary["dp_saving"] = (1 - summary["n_dp_output"] / summary["n_dp_input"]
                            if summary["n_dp_input"] else None)
    summary["dp_saving_reason"] = None if summary["n_dp_input"] else "EMPTY_DP_REFERENCE_DENOMINATOR"
    for name in ("dp_max_error", "common_max_error"):
        values = [row[name] for row in rows if row[name] is not None]
        summary[name] = max(values) if values else None
        summary[name + "_reason"] = None if values else "NO_AVAILABLE_REFERENCE"
    for name in ("point_retention", "dp_saving", "common_coverage", "common_max_error", "common_mean_error"):
        values = [row[name] for row in rows if row[name] is not None]
        summary["record_mean_" + name] = math.fsum(values) / len(values) if values else None
        summary["record_mean_" + name + "_denominator"] = len(values)
        summary["record_mean_" + name + "_unavailable_records"] = len(rows) - len(values)
    for name in ("filter_reason_segments", "filter_reason_points", "direction_undefined_reasons"):
        total = Counter()
        for row in rows:
            total.update(row[name])
        summary[name] = dict(total)
    summary["dp_checks_passed"] = all(row["dp_checks_passed"] for row in rows)
    summary["aggregation_unit"] = "original_record; pooled counts explicitly identified"
    return summary


def _oracle_dp(record, tolerance):
    labels, xy = record["indices"], record["xy"]
    if len(labels) <= 2 or tolerance == 0:
        return list(labels)
    retained, intervals = {0, len(labels) - 1}, [(0, len(labels) - 1)]
    while intervals:
        a, b = intervals.pop()
        if b <= a + 1:
            continue
        distances = [(pos, _direct_distance(xy[pos], xy[a], xy[b])) for pos in range(a + 1, b)]
        pos, distance = max(distances, key=lambda item: item[1])
        if distance > tolerance:
            retained.add(pos)
            intervals.extend(((a, pos), (pos, b)))
    return [labels[pos] for pos in sorted(retained)]


def _oracle_terminal(record, indices, action, reasons, position):
    chosen = _select(record, indices, record["segment_id"])
    return [{"record_id": record["record_id"], "original_index": index, "timestamp": time,
             "xy": deepcopy(xy), "action": action, "reasons": list(reasons), "stage_position": position,
             "segment_id": record["segment_id"], "parent_hash": object_hash(record)}
            for index, time, xy in zip(chosen["indices"], chosen["timestamps"], chosen["xy"])]


def _oracle_trace(raw, parameters, order):
    current = [_select(raw, raw["indices"], "record:" + raw["record_id"])] if raw["indices"] else []
    stages, ledger = [], []
    for position, name in enumerate(order.split("-"), 1):
        inputs, outputs, operations = deepcopy(current), [], []
        for segment in inputs:
            parent = object_hash(segment)
            if name == "S":
                boundaries, intervals = _partition(segment, parameters["dt"], parameters["distance"])
                parts = []
                for i, (a, b) in enumerate(intervals):
                    part = _select(segment, segment["indices"][a:b], segment["segment_id"] + "/S" + str(i))
                    part["segment_index"] = i
                    reasons = []
                    if b - a < parameters["min_points"]:
                        reasons.append("TOO_FEW_POINTS")
                    if part["features"]["length"] < parameters["min_length"]:
                        reasons.append("TOO_SHORT_LENGTH")
                    part["filter_reasons"] = reasons
                    parts.append(part)
                    if reasons:
                        ledger.extend(_oracle_terminal(part, part["indices"], "filtered", reasons, position))
                    else:
                        outputs.append(part)
                operations.append({"input_segment_id": segment["segment_id"], "parent_hash": parent,
                                   "boundaries": boundaries, "segments": parts})
            elif name == "D":
                decisions, removed = _reference_direction(segment, parameters["direction"])
                outputs.append(_select(segment, [i for i in segment["indices"] if i not in removed],
                                       segment["segment_id"]))
                operations.append({"input_segment_id": segment["segment_id"], "parent_hash": parent,
                                   "method": "single_pass_simultaneous_keep_undefined", "passes": 1,
                                   "decisions": decisions, "deleted_indices": removed})
                ledger.extend(_oracle_terminal(segment, removed, "denoised", ["DIRECTION_RULE"], position))
            else:
                ids = _oracle_dp(segment, parameters["dp"])
                output = _select(segment, ids, segment["segment_id"])
                outputs.append(output)
                operations.append({"input_segment_id": segment["segment_id"], "parent_hash": parent,
                                   "tolerance": parameters["dp"], "input_points": len(segment["indices"]),
                                   "output_points": len(ids), "dp_reference_hash": parent,
                                   "dp_output_hash": object_hash(output),
                                   "runtime_dp_check": verify_simplification(segment, output, parameters["dp"])})
                ledger.extend(_oracle_terminal(segment, [i for i in segment["indices"] if i not in ids],
                                               "simplified", ["DP_WITHIN_TOLERANCE"], position))
        stages.append({"name": name, "position": position, "input": inputs,
                       "output": deepcopy(outputs), "operations": operations})
        current = outputs
    for segment in current:
        ledger.extend(_oracle_terminal(segment, segment["indices"], "retained", ["FINAL_OUTPUT"], 4))
    ledger.sort(key=lambda row: row["original_index"])
    return stages, current, ledger


def _matches(actual, expected, field=""):
    # Stored values and parent identity never receive floating tolerance. Only
    # recomputed arithmetic does, at the existing fixed binary64 audit scale.
    if field in ("xy", "timestamps", "timestamp", "indices", "source_record", "parameters", "provenance"):
        return object_hash(actual) == object_hash(expected)
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and set(actual) == set(expected)
                and all(_matches(actual[k], v, k) for k, v in expected.items()))
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(_matches(a, b, field) for a, b in zip(actual, expected)))
    if isinstance(expected, float):
        if isinstance(actual, bool) or not isinstance(actual, (int, float)) or not math.isfinite(actual):
            return False
        absolute = _FLOAT * 360 if field.endswith("difference_degrees") else _FLOAT
        return math.isclose(actual, expected, rel_tol=_FLOAT, abs_tol=absolute)
    return type(actual) is type(expected) and actual == expected


def _trusted_parameters(parameters):
    if not isinstance(parameters, dict) or set(parameters) != _PARAMETERS:
        raise ValueError("TRUSTED_PARAMETERS_REQUIRED")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0
           for v in parameters.values()):
        raise ValueError("INVALID_TRUSTED_PARAMETERS")
    if type(parameters["min_points"]) is not int or parameters["direction"] > 180:
        raise ValueError("INVALID_TRUSTED_PARAMETER_RANGE")


def review_record(candidate, trusted_record=None, *, expected_parameters=None, expected_order=None,
                  contract_hash=None, trusted_provenance=None):
    """Fail closed without candidate-external scope, parameters and provenance."""
    errors, checked = [], []
    result = {"status": "REJECTED", "errors": errors, "checked_components": checked,
              "unchecked_components": ["source_datum", "ground_truth_quality", "model_authenticity"],
              "target_hash": None}
    try:
        result["target_hash"] = object_hash(candidate)
        if not isinstance(candidate, dict):
            raise ValueError("CANDIDATE_RECORD_REQUIRED")
        if (trusted_record is None or _inspect(trusted_record) or trusted_provenance is None
                or not isinstance(trusted_provenance, dict) or expected_order not in _ORDERS
                or not isinstance(contract_hash, str) or len(contract_hash) != 64):
            raise ValueError("TRUSTED_INPUT_CONTRACT_AND_PROVENANCE_REQUIRED")
        _trusted_parameters(expected_parameters)
        source_kind = trusted_provenance.get("source_kind")
        classification = (source_kind if source_kind in {"SYNTHETIC_COUNTEREXAMPLE", "ENGINEERING_TEST"}
                          else "CURRENT_RUN_CONDITIONAL_ANALYSIS")
        expected = {"schema_version": "G2_PROCESSING_V1", "status": "EXECUTED",
                    "classification": classification,
                    "record_id": trusted_record["record_id"], "source_record": trusted_record,
                    "source_record_hash": object_hash(trusted_record), "parameters": expected_parameters,
                    "order": expected_order, "contract_hash": contract_hash,
                    "provenance": trusted_provenance, "source_crs": "UNVERIFIED",
                    "working_unit": "conditional_working_metre", "modified_values": 0}
        for field, value in expected.items():
            if not _matches(candidate.get(field), value, field):
                errors.append({"code": "TRUST_BINDING_OR_VALUE_MISMATCH", "field": field})
        checked.extend(("trusted_input", "parameters", "order", "contract_hash", "provenance"))
        stages, final, ledger = _oracle_trace(trusted_record, expected_parameters, expected_order)
        for field, value in (("stages", stages), ("final_segments", final), ("point_actions", ledger)):
            if not _matches(candidate.get(field), value, field):
                errors.append({"code": "INDEPENDENT_TRACE_MISMATCH", "field": field})
        terminal = ("EMPTY_INPUT" if not trusted_record["indices"] else
                    "ALL_FILTERED" if all(row["action"] == "filtered" for row in ledger) else
                    "NO_OUTPUT_AFTER_STAGE_FILTERING" if not final else "PROCESSED")
        if candidate.get("terminal_status") != terminal:
            errors.append({"code": "TERMINAL_STATUS_MISMATCH"})
        checked.extend(("stage_inputs", "segmentation", "filtering", "direction_schedule", "dp_intervals",
                        "stage_features", "actual_values", "terminal_ledger", "final_segments"))
        oracle = {**expected, "stages": stages, "final_segments": final, "point_actions": ledger}
        metrics = record_metrics(trusted_record, oracle)
        if not _matches(candidate.get("metrics"), metrics):
            errors.append({"code": "METRICS_MISMATCH"})
        checked.extend(("dp_denominator", "common_raw_reference", "coverage", "raw_break_protection", "metrics"))
        result["trusted_reference_hash"] = object_hash(trusted_record)
        result["contract_hash"] = contract_hash
        result["record_id"] = trusted_record["record_id"]
        result["status"] = "REJECTED" if errors else "VERIFIED"
    except (ValueError, KeyError, TypeError, IndexError, ArithmeticError) as exc:
        errors.append({"code": "REVIEW_INPUT_OR_TRACE_ERROR", "reason": str(exc)})
    return result


def review_batch(candidate, trusted_records=None, *, expected_parameters=None, expected_order=None,
                 contract_hash=None, trusted_provenance=None):
    errors, receipts = [], []
    result = {"status": "REJECTED", "target_hash": None, "errors": errors,
              "record_receipts": receipts, "checked_components": [],
              "unchecked_components": ["source_datum", "ground_truth_quality", "model_authenticity"]}
    try:
        result["target_hash"] = object_hash(candidate)
        if not isinstance(candidate, dict):
            raise ValueError("CANDIDATE_BATCH_REQUIRED")
        if not isinstance(trusted_records, list):
            raise ValueError("TRUSTED_COMPLETE_RECORD_LIST_REQUIRED")
        ids = [record["record_id"] for record in trusted_records]
        if len(set(ids)) != len(ids):
            raise ValueError("DUPLICATE_TRUSTED_RECORD")
        _trusted_parameters(expected_parameters)
        if (trusted_provenance is None or expected_order not in _ORDERS
                or not isinstance(contract_hash, str) or len(contract_hash) != 64):
            raise ValueError("TRUSTED_CONTRACT_AND_PROVENANCE_REQUIRED")
        bindings = {"record_scope": ids, "input_hash": object_hash(trusted_records),
                    "parameters": expected_parameters, "order": expected_order,
                    "contract_hash": contract_hash, "provenance": trusted_provenance,
                    "schema_version": "G2_PROCESSING_V1", "status": "EXECUTED"}
        for field, expected in bindings.items():
            if not _matches(candidate.get(field), expected, field):
                errors.append({"code": "BATCH_BINDING_MISMATCH", "field": field})
        observed = [record["record_id"] for record in candidate["records"]]
        if observed != ids:
            raise ValueError("EXACT_ORDERED_RECORD_SCOPE_MISMATCH")
        for record, trusted in zip(candidate["records"], trusted_records):
            receipt = review_record(record, trusted, expected_parameters=expected_parameters,
                                    expected_order=expected_order, contract_hash=contract_hash,
                                    trusted_provenance=trusted_provenance)
            receipts.append(receipt)
            if receipt["status"] != "VERIFIED":
                errors.append({"code": "RECORD_REVIEW_FAILED", "record_id": trusted["record_id"]})
        if not _matches(candidate.get("summary"), summarize(candidate["records"])):
            errors.append({"code": "SUMMARY_MISMATCH"})
        result["checked_components"] = ["complete_record_scope", "record_reviews", "summary", "version_bindings"]
        result["status"] = "REJECTED" if errors else "VERIFIED"
    except (ValueError, KeyError, TypeError, IndexError, ArithmeticError) as exc:
        errors.append({"code": "REVIEW_INPUT_OR_TRACE_ERROR", "reason": str(exc)})
    return result
