"""Independent binding/content checks for the two reviewed report PDFs.

Read-only toward author sources and results. Human/agent visual inspection is
recorded separately; this script does not claim that byte checks are eyesight.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
RB = EV + 'report_build/'
CHECKS, SOURCES, TARGETS = [], {}, {}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def source(relative, target=False):
    path = ROOT / relative
    SOURCES[relative] = digest(path)
    if target:
        TARGETS[relative] = SOURCES[relative]
    return path


def read(relative, target=False):
    return json.loads(source(relative, target).read_text())


def check(name, actual, expected=True):
    CHECKS.append({'name': name, 'actual': actual, 'expected': expected,
                   'passed': actual == expected})


def mapping(label, bindings, target=False):
    for relative, expected in bindings.items():
        actual = digest(source(relative, target))
        check(label + ':' + relative, actual, expected)


def main():
    expected_pdfs = {
        'experiment1': ('46e1b101ee3cfebc0beb6ff8a465c6801df74b777bf1631cf3cf9ba42dd29f54', 21),
        'process1': ('eed1e8ef8f690018c66a157c794d477d5901a426029ae638bce54fdd24a9fcf0', 12),
    }
    build = read(RB + 'build_receipt.json', True)
    archive = read(RB + 'render_archive_receipt.json', True)
    texts = {}
    for report in build['reports']:
        name = report['report']
        expected_hash, expected_pages = expected_pdfs[name]
        pdf = source(report['pdf'], True)
        check(name + ': pinned inspected PDF', digest(pdf), expected_hash)
        check(name + ': build PDF identity', digest(pdf), report['sha256'])
        check(name + ': recorded compile exit', report['compile_exit_code'], 0)
        check(name + ': recorded diagnostic list', report['unresolved_diagnostics'], [])
        check(name + ': recorded page count', report['pages'], expected_pages)
        info = subprocess.run(['pdfinfo', str(pdf)], check=True, capture_output=True,
                              text=True).stdout
        check(name + ': actual PDF pages', int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1)), expected_pages)
        page_size = re.search(r'^Page size:\s+([\d.]+) x ([\d.]+) pts', info, re.M)
        width_pt, height_pt = map(float, page_size.groups())
        extracted = subprocess.run(['pdftotext', '-layout', str(pdf), '-'],
                                   check=True, capture_output=True).stdout
        check(name + ': current PDF text equals fully read archived text', extracted,
              source(RB + name + '_text.txt', True).read_bytes())
        # Large text equality is retained as hashes instead of duplicating prose.
        CHECKS[-1]['actual'] = hashlib.sha256(extracted).hexdigest()
        CHECKS[-1]['expected'] = digest(ROOT / (RB + name + '_text.txt'))
        texts[name] = extracted.decode('utf8')
        log = source('task1/reports/' + name + '/build/' + name + '.log').read_text()
        diagnostics = [line for line in log.splitlines()
                       if re.search(r'^!|Missing character|undefined|Overfull|LaTeX Font Warning', line)]
        check(name + ': independent compile-log scan', diagnostics, [])
        mapping(name + ': compiled source', report['source_sha256'], True)
        source(RB + name + '_compile_output.txt', True)
        check(name + ': recorded render dpi', report['render']['dpi'], 200)
        check(name + ': all page renders', len(report['render']['page_sha256']), expected_pages)
        for relative, expected in report['render']['page_sha256'].items():
            row = next(x for x in archive['pages'] if x['original_render'] == relative)
            rendered = source(row['published_render'], True)
            check(relative + ': published byte equality', digest(rendered), expected)
            check(relative + ': original byte equality', digest(ROOT / relative), expected)
            check(relative + ': archive declared hash', row['sha256'], expected)
            check(relative + ': archive bound PDF', row['pdf_sha256'], expected_hash)
            with Image.open(rendered) as im:
                check(relative + ': 200 dpi pixel dimensions',
                      abs(im.width - width_pt / 72 * 200) <= 1 and
                      abs(im.height - height_pt / 72 * 200) <= 1)
    mapping('shared report source', build['shared_source_sha256'], True)
    check('public render count', len(archive['pages']), 33)

    bindings = {}
    generators = {
        'goal3_development_bindings.json': 'build_goal3_sources.py',
        'goal3_selection_bindings.json': 'build_selection_sources.py',
        'goal3_final_bindings.json': 'build_final_sources.py',
    }
    for name, generator in generators.items():
        entry = read(RB + name, True)
        bindings[name] = entry
        mapping(name + ': actual source bytes', entry['source_bindings'])
        mapping(name + ': exact generated outputs', entry['outputs'], True)
        check(name + ': exact generator source',
              digest(source('task1/reports/' + generator, True)), entry['source_sha256'])
        documents = {key: read(relative) for key, relative in entry['source_aliases'].items()}
        for i, value in enumerate(entry['generated_values']):
            actual = documents[value['source']]
            for key in value['keys']:
                if isinstance(actual, list) and isinstance(key, str) and '/' in key:
                    strategy, group = key.split('/', 1)
                    matches = [x for x in actual if x['strategy'] == strategy and x['group'] == group]
                    check(name + ': unique semantic runtime group ' + key, len(matches), 1)
                    actual = matches[0]
                else:
                    actual = actual[key]
            check(name + ': generated value ' + str(i), actual, value['value'])
        check(name + ': no new processing', entry['new_method_runs'], 0)
        check(name + ': no new record models', entry['new_model_calls'], 0)
    final = bindings['goal3_final_bindings.json']
    check('final source count', len(final['source_bindings']), 411)
    check('final scope', final['scope'], 'CONFIRMATION_AND_FULL')
    docs = {key: read(relative) for key, relative in final['source_aliases'].items()}
    for key in ['C_confirmation', 'C_production', 'C_categories', 'C_coordinates',
                'C_new_coverage_boundary', 'C_filter_attribution']:
        check(key + ': independent verified', docs[key]['status'], 'VERIFIED')
        check(key + ': no independent errors', docs[key].get('errors', []), [])
        for item in docs[key]['targets']:
            check(key + ': target included in report binding ' + item['path'],
                  final['source_bindings'].get(item['path']), item['sha256'])

    history = read(RB + 'history_value_bindings.json', True)
    mapping('historical actual inputs', history['source_sha256'])
    mapping('historical generated values/tables', history['generated_files'], True)
    previous = read(EV + 'independent_documents/historical_checks.json')
    check('prior independent history checks remain passed', all(x['passed'] for x in previous['checks']))
    check('prior historical numerical input hashes unchanged',
          all(digest(ROOT / p) == h for p, h in history['source_sha256'].items()))
    figure_review = read(EV + 'independent_documents/figure_data_repaired_receipt.json')
    check('prior independent 7-figure data audit has no errors', figure_review.get('errors', []), [])
    fig_closure = read(EV + 'independent_documents/G3-FIG-01_closure.json')
    check('figure presentation closure', fig_closure['status'], 'VERIFIED')
    mapping('current inspected figure targets',
            {x['path']: x['sha256'] for x in fig_closure['targets']})

    # Independent reduction of every confirmation pair, preserving null geometry.
    manifest = docs['confirmation']
    strata = defaultdict(lambda: {'n': 0, 'protected': 0, 'gain': 0, 'coverage': 0})
    comparable = gain = added = 0
    error_sum = 0.0
    observed = []
    for shard in manifest['shards']:
        path = ROOT / EV / 'runs/g3-final-confirm-01' / shard['path']
        with gzip.open(path, 'rt', encoding='utf8') as stream:
            rows = [json.loads(line) for line in stream]
        check('confirmation actual shard record identities:' + shard['path'],
              [r['record_id'] for r in rows], shard['input_ids'])
        for row in rows:
            observed.append(row['record_id'])
            pair = row['comparisons']['S0|R0']
            item = strata[pair['stratum']]
            item['n'] += 1
            item['protected'] += bool(pair['feasible'])
            item['gain'] += bool(pair['feasible'] and pair['strict_gain'])
            item['coverage'] += pair['coverage_delta']
            if pair['baseline_common_max'] is not None and pair['candidate_max_on_baseline_covered'] is not None:
                comparable += 1
                gain += pair['candidate_max_on_baseline_covered'] < pair['baseline_common_max'] - pair['numerical_allowance']
            added += pair['newly_covered_count']
            error_sum += pair['newly_covered_error_sum']
    check('all 600 confirmation records in original order', observed, manifest['input_ids'])
    reduced = final['confirmation_actual_shard_reduction']
    check('600 confirmation records', len(observed), 600)
    check('345 comparable / 255 unavailable', comparable, 345)
    check('no strict geometric gain', gain, 0)
    check('all confirmation strata exactly reduced', dict(strata), reduced['strata'])
    check('added coverage identity count', added, 26352)
    check('added coverage error mean', error_sum / added, reduced['new_covered_mean_error_work_m'])
    freeze = docs['final_freeze']
    check('freeze precedes actual confirmation', freeze['frozen_at'] < manifest['started_at'])
    check('same pre-frozen final records', freeze['input_ids'], observed)
    check('same split final records', docs['split']['partitions']['FINAL_CONFIRM'], observed)
    check('no final retuning declaration', docs['release']['retuning_or_new_winner_selection_on_final'], False)
    check('final frozen strategy S0', docs['release']['final_strategy'], 'S0')

    gov = docs['governance']
    calls = Counter(x['tool'] for x in gov['events'] if x['event'] == 'function_call')
    check('fixed governance cutoff', gov['cutoff'], '2026-09-27T06:54:34.496Z')
    check('actual governance event count', len(gov['events']), 198)
    check('actual visible dispatches', dict(calls), {'spawn_agent': 4, 'send_message': 61, 'followup_task': 34})
    check('no plaintext native claim', final['governance_snapshot']['native_plaintext_available'], False)

    summary = docs['result_summary']
    check('actual raw record count', summary['data']['records'], 11386)
    check('actual raw point count', summary['data']['points'], 1173410)
    check('conditional source remains unverified', summary['source_crs'], 'UNVERIFIED')
    check('final exact parameters', summary['definition']['parameters'],
          {'dt': 30, 'distance': 400, 'min_points': 2, 'min_length': 0, 'direction': 35, 'dp': 5})
    for stage in ['confirmation', 'production']:
        sm = summary[stage]['summaries']
        for strategy in ['R0', 'S0']:
            row = sm[strategy]
            check(stage + ':' + strategy + ': exclusive terminal accounting',
                  sum(row[k] for k in ['n_filtered', 'n_direction_removed', 'n_dp_removed', 'n_final']), row['n_input'])
            check(stage + ':' + strategy + ': distinct coverage denominator',
                  row['common_covered_points'] + row['common_uncovered_points'], row['n_input'])
            check(stage + ':' + strategy + ': no original breakpoint crossing', row['raw_break_crossings'], 0)
    check('independent math sample records', docs['C_categories']['unique_math_records'], 50)
    check('independent math actual configuration traces', docs['C_categories']['distinct_configuration_math_checks'], 100)
    check('independent random record count', len(docs['C_categories']['random_records']), 40)
    check('coordinate full raw points', docs['C_coordinates']['counts']['points_checked'], 1173410)
    check('coordinate full actual neighbor edges', docs['C_coordinates']['counts']['raw_adjacent_edges'], 1162024)
    check('coordinate independent sensitivity sample', len(docs['C_coordinates']['independent_sensitivity_record_ids']), 56)
    check('coordinate independent sensitivity actual traces', docs['C_coordinates']['independent_sensitivity_trace_checks'], 112)
    attribution = docs['C_filter_attribution']
    check('exclusive new coverage reason counts', attribution['mutually_exclusive_reference_reason_counts'],
          {'TOO_SHORT_LENGTH': 492513, 'TOO_FEW_POINTS': 5434, 'TOO_FEW_POINTS+TOO_SHORT_LENGTH': 2365})
    check('all added point destinies', attribution['new_point_final_ledger_actions'],
          {'retained': 20679, 'simplified': 475957, 'denoised': 3676})
    check('reason sums retain full denominator', sum(attribution['mutually_exclusive_reference_reason_counts'].values()), 500312)

    # Content anchors supplement the full manual reading; they do not replace it.
    anchors = {
        'experiment1': ['待补姓名', '待补学号', '266.016754', '500,312', '492,513', '5,434', '2,365',
                        '26,352', '22,772', '1,173,410', '11,386', 'SUPPORTED_WITHIN_SCOPE',
                        '只有极少记录的层', '仅核读官方摘要与元数据', '方向', 'S–P–D', 'C-S', '35,5'],
        'process1': ['Workflow Construction', 'Experiment Decision Process', 'NOT_AVAILABLE',
                     'SCHEMA READY / NO EVIDENCE REGISTERED', '待补姓名', '待补学号',
                     '266.02', '198', '99', '34', '61', '未取得可读逐字原文',
                     '没有可用用户逐条判断原话', 'PENDING', 'NOT_READY'],
    }
    for report, wanted in anchors.items():
        compact = re.sub(r'\s+', '', texts[report])
        for token in wanted:
            check(report + ': actual PDF content anchor ' + token,
                  re.sub(r'\s+', '', token) in compact)
        check(report + ': no unfilled generated numerical token',
              re.search(r'__[A-Z][A-Z_]+__', texts[report]) is None)
        check(report + ': no private home path in extracted report',
              '/home/' not in texts[report] and '/Users/' not in texts[report])
    refs = source('task1/reports/experiment1/references.bib', True).read_text()
    fetches = read(RB + 'source_fetch_receipts.json', True)
    check('three actual primary source fetches', len(fetches), 3)
    for row in fetches:
        check('source fetch status:' + row['key'], row['status'], 200)
        check('only actually fetched citation URL:' + row['key'], row['url'] in refs)
    source(RB + 'SOURCE_READ_SCOPE.md', True)
    check('paper scope explicit abstract and metadata only', 'Official abstract and metadata read' in refs)
    check('no source datum proved from PROJ', 'Supports conversion semantics only' in refs)
    check('shared P2 source unchanged',
          digest(ROOT / 'templates/latex/common/p2_cloud_sorbet_colors.tex'),
          '2aa820c3f68ba6c14cf1b52082b12336071d77bb5466db2b05b2fab6890aa243')
    errors = [x for x in CHECKS if not x['passed']]
    receipt = {
        'role_context': '/root/c_documents',
        'at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'VERIFIED_AVAILABLE_REPORT_BINDINGS' if not errors else 'REPAIR_REQUIRED',
        'targets': [{'path': p, 'sha256': h} for p, h in sorted(TARGETS.items())],
        'source_hashes': SOURCES,
        'checks': CHECKS,
        'errors': errors,
        'actual_command': '.venv/bin/python task1/evidence/goal3/independent_documents/review_full_reports.py',
        'checker_sha256': digest(Path(__file__)),
        'checked_components': ['current PDF/source/render identities', '411 final, 40 development and 50 selection source bindings',
                               '218 G3 generated value paths', 'all 600 actual confirmation pairs and strata',
                               'historical generated tables and prior independent numerical inputs',
                               'full terminal accounting and independent coordinate/filter-attribution scope',
                               'stable actual governance metadata snapshot', 'citation primary-source scope',
                               'all 33 published renders byte-identical to inspected originals'],
        'unchecked_components': ['new Notebook full execution and ZIP integration (separate task)',
                                 'underlying model requests/costs unavailable', 'human understanding and GPT second review',
                                 'missing formal identity, real screenshots, approved presentation spec and Evidence Lock'],
        'new_processing_runs': 0, 'new_model_calls': 0,
        'visual_inspection': 'Performed by /root/c_documents via view_image for all 33 pages; separate per-page receipt.',
        'parent_task_closed': False,
    }
    (OUT / 'full_report_bindings_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'checks': len(CHECKS), 'errors': errors,
                      'targets': len(TARGETS)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
