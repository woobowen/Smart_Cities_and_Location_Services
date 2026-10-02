"""Independent final source-byte and protected-file audit; production reads only."""
from hashlib import sha256, sha1
import json
from pathlib import Path
import subprocess
import zipfile
from audit_inputs import BASELINE, ROOT, OUT

START = '6527945ad8e526fa606b2c09835f2e51291fa4d0'
PROTECTED_PREFIXES = (
    'task1/config/', 'task1/workflow/', 'task1/scripts/', 'task1/results/',
    'task1/figures/', 'task1/evidence/', 'task1/notebooks/', 'task1/作业/',
    'task1/submission/', 'task1/data/', 'task1/goal1/', 'task1/goal2/',
    'task1/reports/experiment1/', 'reports/experiment-report/',
    'reports/process-report/pre-task1/', 'templates/latex/experiment-report/',
    'templates/latex/common/', 'docs/research/', 'tools/skills/',
)
PROTECTED_FILES = {'task1/作业.zip', 'task1/实验课1.pptx'}
ALLOWED_STATUS_FILES = {
    'task1/config/assignment.json',
    'task1/goal3/identity.py',
    'task1/reports/metadata.tex',
}
CURRENT_NAVIGATION_HEADER = 'task1/evidence/goal3/REVIEW_PACKET.md'
ALLOWED_OLD_EVIDENCE = {
    'evidence/infrastructure/chatgpt-project-source-sync/sources.json',
    'evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md',
    'evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md',
    'evidence/infrastructure/chatgpt-project-source-sync/README.md',
    'evidence/infrastructure/chatgpt-project-source-sync/test_sync_sources.py',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py',
}


def blob(data):
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    declaration = json.loads((ROOT / 'evidence/infrastructure/chatgpt-project-source-sync/sources.json').read_text())
    rows = {r['canonical_name']: r for r in declaration['sources'] if r['project_source']}
    actual_set = {p.name for p in (ROOT / 'releases/chatgpt-project-sources').iterdir()}
    inputs = []
    for name, expected in BASELINE.items():
        r = rows.get(name)
        for role, path in [('release', ROOT / 'releases/chatgpt-project-sources' / name),
                           ('active', ROOT / r['active_path'] if r else ROOT / '__MISSING_MANIFEST_ENTRY__')]:
            exists = path.is_file() and not path.is_symlink()
            actual = sha256(path.read_bytes()).hexdigest() if exists else None
            inputs.append({'name': name, 'role': role, 'path': str(path.relative_to(ROOT)),
                           'sha256': actual, 'matches_user_baseline': actual == expected,
                           'manifest_matches_user_baseline': bool(r and r['sha256'] == expected)})
    preserved, changed, migrated = [], [], []
    editable = []
    archive = ROOT / 'reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip'
    with zipfile.ZipFile(archive) as supplied:
        for member in supplied.infolist():
            if member.is_dir():
                continue
            relative = Path(member.filename).relative_to('Process_Report_Revised_Source')
            target = ROOT / 'task1/reports/process1/source' / relative
            original = sha256(supplied.read(member)).hexdigest()
            actual = sha256(target.read_bytes()).hexdigest() if target.is_file() else None
            editable.append({'path': relative.as_posix(), 'approved_member_sha256': original,
                             'working_sha256': actual, 'byte_identical': actual == original})
    reading_pdf = ROOT / 'task1/reports/process1/process1.pdf'
    reading_matches = sha256(reading_pdf.read_bytes()).hexdigest() == BASELINE['Process_Report_Revised.pdf']
    tree = subprocess.check_output(['git', 'ls-tree', '-rz', START], cwd=ROOT)
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        metadata, raw = entry.split(b'\t', 1)
        mode, kind, expected_blob = metadata.decode().split()
        path = raw.decode()
        protected = path.startswith(PROTECTED_PREFIXES) or path in PROTECTED_FILES
        protected |= path.startswith('evidence/') and path not in ALLOWED_OLD_EVIDENCE
        protected |= path.startswith('task1/goal3/') and path not in {
            'task1/goal3/__main__.py', 'task1/goal3/package.py', 'task1/goal3/PACKAGE_README.md'}
        if protected and path not in ALLOWED_STATUS_FILES and path != CURRENT_NAVIGATION_HEADER:
            p = ROOT / path
            actual = blob(p.read_bytes()) if p.is_file() else None
            (preserved if actual == expected_blob else changed).append(
                {'path': path, 'expected_git_blob': expected_blob, 'actual_git_blob': actual})
        if path.startswith('task1/reports/process1/'):
            old_relative = Path(path).relative_to('task1/reports/process1')
            p = ROOT / 'task1/reports/process1/history/technical-draft-12p' / old_relative
            actual = blob(p.read_bytes()) if p.is_file() else None
            migrated.append({'old_path': path, 'history_path': str(p.relative_to(ROOT)),
                             'expected_git_blob': expected_blob, 'actual_git_blob': actual,
                             'exact_preservation': actual == expected_blob})
    status_diff = subprocess.check_output(['git', 'diff', START, '--', *sorted(ALLOWED_STATUS_FILES)], cwd=ROOT).decode()
    (OUT / 'allowed_process_status.diff.txt').write_text(status_diff)
    before_assignment = json.loads(subprocess.check_output(['git', 'show', START + ':task1/config/assignment.json'], cwd=ROOT))
    current_assignment = json.loads((ROOT / 'task1/config/assignment.json').read_text())
    allowed_assignment = {
        'process_evidence_status': 'ORIGINALS_AND_SPEC_AVAILABLE_LOCK_NOT_UPGRADED',
        'process_report_status': 'USER_ACCEPTED_FULL_REPORT',
        'current_report_integration_task': 'SC-LAB1-PROCESS-INTEGRATION-SYNC-001',
        'process_approved_pdf_sha256': BASELINE['Process_Report_Revised.pdf'],
    }
    expected_assignment = before_assignment | allowed_assignment
    status_scope_ok = current_assignment == expected_assignment
    previous_metadata = subprocess.check_output(['git', 'show', START + ':task1/reports/metadata.tex'], cwd=ROOT).decode()
    expected_metadata = previous_metadata.replace('送审稿；原始互动证据与批准呈现方案待补', '全文已验收；具体 Evidence Lock 按原记录')
    metadata_scope_ok = (ROOT / 'task1/reports/metadata.tex').read_text() == expected_metadata
    previous_navigation = subprocess.check_output(['git', 'show', START + ':' + CURRENT_NAVIGATION_HEADER], cwd=ROOT).decode()
    current_navigation = (ROOT / CURRENT_NAVIGATION_HEADER).read_text()
    previous_header, previous_body = previous_navigation.split('\n\n', 1)
    navigation_scope_ok = current_navigation.startswith(previous_header + '\n\n') and current_navigation.endswith(previous_body)
    navigation_diff = subprocess.check_output(['git', 'diff', START, '--', CURRENT_NAVIGATION_HEADER], cwd=ROOT).decode()
    (OUT / 'current_navigation_append.diff.txt').write_text(navigation_diff)
    evidence = {'base_commit': START, 'scope': 'independent final read-only working-tree verification',
                'allowed_status_diff': 'allowed_process_status.diff.txt',
                'assignment_only_approved_process_status_updates': status_scope_ok,
                'metadata_only_process_description_changed': metadata_scope_ok,
                'historical_review_body_preserved_with_separate_current_header': navigation_scope_ok,
                'identity_diff_review': 'Read exact diff: only conditional ProcessStatus rendering changed; identity values and dates unchanged.',
                'member_set_matches_user': actual_set == set(BASELINE),
                'manifest_set_matches_user': set(rows) == set(BASELINE),
                'actual_names': sorted(actual_set), 'input_checks': inputs,
                'protected_file_count': len(preserved) + len(changed),
                'protected_changes': changed, 'preserved_files': preserved,
                'old_process_migration': migrated, 'editable_source_members': editable,
                'current_reading_pdf_matches_approved': reading_matches}
    (OUT / 'final_byte_protection_audit.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in evidence.items() if k not in {'preserved_files','input_checks','actual_names','old_process_migration','editable_source_members'}},ensure_ascii=False,indent=2))
    print(json.dumps({'input_instances':len(inputs),'input_matches':sum(r['matches_user_baseline'] for r in inputs),
                      'migration_files':len(migrated),'migration_exact':sum(r['exact_preservation'] for r in migrated),
                      'editable_members':len(editable),'editable_exact':sum(r['byte_identical'] for r in editable)},ensure_ascii=False))
    if (not status_scope_ok or not metadata_scope_ok or not navigation_scope_ok or not evidence['member_set_matches_user'] or not evidence['manifest_set_matches_user'] or changed or
            not all(r['matches_user_baseline'] and r['manifest_matches_user_baseline'] for r in inputs) or
            not all(r['exact_preservation'] for r in migrated) or not reading_matches or
            not all(r['byte_identical'] for r in editable)):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
