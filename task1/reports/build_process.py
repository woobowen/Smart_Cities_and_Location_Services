"""Reproduce the accepted Process report in isolation, without running experiments."""
from pathlib import Path, PurePosixPath
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'task1/reports/process1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_details(path):
    info = subprocess.check_output(['pdfinfo', str(path)], text=True)
    text = subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)
    return info, text, int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))


def verify_source(config):
    approved, archive = (ROOT / config[k] for k in ('canonical_pdf', 'canonical_zip'))
    if sha(approved) != config['pdf_sha256'] or sha(archive) != config['zip_sha256']:
        raise ValueError('ACCEPTED_PROCESS_REFERENCE_PAIR_HASH_MISMATCH')
    source = REPORT / config['source_directory']
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('ACCEPTED_SOURCE_SYMLINK_REJECTED')
    hashes = {}
    with zipfile.ZipFile(archive) as supplied:
        if supplied.testzip() is not None:
            raise ValueError('ACCEPTED_SOURCE_ZIP_CRC_FAILURE')
        names = set()
        for member in supplied.infolist():
            path = PurePosixPath(member.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in member.filename
                    or member.filename in names or (member.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('UNSAFE_ACCEPTED_ARCHIVE_MEMBER')
            names.add(member.filename)
            relative = path.relative_to(config['archive_root'])
            if member.is_dir():
                continue
            local = source.joinpath(*relative.parts)
            if local.is_symlink() or not local.is_file():
                raise ValueError('ACCEPTED_SOURCE_MISSING_OR_SYMLINK: ' + str(relative))
            digest = hashlib.sha256(supplied.read(member)).hexdigest()
            if sha(local) != digest:
                raise ValueError('ACCEPTED_EDITABLE_SOURCE_CHANGED: ' + str(relative))
            hashes[str(relative)] = digest
    actual = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()
              and '__pycache__' not in p.parts}
    if actual != set(hashes):
        raise ValueError('ACCEPTED_SOURCE_MEMBER_SET_CHANGED')
    colors = lambda text: dict(re.findall(
        r'\\definecolor\{([^}]+)\}\{HTML\}\{([A-Fa-f0-9]+)\}', text))
    portable = colors((source / 'main.tex').read_text())
    canonical = colors((ROOT / config['palette_authority']).read_text())
    if any(portable[k] != canonical[v] for k, v in config['palette_aliases'].items()):
        raise ValueError('PORTABLE_P2_COLORS_DIFFER_FROM_AUTHORITY')
    return approved, archive, source, hashes


def build(evidence, render=False, regenerate=False):
    evidence = Path(evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    config = json.loads((REPORT / 'accepted-source.json').read_text())
    approved, archive, source, source_hashes = verify_source(config)
    deps = ROOT / config['report_dependencies']
    env = os.environ.copy()
    env['PATH'] = str(ROOT / '.venv/bin') + os.pathsep + env.get('PATH', '')
    env['PYTHONPATH'] = str(deps) + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['FONTCONFIG_FILE'] = str(REPORT / 'fontconfig.conf')
    if (ROOT / '.venv/texmf').is_dir() and 'TEXMFHOME' not in env:
        env['TEXMFHOME'] = str(ROOT / '.venv/texmf')
    expected_fonts = {
        'Noto Sans': 'NotoSans-Regular',
        'Noto Sans:weight=200': 'NotoSans-ExtraBold',
        'Noto Sans CJK SC': 'NotoSansCJKsc-Regular',
        'Noto Sans CJK SC:weight=200': 'NotoSansCJKsc-Bold',
    }
    font_selection = {pattern: subprocess.check_output(
        ['fc-match', '-f', '%{postscriptname}', pattern], env=env, text=True)
        for pattern in expected_fonts}
    if font_selection != expected_fonts:
        raise ValueError('ACCEPTED_PROCESS_FONT_SELECTION_CHANGED: ' + repr(font_selection))
    receipt = {
        'classification': 'ACCEPTED_PROCESS_REPORT_BUILD_NOT_METHOD_EXECUTION',
        'started_at': datetime.now(timezone.utc).isoformat(),
        'canonical_pdf_sha256': sha(approved), 'canonical_zip_sha256': sha(archive),
        'source_sha256': source_hashes, 'commands': [], 'reports': [],
        'new_model_calls': 0, 'new_method_runs': 0,
        'route': 'B_FULL_GENERATION' if regenerate else 'A_STATIC_COMPILE',
        'visual_inspection': 'NOT_PERFORMED_BY_BUILD_SCRIPT',
        'user_acceptance': config['user_acceptance'],
        'evidence_lock': 'NOT_ASSIGNED_BY_ENGINEERING_BUILD',
        'texmfhome': '.venv/texmf' if env.get('TEXMFHOME') == str(ROOT / '.venv/texmf') else 'caller-provided/default',
        'python_dependencies': config['report_dependencies'],
        'fontconfig': 'task1/reports/process1/fontconfig.conf',
        'fontconfig_sha256': sha(REPORT / 'fontconfig.conf'),
        'font_selection': font_selection,
    }
    try:
        with tempfile.TemporaryDirectory(prefix='accepted-process-report-') as work_name:
            work = Path(work_name)
            cwd = work / 'source'
            shutil.copytree(source, cwd)
            for path in (cwd / 'Process_Report_Revised.pdf', cwd / 'build', cwd / 'review'):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            (cwd / 'review').mkdir()
            receipt['prebuilt_report_pdf_in_clean_directory'] = False

            def run(command):
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
                number = len(receipt['commands']) + 1
                log = f'command-{number:02}.txt'
                (evidence / log).write_text(result.stdout + result.stderr)
                receipt['commands'].append({'command': command, 'exit_code': result.returncode, 'log': log})
                if result.returncode:
                    raise RuntimeError('PROCESS_BUILD_COMMAND_FAILED: ' + ' '.join(command))

            if regenerate:
                run(['python', 'tools/make_diagrams.py'])
                run(['python', 'tools/build_report.py'])
                generated_changes = [p for p, h in source_hashes.items()
                    if p.startswith(('assets/crops/', 'chapters/', 'content/'))
                    or p in ('main.tex', 'provenance/page_map.json', 'provenance/crop_map.json',
                             'provenance/arrow_map.json', 'provenance/input_images.json')]
                if any(sha(cwd / p) != source_hashes[p] for p in generated_changes):
                    raise ValueError('PROCESS_GENERATION_CHANGED_APPROVED_PAGES_OR_EVIDENCE')
                receipt['generated_content_and_evidence_exact_match'] = True
            try:
                run(['bash', 'compile.sh'])
            finally:
                for log in (cwd / 'build').glob('*.log'):
                    shutil.copyfile(log, evidence / (log.name + '.txt'))
            rebuilt = cwd / 'Process_Report_Revised.pdf'
            shutil.copyfile(rebuilt, evidence / 'rebuilt.pdf')
            original = pdf_details(approved)
            actual = pdf_details(rebuilt)
            if original[2] != config['expected_pages'] or actual[2] != config['expected_pages']:
                raise ValueError('ACCEPTED_PROCESS_PAGE_COUNT_CHANGED')
            (evidence / 'pdfinfo.txt').write_text(actual[0])
            (evidence / 'page_text.txt').write_text(actual[1])
            original_pages, actual_pages = original[1].split('\f'), actual[1].split('\f')
            text_checks = [{'page': n + 1, 'exact_match': expected == rebuilt_text,
                            'whitespace_normalized_match': ' '.join(expected.split()) == ' '.join(rebuilt_text.split()),
                            'approved_text_sha256': hashlib.sha256(expected.encode()).hexdigest(),
                            'rebuilt_text_sha256': hashlib.sha256(rebuilt_text.encode()).hexdigest()}
                           for n, (expected, rebuilt_text) in enumerate(zip(original_pages, actual_pages))
                           if expected.strip() or rebuilt_text.strip()]
            receipt['page_text_comparison'] = text_checks
            if len(original_pages) != len(actual_pages) or not all(p['whitespace_normalized_match'] for p in text_checks):
                raise ValueError('ACCEPTED_PROCESS_PAGE_TEXT_CHANGED')
            diagnostics = [line for line in (cwd / 'build/main.log').read_text(errors='replace').splitlines()
                          if re.search(r'^!|Missing character|Undefined control sequence|Overfull|undefined references|undefined citations|Rerun to', line)]
            if diagnostics:
                raise ValueError('UNRESOLVED_PROCESS_DIAGNOSTICS: ' + repr(diagnostics))
            record = {'report': 'process1', 'pages': actual[2], 'newly_compiled_pdf': 'rebuilt.pdf',
                      'rebuilt_sha256': sha(rebuilt), 'reading_pdf_sha256': sha(approved),
                      'current_reading_pdf': config['current_reading_copy'],
                      'text_exact_match': original[1] == actual[1],
                      'text_whitespace_normalized_match': True,
                      'bytes_equal_approved': sha(rebuilt) == sha(approved),
                      'unresolved_diagnostics': diagnostics}
            if regenerate:
                run(['python', 'tools/render_review.py'])
                run(['python', 'tools/audit_report.py'])
                audit = json.loads((cwd / 'provenance/artifact_audit.json').read_text())
                if not audit['all_checks_pass']:
                    raise ValueError('PROCESS_ARTIFACT_CHECK_FAILED')
                shutil.copyfile(cwd / 'provenance/artifact_audit.json', evidence / 'upstream_author_check_replayed.json')
                receipt['upstream_check_role'] = 'REPLAYED_AUTHOR_CHECK_NOT_INDEPENDENT_REVIEW'
            if render:
                # Explicit report-only dependency path; no scientific modules run here.
                sys.path.insert(0, str(deps))
                import fitz
                from PIL import Image, ImageChops, ImageStat
                destination = evidence / 'render200'
                destination.mkdir(exist_ok=True)
                differences = []
                with fitz.open(approved) as expected_doc, fitz.open(rebuilt) as actual_doc:
                    for n, page in enumerate(actual_doc):
                        expected_page = expected_doc[n]
                        if page.rect != expected_page.rect:
                            raise ValueError('PROCESS_PAGE_DIMENSIONS_CHANGED')
                        expected_pix = expected_page.get_pixmap(dpi=200, alpha=False)
                        actual_pix = page.get_pixmap(dpi=200, alpha=False)
                        actual_pix.save(destination / f'p{n + 1:03}.png')
                        expected_im = Image.frombytes('RGB', [expected_pix.width, expected_pix.height], expected_pix.samples)
                        actual_im = Image.frombytes('RGB', [actual_pix.width, actual_pix.height], actual_pix.samples)
                        delta = ImageChops.difference(expected_im, actual_im)
                        differences.append({'page': n + 1, 'pixels_equal': delta.getbbox() is None,
                            'mean_absolute_rgb_difference_0_255': sum(ImageStat.Stat(delta).mean) / 3})
                record['render'] = {'dpi': 200, 'renderer': 'PyMuPDF', 'pages': actual[2],
                                    'page_pixel_comparison': differences,
                                    'all_page_pixels_equal_approved': all(d['pixels_equal'] for d in differences),
                                    'visual_review_status': 'REQUIRES_ACTUAL_REVIEW'}
            receipt['reports'].append(record)
            # Keep the reading copy tied to user approval, independently of PDF metadata changes.
            current = ROOT / config['current_reading_copy']
            if not current.exists() or sha(current) != config['pdf_sha256']:
                temporary = current.with_suffix('.pdf.tmp')
                if temporary.exists():
                    raise FileExistsError('CURRENT_PROCESS_TEMP_EXISTS')
                shutil.copyfile(approved, temporary)
                os.replace(temporary, current)
        verify_source(config)
        receipt.update(status='VERIFIED', finished_at=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        receipt.update(status='FAILED', error=str(error), finished_at=datetime.now(timezone.utc).isoformat())
        (evidence / 'build_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
        raise
    (evidence / 'build_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--regenerate', action='store_true')
    parser.add_argument('--evidence-output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.evidence_output, args.render, args.regenerate)
    print(json.dumps({'status': result['status'], 'route': result['route'],
                      'pages': result['reports'][0]['pages'], 'new_method_runs': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
