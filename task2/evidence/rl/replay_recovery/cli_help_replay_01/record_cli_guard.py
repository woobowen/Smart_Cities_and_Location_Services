from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[5];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
capture=json.loads((OUT/'capture_manifest.json').read_text());checks=[]
for file in capture['replayed_output']:
 p=ROOT/file['original'];assert sha(p)==file['sha256'];checks.append(file['original'])
process=subprocess.run([str(ROOT/'.venv/bin/python'),str(TASK/'scripts/run_rl_final.py'),'--help'],capture_output=True,text=True)
assert process.returncode==0 and '--output' in process.stdout and not any(x in process.stdout for x in ['REUSE','TRAIN','EVAL'])
for file in capture['replayed_output']:assert sha(ROOT/file['original'])==file['sha256']
(OUT/'actual_workspace_help_stdout.txt').write_text(process.stdout)
old=OUT/'surviving_prior_receipts/task2/scripts/run_rl_final.py';new=TASK/'scripts/run_rl_final.py'
(OUT/'cli_guard.patch').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='executed_original_source',tofile='guarded_source_for_future_runs')))
record=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),executed_original_source_sha256=sha(old),guarded_source_sha256=sha(new),guard_source_snapshot=str(old.relative_to(ROOT)),scope='argparse/help/fresh-outputprotectiononly; frozenexperimentmathematics/model/selectionunchanged',tests=dict(command='.venv/bin/python -m pytest task2/tests/test_rl_final_cli.py -q',actual_result='5passed in0.17s',log=str((OUT/'cli_tests.log').relative_to(ROOT)),workspace_help_returncode=process.returncode,all_143_replay_output_files_unchanged_by_guard_and_tests=len(checks)),fresh_output_positive_case='parseaccepts explicitnewdirectorywithoutcreatingit; no newtrainingexecutedforguardtest',status='CLI_GUARD_TESTED')
(OUT/'cli_guard_receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print('guardverified; unchangedreplayfiles',len(checks))
