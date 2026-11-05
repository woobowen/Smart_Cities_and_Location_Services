"""Read-only content probes; report structure and inference counts, never recovered rows."""
from pathlib import Path
import json,hashlib,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent
old=json.loads((TASK/'evidence/research_data/local_only_manifest.json').read_text())
blocked={x['path'] for x in old['files']}
report={'manifest_sha256':hashlib.sha256((TASK/'evidence/research_data/local_only_manifest.json').read_bytes()).hexdigest(),'csv_unclassified':[],'npz_unclassified':[],'teacher_notebook_outputs':[]}
for p in TASK.rglob('*.csv'):
 rel=str(p.relative_to(ROOT))
 if rel in blocked:continue
 with p.open(encoding='utf-8',errors='replace',newline='') as f:cols=next(csv.reader(f),[])
 danger=set(cols)&{'x','y','ox','oy','dx','dy','latitude','longitude','origin_source_row','destination_source_row'}
 if danger:report['csv_unclassified'].append({'path':rel,'columns':cols,'sensitive_columns':sorted(danger),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for p in TASK.rglob('*.npz'):
 rel=str(p.relative_to(ROOT))
 if rel in blocked:continue
 with np.load(p) as a:
  keys=a.files
  if set(keys)<= {'Q','N','V','NV','A','B','NA','NB','curve','td','episodes'}:continue
  shapes={k:list(a[k].shape) for k in keys}
 report['npz_unclassified'].append({'path':rel,'arrays':shapes,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for p in (TASK/'teacher_materials').rglob('*.ipynb'):
 a=json.loads(p.read_text());report['teacher_notebook_outputs'].append({'path':str(p.relative_to(ROOT)),'code_cells':sum(c['cell_type']=='code' for c in a['cells']),'with_outputs':sum(bool(c.get('outputs')) for c in a['cells'])})
# Show why anonymous per-order solution incidence plus objective sums may reveal fares.
paths=[]
for p in (TASK/'results/evolution/runs').glob('*.json'):
 a=json.loads(p.read_text())
 if a.get('batch_id')=='inner_hour18_batchseed2024' and a.get('n_obj')==2:paths.append((p,a))
if paths:
 a0=paths[0][1];n=len(a0['genes'][0]);X=[];y=[]
 for p,a in paths:
  for pairs,F in zip(a['pairs'],a['F']):
   row=np.zeros(n)
   for driver,j in pairs:row[j]=1
   X.append(row);y.append(-F[0])
 X=np.asarray(X);y=np.asarray(y);active=np.flatnonzero(np.any(X,axis=0));A=X[:,active]
 rank=int(np.linalg.matrix_rank(A));recovered=np.linalg.lstsq(A,y,rcond=None)[0]
 batch=ROOT/a0['batch_path']
 with np.load(batch) as b:truth=b['fare'][active]
 report['anonymous_front_fare_reconstruction']={'files_combined':len(paths),'front_equations':len(y),'active_order_columns':len(active),'rank':rank,'unique_fares_identifiable':rank==len(active),'max_fare_reconstruction_error':float(np.max(np.abs(recovered-truth))),'output_scope':'Only rank/error/counts; no individual recovered fares are written','affected_paths':[str(p.relative_to(ROOT)) for p,a in paths]}
(OUT/'content_probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['npz_unclassified']},ensure_ascii=False,indent=2));print('npz_unclassified_count',len(report['npz_unclassified']))
