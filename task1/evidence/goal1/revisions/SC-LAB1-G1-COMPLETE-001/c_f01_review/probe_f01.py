"""Independent C constructed challenges, no model calls or production writes."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from task1.workflow import tools, goal, controller
from task1.workflow.artifact_review import COMPONENTS, review_artifact
from task1.workflow.io import CONFIG, digest, object_hash, read_json, write_json

HERE = Path(__file__).resolve().parent
CODE = ['task1/workflow/'+n for n in ['artifact_review.py','tools.py','controller.py','goal.py','diagnostics.py','io.py']]


def hashes():
    return {name:digest(ROOT/name) for name in CODE}


def call_capture(fn):
    try:
        return {'returned':fn()}
    except Exception as exc:
        return {'exception_type':type(exc).__name__, 'message':str(exc)}


def main():
    out = HERE/'initial_results.json'
    if out.exists():
        raise SystemExit('Refusing to replace initial C review evidence')
    sources = hashes()
    raw = {
        'fixture:edges':[[11,41,72,71,71,101], [[0,0],[1,0],[1,0],[2,0],[3,0],[3,0]]],
        'fixture:missing':[[None,3,3], [[0,0],[0,0],[1,0]]],
        'fixture:empty':[[],[]],
    }
    raw_path = HERE/'constructed_raw.json'
    write_json(raw_path, raw, exclusive=True)
    policy = read_json(CONFIG); policy['raw_sha256'] = digest(raw_path)
    policy_path = HERE/'constructed_policy.json'; write_json(policy_path, policy, exclusive=True)
    pilot_path = HERE/'constructed_pilot.json'; write_json(pilot_path, {'ids':list(raw)}, exclusive=True)
    rows = []
    def audit(action, candidate, components=None, old_hash=None):
        binding = {'artifact_id':'C:constructed-target', 'sha256':'CONSTRUCTED_REGISTERED_FILE_HASH',
                   'output_sha256':object_hash(candidate) if old_hash is None else old_hash,
                   'action':action}
        return review_artifact(action, raw, candidate, policy, binding, components)
    def record(name, expected, result):
        rows.append({'case':name,'expected':expected,'actual':result['status'],'result':result})
    with patch.object(tools, 'DATA', raw_path), patch.object(goal,'DATA',raw_path), patch.object(controller,'DATA',raw_path):
        produced = {a:tools.execute_tool(a,list(raw),policy,classification='ENGINEERING_TEST')
                    for a in ('profile_pilot','time_boundaries','duplicate_details')}
        assert produced['time_boundaries']['result']['trajectories'][0]['partitions'] == [[0,1],[2],[3,4,5]]
        # Hand-derived facts for this fixture, independent of producer implementation.
        assert [x['right_index'] for x in produced['time_boundaries']['result']['trajectories'][0]['cuts']] == [2,3]
        assert [x['right_index'] for x in produced['duplicate_details']['result']['trajectories'][0]['events']] == [2,4,5]
        for action, candidate in produced.items():
            record(action+':correct', 'VERIFIED', audit(action,candidate))
            record(action+':unsupported_component', 'REJECTED', audit(action,candidate,['physical_ground_truth']))
        time_cases = {}
        x=deepcopy(produced['time_boundaries']);x['result']['trajectories'][0]['cuts'].pop(0);time_cases['missing_gap']=x
        x=deepcopy(produced['time_boundaries']);x['result']['trajectories'][0]['cuts'].insert(0,{'right_index':1,'left_index':0,'dt':30,'reasons':['GAP_GT_THRESHOLD']});time_cases['equal_cut']=x
        x=deepcopy(produced['time_boundaries']);x['result']['trajectories'][0]['partitions'][-1]=[3,5,4];time_cases['wrong_order']=x
        x=deepcopy(produced['time_boundaries']);x['result']['trajectories'][0]['partitions'][0][1]=True;time_cases['boolean_original_index']=x
        x=deepcopy(produced['time_boundaries']);x['result']['trajectories'][0]['cuts'][1]['dt']=True;time_cases['wrong_delta']=x
        for name,candidate in time_cases.items():record('time:'+name,'REJECTED',audit('time_boundaries',candidate))
        duplicate_cases={}
        x=deepcopy(produced['duplicate_details']);x['result']['trajectories'][0]['events'].pop();duplicate_cases['missing_event']=x
        x=deepcopy(produced['duplicate_details']);x['result']['trajectories'][0]['events'][0]['reasons']=['SAME_TIME_DIFFERENT_POSITION'];duplicate_cases['wrong_reason']=x
        x=deepcopy(produced['duplicate_details']);x['result']['trajectories'][0]['events'][0]['left_index']=True;duplicate_cases['boolean_original_index']=x
        x=deepcopy(produced['duplicate_details']);x['result']['trajectories'][0]['events'][0]['position_pair_computable']=1;duplicate_cases['integer_boolean_flag']=x
        x=deepcopy(produced['duplicate_details']);x['result']['trajectories'][1]['events'][0]['dt_raw']=0;duplicate_cases['invented_missing_time_delta']=x
        for name,candidate in duplicate_cases.items():record('duplicate:'+name,'REJECTED',audit('duplicate_details',candidate))
        x=deepcopy(produced['profile_pilot']); x['result']['summary']['n_points']=999
        record('profiles:false_summary','REJECTED',audit('profile_pilot',x))
        record('profiles:changed_bytes','REJECTED',audit('profile_pilot',x,old_hash=object_hash(produced['profile_pilot'])))

        # Run actual controller dispatch and receipt binding, never the provider.
        c=controller.Controller('c-f01-binding', mode='MOCK_TEST', base=HERE/'controller_runs', policy_path=policy_path,pilot_path=pilot_path)
        def request(action, role, call, refs=None):
            return {'role':role,'call_id':call,'action':action,'record_ids':list(raw),'feedback_refs':[],
                    'evidence_refs':refs or ['CONSTRUCTED_FIXTURE'],'summary':'Independent constructed C probe',
                    'reason':'ENGINEERING_TEST target and coverage check','request_status':'PROPOSED','candidate_for_future_review':None}
        created={}
        for action in produced:
            created[action]=c.dispatch(request(action,'execution','C-create-'+action),'execution','C-create-'+action)
        c.dispatch(request('verify_profiles','review','C-review-profile'),'review','C-review-profile')
        partial_coverage=c.artifact_coverage()
        for action,tool_action in [('time_boundaries','verify_time_boundaries'),('duplicate_details','verify_duplicate_details')]:
            c.dispatch(request(tool_action,'review','C-review-'+action,[created[action]['tool_id']]),'review','C-review-'+action)
        full_coverage=c.artifact_coverage()
        controller_results={'profile_only':partial_coverage,'all_targets':full_coverage,
                            'unknown_target':call_capture(lambda:c.review_target('recompute_check',{'evidence_refs':['nonexistent']})),
                            'ambiguous_targets':call_capture(lambda:c.review_target('recompute_check',{'evidence_refs':[created['profile_pilot']['tool_id'],created['time_boundaries']['tool_id']]}))}

        # Complete the same task API with explicitly synthetic C-shaped reports.
        # This adversarial harness tests the final gate, not real scientific completion.
        j=goal.GoalJournal(HERE/'gate_challenge');j.bind_code('ENGINEERING_TEST_VERSION_1')
        j.start_run('coverage',policy,list(raw));j.execute('coverage','profile_pilot',policy);j.review('coverage','profile_pilot',policy)
        j.execute('coverage','time_boundaries',policy)
        evidence=[j.attach(raw_path)]
        task_reports=[]
        for task in goal.TASKS:
            report_path=j.directory/(task+'_constructed_C_report.json')
            write_json(report_path,{'classification':'ENGINEERING_TEST_NOT_ACTUAL_GOAL_REVIEW','tasks':{task:{'status':'VERIFIED','evidence':evidence}}},exclusive=True)
            j.complete_task(task,report_path,'C:constructed-gate-probe')
            task_reports.append(str(report_path.relative_to(ROOT)))
        incomplete={'coverage':j.coverage('coverage'),'finalize':j.finalize(),'constructed_task_reports':task_reports}
        j.review('coverage','time_boundaries',policy)
        before_change={'coverage':j.coverage('coverage'),'finalize':j.finalize()}
        j.bind_code('ENGINEERING_TEST_VERSION_2',['task1/workflow/diagnostics.py'])
        after_change={'coverage':j.coverage('coverage'),'run_status':j.state['runs']['coverage']['status'],'finalize':j.finalize(),
                      'task_statuses':{k:v['status'] for k,v in j.state['tasks'].items()}}

        # A failed actual dispatch leaves a durable uncertainty marker.
        interrupted=goal.GoalJournal(HERE/'uncertain_challenge');interrupted.bind_code('ENGINEERING_TEST_VERSION_1')
        interrupted.start_run('uncertain',policy,list(raw))
        with patch.object(goal,'execute_tool',side_effect=OSError('C_CONSTRUCTED_POST_DISPATCH_FAILURE')):
            first_failure=call_capture(lambda:interrupted.execute('uncertain','profile_pilot',policy))
        resumed=goal.GoalJournal(interrupted.directory)
        counter=[]
        def must_not_repeat(*args,**kwargs):counter.append(True);raise AssertionError('SHOULD_NOT_REPEAT')
        with patch.object(goal,'execute_tool',side_effect=must_not_repeat):
            retry=call_capture(lambda:resumed.execute('uncertain','profile_pilot',policy))
        recovery={'first_failure':first_failure,'retry':retry,'new_execute_calls':len(counter),
                  'reconcile':resumed.reconcile('uncertain','profile_pilot'),'finalize':resumed.finalize()}
    result={'classification':'ENGINEERING_TEST','scope':'C2-F01_AND_GOAL_CONTROL_NOT_F02_OR_GOAL_ACCEPTANCE',
            'programmatic_model_calls':0,'source_hashes_before':sources,'source_hashes_after':hashes(),
            'diagnostic_challenges':rows,'controller':controller_results,
            'goal_gate':{'unreviewed_target':incomplete,'fully_reviewed_before_change':before_change,'changed_source':after_change},
            'uncertain_operation':recovery}
    write_json(out,result,exclusive=True)
    print(json.dumps({'mismatches':[{'case':r['case'],'expected':r['expected'],'actual':r['actual']} for r in rows if r['actual']!=r['expected']],
                      'goal_gate':result['goal_gate'],'uncertain_operation':recovery,'source_stable':sources==hashes()},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
