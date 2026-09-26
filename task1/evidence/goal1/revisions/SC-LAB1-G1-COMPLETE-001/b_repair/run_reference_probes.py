"""Replay externally reported C2-F02 challenges after the interface repair.

ENGINEERING_TEST only. Inputs are explicit fixtures; no Provider or real baseline
is invoked. This script preserves the original challenge meanings.
"""
from copy import deepcopy
from pathlib import Path

from task1.workflow.evaluation import review_baseline
from task1.workflow.io import ROOT, digest, now, object_hash, write_json
from task1.workflow.pipeline import run_constructed, trusted_constructed_reference


def main():
    records = [{'record_id': 'fixture:a', 'indices': [0, 1, 2, 3],
                'timestamps': [0, 1, 2, 3], 'xy': [[0, 0], [1, 0], [2, 0], [3, 0]]}]
    contract = {'scope': 'CONSTRUCTED_PLANAR_ONLY', 'approval': 'ENGINEERING_TEST_ONLY',
                'method': 'single_pass_simultaneous_keep_undefined',
                'parameters': {'dt': 30, 'distance': 100, 'min_points': 0,
                               'min_length': 0, 'direction': 35, 'dp': .1, 'time_reliable': True}}
    trusted = trusted_constructed_reference(records, contract)
    valid = run_constructed(records, contract)
    results = []

    def probe(name, candidate, expected, reference=trusted):
        reviewed = review_baseline(candidate, *reference)
        results.append({'case': name, 'expected': expected, 'actual': reviewed,
                        'candidate_sha256': object_hash(candidate),
                        'trusted_reference_sha256': object_hash(reference[0]),
                        'matches_expected': reviewed['status'] == expected})

    probe('valid_control', valid, 'VERIFIED')
    damaged = deepcopy(valid)
    damaged['records'][0]['processed_segments'][0]['output']['xy'][0][0] += 100
    probe('only_final_coordinate_modified', damaged, 'REJECTED')
    damaged = deepcopy(valid)
    item = damaged['records'][0]['processed_segments'][0]
    for target in (item['denoise']['record'], item['output']):
        for point in target['xy']:
            point[0] += 100
    probe('clean_and_final_shifted_ledger_unchanged', damaged, 'REJECTED')
    damaged = deepcopy(valid)
    damaged['records'], damaged['point_actions'] = [], []
    probe('all_records_and_ledger_dropped_counts_unchanged', damaged, 'REJECTED')
    damaged = deepcopy(valid)
    damaged['stage_counts'].update(input=999, retained=999)
    probe('stage_counts_modified', damaged, 'REJECTED')
    full_scope = records + [{'record_id': 'fixture:b', 'indices': [0], 'timestamps': [0], 'xy': [[0, 0]]}]
    other_trusted = trusted_constructed_reference(full_scope, contract)
    probe('candidate_does_not_cover_current_complete_reference', valid, 'REJECTED', other_trusted)
    report = {'at': now(), 'classification': 'ENGINEERING_TEST', 'input_source': 'CONSTRUCTED_FIXTURE',
              'external_issue_source': 'GPT external review; c_initial/initial_reference_probes.json',
              'scope_note': 'Interface adapted to external trusted handle; original mutations preserved.',
              'live_model_calls': 0, 'real_baseline_runs': 0, 'inputs': records,
              'additional_scope_input': full_scope[-1], 'contract': contract,
              'trusted_handle': {'contract': trusted[1], 'provenance': trusted[2]},
              'source_sha256': {name: digest(ROOT / 'task1/workflow' / name)
                                for name in ('evaluation.py', 'pipeline.py')},
              'probes': results, 'all_expectations_met': all(r['matches_expected'] for r in results)}
    write_json(Path(__file__).with_name('reference_probes.json'), report)
    for item in results:
        print(item['case'] + ': ' + item['actual']['status'])
    if not report['all_expectations_met']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
