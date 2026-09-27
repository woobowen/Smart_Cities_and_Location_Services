"""Read-only actual artifact publication review, before the metadata closing commit."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
ARTIFACT = 'fd559e451291b9d424682853ef0909aa5eb94b32'
REPOSITORY = 'https://github.com/woobowen/Smart_Cities_and_Location_Services.git'
RAW_BASE = 'https://raw.githubusercontent.com/woobowen/Smart_Cities_and_Location_Services/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    output = HERE / 'publication_closure_receipt.json'
    assert not output.exists(), 'do not overwrite publication review'
    submission_name = EV + 'publication_review_submission.json'
    submission = read(submission_name); state = read(EV+'goal_state.json')
    task = state['tasks']['publication']
    checks, errors, cache = [], [], {}
    def check(label, condition):
        checks.append({'check':label,'passed':bool(condition)})
        if not condition:errors.append({'check':label})
    def digest(relative):
        if relative not in cache:
            value=hashlib.sha256()
            with (ROOT/relative).open('rb') as stream:
                for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
            cache[relative]=value.hexdigest()
        return cache[relative]
    check('real independent publication submission', task['status']=='REVIEW_PENDING' and task['author']!='/root/c_documents')
    check('exact actual task targets/source map', task['targets']==submission['targets'] and task['source_hashes']==submission['source_hashes'])
    check('six targets and nine sources', len(task['targets'])==6 and len(task['source_hashes'])==9)
    for row in task['targets']:check('actual submitted target:'+row['path'],digest(row['path'])==row['sha256'])
    for relative,expected in task['source_hashes'].items():check('actual submitted source:'+relative,digest(relative)==expected)
    publication = read(EV+'PUBLICATION_RECORD.json')
    check('correct actual artifact in submission/record',submission['ARTIFACT_SHA']==publication['ARTIFACT_SHA']==ARTIFACT)
    check('correct project remote and current branch',git('remote','get-url','origin').decode().strip()==REPOSITORY and git('branch','--show-current').decode().strip()=='main')
    actual_head = git('rev-parse','HEAD').decode().strip()
    actual_origin = git('rev-parse','origin/main').decode().strip()
    actual_remote_line = git('ls-remote','origin','refs/heads/main').decode().strip()
    actual_remote = actual_remote_line.split()[0]
    check('independent actual local/origin/remote equality', actual_head==actual_origin==actual_remote==ARTIFACT)
    check('observed artifact remote matches publication record',
          all(publication['last_actual_push_verification'][k]==ARTIFACT for k in ['local_head','origin_main','remote_main']))
    check('original accepted history remains ancestor',subprocess.run(['git','merge-base','--is-ancestor',publication['accepted_G2_anchor'],ARTIFACT],cwd=ROOT).returncode==0)
    accepted_name = EV+'independent_c/internal_acceptance_receipt.json'
    accepted = read(accepted_name)
    check('actual accepted receipt is inside published commit',sha(git('show',ARTIFACT+':'+accepted_name))==digest(accepted_name))
    check('independent acceptance already consumed before publication submission',
          state['tasks']['internal_acceptance']['status']=='VERIFIED' and accepted['status']=='VERIFIED')
    committed_at=git('show','-s','--format=%cI',ARTIFACT).decode().strip()
    check('internal acceptance preceded artifact commit and remote observation',
          datetime.fromisoformat(accepted['at']) < datetime.fromisoformat(committed_at)
          < datetime.fromisoformat(publication['last_actual_push_verification']['at']))
    check('actual push report is non-force successful operation',publication['artifact_push']['observed_exit_code']==0 and
          publication['artifact_push']['command']=='git push origin main' and publication['artifact_push']['force'] is False)
    check('published code/Notebook/report identities not conflated',
          publication['processing_CODE_SHA']=='e12f8a27944210adb452730be92a0674dfc6b84b' and
          publication['notebook_execution_CODE_SHA']=='0b20be8e4142e8e62246e9357993e83951833e4f' and
          publication['report_source_commit']=='cb4f2118d82da98ca80ef7f83593c1ff6b66a866')

    # Independently download the actual immutable objects; no browser cache,
    # credentials, auth files, generated replacements or disabled TLS are used.
    requested = [row['path'] for row in publication['remote_fixed_sha_readbacks']]
    expected_paths = [EV+'REVIEW_PACKET.md',EV+'result_summary.json','task1/docs/goal3/TECHNICAL_HANDOFF.md',
        'task1/reports/experiment1/experiment1.pdf','task1/reports/process1/process1.pdf',
        'task1/submission/REVIEW_ONLY_实验一.zip','task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb',
        'task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb']
    check('all eight key published objects actually checked',requested==expected_paths)
    committed_refs={p:sha(git('show',ARTIFACT+':'+p)) for p in requested}
    def retrieve(relative):
        url=RAW_BASE+ARTIFACT+'/'+quote(relative,safe='/')
        request=Request(url,headers={'User-Agent':'SC-LAB1-independent-publication-review','Cache-Control':'no-cache'})
        try:
            with urlopen(request,timeout=45) as response:
                value=hashlib.sha256();n=0
                for block in iter(lambda:response.read(1024*1024),b''):value.update(block);n+=len(block)
                return {'path':relative,'url':url,'http_status':response.status,'bytes':n,'sha256':value.hexdigest(),
                    'committed_blob_sha256':committed_refs[relative], 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
                    'matches_committed_blob':value.hexdigest()==committed_refs[relative]}
        except Exception as exc:
            return {'path':relative,'url':url,'error_type':type(exc).__name__,'error':str(exc)}
    with ThreadPoolExecutor(max_workers=3) as pool: remote_readbacks=list(pool.map(retrieve,requested))
    for row,root_row in zip(remote_readbacks,publication['remote_fixed_sha_readbacks']):
        check('actual independent HTTP200 committed bytes:'+row['path'],row.get('http_status')==200 and row.get('matches_committed_blob') is True)
        check('independent remote result matches reported observed bytes:'+row['path'],
              row.get('sha256')==root_row['sha256'] and row.get('bytes')==root_row['bytes'])

    manifest_name=EV+'independent_documents/publication_candidate_manifest.json'
    manifest=read(manifest_name);frozen_files=manifest['files']
    check('stable candidate manifest unchanged',digest(manifest_name)=='91848d44db7b67a4ba809f98adc31b35bab1947bc882002e6702a4f7b8e578b2')
    process=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    committed_bytes=0
    for item in frozen_files:
        relative=item['path']
        process.stdin.write((ARTIFACT+':'+relative+'\n').encode());process.stdin.flush()
        header=process.stdout.readline().decode().strip().split()
        assert len(header)==3 and header[1]=='blob',relative
        size=int(header[2]);value=process.stdout.read(size);assert len(value)==size and process.stdout.read(1)==b'\n'
        check('frozen candidate current and committed:'+relative,sha(value)==digest(relative)==item['sha256'])
        committed_bytes+=size
    process.stdin.close();check('committed blob reader exit',process.wait()==0)
    source_target_count=0
    for name,row in state['tasks'].items():
        if name=='publication' or row['status'] not in {'VERIFIED','BLOCKED_EXTERNAL'}:continue
        for target in row.get('targets',[]):
            check('current closed task actual target:'+name+':'+target['path'],digest(target['path'])==target['sha256']);source_target_count+=1
        for relative,expected in row.get('source_hashes',{}).items():
            check('current closed task actual source:'+name+':'+relative,digest(relative)==expected);source_target_count+=1
    check('all engineering issues remain closed',all(i['status']=='VERIFIED' for i in state['issues'].values()))
    check('external reports/package not hidden by publication',all(state['tasks'][n]['status']=='BLOCKED_EXTERNAL' for n in ['experiment_report','process_report','package']))
    expected_states={'G3-A%02d'%i:'BLOCKED' if i in {15,16,18} else 'PASS' for i in range(1,21)}
    requirements=read(EV+'requirements.json')
    check('17 PASS and three genuine external BLOCKED requirements',
          {r['id']:r['status'] for r in requirements['requirements']}==expected_states)
    check('external authority state remains accurate',
          (state['GPT_SECOND_REVIEW'],state['Understanding'],state['Submission'])==('PENDING','USER_DETERMINED','NOT_READY'))
    final=(ROOT/(EV+'FINAL_RESPONSE.md')).read_text();packet=(ROOT/(EV+'REVIEW_PACKET.md')).read_text()
    # Entire current documents were manually read; retained technical facts are
    # compared with the already reviewed artifact version section by section.
    old_final=git('show',ARTIFACT+':'+EV+'FINAL_RESPONSE.md').decode()
    for heading in ['B','C','D','E','F','G']:
        expression=r'(?ms)^## '+heading+r'\..*?(?=^## |\Z)'
        check('final technical section unchanged since accepted artifact:'+heading,
              re.search(expression,final).group()==re.search(expression,old_final).group())
    for heading in 'ABCDEFGHI':check('final A-I complete:'+heading,'\n## '+heading+'.' in final)
    for anchor in ['PARTIAL_BLOCKED','GPT_SECOND_REVIEW=PENDING','167,289','固定 SHA 回读的 8 个关键文件全部 HTTP 200','最终包含本记录的 HEAD 由最后聊天回复报告']:
        check('final closing boundary:'+anchor,anchor in final)
    check('both current entries report actual published artifact honestly',ARTIFACT in final and ARTIFACT in packet)
    check('artifact snapshot stale-publication wording explicitly explained','最后一个快照保留形成时的发布待办' in final)
    links=[]
    for relative in [EV+'FINAL_RESPONSE.md',EV+'REVIEW_PACKET.md']:
        for destination in re.findall(r'\]\(([^)]+)\)',(ROOT/relative).read_text()):
            url=urlsplit(destination)
            if url.scheme or url.netloc:
                if url.netloc=='github.com' and '/blob/' in url.path:
                    prefix='/woobowen/Smart_Cities_and_Location_Services/blob/'+ARTIFACT+'/'
                    check('public fixed link exact artifact:'+destination,url.path.startswith(prefix))
                    if url.path.startswith(prefix):
                        target=unquote(url.path[len(prefix):]);check('public fixed link exists in actual commit:'+target,
                            subprocess.run(['git','cat-file','-e',ARTIFACT+':'+target],cwd=ROOT).returncode==0)
                continue
            target=((ROOT/relative).parent/unquote(url.path)).resolve();good=target.exists() and target.is_relative_to(ROOT)
            check('closing local link:'+relative+':'+destination,good);links.append({'from':relative,'target':destination,'exists':good})

    # Only new metadata since the actual artifact commit is scanned here.
    changes={p.decode() for p in git('diff','--name-only','-z',ARTIFACT,'--').split(b'\0') if p}
    additions={p.decode() for p in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if p}
    protected=set(manifest['protected_untracked_user_archives_excluded'])
    delta=sorted((changes|additions)-protected-{str(output.relative_to(ROOT))})
    spec=importlib.util.spec_from_file_location('publication_marker_rules',HERE/'prepublication_scan.py')
    scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner)
    scan_rows=[]
    for relative in delta:
        path=ROOT/relative
        check('only current publication text metadata changed:'+relative,path.suffix in {'.json','.md','.py'} and path.is_file() and not path.is_symlink())
        with path.open('rb') as stream:categories,n=scanner.scan_stream(stream)
        if categories:
            check('only known original journal paths in metadata delta:'+relative,
                  set(categories)=={'PERSONAL_ABSOLUTE_PATH'} and relative in {EV+'goal_state.json',EV+'publication_submission_snapshot.json'})
        scan_rows.append({'path':relative,'sha256':digest(relative),'scanned_text_bytes':n,'marker_categories':categories,
            'classification':'PRESERVED_ORIGINAL_COMMAND_PATHS' if categories else 'NO_RECORDED_MARKER_FINDINGS'})
    startup=read(EV+'startup.json');untracked={p.decode() for p in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if p}
    for name,expected in startup['untracked_protected'].items():
        check('original ZIP remains byte exact:'+name,digest(name)==expected)
        if name in protected:check('original ZIP still untracked and unpublished:'+name,name in untracked and
            subprocess.run(['git','cat-file','-e',ARTIFACT+':'+name],cwd=ROOT,capture_output=True).returncode!=0)
    # Ensure no author mutated the submitted bytes during the network reads.
    for row in task['targets']:check('submitted target unchanged at end:'+row['path'],sha((ROOT/row['path']).read_bytes())==row['sha256'])
    final_remote=git('ls-remote','origin','refs/heads/main').decode().split()[0]
    check('remote remained actual artifact throughout review',final_remote==ARTIFACT)
    result={'role_context':'/root/c_documents','target_id':'publication','status':'VERIFIED' if not errors else 'REPAIR_REQUIRED',
        'at_utc':datetime.now(timezone.utc).isoformat(),'targets':task['targets'],'source_hashes':task['source_hashes'],
        'submission':{'path':submission_name,'sha256':digest(submission_name),'actual_status_at_review':'REVIEW_PENDING'},
        'checks':checks,'errors':errors,'ARTIFACT_SHA':ARTIFACT,
        'independent_remote_observation':{'local_head':actual_head,'origin_main':actual_origin,'ls_remote_main':actual_remote,
            'ls_remote_main_at_end':final_remote,'branch':'main','repository':REPOSITORY},
        'chronology':{'internal_acceptance_at':accepted['at'],'artifact_committer_at':committed_at,
            'root_remote_observation_at':publication['last_actual_push_verification']['at']},
        'independent_fixed_sha_readbacks':remote_readbacks,
        'stable_candidate_committed_and_current':{'files':len(frozen_files),'bytes':committed_bytes},
        'closed_task_target_source_occurrences_checked':source_target_count,
        'metadata_delta_scan':scan_rows,'closing_local_links':links,
        'goal_status':'PARTIAL_BLOCKED','GPT_SECOND_REVIEW':'PENDING','Submission':'NOT_READY',
        'checked_components':['Actual independent git ls-remote and local/origin equality for already published ARTIFACT',
            'Independent HTTPS immutable-SHA downloads of all eight key Markdown/JSON/PDF/Notebook/ZIP artifacts, HTTP200 and exact committed SHA256',
            'Independent raw committed-blob read of every 1049 frozen file and all current closed-task targets/sources; no data/report/Notebook/ZIP replacement',
            'Actual independent acceptance precedes artifact commit; accepted receipt was already contained in published history, G2 anchor remains ancestor',
            'Actual submitted six target bytes and nine source hashes, final A-I/links/statuses, bounded metadata secret scan and original untracked ZIP protection',
            'External identity/Evidence gaps retained; publication never claims Evidence Lock, user Understanding, webpage GPT acceptance or teacher submission'],
        'unchecked_components':['Future closing-metadata commit/push and final HEAD equality must be checked after they actually happen; this receipt does not preclaim its own commit SHA',
            'External identity/Evidence Master inputs and final webpage GPT/user decisions'],
        'new_method_runs':0,'new_model_calls':0,'author_files_changed_by_reviewer':False,
        'checker_sha256':sha(Path(__file__).read_bytes()),'actual_command':'.venv/bin/python '+str(Path(__file__).relative_to(ROOT))}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'errors':errors,'remote_objects':len(remote_readbacks),
        'targets':len(task['targets']),'sources':len(task['source_hashes']),
        'receipt':str(output.relative_to(ROOT)),'sha256':sha(output.read_bytes())},ensure_ascii=False))


if __name__=='__main__':main()
