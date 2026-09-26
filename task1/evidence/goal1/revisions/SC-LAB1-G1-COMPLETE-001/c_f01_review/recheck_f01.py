"""Second C review. Reuse initial challenges; catch newly correct gate refusals."""
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0,str(ROOT))
from task1.workflow import goal, tools
from task1.workflow.io import CONFIG, digest, read_json, write_json


def capture(fn):
    try:return {'returned':fn()}
    except Exception as exc:return {'exception_type':type(exc).__name__,'message':str(exc)}


def main():
    folder=HERE/'round2'
    folder.mkdir(exist_ok=False)
    spec=importlib.util.spec_from_file_location('c_initial_probe',HERE/'probe_f01.py')
    probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
    probe.HERE=folder
    source_before=probe.hashes()
    refusals=[]
    actual_complete=goal.GoalJournal.complete_task
    def capture_correct_refusal(self,task,report_path,verifier):
        try:return actual_complete(self,task,report_path,verifier)
        except ValueError as exc:
            refusals.append({'task':task,'error':str(exc)})
    # Only catch exceptions the initial intentionally dishonest task reports now
    # correctly raise. All production checks execute unchanged.
    with patch.object(goal.GoalJournal,'complete_task',capture_correct_refusal):
        probe.main()
    initial=read_json(folder/'initial_results.json')
    raw=folder/'constructed_raw.json';policy=read_json(folder/'constructed_policy.json')
    checks=[]
    def note(name,expected,actual):checks.append({'case':name,'expected':expected,'actual':actual,'pass':expected==actual})
    note('all_original_18_diagnostic_cases_match',18,sum(r['expected']==r['actual'] for r in initial['diagnostic_challenges']))
    note('missing_review_not_ready','IMPLEMENTING',initial['goal_gate']['unreviewed_target']['finalize'])
    note('stale_sources_not_ready','IMPLEMENTING',initial['goal_gate']['changed_source']['finalize'])
    note('failed_operation_not_reexecuted',0,initial['uncertain_operation']['new_execute_calls'])
    note('uncertain_final_state','INTERRUPTED_CHECKPOINT',initial['uncertain_operation']['finalize'])
    note('controller_all_targets_checked','VERIFIED',initial['controller']['all_targets']['status'])
    note('controller_partial_targets_not_closed','NEEDS_REVIEW',initial['controller']['profile_only']['status'])

    with patch.object(tools,'DATA',raw),patch.object(goal,'DATA',raw):
        j=goal.GoalJournal(folder/'normal_and_invalidation');j.bind_code('ENGINEERING_TEST_C2_1')
        # A real issue transition over constructed receipts, without claiming real
        # project implementation or scientific acceptance for these fixtures.
        j.open_issue('fixture:F01','review_targets','CONSTRUCTED_STATE_TRANSITION','fixture defect','fixture closure',[],'B:fixture')
        j.claim_repair('fixture:F01','B:fixture');j.submit_repair('fixture:F01','B:fixture',[HERE/'probe_f01.py'])
        issue_path=j.directory/'constructed_C_issue_review.json'
        write_json(issue_path,{'classification':'ENGINEERING_TEST','issues':{'fixture:F01':{
            'status':'VERIFIED','checked':['constructed repair transition'],'source_hashes':probe.hashes()}}},exclusive=True)
        j.review_repair('fixture:F01',issue_path,'C:fixture-independent')
        note('verified_repair_resumes_parent','PENDING',j.state['tasks']['review_targets']['status'])
        def report(task,ev,run_id=None,suffix=''):
            path=j.directory/(task+suffix+'_C_fixture.json')
            item={'status':'VERIFIED','evidence':ev}
            if run_id is not None:item['run_id']=run_id
            write_json(path,{'classification':'ENGINEERING_TEST_NOT_PROJECT_COMPLETION','tasks':{task:item}},exclusive=True)
            return path
        raw_ev=[j.attach(raw)]
        j.complete_task('review_targets',report('review_targets',raw_ev),'C:fixture-independent')
        j.start_run('three-targets',policy,list(read_json(raw)))
        for action in ['profile_pilot','time_boundaries','duplicate_details']:
            j.execute('three-targets',action,policy);j.review('three-targets',action,policy)
        run=j.state['runs']['three-targets']
        ev=[j.attach(ROOT/v['path']) for v in list(run['artifacts'].values())+list(run['reviews'].values())]
        wrong=capture(lambda:j.complete_task('diagnostics',report('diagnostics',ev,'other-run','_wrong_run'),'C:fixture-independent'))
        note('wrong_run_report_denied','CURRENT_RUN_REVIEW_REQUIRED',wrong.get('message'))
        missing=capture(lambda:j.complete_task('diagnostics',report('diagnostics',ev[:3],'three-targets','_missing_reviews'),'C:fixture-independent'))
        note('audit_receipts_required','ARTIFACT_EVIDENCE_NOT_BOUND',missing.get('message'))
        j.complete_task('diagnostics',report('diagnostics',ev,'three-targets'),'C:fixture-independent')
        note('valid_complete_diagnostics_allowed','VERIFIED',j.state['tasks']['diagnostics']['status'])
        for task in ['governance','trusted_baseline','notebooks','figures','internal_review']:
            j.complete_task(task,report(task,raw_ev),'C:fixture-independent')
        j.bind_code('ENGINEERING_TEST_C2_2',['task1/workflow/geometry.py'])
        note('unrelated_geometry_does_not_invalidate_diagnostics','VERIFIED',j.state['tasks']['diagnostics']['status'])
        j.bind_code('ENGINEERING_TEST_C2_3',['task1/workflow/diagnostics.py'])
        note('changed_diagnostics_invalidate_task','PENDING',j.state['tasks']['diagnostics']['status'])
        for task in ['notebooks','figures','internal_review']:
            note('changed_source_invalidates_dependent_'+task,'PENDING',j.state['tasks'][task]['status'])
        note('changed_source_does_not_reset_governance','VERIFIED',j.state['tasks']['governance']['status'])

        # Original source epoch counterexample, before any artifact exists.
        e=goal.GoalJournal(folder/'empty_epoch');e.bind_code('EPOCH_1');e.start_run('epoch',policy,list(read_json(raw)))
        e.bind_code('EPOCH_2',['task1/workflow/diagnostics.py'])
        denied=capture(lambda:e.execute('epoch','profile_pilot',policy))
        note('old_empty_run_cannot_execute_new_epoch','RUN_OR_CONTRACT_CHANGED',denied.get('message'))
        note('old_epoch_has_no_tool_artifacts',0,len(e.state['runs']['epoch']['artifacts']))

        # Fault injection changes the observed source hash after actual deterministic
        # computation. No production file changes are made.
        h=goal.GoalJournal(folder/'during_run_source_change');h.bind_code('HOT_1');h.start_run('hot',policy,list(read_json(raw)))
        real_digest=goal.digest;flag={'changed':False};actual_tool=goal.execute_tool
        def altered_hash(path):
            return 'ENGINEERING_TEST_CHANGED_SOURCE' if flag['changed'] and Path(path)==ROOT/'task1/workflow/diagnostics.py' else real_digest(path)
        def compute_then_change(*args,**kwargs):
            value=actual_tool(*args,**kwargs);flag['changed']=True;return value
        with patch.object(goal,'digest',altered_hash),patch.object(goal,'execute_tool',compute_then_change):
            hot=capture(lambda:h.execute('hot','profile_pilot',policy))
        note('source_change_during_execution_refused','RUNTIME_CODE_CHANGED',hot.get('message'))
        note('changed_source_output_not_registered',0,len(h.state['runs']['hot']['artifacts']))
        note('changed_source_dispatch_uncertainty_retained','INTERRUPTED_CHECKPOINT',h.finalize())
    source_after=probe.hashes()
    note('reviewed_source_bytes_stable',source_before,source_after)
    all_pass=all(x['pass'] for x in checks)
    result={'classification':'ENGINEERING_TEST','scope':'C2-F01_AND_GOAL_STATE_ONLY','original_probe':'../probe_f01.py',
            'adaptation':'Original diagnostic mutations and gate inputs unchanged; catch newly raised completion denials. Added valid complete run and source-change boundaries.',
            'task_gate_refusals':refusals,'checks':checks,'source_hashes_before':source_before,'source_hashes_after':source_after,
            'programmatic_model_calls':0,'network_calls':0,'original_probe_sha256':digest(HERE/'probe_f01.py'),'status':'VERIFIED' if all_pass else 'REJECTED'}
    write_json(folder/'recheck_results.json',result,exclusive=True)
    receipt={'classification':'ENGINEERING_TEST','scope':'C2-F01_AND_RELATED_GOAL_STATE_ONLY_NOT_F02_OR_GOAL_ACCEPTANCE',
             'issues':{'C2-F01':{'status':result['status'],'checked':[x['case'] for x in checks if x['pass']],
                                'failed':[x for x in checks if not x['pass']], 'source_hashes':source_after,
                                'evidence':'recheck_results.json','initial_rejection_preserved':'../initial_review.json'}}}
    write_json(folder/'review_receipt.json',receipt,exclusive=True)
    print(json.dumps({'status':result['status'],'checks':len(checks),'passed':sum(x['pass'] for x in checks),'failed':[x for x in checks if not x['pass']]},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
