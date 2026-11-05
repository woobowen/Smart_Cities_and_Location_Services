"""Record bounded non-experimental CLI checks and original source identities."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).parent
records=json.loads((HERE/'source_hashes.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={str(p.relative_to(ROOT)):sha(p) for parent in [ROOT/'task2/results/rl',ROOT/'task2/public_results'] for p in parent.rglob('*') if p.is_file()}
commands=[]
for r in records:
 name=Path(r['path']).name
 for mode in ['direct','module']:
  command=[str(ROOT/'.venv/bin/python'),'-S','-B']+([str(ROOT/r['path'])] if mode=='direct' else ['-m','task2.scripts.'+Path(name).stem])+['--help']
  result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
  assert result.returncode==0 and '--output' in result.stdout,result.stderr
  commands.append(dict(script=r['path'],mode=mode,command=command,returncode=result.returncode,stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),stderr=result.stderr))
with tempfile.TemporaryDirectory(prefix='rl_guard_import_') as folder:
 d=Path(folder)
 code=['task2/scripts/run_rl.py','task2/scripts/experiment_cli.py','task2/scripts/build_rl_figures.py','task2/scripts/build_figures.py','task2/src/rl_dispatch.py','templates/latex/common/p2_cloud_sorbet_colors.tex']
 models=['task2/results/rl/development_v1/q_f60_s2024/model.npz','task2/results/rl/development_v1/q_f60_s2024/manifest.json']
 for rel in code+models:
  p=d/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
 assert not (d/'task2/results/data').exists() and not list(d.rglob('trace_*.json')) and not list(d.rglob('*.zip'))
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR=str(d/'.mplconfig'))
 program="import sys;from pathlib import Path;sys.path.insert(0,'task2/scripts');import run_rl;qt,meta=run_rl.load_model(Path('task2/results/rl/development_v1/q_f60_s2024'));assert qt.V.shape==(109,64);import build_rl_figures;assert callable(build_rl_figures.learning_and_values);print('IMPORT_AND_LOAD_ONLY_NO_RENDER')"
 result=subprocess.run([str(ROOT/'.venv/bin/python'),'-B','-c',program],cwd=d,env=env,capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 assert not (d/'task2/figures').exists()
 smoke=dict(returncode=result.returncode,stdout=result.stdout.strip(),stderr=result.stderr,source_sha256={p:sha(ROOT/p) for p in code},private_data_absent=True,figures_generated=0)
assert all(sha(ROOT/p)==h for p,h in protected.items())
assert json.loads((HERE/'scientific_body_equivalence.json').read_text())['status']=='PASS'
assert '55 passed' in (HERE/'pytest_output.txt').read_text()
result=dict(status='PASS_AUTHOR_ENGINEERING_GUARD_ONLY',scope='10 RL launchers plus previously guarded final launcher:55 isolated CLI tests;20 real-workspace direct/module help calls under -S -B; public-only import/load_model/renderer import smoke without rendering. No training/evaluation/experiment executed. Original mathematical statements and library functions are AST-equal after only documented CLI/output plumbing exclusions.',source_hashes=records,helper=dict(path='task2/scripts/experiment_cli.py',sha256=sha(ROOT/'task2/scripts/experiment_cli.py')),test_sha256=sha(ROOT/'task2/tests/test_rl_launcher_cli.py'),tests=(HERE/'pytest_output.txt').read_text().strip().splitlines()[-1],scientific_ast_receipt_sha256=sha(HERE/'scientific_body_equivalence.json'),help_commands=commands,public_import_smoke=smoke,protected_files=len(protected),protected_byte_hashes_unchanged=True,historical_run_identity='Original model/metric code_hashes unchanged. Their exact pre-guard launcher bytes remain in original_sources; guard source hashes are engineering revisions, not code claimed to have executed those historical runs.')
(HERE/'validation_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','protected_files','protected_byte_hashes_unchanged','public_import_smoke']},indent=2))
