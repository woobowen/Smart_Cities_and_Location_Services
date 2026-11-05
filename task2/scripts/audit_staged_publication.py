"""Check the actual Git index for exact local-data exclusions and structural risks.

This bounded scan is one check; independent content review remains separate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    paths = [x.decode() for x in subprocess.check_output(
        ['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).split(b'\0') if x]
    inventory = json.loads((ROOT / 'task2/evidence/research_data/local_only_manifest_current.json').read_text())
    private = {r['path'] for r in inventory['files']}
    forbidden = sorted(private & set(paths))
    findings = []
    rows = []
    secrets = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{32,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
    for name in paths:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            findings.append(dict(path=name, reason='missing/non-file/symlink; inspect explicitly'))
            continue
        if path.suffix.lower() in {'.ttf', '.otf', '.woff', '.woff2'}:
            findings.append(dict(path=name, reason='font binary'))
        blob = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
        if len(blob) >= 100 * 1024 * 1024:
            findings.append(dict(path=name, reason='GitHub ordinary-file size limit'))
        if blob != path.read_bytes():
            findings.append(dict(path=name, reason='working file differs from staged blob'))
        if secrets.search(blob):
            findings.append(dict(path=name, reason='high-confidence secret signature; no value printed'))
        if any(part in {'.venv', '__pycache__', 'build', '.ipynb_checkpoints'} for part in path.relative_to(ROOT).parts):
            findings.append(dict(path=name, reason='environment/cache/build directory'))
        rows.append(dict(path=name, bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest()))
    output = ROOT / 'task2/evidence/publication/staged_structural_audit.json'
    result = dict(status='PASS_STRUCTURAL_SCOPE' if not forbidden and not findings else 'FAIL',
                  checked_staged_files=len(paths), bytes=sum(r['bytes'] for r in rows),
                  local_only_intersection=forbidden, findings=findings, files=rows,
                  scope='Exact inventory intersection, staged/working equality, symlink/font/cache/size and high-confidence secret signatures. Independent semantic record-leak review is separate. This receipt itself is produced after the scanned index snapshot.')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))
    if forbidden or findings:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
