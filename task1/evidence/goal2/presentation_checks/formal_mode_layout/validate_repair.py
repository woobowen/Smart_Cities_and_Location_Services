"""Deterministic B scope/hash checks; actual image review is a separate receipt."""
from pathlib import Path
import ast
from collections import Counter
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
FIGURES = ROOT / 'task1/figures/goal2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def funcs(p):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}

def check():
    source = ROOT / 'task1/scripts/build_goal2_figures.py'
    old_source = HERE / 'build_goal2_figures.before.py'
    before, after = funcs(old_source), funcs(source)
    changed = [k for k in before.keys() | after.keys() if before.get(k) != after.get(k)]
    assert changed == ['mode_figures'], changed
    assert sha(source) == '646547b63e6da6ab80a95ae71b3db908f6ea3dce95900ec12aa642b9939916eb'
    manifest = read(FIGURES / 'figure_manifest.json')
    old = read(HERE / 'before/figure_manifest.json')
    assert len(manifest['figures']) == 11
    assert sha(FIGURES / 'figure_data.json') == manifest['figure_data_sha256'] == old['figure_data_sha256']
    assert (FIGURES / 'CASE_SELECTION.json').read_bytes() == (HERE / 'before/CASE_SELECTION.json').read_bytes()
    assert manifest['generator_sha256'] == sha(source)
    for file, expected in manifest['source_files'].items(): assert sha(ROOT / file) == expected, file
    changed_names = {'four_mode_paired_results', 'four_mode_failures_and_cost', 'memory_coverage_and_consumption'}
    unchanged = []
    for fig in manifest['figures']:
        for item in [*fig['formats'].values(), fig['pdf_render']]: assert sha(FIGURES / item['file']) == item['sha256']
        if fig['name'] not in changed_names:
            assert sha(FIGURES / fig['formats']['png']['file']) == sha(HERE / 'before' / fig['formats']['png']['file'])
            assert sha(FIGURES / fig['pdf_render']['file']) == sha(HERE / 'before' / fig['pdf_render']['file'])
            unchanged.append(fig['name'])
    freeze = read(ROOT / 'task1/evidence/goal2/evaluation_freeze.json')
    assert len(freeze['processing_source_hashes']) == 28
    for path, expected in freeze['processing_source_hashes'].items(): assert sha(ROOT / path) == expected, path
    data = read(FIGURES / 'figure_data.json')
    architecture = data['goal2_actual_architecture']
    drawio = FIGURES / architecture['drawio_file']
    assert sha(drawio) == architecture['drawio_sha256']
    cells = ET.parse(drawio).findall('.//mxCell')
    vertices = {c.attrib['id']: c for c in cells if c.get('vertex') == '1'}
    edges = [c for c in cells if c.get('edge') == '1']
    assert set(vertices) == {n[0] for n in architecture['nodes']}
    assert len(vertices) == 11 and len(edges) == 13
    assert Counter((e.get('source'), e.get('target')) for e in edges) == Counter((e[0], e[1]) for e in architecture['edges'])
    for node in architecture['nodes']:
        assert vertices[node[0]].get('value').replace('<br>', '\n') == node[1]
        if node[7]: assert (ROOT / node[7]).is_file(), node[7]
    # Point units and unavailable denominators come from source observations.
    paired_counts = Counter((p['metric'], p['mode']) for p in data['four_mode_paired_results'])
    assert {v for (metric, _), v in paired_counts.items() if metric == 'common_max_error'} == {57}
    assert {v for (metric, _), v in paired_counts.items() if metric != 'common_max_error'} == {72}
    return {'status': 'VERIFIED_B_SCOPE_AND_BINDINGS', 'changed_functions': changed,
            'generator_sha256': sha(source), 'figure_manifest_sha256': sha(FIGURES / 'figure_manifest.json'),
            'figure_data_sha256': manifest['figure_data_sha256'], 'figure_data_byte_identical': True,
            'case_selection_byte_identical': True, 'unaffected_png_and_pdf_render_byte_identical': unchanged,
            'source_files_verified': len(manifest['source_files']), 'processing_hashes_unchanged': 28,
            'native_drawio_vertices': len(vertices), 'native_drawio_edges': len(edges),
            'native_drawio_limit': 'XML editability and graph/source/export bindings checked; no diagrams.net GUI import claimed',
            'independent_C_status': 'PENDING'}

if __name__ == '__main__':
    result = check()
    with (HERE / 'binding_checks.json').open('x') as output: json.dump(result, output, indent=2); output.write('\n')
    print(json.dumps(result))
