"""Immutable experiment entry points must stop before loading the experiment stack."""
import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
CASES = [
    ('run_rl.py', ['--phase', 'pilot', '--data', 'missing'], 'development_v1'),
    ('run_rl_followup.py', ['--phase', 'beta', '--model', 'missing'], 'beta_validation_v1'),
    ('resume_rl_rngfix.py', ['--phase', 'double'], 'double_v2_rngfix'),
    ('run_reposition_cost.py', [], 'reposition_cost_validation_v1'),
    ('run_rl_fusion.py', [], 'fusion_validation_v1'),
    ('run_rl_component_ablation.py', [], 'component_ablation_v1'),
    ('run_rl_offset_robustness.py', [], 'offset_robustness_v1'),
    ('confirm_rl_movement.py', [], 'movement_trainseed_confirmation_v1'),
    ('confirm_rl_montecarlo.py', [], 'final_montecarlo_v1'),
    ('diagnose_rl_double.py', [], 'double_v2_rngfix'),
]


def isolated_runner(tmp_path, name):
    runner = tmp_path / 'task2/scripts' / name
    runner.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPTS / name, runner)
    shutil.copyfile(SCRIPTS / 'experiment_cli.py', runner.parent / 'experiment_cli.py')
    return runner


@pytest.mark.parametrize('name,required,default', CASES)
def test_help_without_site_packages_or_data(tmp_path, name, required, default):
    runner = isolated_runner(tmp_path, name)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob('*'))
    result = subprocess.run([sys.executable, '-S', '-B', str(runner), '--help'],
                            capture_output=True, text=True)
    assert result.returncode == 0 and '--output' in result.stdout, result.stderr
    assert not any(word in result.stdout for word in ['TRAIN ', 'REUSE ', 'EVAL '])
    assert before == sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob('*'))


@pytest.mark.parametrize('name,required,default', CASES)
def test_module_help_without_site_packages_or_data(tmp_path, name, required, default):
    isolated_runner(tmp_path, name)
    result = subprocess.run([sys.executable, '-S', '-B', '-m',
                             'task2.scripts.' + Path(name).stem, '--help'],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0 and '--output' in result.stdout, result.stderr
    assert not (tmp_path / 'task2/results').exists()


@pytest.mark.parametrize('name,required,default', CASES)
def test_existing_output_refused_before_experiment_import(tmp_path, name, required, default):
    runner = isolated_runner(tmp_path, name)
    output = tmp_path / 'protected'
    output.mkdir()
    sentinel = output / 'sentinel'
    sentinel.write_bytes(b'preserve exact bytes')
    result = subprocess.run([sys.executable, '-S', '-B', str(runner), *required,
                             '--output', str(output)], capture_output=True, text=True)
    assert result.returncode == 2 and 'Output already exists' in result.stderr
    assert result.stdout == '' and sentinel.read_bytes() == b'preserve exact bytes'
    assert list(output.iterdir()) == [sentinel]
    assert not (tmp_path / 'task2/results').exists()


@pytest.mark.parametrize('name,required,default', CASES)
def test_symlink_output_refused(tmp_path, name, required, default):
    runner = isolated_runner(tmp_path, name)
    output = tmp_path / 'dangling'
    output.symlink_to(tmp_path / 'absent', target_is_directory=True)
    result = subprocess.run([sys.executable, '-S', '-B', str(runner), *required,
                             '--output', str(output)], capture_output=True, text=True)
    assert result.returncode == 2 and 'Output already exists' in result.stderr
    assert not (tmp_path / 'absent').exists()


@pytest.mark.parametrize('name,required,default', CASES)
def test_fresh_argument_parsing_does_not_create_directory(tmp_path, name, required, default):
    # Extract the actual parser with only stdlib names: parsing itself must be read-only.
    module = ast.parse((SCRIPTS / name).read_text())
    parser = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == 'parse_args')
    sys.path.insert(0, str(SCRIPTS))
    try:
        from experiment_cli import fixed_output_args, require_fresh_output
        import argparse
        namespace = dict(Path=Path, TASK=tmp_path/'task2', argparse=argparse,
                         __doc__='test', fixed_output_args=fixed_output_args,
                         require_fresh_output=require_fresh_output)
        exec(compile(ast.Module(body=[parser], type_ignores=[]), str(SCRIPTS/name), 'exec'), namespace)
        output = tmp_path / 'fresh'
        args = namespace['parse_args']([*required, '--output', str(output)])
        assert args.output == output and not output.exists()
    finally:
        sys.path.remove(str(SCRIPTS))
