"""Independent C adversarial fixtures for the migrated sync tool; no real bundle writes."""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SCRIPT = Path('evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py')
spec = importlib.util.spec_from_file_location('c_sync_under_test', ROOT / SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snap(root):
    records = {}
    for p in root.rglob('*'):
        if p.is_symlink():
            records[p.relative_to(root).as_posix()] = ['symlink', os.readlink(p)]
        elif p.is_file():
            records[p.relative_to(root).as_posix()] = ['file', p.stat().st_mtime_ns, sha(p.read_bytes())]
        elif p.is_dir():
            records[p.relative_to(root).as_posix()] = ['directory']
    return records


def row(name, path, data):
    return dict(canonical_name=name, active_path=path, project_source=True,
                semantic_role='C_TEST_ONLY', scope='isolated C fixture', version='c-test',
                sha256=sha(data), pair_id=None, approval_scope='fixture only', supersedes=None)


def set_declaration(root, rows):
    (root / sync.DECLARATION_PATH).write_text(json.dumps(dict(
        schema_version=1, approval='C fixture', revision_date='2026-09-29', sources=rows)))


def fixture(parent, name):
    root = parent / name
    (root / sync.INTERNAL_PATH).mkdir(parents=True)
    (root / sync.BUNDLE_PATH).mkdir(parents=True)
    (root / 'inputs').mkdir()
    (root / SCRIPT).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / SCRIPT, root / SCRIPT)
    (root / 'inputs/plain.md').write_bytes(b'C approved text\r\n')
    (root / 'inputs/blob.bin').write_bytes(b'\x00\xff\x10C binary')
    shutil.copy2(ROOT / sync.BUNDLE_PATH / 'publication-plots.zip', root / sync.BUNDLE_PATH / 'publication-plots.zip')
    shutil.copytree(ROOT / 'tools/skills/publication-plots', root / 'tools/skills/publication-plots',
                    ignore=shutil.ignore_patterns('__pycache__'))
    rows = [row('plain.md', 'inputs/plain.md', b'C approved text\r\n'),
            row('blob.bin', 'inputs/blob.bin', b'\x00\xff\x10C binary'),
            row('publication-plots.zip', str(sync.BUNDLE_PATH / 'publication-plots.zip'),
                (root / sync.BUNDLE_PATH / 'publication-plots.zip').read_bytes())]
    set_declaration(root, rows)
    sync.sync(root)
    return root, rows


def reject_no_target_change(parent, name, mutation):
    root, rows = fixture(parent, name)
    (root / sync.BUNDLE_PATH / 'plain.md').write_bytes(b'old target deliberately differs')
    mutation(root, rows)
    before = snap(root / sync.BUNDLE_PATH)
    try:
        sync.sync(root)
    except (ValueError, RuntimeError, OSError) as exc:
        assert snap(root / sync.BUNDLE_PATH) == before, name
        return dict(name=name, rejected=True, target_bytes_mtimes_and_symlinks_unchanged=True, error=str(exc))
    raise AssertionError(f'{name}: unexpected acceptance')


def main():
    parent = OUT / 'build' / 'sync-probes'
    if parent.exists():
        raise SystemExit('Do not overwrite an existing C fixture run')
    parent.mkdir(parents=True)
    results = []
    root, rows = fixture(parent, 'positive-cli')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    before = snap(root)
    for args in (['--plan'], ['--check'], []):
        proc = subprocess.run([sys.executable, str(root / SCRIPT), *args], cwd=root, env=env,
                              text=True, capture_output=True)
        assert proc.returncode == 0, proc.stderr
        assert snap(root) == before, f'CLI {args} mutated fixture'
        results.append(dict(name=f'CLI {args or "no-change sync"}', exit_code=proc.returncode,
                            entire_fixture_bytes_mtimes_unchanged=True, stdout=proc.stdout))
    (root / 'inputs/dummy.extra').write_bytes(b'future approved member')
    rows.append(row('dummy.extra', 'inputs/dummy.extra', b'future approved member'))
    set_declaration(root, rows)
    extended = sync.sync(root)
    assert extended['file_count'] == 4 and len(sync.verify_bundle(root)) == 4
    results.append(dict(name='explicit future dummy member', file_count=4, hardcoded_count_absent=True))

    def bad_hash(root, rows):
        rows[1]['sha256'] = '0' * 64
        set_declaration(root, rows)
    results.append(reject_no_target_change(parent, 'hash_mismatch_before_any_write', bad_hash))
    results.append(reject_no_target_change(parent, 'missing_later_source_before_any_write', lambda r, _: (r / 'inputs/blob.bin').unlink()))
    results.append(reject_no_target_change(parent, 'unknown_regular_file', lambda r, _: (r / sync.BUNDLE_PATH / 'keep-user.txt').write_bytes(b'keep me')))
    results.append(reject_no_target_change(parent, 'dangling_target_symlink', lambda r, _: (r / sync.BUNDLE_PATH / 'dangling').symlink_to(r / 'absent')))
    results.append(reject_no_target_change(parent, 'unexpected_directory', lambda r, _: (r / sync.BUNDLE_PATH / 'personal').mkdir()))
    def duplicate(root, rows):
        rows[1]['canonical_name'] = rows[0]['canonical_name']
        set_declaration(root, rows)
    results.append(reject_no_target_change(parent, 'duplicate_canonical_name', duplicate))
    def traversal(root, rows):
        rows[1]['active_path'] = 'inputs/../outside'
        set_declaration(root, rows)
    results.append(reject_no_target_change(parent, 'active_path_traversal', traversal))
    def parent_symlink(root, _):
        (root / 'inputs').rename(root / 'real_inputs')
        (root / 'inputs').symlink_to(root / 'real_inputs', target_is_directory=True)
    results.append(reject_no_target_change(parent, 'source_parent_symlink', parent_symlink))

    root, rows = fixture(parent, 'late-metadata-failure')
    (root / sync.BUNDLE_PATH / 'plain.md').write_bytes(b'old plain')
    (root / sync.BUNDLE_PATH / 'blob.bin').write_bytes(b'old blob')
    (root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').write_text('old manifest')
    before_bundle = snap(root / sync.BUNDLE_PATH)
    before_manifest = ((root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').read_bytes(),
                       (root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').stat().st_mtime_ns)
    original_replace = sync.os.replace
    def fail_on_metadata(src, dst):
        if str(src).endswith('.new') and Path(dst).name == 'SOURCE_MANIFEST.md':
            raise OSError('C injected metadata replacement failure after bundle updates')
        return original_replace(src, dst)
    sync.os.replace = fail_on_metadata
    try:
        sync.sync(root)
        raise AssertionError('late metadata failure accepted')
    except RuntimeError:
        assert snap(root / sync.BUNDLE_PATH) == before_bundle
        current_manifest = ((root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').read_bytes(),
                            (root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').stat().st_mtime_ns)
        assert current_manifest == before_manifest
        recovery = list((root / sync.INTERNAL_PATH).glob('.sync-transaction-*/recovery.json'))
        assert len(recovery) == 1 and json.loads(recovery[0].read_text())['state'] == 'ROLLED_BACK'
        results.append(dict(name='failure after both bundle swaps, before metadata',
                            entire_bundle_and_manifest_bytes_mtimes_restored=True,
                            recovery_state='ROLLED_BACK'))
    finally:
        sync.os.replace = original_replace
    result = dict(reviewer='independent C', script_sha256=sha((ROOT / SCRIPT).read_bytes()),
                  real_bundle_write_calls=0, probes=results, all_passed=True)
    (OUT / 'independent-sync-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
