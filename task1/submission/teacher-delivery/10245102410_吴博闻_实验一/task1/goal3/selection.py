"""Common-scale paired protection and conservative whole-scope decisions."""
from collections import Counter
from task1.workflow.g2_selection import compare as inherited_compare
from task1.workflow.io import object_hash


def paired(candidate, reference, *, p_only=False):
    for key in ('record_id', 'source_record_hash', 'contract_hash'):
        if candidate.get(key) != reference.get(key) or not candidate.get(key):
            raise ValueError('INCOMPARABLE_TRUSTED_PARENT:' + key)
    if (object_hash(candidate['source_record']) != candidate['source_record_hash']
            or object_hash(reference['source_record']) != reference['source_record_hash']
            or candidate['metrics']['common_reference_id'] != reference['metrics']['common_reference_id']):
        raise ValueError('INCOMPARABLE_OR_CHANGED_RAW_REFERENCE')
    c, b = candidate['metrics'], reference['metrics']
    out = inherited_compare(candidate, reference)
    errors = list(out['protection_failures'])
    before = {r['index']: r['error'] for r in b['common_point_errors'] if r['error'] is not None}
    after = {r['index']: r['error'] for r in c['common_point_errors'] if r['error'] is not None}
    allowance = max(c['common_floating_allowance'], b['common_floating_allowance'])
    windows_before = {r['reference_window'] for r in b['common_point_errors'] if r['error'] is not None}
    windows_after = {r['reference_window'] for r in c['common_point_errors'] if r['error'] is not None}
    if not windows_before <= windows_after:
        errors.append('RAW_WINDOW_IDENTITIES_LOST')
    if c['dp_max_error'] is not None and c['dp_max_error'] > 5 + allowance:
        errors.append('COMMON_DP_BUDGET_EXCEEDED')
    on_base = max((after[i] for i in before), default=None) if set(before) <= set(after) else None
    bmax = max(before.values(), default=None)
    if not p_only:
        if bmax is not None and (on_base is None or on_base > bmax + allowance):
            errors.append('COMMON_GEOMETRIC_PROTECTION_DEGRADED')
        gain = len(after) > len(before) or (on_base is not None and bmax is not None and on_base < bmax - allowance)
    else:
        p_before = next(s for s in reference['stages'] if s['name'] == 'P')['input']
        p_after = next(s for s in candidate['stages'] if s['name'] == 'P')['input']
        if p_before != p_after:
            errors.append('DP_REFERENCE_CHANGED')
        gain = c['n_dp_output'] < b['n_dp_output']
    errors = sorted(set(errors))
    hard = any(e in errors for e in ('RAW_BREAKPOINT_CROSSED', 'DP_CONTRACT_FAILED',
                                     'COMMON_DP_BUDGET_EXCEEDED', 'DP_REFERENCE_CHANGED', 'DP_REFERENCE_COUNT_CHANGED'))
    added = sorted(set(after) - set(before))
    out.update(protection_failures=errors, feasible=not errors, strict_gain=bool(gain and not errors),
               status='REJECTED_BY_CONSTRAINT' if hard else 'TRADEOFF' if errors else
                      'SUPPORTED_WITHIN_SCOPE' if gain else 'NO_DEMONSTRATED_GAIN',
               dp_only_comparison=p_only, candidate_max_on_baseline_covered=on_base,
               newly_covered_indices=added, newly_covered_count=len(added),
               newly_covered_error_sum=sum(after[i] for i in added),
               newly_covered_max_error=max((after[i] for i in added), default=None),
               n_final_delta=c['n_final']-b['n_final'],
               n_P_output_delta=c['n_dp_output']-b['n_dp_output'],
               candidate_dp_max=c['dp_max_error'], comparator_dp_max=b['dp_max_error'])
    out['equivalent_readings'] = (set(before) == set(after)
        and all(abs(after[i]-before[i]) <= allowance for i in before)
        and all(c[k] == b[k] for k in ('n_input', 'n_final', 'n_filtered', 'n_direction_removed',
                                     'n_dp_removed', 'n_dp_input', 'n_dp_output', 'raw_windows_covered')))
    # Full trace keeps identity sets. Compact pair tables avoid copying every set.
    out.pop('candidate_covered_indices', None)
    return out


def aggregate_pairs(rows):
    failures = [r for r in rows if not r['feasible']]
    n_gain = sum(r['strict_gain'] for r in rows)
    hard = any(r['status'] == 'REJECTED_BY_CONSTRAINT' for r in rows)
    p_only = bool(rows) and all(r['dp_only_comparison'] for r in rows)
    group_gain = sum(r['n_P_output_delta'] for r in rows) < 0 if p_only else n_gain > 0
    return {'n_records': len(rows), 'protected_records': len(rows)-len(failures),
            'failure_records': [r['record_id'] for r in failures], 'strict_gain_records': n_gain,
            'status': 'REJECTED_BY_CONSTRAINT' if hard else 'TRADEOFF' if failures else
                      'SUPPORTED_WITHIN_SCOPE' if group_gain else 'NO_DEMONSTRATED_GAIN',
            'all_guards_pass': bool(rows) and not failures,
            'replacement_supported': bool(rows) and not failures and group_gain,
            'coverage_delta': sum(r['coverage_delta'] for r in rows),
            'final_point_delta': sum(r['n_final_delta'] for r in rows),
            'P_output_delta': sum(r['n_P_output_delta'] for r in rows),
            'all_equivalent_readings': bool(rows) and all(r['equivalent_readings'] for r in rows),
            'new_coverage_max_error': max((r['newly_covered_max_error'] for r in rows
                                           if r['newly_covered_max_error'] is not None), default=None),
            'failures_by_reason': dict(Counter(e for r in failures for e in r['protection_failures']))}


def choose(ordered_ids, comparisons, *, initial='R0', eligibility=None, tie_metadata=None):
    """No aggregate language score: every replacement protects both anchors."""
    incumbent = initial
    events = []
    eligibility = eligibility or {cid: True for cid in ordered_ids}
    tie_metadata = tie_metadata or {}
    def tie_key(cid):
        meta = tie_metadata.get(cid, {})
        return (meta.get('enhancement_modules', float('inf')), meta.get('online_model_dependency', True),
                meta.get('measured_seconds', float('inf')), cid)
    for cid in ordered_ids:
        if cid == incumbent:
            continue
        fixed = comparisons[cid + '|R0']
        current = comparisons[cid + '|' + incumbent]
        supported = eligibility.get(cid, False) and fixed['all_guards_pass'] and current['replacement_supported']
        equivalent_simpler = (eligibility.get(cid, False) and fixed['all_guards_pass']
                              and current.get('all_equivalent_readings', False)
                              and current['all_guards_pass'] and tie_key(cid) < tie_key(incumbent))
        replace = supported or equivalent_simpler
        events.append({'candidate': cid, 'previous_incumbent': incumbent,
                       'fixed_reference': fixed, 'incumbent_comparison': current,
                       'component_eligibility': eligibility.get(cid, False),
                       'decision': 'ACCEPT_PROTECTED_STRICT_GAIN' if supported else
                                   'EQUIVALENT_SIMPLER_REPRESENTATIVE' if equivalent_simpler else 'RETAIN_INCUMBENT',
                       'next_incumbent': cid if replace else incumbent})
        if replace:
            incumbent = cid
    frontier = [cid for cid in ordered_ids if eligibility.get(cid, False)
                and comparisons[cid + '|R0']['all_guards_pass']
                and not any(other != cid and eligibility.get(other, False)
                            and comparisons[other + '|' + cid]['replacement_supported']
                            and comparisons[other + '|R0']['all_guards_pass'] for other in ordered_ids)]
    return {'incumbent': incumbent, 'events': events, 'protected_frontier': frontier,
            'rule': 'all-record protection to R0 and current incumbent + strict registered gain; incomparable retains incumbent',
            'global_optimality_claim': False}
