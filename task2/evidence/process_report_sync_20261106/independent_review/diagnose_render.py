"""Quantify actual page differences without altering the accepted PDF or sources."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


def compare(left, right):
    result = []
    for path in sorted(left.glob('page-*.png')):
        a = np.array(Image.open(path).convert('RGB'), dtype=np.int16)
        b = np.array(Image.open(right / path.name).convert('RGB'), dtype=np.int16)
        delta = np.abs(a - b)
        mask = np.any(delta, axis=2)
        ys, xs = np.nonzero(mask)
        result.append({'page': int(path.stem.split('-')[1]),
            'pixels': [int(a.shape[1]), int(a.shape[0])],
            'changed_pixels': int(mask.sum()), 'changed_fraction': float(mask.mean()),
            'mean_absolute_channel_delta': float(delta.mean()),
            'max_channel_delta': int(delta.max()),
            'difference_bbox_xyxy': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)] if len(xs) else None})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-source-compiled-pdf', type=Path, required=True)
    args = parser.parse_args()
    review = Path(__file__).resolve().parent
    root = review.parents[3]
    original = review / 'build/original_source'
    original.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm', '-r', '200', '-png', str(args.original_source_compiled_pdf),
                    str(original/'page')], check=True)
    first = review.parent / 'installed_build/build/process'
    approved_fonts = subprocess.check_output(['pdffonts', str(root/'task2/reports/process/Process_Report.pdf')], text=True)
    compiled_fonts = subprocess.check_output(['pdffonts', str(args.original_source_compiled_pdf)], text=True)
    record = {'dpi': 200,
        'approved_vs_installed_attempt1': compare(first/'approved', first/'compiled'),
        'approved_vs_exact_original_source_compile': compare(first/'approved', original),
        'exact_original_vs_installed_attempt1': compare(original, first/'compiled'),
        'approved_fonts': approved_fonts, 'original_source_compiled_fonts': compiled_fonts,
        'finding': 'Original archive sources and installed path-adapted sources share the same render in this environment. Approved PDF uses NotoSansCJKjp-Bold while this environment resolves the sans bold face as NotoSansCJKjp-Black; compilation environment differs. No report/source/style edits are justified by this discrepancy.'}
    target = review / 'render_diagnosis.json'
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'report': str(target.relative_to(root)),
        'original_vs_installed_equal_pages': sum(row['changed_pixels']==0 for row in record['exact_original_vs_installed_attempt1']),
        'approved_vs_original_equal_pages': sum(row['changed_pixels']==0 for row in record['approved_vs_exact_original_source_compile'])}))


if __name__ == '__main__':
    main()
