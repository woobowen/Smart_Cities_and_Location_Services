"""C-only numerical oracle. No production processing/metric imports.

The caller supplies trusted raw data, frozen parameters/order and a target.
Coordinates are checked against PROJ before actual binary64 working coordinates
are used for an independent Decimal finite-segment calculation. This preserves
the frozen arithmetic domain without treating source coordinates as truth.
"""
from collections import Counter
from decimal import Decimal, localcontext
import math
import sys

import pyproj


def finite_distance(p, a, b):
    with localcontext() as context:
        context.prec = 55
        p, a, b = [tuple(Decimal(x) for x in q) for q in (p, a, b)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        wx, wy = p[0] - a[0], p[1] - a[1]
        length2 = vx * vx + vy * vy
        u = min(Decimal(1), max(Decimal(0), (vx * wx + vy * wy) / length2)) if length2 else Decimal(0)
        return float(((wx - u * vx) ** 2 + (wy - u * vy) ** 2).sqrt())


def dp(xy, indices, tolerance):
    if len(indices) <= 2 or tolerance == 0:
        return list(indices)
    errors = [finite_distance(xy[i], xy[indices[0]], xy[indices[-1]]) for i in indices[1:-1]]
    maximum = max(errors)
    if maximum <= tolerance:
        return [indices[0], indices[-1]]
    middle = errors.index(maximum) + 1
    return dp(xy, indices[:middle + 1], tolerance)[:-1] + dp(xy, indices[middle:], tolerance)


def directions(xy, indices, threshold):
    h = [None if xy[i] == xy[j] else math.degrees(math.atan2(xy[j][0] - xy[i][0], xy[j][1] - xy[i][1])) % 360
         for i, j in zip(indices, indices[1:])]
    result = []
    for pos, index in enumerate(indices):
        reason = ("ENDPOINT" if pos == 0 or pos == len(indices) - 1 else
                  "MISSING_FOLLOWING_OUTGOING_EDGE" if pos + 1 >= len(h) else
                  "UNCOMPUTABLE_DIRECTION_IN_WINDOW" if None in h[pos - 1:pos + 2] else None)
        deltas = None if reason else [min(abs(h[pos] - h[k]), 360 - abs(h[pos] - h[k])) for k in (pos - 1, pos + 1)]
        result.append({"index": index, "reason": reason,
                       "candidate": None if reason else all(v > threshold for v in deltas), "deltas": deltas})
    return result


def partition(times, xy, indices, dt, distance):
    groups, boundaries, current = [], [], []
    for pos, index in enumerate(indices):
        reasons = []
        if pos:
            left = indices[pos - 1]
            delta = times[index] - times[left]
            if delta < 0:
                reasons.append("NEGATIVE_TIME_DIFFERENCE")
            elif delta > dt:
                reasons.append("TIME_GAP")
            if math.dist(xy[left], xy[index]) > distance:
                reasons.append("DISTANCE_GAP")
        if reasons:
            groups.append(current)
            current = []
            boundaries.append({"from_index": left, "to_index": index, "reasons": reasons})
        current.append(index)
    if current:
        groups.append(current)
    return groups, boundaries


def length(xy, indices):
    return math.fsum(math.dist(xy[i], xy[j]) for i, j in zip(indices, indices[1:]))


def allowance(xy, tolerance=0):
    scale = max([1, tolerance] + [abs(x) for p in xy for x in p] +
                [max(p[d] for p in xy) - min(p[d] for p in xy) for d in (0, 1)] if xy else [1, tolerance])
    return 64 * sys.float_info.epsilon * scale


def common_reference(times, xy, final_groups):
    windows, breaks = partition(times, xy, list(range(len(times))), 30, 400)
    window_of = {i: w for w, group in enumerate(windows) for i in group}
    covered, errors, crossed = set(), {}, []
    retained = {i for group in final_groups for i in group}
    for i in retained:
        covered.add(i)
        errors[i] = 0.0
    for group in final_groups:
        for left, right in zip(group, group[1:]):
            if window_of[left] != window_of[right]:
                crossed.append((left, right))
                continue
            for i in range(left, right + 1):
                covered.add(i)
                errors[i] = finite_distance(xy[i], xy[left], xy[right])
    return {"windows": windows, "breaks": breaks, "covered_indices": sorted(covered),
            "uncovered_indices": sorted(set(range(len(times))) - covered),
            "retained_indices": sorted(retained), "errors": errors, "crossed_edges": crossed,
            "max_error": max(errors.values()) if errors else None,
            "mean_error": math.fsum(errors.values()) / len(errors) if errors else None}


def audit_record(target, trusted_raw, parameters, order, model, contract_hash):
    errors, checks = [], []
    def check(name, condition, details=None):
        checks.append(name)
        if not condition:
            errors.append({"check": name, "detail": details})
    times, angular = trusted_raw
    source = target["source_record"]
    xy = source["xy"]
    rid = target["record_id"]
    check("source_alignment", source["record_id"] == rid and source["indices"] == list(range(len(times)))
          and source["timestamps"] == times and len(xy) == len(times))
    check("parameters", target["parameters"] == parameters)
    check("order", target["order"] == order)
    check("contract", target["contract_hash"] == contract_hash)
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    expected_xy = [transform.transform(*p, model["assumed_height_m"])[:2] for p in angular]
    coordinate_error = max((math.dist(a, b) for a, b in zip(xy, expected_xy)), default=0.0)
    check("independent_PROJ_coordinates", coordinate_error <= 1e-6, coordinate_error)
    check("source_claim", target["source_crs"] == "UNVERIFIED" and target["modified_values"] == 0)
    tolerance = allowance(xy, parameters["dp"])

    def record_values(actual, expected, label):
        check(label + ":indices", actual["indices"] == expected)
        check(label + ":unchanged_values", actual["timestamps"] == [times[i] for i in expected]
              and actual["xy"] == [xy[i] for i in expected])
        features = actual["features"]
        edges = features["edges"]
        pairs = list(zip(expected, expected[1:]))
        check(label + ":edge_scope", [(x["from_index"], x["to_index"]) for x in edges] == pairs)
        for pos, (edge, (i, j)) in enumerate(zip(edges, pairs)):
            delta = times[j] - times[i]
            distance = math.dist(xy[i], xy[j])
            heading = None if distance == 0 else math.degrees(math.atan2(xy[j][0] - xy[i][0], xy[j][1] - xy[i][1])) % 360
            check(label + f":edge:{pos}", edge["dt"] == delta and abs(edge["distance"] - distance) <= tolerance
                  and (edge["speed"] is None if delta <= 0 else abs(edge["speed"] - distance / delta) <= tolerance)
                  and (edge["direction_degrees"] is None if heading is None else
                       abs(edge["direction_degrees"] - heading) <= 64 * sys.float_info.epsilon * 360))
        check(label + ":length", abs(features["length"] - length(xy, expected)) <= tolerance)
        check(label + ":coverage", features["coverage"]["edge_denominator"] == len(pairs)
              and features["coverage"]["speed_computable"] == sum(times[j] > times[i] for i, j in pairs)
              and features["coverage"]["direction_computable"] == sum(xy[i] != xy[j] for i, j in pairs))

    current = [list(range(len(times)))] if times else []
    fates = {}
    dp_intervals = []
    check("stage_count", len(target["stages"]) == 3)
    for position, (name, stage) in enumerate(zip(order.split("-"), target["stages"]), 1):
        check(f"stage{position}:identity", stage["name"] == name and stage["position"] == position)
        check(f"stage{position}:input_scope", len(stage["input"]) == len(current) == len(stage["operations"]))
        outputs = []
        for group_number, (indices, actual_input, operation) in enumerate(zip(current, stage["input"], stage["operations"])):
            label = f"stage{position}:group{group_number}"
            record_values(actual_input, indices, label + ":input")
            if name == "S":
                groups, boundaries = partition(times, xy, indices, parameters["dt"], parameters["distance"])
                check(label + ":boundaries", [{key: b[key] for key in ("from_index", "to_index", "reasons")}
                                              for b in operation["boundaries"]] == boundaries)
                check(label + ":all_segments", len(operation["segments"]) == len(groups))
                for number, (group, part) in enumerate(zip(groups, operation["segments"])):
                    reasons = ([] if len(group) >= parameters["min_points"] else ["TOO_FEW_POINTS"])
                    if length(xy, group) < parameters["min_length"]:
                        reasons.append("TOO_SHORT_LENGTH")
                    record_values(part, group, label + f":part{number}")
                    check(label + f":filter{number}", part["filter_reasons"] == reasons)
                    if reasons:
                        fates.update((i, ("filtered", position, reasons)) for i in group)
                    else:
                        outputs.append(group)
            elif name == "D":
                expected = directions(xy, indices, parameters["direction"])
                deleted = [row["index"] for row in expected if row["candidate"] is True]
                check(label + ":one_pass", operation["passes"] == 1 and operation["method"] == "single_pass_simultaneous_keep_undefined")
                check(label + ":deleted", operation["deleted_indices"] == deleted)
                check(label + ":decisions", len(operation["decisions"]) == len(expected) and all(
                    (a["index"], a["reason"], a["candidate"]) == (b["index"], b["reason"], b["candidate"])
                    for a, b in zip(operation["decisions"], expected)))
                fates.update((i, ("denoised", position, ["DIRECTION_RULE"])) for i in deleted)
                outputs.append([i for i in indices if i not in deleted])
            else:
                kept = dp(xy, indices, parameters["dp"])
                residual = {i: 0.0 for i in kept}
                for left, right in zip(kept, kept[1:]):
                    residual.update((i, finite_distance(xy[i], xy[left], xy[right])) for i in indices if left < i < right)
                maximum = max(residual.values(), default=None)
                check(label + ":dp_certificate", len(residual) == len(indices) and (maximum is None or maximum <= parameters["dp"] + tolerance))
                check(label + ":dp_counts", operation["input_points"] == len(indices) and operation["output_points"] == len(kept)
                      and operation["tolerance"] == parameters["dp"])
                fates.update((i, ("simplified", position, ["DP_WITHIN_TOLERANCE"])) for i in indices if i not in kept)
                outputs.append(kept)
                dp_intervals.append({"input_points": len(indices), "output_points": len(kept), "maximum": maximum,
                                     "errors": residual})
        check(f"stage{position}:output_scope", len(stage["output"]) == len(outputs))
        for number, (actual, group) in enumerate(zip(stage["output"], outputs)):
            record_values(actual, group, f"stage{position}:output{number}")
        current = outputs
    check("final_scope", len(target["final_segments"]) == len(current))
    for number, (actual, group) in enumerate(zip(target["final_segments"], current)):
        record_values(actual, group, f"final{number}")
        fates.update((i, ("retained", 4, ["FINAL_OUTPUT"])) for i in group)
    check("ledger_complete_unique", Counter(row["original_index"] for row in target["point_actions"]) == Counter(range(len(times))))
    for row in target["point_actions"]:
        i = row["original_index"]
        check(f"ledger:{i}", row["record_id"] == rid and row["timestamp"] == times[i] and row["xy"] == xy[i]
              and (row["action"], row["stage_position"], row["reasons"]) == fates[i])
    common = common_reference(times, xy, current)
    metrics = target["metrics"]
    expected_counts = {
        "n_input": len(times), "n_final": sum(map(len, current)),
        "n_filtered": sum(value[0] == "filtered" for value in fates.values()),
        "n_direction_removed": sum(value[0] == "denoised" for value in fates.values()),
        "n_dp_removed": sum(value[0] == "simplified" for value in fates.values()),
        "n_dp_input": sum(row["input_points"] for row in dp_intervals),
        "n_dp_output": sum(row["output_points"] for row in dp_intervals),
        "common_raw_points": len(times), "common_covered_points": len(common["covered_indices"]),
        "common_uncovered_points": len(common["uncovered_indices"]),
        "common_error_denominator": len(common["errors"]),
        "raw_break_count": len(common["breaks"]), "raw_break_crossings": len(common["crossed_edges"]),
    }
    for name, expected in expected_counts.items():
        check("metric:" + name, type(metrics[name]) is int and metrics[name] == expected)
    expected_max_dp = max((row["maximum"] for row in dp_intervals if row["maximum"] is not None), default=None)
    expected_reals = {"dp_max_error": expected_max_dp, "common_max_error": common["max_error"],
                      "common_mean_error": common["mean_error"],
                      "dp_saving": 1 - expected_counts["n_dp_output"] / expected_counts["n_dp_input"]
                      if expected_counts["n_dp_input"] else None,
                      "common_coverage": len(common["covered_indices"]) / len(times) if times else None}
    for name, expected in expected_reals.items():
        check("metric:" + name, metrics[name] is None if expected is None else
              metrics[name] is not None and abs(metrics[name] - expected) <= tolerance)
    check("metric:per_point_scope", [row["index"] for row in metrics["common_point_errors"]] == list(range(len(times))))
    for row in metrics["common_point_errors"]:
        index = row["index"]
        expected = common["errors"].get(index)
        check(f"metric:common_point:{index}", row["error"] is None and bool(row["reason"]) if expected is None else
              row["error"] is not None and abs(row["error"] - expected) <= tolerance and row["reason"] is None)
    return {"status": "REJECTED" if errors else "VERIFIED", "record_id": rid, "checks": len(checks),
            "errors": errors, "coordinate_max_error_m": coordinate_error,
            "final_groups": current, "fate_counts": dict(Counter(value[0] for value in fates.values())),
            "dp_reference_points": sum(row["input_points"] for row in dp_intervals),
            "dp_output_points": sum(row["output_points"] for row in dp_intervals),
            "dp_maximum": max((row["maximum"] for row in dp_intervals if row["maximum"] is not None), default=None),
            "common_reference": common,
            "checked_components": ["trusted_raw_alignment", "PROJ_coordinates", "exact_frozen_parameters_order_contract",
                                   "independent_split_filter_direction_DP", "stage_actual_values_features", "ledger_fates",
                                   "reported_common_point_errors_coverage_and_counts", "reported_DP_denominator_saving_max"],
            "unchecked_components": ["batch_scope", "batch_aggregation", "full_hash_graph",
                                     "LLM_path", "memory", "selection", "experiment_admission"]}
