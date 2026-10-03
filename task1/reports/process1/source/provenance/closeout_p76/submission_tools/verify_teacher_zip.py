"""Strictly check a freshly built teacher ZIP; never send it or run experiments.

The optional probe executes the package's existing no-trajectory binding probe.
Use the original scientific Python environment for --probe. The verifier itself
uses the standard library and the existing pdfinfo command.
"""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

EXPERIMENT = 'task1/reports/experiment1/experiment1.pdf'
PROCESS = 'task1/reports/process1/process1.pdf'
NOTEBOOKS = ('task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb',
             'task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb')
DENIED_PARTS = {'.git','.venv','venv','__pycache__','.pytest_cache','.ipynb_checkpoints','node_modules','.ssh','.codex'}
DENIED_SUFFIXES = {'.ttf','.ttc','.otf','.woff','.woff2','.pyc','.pyo','.pem','.key','.zip'}
SECRET_PATTERNS = [re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                   re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
                   re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
                   re.compile(r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b')]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def need(condition: bool, reason: str) -> None:
    if not condition: raise ValueError(reason)

def safe_name(name: str) -> str:
    p = PurePosixPath(name)
    need(bool(name) and not p.is_absolute() and '\\' not in name and ':' not in name,
         'UNSAFE_ARCHIVE_PATH')
    need(all(x and x not in ('.','..') and x == x.rstrip(' .') for x in name.split('/')),
         'UNSAFE_PATH_COMPONENT')
    need(not any(x.lower() in DENIED_PARTS or x.lower().startswith('.env') for x in p.parts),
         'FORBIDDEN_DIRECTORY')
    need(p.suffix.lower() not in DENIED_SUFFIXES and 'Zone.Identifier' not in name,
         'FORBIDDEN_FONT_CACHE_KEY_OR_NESTED_ZIP')
    return unicodedata.normalize('NFC',name).casefold()

def validate(archive: Path, experiment_sha: str, process_sha: str,
             probe: bool = False, python_executable: str = sys.executable) -> dict:
    for digest in (experiment_sha,process_sha):
        need(re.fullmatch('[0-9a-f]{64}',digest) is not None,'INVALID_EXPECTED_HASH')
    need(archive.is_file() and not archive.is_symlink(),'ARCHIVE_MISSING_OR_SYMLINK')
    payload: dict[str,bytes] = {}; names=set()
    with zipfile.ZipFile(archive) as z:
        need(sum(x.file_size for x in z.infolist()) <= 1024**3,'PACKAGE_EXCEEDS_1_GIB_SAFETY_LIMIT')
        for item in z.infolist():
            normalized=safe_name(item.filename.rstrip('/') if item.is_dir() else item.filename)
            need(normalized not in names,'DUPLICATE_OR_WINDOWS_COLLIDING_NAME'); names.add(normalized)
            need(not stat.S_ISLNK(item.external_attr>>16),'SYMLINK_MEMBER')
            need(not (item.flag_bits & 1),'ENCRYPTED_MEMBER')
            if not item.is_dir(): payload[item.filename]=z.read(item)
        need(z.testzip() is None,'ZIP_CRC_FAILURE')
    need('PACKAGE_MANIFEST.json' in payload,'MANIFEST_MISSING')
    manifest=json.loads(payload['PACKAGE_MANIFEST.json'])
    need(manifest.get('package_status') in ('TEACHER_SUBMISSION_CANDIDATE','READY_FOR_USER_SUBMISSION'),'NOT_A_FINAL_TEACHER_CANDIDATE')
    need({'README.md','requirements.txt'} <= set(payload),'README_OR_REQUIREMENTS_MISSING')
    entries=manifest['members']; expected={}
    for e in entries:
        safe_name(e['path']);need(e['path'] not in expected,'DUPLICATE_MANIFEST_ENTRY')
        need(e['path'] != 'PACKAGE_MANIFEST.json','SELF_HASH_ENTRY_NOT_SUPPORTED')
        expected[e['path']]=e
    need(set(payload)==set(expected)|{'PACKAGE_MANIFEST.json'},'EXACT_MEMBER_SET_MISMATCH')
    need(manifest.get('sent_to_teacher') is False,'PACKAGE_MUST_NOT_CLAIM_SENT')
    need(manifest.get('member_count')==len(entries),'MANIFEST_COUNT_MISMATCH')
    need(manifest.get('total_uncompressed_bytes')==sum(len(payload[x]) for x in expected),'MANIFEST_TOTAL_SIZE_MISMATCH')
    for path,e in expected.items():
        data=payload[path]
        need(len(data)==e['bytes'] and sha(data)==e['archive_sha256'],'MANIFEST_SIZE_OR_HASH_MISMATCH:'+path)
    need(set(p for p in payload if p.endswith('.pdf'))=={EXPERIMENT,PROCESS},'EXACT_TWO_REPORTS_REQUIRED')
    need(sha(payload[EXPERIMENT])==experiment_sha,'WRONG_EXPERIMENT_REPORT')
    need(sha(payload[PROCESS])==process_sha,'WRONG_PROCESS_REPORT')
    need(set(p for p in payload if p.endswith('.ipynb'))==set(NOTEBOOKS),'EXACT_TWO_COMPLETED_NOTEBOOKS_REQUIRED')
    notebook_checks=[]
    for path in NOTEBOOKS:
        n=json.loads(payload[path]);need(n.get('nbformat')==4 and isinstance(n.get('cells'),list),'INVALID_NOTEBOOK')
        codes=[c for c in n['cells'] if c.get('cell_type')=='code'];errors=[];unexecuted=[]
        for i,c in enumerate(codes):
            need(isinstance(c.get('outputs',[]),list),'INVALID_NOTEBOOK_OUTPUT')
            if any(o.get('output_type')=='error' for o in c.get('outputs',[])):errors.append(i)
            src=c.get('source',[]);src=''.join(src) if isinstance(src,list) else src
            if src.strip() and c.get('execution_count') is None:unexecuted.append(i)
        need(not errors,'NOTEBOOK_CONTAINS_ERROR_OUTPUT:'+path)
        notebook_checks.append({'path':path,'code_cells':len(codes),'error_outputs':errors,'unexecuted_code_cells':unexecuted,
                                'current_scope':'JSON and saved-output checks only; no Restart/Run All claim'})
    python_files=0;secret_hits=[]
    for path,data in payload.items():
        if path.endswith('.py'):
            ast.parse(data.decode('utf8'),filename=path);python_files+=1
        if path.endswith(('.py','.json','.md','.tex','.txt','.ipynb')):
            text=data.decode('utf8')
            if any(p.search(text) for p in SECRET_PATTERNS):secret_hits.append(path)
    need(not secret_hits,'POSSIBLE_SECRET_FILES:'+','.join(secret_hits))
    probe_result=None;package_verifier=None
    with tempfile.TemporaryDirectory(prefix='sc-teacher-zip-check-') as tmp:
        root=Path(tmp)
        for path,data in payload.items():
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        pages={}
        for path,wanted in [(EXPERIMENT,25),(PROCESS,77)]:
            p=subprocess.run(['pdfinfo',str(root/path)],capture_output=True,text=True,timeout=30)
            need(p.returncode==0,'PDFINFO_FAILED:'+path)
            found=re.search(r'^Pages:\s+(\d+)',p.stdout,re.M)
            need(found is not None and int(found.group(1))==wanted,'PDF_PAGE_COUNT_MISMATCH:'+path)
            pages[path]=int(found.group(1))
        if probe:
            # Execute only the existing manifest verifier and existing static probe.
            # The latter forbids model calls and checks bindings without trajectories.
            code='''import json,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
from task1.goal3.package import verify_directory,static_probe
m=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
payload={e['path']:(root/e['path']).read_bytes() for e in m['members']}
v=verify_directory(root);p=static_probe(payload)
print(json.dumps({'package_verifier':v,'static_probe':p},ensure_ascii=False))
if v.get('status')!='VERIFIED' or p.get('status')!='VERIFIED':raise SystemExit(1)
'''
            p=subprocess.run([python_executable,'-I','-B','-c',code,str(root)],cwd=root,capture_output=True,text=True,timeout=120)
            need(p.returncode==0,'ISOLATED_PACKAGE_VERIFIER_OR_STATIC_PROBE_FAILED; inspect the captured error locally')
            observed=json.loads(p.stdout.splitlines()[-1]);package_verifier=observed['package_verifier'];probe_result=observed['static_probe']
            need(probe_result.get('new_model_calls')==0 and probe_result.get('trajectory_runs')==0,'PROBE_SCOPE_VIOLATION')
    return {'status':'PASS','checked_at':datetime.now(timezone.utc).isoformat(),'archive_sha256':sha(archive.read_bytes()),
            'archive_bytes':archive.stat().st_size,'members_including_manifest':len(payload),'declared_members':len(entries),
            'exact_member_set':True,'zip_crc':True,'all_member_hashes':True,'pages':pages,
            'report_sha256':{EXPERIMENT:experiment_sha,PROCESS:process_sha},'notebooks':notebook_checks,
            'python_syntax_checked_files':python_files,'secret_pattern_hits':secret_hits,
            'scan_scope':'Filenames and decoded text; not a complete privacy/OCR audit of screenshots.',
            'package_verifier':package_verifier,'isolated_static_probe':probe_result,
            'new_model_calls':0,'new_trajectory_runs':0,'full_recompute':'NOT_EXECUTED_BY_THIS_CHECK',
            'teacher_delivery':'NOT_SENT','github_final_review':'SEPARATE_FUTURE_STEP'}

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path);p.add_argument('--experiment-sha256',required=True);p.add_argument('--process-sha256',required=True)
    p.add_argument('--probe',action='store_true');p.add_argument('--python',default=sys.executable);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try:result=validate(args.archive,args.experiment_sha256,args.process_sha256,args.probe,args.python)
    except Exception as e:result={'status':'FAIL','error_type':type(e).__name__,'error':str(e),'teacher_delivery':'NOT_SENT'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__': main()
