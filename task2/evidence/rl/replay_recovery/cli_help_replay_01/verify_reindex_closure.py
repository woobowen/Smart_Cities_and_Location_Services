from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[5];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent;PRIOR=OUT/'surviving_prior_receipts'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=pd.read_csv(PRIOR/'task2/results/rl/SUMMARY.csv',float_precision='round_trip');new=pd.read_csv(TASK/'results/rl/SUMMARY.csv',float_precision='round_trip')
assert list(zip(old.run_id,old.policy))==list(zip(new.run_id,new.policy))
count=0;maxdiff=0
for col in old.columns:
 if col.startswith('runtime_'):continue
 if pd.api.types.is_numeric_dtype(old[col]):
  a=old[col].to_numpy();b=new[col].to_numpy();assert np.allclose(a,b,rtol=1e-13,atol=1e-12,equal_nan=True),col
  finite=np.isfinite(a)&np.isfinite(b)
  if finite.any():maxdiff=max(maxdiff,float(np.max(np.abs(a[finite]-b[finite]))))
  count+=len(a)
 else:assert old[col].fillna('').equals(new[col].fillna('')),col
assert sha(TASK/'results/rl/COST_SCENARIOS.csv')==sha(PRIOR/'task2/results/rl/COST_SCENARIOS.csv')
a=json.loads((TASK/'results/rl/final_v1/paired_differences.json').read_text());b=json.loads((PRIOR/'task2/results/rl/final_v1/paired_differences.json').read_text());assert a['rows']==b['rows']
assert sha(TASK/'results/rl/final_montecarlo_v1/paired_differences.json')==sha(PRIOR/'task2/results/rl/final_montecarlo_v1/paired_differences.json')
index=json.loads((TASK/'results/rl/ACTIVE_RUNS.json').read_text())
for r in index['runs']:
 if r['active']:assert sha(TASK/r['metrics_path'])==r['metrics_sha256']
 if r['path'].startswith('results/rl/final_v1/'):
  assert r['execution_identity']=='REPLAY_RECOMPUTE_SAME_FROZEN_PRIMARY5_NOT_NEW_TEST'
oldmanifest=json.loads((PRIOR/'task2/public_results/projection_manifest.json').read_text());currentmanifest=json.loads((TASK/'public_results/projection_manifest.json').read_text())
oldbindings={r['public_path']:r for r in oldmanifest['bindings']};newbindings={r['public_path']:r for r in currentmanifest['bindings']};assert oldbindings.keys()==newbindings.keys()
changed=[]
for path,binding in newbindings.items():
 assert sha(ROOT/path)==binding['public_sha256'];assert sha(ROOT/binding['source_path'])==binding['source_sha256']
 if binding!=oldbindings[path]:changed.append(path)
assert changed==['task2/public_results/rl/final_fronts.json']
oldpub=json.loads((PRIOR/'task2/public_results/rl/final_fronts.json').read_text());newpub=json.loads((TASK/'public_results/rl/final_fronts.json').read_text());runtimes=0
for key in oldpub:
 for a,b in zip(oldpub[key],newpub[key]):
  for field,value in a.items():
   if field=='runtime':runtimes+=value!=b[field]
   else:assert value==b[field]
assert runtimes==1060
report=dict(status='REPLAY_REINDEX_AND_PUBLIC_BINDINGS_CLOSED',reviewer='/root/reinforcement',scope='Recovery/provenanceengineering; originalreviews/firsttestidentitypreserved. No newmodeltraining/test/render.',scientific_summary_cells_equal=count,maximum_scientific_summary_roundtrip_difference=maxdiff,all_active_metric_hashes_current=True,primary_replay_identity_explicit=True,cost_csv_byte_unchanged=True,primary_paired_rows_unchanged=25,secondary20_paired_file_byte_unchanged=True,public_changed_bindings=changed,public_changes_only_1060runtime_values=True,canonical_hashes={str(p.relative_to(ROOT)):sha(p) for p in [TASK/'results/rl/ACTIVE_RUNS.json',TASK/'results/rl/SUMMARY.csv',TASK/'results/rl/SUMMARY.md',TASK/'results/rl/COST_SCENARIOS.csv',TASK/'results/rl/COST_SCENARIOS.json',TASK/'results/rl/final_v1/paired_differences.json',TASK/'results/rl/final_v1/front_episode_mapping.json',TASK/'public_results/projection_manifest.json',TASK/'public_results/rl/final_fronts.json']},original_review_files_preserved=True)
(OUT/'closure_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('CLOSED',count,'scientificsummarycells,maxdiff',maxdiff,'onepublicbinding1060runtimeonly')
