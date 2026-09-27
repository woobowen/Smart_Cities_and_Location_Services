"""Independent raw/Decimal/PROJ diagnosis of every selection protection failure."""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from task1.evidence.goal2.c_contract.independent_numeric import audit_record, allowance
from task1.evidence.goal3.independent_c.review_run import independent_route

EV=ROOT/'task1/evidence/goal3'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def indices(trace,stage,side):
    return {i for segment in next(s for s in trace['stages'] if s['name']==stage)[side]
            for i in segment['indices']}


def edge_at(groups,index):
    return next(([a,b] for group in groups for a,b in zip(group,group[1:]) if a<=index<=b),None)


def main():
    folder=EV/'runs/g3-selection-01'
    manifest_path=folder/'manifest.json'
    manifest=read(manifest_path)
    expected=['3017','9311','9534']
    assert manifest['comparisons']['G0|R0']['failure_records']==expected
    assert manifest['comparisons']['S0_G0|R0']['failure_records']==expected
    contract_path=ROOT/'task1/config/goal3/contract.json'
    contract=read(contract_path)
    raw_path=ROOT/contract['raw_path']
    assert sha(raw_path)==contract['raw_sha256']
    raw=read(raw_path)
    frozen=read(EV/'selection_freeze.json')
    all_results=[]
    targets=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (
        manifest_path,contract_path,EV/'selection_freeze.json',
        EV/'independent_c/g3-selection-01_receipt.json',
        ROOT/'task1/evidence/goal2/c_contract/independent_numeric.py')]
    for shard in manifest['shards']:
        if not set(shard['input_ids'])&set(expected):
            continue
        path=folder/shard['path']
        assert sha(path)==shard['sha256']
        targets.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
        with gzip.open(path,'rt') as handle:
            for line in handle:
                row=json.loads(line)
                rid=row['record_id']
                if rid not in expected:
                    continue
                traces={cid:row['traces'][row['strategy_configs'][cid]] for cid in frozen['strategy_ids']}
                audits={}
                for cid,trace in traces.items():
                    params,group=independent_route(frozen['strategies'][cid],raw[rid])
                    result=audit_record(trace,raw[rid],params,'S-D-P',contract['model'],sha(contract_path))
                    assert result['status']=='VERIFIED',(rid,cid,result['errors'])
                    assert not result['common_reference']['crossed_edges']
                    assert result['dp_maximum']<=5+allowance(trace['source_record']['xy'])
                    audits[cid]=result
                comparisons=[]
                for candidate,reference in [('G0','R0'),('S0_G0','S0')]:
                    c,b=traces[candidate],traces[reference]
                    ca,ba=audits[candidate],audits[reference]
                    ce,be=ca['common_reference']['errors'],ba['common_reference']['errors']
                    assert set(be)<=set(ce)
                    max_before=max(be.values()); worst=max(be,key=lambda i:ce[i]); max_after=ce[worst]
                    eps=allowance(c['source_record']['xy'])
                    assert max_after>max_before+eps
                    d_before,d_after=indices(b,'D','output'),indices(c,'D','output')
                    p_before,p_after=indices(b,'P','output'),indices(c,'P','output')
                    assert indices(b,'D','input')==indices(c,'D','input')
                    assert d_before<d_after
                    assert p_before-p_after and p_after-p_before
                    comparisons.append({'candidate':candidate,'reference':reference,
                        'source_record':rid,'same_D_input':True,'same_DP_tolerance_work_m':5,
                        'D_before_after':{'before':len(d_before),'after':len(d_after),
                            'additional_retained_original_indices':sorted(d_after-d_before)},
                        'P_before_after':{'before':len(p_before),'after':len(p_after),
                            'original_indices_no_longer_retained':sorted(p_before-p_after),
                            'newly_retained_original_indices':sorted(p_after-p_before)},
                        'common_covered_reference_points':len(be),
                        'common_max_before_work_m_Decimal':max_before,
                        'candidate_max_on_same_raw_set_work_m_Decimal':max_after,
                        'strict_margin_work_m':max_after-max_before,
                        'allowed_numeric_margin_work_m':eps,
                        'worst_candidate_original_index':worst,
                        'same_point_error_before_work_m_Decimal':be[worst],
                        'bracketing_final_edge_before':edge_at(ba['final_groups'],worst),
                        'bracketing_final_edge_after':edge_at(ca['final_groups'],worst),
                        'P_immediate_max_before_work_m_Decimal':ba['dp_maximum'],
                        'P_immediate_max_after_work_m_Decimal':ca['dp_maximum'],
                        'engineering':'VERIFIED','research':'TRADEOFF_COMMON_GEOMETRIC_PROTECTION_DEGRADED'})
                all_results.append({'record_id':rid,'raw_points':len(raw[rid][0]),
                    'runtime_group':row['runtime_groups']['G0'],
                    'independent_mathematics':{cid:{k:v for k,v in a.items() if k not in ('final_groups','common_reference')}
                                               for cid,a in audits.items()},'stage_pair_diagnoses':comparisons})
    assert sorted(r['record_id'] for r in all_results)==expected
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED',
        'target_id':'g3-selection-01:all_three_constraint_failures',
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'targets':targets,'source_hashes':manifest['source_hashes'],
        'checked_components':['All3 actual selection geometric failures from trusted original bytes',
            '12completestrategytrace independent Decimal/PROJ audits with stage/identity/ledger/metric validation',
            'Same S/Dinput within each reference pair; relaxedD keeps strictly more original points',
            'DP on changed complete upstream input removes some former retained indices and retains others at unchanged5tolerance',
            'Raw-reference identity coverage preserved and independent raw-set maximum worsens beyond fixed numerical allowance',
            'Both actual immediateDP errors still<=5workmetres; no rawbreak crossings; no implementation defect found'],
        'unchecked_components':['Noise truth or source datum','FINAL_CONFIRM effects','Alternative parameters/methods were not tried'],
        'interpretation':'Legitimate method tradeoff, not engineering failure. More D-retained input points change DP recursion and chosen vertices; fixed tolerance does not imply raw same-set maximum is nonincreasing. The registered selection protection correctly rejects these3cases.',
        'candidate_or_parameter_changes':False,'records':all_results,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_selection_failures.py',
        'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/selection_failure_receipt.json'
    with output.open('x') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':'VERIFIED','records':len(all_results),'independent_trace_recomputations':12,
        'receipt_sha256':sha(output),'diagnosis':receipt['interpretation']}))


if __name__=='__main__':
    main()
