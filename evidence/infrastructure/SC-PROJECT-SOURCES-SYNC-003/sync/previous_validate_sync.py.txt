"""Validate the current 13-file upload bundle; historical results stay unchanged."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from urllib.parse import unquote
import sync_sources as sync

ROOT = sync.ROOT
OUT = ROOT / 'evidence/infrastructure/SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002'
REFERENCE_NAMES = ('WF_WorkflowConstruction_PreTask1_REVISED.pdf',
                   'WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip')


def fixture_checks():
    """Exercise cleanup/idempotency and failure-before-mutation in an isolated copy."""
    with tempfile.TemporaryDirectory(prefix='chatgpt-upload-bundle-') as tmp:
        root = Path(tmp)
        for _, name, source, _ in sync.SOURCES:
            src = ROOT / source
            dst = root / source
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        shutil.copytree(ROOT / 'tools/skills/publication-plots', root / 'tools/skills/publication-plots')
        bundle = root / sync.BUNDLE_PATH
        before = {source: sync.sha((root / source).read_bytes()) for _, _, source, _ in sync.SOURCES}
        extras = ['SOURCE_MANIFEST.md', 'README.md', 'WORKFLOW_EVIDENCE_PLAN.md', 'SMART_CITIES_VISUAL_SYSTEM(3).md', '.DS_Store', 'test.py', 'test.log']
        for name in extras:
            (bundle / name).write_text('fixture metadata only\n')
        first = sync.sync(root)
        assert set(first['removed']) == set(extras)
        assert all(sync.sha((root / p).read_bytes()) == h for p, h in before.items())
        manifest_before = (root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').read_bytes()
        second = sync.sync(root)
        assert not second['removed'] and not second['updated']
        assert (root / sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').read_bytes() == manifest_before
        (bundle / 'AGENTS.md').write_text('stale bundle copy\n')
        try:
            sync.verify_bundle(root)
        except ValueError:
            pass
        else:
            raise AssertionError('Stale source copy was accepted')
        assert sync.sync(root)['updated'] == ['AGENTS.md']
        binary_repairs = []
        for name in REFERENCE_NAMES:
            (bundle / name).write_bytes(b'stale binary fixture')
            try:
                sync.verify_bundle(root)
            except ValueError:
                pass
            else:
                raise AssertionError(f'Stale binary was accepted: {name}')
            assert sync.sync(root)['updated'] == [name]
            binary_repairs.append(name)
        assert all(sync.sha((root / p).read_bytes()) == h for p, h in before.items())
        # Verify safety failures happen before any copy or cleanup.
        sentinel = bundle / 'do-not-delete-on-failure.txt'
        sentinel.write_text('keep until prerequisites pass')
        source = root / 'AGENTS.md'
        data = source.read_bytes()
        source.unlink()
        failed = []
        for case in ['missing_source', 'wrong_skill_hash', 'unexpected_directory', 'symlink']:
            if case != 'missing_source':
                source.write_bytes(data)
            archive = bundle / 'publication-plots.zip'
            archive_bytes = archive.read_bytes()
            if case == 'wrong_skill_hash':
                archive.write_bytes(b'invalid fixture archive')
            if case == 'unexpected_directory':
                (bundle / 'build').mkdir()
            if case == 'symlink':
                (bundle / 'link.md').symlink_to(source)
            snapshot = {p.name: p.read_bytes() for p in bundle.iterdir() if p.is_file() and not p.is_symlink()}
            try:
                sync.sync(root)
            except ValueError:
                failed.append(case)
            else:
                raise AssertionError(f'{case} was accepted')
            assert sentinel.exists()
            assert all((bundle / name).read_bytes() == value for name, value in snapshot.items())
            if case == 'wrong_skill_hash':
                archive.write_bytes(archive_bytes)
            if case == 'unexpected_directory':
                (bundle / 'build').rmdir()
            if case == 'symlink':
                (bundle / 'link.md').unlink()
        return {'cleanup_cases': extras, 'idempotent': True, 'stale_copy_repaired': True,
                'binary_copies_repaired': binary_repairs,
                'active_sources_unchanged': True, 'fail_before_mutation': failed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', action='store_true', help='Also compare staged Git bytes with active files and bundle')
    parser.add_argument('--evidence-dir', type=Path, default=OUT,
                        help='Current run directory containing preflight.json; never use a historical run directory')
    args = parser.parse_args()
    out = args.evidence_dir.resolve()
    report = {}
    def check(name, ok, detail=None):
        report[name] = {'pass': bool(ok), 'detail': detail}

    rows = sync.verify_bundle(ROOT)
    sync.verify_manifest(ROOT, rows)
    check('exact_13_ordinary_files_and_names', len(rows) == 13, sorted(sync.ALLOWLIST))
    check('active_bytes_equal_bundle', True, {r['filename']: r['sha256'] for r in rows})
    check('internal_manifest_rows_roles_hashes', len(rows) == 13, {'rows': len(rows), 'role': 'PROJECT_SOURCE'})
    check('publication_plots_hash_and_members', True, {'sha256': sync.SKILL_SHA256, 'effective_members': sync.verify_skill(ROOT)})
    before = json.loads((out / 'preflight.json').read_text())
    # Unrelated, untracked user archives are protected locally but are not distributed.
    absent_local_inputs = {p for p in before.get('unrelated_dirty_files', []) if not (ROOT / p).exists()}
    altered = [p for p, h in before['protected_files'].items()
               if p not in absent_local_inputs and
               (not (ROOT / p).is_file() or sync.sha((ROOT / p).read_bytes()) != h)]
    check('research_templates_task1_skill_history_unrelated_unchanged', not altered,
          {'files_checked': len(before['protected_files']) - len(absent_local_inputs), 'changed': altered,
           'local_only_inputs_not_present_in_this_checkout': sorted(absent_local_inputs)})
    reference_rows = {r['filename']: r for r in rows if r['filename'] in REFERENCE_NAMES}
    check('accepted_reference_pdf_zip_canonical_equal_bundle',
          len(reference_rows) == 2 and all((ROOT / r['source']).read_bytes() == (ROOT / r['bundle']).read_bytes()
                                         for r in reference_rows.values()), reference_rows)
    check('accepted_reference_pdf_zip_approved_bytes_preserved',
          all(reference_rows[n]['sha256'] == before['approved_inputs'][(sync.BUNDLE_PATH / n).as_posix()]
              for n in REFERENCE_NAMES))
    protocol = 'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md'
    check('approved_protocol_exact_bytes_preserved',
          sync.sha((ROOT / 'docs/process-report' / protocol).read_bytes()) ==
          before['approved_inputs'][(sync.BUNDLE_PATH / protocol).as_posix()])
    reference_check = json.loads((out / 'source-reference-validation.json').read_text())
    visual_check = json.loads((out / 'visual-inspection.json').read_text())
    check('approved_pdf_31_pages_and_representative_render_inspection',
          reference_check['pages']['approved']['pages'] == 31 and
          reference_check['pages']['approved']['sha256'] == reference_rows[REFERENCE_NAMES[0]]['sha256'] and
          visual_check['approved_representative_structure'] == 'PASS',
          {'pages': 31, 'inspected_pages': visual_check['approved_inspected_pages'],
           'first_page_continuation_note': visual_check['first_page_note']})
    archive_check = json.loads((out / 'source-archive-inventory.json').read_text())
    check('source_archive_valid_and_build_limit_disclosed',
          archive_check['zip_crc'] == 'PASS' and archive_check['tex_files'] > 0 and
          archive_check['evidence_png_assets'] > 0 and
          reference_check['source_archive_build'] in ('PASS', 'PARTIAL', 'BLOCKED') and
          (out / 'source-archive-check.md').is_file(),
          {'source_archive_build': reference_check['source_archive_build'],
           'compile_exit_code': reference_check['exit_code'],
           'rebuilt_pages': reference_check['pages']['rebuilt']['pages'],
           'missing_glyphs': reference_check['warning_counts']['missing_glyph'],
           'revised_text_different_pages': reference_check['approved_rebuilt_text_different_pages'],
           'sync_continuation_authority': 'Approved prompt section 8; this check is not reproduction PASS'})
    versions = {'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md': 'Version: **v1.0**',
                'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md': 'Version: **v2.4**',
                'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md': 'Design System v2.3'}
    check('active_versions', all(v in (ROOT / p).read_text() for p, v in versions.items()))
    duplicates = []
    for canonical in [*versions, 'AGENTS.md']:
        stem = Path(canonical).stem
        found = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob(stem + '*.md') if '.git' not in p.parts]
        expected = {canonical, (sync.BUNDLE_PATH / Path(canonical).name).as_posix()}
        if set(found) != expected:
            duplicates.append({'stem': stem, 'found': found})
    check('no_duplicate_active_governance', not duplicates, duplicates)
    with zipfile.ZipFile(ROOT / 'task1/作业.zip') as z:
        equal = {name: z.read('作业/' + name) == (ROOT / 'task1/作业/作业' / name).read_bytes()
                 for name in ['任务3_LLM辅助评估清洗.ipynb', '作业1轨迹数据预处理.ipynb']}
    check('notebooks_equal_original_archive_without_execution', all(equal.values()), equal)
    docs = [ROOT / 'AGENTS.md', *list((ROOT / 'docs').rglob('*.md')),
            *list((ROOT / 'templates').rglob('README.md')),
            *list((ROOT / sync.BUNDLE_PATH).glob('*.md')), *list((ROOT / sync.INTERNAL_PATH).glob('*.md')),
            *list(out.glob('*.md')),
            Path(__file__).with_name('README.md')]
    broken = []; stale = []; count = 0
    prefix = 'https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/'
    old_path = 'releases/chatgpt-project-sources/' + 'SOURCE_MANIFEST.md'
    for doc in docs:
        text = doc.read_text()
        if old_path in text:
            stale.append(doc.relative_to(ROOT).as_posix())
        for link in re.findall(r'\]\(([^)\s]+)\)', text):
            count += 1
            path, _, anchor = unquote(link).partition('#')
            if path.startswith(prefix):
                target = ROOT / path[len(prefix):]
            elif re.match(r'\w+://', path):
                continue
            else:
                target = (doc.parent / path).resolve() if path else doc
            if not target.exists():
                broken.append({'document': str(doc.relative_to(ROOT)), 'link': link})
            elif anchor and target.suffix == '.md':
                headings = re.findall(r'^#+\s+(.+)$', target.read_text(), re.M)
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
                if anchor not in slugs:
                    broken.append({'document': str(doc.relative_to(ROOT)), 'link': link, 'reason': 'anchor'})
    check('markdown_links_and_anchors', not broken, {'checked': count, 'broken': broken})
    check('no_stale_manifest_reference_in_current_docs', not stale, stale)
    for name in ['sync_sources.py', 'validate_sync.py']:
        compile(Path(__file__).with_name(name).read_text(), name, 'exec')
    check('python_syntax', True)
    check('sync_cleanup_and_failure_scenarios', True, fixture_checks())
    for flags in [[], ['--cached']]:
        result = subprocess.run(['git', 'diff', *flags, '--check'], cwd=ROOT, text=True, capture_output=True)
        check('git_diff_check' + ('_index' if flags else ''), result.returncode == 0, result.stdout + result.stderr)
    if args.index:
        paths = {r['source'] for r in rows} | {r['bundle'] for r in rows} | {(sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md').as_posix()}
        unequal = [p for p in paths if subprocess.check_output(['git', 'show', ':' + p], cwd=ROOT) != (ROOT / p).read_bytes()]
        check('index_matches_verified_bytes', not unequal, unequal)
    (out / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    failed = {k: v for k, v in report.items() if not v['pass']}
    print(json.dumps({'checks': len(report), 'failed': failed}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(failed))


if __name__ == '__main__':
    main()
