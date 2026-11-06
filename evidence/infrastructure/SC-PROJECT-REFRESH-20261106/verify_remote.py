"""Read fixed-commit public bytes over HTTPS and compare SHA256 and Git blob IDs."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = 'woobowen/Smart_Cities_and_Location_Services'
DECLARATION = 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
RELEASE = 'releases/chatgpt-project-sources/'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--readback-dir', type=Path, required=True)
    args = parser.parse_args()
    for value in (args.commit, args.baseline):
        if not re.fullmatch('[0-9a-f]{40}', value):
            parser.error('commit and baseline must be full Git SHAs')
    for path in (args.output.resolve(), args.readback_dir.resolve()):
        if path.is_relative_to(ROOT):
            parser.error('post-publication receipts and readback must stay outside the repository')
    origin = git('remote', 'get-url', 'origin').decode().strip()
    assert origin == 'https://github.com/' + REPOSITORY + '.git', origin
    local = git('rev-parse', 'HEAD').decode().strip()
    tracking = git('rev-parse', 'origin/main').decode().strip()
    remote_before = git('ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    assert local == tracking == remote_before == args.commit
    declaration = json.loads(git('show', args.commit + ':' + DECLARATION))
    rows = declaration['sources']
    active = [row for row in rows if row['project_source']]
    release_paths = set(git('ls-tree', '-r', '--name-only', '-z', args.commit,
                            '--', RELEASE).decode().strip('\0').split('\0'))
    assert release_paths == {RELEASE + row['canonical_name'] for row in active}
    paths = {row['active_path'] for row in rows} | release_paths | {DECLARATION}
    changed = git('diff', '--name-only', '--diff-filter=ACMRT', '-z',
                  args.baseline, args.commit).decode().strip('\0').split('\0')
    paths.update(path for path in changed if path)
    expected = {}
    for path in paths:
        content = git('show', args.commit + ':' + path)
        expected[path] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
                          'git_blob': git('rev-parse', args.commit + ':' + path).decode().strip()}

    def fetch(path):
        errors = []
        url = f'https://raw.githubusercontent.com/{REPOSITORY}/{args.commit}/{quote(path, safe="/")}'
        for attempt in range(3):
            try:
                with urlopen(url, timeout=45) as response:
                    content = response.read()
                digest = hashlib.sha256(content).hexdigest()
                blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
                match = (len(content) == expected[path]['bytes'] and
                         digest == expected[path]['sha256'] and blob == expected[path]['git_blob'])
                if not match:
                    raise ValueError('Remote length, SHA256 or Git blob differs from the fixed local object')
                dest = args.readback_dir / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
                return {'path': path, 'match': True, 'bytes': len(content),
                        'sha256': digest, 'remote_git_blob': blob,
                        'local_git_blob': expected[path]['git_blob'], 'retries': errors}
            except Exception as exc:
                errors.append(f'{type(exc).__name__}: {exc}')
                if attempt < 2:
                    time.sleep(1)
        return {'path': path, 'match': False, 'errors': errors}

    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch, path) for path in sorted(paths)]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records) % 20 == 0 or len(records) == len(paths):
                print(json.dumps({'remote_readback_completed': len(records), 'total': len(paths)}), flush=True)
    records.sort(key=lambda row: row['path'])
    by_path = {row['path']: row for row in records}
    sources_equal = all(by_path[row['active_path']]['match'] and
                        by_path[row['active_path']].get('sha256') == row['sha256'] for row in rows)
    distributed_equal = all(by_path[RELEASE + row['canonical_name']]['match'] and
                            by_path[RELEASE + row['canonical_name']].get('sha256') == row['sha256']
                            for row in active)
    remote_after = git('ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    passed = (all(row['match'] for row in records) and sources_equal and
              distributed_equal and remote_before == remote_after == args.commit)
    result = {'status': 'PASS' if passed else 'FAIL', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'repository': 'https://github.com/' + REPOSITORY, 'branch': 'main',
              'local_HEAD': local, 'origin_main': tracking, 'remote_before': remote_before,
              'remote_after': remote_after, 'fixed_commit': args.commit, 'baseline': args.baseline,
              'method': 'Actual HTTPS raw response bytes at the fixed commit; SHA256 and Git blob SHA1 compared with fixed local Git objects',
              'registered_rows': len(rows), 'project_source_count': len(active),
              'remote_release_exact_set': True, 'all_registered_authorities_match': sources_equal,
              'all_active_distributed_bytes_match': distributed_equal,
              'readback_blob_count': len(records), 'records': records,
              'ui_status': 'USER_UI_ACTION_REQUIRED', 'gpt_external_review': 'NOT_PERFORMED'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}, ensure_ascii=False), flush=True)
    raise SystemExit(not passed)


if __name__ == '__main__':
    main()
