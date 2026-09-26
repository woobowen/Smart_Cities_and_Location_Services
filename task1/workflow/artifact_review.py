"""Target-specific independent checks, shared by runtime and offline review.

The caller resolves the registered artifact. Models cannot supply trusted hashes,
references or tolerances. Diagnostic predicates below do not call the producers.
"""
from .diagnostics import finite, independent_profile_review
from .io import object_hash


COMPONENTS = {
    'profile_pilot': ['record_scope', 'profile_fields', 'profile_counts', 'summary'],
    'time_boundaries': ['record_scope', 'raw_time', 'threshold', 'strict_inequality',
                        'boundaries', 'index_order', 'point_coverage'],
    'duplicate_details': ['record_scope', 'complete_events', 'event_types', 'event_indices'],
    'baseline': ['provenance', 'contract', 'segmentation', 'filtering', 'direction',
                 'actual_values', 'dp_intervals', 'point_accounting', 'summaries'],
}


def same_value(actual, expected):
    # JSON booleans are not integer indices/counts. Python's True == 1 is unsafe.
    try: return object_hash(actual) == object_hash(expected)
    except (TypeError, ValueError): return False


def _rows(raw, rows):
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        return ['RECORD_LIST_REQUIRED']
    ids = [r.get('record_id') for r in rows]
    if any(not isinstance(i, str) for i in ids):
        return ['RECORD_ID_TYPE']
    errors = []
    if len(ids) != len(set(ids)): errors.append('DUPLICATE_RECORD_ID')
    if len(ids) != len(raw) or set(ids) != set(raw): errors.append('RECORD_COVERAGE')
    return errors


def review_times(raw, rows, threshold):
    errors = _rows(raw, rows)
    if errors: return errors
    for row in rows:
        rid = row['record_id']; value = raw[rid]
        valid = (isinstance(value, list) and len(value) == 2
                 and all(isinstance(x, list) for x in value)
                 and len(value[0]) == len(value[1]) and all(finite(t) for t in value[0]))
        if not valid:
            if not same_value(row, {'record_id': rid, 'status': 'BLOCKED', 'reason': 'INVALID_TIMELINE_STRUCTURE'}):
                errors.append(rid + ':INVALID_TIMELINE_NOT_BLOCKED')
            continue
        times, points = value
        cuts = []
        groups = []; current = []
        for i, t in enumerate(times):
            if i and (t < times[i-1] or t-times[i-1] > threshold):
                cuts.append({'right_index': i, 'left_index': i-1, 'dt': t-times[i-1],
                             'reasons': ['NEGATIVE_DT' if t < times[i-1] else 'GAP_GT_THRESHOLD']})
                groups.append(current); current = []
            current.append(i)
        if current: groups.append(current)
        expected = {'threshold_source_seconds': threshold, 'cuts': cuts, 'partitions': groups,
                    'n_input': len(points), 'n_accounted': len(points), 'deleted': 0,
                    'modified': 0, 'status': 'EXECUTED'}
        for name, value in expected.items():
            if not same_value(row.get(name), value): errors.append(f'{rid}:{name}')
    return errors


def review_duplicates(raw, rows):
    errors = _rows(raw, rows)
    if errors: return errors
    for row in rows:
        rid = row['record_id']; value = raw[rid]
        if (not isinstance(value, list) or len(value) != 2
                or not all(isinstance(x, list) for x in value) or len(value[0]) != len(value[1])):
            if not same_value(row, {'record_id': rid, 'status': 'BLOCKED', 'reason': 'INVALID_STRUCTURE'}):
                errors.append(rid + ':INVALID_STRUCTURE_NOT_BLOCKED')
            continue
        times, points = value; events = []
        for left in range(len(points)-1):
            right = left+1; reasons = []
            time_ok = finite(times[left]) and finite(times[right])
            position_ok = all(isinstance(p, list) and len(p) == 2 and all(finite(v) for v in p)
                              for p in (points[left], points[right]))
            if not time_ok: reasons.append('MISSING_OR_INVALID_TIME')
            if not position_ok: reasons.append('INVALID_POSITION_PAIR')
            if position_ok and points[left] == points[right]:
                reasons.append('REPEATED_POSITION_NOT_AUTOMATIC_NOISE')
            if time_ok and times[left] == times[right]:
                reasons.append('ZERO_DT_SPEED_UNAVAILABLE')
                if position_ok and points[left] != points[right]: reasons.append('SAME_TIME_DIFFERENT_POSITION')
            if reasons:
                events.append({'left_index': left, 'right_index': right,
                               'dt_raw': times[right]-times[left] if time_ok else None,
                               'dt_reason': None if time_ok else 'MISSING_OR_INVALID_TIME',
                               'position_pair_computable': position_ok, 'reasons': reasons})
        for name, value in {'events': events, 'modified': 0, 'deleted': 0, 'status': 'EXECUTED'}.items():
            if not same_value(row.get(name), value): errors.append(f'{rid}:{name}')
    return errors


def review_profiles(raw, result):
    audit = independent_profile_review(raw, result.get('profiles'))
    errors = list(audit['errors'])
    if errors: return errors
    # Counts have already been checked against raw input by a separate implementation.
    rows = result['profiles']; counts = {}
    fields = ['n_points', 'n_timestamps', 'invalid_timestamps', 'invalid_coordinates',
              'negative_dt', 'zero_dt', 'positive_dt', 'same_time_different_position',
              'consecutive_duplicate_position', 'long_gap_gt_30_source_seconds',
              'edges_total', 'dt_computable', 'position_pairs_computable']
    for r in rows:
        for k, v in r['dt_counts'].items(): counts[k] = counts.get(k, 0)+v
    expected = {f: sum(r[f] for r in rows) for f in fields}
    expected.update(n_records=len(raw), valid_structure_records=sum(r['valid_structure'] for r in rows),
                    dt_counts=counts, point_count_min=min((r['n_points'] for r in rows), default=None),
                    point_count_max=max((r['n_points'] for r in rows), default=None), modifications=0,
                    physical_distance={'value': None, 'reason': 'CRS_AND_DISTANCE_POLICY_UNRESOLVED'})
    if not same_value(result.get('summary'), expected): errors.append('PROFILE_SUMMARY_MISMATCH')
    return errors


def review_artifact(action, raw, candidate, policy, binding, requested_components=None):
    supported = COMPONENTS.get(action, [])
    requested = list(supported if requested_components is None else requested_components)
    missing = [c for c in requested if c not in supported]
    result = {'status': 'REJECTED', 'target_action': action,
              'target_artifact_id': binding['artifact_id'], 'target_artifact_hash': binding['sha256'],
              'target_output_hash': binding['output_sha256'],
              'trusted_reference': {'raw_sha256': policy['raw_sha256'], 'parent_version': 'RAW:'+policy['raw_sha256'],
                                    'policy_sha256': object_hash(policy)},
              'record_scope': list(raw), 'contract_version': policy['policy_version'],
              'checked_components': [], 'unchecked_components': missing,
              'unchecked_reasons': {c: 'TOOL_CAPABILITY_NOT_IMPLEMENTED' for c in missing}, 'errors': []}
    if not supported:
        result['errors'].append('UNSUPPORTED_TARGET'); return result
    if object_hash(candidate) != binding['output_sha256']:
        result['errors'].append('TARGET_HASH_MISMATCH'); return result
    expected_base = {'input_sha256': policy['raw_sha256'], 'parent_version': 'RAW:'+policy['raw_sha256'],
                     'semantics_version': policy['semantics_version'], 'metrics_version': policy['metrics_version'],
                     'input_records': len(raw), 'input_points': sum(len(v[1]) for v in raw.values()),
                     'modified_values': 0}
    for key, value in expected_base.items():
        if not same_value(candidate.get(key), value): result['errors'].append('ENVELOPE:'+key)
    ids = candidate.get('record_ids')
    if (not isinstance(ids, list) or any(not isinstance(i, str) for i in ids)
            or len(ids) != len(raw) or set(ids) != set(raw)):
        result['errors'].append('ENVELOPE:record_ids')
    try:
        payload = candidate.get('result', {})
        if action == 'profile_pilot': errors = review_profiles(raw, payload)
        elif action == 'time_boundaries': errors = review_times(raw, payload.get('trajectories'), policy['starter_reference']['dt_seconds'])
        elif action == 'duplicate_details': errors = review_duplicates(raw, payload.get('trajectories'))
        else:
            from .pipeline import trusted_real_reference
            from .evaluation import review_baseline
            reference, contract, provenance = trusted_real_reference(raw, list(raw), policy)
            baseline_review = review_baseline(candidate, reference, contract, provenance)
            result['baseline_review'] = baseline_review
            errors = baseline_review['errors']
            result['checked_components']=baseline_review['checked_components']
            result['unchecked_components']+=baseline_review['unchecked_components']
            for component in baseline_review['unchecked_components']:
                result['unchecked_reasons'][component]='BASELINE_STRUCTURE_PREVENTS_COMPLETE_CHECK'
        result['errors'].extend(errors)
        if action!='baseline': result['checked_components'] = supported
    except (ValueError, KeyError, TypeError, IndexError, ArithmeticError) as exc:
        result['errors'].append('INVALID_OR_UNAVAILABLE_REFERENCE:'+str(exc))
        for c in supported:
            if c not in result['unchecked_components']: result['unchecked_components'].append(c)
            result['unchecked_reasons'][c] = 'REFERENCE_OR_STRUCTURE_UNAVAILABLE'
    result['status'] = 'VERIFIED' if not result['errors'] and not result['unchecked_components'] else 'REJECTED'
    return result
