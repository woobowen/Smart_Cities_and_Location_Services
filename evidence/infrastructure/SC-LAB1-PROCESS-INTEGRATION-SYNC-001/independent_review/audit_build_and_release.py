"""Independent read-only final release and rendered build audit.

Writes only this review directory. It does not compile, sync, edit reports or run science.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from audit_inputs import ROOT, OUT, BASELINE

sys.path.insert(0, str(ROOT / '.venv/process-report-build-deps'))
import fitz
from PIL import Image, ImageChops, ImageStat

TASK = OUT.parent
WORK = Path.home() / '.local/state/codex-task-work/SC-LAB1-PROCESS-INTEGRATION-SYNC-001'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def snapshot(paths):
    result = {}
    for path in sorted(paths):
        value = path.lstat()
        result[str(path.relative_to(ROOT))] = {
            'type': stat.S_IFMT(value.st_mode), 'mtime_ns': value.st_mtime_ns,
            'size': value.st_size, 'sha256': digest(path) if stat.S_ISREG(value.st_mode) else None,
        }
    return result


def main():
    declaration = ROOT / 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
    manifest = json.loads(declaration.read_text())
    watched = {declaration, declaration.parent / 'SOURCE_MANIFEST.md', declaration.parent / 'UPLOAD_INSTRUCTIONS.md'}
    watched.update(ROOT / r['active_path'] for r in manifest['sources'])
    watched.update((ROOT / 'releases/chatgpt-project-sources').iterdir())
    watched.add(ROOT / 'releases/chatgpt-project-sources')
    watched.add(declaration.parent)
    before = snapshot(watched)
    sync_script = 'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py'
    commands = []
    for mode in ('--plan', '--check'):
        command = [str(ROOT / '.venv/bin/python'), sync_script, mode]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        log = 'actual_sync_' + mode[2:] + '.txt'
        (OUT / log).write_text(result.stdout + result.stderr)
        after = snapshot(watched)
        commands.append({'command': command, 'exit_code': result.returncode, 'log': log,
                         'unchanged_content_type_size_mtime': before == after})
        assert result.returncode == 0 and before == after
    release = {'commands': commands, 'watched_files_and_directories': len(watched),
               'before': before, 'after': snapshot(watched),
               'user_ui_status': 'USER_REPORTED_UPDATED',
               'input_baseline_identity_source': 'audit_inputs.BASELINE independently transcribed from user prompt'}
    (OUT / 'actual_sync_readonly.json').write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n')

    approved = ROOT / 'Process_Report_Revised.pdf'
    route_a = WORK / 'route-A-final/Process_Report_Revised.pdf'
    route_b = WORK / 'route-B-final/Process_Report_Revised.pdf'
    observations = json.loads((OUT / 'visual_observations.json').read_text())
    viewed = {r['page']: r for r in observations['pages']}
    checks = []
    with fitz.open(approved) as reference, fitz.open(route_a) as document_a, fitz.open(route_b) as document_b:
        assert len(reference) == len(document_a) == len(document_b) == 77
        for index, page in enumerate(document_b):
            n = index + 1
            expected_page = reference[index]
            actual_pix = page.get_pixmap(dpi=200, alpha=False)
            expected_pix = expected_page.get_pixmap(dpi=200, alpha=False)
            actual_im = Image.frombytes('RGB', [actual_pix.width, actual_pix.height], actual_pix.samples)
            expected_im = Image.frombytes('RGB', [expected_pix.width, expected_pix.height], expected_pix.samples)
            delta = ImageChops.difference(expected_im, actual_im)
            viewed_path = WORK / f'route-B-final/review/render_200dpi/p{n:03}.png'
            supplied_render = Image.open(viewed_path).convert('RGB')
            text_a, text_b, text_r = document_a[index].get_text(), page.get_text(), expected_page.get_text()
            fields = ('digest', 'width', 'height', 'bbox', 'transform')
            images_r = [{k: r[k].hex() if isinstance(r[k], bytes) else r[k] for k in fields} for r in expected_page.get_image_info(hashes=True)]
            images_b = [{k: r[k].hex() if isinstance(r[k], bytes) else r[k] for k in fields} for r in page.get_image_info(hashes=True)]
            item = {'page': n, 'page_dimensions_match': page.rect == expected_page.rect == document_a[index].rect,
                    'page_text_exact_A_B_approved': text_a == text_b == text_r,
                    'pixels_equal': delta.getbbox() is None,
                    'mean_absolute_rgb_difference_0_255': sum(ImageStat.Stat(delta).mean) / 3,
                    'maximum_channel_difference': max(high for low, high in delta.getextrema()),
                    'differing_pixel_count': sum(1 for rgb in delta.getdata() if any(rgb)),
                    'render_dimensions': [actual_pix.width, actual_pix.height],
                    'viewed_render_sha256': digest(viewed_path),
                    'saved_render_matches_independent_rerender': supplied_render.tobytes() == actual_im.tobytes(),
                    'embedded_image_digest_dimensions_positions_exact': images_r == images_b,
                    'actually_opened_by_independent_reviewer': n in viewed}
            checks.append(item)
            assert item['page_dimensions_match'] and item['page_text_exact_A_B_approved']
            assert item['saved_render_matches_independent_rerender'] and item['embedded_image_digest_dimensions_positions_exact']
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'renderer': 'PyMuPDF ' + fitz.VersionBind, 'dpi': 200,
              'approved_pdf_sha256': digest(approved), 'route_A_sha256': digest(route_a),
              'route_B_sha256': digest(route_b), 'route_A_B_bytes_identical': route_a.read_bytes() == route_b.read_bytes(),
              'page_count': len(checks), 'pages': checks,
              'pixel_difference_pages': [r['page'] for r in checks if not r['pixels_equal']],
              'actually_viewed_pages': sorted(viewed),
              'visual_role': 'Actual page opens listed in visual_observations.json; other pages programmatically compared only by this context.'}
    assert result['approved_pdf_sha256'] == BASELINE['Process_Report_Revised.pdf']
    assert result['route_B_sha256'] == observations['pdf_sha256']
    assert result['route_A_B_bytes_identical']
    (OUT / 'independent_pdf_comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')

    old = json.loads((ROOT / 'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/report/normal-build-1/build_receipt.json').read_text())
    new = json.loads((TASK / 'unified_build/experiment/build_receipt.json').read_text())
    # The receipt structure is inspected separately; preserve the independently read artifacts here.
    (OUT / 'experiment_receipt_hashes.json').write_text(json.dumps({
        'old_receipt_sha256': digest(ROOT / 'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/report/normal-build-1/build_receipt.json'),
        'new_receipt_sha256': digest(TASK / 'unified_build/experiment/build_receipt.json'),
        'old_report_records': old['reports'], 'new_report_records': new['reports'],
        'role': 'Inherited scope comparison, not a new acceptance or numerical run',
    }, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actual_readonly_checks': commands, 'process_pages': len(checks),
                      'pixel_difference_pages': result['pixel_difference_pages'],
                      'actual_visual_pages': len(viewed), 'A_B_identical': result['route_A_B_bytes_identical']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
