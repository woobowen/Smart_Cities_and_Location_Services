"""One explicitly authorized repair batch, cumulative across all run directories."""
import xml.etree.ElementTree as ET
from .io import ROOT, EVIDENCE, read_json, write_json, digest, bound_path, now

TASK='SC-LAB1-G1-REPAIR-001'
REVISION=EVIDENCE/'revisions'/TASK
AUTH=REVISION/'live_qualification.json'
LEDGER=EVIDENCE/'runs'/'budget_repair_001.json'
OLD=EVIDENCE/'runs'/'budget_live.json'


class RepairBudget:
    def __init__(self):
        qualification=read_json(AUTH)
        if qualification['task_id']!=TASK:raise ValueError('BATCH_AUTHORIZATION_MISMATCH')
        for name,sha in qualification['required_files'].items():
            if digest(bound_path(ROOT,name))!=sha:raise ValueError('BATCH_QUALIFICATION_CHANGED:'+name)
        log=bound_path(ROOT,qualification['test_report'])
        suites=ET.parse(log).getroot().findall('testsuite')
        if not suites or sum(int(s.get('tests',0)) for s in suites)<1 or any(int(s.get(k,0)) for s in suites for k in ('failures','errors')):
            raise ValueError('OFFLINE_GATES_NOT_PASSED')
        if digest(OLD)!=qualification['old_ledger_sha256']:raise ValueError('HISTORICAL_LEDGER_CHANGED')
        self.qualification=qualification
        if not LEDGER.exists():
            write_json(LEDGER,{'batch':TASK,'authorization_sha256':digest(AUTH),'old_ledger_sha256':digest(OLD),
                              'old_model_attempts':read_json(OLD)['model_attempts'],'model_attempts':0,
                              'tool_requests':0,'probe_passed':False,'calls':{},'live_stop':None},exclusive=True)
        if read_json(LEDGER)['authorization_sha256']!=digest(AUTH):raise ValueError('BATCH_ALREADY_BOUND')

    def reserve(self, kind, run_id, call_id=None, *, probe=False):
        state=read_json(LEDGER)
        if state['live_stop']:raise ValueError('LIVE_BUDGET_FROZEN:'+state['live_stop'])
        limit=6 if kind=='model_attempts' else 12
        if state[kind]>=limit:raise ValueError('BUDGET_EXHAUSTED:'+kind)
        if kind=='model_attempts':
            if call_id in state['calls']:raise ValueError('CALL_ALREADY_RESERVED_DO_NOT_RESEND')
            if probe and state['model_attempts']!=0:raise ValueError('ONLY_ONE_INITIAL_PROBE')
            if not probe and not state['probe_passed']:raise ValueError('PROBE_NOT_PASSED')
            state['calls'][call_id]={'run_id':run_id,'reserved_at':now(),'probe':probe,'status':'RESERVED_OUTCOME_UNKNOWN'}
        state[kind]+=1;write_json(LEDGER,state)

    def finish(self, call_id, receipt):
        state=read_json(LEDGER);call=state['calls'][call_id]
        call.update(status=receipt['status'],process_started=receipt.get('process_started','unknown'),
                    completed_turns=receipt.get('completed_turns',0),visible_counts=receipt.get('visible_counts',{}))
        ok=receipt['status']=='VERIFIED_STRUCTURE_ONLY'
        if call['probe']:state['probe_passed']=ok
        if not ok:state['live_stop']=receipt.get('error','UNKNOWN_CALL_OUTCOME')
        write_json(LEDGER,state)

    def freeze(self, reason):
        state=read_json(LEDGER);state['live_stop']=reason;write_json(LEDGER,state)
