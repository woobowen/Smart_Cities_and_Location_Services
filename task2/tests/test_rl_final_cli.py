"""CLI guard regression: help/existing-output commands must not evaluate or write."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'task2/scripts/run_rl_final.py'

def load_runner():
    spec=importlib.util.spec_from_file_location('final_cli_guard',SCRIPT)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_help_does_not_import_experiment_stack_or_create_outputs(tmp_path):
    runner=tmp_path/'task2/scripts/run_rl_final.py';runner.parent.mkdir(parents=True);runner.write_bytes(SCRIPT.read_bytes())
    p=subprocess.run([sys.executable,str(runner),'--help'],capture_output=True,text=True)
    assert p.returncode==0 and '--output' in p.stdout
    assert not (tmp_path/'task2/results').exists()
    assert not any(token in p.stdout for token in ['REUSE','TRAIN','EVAL'])

def test_existing_output_refused_without_reading_inputs(tmp_path):
    target=tmp_path/'existing';target.mkdir();sentinel=target/'do_not_touch.txt';sentinel.write_text('retained')
    p=subprocess.run([sys.executable,str(SCRIPT),'--output',str(target)],capture_output=True,text=True)
    assert p.returncode==2 and 'Output already exists' in p.stderr
    assert sentinel.read_text()=='retained' and list(target.iterdir())==[sentinel]
    assert not any(token in p.stdout for token in ['REUSE','TRAIN','EVAL'])

def test_fresh_output_is_explicit_and_not_created_by_parsing(tmp_path):
    target=tmp_path/'new';args=load_runner().parse_args(['--output',str(target)])
    assert args.output==target and not target.exists()

def test_existing_default_canonical_run_refused():
    p=subprocess.run([sys.executable,str(SCRIPT)],capture_output=True,text=True)
    assert p.returncode==2 and 'Output already exists' in p.stderr
    assert not p.stdout

def test_symlink_output_refused(tmp_path):
    target=tmp_path/'target';target.mkdir();link=tmp_path/'link';link.symlink_to(target,target_is_directory=True)
    with pytest.raises(SystemExit) as error:load_runner().parse_args(['--output',str(link)])
    assert error.value.code==2 and list(target.iterdir())==[]
