"""One-time closeout launcher: preserve actual exit status independently of a tool session."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent


def run(name):
    isolated = name == 'isolated_system_retry'
    if name not in {'repository_basic_retry', 'isolated_system_retry'}:
        raise ValueError('Unknown authorized retry')
    cwd = Path('/tmp/sc-lab1-closeout-package') if isolated else ROOT
    notebook = '任务3_LLM辅助评估清洗_完成版.ipynb' if isolated else '作业1轨迹数据预处理_完成版.ipynb'
    work = Path('/tmp') / ('sc-lab1-closeout-' + name.replace('_', '-'))
    evidence = BASE / 'notebooks' / name
    command = [str(ROOT / '.venv/bin/python'), '-m', 'task1.goal3.execute_notebook',
               str(cwd / 'task1/notebooks/final' / notebook), '--cwd', str(cwd),
               '--work', str(work), '--evidence', str(evidence)]
    record = {'started_at': datetime.now(timezone.utc).isoformat(), 'command': command,
              'status': 'RUNNING', 'same_authorized_entrypoint': True}
    receipt = BASE / (name + '_supervisor.json')
    receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    import os
    environment = os.environ.copy()
    if isolated:
        for key, suffix in [('MPLCONFIGDIR', 'mpl'), ('JUPYTER_CONFIG_DIR', 'jupyter'), ('IPYTHONDIR', 'ipython')]:
            environment[key] = str(work) + '-' + suffix
    with (BASE / (name + '_output.txt')).open('wb') as output:
        result = subprocess.run(command, cwd=ROOT, env=environment, stdout=output, stderr=subprocess.STDOUT)
    record.update(finished_at=datetime.now(timezone.utc).isoformat(), exit_code=result.returncode,
                  status='EXITED', full_success_not_inferred_from_exit_code=True)
    receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    run(sys.argv[1])
