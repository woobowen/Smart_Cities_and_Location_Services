"""Offline recomputation from raw input and saved, validated live decisions."""
from pathlib import Path

from .io import ROOT,CONFIG,DATA,EVIDENCE,read_json,write_json,digest,object_hash,now,bound_path
from .tools import execute_tool
from .controller import validate_request,GateError


def recompute_run(run_id,output_path=None):
    directory=bound_path(EVIDENCE/'runs',run_id)
    manifest=read_json(directory/'manifest.json')
    policy=read_json(CONFIG);pilot=read_json(ROOT/'task1/config/pilot.json')
    if manifest['mode']!='LIVE':raise GateError('REPLAY_REQUIRES_SAVED_LIVE_RUN')
    if digest(DATA)!=manifest['input_sha256'] or digest(CONFIG)!=manifest['policy_sha256']:
        raise GateError('REPLAY_INPUT_OR_CONTRACT_MISMATCH')
    for path,sha in manifest['source_hashes'].items():
        if digest(ROOT/path)!=sha:raise GateError('REPLAY_CODE_CONTENT_MISMATCH:'+path)
    profiles=None;checks=[]
    for tool in manifest['tools']:
        path=bound_path(directory,tool['artifact'])
        if digest(path)!=tool['sha256']:raise GateError('REPLAY_ARTIFACT_HASH_MISMATCH')
        receipt=read_json(path);request=receipt['request']
        validate_request(request,receipt['role'],receipt['call_id'],policy,pilot,mode='REPLAY')
        output=execute_tool(request['action'],request['record_ids'],policy,profiles)
        expected=receipt['output_sha256'];actual=object_hash(output)
        checks.append({'tool_id':tool['tool_id'],'action':request['action'],'expected_sha256':expected,
                       'recomputed_sha256':actual,'equal':expected==actual})
        if request['action']=='profile_pilot':profiles=output['result']['profiles']
    result={'mode':'REPLAY_RECOMPUTE','new_model_calls':0,'source_live_run':run_id,
            'input_sha256':manifest['input_sha256'],'source_code_sha':manifest['code_sha'],
            'recomputed_at':now(),'checks':checks,'status':'VERIFIED' if checks and all(x['equal'] for x in checks) else 'REJECTED',
            'meaning':'Tools genuinely reran on the raw JSON; not a new model experiment or quality approval'}
    if output_path:write_json(output_path,result,exclusive=True)
    return result
