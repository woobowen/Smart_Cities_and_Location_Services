"""Independent F02 trust-boundary challenges with hand-built line artifacts.

No processing runner, geometry producer, or private review helper builds answers.
Every source handle is created before the candidate. All cases are engineering tests.
"""
from copy import deepcopy
import math
from pathlib import Path
import sys
from unittest.mock import patch
from contextlib import ExitStack
import json

ROOT=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(ROOT))
from task1.workflow import pipeline, geometry, tools
from task1.workflow.evaluation import review_baseline
from task1.workflow.io import CONFIG, digest, object_hash, read_json, write_json

HERE=Path(__file__).resolve().parent
SOURCES=['task1/workflow/'+n for n in ['pipeline.py','evaluation.py','coordinates.py','geometry.py','tools.py','artifact_review.py','io.py']]+[
    'task1/config/goal1.json','task1/config/conditional_planar.json',
    'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json',
    'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md']


def features(record):
    # This fixture consists solely of positive-x unit-speed lines.
    ids,times,xy=record['indices'],record['timestamps'],record['xy']
    edges=[]
    for pos in range(1,len(ids)):
        distance=float(xy[pos][0]-xy[pos-1][0]);dt=times[pos]-times[pos-1]
        assert distance>0 and dt>0
        edges.append({'from_index':ids[pos-1],'to_index':ids[pos],'dt':dt,'dt_reason':None,
                      'distance':distance,'speed':distance/dt,'speed_reason':None,
                      'direction_degrees':90.0,'direction_reason':None})
    return {'edges':edges,'length':float(xy[-1][0]-xy[0][0]) if len(xy)>1 else 0.0,
            'direction_convention':'CLOCKWISE_FROM_POSITIVE_Y','time_reliable':True,
            'coverage':{'edge_denominator':len(edges),'speed_computable':len(edges),'direction_computable':len(edges),
                        'reason':None if edges else 'NO_EDGES'}}


def selected(record,ids):
    positions=[record['indices'].index(i) for i in ids]
    result={'record_id':record['record_id'],'indices':list(ids),
            'timestamps':[record['timestamps'][p] for p in positions], 'xy':[deepcopy(record['xy'][p]) for p in positions]}
    result['features']=features(result)
    return result


def manual_numeric(clean,final,tolerance):
    # For these collinear inputs every indexed-interval error is exactly zero.
    n=len(clean['indices']);m=len(final['indices']);length=clean['features']['length'];out_length=final['features']['length']
    def metric(v,reason=None):return {'value':v,'reason':reason}
    coords=clean['xy'];scale=max([1.0,tolerance]+[abs(v) for p in coords for v in p]+[length])
    return {'status':'VERIFIED','quality_status':'PENDING_RESEARCH_REVIEW','errors':[],
            'reference_scope':'SAME_SIMPLIFICATION_INPUT','floating_allowance':64*sys.float_info.epsilon*scale,
            'floating_allowance_formula':'64 * binary64_epsilon * max(1, coordinate_extent, absolute_coordinate, tolerance)',
            'algorithm_tolerance':tolerance,'error_by_original_index':[{'index':i,'error':0.0} for i in clean['indices']],
            'exceeding_points':[], 'metrics':{
                'reference_points':metric(n),'simplified_points':metric(m),'saving':metric(1-m/n),
                'max_error':metric(0.0),'reference_length':metric(length),'simplified_length':metric(out_length),
                'length_change':metric(out_length-length),'relative_length_change':metric(out_length/length-1) if length else metric(None,'ZERO_REFERENCE_LENGTH')},
            'claims_supported':['ORDERED_SUBSEQUENCE','VALUES_UNCHANGED','INDEX_INTERVAL_ERROR_CHECK'],
            'claims_not_supported':['GROUND_TRUTH_RECOVERY','DETECTION_ACCURACY','QUALITY_IMPROVEMENT']}


def make_manual(records,**overrides):
    params={'dt':30,'distance':10,'min_points':3,'min_length':0,'direction':35,'dp':1,'time_reliable':True,**overrides}
    contract={'scope':'CONSTRUCTED_PLANAR_ONLY','approval':'ENGINEERING_TEST_ONLY',
              'method':'single_pass_simultaneous_keep_undefined','parameters':params}
    # The detached trusted handle is obtained before output construction.
    trusted=pipeline.trusted_constructed_reference(deepcopy(records),contract)
    reference,approved,provenance=trusted
    stage_keys=['input','segmented','filtered','denoised','simplified','retained','not_processed']
    counts=dict.fromkeys(stage_keys,0);segment_counts={'total':0,'filtered':0,'processed':0};ledger=[];rows=[]
    for source in reference:
        n=len(source['indices']);c=dict.fromkeys(stage_keys,0);c['input']=n;c['segmented']=1 if n else 0
        sc={'total':1 if n else 0,'filtered':0,'processed':0};filtered=[];processed=[]
        if n:
            segment=selected(source,source['indices']);segment.update(parent_hash=object_hash(source),segment_index=0,filter_reasons=[])
            if n<params['min_points']:segment['filter_reasons'].append('TOO_FEW_POINTS')
            if segment['features']['length']<params['min_length']:segment['filter_reasons'].append('TOO_SHORT_LENGTH')
            if segment['filter_reasons']:
                filtered=[segment];c['filtered']=n;sc['filtered']=1
                fates=[(i,'filtered',segment['filter_reasons'],object_hash(source)) for i in source['indices']]
            else:
                clean=selected(source,source['indices']);clean['parent_hash']=object_hash(segment)
                keep=list(source['indices']) if params['dp']==0 or n<3 else [source['indices'][0],source['indices'][-1]]
                final=selected(source,keep);final['parent_hash']=object_hash(clean)
                decisions=[]
                for pos,index in enumerate(source['indices']):
                    reason='ENDPOINT' if pos in (0,n-1) else 'MISSING_FOLLOWING_OUTGOING_EDGE' if pos>=n-2 else None
                    decisions.append({'index':index,'candidate':None if reason else False,'reason':reason,
                                      'previous_difference_degrees':None if reason else 0.0,
                                      'following_difference_degrees':None if reason else 0.0})
                denoise={'record':clean,'deleted_indices':[],'decisions':decisions,'method':approved['method'],'passes':1,'modified_values':0}
                processed=[{'segment_index':0,'input':segment,'denoise':denoise,'output':final,
                            'independent_review':manual_numeric(clean,final,params['dp'])}]
                c['retained']=len(keep);c['simplified']=n-len(keep);sc['processed']=1
                fates=[(i,'retained' if i in keep else 'simplified',['DP_RETAINED'] if i in keep else ['DP_WITHIN_TOLERANCE'],object_hash(clean)) for i in source['indices']]
            for i,action,reasons,parent_hash in fates:
                pos=source['indices'].index(i)
                ledger.append({'record_id':source['record_id'],'original_index':i,'segment_index':0,'action':action,
                               'reasons':reasons,'parent_hash':parent_hash,'timestamp':source['timestamps'][pos],'xy':deepcopy(source['xy'][pos])})
        rows.append({'record_id':source['record_id'],'source_record':deepcopy(source),'parent_hash':object_hash(source),
                     'boundaries':[],'filtered_segments':filtered,'processed_segments':processed,'stage_counts':c,'segment_counts':sc,
                     'terminal_status':'EMPTY_INPUT' if not n else 'ALL_FILTERED' if filtered else 'PROCESSED'})
        for k in counts:counts[k]+=c[k]
        for k in segment_counts:segment_counts[k]+=sc[k]
    accounting={'status':'VERIFIED','input_records':len(reference),'input_points':counts['input'],
                'stage_points':{k:counts[k] for k in ['filtered','denoised','simplified','retained']},
                'errors':[],'count_conserved':True,'modified_point_count':0}
    output={'status':'VERIFIED','classification':provenance['source_kind'],'parameters':deepcopy(params),
            'contract':deepcopy(approved),'provenance':deepcopy(provenance),'input_hash':object_hash(reference),
            'records':rows,'point_actions':ledger,'stage_counts':counts,'segment_counts':segment_counts,'accounting':accounting,
            'quality_status':'PENDING_RESEARCH_REVIEW','modified_values':0,
            'output_limitation':'EMPTY_INPUT' if not counts['input'] else 'ALL_FILTERED_NO_OUTPUT' if not counts['retained'] else 'GEOMETRY_IS_NOT_GROUND_TRUTH_OR_QUALITY_IMPROVEMENT'}
    return output,trusted


def main():
    HERE.mkdir(exist_ok=True)
    out=HERE/'initial_results.json'
    if out.exists():raise SystemExit('Refusing to overwrite C F02 initial evidence')
    source_before={p:digest(ROOT/p) for p in SOURCES}
    source={'record_id':'fixture:review','indices':[0,1,2,3],'timestamps':[0,1,2,3],'xy':[[0,0],[1,0],[2,0],[3,0]]}
    empty={'record_id':'fixture:empty','indices':[],'timestamps':[],'xy':[]}
    valid,trusted=make_manual([source]);trusted_before=deepcopy(trusted)
    write_json(HERE/'manual_valid_control.json',valid,exclusive=True)
    write_json(HERE/'trusted_handle.json',trusted,exclusive=True)
    cases=[]
    def record(name,candidate,expected='REJECTED',handle=trusted):
        try:result=review_baseline(candidate,*handle)
        except Exception as exc:result={'status':'EXCEPTION','exception_type':type(exc).__name__,'message':str(exc)}
        cases.append({'case':name,'expected':expected,'actual':result['status'],'result':result})
    forbidden_calls=[]
    def forbidden(*args,**kwargs):forbidden_calls.append(True);raise AssertionError('C_REVIEW_MUST_NOT_CALL_PRODUCTION_RUNNER')
    with ExitStack() as stack:
        for name in ['run_planar','run_constructed','run_real','split_trajectory','filter_segments','denoise_trajectory','douglas_peucker_indices','select_indices']:
            stack.enter_context(patch.object(pipeline,name,forbidden))
        for name in ['split_trajectory','filter_segments','denoise_trajectory','douglas_peucker_indices','select_indices','recompute_features','direction_candidates']:
            stack.enter_context(patch.object(geometry,name,forbidden))
        record('normal_four_point_manual_control',valid,'VERIFIED')
        def mutate(name,fn):
            candidate=deepcopy(valid);fn(candidate);record(name,candidate)
        def seg(o):return o['records'][0]['processed_segments'][0]
        mutate('only_final_coordinate_modified',lambda o:seg(o)['output']['xy'][0].__setitem__(0,999))
        def shift(o):
            for r in [seg(o)['denoise']['record'],seg(o)['output']]:r['xy']=[[x+1000,y+1000] for x,y in r['xy']]
        mutate('clean_and_final_shifted_ledger_unchanged',shift)
        mutate('all_records_and_ledger_dropped_counts_unchanged',lambda o:(o.update(records=[]),o.update(point_actions=[])))
        mutate('stage_counts_modified',lambda o:o['stage_counts'].update(input=999,retained=999))
        mutate('source_clean_final_and_ledger_shifted_together',lambda o:[r['xy'][0].__setitem__(0,1000) for r in [o['records'][0]['source_record'],seg(o)['input'],seg(o)['denoise']['record'],seg(o)['output']]])
        mutate('parameters_and_contract_dp_both_relaxed',lambda o:(o['parameters'].update(dp=999),o['contract']['parameters'].update(dp=999)))
        mutate('per_record_counts_forged',lambda o:o['records'][0]['stage_counts'].update(input=999))
        mutate('accounting_forged',lambda o:o['accounting'].update(input_points=999))
        mutate('missing_ledger_entry',lambda o:o['point_actions'].pop())
        mutate('duplicate_ledger_entry',lambda o:o['point_actions'].append(deepcopy(o['point_actions'][0])))
        mutate('wrong_terminal_reason',lambda o:o['point_actions'][0].update(reasons=['INVENTED']))
        mutate('boolean_point_index',lambda o:seg(o)['output']['indices'].__setitem__(0,False))
        mutate('boolean_ledger_index',lambda o:o['point_actions'][0].update(original_index=False))
        mutate('boolean_processed_wrapper_segment_index',lambda o:seg(o).update(segment_index=False))
        mutate('float_processed_wrapper_segment_index',lambda o:seg(o).update(segment_index=0.0))
        mutate('boolean_denosing_decision',lambda o:seg(o)['denoise']['decisions'][1].update(candidate=0))
        mutate('wrong_input_parent',lambda o:seg(o)['input'].update(parent_hash='WRONG'))
        mutate('wrong_clean_parent',lambda o:seg(o)['denoise']['record'].update(parent_hash='WRONG'))
        mutate('wrong_final_parent',lambda o:seg(o)['output'].update(parent_hash='WRONG'))
        mutate('wrong_raw_parent_version',lambda o:o['provenance'].update(parent_version='RAW:FORGED'))
        mutate('wrong_adapter_version',lambda o:o['provenance'].update(adapter_version='forged:v1'))
        mutate('wrong_raw_hash',lambda o:o['provenance'].update(raw_sha256='0'*64))
        mutate('wrong_raw_scope',lambda o:o['provenance'].update(record_scope=['fixture:foreign']))
        mutate('forged_numeric_review',lambda o:seg(o)['independent_review']['metrics']['saving'].update(value=0.99))
        mutate('wrong_filter_reason_on_kept_input',lambda o:seg(o)['input'].update(filter_reasons=['TOO_SHORT_LENGTH']))
        mutate('missing_processed_segment',lambda o:o['records'][0].update(processed_segments=[]))
        for name,records,params in [('legitimate_empty_task',[],{}),('legitimate_empty_record',[empty],{}),
                                   ('legitimate_all_filtered',[source],{'min_points':5,'min_length':10})]:
            candidate,handle=make_manual(records,**params);record(name,candidate,'VERIFIED',handle)
            if name=='legitimate_all_filtered':
                bad=deepcopy(candidate);bad['records'][0]['filtered_segments'][0]['filter_reasons']=['TOO_FEW_POINTS']
                record('omitted_filter_reason',bad,'REJECTED',handle)
        candidate,handle=make_manual([source,empty]);record('complete_multiple_records',candidate,'VERIFIED',handle)
        bad=deepcopy(candidate);bad['records'].pop();record('empty_record_omitted',bad,'REJECTED',handle)
        swapped=deepcopy(candidate);swapped['records'].reverse();swapped['point_actions'].reverse();record('legal_record_and_ledger_reordering',swapped,'VERIFIED',handle)
        record('no_external_handle',valid,'REJECTED',())
        mutated_handle=deepcopy(trusted);mutated_handle[0][0]['xy'][0][0]=1000
        record('trusted_reference_hash_detects_mutation',valid,'REJECTED',mutated_handle)
        fixture={'fixture:a':[[0,1,2],[[0,0],[1,0],[2,0]]],'fixture:b':[[0,1],[[0,0],[1,1]]]}
        raw_path=HERE/'foreign_scope_raw.json';write_json(raw_path,fixture,exclusive=True)
        policy=read_json(CONFIG);policy['raw_sha256']=digest(raw_path)
        with patch.object(tools,'DATA',raw_path):
            tool_result=tools.execute_tool('verify_baseline',list(fixture),policy,classification='ENGINEERING_TEST',previous_baseline=valid)
        cases.append({'case':'verify_baseline_tool_different_raw_records','expected':'REJECTED','actual':tool_result['status'],'result':tool_result})
    source_after={p:digest(ROOT/p) for p in SOURCES}
    failures=[r for r in cases if r['actual']!=r['expected']]
    result={'classification':'ENGINEERING_TEST','scope':'C2-F02_TRUST_BOUNDARY_NOT_REAL_PILOT_ACCEPTANCE',
            'construction':'Manual collinear numeric and bookkeeping answers, trusted handles acquired first; no producer runner called',
            'source_hashes_before':source_before,'source_hashes_after':source_after,'source_stable':source_before==source_after,
            'cases':cases,'production_runner_calls':len(forbidden_calls),'trusted_handle_unchanged':trusted_before==trusted,
            'programmatic_model_calls':0,'status':'REJECTED' if failures else 'VERIFIED'}
    write_json(out,result,exclusive=True)
    print(json.dumps({'cases':len(cases),'matched':len(cases)-len(failures),'failures':failures,'source_stable':result['source_stable'],
                      'production_runner_calls':len(forbidden_calls)},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
