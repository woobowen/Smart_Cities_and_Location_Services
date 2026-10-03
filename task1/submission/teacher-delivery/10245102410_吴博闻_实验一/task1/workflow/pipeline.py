"""Conditional processing chain; test contracts cannot authorize teacher data.

Reference handles come from inputs before processing, not candidate artifacts.
Real registrations require a reviewed adapter and archived approval. Conditional
analysis preserves the unresolved source datum in its own explicit contract.
"""
from copy import deepcopy
import math
from numbers import Real

from .geometry import (split_trajectory, filter_segments, denoise_trajectory,
                       douglas_peucker_indices, select_indices, validate_trajectory)
from .evaluation import verify_simplification, audit_point_accounting
from .io import DATA, ROOT, bound_path, digest, read_json, object_hash

DIRECTION_METHOD = 'single_pass_simultaneous_keep_undefined'
PIPELINE_ORDER = ['split', 'filter', 'denoise', 'simplify']
CONTRACT_VERSION = 'BASELINE_CONTRACT_V2'
PARAMETERS = {'dt', 'distance', 'min_points', 'min_length', 'direction', 'dp', 'time_reliable'}
# Fully established-datum contracts remain separate from conditional analysis.
REAL_CONTRACTS = {}


def _validate_contract(contract):
    if (contract.get('contract_version') != CONTRACT_VERSION
            or contract.get('method') != DIRECTION_METHOD
            or contract.get('order') != PIPELINE_ORDER
            or not isinstance(contract.get('contract_id'), str)
            or not contract['contract_id']
            or not isinstance(contract.get('adapter_version'), str)
            or not contract['adapter_version']):
        raise ValueError('INVALID_BASELINE_CONTRACT')
    units = contract.get('units')
    if (not isinstance(units, dict) or set(units) != {'xy', 'time', 'direction'}
            or any(not isinstance(v, str) or not v for v in units.values())
            or units['direction'] != 'degrees'):
        raise ValueError('EXPLICIT_UNITS_REQUIRED')
    parameters = contract.get('parameters')
    if not isinstance(parameters, dict) or set(parameters) != PARAMETERS:
        raise ValueError('INCOMPLETE_PARAMETERS')
    for key in PARAMETERS - {'time_reliable'}:
        value = parameters[key]
        if key in {'dt', 'distance'} and value is None:
            continue
        if (isinstance(value, bool) or not isinstance(value, Real)
                or not math.isfinite(value) or value < 0):
            raise ValueError('INVALID_PARAMETER:' + key)
    if (type(parameters['min_points']) is not int
            or type(parameters['time_reliable']) is not bool
            or parameters['direction'] > 180):
        raise ValueError('INVALID_PARAMETER_TYPE_OR_RANGE')
    if parameters['dt'] is not None and not parameters['time_reliable']:
        raise ValueError('UNRELIABLE_TIME')


def _validate_inputs(records):
    if not isinstance(records, list):
        raise ValueError('COMPLETE_INPUT_LIST_REQUIRED')
    ids = []
    for record in records:
        validate_trajectory(record)
        ids.append(record['record_id'])
    if len(set(ids)) != len(ids):
        raise ValueError('DUPLICATE_INPUT_RECORD')


def _provenance(records, contract, *, source_kind, raw_sha256, raw_scope_sha256, parent_version):
    return {'source_kind': source_kind, 'raw_sha256': raw_sha256,
            'raw_scope_sha256': raw_scope_sha256, 'reference_sha256': object_hash(records),
            'record_scope': [r['record_id'] for r in records], 'parent_version': parent_version,
            'adapter_version': contract['adapter_version'], 'contract_id': contract['contract_id'],
            'contract_version': contract['contract_version'], 'contract_sha256': object_hash(contract)}


def trusted_constructed_reference(records, contract):
    """Make a detached ENGINEERING_TEST handle directly from caller-owned inputs.

    Call before making a candidate. Defaults describe only the explicit planar
    fixture identity adapter; they never establish real CRS facts.
    """
    _validate_inputs(records)
    if (not isinstance(contract, dict) or contract.get('scope') != 'CONSTRUCTED_PLANAR_ONLY'
            or contract.get('approval') != 'ENGINEERING_TEST_ONLY'
            or contract.get('method') != DIRECTION_METHOD
            or any(not r['record_id'].startswith('fixture:') for r in records)):
        raise ValueError('CONSTRUCTED_CONTRACT_REQUIRED')
    approved = deepcopy(contract)
    approved.setdefault('contract_version', CONTRACT_VERSION)
    approved.setdefault('order', list(PIPELINE_ORDER))
    approved.setdefault('units', {'xy': 'fixture_planar_unit', 'time': 'fixture_time_unit', 'direction': 'degrees'})
    approved.setdefault('adapter_version', 'constructed_identity:v1')
    approved.setdefault('contract_id', 'fixture:' + object_hash(approved))
    _validate_contract(approved)
    if approved['adapter_version'] != 'constructed_identity:v1':
        raise ValueError('UNREGISTERED_CONSTRUCTED_ADAPTER')
    reference = deepcopy(records)
    raw_hash = object_hash(reference)
    provenance = _provenance(reference, approved, source_kind='CONSTRUCTED_FIXTURE',
                             raw_sha256=raw_hash, raw_scope_sha256=raw_hash,
                             parent_version='CONSTRUCTED:' + raw_hash)
    return reference, approved, provenance


def _registered_contract(contract_id):
    if contract_id == 'G1_CONDITIONAL_ENU_V1':
        from .coordinates import registration
        return registration()
    return REAL_CONTRACTS.get(contract_id) if isinstance(contract_id, str) else None


def _direction_approval(policy):
    schedule = policy['method'].get('direction_schedule', {})
    if schedule.get('status') != 'USER_APPROVED' or schedule.get('method') != DIRECTION_METHOD:
        raise ValueError('D2_DIRECTION_SCHEDULE_UNAPPROVED')
    path = bound_path(ROOT, schedule['approval_path'])
    if digest(path) != schedule['approval_sha256']:
        raise ValueError('D2_APPROVAL_HASH_MISMATCH')
    decision = read_json(path)['D2']
    if decision.get('status') != 'USER_APPROVED' or decision.get('method') != DIRECTION_METHOD:
        raise ValueError('D2_APPROVAL_CONTENT_MISMATCH')
    return schedule


def preflight(policy):
    issues = []
    try:
        schedule = _direction_approval(policy)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        schedule = None
        issues.append('D2_DIRECTION_APPROVAL_UNAVAILABLE:' + str(exc))
    contract_id = policy['method'].get('approved_contract_id')
    try:
        contract = _registered_contract(contract_id)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        contract = None
        issues.append('REGISTERED_CONTRACT_UNAVAILABLE:' + str(exc))
    if contract is None:
        issues.append('REAL_INPUT_CONTRACT_AND_ADAPTER_NOT_REGISTERED')
    elif (contract.get('raw_sha256') != policy['raw_sha256']
          or contract.get('contract_id') != contract_id):
        issues.append('REAL_CONTRACT_INPUT_HASH_OR_ID_MISMATCH')
    else:
        if not contract.get('approval_source') or not callable(contract.get('adapter')):
            issues.append('REAL_CONTRACT_APPROVAL_OR_ADAPTER_MISSING')
        approval = contract.get('approval_source')
        if (schedule and (not isinstance(approval, dict)
                          or approval.get('path') != schedule['approval_path']
                          or approval.get('sha256') != schedule['approval_sha256'])):
            issues.append('REAL_CONTRACT_DIRECTION_APPROVAL_MISMATCH')
        try:
            _validate_contract(contract)
        except (ValueError, KeyError, TypeError) as exc:
            issues.append('REGISTERED_CONTRACT_INVALID:' + str(exc))
    conditional = contract is not None and contract.get('approval') == 'CONDITIONAL_ANALYSIS'
    if conditional:
        if (contract_id != 'G1_CONDITIONAL_ENU_V1' or contract.get('source_crs') != 'UNVERIFIED'
                or policy['semantics']['crs']['status'] != 'UNVERIFIED'
                or policy['semantics']['distance_policy']['status'] != 'CONDITIONAL_ANALYSIS_AUTHORIZED'
                or policy['semantics']['distance_policy']['value'] != contract_id
                or policy['method']['processing_status'] != 'APPROVED_CONDITIONAL_ANALYSIS'):
            issues.append('CONDITIONAL_ANALYSIS_POLICY_MISMATCH')
    else:
        if policy['semantics']['crs']['status'] not in ('VERIFIED', 'APPROVED'):
            issues.append('D1_COORDINATE_DATUM_UNKNOWN')
        if policy['semantics']['distance_policy']['status'] != 'APPROVED':
            issues.append('D1_DISTANCE_CONTRACT_UNAPPROVED')
        if contract is not None and contract.get('approval') != 'APPROVED_FOR_REAL_INPUT':
            issues.append('REAL_CONTRACT_APPROVAL_MISSING')
        if policy['method']['processing_status'] != 'APPROVED_FOR_REAL_INPUT':
            issues.append('REAL_PROCESSING_NOT_APPROVED')
    return issues


def trusted_real_reference(raw, record_ids, policy):
    """Resolve only a code-registered real contract; config strings cannot approve.

    The adapter consumes a copy. Original values and adapter version remain
    alongside working coordinates for the raw-to-working relation.
    """
    issues = preflight(policy)
    if issues:
        raise ValueError('; '.join(issues))
    registration = _registered_contract(policy['method']['approved_contract_id'])
    if (not isinstance(record_ids, list) or len(record_ids) != len(set(record_ids))
            or set(record_ids) != set(registration['record_ids'])):
        raise ValueError('REAL_CONTRACT_SCOPE_MISMATCH')
    if digest(DATA) != policy['raw_sha256']:
        raise ValueError('REAL_INPUT_HASH_MISMATCH')
    disk_raw = read_json(DATA)
    if any(rid not in raw or rid not in disk_raw or object_hash(raw[rid]) != object_hash(disk_raw[rid])
           for rid in record_ids):
        raise ValueError('REAL_INPUT_VALUES_MISMATCH')
    approved = deepcopy({k: v for k, v in registration.items() if k != 'adapter'})
    _validate_contract(approved)
    records = []
    for rid in record_ids:
        record = registration['adapter'](rid, deepcopy(raw[rid]))
        if (record['record_id'] != rid or record['indices'] != list(range(len(raw[rid][1])))
                or object_hash(record['timestamps']) != object_hash(raw[rid][0])):
            raise ValueError('REAL_ADAPTER_POINT_COVERAGE_MISMATCH')
        record['raw_values'] = deepcopy(raw[rid])
        record['raw_record_sha256'] = object_hash(raw[rid])
        record['adapter_version'] = approved['adapter_version']
        records.append(record)
    _validate_inputs(records)
    provenance = _provenance(records, approved, source_kind=approved.get('classification', 'CURRENT_RUN_REAL_BASELINE'),
                             raw_sha256=policy['raw_sha256'],
                             raw_scope_sha256=object_hash({rid: raw[rid] for rid in record_ids}),
                             parent_version='RAW:' + policy['raw_sha256'])
    return records, approved, provenance


def run_real(raw, record_ids, policy):
    issues = preflight(policy)
    n = sum(len(raw[k][1]) for k in record_ids)
    if issues:
        return {'status': 'BLOCKED', 'reason': issues,
                'stage_counts': {'input': n, 'segmented': None, 'filtered': None, 'denoised': None,
                                 'simplified': None, 'not_processed': n},
                'unavailable_metrics_reason': '; '.join(issues)}
    records, contract, provenance = trusted_real_reference(raw, record_ids, policy)
    return run_planar(records, contract, provenance)


def run_constructed(records, contract):
    """Explicit fixture entry; never accepts a real-input path or registration."""
    reference, approved, provenance = trusted_constructed_reference(records, contract)
    return run_planar(reference, approved, provenance)


def run_planar(records, contract, provenance):
    """Actual split → separate filter → one-pass denoise → DP → numeric audit."""
    _validate_contract(contract)
    _validate_inputs(records)
    parameters = contract['parameters']
    groups = {k: [] for k in ('filtered', 'denoised', 'simplified', 'retained')}
    per_record, ledger = [], []
    stages = dict.fromkeys(('input', 'segmented', 'filtered', 'denoised', 'simplified', 'retained', 'not_processed'), 0)
    segment_counts = dict.fromkeys(('total', 'filtered', 'processed'), 0)

    def terminal(record, ids, stage, reasons, segment_index, parent_hash):
        selected = select_indices(record, ids, time_reliable=parameters['time_reliable'])
        groups[stage].append(selected)
        for index, timestamp, xy in zip(selected['indices'], selected['timestamps'], selected['xy']):
            ledger.append({'record_id': record['record_id'], 'original_index': index,
                           'segment_index': segment_index, 'action': stage, 'reasons': list(reasons),
                           'parent_hash': parent_hash, 'timestamp': timestamp, 'xy': deepcopy(xy)})

    for record in records:
        counts = dict.fromkeys(stages, 0)
        counts['input'] = len(record['indices'])
        split = split_trajectory(record, parameters['dt'], parameters['distance'], time_reliable=parameters['time_reliable'])
        for segment in split['segments']:
            segment['parent_hash'] = object_hash(record)
        filtered = filter_segments(split['segments'], parameters['min_points'], parameters['min_length'], time_reliable=parameters['time_reliable'])
        counts['segmented'] = len(split['segments'])
        for segment in filtered['dropped']:
            counts['filtered'] += len(segment['indices'])
            terminal(segment, segment['indices'], 'filtered', segment['filter_reasons'], segment['segment_index'], object_hash(record))
        segments = []
        for segment in filtered['kept']:
            clean = denoise_trajectory(segment, parameters['direction'], method=DIRECTION_METHOD,
                                       time_reliable=parameters['time_reliable'])
            denoised = clean['record']
            denoised['parent_hash'] = object_hash(segment)
            retained = douglas_peucker_indices(denoised['xy'], parameters['dp'], denoised['indices'])
            output = select_indices(denoised, retained, time_reliable=parameters['time_reliable'])
            output['parent_hash'] = object_hash(denoised)
            review = verify_simplification(denoised, output, parameters['dp'], expected_parent_hash=object_hash(denoised))
            simplified = [i for i in denoised['indices'] if i not in retained]
            terminal(segment, clean['deleted_indices'], 'denoised', ['DIRECTION_RULE'], segment['segment_index'], object_hash(segment))
            terminal(denoised, simplified, 'simplified', ['DP_WITHIN_TOLERANCE'], segment['segment_index'], object_hash(denoised))
            terminal(denoised, retained, 'retained', ['DP_RETAINED'], segment['segment_index'], object_hash(denoised))
            counts['denoised'] += len(clean['deleted_indices'])
            counts['simplified'] += len(simplified)
            counts['retained'] += len(retained)
            segments.append({'segment_index': segment['segment_index'], 'input': segment, 'denoise': clean,
                             'output': output, 'independent_review': review})
        record_segments = {'total': len(split['segments']), 'filtered': len(filtered['dropped']), 'processed': len(segments)}
        per_record.append({'record_id': record['record_id'], 'source_record': deepcopy(record),
                           'parent_hash': object_hash(record), 'boundaries': split['boundaries'],
                           'filtered_segments': filtered['dropped'], 'processed_segments': segments,
                           'stage_counts': counts, 'segment_counts': record_segments,
                           'terminal_status': ('EMPTY_INPUT' if not record['indices'] else
                                               'ALL_FILTERED' if not segments else 'PROCESSED')})
        for key in stages:
            stages[key] += counts[key]
        for key in segment_counts:
            segment_counts[key] += record_segments[key]
    accounting = audit_point_accounting(records, groups)
    reviews = [s['independent_review'] for r in per_record for s in r['processed_segments']]
    passed = accounting['status'] == 'VERIFIED' and all(r['status'] == 'VERIFIED' for r in reviews)
    return {'status': 'VERIFIED' if passed else 'REJECTED', 'classification': provenance['source_kind'],
            'parameters': deepcopy(parameters), 'contract': deepcopy(contract), 'provenance': deepcopy(provenance),
            'input_hash': object_hash(records), 'records': per_record, 'point_actions': ledger,
            'stage_counts': stages, 'segment_counts': segment_counts, 'accounting': accounting,
            'quality_status': 'PENDING_RESEARCH_REVIEW', 'modified_values': 0,
            'output_limitation': ('EMPTY_INPUT' if not stages['input'] else
                                  'ALL_FILTERED_NO_OUTPUT' if not stages['retained'] else
                                  'GEOMETRY_IS_NOT_GROUND_TRUTH_OR_QUALITY_IMPROVEMENT')}
