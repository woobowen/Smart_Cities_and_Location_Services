"""Independent read-only audit of Goal 3 plot data and the full-boundary handoff.

This reduces hash-bound CSVs and checks actual example traces. It does not run
trajectory processing, change the candidate, or replace C's raw numerical audit.
"""
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = ROOT/'task1/evidence/goal3'
FIG = ROOT/'task1/figures/goal3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources, checks = {}, []

    def check(label, actual, expected=True):
        checks.append({'check': label, 'passed': actual == expected,
                       'actual': actual, 'expected': expected})

    def source(path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT/path
        sources[str(path.relative_to(ROOT))] = sha(path)
        return path

    def load(path):
        return json.loads(source(path).read_text())

    def table(run, name):
        with source(EV/'runs'/run/'analysis'/name).open() as stream:
            return list(csv.DictReader(stream))

    def receipt_binds(receipt, path):
        rel = str(path.relative_to(ROOT))
        check('receipt_binds:'+rel, any(t['path'] == rel and t['sha256'] == sha(path)
                                      for t in receipt['targets']))

    current = load(EV/'current_runs.json')
    manifest = load(FIG/'figure_manifest.json')
    data = load(FIG/'figure_data.json')
    check('figure_data_hash', sha(FIG/'figure_data.json'), manifest['figure_data_sha256'])
    check('seven_figures', len(manifest['figures']), 7)
    check('source_crs_unknown', manifest['source_crs'], 'UNVERIFIED')
    check('conditional_work_units', manifest['units'], 'conditional working metres')
    for rel, digest in manifest['sources'].items():
        check('figure_source:'+rel, sha(source(rel)), digest)
    source('task1/scripts/build_goal2_figures.py')
    for item in manifest['figures']:
        for fmt, output in item['formats'].items():
            path = source(FIG/output['file'])
            check('figure_file:'+path.name, sha(path), output['sha256'])
        render = source(FIG/item['pdf_render']['file'])
        check('render_file:'+item['name'], sha(render), item['pdf_render']['sha256'])
        check('render_dpi:'+item['name'], item['pdf_render']['dpi'] >= 200)
        info = subprocess.run(['pdfinfo', str(FIG/item['formats']['pdf']['file'])],
                              check=True, capture_output=True, text=True).stdout
        size = next(line for line in info.splitlines() if line.startswith('Page size:')).split()
        width, height = float(size[2]), float(size[4])
        with Image.open(render) as image:
            check('render_pixel_width:'+item['name'], abs(image.width-width*200/72) <= 1)
            check('render_pixel_height:'+item['name'], abs(image.height-height*200/72) <= 1)
        with Image.open(FIG/item['formats']['png']['file']) as image:
            check('print_png_pixels:'+item['name'], list(image.size), item['png_size_pixels'])

    run_manifests, metric_tables, pair_tables = {}, {}, {}
    for key in ('development', 'selection', 'confirmation', 'production'):
        run = current[key]
        m = load(EV/'runs'/run/'manifest.json'); run_manifests[key] = m
        raw_review = load(EV/'independent_c'/(run+'_receipt.json'))
        check('actual_C_status:'+key, raw_review['status'], 'VERIFIED')
        receipt_binds(raw_review, EV/'runs'/run/'manifest.json')
        metric_tables[key] = table(run, 'record_metrics.csv')
        pair_tables[key] = table(run, 'record_pairs.csv')
        check('input_ids_unique:'+key, len(set(m['input_ids'])), len(m['input_ids']))
        check('metric_complete_scope:'+key, len(metric_tables[key]),
              len(m['input_ids'])*len(m['strategy_ids']))
        # The independent C table auditor binds the complete production table bytes.
        if key == 'production':
            derivative_review = load(EV/'independent_c'/(run+'_analysis_receipt.json'))
            check('production_table_C_status', derivative_review['status'], 'VERIFIED')
            for name in ('record_metrics.csv', 'record_pairs.csv'):
                receipt_binds(derivative_review, EV/'runs'/run/'analysis'/name)
        for strategy in m['strategy_ids']:
            rows = [r for r in metric_tables[key] if r['strategy'] == strategy]
            check('metric_exact_ids:'+key+':'+strategy,
                  sorted(r['record_id'] for r in rows), sorted(m['input_ids']))
            for field in ('n_input','n_final','n_filtered','n_direction_removed',
                          'n_dp_removed','common_covered_points','common_uncovered_points'):
                check('metric_sum:'+key+':'+strategy+':'+field,
                      sum(int(r[field]) for r in rows), m['record_metrics'][strategy][field])

    for item in data['development_candidates']:
        name = item['strategy']
        rows = [r for r in pair_tables['development']
                if r['candidate_id'] == name and r['reference_id'] == 'R0']
        pairs = {'coverage_delta': sum(int(r['coverage_delta']) for r in rows),
                 'protected': sum(r['feasible'] == 'True' for r in rows),
                 'gain_records': sum(r['strict_gain'] == 'True' for r in rows),
                 'failed': sum(r['feasible'] != 'True' for r in rows),
                 'final_points': sum(int(r['n_final']) for r in metric_tables['development']
                                     if r['strategy'] == name)}
        for field, value in pairs.items():
            check('development_plot:'+name+':'+field, item[field], value)

    sdata = data['selection_tradeoffs']
    failures = []
    for item in sdata['counts']:
        name = item['strategy']
        rows = [r for r in pair_tables['selection']
                if r['candidate_id'] == name and r['reference_id'] == 'R0']
        for field, value in {'gain': sum(r['strict_gain'] == 'True' for r in rows),
            'unchanged': sum(r['feasible'] == 'True' and r['strict_gain'] != 'True' for r in rows),
            'failed': sum(r['feasible'] != 'True' for r in rows)}.items():
            check('selection_plot:'+name+':'+field, item[field], value)
        failures.extend(r for r in rows if r['feasible'] != 'True')
    check('selection_all_failure_identities',
          sorted((r['strategy'],r['record_id']) for r in sdata['all_failures']),
          sorted((r['candidate_id'],r['record_id']) for r in failures))
    for r in sdata['all_failures']:
        stored = next(p for p in failures if p['candidate_id'] == r['strategy']
                      and p['record_id'] == r['record_id'])
        for field in ('baseline_common_max','candidate_max_on_baseline_covered'):
            check('selection_failure_value:'+r['strategy']+':'+r['record_id']+':'+field,
                  r[field], float(stored[field]))
    check('selection_no_unplotted_failures', sdata['noncomparable_failures'], 0)
    check('selection_plotted_6_strategy_record_failures', sdata['plotted_failures'], 6)

    for key, item in data['point_fates_and_coverage'].items():
        m = run_manifests[key]
        check('fates_n_records:'+key, item['records'], len(m['input_ids']))
        check('fates_all_points:'+key, item['raw_points'], m['record_metrics']['R0']['n_input'])
        for strategy, summary in item['summaries'].items():
            check('fates_exact_summary:'+key+':'+strategy, summary, m['record_metrics'][strategy])
            check('fates_partition:'+key+':'+strategy,
                  sum(summary[k] for k in ('n_filtered','n_direction_removed','n_dp_removed','n_final')),
                  item['raw_points'])
            check('coverage_is_not_stored_count:'+key+':'+strategy,
                  summary['common_covered_points'] >= summary['n_final'])

    final = data['final_confirmation_pairs']
    frozen = load(EV/'final_freeze.json')
    check('confirmation_fixed_primary', final['proposed'], frozen['primary_strategy'])
    rows = [r for r in pair_tables['confirmation']
            if r['candidate_id'] == final['proposed'] and r['reference_id'] == 'R0']
    stored_by_id = {r['record_id']: r for r in rows}
    check('confirmation_all_600', len(final['pairs']), 600)
    check('confirmation_exact_ids', sorted(r['record_id'] for r in final['pairs']), sorted(stored_by_id))
    for p in final['pairs']:
        q = stored_by_id[p['record_id']]
        for field in ('baseline_common_max','candidate_max_on_baseline_covered'):
            check('confirmation_plot_value:'+p['record_id']+':'+field,
                  p[field], float(q[field]) if q[field] else None)
        check('confirmation_plot_feasibility:'+p['record_id'],p['feasible'],q['feasible'] == 'True')
        check('confirmation_plot_gain:'+p['record_id'],p['strict_gain'],q['strict_gain'] == 'True')
    valid = [r for r in rows if r['baseline_common_max'] and r['candidate_max_on_baseline_covered']]
    check('confirmation_geometry_comparable', len(valid), 345)
    check('confirmation_geometry_null_retained_elsewhere',len(rows)-len(valid),255)
    check('confirmation_strata_total',sum(g['n'] for g in final['strata']),600)
    for group in final['strata']:
        selected = [r for r in rows if r['stratum'] == group['stratum']]
        vals = {'n':len(selected),'gain':sum(r['feasible']=='True' and r['strict_gain']=='True' for r in selected),
                'unchanged':sum(r['feasible']=='True' and r['strict_gain']!='True' for r in selected),
                'failed':sum(r['feasible']!='True' for r in selected)}
        for field, value in vals.items():
            check('confirmation_stratum:'+group['stratum']+':'+field, group[field], value)

    pm = run_manifests['production']
    pp = [r for r in pair_tables['production'] if r['candidate_id'] == current['final_strategy']
          and r['reference_id']=='R0']
    final_metrics = [r for r in metric_tables['production'] if r['strategy']==current['final_strategy']]
    expected_extrema = {
        'largest_coverage_gain': max((int(r['coverage_delta']), r['record_id']) for r in pp),
        'largest_raw_geometry_error': max((float(r['common_max_error']) if r['common_max_error'] else -1,
                                          r['record_id']) for r in final_metrics),
        'largest_new_coverage_error': max((float(r['newly_covered_max_error']) if r['newly_covered_max_error'] else -1,
                                          r['record_id']) for r in pp)}
    cache = {}
    for case in data['production_trajectory_cases']:
        rid = case['record_id']
        check('trajectory_true_extremum:'+case['criterion'],
              (case['criterion_value'],rid),expected_extrema[case['criterion']])
        shard = next(s for s in pm['shards'] if rid in s['input_ids'])
        path = source(EV/'runs'/current['production']/shard['path'])
        check('example_shard_hash:'+rid,sha(path),shard['sha256'])
        if path not in cache:
            with gzip.open(path,'rt') as stream:
                cache[path] = {r['record_id']:r for r in map(json.loads,stream)}
        row = cache[path][rid]
        for figure_key, strategy in [('reference','R0'),('final',current['final_strategy'])]:
            trace = row['traces'][row['strategy_configs'][strategy]]
            check('trajectory_exact_trace:'+rid+':'+strategy,case[figure_key],trace)
            check('trajectory_units:'+rid+':'+strategy,trace['source_crs'],'UNVERIFIED')
        trace = case['reference']; xy = case['raw_xy_work_m']; ts = trace['source_record']['timestamps']
        check('trajectory_unmodified_work_xy:'+rid,xy,trace['source_record']['xy'])
        breaks = [i for i in range(1,len(xy))
                  if ts[i]-ts[i-1] > 30 or math.dist(xy[i],xy[i-1]) > 400]
        check('trajectory_raw_breaks_from_actual_neighbors:'+rid,
              [b['to_index'] for b in case['raw_breaks']],breaks)
        for name in ('reference','final'):
            for seg in case[name]['final_segments']:
                check('trajectory_no_break_bridge:'+rid+':'+name+':'+str(seg['indices'][0]),
                      not any(seg['indices'][0] < b <= seg['indices'][-1] for b in breaks))
        visible = case['display_original_indices']
        check('trajectory_origin_same_row:'+rid,case['origin_ENU_work_m'],xy[visible[0]])
        if case['criterion'] == 'largest_new_coverage_error':
            check('worst_added_point_complete_window',visible,[104,105,106,107])
            check('worst_added_record',rid,'352')
            check('worst_added_original_index',case['new_coverage_witness']['index'],105)
            check('worst_window_left_is_break',104 in breaks)
            check('worst_window_right_is_break',108 in breaks)
            for name, actions in [('reference',{104:'filtered',105:'filtered',106:'filtered',107:'filtered'}),
                                  ('final',{104:'retained',105:'denoised',106:'retained',107:'retained'})]:
                actual = {r['original_index']:r['action'] for r in case[name]['point_actions']
                          if r['original_index'] in visible}
                check('worst_window_fates:'+name,actual,actions)

    graph = data['goal3_actual_workflow']
    drawio = source(FIG/'goal3_actual_workflow.drawio')
    check('native_drawio_hash',sha(drawio),graph['drawio_sha256'])
    cells = ET.parse(drawio).getroot().findall('.//mxCell')
    vertices = {c.attrib['id']:c for c in cells if c.attrib.get('vertex')=='1'}
    edges = [c for c in cells if c.attrib.get('edge')=='1']
    check('editable_nodes_match_plot_data',sorted(vertices),sorted(n[0] for n in graph['nodes']))
    for node in graph['nodes']:
        check('editable_label:'+node[0],vertices[node[0]].attrib['value'],node[1])
        check('editable_geometry:'+node[0],vertices[node[0]].find('mxGeometry') is not None)
    check('editable_edges_match_plot_data',sorted((c.attrib['source'],c.attrib['target']) for c in edges),
          sorted(tuple(e[:2]) for e in graph['edges']))
    history = load(EV/'decision_history.json')
    check('decision_path_exact_source',data['incumbent_decision_path'],history)
    for path,digest in history['source_bindings'].items():
        check('decision_source_current:'+path,sha(source(path)),digest)
    check('decision_not_quality_score',history['not_quality_score'],True)
    check('decision_no_final_feedback_candidates',history['final_feedback_generated_new_candidates'],False)

    boundary = load(EV/'independent_c/new_coverage_boundary_receipt.json')
    check('independent_boundary_status',boundary['status'],'VERIFIED')
    interactions = load(EV/'interaction_candidates.json')
    check('19_interaction_entries',len(interactions['candidates']),19)
    last = interactions['candidates'][-1]
    check('full_boundary_last',last['candidate_id'],'IH-G3-FULL-BOUNDARY')
    for ref in last['Referenced_materials_and_experiments'] + [last['current_authority_ref']]:
        check('boundary_handoff_source:'+ref['path'],sha(source(ref['path'])),ref['sha256'])
    check('boundary_handoff_no_human_judgment',last['Human_Judgment']['status'],'NOT_AVAILABLE')
    check('boundary_handoff_no_quote',last['User_verbatim_and_source']['quotes'],[])
    for field in ('Tier','screenshot_spec','annotation_spec','report_order'):
        check('boundary_handoff_no_'+field,last[field],None)
    check('boundary_handoff_no_LOCK',last['Evidence_Lock'],'NOT_ASSIGNED_BY_THIS_HANDOFF')
    check('boundary_handoff_system_decision',last['Actual_decision']['type'],
          'SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES')
    check('boundary_handoff_root_context',last['Available_message_range']['root_context'],'/root')
    check('boundary_handoff_actual_time',last['Available_message_range']['artifact_time'],boundary['checked_at_utc'])
    check('boundary_added_count',boundary['added_covered_original_points'],
          sum(int(r['newly_covered_count']) for r in pp))
    check('boundary_worst_error',boundary['witness']['maximum_new_raw_to_final_error_work_m'],
          expected_extrema['largest_new_coverage_error'][0])
    check('boundary_no_method_change',boundary['methods_or_parameters_changed'],False)
    check('A_first15_still_no_final_feedback',all('g3-final-confirm' not in json.dumps(c['Referenced_materials_and_experiments'])
          and 'release_decision' not in json.dumps(c['Referenced_materials_and_experiments']) for c in interactions['candidates'][:15]))

    # Detect concurrent source mutation, rather than attaching the audit to new bytes.
    for path, digest in list(sources.items()):
        check('stable_during_review:'+path,sha(ROOT/path),digest)
    errors = [r for r in checks if not r['passed']]
    receipt = {'role_context':'/root/c_documents','status':'VERIFIED_DATA_ONLY' if not errors else 'FAILED',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'targets':[{'path':p,'sha256':h} for p,h in sources.items() if p.startswith('task1/figures/goal3/')
                   or p in ('task1/goal3/figures.py','task1/evidence/goal3/interaction_candidates.json')],
        'source_hashes':sources,'checks':len(checks),'errors':errors,
        'checked_components':['7 actual SVG/PDF/PNG/export and200dpi-render hashes andsize metadata',
            'Complete scope CSV reaggregation of displayed development/selection/confirmation/production values',
            'Every plotted600confirmation geometry/feasibility/gain value andstratum denominator',
            'All6selection strategy-record failures on fixed R0-covered identity set',
            'Production extrema fromall11386CSV rows; 3exactexample traces frombound gzipshards',
            'Actualrawneighbor breaks and allplotted finalsegments do notbridge; complete104..107window and105fate',
            'Editable drawio nodes/edges/labels match plotted graph; five actualdecision events exactbound source',
            'Root-added19thhandoff facts/nohuman judgment/noLOCK andactualboundaryC receipt'],
        'unchecked_components':['Presentation repair issues andfinalvisual closure are separate receipts',
            'Final report fullpage visual/text acceptance, executedNotebooks, actualZIPfullrecompute',
            'C raw mathematical audit consumed as boundindependent evidence; noallrecordprocessing repeated here',
            'True source datum/noise accuracy, private A context, external Evidence MasterLOCK'],
        'trajectory_processing_evaluations':0,'new_model_calls':0,'parent_task_closed':False,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_documents/review_figure_data.py',
        'checker_sha256':sha(Path(__file__))}
    path = HERE/'figure_data_receipt.json'
    path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'checks':len(checks),'errors':errors,'receipt_sha256':sha(path)},ensure_ascii=False))


if __name__=='__main__':
    main()
