"""Bind reviewed engineering bytes and existing C evidence without self-hashing."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

OUT = Path(__file__).resolve().parent
TASK = OUT.parent
ROOT = OUT.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    definition = ROOT/'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
    sources = json.loads(definition.read_text())['sources']
    files = set()
    for row in sources:
        files |= {row['active_path'], 'releases/chatgpt-project-sources/'+row['canonical_name']}
    files |= {
        'evidence/infrastructure/chatgpt-project-source-sync/sources.json',
        'evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md',
        'evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md',
        'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',
        'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py',
        'evidence/infrastructure/chatgpt-project-source-sync/test_sync_sources.py',
        'task1/reports/build_reports.py', 'task1/goal3/__main__.py', 'task1/goal3/package.py',
        'task1/tests/test_accepted_report_integration.py',
        'task1/reports/experiment1/accepted-source.json',
        'task1/reports/experiment1/experiment1.pdf', 'task1/reports/process1/process1.pdf',
        'task1/config/assignment.json',
        'task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip',
    }
    build = json.loads((TASK/'report/normal-build-2/build_receipt.json').read_text())
    files.update(build['source_sha256'])
    nav = json.loads((OUT/'current-navigation-links.json').read_text())
    files.update(row['path'] for row in nav['current_navigation_files'])
    bindings = {name: sha(ROOT/name) for name in sorted(files)}
    proof_names = [
        'C_REVIEW.md', 'ISSUES.md', 'initial-independent-results.json',
        'independent-content-results.json', 'independent-build-result.json',
        'independent-sync-results.json', 'metadata-independent-checks.json',
        'editable-source-independent-checks.json', 'normal-builds-independent-check.json',
        'visual-coverage-independent-check.json', 'navigation-independent-checks.json',
        'current-navigation-links.json', 'independent-package-review.json',
        'full-starting-inventory-audit.json',
    ]
    package = ROOT/'task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip'
    historical = ROOT/'task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/executed_package/REVIEW_ONLY_10245102410_吴博闻_实验一.zip'
    with zipfile.ZipFile(package) as archive:
        meta = json.loads(archive.read('PACKAGE_MANIFEST.json'))['metadata']
    with zipfile.ZipFile(historical) as archive:
        assert meta == json.loads(archive.read('PACKAGE_MANIFEST.json'))['metadata']
    source_identity = json.loads((ROOT/'task1/config/assignment.json').read_text())
    assert all(meta[key] == value for key, value in source_identity.items())
    extra = {key: value for key, value in meta.items() if key not in source_identity}
    assert extra == {'evidence_master_spec_and_lock': 'NOT_AVAILABLE'}
    result = {
        'reviewer_context': '/root/independent_c',
        'status': 'INTERNAL_C_VERIFIED_FOR_REVIEWED_ARTIFACTS',
        'completed_at': datetime.now(timezone.utc).isoformat(),
        'engineering_bindings': bindings,
        'proof_bindings': {name: sha(OUT/name) for name in proof_names},
        'final_entry_read_snapshot': {name: sha(TASK/name) for name in ['REVIEW_PACKET.md', 'ACCEPTANCE_MATRIX.json']},
        'entry_snapshot_scope': 'Read before root integrates final C/publication links and results. These progress documents may add status/evidence; engineering_bindings define the reviewed artifact bytes.',
        'open_engineering_issues': [],
        'closed_issues': ['C-001 AGENTS declaration now exactly matches actual Revision'],
        'independent_visual_pages': [1, 6, 9, 14, 19, 25],
        'author_actual_visual_coverage': 'All 25 approved/rebuilt pairs; 50 complete 200dpi pages with separate observer receipts',
        'full_recompute_this_task': False,
        'new_model_attempts_in_C_isolated_probe': 0,
        'new_trajectory_runs': 0,
        'package_identity_metadata_scope': {
            'source': 'task1/config/assignment.json',
            'source_sha256': sha(ROOT/'task1/config/assignment.json'),
            'manifest_preserves_all_original_source_fields': True,
            'complete_metadata_equals_historical_executed_package': True,
            'preexisting_derived_fields': extra,
            'inherited_report_revision_date': meta['report_revision_date'],
            'inherited_default_package_name': meta['review_package_name'],
            'interpretation': 'Original identity-source metadata; current Experiment revision is 2026-09-29 and current archive name/SHA come from the actual reviewed ZIP/build receipt. No original config or Process rewrite.',
        },
        'states': {
            'SYNC_01_to_13': 'VERIFIED_INTERNAL', 'SYNC_14': 'PENDING_PUBLICATION',
            'GPT_SECOND_REVIEW': 'PENDING', 'UI_SCOPE_UPDATE': 'USER_ACTION_PENDING',
            'PROCESS_REFERENCE_REPRODUCTION': 'PARTIAL_RETAINED', 'SUBMISSION': 'NOT_READY',
        },
        'limits': [
            'No newly run numerical FULL or complete figure-redraw claim.',
            'Independent C engineering review is not web GPT second review, Evidence Lock, UI upload, Understanding approval or Submission.',
        ],
    }
    (OUT/'C_FINAL_RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'engineering_bindings': len(bindings),
                      'proof_bindings': len(proof_names), 'C_REVIEW_sha256': sha(OUT/'C_REVIEW.md'),
                      'C_FINAL_RESULT_sha256': sha(OUT/'C_FINAL_RESULT.json')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
