"""Independent C review of bounded release evidence and final negative examples.

Reuses the logged full static scan only for exactly matching text bytes and the
same scanner source. Re-executes its 54 changed-file text scans, verifies every
inventory hash, and independently reconciles model proposals against traces.
Writes only this C context's new receipt; no production mutation or LIVE call.
"""
from pathlib import Path
from collections import Counter
import gzip
import importlib.util
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import Audit
from task1.workflow.io import read_json, write_json, digest, now

OUT = Path(__file__).parent
EV = ROOT / 'task1/evidence/goal2'


def bound(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': digest(p)}


def main():
    started = time.perf_counter()
    a = Audit()
    base = EV / 'release_checks/final_01'
    delta_dir = EV / 'release_checks/delta_01'
    delta = read_json(delta_dir / 'delta_reuse_receipt.json')
    old = read_json(base / 'release_check.json')
    report = read_json(delta_dir / 'release_check.json')
    old_inventory = {r['path']: r for r in read_json(base / 'scope_inventory.json')}
    inventory = {r['path']: r for r in read_json(delta_dir / 'scope_inventory.json')}
    scanner_path = EV / 'release_checks/scan_release.py'
    spec = importlib.util.spec_from_file_location('c_inspected_release_scanner', scanner_path)
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    for b in [delta['baseline_report'], delta['baseline_inventory'], delta['portability_review_binding']]:
        a.check('release_input_hash', digest(ROOT / b['path']) == b['sha256'], b['path'])
    a.check('same_scanner_source_for_cache', digest(scanner_path) == old['scanner_sha256'] == delta['scanner_source_sha256'])
    a.check('delta_source_bound', digest(EV / 'release_checks/scan_release_delta.py') == delta['delta_source_sha256'])
    a.check('full_scan_scope', old['checked_files'] == 3260 and old['plaintext_and_decompressed_characters_scanned'] == 5223683232)
    a.check('original_findings_preserved', old['status'] == report['status'] == 'FINDINGS_REQUIRE_REVIEW' and delta['underlying_scanner_exit_code'] == 1)
    a.check('original_concurrent_additions_preserved', old['blocking_counts']['unstable_snapshot'] == 13 and len(old['created_during_scan']) == 13)
    a.check('resolved_concurrent_additions', set(old['created_during_scan']) <= set(inventory) and report['blocking_counts']['unstable_snapshot'] == 0)
    a.check('zero_unresolved_delta_findings', not any(delta['unresolved_counts'].values()))
    a.same('delta_inventory_hash', digest(delta_dir / 'scope_inventory.json'), delta['source_inventory_sha256'])
    a.check('scope_exactly3308_files', len(inventory) == report['checked_files'] == 3308)
    deviations = []
    submitted = read_json(EV / 'final_internal_review_targets.json')['targets']
    immutable = {t['path']: t['sha256'] for t in submitted}
    for p, row in inventory.items():
        file = ROOT / p
        current = digest(file)
        if current != row['sha256']:
            deviations.append({'path': p, 'scanned_sha256': row['sha256'], 'current_sha256': current})
            a.check('only_post_cutoff_control_or_C_review_changes', p == 'task1/evidence/goal2/goal_state.json' or (p.startswith('task1/evidence/goal2/c_contract/') and p not in immutable) or scanner.cache_file(file), p)
        else:
            a.check('release_inventory_current_bytes', file.stat().st_size == row['bytes'])
        a.check('no_over100MiB', row['bytes'] <= 100 * 1024 * 1024, p)
        a.check('no_tracked_cache', not(scanner.cache_file(file) and row['tracked']), p)
    for r in delta['text_reuse']:
        previous = old_inventory[r['path']]
        a.check('exact_prior_scan_byte_reuse', previous['sha256'] == r['sha256'] == inventory[r['path']]['sha256'] and previous['classification'] == 'PROPOSED_G2_SUBSTANTIVE_FILE')
    a.check('3025_exact_reuse54_actual_rescan', len(delta['text_reuse']) == delta['text_reuse_count'] == 3025 and len(delta['text_rescans']) == delta['actual_text_rescan_count'] == 54)
    rescanned_chars = 0
    for r in delta['text_rescans']:
        path = ROOT / r['path']
        a.check('delta_read_was_stable', r['sha256_before_scan'] == r['sha256_after_scan'] == inventory[r['path']]['sha256'])
        # Current goal_state is legitimately advanced by the submit event; its
        # immutable snapshot remains exact. Recheck its latest bytes explicitly.
        findings, absolute, chars = scanner.scan_text(path)
        a.check('C_repeated_changed_text_secret_scan', not findings, r['path'])
        if digest(path) == r['sha256_after_scan']:
            a.check('C_repeated_changed_text_character_count', chars == r['characters_scanned'])
        rescanned_chars += chars
    a.check('logged_delta_char_count', sum(r['characters_scanned'] for r in delta['text_rescans']) == delta['actual_text_characters_rescanned'] == 4038660)
    disposition = read_json(ROOT / delta['portability_review_binding']['path'])
    a.check('exact_three_reviewed_flags', len(disposition['findings']) == len(delta['reviewed_portability']) == 3 and not delta['unreviewed_portability'])
    for row in disposition['findings']:
        a.check('path_disposition_binding', digest(ROOT / row['path']) == row['sha256'])
    reproduce = (ROOT / 'task1/docs/goal2/REPRODUCE.md').read_text()
    provider = (ROOT / 'task1/workflow/g2_provider.py').read_text()
    raster = (ROOT / 'task1/figures/goal2/raster_checks.log').read_text().splitlines()
    a.check('LIVE_absolute_environment_dependency_explicit', '/tmp/sc-g1-codex-0.157.1/node_modules/.bin/codex' in reproduce and 'executable' in provider and '默认 Notebook / RECOMPUTE 不执行上述 CLI' in reproduce)
    a.check('temporary_output_examples_explicitly_replaceable', '/tmp/sc-g2-*' in reproduce and '可替换的临时输出目录' in reproduce)
    a.check('eleven_raster_log_observations_not_source', len(raster) == 11 and all('.png' in line for line in raster))
    links = 0
    for p, row in inventory.items():
        if Path(p).suffix == '.md' and row['classification'] == 'PROPOSED_G2_SUBSTANTIVE_FILE':
            checks, missing = scanner.local_links(ROOT / p)
            links += len(checks)
            a.check('C_current_local_Markdown_link_existence', not missing, p)
    a.check('168_reviewed_local_links', links == report['local_links_checked'] == 168)
    a.check('900_materials_and_three_startup_archives_preserved', report['protected_tracked_files'] == 900 and len(report['protected_user_zip_files']) == 3 and all(r['unchanged'] for r in report['protected_user_zip_files']))
    a.check('C_independently_preserved_materials', read_json(OUT / 'final_protected_bytes_receipt.json')['status'] == 'VERIFIED')
    execution = read_json(delta_dir / 'execution.json')
    a.check('actual_scan_exit0_and_frozen_root_snapshot', execution['exit_code'] == 0 and execution['snapshot_unchanged'] and execution['snapshot_sha256_before'] == execution['snapshot_sha256_after'])
    result = subprocess.run([str(ROOT / '.venv/bin/python'), str(ROOT / scanner.BUNDLE_SCRIPT), '--check'], cwd=ROOT, capture_output=True)
    a.check('C_actual_bundle_check', result.returncode == 0)
    a.check('no_new_installs_recorded', all(not v for v in report['dependency_record']['registered_installations'].values()))
    a.check('all_environment_versions_match', all(v['matches'] for v in report['dependency_record']['package_version_checks']))

    # Independently locate all actual formal model proposals with failed guards.
    manifest = read_json(EV / 'runs/g2-evaluation-modes-01/manifest.json')
    failed = []
    statuses = Counter()
    proposals = 0
    for e in manifest['mode_episodes']:
        ep = read_json(EV / 'runs/g2-evaluation-modes-01' / e['path'])
        for rec in ep['records']:
            for p in rec['proposal_records']:
                proposals += 1
                a.check('formal_original_proposal_legal_executed', p['legal'] and p['executed'])
                if ep['mode'] == 'llm-only':
                    a.check('llmonly_only_locked_original', p['executed_config_id'] == rec['selected_config_id'] and rec['selection']['reason'] == 'LOCKED_SINGLE_PROPOSAL')
                    assessment = rec['research_assessment']
                else:
                    assessment = rec['selection']['assessments'][p['executed_config_id']]
                statuses[assessment['status']] += 1
                if assessment['status'] == 'TRADEOFF':
                    failed.append([ep['episode_id'], rec['record_id'], p['round'], p['original']['candidate_id'], p['executed_config_id']])
    witnesses_path = EV / 'a_epoch02/final_handoff_check/formal_eval_tradeoff_witnesses.json'
    witnesses = read_json(witnesses_path)
    a.check('467_original_proposals_and_exact_two_coverage_tradeoffs', proposals == 467 and len(failed) == 2)
    a.same('complete_formal_research_status_counts', dict(statuses), {'SUPPORTED_WITHIN_SCOPE':291, 'NO_DEMONSTRATED_GAIN':152, 'REJECTED_BY_CONSTRAINT':22, 'TRADEOFF':2})
    a.same('no_cherry_picked_formal_coverage_tradeoff_examples', sorted(failed), sorted([[w['episode_id'], w['record_id'], w['round'], w['candidate_id'], w['config_id']] for w in witnesses]))
    for w in witnesses:
        for kind in ['episode', 'trace', 'lock']:
            a.check('formal_witness_current_binding', digest(ROOT / w[kind + '_path']) == w[kind + '_sha256'])
        ep = read_json(ROOT / w['episode_path'])
        rec = next(r for r in ep['records'] if r['record_id'] == w['record_id'])
        proposal = next(p for p in rec['proposal_records'] if p['original']['candidate_id'] == w['candidate_id'])
        a.same('original_proposal_quote_exact', proposal['original'], w['raw_proposal'])
        for source in w['raw_response_sources']:
            a.check('real_response_hash', digest(ROOT / source['path']) == source['sha256'])
            response = read_json(ROOT / source['path'])
            response_record = next(r for r in response['records'] if r['record_id'] == w['record_id'])
            a.check('real_raw_response_contains_exact_proposal', w['raw_proposal'] in response_record['proposals'])
        with gzip.open(ROOT / w['trace_path'], 'rt') as f:
            traces = json.load(f)['results']
        ref = traces[rec['reference_config_id']]['metrics']
        cand = traces[w['config_id']]['metrics']
        rb = {r['index'] for r in ref['common_point_errors'] if r['error'] is not None}
        cb = {r['index'] for r in cand['common_point_errors'] if r['error'] is not None}
        a.same('actual_lost_coverage_identities', sorted(rb - cb), w['lost_baseline_covered_indices'])
        a.check('explicit_coverage_denominators', len(rb) == w['baseline_covered_count'] and len(cb) == w['candidate_covered_count'])
        a.check('unavailable_baseline_mask_not_numeric_worsening', bool(rb-cb) and w['candidate_max_on_baseline_covered'] is None and w['unavailable_reason'] == 'BASELINE_COVERED_IDENTITIES_LOST' and w['own_coverage_error_values_are_comparable'] is False)
        lock = read_json(ROOT / w['lock_path'])
        a.check('negative_proposal_not_selected_not_fallback', lock['selected_config_id'] == w['selected_config_id'] != w['config_id'] and lock['fallback'] is w['fallback'] is False)
        a.check('frozen_protection_result_retained', lock['selection']['assessments'][w['config_id']]['status'] == w['research_status'] == 'TRADEOFF')
    targets = [bound(p) for p in [base/'release_check.json', base/'scope_inventory.json', base/'findings_disposition.json', delta_dir/'delta_reuse_receipt.json', delta_dir/'scope_inventory.json', delta_dir/'execution.json', scanner_path, EV/'release_checks/scan_release_delta.py', witnesses_path]]
    receipt = {'status': 'VERIFIED' if not a.errors else 'REJECTED', 'role_context': '/root/c_contract', 'classification': 'INDEPENDENT_C_RELEASE_PREPARATION_AND_FINAL_NEGATIVE_CASE_RECONCILIATION', 'at': now(), 'check_count': a.check_count, 'errors': a.errors, 'targets': targets, 'checked_components': ['exact_scope_and_hash_reuse', 'actual_changed_text_rescan', 'documented_portability_findings', 'bundle_and_dependency_checks', 'protected_G1_and_archives', 'formal_negative_proposal_raw_response_trace_lock'], 'unchecked_components': ['actual_staged_file_set', 'actual_git_commit_push_and_remote_readback', 'not_a_proof_absent_unknown_secret_formats', 'external_URL_and_fragment_validity'], 'publication_completed': False, 'full_scan_reuse_files': 3025, 'C_actual_changed_text_rescan_files': 54, 'C_characters_scanned': rescanned_chars, 'post_cutoff_mutable_or_C_review_changes': deviations, 'formal_proposals': proposals, 'formal_negative_proposals': len(witnesses), 'scope_limits': ['Binary formats retain hash/size inspection rather than content credential parsing.', 'Root must scan new acceptance/publication metadata and inspect the actual staged set before push.', 'Provider absolute CLI default is an explicit recorded LIVE environment dependency; default RECOMPUTE is provider-free.'], 'audit_program': bound(Path(__file__)), 'new_model_calls': 0, 'elapsed_seconds': time.perf_counter()-started}
    receipt['formal_original_proposal_research_statuses'] = dict(statuses)
    receipt['formal_negative_proposals'] = statuses['REJECTED_BY_CONSTRAINT'] + statuses['TRADEOFF']
    receipt['formal_coverage_tradeoff_witnesses'] = len(witnesses)
    receipt['C_audit_corrections'] = ['Initial schema probe corrected llm-only post-lock assessment access, without changing production.', 'Initial rejected C receipt conflated all 24 infeasible proposals with the two coverage TRADEOFF witnesses; 22 common-DP-budget constraint rejections are now retained separately.']
    write_json(OUT / 'release_preparation_receipt_v2.json', receipt, exclusive=True)
    print(json.dumps({k: receipt[k] for k in ['status','check_count','errors','elapsed_seconds']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
