"""Independent C final figure data, rendering and bounded repair review.

All figures have been actually viewed as native PNG and 200-dpi PDF renders by
C. The source plotting function is used only in a read-only, capture-only writer
for axes/legend/label inspection. Numeric expectations below are independently
rebuilt from previously raw-verified immutable experiment artifacts.
"""
import ast
from collections import Counter, defaultdict
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import runpy
import statistics
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import Audit, read_compressed
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS
from PIL import Image

OUT = Path(__file__).parent
EV = ROOT / 'task1/evidence/goal2'
FIG = ROOT / 'task1/figures/goal2'
PRE = EV / 'presentation_checks/formal_mode_layout'
MODES = ('llm-only', 'search-only', 'llm+search', 'llm+memory+search')
MODE_NAMES = ('four_mode_paired_results','four_mode_failures_and_cost','memory_coverage_and_consumption')
OBSERVATIONS = {
 'segmentation_filter_response': 'Four OAT panels show distinct point and record denominators with reference verticals; minimum length zero gives zero no-output records. Labels/legend legible; no clipping.',
 'segmentation_filter_grids': 'Four 5-by-5 native heat maps use a common 0-1 fraction scale; all cell labels legible, including length-zero row; no diagonal interpolation artifact in PDF.',
 'direction_threshold_and_neighborhood': 'Deleted/protected counts and the actual record10000/index4 neighborhood are distinct. Input/output adjacency and deletion marker clear with equal working-metre geometry.',
 'dp_error_compression': 'DP input denominator and immediate error explicit; tolerance0 shows zero saving, other tolerance labels and fixed5m vertical budget readable. No truth-quality claim.',
 'order_protection_and_neighborhoods': 'All six orders and zero/count annotations present; accepted/rejected colors include a legend; coverage and raw-break/window counts not conflated.',
 'four_mode_paired_results': 'Current labels show available/total records and record-episode pairs. Circles and outlined record-mean diamonds explained below panels. Available error57/72 differs explicitly from coverage/count72/72.',
 'four_mode_failures_and_cost': 'Actual call/evaluation/time panels legible. Zero-failure panel now has 0..1 integer count scale and twelve visible zeros, avoiding negative count implication.',
 'memory_coverage_and_consumption': 'Delivered/cited/matching-action observations separate; record-episode denominator72 and stratum denominators shown. New figure-level legend sits below bars without obscuring first stratum.',
 'real_trajectory_cases': 'Six fixed-rule G2_EVAL cases show actual point counts and Reference or changed distance95/direction15. Two no-output cases explicit. Index2 near5m residual annotation, six common reference settings and work-plane caveat readable.',
 'synthetic_metric_counterexamples': 'Both authored examples labelled synthetic. Original hidden break and own-clean0 versus common raw0.447m distinguish definitions. Index leaders separate coincident labels.',
 'goal2_actual_architecture': 'Actual governance and evaluated runtime layers separated. User/webGPT, A/root/B/C, repair/resume, bounded tools, frozen memory and final-lock feedback boundary shown; no invented fourth LLM.'
}

def bound(p):
 return {'path': str(p.relative_to(ROOT)), 'sha256': digest(p)}

def main():
 start = time.perf_counter(); a = Audit()
 state = read_json(EV/'goal_state.json')
 issue = state['issues']['G2-B-MODE-FIGURE-001']
 submitted = read_json(EV/'final_figure_review_targets.json')['targets']
 for t in issue['repair_evidence'] + submitted:
  a.check('exact_target_binding', digest(ROOT/t['path']) == t['sha256'])
 source = ROOT/'task1/scripts/build_goal2_figures.py'
 trees = [ast.parse(p.read_text()) for p in (PRE/'build_goal2_figures.before.py',source)]
 defs = [{n.name:ast.dump(n) for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))} for t in trees]
 a.same('only_mode_figure_function_changed', sorted(k for k in defs[0].keys()|defs[1].keys() if defs[0].get(k)!=defs[1].get(k)), ['mode_figures'])
 for name in ('figure_data.json','CASE_SELECTION.json'):
  a.check('display_repair_bytes_unchanged', (FIG/name).read_bytes()==(PRE/'before'/name).read_bytes())
 manifest = read_json(FIG/'figure_manifest.json'); data = read_json(FIG/'figure_data.json')
 a.same('all11_required_figures', sorted(data), sorted(OBSERVATIONS))
 a.same('manifest_all11', sorted(f['name'] for f in manifest['figures']), sorted(data))
 a.check('generator_hash', manifest['generator_sha256']==digest(source))
 a.check('data_hash', manifest['figure_data_sha256']==digest(FIG/'figure_data.json'))
 a.check('P2_palette_hash', manifest['palette_sha256']==digest(ROOT/manifest['palette_source']))
 for path,sha in manifest['source_files'].items(): a.check('trusted_input_hash', digest(ROOT/path)==sha)
 a.check('whole_source_binding_hash', object_hash(manifest['source_files'])==manifest['source_binding_hash'])
 freeze = read_json(EV/'evaluation_freeze.json')
 for path,sha in freeze['processing_source_hashes'].items(): a.check('processing_epoch_unchanged', digest(ROOT/path)==sha)
 current = read_json(EV/'current_runs.json'); reference=read_json(ROOT/'task1/config/goal2/contract.json')['reference_parameters']
 def run(key):
  d=EV/'runs'/current[key]; m=read_json(d/'manifest.json')
  a.check('completed_valid_run', m['status'] not in ('RUNNING','FAILED','STALE','SUPERSEDED'))
  return d,m
 directory,pm=run('parameter_development'); params=read_json(directory/'parameter_table.json')
 def oat(k): return sorted([e for e in params if all(e['parameters'][o]==v for o,v in reference.items() if o!=k)],key=lambda e:e['parameters'][k])
 for key,rows in data['segmentation_filter_response'].items():
  expected=[{'value':e['parameters'][key],'config_id':e['config_id'],'retained_fraction':e['summary']['n_final']/e['summary']['n_input'],
     'no_output_record_fraction':e['summary']['n_no_output_records']/e['summary']['n_records'],'raw_points':e['summary']['n_input'],'records':e['summary']['n_records']} for e in oat(key)]
  a.same('OAT_data:'+key,rows,expected)
 for grid in data['segmentation_filter_grids']:
  rows=[e for e in params if all(e['parameters'][o]==v for o,v in reference.items() if o not in (grid['x'],grid['y']))]
  a.same('grid_domain',grid['config_ids'],[e['config_id'] for e in rows])
  values=[]
  for y in grid['y_values']:
   line=[]
   for x in grid['x_values']:
    e=next(e for e in rows if e['parameters'][grid['x']]==x and e['parameters'][grid['y']]==y)
    s=e['summary']; line.append(s['n_final']/s['n_input'] if grid['metric']=='point_retention' else s['n_no_output_records']/s['n_records'])
   values.append(line)
  a.same('grid_actual_fraction',grid['matrix'],values)
 a.same('direction_registered_data',data['direction_threshold_and_neighborhood']['rows'],oat('direction'))
 a.same('DP_registered_data',data['dp_error_compression'],oat('dp'))
 baseline=next(e for e in params if e['parameters']==reference)
 trace=read_compressed(directory/baseline['file'])
 deleted=sorted((r['record_id'],i) for r in trace['records'] for s in r['stages'] if s['name']=='D' for op in s['operations'] for i in op['deleted_indices'])
 selection=read_json(FIG/'DIRECTION_CASE_SELECTION.json')
 a.same('direction_case_selected_before_plot',selection,data['direction_threshold_and_neighborhood']['case_selection'])
 a.same('direction_case_actual_rule',selection['selected'],{'record_id':deleted[0][0],'index':deleted[0][1]})
 directory,om=run('order_development')
 a.same('six_order_figure_all_data',data['order_protection_and_neighborhoods'],read_json(directory/'order_table.json'))
 directory,mm=run('mode_evaluation'); episodes=[]
 for entry in mm['mode_episodes']:
  path=directory/entry['path'];a.check('mode_episode_binding',digest(path)==entry['sha256']);episodes.append(read_json(path))
 records=[r for ep in episodes for r in ep['records']]
 expected_pairs=[]
 for metric in ('common_coverage','common_max_error','n_final'):
  for mode in MODES:
   for r in records:
    if r['mode']!=mode:continue
    if metric=='common_max_error': cv=r['research_assessment']['candidate_max_on_baseline_covered'];rv=r['research_assessment']['baseline_common_max']
    else:cv=r['selected_metrics'][metric];rv=r['reference_metrics'][metric]
    if cv is not None and rv is not None:expected_pairs.append({'metric':metric,'mode':mode,'record_id':r['record_id'],'episode':r['episode'],'delta':cv-rv})
 a.same('804_actual_paired_points',data['four_mode_paired_results'],expected_pairs)
 costs={}
 for mode in MODES:
  eps=[e for e in episodes if e['mode']==mode];rs=[r for r in records if r['mode']==mode];ps=[p for r in rs for p in r['proposal_records']]
  costs[mode]={'model_dispatches':sum(e['resources']['experiment_model_dispatches'] for e in eps),'candidate_evaluations':sum(e['resources']['candidate_evaluations'] for e in eps),
   'elapsed_seconds':sum(e['elapsed_seconds'] for e in eps),'raw_proposal_slots':len(ps),'illegal_proposals':sum(not p['legal'] for p in ps),'executed_proposals':sum(p['executed'] for p in ps),
   'fallback_records':sum(r['fallback'] for r in rs),'selected_break_violations':sum(r['selected_metrics']['raw_break_crossings']>0 for r in rs),'record_episodes':len(rs)}
 a.same('actual_cost_and_failure_counts',data['four_mode_failures_and_cost'],costs)
 counts=Counter();strata=defaultdict(Counter);memory_rows=[r for r in records if r['mode']=='llm+memory+search']
 for r in memory_rows:
  cs=[rnd['memory_consumption'] for rnd in r['rounds'] if 'memory_consumption' in rnd]
  flags={'Eligible':any(c['retrieved_eligible']>0 for c in cs),'Delivered':any(c['delivered_ids'] for c in cs),'Model cited':any(c['model_cited_valid'] for c in cs),'Action consistent':any(c['action_consistent'] for c in cs)}
  for k,v in flags.items():counts[k]+=v;strata[r['stratum']][k]+=v
  strata[r['stratum']]['denominator']+=1
 a.same('record_episode_memory_observations',data['memory_coverage_and_consumption'],{'counts':dict(counts),'denominator':len(memory_rows),'by_stratum':{k:dict(v) for k,v in strata.items()}})
 # Independently apply fixed case selection to all 14 held-out configurations.
 directory,em=run('evaluation_parameters');candidates={e['config_id']:read_compressed(directory/e['file'])['records'] for e in em['artifacts'].values()}
 baseline={r['record_id']:r for r in candidates['cfg-b15b8281b73592fb']};cards=read_json(EV/'data/raw_diagnostics.json')
 selection=read_json(FIG/'CASE_SELECTION.json');a.same('case_scope',selection['scope'],em['input_ids']);a.same('case_render_binding',selection['cases'],data['real_trajectory_cases'])
 for case in selection['cases']:
  rid,cid=case['record_id'],case['config_id']
  if case['role'].startswith('Representative '):
   group=[i for i in baseline if cards[i]['stratum'].startswith(case['role'].split()[-1]+'_')];mid=statistics.median(cards[i]['span_work_m'] for i in group)
   a.check('representative_raw_span_rule',rid==min(group,key=lambda i:(abs(cards[i]['span_work_m']-mid),i)) and cid=='cfg-b15b8281b73592fb')
  elif case['role']=='Largest covered-point loss':
   ranked=sorted((-(baseline[r['record_id']]['metrics']['common_covered_points']-r['metrics']['common_covered_points']),r['record_id'],c) for c,rs in candidates.items() for r in rs)
   a.check('worst_coverage_fixed_rule',(-case['criterion_value'],rid,cid)==ranked[0])
  elif case['role']=='Largest available raw error':
   ranked=sorted((-r['metrics']['common_max_error'],r['record_id'],c) for c,rs in candidates.items() for r in rs if r['metrics']['common_max_error'] is not None)
   a.check('worst_available_geometry_rule',(-case['criterion_value'],rid,cid)==ranked[0])
  else:
   ranked=sorted((abs(r['parameters']['dp']-p['error']),r['record_id'],c,p['index']) for c,rs in candidates.items() for r in rs for s in r['stages'] if s['name']=='P' for op in s['operations'] for p in op['runtime_dp_check']['error_by_original_index'] if p['error']>0 and abs(r['parameters']['dp']-p['error'])>0)
   a.check('nearest_DP_fixed_rule',(case['criterion_value'],rid,cid,case['original_index'])==ranked[0])
 suite=read_json(ROOT/current['counterexamples']/'synthetic_cases.json')
 for e in data['synthetic_metric_counterexamples']:
  case=next(c for c in suite['cases'] if c['case_id']==e['case_id']);a.same('actual_synthetic_metrics',e['metrics'],case['executions'][e['execution']]['output']['metrics']);a.check('synthetic_classification',e['classification']=='SYNTHETIC_COUNTEREXAMPLE')
 graph=data['goal2_actual_architecture'];cells=ET.parse(FIG/graph['drawio_file']).findall('.//mxCell');vertices={c.get('id'):c for c in cells if c.get('vertex')=='1'};edges=[c for c in cells if c.get('edge')=='1']
 a.check('native_editable_topology',len(vertices)==11 and len(edges)==13 and len({c.get('id') for c in cells})==len(cells))
 a.check('native_graph_hash',digest(FIG/graph['drawio_file'])==graph['drawio_sha256'])
 for ident,label,x,y,w,h,color,module in graph['nodes']:
  v=vertices[ident];g=v.find('mxGeometry');a.check('editable_vertex_geometry',v.get('value')==label and 'image=' not in v.get('style','') and [float(g.get(k)) for k in ('x','y','width','height')]==[x*100,(9-y-h)*100,w*100,h*100])
  if module:a.check('actual_node_module', (ROOT/module).is_file())
 for e,(s,t,label,dashed) in zip(edges,graph['edges']):a.check('editable_edge', [e.get(k) for k in ('source','target','value')]==[s,t,label] and ('dashed=1' in e.get('style',''))==dashed)
 a.check('C_independent_module',next(n[-1] for n in graph['nodes'] if n[0]=='C')=='task1/evidence/goal2/c_contract/independent_numeric.py')
 # Re-render each PDF with an independent invocation, and verify all four export bindings.
 render_dir=OUT/'final_figure_pdf_renders';render_dir.mkdir(exist_ok=True);render_targets=[]
 for figure in manifest['figures']:
  for info in [*figure['formats'].values(),figure['pdf_render']]:a.check('export_hash',digest(FIG/info['file'])==info['sha256'])
  a.check('three_editable_and_raster_formats',set(figure['formats'])=={'svg','pdf','png'})
  with Image.open(FIG/figure['formats']['png']['file']) as im:
   a.same('PNG_pixel_size',list(im.size),figure['png_size_pixels']);a.check('PNG_300dpi',all(abs(v-300)<.1 for v in im.info['dpi']))
  svg=ET.parse(FIG/figure['formats']['svg']['file']);a.check('SVG_text_editable',len(svg.findall('.//{http://www.w3.org/2000/svg}text'))>5)
  prefix=render_dir/figure['name'];subprocess.run(['pdftoppm','-r','200','-singlefile','-png',str(FIG/figure['formats']['pdf']['file']),str(prefix)],capture_output=True,check=True)
  p=prefix.with_suffix('.png');a.check('independent_200dpi_PDF_render',digest(p)==figure['pdf_render']['sha256']);render_targets.append(bound(p))
  if figure['name'] not in MODE_NAMES:
   for info in (figure['formats']['png'],figure['pdf_render']):a.check('eight_unaffected_figures_byte_identical',digest(FIG/info['file'])==digest(PRE/'before'/info['file']))
 # Capture exact old/new plotting objects. No formal output is rewritten.
 namespaces=[runpy.run_path(str(p),run_name='C_READ_ONLY_PLOT_INSPECTION') for p in (PRE/'build_goal2_figures.before.py',source)]
 props=[]
 for ns in namespaces:
  class Capture:
   def __init__(self):self.p=ns['theme']();self.saved={}
   def run(self,key):return run(key)
   def source(self,p):return p
   def save(self,fig,name,data,description):self.saved[name]=(fig,data,description)
  w=Capture();ns['mode_figures'](w)
  paired=w.saved[MODE_NAMES[0]][0];cost=w.saved[MODE_NAMES[1]][0];memory=w.saved[MODE_NAMES[2]][0]
  for fig in (paired,cost,memory):fig.canvas.draw()
  count_axis=cost.axes[3];labels=[t.get_text() for t in paired.texts]+[t.get_text() for ax in paired.axes for t in ax.texts]
  legend=memory.legends[0] if memory.legends else memory.axes[1].get_legend();renderer=memory.canvas.get_renderer();lb=legend.get_window_extent(renderer)
  overlap=any(lb.overlaps(p.get_window_extent(renderer)) for ax in memory.axes for p in ax.patches)
  prop={'count_lower_bound':float(count_axis.get_ylim()[0]),'count_upper_bound':float(count_axis.get_ylim()[1]),'count_ticks':[float(v) for v in count_axis.get_yticks()],
   'count_zero_annotations':sum(t.get_text()=='0' for t in count_axis.texts),'paired_correct_units':any('record-episode pairs' in t for t in labels) and not any(t.endswith('episodes') and t.startswith(('72 ','57 ')) for t in labels),
   'paired_available_pair_labels':sum('/72 pairs' in t for t in labels),'paired_marker_explanation':any('Outlined diamonds' in t and 'per-record means' in t for t in labels),
   'memory_legend_overlaps_bars':overlap,'figure_level_memory_legend':len(memory.legends)==1}
  props.append(prop)
  for fig,_,_ in w.saved.values():ns['plt'].close(fig)
 def valid(p):return p['count_lower_bound']==0 and p['count_upper_bound']>=1 and p['count_zero_annotations']==12 and all(v.is_integer() for v in p['count_ticks']) and p['paired_correct_units'] and p['paired_available_pair_labels']==12 and p['paired_marker_explanation'] and not p['memory_legend_overlaps_bars'] and p['figure_level_memory_legend']
 a.check('fault_rejected_actual_old_plot',not valid(props[0]));a.check('valid_receipt_accepted_actual_new_plot',valid(props[1]))
 a.check('old_faults_observed',props[0]['count_lower_bound']<0 and props[0]['count_zero_annotations']==0 and props[0]['memory_legend_overlaps_bars'] and not props[0]['paired_marker_explanation'])
 # Metadata is inspected against actual current export/processing/source bytes; no B visual pass is substituted for C observations.
 execution=read_json(PRE/'rebuild_execution.json');a.check('actual_rebuild_exit',execution['exit_code']==0)
 execution_text=json.dumps(execution);a.check('correct_generator_command','build_goal2_figures' in execution_text and 'all' in execution_text)
 status='VERIFIED' if not a.errors else 'REJECTED'
 observed=[{'name':f['name'],'native_png':bound(FIG/f['formats']['png']['file']),'pdf_raster_200dpi':bound(FIG/f['pdf_render']['file']),'observation':OBSERVATIONS[f['name']]} for f in manifest['figures']]
 evidence={'at':now(),'status':status,'role_context':'/root/c_contract','check_count':a.check_count,'errors':a.errors,'numeric_data_reconstructed':list(data),'actual_viewed_images':observed,'audit_program':bound(Path(__file__)),
  'independent_PDF_renders':render_targets,'old_new_plot_properties':props,'elapsed_seconds':time.perf_counter()-start,'new_model_calls':0,'new_candidate_evaluations':0,
  'scope_limit':'All figure data/bindings/renderings checked. Underlying processing verification is separately bound to prior C receipts. Native draw.io XML editability checked; no diagrams.net GUI import is claimed. This is not complete Goal2 or remote publication acceptance.'}
 write_json(OUT/'final_figure_independent_checks.json',evidence,exclusive=True)
 closure={**evidence,'issue_id':'G2-B-MODE-FIGURE-001','parent_task':'figures','targets':deepcopy(issue['repair_evidence']),'source_hashes':deepcopy(issue['repair_source_hashes']),
  'checked_components':['fault_rejected','valid_receipt_accepted','source_epoch','actual_PNG_and_PDF_view','record_episode_units','integer_zero_count_axis','unobscured_legend','unchanged_numeric_data'],
  'unchecked_components':['full_Goal2_acceptance','remote_publication']}
 write_json(OUT/'mode_figure_closure_receipt.json',closure,exclusive=True)
 receipt={**evidence,'task_id':'figures','targets':submitted,'source_hashes':{p:digest(ROOT/p) for p in task_sources('figures')},'checked_components':REQUIRED_COMPONENTS['figures'],
  'unchecked_components':['full_Goal2_acceptance','remote_publication'],'repair_closure':bound(OUT/'mode_figure_closure_receipt.json'),
  'trusted_processing_reviews':[bound(OUT/n) for n in ('development_parameters_epoch02_receipt.json','development_orders_epoch02_receipt.json','evaluation_modes_complete_receipt.json','counterexamples_complete_receipt.json','analysis_complete_receipt_v2.json') if (OUT/n).exists()]}
 write_json(OUT/'figures_complete_receipt.json',receipt,exclusive=True)
 print(json.dumps({k:evidence[k] for k in ('status','check_count','errors','elapsed_seconds')},ensure_ascii=False))

if __name__=='__main__':main()
