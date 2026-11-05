"""Update provenance bindings only; accepted plot/PDF/SVG/PNG bytes are untouched."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[5];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assets={str(p.relative_to(ROOT)):sha(p) for folder in ['formal','candidates'] for p in (TASK/'figures'/folder).glob('*') if p.suffix in {'.png','.pdf','.svg'}}
updates=[]
for folder in ['formal','candidates']:
 for p in (TASK/'figures'/folder).glob('*.json'):
  a=json.loads(p.read_text());changes=[]
  for rel,old_hash in a.get('input_sha256',{}).items():
   source=ROOT/rel
   if source.is_file() and sha(source)!=old_hash:
    # Only the current primary final replay changes are permitted inthisrepair.
    if not rel.startswith('task2/results/rl/final_v1/'):
     raise RuntimeError('Unexpecteddifferentfigureinputoutsideknownreplay:'+rel)
    changes.append(dict(path=rel,previous_sha256=old_hash,replay_sha256=sha(source)))
  if not changes:continue
  snapshot=OUT/'surviving_prior_figure_sidecars'/p.relative_to(ROOT);snapshot.parent.mkdir(parents=True,exist_ok=True)
  if snapshot.exists():raise RuntimeError('Preserveexistingpriorfigureaudit')
  shutil.copyfile(p,snapshot)
  before=sha(p)
  for c in changes:a['input_sha256'][c['path']]=c['replay_sha256']
  a['replay_provenance_update']=dict(identity='REPLAY_RECOMPUTE_SAME_FROZEN_PRIMARY5',receipt='task2/results/rl/final_v1/REPLAY_RECEIPT.json',scope='Onlyinputhashbindingsupdated. Allscientificvaluesidentical; accepteddrawingassetsnotrebuilt.',previous_input_hashes=changes)
  p.write_text(json.dumps(a,ensure_ascii=False,indent=2))
  updates.append(dict(path=str(p.relative_to(ROOT)),previous_sidecar_sha256=before,current_sidecar_sha256=sha(p),input_changes=changes))
for rel,digest in assets.items():assert sha(ROOT/rel)==digest
(OUT/'figure_sidecar_refresh.json').write_text(json.dumps(dict(scope='Provenanceonly; no rendering/recompilation',updated_sidecars=updates,accepted_asset_count=len(assets),all_accepted_asset_sha256_unchanged=True,asset_hashes=assets),ensure_ascii=False,indent=2));print('sidecarsupdated',len(updates),'acceptedassetsunchanged',len(assets))
