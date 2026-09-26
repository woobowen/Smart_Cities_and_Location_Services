"""Experiment 1 Goal 1 task/issue journal, with actual repair and review handoff.

Native A/B/C sessions are dispatched by the authorized main Codex session. This
journal records their actual receipts and enforces task dependencies; it does not
pretend to launch an absent model or evaluate model-generated shell commands.
"""
from pathlib import Path
from .io import ROOT, CONFIG, DATA, read_json, write_json, object_hash, digest, now, bound_path
from .pipeline import preflight
from .artifact_review import COMPONENTS
from .tools import execute_tool


TASKS = {
    'governance': [], 'review_targets': [], 'trusted_baseline': [],
    'diagnostics': ['review_targets'],
    'real_baseline': ['trusted_baseline', 'diagnostics'],
    'processing_feedback': ['real_baseline'],
    'notebooks': ['diagnostics'], 'figures': ['diagnostics'],
    'internal_review': ['governance', 'review_targets', 'trusted_baseline', 'diagnostics', 'notebooks', 'figures'],
}
REVIEW_ACTIONS = {'profile_pilot':'verify_profiles', 'time_boundaries':'verify_time_boundaries',
                  'duplicate_details':'verify_duplicate_details', 'baseline':'verify_baseline'}
TASK_ARTIFACTS = {'diagnostics':['profile_pilot','time_boundaries','duplicate_details'],
                  'real_baseline':['baseline'], 'processing_feedback':['baseline']}


class GoalJournal:
    def __init__(self, directory):
        self.directory = Path(directory); self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory/'goal_state.json'
        if self.path.exists():
            self.state = read_json(self.path)
            if set(self.state['tasks']) != set(TASKS): raise ValueError('UNKNOWN_TASK_CHECKPOINT')
        else:
            self.state = {'goal_id':'SC-LAB1-G1-FOUNDATION-001', 'execution':'SC-LAB1-G1-COMPLETE-001',
                          'status':'IMPLEMENTING', 'gpt_second_review':'PENDING', 'submission':'NOT_READY',
                          'tasks':{k:{'status':'PENDING','depends_on':v,'evidence':[]} for k,v in TASKS.items()},
                          'issues':{}, 'events':[], 'runs':{}, 'inflight':None, 'current_code_sha':None}
            self.save()

    def save(self): write_json(self.path, self.state)

    def event(self, kind, **fields):
        event = {'sequence':len(self.state['events']), 'at':now(), 'kind':kind,
                 'previous_hash':self.state['events'][-1]['hash'] if self.state['events'] else 'ROOT', **fields}
        event['hash'] = object_hash(event); self.state['events'].append(event); self.save()

    def attach(self, path):
        p = Path(path).resolve()
        if not p.is_relative_to(ROOT) or p.is_symlink() or not p.is_file(): raise ValueError('EVIDENCE_PATH_REQUIRED')
        return {'path':str(p.relative_to(ROOT)), 'sha256':digest(p)}

    def check_evidence(self, evidence):
        for e in evidence:
            if digest(bound_path(ROOT,e['path'])) != e['sha256']: raise ValueError('EVIDENCE_CHANGED:'+e['path'])

    def open_issue(self, issue_id, parent_task, source, error, contract, affected_artifacts, repairer):
        if issue_id in self.state['issues']: return self.state['issues'][issue_id]
        if parent_task not in TASKS: raise ValueError('UNKNOWN_PARENT_TASK')
        issue = {'issue_id':issue_id, 'parent_task':parent_task, 'source':source, 'actual_error':error,
                 'violated_contract':contract, 'severity':'BLOCKING', 'affected_artifacts':affected_artifacts,
                 'repairer':repairer, 'verifier':None, 'status':'NEEDS_REPAIR', 'closure_evidence':[]}
        self.state['issues'][issue_id] = issue
        self.state['tasks'][parent_task]['status'] = 'NEEDS_REPAIR'
        self.event('ISSUE_OPENED', issue_id=issue_id, source=source)
        return issue

    def claim_repair(self, issue_id, actor):
        issue = self.state['issues'][issue_id]
        if issue['status'] != 'NEEDS_REPAIR' or issue['repairer'] != actor: raise ValueError('REPAIR_HANDOFF_MISMATCH')
        issue['status'] = 'REPAIRING'; self.state['tasks'][issue['parent_task']]['status'] = 'REPAIRING'
        self.event('B_REPAIR_CONSUMED', issue_id=issue_id, actor=actor)

    def submit_repair(self, issue_id, actor, paths):
        issue = self.state['issues'][issue_id]
        if issue['status'] != 'REPAIRING' or actor != issue['repairer']: raise ValueError('REPAIR_NOT_CLAIMED')
        issue['repair_evidence'] = [self.attach(p) for p in paths]
        if not issue['repair_evidence']: raise ValueError('REPAIR_EVIDENCE_REQUIRED')
        issue['status'] = 'AWAITING_REGRESSION'
        self.state['tasks'][issue['parent_task']]['status'] = 'AWAITING_REGRESSION'
        self.event('REPAIR_SUBMITTED', issue_id=issue_id, actor=actor)

    def review_repair(self, issue_id, report_path, verifier):
        issue = self.state['issues'][issue_id]
        if verifier == issue['repairer'] or not verifier.startswith('C:'): raise ValueError('INDEPENDENT_C_REQUIRED')
        if issue['status'] != 'AWAITING_REGRESSION': raise ValueError('REGRESSION_NOT_READY')
        report = read_json(report_path)
        self.check_evidence(issue['repair_evidence'])
        item = report['issues'][issue_id]
        if not item.get('checked') or not item.get('source_hashes'): raise ValueError('REVIEW_COVERAGE_REQUIRED')
        for name, sha in item['source_hashes'].items():
            if digest(bound_path(ROOT,name)) != sha: raise ValueError('REVIEW_CODE_CHANGED')
        issue['verifier'] = verifier
        issue['closure_evidence'].append(self.attach(report_path))
        if item['status'] != 'VERIFIED':
            issue['status'] = 'NEEDS_REPAIR'; self.state['tasks'][issue['parent_task']]['status'] = 'NEEDS_REPAIR'
            self.event('C_REOPENED', issue_id=issue_id, verifier=verifier); return
        issue['status'] = 'VERIFIED'
        parent = issue['parent_task']
        if all(i['status']=='VERIFIED' for i in self.state['issues'].values() if i['parent_task']==parent):
            self.state['tasks'][parent]['status'] = 'PENDING'
        self.event('C_VERIFIED_PARENT_RESUMED', issue_id=issue_id, parent_task=parent, verifier=verifier)

    def complete_task(self, task, report_path, verifier):
        if not verifier.startswith('C:'): raise ValueError('C_VERIFICATION_REQUIRED')
        row = self.state['tasks'][task]
        if any(self.state['tasks'][d]['status']!='VERIFIED' for d in row['depends_on']):
            raise ValueError('DEPENDENCY_NOT_VERIFIED')
        if any(i['status']!='VERIFIED' for i in self.state['issues'].values() if i['parent_task']==task):
            raise ValueError('OPEN_BLOCKING_ISSUE')
        report = read_json(report_path); item = report['tasks'][task]
        if item['status']!='VERIFIED' or not item.get('evidence'): raise ValueError('TASK_REVIEW_INCOMPLETE')
        self.check_evidence(item['evidence'])
        if task in TASK_ARTIFACTS:
            run_id=self.state.get('current_run')
            if item.get('run_id')!=run_id or not run_id: raise ValueError('CURRENT_RUN_REVIEW_REQUIRED')
            coverage=self.coverage(run_id,TASK_ARTIFACTS[task])
            if coverage['status']!='VERIFIED': raise ValueError('REQUIRED_ARTIFACT_REVIEW_INCOMPLETE')
            run=self.state['runs'][run_id]
            required=[run['artifacts'][a] for a in TASK_ARTIFACTS[task]]+[run['reviews'][a] for a in TASK_ARTIFACTS[task]]
            supplied={(e['path'],e['sha256']) for e in item['evidence']}
            if not all((e['path'],e['sha256']) in supplied for e in required): raise ValueError('ARTIFACT_EVIDENCE_NOT_BOUND')
            row['run_id']=run_id
        if task=='processing_feedback':
            followup=self.state['runs'][run_id].get('followup')
            if not followup or not item.get('followup_review'): raise ValueError('REAL_FOLLOWUP_REVIEW_REQUIRED')
            self.check_evidence([followup, item['followup_review']])
            for path,sha in followup['source_hashes'].items():
                if digest(ROOT/path)!=sha: raise ValueError('FOLLOWUP_SOURCE_CHANGED')
            audit=read_json(ROOT/item['followup_review']['path'])
            if (audit.get('status')!='VERIFIED' or audit.get('target_sha256')!=followup['sha256']
                    or not audit.get('checked_components') or audit.get('unchecked_components')):
                raise ValueError('FOLLOWUP_TARGET_REVIEW_INCOMPLETE')
            row['followup_review']=item['followup_review']
        row.update(status='VERIFIED', evidence=item['evidence']+[self.attach(report_path)], verifier=verifier)
        self.event('TASK_VERIFIED', task=task, verifier=verifier)

    def block_external(self, task, reasons):
        if task not in ('real_baseline','processing_feedback') or not reasons: raise ValueError('EXTERNAL_BLOCK_SCOPE')
        self.state['tasks'][task].update(status='BLOCKED_EXTERNAL', blockers=list(reasons))
        self.event('EXTERNAL_DEPENDENCY', task=task, reasons=list(reasons))

    def next_task(self):
        for issue in self.state['issues'].values():
            if issue['status']=='NEEDS_REPAIR': return {'kind':'B-Repair','issue_id':issue['issue_id']}
        for task, row in self.state['tasks'].items():
            if row['status'] in ('PENDING','AWAITING_REVIEW','AWAITING_REGRESSION') and all(
                    self.state['tasks'][d]['status']=='VERIFIED' for d in row['depends_on']):
                return {'kind':'task','task':task,'status':row['status']}
        return None

    def bind_code(self, code_sha, changed_paths=()):
        if self.state['inflight']: raise ValueError('INFLIGHT_OPERATION_DO_NOT_REBIND')
        if self.state['current_code_sha']==code_sha: return
        changed = set(changed_paths)
        for run in self.state['runs'].values():
            if run['status']=='RUNNING': run['status']='PAUSED_FOR_NEW_CODE'
            affected = [a for a in run['artifacts'].values() if changed.intersection(a['source_hashes'])]
            for artifact in affected:
                artifact['valid'] = False; artifact['invalid_reason'] = 'SOURCE_CHANGED_REBUILD_REQUIRED'
            if affected: run['status'] = 'STALE'
        if changed:
            for row in self.state['tasks'].values():
                if row['status']=='VERIFIED' and changed.intersection(e['path'] for e in row['evidence']):
                    row['status']='PENDING'
            for task, actions in TASK_ARTIFACTS.items():
                row=self.state['tasks'][task]
                run=self.state['runs'].get(row.get('run_id'),{})
                for action in actions:
                    target=run.get('artifacts',{}).get(action,{})
                    review=run.get('reviews',{}).get(action,{})
                    if changed.intersection(set(target.get('source_hashes',{}))|set(review.get('source_hashes',{}))):
                        row['status']='PENDING'
            self.invalidate_dependents()
        self.state['current_code_sha'] = code_sha
        self.event('CODE_BOUND', code_sha=code_sha, changed_paths=sorted(changed))

    def invalidate_dependents(self):
        # Finite DAG propagation. Historical artifacts remain on disk.
        for _ in TASKS:
            for row in self.state['tasks'].values():
                if row['status']=='VERIFIED' and any(self.state['tasks'][d]['status']!='VERIFIED' for d in row['depends_on']):
                    row['status']='PENDING'

    def start_run(self, run_id, policy, record_ids):
        if self.state['inflight']: raise ValueError('UNCERTAIN_OPERATION_DO_NOT_REPEAT')
        if run_id in self.state['runs']: raise ValueError('RUN_ALREADY_EXISTS_USE_RECOMPUTE_OR_NEW_RUN')
        if not self.state['current_code_sha']: raise ValueError('CODE_SHA_REQUIRED')
        if len(set(record_ids))!=len(record_ids): raise ValueError('DUPLICATE_RECORD_SCOPE')
        self.state['runs'][run_id] = {'status':'RUNNING','code_sha':self.state['current_code_sha'],
            'policy_hash':object_hash(policy),'input_sha256':policy['raw_sha256'],'record_ids':record_ids,
            'artifacts':{},'reviews':{},'mode':'RECOMPUTE','new_model_calls':0,
            'runtime_source_hashes':{str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'task1/workflow').glob('*.py')}}
        self.state['current_run']=run_id
        for task in TASK_ARTIFACTS:
            if self.state['tasks'][task]['status']=='VERIFIED': self.state['tasks'][task]['status']='PENDING'
        self.invalidate_dependents()
        self.event('RUN_STARTED',run_id=run_id)

    def execute(self, run_id, action, policy):
        run = self.state['runs'][run_id]
        if self.state['inflight']: raise ValueError('UNCERTAIN_OPERATION_DO_NOT_REPEAT')
        affected_tasks={'review_targets'} | ({'trusted_baseline'} if action=='baseline' else set())
        if any(i['status']!='VERIFIED' and i['parent_task'] in affected_tasks for i in self.state['issues'].values()):
            raise ValueError('OPEN_BLOCKING_ISSUE_REPAIR_BEFORE_PROCESSING')
        if (run['status']!='RUNNING' or run['code_sha']!=self.state['current_code_sha']
                or object_hash(policy)!=run['policy_hash']): raise ValueError('RUN_OR_CONTRACT_CHANGED')
        for path,sha in run['runtime_source_hashes'].items():
            if digest(ROOT/path)!=sha: raise ValueError('RUNTIME_CODE_CHANGED')
        if action not in COMPONENTS: raise ValueError('NON_ALLOWLISTED_TOOL')
        if action in run['artifacts']: raise ValueError('ALREADY_EXECUTED_DO_NOT_REPEAT')
        op = run_id+':'+action; self.state['inflight'] = {'id':op, 'kind':'tool', 'action':action}
        self.event('TOOL_DISPATCHED',operation=op)
        path = self.directory/'runs'/run_id/(action+'.json')
        if path.exists(): raise ValueError('UNREGISTERED_OUTPUT_DO_NOT_REPEAT')
        try:
            result = execute_tool(action,run['record_ids'],policy)
            for name,sha in run['runtime_source_hashes'].items():
                if digest(ROOT/name)!=sha: raise ValueError('RUNTIME_CODE_CHANGED')
            write_json(path,result,exclusive=True)
            source_names = ['io.py','tools.py','diagnostics.py'] + (['pipeline.py','geometry.py','evaluation.py'] if action=='baseline' else [])
            artifact = {**self.attach(path),'artifact_id':op,'output_sha256':object_hash(result),'action':action,'valid':True,
                        'source_hashes':{str((Path('task1/workflow')/name)):digest(ROOT/'task1/workflow'/name) for name in source_names}}
            run['artifacts'][action] = artifact; self.state['inflight'] = None
            self.event('TOOL_EXECUTED',operation=op,artifact=artifact)
            return result
        except (ValueError,KeyError,TypeError,OSError) as exc:
            run['status']='INTERRUPTED_CHECKPOINT'
            self.event('TOOL_FAILED_OUTCOME_REQUIRES_RECONCILIATION',operation=op,error=str(exc))
            raise

    def review(self, run_id, action, policy, requested_components=None):
        run=self.state['runs'][run_id]; artifact=run['artifacts'][action]
        if object_hash(policy)!=run['policy_hash'] or digest(DATA)!=run['input_sha256']: raise ValueError('REFERENCE_CHANGED')
        self.check_evidence([artifact])
        if not artifact['valid']: raise ValueError('STALE_ARTIFACT')
        for path,sha in artifact['source_hashes'].items():
            if digest(ROOT/path)!=sha: raise ValueError('CODE_CHANGED_REBUILD_REQUIRED')
        output=execute_tool(REVIEW_ACTIONS[action],run['record_ids'],policy,
                            target_artifact=read_json(ROOT/artifact['path']), target_binding=artifact,
                            requested_components=requested_components)
        review_path=self.directory/'runs'/run_id/(action+'_review.json')
        if review_path.exists(): raise ValueError('REVIEW_ALREADY_EXISTS')
        write_json(review_path,output,exclusive=True)
        run['reviews'][action]={**self.attach(review_path),'source_hashes':{
            'task1/workflow/artifact_review.py':digest(ROOT/'task1/workflow/artifact_review.py'),
            'task1/workflow/evaluation.py':digest(ROOT/'task1/workflow/evaluation.py')}}
        self.event('NUMERIC_REVIEW_EXECUTED',run_id=run_id,target=artifact['artifact_id'],status=output['status'])
        return output

    def coverage(self, run_id, required_actions=None):
        run=self.state['runs'][run_id]; missing=[]
        required_actions=list(run['artifacts']) if required_actions is None else required_actions
        for action in required_actions:
            target=run['artifacts'].get(action)
            if target is None: missing.append(action+':NOT_EXECUTED'); continue
            self.check_evidence([target]); self.check_evidence([run['reviews'][action]]) if action in run['reviews'] else None
            candidate=read_json(ROOT/target['path'])
            if candidate['status']=='BLOCKED': missing.append(action+':BLOCKED'); continue
            entry=run['reviews'].get(action)
            if not entry: missing.append(action+':UNREVIEWED'); continue
            r=read_json(ROOT/entry['path'])['result']
            source_ok=all(digest(ROOT/p)==sha for p,sha in {**target['source_hashes'],**entry['source_hashes']}.items())
            if (not source_ok or not target['valid'] or r['status']!='VERIFIED' or r['unchecked_components']
                    or r['target_artifact_id']!=target['artifact_id'] or r['target_artifact_hash']!=target['sha256']
                    or not set(COMPONENTS[action]).issubset(r['checked_components'])):
                missing.append(action+':INVALID_REVIEW')
        return {'status':'VERIFIED' if required_actions and not missing else 'NEEDS_REVIEW','missing':missing}

    def reconcile(self, run_id, action):
        """A crash after write is inspected; never automatically repeat a write/model."""
        pending=self.state['inflight']
        if not pending or pending['id']!=run_id+':'+action: raise ValueError('NO_MATCHING_PENDING_OPERATION')
        path=self.directory/'runs'/run_id/(action+'.json')
        self.event('RECOVERY_INSPECTION',operation=pending['id'],output_exists=path.exists(),automatic_retry=False)
        return {'status':'MANUAL_RECONCILIATION_REQUIRED','output_exists':path.exists(),'automatic_retry':False}

    def execute_followup(self, run_id, request_path):
        """A bounded next diagnostic chosen from actual baseline review evidence."""
        if self.state['inflight']: raise ValueError('UNCERTAIN_OPERATION_DO_NOT_REPEAT')
        run=self.state['runs'][run_id]
        if run_id!=self.state.get('current_run') or run['code_sha']!=self.state['current_code_sha']:
            raise ValueError('FOLLOWUP_CURRENT_CODE_REQUIRED')
        if 'followup' in run: raise ValueError('FOLLOWUP_ALREADY_EXECUTED')
        if self.coverage(run_id,['baseline'])['status']!='VERIFIED': raise ValueError('BASELINE_REVIEW_REQUIRED')
        request=read_json(request_path);target=run['artifacts']['baseline']
        if (request.get('action')!='coordinate_sensitivity' or not request.get('reason')
                or request.get('parent_artifact_id')!=target['artifact_id']
                or request.get('parent_sha256')!=target['sha256']): raise ValueError('FOLLOWUP_REQUEST_BINDING')
        self.check_evidence([run['reviews']['baseline']])
        self.state['inflight']={'id':run_id+':coordinate_sensitivity','kind':'tool'}
        self.event('FOLLOWUP_DISPATCHED',request=self.attach(request_path),review=run['reviews']['baseline'])
        from .coordinate_review import validate_coordinates
        raw=read_json(DATA);policy=read_json(CONFIG)
        if digest(DATA)!=run['input_sha256'] or object_hash(policy)!=run['policy_hash']:raise ValueError('FOLLOWUP_REFERENCE_CHANGED')
        result=validate_coordinates({i:raw[i] for i in run['record_ids']},read_json(ROOT/target['path']))
        result.update(parent_artifact_id=target['artifact_id'],parent_sha256=target['sha256'],
                      trigger_review=run['reviews']['baseline'],request=self.attach(request_path),code_sha=run['code_sha'])
        path=self.directory/'runs'/run_id/'coordinate_sensitivity.json'
        write_json(path,result,exclusive=True)
        run['followup']={**self.attach(path),'source_hashes':{
            'task1/workflow/coordinate_review.py':digest(ROOT/'task1/workflow/coordinate_review.py'),
            'task1/workflow/coordinates.py':digest(ROOT/'task1/workflow/coordinates.py'),
            'task1/workflow/evaluation.py':digest(ROOT/'task1/workflow/evaluation.py')}}
        self.state['inflight']=None;self.event('FOLLOWUP_EXECUTED',artifact=run['followup'])
        return result

    def finalize(self):
        for row in self.state['tasks'].values():
            if row['status']=='VERIFIED': self.check_evidence(row['evidence'])
        for task,actions in TASK_ARTIFACTS.items():
            row=self.state['tasks'][task]
            if row['status']=='VERIFIED':
                run_id=self.state.get('current_run')
                if not run_id or row.get('run_id')!=run_id or self.coverage(run_id,actions)['status']!='VERIFIED':
                    row['status']='PENDING'
                elif task=='processing_feedback':
                    f=self.state['runs'][run_id].get('followup')
                    if not f or not row.get('followup_review'): row['status']='PENDING'
                    else:
                        self.check_evidence([f,row['followup_review']])
                        if any(digest(ROOT/p)!=h for p,h in f['source_hashes'].items()): row['status']='PENDING'
        self.invalidate_dependents()
        statuses=[r['status'] for r in self.state['tasks'].values()]
        open_issues=any(i['status']!='VERIFIED' for i in self.state['issues'].values())
        if all(s=='VERIFIED' for s in statuses) and not open_issues:
            status='ENGINEERING_READY_FOR_GPT_REVIEW'
        elif all(s in ('VERIFIED','BLOCKED_EXTERNAL') for s in statuses) and not open_issues:
            status='BLOCKED_EXTERNAL'
        else: status='IMPLEMENTING'
        if self.state['inflight']: status='INTERRUPTED_CHECKPOINT'
        self.state['status']=status; self.event('GOAL_REEVALUATED',status=status)
        return status
