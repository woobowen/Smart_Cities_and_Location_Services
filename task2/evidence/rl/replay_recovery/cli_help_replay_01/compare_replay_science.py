"""Compare actual replay with surviving old receipts; never invent lost runtimes."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[5];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent;PRIOR=OUT/'surviving_prior_receipts'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
index=json.loads((PRIOR/'task2/results/rl/ACTIVE_RUNS.json').read_text());summary=pd.read_csv(PRIOR/'task2/results/rl/SUMMARY.csv')
records=[];model_checks=[];all_scientific_summary_equal=True
for row in index['runs']:
 if not row['path'].startswith('results/rl/final_v1/'):continue
 current=TASK/row['metrics_path'];d=pd.DataFrame(json.loads(current.read_text()));counts=0;runtime_changes=[]
 for policy,g in d.groupby('policy'):
  old=summary[(summary.run_id==row['run_id'])&(summary.policy==policy)]
  assert len(old)==1
  for key,value in old.iloc[0].items():
   if key.endswith('_mean'):metric=key[:-5];fn='mean'
   elif key.endswith('_sample_sd'):metric=key[:-10];fn='sd'
   else:continue
   if metric not in g:continue
   actual=float(g[metric].mean() if fn=='mean' else g[metric].std(ddof=1))
   if metric=='runtime':runtime_changes.append(dict(policy=policy,statistic=fn,previous=float(value),replay=actual));continue
   assert np.isclose(actual,float(value),rtol=1e-13,atol=1e-12,equal_nan=True),(row['run_id'],policy,key,value,actual)
   counts+=1
 # These rows retain per-day science; fingerprints exclude nondeterministic elapsed time.
 science=[{k:v for k,v in r.items() if k!='runtime'} for r in json.loads(current.read_text())]
 fingerprint=hashlib.sha256(json.dumps(science,sort_keys=True,separators=(',',':'),allow_nan=True).encode()).hexdigest()
 records.append(dict(run_id=row['run_id'],path=str(current.relative_to(ROOT)),previous_sha256=row['metrics_sha256'],replay_sha256=sha(current),scientific_summary_statistics_equal=counts,scientific_fingerprint_excludes_runtime=fingerprint,runtime_statistics_changes=runtime_changes))
 for model in row['models']:
  p=TASK/model['path']/'model.npz';assert sha(p)==model['model_sha256'];model_checks.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),unchanged=True))
old_checks=json.loads((PRIOR/'task2/evidence/independent_ea_on_rl/result.json').read_text())['trace_checks'];trace_checks=[]
for item in old_checks:
 if not item['trace'].startswith('task2/results/rl/final_v1/'):continue
 t=ROOT/item['trace'];ep=ROOT/item['episode'];assert sha(t)==item['trace_sha256'];assert sha(ep)==item['episode_sha256']
 trace_checks.append(dict(trace=item['trace'],trace_sha256=sha(t),episode=item['episode'],episode_sha256=sha(ep),unchanged_vs_prior_independent_review=True))
assert len(trace_checks)==95
old_pairs=json.loads((PRIOR/'task2/results/rl/final_v1/paired_differences.json').read_text());current=pd.DataFrame(json.loads((TASK/'results/rl/final_v1/enhancements/day_metrics.json').read_text()))
for r in old_pairs['rows']:
 a=current[current.policy==r['candidate']].set_index('day_seed');b=current[current.policy==r['reference']].set_index('day_seed');seeds=r.get('seeds',list(range(50000,50005)))
 actual=(a.loc[seeds,r['metric']]-b.loc[seeds,r['metric']]).to_numpy();assert np.array_equal(actual,np.array(r['differences']))
# Old public projection preserves exact per-frame runtimes; only these change inrawfronts.
old_public=json.loads((PRIOR/'task2/public_results/rl/final_fronts.json').read_text());new_front_path=TASK/'results/rl/final_v1/fusion_fronts.json';new=json.loads(new_front_path.read_text());frame_changes=0;frame_count=0
recovered=copy.deepcopy(new)
for kind in ['knee','constraint']:
 assert len(old_public[kind])==len(new[kind])
 for i,(old,now) in enumerate(zip(old_public[kind],new[kind])):
  for key,value in old.items():
   if key=='runtime':
    frame_changes+=value!=now[key];recovered[kind][i][key]=value
   else:assert value==now[key],(kind,i,key)
  frame_count+=1
old_projection=json.loads((PRIOR/'task2/public_results/projection_manifest.json').read_text());old_front_sha=next(b['source_sha256'] for b in old_projection['bindings'] if b['source_path']=='task2/results/rl/final_v1/fusion_fronts.json')
recovered_bytes=json.dumps(recovered,ensure_ascii=False,indent=2,allow_nan=True).encode();recovered_sha=hashlib.sha256(recovered_bytes).hexdigest()
recovery=dict(attempted=True,source='oldpublicper-frameelapsedtimes + byte-identicalscientificfields/memberships, exactoriginalserializer',original_expected_sha256=old_front_sha,recovered_sha256=recovered_sha,exact_hash_match=recovered_sha==old_front_sha)
if recovered_sha==old_front_sha:
 p=OUT/'hash_verified_original_recovery/fusion_fronts.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(recovered_bytes);recovery['path']=str(p.relative_to(ROOT));recovery['claim']='Exactoldbytes recoveredandSHAverified in aseparatearchive; currentReplayfile NOT overwritten. Per-dayoriginalruntimebytes remain unrecovered.'
selection_sha=sha(TASK/'evidence/rl/FINAL_SELECTION.json');assert selection_sha==sha(PRIOR/'task2/evidence/rl/FINAL_SELECTION.json')
report=dict(observed_utc=datetime.now(timezone.utc).isoformat(),identity='REPLAY_RECOMPUTE_SAME_FROZEN_PRIMARY5_NOT_NEW_TEST',source='root disclosedaccidental--help entry; thiscomparison is forensicverification, notnewexperiment',metric_tables=records,models=model_checks,trace_episode_checks=trace_checks,paired_rows_exactly_equal=len(old_pairs['rows']),dynamic_front_frames=frame_count,only_elapsed_runtime_differences_in_front_projection=frame_changes,front_original_byte_recovery=recovery,selection_contract_unchanged_sha256=selection_sha,limits='Originalcompleteper-daymetricbytes werenotbackedup, so no bytewiseold-vs-newrawrowclaim or inventedoriginalruntimes. Scientificaggregate/pairedfields comparewith survivingfrozenvalues; unchanged95episode/tracehashes link all oldscience to the independentlycheckedreplay.',status='SCIENTIFIC_VALUES_UNCHANGED_TIMING_REPLAY_RECORDED')
(OUT/'science_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('matched95traces,4scientificsummaries,pairedrows',len(old_pairs['rows']),'frontframes',frame_count,'runtimechanged',frame_changes,'exactoldfrontrecovered',recovery['exact_hash_match'])
