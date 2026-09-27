"""Independent streaming check that report tables exactly derive from bound traces."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'task1/evidence/goal3/independent_c'


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def object_sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args()
    folder=args.run.resolve();mp=folder/'manifest.json';m=read(mp);directory=folder/'analysis';sp=directory/'summary.json';s=read(sp)
    assert m['status']=='MACHINE_VERIFIED_PENDING_C' and s['manifest_sha256']==sha(mp)
    assert s['source_sha256']==sha(ROOT/'task1/goal3/analysis.py')
    for name,h in s['tables'].items():assert sha(directory/name)==h,name
    assert s['strategy_summaries']==m['record_metrics'] and s['comparisons']==m['comparisons'] and s['P_comparisons']==m['P_comparisons']
    files={name:(directory/(name+'.csv')).open(newline='') for name in ['record_metrics','record_pairs','P_record_pairs']}
    streams={name:csv.DictReader(f) for name,f in files.items()};counts=Counter();groups=Counter();paired=defaultdict(list)
    added=defaultdict(lambda:{'count':0,'sum':0.,'max':None,'short':0,'zero':0});seen=[];targets=[]
    def csv_row(name,expected):
        row=next(streams[name],None)
        assert row is not None,(name,'missing_row')
        wanted={k:('' if expected.get(k) is None else str(expected[k])) for k in streams[name].fieldnames}
        assert row==wanted,(name,expected.get('record_id'),{k:[row.get(k),v] for k,v in wanted.items() if row.get(k)!=v})
        assert set(expected)<=set(row),('dropped_field',name,set(expected)-set(row))
        counts[name]+=1
    for shard in m['shards']:
        path=folder/shard['path'];assert sha(path)==shard['sha256'];targets.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
        shard_seen=[]
        with gzip.open(path,'rt') as handle:
            for line in handle:
                row=json.loads(line);rid=row['record_id'];shard_seen.append(rid)
                for cid,cfg in row['strategy_configs'].items():
                    trace=row['traces'][cfg];expected={k:v for k,v in trace['metrics'].items() if not isinstance(v,(dict,list))}
                    expected.update(strategy=cid,runtime_group=row['runtime_groups'][cid],terminal_status=trace['terminal_status'],trace_sha256=object_sha(trace))
                    csv_row('record_metrics',expected);groups[(cid,row['runtime_groups'][cid])]+=1
                for family,name in [('comparisons','record_pairs'),('P_comparisons','P_record_pairs')]:
                    for pair_id,pair in row[family].items():
                        expected={k:v for k,v in pair.items() if not isinstance(v,(dict,list))}
                        expected['protection_failures']=';'.join(pair['protection_failures']);csv_row(name,expected)
                        if family=='P_comparisons':continue
                        paired[(pair_id,pair['stratum'])].append(pair)
                        cid=pair_id.split('|')[0];trace=row['traces'][row['strategy_configs'][cid]]
                        extra=set(pair['newly_covered_indices'])
                        if not extra:continue
                        errors={p['index']:p['error'] for p in trace['metrics']['common_point_errors']}
                        z=added[pair_id];z['count']+=len(extra);z['sum']+=math.fsum(errors[i] for i in extra)
                        z['max']=max([v for v in [z['max']] if v is not None]+[errors[i] for i in extra])
                        short={i for st in trace['stages'] if st['name']=='S' for op in st['operations'] for p in op['segments']
                               if len(p['indices'])<5 or p['features']['length']<65 for i in p['indices']}
                        xy=trace['source_record']['xy'];zero={i for j,(a,b) in enumerate(zip(xy,xy[1:])) if a==b for i in (j,j+1)}
                        z['short']+=len(extra&short);z['zero']+=len(extra&zero)
        assert shard_seen==shard['input_ids'];seen.extend(shard_seen)
        if len(seen)%1000==0:print(json.dumps({'C_table_records':len(seen)}),flush=True)
    for name,stream in streams.items():assert next(stream,None) is None,('extra_row',name)
    for f in files.values():f.close()
    assert seen==m['input_ids'] and s['actual_records']==len(seen)
    assert s['actual_strategy_observations']==counts['record_metrics']==len(seen)*len(m['strategy_ids'])
    assert s['runtime_groups']==[{'strategy':cid,'group':group,'records':n} for (cid,group),n in groups.items()]
    with (directory/'by_stratum.csv').open(newline='') as handle:
        stream=csv.DictReader(handle)
        for (pair_id,stratum),rows in sorted(paired.items()):
            failures=[r for r in rows if not r['feasible']];gain=sum(r['strict_gain'] for r in rows);hard=any(r['status']=='REJECTED_BY_CONSTRAINT' for r in rows)
            maximum=max((r['newly_covered_max_error'] for r in rows if r['newly_covered_max_error'] is not None),default=None)
            expected={'pair':pair_id,'stratum':stratum,'n_records':len(rows),'protected_records':len(rows)-len(failures),
                'failure_records':[r['record_id'] for r in failures],'strict_gain_records':gain,
                'status':'REJECTED_BY_CONSTRAINT' if hard else 'TRADEOFF' if failures else 'SUPPORTED_WITHIN_SCOPE' if gain else 'NO_DEMONSTRATED_GAIN',
                'all_guards_pass':bool(rows) and not failures,'replacement_supported':bool(rows) and not failures and gain>0,
                'coverage_delta':sum(r['coverage_delta'] for r in rows),'final_point_delta':sum(r['n_final_delta'] for r in rows),
                'P_output_delta':sum(r['n_P_output_delta'] for r in rows),'all_equivalent_readings':bool(rows) and all(r['equivalent_readings'] for r in rows),
                'new_coverage_max_error':maximum,'failures_by_reason':dict(Counter(e for r in failures for e in r['protection_failures']))}
            actual=next(stream,None);wanted={k:'' if v is None else str(v) for k,v in expected.items()}
            assert actual==wanted,('stratum_aggregate',pair_id,stratum)
        assert next(stream,None) is None
    assert set(s['new_coverage'])==set(added)
    for pair_id,z in added.items():
        actual=s['new_coverage'][pair_id]
        assert actual['newly_covered_points']==z['count'] and actual['max_error_work_m']==z['max']
        assert math.isclose(actual['mean_error_work_m'],z['sum']/z['count'],rel_tol=1e-10,abs_tol=1e-9)
        assert actual['from_segments_shorter_than_R0_filter']==z['short']
        assert actual['raw_exact_zero_displacement_adjacent_endpoints']==z['zero'] and not actual['noise_truth_claim']
    targets+=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [mp,sp,ROOT/'task1/goal3/analysis.py',*sorted(directory.glob('*.csv'))]]
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':m['run_id']+':analysis_derivatives',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':targets,
        'source_hashes':{**m['source_hashes'],'task1/goal3/analysis.py':sha(ROOT/'task1/goal3/analysis.py')},
        'checked_components':['Every scalar metric CSV cell/runtimegroup/terminalstatus/tracehash exactly maps to bound trace',
            'Every wholechain andPonly paired CSV cell and failure list exactly maps to stored pair',
            'Every stratified paired aggregate independently recomputed without imported aggregate_pairs',
            'Whole-scope addedcoverage count/maximum/mean/shortfilter-membership/zeroedge diagnostic independently reduced',
            'Manifest/summary/table/shard/source hashes and exact record/strategy row counts'],
        'unchecked_components':['Raw-to-trace correctness/math: separate mandatory full C run receipt',
            'Shortfilter membership means pointcount<5 OR length<65, not exclusively length<65',
            'Neither zero rawdisplacement nor additionalcoverage establishes noise/cleanliness truth'],
        'counts':dict(counts),'records':len(seen),'stratum_pair_groups':len(paired),'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_analysis_tables.py '+str(args.run),
        'checker_sha256':sha(Path(__file__))}
    output=OUT/(m['run_id']+'_analysis_receipt.json')
    with output.open('x') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','records':len(seen),'counts':dict(counts),'receipt_sha256':sha(output)}))


if __name__=='__main__':main()
