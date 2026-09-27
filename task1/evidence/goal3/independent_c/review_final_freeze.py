"""Independent metadata-only final-confirmation gate; never executes a record."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(bindings):
    for path,value in bindings.items():
        p=(ROOT/path).resolve()
        assert p.is_relative_to(ROOT) and p.is_file() and sha(p)==value,path


def main():
    path=EV/'final_freeze.json'
    f=read(path)
    state=read(EV/'goal_state.json')
    task=state['tasks']['final_freeze']
    assert task['status']=='REVIEW_PENDING'
    assert task['targets']==[{'path':str(path.relative_to(ROOT)),'sha256':sha(path)}]
    parent=state['tasks']['selection']
    assert parent['status']=='VERIFIED'
    for t in parent['targets']+[parent['receipt']]:
        check({t['path']:t['sha256']})
    check(parent['source_hashes'])
    assert all(i['status']=='VERIFIED' for i in state['issues'].values())
    check(task['source_hashes']);check(f['bindings']);check(f['processing_source_hashes'])
    contract=read(ROOT/'task1/config/goal3/contract.json')
    split=read(EV/'split_manifest.json')
    selection=read(EV/'selection_decision.json')
    prior=read(EV/'selection_freeze.json')
    check(selection['bindings']);check(prior['bindings'])
    assert f['partition']=='FINAL_CONFIRM'
    assert f['input_ids']==split['partitions']['FINAL_CONFIRM']
    assert len(f['input_ids'])==len(set(f['input_ids']))==600
    for name,ids in split['partitions'].items():
        if name!='FINAL_CONFIRM':
            assert not set(ids)&set(f['input_ids']),name
    assert f['strategy_ids']==['R0','S0']
    assert f['primary_strategy']==selection['incumbent']=='S0'
    assert f['fallback_strategy']=='R0'
    assert f['strategies']=={cid:prior['strategies'][cid] for cid in f['strategy_ids']}
    ref={'dt':30,'distance':400,'min_points':5,'min_length':65,'direction':35,'dp':5}
    assert f['strategies']['R0']['parameters']==ref
    assert f['strategies']['S0']['parameters']=={**ref,'min_points':2,'min_length':0}
    assert all(v['order']=='S-D-P' and v['conditional_rule'] is None for v in f['strategies'].values())
    assert f['selection_rules']==contract['selection'] and f['release_rules']==contract['release_gate']
    assert f['release_rules']['all_fixed_guards_pass'] and f['release_rules']['strict_predeclared_gain_required']
    assert f['release_rules']['on_no_support_or_tradeoff']=='R0' and not f['release_rules']['retune_on_confirmation']
    assert f['working_model']==contract['model'] and f['source_crs']=='UNVERIFIED'
    assert f['memory']==contract['mode']
    assert sha(ROOT/f['memory']['memory_path'])==f['memory']['memory_sha256']
    assert f['memory']['memory_access']=='FROZEN_READONLY; not used by deterministic record processing'
    assert f['record_mode']==contract['mode']['default_candidate_mode']
    assert f['new_record_model_calls']==0 and not f['record_verifier_fallback']
    assert f['per_record_failure_policy']=='STOP_AFFECTED_RUN_AND_REPAIR_IMPLEMENTATION'
    assert not f['final_results_read_before_freeze'] and f['no_final_parameter_selection']
    assert not f['A_research_context_receives_final_effects']
    assert f['processing_source_hashes']==prior['processing_source_hashes']
    assert task['source_hashes']=={**f['processing_source_hashes'],'task1/goal3/freezes.py':sha(ROOT/'task1/goal3/freezes.py')}
    code=f['processing_code_sha']
    assert code==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name,value in task['source_hashes'].items():
        content=subprocess.check_output(['git','show',code+':'+name],cwd=ROOT)
        assert hashlib.sha256(content).hexdigest()==value,name
    frozen_time=datetime.datetime.fromisoformat(f['frozen_at'])
    assert frozen_time>datetime.datetime.fromisoformat(selection['at'])
    closed=next(event for event in reversed(state['events']) if event['kind']=='C_TASK_CLOSED' and event.get('task')=='selection')
    assert frozen_time>=datetime.datetime.fromisoformat(closed['at'])
    phases=[]
    for p in sorted((EV/'runs').glob('*/manifest.json')):
        meta=read(p)
        assert meta['partition'] in ('G3_DEVELOPMENT','G3_SELECTION'),p
        phases.append({'run_id':meta['run_id'],'partition':meta['partition']})
    assert not (EV/'release_decision.json').exists() and not (EV/'production_freeze.json').exists()
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'final_freeze',
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'targets':task['targets'],'source_hashes':task['source_hashes'],
        'checked_components':['Exact final_freeze target and every binding; current independently closed selection parent task and sources',
            '600ordered originalrecord IDs match prespecified independently audited FINAL_CONFIRM manifest and do not overlap any other partition',
            'PrimaryS0 and reference/fallbackR0 exactly inherit selected complete definitions; no grouping/parameter/memory change',
            'R0 S-D-P(30,400,5,65,35,5); S0 differs only min_points2/min_length0; bothconditional_ruleNone',
            'Allguards+registeredstrictgain orR0 release gate unchanged; no finalretune, no record-verifier fallback, technicalfailure stopsaffectedrun',
            'Fixed conditional ENU/source_crsUNVERIFIED; frozen readonly DEMO memory hash, unused deterministic recordprocessing,0newrecordmodelcalls',
            'All33processing/helper source bytes match recordedGitcommit; numericalsourceepoch unchanged from verified selection',
            'Final freeze follows actual selectiondecision and independent C taskclose; existingrunphase metadata contain only development/selection, no FINAL/full effect'],
        'unchecked_components':['FINAL_CONFIRM effect not read or computed','Final support/fallback decision and production outcomes',
            'Undocumented external exposure cannot be proved absent; raw structure/hash inspection is already documented',
            'Source datum/noise truth/reports/package/publication'],
        'frozen_at':f['frozen_at'],'processing_code_sha':code,'input_records':600,
        'primary_strategy':'S0','fallback_strategy':'R0','existing_run_metadata_only':phases,
        'exposure_language':'NO_DOCUMENTED_METHOD_EXPOSURE before frozen confirmation; not a claim of completely untouched raw data',
        'not_new_user_approval':True,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_final_freeze.py',
        'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/final_freeze_receipt.json'
    with output.open('x') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','target_sha256':sha(path),'receipt_sha256':sha(output),'records':600}))


if __name__=='__main__':
    main()
