"""Exact publication-boundary recommendations; no data or authors' artifacts mutated."""
from pathlib import Path
import fnmatch,hashlib,json
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent
manifest=TASK/'evidence/research_data/local_only_manifest.json';old=json.loads(manifest.read_text());existing={x['path'] for x in old['files']};patterns=old['patterns'];rows={};safe=[]
pattern_files={str(p.relative_to(ROOT)) for g in patterns for p in ROOT.glob(g) if p.is_file()}

def add(p,classification,reason):
 rel=str(p.relative_to(ROOT));rows[rel]={'path':rel,'classification':classification,'reason':reason,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'in_previous_exact_manifest':rel in existing,'covered_by_previous_pattern':rel in pattern_files}
for p in (TASK/'results/rl/offset_robustness_v1').glob('filtered_*.csv'):add(p,'LOCAL_ONLY_DIRECT_RECORDS','Exact source-row IDs and per-proxy origin/destination coordinates, time, individual trip/fare')
for p in (TASK/'results/rl/mechanism_validation_v1').glob('value_samples_*.npz'):add(p,'LOCAL_ONLY_PER_EVENT_SAMPLES','One row per simulated driver idle-state/time-zone and realized return, derived from actual proxy-order samples; not a model parameter or aggregate metric')
p=TASK/'results/rl/fusion_validation_v1/static_input.npz'
if p.exists():add(p,'LOCAL_ONLY_DERIVED_INPUT','One batch driver-order pickup matrix, eachorderfare and destinationzone; individual sampled inputs, not aggregate frontier')
for p in (TASK/'results/evolution/runs').glob('*.json'):
 a=json.loads(p.read_text())
 if a.get('batch_path') and a.get('pairs'):
  add(p,'LOCAL_ONLY_REVERSIBLE_SOLUTION_BINDING','Per-order genes/pairs bind incidence to objective sums; independently demonstrated rank56 recovery of56individual orderfares from sharedbatch fronts. Publish a separate aggregate-only projection preserving original localrun/hash.')
 else:safe.append({'path':str(p.relative_to(ROOT)),'reason':'No real-proxy batch binding; DTLZ2 mathematical control or separate synthetic identity'})
for p in (TASK/'results/evolution/km').glob('*.json'):
 a=json.loads(p.read_text())
 if any(r.get('pairs') or r.get('gene') is not None for r in a.get('runs',[])):
  add(p,'LOCAL_ONLY_REVERSIBLE_SOLUTION_BINDING','Scalar matching output retains anonymous order/driver incidence and individual genes aligned to aggregate objective sums; same reconstruction risk as evolutionary front records')
for p in (TASK/'results/rl/fusion_validation_v1').glob('static_seed*.npz'):add(p,'LOCAL_ONLY_REVERSIBLE_SOLUTION_BINDING','Each full per-order chromosome remains aligned tofrontF; exclude original and publish F-only projection if desired')
for rel in ['results/rl/fusion_validation_v1/static_fronts.json','results/rl/fusion_validation_v1/static_weighted_km.json','results/rl/fusion_validation_v1/dynamic_nsga_fronts.json','results/rl/final_v1/fusion_fronts.json']:
 p=TASK/rel
 if p.exists():add(p,'LOCAL_ONLY_REVERSIBLE_SOLUTION_BINDING','Anonymous local pair IDs aligned to per-matching objective sums can expose individual edge costs in singleton/linear differences; original local evidence preserved, aggregate-only projection allowed')
# Detect remaining coordinate-key objects; keep scoped all-synthetic inputs explicitly.
coordinate_keys={'ox','oy','dx','dy','latitude','longitude','origin_source_row','destination_source_row','oxy','dxy','loc','coordinates'}
key_hits=[]
for p in TASK.rglob('*.json'):
 rel=str(p.relative_to(ROOT))
 if rel in rows or rel in pattern_files:continue
 try:a=json.loads(p.read_text())
 except (json.JSONDecodeError,UnicodeError):continue
 def walk(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if k in coordinate_keys and not isinstance(v,str):yield k
    if k not in {'source','sources','history','F','genes','curve','td'}:yield from walk(v)
  elif isinstance(x,list):
   for v in x:
    if isinstance(v,(dict,list)):yield from walk(v)
 hits=sorted(set(walk(a)))
 if hits:
  identity='synthetic_allowed' if rel.startswith('task2/results/online/') and '/foursquare_proxy_v1/' not in rel else 'needs_context_review'
  reason=''
  if rel in {'task2/evidence/research_data/public_fetch_receipt.json','task2/evidence/research_data/public_fetch_network_verified.json'}:
   identity='aggregate_metadata_allowed';reason='Matched keys occur only in field-difference counts and maximum coordinate-rounding differences, not individual coordinates'
  elif rel=='task2/evidence/research_data/data_audit.json':
   identity='aggregate_metadata_allowed';reason='Matched latitude/longitude keys are only missing-value counts; ranges/schema/source hashes are aggregate audit'
  elif rel=='task2/evidence/research_data/public_conversion_proxy_check.json':
   identity='aggregate_metadata_allowed';reason='Matchedox/oy/dx/dy values are maximum absolute conversion differences, not individual locations'
  elif rel=='task2/evidence/independent_package/content_probe.json':
   identity='schema_only_allowed';reason='Matchedoxy/dxy entries contain only array shapes, not array data; reconstruction evidence reports rank/error/count only'
  key_hits.append({'path':rel,'keys':hits,'identity':identity,'reason':reason})
report={'reviewer':'/root/reinforcement, independent ofNotebook/report/publication-filterauthors; not reusing RL author selftest as package verification','based_on_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'status':'EXACT_CONTENT_CLASSIFICATION_FOR_AUTHOR_REPAIR','new_local_only_files':list(rows.values()),'safe_mathematical_control_examples':safe,'remaining_json_coordinate_key_hits':key_hits,'not_excluded':'ModelQ/V/count/trainingcurves, pureF/HV/Spacing summaries, source/schema/hash audit, code/tests, syntheticcontrols and aggregatefigures remain eligible; classification is content based, not extension based.','reconstruction_evidence':'task2/evidence/independent_package/content_probe.json; only rank/error/counts written, no recoveredperorder values'}
(OUT/'sensitive_classification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('new_local_only_files',len(rows),'needs_context',[x for x in key_hits if x['identity']!='synthetic_allowed'])
