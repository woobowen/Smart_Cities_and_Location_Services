"""Real local PermissionError and malformed-data paths; no model or network."""
import sys
from pathlib import Path
import tempfile
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists());sys.path.insert(0,str(ROOT))
from task1.workflow import tools,controller
from task1.workflow.provider import CodexProvider,ProviderError
from task1.workflow.io import write_json,read_json,digest,CONFIG
from task1.scripts.repair_goal1 import versions
out=Path(__file__).parent;results=[]
with tempfile.TemporaryDirectory(prefix='sc-g1-actual-failure-') as temp:
 p=Path(temp);executable=p/'not-executable';executable.write_text('#!/bin/sh\nexit 0\n');executable.chmod(0o600)
 provider=CodexProvider(executable=str(executable))
 try:provider.call('research','permission','fixture',['source_check'],p/'run/calls/permission')
 except ProviderError:
  receipt=read_json(p/'run/calls/permission/receipt.json')
  assert receipt['error_type']=='PermissionError' and not receipt['process_started']
  results.append({'case':'ACTUAL_OS_PERMISSION_ERROR','receipt':receipt})
 else:raise AssertionError('permission failure incorrectly succeeded')
 raw=p/'raw.json';write_json(raw,{'fixture':None});policy=read_json(CONFIG);policy['raw_sha256']=digest(raw)
 write_json(p/'policy.json',policy);write_json(p/'pilot.json',{'ids':['fixture']})
 with patch.object(tools,'DATA',raw),patch.object(controller,'DATA',raw):
  runner=controller.Controller('actual-data-error',mode='MOCK_TEST',base=p/'runs',policy_path=p/'policy.json',pilot_path=p/'pilot.json')
  request={'role':'execution','call_id':'invalid-data','action':'profile_pilot','record_ids':['fixture'],'feedback_refs':[],'evidence_refs':['CONSTRUCTED_FIXTURE'],'summary':'actual malformed data','reason':'Exercise numeric tool exception','request_status':'PROPOSED','candidate_for_future_review':None}
  try:runner.dispatch(request,'execution','invalid-data')
  except TypeError:
   manifest=read_json(runner.directory/'manifest.json');assert manifest['status']=='FAILED'
   results.append({'case':'ACTUAL_MALFORMED_INPUT_TOOL_FAILURE','failure':read_json(runner.directory/'failures/invalid-data.json'),'manifest_status':manifest['status']})
  else:raise AssertionError('malformed tool input incorrectly succeeded')
write_json(out/'actual_failure_probes.json',{**versions(),'classification':'ENGINEERING_TEST','model_calls':0,'network_calls':0,'results':results,'status':'PASS'})
print('actual OS / data exception paths PASS')
