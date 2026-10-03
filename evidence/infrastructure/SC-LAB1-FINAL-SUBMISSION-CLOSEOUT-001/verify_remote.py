"""Fetch independent remote objects, always resolve FETCH_HEAD, and read blobs."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
URL = 'https://github.com/woobowen/Smart_Cities_and_Location_Services.git'
NAME = '10245102410_吴博闻_实验一'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-sha', required=True)
    p.add_argument('--object-dir', type=Path, required=True)
    p.add_argument('--readback-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert re.fullmatch('[0-9a-f]{40}', args.expected_sha)
    obj = args.object_dir.resolve(); dest = args.readback_dir.resolve()
    assert not obj.is_relative_to(ROOT) and not dest.is_relative_to(ROOT)
    initially_existed = obj.exists()
    # A separate path alone does not exclude inherited local object storage.
    isolated_git_env = os.environ.copy()
    removed_variables = [
        'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_OBJECT_DIRECTORY',
        'GIT_DIR', 'GIT_COMMON_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
    ]
    for key in removed_variables:
        isolated_git_env.pop(key, None)
    if not initially_existed:
        subprocess.run(['git', 'init', '--bare', str(obj)], check=True,
                       capture_output=True, env=isolated_git_env)
        subprocess.run(['git', '--git-dir', str(obj), 'remote', 'add', 'origin', URL],
                       check=True, env=isolated_git_env)
    git = ['git', '--git-dir', str(obj)]
    assert subprocess.check_output(git + ['rev-parse', '--is-bare-repository'],
                                   text=True, env=isolated_git_env).strip() == 'true'
    assert subprocess.check_output(git + ['remote', 'get-url', 'origin'],
                                   text=True, env=isolated_git_env).strip() == URL
    alternates = {}
    for filename in ('alternates', 'http-alternates'):
        path = obj / 'objects' / 'info' / filename
        value = path.read_bytes() if path.exists() else b''
        assert not value.strip(), 'External object alternates are forbidden: ' + filename
        alternates[filename] = {'exists': path.exists(), 'bytes': len(value), 'empty': True}
    fetched = subprocess.run(git + ['fetch', '--depth=1', 'origin', 'main'],
                             capture_output=True, text=True, env=isolated_git_env)
    assert fetched.returncode == 0, fetched.stderr
    for filename in alternates:
        path = obj / 'objects' / 'info' / filename
        assert not path.exists() or not path.read_bytes().strip()
    head = subprocess.check_output(git + ['rev-parse', 'FETCH_HEAD'], text=True, env=isolated_git_env).strip()
    direct = subprocess.check_output(['git', 'ls-remote', URL, 'refs/heads/main'], text=True, env=isolated_git_env).split()[0]
    local = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, env=isolated_git_env).strip()
    origin = subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True, env=isolated_git_env).strip()
    assert head == direct == local == origin == args.expected_sha
    records = {}

    def tree_names(prefix):
        # NUL output preserves Chinese filenames without Git's C-style quoting.
        data = subprocess.check_output(git + [
            'ls-tree', '-r', '--name-only', '-z', 'FETCH_HEAD', '--', prefix], env=isolated_git_env)
        return [name for name in data.decode('utf8').split('\0') if name]

    def read(path):
        target = dest / path; target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('wb') as f:
            subprocess.run(git + ['show', 'FETCH_HEAD:' + path], stdout=f,
                           stderr=subprocess.PIPE, check=True, env=isolated_git_env)
        data = target.read_bytes()
        records[path] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                         'local_bytes_equal': data == (ROOT / path).read_bytes()}
        assert records[path]['local_bytes_equal'], path
        return data

    declaration_path = 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
    declaration = json.loads(read(declaration_path))
    rows = [r for r in declaration['sources'] if r['project_source']]
    release = 'releases/chatgpt-project-sources/'
    names = tree_names(release)
    assert set(names) == {release+r['canonical_name'] for r in rows}
    for row in rows:
        active, distributed = read(row['active_path']), read(release+row['canonical_name'])
        assert active == distributed and hashlib.sha256(active).hexdigest() == row['sha256']
    for path in ('Process_Report_Revised.pdf', 'Process_Report_Revised_LaTeX_Source.zip'):
        read(path)
    process_config = json.loads(read('task1/reports/process1/accepted-source.json'))
    input_check = json.loads((EV / 'input_zip_check.json').read_text())
    source_prefix = 'task1/reports/process1/source/'
    sources = tree_names(source_prefix)
    assert set(sources) == {source_prefix+r['path'] for r in input_check['members']}
    for row in input_check['members']:
        data = read(source_prefix+row['path'])
        assert hashlib.sha256(data).hexdigest() == row['sha256'] and len(data) == row['bytes']
    for report in ('task1/reports/experiment1/experiment1.pdf', process_config['current_reading_copy']): read(report)
    zip_path = 'task1/submission/teacher-delivery/'+NAME+'.zip'
    read(zip_path)
    package_folder = 'task1/submission/teacher-delivery/'+NAME+'/'
    with zipfile.ZipFile(dest / zip_path) as z:
        assert z.testzip() is None
        manifest = json.loads(z.read('PACKAGE_MANIFEST.json'))
        expected = {m['path']: m['archive_sha256'] for m in manifest['members']}
        expected['PACKAGE_MANIFEST.json'] = hashlib.sha256(z.read('PACKAGE_MANIFEST.json')).hexdigest()
        assert set(z.namelist()) == set(expected)
        folder = tree_names(package_folder)
        assert set(folder) == {package_folder+s for s in expected}
        for rel, digest in expected.items():
            data = read(package_folder+rel)
            assert data == z.read(rel) and hashlib.sha256(data).hexdigest() == digest
    result = {'status': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
        'repository': URL, 'branch': 'main', 'expected_sha': args.expected_sha,
        'local_HEAD': local, 'origin_main': origin, 'direct_remote_main': direct, 'independent_FETCH_HEAD': head,
        'readback_method': 'Network fetch into independent bare repository; git show FETCH_HEAD:path, no local object alternates',
        'independent_object_store': {'path': str(obj), 'initially_existed': initially_existed,
            'bare_verified': True, 'origin_url_verified': URL,
            'cleared_git_environment_variables': removed_variables,
            'alternates_before_fetch': alternates, 'alternates_after_fetch_empty': True},
        'project_source_count': len(rows), 'release_exact_set': True,
        'work_source_members_verified': len(input_check['members']),
        'teacher_zip': records[zip_path], 'teacher_zip_crc': True,
        'teacher_folder_zip_members_verified': len(expected),
        'teacher_folder_zip_exact_bytes': True, 'readback_blob_count': len(records),
        'records': records, 'new_model_calls': 0, 'new_trajectory_runs': 0, 'sent_to_teacher': False,
        'fetch_stderr': fetched.stderr}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status','expected_sha','project_source_count','work_source_members_verified','teacher_folder_zip_members_verified','readback_blob_count')}, ensure_ascii=False))


if __name__ == '__main__': main()
