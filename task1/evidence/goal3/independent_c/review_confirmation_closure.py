"""Independent application of the predeclared one-shot confirmation gate."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(bindings):
    for name,value in bindings.items():
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and sha(path)==value,name


def main():
    state=read(EV/'goal_state.json'); task=state['tasks']['confirmation']
    assert task['status']=='REVIEW_PENDING' and len(task['targets'])==6
    for target in task['targets']:
        check({target['path']:target['sha256']})
    check(task['source_hashes'])
    assert state['tasks']['final_freeze']['status']=='VERIFIED'
    parent=state['tasks']['final_freeze']
    for target in parent['targets']+[parent['receipt']]:
        check({target['path']:target['sha256']})
    assert all(issue['status']=='VERIFIED' for issue in state['issues'].values())
    f=read(EV/'final_freeze.json')
    d=read(EV/'release_decision.json')
    r=read(EV/'runs/g3-final-confirm-01/manifest.json')
    contract=read(ROOT/'task1/config/goal3/contract.json')
    for obj in (f,d,r):check(obj['bindings'])
    assert f['release_rules']==contract['release_gate']
    assert task['source_hashes']=={**r['source_hashes'],'task1/goal3/freezes.py':sha(ROOT/'task1/goal3/freezes.py')}
    assert r['input_ids']==f['input_ids'] and r['strategies']==f['strategies']
    assert r['strategy_ids']==f['strategy_ids']==['R0','S0']
    assert r['partition']==f['partition']=='FINAL_CONFIRM'
    assert datetime.datetime.fromisoformat(d['at'])>=datetime.datetime.fromisoformat(r['ended_at'])
    for suffix in ('receipt','pairs_receipt','accounting_receipt','freeze_boundary_receipt'):
        c=read(EV/'independent_c'/('g3-final-confirm-01_'+suffix+'.json'))
        assert c['status']=='VERIFIED' and c['role_context']=='/root/c_protocol' and not c['errors']
        check(c['source_hashes'])
        for target in c['targets']:check({target['path']:target['sha256']})
    primary=f['primary_strategy']; pair=r['comparisons'][primary+'|R0']
    supported=primary!='R0' and pair['all_guards_pass'] and pair['replacement_supported']
    expected_final=primary if supported else f['fallback_strategy']
    assert d['primary_strategy']==primary
    assert d['final_strategy']==expected_final=='S0'
    assert d['trigger']==pair
    assert d['status']==('SUPPORTED_WITHIN_SCOPE' if supported else 'PREDECLARED_REFERENCE_RELEASE')
    assert d['predeclared_fallback_used']==(primary!='R0' and not supported)
    assert not d['retuning_or_new_winner_selection_on_final']
    assert d['human_judgment'].startswith('NOT_AVAILABLE')
    assert pair['n_records']==pair['protected_records']==600 and pair['strict_gain_records']==349
    assert not pair['failure_records'] and pair['coverage_delta']==26352
    assert not (EV/'production_freeze.json').exists()
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'confirmation',
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'targets':task['targets'],'source_hashes':task['source_hashes'],
        'checked_components':['Six exact actual submitted artifacts and33sources; current C-verified final freeze parent',
            'Consumed complete600record/62284point/1200trace raw C audit plus40record80Decimal/PROJsample',
            'Consumed2400complete paired rows, actual counter/committed source and freeze boundary receipts; all target bytes current',
            'Independent predeclared release gate: primaryS0 must satisfy every guard andregisteredstrictgain; otherwiseonlyR0 fallback',
            'Release trigger equals full verified S0|R0pair object; finalS0/status/fallbackfalse/time follow gate exactly',
            'No final retuning/new winnerselection/recordfallback or fabricated human judgment; all original runs remain unchanged'],
        'unchecked_components':['Production not yet frozen/run','Full dataset statistics, final reports/notebooks/package/publication',
            'No noise accuracy/source datum/population universal superiority inference'],
        'confirmation_result':pair,'final_deployment_strategy':'S0',
        'predeclared_fallback_used':False,'research_status':'SUPPORTED_WITHIN_FINAL_CONFIRM_SCOPE',
        'interpretation':'One registered release gate on600previously reserved records; full-production results remain descriptive and are not all independent tests.',
        'errors':[],'not_new_user_approval':True,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_confirmation_closure.py',
        'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/confirmation_closure_receipt.json'
    with output.open('x') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','final_strategy':expected_final,'receipt_sha256':sha(output)}))


if __name__=='__main__':
    main()
