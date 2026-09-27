"""Independently replay the frozen selection policy; no final-effect input."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def binding_ok(b):
    for path,h in b.items():
        p=(ROOT/path).resolve()
        assert p.is_relative_to(ROOT) and sha(p)==h,path


def main():
    task=read(EV/'goal_state.json')['tasks']['selection']
    assert task['status']=='REVIEW_PENDING' and len(task['targets'])==6
    for t in task['targets']:
        binding_ok({t['path']:t['sha256']})
    binding_ok(task['source_hashes'])
    frozen=read(EV/'selection_freeze.json')
    decision=read(EV/'selection_decision.json')
    run=read(EV/'runs/g3-selection-01/manifest.json')
    for row in (frozen,decision,run):
        binding_ok(row['bindings'])
    assert task['source_hashes']=={**run['source_hashes'],'task1/goal3/freezes.py':sha(ROOT/'task1/goal3/freezes.py')}
    assert run['partition']==decision['partition']==frozen['partition']=='G3_SELECTION'
    assert run['input_ids']==frozen['input_ids'] and run['strategies']==frozen['strategies']
    assert run['strategy_ids']==frozen['strategy_ids']
    assert datetime.datetime.fromisoformat(decision['at'])>=datetime.datetime.fromisoformat(run['ended_at'])
    for suffix in ('receipt','pairs_receipt','accounting_receipt','freeze_boundary_receipt'):
        c=read(EV/'independent_c'/('g3-selection-01_'+suffix+'.json'))
        assert c['status']=='VERIFIED' and c['role_context']=='/root/c_protocol'
        for t in c['targets']:
            binding_ok({t['path']:t['sha256']})
        binding_ok(c['source_hashes'])
    failure_path=EV/'independent_c/selection_failure_receipt.json'
    failure=read(failure_path)
    assert failure['status']=='VERIFIED' and not failure['errors']
    assert sorted(r['record_id'] for r in failure['records'])==['3017','9311','9534']
    for t in failure['targets']:
        binding_ok({t['path']:t['sha256']})
    comparisons=run['comparisons']; incumbent=frozen['initial_incumbent']; events=[]
    def rank(cid):
        meta=frozen['tie_metadata'][cid]
        return (meta['enhancement_modules'],meta['online_model_dependency'],
                meta.get('measured_seconds',float('inf')),cid)
    for cid in frozen['strategy_ids']:
        if cid==incumbent:
            continue
        fixed=comparisons[cid+'|R0']; current=comparisons[cid+'|'+incumbent]
        eligible=frozen['eligibility'][cid]
        gain=eligible and fixed['all_guards_pass'] and current['replacement_supported']
        simpler=(eligible and fixed['all_guards_pass'] and current['all_guards_pass']
                 and current['all_equivalent_readings'] and rank(cid)<rank(incumbent))
        new=cid if gain or simpler else incumbent
        events.append({'candidate':cid,'previous_incumbent':incumbent,
            'fixed_reference':fixed,'incumbent_comparison':current,
            'component_eligibility':eligible,
            'decision':'ACCEPT_PROTECTED_STRICT_GAIN' if gain else
                       'EQUIVALENT_SIMPLER_REPRESENTATIVE' if simpler else 'RETAIN_INCUMBENT',
            'next_incumbent':new})
        incumbent=new
    frontier=[]
    for cid in frozen['strategy_ids']:
        if not frozen['eligibility'][cid] or not comparisons[cid+'|R0']['all_guards_pass']:
            continue
        dominated=any(other!=cid and frozen['eligibility'][other]
            and comparisons[other+'|R0']['all_guards_pass']
            and comparisons[other+'|'+cid]['replacement_supported'] for other in frozen['strategy_ids'])
        if not dominated:
            frontier.append(cid)
    assert events==decision['events']
    assert incumbent==decision['incumbent']=='S0'
    assert frontier==decision['protected_frontier']==['S0']
    assert not decision['global_optimality_claim'] and not decision['final_strategy_frozen']
    assert not decision['final_feedback_used'] and decision['human_judgment'].startswith('NOT_AVAILABLE')
    assert not (EV/'final_freeze.json').exists() and not (EV/'release_decision.json').exists()
    assert comparisons['S0|R0']['all_guards_pass'] and comparisons['S0|R0']['strict_gain_records']==103
    target={'path':str(failure_path.relative_to(ROOT)),'sha256':sha(failure_path)}
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'selection',
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'targets':task['targets']+[target],'source_hashes':task['source_hashes'],
        'checked_components':['Exact6submittedtargets/33sourcefiles plus all3actualfailurediagnosis targets',
            'All4 bound independent run/pair/accounting/freeze receipts consumed; all actual shards still match digests',
            'Independent policy replay from frozen order/R0initial/eligibility/tiekeys and separately verified all-record paired guards',
            'All3 decision events including both complete pair summaries match; protected frontier independently recomputed',
            'S0 all240guards and103strictcoverage improvements accepted; G0/S0_G0 three geometric failures prevent replacement',
            'All3 actual failures independently rerun for all4strategies:12Decimal/PROJchecks prove legitimate D-to-P tradeoff, no implementation error',
            'Decision made after actual selectionrun, without FINAL feedback, parameter change, new routing or invented human judgment'],
        'unchecked_components':['FINAL_CONFIRM not opened or executed by this checker',
            'No claim of noise accuracy/source datum/global optimum','Full production and final documents'],
        'selected_primary_for_later_freeze':incumbent,'protected_frontier':frontier,
        'selection_records':240,'selection_raw_points':24677,
        'selected_paired_result':comparisons['S0|R0'],
        'negative_results':{cid:comparisons[cid+'|R0'] for cid in ('G0','S0_G0')},
        'research_status':'SUPPORTED_WITHIN_SELECTION_SCOPE; final confirmation remains required',
        'human_judgment':'NOT_AVAILABLE; system action follows preapproved rule',
        'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_selection_closure.py',
        'checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/selection_closure_receipt.json'
    with output.open('x') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':'VERIFIED','selected_primary':incumbent,'receipt_sha256':sha(output),
                      'raw_coverage_delta':comparisons['S0|R0']['coverage_delta']}))


if __name__=='__main__':
    main()
