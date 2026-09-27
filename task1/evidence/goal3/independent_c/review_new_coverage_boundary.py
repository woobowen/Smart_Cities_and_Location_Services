"""C full enumeration of added-coverage readings and independent worst-case math."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from task1.evidence.goal2.c_contract.independent_numeric import audit_record

EV=ROOT/'task1/evidence/goal3'


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    folder=EV/'runs/g3-full-production-01';mp=folder/'manifest.json';m=read(mp)
    frozen=read(EV/'production_freeze.json')
    assert m['status']=='MACHINE_VERIFIED_PENDING_C' and m['partition']=='FULL_PRODUCTION'
    assert m['input_ids']==frozen['input_ids'] and m['strategies']==frozen['strategies']
    final=frozen['final_strategy']; seen=[];count=0;maximum=None;witness=None;targets=[]
    for shard in m['shards']:
        path=folder/shard['path'];assert sha(path)==shard['sha256']
        targets.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
        observed=[]
        with gzip.open(path,'rt') as handle:
            for line in handle:
                row=json.loads(line);rid=row['record_id'];observed.append(rid)
                b=row['traces'][row['strategy_configs']['R0']];c=row['traces'][row['strategy_configs'][final]]
                before={p['index'] for p in b['metrics']['common_point_errors'] if p['error'] is not None}
                newly=[p for p in c['metrics']['common_point_errors'] if p['error'] is not None and p['index'] not in before]
                count+=len(newly)
                local=max(newly,key=lambda p:p['error'],default=None)
                if local is not None and (maximum is None or local['error']>maximum):
                    maximum=local['error'];witness=(rid,local['index'],b,c,path)
        assert observed==shard['input_ids'];seen.extend(observed)
        if len(seen)%1000==0:print(json.dumps({'new_coverage_C_records':len(seen)}),flush=True)
    assert seen==m['input_ids']
    pair=m['comparisons'][final+'|R0']
    assert count==pair['coverage_delta'] and maximum==pair['new_coverage_max_error']
    assert witness is not None
    rid,index,b,c,witness_path=witness
    cp=ROOT/'task1/config/goal3/contract.json';contract=read(cp);rp=ROOT/contract['raw_path']
    assert sha(rp)==contract['raw_sha256'];raw=read(rp)
    audits={cid:audit_record(t,raw[rid],frozen['strategies'][cid]['parameters'],'S-D-P',contract['model'],sha(cp))
            for cid,t in [('R0',b),(final,c)]}
    assert all(a['status']=='VERIFIED' for a in audits.values())
    before=audits['R0']['common_reference'];after=audits[final]['common_reference']
    assert index not in before['errors']
    assert abs(after['errors'][index]-maximum)<1e-8
    action_b=next(p for p in b['point_actions'] if p['original_index']==index)
    action_c=next(p for p in c['point_actions'] if p['original_index']==index)
    groups=lambda trace,name,side:[s['indices'] for s in next(s for s in trace['stages'] if s['name']==name)[side]]
    edge=next(([a,z] for g in after['retained_indices'] and audits[final]['final_groups'] for a,z in zip(g,g[1:]) if a<=index<=z),None)
    details={'record_id':rid,'original_index':index,'raw_points':len(raw[rid][0]),
        'maximum_new_raw_to_final_error_work_m':maximum,
        'independent_Decimal_same_point_error_work_m':after['errors'][index],
        'R0_point_action':action_b,'final_point_action':action_c,
        'R0_S_output_original_indices':groups(b,'S','output'),
        'final_S_output_original_indices':groups(c,'S','output'),
        'final_D_output_original_indices':groups(c,'D','output'),
        'final_P_input_original_indices':groups(c,'P','input'),
        'final_P_output_original_indices':groups(c,'P','output'),
        'bracketing_final_original_indices':edge,
        'final_P_immediate_max_work_m':audits[final]['dp_maximum'],
        'math_reviews':{cid:{k:v for k,v in value.items() if k not in ('common_reference','final_groups')} for cid,value in audits.items()}}
    targets+=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (mp,EV/'production_freeze.json',cp,ROOT/'task1/evidence/goal2/c_contract/independent_numeric.py')]
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':m['run_id']+':added_coverage_maximum',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':targets,'source_hashes':m['source_hashes'],
        'checked_components':['Complete fullrun shard enumeration: addedoriginal identity set count andmaximum among all covered newpoints',
            'Actual worstrecord bothR0/final stage andledger from trustedraw independently reconstructed byDecimal/PROJ',
            'Worstpoint raw-to-final error verified independently anddistinguished from postD completePinput budget',
            'R0 filter reason, finalpoint fate andactualbracketing finaledge preserved for reporting'],
        'unchecked_components':['Noise/cleanliness truth or source datum','Whole-run numeric closure remains separate mandatory C receipt'],
        'whole_dataset_records_enumerated':len(seen),'added_covered_original_points':count,
        'witness':details,'interpretation':'Additional raw coverage is not additional guaranteed-clean points. The fixed5workmetre P guarantee applies to its postD input; it does not bound all original points newly covered by final bracketing edges.',
        'methods_or_parameters_changed':False,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_new_coverage_boundary.py',
        'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/new_coverage_boundary_receipt.json'
    with output.open('x') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','records':len(seen),'added_points':count,'witness_record':rid,'index':index,
        'raw_to_final_max_work_m':maximum,'actual_P_max_work_m':audits[final]['dp_maximum'],'receipt_sha256':sha(output)}))


if __name__=='__main__':main()
