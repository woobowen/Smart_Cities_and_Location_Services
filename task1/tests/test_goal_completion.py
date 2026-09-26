"""Known-answer target reviews and repair/resume regressions; ENGINEERING_TEST."""
import copy
import tempfile
from pathlib import Path
import pytest

from task1.workflow import tools, goal
from task1.workflow.artifact_review import review_artifact, COMPONENTS
from task1.workflow.io import ROOT, CONFIG, read_json, write_json, digest, object_hash


@pytest.fixture
def setup(tmp_path, monkeypatch):
    raw={'fixture:x':[[0,30,61,61,60,90],[[0,0],[0,0],[1,0],[2,0],[2,0],[3,0]]],
         'fixture:empty':[[],[]]}
    path=tmp_path/'raw.json';write_json(path,raw)
    policy=read_json(CONFIG);policy['raw_sha256']=digest(path)
    monkeypatch.setattr(tools,'DATA',path);monkeypatch.setattr(goal,'DATA',path)
    return raw,policy


def audit(raw,policy,action,candidate,components=None):
    return review_artifact(action,raw,candidate,policy,{'artifact_id':'registered-id', 'sha256':'registered-file-hash',
                           'output_sha256':object_hash(candidate)},components)


@pytest.mark.parametrize('action', ['profile_pilot','time_boundaries','duplicate_details'])
def test_valid_complete_targets_and_unknown_coverage(setup,action):
    raw,p=setup;out=tools.execute_tool(action,list(raw),p)
    r=audit(raw,p,action,out)
    assert r['status']=='VERIFIED' and r['checked_components']==COMPONENTS[action]
    r=audit(raw,p,action,out,COMPONENTS[action]+['physical_truth'])
    assert r['status']=='REJECTED' and r['unchecked_components']==['physical_truth']


@pytest.mark.parametrize('mutation', ['missing_cut','equal_cut','wrong_index','omit_record','duplicate_record','threshold'])
def test_time_boundaries_reject_incomplete_or_wrong_target(setup,mutation):
    raw,p=setup;out=tools.execute_tool('time_boundaries',list(raw),p)
    rows=out['result']['trajectories'];row=rows[0]
    assert row['partitions']==[[0,1],[2,3],[4,5]]  # exactly 30 stays, 31 and negative split
    if mutation=='missing_cut': row['cuts'].pop()
    elif mutation=='equal_cut': row['cuts'].insert(0,{'right_index':1,'left_index':0,'dt':30,'reasons':['GAP_GT_THRESHOLD']})
    elif mutation=='wrong_index': row['partitions'][1]=[3,2]
    elif mutation=='omit_record': rows.pop()
    elif mutation=='duplicate_record': rows.append(copy.deepcopy(rows[0]))
    elif mutation=='threshold': row['threshold_source_seconds']=31
    assert audit(raw,p,'time_boundaries',out)['status']=='REJECTED'


@pytest.mark.parametrize('mutation',['omit_late_event','wrong_type','wrong_index','preview_only'])
def test_duplicate_full_events_not_model_preview(setup,mutation):
    raw,p=setup
    raw['fixture:x']=[[0]*20,[[0,0]]*20]
    write_json(tools.DATA,raw);p['raw_sha256']=digest(tools.DATA)
    out=tools.execute_tool('duplicate_details',list(raw),p);events=out['result']['trajectories'][0]['events']
    assert len(events)==19 and audit(raw,p,'duplicate_details',out)['status']=='VERIFIED'
    if mutation=='omit_late_event':events.pop(16)
    elif mutation=='wrong_type':events[-1]['reasons']=['SAME_TIME_DIFFERENT_POSITION']
    elif mutation=='wrong_index':events[-1]['right_index']=0
    else:del events[8:]
    assert audit(raw,p,'duplicate_details',out)['status']=='REJECTED'


def test_registered_hash_scope_and_summary_are_not_model_assertions(setup):
    raw,p=setup;out=tools.execute_tool('profile_pilot',list(raw),p)
    binding={'artifact_id':'real-id','sha256':'filehash','output_sha256':object_hash(out),'action':'profile_pilot'}
    out['result']['summary']['n_points']=999
    assert review_artifact('profile_pilot',raw,out,p,binding)['errors']==['TARGET_HASH_MISMATCH']
    assert audit(raw,p,'profile_pilot',out)['status']=='REJECTED'
    with pytest.raises(ValueError,match='ACTION_MISMATCH'):
        tools.execute_tool('verify_time_boundaries',list(raw),p,target_artifact=out,target_binding=binding)


@pytest.fixture
def journal():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        yield goal.GoalJournal(Path(directory))


def test_goal_not_closed_by_five_actions_or_partial_profile_review(journal,setup):
    raw,p=setup;journal.bind_code('fixture-code');journal.start_run('test',p,list(raw))
    journal.execute('test','profile_pilot',p);journal.review('test','profile_pilot',p)
    journal.execute('test','time_boundaries',p)
    assert journal.coverage('test')['missing']==['time_boundaries:UNREVIEWED']
    journal.review('test','time_boundaries',p)
    assert journal.coverage('test')['status']=='VERIFIED'
    assert journal.finalize()=='IMPLEMENTING'


def test_actual_repair_consumption_independent_rejection_then_parent_resume(journal):
    j=journal;j.open_issue('known','review_targets','external','wrong result','definition',['x'],'B:engineer')
    assert j.next_task()=={'kind':'B-Repair','issue_id':'known'}
    with pytest.raises(ValueError):j.submit_repair('known','B:engineer',[CONFIG])
    j.claim_repair('known','B:engineer');j.submit_repair('known','B:engineer',[CONFIG])
    report=j.directory/'review.json'
    data={'issues':{'known':{'status':'REJECTED','checked':['counterexample'],
                           'source_hashes':{'task1/config/goal1.json':digest(CONFIG)}}}}
    write_json(report,data)
    with pytest.raises(ValueError,match='INDEPENDENT'):j.review_repair('known',report,'B:engineer')
    j.review_repair('known',report,'C:reviewer')
    assert j.state['issues']['known']['status']=='NEEDS_REPAIR'
    j.claim_repair('known','B:engineer');j.submit_repair('known','B:engineer',[CONFIG])
    # New evidence from a new review; no modification of the rejected review artifact.
    second=j.directory/'review_second.json';data['issues']['known']['status']='VERIFIED';write_json(second,data)
    j.review_repair('known',second,'C:reviewer')
    assert j.state['tasks']['review_targets']['status']=='PENDING'
    assert j.state['issues']['known']['status']=='VERIFIED'
    assert j.state['events'][-1]['kind']=='C_VERIFIED_PARENT_RESUMED'
    assert j.finalize()=='IMPLEMENTING'


def test_changed_source_invalidates_affected_artifact_but_not_unrelated(journal,setup):
    raw,p=setup;j=journal;j.bind_code('v1');j.start_run('run1',p,list(raw))
    j.execute('run1','profile_pilot',p);j.review('run1','profile_pilot',p)
    j.bind_code('v2',['task1/workflow/pipeline.py'])
    assert j.coverage('run1')['status']=='VERIFIED'
    j.bind_code('v3',['task1/workflow/diagnostics.py'])
    assert j.coverage('run1')['status']=='NEEDS_REVIEW'
    with pytest.raises(ValueError,match='STALE'):j.review('run1','profile_pilot',p)


def test_uncertain_operations_never_replayed_on_resume(journal,setup):
    raw,p=setup;j=journal;j.bind_code('v1');j.start_run('x',p,list(raw))
    j.state['inflight']={'id':'x:profile_pilot','kind':'tool','action':'profile_pilot'};j.save()
    resumed=goal.GoalJournal(j.directory)
    with pytest.raises(ValueError,match='UNCERTAIN'):resumed.execute('x','profile_pilot',p)
    with pytest.raises(ValueError,match='INFLIGHT'):resumed.bind_code('v2')
    assert resumed.reconcile('x','profile_pilot')['automatic_retry'] is False
    assert resumed.finalize()=='INTERRUPTED_CHECKPOINT'


def test_only_remaining_external_dependencies_allow_blocked_checkpoint(journal):
    j=journal;j.block_external('real_baseline',['D1','D2']);j.block_external('processing_feedback',['real_baseline'])
    assert j.finalize()=='IMPLEMENTING'
    with pytest.raises(ValueError,match='SCOPE'):j.block_external('trusted_baseline',['D1'])


def test_unknown_crs_cannot_be_bypassed_by_approval_strings(setup):
    raw,p=setup
    p['semantics']['crs']['status']='APPROVED';p['semantics']['distance_policy']['status']='APPROVED'
    p['method']['processing_status']='APPROVED_FOR_REAL_INPUT'
    assert tools.execute_tool('baseline',list(raw),p)['status']=='BLOCKED'


@pytest.mark.parametrize('components', [[], ['profile_counts'], list(goal.FOLLOWUP_COMPONENTS[:-1]), ' '.join(goal.FOLLOWUP_COMPONENTS)])
def test_followup_coverage_cannot_shrink_or_borrow_unrelated_target(components):
    audit={'status':'VERIFIED','target_sha256':'fixed-target',
           'checked_components':components,'unchecked_components':[]}
    assert not goal.followup_review_complete(audit, {'sha256':'fixed-target'})


def test_followup_exact_target_complete_scope_and_explicit_unchecked_required():
    audit={'status':'VERIFIED','target_sha256':'fixed-target',
           'checked_components':list(goal.FOLLOWUP_COMPONENTS),'unchecked_components':[]}
    assert goal.followup_review_complete(audit, {'sha256':'fixed-target'})
    assert not goal.followup_review_complete(audit, {'sha256':'other-target'})
    audit['unchecked_components']=['direction_threshold']
    assert not goal.followup_review_complete(audit, {'sha256':'fixed-target'})
    del audit['unchecked_components']
    assert not goal.followup_review_complete(audit, {'sha256':'fixed-target'})
