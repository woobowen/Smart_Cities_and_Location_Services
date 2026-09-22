"""Maintain the exact 11-file ChatGPT upload bundle; metadata stays internal."""
from pathlib import Path, PurePosixPath
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[3]
BUNDLE_PATH = Path('releases/chatgpt-project-sources')
INTERNAL_PATH = Path('evidence/infrastructure/chatgpt-project-source-sync')
SKILL_SHA256 = 'b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041'
# Logical source, canonical filename, active path, historical UI name (not UI state).
SOURCES = (
    ('Research Protocol', 'SMART_CITIES_RESEARCH_PROTOCOL.md', 'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md', 'Not declared uploaded at baseline'),
    ('Interaction Evidence Protocol', 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md', 'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md', 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL_v2_2(1).md'),
    ('Visual System', 'SMART_CITIES_VISUAL_SYSTEM.md', 'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md', 'SMART_CITIES_VISUAL_SYSTEM(3).md'),
    ('Engineering governance', 'AGENTS.md', 'AGENTS.md', 'Not declared uploaded at baseline'),
    ('Process reference PDF', 'Process_Report_P2_Locked_v1.pdf', 'templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf', 'Process_Report_P2_Locked_v1(3).pdf'),
    ('Experiment reference PDF', 'Experiment_Report_P2_Exact.pdf', 'templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf', 'Experiment_Report_P2_Exact(4).pdf'),
    ('Teacher slides', '实验课1.pptx', 'task1/实验课1.pptx', '实验课1(1).pptx'),
    ('Teacher assignment archive', '作业.zip', 'task1/作业.zip', '作业(1).zip'),
    ('LLM starter notebook', '任务3_LLM辅助评估清洗.ipynb', 'task1/作业/作业/任务3_LLM辅助评估清洗.ipynb', '任务3_LLM辅助评估清洗.ipynb'),
    ('Trajectory starter notebook', '作业1轨迹数据预处理.ipynb', 'task1/作业/作业/作业1轨迹数据预处理.ipynb', '作业1轨迹数据预处理.ipynb'),
    ('Publication plotting distribution', 'publication-plots.zip', 'releases/chatgpt-project-sources/publication-plots.zip', 'publication-plots.zip'),
)
ALLOWLIST = frozenset(row[1] for row in SOURCES)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_skill(root):
    archive = root / BUNDLE_PATH / 'publication-plots.zip'
    require(archive.is_file() and not archive.is_symlink(), 'Missing/invalid original Skill archive')
    require(sha(archive.read_bytes()) == SKILL_SHA256, 'Original Skill archive SHA256 mismatch; do not repackage')
    installed = root / 'tools/skills/publication-plots'
    expected = {p.relative_to(installed).as_posix(): p.read_bytes()
                for p in installed.rglob('*') if p.is_file()
                and '__pycache__' not in p.parts and p.name != '.DS_Store'
                and not p.name.endswith(':Zone.Identifier')}
    payload = {}
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            name = PurePosixPath(item.filename)
            require(not name.is_absolute() and '..' not in name.parts, 'Unsafe archive member')
            if item.is_dir() or '__MACOSX' in name.parts or name.name == '.DS_Store':
                continue
            require(name.parts[0] == 'publication-plots', 'Unexpected Skill archive root')
            relative = PurePosixPath(*name.parts[1:]).as_posix()
            require(relative not in payload, 'Duplicate effective Skill member')
            payload[relative] = z.read(item)
    require(payload == expected and bool(payload), 'Skill archive effective members differ from installed source')
    return len(payload)


def source_rows(root):
    require(len(ALLOWLIST) == len(SOURCES) == 11, 'Invalid upload allowlist')
    verify_skill(root)
    rows = []
    for logical, name, source, previous in SOURCES:
        src = root / source
        require(src.is_file() and not src.is_symlink(), f'Missing/invalid active source: {source}')
        rows.append(dict(logical=logical, filename=name, source=source,
                         bundle=(BUNDLE_PATH / name).as_posix(), role='PROJECT_SOURCE',
                         sha256=sha(src.read_bytes()), previous=previous))
    return rows


def verify_bundle(root):
    rows = source_rows(root)
    bundle = root / BUNDLE_PATH
    entries = list(bundle.iterdir())
    require({p.name for p in entries} == ALLOWLIST, 'UPLOAD_BUNDLE_INVALID: directory must contain exactly the 11 allowlisted names')
    require(all(p.is_file() and not p.is_symlink() for p in entries), 'UPLOAD_BUNDLE_INVALID: only ordinary files allowed')
    for row in rows:
        src, dst = root / row['source'], root / row['bundle']
        require(src.read_bytes() == dst.read_bytes(), f'Active != Bundle: {row["filename"]}')
        require(sha(dst.read_bytes()) == row['sha256'], f'Bundle hash mismatch: {row["filename"]}')
    return rows


def manifest_text(rows, date):
    text = '''# Upload Bundle Manifest

The upload-ready directory is `releases/chatgpt-project-sources/`. Every one of its exactly 11 ordinary files is intended for upload, including AGENTS. All roles are PROJECT_SOURCE. This manifest describes the repository upload bundle, not the current ChatGPT UI state; Previous ChatGPT Display Filename is historical mapping only.

Active sources remain authoritative. Update active sources first, then synchronize distribution bytes. Project Settings stays in ChatGPT UI. This manifest, upload instructions, sync tools, logs and WORKFLOW_EVIDENCE_PLAN remain outside the upload bundle. Versions are managed by Git commits, not duplicate directory/file names.

| Logical Source | Canonical Upload Filename | Active Repo Source | Upload Bundle Path | Role | SHA256 | Active == Bundle | Last Verified Date | Previous ChatGPT Display Filename |
|---|---|---|---|---|---|---|---|---|
'''
    for r in rows:
        text += (f'| {r["logical"]} | `{r["filename"]}` | [{r["source"]}](../../../{r["source"]}) '
                 f'| [{r["bundle"]}](../../../{r["bundle"]}) | PROJECT_SOURCE | `{r["sha256"]}` '
                 f'| YES | {date} | {r["previous"]} |\n')
    text += '''
The publication-plots source intentionally names the retained original distribution in the bundle. Its independent verification is the fixed approved SHA256 plus byte comparison of all effective archive members against `tools/skills/publication-plots/`; self-comparison alone is insufficient. Runtime source remains the installed Skill. No archive is repackaged.

The two PDFs are canonical template/reference previews, not current-run experiment results. Teacher PPTX/ZIP and both notebooks are copied as bytes; no notebook is re-saved or executed. No Project Sources upload or Project Settings edit is performed by the sync tool.

See [upload instructions](UPLOAD_INSTRUCTIONS.md) and [engineering verification](README.md). The manifest is internal and does not hash itself.
'''
    return text


def verify_manifest(root, rows):
    text = (root / INTERNAL_PATH / 'SOURCE_MANIFEST.md').read_text()
    import re
    dates = re.findall(r'\| YES \| (\d{4}-\d{2}-\d{2}) \|', text)
    require(len(dates) == 11 and len(set(dates)) == 1, 'Manifest requires 11 dated, verified rows')
    require(text == manifest_text(rows, dates[0]), 'Manifest content/roles/hashes are stale')


def sync(root=ROOT):
    # Verify all inputs before changing any destination or removing any extra file.
    rows = source_rows(root)
    bundle = root / BUNDLE_PATH
    require(bundle.is_dir() and not bundle.is_symlink(), 'Invalid bundle directory')
    entries = list(bundle.iterdir())
    require(all(p.is_file() and not p.is_symlink() for p in entries),
            'UPLOAD_BUNDLE_INVALID: unexpected directory/symlink; inspect before cleanup')
    updated = []
    for row in rows:
        src, dst = root / row['source'], root / row['bundle']
        if src != dst and (not dst.exists() or src.read_bytes() != dst.read_bytes()):
            shutil.copyfile(src, dst)
            updated.append(row['filename'])
    removed = []
    for p in entries:
        if p.name not in ALLOWLIST:
            p.unlink()  # Only direct ordinary files inside the authorized upload directory.
            removed.append(p.name)
    rows = verify_bundle(root)
    internal = root / INTERNAL_PATH
    internal.mkdir(parents=True, exist_ok=True)
    date = datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    (internal / 'SOURCE_MANIFEST.md').write_text(manifest_text(rows, date))
    verify_manifest(root, rows)
    return {'status': 'UPLOAD BUNDLE READY', 'file_count': 11, 'updated': updated,
            'removed': sorted(removed), 'hashes': {r['filename']: r['sha256'] for r in rows}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify exact set, active bytes, archive and internal manifest without writing')
    args = parser.parse_args()
    if args.check:
        rows = verify_bundle(ROOT)
        verify_manifest(ROOT, rows)
        print('UPLOAD_BUNDLE_CONTENT: PASS; EXACTLY 11; internal manifest verified')
    else:
        print(json.dumps(sync(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
