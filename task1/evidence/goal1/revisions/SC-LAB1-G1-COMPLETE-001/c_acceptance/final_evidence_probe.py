"""C read-only verification of final summary, executed notebooks and entry snapshots.

This imports no production workflow. It writes only C's own evidence directory.
"""
import ast
import base64
import hashlib
import html
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[6]
REV = ROOT / 'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001'
OUT = REV / 'c_acceptance'
RUN = REV / 'runs/g1-complete-pilot-03'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evidence(paths):
    return [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in paths]


def save(name, checks, paths, **extra):
    result = dict(status='VERIFIED' if all(c['passed'] for c in checks) else 'REJECTED',
                  run_id='g1-complete-pilot-03', classification='INDEPENDENT_C_PRODUCT_REVIEW',
                  checks=checks, check_count=len(checks), evidence=evidence(paths), **extra)
    (OUT / name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(name, result['status'], len(checks))
    assert result['status'] == 'VERIFIED', [c for c in checks if not c['passed']]


def rows(cell):
    content = ''.join(''.join(o.get('data', {}).get('text/html', [])) for o in cell.get('outputs', []))
    return [[html.unescape(re.sub('<[^>]+>', '', v)) for v in re.findall(r'<td[^>]*>(.*?)</td>', r)]
            for r in re.findall(r'<tr>(.*?)</tr>', content) if '<td' in r]


def main():
    probe = read(OUT / 'g1-complete-pilot-03_independent.json')
    summary = read(REV / 'result_summary.json')
    followup = read(RUN / 'coordinate_sensitivity.json')
    manifest = read(RUN / 'manifest.json')
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})

    check('independent_reference_verified', probe['status'] == 'VERIFIED')
    check('same_run_code_scope', summary['run_id'] == manifest['run_id'] and summary['code_sha'] == manifest['code_sha']
          and summary['source_crs'] == 'UNVERIFIED' and summary['datum_proven'] is False)
    check('global_stages', summary['stage_counts'] == probe['stage_counts'])
    check('global_segments', summary['segment_counts'] == probe['segment_counts'])
    check('record_scope', [r['record_id'] for r in summary['rows']] == [r['record_id'] for r in probe['per_record']])
    for row, ref in zip(summary['rows'], probe['per_record']):
        rid = row['record_id']; counts = ref['stage_counts']; n = counts['input'] - counts['filtered'] - counts['denoised']
        check(rid + ':stages', all(row[k] == v for k, v in counts.items()) and row['segments'] == ref['segment_counts'])
        check(rid + ':DP_denominator', row['dp_reference_points'] == n)
        expected_saving = 1 - counts['retained'] / n if n else None
        check(rid + ':DP_saving', row['dp_saving'] == expected_saving)
        errors = [r['max_error_m'] for r in probe['dp_checks'] if r['record_id'] == rid]
        check(rid + ':DP_error', abs(row['max_dp_interval_error_m'] - max(errors)) < 1e-10
              if errors else row['max_dp_interval_error_m'] is None)
        check(rid + ':terminal_status', row['terminal_status'] == ('PROCESSED' if n else 'ALL_FILTERED'))
    n = sum(r['dp_reference_points'] for r in summary['rows'])
    check('aggregate_DP_denominator_saving', summary['dp_reference_points'] == n == 461
          and summary['dp_saving'] == 1 - 188 / n)
    check('aggregate_max_DP_error', abs(summary['max_dp_interval_error_m'] - max(r['max_error_m'] for r in probe['dp_checks'])) < 1e-10)
    check('distinct_raw_reduction', summary['raw_to_final_point_reduction'] == 1 - 188 / 783)
    check('all_sensitivity_summary_fields', all(followup[k] == v for k, v in summary['coordinate_sensitivity'].items()))
    check('protected_source_and_claims', summary['modified_raw_values'] == 0 and summary['source_inputs_unchanged'] is True
          and 'not ground-truth accuracy' in summary['interpretation'])
    save('summary_review.json', checks, [REV/'result_summary.json', OUT/'g1-complete-pilot-03_independent.json',
         RUN/'baseline.json', RUN/'coordinate_sensitivity.json', Path(__file__)])

    checks = []
    execution = read(REV/'b_run/notebook_execution.json')
    notebooks = {p.name: read(p) for p in (ROOT/'task1/notebooks').glob('*.ipynb')}
    generator = ROOT/'task1/scripts/build_goal1_notebooks.py'
    check('execution_exit_status', execution['returncode'] == 0 and execution['duration_seconds'] > 0)
    check('generator_hash', execution['generator_sha256'] == sha(generator))
    generator_text = generator.read_text()
    check('fresh_kernel_implementation', 'NotebookClient(' in generator_text and 'TemporaryDirectory' in generator_text
          and 'sys.executable' in generator_text and 'client.execute()' in generator_text)
    check('new_model_calls_zero', execution['new_model_calls'] == 0)
    image_hashes = []
    for row in execution['result']['executions']:
        path = ROOT/row['notebook']; nb = notebooks[path.name]
        code = [c for c in nb['cells'] if c['cell_type'] == 'code']
        check(path.name+':receipt_and_counts', row['sha256'] == sha(path) and row['status'] == 'VERIFIED'
              and row['new_kernel'] is True and row['new_model_calls'] == 0 and len(code) == row['code_cells'] == 8)
        check(path.name+':sequential_execution', [c['execution_count'] for c in code] == list(range(1, 9)))
        check(path.name+':no_cell_errors', not any(o['output_type'] == 'error' for c in code for o in c['outputs']))
        for c in code:
            ast.parse(''.join(c['source']))
        check(path.name+':relative_sources', '/home/' not in ''.join(''.join(c['source']) for c in nb['cells']))
        stream = ''.join(''.join(o.get('text', [])) for c in code for o in c['outputs'])
        check(path.name+':actual_current_binding', manifest['run_id'] in stream and manifest['code_sha'] in stream
              and manifest['input_sha256'] in stream and sha(RUN/'coordinate_sensitivity.json') in stream)
        check(path.name+':default_recompute', nb['metadata']['sc_goal1']['default_mode'] == 'RECOMPUTE')
        for c in code:
            for o in c['outputs']:
                if 'image/png' in o.get('data', {}):
                    image_hashes.append(hashlib.sha256(base64.b64decode(''.join(o['data']['image/png']))).hexdigest())
    baseline_nb = notebooks['01_baseline_and_audit.ipynb']
    expected_rows = [[str(v) for v in [r['record_id'], r['input'], r['segmented'], r['filtered'], r['denoised'],
                     r['dp_reference_points'], r['simplified'], r['retained'], r['not_processed']]] for r in summary['rows']]
    check('baseline_actual_stage_table', rows(baseline_nb['cells'][9]) == expected_rows)
    expected_metrics = [[str(v) for v in [r['record_id'], r['dp_reference_points'], r['retained'], r['dp_saving'],
                        r['max_dp_interval_error_m'], 'ALL_FILTERED' if r['retained'] == 0 else None]] for r in summary['rows']]
    check('baseline_actual_DP_table', rows(baseline_nb['cells'][11]) == expected_metrics)
    actual_source = ''.join(baseline_nb['cells'][7]['source'])
    check('baseline_raw_reexecution_and_review', "execute_tool('baseline'" in actual_source
          and 'review_baseline(baseline, reference, contract, provenance)' in actual_source
          and "manifest['artifacts']['baseline']['output_sha256']" in actual_source)
    agent_nb = notebooks['02_agent_loop_recompute.ipynb']
    check('agent_default_live_disabled', "MODE='RECOMPUTE'" in ''.join(agent_nb['cells'][2]['source'])
          and 'ENABLE_LIVE=False' in ''.join(agent_nb['cells'][2]['source']))
    check('four_actual_recomputations', rows(agent_nb['cells'][6]) == [[a, 'True', 'VERIFIED', '[]'] for a in
          ['profile_pilot', 'duplicate_details', 'time_boundaries', 'baseline']])
    check('actual_embedded_figure_bytes', sorted(image_hashes) == sorted(sha(REV/'figures'/f'{n}.png') for n in
          ['conditional_pilot_trajectories', 'point_terminal_counts', 'goal1_execution_structure']))
    save('notebook_review.json', checks, [ROOT/'task1/notebooks'/n for n in sorted(notebooks)] +
         [REV/'b_run/notebook_execution.json', generator, RUN/'manifest.json', RUN/'coordinate_sensitivity.json',
          REV/'figures/figure_manifest.json', OUT/'summary_review.json', Path(__file__)],
         limitations=['This C independently reviewed B actual fresh-kernel receipts, source and outputs; C did not relaunch model calls.',
                      'Notebook02 captures IMPLEMENTING before subsequent C task registration; final journal status is a later event.'])

    checks = []
    reviewed = []
    snapshots = []
    for path in [ROOT/'task1/evidence/goal1/REVIEW_PACKET.md', REV/'FINAL_RESPONSE.md',
                 ROOT/'task1/evidence/goal1/requirements.json']:
        target = OUT/('reviewed_'+path.name+('.txt' if path.suffix == '.md' else ''))
        target.write_bytes(path.read_bytes()); reviewed.append(target)
        snapshots.append({'path': str(target.relative_to(ROOT)), 'sha256': sha(target),
                          'source_original_path': str(path.relative_to(ROOT)),
                          'classification': 'READ_ONLY_ORIGINAL_BYTES_SNAPSHOT_NOT_ACTIVE_ENTRY'})
        if path.suffix == '.md':
            text = path.read_text()
            bad = []
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if re.match(r'^[a-z]+://', link) or link.startswith('#'): continue
                if not (path.parent/link.split('#')[0]).exists(): bad.append(link)
            check(path.name+':local_links_exist', not bad)
    final = (OUT/'reviewed_FINAL_RESPONSE.md.txt').read_text()
    check('current_numeric_claims', all(token in final for token in ['783', '309', '273', '188', '461', '59.2191%', '75.9898%', '4.938319812632411']))
    check('conditional_claim_and_unpublished_boundary', 'UNVERIFIED' in final and 'GPT_SECOND_REVIEW=PENDING' in final
          and '当前尚未push' in final and 'Submission=NOT_READY' in final and 'Goal 2/3 未执行' in final)
    check('no_accuracy_or_final_report_claim', '不报告误删率、恢复准确率或已证明质量提升' in final and '本轮不发邮件、不宣称SUBMITTED' in final)
    check('counts_separated', '不与261相加' in final and '这些是各自范围的独立检查' in final and '精确剩余额度为unknown' in final)
    save('entry_review.json', checks, reviewed + [OUT/'summary_review.json', OUT/'workflow_trace_review.json'],
         snapshots=snapshots,
         human_review='C read A–H and current entry in full; claims match independently reviewed scope, counts, failures, modes and limitations.',
         status_update_rule='Original active entry/requirements may subsequently record actual C acceptance and publication; this review binds immutable observed snapshots only.',
         pending=['Actual push/remote equality and final publication links', 'GPT remote second review'])


if __name__ == '__main__':
    main()
