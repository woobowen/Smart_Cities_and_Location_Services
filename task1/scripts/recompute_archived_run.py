"""Recompute a saved partial LIVE run using its recorded, committed source.

Only the repository's tracked workflow/config paths are restored. No checkout,
history change, model call, account access or arbitrary model command is involved.
The old source is needed because later controller fixes correctly invalidate a
normal current-code replay. Original run artifacts remain read-only inputs.
"""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from task1.workflow.io import DATA,EVIDENCE,read_json,digest,bound_path


def recompute_archived(run_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,90}',run_id):raise ValueError('ILLEGAL_RUN_ID')
    source=bound_path(EVIDENCE/'runs',run_id)
    manifest=read_json(source/'manifest.json');sha=manifest['code_sha']
    if not re.fullmatch(r'[0-9a-f]{40}',sha):raise ValueError('INVALID_COMMIT')
    # Explicitly enumerate the same task-only source files, excluding unrelated
    # repository files, execution entry points supplied by a model, and secrets.
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',sha,'--','task1/workflow',
                                   'task1/config/goal1.json','task1/config/pilot.json'],cwd=ROOT,text=True).splitlines()
    if not paths:raise ValueError('ARCHIVED_SOURCE_MISSING')
    with tempfile.TemporaryDirectory(prefix='sc-g1-recompute-') as tmp:
        root=Path(tmp)
        for name in paths:
            if not (name.endswith('.py') or name.endswith('.json')):raise ValueError('UNEXPECTED_SOURCE_MEMBER')
            target=bound_path(root,name);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(subprocess.check_output(['git','show',sha+':'+name],cwd=ROOT))
        for path,expected in manifest['source_hashes'].items():
            if digest(bound_path(root,path))!=expected:raise ValueError('ARCHIVED_CODE_HASH_MISMATCH')
        raw_target=root/DATA.relative_to(ROOT);raw_target.parent.mkdir(parents=True,exist_ok=True)
        raw_target.symlink_to(DATA)  # The archived numeric tools only read DATA.
        shutil.copytree(source,root/'task1/evidence/goal1/runs'/run_id)
        command=[sys.executable,'-c',
                 'import json,sys; from task1.workflow.recompute import recompute_run; print(json.dumps(recompute_run(sys.argv[1]),ensure_ascii=False))',run_id]
        result=subprocess.run(command,cwd=root,text=True,capture_output=True,timeout=60,check=True)
        output=json.loads(result.stdout)
    output['restoration']='Tracked workflow/config from existing code_sha; current workspace not checked out or changed'
    output['scope']='Only saved successful tool actions. This partial run has source_evidence only; no completed A/B/C feedback loop.'
    output['archived_source_verified']=True
    return output


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python task1/scripts/recompute_archived_run.py RUN_ID')
    print(json.dumps(recompute_archived(sys.argv[1]),ensure_ascii=False,indent=2))
