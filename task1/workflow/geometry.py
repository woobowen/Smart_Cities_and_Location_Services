"""Planar geometry for Goal 1 ENGINEERING_TEST / CONSTRUCTED_FIXTURE inputs.

No geographic projection or real-data semantic assumption is made here. The
controller must establish a planar distance contract before admitting real data.
The DP stack structure follows the existing traj_agent/core/simplify.py; its
implicit geographic conversion and self-reported error are deliberately omitted.
"""
from __future__ import annotations

from copy import deepcopy
import math
from numbers import Real


class MethodUnresolved(RuntimeError):
    """The teacher's denoising rule has no sufficiently precise approved contract."""


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def _point(point):
    if not isinstance(point, (list, tuple)) or len(point) != 2:
        raise ValueError("planar point must have exactly two coordinates")
    return (_number(point[0], "x"), _number(point[1], "y"))


def validate_trajectory(record):
    """Validate alignment without modifying values or inferring physical units."""
    if not isinstance(record, dict) or not isinstance(record.get("record_id"), str):
        raise ValueError("record_id must be a string")
    for field in ("indices", "timestamps", "xy"):
        if not isinstance(record.get(field), list):
            raise ValueError(f"{field} must be a list")
    n = len(record["indices"])
    if len(record["timestamps"]) != n or len(record["xy"]) != n:
        raise ValueError("indices, timestamps and xy must remain aligned")
    previous = -1
    for index, timestamp, point in zip(record["indices"], record["timestamps"], record["xy"]):
        if type(index) is not int or index <= previous:
            raise ValueError("indices must be unique increasing nonnegative original indices")
        previous = index
        if timestamp is not None:
            _number(timestamp, "timestamp")
        _point(point)


def point_segment_distance(point, start, end):
    """Euclidean distance to a finite segment; units are the input planar units."""
    px, py = _point(point)
    ax, ay = _point(start)
    bx, by = _point(end)
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if not math.isfinite(length) or not math.isfinite(px - ax) or not math.isfinite(py - ay):
        raise ValueError("NUMERIC_RANGE_EXCEEDED")
    if length == 0:
        return math.hypot(px - ax, py - ay)
    ux, uy = dx / length, dy / length
    along = (px - ax) * ux + (py - ay) * uy
    along = min(length, max(0.0, along))
    return math.hypot((px - ax) - along * ux, (py - ay) - along * uy)


def angular_difference(first, second):
    """Unsigned circular difference in [0, 180] degrees, including many turns."""
    first, second = _number(first, "first angle"), _number(second, "second angle")
    return abs((first % 360 - second % 360 + 180) % 360 - 180)


def recompute_features(record, *, time_reliable=False):
    """Derive named edge features from current adjacency, never stored old arrays.

    Direction is clockwise from positive y; it is a planar convention, not a
    geographic bearing. Time differences retain input time units. Speed has
    planar-unit / time-unit dimensions only when time_reliable is explicitly true.
    """
    validate_trajectory(record)
    if type(time_reliable) is not bool:
        raise ValueError("time_reliable must be boolean")
    edges = []
    for position in range(1, len(record["indices"])):
        left, right = record["xy"][position - 1:position + 1]
        before, after = record["timestamps"][position - 1:position + 1]
        dx, dy = right[0] - left[0], right[1] - left[1]
        distance = math.hypot(dx, dy)
        dt = None if before is None or after is None else after - before
        if dt is None:
            speed_reason = "MISSING_TIMESTAMP"
        elif not time_reliable:
            speed_reason = "UNRELIABLE_TIME"
        elif dt == 0:
            speed_reason = "ZERO_TIME_DIFFERENCE"
        elif dt < 0:
            speed_reason = "NEGATIVE_TIME_DIFFERENCE"
        else:
            speed_reason = None
        edges.append({
            "from_index": record["indices"][position - 1],
            "to_index": record["indices"][position],
            "dt": dt,
            "dt_reason": "MISSING_TIMESTAMP" if dt is None else None,
            "distance": distance,
            "speed": None if speed_reason else distance / dt,
            "speed_reason": speed_reason,
            "direction_degrees": None if distance == 0 else math.degrees(math.atan2(dx, dy)) % 360,
            "direction_reason": "ZERO_DISPLACEMENT" if distance == 0 else None,
        })
    edge_count = len(edges)
    return {
        "edges": edges,
        "length": math.fsum(edge["distance"] for edge in edges),
        "direction_convention": "CLOCKWISE_FROM_POSITIVE_Y",
        "time_reliable": time_reliable,
        "coverage": {
            "edge_denominator": edge_count,
            "speed_computable": sum(edge["speed"] is not None for edge in edges),
            "direction_computable": sum(edge["direction_degrees"] is not None for edge in edges),
            "reason": "NO_EDGES" if edge_count == 0 else None,
        },
    }


def select_indices(record, indices, *, time_reliable=False):
    """Select by original index, preserving values and recomputing every edge."""
    validate_trajectory(record)
    indices = list(indices)
    positions = {index: position for position, index in enumerate(record["indices"])}
    if (any(type(index) is not int or index not in positions for index in indices)
            or list(indices) != sorted(set(indices))):
        raise ValueError("selection must be an ordered original-index subsequence")
    chosen = [positions[index] for index in indices]
    output = {
        "record_id": record["record_id"],
        "indices": list(indices),
        "timestamps": [record["timestamps"][i] for i in chosen],
        "xy": [deepcopy(record["xy"][i]) for i in chosen],
    }
    output["features"] = recompute_features(output, time_reliable=time_reliable)
    return output


def split_trajectory(record, dt_threshold, dist_threshold, *, time_reliable=False):
    """Cut before the right point on strict > threshold; negative dt is separate.

    A threshold of None disables that criterion. Temporal cuts require reliable
    time and complete timestamps. Point filtering is a separate operation.
    """
    validate_trajectory(record)
    for name, threshold in (("dt_threshold", dt_threshold), ("dist_threshold", dist_threshold)):
        if threshold is not None and _number(threshold, name) < 0:
            raise ValueError(f"{name} must be nonnegative")
    if dt_threshold is not None:
        if not time_reliable:
            raise ValueError("UNRELIABLE_TIME: temporal segmentation is blocked")
        if any(value is None for value in record["timestamps"]):
            raise ValueError("MISSING_TIMESTAMP: temporal segmentation is blocked")
    features = recompute_features(record, time_reliable=time_reliable)
    boundaries, cuts = [], [0]
    for position, edge in enumerate(features["edges"], start=1):
        reasons = []
        if dt_threshold is not None:
            if edge["dt"] < 0:
                reasons.append("NEGATIVE_TIME_DIFFERENCE")
            elif edge["dt"] > dt_threshold:
                reasons.append("TIME_GAP")
        if dist_threshold is not None and edge["distance"] > dist_threshold:
            reasons.append("DISTANCE_GAP")
        if reasons:
            cuts.append(position)
            boundaries.append({**edge, "reasons": reasons, "right_point_starts_segment": True})
    cuts.append(len(record["indices"]))
    segments = []
    for start, stop in zip(cuts, cuts[1:]):
        if stop > start:
            segment = select_indices(record, record["indices"][start:stop], time_reliable=time_reliable)
            segment["segment_index"] = len(segments)
            segments.append(segment)
    return {"segments": segments, "boundaries": boundaries, "input_points": len(record["indices"])}


def filter_segments(segments, min_points, min_length, *, time_reliable=False):
    """Filter on point count and within-segment cumulative length independently."""
    if type(min_points) is not int or min_points < 0:
        raise ValueError("min_points must be a nonnegative integer")
    if _number(min_length, "min_length") < 0:
        raise ValueError("min_length must be nonnegative")
    kept, dropped = [], []
    for segment in segments:
        validate_trajectory(segment)
        output = deepcopy(segment)
        output["features"] = recompute_features(segment, time_reliable=time_reliable)
        reasons = []
        if len(segment["indices"]) < min_points:
            reasons.append("TOO_FEW_POINTS")
        if output["features"]["length"] < min_length:
            reasons.append("TOO_SHORT_LENGTH")
        output["filter_reasons"] = reasons
        (dropped if reasons else kept).append(output)
    return {"kept": kept, "dropped": dropped}


def douglas_peucker_indices(points, tolerance, indices=None):
    """Finite-segment DP returning original indices, never matching coordinates.

    At equality, the interval is simplified. Zero tolerance preserves the starter
    stack implementation's identity behavior. Algorithm tolerance is not inflated
    by the evaluator's separate floating-point verification allowance.
    """
    if _number(tolerance, "tolerance") < 0:
        raise ValueError("tolerance must be nonnegative")
    for point in points:
        _point(point)
    n = len(points)
    labels = list(range(n)) if indices is None else list(indices)
    if (len(labels) != n or any(type(i) is not int or i < 0 for i in labels)
            or labels != sorted(set(labels))):
        raise ValueError("indices must be unique increasing nonnegative original indices")
    if n <= 2 or tolerance == 0:
        return labels
    keep = {0, n - 1}
    stack = [(0, n - 1)]
    while stack:
        start, stop = stack.pop()
        if stop <= start + 1:
            continue
        farthest, max_distance = None, -1.0
        for position in range(start + 1, stop):
            distance = point_segment_distance(points[position], points[start], points[stop])
            if distance > max_distance:
                farthest, max_distance = position, distance
        if max_distance > tolerance:
            keep.add(farthest)
            stack.append((start, farthest))
            stack.append((farthest, stop))
    return [labels[position] for position in sorted(keep)]


def direction_candidates(record, threshold):
    """Non-mutating diagnostic of the teacher's three outgoing-edge relation.

    At point position i, d[i] is i→i+1. If the circular difference between d[i]
    and each of d[i-1], d[i+1] is strictly > threshold, mark a candidate. This
    simultaneous diagnostic does not settle the still unresolved deletion policy.
    The first and final points, the penultimate point without a following outgoing
    edge, and any three-edge window containing a zero displacement are unevaluable.
    """
    if _number(threshold, "threshold") < 0 or threshold > 180:
        raise ValueError("threshold must be within [0, 180] degrees")
    features = recompute_features(record)
    directions = [edge["direction_degrees"] for edge in features["edges"]]
    rows = []
    for position, index in enumerate(record["indices"]):
        reason, previous_difference, following_difference = None, None, None
        if position == 0 or position == len(record["indices"]) - 1:
            reason = "ENDPOINT"
        elif position + 1 >= len(directions):
            reason = "MISSING_FOLLOWING_OUTGOING_EDGE"
        elif any(value is None for value in directions[position - 1:position + 2]):
            reason = "UNCOMPUTABLE_DIRECTION_IN_WINDOW"
        else:
            previous_difference = angular_difference(directions[position], directions[position - 1])
            following_difference = angular_difference(directions[position], directions[position + 1])
        rows.append({"index": index, "candidate": (None if reason else
                     previous_difference > threshold and following_difference > threshold),
                     "reason": reason, "previous_difference_degrees": previous_difference,
                     "following_difference_degrees": following_difference})
    return {"status": "DIAGNOSTIC_ONLY", "rows": rows,
            "candidate_indices": [row["index"] for row in rows if row["candidate"] is True],
            "deleted_indices": [], "modified_values": 0,
            "limitation": "Deletion/iteration/undefined-direction policy remains unapproved"}


def denoise_trajectory(record, threshold=None, *, method=None, time_reliable=False):
    """Registered mathematical candidate; production approval is checked upstream."""
    if method != 'single_pass_simultaneous_keep_undefined':
        raise MethodUnresolved('TEACHER_DIRECTION_RULE_UNRESOLVED: explicit registered schedule required')
    candidates = direction_candidates(record, threshold)
    removed = candidates['candidate_indices']
    output = select_indices(record, [i for i in record['indices'] if i not in removed],
                            time_reliable=time_reliable)
    return {'record':output,'deleted_indices':removed,'decisions':candidates['rows'],
            'method':method,'passes':1,'modified_values':0}
