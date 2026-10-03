"""Keep accepted Process material immutable and stop a generator rollback before TeX."""
import json
from pathlib import Path
import sys
import zipfile

import pytest
from task1.reports import build_process as reports


@pytest.fixture
def process_fixture(tmp_path, monkeypatch):
    report = tmp_path / 'task1/reports/process1'
    source = report / 'source'
    source.mkdir(parents=True)
    files = {
        'main.tex': r'\definecolor{Ink}{HTML}{2D3238}',
        'chapters/pages.tex': 'Accepted complete report pages',
        'content/evidence_units.json': '{"approved": true}',
        'content/closing_evidence.json': '{"box": [186, 68, 510, 263]}',
        'provenance/closing_crop_map.json': '{"image": "assets/crops/closing_user.png"}',
        'assets/crops/closing_user.png': 'closing native crop fixture',
        'assets/crops/example.png': 'accepted lossless crop bytes',
        'tools/make_diagrams.py': 'print("fixture diagram generator")\n',
        'tools/build_report.py': 'from pathlib import Path\nPath("chapters/pages.tex").write_text("obsolete draft")\n',
        'compile.sh': 'exit 91\n',
    }
    for relative, text in files.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    (report / 'fontconfig.conf').write_text('<fontconfig/>')
    approved = report / 'approved.pdf'
    approved.write_bytes(b'accepted PDF identity fixture')
    current = report / 'process1.pdf'
    current.write_bytes(approved.read_bytes())
    archive = report / 'approved.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        for relative in files:
            z.write(source / relative, 'Process_Report_Revised_Source/' + relative)
    palette = tmp_path / 'palette.tex'
    palette.write_text(files['main.tex'])
    config = {
        'canonical_pdf': str(approved.relative_to(tmp_path)),
        'canonical_zip': str(archive.relative_to(tmp_path)),
        'pdf_sha256': reports.sha(approved), 'zip_sha256': reports.sha(archive),
        'source_directory': 'source', 'archive_root': 'Process_Report_Revised_Source',
        'palette_authority': 'palette.tex', 'palette_aliases': {'Ink': 'Ink'},
        'report_dependencies': '.venv/process-report-build-deps',
        'current_reading_copy': str(current.relative_to(tmp_path)),
        'expected_pages': 77, 'user_acceptance': 'FIXTURE_ONLY',
    }
    (report / 'accepted-source.json').write_text(json.dumps(config))
    python = tmp_path / '.venv/bin/python'
    python.parent.mkdir(parents=True)
    python.symlink_to(sys.executable)
    monkeypatch.setattr(reports, 'ROOT', tmp_path)
    monkeypatch.setattr(reports, 'REPORT', report)
    return tmp_path, report, config


@pytest.mark.parametrize('damage', ['reference_hash', 'specification', 'crop', 'missing',
                                  'closing_crop_missing', 'closing_map_changed', 'closing_spec_changed',
                                  'extra', 'symlink', 'directory_symlink'])
def test_damaged_input_stops_before_any_build_command(process_fixture, monkeypatch, damage):
    root, report, config = process_fixture
    source = report / 'source'
    if damage == 'reference_hash':
        (report / 'approved.pdf').write_bytes(b'wrong approved report')
    elif damage == 'specification':
        (source / 'content/evidence_units.json').write_text('{"old_draft": true}')
    elif damage == 'crop':
        (source / 'assets/crops/example.png').write_bytes(b'replaced crop')
    elif damage == 'missing':
        (source / 'chapters/pages.tex').unlink()
    elif damage == 'closing_crop_missing':
        (source / 'assets/crops/closing_user.png').unlink()
    elif damage == 'closing_map_changed':
        (source / 'provenance/closing_crop_map.json').write_text('{"old_crop": true}')
    elif damage == 'closing_spec_changed':
        (source / 'content/closing_evidence.json').write_text('{"box": [186, 80, 506, 333]}')
    elif damage == 'extra':
        (source / 'old_main.tex').write_text('unapproved old entry')
    elif damage == 'symlink':
        (source / 'main.tex').unlink()
        (source / 'main.tex').symlink_to(root / 'palette.tex')
    else:
        (source / 'extra_directory').symlink_to(root, target_is_directory=True)
    current = (report / 'process1.pdf').read_bytes()
    monkeypatch.setattr(reports.subprocess, 'run', lambda *a, **k: pytest.fail('must reject before executing any build tool'))
    with pytest.raises(ValueError):
        reports.build(root / 'evidence')
    assert (report / 'process1.pdf').read_bytes() == current


def test_generator_reverting_accepted_body_is_blocked_before_compile(process_fixture, monkeypatch):
    root, report, config = process_fixture
    font_names = {'Noto Sans': 'NotoSans-Regular', 'Noto Sans:weight=200': 'NotoSans-ExtraBold',
                  'Noto Sans CJK SC': 'NotoSansCJKsc-Regular',
                  'Noto Sans CJK SC:weight=200': 'NotoSansCJKsc-Bold'}
    monkeypatch.setattr(reports.subprocess, 'check_output', lambda command, **kwargs: font_names[command[-1]])
    current = (report / 'process1.pdf').read_bytes()
    accepted_body = (report / 'source/chapters/pages.tex').read_bytes()
    with pytest.raises(ValueError, match='GENERATION_CHANGED_APPROVED_PAGES_OR_EVIDENCE'):
        reports.build(root / 'evidence', regenerate=True)
    receipt = json.loads((root / 'evidence/build_receipt.json').read_text())
    assert receipt['status'] == 'FAILED'
    assert [c['command'] for c in receipt['commands']] == [
        ['python', 'tools/make_diagrams.py'], ['python', 'tools/build_report.py']]
    assert all(c['exit_code'] == 0 for c in receipt['commands'])
    assert (report / 'source/chapters/pages.tex').read_bytes() == accepted_body
    assert (report / 'process1.pdf').read_bytes() == current
