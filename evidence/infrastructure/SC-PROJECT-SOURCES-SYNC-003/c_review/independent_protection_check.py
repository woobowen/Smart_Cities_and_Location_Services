"""Compare every received starting file, not just selected data prefixes."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
TASK = OUT.parent
ROOT = OUT.parents[3]
APPROVED_MODIFICATIONS = {
    'AGENTS.md', 'README.md', 'docs/design-system/README.md',
    'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md',
    'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md',
    'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/README.md',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py',
    'evidence/infrastructure/chatgpt-project-source-sync/README.md',
    'evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md',
    'evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md',
    'releases/chatgpt-project-sources/AGENTS.md',
    'releases/chatgpt-project-sources/SMART_CITIES_REPORT_WRITING_GUIDE.md',
    'releases/chatgpt-project-sources/SMART_CITIES_RESEARCH_PROTOCOL.md',
    'releases/chatgpt-project-sources/SMART_CITIES_VISUAL_SYSTEM.md',
    'releases/chatgpt-project-sources/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md',
    'task1/evidence/goal3/teacher_delivery_mapping.json',
    'task1/evidence/goal3/teacher_delivery_mapping.md',
    'task1/goal3/__main__.py', 'task1/reports/build_reports.py',
    'task1/reports/experiment1/experiment1.pdf', 'task1/reports/experiment1/experiment1.tex',
    'templates/latex/experiment-report/README.md', 'templates/latex/process-report/README.md',
    'task1/README.md', 'task1/goal3/PACKAGE_README.md',
    'task1/docs/goal3/REVIEW_GUIDE.md', 'task1/docs/goal3/TECHNICAL_HANDOFF.md',
    'task1/docs/goal3/DEFENSE_NOTES.md',
    'task1/evidence/goal3/REVIEW_PACKET.md', 'task1/reports/README.md',
}


def main():
    rows = json.loads((TASK/'starting-protection-inventory.json').read_text())
    changed, missing, mtimes = [], [], []
    for row in rows:
        path = ROOT/row['path']
        if not path.is_file():
            missing.append(row['path'])
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row['sha256']:
            changed.append({'path': row['path'], 'before': row['sha256'], 'after': digest})
        elif path.stat().st_mtime_ns != row['mtime_ns']:
            mtimes.append(row['path'])
    unexpected = sorted({r['path'] for r in changed} - APPROVED_MODIFICATIONS)
    unexpected_missing = [p for p in missing if not p.startswith('releases/chatgpt-project-sources/')
                          or not p.endswith(':Zone.Identifier')]
    data = {'reviewer': 'independent C', 'starting_members': len(rows),
            'byte_unchanged': len(rows)-len(changed)-len(missing),
            'changed': changed, 'missing': missing, 'same_bytes_changed_mtime': mtimes,
            'unapproved_mutations': unexpected, 'unapproved_missing': unexpected_missing,
            'metadata_relocation_independently_verified_in': 'metadata-independent-checks.json',
            'scope': 'All starting inventory entries, including raw, results, frozen evidence, notebooks, user ZIPs, memory, Process, Skill and templates. New outputs are reviewed separately.',
            'status': 'VERIFIED' if not unexpected and not unexpected_missing and not mtimes else 'NEEDS_REVIEW'}
    (OUT/'full-starting-inventory-audit.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k != 'changed'}, ensure_ascii=False, indent=2))
    assert not unexpected and not unexpected_missing and not mtimes


if __name__ == '__main__':
    main()
