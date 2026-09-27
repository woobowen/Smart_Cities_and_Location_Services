"""Independent structural/lineage audit of an actually completed full Notebook.

This does not launch a kernel or repeat the numerical experiment. It verifies the
preserved execution, every task/episode, newly drawn data and exact source bytes.
The project root is explicit so the same checks can audit an extracted ZIP.
"""
import argparse
import ast
import base64
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys

REVIEW_ROOT = Path(__file__).resolve().parents[4]
COUNTS = ('n_input', 'n_final', 'n_filtered', 'n_direction_removed', 'n_dp_removed',
          'n_dp_input', 'n_dp_output', 'common_covered_points', 'raw_break_crossings')
RAW_SHA = 'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def text(value):
    return ''.join(value) if isinstance(value, list) else value


def inside(base, name):
    path = (base/name).resolve()
    assert base.resolve() in path.parents, ('PATH_ESCAPE', name)
    return path


def figure_check(root, topic_dir, info, embedded_pngs):
    manifest_path = inside(topic_dir, info['manifest_path'])
    assert sha(manifest_path) == info['manifest_sha256']
    manifest = read(manifest_path)
    assert manifest['classification'] == 'NEW_FIGURES_FROM_THIS_RAW_RECOMPUTATION'
    assert manifest['old_summary_or_figure_read_for_plotting'] is False
    assert manifest['source_crs'] == 'UNVERIFIED'
    assert manifest['source_sha256'] == sha(root/'task1/goal3/offline_plots.py')
    assert manifest['palette_sha256'] == sha(inside(root, manifest['palette_source']))
    assert len(manifest['figures']) == info['figure_count']
    data_path = inside(manifest_path.parent, manifest['plot_data_path'])
    assert sha(data_path) == manifest['plot_data_sha256'] == info['plot_data_sha256']
    for figure in manifest['figures']:
        assert set(figure['files']) == {'png', 'pdf', 'svg'}
        for fmt, entry in figure['files'].items():
            path = inside(manifest_path.parent, entry['path'])
            assert sha(path) == entry['sha256']
            assert path.stat().st_size == entry['bytes']
            if fmt == 'png':
                assert entry['sha256'] in embedded_pngs, ('FIGURE_NOT_IN_EXECUTED_NOTEBOOK', path.name)
    return read(data_path)


def historical_check(root, evidence, topic, registry, embedded_pngs):
    path = evidence/'artifacts'/topic/'recompute_receipt.json'
    receipt = read(path)
    tasks = registry['topics'][topic]
    assert receipt['status'] == 'VERIFIED'
    assert receipt['mode'] == 'FULL_RECOMPUTE_HISTORICAL_G2' and receipt['topic'] == topic
    assert receipt['new_model_calls'] == 0
    assert receipt['registry_sha256'] == sha(root/'task1/evidence/goal3/historical_recompute_registry.json.gz')
    assert receipt['source_sha256'] == sha(root/'task1/goal3/reproduce.py')
    count = sum(len(t['records']) for t in tasks)
    assert receipt['candidate_record_recomputations'] == count
    assert receipt['checks'] == [
        {'task': i, 'source_run_id': task['source_run_id'], 'records': len(task['records']),
         'raw_recomputed_hash_and_review': 'VERIFIED'} for i, task in enumerate(tasks)]
    progress = [json.loads(line) for line in (evidence/'artifacts'/f'{topic}_progress.txt').read_text().splitlines()]
    assert progress == [
        {'topic': topic, 'task': i+1, 'total_tasks': len(tasks),
         'record_recomputations': sum(len(t['records']) for t in tasks[:i+1])}
        for i in range(0, len(tasks), 10)]
    data = figure_check(root, path.parent, receipt['raw_recomputed_plots'], embedded_pngs)
    assert data['classification'] == 'HISTORICAL_G2_RAW_RECOMPUTE_NOT_NEW_LIVE'
    assert data['provenance'] == {
        'registry_sha256': receipt['registry_sha256'], 'raw_sha256': RAW_SHA,
        'recompute_source_sha256': receipt['source_sha256'], 'candidate_record_recomputations': count}
    plotted_tasks = data['tasks_from_new_results']
    assert len(plotted_tasks) == len(tasks)
    for i, (task, plotted) in enumerate(zip(tasks, plotted_tasks)):
        expected = {'task': i, 'source_run_id': task['source_run_id'],
                    'partition': task['provenance']['partition'], 'parameters': task['parameters'],
                    'order': task['order'], 'record_ids': [r['record_id'] for r in task['records']]}
        assert {k: plotted[k] for k in expected} == expected
        metric = plotted['summary_from_new_raw_results']
        if 'summary' in task:
            assert metric == {k: task['summary'][k] for k in metric}
        assert metric['n_records'] == len(task['records'])
        assert metric['n_input'] == sum(metric[k] for k in ('n_final', 'n_filtered', 'n_direction_removed', 'n_dp_removed'))
    episodes = registry['episode_selections'] if topic == 'modes' else []
    assert receipt['selections'] == [
        {'episode_id': e['episode_id'], 'record_id': e['record_id'],
         'selected_config_id': e['selected_config_id'], 'selection_match': True} for e in episodes]
    plotted_episodes = data['episodes_from_new_results']
    assert len(plotted_episodes) == len(episodes)
    groups = defaultdict(list)
    for e, plotted in zip(episodes, plotted_episodes):
        assert {k: plotted[k] for k in ('episode_id', 'record_id', 'mode', 'selected_config_id')} == {
            k: e[k] for k in ('episode_id', 'record_id', 'mode', 'selected_config_id')}
        assert plotted['candidate_evaluations'] == len(e['candidate_ids']) == len(e['trace_tasks'])
        mapping = dict(zip(e['candidate_ids'], e['trace_tasks']))
        ref_task = next(t for t in e['trace_tasks'] if tasks[t]['parameters'] == {
            'dt': 30, 'distance': 400, 'min_points': 5, 'min_length': 65, 'direction': 35, 'dp': 5})
        for name, ti in [('new_selected_metrics', mapping[e['selected_config_id']]), ('new_R0_metrics', ref_task)]:
            metric = plotted[name]
            summary = plotted_tasks[ti]['summary_from_new_raw_results']
            assert all(metric[k] == summary[k] for k in metric.keys() & summary.keys())
            assert metric['no_output'] == bool(summary['n_no_output_records'])
            assert metric['all_filtered'] == bool(summary['n_all_filtered_records'])
        comparison = plotted['new_comparison']
        assert comparison['coverage_delta'] == (plotted['new_selected_metrics']['common_covered_points'] -
                                                 plotted['new_R0_metrics']['common_covered_points'])
        assert not comparison['strict_gain'] or comparison['feasible']
        groups[(plotted['partition'], plotted['mode'])].append(plotted)
    if topic == 'modes':
        assert len(data['pooled_mode_readings']) == len(groups) == 8
        for pooled in data['pooled_mode_readings']:
            rows = groups[(pooled['partition'], pooled['mode'])]
            assert pooled == {'partition': pooled['partition'], 'mode': pooled['mode'],
                'record_episode_observations': len(rows), 'original_records': len({r['record_id'] for r in rows}),
                'selected': {k: sum(r['new_selected_metrics'][k] for r in rows) for k in COUNTS},
                'R0': {k: sum(r['new_R0_metrics'][k] for r in rows) for k in COUNTS},
                'strict_protected_gain': sum(r['new_comparison']['strict_gain'] for r in rows),
                'protection_failed': sum(not r['new_comparison']['feasible'] for r in rows)}
        assert Counter(e['mode'] for e in episodes) == {m: 96 for m in
            ('llm-only', 'search-only', 'llm+search', 'llm+memory+search')}
    return {'topic': topic, 'record_candidate_recomputations': count, 'registry_tasks': len(tasks),
            'record_episode_selections': len(episodes), 'new_figures': receipt['raw_recomputed_plots']['figure_count'],
            'elapsed_seconds_actual_execution': receipt['elapsed_seconds']}


def production_check(root, evidence, work, embedded_pngs):
    """Read the actually rebuilt shards, without executing any processing code."""
    directory = evidence/'artifacts/production'
    manifest_path = directory/'manifest.json'
    manifest, receipt = read(manifest_path), read(directory/'recompute_receipt.json')
    current = read(root/'task1/evidence/goal3/current_runs.json')
    original_path = root/'task1/evidence/goal3/runs'/current['production']/'manifest.json'
    original = read(original_path)
    freeze = read(root/'task1/evidence/goal3/production_freeze.json')
    assert receipt['status'] == 'VERIFIED' and receipt['mode'] == 'FULL_RECOMPUTE'
    assert receipt['new_model_calls'] == 0 and receipt['actual_full_shard_hash_equality'] is True
    assert receipt['source_sha256'] == sha(root/'task1/goal3/reproduce.py')
    assert manifest['status'] == 'MACHINE_VERIFIED_PENDING_C' and manifest['recompute'] is True
    assert manifest['partition'] == 'FULL_PRODUCTION' and manifest['run_id'] == 'FULL_RECOMPUTE'
    assert manifest['source_hashes'] == original['source_hashes'] == freeze['processing_source_hashes']
    assert manifest['input_ids'] == manifest['completed_record_ids'] == original['input_ids'] == freeze['input_ids']
    assert len(manifest['input_ids']) == len(set(manifest['input_ids'])) == receipt['raw_records'] == 11386
    assert manifest['strategies'] == original['strategies']
    assert manifest['strategy_ids'] == original['strategy_ids'] == freeze['strategy_ids']
    assert manifest['parent_cache'] is None and manifest['cached_trace_rechecks'] == 0
    assert manifest['new_record_model_calls'] == 0 and manifest['failed_records'] == []
    assert manifest['processing_evaluations'] == receipt['record_evaluations'] == 22772
    assert manifest['review_record_calls'] == manifest['strategy_record_observations'] == 22772
    assert manifest['reused_identical_configuration_observations'] == 0
    for key in ('shards', 'record_metrics', 'comparisons', 'P_comparisons'):
        assert manifest[key] == original[key], ('PRODUCTION_DERIVATIVE_DIFF', key)
    assert len(manifest['shards']) == 285
    if (root/'.git').exists():
        assert manifest['code_identity_source'] == 'ACTUAL_LOCAL_GIT_HEAD'
        for name, digest in manifest['source_hashes'].items():
            blob = subprocess.check_output(['git', 'show', manifest['code_sha']+':'+name], cwd=root)
            assert hashlib.sha256(blob).hexdigest() == digest
    else:
        assert manifest['code_identity_source'] == 'FROZEN_SOURCE_BUNDLE'
        assert manifest['code_sha'] == freeze['processing_code_sha']
    assert sha(work/'production/manifest.json') == sha(manifest_path)
    for path, digest in manifest['source_hashes'].items():
        assert sha(inside(root, path)) == digest
    for path, digest in manifest['bindings'].items():
        assert sha(inside(root, path)) == digest
    data = figure_check(root, directory, receipt['raw_recomputed_plots'], embedded_pngs)
    assert data['classification'] == 'FULL_PRODUCTION_NEW_RAW_RECOMPUTE'
    assert data['new_manifest_sha256'] == sha(manifest_path)
    assert data['new_shard_sha256'] == [s['sha256'] for s in manifest['shards']]
    assert len(data['record_readings_from_new_shards']) == 11386
    raw = read(root/'task1/作业/作业/traj_dict.json')
    assert set(raw) == set(manifest['input_ids']) and sum(len(v[0]) for v in raw.values()) == 1173410
    totals = {name: Counter() for name in manifest['strategy_ids']}
    ids, rows_count, best, selected, pilot = [], 0, None, None, None
    new_shard_checks = []
    for si, entry in enumerate(manifest['shards']):
        shard = inside(work/'production', entry['path'])
        assert sha(shard) == entry['sha256'] and shard.stat().st_size == entry['bytes']
        local_ids = []
        with gzip.open(shard, 'rt', encoding='utf8') as stream:
            for line in stream:
                row = json.loads(line); rid = row['record_id']; local_ids.append(rid); ids.append(rid)
                plotted = data['record_readings_from_new_shards'][rows_count]
                assert plotted['record_id'] == rid and set(plotted['new_trace_metrics']) == set(totals)
                for name in manifest['strategy_ids']:
                    trace = row['traces'][row['strategy_configs'][name]]; metrics = trace['metrics']
                    assert metrics['n_input'] == len(raw[rid][0])
                    actions = Counter(p['action'] for p in trace['point_actions'])
                    fate = {'n_filtered': actions['filtered'], 'n_direction_removed': actions['denoised'],
                            'n_dp_removed': actions['simplified'], 'n_final': actions['retained']}
                    assert all(fate[k] == metrics[k] for k in fate) and sum(fate.values()) == len(raw[rid][0])
                    assert plotted['new_trace_metrics'][name] == {k: metrics[k] for k in COUNTS}
                    totals[name].update({k: metrics[k] for k in COUNTS}); totals[name]['n_records'] += 1
                final = data['case']['deployed_id']
                gain = row['comparisons'][final+'|R0']['coverage_delta']
                score = (gain, -int(rid))
                if best is None or score > best:
                    best, selected = score, row
                if rid == '246':
                    pilot = row['traces'][row['strategy_configs']['R0']]
                rows_count += 1
        assert local_ids == entry['input_ids'] and len(local_ids) == entry['records']
        new_shard_checks.append({'path': entry['path'], 'sha256': entry['sha256'], 'records': len(local_ids),
                                 'actual_new_file_checked': True, 'actual_original_point_fates_checked': True})
        if si % 50 == 0:
            print(json.dumps({'review': 'new_notebook_production_shards', 'shards': si+1, 'records': rows_count}), flush=True)
    assert ids == manifest['input_ids'] and rows_count == 11386
    assert data['totals_from_new_shards'] == dict(totals)
    for name in totals:
        assert dict(totals[name]) == {k: manifest['record_metrics'][name][k] for k in totals[name]}
        assert totals[name]['n_input'] == 1173410
    assert selected is not None and pilot is not None
    assert data['case']['record_id'] == selected['record_id'] and data['case']['coverage_delta'] == best[0]
    assert data['case']['R0'] == selected['traces'][selected['strategy_configs']['R0']]
    assert data['case']['deployed'] == selected['traces'][selected['strategy_configs'][data['case']['deployed_id']]]
    return {'raw_records': rows_count, 'raw_points': 1173410, 'record_candidate_recomputations': 22772,
            'new_shards_actual_hash_checked': len(new_shard_checks), 'new_shard_checks': new_shard_checks,
            'new_figures': receipt['raw_recomputed_plots']['figure_count'], 'cached_trace_rechecks': 0,
            'code_identity_source': manifest['code_identity_source'], 'code_sha': manifest['code_sha'],
            'source_hashes': manifest['source_hashes'], 'input_scope_sha256': hashlib.sha256(
                json.dumps(ids, separators=(',', ':')).encode()).hexdigest(),
            'descriptive_case_id': selected['record_id'], 'pilot_reference_trace': pilot,
            'elapsed_seconds_actual_processing': manifest['elapsed_seconds']}


class TableReader(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows = []; self.row = None; self.cell = None
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        if tag in ('td', 'th'): self.cell = ''
    def handle_data(self, value):
        if self.cell is not None: self.cell += value
    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            self.row.append(self.cell); self.cell = None
        if tag == 'tr': self.rows.append(self.row); self.row = None


def basic_demonstration_check(root, evidence, executed, result, pilot):
    synthetic_path = root/'task1/evidence/goal2/counterexamples/formal-02/synthetic_cases.json'
    synthetic = read(synthetic_path)
    assert synthetic['classification'] == 'SYNTHETIC_COUNTEREXAMPLE'
    assert synthetic['status'] == 'ENGINEERING_VERIFIED' and synthetic['real_data_accuracy_claim'] is False
    executions = sum(len(c['executions']) for c in synthetic['cases'])
    assert executions == result['synthetic_pipeline_recomputations'] == 19
    assert sum(len(c['known_answer_checks']) for c in synthetic['cases']) == synthetic['known_answer_check_count'] == 25
    assert all(check['passed'] for c in synthetic['cases'] for check in c['known_answer_checks'])
    assert result['known_exposed_pilot_runs'] == 1
    cells = [c for c in executed['cells'] if c['cell_type'] == 'code']
    synthetic_cell = next(c for c in cells if 'synthetic_recomputations=0' in text(c['source']))
    output = ''.join(text(o.get('text', '')) for o in synthetic_cell['outputs'])
    assert '当前内核已知答案处理链实际复算： 19' in output
    pilot_cell = next(c for c in cells if "pilot=adapt('246',raw['246'])" in text(c['source']))
    output = ''.join(text(o.get('text', '')) for o in pilot_cell['outputs'])
    assert '演示身份：已暴露 PILOT 246；原始点数 108' in output
    plot_cell = next(c for c in cells if "WORK/'pilot_steps.svg'" in text(c['source']))
    table_html = next(text(o['data']['text/html']) for o in plot_cell['outputs'] if 'text/html' in o.get('data', {}))
    table = TableReader(); table.feed(table_html)
    assert len(table.rows) == 2
    for key, displayed in zip(*table.rows):
        expected = pilot['metrics'][key]
        assert displayed == ('不可用（见相应原因）' if expected is None else str(expected))
    svg, png = evidence/'artifacts/pilot_steps.svg', evidence/'artifacts/pilot_steps.png'
    assert svg.is_file() and png.is_file()
    embedded = {hashlib.sha256(base64.b64decode(text(o['data']['image/png']))).hexdigest()
                for o in plot_cell['outputs'] if 'image/png' in o.get('data', {})}
    assert sha(png) in embedded
    # Read the PNG IHDR and pHYs chunks without depending on the plotting package.
    image = png.read_bytes(); assert image[:8] == b'\x89PNG\r\n\x1a\n'
    position, dimensions, dpi = 8, None, None
    while position < len(image):
        size = int.from_bytes(image[position:position+4], 'big'); kind = image[position+4:position+8]
        chunk = image[position+8:position+8+size]
        if kind == b'IHDR': dimensions = [int.from_bytes(chunk[:4], 'big'), int.from_bytes(chunk[4:8], 'big')]
        if kind == b'pHYs' and chunk[8] == 1: dpi = [int.from_bytes(chunk[:4], 'big')*.0254, int.from_bytes(chunk[4:8], 'big')*.0254]
        position += size+12
    assert dimensions == [2600, 800] and dpi and all(abs(value-200) < .02 for value in dpi)
    return {'synthetic_processing_chains': executions, 'historical_known_answer_checks': 25,
            'synthetic_real_data_accuracy_claim': False, 'known_exposed_pilot_id': '246', 'pilot_points': 108,
            'pilot_runs': 1, 'pilot_png_pixels': dimensions, 'pilot_png_dpi': dpi,
            'pilot_numeric_table_matches_actual_rebuilt_R0_trace': True}


def isolated_package_check(root):
    """Read-only import/identity probe, never a substitute for the two FULL runs."""
    assert root != REVIEW_ROOT and not (root/'.git').exists()
    package = read(root/'PACKAGE_MANIFEST.json')
    assert package['package_status'] == 'REVIEW_ONLY' and package['metadata']['student_id'] == 'NOT_AVAILABLE'
    members, seen = [], set()
    for item in package['members']:
        path = inside(root, item['path'])
        assert path not in seen and not path.is_symlink(); seen.add(path)
        assert not any(parent.is_symlink() for parent in path.parents if parent != root.parent)
        assert path.stat().st_size == item['bytes'] and sha(path) == item['archive_sha256']
        members.append({'path': item['path'], 'sha256': item['archive_sha256']})
    code = r'''
import json,sys,hashlib
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
from task1.workflow.io import ROOT
from task1.workflow.g2_provider import ExperimentProvider
from task1.workflow.provider import CodexProvider
def forbid(*args,**kwargs):raise AssertionError('UNEXPECTED_PROVIDER_CALL_IN_C_IMPORT_PROBE')
ExperimentProvider.call=forbid;CodexProvider.call=forbid
from task1.goal3 import reproduce,offline_plots
from task1.goal3.runtime import source_snapshot,code_identity,execution_gate
from task1.workflow import g2_modes
assert ROOT==root and not (root/'.git').exists()
frozen=json.loads((root/'task1/evidence/goal3/production_freeze.json').read_text())
assert source_snapshot()==frozen['processing_source_hashes']
identity=code_identity(source_snapshot(),'FULL_PRODUCTION',True)
assert identity['code_identity_source']=='FROZEN_SOURCE_BUNDLE'
execution_gate('FULL_PRODUCTION',frozen['input_ids'],frozen['strategy_ids'])
modules={}
for name,module in sorted(sys.modules.items()):
 if name=='task1' or name.startswith('task1.'):
  file=getattr(module,'__file__',None)
  if file:
   path=Path(file).resolve();assert root in path.parents,(name,str(path))
   modules[name]={'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
  else:
   assert all(root in Path(p).resolve().parents or root==Path(p).resolve() for p in module.__path__)
raw=root/'task1/作业/作业/traj_dict.json'
print(json.dumps({'status':'VERIFIED','new_trajectory_processing':0,'new_model_calls':0,
 'all_imported_task1_modules_from_extracted_package':True,'modules':modules,
 'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),**identity}))
'''
    done = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(root)], cwd=root,
                          capture_output=True, text=True, check=True, timeout=60)
    probe = json.loads(done.stdout)
    assert probe['status'] == 'VERIFIED' and probe['raw_sha256'] == RAW_SHA
    return {'package_manifest_sha256': sha(root/'PACKAGE_MANIFEST.json'), 'original_members_unchanged': len(members),
            'package_members_checked': members, 'isolated_import_probe': probe,
            'import_probe_does_not_replace_full_notebook_execution': True}


def audit(args):
    root, evidence = args.project_root.resolve(), args.evidence.resolve()
    execution = read(evidence/'execution_receipt.json')
    assert execution['status'] == 'VERIFIED' and execution['failure'] is None
    assert execution['started_from_clean_outputs_and_new_kernel'] is True
    assert Path(execution['kernel_cwd']).resolve() == root
    work = Path(execution['temporary_work_directory']).resolve()
    assert work != root and root not in work.parents
    executor = args.executor_source.resolve() if args.executor_source else root/'task1/goal3/execute_notebook.py'
    assert execution['source_sha256'] == sha(executor)
    executed_path = evidence/args.input_notebook.name
    assert executed_path.is_file()
    assert sha(executed_path) == execution['executed_notebook_sha256']
    if args.source_git_ref:
        assert root == REVIEW_ROOT, 'Git source lookup is confined to repository audit'
        source = subprocess.check_output(['git', 'show', args.source_git_ref+':'+args.input_notebook.as_posix()], cwd=root)
        input_identity = {'type': 'ACTUAL_PRE_EXECUTION_GIT_BLOB', 'commit': args.source_git_ref,
                          'path': args.input_notebook.as_posix()}
    else:
        source_path = inside(root, args.input_notebook)
        source = source_path.read_bytes()
        input_identity = {'type': 'ACTUAL_INPUT_FILE', 'path': args.input_notebook.as_posix()}
    assert hashlib.sha256(source).hexdigest() == execution['notebook_source_sha256']
    original, executed = json.loads(source), read(executed_path)
    assert len(original['cells']) == len(executed['cells'])
    for left, right in zip(original['cells'], executed['cells']):
        assert left['cell_type'] == right['cell_type'] and text(left['source']) == text(right['source'])
        assert left['id'] == right['id']
    code = [(i, c) for i, c in enumerate(executed['cells']) if c['cell_type'] == 'code']
    assert len(code) == execution['total_code_cells'] == execution['executed_code_cells']
    events = read(evidence/'cells.json')
    assert len(events) == len(code)
    last_time = None
    for count, ((i, cell), event) in enumerate(zip(code, events), 1):
        assert cell['execution_count'] == event['execution_count'] == count
        assert event['cell_index'] == i and event['kernel_status'] == 'ok'
        moment = datetime.fromisoformat(event['at'])
        assert last_time is None or moment >= last_time
        last_time = moment
        assert all(output['output_type'] != 'error' for output in cell.get('outputs', []))
        ast.parse(text(cell['source']))
    assert last_time <= datetime.fromisoformat(execution['at'])
    notebook_text = executed_path.read_text()
    assert all(marker not in notebook_text for marker in ('/home/', '/Users/', 'C:\\\\Users\\\\'))
    all_code = '\n'.join(text(c['source']) for _, c in code)
    for required in ("MODE = 'FULL_RECOMPUTE'", 'ENABLE_LIVE = False',
                     'ExperimentProvider.call = forbid_provider', 'CodexProvider.call = forbid_provider',
                     "provider_observation['attempted_new_calls'] == 0", 'MODULE_ROOT.resolve() == ROOT'):
        assert required.replace(' ', '') in all_code.replace(' ', ''), required
    embedded_pngs = {hashlib.sha256(base64.b64decode(text(o['data']['image/png']))).hexdigest()
        for _, c in code for o in c['outputs'] if 'image/png' in o.get('data', {})}
    archived_figures = []
    for _, cell in code:
        for call in ast.walk(ast.parse(text(cell['source']))):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'figure':
                name = ast.literal_eval(call.args[0])
                phase = next((ast.literal_eval(k.value) for k in call.keywords if k.arg == 'phase'), 'goal2')
                path = root/'task1/figures'/phase/(name+'.png')
                assert sha(path) in embedded_pngs, ('ARCHIVED_FIGURE_BYTES_DIFFER', name)
                archived_figures.append(path)
    listed = set()
    for entry in execution['preserved_artifacts']:
        path = inside(evidence, entry['path']); assert sha(path) == entry['sha256']
        assert path not in listed; listed.add(path)
    assert listed == {p.resolve() for p in (evidence/'artifacts').rglob('*') if p.is_file()}
    result = read(evidence/'artifacts/notebook_receipt.json')
    assert result['status'] == 'VERIFIED' and result['mode'] == 'FULL_RECOMPUTE'
    assert result['new_model_call_attempts_observed'] == 0 and result['historical_recompute_is_new_live'] is False
    assert result['raw_sha256_unchanged'] and result['module_root_matches_current_project']
    stage = read(root/'task1/evidence/goal2/result_summary.json')
    memory_path = inside(root, stage['memory']['snapshot_path'])
    assert sha(memory_path) == result['memory_sha256_before'] == result['memory_sha256_after'] == stage['memory']['snapshot_sha256']
    raw_path = root/'task1/作业/作业/traj_dict.json'; assert sha(raw_path) == RAW_SHA == stage['data']['raw_sha256']
    final_text = ''.join(text(o.get('text', '')) for o in code[-1][1]['outputs'])
    embedded_result, _ = json.JSONDecoder().raw_decode(final_text.lstrip())
    assert embedded_result == result
    registry_path = root/'task1/evidence/goal3/historical_recompute_registry.json.gz'
    binding = read(root/'task1/evidence/goal3/historical_recompute_registry_binding.json')
    assert sha(registry_path) == binding['sha256']
    registry = json.loads(gzip.decompress(registry_path.read_bytes()))
    for name, digest in registry['bindings'].items():
        assert sha(inside(root, name)) == digest
    production, demonstration = None, None
    if result['notebook'] == 'llm_system':
        history = historical_check(root, evidence, 'modes', registry, embedded_pngs)
        assert history['record_candidate_recomputations'] == result['historical_record_candidate_recomputations'] == 6001
        assert history['record_episode_selections'] == result['recomputed_original_record_episode_selections'] == 384
        assert len(code) == 8
        scope = 'ACTUAL_COMPLETED_SYSTEM_NOTEBOOK_FULL_RECOMPUTE'
    elif result['notebook'] == 'basic':
        history = historical_check(root, evidence, 'parameters', registry, embedded_pngs)
        assert history['record_candidate_recomputations'] == result['historical_record_candidate_recomputations'] == 9720
        assert len(code) == 12
        production = production_check(root, evidence, work, embedded_pngs)
        assert production['raw_records'] == result['production_raw_records']
        assert production['record_candidate_recomputations'] == result['production_record_evaluations']
        demonstration = basic_demonstration_check(root, evidence, executed, result, production.pop('pilot_reference_trace'))
        scope = 'ACTUAL_COMPLETED_BASIC_NOTEBOOK_FULL_RECOMPUTE'
    else:
        raise AssertionError('UNRECOGNIZED_COMPLETED_NOTEBOOK')
    promotion = evidence/'canonical_copy_receipt.json'
    promotion_paths = []
    if promotion.is_file():
        copy = read(promotion)
        if 'destination' in copy:
            canonical = inside(root, copy['destination'])
            assert sha(canonical) == sha(executed_path) == copy['sha256']
            assert copy['prior_unexecuted_source_sha256'] == execution['notebook_source_sha256']
        else:
            assert copy['status'] == 'EXACT_EXECUTED_BYTES_PROMOTED'
            canonical = inside(root, copy['canonical'])
            assert sha(canonical) == sha(executed_path) == copy['executed_sha256'] == copy['canonical_sha256']
            assert copy['all_cell_sources_unchanged'] is True
            assert copy['previous_source_sha256'] == execution['notebook_source_sha256']
            assert copy['execution_receipt_sha256'] == sha(evidence/'execution_receipt.json')
            prior = inside(root, copy['previous_source_archive'])
            assert prior.read_bytes() == source and sha(prior) == execution['notebook_source_sha256']
            promotion_paths.append(prior)
        promotion_paths.append(canonical)
    isolation = isolated_package_check(root) if root != REVIEW_ROOT else None
    sources = dict(registry['bindings'])
    for name in ('task1/goal3/reproduce.py', 'task1/goal3/offline_plots.py'):
        sources[name] = sha(root/name)
    for name in ('task1/goal3/execute_notebook.py', 'task1/goal3/notebooks.py'):
        if (root/name).is_file(): sources[name] = sha(root/name)
    if production: sources.update(production.pop('source_hashes'))
    supporting = [root/'task1/evidence/goal2/result_summary.json', memory_path, registry_path,
                  root/'task1/evidence/goal3/historical_recompute_registry_binding.json',
                  root/'task1/evidence/goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json',
                  root/'task1/evidence/goal2/tables/memory_consumption.csv',
                  root/'task1/evidence/goal3/current_runs.json', root/'task1/evidence/goal3/production_freeze.json']
    current = read(root/'task1/evidence/goal3/current_runs.json')
    for key in ('production', 'confirmation'):
        if key in current:
            supporting.append(root/'task1/evidence/goal3/runs'/current[key]/'manifest.json')
    supporting.extend(promotion_paths)
    if demonstration:
        supporting.append(root/'task1/evidence/goal2/counterexamples/formal-02/synthetic_cases.json')
    targets, external_members = [], []
    for path in sorted({*listed, executed_path, evidence/'execution_receipt.json', evidence/'cells.json',
                        *supporting, *archived_figures, *([promotion] if promotion.is_file() else [])}):
        if REVIEW_ROOT in path.parents:
            relative = str(path.relative_to(REVIEW_ROOT))
        elif root in path.parents:
            external_members.append({'path_within_extracted_project': str(path.relative_to(root)), 'sha256': sha(path)})
            continue
        else:
            # External evidence must first be preserved in the review repository
            # before a Journal closure can bind it; do not alias it to a local file.
            external_members.append({'path_within_external_evidence': str(path.relative_to(evidence)), 'sha256': sha(path)})
            continue
        targets.append({'path': relative, 'sha256': sha(path)})
    return {'role_context': '/root/c_protocol', 'target_id': args.target_id, 'status': 'VERIFIED',
        'at': datetime.now(timezone.utc).isoformat(), 'scope': scope,
        'targets': targets, 'source_hashes': sources, 'input_identity': input_identity,
        'input_notebook_sha256': execution['notebook_source_sha256'],
        'review_checker_sha256': sha(Path(__file__)),
        'executed_notebook_sha256': sha(executed_path),
        'checked_components': [
            'Actual clean new-kernel execution: all code cells, sequential successful events and error-free outputs',
            'Exact pre-execution source byte hash and unchanged cell identities/source after execution',
            'All preserved artifact hashes, final receipt embedded in Notebook output and canonical promotion bytes',
            'Every historical registry task and saved record-episode selection represented once with exact ordered scope',
            'Raw-loop implementation calls run_record and independent trusted review; old trace hashes and summaries are equality targets',
            'All newly plotted task/episode identities and metrics cross-bound; pooled plot totals independently aggregated',
            'All new SVG/PDF/PNG and plot-data hashes checked; new PNG exists in the executed Notebook',
            'Every displayed archived figure also matches its actual PNG bytes; historical/new figure labels remain distinct',
            'Registered two Provider entrypoints blocked and observed attempts=0; frozen raw and memory hashes unchanged',
            'Notebook source/outputs contain no personal absolute paths; actual project module-root assertion passed'] + ([
            'All 285 actually rebuilt production shard files match the accepted original bytes and exact ordered full scope',
            'Every rebuilt production point fate and plotted record metric independently reduced; all totals and chosen descriptive trace agree',
            '19 actual synthetic chains executed with exact saved output hash assertions; 25 historical known-answer checks remain explicitly synthetic',
            'Exposed pilot246 actual output table agrees with the rebuilt R0 trace; native PNG is embedded at2600x800 pixels and200dpi'] if production else []),
        'unchecked_components': [
            'Reviewer does not re-run the full numerical workload; actual full execution is checked from source and preserved evidence',
            'Other Notebook/ZIP executions and aggregate parent acceptance require their own completed evidence and independent review',
            'Underlying invisible requests/currency costs remain unknown; registered Provider attempts are the measured boundary',
            'Entire notebooks parent task is not closed by this single-system receipt'],
        'history': history, 'production': production, 'demonstration': demonstration,
        'isolated_package': isolation, 'external_checked_files': external_members,
        'executed_code_cells': len(code), 'new_provider_attempts_observed': 0,
        'external_kernel_executor': {'sha256': sha(executor),
            'role': 'kernel orchestration only; numerical modules and raw inputs must resolve from actual kernel cwd'},
        'archived_figure_count': len(archived_figures),
        'raw_sha256': RAW_SHA, 'memory_sha256': sha(memory_path),
        'elapsed_seconds_actual_execution': execution['elapsed_seconds'],
        'reviewer_new_numerical_processing': 0, 'reviewer_new_model_calls': 0, 'errors': [],
        'actual_command': ' '.join(__import__('sys').argv)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, default=REVIEW_ROOT)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--input-notebook', type=Path, required=True)
    parser.add_argument('--source-git-ref')
    parser.add_argument('--executor-source', type=Path,
                        help='Explicit external kernel orchestrator when auditing a ZIP that does not bundle this helper')
    parser.add_argument('--target-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args)
    with args.output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'status': result['status'], 'history': result['history'],
                      'targets': len(result['targets']), 'receipt_sha256': sha(args.output)}))


if __name__ == '__main__':
    main()
