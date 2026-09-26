"""Independent C network readback of the already pushed artifact commit.

Only public repository refs, complete GitHub tree, and fixed-SHA bytes are read.
No push, code change, new experiment, model dispatch or credential export.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import hashlib
import json
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from review_development_runs import Audit
from task1.workflow.io import read_json,write_json,digest,now
from task1.workflow.g2_journal import task_sources,REQUIRED_COMPONENTS
OUT=Path(__file__).parent
EV=ROOT/'task1/evidence/goal2'
REPO='woobowen/Smart_Cities_and_Location_Services'

def command(args):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=60)
    if p.returncode:raise RuntimeError('READ_ONLY_COMMAND_FAILED '+repr(args)+' exit='+str(p.returncode))
    return p.stdout

def sha(raw):return hashlib.sha256(raw).hexdigest()
def bound(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}

def main():
    started_at=now();timer=time.perf_counter();a=Audit()
    registry_path=EV/'final_publication_review_targets.json';registry=read_json(registry_path)
    artifact=registry['artifact_sha'];code=registry['code_sha'];targets=registry['targets']
    a.check('exact_twentyone_publication_targets',len(targets)==21)
    for t in targets:a.check('submitted_target_bytes',digest(ROOT/t['path'])==t['sha256'],t['path'])
    active=read_json(EV/'goal_state.json');a.same('current_controller_submission',active['tasks']['publication']['evidence'],targets)
    a.check('publication_review_pending',active['tasks']['publication']['status']=='REVIEW_PENDING')
    snapshot=read_json(EV/'publication/goal_state_before_publication_acceptance.snapshot.json');state=snapshot['content']
    a.check('asof_state_bytes_reconstruct',sha((json.dumps(state,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())==snapshot['source_sha256'])
    a.check('all_internal_tasks_verified_before_publication',all(r['status']=='VERIFIED' for k,r in state['tasks'].items() if k!='publication'))
    a.check('no_open_issue',all(r['status']=='VERIFIED' for r in state['issues'].values()))
    internal=read_json(OUT/'internal_acceptance_receipt_v2.json');prep=read_json(OUT/'publication_preparation_receipt.json')
    a.check('actual_independent_internal_and_release_reviews',internal['status']==prep['status']=='VERIFIED' and internal['role_context']==prep['role_context']=='/root/c_contract' and not internal['errors'] and not prep['errors'])
    a.check('all17_acceptance_components',internal['checked_components']==['A%02d'%i for i in range(1,18)])
    commit=read_json(EV/'publication/artifact_commit.json');push=read_json(EV/'publication/artifact_push.json')
    a.check('actual_successful_nonforce_push',push['actual_command']==['git','push','origin','main'] and push['exit_code']==0 and push['force_push'] is False and push['artifact_sha']==artifact)
    a.check('actual_commit_matches_code_parent',commit['exit_code']==0 and commit['artifact_sha']==artifact and commit['code_sha']==code and command(['git','rev-parse',artifact+'^']).decode().strip()==code)
    for label,record in [('commit',commit),('push',push)]:a.check('actual_command_log_bound',digest(EV/f'publication/artifact_{label}.log')==record['log_sha256'])
    a.check('internal_acceptance_precedes_commit_and_push',datetime.fromisoformat(internal['at'])<datetime.fromisoformat(commit['started_at'])<datetime.fromisoformat(push['started_at'])<datetime.fromisoformat(push['ended_at']))
    a.check('push_log_actual_main_update',b'main -> main' in (EV/'publication/artifact_push.log').read_bytes())
    relation=subprocess.run(['git','merge-base','--is-ancestor','a45d89f49f2041477b16485f535adc508c32f8ea',artifact],cwd=ROOT,capture_output=True)
    a.check('G1_history_preserved_ancestor',relation.returncode==0)
    sources={p:digest(ROOT/p) for p in task_sources('publication')}
    a.same('submitted_source_epoch_exact',sources,active['tasks']['publication']['source_hashes'])
    for p,h in sources.items():a.check('actual_committed_source_equals_audited_source',sha(command(['git','show',artifact+':'+p]))==h,p)
    expected_url='https://github.com/'+REPO+'.git'
    refs={'local_head':command(['git','rev-parse','HEAD']).decode().strip(),
          'origin_main':command(['git','rev-parse','origin/main']).decode().strip(),
          'actual_remote_before':command(['git','ls-remote','origin','refs/heads/main']).decode().split()[0]}
    a.check('actual_repository_and_branch',command(['git','remote','get-url','origin']).decode().strip()==expected_url and command(['git','branch','--show-current']).decode().strip()=='main')
    a.check('three_actual_refs_equal_artifact',set(refs.values())=={artifact})
    remote_bytes=command(['gh','api',f'repos/{REPO}/git/trees/{artifact}?recursive=1'])
    remote=json.loads(remote_bytes);a.check('actual_remote_complete_tree_not_truncated',remote.get('truncated') is False)
    (OUT/'publication_remote_tree_response.json').write_bytes(remote_bytes)
    actual_tree={r['path']:{'mode':r['mode'],'git_blob':r['sha']} for r in remote['tree'] if r['type']=='blob'}
    local_tree={}
    for row in command(['git','ls-tree','-r','-z',artifact]).split(b'\0'):
        if row:
            fields,p=row.split(b'\t',1);mode,kind,blob=fields.decode().split()
            if kind=='blob':local_tree[p.decode()]={'mode':mode,'git_blob':blob}
    a.same('independent_actual_full_remote_blob_tree',actual_tree,local_tree)
    a.check('actual_all4408_blobs',len(actual_tree)==4408)
    root_report=read_json(EV/'publication/artifact_01/verification.json')
    root_tree=read_json(EV/'publication/artifact_01/remote_tree.json')
    a.same('root_full_remote_tree_semantics',root_tree,remote)
    paths=read_json(EV/'release_checks/fixed_sha_readback_paths.json')
    a.check('26_unique_registered_remote_files',len(paths)==len(set(paths))==26 and paths==[r['path'] for r in root_report['fixed_sha_readbacks']])
    def fetch(p):
        start=now();request=['gh','api','-H','Accept: application/vnd.github.raw+json',f'repos/{REPO}/contents/{quote(p,safe="/")}?ref={artifact}']
        raw=command(request);expected=command(['git','show',artifact+':'+p])
        return {'path':p,'requested_at':start,'completed_at':now(),'bytes':len(raw),'sha256':sha(raw),'git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'equals_actual_commit_bytes':raw==expected,'actual_remote_read':True,'command':request,'url':f'https://github.com/{REPO}/blob/{artifact}/{quote(p,safe="/")}'}
    with ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(fetch,paths))
    for got,claimed in zip(files,root_report['fixed_sha_readbacks']):
        a.check('C_actual_fixed_SHA_bytes_match_commit',got['equals_actual_commit_bytes'] and got['git_blob']==local_tree[got['path']]['git_blob'],got['path'])
        for field in ['path','bytes','sha256','git_blob','actual_remote_read','url']:a.same('root_observation_matches_independent_network_'+field,claimed[field],got[field])
    refs['actual_remote_after']=command(['git','ls-remote','origin','refs/heads/main']).decode().split()[0]
    a.check('remote_did_not_advance_during_C_readback',refs['actual_remote_after']==artifact)
    for k in ['verified_commit','local_head','origin_main','actual_remote_before','actual_remote_after']:a.check('root_ref_observations_match',root_report[k]==artifact)
    a.check('root_readback_exit0',read_json(EV/'publication/artifact_readback_execution.json')['exit_code']==0)
    staging=read_json(EV/'publication/staging_logs.json')
    for r in staging['logs']:
        a.check('substantive_ignored_log_actually_committed',r['path'] in local_tree and sha(command(['git','show',artifact+':'+r['path']]))==r['sha256'],r['path'])
    a.check('staging_log_count_complete',staging['count']==len(staging['logs']))
    startup=read_json(EV/'startup.json');untracked=[]
    for p,h in startup['user_untracked'].items():
        a.check('original_user_archive_preserved',digest(ROOT/p)==h,p)
        if p not in local_tree:untracked.append(p)
    a.check('two_original_untracked_archives_not_published',len(untracked)==2)
    a.check('external_gpt_and_submission_not_forged',state['gpt_second_review']=='PENDING' and state['submission']=='NOT_READY')
    # Recheck exact submitted targets at the end, after asynchronous network I/O.
    for t in targets:a.check('review_target_unchanged_after_remote_reads',digest(ROOT/t['path'])==t['sha256'],t['path'])
    receipt={'goal_id':'SC-LAB1-G2-EXPERIMENTS-001','task':'publication','classification':'INDEPENDENT_C_ACTUAL_GITHUB_PUBLICATION_VERIFICATION','role_context':'/root/c_contract','at':now(),'status':'VERIFIED' if not a.errors else 'REJECTED','checked_components':REQUIRED_COMPONENTS['publication'],'unchecked_components':['future_final_metadata_commit_and_its_remote_readback','GPT_SECOND_REVIEW','teacher_submission_and_Goal3'],'targets':targets,'source_hashes':sources,'check_count':a.check_count,'errors':a.errors,'repository':expected_url,'branch':'main','code_sha':code,'artifact_sha':artifact,'actual_refs':refs,'full_remote_tree_blob_count':len(actual_tree),'complete_remote_tree_matches':actual_tree==local_tree,'fixed_sha_readbacks':files,'independent_remote_tree':bound(OUT/'publication_remote_tree_response.json'),'publication_status':'PUBLISHED_VERIFIED' if not a.errors else 'REJECTED','gpt_second_review':'PENDING','submission':'NOT_READY','preserved_untracked_archives':untracked,'actual_network_operations':{'git_remote_reads':2,'GitHub_API_tree_reads':1,'GitHub_API_fixed_file_reads':26,'maximum_concurrent_file_reads':3},'source_review_and_staging':bound(OUT/'publication_preparation_receipt.json'),'input_registry':bound(registry_path),'audit_program':bound(Path(__file__)),'started_at':started_at,'elapsed_seconds':time.perf_counter()-timer,'new_model_calls':0,'self_reference_boundary':'Observes artifact commit 1ac203c already published. This C receipt and later status metadata are created afterwards and are not claimed to be inside that artifact commit. Root must publish and actually recheck the later metadata commit before final handoff.'}
    write_json(OUT/'publication_receipt.json',receipt,exclusive=True)
    print(json.dumps({k:receipt[k] for k in ['status','check_count','errors','artifact_sha','full_remote_tree_blob_count','elapsed_seconds']},ensure_ascii=False))

if __name__=='__main__':main()
