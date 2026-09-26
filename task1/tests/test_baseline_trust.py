"""C2-F02 regression and independent known-answer checks; ENGINEERING_TEST only."""
from copy import deepcopy

import pytest

from task1.workflow import geometry, pipeline, tools
from task1.workflow.evaluation import review_baseline
from task1.workflow.io import CONFIG, digest, object_hash, read_json, write_json


def record(points, *, rid='fixture:a', times=None, indices=None):
    return {'record_id': rid, 'xy': [list(p) for p in points],
            'timestamps': list(range(len(points))) if times is None else times,
            'indices': list(range(len(points))) if indices is None else indices}


def make_case(records=None, **parameters):
    if records is None:
        records = [record([(0, 0), (1, 0), (2, 0), (3, 0)])]
    contract = {'scope': 'CONSTRUCTED_PLANAR_ONLY', 'approval': 'ENGINEERING_TEST_ONLY',
                'method': 'single_pass_simultaneous_keep_undefined',
                'parameters': {'dt': 30, 'distance': 100, 'min_points': 0, 'min_length': 0,
                               'direction': 35, 'dp': .1, 'time_reliable': True, **parameters}}
    # The review handle comes from original inputs before the candidate exists.
    trusted = pipeline.trusted_constructed_reference(records, contract)
    return pipeline.run_constructed(records, contract), trusted


def error_codes(result):
    return {e['code'] for e in result['errors']}


def segment(result):
    return result['records'][0]['processed_segments'][0]


@pytest.mark.parametrize('bad_index',[False,0.0,True,'0'])
def test_segment_wrapper_identity_requires_actual_integer(bad_index):
    output,trusted=make_case()
    segment(output)['segment_index']=bad_index
    reviewed=review_baseline(output,*trusted)
    assert reviewed['status']=='REJECTED'
    assert 'SEGMENT_FILTER_COVERAGE_MISMATCH' in error_codes(reviewed)


def test_legal_four_point_control_and_detached_trust_handle():
    output, trusted = make_case()
    before = deepcopy(trusted)
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'VERIFIED'
    assert reviewed['stage_counts']['input'] == 4
    assert reviewed['stage_counts']['retained'] == 2
    segment(output)['denoise']['record']['xy'][0][0] += 100
    output['contract']['parameters']['dp'] = 999
    assert trusted == before
    assert review_baseline(output, *trusted)['status'] == 'REJECTED'


@pytest.mark.parametrize('handle_count', [0, 1, 2])
def test_missing_trusted_arguments_fail_closed(handle_count):
    output, trusted = make_case()
    reviewed = review_baseline(output, *trusted[:handle_count])
    assert reviewed['status'] == 'REJECTED'
    assert error_codes(reviewed) == {'TRUSTED_REFERENCE_UNAVAILABLE'}


@pytest.mark.parametrize('candidate', [None, [], {}])
def test_malformed_candidate_is_rejected(candidate):
    _, trusted = make_case()
    assert review_baseline(candidate, *trusted)['status'] == 'REJECTED'


@pytest.mark.parametrize('field', ['xy', 'timestamps'])
@pytest.mark.parametrize('both', [False, True])
def test_actual_clean_and_final_values_bound_to_external_parent(field, both):
    output, trusted = make_case()
    changed = [segment(output)['output']]
    if both:
        changed.append(segment(output)['denoise']['record'])
    for candidate in changed:
        if field == 'xy':
            for point in candidate['xy']:
                point[0] += 100
        else:
            candidate['timestamps'] = [value + 100 for value in candidate['timestamps']]
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'VALUE_MODIFIED' in error_codes(reviewed)


def test_removing_all_records_and_ledger_cannot_shrink_trusted_task():
    output, trusted = make_case()
    output['records'] = []
    output['point_actions'] = []
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'COMPLETE_RECORD_SCOPE_MISMATCH' in error_codes(reviewed)


@pytest.mark.parametrize('mutate', [
    lambda o: o['records'].pop(),
    lambda o: o['records'].append(deepcopy(o['records'][0])),
    lambda o: o['records'][0].update(record_id='fixture:foreign'),
])
def test_missing_duplicate_and_foreign_record_rejected(mutate):
    output, trusted = make_case([record([(0, 0)]), record([], rid='fixture:empty')])
    mutate(output)
    assert 'COMPLETE_RECORD_SCOPE_MISMATCH' in error_codes(review_baseline(output, *trusted))


@pytest.mark.parametrize('mutate', [
    lambda o: o['stage_counts'].update(input=999, retained=999),
    lambda o: o['records'][0]['stage_counts'].update(input=999),
    lambda o: o['records'][0]['segment_counts'].update(total=999),
    lambda o: o['accounting'].update(input_points=999),
    lambda o: o['segment_counts'].update(processed=999),
    lambda o: o['parameters'].update(dp=999),
    lambda o: o['contract']['parameters'].update(dp=999),
    lambda o: o['contract']['units'].update(xy='kilometre'),
    lambda o: o['contract'].update(order=['filter', 'split', 'denoise', 'simplify']),
    lambda o: o['provenance'].update(raw_sha256='0' * 64),
    lambda o: o['provenance'].update(parent_version='WRONG_PARENT'),
    lambda o: o['provenance'].update(adapter_version='unapproved:v9'),
    lambda o: o.update(input_hash='0' * 64),
    lambda o: segment(o)['input'].update(parent_hash='wrong'),
    lambda o: segment(o)['denoise']['record'].update(parent_hash='wrong'),
    lambda o: segment(o)['output'].update(parent_hash='wrong'),
])
def test_summaries_parameters_units_order_and_parent_versions_rejected(mutate):
    output, trusted = make_case()
    mutate(output)
    assert review_baseline(output, *trusted)['status'] == 'REJECTED'


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'wrong-action', 'wrong-index', 'modified-value', 'wrong-reason', 'wrong-segment'])
def test_actual_terminal_ledger_checked_completely(mutation):
    output, trusted = make_case()
    ledger = output['point_actions']
    if mutation == 'missing':
        ledger.pop()
    elif mutation == 'duplicate':
        ledger.append(deepcopy(ledger[0]))
    elif mutation == 'wrong-action':
        ledger[0]['action'] = 'denoised'
    elif mutation == 'wrong-index':
        ledger[0]['original_index'] = 999
    elif mutation == 'modified-value':
        ledger[0]['xy'][0] = 999
    elif mutation == 'wrong-reason':
        ledger[0]['reasons'] = ['INVENTED_REASON']
    else:
        ledger[0]['segment_index'] = 999
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'TERMINAL_LEDGER_MISMATCH' in error_codes(reviewed)


def test_partition_strict_equality_negative_time_and_nonconsecutive_labels():
    source = record([(0, 0), (1, 0), (2, 0), (3, 0)], times=[0, 30, 61, 60], indices=[10, 20, 30, 40])
    output, trusted = make_case([source], dp=0)
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'VERIFIED'
    boundaries = output['records'][0]['boundaries']
    assert [(b['from_index'], b['to_index'], b['reasons']) for b in boundaries] == [
        (20, 30, ['TIME_GAP']), (30, 40, ['NEGATIVE_TIME_DIFFERENCE'])]
    assert [s['input']['indices'] for s in output['records'][0]['processed_segments']] == [[10, 20], [30], [40]]
    boundaries.pop()
    assert 'SEGMENT_BOUNDARIES_MISMATCH' in error_codes(review_baseline(output, *trusted))


@pytest.mark.parametrize('criterion', ['dt', 'distance'])
def test_wrong_equality_cut_rejected_even_when_candidate_has_consistent_own_run(criterion):
    source = record([(0, 0), (30, 0), (61, 0)], times=[0, 30, 61])
    output, trusted = make_case([source], dt=30, distance=30)
    assert review_baseline(output, *trusted)['status'] == 'VERIFIED'
    wrong, _ = make_case([source], dt=30 if criterion == 'distance' else 29,
                         distance=30 if criterion == 'dt' else 29)
    # Even copying the externally approved envelope cannot hide the wrong partition.
    for key in ('parameters', 'contract', 'provenance'):
        wrong[key] = deepcopy(output[key])
    reviewed = review_baseline(wrong, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'SEGMENT_BOUNDARIES_MISMATCH' in error_codes(reviewed)


def test_filter_conditions_reasons_and_equal_length_keep():
    source = record([(0, 0), (1, 0), (20, 0)], times=[0, 1, 2])
    output, trusted = make_case([source], distance=10, min_points=2, min_length=1)
    assert review_baseline(output, *trusted)['status'] == 'VERIFIED'
    dropped = output['records'][0]['filtered_segments'][0]
    assert dropped['filter_reasons'] == ['TOO_FEW_POINTS', 'TOO_SHORT_LENGTH']
    assert output['records'][0]['processed_segments'][0]['input']['indices'] == [0, 1]
    dropped['filter_reasons'] = ['TOO_SHORT_LENGTH']
    assert review_baseline(output, *trusted)['status'] == 'REJECTED'


@pytest.mark.parametrize('records,min_points,expected', [
    ([], 0, 'EMPTY_INPUT'),
    ([record([])], 0, 'EMPTY_INPUT'),
    ([record([(0, 0), (1, 0)])], 3, 'ALL_FILTERED_NO_OUTPUT'),
])
def test_legitimate_empty_and_all_filtered_keep_quality_limit(records, min_points, expected):
    output, trusted = make_case(records, min_points=min_points)
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'VERIFIED'
    assert reviewed['output_limitation'] == expected
    assert reviewed['quality_status'] == 'PENDING_RESEARCH_REVIEW'
    assert reviewed['stage_counts']['retained'] == 0


def test_direction_strict_equality_and_undefined_windows_are_retained():
    turning = record([(0, 0), (1, 0), (1, 1), (2, 1)])
    equal, trusted = make_case([turning], direction=90, dp=0)
    assert segment(equal)['denoise']['deleted_indices'] == []
    assert review_baseline(equal, *trusted)['status'] == 'VERIFIED'
    marked, marked_trust = make_case([turning], direction=89, dp=0)
    assert segment(marked)['denoise']['deleted_indices'] == [1]
    assert review_baseline(marked, *marked_trust)['status'] == 'VERIFIED'
    repeated = record([(0, 0), (1, 0), (1, 0), (2, 0), (3, 0)])
    undefined, undefined_trust = make_case([repeated], dp=0)
    decisions = segment(undefined)['denoise']['decisions']
    assert decisions[1]['candidate'] is None and decisions[2]['candidate'] is None
    assert review_baseline(undefined, *undefined_trust)['status'] == 'VERIFIED'
    decisions[1].update(candidate=True, reason=None)
    assert 'DIRECTION_DECISIONS_MISMATCH' in error_codes(review_baseline(undefined, *undefined_trust))


@pytest.mark.parametrize('points,tolerance,keep', [
    ([(0, 0), (2, 1), (1, 0)], 1.1, [0, 2]),
    ([(0, 0), (1, 1), (2, 0), (1, 1)], .5, [0, 2, 3]),
])
def test_dp_finite_segment_and_original_interval_use_trusted_tolerance(points, tolerance, keep):
    output, trusted = make_case([record(points)], direction=180, dp=tolerance)
    assert review_baseline(output, *trusted)['status'] == 'VERIFIED'
    item = segment(output)
    clean = item['denoise']['record']
    item['output'] = geometry.select_indices(clean, keep, time_reliable=True)
    item['output']['parent_hash'] = object_hash(clean)
    output['parameters']['dp'] = 999
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'ERROR_EXCEEDS_TOLERANCE' in error_codes(reviewed)
    assert any(e['code'] == 'ERROR_EXCEEDS_TOLERANCE' for e in reviewed['errors'])


def test_reviewer_does_not_call_processing_runner_or_geometry(monkeypatch):
    output, trusted = make_case()
    def forbidden(*args, **kwargs):
        pytest.fail('The independent reviewer called production processing')
    for name in ('run_planar', 'run_constructed'):
        monkeypatch.setattr(pipeline, name, forbidden)
    for name in ('split_trajectory', 'filter_segments', 'denoise_trajectory', 'select_indices',
                 'douglas_peucker_indices', 'recompute_features', 'direction_candidates'):
        monkeypatch.setattr(geometry, name, forbidden)
    assert review_baseline(output, *trusted)['status'] == 'VERIFIED'


def test_zero_dp_tolerance_keeps_registered_identity_rule():
    output, trusted = make_case(dp=0)
    item = segment(output)
    clean = item['denoise']['record']
    item['output'] = geometry.select_indices(clean, [0, 3], time_reliable=True)
    item['output']['parent_hash'] = object_hash(clean)
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'ZERO_DP_IDENTITY_MISMATCH' in error_codes(reviewed)


def test_wrong_production_filter_is_rejected_by_independent_predicate(monkeypatch):
    original = pipeline.filter_segments
    monkeypatch.setattr(pipeline, 'filter_segments', lambda rows, *_args, **kw: original(rows, 0, 0, **kw))
    output, trusted = make_case(min_points=5)
    reviewed = review_baseline(output, *trusted)
    assert reviewed['status'] == 'REJECTED'
    assert 'SEGMENT_FILTER_COVERAGE_MISMATCH' in error_codes(reviewed)


def test_tool_raw_scope_mismatch_does_not_trust_constructed_candidate(tmp_path, monkeypatch):
    output, _ = make_case()
    raw = {'fixture:a': [[0, 1, 2, 3], [[0, 0], [1, 0], [2, 0], [3, 0]]],
           'fixture:b': [[0], [[0, 0]]]}
    data = tmp_path / 'raw.json'
    write_json(data, raw)
    policy = read_json(CONFIG)
    policy['raw_sha256'] = digest(data)
    monkeypatch.setattr(tools, 'DATA', data)
    reviewed = tools.execute_tool('verify_baseline', list(raw), policy, previous_baseline=output,
                                  classification='ENGINEERING_TEST')
    assert reviewed['status'] == 'REJECTED'
    assert reviewed['result']['unchecked_components'] == ['baseline']


def test_config_approval_strings_alone_cannot_authorize_real_reference():
    policy = read_json(CONFIG)
    policy['semantics']['crs']['status'] = 'APPROVED'
    policy['semantics']['distance_policy']['status'] = 'APPROVED'
    policy['method']['processing_status'] = 'APPROVED_FOR_REAL_INPUT'
    policy['method']['approved_contract_id'] = 'invented'
    with pytest.raises(ValueError, match='NOT_REGISTERED'):
        pipeline.trusted_real_reference({}, [], policy)
