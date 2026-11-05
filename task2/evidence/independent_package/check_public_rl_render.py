"""Independently redraw public RL figures in a root without private inputs orZIPs."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meta_paths=sorted((TASK/'figures/formal').glob('rl_*.json'))+sorted((TASK/'figures/candidates').glob('rl_*.json'))
inputs={p for m in meta_paths for p in json.loads(m.read_text())['input_sha256']}
code=['task2/scripts/build_rl_figures.py','task2/scripts/build_figures.py','task2/scripts/run_rl.py','task2/scripts/experiment_cli.py','task2/src/rl_dispatch.py','templates/latex/common/p2_cloud_sorbet_colors.tex']
inputs.add('task2/results/rl/development_v1/q_f60_s2024/manifest.json')
private={x['path'] for x in json.loads((TASK/'evidence/research_data/local_only_manifest_current.json').read_text())['files']}
assert not inputs&private,inputs&private
expected={str(p.relative_to(ROOT)):sha(p) for group in ['formal','candidates'] for p in (TASK/'figures'/group).glob('rl_*.png')}
assert len(expected)==12,len(expected)
started=time.perf_counter()
with tempfile.TemporaryDirectory(prefix='dispatch_public_rl_render_') as folder:
 d=Path(folder)
 for rel in sorted(inputs|set(code)):
  p=ROOT/rel;q=d/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
 assert not (d/'task2/results/data').exists()
 assert not list(d.rglob('episode_*.npz')) and not list(d.rglob('trace_*.json')) and not list(d.rglob('*.zip'))
 npzs=list(d.rglob('*.npz'));assert len(npzs)==1 and npzs[0].name=='model.npz'
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR=str(d/'.mplconfig'))
 process=subprocess.run([str(ROOT/'.venv/bin/python'),str(d/'task2/scripts/build_rl_figures.py'),'--final'],cwd=d,env=env,capture_output=True,text=True)
 (OUT/'public_rl_render_stdout.log').write_text(process.stdout);(OUT/'public_rl_render_stderr.log').write_text(process.stderr)
 assert process.returncode==0,process.stderr
 actual={str(p.relative_to(d)):sha(p) for group in ['formal','candidates'] for p in (d/'task2/figures'/group).glob('rl_*.png')}
 assert set(actual)==set(expected)
 equal={p:dict(reference_sha256=expected[p],independent_png_sha256=actual[p],equal=actual[p]==expected[p]) for p in expected}
 assert all(x['equal'] for x in equal.values()),equal
 report=dict(reviewer='/root/reinforcement',scope='Independent ofrootpublic-adapterauthor; scientificplotinput/render integration. EarlierRLfigureproductionandvisualinspection remain authorselfchecks, notthisindependentreplay.',command='isolated copied build_rl_figures.py --final; projectvenv, BLAS1, freshMPLconfig',private_csv_npz_zip_absent=True,allowed_model_npz_count=1,returncode=process.returncode,figures=equal,input_sha256={p:sha(ROOT/p) for p in sorted(inputs)},code_sha256={p:sha(ROOT/p) for p in code},seconds=time.perf_counter()-started,status='PASS_IN_STATED_SCOPE')
 (OUT/'public_rl_render_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS',len(equal),'PNG hashes identical; privateinputs absent')
