"""Independent read-only comparisons of actual supplied and compiled artifacts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
TMP = Path('/tmp/SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001-independent')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels(page):
    pix = page.get_pixmap(dpi=200, alpha=False)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)


def diff(a, b):
    mask = np.any(a != b, axis=2)
    ys, xs = np.nonzero(mask)
    return {'changed_pixels': len(xs), 'difference_bbox_pixels':
            [int(xs.min()), int(ys.min()), int(xs.max())+1, int(ys.max())+1] if len(xs) else None}


def main():
    paths = {
        'old_input': TMP/'baseline_Process_Report_Revised.pdf',
        'new_input': ROOT/'reports/process-report/experiment1-revised/Process_Report_Revised.pdf',
        'old_wsl': EV/'builds/same-environment-old/rebuilt.pdf',
        'new_wsl_A': EV/'builds/route-A/rebuilt.pdf',
        'new_wsl_B': EV/'builds/route-B/rebuilt.pdf',
    }
    assert sha(paths['new_wsl_A']) == sha(paths['new_wsl_B'])
    docs = {k: fitz.open(v) for k, v in paths.items()}
    assert all(len(d) == 77 for d in docs.values())
    rows = []
    for n in range(77):
        pages = {k: d[n] for k, d in docs.items()}
        ref = pages['new_input']
        assert all(p.rect == ref.rect and p.get_text() == ref.get_text() for p in pages.values()), n+1
        im = {k: pixels(p) for k, p in pages.items() if k != 'new_wsl_B'}
        original = diff(im['old_input'], im['new_input'])
        wsl = diff(im['old_wsl'], im['new_wsl_A'])
        old_env = diff(im['old_input'], im['old_wsl'])
        new_env = diff(im['new_input'], im['new_wsl_A'])
        # Compare the full signed difference layer, not only page IDs or bounding boxes.
        signed_exact = np.array_equal(im['old_wsl'].astype(np.int16)-im['old_input'],
                                      im['new_wsl_A'].astype(np.int16)-im['new_input'])
        assert old_env == new_env and signed_exact, n+1
        rows.append({'page': n+1, 'text_and_geometry_exact': True,
                     'input_old_new': original, 'same_environment_old_new': wsl,
                     'old_environment': old_env, 'new_environment': new_env,
                     'full_signed_environment_difference_equal': bool(signed_exact)})
    assert [r['page'] for r in rows if r['input_old_new']['changed_pixels']] == [76]
    assert [r['page'] for r in rows if r['same_environment_old_new']['changed_pixels']] == [76]
    assert [r['page'] for r in rows if r['new_environment']['changed_pixels']] == [34,41,45,59,75,77]
    for field in ('input_old_new','same_environment_old_new'):
        box=rows[75][field]['difference_bbox_pixels']
        assert box[0]>=108 and box[1]>=580 and box[2]<=1188 and box[3]<=1436
    figures=[]
    supplied_root = TMP/'input/Process_Report_Revised_Source/figures'
    generated_root = EV/'builds/route-B/regenerated_figures'
    for a in sorted(supplied_root.glob('*.pdf')):
        b=generated_root/a.name
        with fitz.open(a) as x, fitz.open(b) as y:
            assert len(x)==len(y)==1
            px,py=x[0],y[0]
            assert px.rect==py.rect
            assert px.get_text('words')==py.get_text('words')
            assert np.array_equal(pixels(px),pixels(py))
            native={ext: sha(a.with_suffix(ext)) == sha(b.with_suffix(ext)) for ext in ('.svg','.drawio')}
            assert all(native.values())
            figures.append({'name': a.stem, 'supplied_sha256':sha(a), 'generated_sha256':sha(b),
                'text_and_word_geometry_exact':True, 'page_geometry_exact':True,
                'standalone_200dpi_pixels_exact':True, 'native_files_byte_equal':native})
    assert len(figures)==6
    logs=[]
    for route in ('route-A','route-B','same-environment-old'):
        for name in ('compile_stdout_1.log.txt','compile_stdout_2.log.txt','main.log.txt'):
            path=EV/'builds'/route/name
            text=path.read_text(errors='replace')
            assert 'This is XeTeX' in text and 'Output written on build/main.pdf (77 pages).' in text
            if name=='main.log.txt':
                assert not any(s in text for s in ('Missing character:', 'Undefined control sequence', 'Overfull ', '! Emergency stop', 'undefined references', 'undefined citations'))
            logs.append({'path':str(path.relative_to(ROOT)), 'sha256':sha(path), 'two_pass_log_or_final_actual_log':True})
    result={'reviewer_context':'/root/independent_review','checked_at':datetime.now(timezone.utc).isoformat(),
        'status':'PASS','artifact_sha256':{k:sha(v) for k,v in paths.items()},
        'dpi':200,'pages':rows,'figures':figures,'actual_compiler_logs':logs,
        'method':'Own artifact reading, all-page native text/geometry/pixel comparison and complete signed RGB environment delta comparison',
        'input_and_same_environment_changed_pages':[76], 'inherited_environment_difference_pages':[34,41,45,59,75,77],
        'new_build_byte_identical_to_input':False, 'new_model_calls':0, 'trajectory_runs':0}
    (EV/'independent_build_environment_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','pages':77,'original_and_wsl_changed_pages':[76],
                      'full_signed_environment_difference_exact':True,'figures':len(figures)},ensure_ascii=False))


if __name__ == '__main__':
    main()
