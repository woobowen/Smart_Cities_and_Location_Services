"""Goal 2 task registry, reusing the existing journal's evidence/event helpers."""
from pathlib import Path
from .goal import GoalJournal
from .io import ROOT, read_json, write_json, now, digest, object_hash

TASKS={
 'handoff':[], 'contract':['handoff'], 'split':['contract'], 'core':['contract'],
 'development_parameters':['split','core'], 'development_orders':['split','core'],
 'memory':['split','core'], 'development_modes':['memory','development_parameters'],
 'evaluation_freeze':['development_parameters','development_orders','development_modes'],
 'evaluation_parameters':['evaluation_freeze'], 'evaluation_orders':['evaluation_freeze'],
 'evaluation_modes':['evaluation_freeze'], 'candidates':['evaluation_parameters'],
 'counterexamples':['core'], 'notebooks':['evaluation_modes','candidates','counterexamples'],
 'figures':['evaluation_modes','candidates','counterexamples'],
 'analysis':['evaluation_modes','candidates','counterexamples'],
 'internal_acceptance':['notebooks','figures','analysis'], 'publication':['internal_acceptance']}

REQUIRED_COMPONENTS={
 'handoff':['raw_sha256','teacher_starter_bytes','seven_record_independent_geometry','G1_current_production_recompute_exact_match'],
 'contract':['teacher_requirements','comparison_definitions','selection_rules','data_partition_rules','mode_budgets','scope_boundaries'],
 'split':['raw_hash','exact_scope','record_isolation','strata_recomputation','stable_selection','reserved_protection'],
 'core':['six_orders','independent_metrics','point_accounting','numeric_boundaries','fault_injections','controller_closure'],
 'development_parameters':['exact_grid','complete_record_scope','independent_record_review','metrics_denominators','current_versions'],
 'development_orders':['all_six_orders','raw_breakpoint_failures','stage_dependencies','complete_record_scope','current_versions'],
 'memory':['demo_scope','verifier_admission','retrieval_applicability','leakage_isolation','snapshot_integrity'],
 'development_modes':['four_structures','live_provenance','zero_model_search','budgets','feedback_causality','memory_consumption'],
 'evaluation_freeze':['development_selection_only','candidate_lock','memory_lock','prompt_lock','evaluation_scope_lock'],
 'evaluation_parameters':['frozen_configs','complete_record_scope','independent_record_review','no_eval_reselection','current_versions'],
 'evaluation_orders':['frozen_feasible_orders','complete_record_scope','raw_breakpoint_protection','current_versions'],
 'evaluation_modes':['four_structures','three_episodes','live_provenance','zero_model_search','budgets','memory_readonly','current_versions'],
 'candidates':['three_single_candidates','development_selection_only','heldout_confirmation','negative_results','no_combination'],
 'counterexamples':['known_answers','real_execution','synthetic_labels','pilot_explanations','actual_ai_citations'],
 'notebooks':['fresh_kernel_execution','raw_recompute','zero_new_model_calls','teacher_cell_mapping'],
 'figures':['current_data_binding','editable_sources','visual_inspection','all_required_figures'],
 'analysis':['requirements_coverage','conditional_limits','negative_results','no_quality_overclaim'],
 'internal_acceptance':['A%02d'%i for i in range(1,18)],
 'publication':['internal_acceptance_passed','release_safety','remote_sha_match','fixed_sha_readback']}


def task_sources(task):
    if task=='handoff':return ['task1/workflow/'+p+'.py' for p in ('geometry','evaluation','coordinates','pipeline')]
    if task=='contract':return ['task1/config/goal2/contract.json','task1/config/goal2/experiment_matrix.json','task1/docs/goal2/CONTRACT.md']
    if task=='split':return ['task1/workflow/g2_data.py','task1/config/goal2/contract.json']
    paths=['task1/workflow/'+p+'.py' for p in ('io','geometry','evaluation','coordinates','g2_pipeline','g2_metrics','g2_data','g2_selection')]
    if task in ('core','memory','development_modes','evaluation_freeze','evaluation_modes','internal_acceptance','publication'):
        paths.extend('task1/workflow/'+p+'.py' for p in ('g2_provider','g2_memory','g2_journal'))
    if task not in ('handoff','contract','split'):
        paths.extend(str(p.relative_to(ROOT)) for p in (ROOT/'task1/workflow').glob('g2_*.py'))
        paths.append('task1/scripts/goal2.py')
        scoped={'counterexamples':['goal2_counterexamples.py'],
                'figures':['build_goal2_figures.py'],'notebooks':['build_goal2_notebooks.py'],
                'analysis':['build_goal2_analysis.py'],
                'internal_acceptance':['goal2_counterexamples.py','goal2_coordinate_sensitivity.py','build_goal2_figures.py','build_goal2_notebooks.py','build_goal2_analysis.py'],
                'publication':['goal2_counterexamples.py','goal2_coordinate_sensitivity.py','build_goal2_figures.py','build_goal2_notebooks.py','build_goal2_analysis.py']}
        paths.extend('task1/scripts/'+p for p in scoped.get(task,[]))
    return sorted(set(paths))


def source_snapshot():
    # Processing/decision epoch. Rendering, Notebook generation and post-hoc
    # reports have separate source bindings and cannot affect these arithmetic
    # tools. A presentation edit must not masquerade as a new model episode.
    paths=sorted((ROOT/'task1/workflow').glob('*.py'))
    paths.append(ROOT/'task1/scripts/goal2.py')
    return {str(p.relative_to(ROOT)):digest(p) for p in paths}


class G2Journal(GoalJournal):
    def __init__(self, directory=ROOT/'task1/evidence/goal2'):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.path=self.directory/'goal_state.json'
        if self.path.exists():
            self.state=read_json(self.path)
            if set(self.state['tasks'])!=set(TASKS):raise ValueError('UNKNOWN_G2_TASK_CHECKPOINT')
        else:
            self.state={'goal_id':'SC-LAB1-G2-EXPERIMENTS-001','status':'IMPLEMENTING',
                'gpt_second_review':'PENDING','submission':'NOT_READY','events':[],
                'tasks':{k:{'status':'PENDING','depends_on':v,'evidence':[]} for k,v in TASKS.items()},
                'issues':{},'runs':{},'inflight':None,'governance_role_dispatches':[],
                'experiment_model_dispatches':0,'deterministic_tool_calls':0}
            self.save()

    def dispatch_role(self, role, context, task, operation):
        row={'at':now(),'role':role,'context':context,'task':task,'operation':operation,
             'provider_requests':'unknown','independent_os_sandbox':False}
        self.state['governance_role_dispatches'].append(row)
        self.event('NATIVE_ROLE_DISPATCH',**row)

    def ready(self, task):
        if task in ('internal_acceptance','publication'):
            required=set(TASKS)-{'publication','internal_acceptance'}
            if task=='publication':required.add('internal_acceptance')
            return all(self.state['tasks'][d]['status']=='VERIFIED' for d in required)
        return all(self.state['tasks'][d]['status']=='VERIFIED' for d in TASKS[task])

    def submit(self, task, paths):
        row=self.state['tasks'][task]
        evidence=[self.attach(p) for p in paths]
        if not evidence:raise ValueError('NONEMPTY_TARGETS_REQUIRED')
        if not self.ready(task):raise ValueError('DEPENDENCY_NOT_VERIFIED')
        sources={p:digest(ROOT/p) for p in task_sources(task)}
        row.update(status='REVIEW_PENDING',evidence=evidence,source_hashes=sources)
        self.event('TASK_SUBMITTED',task=task)

    def accept(self, task, receipt_path, verifier):
        if not verifier.startswith('C:'):raise ValueError('INDEPENDENT_C_REQUIRED')
        receipt=read_json(receipt_path)
        item=receipt.get('tasks',{}).get(task,receipt)
        contexts={r['context'] for r in self.state['governance_role_dispatches'] if r['role']=='C'}
        if verifier[2:] not in contexts or receipt.get('role_context')!=verifier[2:]:
            raise ValueError('UNREGISTERED_INDEPENDENT_REVIEWER')
        if item.get('status')!='VERIFIED' or not item.get('checked_components'):
            raise ValueError('INCOMPLETE_C_RECEIPT')
        row=self.state['tasks'][task]
        if row['status']!='REVIEW_PENDING':raise ValueError('TASK_NOT_REVIEW_PENDING')
        if not self.ready(task):raise ValueError('DEPENDENCY_NOT_VERIFIED')
        if not row['evidence']:raise ValueError('NONEMPTY_TARGETS_REQUIRED')
        if not set(REQUIRED_COMPONENTS[task])<=set(item['checked_components']):
            raise ValueError('REQUIRED_CHECK_COVERAGE_MISSING')
        self.check_sources(row,task)
        if item.get('source_hashes')!=row['source_hashes']:raise ValueError('REVIEW_SOURCE_EPOCH_MISMATCH')
        targets=item.get('targets',[])
        self.check_evidence(row['evidence']);self.check_evidence(targets)
        if not {object_hash(e) for e in row['evidence']} <= {object_hash(e) for e in targets}:
            raise ValueError('C_TARGET_MISMATCH')
        if any(i['status']!='VERIFIED' for i in self.state['issues'].values() if i['parent_task']==task):
            raise ValueError('OPEN_ISSUE')
        row.update(status='VERIFIED',verifier=verifier,review=self.attach(receipt_path))
        self.event('TASK_VERIFIED',task=task,verifier=verifier)

    def check_sources(self,row,task):
        if not row.get('source_hashes'):raise ValueError('SOURCE_EPOCH_MISSING')
        if set(row['source_hashes'])!=set(task_sources(task)):raise ValueError('SOURCE_DEPENDENCY_SET_CHANGED')
        for path,sha in row['source_hashes'].items():
            if digest(ROOT/path)!=sha:raise ValueError('SOURCE_EPOCH_CHANGED:'+path)

    def issue(self, issue_id, parent_task, fact, violated_clause, affected, repairer, source):
        if issue_id in self.state['issues']:raise ValueError('ISSUE_ALREADY_REGISTERED')
        self.state['issues'][issue_id]={'issue_id':issue_id,'parent_task':parent_task,
            'fact':fact,'violated_clause':violated_clause,'affected_artifacts':affected,
            'repairer':repairer,'source':source,'verifier':None,'status':'ISSUE_OPEN','closure_evidence':[]}
        self.state['tasks'][parent_task]['status']='ISSUE_OPEN'
        self.event('ISSUE_OPENED',issue_id=issue_id)

    def repair(self, issue_id, paths):
        issue=self.state['issues'][issue_id]
        if issue['status'] not in ('ISSUE_OPEN','REGRESSION_PENDING'):raise ValueError('ISSUE_NOT_OPEN_FOR_REPAIR')
        evidence=[self.attach(p) for p in paths]
        if not evidence:raise ValueError('NONEMPTY_REPAIR_TARGETS_REQUIRED')
        issue['status']='REGRESSION_PENDING'
        issue['repair_evidence']=evidence
        issue['repair_source_hashes']={e['path']:e['sha256'] for e in evidence}
        self.state['tasks'][issue['parent_task']]['status']='REGRESSION_PENDING'
        self.event('B_REPAIR_SUBMITTED',issue_id=issue_id)

    def close_issue(self, issue_id, receipt_path, verifier):
        issue=self.state['issues'][issue_id]
        if not verifier.startswith('C:') or verifier==issue['repairer']:raise ValueError('INDEPENDENT_C_REQUIRED')
        receipt=read_json(receipt_path);item=receipt.get('issues',{}).get(issue_id,receipt)
        contexts={r['context'] for r in self.state['governance_role_dispatches'] if r['role']=='C'}
        if verifier[2:] not in contexts or receipt.get('role_context')!=verifier[2:]:raise ValueError('UNREGISTERED_INDEPENDENT_REVIEWER')
        if issue['status']!='REGRESSION_PENDING' or not issue.get('repair_evidence'):raise ValueError('REPAIR_NOT_SUBMITTED')
        if item.get('issue_id')!=issue_id:raise ValueError('ISSUE_TARGET_MISMATCH')
        if item.get('status')!='VERIFIED' or not item.get('checked_components'):raise ValueError('REGRESSION_NOT_VERIFIED')
        required={'fault_rejected','valid_receipt_accepted','source_epoch'}
        if not required<=set(item['checked_components']):raise ValueError('REGRESSION_COVERAGE_INCOMPLETE')
        if item.get('source_hashes')!=issue['repair_source_hashes']:raise ValueError('REPAIR_SOURCE_EPOCH_MISMATCH')
        targets=item.get('targets',[]);self.check_evidence(targets);self.check_evidence(issue['repair_evidence'])
        if not {object_hash(e) for e in issue['repair_evidence']} <= {object_hash(e) for e in targets}:
            raise ValueError('REPAIR_TARGET_MISMATCH')
        issue.update(status='VERIFIED',verifier=verifier,closure_evidence=[self.attach(receipt_path)])
        self.state['tasks'][issue['parent_task']]['status']='PENDING'
        self.event('C_VERIFIED_PARENT_RESUMED',issue_id=issue_id,parent_task=issue['parent_task'])

    def checkpoint(self):
        for name,row in self.state['tasks'].items():
            if row['status']=='VERIFIED':
                self.check_evidence(row['evidence']);self.check_evidence([row['review']])
                self.check_sources(row,name)
                if not self.ready(name):raise ValueError('VERIFIED_TASK_DEPENDENCY_INVALID')
        self.state['status']='VERIFIED' if all(t['status']=='VERIFIED' for t in self.state['tasks'].values()) and all(i['status']=='VERIFIED' for i in self.state['issues'].values()) else 'IMPLEMENTING'
        self.event('CHECKPOINT',status=self.state['status'])
        return self.state['status']
