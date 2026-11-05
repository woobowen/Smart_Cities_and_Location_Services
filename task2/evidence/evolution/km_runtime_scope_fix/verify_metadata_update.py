"""Verify metadata-only canonical inheritance and refresh existing figure sidecars."""
from datetime import datetime, timezone
from pathlib import Path
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
previous = json.loads((OUT / 'before.json').read_text())


def load(path, old=False):
    return json.loads(((OUT / 'before' if old else ROOT) / path).read_text())


def differences(a, b, path=''):
    assert type(a) is type(b), path
    if isinstance(a, dict):
        assert a.keys() == b.keys(), path
        return sum((differences(a[k], b[k], path + '/' + k) for k in a), [])
    if isinstance(a, list):
        assert len(a) == len(b), path
        return sum((differences(x, y, path + '/' + str(i)) for i, (x, y) in enumerate(zip(a, b))), [])
    return [] if a == b else [dict(path=path, before=a, after=b)]


def numeric_leaves(value, path=''):
    if isinstance(value, dict):
        return sum((numeric_leaves(v, path + '/' + k) for k, v in value.items()), [])
    if isinstance(value, list):
        return sum((numeric_leaves(v, path + '/' + str(i)) for i, v in enumerate(value)), [])
    return [(path, type(value).__name__, value)] if isinstance(value, (int, float)) and not isinstance(value, bool) else []


local_path = 'task2/results/evolution/metrics.json'
public_path = 'task2/public_results/evolution/metrics.json'
manifest_path = 'task2/public_results/projection_manifest.json'
old_local, new_local = load(local_path, True), load(local_path)
old_public, new_public = load(public_path, True), load(public_path)
old_manifest, new_manifest = load(manifest_path, True), load(manifest_path)
local_diff = differences(old_local, new_local)
public_diff = differences(old_public, new_public)
manifest_diff = differences(old_manifest, new_manifest)
assert len(local_diff) == 6
assert len(public_diff) == 7
assert sum(x['path'].endswith('/runtime_scope') for x in local_diff) == 5
assert all(x['path'] == '/runner_sha256' or x['path'].endswith('/runtime_scope') for x in local_diff)
assert all(x['path'] in ['/runner_sha256', '/public_projection/source/sha256'] or
           x['path'].endswith('/runtime_scope') for x in public_diff)
assert len(manifest_diff) == 2
assert all(x['path'].endswith('/source_sha256') or x['path'].endswith('/public_sha256') for x in manifest_diff)
assert numeric_leaves(old_local) == numeric_leaves(new_local)
assert numeric_leaves(old_public) == numeric_leaves(new_public)
assert len(new_local['rows']) == len(new_public['rows']) == 125
for before, after in zip(old_local['rows'], new_local['rows']):
    assert before['metrics'] == after['metrics']
    assert before['numerical_sensitivity'] == after['numerical_sensitivity']
    assert after['metrics']['decimals'] == 10
    assert set(after['numerical_sensitivity']) == {'8', '12'}
assert (OUT / 'before/task2/results/evolution/summary.csv').read_bytes() == (ROOT / 'task2/results/evolution/summary.csv').read_bytes()
old_bindings = {r['public_path']: r for r in old_manifest['bindings']}
new_bindings = {r['public_path']: r for r in new_manifest['bindings']}
assert old_bindings.keys() == new_bindings.keys()
changed_bindings = [p for p in old_bindings if old_bindings[p] != new_bindings[p]]
assert changed_bindings == [public_path]
assert all(sha(ROOT / p) == r['public_sha256'] for p, r in new_bindings.items())

# Prove the evaluator's sole AST change is the descriptive runtime_scope value.
old_ast = ast.parse((OUT / 'before/task2/scripts/evaluate_evolution.py').read_text())
new_ast = ast.parse((ROOT / 'task2/scripts/evaluate_evolution.py').read_text())
for tree in [old_ast, new_ast]:
    matches = [n for n in ast.walk(tree) if isinstance(n, ast.keyword) and n.arg == 'runtime_scope']
    assert len(matches) == 1
    matches[0].value = ast.Constant(value='METADATA_SCOPE_ONLY')
assert ast.dump(old_ast) == ast.dump(new_ast)

sidecars = []
current_public_hash = sha(ROOT / public_path)
for folder in ['formal', 'candidates']:
    for path in sorted((ROOT / 'task2/figures' / folder).glob('*evolution*.json')):
        relative = str(path.relative_to(ROOT))
        original = load(relative, True)
        assert sha(OUT / 'before' / relative) == previous['protected_sha256'][relative]
        assert original['input_sha256'][public_path] == previous['before_sha256'][public_path]
        refreshed = dict(original)
        refreshed['input_sha256'] = dict(original['input_sha256'])
        refreshed['input_sha256'][public_path] = current_public_hash
        refreshed['metadata_inheritance'] = dict(
            identity='METADATA_ONLY_INHERITANCE_NO_FIGURE_REBUILD',
            reason='Only canonical runtime_scope labels and evaluator source binding changed; all numeric leaves are exactly preserved.',
            original_sidecar_sha256=sha(OUT / 'before' / relative),
            original_input_sha256={public_path: original['input_sha256'][public_path]},
            current_input_sha256={public_path: current_public_hash},
            original_sidecar_snapshot='task2/evidence/evolution/km_runtime_scope_fix/before/' + relative,
            verification='task2/evidence/evolution/km_runtime_scope_fix/result.json')
        path.write_text(json.dumps(refreshed, ensure_ascii=False, indent=2) + '\n')
        sidecars.append(dict(path=relative, before_sha256=sha(OUT / 'before' / relative), after_sha256=sha(path)))
assert len(sidecars) == 10
changed_protected = [p for p, h in previous['protected_sha256'].items() if sha(ROOT / p) != h]
assert sorted(changed_protected) == sorted(s['path'] for s in sidecars)
assert sha(ROOT / 'task2/scripts/project_public_results.py') == new_manifest['producer_sha256']
after_source = ROOT / 'task2/scripts/evaluate_evolution.py'
(OUT / 'source_after.py').write_bytes(after_source.read_bytes())
scope_changes = [dict(run_id=a['run_id'], algorithm=a['algorithm'],
                      before=b['runtime_scope'], after=a['runtime_scope'],
                      runtime=a['runtime'], n_eval=a['n_eval'],
                      timing_recompute_sha256=a['timing_recompute_sha256'])
                 for b, a in zip(old_local['rows'], new_local['rows']) if b['runtime_scope'] != a['runtime_scope']]
assert all(r['algorithm'] == 'weighted_km' and r['n_eval'] == 41 for r in scope_changes)
receipt = dict(
    actual_utc=datetime.now(timezone.utc).isoformat(), author='/root/evolution',
    status='PASS_AUTHOR_METADATA_ONLY_NUMERICAL_INHERITANCE',
    commands_executed=['.venv/bin/python -B task2/scripts/evaluate_evolution.py',
                       '.venv/bin/python -B task2/scripts/project_public_results.py'],
    before_sha256=previous['before_sha256'],
    after_sha256={p: sha(ROOT / p) for p in previous['before_sha256']},
    local_field_diff=local_diff, public_field_diff=public_diff, manifest_field_diff=manifest_diff,
    scope_changes=scope_changes, canonical_records=125, full_precision_metric_sets=375,
    primary_decimals=10, sensitivity_decimals=[8, 12],
    local_numeric_leaves_exactly_equal=len(numeric_leaves(new_local)),
    public_numeric_leaves_exactly_equal=len(numeric_leaves(new_public)),
    summary_csv_byte_identical=True, evaluator_ast_equal_except_runtime_scope=True,
    public_bindings=len(new_bindings), changed_public_bindings=changed_bindings,
    unchanged_other_public_bindings=len(new_bindings) - 1,
    sidecar_metadata_updates=sidecars, protected_files=len(previous['protected_sha256']),
    unchanged_protected_except_sidecars=len(previous['protected_sha256']) - len(sidecars),
    scientific_artifact_changes=[],
    limits='Canonical metric recomputation and original aggregate projection only. No scalar assignment solve, EA generation, model training, figure rendering or report rebuild. Original raw/timing/figure/report bytes remain unchanged. Old receipts remain bound to their old artifacts; this is an appended author metadata inheritance check, not an independent EA rerun.')
(OUT / 'result.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'canonical_records', 'full_precision_metric_sets',
    'local_numeric_leaves_exactly_equal', 'public_numeric_leaves_exactly_equal', 'changed_public_bindings',
    'unchanged_protected_except_sidecars']}, ensure_ascii=False))
