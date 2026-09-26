"""Read-only independent C release preparation against an actual artifact commit."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from review_development_runs import Audit
from task1.workflow.io import read_json,write_json,digest,now
OUT=Path(__file__).parent
EV=ROOT/'task1/evidence/goal2'
ARTIFACT='1ac203c1c60b3c64490150cbd473d3091eac8564'
CODE='c1c6272606716f9f59aa785d48bfeadb09c7a30e'

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)

def bound(p):
    return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}

def main():
    a=Audit();started=time.perf_counter();targets=[]
    source=EV/'release_checks/scan_release.py'
    spec=importlib.util.spec_from_file_location('c_release_delta_scanner',source)
    scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner)
    tree={}
    for row in git('ls-tree','-r','-z',ARTIFACT).split(b'\0'):
        if row:
            fields,path=row.split(b'\t',1);mode,kind,blob=fields.decode().split()
            if kind=='blob':tree[path.decode()]={'mode':mode,'git_blob':blob}
    a.check('artifact_direct_parent_is_computational_commit',git('rev-parse',ARTIFACT+'^').decode().strip()==CODE)
    a.check('verified_internal_receipt_already_committed',git('show',ARTIFACT+':task1/evidence/goal2/c_contract/internal_acceptance_receipt_v2.json')==(OUT/'internal_acceptance_receipt_v2.json').read_bytes())
    cumulative_rescans=[]
    for tag in ['delta_02','delta_03']:
        folder=EV/'release_checks'/tag
        d=read_json(folder/'delta_reuse_receipt.json')
        baseline=read_json(ROOT/d['baseline_report']['path'])
        before={r['path']:r for r in read_json(ROOT/d['baseline_inventory']['path'])}
        current={r['path']:r for r in read_json(folder/'scope_inventory.json')}
        a.check('scan_source_equal',digest(source)==d['scanner_source_sha256']==baseline['scanner_sha256'])
        a.check('delta_source_equal',digest(EV/'release_checks/scan_release_delta.py')==d['delta_source_sha256'])
        for b in [d['baseline_report'],d['baseline_inventory'],d['portability_review_binding']]:a.check('prior_scan_exact_target',digest(ROOT/b['path'])==b['sha256'])
        a.check('no_unresolved_scan_findings',d['status']=='DELTA_CONTENT_CHECKS_CLEAR_WITH_BOUND_PATH_REVIEW' and not any(d['unresolved_counts'].values()))
        a.check('raw_scanner_flags_not_erased',d['underlying_scanner_exit_code']==1 and d['underlying_report_status']=='FINDINGS_REQUIRE_REVIEW' and len(d['reviewed_portability'])==3)
        for r in d['text_reuse']:
            a.check('exact_prior_text_reuse',r['sha256']==before[r['path']]['sha256']==current[r['path']]['sha256'] and before[r['path']]['classification']=='PROPOSED_G2_SUBSTANTIVE_FILE')
        for r in d['text_rescans']:
            a.check('actual_delta_text_byte_binding',r['sha256_before_scan']==r['sha256_after_scan']==digest(ROOT/r['path']))
            findings,absolute,chars=scanner.scan_text(ROOT/r['path'])
            a.check('C_repeated_actual_delta_scan',not findings and chars==r['characters_scanned'],r['path'])
            cumulative_rescans.append({'path':r['path'],'characters':chars})
        for r in current.values():
            p=ROOT/r['path']
            if r['classification']=='PROPOSED_G2_SUBSTANTIVE_FILE':
                a.check('all_scanned_substantive_files_committed',r['path'] in tree,r['path'])
                # Hash the trusted frozen local file, then compare its Git blob
                # to the artifact tree; no dependence on the changing index.
                a.check('checked_substantive_bytes_preserved',digest(p)==r['sha256'],r['path'])
                raw=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                a.check('committed_equals_checked_bytes',tree.get(r['path'],{}).get('git_blob')==blob,r['path'])
        e=read_json(folder/'execution.json');a.check('actual_delta_execution_exit0',e['exit_code']==0)
        targets.extend(bound(folder/n) for n in ['delta_reuse_receipt.json','scope_inventory.json','execution.json'])
    staged_path=EV/'publication/staged_content_check.json'
    staged=read_json(staged_path);rows=staged['changes']
    a.check('3245_index_entries_763418136_bytes',len(rows)==staged['staged_files']==3245 and sum(r['bytes'] for r in rows)==staged['staged_bytes']==763418136)
    for row in rows:
        a.check('each_original_staged_blob_is_committed',tree.get(row['path'])=={'mode':row['mode'],'git_blob':row['git_blob']},row['path'])
        a.check('no_symlink_cache_or_oversized_staged_file',row['mode']=='100644' and not scanner.cache_file(Path(row['path'])) and row['bytes']<=100*1024*1024,row['path'])
    startup=read_json(EV/'startup.json')
    a.check('user_archives_not_in_staged_changes',not (set(startup['user_untracked']) & {r['path'] for r in rows}))
    changed={p for p in git('diff-tree','--no-commit-id','--name-only','-r','-z',ARTIFACT).decode().split('\0') if p}
    extras=sorted(changed-{r['path'] for r in rows})
    expected_extras={'task1/evidence/goal2/publication/staged_content_check.json'} | {'task1/evidence/goal2/release_checks/delta_03/'+n for n in ['bundle_check.txt','delta_reuse_receipt.json','execution.json','execution.log','protected_bytes.json','release_check.json','scope_inventory.json']}
    a.check('eight_post_index_snapshot_additions_are_own_safety_receipts',set(extras)==expected_extras)
    for p in extras:
        findings,absolute,chars=scanner.scan_text(ROOT/p)
        a.check('C_actual_post_snapshot_receipt_text_scan',not findings,p)
        a.check('extra_receipt_bytes_are_commit_bytes',git('show',ARTIFACT+':'+p)==(ROOT/p).read_bytes(),p)
    whitespace_path=EV/'publication/staged_whitespace_check.json';ws=read_json(whitespace_path)
    full_cmd=['git','diff','--check',CODE,ARTIFACT]
    full=subprocess.run(full_cmd,cwd=ROOT,capture_output=True)
    a.check('actual_full_whitespace_exit_and_hash',full.returncode==ws['full_exit_code']==2 and len(full.stdout)==ws['full_stdout_bytes'] and hashlib.sha256(full.stdout).hexdigest()==ws['full_stdout_sha256'])
    counts=Counter();paths=Counter()
    for line in full.stdout.decode().splitlines():
        match=re.match(r'^(.*?):\d+: (trailing whitespace\.|new blank line at EOF\.)$',line)
        if match:paths[match[1]]+=1;counts[match[2]]+=1
    a.same('124586_preserved_formatting_diagnostics',dict(counts),ws['warning_counts'])
    a.same('complete_107_affected_paths',dict(paths),{r['path']:r['warnings'] for r in ws['files']})
    source_cmd=['git','diff','--check',CODE,ARTIFACT,'--',*ws['source_command'][5:]]
    source_result=subprocess.run(source_cmd,cwd=ROOT,capture_output=True)
    a.check('actual_executable_config_notebook_document_whitespace_clean',source_result.returncode==ws['source_exit_code']==0 and not source_result.stdout and not source_result.stderr)
    for r in ws['files']:
        if r['classification']=='CSV_STANDARD_CRLF_RECORD_ENDINGS':a.check('CSV_CRLF_actual_format',b'\r\n' in (ROOT/r['path']).read_bytes())
        elif r['classification']=='GENERATED_SVG_PATH_ATTRIBUTE_WHITESPACE':a.check('generated_SVG_extension',Path(r['path']).suffix=='.svg')
        else:a.check('preserved_prompt_or_evidence_only',r['path'].startswith('task1/evidence/goal2/'))
    verifier=EV/'release_checks/verify_publication.py'
    compile(verifier.read_text(),str(verifier),'exec')
    targets += [bound(staged_path),bound(whitespace_path),bound(verifier),bound(source),bound(EV/'release_checks/scan_release_delta.py')]
    receipt={'role_context':'/root/c_contract','classification':'INDEPENDENT_C_ARTIFACT_COMMIT_PREPARATION_REVIEW','at':now(),'status':'VERIFIED' if not a.errors else 'REJECTED','artifact_sha':ARTIFACT,'code_sha':CODE,'check_count':a.check_count,'errors':a.errors,'targets':targets,'delta_text_rescans':cumulative_rescans,'committed_changes':len(changed),'original_staged_snapshot_entries':len(rows),'additional_scanned_receipt_entries':extras,'whitespace_checks':{'full_command':full_cmd,'full_exit_code':full.returncode,'preserved_warning_counts':dict(counts),'executable_command':source_cmd,'executable_exit_code':source_result.returncode},'actual_remote_verified':False,'unchecked_components':['actual_push_exit','actual_remote_head_and_tree','actual_fixed_SHA_file_bytes'],'verify_publication_source_review':'Read completely: fixed40hex commit, main/origin/actual remote equality before/after, repo exact, complete nontruncated remote blob tree, every requested fixed-SHA raw file byte equals git show; writes only an optional new publication observation directory and does not mutate repo or credentials. This source review is not remote publication evidence.','audit_program':bound(Path(__file__)),'new_model_calls':0,'elapsed_seconds':time.perf_counter()-started}
    write_json(OUT/'publication_preparation_receipt.json',receipt,exclusive=True)
    print(json.dumps({k:receipt[k] for k in ['status','check_count','errors','elapsed_seconds']},ensure_ascii=False))

if __name__=='__main__':main()
