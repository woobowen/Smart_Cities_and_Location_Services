"""Lossless source mapping for historical concatenated daily NSGA fronts."""
from pathlib import Path
import json,hashlib
TASK=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for folder,front_file,metrics_subdir in [('fusion_validation_v1','dynamic_nsga_fronts.json','dynamic'),('final_v1','fusion_fronts.json','enhancements')]:
 root=TASK/'results/rl'/folder;source=root/front_file
 if not source.exists():continue
 fronts=json.loads(source.read_text());metrics=json.loads((root/metrics_subdir/'day_metrics.json').read_text());rows=[]
 for key,policy in [('knee','qnsga_knee'),('constraint','qnsga_constraint')]:
  days=[r['day_seed'] for r in metrics if r['policy']==policy]
  assert days==list(range(50000,50005))
  assert all(r['served']>0 for r in metrics if r['policy']==policy),'all-empty day would require replay mapping'
  day_index=0;prev=-1
  traces={seed:json.loads((root/metrics_subdir/f'trace_{policy}_{seed}.json').read_text()) for seed in days}
  for ordinal,frame in enumerate(fronts[key]):
   now=frame['t']
   if now<=prev:day_index+=1
   assert day_index<len(days)
   seed=days[day_index];trace=traces[seed]
   expected=[a for a in trace['assignments'] if a['t']==now]
   assert len(expected)==len(frame['pairs']),'selected pair cardinality differs from raw episode trace'
   episode=root/metrics_subdir/f'episode_{seed}.npz';tp=root/metrics_subdir/f'trace_{policy}_{seed}.json'
   rows.append(dict(policy=policy,front_collection=key,front_ordinal=ordinal,day_seed=seed,t=now,selected=frame['selected'],selected_pair_count=len(frame['pairs']),episode_path=str(episode.relative_to(TASK)),episode_sha256=sha(episode),trace_path=str(tp.relative_to(TASK)),trace_sha256=sha(tp)))
   prev=now
  assert day_index==4,'Expected exactlyfive nonempty daily front segments'
 report=dict(source_front_path=str(source.relative_to(TASK)),source_front_sha256=sha(source),script_sha256=sha(__file__),
             reconstruction='Actualevaluate loop day order50000..50004, strict within-day t monotonicity;4time resets; all5days served>0. Verify selected cardinality at everyframe against rawtrace. OriginalF/pairs preserved.',rows=rows)
 (root/'front_episode_mapping.json').write_text(json.dumps(report,indent=2))
 print(folder,'mappedframes',len(rows))
