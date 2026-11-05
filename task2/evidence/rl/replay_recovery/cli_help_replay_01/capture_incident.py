"""Preserve current replay and surviving earlier receipts before repairs/reindexing."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[5];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=[
 'task2/evidence/rl/ARTIFACT_FREEZE.json','task2/results/rl/ACTIVE_RUNS.json','task2/results/rl/SUMMARY.csv','task2/results/rl/SUMMARY.md',
 'task2/results/rl/COST_SCENARIOS.csv','task2/results/rl/COST_SCENARIOS.json','task2/results/rl/final_v1/paired_differences.json',
 'task2/results/rl/final_montecarlo_v1/paired_differences.json','task2/results/rl/final_v1/front_episode_mapping.json',
 'task2/public_results/rl/final_fronts.json','task2/public_results/projection_manifest.json',
 'task2/evidence/independent_ea_on_rl/result.json','task2/evidence/independent_ea_on_rl/policy_result.json',
 'task2/evidence/independent_package/public_projection_review.json','task2/evidence/rl/FINAL_SELECTION.json',
 'task2/scripts/run_rl_final.py']
saved=[]
for rel in prior:
 p=ROOT/rel
 if not p.is_file():raise FileNotFoundError(p)
 q=OUT/'surviving_prior_receipts'/rel
 if q.exists():raise RuntimeError('Refuse replacing incident snapshot')
 q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
 saved.append(dict(original=rel,snapshot=str(q.relative_to(ROOT)),sha256=sha(p)))
source=TASK/'results/rl/final_v1';replayed=[]
for p in sorted(source.rglob('*')):
 if p.is_symlink():raise RuntimeError('Unexpected symlink in forensic source')
 if not p.is_file():continue
 q=OUT/'replayed_output'/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True)
 if q.exists():raise RuntimeError('Refuse replacing replay snapshot')
 shutil.copyfile(p,q);replayed.append(dict(original=str(p.relative_to(ROOT)),snapshot=str(q.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size))
inputs={}
for rel in ['task2/results/data/trips_train.csv','task2/results/data/trips_validation.csv','task2/results/data/checkins_train.csv','task2/results/data/trips_test.csv']:
 p=ROOT/rel;inputs[rel]=sha(p)
old_index=json.loads((OUT/'surviving_prior_receipts/task2/results/rl/ACTIVE_RUNS.json').read_text());changes=[]
for row in old_index['runs']:
 if not row['path'].startswith('results/rl/final_v1/'):continue
 p=TASK/row['metrics_path'];changes.append(dict(path=str(p.relative_to(ROOT)),prior_sha256=row['metrics_sha256'],replay_sha256=sha(p),bytes_changed=sha(p)!=row['metrics_sha256']))
record=dict(captured_utc=datetime.now(timezone.utc).isoformat(),authority='root explicitly reported accidental run_rl_final.py --help; PID24380 already finished before thiscapture. No fabricated start/finish timestamps.',trigger='Argumentnotparsedbyoldscript, so --help enterednormalREUSE-and-evaluate path',identity='REPLAY_RECOMPUTE_SAME_FROZEN_MODELS_NOT_NEW_INDEPENDENT_TEST',surviving_prior_receipts=saved,replayed_output=replayed,input_files_retained_at_unchanged_original_paths=inputs,prior_index_metric_hash_comparison=changes,original_metric_bytes='No prior day_metrics fullbytes are present in these receipts; hashes/aggregatevalues/CI/trace-linked scientific evidence survive. Do not claim recovery ofindividual original runtimes.',source_captured_before_cli_edit=True)
(OUT/'capture_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print('captured',len(saved),'priorreceipts',len(replayed),'replayfiles',sum(x['bytes'] for x in replayed),'bytes');print(json.dumps(changes,indent=2))
