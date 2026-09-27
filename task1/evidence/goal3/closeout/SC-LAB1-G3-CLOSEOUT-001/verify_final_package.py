"""Bind the current report-only ZIP revision to the actual FULL input archive."""
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone

from task1.goal3.package import relative_path, verify_directory

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
NAME = 'REVIEW_ONLY_10245102410_吴博闻_实验一.zip'
REPORTS = {'task1/reports/experiment1/experiment1.pdf', 'task1/reports/process1/process1.pdf'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_contents(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert archive.testzip() is None
        for info in archive.infolist():
            relative_path(info.filename)
            assert not stat.S_ISLNK(info.external_attr >> 16)
        contents = {name: archive.read(name) for name in names}
        manifest = json.loads(contents['PACKAGE_MANIFEST.json'])
        hashes = {row['path']: row['archive_sha256'] for row in manifest['members']}
        assert set(hashes) == set(contents) - {'PACKAGE_MANIFEST.json'}
        for name, expected in hashes.items():
            assert digest(contents[name]) == expected
        return contents, manifest, hashes


def main():
    current = ROOT / 'task1/submission' / NAME
    executed = BASE / 'executed_package' / NAME
    old, _, old_hashes = checked_contents(executed)
    new, manifest, hashes = checked_contents(current)
    assert set(old) == set(new)
    changed = sorted(name for name in old if old[name] != new[name])
    assert set(changed) <= REPORTS | {'PACKAGE_MANIFEST.json'}
    runtime_paths = sorted(set(hashes) - REPORTS)
    assert all(hashes[p] == old_hashes[p] for p in runtime_paths)
    assert all(new[p] == (ROOT / p).read_bytes() for p in REPORTS)
    identity = manifest['metadata']
    assert identity['student_name'] == '吴博闻'
    assert type(identity['student_id']) is str and identity['student_id'] == '10245102410'
    assert manifest['submission_status'] == 'NOT_READY' and manifest['sent_to_teacher'] is False
    with tempfile.TemporaryDirectory(prefix='sc-lab1-current-zip-verification-') as temp:
        directory = Path(temp)
        for name, data in new.items():
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        extracted_check = verify_directory(directory)
        assert extracted_check['status'] == 'VERIFIED'
    content_id = digest(json.dumps(hashes, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
    result = {
        'at': datetime.now(timezone.utc).isoformat(), 'status': 'STATIC_VERIFIED_FULL_EVIDENCE_SEPARATE',
        'zip_path': str(current.relative_to(ROOT)), 'zip_sha256': digest(current.read_bytes()),
        'zip_bytes': current.stat().st_size, 'members_including_manifest': len(new),
        'PACKAGE_CONTENT_ID': content_id,
        'content_id_definition': 'SHA256 UTF-8 compact sorted JSON (ensure_ascii=False) of payload path -> archive_sha256; excludes manifest',
        'NUMERIC_CODE_SHA': 'e12f8a27944210adb452730be92a0674dfc6b84b',
        'DOCUMENT_BUILD_CODE_SHA': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'report_build_source_pinned_after_build': True,
        'reports': {p: hashes[p] for p in sorted(REPORTS)},
        'identity': identity,
        'crc_safe_paths_no_symlinks_unique_members': 'VERIFIED',
        'pdf_bytes_equal_current': True, 'directory_verification': extracted_check,
        'equivalent_executed_archive': str(executed.relative_to(ROOT)),
        'equivalent_executed_archive_sha256': digest(executed.read_bytes()),
        'executed_input_directory': '/tmp/sc-lab1-closeout-package',
        'changed_members': changed,
        'identical_non_pdf_payload_members': len(runtime_paths),
        'identical_complete_runtime_inputs_sha256': {p: hashes[p] for p in runtime_paths},
        'full_evidence_relationship': 'Report-only revision. The complete Notebook/dependency/input payload is byte-identical to the preserved archive used for actual isolated new-kernel FULL runs. Execution receipts are checked separately; this is equivalence, not a new execution.',
        'new_trajectory_runs_in_this_check': 0, 'new_record_model_calls_in_this_check': 0,
        'submission_status': 'NOT_READY', 'new_gpt_second_review': 'PENDING'
    }
    (BASE / 'PACKAGE_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('zip_sha256', 'zip_bytes', 'members_including_manifest', 'PACKAGE_CONTENT_ID', 'changed_members', 'identical_non_pdf_payload_members')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
