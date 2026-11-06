"""Isolated adversarial guard checks; does not compile or change real reports."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image


def load(path, name):
    ast.parse(path.read_text())
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    sys.dont_write_bytecode = True
    review = Path(__file__).resolve().parent
    root = review.parents[3]
    scratch = review / 'build/guard_tests'
    scratch.mkdir(parents=True, exist_ok=True)
    builder_path = root / 'task2/scripts/build_reports.py'
    package_path = root / 'task2/scripts/package_report_sources.py'
    builder = load(builder_path, 'independent_builder')
    packager = load(package_path, 'independent_packager')
    tests = []
    actual_temp = tempfile.TemporaryDirectory

    def own_temp(*args, **kwargs):
        kwargs['dir'] = scratch
        return actual_temp(*args, **kwargs)

    for mode in ('success', 'compile_failure', 'text_mismatch', 'pixel_mismatch'):
        with own_temp(prefix=mode + '-') as temporary:
            fixture = Path(temporary)
            folder = fixture / 'task2/reports/process'
            folder.mkdir(parents=True)
            accepted = folder / 'Process_Report.pdf'
            accepted.write_bytes(b'accepted immutable bytes')
            before = accepted.read_bytes()
            evidence = fixture / 'evidence'
            evidence.mkdir()
            builder.ROOT = fixture

            def fake_run(command, **kwargs):
                if command[0] == 'latexmk':
                    if mode == 'compile_failure':
                        return subprocess.CompletedProcess(command, 1, 'synthetic failure')
                    build = Path(next(part[8:] for part in command if part.startswith('-outdir=')))
                    (build / 'main.pdf').write_bytes(b'recompiled distinct metadata bytes')
                    (build / 'main.log').write_text('No compilation warnings.\n')
                    return subprocess.CompletedProcess(command, 0, 'synthetic successful compile')
                if command[0] == 'pdftoppm':
                    prefix = Path(command[-1])
                    color = 'black' if mode == 'pixel_mismatch' and prefix.parent.name == 'compiled' else 'white'
                    Image.new('RGB', (8, 8), color).save(str(prefix) + '-1.png')
                    return subprocess.CompletedProcess(command, 0)
                raise AssertionError('unexpected subprocess.run ' + repr(command))

            def fake_output(command, **kwargs):
                if command[0] == 'fc-list':
                    return '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc\n'
                if command[0] == 'pdfinfo':
                    return 'Pages: 1\n'
                if command[0] == 'pdftotext':
                    return b'different' if mode == 'text_mismatch' and str(command[2]).endswith('main.pdf') else b'same text'
                raise AssertionError('unexpected subprocess.check_output ' + repr(command))

            failure = None
            with patch.object(builder.tempfile, 'TemporaryDirectory', own_temp), \
                 patch.object(builder.subprocess, 'run', fake_run), \
                 patch.object(builder.subprocess, 'check_output', fake_output):
                try:
                    receipt = builder.verify_approved_process(evidence)
                except RuntimeError as error:
                    failure = str(error)
            assert accepted.read_bytes() == before
            assert (failure is None) == (mode == 'success')
            tests.append({'test': 'builder_' + mode, 'result': 'PASS',
                          'accepted_bytes_unchanged': True,
                          'expected_failure_observed': failure is not None})

    with own_temp(prefix='package-') as temporary:
        fixture = Path(temporary)
        process = fixture / 'task2/reports/process'
        assets = process / 'evidence/assets'
        assets.mkdir(parents=True)
        (process / 'main.tex').write_text('\\evidenceshot{selected}{title}{note}{0}{0}{0}{C1}')
        (process / 'Process_Report.pdf').write_bytes(b'accepted PDF fixture')
        (assets / 'selected.png').write_bytes(b'approved asset fixture')
        required = ['templates/latex/common/p2_cloud_sorbet_colors.tex',
                    'task2/scripts/build_reports.py', 'task2/reports/generated/sources.json',
                    'task2/docs/ENVIRONMENT_CHANGELOG.md']
        for name in required:
            target = fixture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('{}' if name.endswith('.json') else '% fixture\n')
        packager.ROOT = fixture

        def invoke(output):
            with patch.object(sys, 'argv', ['package_report_sources.py', '--output', str(output)]), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try:
                    packager.main()
                    return 0
                except SystemExit as error:
                    return error.code

        output = fixture / 'source.zip'
        assert invoke(output) == 0
        original = output.read_bytes()
        assert invoke(output) == 2
        assert output.read_bytes() == original
        tests.append({'test': 'package_existing_output_preserved', 'result': 'PASS'})
        (assets / 'private_unused.png').write_bytes(b'must not be published')
        extra_output = fixture / 'extra.zip'
        assert invoke(extra_output) == 2 and not extra_output.exists()
        tests.append({'test': 'package_rejects_unreferenced_asset_before_writing', 'result': 'PASS'})
        (assets / 'private_unused.png').unlink()
        (assets / 'selected.png').unlink()
        missing_output = fixture / 'missing.zip'
        assert invoke(missing_output) == 2 and not missing_output.exists()
        tests.append({'test': 'package_rejects_missing_asset_before_writing', 'result': 'PASS'})

    record = {'reviewer': 'Codex independent agent process_integration_verifier',
        'method': 'AST syntax parsing and isolated synthetic mocked guard tests; these are not actual report compilation or visual inspection.',
        'reviewed_scripts': [{'path': str(path.relative_to(root)),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                            for path in (builder_path, package_path)],
        'tests': tests, 'result': 'PASS',
        'limits': ['Only the Process builder branch is exercised; Experiment branch is not run.',
                   'Actual XeLaTeX/text/render receipts remain separate from synthetic guard tests.',
                   'This result does not grant Evidence Lock or GPT external review.']}
    destination = review / 'script_guard_checks.json'
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'report': str(destination.relative_to(root)), 'checks_passed': len(tests)}))


if __name__ == '__main__':
    main()
