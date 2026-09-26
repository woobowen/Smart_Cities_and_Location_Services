"""Reproduce this repair's bounded diagnostics, validation and one authorized batch."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from task1.workflow.io import CONFIG,DATA,EVIDENCE,read_json,write_json,digest,relative,now,object_hash
from task1.workflow.tools import execute_tool
from task1.workflow.budget import RepairBudget, REVISION, AUTH, OLD, LEDGER, TASK
from task1.workflow.provider import CodexProvider,ProviderError
from task1.workflow.controller import Controller


def versions():
    return {'code_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_hashes':{relative(p):digest(p) for pattern in ('task1/workflow/*.py','task1/scripts/*.py','task1/tests/*.py','task1/config/*.json') for p in sorted(ROOT.glob(pattern))},
            'input_sha256':digest(DATA),'at':now()}


def validate():
    commands=[([sys.executable,'-m','compileall','-q','task1/workflow','task1/scripts','task1/tests'],ROOT,'syntax'),
              ([sys.executable,'-m','pytest','task1/tests','-q','--junitxml='+str(REVISION/'tests_final.xml')],ROOT,'tests_final'),
              ([sys.executable,'-m','pytest','tests','-q','-rs','--junitxml='+str(REVISION/'starter_full.xml')],ROOT/'task1/作业/作业','starter_full')]
    log=[]
    for args,cwd,name in commands:
        with (REVISION/(name+'.txt')).open('w') as f:r=subprocess.run(args,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
        log.append({'args':[x.replace(str(ROOT),'<REPO>') for x in args],'cwd':str(cwd.relative_to(ROOT)), 'exit_code':r.returncode,'log':name+'.txt'})
        write_json(REVISION/'validation.json',{**versions(),'commands':log})
        print(name,r.returncode,flush=True)
        if r.returncode:raise RuntimeError('VALIDATION_FAILED:'+name)


def diagnostics():
    policy=read_json(CONFIG);pilot=read_json(ROOT/'task1/config/pilot.json');out=REVISION/'results'
    out.mkdir(exist_ok=True)
    outputs={};rows=None
    for action in ('profile_pilot','verify_profiles','recompute_check','time_boundaries','duplicate_details','baseline','source_check'):
        outputs[action]=execute_tool(action,pilot['ids'],policy,rows)
        if action=='profile_pilot':rows=outputs[action]['result']['profiles']
        write_json(out/(action+'.json'),outputs[action])
    assert outputs['verify_profiles']['status']==outputs['recompute_check']['status']=='VERIFIED'
    raw=read_json(DATA)
    with (out/'point_actions.jsonl').open('w') as f:
        for rid in pilot['ids']:
            for i in range(len(raw[rid][1])):
                f.write(json.dumps({'record_id':rid,'original_index':i,'action':'PRESERVE_UNPROCESSED',
                                    'classification':'CURRENT_RUN_REAL_DATA_DIAGNOSTIC','parent_version':'RAW:'+policy['raw_sha256'],
                                    'deleted':False,'modified_values':0,'reason':outputs['baseline'].get('reason')},ensure_ascii=False)+'\n')
    write_json(out/'manifest.json',{**versions(),'classification':'CURRENT_RUN_REAL_DATA_DIAGNOSTIC',
               'model_calls':0,'pilot':pilot,'processing_status':outputs['baseline']['status'],
               'files':{p.name:digest(p) for p in out.iterdir() if p.name!='manifest.json'}})
    print('diagnostics: seven original records;',outputs['profile_pilot']['input_points'],'points')


def qualify():
    validation=read_json(REVISION/'validation.json');current=versions()
    if validation['code_sha']!=current['code_sha'] or validation['source_hashes']!=current['source_hashes']:
        raise ValueError('VALIDATION_CODE_CHANGED')
    if any(c['exit_code'] for c in validation['commands']):raise ValueError('TESTS_FAILED')
    if subprocess.check_output(['git','diff','--name-only','HEAD','--','task1/workflow','task1/tests','task1/config','task1/scripts'],cwd=ROOT,text=True).strip():
        raise ValueError('UNCOMMITTED_RESULT_CODE')
    env=read_json(REVISION/'environment.json')
    pin={'executable':env['cli_path'],'expected_sha256':env['cli_sha256'],
         'native_path':env['native_path'],'native_sha256':env['native_sha256']}
    files={**current['source_hashes']}
    for name in ('tests_final.xml','validation.json','provider_version_evidence.json','cli_https_revalidation.json','environment.json','handoff/SC-LAB1-G1-REPAIR-001_CODEX_PROMPT.md'):
        files[relative(REVISION/name)]=digest(REVISION/name)
    write_json(AUTH,{'task_id':TASK,'code_sha':current['code_sha'],'required_files':files,
                    'test_report':relative(REVISION/'tests_final.xml'),'old_ledger_sha256':digest(OLD),
                    'limits':{'outer_dispatches':6,'initial_probes':1,'role_dispatches':5,'tool_requests':12,'seconds_per_call':180,'concurrency':1},
                    'provider_pin':pin,'authorization':'Current user Prompt R1-F05; D1/D2 not approved',
                    'underlying_requests':'unknown; first visible fault stops process group'},exclusive=True)
    RepairBudget();print('qualified: one probe then at most five roles; no automatic resubmission')


def live():
    batch=RepairBudget();state=read_json(LEDGER)
    # This entry cannot be restarted to obtain a second probe or repeat uncertain calls.
    if state['model_attempts']:raise ValueError('BATCH_ALREADY_STARTED_DO_NOT_RESUBMIT')
    run='g1-repair-connectivity-01';directory=REVISION/'runs'/run;call=run+'-probe'
    directory.mkdir(parents=True,exist_ok=False)
    checkpoint={**versions(),'run_id':run,'classification':'LIVE_CONNECTIVITY_PROBE','status':'PLANNED','call_id':call}
    batch.reserve('model_attempts',run,call,probe=True)
    checkpoint['status']='DISPATCHED';write_json(directory/'checkpoint.json',checkpoint)
    provider=CodexProvider(180,**batch.qualification['provider_pin'])
    prompt=('Small connectivity probe only. Return JSON with role="research", call_id="'+call+'", action="connectivity_probe", record_ids=[], feedback_refs=[], evidence_refs=["repair:authorization"], summary="CONNECTIVITY_OK", reason="Small connectivity probe", request_status="PROPOSED", candidate_for_future_review=null. Do not use tools or perform any trajectory task.')
    try:
        value,receipt=provider.call('research',call,prompt,['connectivity_probe'],directory/'calls'/call)
        batch.finish(call,receipt)
        checkpoint['status']='VERIFIED';checkpoint['response']=value
    except (ProviderError,OSError,ValueError,KeyboardInterrupt) as exc:
        receipt_path=directory/'calls'/call/'receipt.json'
        if receipt_path.exists():batch.finish(call,read_json(receipt_path))
        else:batch.freeze('MISSING_PROBE_RECEIPT; '+str(exc))
        checkpoint.update(status='BLOCKED',error=str(exc))
    finally:
        checkpoint['ended_at']=now();write_json(directory/'checkpoint.json',checkpoint)
        write_json(directory/'manifest.json',{**checkpoint,'files':{str(p.relative_to(directory)):digest(p) for p in directory.rglob('*') if p.is_file() and p.name!='manifest.json'}})
    print('probe',checkpoint['status'],flush=True)
    if checkpoint['status']!='VERIFIED':return
    controller=Controller('g1-repair-roles-01',base=REVISION/'runs',batch=batch)
    try:controller.run(provider)
    except (ProviderError,OSError,ValueError,KeyboardInterrupt) as exc:print('roles stopped:',str(exc),flush=True)


def notebooks():
    import nbformat
    from nbclient import NotebookClient
    logs=[]
    with tempfile.TemporaryDirectory(prefix='sc-g1-kernel-') as tmp:
        kernel=Path(tmp)/'kernels/sc-g1-repair';kernel.mkdir(parents=True)
        write_json(kernel/'kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'], 'display_name':'SC Goal1 repair','language':'python'})
        old=os.environ.get('JUPYTER_PATH');os.environ['JUPYTER_PATH']=tmp+(os.pathsep+old if old else '')
        try:
            for path in sorted((ROOT/'task1/notebooks').glob('*.ipynb')):
                nb=nbformat.read(path,as_version=4);started=now()
                client=NotebookClient(nb,timeout=180,kernel_name='sc-g1-repair',resources={'metadata':{'path':str(path.parent)}})
                client.execute();nbformat.write(nb,path)
                logs.append({'notebook':relative(path),'sha256':digest(path),'started_at':started,'ended_at':now(),
                             'new_kernel':True,'python':sys.executable,'new_model_calls':0,'code_cells':sum(c.cell_type=='code' for c in nb.cells),'status':'PASS'})
        finally:
            if old is None:os.environ.pop('JUPYTER_PATH',None)
            else:os.environ['JUPYTER_PATH']=old
    write_json(REVISION/'notebooks.json',{**versions(),'executions':logs});print('two notebooks executed in fresh venv kernels')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['validate','diagnostics','qualify','live','notebooks'])
    globals()[parser.parse_args().action]()
