"""Write the actual stage freezes and apply the already registered decision rules."""
import argparse
import subprocess

from task1.workflow.io import ROOT, digest, read_json, write_json, now, bound_path
from .data import EV, CFG, GOAL
from .runtime import source_snapshot, definitions, assert_binding
from .selection import choose
from .control import Journal


def bindings(paths=()):
    contract = read_json(CFG/'contract.json')
    fixed = [CFG/'contract.json', EV/'split_manifest.json', EV/'a_candidate_plan.json',
             EV/'contract_freeze.json', ROOT/contract['mode']['memory_path'],
             ROOT/'task1/goal3/freezes.py']
    return {**source_snapshot(), **{str(p.relative_to(ROOT)): digest(p) for p in [*fixed, *paths]}}


def verified_task(name):
    journal = Journal()
    row = journal.state['tasks'][name]
    if row['status'] != 'VERIFIED' or not journal.current(row):
        raise ValueError('CURRENT_INDEPENDENT_C_TASK_REQUIRED:' + name)
    return ROOT/row['receipt']['path']


def verified_run(run_id):
    path = EV/'runs'/run_id/'manifest.json'
    run = read_json(path)
    assert_binding(run['bindings'])
    receipt_path = EV/'independent_c'/(run_id+'_receipt.json')
    receipt = read_json(receipt_path)
    if (run['status'] != 'MACHINE_VERIFIED_PENDING_C' or run['failed_records']
            or run['completed_record_ids'] != run['input_ids']
            or run['source_hashes'] != source_snapshot()
            or receipt['status'] != 'VERIFIED'
            or receipt.get('source_hashes') != run['source_hashes']
            or {'path': str(path.relative_to(ROOT)), 'sha256': digest(path)} not in receipt['targets']):
        raise ValueError('COMPLETE_INDEPENDENTLY_VERIFIED_RUN_REQUIRED')
    for target in receipt['targets']:
        if digest(bound_path(ROOT, target['path'])) != target['sha256']:
            raise ValueError('STALE_INDEPENDENT_REVIEW_TARGET:' + target['path'])
    for shard in run['shards']:
        if digest(bound_path(path.parent, shard['path'])) != shard['sha256']:
            raise ValueError('CHANGED_ACTUAL_RUN_SHARD:' + shard['path'])
    return run, [path, receipt_path]


def common(partition, strategy_ids, paths):
    contract = read_json(CFG/'contract.json')
    split = read_json(EV/'split_manifest.json')
    ids = ([rid for group in split['partitions'].values() for rid in group]
           if partition == 'FULL_PRODUCTION' else split['partitions'][partition])
    registry = definitions()
    return {'goal_id': GOAL, 'frozen_at': now(), 'partition': partition, 'input_ids': ids,
            'strategy_ids': strategy_ids, 'strategies': {cid: registry[cid] for cid in strategy_ids},
            'bindings': bindings(paths), 'processing_source_hashes': source_snapshot(),
            'processing_code_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'source_crs': 'UNVERIFIED', 'working_model': contract['model'],
            'record_mode': contract['mode']['default_candidate_mode'],
            'new_record_model_calls': 0, 'memory': contract['mode'],
            'record_verifier_fallback': False, 'per_record_failure_policy': 'STOP_AFFECTED_RUN_AND_REPAIR_IMPLEMENTATION',
            'selection_rules': contract['selection'], 'release_rules': contract['release_gate'],
            'authority': 'CURRENT_USER_PREAPPROVED_RULES; internal review is not a new user approval'}


def selection_freeze():
    receipt = verified_task('development')
    convergence = read_json(EV/'CONVERGENCE_REVIEW.json')
    if convergence['status'] != 'CONVERGED_WITHIN_REGISTERED_SCOPE':
        raise ValueError('DEVELOPMENT_NOT_CONVERGED')
    ids = convergence['shortlist_order']
    if len(ids) > 4 or ids[0] != 'R0':
        raise ValueError('SHORTLIST_SCOPE')
    frozen = common('G3_SELECTION', ids, [receipt, EV/'CONVERGENCE_REVIEW.json', EV/'A3_DECISION.json'])
    frozen.update(initial_incumbent='R0', development_incumbent=convergence['previous_incumbent_sequence'][-1],
                  eligibility={cid: True for cid in ids},
                  tie_metadata={row['canonical_id']: {'enhancement_modules': row['enhancement_modules'],
                    'online_model_dependency': row['online_model_dependency']} for row in convergence['shortlist']},
                  measured_cost_status='UNKNOWN_FOR_ALL; no comparable per-strategy timer; absent key sorts equally',
                  selection_results_read_before_freeze=False, final_results_read_before_freeze=False,
                  no_new_candidate_or_rule_from_selection=True)
    write_json(EV/'selection_freeze.json', frozen, exclusive=True)
    return frozen


def selection_decision(run_id):
    frozen = read_json(EV/'selection_freeze.json'); assert_binding(frozen['bindings'])
    run, paths = verified_run(run_id)
    if (run['partition'] != 'G3_SELECTION' or run['input_ids'] != frozen['input_ids']
            or run['strategy_ids'] != frozen['strategy_ids']):
        raise ValueError('SELECTION_SCOPE_MISMATCH')
    decision = choose(frozen['strategy_ids'], run['comparisons'], initial=frozen['initial_incumbent'],
                      eligibility=frozen['eligibility'], tie_metadata=frozen['tie_metadata'])
    decision.update(at=now(), partition='G3_SELECTION', run_id=run_id,
                    bindings=bindings([*paths, EV/'selection_freeze.json']),
                    final_strategy_frozen=False, human_judgment='NOT_AVAILABLE; system decision under approved rules',
                    next_action='FREEZE_PRIMARY_AND_R0_BEFORE_FINAL_CONFIRM', final_feedback_used=False)
    write_json(EV/'selection_decision.json', decision, exclusive=True)
    return decision


def final_freeze():
    receipt = verified_task('selection')
    decision = read_json(EV/'selection_decision.json'); assert_binding(decision['bindings'])
    primary = decision['incumbent']
    ids = list(dict.fromkeys(['R0', primary]))
    frozen = common('FINAL_CONFIRM', ids, [receipt, EV/'selection_decision.json', EV/'selection_freeze.json'])
    frozen.update(primary_strategy=primary, fallback_strategy='R0',
                  final_results_read_before_freeze=False,
                  confirmation_decision='primary must pass every fixed guard and show registered strict gain; otherwise R0',
                  no_final_parameter_selection=True, A_research_context_receives_final_effects=False,
                  optional_parent_comparisons='none needed for this one-shot release gate; complete parents preserved in development/selection')
    write_json(EV/'final_freeze.json', frozen, exclusive=True)
    return frozen


def release_decision(run_id):
    frozen = read_json(EV/'final_freeze.json'); assert_binding(frozen['bindings'])
    run, paths = verified_run(run_id)
    if (run['partition'] != 'FINAL_CONFIRM' or run['input_ids'] != frozen['input_ids']
            or run['strategy_ids'] != frozen['strategy_ids']):
        raise ValueError('CONFIRMATION_SCOPE_MISMATCH')
    primary = frozen['primary_strategy']
    pair = run['comparisons'][primary+'|R0']
    supported = primary != 'R0' and pair['all_guards_pass'] and pair['replacement_supported']
    final = primary if supported else 'R0'
    decision = {'at': now(), 'run_id': run_id, 'primary_strategy': primary, 'final_strategy': final,
                'status': 'SUPPORTED_WITHIN_SCOPE' if supported else 'PREDECLARED_REFERENCE_RELEASE',
                'trigger': pair, 'predeclared_fallback_used': primary != 'R0' and not supported,
                'retuning_or_new_winner_selection_on_final': False,
                'bindings': bindings([*paths, EV/'final_freeze.json']),
                'interpretation': 'One predeclared release gate on the complete frozen sample; not proof of universal superiority.',
                'human_judgment': 'NOT_AVAILABLE; system decision under preapproved release rule'}
    write_json(EV/'release_decision.json', decision, exclusive=True)
    return decision


def production_freeze():
    receipt = verified_task('confirmation')
    decision = read_json(EV/'release_decision.json'); assert_binding(decision['bindings'])
    final = decision['final_strategy']
    ids = list(dict.fromkeys(['R0', final]))
    frozen = common('FULL_PRODUCTION', ids, [receipt, EV/'release_decision.json', EV/'final_freeze.json'])
    frozen.update(final_strategy=final, full_scope='ALL_PARTITIONS_INCLUDING_EXPOSED_DEVELOPMENT',
                  same_strategy_single_execution=final == 'R0',
                  method_changes_from_full_results_forbidden=True,
                  full_statistics_identity='DESCRIPTIVE_DATASET_PRODUCTION; not an independent test')
    write_json(EV/'production_freeze.json', frozen, exclusive=True)
    return frozen


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['selection-freeze', 'selection-decision', 'final-freeze',
                                          'release-decision', 'production-freeze'])
    parser.add_argument('--run-id')
    args = parser.parse_args()
    functions = {'selection-freeze': selection_freeze, 'selection-decision': selection_decision,
                 'final-freeze': final_freeze, 'release-decision': release_decision, 'production-freeze': production_freeze}
    if args.action.endswith('decision') and not args.run_id:
        parser.error('--run-id is required for a result decision')
    result = functions[args.action](args.run_id) if args.action.endswith('decision') else functions[args.action]()
    print({k: result[k] for k in ('partition', 'strategy_ids', 'incumbent', 'primary_strategy', 'final_strategy', 'status') if k in result})
