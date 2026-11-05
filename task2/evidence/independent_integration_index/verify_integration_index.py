"""Read existing integration artifacts; never launch experiments or figure builds."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re
import statistics
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
inputs = {}
checks = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = ROOT / path
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return path.read_text()


def js(path):
    return json.loads(read(path))


def rows(path):
    return list(csv.DictReader(read(path).splitlines()))


def check(label, actual, expected, digits=None):
    equal = round(actual, digits) == expected if digits is not None else actual == expected
    checks.append(dict(label=label, actual=actual, expected=expected,
                       decimal_places=digits, passed=equal))
    assert equal, (label, actual, expected)


docs = sorted((ROOT / 'task2/review').glob('*.md')) + [
    ROOT / 'task2/docs' / name for name in
    ['REVIEW_LOG.md', 'EXPERIMENT_PLAN.md', 'REPRODUCIBILITY_GUIDE.md']
] + [ROOT / 'task2/README.md']
broken = []
documents = {}
for p in docs:
    content = read(p.relative_to(ROOT))
    documents[str(p.relative_to(ROOT))] = sha(p)
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
        target = target.strip('<>').split('#')[0]
        if target and '://' not in target and not target.startswith('mailto:'):
            if not (p.parent / target).exists():
                broken.append(dict(document=str(p.relative_to(ROOT)), target=target))
check('Markdown local links exist', broken, [])
check('reviewed integration documents', len(docs), 12)
check('no global-policy-optimality overclaim', '政策最优性' in
      read('task2/review/VERIFICATION_PACKET.md'), False)
check('training metadata uses actual filename', 'training_manifest' in
      read('task2/review/EXPERIMENT_INDEX.md'), False)

formal = sorted((ROOT / 'task2/figures/formal').glob('*.pdf'))
check('formal scientific figure count', len(formal), 22)
check('formal figure branches', dict(Counter(p.name.split('_')[0] for p in formal)),
      {'online': 5, 'evolution': 7, 'rl': 10})
check('generated table count', len(list((ROOT / 'task2/reports/generated').glob('*.tex'))), 10)

active = js('task2/results/rl/ACTIVE_RUNS.json')
check('RL run identities', len(active['runs']), 39)
check('active day-metric tables', len(active['active_day_metrics']), 36)
check('unique active tables', len(set(active['active_day_metrics'])), 36)
models = {m['path']: m for run in active['runs'] if run['active']
          for m in run.get('models', [])}
model_checks = []
for relative, reference in sorted(models.items()):
    base = ROOT / 'task2' / relative
    mpath, npzpath = base / 'manifest.json', base / 'model.npz'
    manifest = js(mpath.relative_to(ROOT))
    inputs[str(npzpath.relative_to(ROOT))] = sha(npzpath)
    assert sha(mpath) == reference['manifest_sha256']
    assert sha(npzpath) == reference['model_sha256']
    with np.load(npzpath) as arrays:
        episode_rows, td_rows = len(arrays['episodes']), len(arrays['td'])
    declared = manifest['real_training_episodes']
    assert declared == episode_rows == td_rows
    model_checks.append(dict(path=str(base.relative_to(ROOT)), episodes=declared,
                             episode_rows=episode_rows, td_rows=td_rows,
                             manifest_sha256=sha(mpath), model_sha256=sha(npzpath)))
check('unique active training models', len(models), 30)
check('model training episode counts', dict(Counter(m['episodes'] for m in model_checks)),
      {10: 1, 300: 29})
check('training episodes, excluding Notebook recomputation and REPLAY',
      sum(m['episodes'] for m in model_checks), 8710)

ea = rows('task2/results/evolution/summary.csv')
check('EA and KM canonical records', len(ea), 125)
check('full EA records', sum(r['algorithm'] != 'weighted_km' for r in ea), 115)
check('EA stage counts', dict(Counter(r['stage'] for r in ea)),
      {'basic': 5, 'weighted_km': 10, 'baseline': 60, 'combination': 10,
       'confirmation_km': 5, 'confirmation_teacher': 5, 'hybrid': 10, 'scale': 20})
check('advanced raw EA files', len(list((ROOT / 'task2/results/evolution/runs').glob('*.json'))), 110)
check('basic raw EA files', len(list((ROOT / 'task2/results/evolution/basic').glob('basic_nsga2_seed*.json'))), 5)


def ea_group(stage, algorithm, batch='inner_hour18_batchseed2024', n_obj='2'):
    return [float(r['HV']) for r in ea if r['stage'] == stage
            and r['algorithm'] == algorithm and r['batch_id'] == batch and r['n_obj'] == n_obj]


for nobj, algo, mean, sd in [('2', 'nsga2', 1.090244, .004460),
                            ('2', 'nsga3', 1.077092, .009530),
                            ('3', 'nsga2', 1.014845, .010260),
                            ('3', 'nsga3', 1.012638, .005689)]:
    data = ea_group('baseline', algo, n_obj=nobj)
    check(f'18h {nobj}D {algo} HV mean', statistics.mean(data), mean, 6)
    check(f'18h {nobj}D {algo} HV sample SD', statistics.stdev(data), sd, 6)
for algo, mean, sd in [('nsga2', .707111, .006190), ('nsga3', .744325, .000235)]:
    data = ea_group('baseline', algo, 'dtlz2_integer_teacher', '3')
    check(f'integer DTLZ2 {algo} mean', statistics.mean(data), mean, 6)
    check(f'integer DTLZ2 {algo} sample SD', statistics.stdev(data), sd, 6)
for algo, mean, gain in [('nsga2', 1.111427, .001485), ('nsga3', 1.111494, .000578)]:
    h = statistics.mean(ea_group('hybrid', algo))
    check(f'hybrid {algo} HV', h, mean, 6)
    check(f'combination incremental HV {algo}',
          statistics.mean(ea_group('combination', algo)) - h, gain, 6)
future = []
for seed in range(9010, 9015):
    batch = f'test_hour18_batchseed{seed}'
    future.append(ea_group('confirmation_km', 'nsga2', batch)[0] -
                  ea_group('confirmation_teacher', 'nsga2', batch)[0])
check('future paired HV mean', statistics.mean(future), .031470, 6)
check('future paired HV sample SD', statistics.stdev(future), .006573, 6)
check('future inputs with positive paired HV', sum(x > 0 for x in future), 5)

online = {}
for name, count in [('development_v1', 1045), ('confirmation_v1', 1045),
                    ('threshold_diagnosis_v1', 150), ('foursquare_proxy_v1', 200)]:
    online[name] = rows(f'task2/results/online/{name}/metrics.csv')
    check(f'online {name} metric count', len(online[name]), count)
for method, average, maximum in [('TBG_g2', 7.639, 13.581), ('TBG_g5', 5.411, 15.927)]:
    data = [r for r in online['confirmation_v1']
            if r['scenario'] == 'teacher' and r['method'] == method]
    check(method + ' confirmation mean delay', statistics.mean(float(r['avg_delay']) for r in data), average, 3)
    check(method + ' confirmation mean maximum', statistics.mean(float(r['max_delay']) for r in data), maximum, 3)
for scenario, method, rate in [('teacher', 'BB_discard_t0.5', .25),
                                ('teacher', 'BB_recycle_t0.5', 1.),
                                ('workers_first', 'BB_discard_t0.5', 0.)]:
    data = [r for r in online['development_v1'] if r['scenario'] == scenario and r['method'] == method]
    check(f'{scenario} {method} coverage', statistics.mean(float(r['match_rate']) for r in data), rate)
seed13 = {r['method']: r for r in online['development_v1']
          if r['scenario'] == 'teacher' and r['seed'] == '13'}
check('teacher seed13 local BBmax daily delay excess',
      float(seed13['BBmax_recycle_t1']['max_delay']) - float(seed13['BB_recycle_t1']['max_delay']), 2.162, 3)

rl = rows('task2/results/rl/SUMMARY.csv')
check('RL summary unique active run tables', len({r['run_id'] for r in rl}), 36)


def rlvalue(run, policy, metric='revenue_mean'):
    data = [r for r in rl if r['run_id'] == run and r['policy'] == policy]
    assert len(data) == 1
    return float(data[0][metric])


for fleet, q, km in [(40, 13994.90, 12437.18), (60, 17170.85, 16757.42),
                      (100, 20046.49, 20793.01)]:
    check(f'final fleet{fleet} Q revenue', rlvalue(f'final_fleet{fleet}', 'qkm'), q, 2)
    check(f'final fleet{fleet} KM revenue', rlvalue(f'final_fleet{fleet}', 'km'), km, 2)
for family, revenue, response in [('fair_double_b1', 14771.95, .53797),
                                   ('fair_q_b1', 14173.08, .57176)]:
    data = [r for r in rl if r['run_id'].startswith(family) and r['policy'] == 'beta1']
    check(f'{family} train seed count', len(data), 5)
    check(f'{family} revenue', statistics.mean(float(r['revenue_mean']) for r in data), revenue, 2)
    check(f'{family} response', statistics.mean(float(r['answer_rate_mean']) for r in data), response, 5)
for policy, metric, expected, precision in [
    ('double_beta1', 'revenue_mean', 14336.25, 2), ('q_beta1', 'revenue_mean', 13995.18, 2),
    ('km_move3', 'revenue_mean', 17811.65, 2), ('km_move3', 'empty_km_mean', 826.55, 2),
    ('qnsga_constraint', 'avg_pickup_mean', 1.360, 3), ('qkm', 'avg_pickup_mean', 1.928, 3),
    ('qnsga_constraint', 'revenue_mean', 16932.91, 2),
    ('qnsga_constraint', 'answer_rate_mean', .64933, 5), ('qkm', 'answer_rate_mean', .66027, 5),
]:
    check(f'final enhancements {policy} {metric}', rlvalue('final_enhancements', policy, metric), expected, precision)
mc = js('task2/results/rl/final_montecarlo_v1/paired_differences.json')
mc_rows = {r['metric']: r for r in mc['rows']
           if r['candidate'] == 'km_move3' and r['reference'] == 'qkm'}
for key, expected in [('mean_difference', 435.45), ('descriptive_t95_low', 141.68),
                       ('descriptive_t95_high', 729.23)]:
    check('MC20 gross ' + key, mc_rows['revenue'][key], expected, 2)
check('MC20 additional empty km', mc_rows['empty_km']['mean_difference'], 848.08, 2)
net = [fare - km for fare, km in zip(mc_rows['revenue']['differences'], mc_rows['empty_km']['differences'])]
net_mean = statistics.mean(net)
net_half = 2.093024054408263 * statistics.stdev(net) / len(net) ** .5
check('hypothetical unit-cost net mean', net_mean, -412.62, 2)
check('hypothetical unit-cost net t95 low', net_mean - net_half, -717.03, 2)
check('hypothetical unit-cost net t95 high', net_mean + net_half, -108.22, 2)

archive = ROOT / 'task2/releases/Dispatch_Reports_LaTeX_Source.zip'
inputs[str(archive.relative_to(ROOT))] = sha(archive)
old = js('task2/evidence/independent_package/report_source_01/archive_inspection.json')
compiled = js('task2/evidence/independent_package/report_source_01/compile_comparison.json')
changes = []
with zipfile.ZipFile(archive) as zipped:
    check('source archive exact member set', sorted(zipped.namelist()), sorted(old['member_paths']))
    for entry in old['package_manifest']['files']:
        current = hashlib.sha256(zipped.read(entry['path'])).hexdigest()
        if current != entry['sha256']:
            changes.append(dict(path=entry['path'], old_sha256=entry['sha256'], new_sha256=current))
    check('source archive content changes since isolated compile', [c['path'] for c in changes],
          ['task2/reports/generated/sources.json'])
    current_source = json.loads(zipped.read('task2/reports/generated/sources.json'))
old_source = js('task2/evidence/independent_package/report_source_01/build/source/task2/reports/generated/sources.json')
old_input = old_source['actual_input_hashes'].pop('task2/results/rl/SUMMARY.csv')
new_input = current_source['actual_input_hashes'].pop('task2/results/rl/SUMMARY.csv')
check('source metadata change is only RL summary input hash', old_source, current_source)
check('inherited isolated source compile page counts', [r['pages'] for r in compiled['reports']], [26, 8])
check('inherited isolated source compile pixel comparisons',
      sum(len(r['page_comparisons']) for r in compiled['reports']), 34)
assert all(r['returncode'] == 0 and r['full_text_equal'] and
           all(p['pixels_equal'] for p in r['page_comparisons']) for r in compiled['reports'])
visual = js('task2/evidence/independent_report_review/pdf_final_review.json')
for record in visual['reports']:
    path = ROOT / record['pdf']['source']
    inputs[str(path.relative_to(ROOT))] = sha(path)
    check(record['kind'] + ' current PDF matches R independent visual review', sha(path), record['pdf']['sha256'])

receipt = dict(
    actual_utc=datetime.now(timezone.utc).isoformat(), reviewer='/root/evolution',
    status='PASS_IN_STATED_INTEGRATION_INDEX_SCOPE',
    scope='Read-only integration-index review of12 Markdown documents against existing artifacts; independently recomputed counts and stated aggregate arithmetic; no experiment, training, figure generation, PDF compilation or new PDF visual review.',
    document_sha256=documents, input_sha256=inputs, checks_count=len(checks), checks=checks,
    active_model_evidence=model_checks,
    closed_findings=[
        'Root replaced global policy-optimality wording with two beta1 trajectory edge-weight and local exact-matching scope.',
        'RL training metadata file is each model directory manifest.json; training_manifest is not an actual filename.',
    ],
    source_archive_inheritance=dict(
        current_bundle_sha256=sha(archive), actually_compiled_bundle_sha256=compiled['bundle_sha256'],
        content_changes=changes, changed_json_key='actual_input_hashes/task2/results/rl/SUMMARY.csv',
        old_summary_sha256=old_input, current_summary_sha256=new_input,
        basis='All TeX, build script, generated TeX tables, PDFs, diagrams and vector figures are byte-identical to the isolated-compiled package. Only provenance JSON and its package manifest change. The old compile receipt remains its own bundle identity; no new compile is claimed.'),
    excluded=[
        'EB final public Git file-set/security review, final fixed commit and remote publication',
        'Independent re-review of source package compilation: inherited from EB on byte-identical render inputs',
        'Independent re-review of PDF pages: inherited from R exact current PDF hashes',
        'Process UI Evidence production/Lock, external GPT audit, user acceptance or teacher submission',
        'Global RL or NSGA optimality, real operational profit or confirmed geographic datum',
    ])
(OUT / 'result.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(status=receipt['status'], checks=len(checks), documents=len(documents),
                     source_package_changes=[c['path'] for c in changes]), ensure_ascii=False))
