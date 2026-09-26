"""ENGINEERING_TEST: controller fixtures, no live model requests or paid API."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

from task1.workflow import controller as c,tools
from task1.workflow.io import CONFIG,read_json,write_json,digest,object_hash,bound_path
from task1.workflow.provider import parse_response,visible_events,response_schema,ProviderError,CodexProvider
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
