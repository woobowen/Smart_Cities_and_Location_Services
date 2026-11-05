from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for directory in [OUT/'replayed_output',OUT/'hash_verified_original_recovery']:
 for p in sorted(directory.rglob('*')):
  if not p.is_file():continue
  if p.name.startswith('episode_') and p.suffix=='.npz':reason='per-order simulationinputs/locations fromrealproxypool, forensiccopy remainslocal'
  elif p.name.startswith('trace_') and p.suffix=='.json':reason='individualdriver/order timeline/positions/movements, forensiccopy remainslocal'
  elif p.name=='fusion_fronts.json':reason='matchingmembership linked toobjectives, including recoveredoldoriginal; reversibleper-order inputs, stayslocal'
  else:continue
  rows.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size,classification='LOCAL_ONLY_REPLAY_FORENSIC_RECORDS',reason=reason))
canonical=ROOT/'task2/results/rl/final_v1/fusion_fronts.json'
report=dict(authority='RootexplicitaccidentalReplayrecovery task andlatestuser no per-record/reversible-inputpublicupload',new_sensitive_files=rows,canonical_sensitive_file_changed=dict(path=str(canonical.relative_to(ROOT)),current_sha256=sha(canonical),reason='Onlyper-frameruntimechanged inReplay; originalrecordclassificationretained, currenthashmustrefreshwithdisclosedreplayreceipt'),not_excluded='code/guards/aggregateaudits/sourcehashes/survivingprioraggregateprojections/modelparametersremainpubliceligible',count=len(rows))
(OUT/'replay_sensitive_classification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('new sensitive exactfiles',len(rows))
