"""Build the explicitly authorized teacher candidate using the frozen closure.

The historical REVIEW_ONLY builder retains its filename gate. This separate
entry writes a folder and a ZIP, verifies both in staging, and never sends them.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from task1.goal3 import package

TASK = 'SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001'
NAME = '10245102410_吴博闻_实验一'
EXPERIMENT_SHA = '2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0'
PROCESS_SHA = 'dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23'


def validate_payload(payload):
    folded = set()
    for name, data in payload.items():
        package.relative_path(name)
        normalized = unicodedata.normalize('NFC', name).casefold()
        if normalized in folded or any(x != x.rstrip(' .') for x in name.split('/')):
            raise ValueError('WINDOWS_PATH_COLLISION_OR_UNSAFE_NAME')
        folded.add(normalized)
        if package.content_issues(name, data):
            raise ValueError('TEACHER_PAYLOAD_CONTENT_REJECTED:' + name)
    for path, digest in zip(package.REPORTS, (EXPERIMENT_SHA, PROCESS_SHA)):
        if package.sha(payload[path]) != digest:
            raise ValueError('AUTHORIZED_TEACHER_REPORT_HASH_MISMATCH:' + path)


def build_teacher(root=ROOT, delivery=None):
    root = Path(root).resolve()
    delivery = Path(delivery or root / 'task1/submission/teacher-delivery')
    folder, archive = delivery / NAME, delivery / (NAME + '.zip')
    if delivery.is_symlink() or any(p.is_symlink() for p in delivery.parents):
        raise ValueError('SYMLINK_DELIVERY_PATH')
    if folder.exists() or folder.is_symlink() or archive.exists() or archive.is_symlink():
        raise ValueError('EXISTING_TEACHER_CANDIDATE_PROTECTED')
    report, payload = package.closure(root)
    if report['status'] != 'STATIC_CLOSURE_COMPLETE':
        raise ValueError('FROZEN_CLOSURE_NOT_READY:' + json.dumps(
            {k: report[k] for k in ('missing', 'errors')}, ensure_ascii=False))
    readme_source = 'task1/submission/TEACHER_README.md'
    readme = (root / readme_source).read_bytes()
    payload['README.md'] = readme
    members = [dict(m) for m in report['members'] if m['path'] != 'README.md']
    members.append({'path': 'README.md', 'bytes': len(readme),
        'source_path': readme_source, 'source_sha256': package.sha(readme),
        'archive_sha256': package.sha(readme), 'transformations': [],
        'reasons': ['current teacher-facing reading and offline reproduction instructions']})
    # Preserve the source/target relation for every unchanged runtime member.
    for member in members:
        member.setdefault('source_path', member['path'])
    validate_payload(payload)
    probe = package.static_probe(payload)
    if probe.get('status') != 'VERIFIED' or probe.get('new_model_calls') != 0 or probe.get('trajectory_runs') != 0:
        raise ValueError('TEACHER_ISOLATED_STATIC_PROBE_FAILED:' + json.dumps(probe))
    manifest = {**report, 'package_status': 'TEACHER_SUBMISSION_CANDIDATE',
        'submission_status': 'NOT_READY', 'sent_to_teacher': False,
        'member_count': len(members),
        'total_uncompressed_bytes': sum(m['bytes'] for m in members),
        'members': sorted(members, key=lambda m: m['path']),
        'isolated_static_probe': probe, 'build_authorization': TASK,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'manifest_self_hash': 'intentionally omitted to avoid self-reference'}
    contents = {**payload, 'PACKAGE_MANIFEST.json': package.json_bytes(manifest)}
    delivery.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.teacher-stage-', dir=delivery) as temp:
        stage = Path(temp); staged_folder = stage / NAME; staged_folder.mkdir()
        for path, data in contents.items():
            target = staged_folder / path; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        package.verify_directory(staged_folder)
        staged_zip = stage / (NAME + '.zip')
        with zipfile.ZipFile(staged_zip, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for path in sorted(contents):
                info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, contents[path])
        with zipfile.ZipFile(staged_zip) as z:
            if z.testzip() is not None or set(z.namelist()) != set(contents):
                raise ValueError('STAGED_TEACHER_ZIP_CRC_OR_SET_MISMATCH')
            for path, data in contents.items():
                if z.read(path) != data or (staged_folder / path).read_bytes() != data:
                    raise ValueError('STAGED_TEACHER_FOLDER_ZIP_BYTES_MISMATCH:' + path)
        os.replace(staged_folder, folder)
        os.replace(staged_zip, archive)
    return {'status': 'TEACHER_SUBMISSION_CANDIDATE', 'folder': str(folder),
        'zip': str(archive), 'zip_sha256': package.sha(archive.read_bytes()),
        'zip_bytes': archive.stat().st_size, 'declared_members': len(members),
        'files_including_manifest': len(contents), 'folder_zip_equal': True,
        'isolated_static_probe': probe, 'full_recompute_this_task': 'NOT_RUN_UNCHANGED_SCIENCE',
        'sent_to_teacher': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    result = build_teacher()
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(package.json_bytes(result))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
