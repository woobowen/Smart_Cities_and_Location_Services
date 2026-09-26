"""C version-aligned interface review; all state fixtures are ENGINEERING_TEST."""
from copy import deepcopy
from pathlib import Path
import sys
from unittest.mock import patch
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
REV=HERE.parent
sys.path.insert(0,str(ROOT))
from task1.workflow import tools,goal
from task1.workflow.artifact_review import COMPONENTS
from task1.workflow.io import CONFIG,digest,read_json,write_json,object_hash


def capture(fn):
    try:return {'returned':fn()}
    except Exception as exc:return {'exception_type':type(exc).__name__,'message':str(exc)}


def rerun(path):
    source=path.read_text()
    assert source.count("folder=HERE/'round2'")==1
    namespace={'__file__':str(path),'__name__':'c_saved_recheck'}
    exec(compile(source.replace("folder=HERE/'round2'","folder=HERE/'round3'"),str(path),'exec'),namespace)
    namespace['main']()


def main():
    out=HERE/'combined_closure.json'
    if out.exists():raise SystemExit('Refusing to overwrite C combined review')
    source_paths=sorted(set([
        'task1/workflow/'+n for n in ['goal.py','controller.py','tools.py','artifact_review.py','diagnostics.py','evaluation.py','pipeline.py','coordinates.py','coordinate_review.py','geometry.py','io.py']]+[
        'task1/config/goal1.json','task1/config/conditional_planar.json',
        'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json',
        'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md']))
    before={p:digest(ROOT/p) for p in source_paths}
    rerun(REV/'c_f01_review/recheck_f01.py')
    rerun(REV/'c_f02_review/recheck_f02.py')
    r1=read_json(REV/'c_f01_review/round3/review_receipt.json')['issues']['C2-F01']
    r2=read_json(REV/'c_f02_review/round3/review_receipt.json')['issues']['C2-F02']
    raw={'fixture:review':[[0,1,2,3],[[0,0],[1,0],[2,0],[3,0]]]}
    raw_path=HERE/'fixture_raw.json';write_json(raw_path,raw,exclusive=True)
    policy=read_json(CONFIG);policy['raw_sha256']=digest(raw_path)
    results=[]
    def note(case,passed,actual):results.append({'case':case,'pass':bool(passed),'actual':actual})
    with patch.object(tools,'DATA',raw_path),patch.object(goal,'DATA',raw_path):
        profiles=tools.execute_tool('profile_pilot',list(raw),policy,classification='ENGINEERING_TEST')['result']['profiles']
        for action in ['verify_profiles','recompute_check','verify_baseline']:
            result=capture(lambda:tools.execute_tool(action,list(raw),policy,profiles,requested_components=['time_boundaries']))
            note('legacy_'+action+'_cannot_request_unbound_coverage',result.get('message')=='REGISTERED_TARGET_REQUIRED_FOR_COVERAGE_REQUEST',result)
        for action in ['verify_profiles','recompute_check']:
            result=tools.execute_tool(action,list(raw),policy,profiles,classification='ENGINEERING_TEST')
            note('legacy_'+action+'_states_unchecked',result['result']['unchecked_components']==['summary','artifact_binding'],result)
        for parent,action in [('review_targets','profile_pilot'),('review_targets','baseline'),('trusted_baseline','baseline')]:
            j=goal.GoalJournal(HERE/('open_'+parent+'_'+action));j.bind_code('CONSTRUCTED_CODE');j.start_run('test',policy,list(raw))
            j.open_issue('fixture:open',parent,'ENGINEERING_TEST','fixture fault','fixture required repair',[],'B:fixture')
            calls=[]
            def forbidden(*args,**kwargs):calls.append(True);raise AssertionError('DISPATCHED_BEFORE_REPAIR')
            with patch.object(goal,'execute_tool',forbidden):
                result=capture(lambda:j.execute('test',action,policy))
            note('open_'+parent+'_blocks_'+action,result.get('message')=='OPEN_BLOCKING_ISSUE_REPAIR_BEFORE_PROCESSING' and not calls,{'response':result,'execute_calls':len(calls)})

        # Isolate the feedback gate after an explicitly constructed already-reviewed
        # parent. Manual numerical baseline and its actual C review come from F02.
        j=goal.GoalJournal(HERE/'feedback_gate');j.bind_code('CONSTRUCTED_CODE');j.start_run('test',policy,list(raw))
        bpath=j.directory/'baseline_fixture.json'
        candidate=read_json(REV/'c_f02_review/round3/manual_valid_control.json');write_json(bpath,candidate,exclusive=True)
        target={**j.attach(bpath),'artifact_id':'test:baseline','output_sha256':object_hash(candidate),
                'action':'baseline','valid':True,'source_hashes':{'task1/workflow/evaluation.py':digest(ROOT/'task1/workflow/evaluation.py')}}
        numerical=read_json(REV/'c_f02_review/round3/initial_results.json')['cases'][0]['result']
        numerical.update(target_artifact_id=target['artifact_id'],target_artifact_hash=target['sha256'])
        brpath=j.directory/'baseline_review_fixture.json';write_json(brpath,{'classification':'ENGINEERING_TEST_IMPORTED_C_RESULT','result':numerical},exclusive=True)
        review={**j.attach(brpath),'source_hashes':{'task1/workflow/evaluation.py':digest(ROOT/'task1/workflow/evaluation.py')}}
        run=j.state['runs']['test'];run['artifacts']['baseline']=target;run['reviews']['baseline']=review
        j.state['tasks']['real_baseline'].update(status='VERIFIED',run_id='test',evidence=[j.attach(bpath),j.attach(brpath)])
        j.save()
        def task_report(name,followup_review=None):
            item={'status':'VERIFIED','run_id':'test','evidence':[j.attach(bpath),j.attach(brpath)]}
            if followup_review is not None:item['followup_review']=followup_review
            path=j.directory/(name+'.json');write_json(path,{'classification':'ENGINEERING_TEST_GATE_FIXTURE','tasks':{'processing_feedback':item}},exclusive=True)
            return path
        missing=capture(lambda:j.complete_task('processing_feedback',task_report('missing_followup'),'C:fixture'))
        note('feedback_requires_actual_followup',missing.get('message')=='REAL_FOLLOWUP_REVIEW_REQUIRED',missing)
        fpath=j.directory/'coordinate_sensitivity_fixture.json'
        write_json(fpath,{'classification':'ENGINEERING_TEST_STUB_NOT_REAL_SENSITIVITY','status':'VERIFIED','action':'coordinate_sensitivity'},exclusive=True)
        run['followup']={**j.attach(fpath),'source_hashes':{'task1/workflow/coordinate_review.py':digest(ROOT/'task1/workflow/coordinate_review.py')}}
        no_audit=capture(lambda:j.complete_task('processing_feedback',task_report('missing_followup_review'),'C:fixture'))
        note('feedback_requires_C_review',no_audit.get('message')=='REAL_FOLLOWUP_REVIEW_REQUIRED',no_audit)
        for name,sha,components in [('wrong_hash','0'*64,['coordinate_transform']),('empty_coverage',digest(fpath),[]),
                                     ('unrelated_profile_coverage',digest(fpath),['profile_counts'])]:
            apath=j.directory/(name+'_audit.json');write_json(apath,{'classification':'ENGINEERING_TEST','status':'VERIFIED','target_sha256':sha,
                'checked_components':components,'unchecked_components':[]},exclusive=True)
            result=capture(lambda:j.complete_task('processing_feedback',task_report(name,j.attach(apath)),'C:fixture'))
            note('feedback_rejects_'+name,'exception_type' in result,result)
    after={p:digest(ROOT/p) for p in source_paths}
    note('core_source_hashes_stable',before==after,{'before':before,'after':after})
    failed=[r for r in results if not r['pass']]
    report={'classification':'ENGINEERING_TEST','scope':'VERSION_ALIGNED_F01_F02_AND_REQUESTED_INTERFACE_GATES_NOT_GOAL_ACCEPTANCE',
            'adaptation':'Only rerun output directories change round2 to round3 in the archived adapters; original probes/expectations unchanged.',
            'extra_checks':results,'issues':{
                'C2-F01':{**r1,'status':'REJECTED' if failed else r1['status'],'source_hashes':after,
                          'checked':r1['checked']+[r['case'] for r in results], 'failed':failed},
                'C2-F02':{**r2,'status':r2['status'] if before==after else 'REJECTED','source_hashes':after}}}
    write_json(out,report,exclusive=True)
    print(json.dumps({'extra_checks':len(results),'failed':failed,'F01':report['issues']['C2-F01']['status'],'F02':report['issues']['C2-F02']['status']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
