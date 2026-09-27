"""Rebind independently read/viewed content to actual REPORT_BUILD outputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
RB = EV + 'report_build/'
ARCHIVE = RB + 'pre_report_entry/'
CHECKS = []


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda: stream.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def check(name, actual, expected=True):
    CHECKS.append({'name': name, 'actual': actual, 'expected': expected, 'passed': actual == expected})


def verify(label, mapping):
    for relative, expected in mapping.items():
        check(label + ':' + relative, sha(ROOT / relative), expected)


def main():
    submission = read(EV + 'document_review_submission.json')
    old_review = read(EV + 'independent_documents/full_report_review_receipt.json')
    old_binding = read(EV + 'independent_documents/full_report_bindings_receipt.json')
    old_build = read(ARCHIVE + RB + 'build_receipt.json')
    current_build = read(RB + 'build_receipt.json')
    old_figures = read(ARCHIVE + 'task1/figures/goal3/figure_manifest.json')
    current_figures = read('task1/figures/goal3/figure_manifest.json')
    figure_closure = read(EV + 'independent_documents/G3-FIG-01_closure.json')
    original_figures = {x['name']: x for x in old_figures['figures']}
    check('previous full report engineering verified', old_review['status'],
          'VERIFIED_AVAILABLE_REPORT_ENGINEERING_WITH_EXTERNAL_DEPENDENCIES')
    check('previous full report binding errors', old_binding['errors'], [])
    check('previous figure repair independently closed', figure_closure['status'], 'VERIFIED')
    check('same seven figures', [x['name'] for x in current_figures['figures']], list(original_figures))
    check('exact unchanged figure data', sha(ROOT / 'task1/figures/goal3/figure_data.json'),
          old_figures['figure_data_sha256'])
    check('exact unchanged figure code/contracts/inputs', current_figures['sources'], old_figures['sources'])
    verify('current figures source', current_figures['sources'])
    figure_rebindings = []
    with tempfile.TemporaryDirectory(prefix='independent-c-report-delta-') as tmp:
        tmp = Path(tmp)
        for figure in current_figures['figures']:
            name = figure['name']; old = original_figures[name]
            for info in figure['formats'].values():
                check(name + ': actual current figure format', sha(ROOT / 'task1/figures/goal3' / info['file']), info['sha256'])
            check(name + ': archived displayed PNG unchanged', figure['formats']['png']['sha256'], old['formats']['png']['sha256'])
            check(name + ': actual 200 dpi render unchanged', figure['pdf_render']['sha256'], old['pdf_render']['sha256'])
            pdf = ROOT / 'task1/figures/goal3' / figure['formats']['pdf']['file']
            prefix = tmp / name
            subprocess.run(['pdftoppm', '-r', '200', '-png', '-singlefile', str(pdf), str(prefix)],
                           check=True, capture_output=True)
            actual = sha(prefix.with_suffix('.png'))
            check(name + ': independent current PDF rerender equals previously viewed image', actual,
                  old['pdf_render']['sha256'])
            figure_rebindings.append({'name': name, 'new_pdf_sha256': sha(pdf),
                                      'independent_current_pdf_render_sha256': actual,
                                      'previously_inspected_render_sha256': old['pdf_render']['sha256'],
                                      'actual_new_visual_view': False,
                                      'basis': 'exact bytes of independently regenerated 200 dpi current-PDF image equal the prior actually viewed raster'})
        prior_pages = {x['published_render']: x for x in old_review['pages']}
        page_rebindings = []
        for report in current_build['reports']:
            name = report['report']
            old = next(x for x in old_build['reports'] if x['report'] == name)
            check(name + ': all report source bytes unchanged', report['source_sha256'], old['source_sha256'])
            verify(name + ': current source hash', report['source_sha256'])
            pdf = ROOT / report['pdf']
            check(name + ': current actual PDF identity', sha(pdf), report['sha256'])
            check(name + ': page count unchanged', report['pages'], old['pages'])
            check(name + ': compile completed', report['compile_exit_code'], 0)
            check(name + ': no reported compile errors', report['unresolved_diagnostics'], [])
            log = (ROOT / 'task1/reports' / name / 'build' / (name + '.log')).read_text()
            check(name + ': independent current compile diagnostics',
                  [l for l in log.splitlines() if re.search(r'^!|Missing character|undefined|Overfull|LaTeX Font Warning', l)], [])
            text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True, capture_output=True).stdout
            check(name + ': complete current text equals prior full reading', hashlib.sha256(text).hexdigest(),
                  old_binding['source_hashes'][RB + name + '_text.txt'])
            render_dir = tmp / name; render_dir.mkdir()
            subprocess.run(['pdftoppm', '-r', '200', '-png', str(pdf), str(render_dir / 'page')],
                           check=True, capture_output=True)
            actual_pages = sorted(render_dir.glob('page-*.png'))
            check(name + ': independent actual rendered page count', len(actual_pages), report['pages'])
            for page in actual_pages:
                rel = RB + 'render200/' + name + '/' + page.name
                old_page = prior_pages[rel]
                actual = sha(page)
                check(rel + ': independent current PDF image equals previously viewed page', actual, old_page['sha256'])
                check(rel + ': public render equals independent fresh PDF render', sha(ROOT / rel), actual)
                check(rel + ': current manifest binds actual image', report['render']['page_sha256'][rel], actual)
                page_rebindings.append({'published_render': rel, 'sha256': actual, 'new_pdf': report['pdf'],
                                        'new_pdf_sha256': sha(pdf), 'prior_pdf_sha256': old_page['pdf_sha256'],
                                        'prior_visual_receipt': EV + 'independent_documents/full_report_review_receipt.json',
                                        'prior_page_note': old_page['note'], 'new_visual_view': False,
                                        'basis': 'independent pdftoppm rerender exact bytes equal the prior actually viewed 200 dpi page'})
    check('33 current report pages rebound', len(page_rebindings), 33)
    verify('current shared report sources', current_build['shared_source_sha256'])
    check('shared report sources unchanged', current_build['shared_source_sha256'], old_build['shared_source_sha256'])

    # Generators ran again; all current inputs and outputs are verified. The final
    # generator values/reduction must equal the already independently checked run.
    for name in ['goal3_development_bindings.json', 'goal3_selection_bindings.json', 'goal3_final_bindings.json']:
        binding = read(RB + name)
        verify(name + ': current source bytes', binding['source_bindings'])
        verify(name + ': current output bytes', binding['outputs'])
        if name == 'goal3_final_bindings.json':
            old = read(ARCHIVE + RB + name)
            for field in ['scope', 'source_sha256', 'source_aliases', 'generated_values',
                          'confirmation_actual_shard_reduction', 'governance_snapshot', 'outputs', 'full']:
                check(name + ': exact unchanged verified semantics ' + field, binding[field], old[field])
        else:
            # Their complete prior input maps and outputs are available from the
            # unchanged sources/output hashes in the initial independent receipt.
            for rel, h in binding['source_bindings'].items():
                check(name + ': source remains independently checked ' + rel, h, old_binding['source_hashes'][rel])
            for rel, h in binding['outputs'].items():
                check(name + ': generated prose remains independently read ' + rel, h, old_binding['source_hashes'][rel])
    entry = read(EV + 'package/report_build_entry_receipt.json')
    check('actual REPORT_BUILD exit code', entry['exit_code'], 0)
    check('actual REPORT_BUILD status', entry['status'], 'EXECUTED_SUCCESSFULLY')
    verify('actual executed REPORT_BUILD inputs', {'task1/goal3/__main__.py': entry['entry_source_sha256'],
           'task1/reports/build_reports.py': entry['report_builder_sha256'], entry['output_log']: entry['output_log_sha256']})
    for task_name, task in submission['tasks'].items():
        verify(task_name + ': exact submitted source map', task['source_hashes'])
        verify(task_name + ': exact submitted targets', {x['path']: x['sha256'] for x in task['targets']})
    errors = [x for x in CHECKS if not x['passed']]
    delta = {'role_context': '/root/c_documents', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
             'status': 'VERIFIED_CURRENT_DELIVERY_DELTA' if not errors else 'REPAIR_REQUIRED',
             'checks': CHECKS, 'errors': errors, 'figure_rebindings': figure_rebindings,
             'report_page_rebindings': page_rebindings,
             'current_submission_sha256': sha(ROOT / (EV + 'document_review_submission.json')),
             'actual_command': '.venv/bin/python task1/evidence/goal3/independent_documents/review_report_entry_delta.py',
             'checker_sha256': sha(Path(__file__)), 'new_method_runs': 0, 'new_model_calls': 0,
             'actual_independent_pdf_rerenders': {'figures': 7, 'report_pages': 33},
             'visual_rebinding_boundary': 'No claim of a second eyesight pass: current PDF rasters independently regenerated and byte-identical to those already actually viewed.',
             'package_FULL': 'NOT_CHECKED_BY_THIS_DELTA'}
    (HERE / 'report_entry_delta_receipt.json').write_text(json.dumps(delta, ensure_ascii=False, indent=2) + '\n')
    if not errors:
        task = submission['tasks']['figures']
        closure = {'role_context': '/root/c_documents', 'task_id': 'figures', 'target_id': 'figures',
                   'status': 'VERIFIED', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                   'targets': task['targets'], 'source_hashes': task['source_hashes'],
                   'checked_components': ['exact 31 current submitted artifacts and 13 submitted source hashes',
                                          'all seven current PDFs independently rerendered at 200 dpi and exact-byte matched to actually inspected prior renders',
                                          'all 7 figure PNGs unchanged; numerical figure_data, native source, contracts and full run identities unchanged',
                                          'prior independent 2965 numeric/data checks remain applicable to exact same data',
                                          'repaired trajectory S/D legend, worst added-coverage record352 window104–107, full/confirm separation',
                                          'editable drawio unchanged, ten actual role edges, prefreeze-only A feedback and FINAL_CONFIRM isolation'],
                   'unchecked_components': ['Report completion external dependencies', 'ZIP isolated FULL run',
                                            'human understanding and webpage GPT review'],
                   'errors': [], 'delta_receipt': {'path': EV + 'independent_documents/report_entry_delta_receipt.json',
                                                   'sha256': sha(HERE / 'report_entry_delta_receipt.json')},
                   'new_method_runs': 0, 'new_model_calls': 0}
        (HERE / 'figures_current_closure.json').write_text(json.dumps(closure, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': delta['status'], 'checks': len(CHECKS), 'errors': errors,
                      'current_figure_closure_written': not errors}, ensure_ascii=False))


if __name__ == '__main__':
    main()
