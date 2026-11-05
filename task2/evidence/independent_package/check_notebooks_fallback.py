"""Independent integration check of root-authored notebook outputs and data fallback."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'reviewer':'/root/reinforcement, independent ofnotebookgenerator/executor andpublication-filterauthors','scope':'Current deliverednotebookoutputstructure/receipt/source-tests/active-index arithmetic and isolatedpublic-source fallback; no new certification ofownRL mathematics','notebooks':[]}
with zipfile.ZipFile(ROOT/'归档.zip') as z:
 original=json.loads(z.read(next(n for n in z.namelist() if n.endswith('.ipynb'))))
 original_assertions=[]
 for i in [31,33]:
  s=''.join(original['cells'][i]['source']);original_assertions.append(s[s.index('# 单元测试'):])
active=json.loads((TASK/'results/rl/ACTIVE_RUNS.json').read_text());active_paths=[TASK/x for x in active['active_day_metrics']]
assert all(p.is_file() for p in active_paths)
active_hash={r['metrics_path']:r['metrics_sha256'] for r in active['runs'] if r['active']}
assert all(sha(p)==active_hash[str(p.relative_to(TASK))] for p in active_paths)
report['active_index']={'sha256':sha(TASK/'results/rl/ACTIVE_RUNS.json'),'active_tables':len(active_paths),'all_metric_hashes_match':True,'invalid_and_historical_excluded':all(r['metrics_path'] not in active['active_day_metrics'] for r in active['runs'] if not r['active'])}
for name,attempt in [('作业2_运力调度_完成版',3),('实验3_多目标与强化学习派单_完成版',2)]:
 p=TASK/'notebooks'/f'{name}.ipynb';nb=json.loads(p.read_text());cells=[c for c in nb['cells'] if c['cell_type']=='code'];counts=[c.get('execution_count') for c in cells]
 receipt_path=TASK/'evidence/notebook_execution'/f'{name}_attempt{attempt}.json';receipt=json.loads(receipt_path.read_text())
 assert counts==list(range(1,len(cells)+1)),counts
 assert receipt['status']=='PASSED' and receipt['fresh_kernel'] and receipt['error'] is None
 assert receipt['output_sha256']==sha(p)
 assert not any(o.get('output_type')=='error' for c in cells for o in c.get('outputs',[]))
 whole='\n'.join(''.join(c['source']) for c in cells)
 assert '/home/' not in whole and 'C:\\' not in whole
 row={'path':str(p.relative_to(ROOT)),'sha256':sha(p),'actual_execution_counts':counts,'receipt':str(receipt_path.relative_to(ROOT)),'receipt_sha256':sha(receipt_path),'freshkernel_receipt_matches':True,'error_outputs':0,'source_paths_are_relative':True,'n_png_outputs':sum('image/png' in o.get('data',{}) for c in cells for o in c.get('outputs',[]))}
 if name.startswith('实验3'):
  row['original_teacher_tests_retained_verbatim']=[s in whole for s in original_assertions]
  assert all(row['original_teacher_tests_retained_verbatim'])
  streams=''.join(''.join(o.get('text',[])) for c in cells for o in c.get('outputs',[]) if o.get('output_type')=='stream')
  assert 'TODO 1 通过测试' in streams and 'TODO 2 / TODO 3 通过测试' in streams
  assert 'n_episodes=300' in whole and 'assert len(td)==300' in whole and 'active_day_metrics' in whole
  row['actual_300episode_training_cell_present']=True;row['active_registry_read_not_rglob']=True
 report['notebooks'].append(row)
# Independently import a copy with no teacher path and no originalZIP in its ROOT.
source=TASK/'src/dispatch_data.py';converted=TASK/'teacher_materials/author_fetch_reproduction/dataset_TSMC2014_NYC.csv'
with tempfile.TemporaryDirectory(prefix='dispatch_pkg_fallback_') as tmp:
 tmp=Path(tmp);dest=tmp/'task2/src/dispatch_data.py';dest.parent.mkdir(parents=True);shutil.copyfile(source,dest)
 inp=tmp/'task2/teacher_materials/author_fetch_reproduction/dataset_TSMC2014_NYC.csv';inp.parent.mkdir(parents=True);shutil.copyfile(converted,inp)
 code="import sys,json;sys.path.insert(0,sys.argv[1]);import dispatch_data as d;b=d.load_data();print(json.dumps(dict(source=d.source_metadata(d.source_path())['source_identity'],rows=len(b.trips),split={k:v['rows'] for k,v in b.audit['split'].items()},teacher_exists=(d.ROOT/'task2/teacher_materials/advanced').exists())))"
 proc=subprocess.run([str(ROOT/'.venv/bin/python'),'-c',code,str(dest.parent)],capture_output=True,text=True,check=True)
 fallback=json.loads(proc.stdout);assert fallback['source']=='AUTHOR_RECONSTRUCTED' and fallback['rows']==25550 and not fallback['teacher_exists']
 with inp.open('ab') as f:f.write(b'\n')
 bad="import sys;sys.path.insert(0,sys.argv[1]);import dispatch_data as d\ntry:d.load_data()\nexcept ValueError as e:print(type(e).__name__);sys.exit(0)\nsys.exit(3)"
 proc_bad=subprocess.run([str(ROOT/'.venv/bin/python'),'-c',bad,str(dest.parent)],capture_output=True,text=True)
 assert proc_bad.returncode==0 and 'ValueError' in proc_bad.stdout
 report['isolated_fallback']={'module_sha256':sha(source),'input_sha256':sha(converted),'actual_result':fallback,'unknown_input_hash_rejected':True,'network_fetch_rerun':False,'scope':'cached public conversion independently loaded from cleanroot with teacherfiles absent; source retrieval/downloadreceipt itself not rerun bythisreviewer'}
report['limitations']=['Notebook execution was inspected against actual freshkernel receipt andcurrentoutputhash; this reviewer did not independently rerun the fullstochasticNotebook again.','Prepublicationprojection/finalGitcandidate set notyetprovided; reportsourceZIP build/render audit pending exactartifactpaths.','Earlier RLauthor unit tests are not counted as this integrationreview.']
(OUT/'notebook_fallback_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
