"""Actual same-environment old build and scoped render/figure regression."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
SOURCE = ROOT / 'task1/reports/process1/source'
HISTORY = ROOT / 'reports/process-report/experiment1-revised/history/accepted-20261002'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def comparison(before, after):
    rows = []
    with fitz.open(before) as a, fitz.open(after) as b:
        assert len(a) == len(b) == 77
        for i, (x, y) in enumerate(zip(a, b), 1):
            assert x.rect == y.rect and x.get_text() == y.get_text(), i
            px, py = x.get_pixmap(dpi=200, alpha=False), y.get_pixmap(dpi=200, alpha=False)
            ax = np.frombuffer(px.samples, np.uint8).reshape(px.height, px.width, px.n)
            ay = np.frombuffer(py.samples, np.uint8).reshape(py.height, py.width, py.n)
            different = np.any(ax != ay, axis=2); ys, xs = np.nonzero(different)
            rows.append({'page': i, 'text_exact': True, 'geometry_exact': True,
                'render_pixels_equal': not bool(len(xs)), 'changed_pixels': len(xs),
                'difference_bbox_pixels': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)] if len(xs) else None})
    return rows


def main():
    env = os.environ.copy()
    env.update(FONTCONFIG_FILE=str(ROOT / 'task1/reports/process1/fontconfig.conf'),
               TEXMFHOME=str(ROOT / '.venv/texmf'))
    env['PATH'] = str(ROOT / '.venv/bin') + os.pathsep + env['PATH']
    env['PYTHONPATH'] = str(ROOT / '.venv/process-report-build-deps')
    out = EV / 'builds/same-environment-old'; out.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='sc-old-process-baseline-') as temp:
        work = Path(temp)
        with zipfile.ZipFile(HISTORY / 'Process_Report_Revised_LaTeX_Source.zip') as z:
            z.extractall(work)
        source = work / 'Process_Report_Revised_Source'
        (source / 'Process_Report_Revised.pdf').unlink()
        for name in ('build', 'review'):
            if (source / name).exists(): shutil.rmtree(source / name)
        assert not (source / 'Process_Report_Revised.pdf').exists()
        p = subprocess.run(['bash', 'compile.sh'], cwd=source, env=env, capture_output=True, text=True)
        (out / 'command-01.txt').write_text(p.stdout+p.stderr)
        for path in (source / 'build').glob('*.log'): shutil.copyfile(path, out / (path.name+'.txt'))
        assert p.returncode == 0
        shutil.copyfile(source / 'Process_Report_Revised.pdf', out / 'rebuilt.pdf')
    original = SOURCE / 'Process_Report_Revised.pdf'
    current = EV / 'builds/route-A/rebuilt.pdf'
    full = EV / 'builds/route-B/rebuilt.pdf'
    old_actual = out / 'rebuilt.pdf'
    input_pair = comparison(HISTORY / 'Process_Report_Revised.pdf', original)
    environment_control = comparison(HISTORY / 'Process_Report_Revised.pdf', old_actual)
    old_to_new_environment = comparison(old_actual, current)
    new_environment = comparison(original, current)
    assert [r['page'] for r in input_pair if not r['render_pixels_equal']] == [76]
    assert [r['page'] for r in old_to_new_environment if not r['render_pixels_equal']] == [76]
    assert all(a == b for a,b in zip(environment_control, new_environment)), 'Environment differences must be demonstrated, not inferred by page number'
    assert sha(current) == sha(full), 'Static/full route difference'
    bbox = old_to_new_environment[75]['difference_bbox_pixels']
    assert bbox[0] >= 108 and bbox[1] >= 580 and bbox[2] <= 1188 and bbox[3] <= 1436
    figures = []
    for supplied in sorted((SOURCE / 'figures').glob('*.pdf')):
        generated = EV / 'builds/route-B/regenerated_figures' / supplied.name
        with fitz.open(supplied) as a, fitz.open(generated) as b:
            x, y = a[0], b[0]
            words_a, words_b = x.get_text('words'), y.get_text('words')
            words_exact = [w[4] for w in words_a] == [w[4] for w in words_b]
            max_word_delta = max((abs(u-v) for wa,wb in zip(words_a, words_b) for u,v in zip(wa[:4], wb[:4])), default=0.) if len(words_a)==len(words_b) else None
            px, py = x.get_pixmap(dpi=200, alpha=False), y.get_pixmap(dpi=200, alpha=False)
            pixels_equal = px.width == py.width and px.height == py.height and px.samples == py.samples
            native_exact = all((SOURCE / 'figures' / (supplied.stem+ext)).read_bytes() ==
                (generated.parent / (supplied.stem+ext)).read_bytes() for ext in ('.svg', '.drawio'))
            figure = {'figure': supplied.stem, 'supplied_sha256': sha(supplied),
                'generated_sha256': sha(generated), 'native_svg_drawio_exact': native_exact,
                'text_words_exact': words_exact, 'max_word_bbox_delta_points': max_word_delta,
                'page_geometry_exact': x.rect == y.rect, 'standalone_200dpi_pixels_equal': pixels_equal,
                'supplied_producer': a.metadata.get('producer'), 'generated_producer': b.metadata.get('producer')}
            figures.append(figure)
            assert native_exact and words_exact and x.rect == y.rect and max_word_delta is not None and max_word_delta < .01
            assert pixels_equal, 'Standalone figure must be checked, not only its Producer'
    result = {'status': 'PASS', 'scope': 'ENGINEERING_COMPILE_AND_SAME_ENVIRONMENT_REGRESSION',
        'old_baseline_prebuilt_main_pdf_removed': True, 'old_compile_command': ['bash', 'compile.sh'],
        'old_compile_exit_code': 0, 'old_rebuilt_sha256': sha(old_actual),
        'new_route_A_sha256': sha(current), 'new_route_B_sha256': sha(full),
        'new_input_pdf_sha256': sha(original), 'new_build_byte_identical_to_input': False,
        'input_old_new_200dpi': input_pair, 'old_input_to_old_same_environment_build': environment_control,
        'same_environment_old_to_new': old_to_new_environment, 'new_input_to_new_build': new_environment,
        'environment_difference_control_exact': True, 'figure_checks': figures,
        'conclusion': 'Both original pair and same-environment old/new build change only the authorized p76 image rectangle. WSL inherited six-page vector/font rounding is identical in old and new controls. All six regenerated standalone diagrams are text/geometry/pixel equivalent.',
        'new_model_calls': 0, 'new_trajectory_runs': 0, 'visual_inspection': 'SEPARATE_ACTUAL_VIEW_RECORD'}
    (EV / 'report_environment_comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'same_environment_changed_pages': [76],
                      'environment_pages': [r['page'] for r in environment_control if not r['render_pixels_equal']],
                      'figures': len(figures)}, ensure_ascii=False))


if __name__ == '__main__': main()
