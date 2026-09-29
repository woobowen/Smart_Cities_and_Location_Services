"""Behavioral safety tests; fixtures never modify the real upload directory."""
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py'
spec = importlib.util.spec_from_file_location('sync_sources', SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def row(name, source, content):
    return dict(canonical_name=name, active_path=source, sha256=sync.sha(content), project_source=True,
                semantic_role='test_only', scope='temporary fixture', version='test', pair_id=None,
                approval_scope='explicit temporary fixture', supersedes=None)


@pytest.fixture
def root(tmp_path):
    (tmp_path / sync.INTERNAL_PATH).mkdir(parents=True)
    (tmp_path / sync.BUNDLE_PATH).mkdir(parents=True)
    (tmp_path / 'active').mkdir()
    (tmp_path / 'active/A.md').write_bytes(b'approved A\n')
    (tmp_path / 'active/B.bin').write_bytes(b'\x00\x01\xffapproved B')
    archive = sync.ROOT / sync.BUNDLE_PATH / 'publication-plots.zip'
    shutil.copy2(archive, tmp_path / sync.BUNDLE_PATH / archive.name)
    shutil.copytree(sync.ROOT / 'tools/skills/publication-plots', tmp_path / 'tools/skills/publication-plots',
                    ignore=shutil.ignore_patterns('__pycache__'))
    rows = [row('A.md', 'active/A.md', b'approved A\n'),
            row('B.bin', 'active/B.bin', b'\x00\x01\xffapproved B'),
            row(archive.name, str(sync.BUNDLE_PATH / archive.name), archive.read_bytes())]
    (tmp_path / sync.DECLARATION_PATH).write_text(json.dumps(dict(schema_version=1, approval='TEST',
                                                               revision_date='2026-09-29', sources=rows)))
    return tmp_path


def snapshot(path):
    return {p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in path.rglob('*') if p.is_file() and not p.is_symlink()}


def edit_declaration(root, update):
    path = root / sync.DECLARATION_PATH
    data = json.loads(path.read_text())
    update(data)
    path.write_text(json.dumps(data))


def test_positive_readonly_and_idempotent(root):
    plan = sync.difference_plan(root)
    assert plan['safe_to_sync'] and set(plan['add']) == {'A.md', 'B.bin'}
    result = sync.sync(root)
    assert result['file_count'] == len(sync.declaration(root)['sources'])
    before = snapshot(root)
    sync.verify_manifest(root, sync.verify_bundle(root))
    assert snapshot(root) == before
    assert sync.sync(root)['updated'] == []
    assert snapshot(root) == before
    assert sync.difference_plan(root)['change'] == []


def test_declared_dummy_member_uses_dynamic_count(root):
    sync.sync(root)
    count = len(sync.declaration(root)['sources'])
    (root / 'active/dummy.txt').write_bytes(b'explicit dummy')
    edit_declaration(root, lambda d: d['sources'].append(row('dummy.txt', 'active/dummy.txt', b'explicit dummy')))
    assert sync.sync(root)['file_count'] == count + 1
    assert len(sync.verify_bundle(root)) == count + 1
    assert (root / sync.BUNDLE_PATH / 'dummy.txt').read_bytes() == b'explicit dummy'


@pytest.mark.parametrize('case', ['duplicate', 'missing', 'hash', 'extra', 'directory', 'symlink',
                                 'parent_symlink', 'target_parent_symlink', 'traversal', 'absolute',
                                 'canonical_traversal', 'suffix', 'wrong_skill', 'metadata_symlink'])
def test_invalid_inputs_never_partially_change_targets(root, case):
    sync.sync(root)
    bundle = root / sync.BUNDLE_PATH
    (bundle / 'B.bin').write_bytes(b'stale target must remain on failure')
    if case == 'duplicate':
        edit_declaration(root, lambda d: d['sources'].append(d['sources'][0]))
    elif case == 'missing':
        (root / 'active/A.md').unlink()
    elif case == 'hash':
        (root / 'active/A.md').write_bytes(b'unapproved changed source')
    elif case == 'extra':
        (bundle / 'unexpected.txt').write_bytes(b'user data')
    elif case == 'directory':
        (bundle / 'A.md').unlink()
        (bundle / 'A.md').mkdir()
    elif case == 'symlink':
        (bundle / 'A.md').unlink()
        (bundle / 'A.md').symlink_to(root / 'active/A.md')
    elif case == 'parent_symlink':
        (root / 'active').rename(root / 'real_active')
        (root / 'active').symlink_to(root / 'real_active', target_is_directory=True)
    elif case == 'target_parent_symlink':
        bundle.rename(root / 'real_bundle')
        bundle.symlink_to(root / 'real_bundle', target_is_directory=True)
    elif case in ('traversal', 'absolute'):
        edit_declaration(root, lambda d: d['sources'][0].update(active_path='../escape' if case == 'traversal' else '/tmp/escape'))
    elif case == 'canonical_traversal':
        edit_declaration(root, lambda d: d['sources'][0].update(canonical_name='../escape.md'))
    elif case == 'suffix':
        edit_declaration(root, lambda d: d['sources'][0].update(canonical_name='A(3).md'))
    elif case == 'wrong_skill':
        (bundle / 'publication-plots.zip').write_bytes(b'wrong archive')
    elif case == 'metadata_symlink':
        target = root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md'
        target.unlink()
        target.symlink_to(root / 'active/A.md')
    before = snapshot(bundle)
    with pytest.raises((ValueError, RuntimeError)):
        sync.sync(root)
    assert snapshot(bundle) == before


def test_failure_during_update_rolls_back_bytes_and_mtimes(root, monkeypatch):
    sync.sync(root)
    bundle = root / sync.BUNDLE_PATH
    (bundle / 'A.md').write_bytes(b'old A')
    (bundle / 'B.bin').write_bytes(b'old B')
    before = snapshot(bundle)
    original_replace = sync.os.replace
    calls = 0

    def fail_second(src, dst):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError('injected update failure')
        original_replace(src, dst)

    monkeypatch.setattr(sync.os, 'replace', fail_second)
    with pytest.raises(RuntimeError, match='recovery information'):
        sync.sync(root)
    assert snapshot(bundle) == before
    records = list((root / sync.INTERNAL_PATH).glob('.sync-transaction-*/recovery.json'))
    assert len(records) == 1 and json.loads(records[0].read_text())['state'] == 'ROLLED_BACK'


def test_plan_reports_missing_extra_and_unsafe_without_writes(root):
    (root / 'active/A.md').unlink()
    (root / sync.BUNDLE_PATH / 'unknown').mkdir()
    before = snapshot(root)
    plan = sync.difference_plan(root)
    assert not plan['safe_to_sync']
    assert plan['missing'] == ['active/A.md']
    assert plan['unexpected'] == ['unknown'] and plan['unsafe'] == ['unknown']
    assert snapshot(root) == before


def test_stale_metadata_check_is_readonly(root):
    sync.sync(root)
    (root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').write_text('stale')
    before = snapshot(root)
    with pytest.raises(ValueError, match='Metadata stale'):
        sync.verify_manifest(root, sync.verify_bundle(root))
    assert snapshot(root) == before
