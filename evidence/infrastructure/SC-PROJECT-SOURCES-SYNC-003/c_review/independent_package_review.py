"""Independent C archive bytes, historical binding and isolated entry checks.

Writes only to this review directory; never runs numerical or model work.
The CLI/gate regression is explicitly not a new FULL execution.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def payload(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names))
        for info in archive.infolist():
            name = PurePosixPath(info.filename)
            assert not name.is_absolute() and '..' not in name.parts
            assert not stat.S_ISLNK(info.external_attr >> 16)
            assert name.suffix.lower() not in {'.ttf', '.otf', '.woff', '.woff2', '.key', '.pem'}
        return {n: archive.read(n) for n in names}


ISOLATED_CODE = r'''
import contextlib, io, json, pathlib, sys
root = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
from task1.workflow import io as workflow_io
from task1.workflow.g2_provider import ExperimentProvider
from task1.workflow.provider import CodexProvider
from task1.goal3 import __main__ as entry
from task1.goal3.runtime import assert_binding, execution_gate, definitions, source_snapshot, code_identity
assert workflow_io.ROOT == root and entry.ROOT == root and not (root/'.git').exists()
attempts = []
def forbidden(*args, **kwargs):
    attempts.append('attempt')
    raise AssertionError('INDEPENDENT_C_FORBIDS_MODEL_CALLS')
ExperimentProvider.call = CodexProvider.call = forbidden
observations = []
def rejected(name, call, expected):
    try:
        call()
    except ValueError as exc:
        assert expected in str(exc), (name, str(exc))
        observations.append({'case': name, 'result': str(exc)})
    else:
        raise AssertionError('EXPECTED_REJECTION: ' + name)
rejected('FULL existing-output protection', lambda: entry.full_recompute(root), 'NEW_OUTPUT_DIRECTORY_REQUIRED')
rejected('LIVE disabled/no Git protection', lambda: entry.live('c-boundary-probe', False), 'LIVE_REQUIRES_ENABLE_LIVE')
rejected('REPORT invalid filename', lambda: entry.report_build(root/'invalid.zip'), 'REPORT_BUILD_REQUIRES_REVIEW_ONLY')
rejected('REPORT protects existing file', lambda: entry.report_build(root/'README.md'), 'EXISTING_PACKAGE_PROTECTED')
rejected('REPORT isolated package is not a complete report checkout', lambda: entry.report_build(root/'REVIEW_ONLY_c-probe.zip'), 'REPORT_BUILD_REQUIRES_COMPLETE_REPOSITORY')
for argv, expected_exit in [(['--help'], 0), (['FULL_RECOMPUTE'], 2)]:
    sys.argv = ['task1.goal3'] + argv
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        try:
            entry.main()
        except SystemExit as exc:
            assert exc.code == expected_exit
        else:
            raise AssertionError('EXPECTED_CLI_EXIT')
    observations.append({'case': 'actual CLI ' + ' '.join(argv), 'exit': expected_exit,
                         'output': output.getvalue()})
frozen = json.loads((root/'task1/evidence/goal3/contract_freeze.json').read_text())
assert_binding(frozen['bindings'])
production = json.loads((root/'task1/evidence/goal3/production_freeze.json').read_text())
execution_gate('FULL_PRODUCTION', production['input_ids'], production['strategy_ids'])
identity = code_identity(source_snapshot(), 'FULL_PRODUCTION', True)
assert identity['code_sha'] == production['processing_code_sha']
assert source_snapshot() == production['processing_source_hashes']
registered = definitions()
assert len(registered) == 11 and attempts == []
modules = [entry, workflow_io]
assert all(pathlib.Path(m.__file__).resolve().is_relative_to(root) for m in modules)
print(json.dumps({'status': 'VERIFIED', 'isolated_root': True, 'git_present': False,
                 'new_model_attempts': len(attempts), 'new_trajectory_runs': 0,
                 'contract_and_production_gate': 'VERIFIED', 'registered_strategies': len(registered),
                 'frozen_processing_identity': identity,
                 'processing_source_count': len(source_snapshot()),
                 'entry_boundary_cases': observations,
                 'scope': 'actual isolated imports, CLI and early rejection paths; no FULL execution'}, ensure_ascii=False))
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    archive = args.archive.resolve()
    current = payload(archive)
    manifest = json.loads(current['PACKAGE_MANIFEST.json'])
    entries = manifest['members']
    assert set(current) == {m['path'] for m in entries} | {'PACKAGE_MANIFEST.json'}
    rows = []
    for member in entries:
        path = member['path']
        assert sha(current[path]) == member['archive_sha256']
        assert len(current[path]) == member['bytes']
        source = ROOT / member.get('source_path', path)
        assert sha(source.read_bytes()) == member['source_sha256'], path
        if not member['transformations']:
            assert current[path] == source.read_bytes(), path
        rows.append({'path': path, 'sha256': sha(current[path]),
                     'transformations': member['transformations']})
    approved = ROOT/'reports/experiment-report/experiment1-reconstructed/Experiment_Report_吴博闻_10245102410.pdf'
    assert current['task1/reports/experiment1/experiment1.pdf'] == approved.read_bytes()
    assert current['task1/reports/process1/process1.pdf'] == (ROOT/'task1/reports/process1/process1.pdf').read_bytes()
    previous = ROOT/'task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一.zip'
    executed = ROOT/'task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/executed_package/REVIEW_ONLY_10245102410_吴博闻_实验一.zip'
    comparisons = []
    for before in (previous, executed):
        old = payload(before)
        assert set(old) == set(current)
        changes = [{'path': n, 'old_sha256': sha(old[n]), 'new_sha256': sha(current[n])}
                   for n in sorted(current) if old[n] != current[n]]
        comparisons.append({'reference': str(before.relative_to(ROOT)),
                            'reference_sha256': sha(before.read_bytes()), 'changed': changes,
                            'unchanged_members': len(current)-len(changes)})
        assert {c['path'] for c in changes} <= {
            'PACKAGE_MANIFEST.json', 'README.md', 'task1/reports/experiment1/experiment1.pdf',
            'task1/goal3/__main__.py'}
        old_ast, new_ast = ast.parse(old['task1/goal3/__main__.py']), ast.parse(current['task1/goal3/__main__.py'])
        methods = lambda tree: {n.name: ast.dump(n, include_attributes=False)
                                for n in tree.body if isinstance(n, ast.FunctionDef)}
        a, b = methods(old_ast), methods(new_ast)
        assert a['full_recompute'] == b['full_recompute'] and a['live'] == b['live']
    fixture = OUT/'build/current-package'
    assert not fixture.exists(), 'preserve previous C extraction evidence'
    fixture.mkdir(parents=True)
    for name, data in current.items():
        path = fixture/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    before_state = {n: [sha((fixture/n).read_bytes()), (fixture/n).stat().st_mtime_ns] for n in current}
    result = subprocess.run([str(ROOT/'.venv/bin/python'), '-I', '-B', '-c', ISOLATED_CODE, str(fixture)],
                            cwd=fixture, text=True, capture_output=True, timeout=60,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                                     MPLCONFIGDIR=str(OUT/'build/matplotlib-cache')))
    (OUT/'package-isolated-console.txt').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    isolated = json.loads(result.stdout.splitlines()[-1])
    after_state = {n: [sha((fixture/n).read_bytes()), (fixture/n).stat().st_mtime_ns] for n in current}
    assert before_state == after_state
    report = {'reviewer': 'independent C', 'archive': str(archive.relative_to(ROOT)),
              'archive_sha256': sha(archive.read_bytes()), 'members': len(current),
              'CRC_safe_names_member_bytes_sources': 'VERIFIED', 'member_hashes': rows,
              'historical_comparisons': comparisons, 'isolated': isolated,
              'isolated_payload_bytes_and_mtimes_unchanged': True,
              'FULL_execution_this_task': False,
              'inheritance_boundary': 'Exact unchanged numerical runtime/Notebook/input members bind historical FULL. __main__.py changed only report routing/CLI; unchanged numerical function AST plus actual isolated boundary regression support that scope. No newly run FULL is claimed.'}
    (OUT/'independent-package-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'member_hashes'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
