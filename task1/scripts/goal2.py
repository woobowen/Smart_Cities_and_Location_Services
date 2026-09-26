"""Goal 2 explicit production, LIVE, and default no-model recomputation entrypoints."""
import argparse
import json
from pathlib import Path
import time
from task1.workflow.io import ROOT,read_json,write_json,digest,object_hash,now
from task1.workflow.g2_experiments import (EV,CFG,ExperimentRun,parameter_development,order_development,
    candidate_lock,read_gzip,write_gzip,compact_metrics)
from task1.workflow.g2_selection import (REFERENCE,config_id,search_sequence,select_record,compare,
                                       legal_parameters,execution_parameters)
from task1.workflow.g2_memory import build_snapshot,FrozenMemory
from task1.workflow.g2_modes import MODES,run_batch_episode,validate_response,PROMPT_TEMPLATE
from task1.workflow.g2_pipeline import run_batch,run_record
from task1.workflow.g2_metrics import review_batch,review_record
from task1.workflow.g2_journal import source_snapshot


def cards():return read_json(EV/'data/raw_diagnostics.json')


def update_current(key,value):
    path=EV/'current_runs.json';current=read_json(path) if path.exists() else {}
    current[key]=value;write_json(path,current)


def build_memory(run):
    results={};audits={};entries=[];sequence=search_sequence()
    for parameters in sequence:
        result,entry=run.evaluate_batch(parameters,experiment_ids=['G2-DEMO-MEMORY-SEARCH'])
        cid=config_id(parameters);results[cid]={r['record_id']:r for r in result['records']}
        audit=read_json(run.directory/entry['review_file'])
        audits[cid]={rid:r for rid,r in zip(run.ids,audit['record_receipts'])}
    for rid in run.ids:
        candidate_records={cid:v[rid] for cid,v in results.items()}
        selected,selection=select_record(candidate_records,config_id(REFERENCE))
        result=candidate_records[selected];audit=audits[selected][rid]
        trace_path=run.directory/'admission'/f'{rid}_selected.json.gz'
        review_path=run.directory/'admission'/f'{rid}_review.json'
        write_gzip(trace_path,result);write_json(review_path,audit,exclusive=True)
        entry={'record_id':rid,'engineering_status':audit['status'],'selected_config_id':selected,
            'selected_parameters':result['parameters'],'selected_metrics':compact_metrics(result['metrics']),
            'research_status':compare(result,candidate_records[config_id(REFERENCE)])['status'],
            'selection_reason':selection['reason'],'candidate_evaluations':20,
            'trace_path':str(trace_path.relative_to(ROOT)),'trace_sha256':digest(trace_path),
            'review_path':str(review_path.relative_to(ROOT)),'review_sha256':digest(review_path),
            'trusted_provenance':run.provenance(run.ids)}
        entries.append(entry)
    snapshot=run.directory/'memory_snapshot.json'
    build_snapshot(snapshot,entries,run.split,cards(),run.contract_hash)
    run.manifest['memory_snapshot']={'path':str(snapshot.relative_to(run.directory)),'sha256':digest(snapshot)}
    run.finish();return snapshot


def run_modes(run,episodes,*,enable_live=False):
    if not enable_live:raise ValueError('REAL_MODEL_EXPERIMENT_REQUIRES_EXPLICIT_ENABLE_LIVE')
    index=read_json(EV/'current_runs.json');memory_run=EV/'runs'/index['memory']
    manifest=read_json(memory_run/'manifest.json');info=manifest['memory_snapshot']
    memory=FrozenMemory(memory_run/info['path'],info['sha256'],run.contract_hash,run.split)
    ids=run.split['llm_subsets'][run.partition];observed=cards()
    for mode in MODES:
        for episode in range(1,episodes+1):
            for offset in range(0,len(ids),8):
                result=run_batch_episode(run,mode,episode,ids[offset:offset+8],observed,
                    memory=memory if mode=='llm+memory+search' else None)
                print(json.dumps({'episode':result['episode_id'],'model_dispatches':result['resources']['experiment_model_dispatches'],
                    'candidate_evaluations':result['resources']['candidate_evaluations'],'seconds':round(result['elapsed_seconds'],2)}),flush=True)
    run.finish()


def freeze_evaluation():
    index=read_json(EV/'current_runs.json');required=('parameter_development','order_development','memory','mode_development')
    manifests={key:read_json(EV/'runs'/index[key]/'manifest.json') for key in required}
    if any(m['status']!='REVIEW_PENDING' for m in manifests.values()):raise ValueError('DEVELOPMENT_NOT_COMPLETE')
    modes=manifests['mode_development']['mode_episodes']
    if len(modes)!=12 or any(len([r for r in modes if r['mode']==m])!=3 for m in MODES):raise ValueError('DEVELOPMENT_MODE_SCOPE_INCOMPLETE')
    expected_ids=read_json(EV/'data/split_manifest.json')['llm_subsets']['DEVELOPMENT']
    for mode in MODES:
        refs=[r for r in modes if r['mode']==mode]
        if [rid for r in refs for rid in r['input_ids']]!=expected_ids or any(r['episode']!=1 for r in refs):raise ValueError('DEVELOPMENT_MODE_EXACT_SCOPE_MISMATCH')
        for ref in refs:
            path=EV/'runs'/index['mode_development']/ref['path']
            if digest(path)!=ref['sha256']:raise ValueError('DEVELOPMENT_MODE_EVIDENCE_CHANGED')
            episode=read_json(path)
            expected_class='DETERMINISTIC_ZERO_MODEL_SEARCH' if mode=='search-only' else 'LIVE_EXPERIMENT'
            if episode['classification']!=expected_class:raise ValueError('DEVELOPMENT_MODE_NOT_REAL')
    lock=read_json(EV/'candidate_lock.json')
    memory_info=manifests['memory']['memory_snapshot'];memory_path=EV/'runs'/index['memory']/memory_info['path']
    receipt={'goal_id':'SC-LAB1-G2-EXPERIMENTS-001','status':'LOCKED_BEFORE_G2_EVAL','frozen_at':now(),
        'authority':'predeclared USER_PROMPT rules, not new Human Approval',
        'contract_sha256':digest(CFG/'contract.json'),'split_sha256':digest(EV/'data/split_manifest.json'),
        'candidate_lock_sha256':digest(EV/'candidate_lock.json'),
        'selected_single_candidates':lock['selected_single_candidates'],'orders':lock['feasible_orders'],
        'representative_config_ids':lock['eval_representatives'],'memory_sha256':digest(memory_path),
        'memory_path':str(memory_path.relative_to(ROOT)),'prompt_template_sha256':object_hash(PROMPT_TEMPLATE),
        'mode_implementation_sha256':digest(ROOT/'task1/workflow/g2_modes.py'),
        'provider_implementation_sha256':digest(ROOT/'task1/workflow/g2_provider.py'),
        'processing_source_hashes':source_snapshot(),
        'development_manifest_hashes':{k:digest(EV/'runs'/index[k]/'manifest.json') for k in required},
        'eval_ids':read_json(EV/'data/split_manifest.json')['splits']['G2_EVAL'],
        'eval_llm_ids':read_json(EV/'data/split_manifest.json')['llm_subsets']['G2_EVAL'],
        'evaluation_episodes':3,'evaluation_previously_observed':False}
    write_json(EV/'evaluation_freeze.json',receipt,exclusive=True);return receipt


def evaluation_parameters(run):
    freeze=read_json(EV/'evaluation_freeze.json');matrix=read_json(CFG/'experiment_matrix.json')
    configurations={r['config_id']:r['parameters'] for r in matrix['parameter_configurations']}
    requested=set(freeze['representative_config_ids'])|{r['config_id'] for r in freeze['selected_single_candidates'].values()}
    rows=[]
    for cid in sorted(requested):
        result,entry=run.evaluate_batch(configurations[cid],experiment_ids=['G2-EVAL-REPRESENTATIVES-AND-SINGLE-CANDIDATES'])
        rows.append(entry);print(json.dumps({'evaluation_config':cid,'records':len(result['records'])}),flush=True)
    write_json(run.directory/'evaluation_table.json',rows)
    run.manifest.setdefault('tables',{})['evaluation_table.json']=digest(run.directory/'evaluation_table.json');run.finish()


def evaluation_orders(run):
    freeze=read_json(EV/'evaluation_freeze.json');entries=[]
    for order in freeze['orders']:
        result,entry=run.evaluate_batch(REFERENCE,order,experiment_ids=['G2-EVAL-FROZEN-FEASIBLE-ORDERS'])
        entries.append(entry)
    write_json(run.directory/'order_table.json',entries)
    run.manifest.setdefault('tables',{})['order_table.json']=digest(run.directory/'order_table.json');run.finish()


def recompute_saved_run(run_id,output_directory):
    directory=EV/'runs'/run_id;manifest=read_json(directory/'manifest.json')
    run=ExperimentRun(run_id,manifest['partition'],resume=True);checks=[]
    for key,entry in manifest['artifacts'].items():
        path=directory/entry['file']
        if digest(path)!=entry['sha256']:raise ValueError('ARCHIVED_RESULT_HASH_MISMATCH')
        old=read_gzip(path);ids=entry['input_ids'];trusted=[run.records[rid] for rid in ids]
        result=run_batch(trusted,entry['parameters'],entry['order'],contract_hash=run.contract_hash,provenance=run.provenance(ids))
        audit=review_batch(result,trusted,expected_parameters=entry['parameters'],expected_order=entry['order'],
                           contract_hash=run.contract_hash,trusted_provenance=run.provenance(ids))
        match=object_hash(old)==object_hash(result)
        checks.append({'experiment_key':key,'record_scope':ids,'exact_output_match':match,'review_status':audit['status']})
        if not match or audit['status']!='VERIFIED':raise ValueError('RAW_RECOMPUTE_MISMATCH:'+key)
    result={'status':'VERIFIED','mode':'RECOMPUTE','new_model_calls':0,'run_id':run_id,'checks':checks,
            'candidate_record_recomputations':sum(len(c['record_scope']) for c in checks),'at':now()}
    write_json(output_directory/(run_id+'_recompute.json'),result)
    return result


def recompute_saved_modes(run_id,output_directory):
    directory=EV/'runs'/run_id;manifest=read_json(directory/'manifest.json')
    run=ExperimentRun(run_id,manifest['partition'],resume=True);checks=[]
    for ep_ref in manifest['mode_episodes']:
        path=directory/ep_ref['path']
        if digest(path)!=ep_ref['sha256']:raise ValueError('EPISODE_HASH_MISMATCH')
        episode=read_json(path);parent=path.parent
        for file,h in episode['artifact_hashes'].items():
            if digest(parent/file)!=h:raise ValueError('EPISODE_CHILD_HASH_MISMATCH')
        for row in episode['records']:
            rid=row['record_id'];saved=read_gzip(parent/f'{rid}_candidate_traces.json.gz');rebuilt={}
            schedule={config_id(REFERENCE):REFERENCE.copy()}
            if row['mode']=='search-only':schedule={config_id(p):p for p in search_sequence()}
            else:
                for rd in row['rounds']:
                    action=rd.get('raw_action')
                    if action is None:continue
                    for proposal in action['proposals']:
                        ok,_=legal_parameters(proposal['parameters'])
                        if ok:
                            params=execution_parameters(proposal['parameters']);schedule[config_id(params)]=params
                    if row['mode']!='llm-only' and not action['stop']:
                        target={1:8,2:14,3:20}[rd['round']]
                        for params in search_sequence():
                            if len(schedule)>=target:break
                            schedule.setdefault(config_id(params),params)
            if list(schedule)!=row['candidate_ids'] or set(schedule)!=set(saved['results']):
                raise ValueError('REPLAY_ACTION_SCHEDULE_MISMATCH')
            for cid,parameters in schedule.items():
                old=saved['results'][cid];provenance={**run.provenance([rid]),'episode_id':row['episode_id']}
                result=run_record(run.records[rid],parameters,'S-D-P',contract_hash=run.contract_hash,provenance=provenance)
                audit=review_record(result,run.records[rid],expected_parameters=parameters,expected_order='S-D-P',
                    contract_hash=run.contract_hash,trusted_provenance=provenance)
                if object_hash(result)!=object_hash(old) or audit['status']!='VERIFIED':raise ValueError('MODE_RAW_RECOMPUTE_MISMATCH')
                rebuilt[cid]=result
            if row['mode']=='llm-only':
                legal=[p['executed_config_id'] for p in row['proposal_records'] if p.get('executed')]
                selected=legal[0] if legal and not rebuilt[legal[0]]['metrics']['raw_break_crossings'] else config_id(REFERENCE)
            else:selected,_=select_record(rebuilt,config_id(REFERENCE))
            if selected!=row['selected_config_id']:raise ValueError('REPLAY_SELECTION_MISMATCH')
            checks.append({'episode_id':row['episode_id'],'record_id':rid,'candidates_recomputed':len(schedule),
                           'raw_execution_match':True,'selection_match':True})
    result={'status':'VERIFIED','mode':'REPLAY_RECOMPUTE','new_model_calls':0,'run_id':run_id,'checks':checks,
            'candidate_record_recomputations':sum(c['candidates_recomputed'] for c in checks),'at':now()}
    write_json(output_directory/(run_id+'_recompute.json'),result);return result


def recompute(topic,output_directory,rebuild_figures=True):
    output_directory=Path(output_directory);output_directory.mkdir(parents=True,exist_ok=True)
    index=read_json(EV/'current_runs.json');checks=[]
    if topic=='parameters':
        for key in ('parameter_development','order_development','evaluation_parameters','evaluation_orders'):
            checks.append(recompute_saved_run(index[key],output_directory))
    elif topic=='modes':
        checks.append(recompute_saved_run(index['memory'],output_directory))
        for key in ('mode_development','mode_evaluation'):
            checks.append(recompute_saved_modes(index[key],output_directory))
    elif topic=='candidates':
        checks.append(recompute_saved_run(index['evaluation_parameters'],output_directory))
        import subprocess
        dest=output_directory/'counterexamples'
        subprocess.run([str(ROOT/'.venv/bin/python'),'-m','task1.scripts.goal2_counterexamples','--output',str(dest),
                        '--run-id','G2-NOTEBOOK-COUNTEREXAMPLES-RECOMPUTE'],cwd=ROOT,check=True)
    else:raise ValueError('UNKNOWN_RECOMPUTE_TOPIC')
    if rebuild_figures:
        import subprocess
        subprocess.run([str(ROOT/'.venv/bin/python'),'-m','task1.scripts.build_goal2_figures',
                        '--current-runs',str(EV/'current_runs.json'),'--output',str(output_directory/'figures')],cwd=ROOT,check=True)
    summary={'status':'VERIFIED','topic':topic,'mode':'RECOMPUTE','new_model_calls':0,'checks':checks,
             'figures_rebuilt':rebuild_figures,'at':now()}
    write_json(output_directory/'recompute_summary.json',summary);return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['smoke','development-parameters','development-orders','memory','development-modes','lock-candidates','freeze-evaluation','evaluation-parameters','evaluation-orders','evaluation-modes','recompute'])
    parser.add_argument('--run-id');parser.add_argument('--enable-live',action='store_true')
    parser.add_argument('--topic',choices=['parameters','modes','candidates']);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.action=='recompute':print(json.dumps(recompute(args.topic,args.output),ensure_ascii=False));return
    if args.action=='lock-candidates':
        index=read_json(EV/'current_runs.json');candidate_lock(index['parameter_development'],index['order_development']);return
    if args.action=='freeze-evaluation':freeze_evaluation();return
    if not args.run_id:parser.error('--run-id required')
    action=args.action
    partition='DEMO_MEMORY' if action=='memory' else 'G2_EVAL' if action.startswith('evaluation') else 'DEVELOPMENT'
    run=ExperimentRun(args.run_id,partition,classification='ENGINEERING_SMOKE_TEST' if action=='smoke' else 'CURRENT_RUN_CONDITIONAL_ANALYSIS')
    if action=='smoke':
        for parameters in [REFERENCE,{**REFERENCE,'dp':2}]:
            _,entry=run.evaluate_batch(parameters,record_ids=run.ids[:3],experiment_ids=['ENGINEERING_SMOKE_COST'])
            print(json.dumps({'status':entry['engineering_status'],'records':3,'seconds':entry['elapsed_seconds']}),flush=True)
        run.finish();return
    if action=='development-parameters':parameter_development(run)
    elif action=='development-orders':order_development(run)
    elif action=='memory':build_memory(run)
    elif action in ('development-modes','evaluation-modes'):run_modes(run,3 if partition=='G2_EVAL' else 1,enable_live=args.enable_live)
    elif action=='evaluation-parameters':evaluation_parameters(run)
    elif action=='evaluation-orders':evaluation_orders(run)
    update_current(action.replace('-','_').replace('development_parameters','parameter_development').replace('development_orders','order_development').replace('development_modes','mode_development').replace('evaluation_modes','mode_evaluation'),args.run_id)


if __name__=='__main__':main()
