"""Metadata-only C check linking a completed run to its preceding exact freeze."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run',type=Path)
    args=parser.parse_args()
    manifest_path=args.run.resolve()/'manifest.json'
    assert manifest_path.is_relative_to(EV/'runs')
    run=json.loads(manifest_path.read_text())
    phase=run['partition']
    filename={'G3_SELECTION':'selection_freeze.json','FINAL_CONFIRM':'final_freeze.json',
              'FULL_PRODUCTION':'production_freeze.json'}[phase]
    path=EV/filename
    frozen=json.loads(path.read_text())
    for name,value in frozen['bindings'].items():
        assert sha(ROOT/name)==value, name
    for key in ('partition','input_ids','strategy_ids','strategies'):
        assert run[key]==frozen[key], key
    assert run['source_hashes']==frozen['processing_source_hashes']
    assert run['code_sha']==frozen['processing_code_sha']
    assert datetime.datetime.fromisoformat(run['started_at'])>datetime.datetime.fromisoformat(frozen['frozen_at'])
    assert run['completed_record_ids']==frozen['input_ids'] and not run['failed_records']
    assert run['new_record_model_calls']==frozen['new_record_model_calls']==0
    out={'role_context':'/root/c_protocol','status':'VERIFIED',
         'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'target_id':run['run_id']+':predeclared_freeze_boundary',
         'targets':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (manifest_path,path)],
         'source_hashes':run['source_hashes'],
         'checked_components':['Every actual frozen binding remains current',
             'Exact input order/partition/complete strategy definitions and IDs match freeze',
             'Processing source and Git code identity match freeze; actual run starts after freeze',
             'Complete frozen record scope reached terminal success; record model count matches zero'],
         'unchecked_components':['Numerical trace correctness and paired results: separate bound C run/pairs receipts',
             'Undocumented external exposure cannot be established from filesystem metadata'],
         'frozen_at':frozen['frozen_at'],'started_at':run['started_at'],
         'input_records':len(run['input_ids']),'strategy_ids':run['strategy_ids'],'errors':[],
         'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_frozen_run_boundary.py '+str(args.run),
         'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c'/(run['run_id']+'_freeze_boundary_receipt.json')
    with output.open('x') as f:
        json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':'VERIFIED','target_id':out['target_id'],'receipt_sha256':sha(output)}))


if __name__=='__main__':
    main()
