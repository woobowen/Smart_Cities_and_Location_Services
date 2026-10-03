"""Bounded Goal 1 dispatcher and resumable journal. This is not a fourth agent."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import time

import jsonschema

from .io import ROOT,CONFIG,EVIDENCE,DATA,read_json,write_json,digest,object_hash,now,bound_path,relative
from .provider import CodexProvider,ProviderError,response_schema,verify_saved_call
from .tools import execute_tool
from .sources import source_context, validate_references
from .pipeline import preflight
from .provider import redact

PHASES=[
    ('research','Inspect actual source excerpts, contract and initial diagnostics. Choose an allowed initial diagnostic or escalate insufficient evidence. Never approve unknown semantics.'),
    ('execution','Use the prior research request and current artifacts. Establish complete pilot profiles if absent; otherwise choose a justified diagnostic or approved baseline. Escalation is allowed.'),
    ('review','Review actual artifacts. Request independent numeric verification. Evidence insufficiency is valid; do not invent a defect.'),
    ('research','Use the current reviewer conclusion AND its verified numeric result. Choose a justified follow-up diagnostic/recheck or escalate. Cite all required_feedback IDs.'),
    ('review','Review the actual follow-up, cite required_feedback, run final independent verification or escalate. State the next task and distinguish diagnostic from processing closure.'),
]
# Broad per-stage upper bounds; available_actions further enforces prerequisites.
PHASE_ACTIONS=[['contract_snapshot','source_check','profile_pilot','time_boundaries','duplicate_details','escalate'],
               ['profile_pilot','time_boundaries','duplicate_details','baseline','escalate'],
               ['verify_profiles','recompute_check','verify_baseline','escalate'],
               ['duplicate_details','time_boundaries','recompute_check','source_check','escalate'],
               ['recompute_check','verify_profiles','verify_baseline','escalate']]


class GateError(ValueError):
    pass


def validate_request(request,role,call_id,policy,pilot,*,mode='LIVE',feedback_ids=(),context=None,run_id=None):
    jsonschema.validate(request,response_schema(role,call_id,policy['actions'][role]))
    if policy['goal']!=1 or policy['metrics_version']!='g1-metrics-v1' or policy['semantics_version']!='g1-semantics-v1':
        raise GateError('UNAPPROVED_GOAL_OR_CONTRACT_VERSION')
    if mode=='SEARCH_ONLY':
        raise GateError('LLM_FORBIDDEN_IN_SEARCH_ONLY')
    ids=request['record_ids']
    if len(ids)!=len(set(ids)) or not ids or len(ids)>policy['budget']['max_pilot_records'] or set(ids)!=set(pilot['ids']):
        raise GateError('RECORD_SCOPE_OR_HOLDOUT_VIOLATION')
    if not request['reason'].strip() or not request['evidence_refs']:
        raise GateError('MISSING_REASON_OR_SOURCE')
    if feedback_ids and not set(feedback_ids).issubset(request['feedback_refs']):
        raise GateError('MISSING_ACTUAL_FEEDBACK_REFERENCE')
    try:
        validate_references(request,context if context is not None else source_context(),
                            'RAW:'+policy['raw_sha256'],run_id,feedback_ids)
    except ValueError as exc: raise GateError(str(exc)) from exc
    if request['request_status']!='PROPOSED' and request['action']!='escalate':
        raise GateError('ROLE_REQUEST_REQUIRES_REVIEW:'+request['request_status'])
    if request['action']=='baseline' and preflight(policy):
        raise GateError('UNKNOWN_SEMANTICS_BASELINE_BLOCKED')
    return request


class Controller:
    def __init__(self,run_id,*,mode='LIVE',base=EVIDENCE/'runs',policy_path=CONFIG,pilot_path=ROOT/'task1/config/pilot.json',batch=None):
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,90}',run_id):
            raise GateError('ILLEGAL_RUN_ID')
        if mode not in ('LIVE','MOCK_TEST','REPLAY','SEARCH_ONLY'):
            raise GateError('UNKNOWN_MODE')
        self.batch=batch
        self.base=Path(base).resolve();self.base.mkdir(parents=True,exist_ok=True)
        self.directory=bound_path(self.base,run_id)
        if self.directory.is_symlink():raise GateError('SYMLINK_RUN')
        self.directory.mkdir(exist_ok=True)
        self.policy_path=Path(policy_path);self.pilot_path=Path(pilot_path)
        self.policy=read_json(policy_path);self.pilot=read_json(pilot_path)
        self.config_hash=digest(policy_path);self.pilot_hash=digest(pilot_path)
        self.mode=mode;self.run_id=run_id
        self.state_path=self.directory/'checkpoint.json'
        if self.state_path.exists():
            self.state=read_json(self.state_path)
            if self.state['mode']!=mode or self.state['policy_sha256']!=self.config_hash or self.state['pilot_sha256']!=self.pilot_hash:
                raise GateError('CHECKPOINT_CONTRACT_OR_MODE_MISMATCH')
        else:
            self.state={'run_id':run_id,'mode':mode,'status':'PLANNED','phase':0,'inflight_model':None,
                        'policy_sha256':self.config_hash,'pilot_sha256':self.pilot_hash,
                        'input_sha256':self.policy['raw_sha256'],'started_at':now(),
                        'code_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                        'source_hashes':{relative(p):digest(p) for p in [*sorted((ROOT/'task1/workflow').glob('*.py')),ROOT/'task1/config/goal1_sources.json']},
                        'tools':[],'calls':[],'model_dispatches':{},'decisions':[],'accepted_version':None,'errors':[]}
            self.save()
        self.ledger_path=(EVIDENCE/'runs'/'budget_live.json') if mode=='LIVE' else self.base/('budget_'+mode.lower()+'.json')
        if not self.ledger_path.exists():
            write_json(self.ledger_path,{'model_attempts':0,'tool_requests':0,'by_run':{},'retry_failures':{}},exclusive=True)

    def save(self):
        write_json(self.state_path,self.state)

    def event(self,kind,**fields):
        path=self.directory/'events.jsonl'
        previous='ROOT';number=0
        if path.exists():
            lines=path.read_text().splitlines()
            if lines:
                last=json.loads(lines[-1]);previous=last['event_hash'];number=last['sequence']+1
        e={'sequence':number,'at':now(),'kind':kind,'run_id':self.run_id,'previous_hash':previous,**fields}
        e['event_hash']=object_hash(e)
        with path.open('a') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
        return e['event_hash']

    def spend(self,kind,call_id=None):
        if self.mode=='LIVE' and self.batch is not None:
            self.batch.reserve(kind,self.run_id,call_id);return
        # Execution is serial by contract; budget persists across run IDs.
        ledger=read_json(self.ledger_path)
        if kind=='model_attempts' and ledger.get('live_stop'):
            raise GateError('LIVE_BUDGET_FROZEN:'+ledger['live_stop'])
        limit=self.policy['budget']['max_model_calls' if kind=='model_attempts' else 'max_tool_calls']
        if ledger[kind]>=limit:raise GateError('BUDGET_EXHAUSTED:'+kind)
        ledger[kind]+=1
        entry=ledger['by_run'].setdefault(self.run_id,{'model_attempts':0,'tool_requests':0})
        entry[kind]+=1
        if call_id:
            ledger.setdefault('dispatched_calls',{})[call_id]={'run_id':self.run_id,'at':now()}
        write_json(self.ledger_path,ledger)

    def protection_check(self):
        if digest(self.policy_path)!=self.config_hash or digest(self.pilot_path)!=self.pilot_hash:
            raise GateError('PROTECTED_CONTRACT_CHANGED')
        if digest(DATA)!=self.state['input_sha256']:
            raise GateError('INPUT_HASH_MISMATCH')
        for path,sha in self.state['source_hashes'].items():
            if digest(ROOT/path)!=sha:raise GateError('RUNTIME_CODE_CHANGED:'+path)

    def profiles(self):
        for tool in reversed(self.state['tools']):
            if tool['action']=='profile_pilot' and tool['status']=='EXECUTED':
                payload=self.read_tool(tool)
                return payload['output']['result']['profiles']
        return None

    def read_tool(self,tool):
        path=bound_path(self.directory,tool['artifact'])
        if not path.is_file():raise GateError('MISSING_OUTPUT')
        if digest(path)!=tool['sha256']:raise GateError('OUTPUT_FILE_HASH_MISMATCH')
        payload=read_json(path)
        if payload.get('tool_id')!=tool['tool_id'] or payload.get('request_hash')!=tool['tool_id'] or payload.get('run_id')!=self.run_id or payload.get('mode')!=self.mode:
            raise GateError('TOOL_RECEIPT_BINDING_MISMATCH')
        if object_hash(payload['output'])!=payload['output_sha256']:raise GateError('OUTPUT_HASH_MISMATCH')
        if payload['output'].get('parent_version')!='RAW:'+self.state['input_sha256']:
            raise GateError('WRONG_PARENT_VERSION')
        if payload['output'].get('input_sha256')!=self.state['input_sha256']:
            raise GateError('INPUT_HASH_MISMATCH')
        if payload['output'].get('status') not in ('EXECUTED','VERIFIED','REJECTED','BLOCKED','FAILED'):
            raise GateError('FORGED_SUCCESS_STATUS')
        if payload['output'].get('status')!=tool['status'] or payload['request'].get('action')!=tool['action']:
            raise GateError('TOOL_SUMMARY_MISMATCH')
        return payload

    def review_target(self, action, request):
        """Resolve actual registered bytes, never an ID/hash asserted by a model."""
        from .artifact_review import COMPONENTS
        explicit = {'verify_profiles':'profile_pilot', 'verify_time_boundaries':'time_boundaries',
                    'verify_duplicate_details':'duplicate_details', 'verify_baseline':'baseline'}
        if action not in (*explicit, 'recompute_check'): return None, None
        artifacts = [t for t in self.state['tools'] if t['action'] in COMPONENTS
                     and t['status'] in ('EXECUTED', 'VERIFIED')]
        if action in explicit: artifacts = [t for t in artifacts if t['action'] == explicit[action]]
        referenced = [t for t in artifacts if t['tool_id'] in request['evidence_refs']]
        if len(referenced) > 1: raise GateError('AMBIGUOUS_REVIEW_TARGET')
        target = referenced[0] if referenced else (artifacts[-1] if artifacts else None)
        if target is None: raise GateError('MISSING_REGISTERED_REVIEW_TARGET')
        receipt = self.read_tool(target)
        binding = {'artifact_id':target['tool_id'], 'sha256':target['sha256'],
                   'output_sha256':receipt['output_sha256'], 'action':target['action']}
        return receipt['output'], binding

    def artifact_coverage(self):
        from .artifact_review import COMPONENTS
        unchecked = []
        for target in self.state['tools']:
            if target['action'] not in COMPONENTS or target['status'] not in ('EXECUTED','VERIFIED'): continue
            self.read_tool(target)
            matched = False
            for review in self.state['tools']:
                r = self.read_tool(review)['output'].get('result', {})
                if (r.get('target_artifact_id') == target['tool_id']
                        and r.get('target_artifact_hash') == target['sha256']
                        and r.get('status') == 'VERIFIED' and not r.get('unchecked_components')
                        and set(COMPONENTS[target['action']]).issubset(r.get('checked_components', []))):
                    matched = True
            if not matched: unchecked.append(target['tool_id'])
        return {'status':'VERIFIED' if not unchecked else 'NEEDS_REVIEW', 'unchecked_artifact_ids':unchecked}

    def _dispatch(self,request,role,call_id,*,feedback_ids=(),inject_failure=False):
        self.protection_check()
        if self.state['phase']>=3:
            actual=self.required_feedback()
            if set(feedback_ids)!=set(actual):raise GateError('WRONG_CURRENT_FEEDBACK_TRIGGER')
        try:
            validate_request(request,role,call_id,self.policy,self.pilot,mode=self.mode,feedback_ids=feedback_ids,context=self.context(),run_id=self.run_id)
        except (ValueError,jsonschema.ValidationError) as exc:
            self.event('REQUEST_REJECTED',call_id=call_id,reason=str(exc))
            raise
        target, binding = self.review_target(request['action'], request)
        self.spend('tool_requests')
        key=object_hash({'call_id':call_id,'action':request['action'],'ids':request['record_ids'],'input':self.state['input_sha256'],
                         'contract':self.config_hash,'target':binding})
        artifact='tools/'+key+'.json'
        path=bound_path(self.directory,artifact)
        if path.exists():
            registered=next((t for t in self.state['tools'] if t['tool_id']==key),None)
            if registered is None:raise GateError('UNREGISTERED_CACHED_OUTPUT')
            receipt=self.read_tool(registered)
            self.event('TOOL_REUSED_NO_SIDE_EFFECT',call_id=call_id,artifact=artifact)
        else:
            self.state['status']='DISPATCHED';self.save()
            self.event('TOOL_DISPATCHED',call_id=call_id,action=request['action'],request_hash=key)
            start=time.perf_counter();self.state['status']='RUNNING';self.save()
            if inject_failure: raise GateError('INJECTED_FAILURE')
            output=execute_tool(request['action'],request['record_ids'],self.policy,self.profiles(),
                                classification='CURRENT_RUN_REAL_DATA' if self.mode=='LIVE' else self.mode,
                                previous_baseline=self.baseline_output(), target_artifact=target, target_binding=binding)
            self.protection_check()
            if output.get('status') not in ('EXECUTED','VERIFIED','REJECTED','BLOCKED','FAILED'):
                raise GateError('FORGED_SUCCESS_STATUS')
            receipt={'tool_id':key,'request_hash':key,'role':role,'call_id':call_id,'request':request,
                     'run_id':self.run_id,'mode':self.mode,'classification':'CURRENT_RUN_REAL_DATA' if self.mode=='LIVE' else self.mode,
                     'code_sha':self.state['code_sha'],'output':output,'output_sha256':object_hash(output),
                     'elapsed_seconds':time.perf_counter()-start,'completed_at':now()}
            write_json(path,receipt,exclusive=True)
            self.event('TOOL_EXECUTED',call_id=call_id,artifact=artifact,output_sha256=receipt['output_sha256'])
        summary={'tool_id':key,'artifact':artifact,'sha256':digest(path),'action':request['action'],
                 'call_id':call_id,'status':receipt['output']['status']}
        if not any(t['tool_id']==key for t in self.state['tools']):self.state['tools'].append(summary)
        self.state['status']=receipt['output']['status'];self.save()
        return receipt

    def terminate_failure(self, call_id, exc):
        failure={'run_id':self.run_id,'call_id':call_id,'reason':redact(str(exc)),
                 'error_type':type(exc).__name__,'classification':'ENGINEERING_TEST' if self.mode!='LIVE' else 'LIVE',
                 'status':'FAILED','ended_at':now(),'automatic_resubmission':False}
        self.state['status']='FAILED';self.state['ended_at']=failure['ended_at'];self.state['errors'].append(failure)
        if self.batch is not None:self.batch.freeze(failure['reason'])
        try:
            self.save();write_json(bound_path(self.directory,'failures/'+call_id+'.json'),failure)
            self.event('EXECUTION_FAILED',**{k:v for k,v in failure.items() if k!='run_id'})
            self.export_manifest()
        except OSError as disk:
            raise GateError('EVIDENCE_MISSING: failure checkpoint/manifest could not be saved; do not resend') from disk

    def dispatch(self, request, role, call_id, **kwargs):
        try:return self._dispatch(request,role,call_id,**kwargs)
        except (OSError,ValueError,TypeError,KeyError,ArithmeticError,RuntimeError) as exc:
            self.terminate_failure(call_id,exc);raise

    def baseline_output(self):
        for tool in reversed(self.state['tools']):
            if tool['action']=='baseline' and tool['status']=='VERIFIED':return self.read_tool(tool)['output']
        return None

    def context(self):
        context=source_context()
        if self.mode=='MOCK_TEST':
            context['CONSTRUCTED_FIXTURE']={'kind':'source','claim_status':'TEST_ONLY'}
        for tool in self.state['tools']:
            receipt=self.read_tool(tool)
            context[tool['tool_id']]={'kind':'tool','status':tool['status'],'action':tool['action'],
                                     'run_id':self.run_id,'parent_version':receipt['output']['parent_version']}
        for call in self.state['calls']:
            path=bound_path(self.directory,call['response'])
            dispatch=self.state['model_dispatches'].get(call['call_id'],{})
            expected=dispatch.get('artifact_hashes',{}).get('response.json')
            if expected is None or digest(path)!=expected:raise GateError('CALL_REFERENCE_HASH_MISMATCH')
            context[call['call_id']]={'kind':'review' if call['role']=='review' else 'call',
                                    'run_id':self.run_id,'parent_version':'RAW:'+self.state['input_sha256']}
        return context

    def required_feedback(self):
        if self.state['phase']<3:return []
        current=f"{self.run_id}-{self.state['phase']+1:02d}-{PHASES[self.state['phase']][0]}"
        prior=[c for c in self.state['calls'] if c['call_id']!=current]
        reviews=[c for c in prior if c['role']=='review']
        # Only the completed reviewer that triggered this follow-up, never the current reply.
        completed=[c for c in reviews if any(t['call_id']==c['call_id'] for t in self.state['tools'])]
        if not completed:raise GateError('MISSING_ACTUAL_REVIEW')
        reviewer=completed[-1]
        audits=[t for t in self.state['tools'] if t['call_id']==reviewer['call_id'] and t['status']=='VERIFIED']
        if not audits:raise GateError('MISSING_VERIFIED_REVIEW_TOOL')
        required=[reviewer['call_id'],audits[-1]['tool_id']]
        if self.state['phase']==4:
            required.extend([prior[-1]['call_id'],self.state['tools'][-1]['tool_id']])
        return list(dict.fromkeys(required))

    def available_actions(self):
        actions=[a for a in PHASE_ACTIONS[self.state['phase']] if a in self.policy['actions'][PHASES[self.state['phase']][0]]]
        if self.profiles() is None:
            actions=[a for a in actions if a not in ('verify_profiles','recompute_check')]
            if self.state['phase']==1:actions=[a for a in actions if a in ('profile_pilot','escalate','baseline')]
        if preflight(self.policy):actions=[a for a in actions if a!='baseline']
        if self.baseline_output() is None:actions=[a for a in actions if a!='verify_baseline']
        return actions

    def prompt(self,role,call_id,instruction):
        previous=[]
        for c in self.state['calls']:
            previous.append({'call_id':c['call_id'],'role':c['role'],'response':read_json(self.directory/c['response'])})
        tool_outputs=[]
        for t in self.state['tools']:
            receipt=self.read_tool(t)
            output=receipt['output']
            # Full point-level diagnostics are artifacts; model gets exact counts and a bounded preview.
            if t['action']=='duplicate_details':
                output=json.loads(json.dumps(output))
                for trajectory in output['result']['trajectories']:
                    trajectory['events_total']=len(trajectory['events'])
                    trajectory['events']=trajectory['events'][:8]
            tool_outputs.append({'tool_id':t['tool_id'],'action':t['action'],'output':output})
        inventory=read_json(EVIDENCE/'inventory/structure_summary.json')
        inventory.pop('dt_counts',None)
        payload={'task_id':self.policy['task_id'],'goal':1,'role':role,'call_id':call_id,'instruction':instruction,
                 'policy':self.policy,'pilot':self.pilot,'raw_structure':inventory,
                 'prior_calls':previous,'tool_receipts':tool_outputs,
                 'available_actions':self.available_actions(),'allowed_references':self.context(),
                 'required_feedback':self.required_feedback()}
        return ('You are one real, separately called role in the Experiment1 Goal1 controller. '
                'Return exactly the requested JSON schema. No terminal, file editing, browsing or spawning. '
                'Your structured action will be validated and executed by deterministic code. '
                'Cite only exact allowed_references IDs; never invent computed numbers, approvals or truth labels. '
                'Do not report hidden reasoning; provide only concise visible task rationale. '
                'All numeric facts must come from supplied actual tool receipts. '
                'record_ids should include the entire seven-record pilot so no difficult case is omitted. '
                'Unknown CRS and direction schedule block full baseline, not raw/time diagnostics. '
                'In phase3 and later reference actual earlier reviewer/tool feedback IDs.\n'+json.dumps(payload,ensure_ascii=False))

    def _run(self,provider=None,*,stop_after=None):
        if self.mode!='LIVE':raise GateError('LIVE_ENTRY_REQUIRES_LIVE_MODE')
        provider=provider or CodexProvider(self.policy['budget']['max_seconds_per_model_call'],
            **(self.batch.qualification['provider_pin'] if self.batch is not None else {}))
        if type(provider) is not CodexProvider:raise GateError('MOCK_CANNOT_BE_LIVE')
        if not self.policy.get('live_execution_enabled',False) and self.batch is None:raise GateError('LIVE_DISABLED_PENDING_BUDGET_REVIEW')
        self.protection_check()
        if self.state['inflight_model']:
            pending=self.state['inflight_model']
            response_path=self.directory/'calls'/pending/'response.json'
            receipt_path=self.directory/'calls'/pending/'receipt.json'
            if not response_path.exists() or not receipt_path.exists():
                raise GateError('UNCERTAIN_MODEL_CALL_DO_NOT_REPEAT')
        while self.state['phase']<len(PHASES):
            phase=self.state['phase'];role,instruction=PHASES[phase]
            actions=self.available_actions(); required_feedback=self.required_feedback()
            call_id=f'{self.run_id}-{phase+1:02d}-{role}'
            call_dir=self.directory/'calls'/call_id
            response_path=call_dir/'response.json'
            if response_path.exists():
                dispatch=self.state.get('model_dispatches',{}).get(call_id)
                ledger=read_json(self.ledger_path)
                if not dispatch or (ledger.get('dispatched_calls',{}).get(call_id,{}).get('run_id')!=self.run_id and self.batch is None):
                    raise GateError('UNDISPATCHED_MODEL_RESPONSE')
                value,receipt,hashes=verify_saved_call(call_dir,role,call_id,actions,dispatch['input_hash'])
                if dispatch.get('artifact_hashes') and dispatch['artifact_hashes']!=hashes:
                    raise GateError('MODEL_ARTIFACT_HASH_MISMATCH')
                dispatch['artifact_hashes']=hashes;self.save()
                self.event('MODEL_RESPONSE_RECOVERED',call_id=call_id)
            else:
                if call_dir.exists():raise GateError('PREEXISTING_OR_INCOMPLETE_CALL_DIRECTORY')
                prompt=self.prompt(role,call_id,instruction)
                saved_input={'role':role,'call_id':call_id,'prompt':prompt,'schema':response_schema(role,call_id,actions)}
                self.spend('model_attempts',call_id)
                self.state.setdefault('model_dispatches',{})[call_id]={'input_hash':object_hash(saved_input)}
                self.state['inflight_model']=call_id;self.state['status']='DISPATCHED';self.save()
                self.event('MODEL_DISPATCHED',role=role,call_id=call_id)
                try:
                    provider.call(role,call_id,prompt,actions,call_dir)
                    if self.batch is not None:self.batch.finish(call_id,read_json(call_dir/'receipt.json'))
                    value,receipt,hashes=verify_saved_call(call_dir,role,call_id,actions,object_hash(saved_input))
                    self.state['model_dispatches'][call_id]['artifact_hashes']=hashes;self.save()
                except ProviderError as exc:
                    if self.batch is not None:
                        if (call_dir/'receipt.json').exists():self.batch.finish(call_id,read_json(call_dir/'receipt.json'))
                        else:self.batch.freeze('MISSING_RECEIPT')
                    self.state['status']='BLOCKED';self.state['ended_at']=now();self.state['errors'].append({'call_id':call_id,'reason':str(exc)})
                    self.save();self.event('LIVE_AGENT_BLOCKED',call_id=call_id,reason=str(exc));raise
            if not any(c['call_id']==call_id for c in self.state['calls']):
                self.state['calls'].append({'call_id':call_id,'role':role,'thread_id':receipt.get('thread_id','unavailable'),
                                           'response':str(response_path.relative_to(self.directory))})
            try:
                tool=self.dispatch(value,role,call_id,feedback_ids=required_feedback)
            except (ValueError,jsonschema.ValidationError) as exc:
                self.state['status']='NEEDS_REVIEW';self.state['ended_at']=now();self.state['errors'].append({'call_id':call_id,'reason':str(exc)})
                self.state['inflight_model']=None;self.save();raise
            if tool['output']['status'] not in ('EXECUTED','VERIFIED'):
                self.state['status']=tool['output']['status'];self.state['ended_at']=now()
                self.state['inflight_model']=None;self.save()
                self.event('BRANCH_STOPPED',call_id=call_id,status=self.state['status'])
                self.export_manifest();return self.state
            decision={'decision_id':call_id+'-decision','trigger_call':call_id,'trigger_tool':tool['tool_id'],
                      'status':'NEEDS_REVIEW','reason':'Executed '+value['action']+'; quality acceptance requires research review',
                      'quality_acceptance':'PENDING_RESEARCH_REVIEW','next_task':value['candidate_for_future_review'] or value['summary']}
            self.state['decisions'].append(decision)
            self.state['phase']+=1;self.state['inflight_model']=None;self.state['status']='VERIFIED';self.save()
            self.event('FEEDBACK_HANDOFF',decision=decision,next_phase=self.state['phase'])
            if stop_after is not None and self.state['phase']>=stop_after:return self.state
        coverage = self.artifact_coverage()
        self.state.update(status='FRAGMENT_COMPLETE' if coverage['status']=='VERIFIED' else 'NEEDS_REVIEW',ended_at=now(),
                          diagnostic_loop_status='REAL_DIAGNOSTIC_LOOP' if self.state['phase']==5 and self.baseline_output() is None else 'NOT_APPLICABLE',
                          artifact_coverage=coverage, goal1_complete=False,
                          real_baseline_status='AWAITING_INDEPENDENT_REVIEW' if self.baseline_output() else ('BLOCKED' if preflight(self.policy) else 'NOT_RUN'),gpt_second_review='PENDING')
        self.save();self.export_manifest()
        return self.state

    def run(self, provider=None, *, stop_after=None):
        try:return self._run(provider,stop_after=stop_after)
        except (OSError,ValueError,TypeError,KeyError,ArithmeticError,RuntimeError,KeyboardInterrupt) as exc:
            self.terminate_failure(self.state.get('inflight_model') or self.run_id+'-control',exc);raise
        finally:
            try:self.export_manifest()
            except OSError as exc:raise GateError('EVIDENCE_MISSING: manifest could not be saved; do not resend') from exc

    def export_manifest(self):
        files={str(p.relative_to(self.directory)):digest(p) for p in sorted(self.directory.rglob('*')) if p.is_file() and p.name!='manifest.json'}
        write_json(self.directory/'manifest.json',{'run_id':self.run_id,'mode':self.mode,'code_sha':self.state['code_sha'],
                   'source_hashes':self.state['source_hashes'],'input_sha256':self.state['input_sha256'],
                   'pilot':self.pilot,'policy_sha256':self.config_hash,'semantics_version':self.policy['semantics_version'],
                   'metrics_version':self.policy['metrics_version'],'status':self.state['status'],
                   'started_at':self.state['started_at'],'ended_at':self.state.get('ended_at'),
                   'diagnostic_loop_status':self.state.get('diagnostic_loop_status','NOT_COMPLETE'),
                   'real_baseline_status':self.state.get('real_baseline_status','BLOCKED' if preflight(self.policy) else 'NOT_RUN'),
                   'calls':self.state['calls'],'tools':self.state['tools'],'errors':self.state['errors'],'artifacts':files})
        return files
