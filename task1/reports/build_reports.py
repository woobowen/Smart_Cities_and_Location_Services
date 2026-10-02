"""Rebuild accepted Experiment and Process reports without executing experiments."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'task1/reports/experiment1'
DEFAULT_EVIDENCE = ROOT / 'task1/evidence/goal3/report_build/accepted'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(directory):
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(directory.rglob('*'))
            if p.is_file() and 'build' not in p.parts and '__pycache__' not in p.parts}


def pdf_details(pdf):
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
    return info, text, int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))


def compare_content(approved, rebuilt, expected_pages):
    original, actual = pdf_details(approved), pdf_details(rebuilt)
    if original[2] != expected_pages or actual[2] != expected_pages:
        raise ValueError('ACCEPTED_REPORT_PAGE_COUNT_CHANGED')
    if original[1] != actual[1]:
        raise ValueError('ACCEPTED_REPORT_TEXT_CHANGED; preserve approved content')
    for identity in ('吴博闻', '10245102410'):
        if identity not in actual[0] or identity not in actual[1].split('\f')[0]:
            raise ValueError('REPORT_COVER_OR_METADATA_IDENTITY_MISSING')
    return actual


def build(evidence, render=False):
    evidence = Path(evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    config = json.loads((REPORT / 'accepted-source.json').read_text())
    approved, archive = (ROOT / config[k] for k in ('canonical_pdf', 'canonical_zip'))
    if sha(approved) != config['pdf_sha256'] or sha(archive) != config['zip_sha256']:
        raise ValueError('ACCEPTED_REFERENCE_PAIR_HASH_MISMATCH')
    process_before = snapshot(ROOT / 'task1/reports/process1')
    sources = [REPORT / config['entry'], REPORT / 'build.sh']
    for sub in ('chapters', 'figures', 'source'):
        sources.extend(p for p in sorted((REPORT / sub).rglob('*')) if p.is_file())
    palette = ROOT / config['palette_authority']
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in sources + [palette]}
    with zipfile.ZipFile(archive) as supplied:
        for path in sources:
            relative = path.relative_to(REPORT).as_posix()
            if relative == 'source/p2_cloud_sorbet_colors.tex':
                continue  # The sole source adaptation routes to the shared palette.
            if path.read_bytes() != supplied.read('Experiment_Report_source/' + relative):
                raise ValueError('ACCEPTED_EDITABLE_SOURCE_CHANGED: ' + relative)
        colors = lambda s: dict(re.findall(r'\\definecolor\{([^}]+)\}\{HTML\}\{([A-Fa-f0-9]+)\}', s))
        if colors(palette.read_text()) != colors(supplied.read(
                'Experiment_Report_source/source/p2_cloud_sorbet_colors.tex').decode()):
            raise ValueError('PUBLIC_P2_PALETTE_DIFFERS_FROM_ACCEPTED_REPORT')
    env = os.environ.copy()
    isolated_tex = ROOT / '.venv/texmf'
    if isolated_tex.is_dir() and 'TEXMFHOME' not in env:
        env['TEXMFHOME'] = str(isolated_tex)
    receipt = {'classification': 'ACCEPTED_EXPERIMENT_REPORT_BUILD_NOT_METHOD_EXECUTION',
               'started_at': datetime.now(timezone.utc).isoformat(),
               'new_model_calls': 0, 'new_method_runs': 0,
               'source_sha256': source_hashes, 'canonical_pdf_sha256': sha(approved),
               'canonical_zip_sha256': sha(archive), 'render_dpi': 200 if render else None,
               'visual_inspection': 'NOT_PERFORMED_BY_BUILD_SCRIPT',
               'process_report_action': 'READ_ONLY_PROTECTION_CHECK',
               'texmfhome': '.venv/texmf' if env.get('TEXMFHOME') == str(isolated_tex) else 'caller-provided/default',
               'reports': []}
    with tempfile.TemporaryDirectory(prefix='accepted-experiment-report-') as work:
        work = Path(work)
        for source in sources + [palette]:
            if source.is_symlink():
                raise ValueError('REPORT_SOURCE_SYMLINK_REJECTED')
            target = work / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        cwd = work / REPORT.relative_to(ROOT)
        rebuilt = cwd / 'Experiment_Report.pdf'
        assert not rebuilt.exists() and not (cwd / 'build').exists()
        result = subprocess.run(['bash', 'build.sh'], cwd=cwd, env=env,
                                text=True, capture_output=True)
        (evidence / 'compile-output.txt').write_text(result.stdout + result.stderr)
        for log in (cwd / 'build').glob('*.log'):
            shutil.copyfile(log, evidence / (log.stem + '-log.txt'))
        receipt.update(command=['bash', 'build.sh'], compile_exit_code=result.returncode,
                       prebuilt_report_pdf_in_clean_directory=False)
        if result.returncode:
            (evidence / 'failed-build.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
            raise RuntimeError('ACCEPTED_SOURCE_COMPILE_FAILED; inspect compile-output.txt')
        log = (cwd / 'build/Experiment_Report.log').read_text(errors='replace')
        diagnostics = [line for line in log.splitlines() if re.search(
            r'^!|Missing character|undefined references|undefined citations|Overfull|LaTeX Font Warning|Rerun to', line)]
        if diagnostics:
            raise RuntimeError('UNRESOLVED_REPORT_DIAGNOSTICS: ' + repr(diagnostics))
        info, text, pages = compare_content(approved, rebuilt, config['expected_pages'])
        shutil.copyfile(rebuilt, evidence / 'rebuilt.pdf')
        (evidence / 'pdfinfo.txt').write_text(info)
        (evidence / 'experiment1_text.txt').write_text(text)
        texts = text.split('\f')
        if texts and not texts[-1].strip():
            texts.pop()
        (evidence / 'experiment1_pages.txt').write_text('\n'.join(
            f'===== PDF物理页 {n} =====\n{t}' for n, t in enumerate(texts, 1)))
        record = {'report': 'experiment1', 'pages': pages, 'newly_compiled_pdf': 'rebuilt.pdf',
                  'rebuilt_sha256': sha(rebuilt), 'current_reading_pdf': config['current_reading_copy'],
                  'reading_pdf_sha256': sha(approved), 'text_exact_match': True,
                  'unresolved_diagnostics': diagnostics,
                  'page_text_sha256': {str(n): hashlib.sha256(t.encode()).hexdigest()
                                       for n, t in enumerate(texts, 1)}}
        if render:
            from PIL import Image, ImageChops, ImageStat
            for name, pdf in (('approved', approved), ('rebuilt', rebuilt)):
                target = work / name
                target.mkdir()
                subprocess.run(['pdftoppm', '-r', '200', '-png', str(pdf), str(target / 'page')], check=True)
            rendered = sorted((work / 'rebuilt').glob('page-*.png'))
            if len(rendered) != pages:
                raise ValueError('RENDERED_PAGE_COUNT_MISMATCH')
            differences = []
            for page in rendered:
                with Image.open(page) as actual, Image.open(work / 'approved' / page.name) as expected:
                    if actual.size != expected.size:
                        raise ValueError('ACCEPTED_REPORT_PAGE_DIMENSIONS_CHANGED')
                    delta = ImageChops.difference(actual, expected)
                    differences.append({'page': page.name, 'pixels_equal': delta.getbbox() is None,
                        'mean_absolute_rgb_difference_0_255': sum(ImageStat.Stat(delta).mean) / 3})
            destination = evidence / 'render200'
            destination.mkdir(exist_ok=True)
            for page in rendered:
                shutil.copyfile(page, destination / page.name)
            record['render'] = {'dpi': 200, 'pages': pages,
                                'all_page_pixels_equal_approved': all(d['pixels_equal'] for d in differences),
                                'page_pixel_comparison': differences,
                                'page_sha256': {p.name: sha(p) for p in rendered},
                                'visual_review_status': 'REQUIRES_ACTUAL_REVIEW'}
        current = ROOT / config['current_reading_copy']
        if not current.exists() or sha(current) != sha(approved):
            temporary = current.with_suffix('.pdf.tmp')
            if temporary.exists():
                raise FileExistsError('CURRENT_REPORT_TEMP_EXISTS')
            shutil.copyfile(approved, temporary)
            os.replace(temporary, current)
        receipt['reports'].append(record)
    if snapshot(ROOT / 'task1/reports/process1') != process_before:
        raise ValueError('PROCESS_REPORT_CHANGED_DURING_EXPERIMENT_BUILD')
    if any(sha(ROOT / p) != h for p, h in source_hashes.items()):
        raise ValueError('REPORT_SOURCE_CHANGED_DURING_BUILD')
    if sha(approved) != config['pdf_sha256'] or sha(archive) != config['zip_sha256']:
        raise ValueError('ACCEPTED_REFERENCE_CHANGED_DURING_BUILD')
    receipt.update(status='VERIFIED', process_report_unchanged=True,
                   finished_at=datetime.now(timezone.utc).isoformat())
    (evidence / 'build_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', choices=('experiment', 'process', 'all'), default='all',
                        help='Select accepted report sources; default builds both.')
    parser.add_argument('--regenerate', action='store_true',
                        help='Regenerate the accepted Process diagrams/pages before compiling.')
    parser.add_argument('--render', action='store_true', help='Compare every page at 200 dpi.')
    parser.add_argument('--evidence-output', type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args()
    if args.regenerate and args.report == 'experiment':
        parser.error('--regenerate applies to the Process source only')
    selected = ('experiment', 'process') if args.report == 'all' else (args.report,)
    receipts = {}
    for name in selected:
        destination = args.evidence_output / name if len(selected) > 1 else args.evidence_output
        if name == 'experiment':
            receipts[name] = build(destination, args.render)
        else:
            from task1.reports.build_process import build as build_process
            receipts[name] = build_process(destination, render=args.render,
                                           regenerate=args.regenerate)
    summary = {'status': 'VERIFIED', 'selected_reports': list(selected),
               'new_model_calls': 0, 'new_method_runs': 0,
               'receipt_paths': {name: str((args.evidence_output / name if len(selected) > 1
                                          else args.evidence_output) / 'build_receipt.json')
                                 for name in selected}}
    if len(selected) > 1:
        (args.evidence_output / 'build_receipt.json').write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    # Direct file invocation and python -m use the same package imports.
    import sys
    sys.path.insert(0, str(ROOT))
    main()
