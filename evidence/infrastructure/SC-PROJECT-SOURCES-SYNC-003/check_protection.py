"""Compare every captured original file with the final workspace; enumerate all allowed changes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
APPROVED_CHANGED_PATHS = {
    'AGENTS.md', 'README.md', 'docs/design-system/README.md',
    'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md',
    'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md',
    'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md',
    'templates/latex/experiment-report/README.md', 'templates/latex/process-report/README.md',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/README.md',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py',
    'evidence/infrastructure/chatgpt-project-source-sync/README.md',
    'evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md',
    'evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md',
    'task1/README.md', 'task1/reports/README.md', 'task1/docs/goal3/REVIEW_GUIDE.md',
    'task1/docs/goal3/DEFENSE_NOTES.md', 'task1/docs/goal3/TECHNICAL_HANDOFF.md',
    'task1/goal3/PACKAGE_README.md',
    'task1/evidence/goal3/teacher_delivery_mapping.json', 'task1/evidence/goal3/teacher_delivery_mapping.md',
    'task1/evidence/goal3/REVIEW_PACKET.md',
    'task1/goal3/__main__.py', 'task1/reports/build_reports.py',
    'task1/reports/experiment1/experiment1.tex', 'task1/reports/experiment1/experiment1.pdf',
}
APPROVED_CHANGED_PATHS |= {'releases/chatgpt-project-sources/' + name for name in (
    'AGENTS.md', 'SMART_CITIES_RESEARCH_PROTOCOL.md', 'SMART_CITIES_REPORT_WRITING_GUIDE.md',
    'SMART_CITIES_VISUAL_SYSTEM.md', 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md')}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    originals = json.loads((OUT / 'starting-protection-inventory.json').read_text())
    relocations = {r['path']: r for r in json.loads((OUT / 'metadata-relocation.json').read_text())}
    changes, failures, unchanged = [], [], []
    for original in originals:
        path = original['path']
        current = ROOT / path
        if original['type'] != 'file':
            continue
        value = digest(current) if current.is_file() and not current.is_symlink() else None
        if value == original['sha256']:
            unchanged.append(path)
        elif path in relocations:
            kept = ROOT / relocations[path]['retained_path']
            if not kept.is_file() or digest(kept) != original['sha256']:
                failures.append({'path': path, 'reason': 'quarantined original not preserved'})
            changes.append({'path': path, 'classification': 'OS_METADATA_RELOCATED_BYTES_PRESERVED'})
        elif path in APPROVED_CHANGED_PATHS and value is not None:
            changes.append({'path': path, 'classification': 'AUTHORIZED_GOVERNANCE_OR_REPORT_INTEGRATION',
                            'before_sha256': original['sha256'], 'after_sha256': value})
        else:
            failures.append({'path': path, 'reason': 'Unexpected changed or removed protected file',
                             'before_sha256': original['sha256'], 'after_sha256': value})
    result = dict(captured_files=len(originals), unchanged_count=len(unchanged),
                  approved_changes=changes, unexpected_changes=failures,
                  scope='all captured files except .git/.venv/cache; new files separately publication-audited',
                  unchanged_paths=unchanged, pass_all=not failures)
    (OUT / 'protection-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('unchanged_paths', 'approved_changes')}, ensure_ascii=False))
    raise SystemExit(not result['pass_all'])


if __name__ == '__main__':
    main()
