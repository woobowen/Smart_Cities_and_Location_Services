"""Conditional processing chain; synthetic contracts cannot authorize teacher data.

Production registrations are reviewed code, not model/config supplied approvals.
No real-input registration exists: D1/D2 and parameters remain unapproved.
"""
from .geometry import (split_trajectory, filter_segments, denoise_trajectory,
                       douglas_peucker_indices, select_indices, validate_trajectory)
from .evaluation import verify_simplification, audit_point_accounting
from .io import object_hash

DIRECTION_METHOD = 'single_pass_simultaneous_keep_undefined'
# Add a real contract/coordinate adapter only after an archived research approval.
REAL_CONTRACTS = {}


def preflight(policy):
    issues = []
    if policy['semantics']['crs']['status'] not in ('VERIFIED', 'APPROVED'):
        issues.append('D1_COORDINATE_DATUM_UNKNOWN')
    if policy['semantics']['distance_policy']['status'] != 'APPROVED':
        issues.append('D1_DISTANCE_CONTRACT_UNAPPROVED')
    if policy['method']['processing_status'] != 'APPROVED_FOR_REAL_INPUT':
        issues.append('D2_DIRECTION_SCHEDULE_UNAPPROVED')
    contract_id=policy['method'].get('approved_contract_id')
    contract = REAL_CONTRACTS.get(contract_id) if isinstance(contract_id,str) else None
    if contract is None:
        issues.append('REAL_INPUT_CONTRACT_AND_ADAPTER_NOT_REGISTERED')
    elif contract['raw_sha256'] != policy['raw_sha256']:
        issues.append('REAL_CONTRACT_INPUT_HASH_MISMATCH')
    return issues


def run_real(raw, record_ids, policy):
    issues = preflight(policy)
    n = sum(len(raw[k][1]) for k in record_ids)
    if issues:
        return {'status':'BLOCKED','reason':issues,
                'stage_counts':{'input':n,'segmented':None,'filtered':None,'denoised':None,
                                'simplified':None,'not_processed':n},
                'unavailable_metrics_reason':'; '.join(issues)}
    contract = REAL_CONTRACTS[policy['method']['approved_contract_id']]
    if set(record_ids) != set(contract['record_ids']):
        raise ValueError('REAL_CONTRACT_SCOPE_MISMATCH')
    records = [contract['adapter'](rid, raw[rid]) for rid in record_ids]
    return run_planar(records, contract['parameters'], classification='CURRENT_RUN_REAL_BASELINE')


def run_constructed(records, contract):
    """Explicit fixture entry. Never reads DATA or accepts a path to real input."""
    if (contract.get('scope') != 'CONSTRUCTED_PLANAR_ONLY'
            or contract.get('approval') != 'ENGINEERING_TEST_ONLY'
            or contract.get('method') != DIRECTION_METHOD
            or any(not r['record_id'].startswith('fixture:') for r in records)):
        raise ValueError('CONSTRUCTED_CONTRACT_REQUIRED')
    return run_planar(records, contract['parameters'], classification='CONSTRUCTED_FIXTURE')


def run_planar(records, parameters, *, classification):
    """Actual split → separate filter → one-pass denoise → DP → independent audit."""
    required = {'dt','distance','min_points','min_length','direction','dp','time_reliable'}
    if set(parameters) != required: raise ValueError('INCOMPLETE_PARAMETERS')
    groups = {k:[] for k in ('filtered','denoised','simplified','retained')}
    per_record = []; stages = {'input':0,'segmented':0,'filtered':0,'denoised':0,'simplified':0,'not_processed':0}
    for record in records:
        validate_trajectory(record)
        stages['input'] += len(record['indices'])
        split = split_trajectory(record, parameters['dt'], parameters['distance'], time_reliable=parameters['time_reliable'])
        filtered = filter_segments(split['segments'], parameters['min_points'], parameters['min_length'], time_reliable=parameters['time_reliable'])
        stages['segmented'] += len(split['segments'])
        groups['filtered'].extend(filtered['dropped'])
        segments = []
        for segment in filtered['kept']:
            clean = denoise_trajectory(segment, parameters['direction'], method=DIRECTION_METHOD,
                                       time_reliable=parameters['time_reliable'])
            denoised = clean['record']
            retained = douglas_peucker_indices(denoised['xy'], parameters['dp'], denoised['indices'])
            output = select_indices(denoised, retained, time_reliable=parameters['time_reliable'])
            output['parent_hash'] = object_hash(denoised)
            review = verify_simplification(denoised, output, parameters['dp'], expected_parent_hash=object_hash(denoised))
            groups['denoised'].append(select_indices(segment, clean['deleted_indices']))
            groups['simplified'].append(select_indices(denoised, [i for i in denoised['indices'] if i not in retained]))
            groups['retained'].append(output)
            segments.append({'segment_index':segment['segment_index'],'input':segment,'denoise':clean,
                             'output':output,'independent_review':review})
        per_record.append({'record_id':record['record_id'],'boundaries':split['boundaries'],
                           'filtered_segments':filtered['dropped'],'processed_segments':segments})
    accounting = audit_point_accounting(records, groups)
    ledger = [{'record_id':r['record_id'],'original_index':i,'action':stage,
               'timestamp':t,'xy':xy} for stage, rows in groups.items() for r in rows
              for i,t,xy in zip(r['indices'],r['timestamps'],r['xy'])]
    for stage in ('filtered','denoised','simplified'):
        stages[stage] = accounting['stage_points'][stage]
    stages['retained'] = accounting['stage_points']['retained']
    reviews = [s['independent_review'] for r in per_record for s in r['processed_segments']]
    passed = accounting['status']=='VERIFIED' and all(r['status']=='VERIFIED' for r in reviews)
    return {'status':'VERIFIED' if passed else 'REJECTED','classification':classification,
            'parameters':parameters,'input_hash':object_hash(records),'records':per_record,
            'point_actions':ledger,'stage_counts':stages,'accounting':accounting,
            'quality_status':'PENDING_RESEARCH_REVIEW','modified_values':0}
