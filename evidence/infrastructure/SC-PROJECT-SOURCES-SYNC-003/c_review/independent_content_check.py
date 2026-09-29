"""Independent C byte/set/preservation checks. Does not trust sync's own PASS."""
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
TASK = OUT.parent
EXPECTED_NAMES = {
    'AGENTS.md', 'SMART_CITIES_RESEARCH_PROTOCOL.md', 'SMART_CITIES_REPORT_WRITING_GUIDE.md',
    'SMART_CITIES_VISUAL_SYSTEM.md', 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md',
    'Experiment_Report_P2_Exact.pdf', 'Process_Report_P2_Locked_v1.pdf',
    'WF_WorkflowConstruction_PreTask1_REVISED.pdf', 'WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip',
    'Experiment_Report_吴博闻_10245102410.pdf', 'Experiment_Report_完整重构_源文件.zip',
    '实验课1.pptx', '作业.zip', '任务3_LLM辅助评估清洗.ipynb', '作业1轨迹数据预处理.ipynb', 'publication-plots.zip',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    declaration = ROOT / 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
    rows = json.loads(declaration.read_text())['sources']
    bundle = ROOT / 'releases/chatgpt-project-sources'
    assert len(rows) == len(EXPECTED_NAMES)
    assert {r['canonical_name'] for r in rows} == EXPECTED_NAMES == {p.name for p in bundle.iterdir()}
    original = {Path(r['path']).name: r for r in json.loads((TASK / 'received-release-inventory.json').read_text())}
    checks = []
    targets = {declaration}
    diff = []
    for r in rows:
        p, q = ROOT / r['active_path'], bundle / r['canonical_name']
        assert p.is_file() and q.is_file() and not p.is_symlink() and not q.is_symlink()
        active_bytes, bundle_bytes = p.read_bytes(), q.read_bytes()
        assert active_bytes == bundle_bytes and sha(active_bytes) == r['sha256']
        changed = sha(bundle_bytes) != original[r['canonical_name']]['sha256']
        assert changed == (q.suffix == '.md')
        checks.append(dict(name=q.name, active=r['active_path'], active_sha256=sha(active_bytes),
                           bundle_sha256=sha(bundle_bytes), changed_from_received=changed))
        targets.update([p, q])
        if q.suffix == '.md':
            before = (TASK / 'received' / q.name).read_text()
            after = p.read_text()
            diff.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                           fromfile='received/'+q.name, tofile=r['active_path']))
    for name in ('SOURCE_MANIFEST.md', 'UPLOAD_INSTRUCTIONS.md'):
        targets.add(declaration.parent / name)
    before = {str(p.relative_to(ROOT)): [sha(p.read_bytes()), p.stat().st_mtime_ns] for p in targets}
    command = [str(ROOT / '.venv/bin/python'), 'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py', '--check']
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    after = {str(p.relative_to(ROOT)): [sha(p.read_bytes()), p.stat().st_mtime_ns] for p in targets}
    assert result.returncode == 0 and before == after
    skill = bundle / 'publication-plots.zip'
    assert sha(skill.read_bytes()) == 'b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041'
    installed = ROOT / 'tools/skills/publication-plots'
    expected = {p.relative_to(installed).as_posix(): p.read_bytes() for p in installed.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store' and not p.name.endswith(':Zone.Identifier')}
    with zipfile.ZipFile(skill) as z:
        payload = {PurePosixPath(*PurePosixPath(n).parts[1:]).as_posix(): z.read(n) for n in z.namelist()
                   if not n.endswith('/') and '__MACOSX' not in PurePosixPath(n).parts and PurePosixPath(n).name != '.DS_Store'}
    assert expected == payload and payload
    protected = json.loads((TASK / 'starting-protection-inventory.json').read_text())
    protect_prefixes = ('task1/workflow/', 'task1/config/', 'task1/data/', 'task1/notebooks/', 'task1/memory/',
                        'task1/evidence/goal1/', 'task1/evidence/goal2/', 'task1/evidence/goal3/runs/',
                        'task1/reports/process1/', 'reports/process-report/', 'tools/skills/')
    preserved = []
    for item in protected:
        path = item['path']
        special = path == 'templates/latex/common/p2_cloud_sorbet_colors.tex' or (
            path.startswith('templates/') and not path.endswith('README.md')) or (
            '/' not in path and path.endswith('.zip'))
        if path.startswith(protect_prefixes) or special:
            p = ROOT / path
            assert p.is_file() and sha(p.read_bytes()) == item['sha256'], f'Protected mutation: {path}'
            preserved.append(path)
    data = dict(reviewer='independent C', expected_set_from='approved Prompt section 9',
                member_count=len(checks), members=checks,
                actual_check_command=command, check_exit=result.returncode,
                check_stdout=result.stdout, checked_sources_bundle_metadata_bytes_mtimes_unchanged=before == after,
                independently_verified_skill_members=len(payload), protected_files_verified=len(preserved),
                protected_prefixes=list(protect_prefixes), extra_protection='all non-README templates; root ZIP inputs; public P2 source',
                status='VERIFIED_WITHIN_RECORDED_SCOPE')
    (OUT / 'independent-content-results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    (OUT / 'received-to-active-reviewed.diff').write_text(''.join(diff))
    print(json.dumps({k:v for k,v in data.items() if k != 'members'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
