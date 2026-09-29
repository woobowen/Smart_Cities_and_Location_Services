"""Inspect precisely this task's changed files before staging; do not stage user ZIPs."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
USER_ZIPS = {'Experiment_Report_完整重构_源文件.zip', 'SC-LAB1-G1-CLOSURE-002_HANDOFF.zip',
             'SC-LAB1-G1-COMPLETE-001_HANDOFF.zip'}


def git_paths(*args):
    return {p for p in subprocess.check_output(['git', *args, '-z'], cwd=ROOT).decode().split('\0') if p}


def main():
    paths = git_paths('diff', '--name-only', '4483f520eabb5358d1f35cf5c33a81d3b01e47e0')
    paths |= git_paths('ls-files', '--others', '--exclude-standard') - USER_ZIPS
    rules = {
        'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'github_token': rb'gh[pousr]_[A-Za-z0-9]{30,}',
        'provider_secret': rb'sk-[A-Za-z0-9_-]{32,}',
    }
    findings, large, fonts, absolute, checked = [], [], [], [], []

    def inspect(name, content):
        for rule, pattern in rules.items():
            if re.search(pattern, content):
                findings.append({'path': name, 'rule': rule})  # Never print a potential secret.
        if re.search(rb'/home/[^/\s]+/|/mnt/[a-z]/|/tmp/[A-Za-z]', content):
            absolute.append(name)

    for path in sorted(paths):
        p = ROOT / path
        if p in (OUT / 'publication-audit.json', OUT / 'staging-paths.json'):
            continue  # Generated audit/index do not hash themselves.
        if not p.is_file():
            raise ValueError(f'Deleted or nonregular changed path: {path}')
        if p.is_symlink():
            raise ValueError(f'Symlink changed path: {path}')
        content = p.read_bytes()
        if len(content) >= 100 * 1024 * 1024:
            large.append(path)
        if p.suffix.lower() in ('.ttf', '.otf', '.woff', '.woff2', '.ttc'):
            fonts.append(path)
        if p.suffix.lower() not in ('.pdf', '.png', '.jpg', '.zip', '.pptx'):
            inspect(path, content)
        if p.suffix.lower() == '.zip':
            with zipfile.ZipFile(p) as archive:
                for member in archive.infolist():
                    if member.is_dir():
                        continue
                    suffix = Path(member.filename).suffix.lower()
                    if suffix in ('.ttf', '.otf', '.woff', '.woff2', '.ttc'):
                        fonts.append(path + '!' + member.filename)
                    if suffix in ('.py', '.sh', '.md', '.json', '.yaml', '.yml', '.toml', '.tex', '.txt', '.ipynb', '.env'):
                        inspect(path + '!' + member.filename, archive.read(member))
        checked.append({'path': path, 'size': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    result = dict(files=checked, high_confidence_secret_matches=findings, oversize_files=large,
                  font_binaries=fonts, absolute_path_candidates=sorted(set(absolute)),
                  absolute_path_policy='Evidence command provenance and immutable supplied/history text may contain actual original paths; active runtime must use repository-relative paths.',
                  preserved_untracked_user_zips=sorted(USER_ZIPS),
                  self_hash_exclusions=['publication-audit.json', 'staging-paths.json'],
                  pass_security_size_fonts=not (findings or large or fonts))
    (OUT / 'publication-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'staging-paths.json').write_text(json.dumps(sorted(paths), ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'files': len(paths), 'secret_matches': len(findings), 'oversize': large,
                      'fonts': fonts, 'absolute_path_candidates': len(set(absolute)),
                      'pass_security_size_fonts': result['pass_security_size_fonts']}, ensure_ascii=False))
    raise SystemExit(not result['pass_security_size_fonts'])


if __name__ == '__main__':
    main()
