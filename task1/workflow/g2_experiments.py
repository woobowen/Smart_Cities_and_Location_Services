"""Bounded deterministic experiments, compressed full traces, and raw recompute."""
import gzip
import json
import time
import subprocess
from pathlib import Path
from .io import ROOT, digest, object_hash, read_json, write_json, now, bound_path
from .g2_data import raw_data, adapt
from .g2_pipeline import run_batch, run_record
from .g2_metrics import review_batch, review_record, summarize
from .g2_journal import source_snapshot
from .g2_selection import REFERENCE, GRID, config_id, execution_parameters, compare

EV=ROOT/'task1/evidence/goal2'
CFG=ROOT/'task1/config/goal2'


def write_gzip(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError('RESULT_EXISTS_NO_OVERWRITE')
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as stream:
            stream.write(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode())


def read_gzip(path):
    with gzip.open(path,'rt',encoding='utf-8') as stream:return json.load(stream)


def compact_metrics(metrics):
    return {k:v for k,v in metrics.items() if not isinstance(v,(dict,list))}


class ExperimentRun:
    def __init__(self, run_id, partition, *, resume=False, classification='CURRENT_RUN_CONDITIONAL_ANALYSIS'):
        self.directory=EV/'runs'/run_id;self.run_id=run_id
        self.contract=read_json(CFG/'contract.json');self.contract_hash=digest(CFG/'contract.json')
        self.split=read_json(EV/'data/split_manifest.json');self.split_hash=digest(EV/'data/split_manifest.json')
        self.partition=partition;self.ids=self.split['splits'][partition]
        if partition=='G3_RESERVED':raise ValueError('G3_NOT_AUTHORIZED')
        if partition=='G2_EVAL' and not (EV/'evaluation_freeze.json').is_file():raise ValueError('EVALUATION_NOT_FROZEN')
        if partition=='G2_EVAL':
            freeze=read_json(EV/'evaluation_freeze.json')
            if freeze['status']!='LOCKED_BEFORE_G2_EVAL' or freeze['contract_sha256']!=self.contract_hash or freeze['split_sha256']!=self.split_hash:
                raise ValueError('EVALUATION_FREEZE_VERSION_MISMATCH')
            if digest(EV/'candidate_lock.json')!=freeze['candidate_lock_sha256'] or self.ids!=freeze['eval_ids'] or self.split['llm_subsets'][partition]!=freeze['eval_llm_ids']:
                raise ValueError('EVALUATION_CANDIDATE_OR_SCOPE_CHANGED')
            for path,key in ((ROOT/'task1/workflow/g2_modes.py','mode_implementation_sha256'),
                             (ROOT/'task1/workflow/g2_provider.py','provider_implementation_sha256'),
                             (ROOT/freeze['memory_path'],'memory_sha256')):
                if digest(path)!=freeze[key]:raise ValueError('EVALUATION_FROZEN_COMPONENT_CHANGED:'+key)
            if freeze['processing_source_hashes']!=source_snapshot():raise ValueError('EVALUATION_PROCESSING_CODE_CHANGED')
        if self.contract['reference_parameters']!=REFERENCE or self.contract['parameter_grids']!=GRID:
            raise ValueError('IMPLEMENTATION_CONTRACT_MISMATCH')
        self.raw=raw_data();self.records={rid:adapt(rid,self.raw[rid]) for rid in self.ids}
        self.source_hashes=source_snapshot();self.tree_hash=object_hash(self.source_hashes)
        self.path=self.directory/'manifest.json'
        if self.path.exists():
            if not resume:raise ValueError('RUN_EXISTS_RESUME_EXPLICITLY')
            self.manifest=read_json(self.path)
            if self.manifest['partition']!=partition or self.manifest['input_ids']!=self.ids or self.manifest['raw_sha256']!=self.split['raw_sha256']:
                raise ValueError('RUN_SCOPE_OR_PARTITION_MISMATCH')
            self.source_hashes=self.manifest['source_hashes'];self.tree_hash=object_hash(self.source_hashes)
            if self.tree_hash!=self.manifest['source_tree_sha256']:raise ValueError('SOURCE_TREE_BINDING_MISMATCH')
            self.assert_epoch()
            if self.manifest['contract_sha256']!=self.contract_hash or self.manifest['split_sha256']!=self.split_hash:
                raise ValueError('RUN_PARENT_VERSION_MISMATCH')
        else:
            self.directory.mkdir(parents=True,exist_ok=True)
            self.manifest={'goal_id':self.contract['goal_id'],'run_id':run_id,'started_at':now(),
                'status':'RUNNING','classification':classification,'source_crs':'UNVERIFIED',
                'raw_sha256':self.split['raw_sha256'],'partition':partition,'input_ids':self.ids,
                'contract_sha256':self.contract_hash,'split_sha256':self.split_hash,
                'source_hashes':self.source_hashes,'source_tree_sha256':self.tree_hash,
                'code_head_at_start':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'code_binding':'verifiable exact source hashes; final CODE_SHA mapped at publication',
                'artifacts':{},'candidate_evaluations':0,'deterministic_tool_calls':0,'cache_reads':0,
                'experiment_model_dispatches':0,'command':' '.join(__import__('sys').argv)}
            self.save()

    def save(self):write_json(self.path,self.manifest)

    def assert_epoch(self):
        if set(self.source_hashes)!=set(source_snapshot()):raise ValueError('SOURCE_DEPENDENCY_SET_CHANGED_NEW_RUN_REQUIRED')
        for p,h in self.source_hashes.items():
            if digest(ROOT/p)!=h:raise ValueError('SOURCE_CHANGED_NEW_RUN_REQUIRED:'+p)
        if digest(CFG/'contract.json')!=self.contract_hash:raise ValueError('CONTRACT_CHANGED')
        if digest(EV/'data/split_manifest.json')!=self.split_hash:raise ValueError('SPLIT_CHANGED')

    def provenance(self,ids):
        return {'goal_id':self.contract['goal_id'],'run_id':self.run_id,'raw_sha256':self.split['raw_sha256'],
                'partition':self.partition,'scope_sha256':object_hash(ids),'source_tree_sha256':self.tree_hash,
                'contract_sha256':self.contract_hash,'split_sha256':self.split_hash,
                'adapter_version':self.contract['model']['adapter_version']}

    def evaluate_batch(self,parameters,order='S-D-P',*,record_ids=None,experiment_ids=None):
        self.assert_epoch();parameters=execution_parameters(parameters);ids=record_ids or self.ids
        if not set(ids)<=set(self.ids):raise ValueError('OUT_OF_SCOPE_RECORD')
        key=object_hash({'raw':self.split['raw_sha256'],'scope':ids,'code':self.tree_hash,
                         'contract':self.contract_hash,'config':parameters,'order':order})
        if key in self.manifest['artifacts']:
            entry=self.manifest['artifacts'][key]
            path=bound_path(self.directory,entry['file']);review_path=bound_path(self.directory,entry['review_file'])
            if digest(path)!=entry['sha256'] or digest(review_path)!=entry['review_sha256']:raise ValueError('CACHE_CORRUPTED')
            result=read_gzip(path);saved_review=read_json(review_path)
            if saved_review['status']!='VERIFIED' or saved_review['target_hash']!=object_hash(result):raise ValueError('CACHE_REVIEW_TARGET_MISMATCH')
            review=review_batch(result,[self.records[rid] for rid in ids],expected_parameters=parameters,expected_order=order,
                contract_hash=self.contract_hash,trusted_provenance=self.provenance(ids))
            if review['status']!='VERIFIED' or entry['summary']!=result['summary'] or entry['engineering_status']!=review['status']:
                raise ValueError('CACHE_INDEPENDENT_RECHECK_FAILED')
            self.manifest['cache_reads']+=1;self.save()
            return result,entry
        started=time.perf_counter();records=[self.records[rid] for rid in ids];provenance=self.provenance(ids)
        result=run_batch(records,parameters,order,contract_hash=self.contract_hash,provenance=provenance)
        audit=review_batch(result,records,expected_parameters=parameters,expected_order=order,
                           contract_hash=self.contract_hash,trusted_provenance=provenance)
        filename=f'{config_id(parameters)}_{order}_{object_hash(ids)[:8]}.json.gz'
        write_gzip(self.directory/filename,result)
        audit_file=filename.removesuffix('.json.gz')+'_review.json';write_json(self.directory/audit_file,audit,exclusive=True)
        entry={'experiment_key':key,'experiment_ids':experiment_ids or [],'config_id':config_id(parameters),
               'parameters':parameters,'order':order,'input_ids':ids,'file':filename,'sha256':digest(self.directory/filename),
               'review_file':audit_file,'review_sha256':digest(self.directory/audit_file),'engineering_status':audit['status'],
               'summary':result['summary'],'elapsed_seconds':time.perf_counter()-started}
        self.manifest['artifacts'][key]=entry;self.manifest['candidate_evaluations']+=len(ids)
        self.manifest['deterministic_tool_calls']+=2;self.save()
        if audit['status']!='VERIFIED':raise ValueError('PROCESSING_REVIEW_FAILED:'+key)
        return result,entry

    def finish(self):
        self.assert_epoch();self.manifest.update(status='REVIEW_PENDING',ended_at=now());self.save()


def parameter_development(run):
    matrix=read_json(CFG/'experiment_matrix.json');rows=[]
    for config in matrix['parameter_configurations']:
        result,entry=run.evaluate_batch(config['parameters'],experiment_ids=config['memberships'])
        rows.append(entry)
        print(json.dumps({'config':entry['config_id'],'records':len(result['records']),'status':entry['engineering_status'],'seconds':round(entry['elapsed_seconds'],2)}),flush=True)
    write_json(run.directory/'parameter_table.json',rows)
    run.manifest.setdefault('tables',{})['parameter_table.json']=digest(run.directory/'parameter_table.json');run.finish()
    return rows


def order_development(run):
    entries=[]
    baseline,_=run.evaluate_batch(REFERENCE,'S-D-P',experiment_ids=['G2-ORDER'])
    base={r['record_id']:r for r in baseline['records']}
    for order in run.contract['orders']:
        result,entry=run.evaluate_batch(REFERENCE,order,experiment_ids=['G2-ORDER'])
        failures=[];comparisons=[]
        for row in result['records']:
            b=base[row['record_id']];c=compare(row,b);comparisons.append({'record_id':row['record_id'],**c})
            protected={v['index'] for v in b['metrics']['common_point_errors'] if v['error'] is not None}
            covered={v['index'] for v in row['metrics']['common_point_errors'] if v['error'] is not None}
            if row['metrics']['raw_break_crossings'] or not protected<=covered or row['metrics']['raw_windows_covered']<b['metrics']['raw_windows_covered'] or (b['metrics']['record_covered'] and not row['metrics']['record_covered']):
                failures.append({'record_id':row['record_id'],'raw_break_crossings':row['metrics']['raw_break_crossings'],
                                 'lost_covered_indices':sorted(protected-covered),'record_or_window_loss':row['metrics']['raw_windows_covered']<b['metrics']['raw_windows_covered']})
        entry['safety_failures']=failures;entry['record_comparisons']=comparisons
        entry['research_status']='REJECTED_BY_CONSTRAINT' if failures else 'FEASIBLE_FOR_STAGE_EVALUATION'
        entry['geometric_status']='TRADEOFF' if any(not c['feasible'] for c in comparisons) else 'NO_PROTECTION_DEGRADATION'
        entries.append(entry)
        print(json.dumps({'order':order,'crossings':result['summary']['raw_break_crossings'],'records':len(result['records'])}),flush=True)
    write_json(run.directory/'order_table.json',entries)
    run.manifest.setdefault('tables',{})['order_table.json']=digest(run.directory/'order_table.json');run.finish();return entries


def candidate_lock(parameter_run_id,order_run_id):
    directory=EV/'runs'/parameter_run_id;manifest=read_json(directory/'manifest.json')
    if manifest['partition']!='DEVELOPMENT':raise ValueError('SELECTION_REQUIRES_DEVELOPMENT')
    trusted_run=ExperimentRun(parameter_run_id,'DEVELOPMENT',resume=True)
    expected_configs={c['config_id']:c['parameters'] for c in read_json(CFG/'experiment_matrix.json')['parameter_configurations']}
    if {e['config_id'] for e in manifest['artifacts'].values()}!=set(expected_configs):raise ValueError('INCOMPLETE_DEVELOPMENT_GRID')
    for entry in manifest['artifacts'].values():
        if entry['parameters']!=expected_configs[entry['config_id']] or entry['input_ids']!=trusted_run.ids or entry['order']!='S-D-P':
            raise ValueError('DEVELOPMENT_CONFIG_OR_SCOPE_MISMATCH')
        if digest(directory/entry['file'])!=entry['sha256'] or digest(directory/entry['review_file'])!=entry['review_sha256']:
            raise ValueError('DEVELOPMENT_RESULT_OR_REVIEW_CHANGED')
        result=read_gzip(directory/entry['file']);audit=read_json(directory/entry['review_file'])
        if audit['status']!='VERIFIED' or audit['target_hash']!=object_hash(result):raise ValueError('DEVELOPMENT_REVIEW_TARGET_MISMATCH')
        trusted=review_batch(result,[trusted_run.records[rid] for rid in trusted_run.ids],
            expected_parameters=expected_configs[entry['config_id']],expected_order='S-D-P',
            contract_hash=trusted_run.contract_hash,trusted_provenance=trusted_run.provenance(trusted_run.ids))
        if trusted['status']!='VERIFIED':raise ValueError('DEVELOPMENT_SELECTION_RECHECK_FAILED')
        expected_key=object_hash({'raw':trusted_run.split['raw_sha256'],'scope':trusted_run.ids,'code':trusted_run.tree_hash,
            'contract':trusted_run.contract_hash,'config':expected_configs[entry['config_id']],'order':'S-D-P'})
        if entry['summary']!=result['summary'] or entry['engineering_status']!=trusted['status'] or entry['config_id']!=config_id(result['parameters']) or entry['experiment_key']!=expected_key:
            raise ValueError('DEVELOPMENT_MANIFEST_SUMMARY_OR_BINDING_MISMATCH')
    entries=list(manifest['artifacts'].values());reference=next(e for e in entries if e['parameters']==REFERENCE)
    baseline=read_gzip(directory/reference['file']);base={r['record_id']:r for r in baseline['records']}
    per_config={};result_map={};feasible=[]
    for entry in entries:
        result=read_gzip(directory/entry['file']);cid=entry['config_id'];result_map[cid]=entry
        comparisons=[compare(r,base[r['record_id']]) for r in result['records']]
        good=all(c['feasible'] for c in comparisons);gain=any(c['strict_gain'] for c in comparisons)
        item={'config_id':cid,'parameters':entry['parameters'],'engineering_status':entry['engineering_status'],
              'feasible_all_records':good,'strict_gain_any_record':gain,'record_comparisons':comparisons,
              'summary':entry['summary'],'status':'SUPPORTED_WITHIN_SCOPE' if good and gain else
              'NO_DEMONSTRATED_GAIN' if good else 'REJECTED_BY_CONSTRAINT' if any(c['status']=='REJECTED_BY_CONSTRAINT' for c in comparisons) else 'TRADEOFF'}
        per_config[cid]=item
        if good:feasible.append(cid)
    chosen={};refid=reference['config_id']
    for name,allowed in [('C-S',set(P for P in ('dt','distance','min_points','min_length'))),('C-D',{'direction'}),('C-P',{'dp'})]:
        domain=[cid for cid,e in result_map.items() if all(e['parameters'][k]==REFERENCE[k] for k in REFERENCE if k not in allowed)]
        gains=[cid for cid in domain if per_config[cid]['feasible_all_records'] and per_config[cid]['strict_gain_any_record']]
        def dominates(first,second):
            strict=False
            for x,y in zip(per_config[first]['record_comparisons'],per_config[second]['record_comparisons']):
                if not set(y['candidate_covered_indices'])<=set(x['candidate_covered_indices']):return False
                strict=strict or x['candidate_covered_count']>y['candidate_covered_count']
                a,b=x['candidate_max_on_baseline_covered'],y['candidate_max_on_baseline_covered']
                eps=max(x['numerical_allowance'],y['numerical_allowance'])
                if b is not None and (a is None or a>b+eps):return False
                if a is not None and b is not None and a<b-eps:strict=True
            return strict
        frontier=[a for a in gains if not any(dominates(b,a) for b in gains if a!=b)]
        if name=='C-P' and gains:
            selected=min(gains,key=lambda cid:(per_config[cid]['summary']['n_dp_output'],per_config[cid]['summary']['dp_max_error'] or 0,result_map[cid]['parameters']['dp'],cid))
            reason='COMPRESSION_WITHIN_COMMON_5_WORK_METRE_BUDGET'
        elif len(frontier)==1:selected=frontier[0];reason='UNIQUE_PROTECTED_PARETO_GAIN'
        else:selected=refid;reason='NO_UNIQUE_COMPARABLE_GAIN_KEEP_REFERENCE'
        chosen[name]={'config_id':selected,'parameters':result_map[selected]['parameters'],
                      'selection_reason':reason,'eligible_gain_ids':gains,'pareto_frontier':frontier,'domain_ids':domain,
                      'research_status':per_config[selected]['status'],'final_method_frozen':False}
    order_run=ExperimentRun(order_run_id,'DEVELOPMENT',resume=True)
    if digest(order_run.directory/'order_table.json')!=order_run.manifest['tables']['order_table.json']:
        raise ValueError('ORDER_SELECTION_TABLE_CHANGED')
    orders=read_json(order_run.directory/'order_table.json')
    if {r['order'] for r in orders}!=set(order_run.contract['orders']):raise ValueError('INCOMPLETE_SIX_ORDER_STUDY')
    for item in orders:
        if digest(order_run.directory/item['file'])!=item['sha256'] or item['input_ids']!=order_run.ids:
            raise ValueError('ORDER_TARGET_OR_SCOPE_CHANGED')
        result=read_gzip(order_run.directory/item['file']);trusted=[order_run.records[rid] for rid in order_run.ids]
        audit=review_batch(result,trusted,expected_parameters=REFERENCE,expected_order=item['order'],
            contract_hash=order_run.contract_hash,trusted_provenance=order_run.provenance(order_run.ids))
        if audit['status']!='VERIFIED':raise ValueError('ORDER_RECHECK_FAILED')
        failures=[]
        for row in result['records']:
            base_row=base[row['record_id']]
            before={x['index'] for x in base_row['metrics']['common_point_errors'] if x['error'] is not None}
            after={x['index'] for x in row['metrics']['common_point_errors'] if x['error'] is not None}
            if row['metrics']['raw_break_crossings'] or not before<=after or row['metrics']['raw_windows_covered']<base_row['metrics']['raw_windows_covered'] or (base_row['metrics']['record_covered'] and not row['metrics']['record_covered']):failures.append(row['record_id'])
        safe=not failures
        if safe!=(item['research_status']=='FEASIBLE_FOR_STAGE_EVALUATION'):raise ValueError('ORDER_FEASIBILITY_TABLE_MISMATCH')
    lock={'frozen_at':now(),'source_partition':'DEVELOPMENT','parameter_run_id':parameter_run_id,
          'order_run_id':order_run_id,'selected_single_candidates':chosen,'all_config_assessments':per_config,
          'feasible_set':feasible,'feasible_orders':[e['order'] for e in orders if e['research_status']=='FEASIBLE_FOR_STAGE_EVALUATION'],
          'eval_representatives':read_json(CFG/'experiment_matrix.json')['fixed_eval_representative_config_ids'],
          'g2_eval_observed_for_selection':False,'structural_candidates':read_json(CFG/'contract.json')['structural_candidates']}
    write_json(EV/'candidate_lock.json',lock,exclusive=True)
    return lock
