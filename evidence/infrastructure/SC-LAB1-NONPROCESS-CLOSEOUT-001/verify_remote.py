"""Read fixed GitHub bytes for the approved source set and this closeout's changes."""
import argparse
import hashlib
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
BASE = '89371f6597f92f7dac9abf61f6f6b18e29ed76cc'
REPOSITORY = 'woobowen/Smart_Cities_and_Location_Services'


def git_blob(commit, path):
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)


def remote_head():
    attempts = []
    for index in range(3):
        proc = subprocess.run(['git', 'ls-remote', 'origin', 'refs/heads/main'],
                              cwd=ROOT, text=True, capture_output=True, timeout=45)
        attempts.append(dict(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        if proc.returncode == 0:
            return proc.stdout.split()[0], attempts
        if index < 2:
            time.sleep(2)
    return None, attempts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = dict(repository=f'https://github.com/{REPOSITORY}', branch='main', commit=args.commit,
                  baseline=BASE, started_at_utc=datetime.now(timezone.utc).isoformat(),
                  method='Actual HTTPS fixed-commit response bytes compared with git blob SHA256; no TLS/credential changes')

    def save():
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')

    before, attempts = remote_head()
    result.update(actual_remote_before=before, remote_before_attempts=attempts)
    if before != args.commit:
        result.update(pass_all=False, error='Remote unavailable or advanced; retain work and review divergence')
        save()
        raise SystemExit(1)
    declaration = json.loads(git_blob(args.commit, 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'))
    paths = {r['active_path'] for r in declaration['sources']}
    paths |= {'releases/chatgpt-project-sources/' + r['canonical_name'] for r in declaration['sources']}
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=ACMRT', '-z', BASE, args.commit], cwd=ROOT)
    paths |= {p for p in changed.decode().split('\0') if p}

    def fetch(path):
        expected = hashlib.sha256(git_blob(args.commit, path)).hexdigest()
        url = f'https://raw.githubusercontent.com/{REPOSITORY}/{args.commit}/{quote(path, safe="/")}'
        errors = []
        for attempt in range(3):
            try:
                total, hasher = 0, hashlib.sha256()
                with urlopen(url, timeout=45) as response:
                    while chunk := response.read(1024 * 1024):
                        total += len(chunk)
                        hasher.update(chunk)
                observed = hasher.hexdigest()
                return dict(path=path, bytes=total, expected_blob_sha256=expected,
                            actual_remote_sha256=observed, match=expected == observed, retries=errors)
            except Exception as exc:
                errors.append(f'{type(exc).__name__}: {exc}')
                if attempt < 2:
                    time.sleep(2)
        return dict(path=path, match=False, errors=errors)

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(fetch, sorted(paths)))
    result.update(rows=rows, verified_files=len(rows), source_set_count=len(declaration['sources']),
                  raw_hashes_all_match=all(r['match'] for r in rows), pass_all=False)
    save()  # Preserve completed byte evidence even if the final reference query fails.
    after, attempts = remote_head()
    result.update(actual_remote_after=after, remote_after_attempts=attempts,
                  local_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  origin_main=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
                  completed_at_utc=datetime.now(timezone.utc).isoformat())
    result['pass_all'] = (result['raw_hashes_all_match'] and after == args.commit ==
                          result['local_head'] == result['origin_main'])
    save()
    print(json.dumps({k: v for k, v in result.items() if k not in {'rows', 'remote_before_attempts', 'remote_after_attempts'}}, ensure_ascii=False, indent=2))
    raise SystemExit(not result['pass_all'])


if __name__ == '__main__':
    main()
