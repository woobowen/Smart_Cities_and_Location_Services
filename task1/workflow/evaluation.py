"""Independent planar verification; no production geometry/DP code is imported.

Checks establish implementation validity, never unknown ground truth or quality
improvement. Error belongs to each original index interval, not the globally
closest output segment. All metrics use the actual simplification input.
"""
from __future__ import annotations

from collections import Counter
import math
from numbers import Real
import sys


FLOAT_ULP_FACTOR = 64


def _finite(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _inspect(record):
    if not isinstance(record, dict) or not isinstance(record.get("record_id"), str):
        return "INVALID_RECORD_ID"
    if any(not isinstance(record.get(key), list) for key in ("indices", "timestamps", "xy")):
        return "MISSING_OUTPUT_OR_FIELDS"
    n = len(record["indices"])
    if len(record["xy"]) != n or len(record["timestamps"]) != n:
        return "MISALIGNED_FIELDS"
    idx = record["indices"]
    if any(type(i) is not int or i < 0 for i in idx) or idx != sorted(set(idx)):
        return "INVALID_INDEX_ORDER"
    if any(t is not None and not _finite(t) for t in record["timestamps"]):
        return "INVALID_TIMESTAMP"
    if any(not isinstance(p, (tuple, list)) or len(p) != 2 or not all(_finite(v) for v in p)
           for p in record["xy"]):
        return "INVALID_PLANAR_COORDINATE"
    return None


def _direct_distance(point, start, end):
    """Independent endpoint classification and cross-product distance."""
    vx, vy = end[0] - start[0], end[1] - start[1]
    wx, wy = point[0] - start[0], point[1] - start[1]
    length_squared = vx * vx + vy * vy
    if not math.isfinite(length_squared):
        raise ArithmeticError("NUMERIC_RANGE_EXCEEDED")
    if length_squared == 0:
        return math.hypot(wx, wy)
    dot = wx * vx + wy * vy
    if not math.isfinite(dot):
        raise ArithmeticError("NUMERIC_RANGE_EXCEEDED")
    if dot <= 0:
        return math.hypot(wx, wy)
    if dot >= length_squared:
        return math.hypot(point[0] - end[0], point[1] - end[1])
    return abs(vx * wy - vy * wx) / math.sqrt(length_squared)


def _length(points):
    return math.fsum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def floating_allowance(points, tolerance):
    """Fixed 64 binary64 eps times input scale, before inspecting output error.

    Absolute coordinate magnitude covers subtraction rounding for translated
    coordinates; extent covers vector arithmetic. This is a numerical allowance,
    not a tunable method threshold. It is reported for every verification.
    """
    extent = 0.0
    magnitude = 0.0
    if points:
        extent = max(max(p[axis] for p in points) - min(p[axis] for p in points) for axis in (0, 1))
        magnitude = max(abs(value) for point in points for value in point)
    return FLOAT_ULP_FACTOR * sys.float_info.epsilon * max(1.0, extent, magnitude, tolerance)


def _metric(value, reason=None):
    return {"value": value, "reason": reason}


def verify_simplification(reference, candidate, tolerance, *, expected_parent_hash=None):
    """Reject malformed, altered, wrongly indexed or over-tolerance candidates."""
    errors = []
    for name, record in (("reference", reference), ("candidate", candidate)):
        problem = _inspect(record)
        if problem:
            errors.append({"code": problem, "object": name})
    if not _finite(tolerance) or tolerance < 0:
        errors.append({"code": "INVALID_TOLERANCE"})
    result = {
        "status": "REJECTED",
        "quality_status": "PENDING_RESEARCH_REVIEW",
        "errors": errors,
        "metrics": {},
        "reference_scope": "SAME_SIMPLIFICATION_INPUT",
    }
    if errors:
        return result
    if candidate["record_id"] != reference["record_id"]:
        errors.append({"code": "WRONG_RECORD"})
    if expected_parent_hash is not None and candidate.get("parent_hash") != expected_parent_hash:
        errors.append({"code": "WRONG_PARENT_HASH"})
    lookup = {label: i for i, label in enumerate(reference["indices"])}
    for position, label in enumerate(candidate["indices"]):
        if label not in lookup:
            errors.append({"code": "INDEX_NOT_IN_PARENT", "index": label})
        else:
            original = lookup[label]
            if (list(candidate["xy"][position]) != list(reference["xy"][original])
                    or candidate["timestamps"][position] != reference["timestamps"][original]):
                errors.append({"code": "VALUE_MODIFIED", "index": label})
    n_ref, n_output = len(reference["indices"]), len(candidate["indices"])
    if n_ref:
        if (not n_output or candidate["indices"][0] != reference["indices"][0]
                or candidate["indices"][-1] != reference["indices"][-1]):
            errors.append({"code": "ENDPOINT_MISSING"})
    elif n_output:
        errors.append({"code": "NONEMPTY_OUTPUT_FOR_EMPTY_INPUT"})
    if errors:
        return result

    allowance = floating_allowance(reference["xy"], tolerance)
    point_errors = {label: 0.0 for label in candidate["indices"]}
    for left, right in zip(candidate["indices"], candidate["indices"][1:]):
        a, b = lookup[left], lookup[right]
        for position in range(a + 1, b):
            try:
                distance = _direct_distance(reference["xy"][position], reference["xy"][a], reference["xy"][b])
            except ArithmeticError:
                distance = math.inf
            if not math.isfinite(distance):
                errors.append({"code": "NUMERIC_RANGE_EXCEEDED", "index": reference["indices"][position]})
                return result
            point_errors[reference["indices"][position]] = distance
    violations = [{"index": index, "error": error}
                  for index, error in sorted(point_errors.items()) if error > tolerance + allowance]
    if violations:
        errors.append({"code": "ERROR_EXCEEDS_TOLERANCE", "points": violations})
    try:
        before_length, after_length = _length(reference["xy"]), _length(candidate["xy"])
    except ArithmeticError:
        before_length = after_length = math.inf
    if not all(math.isfinite(value) for value in (allowance, before_length, after_length)):
        errors.append({"code": "NUMERIC_RANGE_EXCEEDED"})
        return result
    result.update({
        "status": "REJECTED" if errors else "VERIFIED",
        "floating_allowance": allowance,
        "floating_allowance_formula": "64 * binary64_epsilon * max(1, coordinate_extent, absolute_coordinate, tolerance)",
        "algorithm_tolerance": tolerance,
        "error_by_original_index": [{"index": i, "error": error} for i, error in sorted(point_errors.items())],
        "exceeding_points": violations,
        "metrics": {
            "reference_points": _metric(n_ref),
            "simplified_points": _metric(n_output),
            "saving": _metric(1 - n_output / n_ref) if n_ref else _metric(None, "EMPTY_REFERENCE_DENOMINATOR"),
            "max_error": _metric(max(point_errors.values())) if n_ref else _metric(None, "EMPTY_REFERENCE"),
            "reference_length": _metric(before_length) if n_ref else _metric(None, "EMPTY_REFERENCE"),
            "simplified_length": _metric(after_length) if n_output else _metric(None, "EMPTY_OUTPUT"),
            "length_change": _metric(after_length - before_length) if n_ref else _metric(None, "EMPTY_REFERENCE"),
            "relative_length_change": (_metric(after_length / before_length - 1) if before_length else
                                       _metric(None, "ZERO_REFERENCE_LENGTH" if n_ref else "EMPTY_REFERENCE")),
        },
        "claims_supported": ["ORDERED_SUBSEQUENCE", "VALUES_UNCHANGED", "INDEX_INTERVAL_ERROR_CHECK"],
        "claims_not_supported": ["GROUND_TRUTH_RECOVERY", "DETECTION_ACCURACY", "QUALITY_IMPROVEMENT"],
    })
    return result


def audit_point_accounting(inputs, stage_groups):
    """Each input point must have exactly one terminal fate, including losses.

    stage_groups contains filtered/denoised/simplified/retained record lists.
    Record ID is part of identity, so equal coordinates cannot merge records.
    """
    expected_groups = {"filtered", "denoised", "simplified", "retained"}
    if set(stage_groups) != expected_groups:
        raise ValueError("all four terminal stage groups must be supplied")
    originals = {}
    for record in inputs:
        problem = _inspect(record)
        if problem:
            raise ValueError(f"invalid accounting input: {problem}")
        for index, timestamp, point in zip(record["indices"], record["timestamps"], record["xy"]):
            key = (record["record_id"], index)
            if key in originals:
                raise ValueError("duplicate input point identity")
            originals[key] = (timestamp, tuple(point))
    observed, errors, counts = Counter(), [], {}
    for stage, records in stage_groups.items():
        counts[stage] = 0
        for record in records:
            problem = _inspect(record)
            if problem:
                errors.append({"code": problem, "stage": stage})
                continue
            for index, timestamp, point in zip(record["indices"], record["timestamps"], record["xy"]):
                key = (record["record_id"], index)
                observed[key] += 1
                counts[stage] += 1
                if key not in originals:
                    errors.append({"code": "UNKNOWN_POINT", "record_id": key[0], "index": index, "stage": stage})
                elif originals[key] != (timestamp, tuple(point)):
                    errors.append({"code": "VALUE_MODIFIED", "record_id": key[0], "index": index, "stage": stage})
    for key in originals:
        if observed[key] != 1:
            errors.append({"code": "MISSING_POINT" if observed[key] == 0 else "DUPLICATED_POINT",
                           "record_id": key[0], "index": key[1], "observed_count": observed[key]})
    return {"status": "REJECTED" if errors else "VERIFIED", "input_records": len(inputs),
            "input_points": len(originals), "stage_points": counts, "errors": errors,
            "count_conserved": sum(counts.values()) == len(originals),
            "modified_point_count": sum(e["code"] == "VALUE_MODIFIED" for e in errors)}


def assess_improvement(*, hard_conditions, measured_gain=None, minimum_gain=None,
                       protection_changes=None, allowed_degradations=None,
                       comparison_valid=None, evidence_sufficient=None):
    """Apply the approved Boolean logic, blocking absent research thresholds."""
    if hard_conditions is False:
        return {"status": "REJECTED", "reason": "HARD_CONDITION_FAILED"}
    required = {"hard_conditions": hard_conditions, "measured_gain": measured_gain,
                "minimum_gain": minimum_gain, "protection_changes": protection_changes,
                "allowed_degradations": allowed_degradations, "comparison_valid": comparison_valid,
                "evidence_sufficient": evidence_sufficient}
    missing = [name for name, value in required.items() if value is None]
    if missing:
        return {"status": "PENDING_RESEARCH_REVIEW", "reason": "UNFROZEN_OR_MISSING_CONTRACT", "missing": missing}
    if any(type(value) is not bool for value in (hard_conditions, comparison_valid, evidence_sufficient)):
        raise ValueError("Boolean acceptance inputs must be actual booleans")
    if not _finite(measured_gain) or not _finite(minimum_gain):
        raise ValueError("gain and its threshold must be finite")
    if set(protection_changes) != set(allowed_degradations):
        return {"status": "PENDING_RESEARCH_REVIEW", "reason": "INCOMPLETE_PROTECTION_CONTRACT"}
    for name in protection_changes:
        if (not _finite(protection_changes[name]) or not _finite(allowed_degradations[name])
                or allowed_degradations[name] < 0):
            raise ValueError("protection changes must be finite and limits nonnegative")
    passed = (hard_conditions and measured_gain >= minimum_gain and comparison_valid and evidence_sufficient
              and all(protection_changes[name] <= allowed_degradations[name] for name in protection_changes))
    return {"status": "QUALITY_ACCEPTED" if passed else "REJECTED",
            "reason": "EXPLICIT_CONTRACT_SATISFIED" if passed else "EXPLICIT_CONTRACT_FAILED"}
