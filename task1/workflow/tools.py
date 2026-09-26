"""Allowlisted deterministic task tools; every value comes from current raw data."""
from .io import DATA, digest, read_json, object_hash
from .diagnostics import profile, aggregate, time_boundaries, duplicate_details, independent_profile_review


def execute_tool(action, record_ids, policy, previous_profiles=None,classification='CURRENT_RUN_REAL_DATA',previous_baseline=None,
                 *, target_artifact=None, target_binding=None, requested_components=None):
    if digest(DATA)!=policy['raw_sha256']:
        raise ValueError('INPUT_HASH_MISMATCH')
    raw=read_json(DATA)
    subset={rid:raw[rid] for rid in record_ids}
    base={'classification':classification,'input_sha256':policy['raw_sha256'],
          'record_ids':record_ids,'input_records':len(subset),
          'input_points':sum(len(v[1]) for v in subset.values()),'modified_values':0,
          'parent_version':'RAW:'+policy['raw_sha256'],'semantics_version':policy['semantics_version'],
          'metrics_version':policy['metrics_version']}
    if target_artifact is not None:
        from .artifact_review import review_artifact
        if target_binding is None: raise ValueError('REGISTERED_TARGET_REQUIRED')
        expected={'verify_profiles':'profile_pilot', 'verify_time_boundaries':'time_boundaries',
                  'verify_duplicate_details':'duplicate_details', 'verify_baseline':'baseline'}
        target_action=target_binding['action']
        if action != 'recompute_check' and expected.get(action) != target_action:
            raise ValueError('REVIEW_TARGET_ACTION_MISMATCH')
        payload=review_artifact(target_action, subset, target_artifact, policy, target_binding, requested_components)
        return {**base,'status':payload['status'],'result':payload}
    if action in ('verify_time_boundaries', 'verify_duplicate_details'):
        raise ValueError('REGISTERED_TARGET_REQUIRED')
    if requested_components is not None:
        raise ValueError('REGISTERED_TARGET_REQUIRED_FOR_COVERAGE_REQUEST')
    if action in ('contract_snapshot', 'source_evidence'):
        payload={'scope':'SAVED_CONTRACT_ONLY_NOT_SOURCE_VERIFICATION','semantics':policy['semantics'],'method':policy['method'],
                 'starter_reference':policy['starter_reference'],'teacher_95m':policy['teacher_95m']}
    elif action=='profile_pilot':
        rows=[profile(k,v,classification) for k,v in subset.items()]
        payload={'profiles':rows,'summary':aggregate(rows)}
    elif action=='time_boundaries':
        payload={'trajectories':[time_boundaries(k,v,policy['starter_reference']['dt_seconds'],classification) for k,v in subset.items()],
                 'scope':'TIME_ONLY_DIAGNOSTIC_NOT_BASELINE'}
    elif action=='duplicate_details':
        payload={'trajectories':[duplicate_details(k,v) for k,v in subset.items()],
                 'scope':'EXACT_RAW_REPETITIONS; no noise judgment or deletion'}
    elif action in ('verify_profiles','recompute_check'):
        if previous_profiles is None:
            raise ValueError('MISSING_PROFILE_OUTPUT')
        payload=independent_profile_review(subset,previous_profiles)
        payload.update(checked_components=['record_scope','profile_fields','profile_counts'],
                       unchecked_components=['summary','artifact_binding'],
                       scope='UNBOUND_PROFILE_LIST_HELPER_NOT_TASK_CLOSURE')
        if payload['status'] != 'VERIFIED':
            if action == 'recompute_check': payload['exact_match'] = False
            return {**base,'status':'REJECTED','result':payload}
        by_id={p['record_id']:p for p in previous_profiles}
        selected=[by_id[k] for k in subset]
        if action=='recompute_check':
            recomputed=[profile(k,v,classification) for k,v in subset.items()]
            equal=object_hash(recomputed)==object_hash(selected)
            payload.update(recomputed_sha256=object_hash(recomputed),stored_sha256=object_hash(selected),exact_match=equal)
            if not equal:payload['status']='REJECTED'
    elif action=='verify_baseline':
        from .evaluation import review_baseline
        from .pipeline import trusted_real_reference
        if previous_baseline is None:raise ValueError('MISSING_BASELINE_OUTPUT')
        try:
            reference,contract,provenance=trusted_real_reference(raw,record_ids,policy)
            payload=review_baseline(previous_baseline,reference,contract,provenance)
        except ValueError as exc:
            payload={'status':'REJECTED','errors':['TRUSTED_REFERENCE_UNAVAILABLE:'+str(exc)],
                     'checked_components':[], 'unchecked_components':['baseline']}
    elif action=='baseline':
        from .pipeline import run_real
        return {**base, **run_real(raw, record_ids, policy)}
    elif action == 'source_check':
        from .sources import source_context
        payload = {'sources':source_context(), 'scope':'EXACT_LOCAL_SOURCE_EXCERPTS; datum remains unverified'}
    elif action == 'escalate':
        payload = {'status':'BLOCKED','reason':'ROLE_REQUESTED_RESEARCH_REVIEW; no numeric modification'}

    else:
        raise ValueError('UNKNOWN_TOOL')
    return {**base,'status':payload.get('status','EXECUTED'),'result':payload}
