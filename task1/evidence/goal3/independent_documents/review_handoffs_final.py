"""Read-only final handoff checks; task closure requires a later real submission."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
TARGETS = [
    'task1/docs/goal3/TECHNICAL_HANDOFF.md',
    'task1/docs/goal3/INTERACTION_HANDOFF.md',
    'task1/docs/goal3/DEFENSE_NOTES.md',
    EV + 'interaction_candidates.json',
    EV + 'teacher_delivery_mapping.json',
    EV + 'teacher_delivery_mapping.md',
]


def main():
    sources, checks = {}, []

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def bind(relative):
        path = ROOT / relative
        assert path.is_file() and not path.is_symlink()
        sources[relative] = digest(path)
        return path

    def read(relative):
        return json.loads(bind(relative).read_text())

    def check(label, actual, expected=True):
        checks.append({'check': label, 'passed': actual == expected,
                       'actual': actual, 'expected': expected})

    technical = bind(TARGETS[0]).read_text()
    interaction_text = bind(TARGETS[1]).read_text()
    defense = bind(TARGETS[2]).read_text()
    interactions = read(TARGETS[3])
    nav = read(TARGETS[4])
    bind(TARGETS[5])
    previous = read(EV + 'independent_documents/navigation_interaction_receipt.json')
    check('prior navigation review actually passed', all(c['passed'] for c in previous['checks']))
    for relative, expected in previous['source_hashes'].items():
        check('unchanged previously checked navigation/interaction source:' + relative,
              digest(bind(relative)), expected)
    for target in previous['targets']:
        check('unchanged previously checked target:' + target['path'], digest(bind(target['path'])), target['sha256'])
    check('inherited exact source-cell locator count', sum(len(n['cells']) for e in nav['entries'] for n in e['notebooks']), 90)
    check('inherited actual report-location count', sum(len(e['reports']) for e in nav['entries']), 45)
    check('teacher navigation complete G1 IDs', len(nav['requirement_coverage']['G1_ids_located']), 16)
    check('teacher navigation complete G2 IDs', len(nav['requirement_coverage']['G2_ids_located']), 10)

    references, quotes = [], []
    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and re.fullmatch('[0-9a-f]{64}', str(value.get('sha256', ''))):
                references.append(value)
            if isinstance(value.get('verbatim'), str) and isinstance(value.get('source'), dict):
                quotes.append(value)
            for child in value.values(): walk(child)
        elif isinstance(value, list):
            for child in value: walk(child)
    walk(interactions)
    for reference in references:
        check('actual interaction source identity:' + reference['path'],
              digest(bind(reference['path'])), reference['sha256'])
    check('available genuine verbatim source occurrences', len(quotes), 11)
    for index, quotation in enumerate(quotes):
        original = bind(quotation['source']['path']).read_text()
        check('exact available user quotation:' + str(index), quotation['verbatim'] in original)
        locator = quotation['source'].get('locator', '')
        match = re.fullmatch(r'lines (\d+)-(\d+)', locator)
        if match:
            check('exact available quotation line range:' + str(index),
                  '\n'.join(original.splitlines()[int(match[1])-1:int(match[2])]), quotation['verbatim'])
    candidates = interactions['candidates']
    check('actual unique interaction candidates', len({c['candidate_id'] for c in candidates}), 19)
    check('actual Markdown candidate order', re.findall(r'^#{2,3} (IH-[A-Z0-9-]+) · ', interaction_text, re.M),
          [c['candidate_id'] for c in candidates])
    for candidate in candidates:
        cid = candidate['candidate_id']
        for name in ['Tier', 'screenshot_spec', 'annotation_spec', 'report_order']:
            check(cid + ': no invented ' + name, candidate[name], None)
        for name in ['Evidence_Lock', 'formal_evidence_selection']:
            check(cid + ': no unauthorized ' + name, candidate[name], 'NOT_ASSIGNED_BY_THIS_HANDOFF')
        if candidate['Human_Judgment']['status'] == 'NOT_AVAILABLE':
            check(cid + ': missing judgment remains unavailable',
                  [candidate['Human_Judgment']['verbatim'], candidate['Human_Judgment']['meaning']], [None, None])
        if candidate['User_verbatim_and_source']['status'] == 'NOT_AVAILABLE':
            check(cid + ': missing user quotation remains empty', candidate['User_verbatim_and_source']['quotes'], [])
    for candidate in candidates[-4:]:
        check(candidate['candidate_id'] + ': authorized autonomous system decision',
              candidate['Actual_decision']['type'], 'SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES')
        check(candidate['candidate_id'] + ': postfreeze root authorship',
              candidate['Available_message_range']['root_context'], '/root')
    check('A final-confirmation information boundary', interactions['FINAL_CONFIRM_effects_read'],
          'ROOT_AND_C_ONLY_AFTER_FINAL_FREEZE; NOT_SENT_TO_A')
    check('encrypted-message metadata not presented as verbatim', 'not recovered verbatim' in interactions['native_message_limits'])

    result = read(EV + 'result_summary.json')
    for relative, expected in result['source_bindings'].items():
        check('summary source still exact:' + relative, digest(bind(relative)), expected)
    check('reported true original scope', (result['data']['records'], result['data']['points']), (11386, 1173410))
    check('final S0 actual parameter vector', result['definition']['parameters'],
          {'dt': 30, 'distance': 400, 'min_points': 2, 'min_length': 0, 'direction': 35, 'dp': 5})
    check('conditional source CRS remains unknown', result['source_crs'], 'UNVERIFIED')
    check('final result actual strategy', result['final_strategy'], 'S0')
    check('actual final sample', (result['confirmation']['records'], result['confirmation']['points']), (600, 62284))
    check('final strict covered-record gain', result['confirmation']['pair']['strict_gain_records'], 349)
    check('final no retuning', result['confirmation']['release']['retuning_or_new_winner_selection_on_final'], False)
    check('prefrozen fallback not triggered', result['confirmation']['release']['predeclared_fallback_used'], False)
    check('whole production no unresolved failed records', result['production']['processing_failures'], [])
    check('whole production all terminals', result['production']['records_with_terminal_state'], 11386)
    check('full strict record gain', result['production']['final_vs_R0']['strict_gain_records'], 6522)
    labels = {'S 过滤点': 'n_filtered', 'D 删除点': 'n_direction_removed', 'P 简化点': 'n_dp_removed',
              '显式保留点': 'n_final', '共同 raw 覆盖点': 'common_covered_points',
              '无输出记录': 'n_no_output_records', '覆盖的原始窗口': 'raw_windows_covered',
              '原始断点跨越': 'raw_break_crossings'}
    for label, key in labels.items():
        line = next(line for line in technical.splitlines() if line.startswith('| ' + label + ' |'))
        displayed = [int(v.strip().replace(',', '')) for v in line.split('|')[2:4]]
        check('handoff actual production table:' + label, displayed,
              [result['production']['summaries'][s][key] for s in ['R0', 'S0']])
    for phase in ['confirmation', 'production']:
        summaries = result[phase]['summaries']
        for strategy in ['R0', 'S0']:
            summary = summaries[strategy]
            check(phase + ':' + strategy + ': terminal point conservation',
                  sum(summary[k] for k in ['n_filtered', 'n_direction_removed', 'n_dp_removed', 'n_final']),
                  summary['n_input'])
    full_C = read(EV + 'independent_c/production_closure_receipt.json')
    check('production independent closure', full_C['status'], 'VERIFIED')
    check('math sample honest distinct from all-record validation',
          (full_C['independent_category_math_records'], full_C['independent_sensitivity_records']), (50, 56))
    boundary = read(EV + 'independent_c/new_coverage_boundary_receipt.json')
    witness = boundary['witness']
    check('worst newly covered record/index', (witness['record_id'], witness['original_index']), ('352', 105))
    check('worst original R0 reason', witness['R0_point_action']['reasons'], ['TOO_FEW_POINTS'])
    check('worst S0 point was removed by direction', witness['final_point_action']['action'], 'denoised')
    check('worst actual error', witness['maximum_new_raw_to_final_error_work_m'], 266.01675442514176)
    for field in ['final_P_input_original_indices', 'final_P_output_original_indices']:
        check('worst local P identity:' + field, [104, 106, 107] in witness[field])
    attribution = read(EV + 'independent_c/full_filter_attribution_receipt.json')
    check('actual mutually exclusive filter attribution', attribution['mutually_exclusive_reference_reason_counts'],
          {'TOO_SHORT_LENGTH': 492513, 'TOO_FEW_POINTS': 5434, 'TOO_FEW_POINTS+TOO_SHORT_LENGTH': 2365})
    check('newly covered point fate separation', attribution['new_point_final_ledger_actions'],
          {'retained': 20679, 'simplified': 475957, 'denoised': 3676})
    for literal in ['266.016754', '492,513', '5,434', '2,365', '475,957', '3,676',
                    '11,386', '1,173,410', '35,868→62,220', '10,991→12,114',
                    '4.9971311138733405', '280.69670439064976', '6.087101997252068',
                    '50 条、100 份', '56 条记录、112 份', '1,763.65',
                    '没有读最终集来开发新候选', '不能把此误差归给 P', '没有发送邮件']:
        check('technical current factual text:' + literal, literal in technical)
    for literal in ['266.017', '35,868', '62,220', '3017、9311、9534', 'Understanding',
                    'source_crs=UNVERIFIED', '不是另一批独立最终测试', '不说明新增点干净']:
        check('defense honest method/result/authority boundary:' + literal, literal in defense)
    freeze = read(EV + 'final_freeze.json')
    check('technical precise freeze time', freeze['frozen_at'] in technical)
    check('technical precise processing code identity', freeze['processing_code_sha'] in technical)
    check('technical precise freeze hash', digest(ROOT / (EV + 'final_freeze.json')) in technical)
    check('technical precise split hash', digest(bind(EV + 'split_manifest.json')) in technical)

    full_checks = []
    for context in ['repository', 'isolated_package']:
        for kind, cells in [('basic', 12), ('system', 8)]:
            if context == 'repository':
                name = 'repository_basic_full_02_receipt.json' if kind == 'basic' else 'repository_system_full_02_current_receipt.json'
                run = 'repository_' + kind + '_full_02'
            else:
                name = 'isolated_package_' + kind + '_full_receipt.json'
                run = 'isolated_' + kind + '_full_01'
            receipt = read(EV + 'independent_c/' + name)
            execution = read(EV + 'notebook_verification/' + run + '/execution_receipt.json')
            check(name + ': genuine independent context', receipt['role_context'], '/root/c_protocol')
            check(name + ': independent outcome', receipt['status'], 'VERIFIED')
            check(name + ': no unresolved numerical errors', receipt['errors'], [])
            check(name + ': complete fresh kernel', execution['started_from_clean_outputs_and_new_kernel'])
            check(name + ': all code cells', (execution['executed_code_cells'], execution['total_code_cells'], receipt['executed_code_cells']), (cells, cells, cells))
            check(name + ': model-call sentinel', receipt['new_provider_attempts_observed'], 0)
            check(name + ': original raw identity', receipt['raw_sha256'], result['data']['raw_sha256'])
            check(name + ': same actual elapsed time', receipt['elapsed_seconds_actual_execution'], execution['elapsed_seconds'])
            check(name + ': executed Notebook identity', receipt['executed_notebook_sha256'], execution['executed_notebook_sha256'])
            if kind == 'basic':
                check(name + ': real historical processing', receipt['history']['record_candidate_recomputations'], 9720)
                check(name + ': real synthetic chains', receipt['demonstration']['synthetic_processing_chains'], 19)
                check(name + ': real pilot', receipt['demonstration']['pilot_runs'], 1)
                check(name + ': actual full processing', receipt['production']['record_candidate_recomputations'], 22772)
                check(name + ': actual complete original range', (receipt['production']['raw_records'], receipt['production']['raw_points']), (11386, 1173410))
                expected_identity = 'FROZEN_SOURCE_BUNDLE' if context == 'isolated_package' else 'ACTUAL_LOCAL_GIT_HEAD'
                check(name + ': honest Git versus no-Git source identity', receipt['production']['code_identity_source'], expected_identity)
            else:
                check(name + ': real historical processing', receipt['history']['record_candidate_recomputations'], 6001)
                check(name + ': preserved historical episodes', receipt['history']['record_episode_selections'], 384)
            if context == 'isolated_package':
                check(name + ': unchanged original ZIP members', receipt['isolated_package']['original_members_unchanged'], 112)
                check(name + ': only extracted task source imported',
                      receipt['isolated_package']['isolated_import_probe']['all_imported_task1_modules_from_extracted_package'])
            full_checks.append({'run': run, 'independent_receipt': EV + 'independent_c/' + name,
                                'executed_code_cells': cells, 'provider_attempts': 0,
                                'elapsed_seconds': execution['elapsed_seconds']})
    for literal in ['2,811.70 秒', '534.86 秒', 'FROZEN_SOURCE_BUNDLE', '不能用静态检查或进程退出码单独代替后者',
                    'REVIEW_ONLY / NOT_READY', 'GPT_SECOND_REVIEW=PENDING', '本次未新增系统包']:
        check('delivery and remaining external boundary:' + literal, literal in technical)
    package = bind('task1/submission/REVIEW_ONLY_实验一.zip')
    check('actual submitted package identity in handoff', digest(package) in technical)
    check('actual package size in handoff', f'{package.stat().st_size:,}' in technical)
    with zipfile.ZipFile(package) as archive:
        check('actual package members', len(archive.namelist()), 113)
    for relative in ['task1/goal3/__main__.py', 'task1/goal3/reproduce.py', 'task1/goal3/package.py',
                     'task1/goal3/execute_notebook.py', 'task1/goal3/control.py',
                     EV + 'append_postfreeze_interaction_facts.py',
                     EV + 'independent_documents/actual_zip_static_receipt.json',
                     EV + 'independent_documents/report_entry_delta_receipt.json']:
        bind(relative)
    link_count = 0
    for relative in TARGETS:
        if not relative.endswith('.md'): continue
        for destination in re.findall(r'\]\(([^)]+)\)', (ROOT / relative).read_text()):
            url = urlsplit(destination)
            if url.scheme or url.netloc or not url.path: continue
            target = ((ROOT / relative).parent / unquote(url.path)).resolve()
            check('actual local handoff navigation:' + relative + ':' + destination,
                  target.exists() and target.is_relative_to(ROOT))
            link_count += 1
    bind(str(Path(__file__).relative_to(ROOT)))
    errors = [c for c in checks if not c['passed']]
    receipt = {
        'role_context': '/root/c_documents', 'target_id': 'handoffs',
        'status': 'VERIFIED_HANDOFFS_READY_FOR_SUBMISSION' if not errors else 'REPAIR_REQUIRED',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'targets': [{'path': p, 'sha256': digest(ROOT/p)} for p in TARGETS],
        'source_hashes': dict(sorted(sources.items())), 'checks': checks, 'errors': errors,
        'checked_components': [
            'Current Technical Handoff and Defense Notes manually read end-to-end; method, source/selection/final/production scopes, negative results, 266m witness and limits checked against actual bound sources.',
            'All 19 interaction candidates and 11 exact available quotation/source occurrences rechecked; no invented human judgments, screenshot specifications, presentation ordering or LOCK.',
            'All 80 prior navigation/interaction source hashes remain identical; inherits the actually performed 1283 checks of 90 source-cell locators and 45 actual PDF page/anchor groups.',
            'All four real FULL execution receipts reconciled with independent C-protocol receipts: 12/8 code cells, actual raw processing counts, zero new provider attempts, exact elapsed times and no-Git source identity.',
            'Actual 113-member ZIP hash/bytes and current entrypoint source bindings checked; prior independent static package/PDF checks remain linked.',
            'All local links within six handoff/navigation deliverables resolve; absent identity and Evidence Master material remain explicit external report/package dependencies.'
        ],
        'full_execution_observations': full_checks, 'local_links_checked': link_count,
        'external_dependencies': ['META_DEPENDENCY', 'EVIDENCE_MASTER_DEPENDENCY'],
        'external_dependencies_block_report_package_completion_not_factual_handoff': True,
        'unchecked_components': ['Future GitHub push and fixed-SHA readback', 'Evidence Master decisions, original missing screenshots and LOCK', 'User Understanding and webpage GPT second review'],
        'new_method_runs': 0, 'new_model_calls': 0, 'parent_task_closed': False,
        'review_harness_correction': 'The first independent checker invocation compared the integer count original_members_unchanged=112 to Boolean true. Corrected to the actual 112-member count; this was a checker schema mistake, not a delivery defect. First attempt retained separately.',
        'actual_command': '.venv/bin/python task1/evidence/goal3/independent_documents/review_handoffs_final.py'
    }
    output = HERE / 'handoffs_final_pre_submission.json'
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'targets': len(receipt['targets']),
                      'sources': len(sources), 'checks': len(checks), 'errors': errors,
                      'receipt_path': str(output.relative_to(ROOT)), 'sha256': digest(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
