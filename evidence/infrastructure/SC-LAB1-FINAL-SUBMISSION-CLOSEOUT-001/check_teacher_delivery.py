"""Real candidate folder/ZIP and explicit fresh --verify-dir/probe checks."""
from pathlib import Path
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
import nbformat
from IPython.core.inputtransformer2 import TransformerManager

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
NAME = '10245102410_吴博闻_实验一'
DELIVERY = ROOT / 'task1/submission/teacher-delivery'
PYTHON = ROOT / '.venv/bin/python'


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def main():
    archive = DELIVERY / (NAME + '.zip'); folder = DELIVERY / NAME
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        payload = {i.filename: z.read(i) for i in z.infolist() if not i.is_dir()}
    actual = hashes(folder); expected = {p: hashlib.sha256(d).hexdigest() for p,d in payload.items()}
    assert actual == expected and archive.name not in actual
    manifest = json.loads(payload['PACKAGE_MANIFEST.json'])
    assert len(manifest['members']) + 1 == len(expected)
    notebooks = []
    transformer = TransformerManager()
    for name in sorted(p for p in payload if p.endswith('.ipynb')):
        nb = nbformat.reads(payload[name].decode(), as_version=4); nbformat.validate(nb)
        cells = [c for c in nb.cells if c.cell_type == 'code']
        for cell in cells: ast.parse(transformer.transform_cell(cell.source))
        error_cells = [i for i,c in enumerate(cells) if any(o.output_type == 'error' for o in c.outputs)]
        assert not error_cells
        assert payload[name] == (ROOT / name).read_bytes()
        notebooks.append({'path': name, 'nbformat_validation': 'PASS', 'code_syntax': 'PASS',
            'code_cells': len(cells), 'execution_counts': [c.execution_count for c in cells],
            'saved_output_count': sum(len(c.outputs) for c in cells), 'error_cells': error_cells,
            'byte_identical_to_unchanged_completed_notebook': True,
            'scope': 'Completed recomputation code; execution counts null and saved outputs zero. Prior bound FULL execution evidence is external; no current Run All'})
    env = os.environ.copy(); env.pop('PYTHONPATH', None); env['PYTHONDONTWRITEBYTECODE'] = '1'
    with tempfile.TemporaryDirectory(prefix='sc-final-teacher-fresh-') as temp:
        isolated = Path(temp)
        for p,data in payload.items():
            target = isolated / p; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        assert not (isolated / '.git').exists()
        before = hashes(isolated)
        command = [str(PYTHON), '-B', '-m', 'task1.goal3.package', '--verify-dir', '.']
        verifier = subprocess.run(command, cwd=isolated, env=env, capture_output=True, text=True, timeout=60)
        (EV / 'teacher_fresh_verify_dir_output.txt').write_text(verifier.stdout + verifier.stderr)
        assert verifier.returncode == 0 and json.loads(verifier.stdout)['status'] == 'VERIFIED'
        code = '''import json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
from task1.workflow.io import ROOT
from task1.goal3.package import static_probe
assert ROOT==root and not (root/'.git').exists()
m=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
p=static_probe({e['path']:(root/e['path']).read_bytes() for e in m['members']})
print(json.dumps({'current_ROOT':str(ROOT),'matches_fresh_root':True,'git_present':False,'static_probe':p}))
assert p['status']=='VERIFIED' and p['new_model_calls']==0 and p['trajectory_runs']==0
'''
        probe_command = [str(PYTHON), '-I', '-B', '-c', code, str(isolated)]
        probe = subprocess.run(probe_command, cwd=isolated, env=env, capture_output=True, text=True, timeout=90)
        (EV / 'teacher_fresh_probe_output.txt').write_text(probe.stdout + probe.stderr)
        assert probe.returncode == 0
        probe_result = json.loads(probe.stdout.splitlines()[-1])
        assert hashes(isolated) == before, 'Read-only verification modified extracted inputs'
        receipt = {'status': 'PASS', 'actual_zip_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'actual_zip_bytes': archive.stat().st_size, 'files_including_manifest': len(expected),
            'manifest_member_count_excludes_self': len(manifest['members']),
            'folder_zip_exact_set_and_bytes': True, 'zip_not_inside_folder': True,
            'fresh_root': str(isolated), 'fresh_no_git': True, 'fresh_extraction_hashes_unchanged_after_checks': True,
            'package_verify_dir_command': command, 'package_verify_dir_exit_code': verifier.returncode,
            'package_verify_dir_result': json.loads(verifier.stdout), 'probe_exit_code': probe.returncode,
            'probe': probe_result, 'notebooks': notebooks, 'new_model_calls': 0, 'trajectory_runs': 0,
            'full_recompute_current_task': 'NOT_RUN; unchanged previously executed science inherited',
            'sent_to_teacher': False, 'members_sha256': expected}
    (EV / 'teacher_delivery_check.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: receipt[k] for k in ('status','actual_zip_sha256','files_including_manifest','package_verify_dir_exit_code','probe_exit_code','new_model_calls','trajectory_runs')}, ensure_ascii=False))


if __name__ == '__main__': main()
