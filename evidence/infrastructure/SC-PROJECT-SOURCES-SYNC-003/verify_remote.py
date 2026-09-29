"""Fetch actual fixed-commit raw bytes after publication, without using tracking-cache blobs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REPO = 'woobowen/Smart_Cities_and_Location_Services'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    actual = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=ROOT, text=True).split()[0]
    if actual != args.commit:
        raise SystemExit(f'Remote main advanced or differs: {actual}')
    data = json.loads((ROOT / 'evidence/infrastructure/chatgpt-project-source-sync/sources.json').read_text())
    paths = {r['active_path'] for r in data['sources']}
    paths |= {'releases/chatgpt-project-sources/' + r['canonical_name'] for r in data['sources']}
    # Every path changed by this delivery is read from GitHub, including source, tests,
    # PDF/ZIP, reports, navigation and evidence. Historical unchanged blobs need no reread.
    changed = subprocess.check_output(['git', 'diff', '--name-only', '-z',
        '4483f520eabb5358d1f35cf5c33a81d3b01e47e0', args.commit], cwd=ROOT).decode().split('\0')
    paths |= {p for p in changed if p and (ROOT / p).is_file()}

    def fetch(path):
        expected = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        url = f'https://raw.githubusercontent.com/{REPO}/{args.commit}/{quote(path, safe="/")}'
        errors = []
        for attempt in range(3):
            try:
                with urlopen(url, timeout=45) as response:
                    content = response.read()
                actual_hash = hashlib.sha256(content).hexdigest()
                return dict(path=path, bytes=len(content), local_sha256=expected,
                            remote_sha256=actual_hash, match=actual_hash == expected, retries=errors)
            except Exception as exc:
                errors.append(f'{type(exc).__name__}: {exc}')
                if attempt < 2:
                    time.sleep(1)
        return dict(path=path, match=False, errors=errors)

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(fetch, sorted(paths)))
    remote_after = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=ROOT, text=True).split()[0]
    result = dict(commit=args.commit, repository=f'https://github.com/{REPO}', branch='main',
                  actual_remote_before=actual, actual_remote_after=remote_after,
                  method='HTTPS raw bytes at fixed commit, SHA256 of response body',
                  verified_files=len(rows), rows=rows,
                  pass_all=all(r['match'] for r in rows) and remote_after == args.commit)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, ensure_ascii=False, indent=2))
    raise SystemExit(not result['pass_all'])


if __name__ == '__main__':
    main()
