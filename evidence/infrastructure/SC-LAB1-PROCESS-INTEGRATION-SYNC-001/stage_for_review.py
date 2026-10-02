"""Stage only this task's reviewed whitelist; never blanket-add the workspace."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
TASK = 'evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/'
EXACT = {
    'AGENTS.md', 'README.md',
    'docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md',
    'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md',
    'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md',
    'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',
    'releases/skills/publication-plots-approved-original.zip',
    'task1/README.md', 'task1/docs/goal3/TECHNICAL_HANDOFF.md',
    'task1/evidence/goal3/REVIEW_PACKET.md', 'task1/config/assignment.json',
    'task1/goal3/PACKAGE_README.md', 'task1/goal3/__main__.py',
    'task1/goal3/package.py', 'task1/goal3/identity.py',
    'task1/reports/README.md', 'task1/reports/build_reports.py',
    'task1/reports/build_process.py', 'task1/reports/metadata.tex',
    'task1/tests/test_accepted_report_integration.py',
    'task1/tests/test_closeout_identity.py', 'task1/tests/test_process_report_build.py',
    'task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_完整双报告.zip',
    'Experiment_Report_完整重构_源文件.zip', 'Process_Report_Revised.pdf',
    'Process_Report_Revised_LaTeX_Source.zip',
    'SC-LAB1-G1-CLOSURE-002_HANDOFF.zip', 'SC-LAB1-G1-COMPLETE-001_HANDOFF.zip',
}
EXACT |= {'evidence/infrastructure/chatgpt-project-source-sync/' + p for p in
          ('sources.json', 'SOURCE_MANIFEST.md', 'UPLOAD_INSTRUCTIONS.md', 'README.md', 'test_sync_sources.py')}
BASELINE = (ROOT / TASK / 'approved_input_sha256.txt').read_text().splitlines()
EXACT |= {'releases/chatgpt-project-sources/' + line.split('  ', 1)[1] for line in BASELINE}
EXACT |= {'releases/chatgpt-project-sources/' + p for p in (
    'WF_WorkflowConstruction_PreTask1_REVISED.pdf',
    'WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip', 'Process_Report_P2_Locked_v1.pdf')}
PREFIXES = (TASK, 'task1/reports/process1/', 'reports/process-report/experiment1-revised/',
            'templates/latex/process-report/')

def names(*args):
    return subprocess.check_output(['git', *args, '-z'], cwd=ROOT).decode().split('\0')[:-1]

candidates = sorted(set(names('diff', '--no-renames', '--name-only', 'HEAD') +
                        names('diff', '--no-renames', '--name-only') +
                        names('ls-files', '--others', '--exclude-standard')))
unrelated = [p for p in candidates if p not in EXACT and not p.startswith(PREFIXES)]
if unrelated:
    raise SystemExit('Unrelated paths left untouched; review required: ' + repr(unrelated))
# A deletion already staged is absent from both the index and the filesystem.
# Preserve that staged deletion instead of passing its nonexistent path to add.
index_paths = set(names('ls-files'))
already_staged_deletions = [p for p in candidates if not (ROOT / p).exists() and p not in index_paths]
candidates = [p for p in candidates if p not in already_staged_deletions]
for start in range(0, len(candidates), 150):
    subprocess.run(['git', 'add', '--', *candidates[start:start+150]], cwd=ROOT, check=True)
# Preserve substantive actual command logs despite the general LaTeX *.log rule.
logs = sorted(str(p.relative_to(ROOT)) for directory in (ROOT/TASK, ROOT/'task1/reports/process1/source')
              for p in directory.rglob('*.log') if p.is_file() and not p.is_symlink())
for start in range(0, len(logs), 150):
    subprocess.run(['git', 'add', '-f', '--', *logs[start:start+150]], cwd=ROOT, check=True)
print(json.dumps({'staged_candidate_count': len(candidates), 'explicit_substantive_logs': len(logs),
                  'preserved_staged_deletions': already_staged_deletions,
                  'unrelated_paths': unrelated, 'blanket_add_used': False}, ensure_ascii=False))
