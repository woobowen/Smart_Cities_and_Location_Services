"""Predeclared feasibility and conservative selection, with no scalar quality score."""
from .io import object_hash

PARAMETERS=('dt','distance','min_points','min_length','direction','dp')
REFERENCE={'dt':30,'distance':400,'min_points':5,'min_length':65,'direction':35,'dp':5}
GRID={'dt':[15,20,30,45,60],'distance':[95,200,400,600,800],
      'min_points':[2,3,5,7,10],'min_length':[0,32.5,65,97.5,130],
      'direction':[15,25,35,45,60],'dp':[0,0.5,1,2,5,10,20]}


def config_id(parameters):
    return 'cfg-'+object_hash({k:float(parameters[k]) for k in PARAMETERS})[:16]


def legal_parameters(value):
    if not isinstance(value,dict) or set(value)!=set(PARAMETERS):return False,'PARAMETER_FIELDS_MISMATCH'
    for k,v in value.items():
        if isinstance(v,bool) or not isinstance(v,(int,float)) or v not in GRID[k]:
            return False,'OUTSIDE_REGISTERED_GRID:'+k
    if float(value['min_points'])!=int(value['min_points']):return False,'MIN_POINTS_NOT_INTEGER'
    return True,None


def execution_parameters(value):
    ok,reason=legal_parameters(value)
    if not ok:raise ValueError(reason)
    # JSON schema uses number for all values. This exact integer conversion is
    # representation normalization after legality accounting, never clamping.
    return {**value,'min_points':int(value['min_points'])}


def search_sequence():
    result=[REFERENCE.copy()]
    for key,values in [('dp',[0,1,2,10,20]),('direction',[15,25,45,60]),('dt',[15,60]),
                       ('distance',[95,800]),('min_points',[2,3,7]),('min_length',[0,32.5,130])]:
        result.extend({**REFERENCE,key:value} for value in values)
    assert len(result)==20
    return result


def compare(candidate,reference):
    """Same record, complete common reference; reference itself has no gain."""
    c,b=candidate['metrics'],reference['metrics'];reasons=[]
    before={r['index']:r['error'] for r in b['common_point_errors'] if r['error'] is not None}
    after={r['index']:r['error'] for r in c['common_point_errors'] if r['error'] is not None}
    allowance=max(c['common_floating_allowance'],b['common_floating_allowance'])
    coverage_preserved=set(before)<=set(after)
    if not coverage_preserved:reasons.append('COMMON_COVERED_IDENTITIES_LOST')
    if c['raw_break_crossings']:reasons.append('RAW_BREAKPOINT_CROSSED')
    if not c['dp_checks_passed'] or c['n_dp_exceedances']:reasons.append('DP_CONTRACT_FAILED')
    if b['record_covered'] and not c['record_covered']:reasons.append('RECORD_COVERAGE_LOST')
    if c['raw_windows_covered']<b['raw_windows_covered']:reasons.append('RAW_WINDOW_COVERAGE_LOST')
    baseline_error=max(before.values()) if before else None
    on_base=max(after[i] for i in before) if before and coverage_preserved else None
    same_upstream=all(candidate['parameters'][k]==reference['parameters'][k] for k in PARAMETERS if k!='dp') and candidate['order']==reference['order']=='S-D-P'
    cp_mode=same_upstream
    if cp_mode:
        if c['n_dp_input']!=b['n_dp_input']:reasons.append('DP_REFERENCE_COUNT_CHANGED')
        p_before=next(s for s in reference['stages'] if s['name']=='P')['input']
        p_after=next(s for s in candidate['stages'] if s['name']=='P')['input']
        if p_before!=p_after:reasons.append('DP_REFERENCE_CHANGED')
        if c['dp_max_error'] is not None and c['dp_max_error']>5+allowance:reasons.append('COMMON_DP_BUDGET_EXCEEDED')
        gain=c['n_dp_output']<b['n_dp_output']
    else:
        if baseline_error is not None and (on_base is None or on_base>baseline_error+allowance):
            reasons.append('COMMON_GEOMETRIC_PROTECTION_DEGRADED')
        gain=(len(after)>len(before) or (on_base is not None and baseline_error is not None and on_base<baseline_error-allowance))
    hard=any(r in reasons for r in ('RAW_BREAKPOINT_CROSSED','DP_CONTRACT_FAILED','COMMON_DP_BUDGET_EXCEEDED','DP_REFERENCE_CHANGED','DP_REFERENCE_COUNT_CHANGED'))
    status=('REJECTED_BY_CONSTRAINT' if hard else 'TRADEOFF' if reasons else
            'SUPPORTED_WITHIN_SCOPE' if gain else 'NO_DEMONSTRATED_GAIN')
    return {'record_id':candidate['record_id'],'status':status,'feasible':not reasons,'strict_gain':bool(gain and not reasons),
            'protection_failures':reasons,'dp_only_comparison':cp_mode,
            'baseline_covered_count':len(before),'candidate_covered_count':len(after),
            'candidate_covered_indices':sorted(after),
            'coverage_delta':len(after)-len(before),'baseline_common_max':baseline_error,
            'candidate_max_on_baseline_covered':on_base,
            'newly_covered_max_error':max((after[i] for i in set(after)-set(before)),default=None),
            'quality_accepted':False,'numerical_allowance':allowance}


def select_record(candidates, reference_id):
    reference=candidates[reference_id]
    assessments={cid:compare(c,reference) for cid,c in candidates.items()}
    feasible=[cid for cid,a in assessments.items() if a['feasible']]
    def descriptive_dominates(first,second):
        x,y=assessments[first],assessments[second]
        if not set(y['candidate_covered_indices'])<=set(x['candidate_covered_indices']):return False
        a,b=x['candidate_max_on_baseline_covered'],y['candidate_max_on_baseline_covered']
        tol=max(x['numerical_allowance'],y['numerical_allowance'])
        if (a is None)!=(b is None):return False
        if a is not None and a>b+tol:return False
        n1,n2=candidates[first]['metrics']['n_final'],candidates[second]['metrics']['n_final']
        if n1>n2:return False
        return (x['candidate_covered_count']>y['candidate_covered_count'] or n1<n2 or
                (a is not None and a<b-tol))
    frontier=[cid for cid in feasible if not any(descriptive_dominates(other,cid) for other in feasible if other!=cid)]
    evidence={'assessments':assessments,'feasible_ids':feasible,'frontier':frontier,
              'pareto_dimensions':['covered_original_point_identities maximize','maximum_error_on_reference_covered minimize','final_point_count minimize'],
              'pareto_is_quality_score':False}
    gains=[cid for cid,a in assessments.items() if a['strict_gain']]
    if not gains:return reference_id,{**evidence,'reason':'NO_UNAMBIGUOUS_PROTECTED_GAIN','eligible_gain_frontier':[]}
    cp=[cid for cid in gains if assessments[cid]['dp_only_comparison']]
    other=[cid for cid in gains if cid not in cp]
    if cp and not other:
        selected=min(cp,key=lambda cid:(candidates[cid]['metrics']['n_dp_output'],
            candidates[cid]['metrics']['dp_max_error'] or 0,candidates[cid]['parameters']['dp'],cid))
        return selected,{**evidence,'reason':'FIXED_5_WORK_METRE_BUDGET_COMPRESSION','eligible_gain_frontier':cp}
    def dominates(a,b):
        x,y=assessments[a],assessments[b]
        if x['dp_only_comparison']!=y['dp_only_comparison']:return False
        e1,e2=x['candidate_max_on_baseline_covered'],y['candidate_max_on_baseline_covered']
        tol=max(x['numerical_allowance'],y['numerical_allowance'])
        if e1 is None or e2 is None:
            return e1 is None and e2 is None and x['candidate_covered_count']>y['candidate_covered_count']
        return (x['candidate_covered_count']>=y['candidate_covered_count'] and e1<=e2+tol and
                (x['candidate_covered_count']>y['candidate_covered_count'] or e1<e2-tol))
    gain_frontier=[a for a in gains if not any(dominates(b,a) for b in gains if a!=b)]
    selected=gain_frontier[0] if len(gain_frontier)==1 else reference_id
    return selected,{**evidence,'reason':'UNIQUE_PROTECTED_PARETO_GAIN' if len(gain_frontier)==1 else 'INCOMPARABLE_OR_TIED_RETAIN_REFERENCE',
                     'eligible_gain_frontier':gain_frontier}


def prediction_result(proposal, candidate, reference):
    metric=proposal['metric_id'];sign=proposal['predicted_sign']
    common={'metric_id':metric,'predicted_sign':sign,'reference_handle':object_hash(reference),
            'candidate_handle':object_hash(candidate)}
    if sign=='not_predicted':return {**common,'status':'NOT_PREDICTED','evaluable':False}
    allowed=('n_final','common_covered_points','common_max_error','dp_saving','raw_break_crossings','n_direction_removed')
    if metric not in allowed:return {**common,'status':'UNREGISTERED_PREDICTION_METRIC','evaluable':False}
    a,b=candidate['metrics'][metric],reference['metrics'][metric]
    if a is None or b is None:return {**common,'status':'METRIC_UNAVAILABLE','evaluable':False}
    if metric=='dp_saving' and any(candidate['parameters'][k]!=reference['parameters'][k] for k in PARAMETERS if k!='dp'):
        return {**common,'status':'DIFFERENT_DP_REFERENCE','evaluable':False}
    if metric=='common_max_error':
        ia={r['index'] for r in candidate['metrics']['common_point_errors'] if r['error'] is not None}
        ib={r['index'] for r in reference['metrics']['common_point_errors'] if r['error'] is not None}
        if ia!=ib:return {**common,'status':'DIFFERENT_COMMON_COVERAGE','evaluable':False}
    delta=a-b;eps=0 if metric in ('n_final','common_covered_points','raw_break_crossings','n_direction_removed') else (1e-12 if metric=='dp_saving' else candidate['metrics']['common_floating_allowance'])
    observed='unchanged' if abs(delta)<=eps else 'increase' if delta>0 else 'decrease'
    if observed=='unchanged':return {**common,'status':'NEAR_ZERO_OR_UNCHANGED','delta':delta,'observed_sign':observed,'evaluable':False,'prediction_matches':sign==observed}
    return {**common,'status':'EVALUABLE','delta':delta,'observed_sign':observed,'evaluable':True,'prediction_matches':sign==observed}
