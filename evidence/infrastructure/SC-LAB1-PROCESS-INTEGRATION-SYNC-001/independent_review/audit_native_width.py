"""Recompute actual source-resolution values, without changing approved layout."""
from hashlib import sha256
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'task1/reports/process1/source'


def main():
    mapping = json.loads((SOURCE / 'provenance/crop_map.json').read_text())
    checks = []
    for row in mapping:
        with Image.open(SOURCE / row['image']) as crop, Image.open(SOURCE / row['source']) as raw:
            width_mm, height_mm = row['placement_mm'][2:]
            actual_ppi = min(crop.width / (width_mm / 25.4), crop.height / (height_mm / 25.4))
            actual_crop = raw.crop(tuple(row['box']))
            pixels_equal = actual_crop.size == crop.size and actual_crop.convert('RGB').tobytes() == crop.convert('RGB').tobytes()
            checks.append({'page': row['page'], 'unit': row['unit'], 'source': row['source'],
                           'crop': row['image'], 'raw_pixels': list(raw.size), 'crop_pixels': list(crop.size),
                           'crop_box': row['box'], 'display_mm': [width_mm, height_mm],
                           'effective_ppi': actual_ppi, 'recorded_ppi': row['ppi'],
                           'ppi_record_matches': abs(actual_ppi - row['ppi']) < 1e-8,
                           'lossless_crop_pixels_match': pixels_equal,
                           'source_resolution_scope': 'APPROVED_NATIVE_WIDTH under current user acceptance; no new Evidence Lock'})
    result = {'scope': 'All 134 regular evidence windows in the approved crop_map, independently recomputed; closing-page extra image is outside this map and not covered by this calculation.',
              'accepted_pdf_sha256': sha256((ROOT / 'Process_Report_Revised.pdf').read_bytes()).hexdigest(),
              'windows': len(checks), 'minimum_actual_ppi': min(x['effective_ppi'] for x in checks),
              'maximum_actual_ppi': max(x['effective_ppi'] for x in checks),
              'below_180_count': sum(x['effective_ppi'] < 180 for x in checks),
              'all_recorded_ppi_match': all(x['ppi_record_matches'] for x in checks),
              'all_lossless_crops_match': all(x['lossless_crop_pixels_match'] for x in checks),
              'checks': checks}
    (OUT / 'native_width_resolution_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'checks'},ensure_ascii=False,indent=2))
    if not result['all_recorded_ppi_match'] or not result['all_lossless_crops_match']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
