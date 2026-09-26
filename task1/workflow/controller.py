"""Bounded Goal 1 dispatcher and resumable journal. This is not a fourth agent."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import time

import jsonschema

from .io import ROOT,CONFIG,EVIDENCE,DATA,read_json,write_json,digest,object_hash,now,bound_path,relative
from .provider import CodexProvider,ProviderError,response_schema
from .tools import execute_tool

PHASES=[
    ('research','Initial TaskPlan: inspect the supplied requirements, semantics and actual raw diagnostics. Request source_evidence to check the semantic blockers and state an in-scope plan for the execution role, with sources and limitations. Do not approve unknown semantics.'),
    ('execution','Execute the approved diagnostic scope. Request profile_pilot now to establish the required complete numeric input for the independent reviewer. Other tools require this prerequisite. Real full baseline is currently blocked.'),
    ('review','Review actual tool receipts. Request verify_profiles (independent deterministic audit) and identify one concrete diagnostic gap to feed back. Distinguish implementation from quality.'),
    ('research','You now have actual reviewer feedback and independent tool results. Refer to their exact IDs in feedback_refs. Choose a justified follow-up: duplicate_details, time_boundaries or recompute_check, or flag a research escalation. Do not merely repeat the previous task.'),
    ('review','Review the executed follow-up and the earlier independent audit. Request recompute_check or verify_profiles for final reproducibility. State what remains blocked and a concrete next research task; no quality upgrade without thresholds.'),
]
PHASE_ACTIONS=[['source_evidence'],['profile_pilot'],['verify_profiles'],
               ['duplicate_details','time_boundaries','recompute_check'],['recompute_check','verify_profiles']]


class GateError(ValueError):
    pass


def validate_request(request,role,call_id,policy,pilot,*,mode='LIVE',feedback_ids=()):
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
    if feedback_ids and not set(request['feedback_refs']).intersection(feedback_ids):
        raise GateError('MISSING_ACTUAL_FEEDBACK_REFERENCE')
    if request['action']=='baseline' and policy['method']['processing_status']!='APPROVED_FOR_REAL_INPUT':
        raise GateError('UNKNOWN_SEMANTICS_BASELINE_BLOCKED')
    return request


class Controller:
    def __init__(self,run_id,*,mode='LIVE',base=EVIDENCE/'runs',policy_path=CONFIG,pilot_path=ROOT/'task1/config/pilot.json'):
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,90}',run_id):
            raise GateError('ILLEGAL_RUN_ID')
        if mode not in ('LIVE','MOCK_TEST','REPLAY','SEARCH_ONLY'):
            raise GateError('UNKNOWN_MODE')
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
                        'source_hashes':{relative(p):digest(p) for p in sorted((ROOT/'task1/workflow').glob('*.py'))},
                        'tools':[],'calls':[],'decisions':[],'accepted_version':None,'errors':[]}
            self.save()
        self.ledger_path=self.base/('budget_live.json' if mode=='LIVE' else 'budget_'+mode.lower()+'.json')
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

    def spend(self,kind):
        # Execution is serial by contract; budget persists across run IDs.
        ledger=read_json(self.ledger_path)
        limit=self.policy['budget']['max_model_calls' if kind=='model_attempts' else 'max_tool_calls']
        if ledger[kind]>=limit:raise GateError('BUDGET_EXHAUSTED:'+kind)
        ledger[kind]+=1
        entry=ledger['by_run'].setdefault(self.run_id,{'model_attempts':0,'tool_requests':0})
        entry[kind]+=1
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
        if object_hash(payload['output'])!=payload['output_sha256']:raise GateError('OUTPUT_HASH_MISMATCH')
        if payload['output'].get('parent_version')!='RAW:'+self.state['input_sha256']:
            raise GateError('WRONG_PARENT_VERSION')
        if payload['output'].get('input_sha256')!=self.state['input_sha256']:
            raise GateError('INPUT_HASH_MISMATCH')
        if payload['output'].get('status') not in ('EXECUTED','VERIFIED','REJECTED','BLOCKED'):
            raise GateError('FORGED_SUCCESS_STATUS')
        return payload

    def dispatch(self,request,role,call_id,*,feedback_ids=(),inject_failure=False):
        self.protection_check()
        try:
            validate_request(request,role,call_id,self.policy,self.pilot,mode=self.mode,feedback_ids=feedback_ids)
        except (ValueError,jsonschema.ValidationError) as exc:
            self.event('REQUEST_REJECTED',call_id=call_id,reason=str(exc))
            raise
        self.spend('tool_requests')
        key=object_hash({'action':request['action'],'ids':request['record_ids'],'input':self.state['input_sha256'],
                         'contract':self.config_hash,'profiles':self.profiles() if request['action'] in ('verify_profiles','recompute_check') else None})
        artifact='tools/'+key+'.json'
        path=bound_path(self.directory,artifact)
        if path.exists():
            receipt=read_json(path)
            if receipt['request_hash']!=key or receipt['output_sha256']!=object_hash(receipt['output']):
                raise GateError('OUTPUT_HASH_MISMATCH')
            self.event('TOOL_REUSED_NO_SIDE_EFFECT',call_id=call_id,artifact=artifact)
        else:
            self.state['status']='DISPATCHED';self.save()
            self.event('TOOL_DISPATCHED',call_id=call_id,action=request['action'],request_hash=key)
            start=time.perf_counter();self.state['status']='RUNNING';self.save()
            if inject_failure:
                self.state['errors'].append({'call_id':call_id,'reason':'INJECTED_FAILURE','classification':'ENGINEERING_TEST'})
                self.state['status']='REJECTED';self.save()
                self.event('TOOL_FAILED',call_id=call_id,reason='INJECTED_FAILURE',classification='ENGINEERING_TEST')
                raise GateError('INJECTED_FAILURE')
            output=execute_tool(request['action'],request['record_ids'],self.policy,self.profiles(),
                                classification='CURRENT_RUN_REAL_DATA' if self.mode=='LIVE' else self.mode)
            self.protection_check()
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
                 'available_actions':PHASE_ACTIONS[self.state['phase']]}
        return ('You are one real, separately called role in the Experiment1 Goal1 controller. '
                'Return exactly the requested JSON schema. No terminal, file editing, browsing or spawning. '
                'Your structured action will be validated and executed by deterministic code. '
                'Cite source paths or prior call/tool IDs; never invent computed numbers, approvals or truth labels. '
                'Do not report hidden reasoning; provide only concise visible task rationale. '
                'All numeric facts must come from supplied actual tool receipts. '
                'record_ids should include the entire seven-record pilot so no difficult case is omitted. '
                'Unknown CRS and direction schedule block full baseline, not raw/time diagnostics. '
                'In phase3 and later reference actual earlier reviewer/tool feedback IDs.\n'+json.dumps(payload,ensure_ascii=False))

    def run(self,provider=None,*,stop_after=None):
        if self.mode!='LIVE':raise GateError('LIVE_ENTRY_REQUIRES_LIVE_MODE')
        provider=provider or CodexProvider(self.policy['budget']['max_seconds_per_model_call'])
        if type(provider) is not CodexProvider:raise GateError('MOCK_CANNOT_BE_LIVE')
        self.protection_check()
        if self.state['inflight_model']:
            pending=self.state['inflight_model']
            response_path=self.directory/'calls'/pending/'response.json'
            receipt_path=self.directory/'calls'/pending/'receipt.json'
            if not response_path.exists() or not receipt_path.exists():
                raise GateError('UNCERTAIN_MODEL_CALL_DO_NOT_REPEAT')
        while self.state['phase']<len(PHASES):
            phase=self.state['phase'];role,instruction=PHASES[phase]
            call_id=f'{self.run_id}-{phase+1:02d}-{role}'
            call_dir=self.directory/'calls'/call_id
            response_path=call_dir/'response.json'
            if response_path.exists():
                value=read_json(response_path);receipt=read_json(call_dir/'receipt.json')
                self.event('MODEL_RESPONSE_RECOVERED',call_id=call_id)
            else:
                self.spend('model_attempts')
                self.state['inflight_model']=call_id;self.state['status']='DISPATCHED';self.save()
                self.event('MODEL_DISPATCHED',role=role,call_id=call_id)
                try:
                    value,receipt=provider.call(role,call_id,self.prompt(role,call_id,instruction),PHASE_ACTIONS[phase],call_dir)
                except ProviderError as exc:
                    self.state['status']='BLOCKED';self.state['errors'].append({'call_id':call_id,'reason':str(exc)})
                    self.save();self.event('LIVE_AGENT_BLOCKED',call_id=call_id,reason=str(exc));raise
            if not any(c['call_id']==call_id for c in self.state['calls']):
                self.state['calls'].append({'call_id':call_id,'role':role,'thread_id':receipt.get('thread_id','unavailable'),
                                           'response':str(response_path.relative_to(self.directory))})
            feedback_ids=[c['call_id'] for c in self.state['calls'][:-1] if c['role']=='review']+[t['tool_id'] for t in self.state['tools']]
            try:
                tool=self.dispatch(value,role,call_id,feedback_ids=feedback_ids if phase>=3 else ())
            except (ValueError,jsonschema.ValidationError) as exc:
                self.state['status']='NEEDS_REVIEW';self.state['errors'].append({'call_id':call_id,'reason':str(exc)})
                self.state['inflight_model']=None;self.save();raise
            decision={'decision_id':call_id+'-decision','trigger_call':call_id,'trigger_tool':tool['tool_id'],
                      'status':'NEEDS_REVIEW','reason':'Engineering diagnostics executed; real baseline semantic blockers and quality thresholds unresolved',
                      'quality_acceptance':'PENDING_RESEARCH_REVIEW','next_task':value['candidate_for_future_review'] or value['summary']}
            self.state['decisions'].append(decision)
            self.state['phase']+=1;self.state['inflight_model']=None;self.state['status']='VERIFIED';self.save()
            self.event('FEEDBACK_HANDOFF',decision=decision,next_phase=self.state['phase'])
            if stop_after is not None and self.state['phase']>=stop_after:return self.state
        self.state.update(status='NEEDS_REVIEW',ended_at=now(),real_baseline_status='BLOCKED',gpt_second_review='PENDING')
        self.save();self.export_manifest()
        return self.state

    def export_manifest(self):
        files={str(p.relative_to(self.directory)):digest(p) for p in sorted(self.directory.rglob('*')) if p.is_file() and p.name!='manifest.json'}
        write_json(self.directory/'manifest.json',{'run_id':self.run_id,'mode':self.mode,'code_sha':self.state['code_sha'],
                   'source_hashes':self.state['source_hashes'],'input_sha256':self.state['input_sha256'],
                   'pilot':self.pilot,'policy_sha256':self.config_hash,'semantics_version':self.policy['semantics_version'],
                   'metrics_version':self.policy['metrics_version'],'status':self.state['status'],
                   'started_at':self.state['started_at'],'ended_at':self.state.get('ended_at'),
                   'calls':self.state['calls'],'tools':self.state['tools'],'errors':self.state['errors'],'artifacts':files})
        return files
