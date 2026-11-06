"""Audit the approved refresh package and frozen reports without changing sources."""
import argparse
import difflib
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--record-name', default='initial_refresh_audit.json')
    args = parser.parse_args()
    review = Path(__file__).resolve().parent
    root = review.parents[3]
    if Path(args.record_name).name != args.record_name:
        raise ValueError('Record must be a plain filename within this review directory')
    baseline = 'b7fd9ee522905c11ddcea760470e7a5f0c1be9f0'
    expected_archive = '5012d8643f7a59208b89dc5be803b65b8701e9c55a85cb8c345767adf55dae13'

    def git(*arguments):
        return subprocess.check_output(['git', *arguments], cwd=root)

    record = {'reviewer': 'Codex independent agent process_integration_verifier',
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'baseline': baseline,
        'scope': 'Approved document bytes, actual diff, target semantics, frozen artifacts and candidate publication boundary; no source writes, media extraction, experiment run or report compile.'}
    with zipfile.ZipFile(args.package) as archive:
        record['package_sha256'] = sha(args.package.read_bytes())
        record['package_sha_matches_user'] = record['package_sha256'] == expected_archive
        record['package_members'] = len(archive.infolist())
        record['package_crc_ok'] = archive.testzip() is None
        record['package_unsafe_members'] = [item.filename for item in archive.infolist()
            if PurePosixPath(item.filename).is_absolute() or
               '..' in PurePosixPath(item.filename).parts or '\\' in item.filename or
               stat.S_ISLNK(item.external_attr >> 16)]
        versions = json.loads(archive.read('VERSION_AND_SHA256_MANIFEST.json'))
        target = json.loads(archive.read('PROJECT_SOURCES_TARGET_12.json'))
        documents = []
        actual_diff = []
        for row in versions['changed_documents']:
            name = row['repo_active_path']
            approved = archive.read('Project_Sources_Replace/' + row['filename'])
            actual = (root / name).read_bytes()
            old = git('show', baseline + ':' + name)
            documents.append({'path': name, 'version': row['new_version'],
                'sha256': sha(actual), 'bytes': len(actual),
                'exact_full_approved_package_bytes': actual == approved,
                'matches_approved_manifest': sha(actual) == row['new_sha256'] and len(actual) == row['new_bytes'],
                'old_git_bytes_match_package_baseline': sha(old) == row['old_sha256'],
                'old_git_blob_matches_package_baseline': git('rev-parse', baseline + ':' + name).decode().strip() == row['old_git_blob_sha']})
            actual_diff.append(''.join(difflib.unified_diff(old.decode().splitlines(keepends=True),
                actual.decode().splitlines(keepends=True), fromfile='a/'+name, tofile='b/'+name)))
        record['documents'] = documents
        record['actual_diff_matches_parent_record'] = ''.join(actual_diff) == (review.parent/'governance.diff').read_text()
        record['approved_target_record_exact_package_bytes'] = (review.parent/'approved_target.json').read_bytes() == archive.read('PROJECT_SOURCES_TARGET_12.json')
        record['approved_versions_record_exact_package_bytes'] = (review.parent/'approved_versions.json').read_bytes() == archive.read('VERSION_AND_SHA256_MANIFEST.json')
        target_names = [row['name'] for row in target['target_project_sources']]
        record['approved_target'] = {'active_count': len(target_names),
            'names_unique': len(set(target_names)) == len(target_names),
            'expected_final_registration_rows': target['target_total_metadata_records_if_baseline_unchanged'],
            'expected_final_false_count': len(target['deactivate_keep_original_repo_files']) + len(target['already_false_keep_false']),
            'active_names': target_names,
            'deactivate_names': target['deactivate_keep_original_repo_files'],
            'already_false_names': target['already_false_keep_false'],
            'identity': 'Approved target plan; never treated as the active sources.json'}
        settings = archive.read('PROJECT_SETTINGS_直接替换全文.txt')

    protected_roots = ['templates/', 'task1/', 'task2/src/', 'task2/results/',
        'task2/public_results/', 'task2/figures/', 'task2/diagrams/', 'task2/tests/',
        'task2/notebooks/', 'task2/reports/experiment/', 'task2/reports/generated/']
    protected_single = ['docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md', 'task2/reports/common.tex',
        'task2/releases/Dispatch_Reports_LaTeX_Source.zip']
    frozen_changed = git('diff', '--name-only', baseline, '--', *protected_roots, *protected_single).decode().splitlines()
    record['protected_git_roots'] = protected_roots + protected_single
    record['protected_git_paths_changed'] = frozen_changed
    research = root/'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md'
    record['research_v13_unchanged'] = sha(research.read_bytes()) == versions['unchanged_research_protocol_sha256']
    record['research_sha256'] = sha(research.read_bytes())
    reports = []
    for kind, expected, page_count in [
        ('process', 'c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f', 16),
        ('experiment', '7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101', 26)]:
        path = root/'task2/reports'/kind/('Process_Report.pdf' if kind == 'process' else 'Experiment_Report.pdf')
        info = subprocess.check_output(['pdfinfo', str(path)], text=True)
        pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
        reports.append({'kind': kind, 'path': str(path.relative_to(root)), 'sha256': sha(path.read_bytes()),
                        'expected_sha_matches': sha(path.read_bytes()) == expected,
                        'pages': pages, 'expected_pages_match': pages == page_count})
    record['reports'] = reports
    prior = root/'task2/evidence/process_report_sync_20261106/independent_review'
    integration = json.loads((prior/'integration_audit.json').read_text())
    record['process_sources_unchanged_since_prior_integration_audit'] = all(
        sha((root/row['path']).read_bytes()) == row['installed_sha256'] for row in integration['tex'])
    record['selected_18_pngs_unchanged_since_prior_pdf_embedding_audit'] = all(
        sha((root/row['path']).read_bytes()) == row['sha256'] for row in integration['assets'])
    prior_snapshot = json.loads((prior/'FINAL_STAGED_REVIEW.json').read_text())
    prior_reviews = [row for row in prior_snapshot['staged_snapshot']
        if row['path'].startswith('task2/evidence/process_report_sync_20261106/independent_review/')]
    record['prior_independent_records_checked'] = len(prior_reviews)
    record['prior_independent_records_unchanged'] = all(
        sha((root/row['path']).read_bytes()) == row['sha256'] for row in prior_reviews)
    record['strict_render_limit_inherited'] = 'Same Process PDF and sources; prior compile/text verification applies, strict pixel verification remained nonzero. No new compilation or visual check is claimed.'
    active = json.loads((root/'evidence/infrastructure/chatgpt-project-source-sync/sources.json').read_text())
    active_rows = [row for row in active['sources'] if row['project_source']]
    record['current_manifest_snapshot'] = {'rows': len(active['sources']), 'active': len(active_rows),
        'false': len(active['sources'])-len(active_rows),
        'matches_target_active_names': {row['canonical_name'] for row in active_rows} == set(target_names),
        'status': 'IN_PROGRESS_EXPECTED_NOT_FINAL; final synchronization/staged review is a separate appended record'}
    candidates = [name.decode() for name in git('diff','--cached','--name-only','-z').split(b'\0') if name]
    record['candidate_boundary'] = {
        'staged_contains_complete_settings_body': any(settings in git('show', ':'+name) for name in candidates),
        'staged_raw_media_or_input_names': [name for name in candidates
            if Path(name).suffix.lower() in ('.mp4','.mov','.webm') or
               'PROJECT_SETTINGS_' in name or 'Smart_Cities_Project_Sources_Video_Workflow_Update_' in name or
               'SOURCE_resend.zip' in name or '/evidence/raw/' in name],
        'source_package_and_settings_policy': 'Private input/TRANSFER_COPY only; no active Settings file or Project Source is created'}
    record['not_checked'] = ['Final manifest synchronization and staged publication set remain pending.',
        'No original video was supplied or reviewed; no new Evidence Master Lock is granted.',
        'No ChatGPT UI Settings paste/upload, remote publication or GPT external review was performed by this audit.']
    record['result'] = 'APPROVED_DOCUMENT_BYTES_AND_FROZEN_ARTIFACTS_VERIFIED; FINAL_COLLECTION_AND_PUBLICATION_REVIEW_PENDING'
    destination = review/args.record_name
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'report': str(destination.relative_to(root)),
        'four_documents_exact': all(row['exact_full_approved_package_bytes'] and row['matches_approved_manifest'] for row in documents),
        'actual_diff_exact': record['actual_diff_matches_parent_record'],
        'frozen_paths_changed': frozen_changed, 'reports': reports,
        'target_count': len(target_names), 'current_manifest': record['current_manifest_snapshot'],
        'private_boundary': record['candidate_boundary']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
