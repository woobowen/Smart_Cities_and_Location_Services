"""Independent CLI boundary checks in disposable source-only copies.

No experiment is launched. The regular-environment smoke only imports public
plot modules and reads two existing model files in a separate copied layout.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
HEAVY = ['numpy','pandas','scipy','matplotlib','rl_dispatch','rl_extensions',
         'rl_fusion','evolution','dispatch_data']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree_state(root):
    rows = []
    for p in sorted(root.rglob('*')):
        stat = p.lstat()
        content = ('link:'+os.readlink(p) if p.is_symlink() else
                   'dir' if p.is_dir() else sha(p))
        rows.append((str(p.relative_to(root)), content, stat.st_mtime_ns))
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def copy_file(rel, target):
    dst = target/rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/rel, dst)


def main():
    declarations = json.loads((ROOT/'task2/evidence/rl/launcher_guard_01/source_hashes.json').read_text())
    launchers = [r['path'] for r in declarations] + [
        'task2/scripts/run_rl_final.py', 'task2/scripts/run_basic_multiobjective.py']
    helper = 'task2/scripts/experiment_cli.py'
    source_hashes = {rel:sha(ROOT/rel) for rel in launchers+[helper]}
    for row in declarations:
        assert source_hashes[row['path']] == row['guarded_sha256']
        assert sha(ROOT/row['original_snapshot']) == row['original_sha256']
    assert source_hashes[helper] == '3bd3a51d7fc5c3fe4f384e394c3d0f0721902bc77b0e5558c5c3ecf5ab604568'
    old_library = ROOT/'task2/evidence/rl/launcher_guard_01/original_sources/run_rl.py'
    def function(p, name):
        return ast.dump(next(n for n in ast.parse(p.read_text()).body
                             if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
    assert function(old_library,'load_model') == function(ROOT/'task2/scripts/run_rl.py','load_model')
    cases = []
    defaults = {
        'run_reposition_cost.py':'reposition_cost_validation_v1',
        'run_rl_fusion.py':'fusion_validation_v1',
        'run_rl_component_ablation.py':'component_ablation_v1',
        'run_rl_offset_robustness.py':'offset_robustness_v1',
        'confirm_rl_movement.py':'movement_trainseed_confirmation_v1',
        'confirm_rl_montecarlo.py':'final_montecarlo_v1',
        'diagnose_rl_double.py':'double_v2_rngfix',
        'run_rl_final.py':'final_v1', 'resume_rl_rngfix.py':'sensitivity_v2_rngfix',
    }
    with tempfile.TemporaryDirectory(prefix='dispatch-cli-independent-') as temporary:
        clone = Path(temporary)/'clone'
        for rel in launchers+[helper]: copy_file(rel,clone)
        for target in defaults.values():
            (clone/'task2/results/rl'/target).mkdir(parents=True,exist_ok=True)
        (clone/'task2/results/evolution/basic').mkdir(parents=True)
        (clone/'task2/results/rl/existing_run').mkdir()
        existing = clone/'fixture_existing_directory';existing.mkdir()
        regular_file = clone/'fixture_existing_file';regular_file.write_text('immutable sentinel')
        dangling = clone/'fixture_dangling_link';dangling.symlink_to(clone/'absent_destination')
        expected = tree_state(clone)
        env = os.environ.copy();env.pop('PYTHONPATH',None)
        env['PYTHONDONTWRITEBYTECODE']='1'
        for rel in launchers:
            name=Path(rel).name
            required = (['--phase','pilot','--data',str(clone/'no_data')] if name=='run_rl.py' else
                        ['--phase','beta','--model',str(clone/'no_model')] if name=='run_rl_followup.py' else
                        ['--phase','sensitivity'] if name=='resume_rl_rngfix.py' else [])
            default_args = required + (['--run','existing_run'] if name in ['run_rl.py','run_rl_followup.py'] else [])
            variants=[('help',['--help'],0),('short-help',['-h'],0),
                      ('existing-directory',required+['--output',str(existing)],2),
                      ('existing-file',required+['--output',str(regular_file)],2),
                      ('dangling-symlink',required+['--output',str(dangling)],2),
                      ('unknown-option',required+['--output',str(clone/'unused_fresh'),'--not-a-real-option'],2),
                      ('existing-default-or-run-alias',default_args,2)]
            for mode in ['direct','module']:
                entry=[str(clone/rel)] if mode=='direct' else ['-m',rel[:-3].replace('/','.')]
                for label,args,code in variants:
                    cmd=[sys.executable,'-S','-B','-X','importtime',*entry,*args]
                    p=subprocess.run(cmd,cwd=clone,env=env,text=True,capture_output=True,timeout=20)
                    loaded=[line.rsplit('|',1)[-1].strip() for line in p.stderr.splitlines()
                            if line.startswith('import time:') and '|' in line]
                    heavy=[m for m in loaded if any(m==h or m.startswith(h+'.') for h in HEAVY)]
                    unchanged=tree_state(clone)==expected
                    assert p.returncode==code,(name,mode,label,p.returncode,p.stderr[-1600:])
                    assert not heavy,(name,mode,label,heavy)
                    assert unchanged,(name,mode,label,'filesystem mutation')
                    assert 'Traceback' not in p.stderr
                    diagnostic=[x for x in p.stderr.splitlines() if not x.startswith('import time:')]
                    assert ('usage:' in p.stdout if code==0 else any('error:' in x for x in diagnostic))
                    cases.append(dict(launcher=rel,mode=mode,case=label,returncode=p.returncode,
                        command=cmd,source_only_fixture_unchanged=unchanged,experiment_imports=heavy,
                        imported_module_count=len(loaded),stderr_sha256=hashlib.sha256(p.stderr.encode()).hexdigest(),
                        parser_diagnostic=diagnostic[-3:]))
    # Separate regular interpreter, no raw CSVs/episodes or experiment results.
    with tempfile.TemporaryDirectory(prefix='dispatch-import-independent-') as temporary:
        base=Path(temporary);clone=base/'clone';cache=base/'matplotlib-cache';cache.mkdir()
        files=[helper,'task2/scripts/run_rl.py',
               'task2/scripts/build_figures.py','task2/scripts/build_evolution_figures.py','task2/scripts/build_rl_figures.py',
               'task2/src/rl_dispatch.py','task2/src/evolution.py','task2/src/front_metrics.py',
               'templates/latex/common/p2_cloud_sorbet_colors.tex']
        models=['task2/results/rl/final_v1/q_f60','task2/results/rl/final_v1/double_beta1']
        for rel in files:copy_file(rel,clone)
        for folder in models:
            for filename in ['model.npz','manifest.json']:copy_file(folder+'/'+filename,clone)
        before=tree_state(clone)
        smoke_code=r'''
import sys,json
from pathlib import Path
root=Path.cwd()
sys.path.insert(0,str(root/'task2/scripts'))
sys.path.insert(0,str(root/'task2/src'))
blocked={'train_q_km','run_episode','sample_episode','run_nsga','fit','evaluate','main','save','prepare_aggregate_inputs'}
def profile(frame,event,arg):
    if event=='call' and frame.f_code.co_filename.startswith(str(root/'task2')) and frame.f_code.co_name in blocked:
        raise AssertionError('Experiment or rendering function called: '+frame.f_code.co_name)
sys.setprofile(profile)
import run_rl
from task2.scripts.run_rl import load_model as package_load
import numpy as np
rows=[]
for folder in ['q_f60','double_beta1']:
    p=root/'task2/results/rl/final_v1'/folder
    q,meta=run_rl.load_model(p)
    q2,_=package_load(p)
    keys=['V','NV','A','B','NA','NB'] if meta['double'] else ['V','NV','Q','N']
    with np.load(p/'model.npz') as raw:
        assert all(np.array_equal(getattr(q,k),raw[k]) and np.array_equal(getattr(q2,k),raw[k]) for k in keys)
    rows.append({'model':folder,'double':meta['double'],'arrays_exact':keys})
import build_figures,build_evolution_figures,build_rl_figures
import matplotlib.pyplot as plt
assert plt.get_fignums()==[]
assert not (root/'task2/figures').exists()
sys.setprofile(None)
print(json.dumps({'models':rows,'public_plot_modules':['build_figures','build_evolution_figures','build_rl_figures'],'figures_created':0,'experiment_calls':0}))
'''
        env=os.environ.copy();env.pop('PYTHONPATH',None)
        env.update(PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(cache),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        p=subprocess.run([sys.executable,'-B','-c',smoke_code],cwd=clone,env=env,text=True,capture_output=True,timeout=40)
        assert p.returncode==0,p.stderr
        assert tree_state(clone)==before,'public-only import/read smoke changed copied inputs'
        smoke=json.loads(p.stdout)
        smoke['source_only_fixture_unchanged']=True
        smoke['matplotlib_cache_scope']='Temporary cache outside copied source/model tree; removed with fixture'
    assert all(sha(ROOT/p)==h for p,h in source_hashes.items()),'sources changed during audit'
    result=dict(actual_utc=datetime.now(timezone.utc).isoformat(),reviewer='/root/research_data',
                status='PASS_INDEPENDENT_CLI_AND_IMPORT_SCOPE',source_sha256=source_hashes,
                cases_count=len(cases),cases=cases,load_model_ast_equal_to_original=True,smoke=smoke,
                mathematical_equivalence_scope='Independently checked load_model AST only. Broader launcher-body AST equivalence belongs to the explicitly attributed EB/EA author receipts, not a new full mathematical audit.',
                limits='No training/evaluation, new statistical samples, raw-data generation, model overwrite, figure rendering, or report rebuild. Temporary copies only; old run source identities and previous numerical/PDF reviews remain unchanged.')
    (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:result[k] for k in ['status','cases_count','load_model_ast_equal_to_original','smoke']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
