"""Independent numerical/content check of aggregate publication projections."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path=TASK/'public_results/projection_manifest.json';manifest=json.loads(manifest_path.read_text())
forbidden={'genes','gene','pairs','initial_genes','cand','n_cand','trip_indices','drv','o_xy','d_xy','pickup','weights','fare','drivers','orders','driver_zone','drv_zone','dest_zone','dzone','origin_source_row','destination_source_row','oxy','dxy','loc','coordinates','userId','venueId'}
probes={x['path']:x for x in json.loads((OUT/'sensitive_classification.json').read_text())['new_local_only_files']}
checks=[];numeric_fields=0;membership_found=[]

def inspect(x,path):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in forbidden:membership_found.append(path+'/'+k)
   if k in {'F','front'}:
    assert isinstance(v,list)
    if v and isinstance(v[0],list):
     assert all(len(p) in [2,3] and all(isinstance(a,(int,float)) and math.isfinite(a) for a in p) for p in v)
   inspect(v,path+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):
   if isinstance(v,(dict,list)):inspect(v,path+'/'+str(i))

def preserved(public,original,path=''):
 global numeric_fields
 if isinstance(public,dict):
  for key,value in public.items():
   if key in {'public_projection','public_sha256'}:continue
   if key in {'path','source_path'}:continue
   assert key in original,(path,key)
   preserved(value,original[key],path+'/'+key)
 elif isinstance(public,list):
  assert len(public)==len(original),(path,len(public),len(original))
  for i,(a,b) in enumerate(zip(public,original)):preserved(a,b,path+'/'+str(i))
 else:
  assert public==original,(path,public,original)
  if isinstance(public,(int,float)):numeric_fields+=1
bindings=manifest['bindings'];assert len({b['public_path'] for b in bindings})==len(bindings)
for binding in bindings:
 source=ROOT/binding['source_path'];public=ROOT/binding['public_path']
 assert sha(source)==binding['source_sha256'] and sha(public)==binding['public_sha256']
 original=json.loads(source.read_text());projection=json.loads(public.read_text())
 inspect(projection,binding['public_path'])
 if '/evolution/runs/' in binding['public_path']:
  preserved(projection,original)
 elif '/evolution/km/' in binding['public_path']:
  p=dict(projection);p.pop('algorithm',None);preserved(p,original)
 elif binding['public_path'].endswith('/evolution/metrics.json'):
  p=dict(projection);p.pop('public_projection',None)
  # Paths deliberately remap toaggregate-only objects; all scalar/vector data retained.
  for a,b in zip(p['rows'],original['rows']):
   assert a['source_path']==b['path'];assert (ROOT/a['path']).is_file()
   assert sha(ROOT/a['path'])==a['public_sha256']
  preserved(p,original)
 else:preserved(projection,original)
 if binding['source_path'] in probes:
  assert sha(source)==probes[binding['source_path']]['sha256'],'Original changed since prior independentcontentclassification'
 checks.append(dict(source=binding['source_path'],source_sha256=sha(source),public=binding['public_path'],public_sha256=sha(public),numeric_data_unchanged=True))
assert not membership_found,membership_found
actual={str(p.relative_to(ROOT)) for p in (TASK/'public_results').rglob('*') if p.is_file()}
expected={b['public_path'] for b in bindings}|{'task2/public_results/projection_manifest.json'}
assert actual==expected,{'extra':list(actual-expected),'missing':list(expected-actual)}
assert sha(TASK/'scripts/project_public_results.py')==manifest['producer_sha256']
report=dict(reviewer='/root/reinforcement',scope='Independent ofpublicprojectionauthor; exact aggregate numerical preservation, hashes and forbidden-context scan only; no claim that aggregate information reveals nothing in a theoretical privacy sense',manifest_sha256=sha(manifest_path),producer_sha256=manifest['producer_sha256'],checked_bindings=len(bindings),checked_numeric_leaves=numeric_fields,no_membership_or_context_fields=True,exact_public_file_set=True,originals_match_preprojection_independent_classification=True,checks=checks,status='PASS_IN_STATED_SCOPE')
(OUT/'public_projection_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS',len(bindings),'bindings',numeric_fields,'numeric leaves preserved')
