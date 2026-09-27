"""Independent preflight of actual full scope; no production execution/closure."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

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
    path=EV/'production_freeze.json';f=read(path)
    state=read(EV/'goal_state.json')
    assert state['tasks']['production']['status']!='VERIFIED'
    parent=state['tasks']['confirmation']
    assert parent['status']=='VERIFIED'
    for t in parent['targets']+[parent['receipt']]:check({t['path']:t['sha256']})
    check(parent['source_hashes'])
    assert all(i['status']=='VERIFIED' for i in state['issues'].values())
    contract_path=ROOT/'task1/config/goal3/contract.json';contract=read(contract_path)
    split_path=EV/'split_manifest.json';split=read(split_path)
    raw_path=ROOT/contract['raw_path']
    assert sha(raw_path)==contract['raw_sha256']=='c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'
    raw=read(raw_path)
    assert len(raw)==11386
    assert all(len(record[0])==len(record[1]) for record in raw.values())
    points=sum(len(record[0]) for record in raw.values())
    assert points==1173410
    merged=[rid for part in split['partitions'].values() for rid in part]
    assert Counter(merged)==Counter({rid:1 for rid in raw})
    assert f['partition']=='FULL_PRODUCTION' and f['input_ids']==merged
    assert len(f['input_ids'])==11386 and len(set(f['input_ids']))==11386
    assert sum(len(raw[rid][0]) for rid in f['input_ids'])==points
    release=read(EV/'release_decision.json');prior=read(EV/'final_freeze.json')
    for obj in (f,release,prior):check(obj['bindings'])
    assert f['final_strategy']==release['final_strategy']=='S0'
    assert f['strategy_ids']==['R0','S0']
    assert f['strategies']==prior['strategies']
    assert f['working_model']==contract['model'] and f['source_crs']=='UNVERIFIED'
    assert f['memory']==contract['mode']
    assert sha(ROOT/f['memory']['memory_path'])==f['memory']['memory_sha256']
    assert f['memory']['memory_access']=='FROZEN_READONLY; not used by deterministic record processing'
    assert f['new_record_model_calls']==0 and not f['record_verifier_fallback']
    assert f['record_mode']==prior['record_mode']
    assert f['per_record_failure_policy']==prior['per_record_failure_policy']
    assert f['selection_rules']==contract['selection'] and f['release_rules']==contract['release_gate']
    assert f['processing_source_hashes']==prior['processing_source_hashes']
    sources={**f['processing_source_hashes'],'task1/goal3/freezes.py':sha(ROOT/'task1/goal3/freezes.py')}
    assert sources==parent['source_hashes'];check(sources)
    code=f['processing_code_sha']
    assert code==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name,value in sources.items():
        content=subprocess.check_output(['git','show',code+':'+name],cwd=ROOT)
        assert hashlib.sha256(content).hexdigest()==value,name
    assert f['full_scope']=='ALL_PARTITIONS_INCLUDING_EXPOSED_DEVELOPMENT'
    assert not f['same_strategy_single_execution']
    assert f['method_changes_from_full_results_forbidden']
    assert f['full_statistics_identity']=='DESCRIPTIVE_DATASET_PRODUCTION; not an independent test'
    closed=next(e for e in reversed(state['events']) if e['kind']=='C_TASK_CLOSED' and e.get('task')=='confirmation')
    frozen_time=datetime.datetime.fromisoformat(f['frozen_at'])
    assert frozen_time>=datetime.datetime.fromisoformat(closed['at'])
    assert frozen_time>datetime.datetime.fromisoformat(release['at'])
    for p in (EV/'runs').glob('*/manifest.json'):
        assert read(p)['partition']!='FULL_PRODUCTION',p
    targets=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (
        path,split_path,contract_path,EV/'release_decision.json',EV/'final_freeze.json',ROOT/parent['receipt']['path'])]
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'production_freeze_preflight',
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'targets':targets,'source_hashes':sources,
        'checked_components':['Actual originalrawSHA and parsed11386record/1173410point count; eachrawtimestamp/coordinate array length matches',
            'AllpartitionIDs concatenated in frozenorder; Counter exactly equals everyrawkey once, no missing/extra/duplicate records',
            'Current C-closed confirmation task and exactrelease/finalfreeze graph; productionfreeze follows both decision and independent closure',
            'Complete R0/S0 definitions unchanged; deploymentS0 exactly equals predeclared release result; bothreference andfinal to beactually executed',
            'All33sourcebytes match actual frozenGitcommit; fixed model/sourcecrsUNVERIFIED and readonlymemory SHA unchanged',
            '0newrecordmodelcalls, no unregistered recordfallback, implementationfailurepolicy and originalselection/release rules preserved',
            'Full result identity explicitly descriptive across all exposed/reserved partitions; no new method from production feedback',
            'No FULL_PRODUCTION manifest existed before this preflight'],
        'unchecked_components':['Actual full processing, everypointterminalledger and full result consistency',
            'Expanded coordinate and category representative mathematical audit',
            'Final notebooks/reports/package/publication'],
        'does_not_close_production_task':True,
        'raw_sha256':sha(raw_path),'actual_raw_records':len(raw),'actual_raw_points':points,
        'partition_counts':{k:len(v) for k,v in split['partitions'].items()},
        'frozen_at':f['frozen_at'],'processing_code_sha':code,
        'strategy_ids':f['strategy_ids'],'final_strategy':f['final_strategy'],
        'errors':[],'not_new_user_approval':True,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_production_freeze.py',
        'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/production_freeze_receipt.json'
    with output.open('x') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','target_sha256':sha(path),'receipt_sha256':sha(output),
                      'raw_records':len(raw),'raw_points':points,'production_closed':False}))


if __name__=='__main__':
    main()
