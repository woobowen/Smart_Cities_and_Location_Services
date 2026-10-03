"""Recheck actual approved project-source set and all protected tracked bytes."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
EV=Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    initial=json.loads((EV/'independent_initial_tracked_hashes.json').read_text())
    prior=json.loads((EV/'independent_current_mapping_and_protection.json').read_text())
    relative='evidence/infrastructure/chatgpt-project-source-sync/sources.json'
    current=json.loads((ROOT/relative).read_text())
    baseline=json.loads(subprocess.check_output(['git','show',f'9d91392289b31a4afa5c94cfd3869da9f021b4ad:{relative}'],cwd=ROOT))
    all_base={m['canonical_name']:m for m in baseline['sources']}
    all_current={m['canonical_name']:m for m in current['sources']}
    assert set(all_base)==set(all_current)
    approved={n:m for n,m in all_current.items() if m['project_source']}
    old_approved={n:m for n,m in all_base.items() if m['project_source']}
    expected={'AGENTS.md','SMART_CITIES_RESEARCH_PROTOCOL.md','SMART_CITIES_REPORT_WRITING_GUIDE.md',
        'SMART_CITIES_VISUAL_SYSTEM.md','WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md', '实验课1.pptx',
        '作业.zip','作业1轨迹数据预处理.ipynb','任务3_LLM辅助评估清洗.ipynb','publication-plots.zip',
        'Experiment_Report_P2_Exact.pdf','Experiment_Report_吴博闻_10245102410.pdf',
        'Experiment_Report_完整重构_源文件.zip','Process_Report_Revised.pdf','Process_Report_Revised_LaTeX_Source.zip'}
    assert set(approved)==set(old_approved)==expected
    two={'Process_Report_Revised.pdf','Process_Report_Revised_LaTeX_Source.zip'}
    assert all(m==all_base[n] for n,m in all_current.items() if n not in two)
    release=ROOT/'releases/chatgpt-project-sources'
    assert {p.name for p in release.iterdir()}==set(approved)
    rows=[]
    for name,m in approved.items():
        a=(ROOT/m['active_path']).read_bytes();b=(release/name).read_bytes()
        assert a==b and sha(a)==m['sha256']
        changed=name in two
        if not changed:assert sha(a)==initial[m['active_path']]['sha256']
        rows.append({'name':name,'active_path':m['active_path'],'sha256':sha(a),'bytes':len(a),
            'metadata_unchanged':not changed,'baseline_hash_unchanged':not changed,'active_release_byte_equal':True})
    inputs={'Process_Report_Revised.pdf':('dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23',8143247),
        'Process_Report_Revised_LaTeX_Source.zip':('831d61baa7de160796827b60f29e1ada9f1b3809c2a87aa4acd6b98703e352ef',56878339)}
    versions=[]
    for name,(expected,size) in inputs.items():
        paths=[name,'reports/process-report/experiment1-revised/'+name,'releases/chatgpt-project-sources/'+name]
        if name.endswith('.pdf'):paths+=['task1/reports/process1/process1.pdf','task1/reports/process1/source/Process_Report_Revised.pdf']
        for rel in paths:
            path=ROOT/rel;assert path.stat().st_size==size and sha(path.read_bytes())==expected
            versions.append({'path':rel,'sha256':expected,'bytes':size})
    source=ROOT/'task1/reports/process1/source'
    actual={str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
    with zipfile.ZipFile(ROOT/'reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip') as archive:
        members={n.removeprefix('Process_Report_Revised_Source/'):archive.read(n) for n in archive.namelist()}
        assert actual==set(members) and len(members)==397
        assert all((source/n).read_bytes()==v for n,v in members.items())
    changes=[];missing=[];protected_count=0
    for path,original in initial.items():
        current_path=ROOT/path
        if not current_path.is_file():missing.append(path);continue
        digest=sha(current_path.read_bytes())
        if digest!=original['sha256']:
            changes.append({'path':path,'initial_sha256':original['sha256'],'current_sha256':digest})
        if any(path.startswith(p) for p in prior['protected_scope']):
            protected_count+=1;assert digest==original['sha256'],path
    assert protected_count==5527 and not missing
    old_pair=[]
    for name,expected in [('Process_Report_Revised.pdf','45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83'),
            ('Process_Report_Revised_LaTeX_Source.zip','00cb7b641b37b2a71a552fc5bef47fc551a16ea7ce88bcf139f2e68a5f1451da')]:
        path=ROOT/'reports/process-report/experiment1-revised/history/accepted-20261002'/name
        assert sha(path.read_bytes())==expected
        old_pair.append({'path':str(path.relative_to(ROOT)),'sha256':expected})
    check=['.venv/bin/python','-B','evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py','--check']
    actual_check=subprocess.run(check,cwd=ROOT,text=True,capture_output=True)
    assert actual_check.returncode==0
    result={'reviewer_context':'/root/independent_review','checked_at':datetime.now(timezone.utc).isoformat(),
        'status':'PASS','project_source_members':rows,'project_source_count':len(rows),
        'historical_excluded_rows_preserved':True,'other13_hashes_and_metadata_baseline_exact':True,
        'release_exact_set':True,'current_process_artifacts':versions,'current_work_source_files':len(members),
        'work_zip_every_member_byte_exact':True,'protected_scope':prior['protected_scope'],
        'protected_files_unchanged':protected_count,'initial_tracked_checked':len(initial),
        'tracked_byte_changes':changes,'missing_tracked_files':missing,'old_approved_pair':old_pair,
        'settings_changed':False,'ui_status':current.get('ui_status'),'ui_not_claimed_updated':True,
        'sync_readonly_check':{'actual_command':check,'exit_code':actual_check.returncode,'result':json.loads(actual_check.stdout)},
        'new_model_calls':0,'trajectory_runs':0}
    (EV/'independent_final_mapping_and_protection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','project_source_count':len(rows),'other13_metadata_and_bytes_unchanged':True,
        'work_source_exact':len(members),'protected_unchanged':protected_count,
        'tracked_byte_changes':len(changes),'missing':0,'ui_status':current.get('ui_status')},ensure_ascii=False))


if __name__=='__main__':main()
