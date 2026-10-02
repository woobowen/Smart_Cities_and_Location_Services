"""Accepted report content guards and the side-effect boundary of REPORT_BUILD."""
import ast
import json
from pathlib import Path
import shutil
import zipfile

import pytest
from task1.goal3 import __main__ as cli
from task1.reports import build_reports as reports


@pytest.fixture
def copied_report(tmp_path, monkeypatch):
    original = reports.ROOT
    directory = tmp_path/'task1/reports/experiment1'
    shutil.copytree(original/'task1/reports/experiment1', directory,
                    ignore=shutil.ignore_patterns('build', '__pycache__'))
    config = json.loads((directory/'accepted-source.json').read_text())
    for key in ('canonical_pdf', 'canonical_zip', 'palette_authority'):
        target = tmp_path/config[key]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original/config[key], target)
    process = tmp_path/'task1/reports/process1'
    process.mkdir()
    (process/'sentinel.txt').write_text('protected Process content')
    monkeypatch.setattr(reports, 'ROOT', tmp_path)
    monkeypatch.setattr(reports, 'REPORT', directory)
    return tmp_path, config


def test_bad_reference_hash_rejected_before_compile(copied_report, monkeypatch):
    root, config = copied_report
    (root/config['canonical_pdf']).write_bytes(b'damaged supplied PDF')
    monkeypatch.setattr(reports.subprocess, 'run', lambda *a, **k: pytest.fail('must not compile'))
    with pytest.raises(ValueError, match='REFERENCE_PAIR_HASH_MISMATCH'):
        reports.build(root/'evidence')


def test_changed_chapter_preserves_current_pdf_and_process(copied_report, monkeypatch):
    root, config = copied_report
    current = root/config['current_reading_copy']
    before = current.read_bytes()
    chapter = root/'task1/reports/experiment1/chapters/01_data.tex'
    chapter.write_text(chapter.read_text()+'\nUnauthorized content change\n')
    monkeypatch.setattr(reports.subprocess, 'run', lambda *a, **k: pytest.fail('must not compile'))
    with pytest.raises(ValueError, match='ACCEPTED_EDITABLE_SOURCE_CHANGED'):
        reports.build(root/'evidence')
    assert current.read_bytes() == before
    assert (root/'task1/reports/process1/sentinel.txt').read_text() == 'protected Process content'


def test_report_route_only_compiles_and_packages(tmp_path, monkeypatch):
    target = tmp_path/'REVIEW_ONLY_scope.zip'
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        if 'task1.goal3.package' in command:
            target.write_bytes(b'test archive result')
    monkeypatch.setattr(cli.subprocess, 'run', run)
    result = cli.report_build(target, tmp_path/'evidence')
    assert len(calls) == 2
    assert calls[0][1].endswith('/task1/reports/build_reports.py')
    assert '--render' in calls[0] and '--evidence-output' in calls[0]
    assert calls[0][calls[0].index('--report') + 1] == 'all'
    assert result['process_report_compiled'] is True
    assert calls[1][1:3] == ['-m', 'task1.goal3.package']
    assert '--probe' in calls[1]
    assert result['new_numerical_runs'] == 0
    assert result['process_report_regenerated'] is False


def test_existing_package_is_never_overwritten(tmp_path, monkeypatch):
    target = tmp_path/'REVIEW_ONLY_existing.zip'
    target.write_bytes(b'previous user artifact')
    monkeypatch.setattr(cli.subprocess, 'run', lambda *a, **k: pytest.fail('must not rebuild'))
    with pytest.raises(ValueError, match='EXISTING_PACKAGE_PROTECTED'):
        cli.report_build(target)
    assert target.read_bytes() == b'previous user artifact'


def test_numerical_entry_functions_match_actually_executed_package():
    actual = Path('task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/executed_package/REVIEW_ONLY_10245102410_吴博闻_实验一.zip')
    with zipfile.ZipFile(actual) as archive:
        old = archive.read('task1/goal3/__main__.py').decode()
    new = Path(cli.__file__).read_text()
    functions = lambda text: {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    for name in ('full_recompute', 'live'):
        assert functions(old)[name] == functions(new)[name]


@pytest.mark.parametrize('damaged', ['current_reading_copy', 'canonical_pdf'])
def test_package_rejects_stale_process_before_runtime_reads(tmp_path, damaged):
    import hashlib
    from task1.goal3.package import closure
    for name in ('experiment1', 'process1'):
        directory = tmp_path / 'task1/reports' / name
        directory.mkdir(parents=True)
        content = ('accepted ' + name).encode()
        config = {'current_reading_copy': f'task1/reports/{name}/current.pdf',
                  'canonical_pdf': f'task1/reports/{name}/approved.pdf',
                  'pdf_sha256': hashlib.sha256(content).hexdigest(), 'expected_pages': 1}
        for field in ('current_reading_copy', 'canonical_pdf'):
            (tmp_path / config[field]).write_bytes(content)
        (directory / 'accepted-source.json').write_text(json.dumps(config))
    (tmp_path / config[damaged]).write_bytes(b'old Process draft')
    # No numerical inputs exist in this fixture; the report guard must fail first.
    with pytest.raises(ValueError, match='ACCEPTED_REPORT_HASH_MISMATCH:process1'):
        closure(tmp_path)
