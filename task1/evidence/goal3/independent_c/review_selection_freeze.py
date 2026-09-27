"""Independent metadata-only review before opening G3_SELECTION results."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EV = ROOT/'task1/evidence/goal3'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_bindings(bindings):
    for p, h in bindings.items():
        full=(ROOT/p).resolve()
        assert full.is_relative_to(ROOT) and full.is_file()
        assert sha(full)==h, p


def main():
    path=EV/'selection_freeze.json'
    frozen=read(path)
    state=read(EV/'goal_state.json')
    task=state['tasks']['selection_freeze']
    assert task['status']=='REVIEW_PENDING'
    assert task['targets']==[{'path':str(path.relative_to(ROOT)),'sha256':sha(path)}]
    assert state['tasks']['development']['status']=='VERIFIED'
    development=state['tasks']['development']
    for t in development['targets']+[development['receipt']]:
        check_bindings({t['path']:t['sha256']})
    check_bindings(development['source_hashes'])
    assert all(i['status']=='VERIFIED' for i in state['issues'].values())
    check_bindings(task['source_hashes'])
    check_bindings(frozen['bindings'])
    check_bindings(frozen['processing_source_hashes'])
    assert frozen['processing_source_hashes']==development['source_hashes']
    assert task['source_hashes']=={**frozen['processing_source_hashes'],
        'task1/goal3/freezes.py':sha(ROOT/'task1/goal3/freezes.py')}
    sha_code=frozen['processing_code_sha']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==sha_code
    for name,digest in task['source_hashes'].items():
        content=subprocess.check_output(['git','show',sha_code+':'+name],cwd=ROOT)
        assert hashlib.sha256(content).hexdigest()==digest, name
    commit_time=datetime.datetime.fromisoformat(subprocess.check_output(
        ['git','show','-s','--format=%cI',sha_code],cwd=ROOT,text=True).strip())
    frozen_time=datetime.datetime.fromisoformat(frozen['frozen_at'])
    assert commit_time<=frozen_time
    split=read(EV/'split_manifest.json')
    contract=read(ROOT/'task1/config/goal3/contract.json')
    convergence=read(EV/'CONVERGENCE_REVIEW.json')
    definitions={r['candidate_id']:r for r in read(EV/'a_candidate_plan.json')['candidate_definitions']}
    assert frozen['partition']=='G3_SELECTION'
    assert frozen['input_ids']==split['partitions']['G3_SELECTION']
    assert len(frozen['input_ids'])==len(set(frozen['input_ids']))==240
    for name,ids in split['partitions'].items():
        if name!='G3_SELECTION':
            assert not set(ids)&set(frozen['input_ids']), name
    assert frozen['strategy_ids']==convergence['shortlist_order']==['R0','S0','G0','S0_G0']
    assert frozen['strategies']=={cid:definitions[cid] for cid in frozen['strategy_ids']}
    assert frozen['selection_rules']==contract['selection']
    assert frozen['release_rules']==contract['release_gate']
    assert frozen['working_model']==contract['model']
    assert frozen['memory']==contract['mode']
    assert frozen['initial_incumbent']==contract['selection']['initial_incumbent']=='R0'
    assert frozen['development_incumbent']==convergence['previous_incumbent_sequence'][-1]=='S0_G0'
    assert frozen['eligibility']==dict.fromkeys(frozen['strategy_ids'],True)
    for row in convergence['shortlist']:
        assert frozen['tie_metadata'][row['canonical_id']]=={
            'enhancement_modules':row['enhancement_modules'],
            'online_model_dependency':row['online_model_dependency']}
        assert row['measured_seconds'] is None
    assert frozen['measured_cost_status'].startswith('UNKNOWN_FOR_ALL')
    assert frozen['record_mode']=='DETERMINISTIC_FIXED_OR_RAW_DIAGNOSTIC_RULE'
    assert frozen['new_record_model_calls']==0
    assert frozen['source_crs']=='UNVERIFIED'
    assert not frozen['record_verifier_fallback']
    assert frozen['per_record_failure_policy']=='STOP_AFFECTED_RUN_AND_REPAIR_IMPLEMENTATION'
    assert not frozen['selection_results_read_before_freeze']
    assert not frozen['final_results_read_before_freeze']
    assert frozen['no_new_candidate_or_rule_from_selection']
    metadata_seen=[]
    for run_path in sorted((EV/'runs').glob('*/manifest.json')):
        meta=read(run_path)
        # This audit consumes only phase/time metadata, never comparisons or metrics.
        assert meta['partition']=='G3_DEVELOPMENT', run_path
        metadata_seen.append({'run_id':meta['run_id'],'partition':meta['partition']})
    for name in ('selection_decision.json','final_freeze.json','release_decision.json','production_freeze.json'):
        assert not (EV/name).exists(), name
    assert sha(ROOT/'task1/作业/作业/traj_dict.json')=='c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'selection_freeze',
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'targets':task['targets'],'source_hashes':task['source_hashes'],
        'checked_components':[
            'Exact actual selection_freeze target SHA and all bindings including contract/split/plan/memory/developmentC/convergence/A3/freezes helper',
            '240 ordered original record IDs exactly match independently audited prespecified selection split; no other partition overlap',
            'Four complete definitions and fixed order R0,S0,G0,S0_G0 unchanged from C-closed development; initial R0 and conservative approved policy exact',
            'All33 processing/helper source bytes equal recorded Git commit; commit precedes freeze; numerical sources unchanged from accepted development',
            'Workingmodel/source_crsUNVERIFIED, fixed recordmode0newLLMcalls, readonlymemory, no unregistered recordverifierfallback',
            'Equivalent-reading tie modules0/2/1/3, noonline dependency and unknown ratherthan0cost; fixed release fallbackR0 and no finalretuning',
            'Current development parentC closure and every issue includingC08 independently closed; originalrawSHA unchanged',
            'All existing run phase metadata are DEVELOPMENT; no selection/final decision/freeze or held-out run existed at this check'],
        'unchecked_components':['Future selection results; this receipt does not select a final strategy',
            'Future final confirmation/full production/reports/publication',
            'Absence of undocumented external human/data exposure cannot be proved by filesystem metadata'],
        'frozen_at':frozen['frozen_at'],'processing_code_sha':sha_code,
        'existing_run_metadata_only':metadata_seen,'input_records':240,
        'strategy_ids':frozen['strategy_ids'],'errors':[],
        'authority':'INDEPENDENT_INTERNAL_CONSISTENCY_CHECK; not new user approval',
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_selection_freeze.py',
        'checker_sha256':sha(Path(__file__))}
    out=EV/'independent_c/selection_freeze_receipt.json'
    with out.open('x') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':'VERIFIED','target_sha256':sha(path),'receipt_sha256':sha(out),'records':240}))


if __name__=='__main__':
    main()
