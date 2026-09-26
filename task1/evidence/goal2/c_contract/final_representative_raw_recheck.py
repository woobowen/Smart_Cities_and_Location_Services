"""Final C raw-based spot recheck across all method families and risky cases.

Selection is declared in this program, uses existing frozen case rules, and does
not alter methods. Decimal DP, independent S/D and PROJ come exclusively from
C's independent_numeric, not production processing or its verifier.
"""
from collections import defaultdict
from pathlib import Path
import json
import sys
import time
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from task1.workflow.io import read_json,write_json,digest,now
from independent_numeric import audit_record
from review_development_runs import read_compressed
OUT=Path(__file__).parent;EV=ROOT/'task1/evidence/goal2'

def bound(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}
def main():
 started=time.perf_counter();contract_path=ROOT/'task1/config/goal2/contract.json';contract=read_json(contract_path);rawpath=ROOT/contract['raw_path']
 assert digest(rawpath)==contract['raw_sha256'];raw=read_json(rawpath);current=read_json(EV/'current_runs.json');cards=read_json(EV/'data/raw_diagnostics.json')
 jobs={};bindings={str(contract_path.relative_to(ROOT)):digest(contract_path),str(rawpath.relative_to(ROOT)):digest(rawpath)}
 def add(path,rid,row,label):
  bindings[str(path.relative_to(ROOT))]=digest(path);key=(str(path.relative_to(ROOT)),rid,json.dumps(row['parameters'],sort_keys=True),row['order'])
  if key not in jobs:jobs[key]={'row':row,'labels':[],'trace_file':bound(path)}
  jobs[key]['labels'].append(label)
 directory=EV/'runs'/current['evaluation_parameters'];manifest=read_json(directory/'manifest.json');entries={e['config_id']:e for e in manifest['artifacts'].values()};batches={cid:read_compressed(directory/e['file']) for cid,e in entries.items()}
 casepath=ROOT/'task1/figures/goal2/CASE_SELECTION.json';cases=read_json(casepath)['cases'];bindings[str(casepath.relative_to(ROOT))]=digest(casepath)
 for case in cases:
  cid,rid=case['config_id'],case['record_id'];row=next(r for r in batches[cid]['records'] if r['record_id']==rid);add(directory/entries[cid]['file'],rid,row,'fixed_figure_case:'+case['role'])
 lockpath=EV/'candidate_lock.json';lock=read_json(lockpath);bindings[str(lockpath.relative_to(ROOT))]=digest(lockpath)
 for name,candidate in lock['selected_single_candidates'].items():
  cid=candidate['config_id']
  for case in cases[:3]:
   rid=case['record_id'];row=next(r for r in batches[cid]['records'] if r['record_id']==rid);add(directory/entries[cid]['file'],rid,row,'single:'+name+':'+case['role'])
 directory=EV/'runs'/current['order_development'];manifest=read_json(directory/'manifest.json');table=read_json(directory/'order_table.json')
 for e in table:
  batch=read_compressed(directory/e['file']);rows=batch['records'];chosen=[min(rows,key=lambda r:r['record_id'])]
  chosen.append(max(rows,key=lambda r:(r['metrics']['raw_break_crossings'],r['metrics']['direction_windows_across_raw_breaks'],r['record_id'])))
  for row in chosen:add(directory/e['file'],row['record_id'],row,'order:'+e['order']+':stable_first_or_highest_raw_risk')
 directory=EV/'runs'/current['memory'];manifest=read_json(directory/'manifest.json')
 ref=next(e for e in manifest['artifacts'].values() if e['parameters']==contract['reference_parameters']);rows=read_compressed(directory/ref['file'])['records']
 for row in (next(r for r in rows if r['record_id']=='1347'),max(rows,key=lambda r:len(r['source_record']['indices']))):add(directory/ref['file'],row['record_id'],row,'DEMO:all_zero_or_longest_raw')
 directory=EV/'runs'/current['mode_evaluation'];manifest=read_json(directory/'manifest.json');allrows=[]
 for epref in manifest['mode_episodes']:
  path=directory/epref['path'];assert digest(path)==epref['sha256'];ep=read_json(path)
  for row in ep['records']:allrows.append((path.parent,row))
 for mode in ('llm-only','search-only','llm+search','llm+memory+search'):
  eligible=[x for x in allrows if x[1]['mode']==mode and x[1]['episode']==1]
  for level in ('LOW','MID','HIGH'):
   parent,row=min((x for x in eligible if cards[x[1]['record_id']]['stratum'].startswith(level+'_')),key=lambda x:x[1]['record_id'])
   p=parent/(row['record_id']+'_candidate_traces.json.gz');saved=read_compressed(p)['results']
   for kind,cid in (('selected',row['selected_config_id']),('reference',row['reference_config_id'])):add(p,row['record_id'],saved[cid],'mode:'+mode+':'+level+':'+kind)
 results=[]
 for job in jobs.values():
  row=job['row'];check=audit_record(row,raw[row['record_id']],row['parameters'],row['order'],contract['model'],digest(contract_path))
  results.append({'labels':job['labels'],'trace_file':job['trace_file'],'record_id':row['record_id'],'parameters':row['parameters'],'order':row['order'],'review':check})
 receipt={'role_context':'/root/c_contract','classification':'FINAL_INDEPENDENT_RAW_RECONSTRUCTION_SAMPLE','at':now(),'status':'VERIFIED' if all(r['review']['status']=='VERIFIED' for r in results) else 'REJECTED',
  'sampling_rule':'Six predeclared figure cases; each frozen single candidate at all three representative span strata, shared calculations deduplicated; all six orders at stable first/highest raw-risk records; DEMO zero-motion1347 and longest input; every mode at stable first LOW/MID/HIGH record in formal episode1, selected and reference.',
  'targets':[{'path':p,'sha256':s} for p,s in bindings.items()],'audit_program':bound(Path(__file__)),'independent_oracle':bound(OUT/'independent_numeric.py'),
  'distinct_trace_record_configurations':len(results),'checks':sum(r['review']['checks'] for r in results),'results':results,'elapsed_seconds':time.perf_counter()-started,'new_model_calls':0,
  'checked_components':['raw_original_alignment','independent_PROJ','Decimal_finite_segment_DP','independent_stage_reconstruction','full_sample_point_ledger','sample_metrics_and_denominators'],
  'unchecked_components':['full_population_Decimal_reexecution','source_datum_truth','remote_publication'],
  'limits':'This final sample supplements earlier full range/hash/ledger/common-metric reviews and hundreds of independent numeric sample checks; it is not reported as all15,721 traces independently rebuilt with Decimal.'}
 write_json(OUT/'final_representative_raw_receipt.json',receipt,exclusive=True)
 print(json.dumps({k:receipt[k] for k in ('status','distinct_trace_record_configurations','checks','elapsed_seconds')}))
if __name__=='__main__':main()
