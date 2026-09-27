"""Check the authorized closeout diff; print only categories for possible secrets."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone

from task1.goal3.package import PERSONAL_PATH, SECRET_PATTERNS

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
ANCHOR = '1a5e26b43189aef64a46f8986b3cc442fa50d2c5'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    changed = git('diff', '--name-only', '-z', ANCHOR).decode().split('\0')
    untracked = git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')
    paths = sorted({p for p in changed + untracked if p.startswith('task1/')
                    and p != str((BASE / 'PREFLIGHT.json').relative_to(ROOT))})
    findings = []; absolute = []; sizes = []; notebook_states = []
    for name in paths:
        path = ROOT / name
        if not path.is_file():
            findings.append({'path': name, 'kind': 'DELETED_OR_MISSING'}); continue
        size = path.stat().st_size
        sizes.append({'path': name, 'bytes': size})
        if size >= 100 * 1024 * 1024:
            findings.append({'path': name, 'kind': 'GITHUB_LARGE_FILE'})
        if path.suffix.lower() in {'.ttf', '.otf', '.woff', '.woff2', '.pem', '.key'}:
            findings.append({'path': name, 'kind': 'UNEXPECTED_FONT_OR_PRIVATE_KEY_FILE'})
        if path.suffix.lower() not in {'.py','.md','.json','.jsonl','.ipynb','.tex','.bib','.txt','.xml','.csv','.svg','.drawio','.yaml','.yml','.toml'}:
            continue
        text = path.read_text(errors='replace')
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append({'path': name, 'kind': 'POSSIBLE_SECRET_REQUIRES_REVIEW'})
        if PERSONAL_PATH.search(text):
            kind = ('RECORDED_EXECUTION_PROVENANCE' if name.startswith('task1/evidence/')
                    else 'UNEXPECTED_PERSONAL_PATH')
            absolute.append({'path': name, 'classification': kind})
            if kind == 'UNEXPECTED_PERSONAL_PATH': findings.append({'path': name, 'kind': kind})
        if name.startswith('task1/notebooks/final/') and path.suffix == '.ipynb':
            notebook = json.loads(text)
            cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
            clean = all(not c.get('outputs') and c.get('execution_count') is None for c in cells)
            notebook_states.append({'path': name, 'clean_generated_source': clean,
                'code_cells': len(cells), 'executed_copies_location': str((BASE/'notebooks').relative_to(ROOT))})
            if not clean: findings.append({'path': name, 'kind': 'UNEXPECTED_FINAL_NOTEBOOK_OUTPUT'})
    startup = json.loads((BASE/'startup.json').read_text())
    protected = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h
                 for p, h in startup['protected_files'].items()}
    if not all(protected.values()): findings.append({'kind':'PROTECTED_FILE_CHANGED'})
    global_changes = [p for p in changed if p and not p.startswith('task1/')]
    if global_changes: findings.append({'kind':'OUTSIDE_TASK_CHANGE','paths':global_changes})
    forbidden_history_changes = [p for p in paths if p.startswith(('task1/evidence/goal1/', 'task1/evidence/goal2/', 'task1/evidence/goal3/runs/', 'task1/workflow/'))]
    if forbidden_history_changes: findings.append({'kind':'FROZEN_RESEARCH_OR_HISTORY_CHANGED','paths':forbidden_history_changes})
    result = {'at':datetime.now(timezone.utc).isoformat(),'status':'PASS' if not findings else 'REVIEW_REQUIRED',
        'scope':'All current tracked changes since the handover anchor plus nonignored new task1 files; ZIP member security is checked independently by C.',
        'checked_file_count':len(paths),'findings':findings,'protected_files_equal_startup':protected,
        'personal_absolute_paths':absolute,'absolute_path_boundary':'Recorded local interpreter/cwd/work provenance remains in internal execution evidence. Final runtime Notebook/dependencies and ZIP are separately checked for portability.',
        'largest_files':sorted(sizes,key=lambda r:r['bytes'],reverse=True)[:12],
        'final_notebook_output_policy':notebook_states,'unrelated_original_untracked_preserved':startup['initial_untracked'],
        'outside_task_changes':global_changes,'new_installs':[],'persistent_environment_changes':[],
        'new_record_model_calls':0,'teacher_submission_performed':False}
    (BASE/'PREFLIGHT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','checked_file_count','findings','outside_task_changes']},ensure_ascii=False))
    if findings: raise SystemExit(1)


if __name__ == '__main__':
    main()
