"""Current Goal 1 deterministic execution/recomputation; never calls a model.

Run with .venv/bin/python -m task1.scripts.complete_goal1 recompute --run-id ...
after committing processing code. Native role handoff is in the same Goal journal.
"""
import argparse
import json
import subprocess
from pathlib import Path
from task1.workflow.io import ROOT, DATA, CONFIG, EVIDENCE, read_json, write_json, digest, object_hash, now
from task1.workflow.goal import GoalJournal
from task1.workflow.pipeline import preflight
from task1.workflow.tools import execute_tool
from task1.workflow.artifact_review import review_artifact, COMPONENTS

REVISION=EVIDENCE/'revisions/SC-LAB1-G1-COMPLETE-001'
ACTIONS=('profile_pilot','duplicate_details','time_boundaries','baseline')


def current_code():
    paths=['task1/workflow','task1/config','task1/scripts/complete_goal1.py']
    dirty=subprocess.check_output(['git','status','--porcelain','--',*paths],cwd=ROOT,text=True)
    if dirty.strip(): raise ValueError('COMMIT_PROCESSING_CODE_BEFORE_FINAL_RUN')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()


def run_current(run_id):
    policy=read_json(CONFIG);pilot=read_json(ROOT/'task1/config/pilot.json')
    g=GoalJournal(REVISION);code=current_code()
    changed=[]
    for run in g.state['runs'].values():
        for artifact in run['artifacts'].values():
            changed.extend(p for p,h in artifact['source_hashes'].items() if digest(ROOT/p)!=h)
    g.bind_code(code,changed);g.start_run(run_id,policy,pilot['ids'])
    for action in ACTIONS:
        result=g.execute(run_id,action,policy)
        if result['status']!='BLOCKED':
            checked=g.review(run_id,action,policy)
            if checked['status']!='VERIFIED':
                g.open_issue('NUMERIC:'+run_id+':'+action,'diagnostics' if action!='baseline' else 'real_baseline',
                             'independent numeric runtime check',checked['result']['errors'],
                             'approved contract', [run_id+':'+action], 'B-Repair:root')
                raise ValueError('RUNTIME_REVIEW_REJECTED_REPAIR_REQUIRED:'+action)
    raw=read_json(DATA);baseline=read_json(REVISION/'runs'/run_id/'baseline.json')
    if baseline['status']=='BLOCKED':
        g.block_external('real_baseline',preflight(policy))
        g.block_external('processing_feedback',['real_baseline requires D1/D2'])
        ledger=[{'record_id':rid,'original_index':i,'timestamp':t,'raw_coordinates':xy,
                 'action':'NOT_PROCESSED','reason':baseline['reason'],
                 'parent_version':'RAW:'+policy['raw_sha256'],'coordinate_domain':'RAW_UNKNOWN_DATUM'}
                for rid in pilot['ids'] for i,(t,xy) in enumerate(zip(*raw[rid]))]
    else: ledger=baseline['point_actions']
    ledger_path=REVISION/'runs'/run_id/'point_actions.jsonl'
    with ledger_path.open('x') as f:
        for row in ledger:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    run=g.state['runs'][run_id]
    run['status']='BLOCKED_EXTERNAL' if baseline['status']=='BLOCKED' else 'AWAITING_INDEPENDENT_C'
    g.event('PROCESSING_BRANCH_RECORDED',run_id=run_id,status=run['status'],ledger_sha256=digest(ledger_path))
    manifest={'at':now(),'code_sha':code,'policy_sha256':digest(CONFIG),'input_sha256':digest(DATA),
              'run_id':run_id,'classification':'CURRENT_RUN_CONDITIONAL_ANALYSIS','execution':'RECOMPUTE',
              'source_crs':'UNVERIFIED','analysis_contract_id':policy['method']['approved_contract_id'],
              'new_model_calls':0,'record_scope':pilot['ids'],'artifacts':run['artifacts'],
              'reviews':run['reviews'],'point_actions':g.attach(ledger_path),'coverage':g.coverage(run_id),
              'baseline_status':baseline['status'],'goal1_complete':False}
    write_json(REVISION/'runs'/run_id/'manifest.json',manifest,exclusive=True)
    write_json(REVISION/'current_run.json',{'run_id':run_id,'manifest':str((REVISION/'runs'/run_id/'manifest.json').relative_to(ROOT))})
    return manifest


def recompute_saved(run_id):
    """Fresh raw input and independent predicates, with stored bytes only as comparison."""
    directory=REVISION/'runs'/run_id;manifest=read_json(directory/'manifest.json')
    policy=read_json(CONFIG)
    if digest(DATA)!=manifest['input_sha256'] or digest(CONFIG)!=manifest['policy_sha256']:
        raise ValueError('RECOMPUTE_INPUT_OR_CONTRACT_CHANGED')
    raw=read_json(DATA);ids=manifest['record_scope'];checks=[]
    for action,artifact in manifest['artifacts'].items():
        if digest(ROOT/artifact['path'])!=artifact['sha256']: raise ValueError('SAVED_ARTIFACT_CHANGED')
        for path,sha in artifact['source_hashes'].items():
            if digest(ROOT/path)!=sha: raise ValueError('CODE_CHANGED_REBUILD_REQUIRED')
        actual=execute_tool(action,ids,policy)
        same=object_hash(actual)==artifact['output_sha256']
        check={'action':action,'exact_match':same,'new_output_sha256':object_hash(actual)}
        if actual['status']!='BLOCKED':
            audit=review_artifact(action,{k:raw[k] for k in ids},actual,policy,artifact)
            check['independent_review']=audit
        else:check.update(status='BLOCKED',reason=actual['reason'])
        checks.append(check)
    passed=all(c['exact_match'] and c.get('independent_review',{}).get('status','VERIFIED')=='VERIFIED' for c in checks)
    return {'mode':'RECOMPUTE','new_model_calls':0,'status':'VERIFIED' if passed else 'REJECTED',
            'scope':'fresh raw diagnostics and conditional baseline recomputation; not Goal completion',
            'source_run':run_id,'source_code_sha':manifest['code_sha'],'checks':checks}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['recompute','verify','status'])
    parser.add_argument('--run-id')
    args=parser.parse_args()
    if args.mode=='status':result=GoalJournal(REVISION).state
    else:
        if not args.run_id:parser.error('--run-id required')
        result=run_current(args.run_id) if args.mode=='recompute' else recompute_saved(args.run_id)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
