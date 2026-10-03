"""Independent planar verification; no production geometry/DP code is imported.

Checks establish implementation validity, never unknown ground truth or quality
improvement. Error belongs to each original index interval, not the globally
closest output segment. All metrics use the actual simplification input.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import math
from numbers import Real
import sys

from .io import object_hash


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


BASELINE_COMPONENTS = ['provenance', 'contract', 'segmentation', 'filtering', 'direction',
                       'actual_values', 'dp_intervals', 'point_accounting', 'summaries']
DIRECTION_FLOAT_ALLOWANCE_DEGREES = FLOAT_ULP_FACTOR * sys.float_info.epsilon * 360.0


def _same(actual, expected):
    """Exact stored-value comparison, also distinguishing booleans from numbers."""
    return object_hash(actual) == object_hash(expected)


def _derived_same(actual, expected):
    """Only derived floating arithmetic gets a fixed binary64 rounding allowance."""
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and set(actual) == set(expected)
                and all(_derived_same(actual[k], v) for k, v in expected.items()))
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(_derived_same(a, b) for a, b in zip(actual, expected)))
    if isinstance(expected, float):
        return (_finite(actual) and math.isclose(actual, expected, rel_tol=64 * sys.float_info.epsilon,
                                               abs_tol=64 * sys.float_info.epsilon))
    return type(actual) is type(expected) and actual == expected


def _reference_features(record, time_reliable):
    """Direct edge arithmetic, independent of production feature/segment tools."""
    edges = []
    for pos in range(1, len(record['indices'])):
        a, b = record['xy'][pos - 1:pos + 1]
        t0, t1 = record['timestamps'][pos - 1:pos + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        distance = math.hypot(dx, dy)
        dt = None if t0 is None or t1 is None else t1 - t0
        speed_reason = ('MISSING_TIMESTAMP' if dt is None else 'UNRELIABLE_TIME' if not time_reliable
                        else 'ZERO_TIME_DIFFERENCE' if dt == 0 else
                        'NEGATIVE_TIME_DIFFERENCE' if dt < 0 else None)
        edges.append({'from_index': record['indices'][pos - 1], 'to_index': record['indices'][pos],
                      'dt': dt, 'dt_reason': 'MISSING_TIMESTAMP' if dt is None else None,
                      'distance': distance, 'speed': None if speed_reason else distance / dt,
                      'speed_reason': speed_reason,
                      'direction_degrees': None if dx == dy == 0 else math.degrees(math.atan2(dx, dy)) % 360,
                      'direction_reason': 'ZERO_DISPLACEMENT' if dx == dy == 0 else None})
    return {'edges': edges, 'length': math.fsum(e['distance'] for e in edges),
            'direction_convention': 'CLOCKWISE_FROM_POSITIVE_Y', 'time_reliable': time_reliable,
            'coverage': {'edge_denominator': len(edges),
                         'speed_computable': sum(e['speed'] is not None for e in edges),
                         'direction_computable': sum(e['direction_degrees'] is not None for e in edges),
                         'reason': None if edges else 'NO_EDGES'}}


def _reference_selection(record, indices, time_reliable):
    positions = {index: pos for pos, index in enumerate(record['indices'])}
    selected = {'record_id': record['record_id'], 'indices': list(indices),
                'timestamps': [record['timestamps'][positions[i]] for i in indices],
                'xy': [deepcopy(record['xy'][positions[i]]) for i in indices]}
    selected['features'] = _reference_features(selected, time_reliable)
    return selected


def _reference_partition(record, parameters):
    features = _reference_features(record, parameters['time_reliable'])
    boundaries, starts = [], [0]
    for position, edge in enumerate(features['edges'], 1):
        reasons = []
        if parameters['dt'] is not None:
            if edge['dt'] is None:
                raise ValueError('TRUSTED_TEMPORAL_INPUT_MISSING_TIME')
            if edge['dt'] < 0:
                reasons.append('NEGATIVE_TIME_DIFFERENCE')
            elif edge['dt'] > parameters['dt']:
                reasons.append('TIME_GAP')
        if parameters['distance'] is not None and edge['distance'] > parameters['distance']:
            reasons.append('DISTANCE_GAP')
        if reasons:
            boundaries.append({**edge, 'reasons': reasons, 'right_point_starts_segment': True})
            starts.append(position)
    starts.append(len(record['indices']))
    segments = []
    for start, stop in zip(starts, starts[1:]):
        if stop == start:
            continue
        segment = _reference_selection(record, record['indices'][start:stop], parameters['time_reliable'])
        segment.update(segment_index=len(segments), parent_hash=object_hash(record))
        reasons = []
        if stop - start < parameters['min_points']:
            reasons.append('TOO_FEW_POINTS')
        if segment['features']['length'] < parameters['min_length']:
            reasons.append('TOO_SHORT_LENGTH')
        segment['filter_reasons'] = reasons
        segments.append(segment)
    return boundaries, segments


def _reference_direction(record, threshold):
    directions = [e['direction_degrees'] for e in record['features']['edges']]
    rows, removed = [], []
    for position, index in enumerate(record['indices']):
        reason, previous, following = None, None, None
        if position in (0, len(record['indices']) - 1):
            reason = 'ENDPOINT'
        elif position + 1 >= len(directions):
            reason = 'MISSING_FOLLOWING_OUTGOING_EDGE'
        elif None in directions[position - 1:position + 2]:
            reason = 'UNCOMPUTABLE_DIRECTION_IN_WINDOW'
        else:
            angle = directions[position]
            differences = [abs(angle - directions[p]) for p in (position - 1, position + 1)]
            previous, following = [min(d, 360 - d) for d in differences]
        candidate = None if reason else previous > threshold and following > threshold
        if candidate is True:
            removed.append(index)
        rows.append({'index': index, 'candidate': candidate, 'reason': reason,
                     'previous_difference_degrees': previous, 'following_difference_degrees': following})
    return rows, removed


def _direction_rows_same(actual, expected):
    """Compare angular arithmetic at the normalized input scale, not its residual.

    Subtraction around a half/full turn can lose low bits when the final angle
    difference is small. Only reported unsigned differences get this fixed
    binary64 allowance. The strict threshold predicate, deletion decisions,
    undefined reasons and identities retain exact comparison.
    """
    if not isinstance(actual, list) or len(actual) != len(expected):
        return False
    angle_fields = ('previous_difference_degrees', 'following_difference_degrees')
    for row, reference in zip(actual, expected):
        if not isinstance(row, dict) or set(row) != set(reference):
            return False
        if any(not _same(row[key], reference[key]) for key in ('index', 'candidate', 'reason')):
            return False
        for key in angle_fields:
            value, truth = row[key], reference[key]
            if truth is None:
                if value is not None:
                    return False
            elif (not _finite(value) or not 0 <= value <= 180
                  or abs(value - truth) > DIRECTION_FLOAT_ALLOWANCE_DEGREES):
                return False
    return True


def _check_actual_record(actual, expected, errors, context):
    problem = _inspect(actual)
    if problem:
        errors.append({'code': problem, 'object': context})
        return
    for field in ('record_id', 'indices', 'timestamps', 'xy', 'parent_hash', 'segment_index', 'filter_reasons'):
        if field in expected and not _same(actual.get(field), expected[field]):
            errors.append({'code': 'ACTUAL_PARENT_OR_VALUE_MISMATCH', 'object': context, 'field': field})
    if not _derived_same(actual.get('features'), expected['features']):
        errors.append({'code': 'ACTUAL_FEATURES_MISMATCH', 'object': context})


def _validate_trusted_baseline(inputs, contract, provenance):
    """Validate a caller-provided trust boundary; never read it from the candidate."""
    if not isinstance(inputs, list) or not isinstance(contract, dict) or not isinstance(provenance, dict):
        raise ValueError('TRUSTED_COMPLETE_INPUT_CONTRACT_AND_PROVENANCE_REQUIRED')
    ids = []
    for record in inputs:
        if _inspect(record):
            raise ValueError('INVALID_TRUSTED_INPUT')
        ids.append(record['record_id'])
    if len(ids) != len(set(ids)):
        raise ValueError('DUPLICATE_TRUSTED_INPUT_RECORD')
    if (contract['contract_version'] != 'BASELINE_CONTRACT_V2'
            or contract['method'] != 'single_pass_simultaneous_keep_undefined'
            or contract['order'] != ['split', 'filter', 'denoise', 'simplify']
            or not isinstance(contract['contract_id'], str) or not contract['contract_id']
            or not isinstance(contract['adapter_version'], str) or not contract['adapter_version']):
        raise ValueError('UNSUPPORTED_TRUSTED_CONTRACT')
    units = contract['units']
    if (set(units) != {'xy', 'time', 'direction'} or units['direction'] != 'degrees'
            or any(not isinstance(v, str) or not v for v in units.values())):
        raise ValueError('INVALID_TRUSTED_UNITS')
    parameters = contract['parameters']
    if set(parameters) != {'dt', 'distance', 'min_points', 'min_length', 'direction', 'dp', 'time_reliable'}:
        raise ValueError('INVALID_TRUSTED_PARAMETERS')
    for key, value in parameters.items():
        if key == 'time_reliable' or key in ('dt', 'distance') and value is None:
            continue
        if not _finite(value) or value < 0:
            raise ValueError('INVALID_TRUSTED_PARAMETER:' + key)
    if (type(parameters['min_points']) is not int or type(parameters['time_reliable']) is not bool
            or parameters['direction'] > 180
            or parameters['dt'] is not None and not parameters['time_reliable']):
        raise ValueError('INVALID_TRUSTED_PARAMETER_TYPE_OR_TIME')
    if (provenance['reference_sha256'] != object_hash(inputs) or provenance['record_scope'] != ids
            or provenance['contract_sha256'] != object_hash(contract)
            or any(provenance[k] != contract[k] for k in ('contract_id', 'contract_version', 'adapter_version'))):
        raise ValueError('TRUSTED_HANDLE_BINDING_MISMATCH')
    for key in ('raw_sha256', 'raw_scope_sha256'):
        value = provenance[key]
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('INVALID_TRUSTED_RAW_HASH')
    if provenance['source_kind'] == 'CONSTRUCTED_FIXTURE':
        if (contract['scope'] != 'CONSTRUCTED_PLANAR_ONLY' or contract['approval'] != 'ENGINEERING_TEST_ONLY'
                or any(not rid.startswith('fixture:') for rid in ids)
                or contract['adapter_version'] != 'constructed_identity:v1'
                or provenance['raw_sha256'] != object_hash(inputs)
                or provenance['raw_scope_sha256'] != object_hash(inputs)
                or provenance['parent_version'] != 'CONSTRUCTED:' + provenance['raw_sha256']):
            raise ValueError('INVALID_CONSTRUCTED_TRUST_BOUNDARY')
    elif provenance['source_kind'] in ('CURRENT_RUN_REAL_BASELINE', 'CURRENT_RUN_CONDITIONAL_ANALYSIS'):
        conditional = provenance['source_kind'] == 'CURRENT_RUN_CONDITIONAL_ANALYSIS'
        expected_approval = 'CONDITIONAL_ANALYSIS' if conditional else 'APPROVED_FOR_REAL_INPUT'
        if (contract['approval'] != expected_approval or not contract['approval_source']
                or set(contract['record_ids']) != set(ids) or contract['raw_sha256'] != provenance['raw_sha256']
                or provenance['parent_version'] != 'RAW:' + provenance['raw_sha256']):
            raise ValueError('INVALID_REAL_TRUST_BOUNDARY')
        if conditional and (contract.get('source_crs') != 'UNVERIFIED'
                            or contract.get('classification') != 'CURRENT_RUN_CONDITIONAL_ANALYSIS'):
            raise ValueError('CONDITIONAL_DATUM_LIMITATION_MISSING')
        for record in inputs:
            if (record['raw_record_sha256'] != object_hash(record['raw_values'])
                    or record['adapter_version'] != contract['adapter_version']
                    or record['indices'] != list(range(len(record['raw_values'][1])))
                    or not _same(record['timestamps'], record['raw_values'][0])):
                raise ValueError('INVALID_RAW_TO_WORKING_BINDING')
        if provenance['raw_scope_sha256'] != object_hash({r['record_id']: r['raw_values'] for r in inputs}):
            raise ValueError('INVALID_RAW_SCOPE_BINDING')
    else:
        raise ValueError('UNSUPPORTED_REFERENCE_SOURCE')


def review_baseline(output, trusted_complete_inputs=None, approved_contract=None, trusted_provenance=None):
    """Independently inspect an actual artifact against externally supplied inputs.

    All four arguments are required for verification. Omitted handles fail closed;
    output.input, output.parameters and output.provenance never establish trust.
    No production processing/geometry function is called to make an oracle run.
    """
    result = {'status': 'REJECTED', 'errors': [], 'quality_status': 'PENDING_RESEARCH_REVIEW',
              'checked_components': [], 'unchecked_components': list(BASELINE_COMPONENTS),
              'scope': 'Complete trusted input, approved method, actual artifacts; no ground-truth claim'}
    errors = result['errors']
    try:
        _validate_trusted_baseline(trusted_complete_inputs, approved_contract, trusted_provenance)
    except (ValueError, KeyError, TypeError, IndexError, ArithmeticError) as exc:
        errors.append({'code': 'TRUSTED_REFERENCE_UNAVAILABLE', 'reason': str(exc)})
        return result
    result.update(trusted_reference=deepcopy(trusted_provenance),
                  record_scope=[r['record_id'] for r in trusted_complete_inputs],
                  contract_version=approved_contract['contract_version'],
                  direction_numeric_allowance_degrees=DIRECTION_FLOAT_ALLOWANCE_DEGREES,
                  direction_numeric_allowance_rule='64 * binary64_epsilon * 360; derived angles only, strict decisions unchanged')
    try:
        complete = _review_baseline_artifact(output, trusted_complete_inputs, approved_contract, trusted_provenance, result)
    except (ValueError, KeyError, TypeError, IndexError, ArithmeticError) as exc:
        errors.append({'code': 'MALFORMED_BASELINE_ARTIFACT', 'reason': str(exc)})
        return result
    result['status'] = 'REJECTED' if errors else 'VERIFIED'
    if complete:
        result.update(checked_components=list(BASELINE_COMPONENTS), unchecked_components=[])
    return result


def _review_baseline_artifact(output, inputs, contract, provenance, result):
    errors = result['errors']
    parameters = contract['parameters']
    if not isinstance(output, dict):
        raise ValueError('BASELINE_ARTIFACT_OBJECT_REQUIRED')
    for key, expected in (('input_hash', object_hash(inputs)), ('contract', contract),
                          ('parameters', parameters), ('provenance', provenance),
                          ('classification', provenance['source_kind']), ('modified_values', 0),
                          ('quality_status', 'PENDING_RESEARCH_REVIEW'), ('status', 'VERIFIED')):
        if not _same(output.get(key), expected):
            errors.append({'code': 'BASELINE_ENVELOPE_MISMATCH', 'field': key})
    result.update(checked_components=['provenance', 'contract'], unchecked_components=BASELINE_COMPONENTS[2:])
    records = output['records']
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError('INVALID_RECORD_LIST')
    ids = [r.get('record_id') for r in records]
    if (any(not isinstance(rid, str) for rid in ids) or len(ids) != len(set(ids))
            or set(ids) != {r['record_id'] for r in inputs}):
        errors.append({'code': 'COMPLETE_RECORD_SCOPE_MISMATCH'})
        return False
    by_id = {r['record_id']: r for r in records}
    stages = dict.fromkeys(('input', 'segmented', 'filtered', 'denoised', 'simplified', 'retained', 'not_processed'), 0)
    segment_counts = dict.fromkeys(('total', 'filtered', 'processed'), 0)
    ledger, record_reviews = [], []

    def terminal(record, indices, action, reasons, segment_index, parent_hash):
        positions = {index: pos for pos, index in enumerate(record['indices'])}
        for index in indices:
            pos = positions[index]
            ledger.append({'record_id': record['record_id'], 'original_index': index,
                           'segment_index': segment_index, 'action': action, 'reasons': list(reasons),
                           'parent_hash': parent_hash, 'timestamp': record['timestamps'][pos],
                           'xy': deepcopy(record['xy'][pos])})

    for reference in inputs:
        rid = reference['record_id']
        actual = by_id[rid]
        if not _same(actual.get('source_record'), reference) or actual.get('parent_hash') != object_hash(reference):
            errors.append({'code': 'RAW_WORKING_PARENT_MISMATCH', 'record_id': rid})
        boundaries, segments = _reference_partition(reference, parameters)
        if not _derived_same(actual['boundaries'], boundaries):
            errors.append({'code': 'SEGMENT_BOUNDARIES_MISMATCH', 'record_id': rid})
        dropped = [s for s in segments if s['filter_reasons']]
        kept = [s for s in segments if not s['filter_reasons']]
        actual_dropped, actual_kept = actual['filtered_segments'], actual['processed_segments']
        if (not _same([s['segment_index'] for s in actual_dropped], [s['segment_index'] for s in dropped])
                or not _same([s['segment_index'] for s in actual_kept], [s['segment_index'] for s in kept])):
            errors.append({'code': 'SEGMENT_FILTER_COVERAGE_MISMATCH', 'record_id': rid})
        counts = dict.fromkeys(stages, 0)
        counts.update(input=len(reference['indices']), segmented=len(segments))
        for expected, submitted in zip(dropped, actual_dropped):
            _check_actual_record(submitted, expected, errors, rid + ':filtered')
        for expected in dropped:
            counts['filtered'] += len(expected['indices'])
            terminal(expected, expected['indices'], 'filtered', expected['filter_reasons'],
                     expected['segment_index'], object_hash(reference))
        for expected, submitted in zip(kept, actual_kept):
            context = rid + ':segment:' + str(expected['segment_index'])
            _check_actual_record(submitted['input'], expected, errors, context + ':input')
            decisions, removed = _reference_direction(expected, parameters['direction'])
            denoise = submitted['denoise']
            for key, value in (('method', contract['method']), ('passes', 1),
                               ('modified_values', 0), ('deleted_indices', removed)):
                if not _same(denoise.get(key), value):
                    errors.append({'code': 'DIRECTION_SCHEDULE_MISMATCH', 'object': context, 'field': key})
            if not _direction_rows_same(denoise['decisions'], decisions):
                errors.append({'code': 'DIRECTION_DECISIONS_MISMATCH', 'object': context})
            clean = _reference_selection(expected, [i for i in expected['indices'] if i not in removed], parameters['time_reliable'])
            clean['parent_hash'] = object_hash(expected)
            _check_actual_record(denoise['record'], clean, errors, context + ':clean')
            final = submitted['output']
            numeric = verify_simplification(clean, final, parameters['dp'], expected_parent_hash=object_hash(clean))
            if numeric['status'] != 'VERIFIED':
                errors.extend({**e, 'object': context + ':final'} for e in numeric['errors'])
            if not _derived_same(submitted.get('independent_review'), numeric):
                errors.append({'code': 'STORED_NUMERIC_REVIEW_MISMATCH', 'object': context})
            final_ids = final['indices'] if _inspect(final) is None else []
            if parameters['dp'] == 0 and final_ids != clean['indices']:
                errors.append({'code': 'ZERO_DP_IDENTITY_MISMATCH', 'object': context})
            known_ids = [i for i in final_ids if i in clean['indices']]
            expected_final = _reference_selection(clean, known_ids, parameters['time_reliable'])
            expected_final['parent_hash'] = object_hash(clean)
            _check_actual_record(final, expected_final, errors, context + ':final')
            simplified = [i for i in clean['indices'] if i not in final_ids]
            terminal(expected, removed, 'denoised', ['DIRECTION_RULE'], expected['segment_index'], object_hash(expected))
            terminal(clean, simplified, 'simplified', ['DP_WITHIN_TOLERANCE'], expected['segment_index'], object_hash(clean))
            terminal(clean, known_ids, 'retained', ['DP_RETAINED'], expected['segment_index'], object_hash(clean))
            counts['denoised'] += len(removed)
            counts['simplified'] += len(simplified)
            counts['retained'] += len(known_ids)
        expected_segments = {'total': len(segments), 'filtered': len(dropped), 'processed': len(kept)}
        terminal_status = 'EMPTY_INPUT' if not reference['indices'] else 'ALL_FILTERED' if not kept else 'PROCESSED'
        for key, value in (('stage_counts', counts), ('segment_counts', expected_segments), ('terminal_status', terminal_status)):
            if not _same(actual.get(key), value):
                errors.append({'code': 'RECORD_SUMMARY_MISMATCH', 'record_id': rid, 'field': key})
        record_reviews.append({'record_id': rid, 'stage_counts': counts, 'segment_counts': expected_segments,
                               'terminal_status': terminal_status})
        for key in stages:
            stages[key] += counts[key]
        for key in segment_counts:
            segment_counts[key] += expected_segments[key]
    actual_ledger = output['point_actions']
    if not isinstance(actual_ledger, list):
        raise ValueError('INVALID_TERMINAL_LEDGER')
    if Counter(object_hash(row) for row in actual_ledger) != Counter(object_hash(row) for row in ledger):
        errors.append({'code': 'TERMINAL_LEDGER_MISMATCH'})
    groups = {k: [] for k in ('filtered', 'denoised', 'simplified', 'retained')}
    for row in actual_ledger:
        if row['action'] not in groups:
            errors.append({'code': 'UNKNOWN_TERMINAL_ACTION'})
            continue
        groups[row['action']].append({'record_id': row['record_id'], 'indices': [row['original_index']],
                                     'timestamps': [row['timestamp']], 'xy': [row['xy']]})
    accounting = audit_point_accounting(inputs, groups)
    errors.extend(accounting['errors'])
    limitation = ('EMPTY_INPUT' if not stages['input'] else 'ALL_FILTERED_NO_OUTPUT' if not stages['retained']
                  else 'GEOMETRY_IS_NOT_GROUND_TRUTH_OR_QUALITY_IMPROVEMENT')
    for key, expected in (('accounting', accounting), ('stage_counts', stages),
                          ('segment_counts', segment_counts), ('output_limitation', limitation)):
        if not _same(output.get(key), expected):
            errors.append({'code': 'GLOBAL_SUMMARY_MISMATCH', 'field': key})
    result.update(accounting=accounting, record_reviews=record_reviews, stage_counts=stages,
                  segment_counts=segment_counts, output_limitation=limitation)
    return True
