"""Execution-boundary tests: no test output is a LIVE model experiment."""
from copy import deepcopy
from pathlib import Path
import pytest
from task1.workflow.g2_modes import run_batch_episode,validate_response
from task1.workflow.g2_selection import legal_parameters,REFERENCE,compare,config_id
from task1.workflow.g2_pipeline import run_record


class SyntheticRun:
    def __init__(self,path):
        self.directory=path;self.directory.mkdir()
        self.partition='DEVELOPMENT';self.contract_hash='c'*64;self.tree_hash='s'*64
        self.split={'raw_sha256':'r'*64,'llm_subsets':{'DEVELOPMENT':['test']}}
        self.records={'test':{'record_id':'test','indices':list(range(6)),
            'timestamps':[0,10,20,30,40,50],'xy':[[0,0],[100,0],[200,0],[300,0],[400,0],[500,0]]}}
        self.manifest={'experiment_model_dispatches':0,'candidate_evaluations':0,'deterministic_tool_calls':0}
    def assert_epoch(self):pass
    def provenance(self,ids):return {'source_kind':'ENGINEERING_TEST','scope':ids,'raw_sha256':'r'*64}
    def save(self):pass


def test_search_only_never_instantiates_callable_provider(tmp_path):
    run=SyntheticRun(tmp_path/'run')
    def forbidden():raise AssertionError('HIDDEN_MODEL_CALL_OR_INSTANTIATION')
    result=run_batch_episode(run,'search-only',1,['test'],{'test':{'stratum':'TEST'}},provider_factory=forbidden)
    assert result['resources']['experiment_model_dispatches']==0
    assert result['resources']['candidate_evaluations']==20
    assert result['records'][0]['resources']['unique_candidate_evaluations']==20


@pytest.mark.parametrize('value',[{**REFERENCE,'dp':-1},{**REFERENCE,'min_points':True},{**REFERENCE,'distance':401},{}])
def test_illegal_original_parameters_rejected_without_clamping(value):
    before=deepcopy(value)
    assert not legal_parameters(value)[0]
    assert value==before


def test_batch_scope_rejects_missing_extra_and_duplicate_records():
    for rows in ([],[{'record_id':'a'},{'record_id':'a'}],[{'record_id':'a'},{'record_id':'foreign'}]):
        valid,errors=validate_response({'records':rows},['a','b'],1,'llm-only')
        assert not valid and errors


def test_llm_only_second_proposal_is_rejected():
    p={'candidate_id':'x','parameters':REFERENCE}
    valid,errors=validate_response({'records':[{'record_id':'a','proposals':[p,{**p,'candidate_id':'y'}],'stop':True}]},['a'],1,'llm-only')
    assert not valid and errors


def test_empty_output_cannot_win_by_zero_error():
    raw={'record_id':'test','indices':list(range(6)), 'timestamps':[0,10,20,30,40,50],
         'xy':[[0,0],[20,0],[40,5],[60,0],[80,0],[100,0]]}
    base=run_record(raw,REFERENCE,contract_hash='c'*64,provenance={'source_kind':'ENGINEERING_TEST'})
    empty=run_record(raw,{**REFERENCE,'min_length':130},contract_hash='c'*64,provenance={'source_kind':'ENGINEERING_TEST'})
    assert empty['metrics']['common_max_error'] is None
    assessment=compare(empty,base)
    assert not assessment['feasible'] and not assessment['strict_gain']
