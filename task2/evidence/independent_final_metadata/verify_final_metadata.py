"""Read-only independent comparison of the final metadata/source-package delta.

This writes its own receipts only. It does not import or run experiment code.
"""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIX = ROOT / 'task2/evidence/evolution/km_runtime_scope_fix'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def leaves(value, path=''):
    if isinstance(value, dict):
        return {p: x for k, v in value.items() for p, x in leaves(v, path+'/'+k).items()}
    if isinstance(value, list):
        return {p: x for i, v in enumerate(value) for p, x in leaves(v, path+'/'+str(i)).items()}
    return {path: value}


def differences(old, new):
    a, b = leaves(old), leaves(new)
    missing = object()
    return [{'path': p, 'before': a.get(p, '__ABSENT__'), 'after': b.get(p, '__ABSENT__')}
            for p in sorted(a.keys() | b.keys())
            if type(a.get(p, missing)) is not type(b.get(p, missing))
            or a.get(p, missing) != b.get(p, missing)]


def numeric(value):
    return {p: (type(v).__name__, v) for p, v in leaves(value).items()
            if type(v) in (int, float)}


def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


before = read(FIX/'before.json')
author = read(FIX/'result.json')
for path, expected in before['before_sha256'].items():
    assert sha(FIX/'before'/path) == expected, ('old snapshot', path)
local_path = 'task2/results/evolution/metrics.json'
public_path = 'task2/public_results/evolution/metrics.json'
manifest_path = 'task2/public_results/projection_manifest.json'
old_local, new_local = read(FIX/'before'/local_path), read(ROOT/local_path)
old_public, new_public = read(FIX/'before'/public_path), read(ROOT/public_path)
old_manifest, new_manifest = read(FIX/'before'/manifest_path), read(ROOT/manifest_path)
local_diff = differences(old_local, new_local)
public_diff = differences(old_public, new_public)
manifest_diff = differences(old_manifest, new_manifest)
scope_paths = {'/rows/'+str(i)+'/runtime_scope' for i in range(5, 10)}
assert {d['path'] for d in local_diff} == scope_paths | {'/runner_sha256'}
assert {d['path'] for d in public_diff} == scope_paths | {'/runner_sha256', '/public_projection/source/sha256'}
assert len(manifest_diff) == 2
assert len(new_local['rows']) == len(old_local['rows']) == 125
for old, new in zip(old_local['rows'], new_local['rows']):
    assert old['run_id'] == new['run_id']
    assert old['metrics'] == new['metrics']
    assert old['numerical_sensitivity'] == new['numerical_sensitivity']
    assert set(new['numerical_sensitivity']) == {'8', '12'}
    assert new['metrics']['decimals'] == 10
    if old['runtime_scope'] != new['runtime_scope']:
        assert new['algorithm'] == 'weighted_km' and new['n_eval'] == 41
        if new['timing_recompute_path']:
            timing = read(ROOT/new['timing_recompute_path'])
            assert sha(ROOT/new['timing_recompute_path']) == new['timing_recompute_sha256']
            assert timing['runtime_scope'] == new['runtime_scope']
        else:
            assert new['runtime'] is None and 'not captured' in new['runtime_scope']
assert numeric(old_local) == numeric(new_local)
assert numeric(old_public) == numeric(new_public)
assert sha(ROOT/'task2/results/evolution/summary.csv') == before['before_sha256']['task2/results/evolution/summary.csv']
assert new_public['public_projection']['source']['sha256'] == sha(ROOT/local_path)
assert new_local['runner_sha256'] == sha(ROOT/'task2/scripts/evaluate_evolution.py')

# Restrict our independent AST claim to the actual changed runtime_scope keyword.
old_ast = ast.parse((FIX/'before/task2/scripts/evaluate_evolution.py').read_text())
new_ast = ast.parse((ROOT/'task2/scripts/evaluate_evolution.py').read_text())
counts = []
for tree in (old_ast, new_ast):
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == 'runtime_scope':
            node.value = ast.Constant(value='IGNORED_RUNTIME_SCOPE_METADATA')
            count += 1
    counts.append(count)
assert counts == [1, 1]
assert ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)

changed_bindings = []
assert len(old_manifest['bindings']) == len(new_manifest['bindings']) == 124
for a, b in zip(old_manifest['bindings'], new_manifest['bindings']):
    assert a['source_path'] == b['source_path'] and a['public_path'] == b['public_path']
    if a != b:
        changed_bindings.append(b['public_path'])
        assert b['source_path'] == local_path and b['public_path'] == public_path
        assert b['source_sha256'] == sha(ROOT/local_path)
    assert sha(ROOT/b['public_path']) == b['public_sha256']
assert changed_bindings == [public_path]

sidecars = {x['path'] for x in author['sidecar_metadata_updates']}
assert len(sidecars) == 10
sidecar_receipt = []
for path in sorted(sidecars):
    old, new = read(FIX/'before'/path), read(ROOT/path)
    inheritance = new.pop('metadata_inheritance')
    assert inheritance['identity'] == 'METADATA_ONLY_INHERITANCE_NO_FIGURE_REBUILD'
    assert inheritance['original_sidecar_sha256'] == sha(FIX/'before'/path)
    assert new['input_sha256'][public_path] == sha(ROOT/public_path)
    new['input_sha256'][public_path] = old['input_sha256'][public_path]
    assert new == old
    sidecar_receipt.append({'path': path, 'current_sha256': sha(ROOT/path)})

summary_path = 'task2/results/evolution/SUMMARY.md'
summary_old = (FIX/'before'/summary_path).read_bytes()
summary_new = (ROOT/summary_path).read_bytes()
old_sha = before['before_sha256'][local_path]
new_sha = sha(ROOT/local_path)
assert summary_old.count(old_sha.encode()) == 1
assert summary_old.replace(old_sha.encode(), new_sha.encode()) == summary_new
protected_unchanged = []
generated_sources = 'task2/reports/generated/sources.json'
table_regression = read(ROOT/'task2/evidence/report_build/km_metadata_table_regression.json')
assert table_regression['changed_tex'] == []
assert sha(ROOT/generated_sources) == table_regression['current_sources_sha256']
for path, expected in before['protected_sha256'].items():
    actual = sha(ROOT/path)
    if path not in sidecars | {summary_path, generated_sources}:
        assert actual == expected, ('protected file changed', path)
        protected_unchanged.append(path)
    elif path != generated_sources:
        assert sha(FIX/'before'/path) == expected

km_receipt = {
    'actual_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reviewer': '/root/research_data, independent of EA implementation and metadata author',
    'status': 'PASS',
    'command': '.venv/bin/python -B task2/evidence/independent_final_metadata/verify_final_metadata.py',
    'scope': 'Read actual before/current JSON, code AST, bytes and artifact hashes; no EA/KM solves, training, plotting or report compilation.',
    'before_sha256': before['before_sha256'],
    'after_sha256': {p: sha(ROOT/p) for p in before['before_sha256']},
    'local_diff': local_diff, 'public_diff': public_diff, 'manifest_diff': manifest_diff,
    'canonical_records': 125, 'full_metric_dicts_exactly_equal_8_10_12': 375,
    'numeric_local_leaves_type_path_value_exact': len(numeric(new_local)),
    'numeric_public_leaves_type_path_value_exact': len(numeric(new_public)),
    'summary_csv_byte_identical': True,
    'evaluator_ast_exact_except_single_runtime_scope_keyword': True,
    'summary_md_only_one_canonical_hash_replacement': {'before_sha256': hashlib.sha256(summary_old).hexdigest(), 'after_sha256': hashlib.sha256(summary_new).hexdigest(), 'new_packet_sha256': new_sha},
    'public_bindings': 124, 'changed_public_bindings': changed_bindings,
    'other_public_bindings_exactly_equal': 123,
    'sidecar_only_hash_plus_explicit_inheritance': sidecar_receipt,
    'protected_snapshot_count': len(before['protected_sha256']),
    'protected_files_exactly_unchanged_excluding_10_sidecars_summary_header_and_generated_provenance': len(protected_unchanged),
    'generated_provenance_followup': {'path': generated_sources, 'before_sha256': before['protected_sha256'][generated_sources], 'current_sha256': sha(ROOT/generated_sources), 'table_regression_receipt': 'task2/evidence/report_build/km_metadata_table_regression.json'},
    'verification_iteration': 'Initial protected-hash assertion identified the already-authorized generated/sources.json regeneration after the EA snapshot. Explicitly verified its current hash against the table receipt and old/current package manifests; no original artifacts were modified by this verifier.',
    'limits': 'Independent append to existing scientific audits. Does not claim a new experiment, new rendering, user acceptance, remote review, or independent certification of all CLI mathematical bodies.'
}
save('km_scope_metadata_review.json', km_receipt)

prior_dir = ROOT/'task2/evidence/independent_package/report_source_01'
prior = read(prior_dir/'archive_inspection.json')
compile_prior = read(prior_dir/'compile_comparison.json')
bundle = ROOT/'task2/releases/Dispatch_Reports_LaTeX_Source.zip'
assert prior['sha256'] == compile_prior['bundle_sha256'] == '0215d2cd3f8dd25bbbc130c70467e0d56d01058008f393215a8255eec51b8fd4'
assert sha(bundle) == '781dfd5a0990e9f9ddf0ce830bb1401a884481ab3d6fb0240a8f619f79d3a16e'
old_entries = {x['path']: x for x in prior['package_manifest']['files']}
# The pre-fix artifact inventory and earlier compiled ZIP are distinct snapshots;
# compare each recorded provenance version without assuming their bytes match.
with zipfile.ZipFile(bundle) as archive:
    names = archive.namelist()
    assert len(names) == len(set(names)) == prior['members'] == 81
    assert set(names) == set(prior['member_paths'])
    current_manifest = json.loads(archive.read('SOURCE_PACKAGE_MANIFEST.json'))
    new_entries = {x['path']: x for x in current_manifest['files']}
    # The bundle manifest covers 79 source/assets; the generated README and the
    # manifest itself are the other two entries. Also read the actual extraction
    # retained by the independent compiler to compare those two members.
    old_extraction = prior_dir/'build/source'
    assert read(old_extraction/'SOURCE_PACKAGE_MANIFEST.json') == prior['package_manifest']
    assert set(old_entries) == set(new_entries) == set(names)-{'SOURCE_PACKAGE_MANIFEST.json', 'README_SOURCE_PACKAGE.md'}
    actual_changed_zip_members = []
    for name in names:
        previous_raw = (old_extraction/name).read_bytes()
        if archive.read(name) != previous_raw:
            actual_changed_zip_members.append(name)
        if name in old_entries:
            assert hashlib.sha256(previous_raw).hexdigest() == old_entries[name]['sha256']
    assert set(actual_changed_zip_members) == {'task2/reports/generated/sources.json', 'SOURCE_PACKAGE_MANIFEST.json'}
    changed = []
    unchanged = []
    for name, entry in new_entries.items():
        raw = archive.read(name)
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == entry['sha256'] and len(raw) == entry['bytes']
        assert raw == (ROOT/name).read_bytes(), ('ZIP versus current working source', name)
        if entry != old_entries[name]:
            changed.append({'path': name, 'before': old_entries[name], 'after': entry})
        else:
            unchanged.append(name)
    assert [c['path'] for c in changed] == ['task2/reports/generated/sources.json']
    assert archive.read('README_SOURCE_PACKAGE.md') == (old_extraction/'README_SOURCE_PACKAGE.md').read_bytes()
    unchanged.append('README_SOURCE_PACKAGE.md')
    assert archive.read('task2/reports/generated/sources.json') == (ROOT/'task2/reports/generated/sources.json').read_bytes()
    manifest_diff = differences(prior['package_manifest'], current_manifest)
    assert len(manifest_diff) == 1 and manifest_diff[0]['path'].endswith('/sha256')
    report_pdf_members = [n for n in names if n.startswith('task2/reports/') and n.endswith('.pdf')]
    assert len(report_pdf_members) == 2
    report_sha = {n: hashlib.sha256(archive.read(n)).hexdigest() for n in report_pdf_members}
for report in compile_prior['reports']:
    assert report['returncode'] == 0 and report['full_text_equal']
    assert len(report['page_comparisons']) == report['pages']
    assert all(p['pixels_equal'] for p in report['page_comparisons'])
    assert report['reference_pdf_sha256'] in report_sha.values()
zip_receipt = {
    'actual_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reviewer': '/root/research_data, independent of source-package author',
    'status': 'PASS_COMPILATION_ASSET_INHERITANCE',
    'command': km_receipt['command'],
    'current_bundle': {'path': str(bundle.relative_to(ROOT)), 'sha256': sha(bundle), 'bytes': bundle.stat().st_size, 'members': len(names)},
    'prior_independently_compiled_bundle_sha256': prior['sha256'],
    'prior_archive_receipt': {'path': str((prior_dir/'archive_inspection.json').relative_to(ROOT)), 'sha256': sha(prior_dir/'archive_inspection.json')},
    'prior_actual_isolated_compile_receipt': {'path': str((prior_dir/'compile_comparison.json').relative_to(ROOT)), 'sha256': sha(prior_dir/'compile_comparison.json'), 'executor': compile_prior['reviewer']},
    'actual_member_path_set_identical': True,
    'all_79_manifest_listed_assets_current_size_sha_and_working_bytes_validated': True,
    'generated_readme_compared_to_actual_prior_extraction': True,
    'all_81_members_compared_to_actual_prior_compiler_extraction': True,
    'changed_data_members': changed,
    'changed_package_manifest_fields': manifest_diff,
    'only_two_changed_zip_members': actual_changed_zip_members,
    'distinct_prior_provenance_baselines': {'ea_protected_inventory_sha256': before['protected_sha256'][generated_sources], 'previously_compiled_zip_member_sha256': old_entries[generated_sources]['sha256'], 'current_sha256': sha(ROOT/generated_sources)},
    'unchanged_other_members': len(unchanged),
    'report_pdf_sha256': report_sha,
    'inherited_prior_compilation': [{'label': r['label'], 'prior_executor': compile_prior['reviewer'], 'returncode': r['returncode'], 'pages': r['pages'], 'full_text_equal': r['full_text_equal'], 'all_200dpi_pages_pixel_equal': all(p['pixels_equal'] for p in r['page_comparisons'])} for r in compile_prior['reports']],
    'limits': 'No new compilation or visual inspection in this check. Actual bytes of every TeX/PDF/figure/build asset are unchanged relative to prior per-member evidence; only generated provenance sources.json and its enclosing checksum changed. Prior independent compile and our prior 34-page visual audit remain applicable to those unchanged assets.'
}
save('source_package_inheritance_review.json', zip_receipt)
print(json.dumps({'status': 'PASS', 'canonical_records': 125, 'metric_sets_equal': 375, 'local_numeric_leaves_equal': len(numeric(new_local)), 'public_numeric_leaves_equal': len(numeric(new_public)), 'protected_unchanged': len(protected_unchanged), 'zip_members': len(names), 'zip_changed': zip_receipt['only_two_changed_zip_members'], 'receipts': ['km_scope_metadata_review.json', 'source_package_inheritance_review.json']}, ensure_ascii=False))
