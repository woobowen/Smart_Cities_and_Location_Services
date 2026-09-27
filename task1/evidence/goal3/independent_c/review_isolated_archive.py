"""Bind the actual ZIP, unchanged extracted members and two real launch inputs.

This is an archive/launch provenance check, not either FULL execution acceptance.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shlex
import zipfile

ROOT = Path(__file__).resolve().parents[4]
EV = ROOT/'task1/evidence/goal3'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    extraction_path = EV/'package/isolated_extraction_receipt.json'
    launches_path = EV/'package/isolated_launches.json'
    build_path = EV/'package/package_build_receipt.json'
    extraction, launches, build = read(extraction_path), read(launches_path), read(build_path)
    archive = ROOT/extraction['zip_path']; extracted = Path(extraction['actual_extraction_root']).resolve()
    assert sha(archive) == extraction['zip_sha256'] == launches['zip_sha256'] == build['zip_sha256']
    assert archive.stat().st_size == extraction['zip_bytes'] == build['zip_bytes']
    assert extracted == Path(launches['extracted_root']).resolve() and not (extracted/'.git').exists()
    assert extraction['fresh_root'] is True and extraction['git_present'] is False
    manifest_path = extracted/'PACKAGE_MANIFEST.json'; manifest = read(manifest_path)
    assert sha(manifest_path) == extraction['package_manifest_sha256']
    members = {item['path']: item for item in manifest['members']}
    assert len(members) == len(manifest['members']) == extraction['member_check']['verified_members'] == 112
    verified = []
    with zipfile.ZipFile(archive) as stream:
        names = stream.namelist()
        assert len(names) == len(set(names)) == extraction['members_including_manifest'] == build['members_including_manifest'] == 113
        assert set(names) == set(members) | {'PACKAGE_MANIFEST.json'} and stream.testzip() is None
        for name in names:
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
            info = stream.getinfo(name)
            assert (info.external_attr >> 16) & 0o170000 != 0o120000
            payload = stream.read(name); target = (extracted/name).resolve()
            assert extracted in target.parents and target.is_file() and not target.is_symlink()
            digest = hashlib.sha256(payload).hexdigest()
            assert sha(target) == digest and target.stat().st_size == len(payload)
            if name != 'PACKAGE_MANIFEST.json':
                assert digest == members[name]['archive_sha256'] and len(payload) == members[name]['bytes']
            else:
                assert digest == extraction['package_manifest_sha256']
            verified.append({'path': name, 'sha256': digest, 'bytes': len(payload)})
    assert len(launches['jobs']) == 2 and {job['kind'] for job in launches['jobs']} == {'basic', 'system'}
    assert len({job['work'] for job in launches['jobs']}) == len({job['cache'] for job in launches['jobs']}) == 2
    launch_checks = []
    removed = {'OPENAI_API_KEY', 'CODEX_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'AZURE_OPENAI_API_KEY'}
    for job in launches['jobs']:
        argv = shlex.split(job['cmd'])
        assert argv[0] == 'env'
        assert {argv[i+1] for i, token in enumerate(argv[:-1]) if token == '-u'} == removed
        assert {'PYTHONPATH=', 'PYTHONNOUSERSITE=1', 'PYTHONDONTWRITEBYTECODE=1'} <= set(argv)
        assert '-I' in argv and argv[argv.index('--cwd')+1] == str(extracted)
        assert argv[argv.index('--work')+1] == job['work']
        assert argv[argv.index('--evidence')+1] == job['evidence']
        assert extracted not in Path(job['work']).resolve().parents
        assert job['actual_launch']['status'] == 'fulfilled' and job['actual_launch']['value']['session_id']
        name = 'task1/notebooks/final/'+job['name']
        assert name in members and name in argv
        launch_checks.append({'kind': job['kind'], 'input_notebook_path': name,
            'input_notebook_sha256': members[name]['archive_sha256'],
            'actual_launch_session': job['actual_launch']['value']['session_id'],
            'separate_work_and_cache_directories': True, 'registered_api_key_environment_removals': sorted(removed),
            'scope': 'Launch provenance only; completion must be established from the separate actual FULL execution and C receipts.'})
    executor = extraction['external_executor_source']
    assert sha(ROOT/executor['path']) == executor['sha256']
    paths = [archive, extraction_path, launches_path, build_path, ROOT/executor['path']]
    receipt = {'role_context': '/root/c_protocol', 'target_id': 'actual_isolated_zip_archive_binding',
        'status': 'VERIFIED', 'scope': 'ARCHIVE_MEMBERS_AND_LAUNCH_BINDING_ONLY_NOT_FULL_COMPLETION',
        'at': datetime.now(timezone.utc).isoformat(),
        'targets': [{'path': str(path.relative_to(ROOT)), 'sha256': sha(path)} for path in paths],
        'source_hashes': {str(Path(__file__).relative_to(ROOT)): sha(__file__)},
        'zip_sha256': sha(archive), 'package_manifest_sha256': sha(manifest_path),
        'actual_zip_members_and_extracted_files_checked': verified, 'launch_checks': launch_checks,
        'checked_components': ['Actual ZIP SHA/CRC, unique safe members and complete manifest scope',
            'Every actual ZIP member compared byte-for-byte/hash with the extracted original input',
            'Both launched kernels use Notebook input bytes from this same archive',
            'Separate explicit work/cache paths, cleared Python path, removed registered API key env names and actual launch sessions'],
        'unchecked_components': ['Launches alone do not prove successful completion; each FULL Notebook has a separate independent receipt',
            'Report content, personal metadata, Evidence Master LOCK and final package/submission readiness are separate'],
        'new_trajectory_processing': 0, 'new_model_calls': 0, 'errors': [],
        'actual_command': '.venv/bin/python task1/evidence/goal3/independent_c/review_isolated_archive.py'}
    output = EV/'independent_c/isolated_archive_binding_receipt.json'
    with output.open('x') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'status': 'VERIFIED', 'zip_members': len(verified), 'zip_sha256': sha(archive),
                      'receipt_sha256': sha(output)}))


if __name__ == '__main__':
    main()
