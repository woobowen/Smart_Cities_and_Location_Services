"""Repair regressions: constructed inputs and offline child processes only."""
import copy
import json
import subprocess
import sys
import time
from pathlib import Path
import pytest
from task1.tests.test_control import controller, request
from task1.workflow import controller as c, tools, provider as p, budget
from task1.workflow.diagnostics import profile, duplicate_details, independent_profile_review
from task1.workflow.io import read_json, write_json, digest, object_hash, CONFIG
from task1.workflow.sources import validate_references, source_context
from task1.workflow.pipeline import run_constructed, preflight, trusted_constructed_reference
from task1.workflow.evaluation import review_baseline


@pytest.mark.parametrize('action',['verify_profiles','recompute_check'])
@pytest.mark.parametrize('case',['duplicate','extra','missing','reordered','valid','missing_field','wrong_type','not_list','not_row'])
def test_entire_profile_submission(controller, action, case):
    raw=read_json(tools.DATA);raw['second']=[[0,1],[[1,1],[2,2]]];write_json(tools.DATA,raw)
    policy=copy.deepcopy(controller.policy);policy['raw_sha256']=digest(tools.DATA)
    rows=[profile(k,v,'MOCK_TEST') for k,v in raw.items()]
    if case=='duplicate':rows.append(copy.deepcopy(rows[0]))
    if case=='extra':rows.append({**rows[0],'record_id':'foreign'})
    if case=='missing':rows.pop()
    if case=='reordered':rows.reverse()
    if case=='missing_field':del rows[0]['zero_dt']
    if case=='wrong_type':rows[0]['zero_dt']=True
    if case=='not_list':rows={'x':rows}
    if case=='not_row':rows[0]=None
    result=tools.execute_tool(action,list(raw),policy,rows,classification='MOCK_TEST')
    assert result['status']==('VERIFIED' if case in ('valid','reordered') else 'REJECTED')
    if action=='recompute_check':assert result['result']['exact_match']==(case in ('valid','reordered'))


def test_missing_time_keeps_position_diagnostic_without_fake_dt():
    result=duplicate_details('fixture',[[None,1],[[0,0],[0,0]]])
    assert result['status']=='EXECUTED' and result['events'][0]['dt_raw'] is None
    assert 'REPEATED_POSITION_NOT_AUTOMATIC_NOISE' in result['events'][0]['reasons']
    assert result['events'][0]['dt_reason']=='MISSING_OR_INVALID_TIME'
    bad=duplicate_details('fixture',[[None,None],[None,None]])
    assert 'SAME_TIME_DIFFERENT_POSITION' not in bad['events'][0]['reasons']
    assert not bad['events'][0]['position_pair_computable']


@pytest.mark.parametrize('item',[None,[],3,'x',{}, {'type':'agent_message','text':None}])
def test_invalid_event_item_is_protocol_failure(item):
    with pytest.raises(p.ProviderError):p.visible_events(json.dumps({'type':'item.started','item':item}))


@pytest.mark.parametrize('fault',['spawn','timeout','bad_jsonl'])
def test_provider_failure_receipt_preserves_safe_partial_events(tmp_path,monkeypatch,fault):
    stream='{"type":"thread.started","thread_id":"fixture"}\n'
    def fail(*args):
        if fault=='spawn':raise OSError('fixture launch failure')
        if fault=='timeout':raise subprocess.TimeoutExpired('fixture',.1,output=stream,stderr='fixture partial stderr')
        return subprocess.CompletedProcess('fixture',0,stream+'{invalid\n','ERROR fixture malformed')
    monkeypatch.setattr(p,'run_limited',fail)
    provider=p.CodexProvider(executable=sys.executable)
    out=tmp_path/'run'/'calls'/'call'
    with pytest.raises(p.ProviderError):provider.call('research','call','fixture',['source_check'],out)
    receipt=read_json(out/'receipt.json')
    assert receipt['status']=='BLOCKED' and receipt['call_id']=='call' and receipt['run_id']=='run'
    assert receipt['process_started']==(fault!='spawn')
    if fault!='spawn':assert 'thread.started' in (out/'visible_events.jsonl').read_text() and receipt['stderr']
    if fault=='bad_jsonl':assert 'stdout_line=2' in receipt['error']


@pytest.mark.parametrize('exc',[OSError('fixture IO'),ArithmeticError('fixture numeric'),TypeError('fixture bad data')])
def test_real_tool_exceptions_close_checkpoint_manifest(controller,monkeypatch,exc):
    def fail(*args,**kwargs):raise exc
    monkeypatch.setattr(c,'execute_tool',fail)
    with pytest.raises(type(exc)):controller.dispatch(request(),'execution','test-call')
    assert read_json(controller.state_path)['status']=='FAILED'
    assert read_json(controller.directory/'manifest.json')['status']=='FAILED'
    assert read_json(controller.directory/'failures/test-call.json')['call_id']=='test-call'


def test_disk_failure_reports_missing_evidence(controller,monkeypatch):
    def fail(*args,**kwargs):raise OSError('disk fixture')
    monkeypatch.setattr(c,'write_json',fail)
    with pytest.raises(c.GateError,match='EVIDENCE_MISSING'):controller.dispatch(request(),'execution','test-call')
    assert controller.state['status']=='FAILED'


@pytest.mark.parametrize('channel',['out','err'])
def test_realtime_retry_stop_kills_parent_and_child(tmp_path,channel):
    marker=tmp_path/'later'
    child="import pathlib,time;time.sleep(.5);pathlib.Path(%r).write_text('BAD')"%str(marker)
    notice=json.dumps({'type':'error','message':'Reconnecting 1/5'}) if channel=='out' else 'ERROR sampling retry 1/5'
    code='import subprocess,sys,time;subprocess.Popen([sys.executable,"-c",%r]);print(%r,file=sys.%s,flush=True);time.sleep(10)'%(child,notice,'stdout' if channel=='out' else 'stderr')
    start=time.monotonic()
    with pytest.raises(p.ProviderError) as e:p.run_limited([sys.executable,'-c',code],'',tmp_path,3)
    assert time.monotonic()-start<1
    time.sleep(.65);assert not marker.exists()
    assert e.value.returncode!=0


def test_timeout_retains_stream_and_stops_descendants(tmp_path):
    marker=tmp_path/'later'
    child="import pathlib,time;time.sleep(.5);pathlib.Path(%r).write_text('BAD')"%str(marker)
    code='import subprocess,sys,time;subprocess.Popen([sys.executable,"-c",%r]);print(\'{"type":"thread.started","thread_id":"fixture"}\',flush=True);print("WARN fixture",file=sys.stderr,flush=True);time.sleep(10)'%child
    with pytest.raises(subprocess.TimeoutExpired) as e:p.run_limited([sys.executable,'-c',code],'',tmp_path,.15)
    assert 'thread.started' in e.value.output and 'WARN' in e.value.stderr
    time.sleep(.6);assert not marker.exists()


def refs():
    return {'source':{'kind':'source'},'review':{'kind':'review','run_id':'r','parent_version':'RAW:x'},
            'numeric':{'kind':'tool','status':'VERIFIED','run_id':'r','parent_version':'RAW:x'}}


@pytest.mark.parametrize('bad',['unknown','path','wrong_parent','wrong_run','nonreview','old_review','missing_numeric'])
def test_feedback_denies_false_or_unrelated_references(bad):
    ctx=refs();r={'evidence_refs':['source'],'feedback_refs':['review','numeric']}
    if bad=='unknown':r['evidence_refs']=['invented']
    if bad=='path':r['evidence_refs']=['../../auth.json']
    if bad=='wrong_parent':ctx['numeric']['parent_version']='RAW:wrong'
    if bad=='wrong_run':ctx['review']['run_id']='old'
    if bad=='nonreview':ctx['review']['kind']='call'
    if bad=='old_review':r['feedback_refs']=['numeric']
    if bad=='missing_numeric':r['feedback_refs']=['review']
    with pytest.raises(ValueError):validate_references(r,ctx,'RAW:x','r',['review','numeric'])


def test_valid_feedback_and_real_sources():
    validate_references({'evidence_refs':['source'],'feedback_refs':['review','numeric']},refs(),'RAW:x','r',['review','numeric'])
    assert all(s['excerpt'] for s in source_context().values())


def constructed_run():
    records=[{'record_id':'fixture:plane','indices':list(range(8)), 'timestamps':list(range(8)),
              'xy':[[0,0],[1,0],[0,0],[1,0],[2,0],[3,0],[100,0],[101,0]]}]
    contract={'scope':'CONSTRUCTED_PLANAR_ONLY','approval':'ENGINEERING_TEST_ONLY',
              'method':'single_pass_simultaneous_keep_undefined',
              'parameters':{'dt':30,'distance':10,'min_points':3,'min_length':0,'direction':35,'dp':.1,'time_reliable':True}}
    return records,contract


def test_complete_constructed_runner_and_independent_review():
    records,contract=constructed_run();before=copy.deepcopy(records)
    trusted=trusted_constructed_reference(records,contract)
    result=run_constructed(records,contract)
    assert records==before and result['status']=='VERIFIED'
    assert result['stage_counts']=={'input':8,'segmented':2,'filtered':2,'denoised':1,'simplified':3,'retained':2,'not_processed':0}
    assert review_baseline(result,*trusted)['status']=='VERIFIED'
    assert {r['original_index'] for r in result['point_actions']}==set(range(8))
    damaged=copy.deepcopy(result);damaged['point_actions'].pop()
    assert review_baseline(damaged,*trusted)['status']=='REJECTED'
    damaged=copy.deepcopy(result);damaged['records'][0]['processed_segments'][0]['denoise']['deleted_indices']=[]
    assert review_baseline(damaged,*trusted)['status']=='REJECTED'


def test_constructed_approval_cannot_unlock_real_input():
    policy=read_json(CONFIG);policy['method']['processing_status']='APPROVED_FOR_REAL_INPUT'
    policy['method']['blocking_ids']=[];policy['semantics']['crs']['status']='APPROVED';policy['semantics']['distance_policy']['status']='APPROVED'
    policy['method']['approved_contract_id']=constructed_run()[1]
    # No untrusted approval object is looked up as a production contract.
    result=tools.execute_tool('baseline',['0','1','2','246','256','306','352'],policy)
    assert result['status']=='BLOCKED' and result['stage_counts']['not_processed']==783


def test_legal_choices_and_preflight(controller):
    assert len(controller.available_actions())>=3 and 'source_check' in controller.available_actions()
    assert preflight(controller.policy)
    result=controller.dispatch(request('duplicate_details'),'execution','test-call')
    assert result['output']['status']=='EXECUTED'


def test_batch_budget_fixed_across_instances_and_keeps_old_ledger(tmp_path,monkeypatch):
    old=tmp_path/'old.json';write_json(old,{'model_attempts':4,'live_stop':'historical fail'})
    xml=tmp_path/'tests.xml';xml.write_text('<testsuites><testsuite tests="1" failures="0" errors="0"/></testsuites>')
    auth=tmp_path/'auth.json';write_json(auth,{'task_id':budget.TASK,'required_files':{'tests.xml':digest(xml)},'test_report':'tests.xml','old_ledger_sha256':digest(old)})
    for name,value in [('ROOT',tmp_path),('AUTH',auth),('OLD',old),('LEDGER',tmp_path/'ledger.json')]:monkeypatch.setattr(budget,name,value)
    initial=digest(old);b=budget.RepairBudget();b.reserve('model_attempts','a','probe',probe=True)
    b.finish('probe',{'status':'VERIFIED_STRUCTURE_ONLY'})
    for i in range(5):budget.RepairBudget().reserve('model_attempts',str(i),'call'+str(i))
    with pytest.raises(ValueError,match='BUDGET'):budget.RepairBudget().reserve('model_attempts','new-run','x')
    b.freeze('fixture fault')
    with pytest.raises(ValueError,match='FROZEN'):budget.RepairBudget().reserve('tool_requests','new-base')
    assert digest(old)==initial


def test_five_stage_offline_recovery_validates_actual_feedback(controller,monkeypatch):
    """Replay signed fixture events, never calls a model; exercises full scheduler."""
    from task1.tests.test_control import prepare_recovery_fixture
    prepare_recovery_fixture(controller)
    monkeypatch.setattr(p.CodexProvider,'call',lambda *a,**k:pytest.fail('fixture must never call model'))
    controller.run(stop_after=1)
    for phase,action in [(1,'profile_pilot'),(2,'verify_profiles'),(3,'duplicate_details'),(4,'recompute_check')]:
        role=c.PHASES[phase][0];call=f'{controller.run_id}-{phase+1:02d}-{role}';out=controller.directory/'calls'/call
        value=request(action,role,call);value['evidence_refs']=['teacher:20'];value['feedback_refs']=controller.required_feedback()
        schema=p.response_schema(role,call,controller.available_actions());saved={'role':role,'call_id':call,'prompt':'CONSTRUCTED_FIXTURE','schema':schema}
        write_json(out/'input.json',saved);write_json(out/'response.json',value)
        events=[{'type':'thread.started','thread_id':call+'-fixture'}, {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(value)}},{'type':'turn.completed','usage':{}}]
        (out/'visible_events.jsonl').write_text('\n'.join(map(json.dumps,events)))
        write_json(out/'receipt.json',{'role':role,'call_id':call,'classification':'LIVE_CALL_ATTEMPT','status':'VERIFIED_STRUCTURE_ONLY','sandbox':'read-only','shell_tools':'disabled','exit_code':0,'thread_id':call+'-fixture','usage':{}})
        controller.spend('model_attempts',call);controller.state['model_dispatches'][call]={'input_hash':object_hash(saved)};controller.state['inflight_model']=call;controller.save()
        state=controller.run(stop_after=phase+1 if phase<4 else None)
    assert state['phase']==5 and state['diagnostic_loop_status']=='REAL_DIAGNOSTIC_LOOP'
    # This label tests the production scheduler; fixture artifacts stay under pytest tmp.
    assert state['real_baseline_status']=='BLOCKED' and len(state['tools'])==5
    assert len(state['calls'])==5 and state['accepted_version'] is None
