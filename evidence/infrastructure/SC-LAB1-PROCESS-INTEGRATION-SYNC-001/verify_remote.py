"""Read GitHub through an independent object store and verify approved bytes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

REPOSITORY = 'https://github.com/woobowen/Smart_Cities_and_Location_Services.git'
TASK = 'evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001'
MANIFEST = 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--object-dir', type=Path, required=True)
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-network-store', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing to replace a previous verification receipt')
    expected = dict(line.split('  ', 1)[::-1] for line in
                    Path(__file__).with_name('approved_input_sha256.txt').read_text().splitlines())
    commands = []

    def run(command, cwd=None):
        result = subprocess.run(command, cwd=cwd, capture_output=True, check=True)
        commands.append({'command': command, 'exit_code': result.returncode})
        return result.stdout

    direct = run(['git', 'ls-remote', REPOSITORY, 'refs/heads/main']).decode().split()[0]
    if direct != args.expected_sha:
        raise SystemExit('Remote main changed before verification: ' + direct)
    if not args.reuse_network_store:
        if args.object_dir.exists():
            raise SystemExit('Initial network object store must be new')
        args.object_dir.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '--bare', '--filter=blob:none', '--depth=1', '--single-branch',
             '--branch', 'main', REPOSITORY, str(args.object_dir)])
    else:
        if run(['git', 'remote', 'get-url', 'origin'], args.object_dir).decode().strip() != REPOSITORY:
            raise SystemExit('Incorrect object-store origin')
        run(['git', 'fetch', '--depth=1', '--filter=blob:none', 'origin',
             'refs/heads/main:refs/heads/main'], args.object_dir)
    if (args.object_dir / 'objects/info/alternates').exists():
        raise SystemExit('Local object alternates are forbidden for this verification')
    observed = run(['git', 'rev-parse', 'refs/heads/main'], args.object_dir).decode().strip()
    if observed != args.expected_sha:
        raise SystemExit('Fetched commit does not match requested remote main')
    tree = {}
    for record in run(['git', 'ls-tree', '-r', '-z', observed], args.object_dir).split(b'\0'):
        if record:
            header, path = record.split(b'\t', 1)
            mode, kind, oid = header.decode().split()
            tree[path.decode()] = {'mode': mode, 'kind': kind, 'git_oid': oid}

    cache = {}

    def blob(path):
        entry = tree[path]
        if entry['mode'] not in ('100644', '100755') or entry['kind'] != 'blob':
            raise ValueError('Not an ordinary Git file: ' + path)
        oid = entry['git_oid']
        if oid not in cache:
            cache[oid] = run(['git', 'cat-file', 'blob', oid], args.object_dir)
        return cache[oid]

    manifest_bytes = blob(MANIFEST)
    manifest = json.loads(manifest_bytes)
    sources = [row for row in manifest['sources'] if row.get('project_source')]
    if {row['canonical_name'] for row in sources} != set(expected) or len(sources) != len(expected):
        raise ValueError('Remote manifest membership differs from approved input set')
    release_prefix = 'releases/chatgpt-project-sources/'
    actual_release = {path[len(release_prefix):] for path in tree if path.startswith(release_prefix)}
    if actual_release != set(expected):
        raise ValueError('Remote release membership differs from approved input set')
    checks = []
    for source in sources:
        name = source['canonical_name']
        if source['sha256'] != expected[name]:
            raise ValueError('Remote manifest changed expected input hash: ' + name)
        for role, path in [('active', source['active_path']), ('release', release_prefix + name)]:
            data = blob(path)
            digest = hashlib.sha256(data).hexdigest()
            if digest != expected[name] or data.startswith(b'version https://git-lfs.github.com/spec/v1'):
                raise ValueError('Remote bytes differ from approved input: ' + path)
            checks.append({'canonical_name': name, 'role': role, 'path': path,
                           **tree[path], 'size': len(data), 'sha256': digest, 'matches_input': True})
    direct_after = run(['git', 'ls-remote', REPOSITORY, 'refs/heads/main']).decode().split()[0]
    if direct_after != observed:
        raise ValueError('Remote main changed during verification')
    receipt = {
        'status': 'PASS', 'verified_at': datetime.now(timezone.utc).isoformat(),
        'repository': REPOSITORY, 'branch': 'main', 'fetched_commit': observed,
        'direct_remote_before': direct, 'direct_remote_after': direct_after,
        'network_store_created_fresh': not args.reuse_network_store,
        'local_object_alternates': False, 'object_store': str(args.object_dir),
        'baseline_origin': 'User Prompt independent SHA256 appendix, not generated manifest',
        'baseline_sha256': hashlib.sha256(Path(__file__).with_name('approved_input_sha256.txt').read_bytes()).hexdigest(),
        'manifest_git_oid': tree[MANIFEST]['git_oid'],
        'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
        'project_source_count': len(sources), 'verified_active_and_release_instances': len(checks),
        'checks': checks, 'commands': commands,
        'web_gpt_review': 'PENDING', 'teacher_submission': 'NOT_PERFORMED',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'fetched_commit', 'project_source_count',
                                             'verified_active_and_release_instances')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
