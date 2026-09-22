"""Sync the approved source inventory, preserving the original Skill distribution."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MIRROR = ROOT / 'releases/chatgpt-project-sources'
# These mappings were verified by content/archive inspection, not filename inference.
SOURCES = [
    ('Interaction Evidence Protocol', 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL_v2_2(1).md', 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md', 'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md', 'PROJECT_SOURCE'),
    ('Visual System', 'SMART_CITIES_VISUAL_SYSTEM(3).md', 'SMART_CITIES_VISUAL_SYSTEM.md', 'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md', 'PROJECT_SOURCE'),
    ('Research Protocol', '未上传（本轮新增）', 'SMART_CITIES_RESEARCH_PROTOCOL.md', 'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md', 'NEW_PROJECT_SOURCE_TO_UPLOAD'),
    ('Engineering governance', '未声明已上传', 'AGENTS.md', 'AGENTS.md', 'SUPPORTING_GOVERNANCE'),
    ('Process reference PDF', 'Process_Report_P2_Locked_v1(3).pdf', 'Process_Report_P2_Locked_v1.pdf', 'templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf', 'PROJECT_SOURCE'),
    ('Experiment reference PDF', 'Experiment_Report_P2_Exact(4).pdf', 'Experiment_Report_P2_Exact.pdf', 'templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf', 'PROJECT_SOURCE'),
    ('Teacher slides', '实验课1(1).pptx', '实验课1.pptx', 'task1/实验课1.pptx', 'PROJECT_SOURCE'),
    ('Teacher assignment archive', '作业(1).zip', '作业.zip', 'task1/作业.zip', 'PROJECT_SOURCE'),
    ('LLM starter notebook', '任务3_LLM辅助评估清洗.ipynb', '任务3_LLM辅助评估清洗.ipynb', 'task1/作业/作业/任务3_LLM辅助评估清洗.ipynb', 'PROJECT_SOURCE'),
    ('Trajectory starter notebook', '作业1轨迹数据预处理.ipynb', '作业1轨迹数据预处理.ipynb', 'task1/作业/作业/作业1轨迹数据预处理.ipynb', 'PROJECT_SOURCE'),
    ('Publication plotting archive', 'publication-plots.zip', 'publication-plots.zip', 'releases/chatgpt-project-sources/publication-plots.zip', 'DISTRIBUTION_ARCHIVE'),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    MIRROR.mkdir(exist_ok=True)
    date = datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    previous = OUT / 'source-inventory.json'
    old = {r['canonical']: r for r in json.loads(previous.read_text())} if previous.exists() else {}
    rows = []
    for logical, display, canonical, source, role in SOURCES:
        src, dst = ROOT / source, MIRROR / canonical
        if canonical == 'publication-plots.zip':
            # This is the historically verified original, not the sanitized release ZIP.
            assert sha(src) == 'b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041'
        equal = dst.exists() and src.read_bytes() == dst.read_bytes()
        status = 'UNCHANGED_VERIFIED' if equal else 'UPDATED_THIS_RUN'
        if src != dst and not equal:
            shutil.copyfile(src, dst)
        digest = sha(dst)
        assert digest == sha(src)
        if canonical in old and old[canonical]['sha256'] == digest:
            status = old[canonical]['status']
        rows.append(dict(logical=logical, display=display, canonical=canonical, source=source,
                         role=role, sha256=digest, status=status, date=date))
    previous.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    text = '''# ChatGPT Project Sources — Source Manifest

This fixed directory is a distribution / synchronization / upload convenience mirror, not a second active source of truth. Governance edits happen in installed sources first; mirror bytes and hashes must then match. Project Settings remains user-maintained in ChatGPT UI and is not copied. WORKFLOW_EVIDENCE_PLAN is internal and is not included.

Display filenames below are the user-declared current ChatGPT inventory; they preserve the original upload-name mapping. Local synchronization does not claim an upload or modification in the ChatGPT UI. Research Protocol is a new source to upload; AGENTS is supporting governance, not a claim of an existing upload. Canonical filenames omit duplicate-upload suffixes.

| Logical Source | ChatGPT Display Filename | Canonical Mirror Filename | Active Repo Source | Role | SHA256 | Sync Status | Last Verified Date |
|---|---|---|---|---|---|---|---|
'''
    for r in rows:
        text += f"| {r['logical']} | {r['display']} | [{r['canonical']}]({r['canonical']}) | [source](../../{r['source']}) `{r['source']}` | {r['role']} | `{r['sha256']}` | {r['status']} | {r['date']} |\n"
    text += '''
## Verification and provenance

- Governance versions: Research Protocol v1.0; Evidence Protocol v2.3; Visual System v2.2; AGENTS current. Their installed paths remain authoritative. Document links retain valid repository targets from both active and mirrored locations; AGENTS uses repository URLs because its mirror is at a different depth.
- Process PDF is the freshly compiled installed template preview. Experiment PDF is copied from its unchanged installed preview. Both are synthetic/template references, not task results.
- Teacher slides and assignment ZIP are the existing tracked task1 originals. Slides were opened as OOXML and their course/experiment content inspected. Both notebooks were parsed as JSON and byte-compared against their corresponding original assignment ZIP members; no notebook was executed. Supplied outputs remain historical/pre-generated, not current-run experiment results.
- `publication-plots.zip` is the existing original Project Source distribution/archive, retained byte-for-byte at its existing location. Its source entry intentionally points to this retained original archive; it is verified against the historical original SHA256 and all six effective installed files, not by self-comparison alone. `releases/skills/publication-plots.zip` is the separately retained metadata-sanitized distribution (SHA256 `2648e19b1854e120421e52eef14a31900fd7fb6d1cce7f549744e530f9e60325`); its six effective files are identical. No ZIP was repackaged this run. Runtime Skill source remains `tools/skills/publication-plots/`.
- The old Design System v2.1 ZIP is a historical archive, not the source of current governance or Process preview.
- `SOURCE_MANIFEST.md` does not hash itself. Eleven payload files are verified individually with `sha256sum`; all source mappings and verification evidence are in [this run's evidence](../../evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/README.md).

No missing sources. All eleven required logical sources are available. `UPDATED_THIS_RUN` means the local mirror was created/refreshed, not that ChatGPT UI files were replaced.
'''
    (MIRROR / 'SOURCE_MANIFEST.md').write_text(text)
    result = subprocess.run(['sha256sum', *[r['canonical'] for r in rows]], cwd=MIRROR,
                            text=True, capture_output=True, check=True)
    (OUT / 'mirror-sha256.txt').write_text(result.stdout)
    print(f'{len(rows)} sources synchronized and SHA256 verified')

if __name__ == '__main__':
    main()
