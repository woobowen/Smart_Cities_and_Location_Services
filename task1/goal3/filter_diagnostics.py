"""Explain added coverage using actual reference filter reasons, without retuning."""
from collections import Counter
from task1.workflow.io import ROOT, read_json, write_json, digest, now
from .data import EV
from .runtime import read_rows, assert_binding


def build():
    directory = EV/'runs/g3-full-production-01'
    manifest = read_json(directory/'manifest.json')
    assert_binding(manifest['bindings'])
    if manifest['status'] != 'MACHINE_VERIFIED_PENDING_C' or manifest['failed_records']:
        raise ValueError('COMPLETE_PRODUCTION_REQUIRED')
    freeze = read_json(EV/'production_freeze.json')
    final = freeze['final_strategy']
    counts, per_reason, records, stages = Counter(), Counter(), [], Counter()
    for row in read_rows(directory):
        ref = row['traces'][row['strategy_configs']['R0']]
        candidate = row['traces'][row['strategy_configs'][final]]
        before = {p['index'] for p in ref['metrics']['common_point_errors'] if p['error'] is not None}
        after = {p['index'] for p in candidate['metrics']['common_point_errors'] if p['error'] is not None}
        added = after-before
        ledger = {p['original_index']: p for p in ref['point_actions']}
        c_ledger = {p['original_index']: p for p in candidate['point_actions']}
        local = Counter()
        for i in added:
            item = ledger[i]
            if item['action'] != 'filtered':
                raise ValueError('ADDED_POINT_NOT_REFERENCE_FILTERED')
            reasons = set(item['reasons'])
            if not reasons <= {'TOO_FEW_POINTS', 'TOO_SHORT_LENGTH'} or not reasons:
                raise ValueError('UNRECOGNIZED_REFERENCE_FILTER_REASON')
            key = '+'.join(sorted(reasons)); local[key] += 1
            per_reason.update(reasons); stages[c_ledger[i]['action']] += 1
        counts.update(local)
        records.append({'record_id': row['record_id'], 'added_points': len(added),
                        'mutually_exclusive_reference_reason_counts': dict(local)})
    expected = manifest['comparisons'][final+'|R0']['coverage_delta']
    if sum(counts.values()) != expected or [r['record_id'] for r in records] != manifest['input_ids']:
        raise ValueError('ATTRIBUTION_SCOPE_OR_TOTAL_MISMATCH')
    result = {'at': now(), 'classification': 'POST_FREEZE_DESCRIPTIVE_FILTER_ATTRIBUTION',
        'engineering_status': 'MACHINE_CHECKED_PENDING_INDEPENDENT_C',
        'records': len(records), 'newly_covered_points': sum(counts.values()),
        'mutually_exclusive_reference_reason_counts': dict(counts),
        'per_reason_counts_overlap_allowed': dict(per_reason),
        'new_point_final_ledger_actions': dict(stages), 'per_record': records,
        'legacy_analysis_field': {'name': 'from_segments_shorter_than_R0_filter',
            'actual_definition': 'len(S-segment indices) < 5 OR S-segment length < 65 working metres',
            'not_definition': 'All points came from segments whose length alone was <65.',
            'historical_artifacts_rewritten': False},
        'source_bindings': {str((directory/'manifest.json').relative_to(ROOT)): digest(directory/'manifest.json'),
            'task1/evidence/goal3/production_freeze.json': digest(EV/'production_freeze.json'),
            'task1/goal3/filter_diagnostics.py': digest(__file__)},
        'method_or_parameter_change': False, 'new_model_calls': 0,
        'interpretation': 'Mutually exclusive reason buckets sum to added raw coverage; per-reason columns may overlap. Coverage is not storage or noise truth.'}
    write_json(EV/'full_filter_attribution.json', result)
    print({k:result[k] for k in ('records','newly_covered_points','mutually_exclusive_reference_reason_counts','new_point_final_ledger_actions')})
    return result


if __name__ == '__main__':
    build()
