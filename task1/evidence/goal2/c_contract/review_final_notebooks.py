"""Independent C inspection of actual fresh-kernel notebook executions.

Does not rerun expensive full notebooks or change delivered files. Reconstructs
complete embedded recompute scopes, validates all executed source cells/logs,
checks rebuilt PNG pixels, and separately executes sentinel and held-out binding
assertions in this C process using copied, real recompute evidence.
"""
import ast
import base64
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import runpy
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from review_development_runs import Audit
from task1.workflow.io import read_json,write_json,digest,now
from task1.workflow.g2_journal import task_sources,REQUIRED_COMPONENTS
from PIL import Image
import nbformat
OUT=Path(__file__).parent;EV=ROOT/'task1/evidence/goal2';RUN=EV/'notebook_runs/fresh-01';PRE=EV/'notebook_checks/heldout_display'

def bound(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}
def joined(v):return ''.join(v) if isinstance(v,list) else v
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ('th','td'):self.cell=[]
 def handle_data(self,data):
  if self.cell is not None:self.cell.append(data)
 def handle_endtag(self,tag):
  if tag in ('th','td'):self.row.append(''.join(self.cell));self.cell=None
  if tag=='tr':self.rows.append(self.row)
 def records(self):return [dict(zip(self.rows[0],row)) for row in self.rows[1:]]
def tables(cell):
 result=[]
 for o in cell['outputs']:
  if 'text/html' in o.get('data',{}):
   p=Table();p.feed(joined(o['data']['text/html']));result.append(p.records())
 return result

def main():
 started=time.perf_counter();a=Audit();state=read_json(EV/'goal_state.json');issue=state['issues']['G2-B-NOTEBOOK-CONFIRMATION-001']
 submitted=read_json(EV/'final_notebook_review_targets.json')['targets']
 bs=read_json(RUN/'b_self_check.json');repair=read_json(PRE/'fresh_kernel_repair_receipt.json')
 for t in submitted+issue['repair_evidence']+bs['targets']+repair['targets']:a.check('actual_bound_target',digest(ROOT/t['path'])==t['sha256'])
 combined=read_json(RUN/'combined_receipt.json');launch=read_json(RUN/'launch_context.json')
 a.check('canonical_merged_receipt_bytes',digest(EV/'notebook_execution.json')==digest(RUN/'combined_receipt.json'))
 a.check('three_fresh_successful_kernels',combined['status']=='VERIFIED' and combined['executed'] and len(combined['worker_receipts'])==3 and not combined['unstarted_notebooks'])
 a.check('existing_environment_bounded_parallelism',combined['environment']=='existing .venv' and combined['effective_parallelism']==2 and combined['new_persistent_kernels']==0)
 for path,sha in launch['bindings'].items():a.check('before_after_frozen_binding',digest(ROOT/path)==sha)
 a.check('fortyfive_frozen_inputs',len(launch['bindings'])==45)
 freeze=read_json(EV/'evaluation_freeze.json');a.check('memory_snapshot_stable',digest(ROOT/freeze['memory_path'])==combined['memory_before_sha256']==combined['memory_after_sha256']==freeze['memory_sha256'])
 source=ROOT/'task1/scripts/build_goal2_notebooks.py';namespace=runpy.run_path(str(source),run_name='C_READ_ONLY_NOTEBOOK_SOURCE')
 a.check('notebook_generator_version',combined['generator_sha256']==digest(source))
 a.check('wrapper_version',combined['wrapper_sha256']==digest(EV/'notebook_checks/execute_fresh_notebooks.py'))
 specs={'01_parameters_and_orders.ipynb':('parameters_notebook',7),'02_real_modes_and_memory.ipynb':('modes_notebook',6),'03_candidates_counterexamples_and_cases.ipynb':('candidates_notebook',8)}
 expected_runs={
  '01_parameters_and_orders.ipynb':['g2-development-parameters-02','g2-development-orders-02','g2-evaluation-parameters-01','g2-evaluation-orders-01'],
  '02_real_modes_and_memory.ipynb':['g2-demo-memory-02','g2-development-modes-02','g2-evaluation-modes-01'],
  '03_candidates_counterexamples_and_cases.ipynb':['g2-evaluation-parameters-01']}
 figures={f['name']:f for f in read_json(ROOT/'task1/figures/goal2/figure_manifest.json')['figures']};notebooks={};recomputations={};counts={};checked_images=[]
 for worker in combined['worker_receipts']:
  path=ROOT/worker['notebook'];name=path.name;notebook=read_json(path);notebooks[name]=notebook;nbformat.validate(nbformat.read(path,as_version=4))
  function,n=specs[name];expected_cells=namespace[function]()
  a.same('generated_source_cells',[[c['cell_type'],joined(c['source'])] for c in notebook['cells']],[[c['cell_type'],c['source']] for c in expected_cells])
  code=[c for c in notebook['cells'] if c['cell_type']=='code']
  a.same('fresh_kernel_execution_counts',[c['execution_count'] for c in code],list(range(1,n+1)))
  for i,c in enumerate(code):
   compile(joined(c['source']),name+':'+str(i),'exec')
   a.check('no_cell_errors',all(o['output_type']!='error' for o in c['outputs']))
   a.check('no_machine_absolute_paths_in_source','/home/' not in joined(c['source']))
  a.check('actual_notebook_worker_hash',digest(path)==worker['output_notebook_sha256']==worker['execution']['sha256'])
  archived_worker=read_json(ROOT/worker['worker_receipt']);a.same('merged_worker_evidence',{k:v for k,v in worker.items() if k!='worker_receipt'},archived_worker)
  directory=Path(ROOT/worker['worker_receipt']).parent;dispatch=read_json(directory/'dispatch_receipt.json');a.check('worker_exit_zero',dispatch['exit_code']==0 and dispatch['command'][0]==str(ROOT/'.venv/bin/python'))
  logs=(directory/'execution.log').read_text().splitlines();events=[json.loads(s) for s in logs if s.startswith('{"event"')]
  a.same('actual_log_start',events[0],{'event':'NOTEBOOK_STARTED','notebook':name,'at':worker['started_at']})
  a.same('actual_log_finish',events[-1],{'event':'NOTEBOOK_FINISHED','notebook':name,'status':'VERIFIED','seconds':worker['elapsed_monotonic_seconds']})
  a.check('actual_figure_rebuild_logged',any('"figures": 11' in line for line in logs))
  a.check('memory_and_sentinel',worker['new_model_calls']==0 and worker['memory_unchanged'] and worker['memory_before_sha256']==worker['memory_after_sha256']==freeze['memory_sha256'])
  setup=next(c for c in code if 'ExperimentProvider.call = reject_model_call' in joined(c['source']));recompute_cell=next(c for c in code if 'recomputed = recompute(' in joined(c['source']))
  a.check('default_RECOMPUTE_guard',"MODE = 'RECOMPUTE'" in joined(setup['source']) and 'ENABLE_LIVE = False' in joined(setup['source']) and "assert model_sentinel['calls'] == 0" in joined(recompute_cell['source']))
  rows=tables(recompute_cell)[0];a.same('exact_recomputed_run_scope',[r['run_id'] for r in rows],expected_runs[name]);total=0;recomputations[name]=[]
  for row in rows:
   # This is a literal structure generated by show(), not executable code or model output.
   checks=ast.literal_eval(row['checks']);run_id=row['run_id'];manifest=read_json(EV/'runs'/run_id/'manifest.json')
   a.check('raw_recompute_success_label',row['status']=='VERIFIED' and row['new_model_calls']=='0')
   if 'mode_episodes' in manifest:
    expected=[]
    for epref in manifest['mode_episodes']:
     ep=read_json(EV/'runs'/run_id/epref['path'])
     for r in ep['records']:expected.append({'episode_id':r['episode_id'],'record_id':r['record_id'],'candidates_recomputed':len(r['candidate_ids']),'raw_execution_match':True,'selection_match':True})
    count=sum(r['candidates_recomputed'] for r in expected)
   else:
    expected=[{'experiment_key':key,'record_scope':e['input_ids'],'exact_output_match':True,'review_status':'VERIFIED'} for key,e in manifest['artifacts'].items()];count=sum(len(r['record_scope']) for r in expected)
   a.same('every_actual_raw_recompute_scope',checks,expected);a.check('recompute_record_candidate_denominator',int(row['candidate_record_recomputations'])==count);total+=count
   recomputations[name].append({**row,'checks':checks,'candidate_record_recomputations':count,'new_model_calls':0})
  counts[name]=total
  # Images embedded by the fresh kernel are actual regenerated PNGs. Pixel
  # equivalence binds them to the independently visually reviewed formal files.
  for c in code:
   tree=ast.parse(joined(c['source']));names=[node.args[0].value for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='figure' and node.args and isinstance(node.args[0],ast.Constant)]
   images=[o['data']['image/png'] for o in c['outputs'] if 'image/png' in o.get('data',{})]
   a.check('all_requested_figures_embedded',len(names)==len(images))
   for image_name,raw in zip(names,images):
    image_bytes=base64.b64decode(joined(raw));official=ROOT/'task1/figures/goal2'/figures[image_name]['formats']['png']['file']
    with Image.open(io.BytesIO(image_bytes)) as rebuilt,Image.open(official) as expected:
     a.check('recomputed_image_pixels',rebuilt.size==expected.size and rebuilt.convert('RGB').tobytes()==expected.convert('RGB').tobytes())
    checked_images.append({'notebook':name,'figure':image_name,'embedded_sha256':hashlib.sha256(image_bytes).hexdigest(),'formal_target':bound(official)})
  if name.startswith('03'):
   text='\n'.join(joined(o['text']) for c in code for o in c['outputs'] if o['output_type']=='stream')
   a.check('actual_counterexample_reexecution',all(word in text for word in ("'synthetic_pipeline_executions': 19","'pilot_pipeline_executions': 10","'known_answer_checks': 25","'experiment_model_dispatches': 0")))
 a.same('all_raw_recomputation_counts',counts,{'01_parameters_and_orders.ipynb':9720,'02_real_modes_and_memory.ipynb':6001,'03_candidates_counterexamples_and_cases.ipynb':1680})
 a.check('total17401_recomputed_observations',sum(counts.values())==17401)
 a.check('eleven_figures_embedded',len(checked_images)==11 and {e['figure'] for e in checked_images}==set(figures))
 # Independently exercise the real SETUP sentinel in this process, restoring it afterwards.
 from task1.workflow.g2_provider import ExperimentProvider
 original=ExperimentProvider.call;env={};out=io.StringIO()
 try:
  with redirect_stdout(out):exec(compile(namespace['SETUP'],'C_setup_sentinel','exec'),env)
  try:ExperimentProvider.call(None,None);rejected=False
  except RuntimeError as err:rejected=str(err)=='RECOMPUTE_FORBIDS_NEW_MODEL_CALLS'
  a.check('actual_model_call_rejected',rejected and env['model_sentinel']['calls']==1)
 finally:
  ExperimentProvider.call=original
  if 'WORK' in env:shutil.rmtree(env['WORK'])
 # Read-only replay of actual heldout display cell; validate it rejects missing
 # raw-recompute evidence and accepts the real, complete execution evidence.
 nb=notebooks['03_candidates_counterexamples_and_cases.ipynb'];cell=next(c for c in nb['cells'] if c['cell_type']=='code' and 'heldout_rows.append' in joined(c['source']))
 confirmation=read_json(EV/'a_epoch02/heldout_single_confirmation/single_candidate_confirmation.json');review=read_json(OUT/'single_candidate_confirmation_receipt.json')
 expected=[]
 for r in confirmation['candidate_results']:
  expected.append({'candidate':r['candidate'],'config_id':r['config_id'],'protected_records':f"{r['feasible_records']}/{r['n_records']}",'strict_gain_records':f"{r['strict_gain_records']}/{r['n_records']}",
   'covered_raw_points':f"{r['common_covered_points']}/{r['common_raw_points']}",'retained_raw_points':f"{r['n_final']}/{r['n_input']}",'no_output_records':f"{r['n_no_output_records']}/{r['n_records']}",'research_status':r['evaluation_status'],'quality_accepted':str(r['quality_accepted'])})
 a.same('actual_heldout_HTML_table',tables(cell)[0],expected);a.same('B_heldout_receipt_readback',repair['displayed_results'],expected)
 display_env={'ROOT':ROOT,'EV':EV,'read_json':read_json,'digest':digest,'split':read_json(EV/'data/split_manifest.json'),'current':read_json(EV/'current_runs.json'),'lock':read_json(EV/'candidate_lock.json'),
  'recomputed':{'checks':deepcopy(recomputations['03_candidates_counterexamples_and_cases.ipynb'])},'show':lambda rows:None}
 with redirect_stdout(io.StringIO()):exec(compile(joined(cell['source']),'C_actual_heldout_cell','exec'),display_env)
 a.same('heldout_cell_readonly_positive',[{k:str(v) if isinstance(v,bool) else v for k,v in r.items()} for r in display_env['heldout_rows']],expected)
 fault_env=deepcopy({k:v for k,v in display_env.items() if k not in ('__builtins__','read_json','digest','show')});fault_env.update(read_json=read_json,digest=digest,show=lambda rows:None)
 fault_env['recomputed']['checks'][0]['checks']=[]
 try:
  with redirect_stdout(io.StringIO()):exec(compile(joined(cell['source']),'C_fault_missing_raw_binding','exec'),fault_env)
  rejected=False
 except AssertionError:rejected=True
 a.check('fault_rejected_missing_raw_confirmation_binding',rejected)
 old_ns=runpy.run_path(str(PRE/'build_goal2_notebooks.before.py'),run_name='C_OLD_NOTEBOOK_SOURCE')
 old_cells=old_ns['candidates_notebook']();a.check('fault_rejected_original_missing_heldout_display',not any('heldout_rows.append' in c['source'] for c in old_cells))
 olddefs,newdefs=[{n.name:ast.dump(n) for n in ast.parse(p.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))} for p in (PRE/'build_goal2_notebooks.before.py',source)]
 a.same('only_candidate_presentation_changed',sorted(k for k in olddefs if olddefs[k]!=newdefs[k]),['candidates_notebook'])
 teacher=read_json(ROOT/'task1/作业/作业/作业1轨迹数据预处理.ipynb')
 for i,word in ((4,'split_traj'),(6,'denoise_traj'),(8,'simplify_traj')):a.check('teacher_cell_mapping',word in joined(teacher['cells'][i]['source']).lower())
 for i in (12,14,16):
  a.check('teacher_optional_blank_implementation', '选做' in joined(teacher['cells'][i]['source']) and teacher['cells'][i+1]['cell_type']=='code' and not joined(teacher['cells'][i+1]['source']))
 a.check('three_work_notebook_stage_identity',all(n['metadata']['default_mode']=='RECOMPUTE' and n['metadata']['goal_id']=='SC-LAB1-G2-EXPERIMENTS-001' for n in notebooks.values()))
 receipt={'status':'VERIFIED' if not a.errors else 'REJECTED','role_context':'/root/c_contract','at':now(),'check_count':a.check_count,'errors':a.errors,'audit_program':bound(Path(__file__)),
  'executed_code_cells':21,'actual_fresh_kernels':3,'raw_record_candidate_recomputations':counts,'recomputed_images':checked_images,'new_model_calls':0,'memory_sha256':freeze['memory_sha256'],
  'actual_heldout_table':expected,'new_independent_research_experiments':0,'elapsed_seconds':time.perf_counter()-started,
  'scope_limit':'C verified actual B fresh-kernel execution artifacts, all delivered source cells, full embedded raw-recompute scopes and regenerated image pixels; separately executed the real sentinel and heldout binding tests. C did not duplicate the 17,401 full recomputations. Notebook OS/kernel timings are observed historical process metadata, not claimed independently remeasured.'}
 receipt['C_audit_program_correction']={'previous_receipt':bound(OUT/'final_notebook_independent_checks.json'),'previous_program':bound(OUT/'review_final_notebooks_before_schema_fix.py'),'fact':'C comparator does not accept tuple pairs; converted source-cell pairs to lists. Actual teacher cell8 is simplify_traj and optional code cells13/15/17 are intentionally blank, so checked exact stub names and blank assignment slots instead of requiring nonempty source. Production sources, outputs and numerical evidence unchanged.'}
 write_json(OUT/'final_notebook_independent_checks_v2.json',receipt,exclusive=True)
 closure={**receipt,'issue_id':'G2-B-NOTEBOOK-CONFIRMATION-001','parent_task':'notebooks','targets':deepcopy(issue['repair_evidence']),'source_hashes':deepcopy(issue['repair_source_hashes']),
  'checked_components':['fault_rejected','valid_receipt_accepted','source_epoch','actual_03_fresh_kernel','raw_recompute_binding','heldout_table_and_denominators','unchanged_processing'],
  'unchecked_components':['full_Goal2_acceptance','remote_publication'],'actual_new_kernel_evidence':[bound(ROOT/t['path']) for t in repair['targets']]}
 write_json(OUT/'notebook_confirmation_closure_receipt_v2.json',closure,exclusive=True)
 full={**receipt,'task_id':'notebooks','targets':submitted,'source_hashes':{p:digest(ROOT/p) for p in task_sources('notebooks')},'checked_components':REQUIRED_COMPONENTS['notebooks'],'unchecked_components':['full_Goal2_acceptance','remote_publication'],
  'repair_closure':bound(OUT/'notebook_confirmation_closure_receipt_v2.json')}
 write_json(OUT/'notebooks_complete_receipt_v2.json',full,exclusive=True)
 print(json.dumps({k:receipt[k] for k in ('status','check_count','errors','elapsed_seconds')},ensure_ascii=False))

if __name__=='__main__':main()
