"""Verify the saved current-run figures and executed working notebooks."""
from pathlib import Path
import base64
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

import nbformat
from PIL import Image, ImageStat

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT))
from task1.scripts.build_complete_figures import FIGURE_NAMES, load_current

REVISION = ROOT / 'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001'
OUT = REVISION / 'b_run'
FIGURES = REVISION / 'figures'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def relative(path):
    return str(path.relative_to(ROOT))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    current, manifest, baseline = load_current()
    generated = read(FIGURES / 'figure_manifest.json')
    assert generated['run_id'] == current['run_id']
    assert generated['baseline'] == manifest['artifacts']['baseline']
    assert generated['stage_counts'] == baseline['stage_counts']
    assert generated['generator_sha256'] == digest(ROOT / generated['generator'])
    file_checks = []
    for item in generated['files']:
        path = ROOT / item['path']
        assert digest(path) == item['sha256'], path
        file_checks.append({**item, 'size_bytes': path.stat().st_size})
    raster_checks = []
    pngs = sorted(FIGURES.rglob('*.png'))
    for path in pngs:
        with Image.open(path) as image:
            raster_checks.append({'path': relative(path), 'sha256': digest(path),
                                  'width': image.width, 'height': image.height,
                                  'stored_dpi': image.info.get('dpi'),
                                  'grayscale_stddev': ImageStat.Stat(image.convert('L')).stddev[0]})
    command = [sys.executable, 'tools/skills/publication-plots/scripts/check_figure_set.py',
               *[relative(path) for path in pngs], '--min-width', '1600', '--min-height', '1000']
    checker = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert checker.returncode == 0, checker.stdout + checker.stderr
    drawing = ET.parse(FIGURES / 'goal1_execution_structure.drawio')
    cells = drawing.findall('.//mxCell')
    labels = [line for cell in cells for line in cell.get('value', '').splitlines() if line]
    svg = ET.parse(FIGURES / 'goal1_execution_structure.svg')
    svg_text = [''.join(node.itertext()) for node in svg.iter() if node.tag.endswith('}text')]
    missing = [label for label in labels if label not in svg_text]
    assert not missing, missing
    geometry = {'vertices': sum(c.get('vertex') == '1' for c in cells),
                'edges': sum(c.get('edge') == '1' for c in cells),
                'nonempty_label_lines': len(labels), 'missing_svg_label_lines': missing,
                'render_source': 'render_architecture parses this draw.io mxGeometry and labels for every export'}
    assert geometry['vertices'] == 11 and geometry['edges'] == 10
    timestamp = datetime.now(timezone.utc).isoformat()
    write('figure_verification.json', {
        'verified_at': timestamp, 'status': 'ENGINEERING_CHECKS_VERIFIED',
        'independent_acceptance': 'PENDING_C_REVIEW',
        'run_id': current['run_id'], 'processing_code_sha': manifest['code_sha'],
        'current_pointer_sha256': digest(REVISION / 'current_run.json'),
        'figure_manifest_sha256': digest(FIGURES / 'figure_manifest.json'),
        'generator_sha256': generated['generator_sha256'],
        'baseline_sha256': generated['baseline']['sha256'],
        'source_crs': 'UNVERIFIED', 'classification': baseline['classification'],
        'stage_counts': baseline['stage_counts'], 'files': file_checks,
        'rasters': raster_checks, 'drawio_svg_consistency': geometry,
        'checker_command': ['.venv/bin/python', *command[1:]],
        'checker_returncode': checker.returncode,
        'checker_stdout': checker.stdout, 'checker_stderr': checker.stderr,
        'render_commands_executed_before_this_check': [
            f'pdftoppm -r 200 -png -singlefile {relative(FIGURES / (name + ".pdf"))} {relative(FIGURES / (name + "_pdf_render"))}'
            for name in FIGURE_NAMES],
        'manual_visual_inspection': {
            'inspector': 'B-Run:b_baseline',
            'method': 'view_image on final 300-dpi PNG, 200-dpi PDF render and grayscale inspection copy',
            'observations': [
                'Seven trajectory panels and legend are legible; no title, axis label or legend clipping.',
                'Record 2 uses full numeric ticks without offset notation; each panel has equal x/y scale and independent limits.',
                'Raw points are scatter only. Clean/final lines use actual processed segments; all-filtered records show no fabricated output.',
                'Terminal-action bars conserve 783 points; hatches distinguish classes in grayscale.',
                'Architecture labels remain inside their boxes; arrow directions and repair/reopen/parent-return routes are unambiguous.',
                'Later Goal 2/3 is visibly marked not executed. The structure is not presented as a global interaction evidence timeline.'
            ],
            'display_only_adjustments_before_final_inspection': [
                'Disabled trajectory tick offset notation.',
                'Shortened bottom architecture labels to fit existing geometry without changing relationships.'
            ]
        },
        'new_model_calls': 0, 'new_dependencies': [], 'persistent_configuration_changes': []
    })

    execution = read(OUT / 'notebook_execution.json')
    assert execution['returncode'] == 0 and execution['result']['executed']
    assert execution['generator_sha256'] == digest(ROOT / 'task1/scripts/build_goal1_notebooks.py')
    assert execution['resources_snapshot_sha256'] == digest(REVISION / 'resources.json')
    expected_images = {
        '01_baseline_and_audit.ipynb': [digest(FIGURES / (name + '.png')) for name in FIGURE_NAMES[:2]],
        '02_agent_loop_recompute.ipynb': [digest(FIGURES / (FIGURE_NAMES[2] + '.png'))]
    }
    notebook_checks = []
    for item in execution['result']['executions']:
        path = ROOT / item['notebook']
        assert digest(path) == item['sha256'], path
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        code_cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
        counts = [cell.execution_count for cell in code_cells]
        assert counts == list(range(1, len(code_cells) + 1)), counts
        errors, embedded, stream = [], [], []
        for index, cell in enumerate(code_cells):
            compile(cell.source, f'{path.name}:cell{index}', 'exec')
            for output in cell.outputs:
                if output.output_type == 'error':
                    errors.append(dict(output))
                if output.output_type == 'stream':
                    stream.append(output.text)
                image = output.get('data', {}).get('image/png')
                if image:
                    embedded.append(hashlib.sha256(base64.b64decode(image)).hexdigest())
        assert not errors, errors
        assert embedded == expected_images[path.name], embedded
        combined_stream = '\n'.join(stream)
        assert current['run_id'] in combined_stream and manifest['code_sha'] in combined_stream
        if path.name.startswith('01'):
            assert 'Fresh baseline: VERIFIED | independent review: VERIFIED' in combined_stream
            assert 'exact output hash match' in combined_stream
            assert 'UNVERIFIED' in combined_stream
        else:
            assert 'Selected mode: RECOMPUTE' in combined_stream
            assert 'Journal snapshot at Notebook execution:' in combined_stream
            assert 'final status: task1/evidence/goal1/REVIEW_PACKET.md' in combined_stream
        notebook_checks.append({**item, 'execution_counts': counts, 'error_outputs': errors,
                                'embedded_image_sha256': embedded, 'schema_valid': True,
                                'code_cells_compile': True})
    for path in (ROOT / 'task1/scripts/build_complete_figures.py', ROOT / 'task1/scripts/build_goal1_notebooks.py'):
        compile(path.read_text(), str(path), 'exec')
    write('notebook_verification.json', {
        'verified_at': timestamp, 'status': 'ENGINEERING_CHECKS_VERIFIED',
        'independent_acceptance': 'PENDING_C_REVIEW',
        'run_id': current['run_id'], 'processing_code_sha': manifest['code_sha'],
        'execution_receipt_sha256': digest(OUT / 'notebook_execution.json'),
        'generator_sha256': execution['generator_sha256'],
        'resources_snapshot_sha256': execution['resources_snapshot_sha256'],
        'notebooks': notebook_checks, 'new_model_calls': 0,
        'observed_execution_warning': 'Existing local ipykernel warned about unencrypted TCP transport; both fresh kernels completed without cell errors. No Provider was invoked.',
        'new_dependencies': [], 'persistent_configuration_changes': [],
        'scope': 'Seven-record current conditional pilot. Formal reports remain working material; final project acceptance is separate.'
    })
    print(json.dumps({'run_id': current['run_id'], 'figure_files_checked': len(file_checks),
                      'raster_files_checked': len(raster_checks), 'notebooks_checked': len(notebook_checks),
                      'notebook_error_outputs': 0, 'status': 'ENGINEERING_CHECKS_VERIFIED'}, indent=2))


if __name__ == '__main__':
    main()
