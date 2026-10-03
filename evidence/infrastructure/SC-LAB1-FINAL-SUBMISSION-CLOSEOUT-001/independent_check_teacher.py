"""Independently extract the real final ZIP and execute only frozen dependency checks."""
from datetime import datetime, timezone
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[3]
EV=Path(__file__).resolve().parent
TEMP=Path('/tmp/SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001-independent')
PY=ROOT/'.venv/bin/python'
NAME='10245102410_吴博闻_实验一'
ARCHIVE=ROOT/'task1/submission/teacher-delivery'/f'{NAME}.zip'
FOLDER=ARCHIVE.with_suffix('')
EXPECTED='c1d0b80313f81e81a6bcd4cc02d06002c442201379ea871c4c338386bde2eb66'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files(directory):
    return {str(p.relative_to(directory)):p.read_bytes() for p in directory.rglob('*') if p.is_file()}


def main():
    initial=json.loads((EV/'independent_initial_tracked_hashes.json').read_text())
    scope=json.loads((EV/'independent_current_mapping_and_protection.json').read_text())['protected_scope']
    protected={p:sha((ROOT/p).read_bytes()) for p in initial if any(p.startswith(s) for s in scope)}
    assert len(protected)==5527 and all(h==initial[p]['sha256'] for p,h in protected.items())
    assert sha(ARCHIVE.read_bytes())==EXPECTED
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        names=[x.filename for x in z.infolist()]
        assert len(names)==len(set(names))==len({n.casefold() for n in names})
        for info in z.infolist():
            n=info.filename;path=PurePosixPath(n)
            assert not info.is_dir() and not path.is_absolute() and '..' not in path.parts
            assert '\\' not in n and ':' not in n and not stat.S_ISLNK(info.external_attr>>16)
            assert not any(p in ('.git','.venv','__pycache__') for p in path.parts)
            assert path.suffix.lower() not in ('.ttf','.otf','.ttc','.woff','.woff2')
        contents={n:z.read(n) for n in names}
    manifest=json.loads(contents['PACKAGE_MANIFEST.json'])
    members=manifest['members'];declared={m['path'] for m in members}
    assert manifest['member_count']==len(members)==len(declared)
    assert set(contents)==declared|{'PACKAGE_MANIFEST.json'}
    assert manifest['total_uncompressed_bytes']==sum(m['bytes'] for m in members)
    assert manifest['package_status']=='TEACHER_SUBMISSION_CANDIDATE'
    assert manifest['sent_to_teacher'] is False
    changed=[]
    for m in members:
        data=contents[m['path']]
        assert len(data)==m['bytes'] and sha(data)==m['archive_sha256'],m['path']
        assert sha((ROOT/m['source_path']).read_bytes())==m['source_sha256'],m['path']
        if m['source_sha256']!=m['archive_sha256']:
            assert m['transformations'];changed.append({k:m[k] for k in ('path','source_path','source_sha256','archive_sha256','transformations')})
    assert [m['path'] for m in changed]==['task1/evidence/goal2/result_summary.json']
    assert files(FOLDER)==contents and not (FOLDER/ARCHIVE.name).exists()
    assert b'\x00' not in contents['README.md']
    readme=contents['README.md'].decode()
    assert '执行计数为空、保存输出为0' in readme and '保留已完成运行的输出' not in readme
    notebooks=[]
    for n,data in contents.items():
        if not n.endswith('.ipynb'):continue
        d=json.loads(data)
        assert d['nbformat']==4 and isinstance(d['cells'],list)
        codes=[c for c in d['cells'] if c['cell_type']=='code']
        assert codes
        for c in codes:ast.parse(''.join(c['source']))
        errors=[i for i,c in enumerate(codes) if any(o.get('output_type')=='error' for o in c['outputs'])]
        assert not errors
        assert sha(data)==initial[n]['sha256']
        notebooks.append({'path':n,'sha256':sha(data),'cell_count':len(d['cells']),'code_cells':len(codes),
            'execution_counts':[c['execution_count'] for c in codes],
            'saved_output_cells':sum(bool(c['outputs']) for c in codes),'error_output_cells':errors,
            'byte_identical_to_prior_completed_notebook':True,
            'current_run_all':'NOT_EXECUTED_STATIC_READ_ONLY_SCOPE'})
    assert len(notebooks)==2
    fresh=Path(tempfile.mkdtemp(prefix='teacher-candidate-02-fresh-',dir=TEMP))
    for n,data in contents.items():
        p=fresh/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    assert not (fresh/'.git').exists()
    env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    cli=[str(PY),'-B','-m','task1.goal3.package','--verify-dir','.']
    verify_proc=subprocess.run(cli,cwd=fresh,env=env,text=True,capture_output=True)
    (EV/'independent_teacher_verify_dir.log.txt').write_text(verify_proc.stdout+verify_proc.stderr)
    assert verify_proc.returncode==0,verify_proc.stderr
    verify=json.loads(verify_proc.stdout)
    assert verify['status']=='VERIFIED' and verify['verified_members']==len(members)
    code="""import sys,json,pathlib
root=pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0,str(root))
from task1.workflow.io import ROOT
from task1.goal3.package import static_probe
assert ROOT.resolve()==root
assert not (root/'.git').exists()
m=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
p={x['path']:(root/x['path']).read_bytes() for x in m['members']}
print(json.dumps({'outer_ROOT':str(ROOT),'ROOT_is_fresh':ROOT.resolve()==root,'git_present':False,'probe':static_probe(p)}))
"""
    probe_cmd=[str(PY),'-I','-B','-c',code,str(fresh)]
    probe_proc=subprocess.run(probe_cmd,cwd=fresh,env=env,text=True,capture_output=True)
    (EV/'independent_teacher_static_probe.log.txt').write_text(probe_proc.stdout+probe_proc.stderr)
    assert probe_proc.returncode==0,probe_proc.stderr
    probe=json.loads(probe_proc.stdout)
    assert probe['ROOT_is_fresh'] and probe['probe']['status']=='VERIFIED'
    assert probe['probe']['new_model_calls']==probe['probe']['trajectory_runs']==0
    assert files(fresh)==contents
    assert all(sha((ROOT/p).read_bytes())==h for p,h in protected.items())
    result={'task':'SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001','reviewer_context':'/root/independent_review',
        'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS',
        'archive':str(ARCHIVE.relative_to(ROOT)),'archive_bytes':ARCHIVE.stat().st_size,'archive_sha256':EXPECTED,
        'zip_crc':True,'exact_set':True,'member_hashes':True,
        'zip_members_including_manifest':len(contents),'declared_members_excluding_manifest':len(members),
        'manifest_total_uncompressed_bytes_excluding_manifest':manifest['total_uncompressed_bytes'],
        'folder_exact_set_and_bytes':True,'folder_contains_own_zip':False,'all_sources_sha256_match':True,
        'explicit_transformed_members':changed,'fresh_root':str(fresh),'fresh_git_present':False,
        'actual_cli_verify_directory':{'command':cli,'cwd':str(fresh),'exit_code':verify_proc.returncode,'result':verify},
        'actual_static_probe':{'command':probe_cmd,'cwd':str(fresh),'exit_code':probe_proc.returncode,'result':probe},
        'notebooks':notebooks,'teacher_readme_saved_output_statement_matches_actual_notebooks':True,
        'fresh_files_unchanged_by_checks':True,'protected_before_after_file_count':len(protected),
        'protected_before_after_bytes_unchanged':True,'protected_initial_bytes_unchanged':True,
        'new_model_calls':0,'trajectory_runs':0,'teacher_sent':False,'webpage_second_review':'PENDING'}
    (EV/'independent_teacher_fresh_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','archive_sha256':EXPECTED,'members':len(contents),'declared_members':len(members),
        'folder_zip_equal':True,'actual_verify_dir_exit':verify_proc.returncode,'actual_probe_exit':probe_proc.returncode,
        'new_model_calls':0,'trajectory_runs':0,'protected_unchanged':len(protected)},ensure_ascii=False))


if __name__=='__main__':main()
