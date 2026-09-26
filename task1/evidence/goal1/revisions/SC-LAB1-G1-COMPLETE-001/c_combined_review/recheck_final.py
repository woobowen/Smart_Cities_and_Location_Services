"""Final bounded C feedback-gate review. Original failures remain immutable."""
from pathlib import Path
import sys
from unittest.mock import patch
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT))
from task1.workflow import goal,tools
from task1.workflow.io import CONFIG,read_json,write_json,digest


def main():
    final_folder=HERE/'round2';final_folder.mkdir(exist_ok=True)
    folder=final_folder/'retry1';folder.mkdir(exist_ok=False)
    driver=HERE/'verify_closure.py';source=driver.read_text()
    # Output-only adapter: re-run the exact saved cases in fresh directories.
    source=source.replace('round3','round5').replace("out=HERE/'combined_closure.json'","out=HERE/'combined_closure_base.json'")
    ns={'__file__':str(driver),'__name__':'c_combined_output_adapter'}
    exec(compile(source,str(driver),'exec'),ns)
    ns['HERE']=folder
    ns['main']()
    report=read_json(folder/'combined_closure_base.json')
    before=report['issues']['C2-F01']['source_hashes']
    checks=[]
    def note(name,passed,actual):checks.append({'case':name,'pass':bool(passed),'actual':actual})
    raw_path=folder/'fixture_raw.json';policy=read_json(CONFIG);policy['raw_sha256']=digest(raw_path)
    with patch.object(tools,'DATA',raw_path),patch.object(goal,'DATA',raw_path):
        j=goal.GoalJournal(folder/'feedback_gate');run=j.state['runs']['test']
        # The preceding negative tests correctly returned before saving an
        # in-memory stub. Explicitly register the existing constructed fixture.
        fpath=j.directory/'coordinate_sensitivity_fixture.json'
        run['followup']={**j.attach(fpath),'source_hashes':{
            'task1/workflow/coordinate_review.py':digest(ROOT/'task1/workflow/coordinate_review.py')}}
        j.save()
        def task_report(task,ev,run_id=None,extra=None):
            item={'status':'VERIFIED','evidence':ev}
            if run_id is not None:item['run_id']=run_id
            if extra:item.update(extra)
            path=j.directory/(task+'_complete_scope_fixture.json')
            write_json(path,{'classification':'ENGINEERING_TEST_NOT_PROJECT_ACCEPTANCE','tasks':{task:item}},exclusive=True)
            return path
        # Establish all actual diagnostic dependencies, leaving only unrelated
        # document tasks pending. The baseline remains the hand-built C fixture.
        for task in ['governance','review_targets','trusted_baseline']:
            j.complete_task(task,task_report(task,[j.attach(raw_path)]),'C:fixture')
        for action in ['profile_pilot','time_boundaries','duplicate_details']:
            j.execute('test',action,policy);j.review('test',action,policy)
        ev=[j.attach(ROOT/run[group][a]['path']) for group in ['artifacts','reviews']
            for a in ['profile_pilot','time_boundaries','duplicate_details']]
        j.complete_task('diagnostics',task_report('diagnostics',ev,'test'),'C:fixture')
        baseline_ev=[j.attach(ROOT/run[group]['baseline']['path']) for group in ['artifacts','reviews']]
        j.complete_task('real_baseline',task_report('real_baseline',baseline_ev,'test'),'C:fixture')
        followup=run['followup'];audit_path=j.directory/'complete_nine_components_audit.json'
        audit={'classification':'ENGINEERING_TEST_SCOPE_GATE','status':'VERIFIED','target_sha256':followup['sha256'],
               'checked_components':list(goal.FOLLOWUP_COMPONENTS),'unchecked_components':[]}
        write_json(audit_path,audit,exclusive=True)
        j.complete_task('processing_feedback',task_report('processing_feedback',baseline_ev,'test',{'followup_review':j.attach(audit_path)}),'C:fixture')
        note('complete_nine_components_task_accepted',j.state['tasks']['processing_feedback']['status']=='VERIFIED',j.state['tasks']['processing_feedback']['status'])
        j.finalize()
        note('complete_nine_components_survives_finalize',j.state['tasks']['processing_feedback']['status']=='VERIFIED',j.state['tasks']['processing_feedback']['status'])
        # Recreate a pre-fix checkpoint with a genuine file hash but the wrong
        # review scope. No prior evidence file is modified.
        wrong=j.directory/'unrelated_profile_coverage_audit.json'
        j.state['tasks']['processing_feedback']['followup_review']=j.attach(wrong)
        j.save()
        resumed=goal.GoalJournal(j.directory);state=resumed.finalize()
        note('legacy_wrong_scope_reset_on_finalize',resumed.state['tasks']['processing_feedback']['status']=='PENDING',
             {'goal_status':state,'task_status':resumed.state['tasks']['processing_feedback']['status']})
        missing=dict(audit);missing.pop('unchecked_components')
        note('unchecked_must_be_explicit_empty',not goal.followup_review_complete(missing,followup),goal.followup_review_complete(missing,followup))
        partial=dict(audit);partial['checked_components']=list(goal.FOLLOWUP_COMPONENTS[:-1])
        note('eight_of_nine_components_denied',not goal.followup_review_complete(partial,followup),goal.followup_review_complete(partial,followup))
        # Inspect actual execution dependency registration with a clearly labelled
        # hand-built computation stub; this is not real baseline processing.
        dep=goal.GoalJournal(folder/'baseline_source_dependencies');dep.bind_code('DEPENDENCY_FIXTURE_1');dep.start_run('dep',policy,list(read_json(raw_path)))
        candidate=read_json(ROOT/run['artifacts']['baseline']['path'])
        with patch.object(goal,'execute_tool',return_value=candidate):
            dep.execute('dep','baseline',policy)
        deps=dep.state['runs']['dep']['artifacts']['baseline']['source_hashes']
        note('baseline_tracks_coordinates_adapter','task1/workflow/coordinates.py' in deps,deps)
        note('baseline_tracks_frozen_coordinate_contract','task1/config/conditional_planar.json' in deps,deps)
        dep.bind_code('DEPENDENCY_FIXTURE_2',['task1/workflow/coordinates.py'])
        note('adapter_change_invalidates_baseline',dep.state['runs']['dep']['artifacts']['baseline']['valid'] is False,dep.state['runs']['dep']['artifacts']['baseline']['valid'])
    after={p:digest(ROOT/p) for p in before}
    note('final_source_hashes_stable',before==after,after)
    failed=[r for r in checks if not r['pass']]
    report['final_feedback_checks']=checks
    report['adaptation']+=' Final adapter changes only output directories; added complete nine-component positive control and persisted legacy wrong-scope checkpoint.'
    for item in report['issues'].values():item['source_hashes']=after
    report['issues']['C2-F01']['checked'] += [r['case'] for r in checks]
    report['issues']['C2-F01']['failed'] += failed
    if failed:report['issues']['C2-F01']['status']='REJECTED'
    report['evidence_directory']=str(folder.relative_to(ROOT))
    report['harness_recovery']='Prior C harness KeyError on unpersisted followup fixture preserved in harness_failure.json; fresh run explicitly registers that ENGINEERING_TEST fixture before reload-dependent checks.'
    write_json(final_folder/'combined_closure.json',report,exclusive=True)
    print(json.dumps({'F01':report['issues']['C2-F01']['status'],'F02':report['issues']['C2-F02']['status'],
                      'final_checks':len(checks),'passed':sum(r['pass'] for r in checks),'failures':failed},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
