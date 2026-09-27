"""Explicit final-delivery boundary challenges on synthetic inputs only."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from task1.goal3 import runtime
from task1.evidence.goal2.c_contract.test_g2_modes_independent import memory_fixture, card

ROOT=Path(__file__).resolve().parents[4]


@pytest.mark.parametrize('forbidden_channel',[
    'raw_record_id_in_predicate',
    'method_result_or_final_feedback_in_predicate',
])
def test_routing_rejects_identifier_or_hidden_final_feedback(forbidden_channel):
    plan=json.loads((ROOT/'task1/evidence/goal3/a_candidate_plan.json').read_text())
    strategy=deepcopy(next(c for c in plan['candidate_definitions'] if c['candidate_id']=='G0'))
    strategy['conditional_rule'][forbidden_channel]=True
    with pytest.raises(ValueError,match='UNREGISTERED_ROUTING_RULE'):
        runtime.resolve_parameters(strategy,[[0,10,20],[[0,0],[1,0],[2,0]]])


@pytest.mark.parametrize('hidden_partition',['G3_SELECTION','FINAL_CONFIRM'])
def test_frozen_memory_rejects_selection_or_final_example(tmp_path,hidden_partition):
    memory=memory_fixture(tmp_path,count=1,
        edits=lambda entries:entries[0].update(partition=hidden_partition))
    result=memory.retrieve(card('SYNTHETIC_QUERY'))
    assert result['delivered']==[]
    assert result['empty_reason']=='NO_APPLICABLE_VERIFIED_DEMONSTRATION'
    assert 'NOT_DEMO_MEMORY' in result['filtered'][0]['reasons']
