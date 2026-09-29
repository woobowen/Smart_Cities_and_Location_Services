"""Scan only this task's authorized publication candidates; never stage user ZIPs."""
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = '89371f6597f92f7dac9abf61f6f6b18e29ed76cc'
USER_FILES = {'Experiment_Report_完整重构_源文件.zip', 'SC-LAB1-G1-CLOSURE-002_HANDOFF.zip',
              'SC-LAB1-G1-COMPLETE-001_HANDOFF.zip'}
EXISTING_ALLOWED = {
    'AGENTS.md', 'README.md', 'releases/chatgpt-project-sources/AGENTS.md',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',
    'evidence/infrastructure/chatgpt-project-source-sync/sources.json',
    'evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md',
    'evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md',
    'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md',
    'task1/README.md', 'task1/evidence/goal3/REVIEW_PACKET.md',
    'task1/docs/goal3/TECHNICAL_HANDOFF.md', 'task1/reports/README.md',
}


def git_paths(*args):
    return {p for p in subprocess.check_output(['git', *args, '-z'], cwd=ROOT).decode().split('\0') if p}


def main():
    paths = git_paths('diff', '--name-only', BASE)
    paths |= git_paths('ls-files', '--others', '--exclude-standard') - USER_FILES
    audit_path = (OUT / 'publication-audit.json').relative_to(ROOT).as_posix()
    paths.add(audit_path)
    allowed_prefixes = [OUT.relative_to(ROOT).as_posix() + '/',
                        'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review/']
    unauthorized = [p for p in paths if p not in EXISTING_ALLOWED and not any(p.startswith(x) for x in allowed_prefixes)]
    assert not unauthorized, unauthorized
    rows, issues, absolute = [], [], []
    patterns = [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'sk-[A-Za-z0-9_-]{32,}']

    def inspect(path, data):
        if any(re.search(rule, data) for rule in patterns):
            issues.append(dict(path=path, issue='potential_secret'))
        if re.search(rb'/home/[^/\s]+/|/mnt/[a-z]/|/tmp/[A-Za-z]', data):
            absolute.append(path)

    for relative in sorted(paths):
        if relative == audit_path:
            continue
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            issues.append(dict(path=relative, issue='nonregular_or_deleted'))
            continue
        data = path.read_bytes()
        if len(data) >= 100 * 1024 * 1024:
            issues.append(dict(path=relative, issue='over_github_normal_limit'))
        if path.suffix.lower() in {'.ttf', '.otf', '.ttc', '.woff', '.woff2'}:
            issues.append(dict(path=relative, issue='font_binary'))
        if path.suffix.lower() == '.zip':
            with zipfile.ZipFile(path) as archive:
                for member in archive.infolist():
                    if not member.is_dir():
                        inspect(relative + '!' + member.filename, archive.read(member))
        else:
            inspect(relative, data)
        rows.append(dict(path=relative, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    result = dict(baseline=BASE, files=rows, publication_paths=sorted(paths), issues=issues,
                  absolute_path_candidates=sorted(absolute),
                  absolute_path_scope='Task evidence/probes record observed cwd or unique temporary paths; inherited README command examples also use replaceable /tmp output paths. Active synchronization behavior keeps repository-relative paths.',
                  preserved_untracked_user_files=sorted(USER_FILES), self_hash_exclusion=audit_path,
                  pass_all=not issues)
    (ROOT / audit_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(files=len(paths), issues=issues, absolute_candidates=len(absolute), pass_all=not issues)))
    raise SystemExit(bool(issues))


if __name__ == '__main__':
    main()
