"""Allowlisted deterministic task tools; every value comes from current raw data."""
from .io import DATA, digest, read_json, object_hash
from .diagnostics import profile, aggregate, time_boundaries, duplicate_details, independent_profile_review


def execute_tool(action, record_ids, policy, previous_profiles=None,classification='CURRENT_RUN_REAL_DATA'):
    if digest(DATA)!=policy['raw_sha256']:
        raise ValueError('INPUT_HASH_MISMATCH')
    raw=read_json(DATA)
    subset={rid:raw[rid] for rid in record_ids}
    base={'classification':classification,'input_sha256':policy['raw_sha256'],
          'record_ids':record_ids,'input_records':len(subset),
          'input_points':sum(len(v[1]) for v in subset.values()),'modified_values':0,
          'parent_version':'RAW:'+policy['raw_sha256'],'semantics_version':policy['semantics_version'],
          'metrics_version':policy['metrics_version']}
    if action=='source_evidence':
        payload={'semantics':policy['semantics'],'method':policy['method'],
                 'starter_reference':policy['starter_reference'],'teacher_95m':policy['teacher_95m']}
    elif action=='profile_pilot':
        rows=[profile(k,v,classification) for k,v in subset.items()]
        payload={'profiles':rows,'summary':aggregate(rows)}
    elif action=='time_boundaries':
        payload={'trajectories':[time_boundaries(k,v,policy['starter_reference']['dt_seconds']) for k,v in subset.items()],
                 'scope':'TIME_ONLY_DIAGNOSTIC_NOT_BASELINE'}
    elif action=='duplicate_details':
        payload={'trajectories':[duplicate_details(k,v) for k,v in subset.items()],
                 'scope':'EXACT_RAW_REPETITIONS; no noise judgment or deletion'}
    elif action in ('verify_profiles','recompute_check'):
        if previous_profiles is None:
            raise ValueError('MISSING_PROFILE_OUTPUT')
        selected=[p for p in previous_profiles if p['record_id'] in subset]
        payload=independent_profile_review(subset,selected)
        if action=='recompute_check':
            recomputed=[profile(k,v,classification) for k,v in subset.items()]
            equal=object_hash(recomputed)==object_hash(selected)
            payload.update(recomputed_sha256=object_hash(recomputed),stored_sha256=object_hash(selected),exact_match=equal)
            if not equal:payload['status']='REJECTED'
    elif action=='baseline':
        # Deliberately no projection/deletion fallback. The diagnostic path remains usable.
        return {**base,'status':'BLOCKED','reason':policy['method']['blocking_ids'],
                'stage_counts':{'input':base['input_points'],'segmented':None,'filtered':None,
                                'denoised':None,'simplified':None,'not_processed':base['input_points']},
                'unavailable_metrics_reason':'CRS/distance policy and direction execution schedule unresolved'}
    else:
        raise ValueError('UNKNOWN_TOOL')
    return {**base,'status':payload.get('status','EXECUTED'),'result':payload}
