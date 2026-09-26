"""Offline verification of saved LIVE artifacts; does not dispatch a model."""
from pathlib import Path
import sys,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists());sys.path.insert(0,str(ROOT))
from task1.workflow.io import read_json,write_json,digest,object_hash,DATA,CONFIG,bound_path,relative
from task1.workflow.provider import verify_saved_call,transport_counts
from task1.workflow.controller import validate_request
from task1.workflow.budget import REVISION,LEDGER,OLD
from task1.scripts.repair_goal1 import versions

base=REVISION/'runs/g1-repair-roles-01';manifest=read_json(base/'manifest.json');checks=[]
for name,sha in manifest['artifacts'].items():assert digest(bound_path(base,name))==sha
for name,sha in manifest['source_hashes'].items():assert digest(ROOT/name)==sha
policy=read_json(CONFIG);pilot=manifest['pilot'];raw=read_json(DATA)
assert digest(DATA)==manifest['input_sha256'] and digest(CONFIG)==manifest['policy_sha256']
for call in manifest['calls']:
 directory=base/'calls'/call['call_id'];saved=read_json(directory/'input.json');actions=saved['schema']['properties']['action']['enum']
 response,receipt,hashes=verify_saved_call(directory,call['role'],call['call_id'],actions,object_hash(saved))
 context=json.loads(saved['prompt'].split('\n',1)[1])
 validate_request(response,call['role'],call['call_id'],policy,pilot,context=context['allowed_references'],run_id=manifest['run_id'],feedback_ids=context['required_feedback'])
 checks.append({'call_id':call['call_id'],'role':call['role'],'action':response['action'],'feedback_refs':response['feedback_refs'],'required_feedback':context['required_feedback'],'status':'VERIFIED','receipt_sha256':digest(directory/'receipt.json')})
previous='ROOT'
for line in (base/'events.jsonl').read_text().splitlines():
 event=json.loads(line);sha=event.pop('event_hash');assert sha==object_hash(event) and event['previous_hash']==previous;previous=sha
numeric=[]
for tool in manifest['tools']:
 r=read_json(base/tool['artifact']);assert object_hash(r['output'])==r['output_sha256']
 output=r['output'];action=tool['action']
 if action=='time_boundaries':
  for row in output['result']['trajectories']:
   t,xy=raw[row['record_id']];cuts=[i for i in range(1,len(t)) if t[i]-t[i-1]>30 or t[i]<t[i-1]]
   assert [e['right_index'] for e in row['cuts']]==cuts
   bounds=[0]+cuts+[len(t)];assert row['partitions']==[list(range(a,b)) for a,b in zip(bounds,bounds[1:]) if a<b]
 elif action=='duplicate_details':
  for row in output['result']['trajectories']:
   t,xy=raw[row['record_id']];expected=[]
   for i in range(1,len(t)):
    tags=[]
    if xy[i]==xy[i-1]:tags.append('REPEATED_POSITION_NOT_AUTOMATIC_NOISE')
    if t[i]==t[i-1]:
     tags.append('ZERO_DT_SPEED_UNAVAILABLE')
     if xy[i]!=xy[i-1]:tags.append('SAME_TIME_DIFFERENT_POSITION')
    if tags:expected.append({'left_index':i-1,'right_index':i,'dt_raw':t[i]-t[i-1],'dt_reason':None,'position_pair_computable':True,'reasons':tags})
   assert row['events']==expected
 numeric.append({'tool_id':tool['tool_id'],'action':action,'status':output['status'],'hash_valid':True,'extra_direct_check':action in ('time_boundaries','duplicate_details')})
ledger=read_json(LEDGER);receipts=[]
for call,item in ledger['calls'].items():
 p=REVISION/'runs'/item['run_id']/'calls'/call/'receipt.json';r=read_json(p)
 receipts.append({'call_id':call,'probe':item['probe'],'process_started':r.get('process_started'),'completed_turns':r.get('completed_turns',0),'valid_response':r['status']=='VERIFIED_STRUCTURE_ONLY','status':r['status'],'elapsed_seconds':r['elapsed_seconds'],'visible_counts':r['visible_counts'],'receipt':relative(p)})
counts={'budget_reservations':ledger['model_attempts'],'processes_started':sum(r['process_started'] is True for r in receipts),'completed_turns':sum(r['completed_turns'] for r in receipts),'valid_structured_responses':sum(r['valid_response'] for r in receipts),'role_calls':sum(not r['probe'] for r in receipts),'tool_requests':ledger['tool_requests'],'actual_tools_executed':len(manifest['tools']),'underlying_requests':'unknown'}
for key in ('reconnect_notifications','fallback_notifications','sampling_retry_lines'):counts[key]=sum(r['visible_counts'][key] for r in receipts)
old=read_json(OLD);old_stderr=read_json(ROOT/'task1/evidence/goal1/runs/g1-live-20260926-03/calls/g1-live-20260926-03-02-execution/receipt.json')['stderr']
write_json(REVISION/'live_audit.json',{**versions(),'classification':'OFFLINE_AUDIT_OF_ACTUAL_LIVE_ARTIFACTS','new_model_calls_by_audit':0,'manifest_status':manifest['status'],'diagnostic_loop':manifest['diagnostic_loop_status'],'real_baseline':manifest['real_baseline_status'],'checks':checks,'tools':numeric,'counts':counts,'receipts':receipts,'historical_budget':{'outer_dispatches':old['model_attempts'],'reconnect_notifications':9,'fallback_notifications':1,'sampling_retry_lines':sum('sampling' in line and 'retry' in line for line in old_stderr.splitlines()),'underlying_requests':'unknown','historical_status':'FAIL_ON_RUN03'},'status':'PASS'})
print(json.dumps(counts,ensure_ascii=False))
