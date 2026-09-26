"""Goal 2 release delta: reuse exact-byte text checks, repeat other checks.

This is B publication preparation, not independent C scientific acceptance.
The existing scanner remains unchanged. Unchanged text results are reused only
when their path, SHA256, and scanner source match the recorded baseline.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'task1/evidence/goal2/release_checks'
SOURCE = BASE / 'scan_release.py'
spec = importlib.util.spec_from_file_location('goal2_existing_release_scan', SOURCE)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


def read(path):
    return json.loads(path.read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dispositions', type=Path,
                        default=BASE / 'final_01/findings_disposition.json')
    args = parser.parse_args()
    baseline = (ROOT / args.baseline).resolve()
    output = (ROOT / args.output).resolve()
    dispositions_path = (ROOT / args.dispositions).resolve()
    if not baseline.is_relative_to(BASE) or not output.is_relative_to(BASE) or output.exists():
        raise ValueError('NEW_RELEASE_DELTA_DIRECTORY_AND_BOUNDED_BASELINE_REQUIRED')
    old = read(baseline / 'release_check.json')
    inventory_path = baseline / 'scope_inventory.json'
    if scanner.sha(SOURCE) != old['scanner_sha256']:
        raise ValueError('SCANNER_SOURCE_CHANGED_FULL_TEXT_SCAN_REQUIRED')
    if scanner.sha(inventory_path) != old['inventory_sha256']:
        raise ValueError('BASELINE_INVENTORY_CHANGED')
    inventory = {row['path']: row for row in read(inventory_path)}
    old_secrets = defaultdict(list)
    for finding in old['secret_pattern_findings']:
        old_secrets[finding['path']].append({k: v for k, v in finding.items() if k != 'path'})
    old_absolute = {row['path']: row['lines'] for row in old['absolute_path_findings']}
    actual_scan_text = scanner.scan_text
    reused, rescanned = [], []

    def exact_byte_text_check(path):
        name = scanner.relative(path)
        current_hash = scanner.sha(path)
        previous = inventory.get(name, {})
        if (previous.get('sha256') == current_hash
                and previous.get('classification') == 'PROPOSED_G2_SUBSTANTIVE_FILE'):
            reused.append({'path': name, 'sha256': current_hash})
            return old_secrets.get(name, []), old_absolute.get(name, []), 0
        findings, absolute, characters = actual_scan_text(path)
        rescanned.append({'path': name, 'sha256_before_scan': current_hash,
                          'sha256_after_scan': scanner.sha(path), 'characters_scanned': characters})
        return findings, absolute, characters

    actual_command = list(sys.argv)
    started, timer = now(), time.perf_counter()
    scanner.scan_text = exact_byte_text_check
    try:
        sys.argv = [str(SOURCE), '--output', str(output), '--final']
        underlying_exit = scanner.main()
    finally:
        scanner.scan_text = actual_scan_text
        sys.argv = actual_command
    report = read(output / 'release_check.json')
    current_inventory = {row['path']: row for row in read(output / 'scope_inventory.json')}
    current_paths = scanner.scope(output)
    end_snapshot, drift = {}, []
    for path in current_paths:
        if path.is_symlink():
            continue
        name = scanner.relative(path)
        try:
            end_snapshot[name] = {'bytes': path.stat().st_size, 'sha256': scanner.sha(path)}
        except FileNotFoundError:
            end_snapshot[name] = {'missing': True}
        recorded = current_inventory.get(name)
        if not recorded or recorded.get('sha256') != end_snapshot[name].get('sha256'):
            drift.append(name)
    disappeared_during_scan = sorted(set(current_inventory) - set(end_snapshot))
    removed_since_baseline = sorted(name for name, row in inventory.items()
                                    if row.get('classification') == 'PROPOSED_G2_SUBSTANTIVE_FILE'
                                    and name not in current_inventory)
    unstable_text = [row['path'] for row in rescanned
                     if row['sha256_before_scan'] != row['sha256_after_scan']]
    dispositions = read(dispositions_path)
    reviewed = {row['path']: row for row in dispositions['findings']}
    resolved_absolute, unresolved_absolute = [], []
    for item in report['absolute_path_findings']:
        if item['classification'] not in ('REPRODUCTION_SOURCE_REQUIRES_REVIEW', 'NOTEBOOK_CODE_DEPENDENCY'):
            continue
        bound = reviewed.get(item['path'])
        current_hash = end_snapshot.get(item['path'], {}).get('sha256')
        if bound and current_hash == bound['sha256']:
            resolved_absolute.append({'finding': item, 'bound_review': bound})
        else:
            unresolved_absolute.append(item)
    contract_path = ROOT / 'task1/config/goal2/contract.json'
    contract = read(contract_path)
    raw_path = ROOT / contract['raw_path']
    raw_hash = scanner.sha(raw_path)
    raw_check = {'path': contract['raw_path'], 'expected_sha256': contract['raw_sha256'],
                 'actual_sha256': raw_hash, 'matches': raw_hash == contract['raw_sha256']}
    unresolved = dict(report['blocking_counts'])
    unresolved['reproduction_absolute_path_findings'] = len(unresolved_absolute)
    unresolved.update(whole_scan_file_drift=len(drift) + len(disappeared_during_scan),
                      text_scan_byte_drift=len(unstable_text),
                      substantive_files_removed_since_baseline=len(removed_since_baseline),
                      raw_hash_mismatch=int(not raw_check['matches']))
    ok = not any(unresolved.values())
    receipt = {
        'classification': 'EXACT_BYTE_REUSED_TEXT_CHECKS_WITH_REAL_DELTA_SCAN',
        'status': 'DELTA_CONTENT_CHECKS_CLEAR_WITH_BOUND_PATH_REVIEW' if ok else 'DELTA_FINDINGS_REQUIRE_REVIEW',
        'started_at': started, 'ended_at': now(),
        'elapsed_monotonic_seconds': time.perf_counter() - timer,
        'actual_command': actual_command,
        'underlying_scanner_exit_code': underlying_exit,
        'underlying_report_status': report['status'],
        'baseline_report': {'path': scanner.relative(baseline / 'release_check.json'),
                            'sha256': scanner.sha(baseline / 'release_check.json')},
        'baseline_inventory': {'path': scanner.relative(inventory_path), 'sha256': scanner.sha(inventory_path)},
        'scanner_source_sha256': scanner.sha(SOURCE), 'delta_source_sha256': scanner.sha(Path(__file__)),
        'text_reuse': reused, 'text_rescans': rescanned,
        'text_reuse_count': len(reused), 'actual_text_rescan_count': len(rescanned),
        'actual_text_characters_rescanned': sum(row['characters_scanned'] for row in rescanned),
        'local_links_rechecked_all_current_markdown': report['local_links_checked'],
        'protected_originals_rechecked': report['protected_tracked_files'],
        'bundle_check_reexecuted': report['bundle_check'],
        'dependency_inventory_rechecked': report['dependency_record'],
        'raw_check': raw_check,
        'reviewed_portability': resolved_absolute, 'unreviewed_portability': unresolved_absolute,
        'portability_review_binding': {'path': scanner.relative(dispositions_path),
                                       'sha256': scanner.sha(dispositions_path)},
        'unresolved_counts': unresolved,
        'created_or_changed_after_scanner_read': drift,
        'removed_during_scan': disappeared_during_scan,
        'removed_since_baseline': removed_since_baseline,
        'unstable_text_reads': unstable_text,
        'cutoff_snapshot': end_snapshot,
        'source_inventory_sha256': scanner.sha(output / 'scope_inventory.json'),
        'scope_limits': [
            'Only exact matching text bytes reuse the baseline findings; changed and new plaintext/gzip are actually read.',
            'All current Markdown local links, protected material bytes, raw hash, bundle, dependencies, sizes and caches are rechecked.',
            'Three documented path reviews are exact-hash bound; the original scanner report and nonzero flags remain preserved.',
            'This does not replace independent C acceptance or remote publication verification.',
            'Writes are new release receipts only; no production source edit, staging, commit, push, install or account history read.'
        ]}
    scanner.write(output / 'delta_reuse_receipt.json', receipt)
    print(json.dumps({'status': receipt['status'], 'reused_text_files': len(reused),
                      'actually_rescanned_text_files': len(rescanned), 'unresolved_counts': unresolved,
                      'receipt': scanner.relative(output / 'delta_reuse_receipt.json')}))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
