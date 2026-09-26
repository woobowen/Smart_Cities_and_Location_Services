"""Independent current-run diagnostics, bindings and sensitivity artifact review."""
from collections import Counter
import json
import math
import subprocess
import sys

from independent_probe import ROOT, OUT, REV, RAW, RAW_HASH, IDS, EPS, read, sha, obj, same

COMPONENTS={
    'profile_pilot':['record_scope','profile_fields','profile_counts','summary'],
    'time_boundaries':['record_scope','raw_time','threshold','strict_inequality','boundaries','index_order','point_coverage'],
    'duplicate_details':['record_scope','complete_events','event_types','event_indices'],
    'baseline':['provenance','contract','segmentation','filtering','direction','actual_values','dp_intervals','point_accounting','summaries']}
FOLLOWUP=['trusted_raw_scope','approved_analysis_contract','independent_coordinates','local_distance_error',
          'distance_split_threshold','short_segment_threshold','direction_threshold','dp_interval_sensitivity','source_semantics_limitations']


def main(run_id):
    directory=REV/'runs'/run_id;manifest=read(directory/'manifest.json')
    raw_all=read(RAW);raw={rid:raw_all[rid] for rid in IDS};policy=read(ROOT/'task1/config/goal1.json')
    contract=read(ROOT/'task1/config/conditional_planar.json');baseline=read(directory/'baseline.json')
    probe=read(OUT/(run_id+'_independent.json'));checks=[];errors=[]
    def check(name, passed, detail=None):
        row={'name':name,'passed':bool(passed),'detail':detail};checks.append(row)
        if not passed:errors.append(row)
    def close(a,b,scale=1):
        return isinstance(a,(int,float)) and not isinstance(a,bool) and math.isfinite(a) and abs(a-b)<=64*EPS*max(scale,abs(a),abs(b))
    check('C_raw_baseline_probe',probe['status']=='VERIFIED' and probe['target']['sha256']==sha(directory/'baseline.json'))
    totals=Counter();delta_counts=Counter();point_counts=[]
    for action in COMPONENTS:
        candidate=read(directory/(action+'.json'));binding=manifest['artifacts'][action];review_binding=manifest['reviews'][action]
        review=read(ROOT/review_binding['path'])['result']
        check(action+':artifact_file_object_binding',sha(ROOT/binding['path'])==binding['sha256'] and obj(candidate)==binding['output_sha256'])
        check(action+':actual_review_coverage',sha(ROOT/review_binding['path'])==review_binding['sha256'] and review['status']=='VERIFIED'
              and review['unchecked_components']==[] and set(COMPONENTS[action]).issubset(review['checked_components'])
              and review['target_artifact_id']==binding['artifact_id'] and review['target_artifact_hash']==binding['sha256']
              and review['target_output_hash']==binding['output_sha256'])
        check(action+':trusted_external_reference',review['trusted_reference']['raw_sha256']==RAW_HASH
              and review['trusted_reference']['policy_sha256']==obj(policy) and review['record_scope']==IDS)
        check(action+':raw_envelope',candidate['input_sha256']==RAW_HASH and candidate['record_ids']==IDS and
              candidate['input_points']==783 and candidate['input_records']==7 and candidate['modified_values']==0)
        for name,h in {**binding['source_hashes'],**review_binding['source_hashes']}.items():
            committed=subprocess.check_output(['git','show',manifest['code_sha']+':'+name],cwd=ROOT)
            import hashlib
            check(action+':source:'+name,sha(ROOT/name)==h and hashlib.sha256(committed).hexdigest()==h)
    profiles=read(directory/'profile_pilot.json')['result'];times_art=read(directory/'time_boundaries.json')['result']['trajectories'];duplicates=read(directory/'duplicate_details.json')['result']['trajectories']
    for rid,(times,xy) in raw.items():
        d=[b-a for a,b in zip(times,times[1:])];n=len(xy);point_counts.append(n);pairs=list(zip(xy,xy[1:]));count=Counter(str(v) for v in d)
        expected={'n_points':n,'n_timestamps':n,'invalid_timestamps':0,'invalid_coordinates':0,
                  'negative_dt':sum(v<0 for v in d),'zero_dt':d.count(0),'positive_dt':sum(v>0 for v in d),
                  'same_time_different_position':sum(dt==0 and a!=b for dt,(a,b) in zip(d,pairs)),
                  'consecutive_duplicate_position':sum(a==b for a,b in pairs),'long_gap_gt_30_source_seconds':sum(v>30 for v in d),
                  'edges_total':n-1,'dt_computable':n-1,'position_pairs_computable':n-1}
        profile=next(v for v in profiles['profiles'] if v['record_id']==rid)
        check(rid+':raw_profile_fields',all(same(profile[k],v) for k,v in expected.items()) and profile['valid_structure'] is True and
              profile['issues']==[] and same(profile['dt_counts'],dict(count)) and profile['time_span_raw']==times[-1]-times[0]
              and profile['dt_min_raw']==min(d) and profile['dt_max_raw']==max(d))
        totals.update(expected);delta_counts.update(count)
        cuts=[{'left_index':i,'right_index':i+1,'dt':dt,'reasons':['NEGATIVE_DT' if dt<0 else 'GAP_GT_THRESHOLD']}
              for i,dt in enumerate(d) if dt<0 or dt>30]
        limits=[0]+[c['right_index'] for c in cuts]+[n];partitions=[list(range(a,b)) for a,b in zip(limits,limits[1:])]
        time=next(v for v in times_art if v['record_id']==rid)
        check(rid+':time_partitions',same(time['cuts'],cuts) and same(time['partitions'],partitions) and time['n_input']==time['n_accounted']==n
              and time['deleted']==time['modified']==0 and time['threshold_source_seconds']==30 and 'BLOCKED' not in time['limitation'])
        events=[]
        for i,(dt,(a,b)) in enumerate(zip(d,pairs)):
            reasons=[]
            if a==b:reasons.append('REPEATED_POSITION_NOT_AUTOMATIC_NOISE')
            if dt==0:
                reasons.append('ZERO_DT_SPEED_UNAVAILABLE')
                if a!=b:reasons.append('SAME_TIME_DIFFERENT_POSITION')
            if reasons:events.append({'left_index':i,'right_index':i+1,'dt_raw':dt,'dt_reason':None,'position_pair_computable':True,'reasons':reasons})
        dupe=next(v for v in duplicates if v['record_id']==rid)
        check(rid+':complete_duplicate_events',same(dupe['events'],events) and dupe['deleted']==dupe['modified']==0)
    expected=dict(totals);expected.update(n_records=7,valid_structure_records=7,dt_counts=dict(delta_counts),
        point_count_min=min(point_counts),point_count_max=max(point_counts),modifications=0,
        physical_distance={'value':None,'reason':'CRS_AND_DISTANCE_POLICY_UNRESOLVED'})
    check('profile_global_summary',same(profiles['summary'],expected))
    check('strict_time_equality_actual_record1',raw['1'][0][1]-raw['1'][0][0]==30 and next(x for x in times_art if x['record_id']=='1')['cuts']==[])
    diagnostic_report={'status':'REJECTED' if errors else 'VERIFIED','classification':'INDEPENDENT_C_REAL_DIAGNOSTIC_AND_VERSION_CHECK',
        'run_id':run_id,'checks':checks,'errors':errors,'check_count':len(checks),'raw_sha256':sha(RAW),
        'source_code_sha':manifest['code_sha'],'target_manifest_sha256':sha(directory/'manifest.json'),
        'probe_sha256':sha(__file__),'totals':dict(totals),'new_model_calls':0}
    (OUT/(run_id+'_diagnostics.json')).write_text(json.dumps(diagnostic_report,ensure_ascii=False,indent=2)+'\n')
    print('diagnostics',diagnostic_report['status'],len(checks),errors)
    target=directory/'coordinate_sensitivity.json'
    if not target.exists():
        print('followup NOT_YET_GENERATED');return
    a=read(target);checks=[];errors=[]
    check('trusted_raw_scope',a['raw_scope_sha256']==obj(raw) and a['points_checked']==783)
    check('approved_contract',a['contract_id']==contract['contract_id'] and a['contract_sha256']==obj(contract))
    check('independent_coordinates',close(a['max_coordinate_crosscheck_error_m'],probe['max_coordinate_crosscheck_error_m'])
          and a['max_coordinate_crosscheck_error_m']<=1e-6)
    check('local_model_all_pairs',a['within_record_pairs_checked']==probe['within_record_pairs_checked'] and
          close(a['max_pair_distance_absolute_difference_m'],probe['max_pair_distance_absolute_difference_m']) and
          close(a['max_pair_distance_relative_difference'],probe['max_pair_distance_relative_difference']))
    lookup={(v['record_id'],v['left_index'],v['right_index']):v for v in probe['edge_checks']}
    check('edge_scope',len(a['edge_checks'])==len(lookup)==776)
    for row in a['edge_checks']:
        x=lookup[(row['record_id'],row['left_index'],row['right_index'])]
        check('edge:'+str((row['record_id'],row['right_index'])),close(row['enu_m'],x['enu_m']) and
              close(row['ellipsoid_m'],x['ellipsoid_m']) and row['threshold_disagreement']==x['threshold_disagreement']
              and close(row['margin_to_400m'],abs(x['enu_m']-400)))
    check('edge_disagreement_summary',a['edge_400m_disagreements']==sum(x['threshold_disagreement'] for x in lookup.values()))
    lookup={(v['record_id'],v['segment_index']):v for v in probe['segment_checks']}
    check('segment_scope',len(a['segment_65m_checks'])==len(lookup)==30)
    for row in a['segment_65m_checks']:
        x=lookup[(row['record_id'],row['segment_index'])]
        check('segment:'+str((row['record_id'],row['segment_index'])),row['points']==x['points'] and close(row['enu_length_m'],x['enu_length_m'])
              and close(row['ellipsoid_length_m'],x['ellipsoid_length_m']) and row['threshold_disagreement']==x['threshold_disagreement']
              and close(row['margin_to_65m'],abs(x['enu_length_m']-65)))
    check('segment_disagreement_summary',a['segment_65m_disagreements']==sum(x['threshold_disagreement'] for x in lookup.values()))
    lookup={(v['record_id'],v['segment_index'],v['original_index']):v for v in probe['direction_checks']}
    check('direction_scope',len(a['direction_35deg_checks'])==len(lookup)==474)
    for row in a['direction_35deg_checks']:
        x=lookup[(row['record_id'],row['segment_index'],row['original_index'])]
        en=x['enu_differences_degrees'];alt=x['aeqd_differences_degrees'];good=True
        for submitted,expected in [(row['enu_differences_degrees'],en),(row['aeqd_grid_differences_degrees'],alt)]:
            good &= submitted is None if expected is None else len(submitted)==2 and all(close(v,w,360) for v,w in zip(submitted,expected))
        candidate=None if en is None else min(en)>35
        acandidate=None if alt is None else min(alt)>35
        check('direction:'+str((row['record_id'],row['original_index'])),good and row['enu_undefined_reason']==x['reason']
              and row['aeqd_undefined_reason']==x['reason'] and row['enu_candidate']==candidate and row['aeqd_candidate']==acandidate
              and row['actual_deleted']==(candidate is True) and row['predicate_disagreement']==(candidate!=acandidate)
              and (row['margin_to_35deg'] is None if en is None else close(row['margin_to_35deg'],min(abs(v-35) for v in en),360)))
    check('direction_summaries',a['direction_35deg_disagreements']==sum(x['predicate_disagreement'] for x in lookup.values()) and
          a['direction_undefined_points']==sum(x['reason'] is not None for x in lookup.values()) and a['direction_undefined_disagreements']==0)
    lookup={(v['record_id'],v['segment_index']):v for v in probe['dp_checks']}
    check('DP_interval_scope',len(a['dp_5m_checks'])==len(lookup)==23)
    for row in a['dp_5m_checks']:
        x=lookup[(row['record_id'],row['segment_index'])]
        check('DP:'+str((row['record_id'],row['segment_index'])),abs(row['max_error_m']-x['aeqd_max_error_m'])<=x['allowance'] and
              abs(row['enu_max_error_m']-x['max_error_m'])<=x['allowance'] and row['status']==row['enu_status']=='VERIFIED' and
              abs(row['max_error_change_m']-(x['aeqd_max_error_m']-x['max_error_m']))<=2*x['allowance'] and row['exceeding_points']==[])
    check('DP_disagreement_summary',a['dp_5m_disagreements']==0)
    check('limitations_not_datum_proof',a['source_crs']=='UNVERIFIED' and a['source_datum_proven'] is False and
          set(a['unavailable_claims'])=={'absolute_geographic_accuracy','true_ground_error','datum_or_offset_identification'})
    check('actual_baseline_parent',a['parent_sha256']==sha(directory/'baseline.json') and a['parent_artifact_id']==manifest['artifacts']['baseline']['artifact_id'])
    check('actual_trigger_review',same(a['trigger_review'],manifest['reviews']['baseline']))
    check('request_hash',sha(ROOT/a['request']['path'])==a['request']['sha256'])
    request=read(ROOT/a['request']['path'])
    check('request_actual_case',request['parent_sha256']==sha(directory/'baseline.json') and '4.938319812632412' in request['reason'])
    check('fixed_code_binding',a['code_sha']==manifest['code_sha'])
    check('followup_success',a['status']=='VERIFIED' and a['errors']==[] and a['processing_threshold_checks']=='EXECUTED')
    passed=not errors
    report={'status':'VERIFIED' if passed else 'REJECTED','classification':'INDEPENDENT_C_REAL_FOLLOWUP_ARTIFACT_REVIEW',
            'run_id':run_id,'target_path':str(target.relative_to(ROOT)),'target_sha256':sha(target),
            'checked_components':FOLLOWUP if passed else [],'unchecked_components':[] if passed else FOLLOWUP,
            'checks':checks,'errors':errors,'check_count':len(checks),'source_code_sha':manifest['code_sha'],
            'source_crs':'UNVERIFIED','source_datum_proven':False,
            'evidence':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [RAW,ROOT/'task1/config/conditional_planar.json',
                ROOT/'task1/config/goal1.json',REV/'AUTHORIZATION_SUPPLEMENT.md',REV/'USER_DECISIONS.json',
                OUT/(run_id+'_independent.json'),OUT/'independent_probe.py',OUT/'remaining_probe.py',directory/'baseline.json']],
            'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'task1/workflow/coordinate_review.py',ROOT/'task1/workflow/coordinates.py',ROOT/'task1/workflow/evaluation.py']},
            'limitations':['Conditional model geometry only, unknown source datum and offset remain unknown',
                'AEQD shares the mathematical ellipsoid assumption and cannot establish ground truth',
                'Same retained-index intervals, no alternate cleaning or parameter choice',
                'All 461 clean points independently checked using Decimal finite segments; filtered and direction-deleted points excluded only from DP denominator']}
    (OUT/'followup_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('followup',report['status'],len(checks),errors)


if __name__=='__main__':main(sys.argv[1])
