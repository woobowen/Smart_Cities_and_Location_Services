"""ENGINEERING_TEST: controller fixtures, no live model requests or paid API."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import time

import jsonschema
import pytest

from task1.workflow import controller as c,tools
from task1.workflow.io import CONFIG,read_json,write_json,digest,object_hash,bound_path
from task1.workflow.provider import parse_response,visible_events,response_schema,ProviderError,CodexProvider,DISABLED_CODE_HOST,run_limited
from task1.workflow.diagnostics import profile,independent_profile_review,time_boundaries


@pytest.fixture
def controller(tmp_path,monkeypatch):
    data=tmp_path/'raw.json'
    write_json(data,{'fixture':[[0,0,10,50],[[0,0],[1,0],[1,0],[2,1]]]})
    policy=read_json(CONFIG);policy['raw_sha256']=digest(data)
    policy_path=tmp_path/'policy.json';write_json(policy_path,policy)
    pilot_path=tmp_path/'pilot.json';write_json(pilot_path,{'ids':['fixture']})
    monkeypatch.setattr(c,'DATA',data);monkeypatch.setattr(tools,'DATA',data)
    return c.Controller('engineering-test',mode='MOCK_TEST',base=tmp_path/'runs',policy_path=policy_path,pilot_path=pilot_path)


def request(action='profile_pilot',role='execution',call='test-call'):
    return {'role':role,'call_id':call,'action':action,'record_ids':['fixture'],
            'feedback_refs':[],'evidence_refs':['CONSTRUCTED_FIXTURE'],
            'summary':'Fixture diagnostic','reason':'Known nonpositive time and repeated position fixture',
            'request_status':'PROPOSED','candidate_for_future_review':None}


def test_correct_request_executes_and_independent_audit_accepts(controller):
    r=controller.dispatch(request(),'execution','test-call')
    assert r['output']['result']['summary']['zero_dt']==1
    q=request('verify_profiles','review','audit')
    result=controller.dispatch(q,'review','audit')
    assert result['output']['status']=='VERIFIED'
    assert controller.state['accepted_version'] is None
    assert r['mode']=='MOCK_TEST'
    assert r['output']['classification']=='MOCK_TEST'


@pytest.mark.parametrize('mutation,expected',[
    (lambda r:r.update(action='map_match'),jsonschema.ValidationError),
    (lambda r:r.update(path='../../approved.json'),jsonschema.ValidationError),
    (lambda r:r.update(parameters={'tolerance':999}),jsonschema.ValidationError),
    (lambda r:r.update(record_ids=['holdout']),c.GateError),
    (lambda r:r.update(record_ids=['fixture','fixture']),c.GateError),
    (lambda r:r.update(action='baseline'),c.GateError),
    (lambda r:r.update(evidence_refs=[]),c.GateError),
])
def test_scope_and_schema_denials(controller,mutation,expected):
    r=request();mutation(r)
    with pytest.raises(expected):controller.dispatch(r,'execution','test-call')
    assert not controller.state['tools']


def test_unapproved_metric_and_goal_denied(controller):
    for field,value in [('goal',2),('metrics_version','unapproved'),('semantics_version','unapproved')]:
        p=copy.deepcopy(controller.policy);p[field]=value
        with pytest.raises(c.GateError):c.validate_request(request(),'execution','test-call',p,controller.pilot)


def test_feedback_must_reference_real_trigger(controller):
    with pytest.raises(c.GateError,match='FEEDBACK'):
        controller.dispatch(request(),'execution','test-call',feedback_ids=['actual-review'])
    r=request();r['feedback_refs']=['actual-review']
    controller.dispatch(r,'execution','test-call',feedback_ids=['actual-review'])


@pytest.mark.parametrize('name',['../x','/tmp/x','a/../../x'])
def test_illegal_paths(tmp_path,name):
    with pytest.raises(ValueError):bound_path(tmp_path,name)


def test_symlink_escape_denied(tmp_path):
    (tmp_path/'link').symlink_to('/tmp')
    with pytest.raises(ValueError):bound_path(tmp_path,'link/output')


def test_raw_hash_mismatch_denied(controller):
    c.DATA.write_text('{}')
    with pytest.raises(c.GateError,match='HASH'):controller.dispatch(request(),'execution','test-call')


def test_contract_protected(controller):
    controller.policy_path.write_text('{}')
    with pytest.raises(c.GateError,match='CONTRACT'):controller.dispatch(request(),'execution','test-call')


@pytest.mark.parametrize('kind',['missing','file_hash','wrong_parent','wrong_input','forged_status'])
def test_output_tampering_is_rejected(controller,kind):
    controller.dispatch(request(),'execution','test-call')
    tool=controller.state['tools'][0];path=controller.directory/tool['artifact']
    if kind=='missing':path.unlink()
    else:
        value=read_json(path)
        if kind=='file_hash':value['output']['result']['summary']['zero_dt']=0
        elif kind=='wrong_parent':value['output']['parent_version']='FALSE_PARENT'
        elif kind=='wrong_input':value['output']['input_sha256']='FALSE_HASH'
        else:value['output']['status']='QUALITY_ACCEPTED'
        value['output_sha256']=object_hash(value['output']);write_json(path,value)
        if kind!='file_hash':tool['sha256']=digest(path)
    with pytest.raises(c.GateError):controller.read_tool(tool)


def test_failure_preserves_old_artifacts_and_resume_does_not_repeat_effect(controller):
    controller.dispatch(request(),'execution','test-call')
    artifact=controller.directory/controller.state['tools'][0]['artifact'];before=digest(artifact)
    with pytest.raises(c.GateError,match='INJECTED'):
        controller.dispatch(request('duplicate_details','execution','fault'),'execution','fault',inject_failure=True)
    assert digest(artifact)==before and controller.state['errors'][0]['classification']=='ENGINEERING_TEST'
    resumed=c.Controller(controller.run_id,mode='MOCK_TEST',base=controller.base,policy_path=controller.policy_path,pilot_path=controller.pilot_path)
    resumed.dispatch(request(),'execution','test-call')
    assert len(resumed.state['tools'])==1 and digest(artifact)==before
    assert 'TOOL_REUSED_NO_SIDE_EFFECT' in (controller.directory/'events.jsonl').read_text()


def test_budget_cannot_reset_by_new_run_id(controller):
    for _ in range(controller.policy['budget']['max_model_calls']):controller.spend('model_attempts')
    other=c.Controller('other-run',mode='MOCK_TEST',base=controller.base,policy_path=controller.policy_path,pilot_path=controller.pilot_path)
    with pytest.raises(c.GateError,match='BUDGET'):other.spend('model_attempts')


def test_search_only_no_llm_and_mock_not_live(controller):
    with pytest.raises(c.GateError,match='SEARCH_ONLY'):
        c.validate_request(request(),'execution','test-call',controller.policy,controller.pilot,mode='SEARCH_ONLY')
    with pytest.raises(c.GateError,match='LIVE_ENTRY'):controller.run()
    controller.mode='LIVE'
    with pytest.raises(c.GateError,match='MOCK'):controller.run(provider=object())


def test_unavailable_provider_never_succeeds(tmp_path):
    p=CodexProvider();p.executable=None
    with pytest.raises(ProviderError,match='LIVE_AGENT_BLOCKED'):
        p.call('research','missing','fixture prompt',['source_evidence'],tmp_path/'out')


def test_jsonl_and_schema_are_strict_and_reasoning_not_saved():
    response=request()
    events=[{'type':'thread.started','thread_id':'fixture-session'}, {'type':'turn.started'},
            {'type':'item.completed','item':{'type':'reasoning','text':'DO_NOT_SAVE'}},
            {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(response)}},
            {'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}}]
    visible=visible_events('\n'.join(json.dumps(e) for e in events))
    assert 'DO_NOT_SAVE' not in json.dumps(visible)
    schema=response_schema('execution','test-call',['profile_pilot'])
    assert parse_response(visible,schema,0)[0]==response
    for bad in ['not JSON','{"type":','[]']:
        with pytest.raises(ProviderError):visible_events(bad)
    with pytest.raises(ProviderError):parse_response(visible,schema,1)
    with pytest.raises(ProviderError):parse_response(visible[:-1],schema,0)
    visible[-2]['item']['text']='{"ok":true}'
    with pytest.raises(ProviderError):parse_response(visible,schema,0)


def test_unexpected_cli_tools_cannot_pass():
    events=visible_events(json.dumps({'type':'item.completed','item':{'type':'command_execution','id':'bad'}}))
    with pytest.raises(ProviderError):parse_response(events,{},0)


def test_intentionally_disabled_code_host_requires_completed_valid_turn():
    raw=[{'type':'thread.started','thread_id':'fixture'},
         {'type':'item.completed','item':{'type':'error','message':DISABLED_CODE_HOST,'id':'startup'}},
         {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(request())}},
         {'type':'turn.completed','usage':{}}]
    schema=response_schema('execution','test-call',['profile_pilot'])
    events=visible_events('\n'.join(map(json.dumps,raw)))
    assert events[1]['type']=='capability.disabled'
    assert parse_response(events,schema,0)[0]==request()
    with pytest.raises(ProviderError):parse_response(events[:-1],schema,0)
    with pytest.raises(ProviderError):parse_response(events,schema,1)
    raw[1]['item']['message']='A different unexpected startup error'
    with pytest.raises(ProviderError):
        parse_response(visible_events('\n'.join(map(json.dumps,raw))),schema,0)


def test_known_raw_fixture_counts_and_time_partition():
    value=[[0,0,-1,40],[[0,0],[1,0],[1,0],[2,1]]]
    row=profile('fixture',value,'CONSTRUCTED_FIXTURE')
    assert (row['zero_dt'],row['negative_dt'],row['same_time_different_position'],row['consecutive_duplicate_position'])==(1,1,1,1)
    assert independent_profile_review({'fixture':value},[row])['status']=='VERIFIED'
    row['zero_dt']=0
    assert independent_profile_review({'fixture':value},[row])['status']=='REJECTED'
    part=time_boundaries('fixture',value)
    assert part['partitions']==[[0,1],[2],[3]] and part['n_accounted']==4
    empty=profile('empty',[[],[]],'CONSTRUCTED_FIXTURE')
    assert empty['time_span_raw'] is None and empty['dt_min_raw'] is None


def prepare_recovery_fixture(controller):
    """CONSTRUCTED_FIXTURE of a crash after response, never live-model evidence."""
    controller.mode='LIVE';controller.policy['live_execution_enabled']=True
    call=controller.run_id+'-01-research'
    value=request('source_evidence','research',call)
    schema=response_schema('research',call,['source_evidence'])
    saved={'role':'research','call_id':call,'prompt':'CONSTRUCTED_FIXTURE','schema':schema}
    out=controller.directory/'calls'/call
    write_json(out/'input.json',saved);write_json(out/'response.json',value)
    events=[{'type':'thread.started','thread_id':'FIXTURE_SESSION'},
            {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(value)}},
            {'type':'turn.completed','usage':{}}]
    (out/'visible_events.jsonl').write_text('\n'.join(map(json.dumps,events)))
    receipt={'role':'research','call_id':call,'classification':'LIVE_CALL_ATTEMPT',
             'status':'VERIFIED_STRUCTURE_ONLY','sandbox':'read-only','shell_tools':'disabled',
             'exit_code':0,'thread_id':'FIXTURE_SESSION','usage':{}}
    write_json(out/'receipt.json',receipt)
    controller.spend('model_attempts',call)
    controller.state['model_dispatches'][call]={'input_hash':object_hash(saved)}
    controller.state['inflight_model']=call;controller.save()
    return out,call


def test_preplanted_live_response_is_rejected_without_model(controller,monkeypatch):
    controller.mode='LIVE';controller.policy['live_execution_enabled']=True
    call=controller.run_id+'-01-research'
    out=controller.directory/'calls'/call
    write_json(out/'response.json',request('source_evidence','research',call))
    write_json(out/'receipt.json',{})
    monkeypatch.setattr(CodexProvider,'call',lambda *a,**k:pytest.fail('No model call allowed'))
    with pytest.raises(c.GateError,match='UNDISPATCHED'):controller.run(stop_after=1)
    assert read_json(controller.ledger_path)['model_attempts']==0
    assert controller.state['status']=='PLANNED' and not controller.state['calls']


@pytest.mark.parametrize('tamper',['missing_events','empty_receipt','wrong_response','wrong_input','wrong_event','tool_event','fake_disabled'])
def test_recovery_requires_bound_visible_call_evidence(controller,monkeypatch,tamper):
    out,call=prepare_recovery_fixture(controller)
    if tamper=='missing_events':(out/'visible_events.jsonl').unlink()
    elif tamper=='empty_receipt':write_json(out/'receipt.json',{})
    elif tamper=='wrong_response':
        value=read_json(out/'response.json');value['reason']='tampered';write_json(out/'response.json',value)
    elif tamper=='wrong_input':
        value=read_json(out/'input.json');value['prompt']='tampered';write_json(out/'input.json',value)
    elif tamper=='wrong_event':(out/'visible_events.jsonl').write_text('{invalid')
    else:
        event={'type':'item.completed','item':{'type':'command_execution'}} if tamper=='tool_event' else {'type':'capability.disabled','message':'Unexpected error disguised'}
        with (out/'visible_events.jsonl').open('a') as f:f.write('\n'+json.dumps(event))
    monkeypatch.setattr(CodexProvider,'call',lambda *a,**k:pytest.fail('No model call allowed'))
    with pytest.raises(ProviderError):controller.run(stop_after=1)
    assert not controller.state['tools'] and controller.state['phase']==0


def test_valid_recovery_executes_once_without_new_model(controller,monkeypatch):
    prepare_recovery_fixture(controller)
    monkeypatch.setattr(CodexProvider,'call',lambda *a,**k:pytest.fail('No model call allowed'))
    state=controller.run(stop_after=1)
    assert state['phase']==1 and state['status']=='VERIFIED' and len(state['tools'])==1
    assert read_json(controller.ledger_path)['model_attempts']==1
    assert state['accepted_version'] is None


def test_cached_output_self_hash_cannot_replace_registered_hash(controller):
    controller.dispatch(request(),'execution','test-call')
    path=controller.directory/controller.state['tools'][0]['artifact']
    value=read_json(path);value['output']['result']['summary']['zero_dt']=999
    value['output']['status']='QUALITY_ACCEPTED';value['output_sha256']=object_hash(value['output'])
    write_json(path,value)
    with pytest.raises(c.GateError,match='FILE_HASH'):controller.dispatch(request(),'execution','test-call')
    assert controller.state['status']!='QUALITY_ACCEPTED'


@pytest.mark.parametrize('status',['REJECTED','BLOCKED'])
def test_bad_tool_does_not_advance_or_upgrade(controller,monkeypatch,status):
    prepare_recovery_fixture(controller)
    real=c.execute_tool
    def failing(*args,**kwargs):
        output=real(*args,**kwargs);output['status']=status;return output
    monkeypatch.setattr(c,'execute_tool',failing)
    monkeypatch.setattr(CodexProvider,'call',lambda *a,**k:pytest.fail('No model call allowed'))
    state=controller.run(stop_after=1)
    assert state['status']==status and state['phase']==0 and not state['decisions']


def test_tool_start_event_is_a_violation_even_with_valid_final():
    raw=[{'type':'thread.started','thread_id':'FIXTURE_SESSION'},
         {'type':'item.started','item':{'type':'command_execution','id':'forbidden'}},
         {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(request())}},
         {'type':'turn.completed','usage':{}}]
    with pytest.raises(ProviderError):
        parse_response(visible_events('\n'.join(map(json.dumps,raw))),response_schema('execution','test-call',['profile_pilot']),0)


def test_timeout_kills_child_process_group(tmp_path):
    marker=tmp_path/'orphan-marker'
    child="import pathlib,time; time.sleep(.4); pathlib.Path(%r).write_text('orphan')" % str(marker)
    parent='import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",%r]); time.sleep(10)' % child
    with pytest.raises(subprocess.TimeoutExpired):
        run_limited([sys.executable,'-c',parent],'',tmp_path,.15)
    time.sleep(.5)
    assert not marker.exists()


def test_mock_time_partitions_keep_mock_classification(controller):
    result=controller.dispatch(request('time_boundaries'),'execution','test-call')
    assert all(t['classification']=='MOCK_TEST' for t in result['output']['result']['trajectories'])


def test_recompute_accepts_same_record_set_in_different_order(controller):
    raw=read_json(tools.DATA);raw['fixture2']=[[0,1],[[1,1],[2,1]]];write_json(tools.DATA,raw)
    policy=copy.deepcopy(controller.policy);policy['raw_sha256']=digest(tools.DATA)
    prior=tools.execute_tool('profile_pilot',['fixture','fixture2'],policy,classification='MOCK_TEST')['result']['profiles']
    result=tools.execute_tool('recompute_check',['fixture2','fixture'],policy,prior,classification='MOCK_TEST')
    assert result['status']=='VERIFIED' and result['result']['exact_match']


def test_budget_freeze_cannot_be_reset_with_new_run_id(controller):
    ledger=read_json(controller.ledger_path);ledger['live_stop']='fixture retry breach';write_json(controller.ledger_path,ledger)
    other=c.Controller('new-id',mode='MOCK_TEST',base=controller.base,policy_path=controller.policy_path,pilot_path=controller.pilot_path)
    with pytest.raises(c.GateError,match='FROZEN'):other.spend('model_attempts')


def test_escalation_request_not_executed(controller):
    r=request();r['request_status']='NEEDS_REVIEW'
    with pytest.raises(c.GateError,match='REQUIRES_REVIEW'):controller.dispatch(r,'execution','test-call')
    assert not controller.state['tools']


def test_final_policy_disables_all_new_live_calls(controller,monkeypatch):
    controller.mode='LIVE'
    monkeypatch.setattr(CodexProvider,'call',lambda *a,**k:pytest.fail('No model call allowed'))
    with pytest.raises(c.GateError,match='LIVE_DISABLED'):controller.run()


@pytest.mark.parametrize('field,bad',[('invalid_timestamps',99),('dt_counts',{}),('time_span_raw',999),
                                    ('dt_min_raw',99),('position_pairs_computable',0),('issues',['fabricated'])])
def test_independent_profile_review_checks_all_reported_numeric_fields(field,bad):
    raw={'fixture':[[0,0,5],[[1,1],[2,2],[2,2]]]}
    row=profile('fixture',raw['fixture'],'CONSTRUCTED_FIXTURE')
    assert independent_profile_review(raw,[row])['status']=='VERIFIED'
    row[field]=bad
    result=independent_profile_review(raw,[row])
    assert result['status']=='REJECTED' and 'fixture:'+field in result['errors']
