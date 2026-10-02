"""Distribute the approved sources.json set; unknown files are never deleted."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[3]
BUNDLE_PATH = Path('releases/chatgpt-project-sources')
INTERNAL_PATH = Path('evidence/infrastructure/chatgpt-project-source-sync')
DECLARATION_PATH = INTERNAL_PATH / 'sources.json'
SKILL_SHA256 = 'b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(root, relative, *, allow_missing=False, directory=False):
    """Reject traversal and symlinks in every component, including parent paths."""
    require(isinstance(relative, (str, Path)), 'Path must be a relative string')
    raw = str(relative)
    path = PurePosixPath(raw)
    require(raw and '\\' not in raw and not path.is_absolute() and
            all(p not in ('', '.', '..') for p in raw.split('/')), f'Unsafe path: {raw}')
    current = root
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), f'Symlink path: {raw}')
    if current.exists():
        require(current.is_dir() if directory else current.is_file(), f'Wrong file type: {raw}')
    else:
        require(allow_missing, f'Missing source: {raw}')
    return current


def declaration(root):
    data = json.loads(safe_path(root, DECLARATION_PATH).read_text())
    require(data.get('schema_version') == 1, 'Unsupported source declaration')
    rows = data.get('sources')
    require(isinstance(rows, list) and bool(rows), 'Empty or invalid source declaration')
    names = set()
    paths = set()
    fields = {'canonical_name', 'active_path', 'project_source', 'semantic_role', 'scope',
              'version', 'sha256', 'pair_id', 'approval_scope', 'supersedes'}
    for row in rows:
        require(isinstance(row, dict) and fields <= row.keys(), 'Incomplete source metadata')
        name = row['canonical_name']
        require(isinstance(name, str) and name not in ('', '.', '..') and
                '/' not in name and '\\' not in name and not re.search(r'\(\d+\)(?=\.|$)', name),
                f'Noncanonical upload name: {name}')
        require(name not in names, f'Duplicate canonical name: {name}')
        active = row['active_path']
        require(isinstance(active, str), f'Invalid active source path: {name}')
        require(active not in paths, f'Duplicate active source: {active}')
        require(not PurePosixPath(active).is_relative_to(BUNDLE_PATH),
                f'Bundle cannot be an active source: {name}')
        require(isinstance(row['project_source'], bool), f'Invalid Project Source identity: {name}')
        require(re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None, f'Invalid SHA256: {name}')
        names.add(name)
        paths.add(row['active_path'])
    require(any(row['project_source'] for row in rows), 'No approved Project Sources')
    return data


def verify_skill(root, data):
    sources = [r for r in data['sources'] if r['canonical_name'] == 'publication-plots.zip'
               and r['project_source']]
    require(len(sources) == 1, 'Required original Skill archive is not an approved source')
    archive = safe_path(root, sources[0]['active_path'])
    require(sha(archive.read_bytes()) == SKILL_SHA256, 'Original Skill archive SHA256 mismatch; do not repackage')
    installed = safe_path(root, 'tools/skills/publication-plots', directory=True)
    expected = {}
    for p in installed.rglob('*'):
        require(not p.is_symlink(), f'Installed Skill symlink: {p.name}')
        if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store' and not p.name.endswith(':Zone.Identifier'):
            expected[p.relative_to(installed).as_posix()] = p.read_bytes()
    payload = {}
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None, 'Skill archive CRC failure')
        for item in z.infolist():
            name = PurePosixPath(item.filename)
            require(not name.is_absolute() and '..' not in name.parts and '\\' not in item.filename,
                    'Unsafe archive member')
            require(not stat.S_ISLNK(item.external_attr >> 16), 'Skill archive symlink')
            if item.is_dir() or '__MACOSX' in name.parts or name.name == '.DS_Store':
                continue
            require(name.parts[0] == 'publication-plots', 'Unexpected Skill archive root')
            relative = PurePosixPath(*name.parts[1:]).as_posix()
            require(relative not in payload, 'Duplicate effective Skill member')
            payload[relative] = z.read(item)
    require(payload == expected and bool(payload), 'Skill archive effective members differ from installed source')
    return len(payload)


def source_rows(root):
    rows = []
    data = declaration(root)
    for entry in data['sources']:
        source = safe_path(root, entry['active_path'])
        require(sha(source.read_bytes()) == entry['sha256'], f'Active source SHA256 mismatch: {entry["canonical_name"]}')
        if not entry['project_source']:
            continue
        rows.append(dict(entry, filename=entry['canonical_name'], source=entry['active_path'],
                         bundle=(BUNDLE_PATH / entry['canonical_name']).as_posix()))
    verify_skill(root, data)
    return rows


def inspect_bundle(root, names):
    bundle = safe_path(root, BUNDLE_PATH, directory=True)
    entries = list(bundle.iterdir())
    extra = sorted(p.name for p in entries if p.name not in names)
    unsafe = sorted(p.name for p in entries if p.is_symlink() or not p.is_file())
    return entries, extra, unsafe


def manifest_text(rows, data):
    lines = [
        '# Upload Bundle Manifest', '',
        f'批准清单：[sources.json](sources.json)；批准记录 `{data["approval"]}`；修订日期 {data["revision_date"]}。',
        f'本次清单计算得到 **{len(rows)}** 个普通文件。数量由清单推导，未来变更须先批准并更新清单。',
        'PROJECT_SOURCE 是上传身份；下表单独记录语义角色、适用范围、版本、配对和替代关系。此表不声明当前 UI 状态。', '',
        '| Canonical name | Active source | Identity / semantic role | Scope | Version | SHA256 | Pair | Approval / supersedes |',
        '|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        lines.append(f'| `{r["filename"]}` | [{r["source"]}](../../../{r["source"]}) | PROJECT_SOURCE / {r["semantic_role"]} | '
                     f'{r["scope"]} | {r["version"]} | `{r["sha256"]}` | {r["pair_id"] or "—"} | '
                     f'{r["approval_scope"]} / {r["supersedes"] or "—"} |')
    lines += ['',
        '权威源先更新，再分发到 `releases/chatgpt-project-sources/`。`--check` 验证集合、每项来源和目标字节及本表；仅本表存在不代表 bundle 已通过检查。',
        'publication-plots.zip 从表中独立 active source 分发，以固定批准 SHA256 加 installed Skill 全部有效成员独立验证；保留原始字节，不重打包。',
        '合成模板、已验收成品和历史局部材料的身份以每项 semantic role / scope 为准；报告与源包按 pair_id 配对，批准范围不自动推广到新实验、Evidence Lock 或教师提交。',
        '教师材料与 starter 原字节保留；同步不执行 Notebook、实验模型或数值实验。',
        'Project Settings 仅在 UI 维护；metadata、脚本、日志和 UI 补丁不进入 upload bundle。',
        '上传采取[差异更新](UPLOAD_INSTRUCTIONS.md)，不要求删除全部现有 Project Sources。', '']
    historical = [r for r in data['sources'] if not r['project_source']]
    if historical:
        lines += ['## 非上传的保留来源', '',
                  '| Canonical name | Preserved source | Semantic role / scope | SHA256 |',
                  '|---|---|---|---|']
        for r in historical:
            lines.append(f'| `{r["canonical_name"]}` | [{r["active_path"]}](../../../{r["active_path"]}) | '
                         f'{r["semantic_role"]} / {r["scope"]} | `{r["sha256"]}` |')
        lines.append('')
    return '\n'.join(lines)


def instructions_text(rows, data):
    handoff = data.get('current_ui_handoff', '../SC-PROJECT-SOURCES-SYNC-003/handoff/UI_SOURCE_DIFF.md')
    return '\n'.join([
        '# Project Sources 差异更新说明', '',
        f'当前批准集合由 [sources.json](sources.json) 定义，共 {len(rows)} 项；完整来源、角色和 SHA256 见 [manifest](SOURCE_MANIFEST.md)。',
        '1. 修改权威文件后，经批准更新清单的版本和 SHA256，再运行同步工具 `--plan` 查看差异。',
        '2. 运行写同步及 `--check`；所有来源完整、安全且 hash 正确才写入。未知 extra、目录、符号链接不会被删除。',
        f'3. 发布并实际回读固定远程版本后，按 [当前 UI 交接说明]({handoff}) 核对用户实际 UI 版本，再逐项更新。',
        '4. 内容变化的同名文档逐个替换；保留未变有效资料。不删除全部当前 Project Sources，不重复上传未变 PDF/ZIP。',
        '5. UI版本未知时记录 USER_CONFIRMATION_REQUIRED；用户报告已更新时记录 USER_REPORTED_UPDATED，逐项比对其批准输入与最终分发字节。无内容差异时不要求重复上传。', '',
        '生成文件、本地同步、远程核验、UPLOAD_BUNDLE READY、用户实际 UI 上传是五种不同状态。工具只负责前述仓库步骤。',
        '历史 [SYNC-003 UI差异表](../SC-PROJECT-SOURCES-SYNC-003/handoff/UI_SOURCE_DIFF.md) 及 [Settings transfer补丁](../SC-PROJECT-SOURCES-SYNC-003/handoff/PROJECT_SETTINGS_SCOPE_PATCH.md) 仅说明当时输入与交付，不代表当前UI状态或本轮需要重复套用。',
        'Project Settings由用户在UI维护；当前交接不生成第二份active设置或新的长稿。', '',
        '| Canonical upload filename | Semantic role |', '|---|---|',
        *[f'| `{r["filename"]}` | {r["semantic_role"]} |' for r in rows], ''])


def metadata_bytes(root, rows):
    data = declaration(root)
    return {INTERNAL_PATH / 'SOURCE_MANIFEST.md': manifest_text(rows, data).encode(),
            INTERNAL_PATH / 'UPLOAD_INSTRUCTIONS.md': instructions_text(rows, data).encode()}


def verify_bundle(root):
    rows = source_rows(root)
    entries, extra, unsafe = inspect_bundle(root, {r['filename'] for r in rows})
    require(not unsafe and not extra, f'Unsafe or unexpected bundle entries: unsafe={unsafe}, extra={extra}')
    require({p.name for p in entries} == {r['filename'] for r in rows}, 'Bundle members missing')
    for row in rows:
        require((root / row['source']).read_bytes() == (root / row['bundle']).read_bytes(),
                f'Active != Bundle: {row["filename"]}')
    return rows


def verify_manifest(root, rows):
    for path, content in metadata_bytes(root, rows).items():
        require(safe_path(root, path).read_bytes() == content, f'Metadata stale: {path}')


def difference_plan(root):
    result = dict(add=[], change=[], missing=[], unexpected=[], unsafe=[], errors=[], metadata_change=[])
    data = declaration(root)
    names = {r['canonical_name'] for r in data['sources'] if r['project_source']}
    try:
        entries, result['unexpected'], result['unsafe'] = inspect_bundle(root, names)
    except ValueError as exc:
        result['errors'].append(str(exc))
    for r in data['sources']:
        try:
            src = safe_path(root, r['active_path'])
            content = src.read_bytes()
            require(sha(content) == r['sha256'], f'Active source SHA256 mismatch: {r["canonical_name"]}')
            if not r['project_source']:
                continue
            dst = safe_path(root, BUNDLE_PATH / r['canonical_name'], allow_missing=True)
            if not dst.exists():
                result['add'].append(r['canonical_name'])
            elif dst.read_bytes() != content:
                result['change'].append(r['canonical_name'])
        except ValueError as exc:
            result['errors'].append(str(exc))
            if not (root / r['active_path']).exists():
                result['missing'].append(r['active_path'])
    if not result['errors']:
        try:
            rows = source_rows(root)
            for path, value in metadata_bytes(root, rows).items():
                p = safe_path(root, path, allow_missing=True)
                if not p.exists() or p.read_bytes() != value:
                    result['metadata_change'].append(path.as_posix())
        except ValueError as exc:
            result['errors'].append(str(exc))
    result['file_count'] = len(names)
    result['safe_to_sync'] = not (result['errors'] or result['unsafe'] or result['unexpected'])
    return result


def sync(root=ROOT):
    root = Path(root)
    rows = source_rows(root)
    _, extra, unsafe = inspect_bundle(root, {r['filename'] for r in rows})
    require(not extra and not unsafe, f'Refusing mutation: extra={extra}, unsafe={unsafe}')
    targets = {Path(r['bundle']): (root / r['source']).read_bytes() for r in rows}
    targets.update(metadata_bytes(root, rows))
    changed = {}
    for path, content in targets.items():
        dst = safe_path(root, path, allow_missing=True)
        if not dst.exists() or dst.read_bytes() != content:
            changed[path] = content
    if not changed:
        verify_bundle(root)
        verify_manifest(root, rows)
        return dict(status='UPLOAD BUNDLE READY', file_count=len(rows), updated=[], removed=[])
    # Stage every replacement before mutation; keep recoverable backups until verification.
    stage = Path(tempfile.mkdtemp(prefix='.sync-transaction-', dir=root / INTERNAL_PATH))
    originals = {}
    applied = []
    try:
        for i, (path, content) in enumerate(changed.items()):
            dst = root / path
            backup = stage / f'{i}.before'
            if dst.exists():
                shutil.copy2(dst, backup)
                originals[path] = backup
            else:
                originals[path] = None
            (stage / f'{i}.new').write_bytes(content)
        (stage / 'recovery.json').write_text(json.dumps({'state': 'STAGED', 'paths': [str(p) for p in changed]}, indent=2))
        for i, path in enumerate(changed):
            os.replace(stage / f'{i}.new', root / path)
            applied.append(path)
        verify_bundle(root)
        verify_manifest(root, rows)
    except BaseException as exc:
        failures = []
        for path in reversed(applied):
            try:
                backup = originals[path]
                if backup is None:
                    (root / path).unlink()  # Only remove a new file created by this transaction.
                else:
                    os.replace(backup, root / path)
            except OSError as rollback_error:
                failures.append(f'{path}: {rollback_error}')
        (stage / 'recovery.json').write_text(json.dumps({'state': 'ROLLBACK_REQUIRED' if failures else 'ROLLED_BACK',
            'error': str(exc), 'paths': [str(p) for p in changed], 'rollback_errors': failures}, indent=2))
        raise RuntimeError(f'Sync failed; recovery information: {stage / "recovery.json"}') from exc
    shutil.rmtree(stage)  # This exact tool-owned temporary directory only; never a bundle entry.
    return dict(status='UPLOAD BUNDLE READY', file_count=len(rows),
                updated=[p.as_posix() for p in changed], removed=[])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='Read-only set, bytes, hashes, Skill and metadata verification')
    group.add_argument('--plan', action='store_true', help='Read-only additions, changes, missing, unexpected and unsafe inputs')
    args = parser.parse_args()
    try:
        if args.check:
            rows = verify_bundle(ROOT)
            verify_manifest(ROOT, rows)
            result = dict(status='UPLOAD BUNDLE READY', file_count=len(rows), readonly=True)
        elif args.plan:
            result = difference_plan(ROOT)
        else:
            result = sync()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.plan and not result['safe_to_sync']:
            raise SystemExit(1)
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
