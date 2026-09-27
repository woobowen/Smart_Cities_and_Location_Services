"""Read-only C closure of the submitted development decision graph."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EV = ROOT/'task1/evidence/goal3'
C = EV/'independent_c'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_ok(target):
    path = (ROOT/target['path']).resolve()
    assert path.is_relative_to(ROOT), target
    assert path.is_file() and sha(path) == target['sha256'], target


def binding_ok(bindings):
    for p, h in bindings.items():
        target_ok({'path': p, 'sha256': h})


def subset_equal(given, actual):
    assert all(actual[k] == v for k, v in given.items()), (given, actual)


def main():
    state = read(EV/'goal_state.json')
    submitted = state['tasks']['development']
    assert submitted['status'] == 'REVIEW_PENDING'
    assert len(submitted['targets']) == 18
    for target in submitted['targets']:
        target_ok(target)
    binding_ok(submitted['source_hashes'])
    for issue in state['issues'].values():
        if issue['parent_task'] in ('implementation', 'development'):
            assert issue['status'] == 'VERIFIED', issue['issue_id']
    contract = read(ROOT/'task1/config/goal3/contract.json')
    split = read(EV/'split_manifest.json')
    plan = read(EV/'a_candidate_plan.json')
    defs = {r['candidate_id']: r for r in plan['candidate_definitions']}
    run_ids = ['g3-development-parents-03', 'g3-development-routing-03',
               'g3-development-interactions-01']
    runs = []
    checked_shards = 0
    for rid in run_ids:
        path = EV/'runs'/rid/'manifest.json'
        run = read(path)
        binding_ok(run['bindings'])
        assert run['source_hashes'] == submitted['source_hashes']
        assert run['partition'] == 'G3_DEVELOPMENT'
        assert run['input_ids'] == split['partitions']['G3_DEVELOPMENT']
        assert run['completed_record_ids'] == run['input_ids']
        assert not run['failed_records'] and run['new_record_model_calls'] == 0
        assert run['strategies'] == {cid: defs[cid] for cid in run['strategy_ids']}
        for shard in run['shards']:
            assert sha(path.parent/shard['path']) == shard['sha256']
            checked_shards += 1
        for suffix in ('receipt', 'pairs_receipt', 'accounting_receipt'):
            receipt = read(C/(rid+'_'+suffix+'.json'))
            assert receipt['role_context'] == '/root/c_protocol'
            assert receipt['status'] == 'VERIFIED'
            for target in receipt['targets']:
                target_ok(target)
            if 'source_hashes' in receipt:
                binding_ok(receipt['source_hashes'])
            assert {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)} in receipt['targets']
        runs.append(run)
    names = ['A1_RECOMPUTE03_DECISION.json', 'A2_DECISION.json', 'A3_DECISION.json']
    decisions = [read(EV/n) for n in names]
    for decision, run in zip(decisions, runs):
        assert decision['role_context'] == '/root/a_candidates'
        assert decision['target_run_id'] == run['run_id']
        assert decision['target_manifest_sha256'] == sha(EV/'runs'/run['run_id']/'manifest.json')
        assert decision['current_code_sha'] == run['code_sha']
        binding_ok(decision['bindings'])
        assert not decision['selection_results_read']
        assert not decision.get('FINAL_CONFIRM_results_read', decision.get('final_confirm_results_read'))
        assert not decision['final_method_frozen']
        assert decision['source_crs'] == 'UNVERIFIED'
        for cid, row in decision['candidate_status'].items():
            assert row['fixed_reference_comparison'] == run['comparisons'][cid+'|R0']
            subset_equal(row['readings'], run['record_metrics'][cid])
            if row.get('P_component_comparison') is not None:
                ref = 'S0' if cid.startswith('S0_') else 'R0'
                assert row['P_component_comparison'] == run['P_comparisons'][cid+'|'+ref]
            if 'incumbent_comparison' in row:
                ref = row.get('previous_incumbent_at_comparison', decision['previous_incumbent'])
                assert row['incumbent_comparison'] == run['comparisons'][cid+'|'+ref]
            for parent, pair in row.get('parent_comparisons', {}).items():
                assert pair == run['comparisons'][cid+'|'+parent]
    a1, a2, a3 = decisions
    assert [(d['previous_incumbent'], d['next_incumbent']) for d in decisions] == [
        ('R0','S0'), ('S0','S0'), ('S0','S0_G0')]
    assert runs[0]['comparisons']['S0|R0']['replacement_supported']
    assert runs[1]['comparisons']['G0|R0']['replacement_supported']
    assert not runs[1]['comparisons']['G0|S0']['replacement_supported']
    incumbent = 'S0'
    events = []
    for cid in a3['consumption_order']:
        fixed = runs[2]['comparisons'][cid+'|R0']
        current = runs[2]['comparisons'][cid+'|'+incumbent]
        accepted = fixed['all_guards_pass'] and current['replacement_supported']
        events.append({'candidate': cid, 'previous_incumbent': incumbent, 'accepted': accepted})
        if accepted:
            incumbent = cid
    assert incumbent == a3['next_incumbent']
    for check in a3['component_removal_checks'].values():
        assert check['result'] == runs[2]['comparisons'][check['comparison']]
        assert not check['result']['all_guards_pass']
    analysis = read(EV/'runs'/run_ids[2]/'analysis/summary.json')
    assert a3['new_coverage'] == analysis['new_coverage']['S0_G0|R0']
    assert not a3['new_coverage']['noise_truth_claim']
    convergence = read(EV/'CONVERGENCE_REVIEW.json')
    target_ok(convergence['a3_decision_ref'])
    assert convergence['status'] == 'CONVERGED_WITHIN_REGISTERED_SCOPE'
    assert convergence['shortlist_order'] == a3['shortlist_order'] == ['R0','S0','G0','S0_G0']
    assert convergence['selection_initial_incumbent'] == contract['selection']['initial_incumbent'] == 'R0'
    assert not convergence['selection_results_read'] and not convergence['FINAL_CONFIRM_results_read']
    assert convergence['not_goal_complete'] and convergence['selection_cost_tie_value'] is None
    assert convergence['previous_incumbent_sequence'] == ['R0','S0','S0','S0_G0']
    for row in convergence['shortlist']:
        cid = row['canonical_id']
        for key in ('parameters', 'conditional_rule', 'order'):
            assert row[key] == defs[cid][key]
        assert row['enhancement_modules'] == a3['enhancement_modules'][cid]
        assert not row['online_model_dependency'] and row['measured_seconds'] is None
        assert row['measured_seconds_status'].startswith('UNKNOWN')
        assert row['parameters']['dp'] == 5
        subset_equal(row['development_readings'], runs[2]['record_metrics'][cid])
    singles = sum(d['new_single_definition_count'] for d in defs.values())
    combinations = sum(d['new_combination_definition_count'] for d in defs.values())
    assert (singles, combinations) == (1, 3)
    assert convergence['new_candidate_definitions']['single'] == singles
    assert convergence['new_candidate_definitions']['combination'] == combinations
    assert max(a3['enhancement_modules'].values()) <= 3
    text = (EV/'CONVERGENCE_REVIEW.md').read_text()
    assert 'S0_G0' in text and '6,704' in text and '178' in text
    targets = list(submitted['targets'])
    receipt = {'role_context': '/root/c_protocol', 'status': 'VERIFIED',
        'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'target_id': 'development', 'targets': targets, 'source_hashes': submitted['source_hashes'],
        'checked_components': [
            'Current submitted18targets and32processing sources: actual hashes; original three C run/pair/accounting receipts consumed',
            'Three current developmental manifests and all18compressed trace shard bytes still current; original raw/S-D-P/commonmetric reviews retained',
            'A1/A2/A3 actual candidate summaries, fixed/current/parent/P-only comparisons, sourcebindings and sequence against C-verified run data',
            'A3 three-candidate conservative incumbent loop independently replayed from all-record guards; both parent-removal comparisons and two S-parent ablations',
            'Four complete unchanged definitions, fixed order, R0 initial selection incumbent, null/unknown measured latency, dp5 release constraint',
            'One new single/three combinations/depth3; negative P and unconditional D results retained; evidence-based scope convergence without winner or global-optimum claim',
            'Manual reading of convergence JSON/Markdown and limitations: no selection/final effects viewed; no universal irreducibility claim for unregistered fine-grained combo ablations'],
        'unchecked_components': ['Future selection and final confirmation effects', 'Full production',
            'Source datum and real noise ground truth', 'Final reports/notebooks/package/publication',
            'Auxiliary freeze gate G3-C08 is separate repair required before actual selection freeze'],
        'evidence_scope': {'raw_records':240, 'raw_points':23950, 'development_manifests':3,
                           'checked_shards':checked_shards, 'candidate_definitions':11,
                           'shortlist':convergence['shortlist_order'], 'development_incumbent':incumbent,
                           'new_record_model_calls':0, 'governance_hidden_requests_and_cost':'unknown'},
        'independent_decision_replay':events,
        'research_interpretation':'SUPPORTED_WITHIN_EXPOSED_DEVELOPMENT_SCOPE; no final winner frozen; P variants not admitted for publication',
        'oracle_limit':'Full trace C checks previously use the external inherited reviewer; separate Decimal/PROJ recomputation covers40 stable records per run, not all records.',
        'not_new_user_approval': True, 'errors':[],
        'checker_development_note':'Initial C-only Markdown presence assertion expected an unformatted6704; actual prose correctly uses6,704. Assertion corrected after reading prose. No B artifact or numeric defect.',
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_development_closure.py',
        'checker_sha256':sha(Path(__file__))}
    output=C/'development_closure_receipt.json'
    with output.open('x') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'status':receipt['status'],'targets':len(targets),'shards':checked_shards,
                      'incumbent':incumbent,'receipt_sha256':sha(output)}))


if __name__ == '__main__':
    main()
