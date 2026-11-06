"""Read-only integration audit; private archive is supplied explicitly at runtime."""
import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from PIL import Image


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--baseline', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    review = Path(__file__).resolve().parent
    expected_pdf = 'c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f'
    expected_zip = 'f73432aef93abdad0c37757df03b13811ab0beb1b508f700562bb0edada1c55a'
    pdf = root / 'task2/reports/process/Process_Report.pdf'
    folder = pdf.parent
    record = {'reviewer': 'Codex independent agent process_integration_verifier',
              'baseline': args.baseline, 'recorded_utc': datetime.now(timezone.utc).isoformat()}
    with zipfile.ZipFile(args.archive) as archive:
        record['archive_sha256'] = sha(args.archive.read_bytes())
        record['archive_sha_matches_user'] = record['archive_sha256'] == expected_zip
        record['archive_crc_ok'] = archive.testzip() is None
        record['archive_unsafe_paths'] = [name for name in archive.namelist()
            if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or '\\' in name]
        record['pdf_sha256'] = sha(pdf.read_bytes())
        record['pdf_sha_matches_user_and_archive'] = (
            record['pdf_sha256'] == expected_pdf and
            pdf.read_bytes() == archive.read('task2/reports/process/main.pdf'))
        tex = []
        replacements = {
            '../../../evidence/crops/': 'evidence/assets/',
            '../../../evidence/codex_question_original.png': 'evidence/assets/codex_question_original.png'}
        for name in archive.namelist():
            if not (name.startswith('task2/reports/process/') and name.endswith('.tex')):
                continue
            inbound = archive.read(name)
            actual = (root / name).read_bytes()
            adapted = inbound
            if name.endswith('/main.tex') or name.endswith('/evidence/03_license.tex'):
                for old, new in replacements.items():
                    adapted = adapted.replace(old.encode(), new.encode())
            tex.append({'path': name, 'inbound_sha256': sha(inbound),
                        'installed_sha256': sha(actual), 'exact_inbound_bytes': inbound == actual,
                        'only_allowed_path_adaptations': actual == adapted})
        record['tex'] = tex
        texts = '\n'.join(path.read_text() for path in folder.rglob('*.tex'))
        refs = {name + '.png' for name in re.findall(r'\\evidenceshot\{([^#}]+)\}', texts)}
        refs.update(Path(name).name for name in re.findall(
            r'\\includegraphics(?:\[[^\]]*\])?\{([^#}]+\.png)\}', texts))
        assets = {path.name: path for path in (folder / 'evidence/assets').glob('*.png')}
        record['asset_reference_set_equal_actual'] = refs == set(assets)
        record['unreferenced_assets'] = sorted(set(assets) - refs)
        record['missing_assets'] = sorted(refs - set(assets))
        asset_records = []
        for name, path in sorted(assets.items()):
            member = 'evidence/' + ('' if name == 'codex_question_original.png' else 'crops/') + name
            asset_records.append({'path': str(path.relative_to(root)), 'sha256': sha(path.read_bytes()),
                                  'exact_archive_bytes': path.read_bytes() == archive.read(member)})
        record['assets'] = asset_records
        record['published_asset_count'] = len(assets)
        image_dir = review / 'build/embedded_images'
        image_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['pdfimages', '-png', str(pdf), str(image_dir / 'image')], check=True)
        embedded = {}
        for path in image_dir.glob('image-*.png'):
            with Image.open(path) as image:
                embedded[path.name] = (image.size, sha(image.convert('RGB').tobytes()))
        matches = []
        for name, path in sorted(assets.items()):
            with Image.open(path) as image:
                identity = (image.size, sha(image.convert('RGB').tobytes()))
            matches.append({'asset': name, 'matching_pdf_images': sorted(
                key for key, value in embedded.items() if value == identity)})
        record['actual_pdf_embedded_image_count'] = len(embedded)
        record['assets_match_embedded_pdf_pixels'] = matches
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    record['pages'] = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    pdftext = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
    record['removed_appendix_absent_from_source_and_pdf_text'] = (
        '\\appendix' not in texts and '视频证据的来源、裁切与复现' not in texts and
        '视频证据的来源、裁切与复现' not in pdftext)
    frozen_roots = ('templates/', 'task2/reports/experiment/', 'task2/reports/generated/',
                    'task2/src/', 'task2/results/', 'task2/public_results/', 'task2/figures/',
                    'task2/diagrams/', 'task2/tests/', 'task2/notebooks/')
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', args.baseline],
                                    cwd=root, text=True).splitlines()
    frozen = [name for name in names if name.startswith(frozen_roots) or
              name == 'task2/reports/common.tex' or
              (name.startswith('task2/scripts/') and Path(name).name not in
               ('build_reports.py', 'package_report_sources.py'))]
    changed = []
    for name in frozen:
        original = subprocess.check_output(['git', 'show', args.baseline + ':' + name], cwd=root)
        current = root / name
        if not current.is_file() or current.read_bytes() != original:
            changed.append(name)
    record['frozen_files_checked'] = len(frozen)
    record['frozen_files_changed'] = changed
    historical = folder / 'history/20261105_8page_handoff/Process_Report_Technical_Handoff_20261105_8p.pdf'
    old = subprocess.check_output(['git', 'show', args.baseline + ':task2/reports/process/Process_Report.pdf'], cwd=root)
    record['historical_pdf_exact_baseline_bytes'] = historical.read_bytes() == old
    record['historical_pdf_sha256'] = sha(historical.read_bytes())
    record['historical_pages'] = int(re.search(r'^Pages:\s+(\d+)', subprocess.check_output(
        ['pdfinfo', str(historical)], text=True), re.M).group(1))
    record['scope_limitations'] = [
        'No new algorithm run, model training or evaluation was executed.',
        'No independent Evidence Master Lock or GPT external review is granted.',
        'No original video was supplied or reviewed; raw archive material remains private.',
        'This audit compares integration against the exact user-pinned archive, not an unavailable pre-removal full approved report.',
        'Rendering/compiler diagnosis and final staged publication review are recorded separately.']
    destination = review / 'integration_audit.json'
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'report': str(destination.relative_to(root)), 'pdf_sha_matches': record['pdf_sha_matches_user_and_archive'],
          'tex_checked': len(tex), 'tex_allowed': all(row['only_allowed_path_adaptations'] for row in tex),
          'assets': len(assets), 'asset_set_exact': record['asset_reference_set_equal_actual'],
          'all_asset_bytes_exact': all(row['exact_archive_bytes'] for row in asset_records),
          'all_assets_embedded': all(len(row['matching_pdf_images']) == 1 for row in matches),
          'frozen_files_checked': len(frozen), 'frozen_changed': changed,
          'history_exact': record['historical_pdf_exact_baseline_bytes']}))


if __name__ == '__main__':
    main()
