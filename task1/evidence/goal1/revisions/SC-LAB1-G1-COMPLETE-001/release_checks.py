"""Bounded publication checks for this authorized Goal revision; not scientific acceptance."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

from task1.workflow.io import ROOT, DATA, digest, write_json

REV = ROOT / 'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001'
ANCHOR = '7e6cd4082c2cdad2452fa5a1006e99dcfb050d17'
ALLOWED_CURRENT = {'task1/evidence/goal1/' + name for name in
                   ('requirements.json', 'acceptance.json', 'REVIEW_PACKET.md')}
paths = set(subprocess.check_output(['git', 'diff', '--name-only', ANCHOR], cwd=ROOT, text=True).splitlines())
paths.update(str(p.relative_to(ROOT)) for p in REV.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
patterns = {
    'api_token': re.compile(r'(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{32,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'credential_url': re.compile(r'https?://[^\s/@:]+:[^\s/@]+@'),
}
secrets, large, symlinks, broken, portable, absolute_evidence = [], [], [], [], [], []
for name in sorted(paths):
    p = ROOT / name
    if not p.exists():
        continue
    if p.is_symlink():
        symlinks.append(name)
        continue
    if p.stat().st_size > 50 * 1024 * 1024:
        large.append({'path': name, 'bytes': p.stat().st_size})
    try:
        contents = p.read_text()
    except (UnicodeError, OSError):
        continue
    for label, rx in patterns.items():
        if rx.search(contents):
            secrets.append({'path': name, 'type': label})  # Never print credential content.
    if any(prefix in contents for prefix in ('/home/', '/tmp/', '/mnt/data/')):
        group = portable if name.startswith(('task1/workflow/', 'task1/scripts/', 'task1/notebooks/')) else absolute_evidence
        group.append(name)
    if p.suffix == '.md':
        for match in re.finditer(r'(?<!!)\[[^\]\n]*\]\(([^\n]+?)\)', contents):
            dest = match.group(1).split(' "')[0].strip('<>')
            if re.match(r'^(?:https?://|mailto:|app:|#)', dest):
                continue
            dest = unquote(dest.split('#')[0])
            if dest and not dest.startswith('/') and not (p.parent / dest).exists():
                broken.append({'file': name, 'link': dest})
protected = json.loads((REV / 'initial_protected_hashes.json').read_text())
changes, unauthorized = [], []
for name, expected in protected.items():
    p = ROOT / name
    actual = digest(p) if p.is_file() else None
    if actual != expected:
        row = {'path': name, 'before_sha256': expected, 'after_sha256': actual,
               'explicitly_authorized_current_entry': name in ALLOWED_CURRENT}
        changes.append(row)
        if name not in ALLOWED_CURRENT:
            unauthorized.append(row)
nb_errors = []
for p in (ROOT / 'task1/notebooks').glob('*.ipynb'):
    nb = json.loads(p.read_text())
    for i, cell in enumerate(nb['cells']):
        if any(o.get('output_type') == 'error' for o in cell.get('outputs', [])):
            nb_errors.append({'path': str(p.relative_to(ROOT)), 'cell': i})
report = {
    'classification': 'PREPUBLICATION_ENGINEERING_CHECK',
    'command': 'PYTHONPATH=. .venv/bin/python ' + str(Path(__file__).relative_to(ROOT)),
    'checked_files': len(paths), 'secrets_pattern_findings': secrets,
    'over_50MiB_files': large, 'symlinks': symlinks, 'broken_local_links': broken,
    'absolute_paths_in_reproduction_entrypoints': portable,
    'absolute_paths_in_evidence': absolute_evidence,
    'absolute_path_note': 'Required cwd/commands and archived probes retain historical paths; executable reproduction inputs use project-relative paths.',
    'protected_total': len(protected), 'authorized_protected_changes': changes,
    'unauthorized_protected_changes': unauthorized, 'notebook_errors': nb_errors,
    'original_material_git_byte_audit': 'a_scope/release_scope_check.json: 150 additional original material/template/plot/history files matched initial Git bytes',
    'raw_sha256': digest(DATA),
    'source_bundle_check': 'sync_sources.py --check: recorded separately; exactly 11 active byte-equal files',
}
report['status'] = 'PASS' if not any((secrets, large, symlinks, broken, portable, unauthorized, nb_errors)) else 'FAIL'
write_json(REV / 'prepublication_check.json', report)
print(json.dumps({k: v for k, v in report.items() if k not in ('absolute_paths_in_evidence', 'authorized_protected_changes')}, ensure_ascii=False, indent=2))
raise SystemExit(0 if report['status'] == 'PASS' else 1)
