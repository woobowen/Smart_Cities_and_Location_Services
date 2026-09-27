"""Merge actual independent delivery evidence; never run a Notebook or edit Journal.

prepare emits a precise submission set, with missing evidence as blockers.
accept requires that exact set to be submitted and all actual FULLs complete.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from review_internal_acceptance import (Review, ROOT, EV, read, objsha,
    MUTABLE_CLOSEOUT, NOTEBOOK_RECEIPTS, RAW_SHA, PROCESSING_CODE, NOTEBOOK_CODE)

C = EV/'independent_c'
ROLE = '/root/c_protocol'
EXTERNAL = {'META_DEPENDENCY', 'EVIDENCE_MASTER_DEPENDENCY'}


def collect(task):
    review = Review()
    state = read(EV/'goal_state.json')
    roles = {r['context'] for r in state['role_dispatches'] if r['role'] == 'C'}
    assert ROLE in roles
    findings = []
    receipts = {}
    previous = read(C/'notebook_review_submission_preparation.json')
    review.target_rows(previous['checked_current_local_targets'])
    review.mapping(previous['current_proposed_source_hashes'], source=True)
    review.check(C/'notebook_review_submission_preparation.json')
    for name in NOTEBOOK_RECEIPTS:
        path = C/name
        if not path.is_file():
            review.blockers.append({'kind': 'FULL_NOTEBOOK_RECEIPT_MISSING', 'path': str(path.relative_to(ROOT))})
            continue
        _, r = review.receipt(path, roles)
        assert r['role_context'] == ROLE and r['new_provider_attempts_observed'] == 0
        assert r['raw_sha256'] == RAW_SHA and not r['errors']
        basic, isolated = 'basic' in name, name.startswith('isolated_')
        assert r['executed_code_cells'] == (12 if basic else 8)
        assert r['history']['record_candidate_recomputations'] == (9720 if basic else 6001)
        if basic:
            p = r['production']
            assert (p['raw_records'], p['raw_points'], p['record_candidate_recomputations']) == (11386, 1173410, 22772)
            assert p['new_shards_actual_hash_checked'] == 285 and p['cached_trace_rechecks'] == 0
            assert p['code_identity_source'] == ('FROZEN_SOURCE_BUNDLE' if isolated else 'ACTUAL_LOCAL_GIT_HEAD')
            assert p['code_sha'] == (PROCESSING_CODE if isolated else NOTEBOOK_CODE)
            assert r['demonstration']['synthetic_processing_chains'] == 19
        else:
            assert r['history']['record_episode_selections'] == 384
        receipts[('isolated' if isolated else 'repository', 'basic' if basic else 'system')] = r
        findings.append({'receipt': str(path.relative_to(ROOT)), 'sha256': review.digest(path),
                         'cells': r['executed_code_cells'], 'elapsed_seconds': r['elapsed_seconds_actual_execution']})

    _, archive = review.receipt(C/'isolated_archive_binding_receipt.json', roles)
    review.receipt(C/'full_notebook_figure_visual_receipt.json', roles)
    build_path, closure_path = EV/'package/package_build_receipt.json', EV/'package/source_closure.json'
    build, closure = read(build_path), read(closure_path)
    review.check(build_path); review.check(closure_path)
    assert closure['status'] == 'STATIC_CLOSURE_COMPLETE' and not closure['errors'] and not closure['missing']
    assert closure['package_status'] == build['status'] == 'REVIEW_ONLY'
    assert closure['member_count'] == len(closure['members']) == 112
    assert build['zip_sha256'] == archive['zip_sha256']
    members = {r['path']: r['archive_sha256'] for r in closure['members']}
    for member in closure['members']:
        review.check(member.get('source_path', member['path']), member['source_sha256'])
    for kind in ('basic', 'system'):
        isolated = receipts.get(('isolated', kind))
        if isolated is None:
            continue
        original = receipts[('repository', kind)]
        assert isolated['input_notebook_sha256'] == original['executed_notebook_sha256']
        package = isolated['isolated_package']
        assert package['package_manifest_sha256'] == archive['package_manifest_sha256']
        assert package['original_members_unchanged'] == 112
        assert {r['path']: r['sha256'] for r in package['package_members_checked']} == members
        launch = next(r for r in archive['launch_checks'] if r['kind'] == kind)
        assert launch['input_notebook_sha256'] == isolated['input_notebook_sha256']
        assert members[launch['input_notebook_path']] == isolated['input_notebook_sha256']

    static_path = EV/'independent_documents/actual_zip_static_receipt.json'
    static = read(static_path); review.check(static_path)
    assert static['role_context'] in roles and static['status'] == 'VERIFIED_ACTUAL_ZIP_STATIC_CLOSURE_PENDING_FULL'
    assert not static['errors'] and all(r['passed'] for r in static['checks'])
    assert static['independent_fresh_zip_probe']['status'] == 'VERIFIED'
    review.target_rows(static['targets'])
    review.check('task1/evidence/goal3/independent_documents/review_actual_zip.py', static['checker_sha256'], source=True)
    for source in ('task1/goal3/package.py', 'task1/goal3/execute_notebook.py',
                   'task1/evidence/goal3/independent_c/review_internal_acceptance.py',
                   str(Path(__file__).resolve().relative_to(ROOT))):
        review.check(source, source=True)

    dependencies = {}
    required = ('production',) if task == 'notebooks' else ('notebooks', 'experiment_report', 'process_report')
    external = set()
    for name in required:
        row = state['tasks'][name]
        if row['status'] not in {'VERIFIED', 'BLOCKED_EXTERNAL'}:
            review.blockers.append({'kind': 'DEPENDENCY_NOT_CLOSED', 'task': name, 'status': row['status']})
            continue
        review.target_rows([row['receipt']])
        receipt = read(ROOT/row['receipt']['path'])
        part = receipt.get('tasks', {}).get(name, receipt)
        assert row['verifier'] == receipt['role_context'] in roles and row['verifier'] != row['author']
        assert part['status'] == row['status'] and part['source_hashes'] == row['source_hashes']
        assert {objsha(r) for r in row['targets']} <= {objsha(r) for r in part['targets']}
        # Dependencies keep their own complete target sets; verify their current
        # bytes without duplicating hundreds of report-render targets here.
        for target in row['targets']:
            review.check(target['path'], target['sha256'], collect=False)
        for source, sha in row['source_hashes'].items():
            review.check(source, sha, collect=False)
        if row['status'] == 'BLOCKED_EXTERNAL':
            assert name in {'experiment_report', 'process_report'}
            assert part.get('available_engineering_status', part.get('engineering_status')) == 'VERIFIED'
            deps = set(part['external_dependencies'])
            assert deps and deps <= EXTERNAL
            external |= deps
        else:
            assert name in {'production', 'notebooks'}
        dependencies[name] = {'status': row['status'], 'receipt': row['receipt'],
                              'target_count': len(row['targets']), 'source_count': len(row['source_hashes'])}
    if task == 'package':
        assert external == EXTERNAL
    for name, issue in state['issues'].items():
        if issue.get('parent_task') == task and issue['status'] != 'VERIFIED':
            review.blockers.append({'kind': 'OPEN_TASK_ISSUE', 'issue': name})
    assert not set(review.targets) & MUTABLE_CLOSEOUT
    return review, state, {'actual_full_receipts': findings, 'dependencies_observed': dependencies,
        'external_dependencies': sorted(external), 'zip_sha256': archive['zip_sha256'],
        'package_manifest_sha256': archive['package_manifest_sha256'],
        'scope': 'Actual independent four-FULL receipts and same-archive source/launch binding; no numerical recomputation',
        'old_static_receipts_scope': 'As-of builder/static checks are retained; only completed FULL receipts establish runtime completion.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task', choices=('notebooks', 'package'), required=True)
    p.add_argument('--mode', choices=('prepare', 'accept'), default='prepare')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    review, state, details = collect(args.task)
    targets = [{'path': p, 'sha256': s} for p, s in sorted(review.targets.items())]
    sources = dict(sorted(review.sources.items()))
    result = {'role_context': ROLE, 'task_id': args.task, 'target_id': args.task,
        'at': datetime.now(timezone.utc).isoformat(), 'status': 'PREPARATION_ONLY_NOT_PARENT_ACCEPTANCE',
        'targets': targets, 'source_hashes': sources, 'blockers': review.blockers,
        'ready_for_actual_submission': not review.blockers, 'new_numerical_processing': 0,
        'new_model_calls': 0, 'does_not_close_any_task': True, **details}
    if args.mode == 'accept':
        assert not review.blockers, ('INCOMPLETE_DELIVERY', review.blockers)
        row = state['tasks'][args.task]
        assert row['status'] == 'REVIEW_PENDING' and row['author'] != ROLE
        assert {objsha(r) for r in row['targets']} == {objsha(r) for r in targets}, 'SUBMITTED_TARGET_SET_DIFFERS'
        assert row['source_hashes'] == sources, 'SUBMITTED_SOURCE_SET_DIFFERS'
        result.update(status='VERIFIED' if args.task == 'notebooks' else 'BLOCKED_EXTERNAL',
            engineering_status='VERIFIED', available_engineering_status='VERIFIED',
            checked_components=['Four completed fresh-kernel FULL runs with independent exact scope/count/zero-Provider reviews',
                'Current canonical Notebook sources and output promotion; original teacher files retained',
                'Same actual ZIP, complete member/source closure, isolated input/import/launch identity',
                'Current exact task submission and independently closed dependency receipts'],
            unchecked_components=['Official identity and Evidence Master inputs/LOCK', 'Remote publication, external GPT review and user Understanding'],
            package_status='REVIEW_ONLY', Submission='NOT_READY', GPT_SECOND_REVIEW='PENDING',
            does_not_close_any_task=False, controller_consumption='Root must separately consume this receipt with Journal.accept.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'status': result['status'], 'targets': len(targets), 'sources': len(sources),
        'blockers': review.blockers, 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
