"""Close production only after actual whole-run, category, coordinate and table audits."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'
RUN='g3-full-production-01'


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def check(bindings):
    for name,value in bindings.items():
        p=(ROOT/name).resolve()
        assert p.is_relative_to(ROOT) and p.is_file() and sha(p)==value,name


def main():
    state=read(EV/'goal_state.json');task=state['tasks']['production']
    assert task['status']=='REVIEW_PENDING','REAL_CURRENT_PRODUCTION_SUBMISSION_REQUIRED'
    assert state['tasks']['confirmation']['status']=='VERIFIED'
    for t in task['targets']:check({t['path']:t['sha256']})
    check(task['source_hashes'])
    assert all(i['status']=='VERIFIED' for i in state['issues'].values())
    frozen=read(EV/'production_freeze.json');mp=EV/'runs'/RUN/'manifest.json';m=read(mp)
    for obj in (frozen,m):check(obj['bindings'])
    assert m['status']=='MACHINE_VERIFIED_PENDING_C' and m['partition']=='FULL_PRODUCTION'
    assert m['input_ids']==m['completed_record_ids']==frozen['input_ids'] and not m['failed_records']
    assert m['strategies']==frozen['strategies'] and m['strategy_ids']==frozen['strategy_ids']
    assert m['code_sha']==frozen['processing_code_sha']
    assert m['source_hashes']==frozen['processing_source_hashes']
    contract=read(ROOT/'task1/config/goal3/contract.json');raw_path=ROOT/contract['raw_path']
    assert sha(raw_path)==contract['raw_sha256'];raw=read(raw_path)
    assert Counter(m['input_ids'])==Counter({rid:1 for rid in raw})
    n=len(raw);points=sum(len(value[0]) for value in raw.values());assert (n,points)==(11386,1173410)
    receipts={}
    suffixes=['receipt','pairs_receipt','accounting_receipt','freeze_boundary_receipt','categories_receipt','coordinates_receipt','analysis_receipt']
    mandatory={str(mp.relative_to(ROOT)), 'task1/evidence/goal3/coordinates/coordinate_checks.json'}
    for suffix in suffixes:
        path=EV/'independent_c'/(RUN+'_'+suffix+'.json');receipt=read(path)
        assert receipt['status']=='VERIFIED' and receipt['role_context']=='/root/c_protocol' and not receipt['errors'],suffix
        for t in receipt['targets']:check({t['path']:t['sha256']})
        mandatory.update(t['path'] for t in receipt['targets'])
        check(receipt['source_hashes']);receipts[suffix]=receipt;mandatory.add(str(path.relative_to(ROOT)))
    boundary_path=EV/'independent_c/new_coverage_boundary_receipt.json';boundary=read(boundary_path)
    assert boundary['status']=='VERIFIED' and not boundary['errors']
    for t in boundary['targets']:check({t['path']:t['sha256']})
    mandatory.update(t['path'] for t in boundary['targets'])
    mandatory.add(str(boundary_path.relative_to(ROOT)))
    attribution_path=EV/'independent_c/full_filter_attribution_receipt.json';attribution=read(attribution_path)
    assert attribution['status']=='VERIFIED' and attribution['role_context']=='/root/c_protocol' and not attribution['errors']
    for t in attribution['targets']:check({t['path']:t['sha256']})
    mandatory.update(t['path'] for t in attribution['targets'])
    check(attribution['source_hashes'])
    mandatory.update([str(attribution_path.relative_to(ROOT)),'task1/evidence/goal3/full_filter_attribution.json'])
    assert mandatory<={t['path'] for t in task['targets']},('UNSUBMITTED_MANDATORY_ARTIFACT',mandatory-{t['path'] for t in task['targets']})
    for name in ['task1/goal3/freezes.py','task1/goal3/coordinates.py','task1/scripts/goal2_coordinate_sensitivity.py','task1/goal3/analysis.py','task1/goal3/filter_diagnostics.py']:
        assert task['source_hashes'].get(name)==sha(ROOT/name),('AUXILIARY_INVALIDATION_SOURCE_MISSING',name)
    r=receipts['receipt'];assert r['counts']['raw_records']==n and r['counts']['raw_points']==points
    assert r['counts']['distinct_config_trace_reviews']==n*len(m['strategy_ids'])
    for cid in m['strategy_ids']:
        assert sum(r['point_fate_totals'][cid].values())==points
        assert m['record_metrics'][cid]['n_input']==points and m['record_metrics'][cid]['n_records']==n
        assert m['record_metrics'][cid]['raw_break_crossings']==0
        assert m['record_metrics'][cid]['dp_checks_passed'] and m['record_metrics'][cid]['n_dp_exceedances']==0
    accounting=receipts['accounting_receipt']['derived_counts'];assert accounting['processing_evaluations']==n*len(m['strategy_ids'])
    assert accounting['cached_trace_rechecks']==accounting['reused_identical_configuration_observations']==accounting['new_record_model_calls']==0
    assert receipts['pairs_receipt']['paired_rows']==n*len(m['strategy_ids'])**2
    category=receipts['categories_receipt'];assert category['whole_dataset_records_categorized']==n
    assert len(category['random_records'])>=contract['full_audit']['independent_math_sample']['random_records']
    assert category['all_failure_receipts']['observed']==category['all_fallback_receipts']['observed']==0
    coord=receipts['coordinates_receipt'];assert coord['counts']['points_checked']==points and coord['counts']['records_checked']==n
    assert coord['counts']['unique_actual_traces_checked']==r['counts']['distinct_config_trace_reviews']
    cat_sample=set(category['random_records'])
    for c in category['categories'].values():cat_sample.update(c['selected_records'])
    assert cat_sample<=set(coord['independent_sensitivity_record_ids'])
    assert receipts['analysis_receipt']['records']==n
    assert receipts['analysis_receipt']['counts']['record_metrics']==n*len(m['strategy_ids'])
    final=frozen['final_strategy'];pair=m['comparisons'][final+'|R0']
    assert boundary['added_covered_original_points']==pair['coverage_delta']
    assert boundary['witness']['maximum_new_raw_to_final_error_work_m']==pair['new_coverage_max_error']
    assert attribution['actual_records']==n and attribution['actual_points']==points
    assert attribution['newly_covered_points']==pair['coverage_delta']
    assert final==read(EV/'release_decision.json')['final_strategy']
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'production',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':task['targets'],'source_hashes':task['source_hashes'],
        'checked_components':['Exact actual submitted production artifacts, alltransitive C targets/shards and allrequired processing/helper derivation sources',
            'Actualraw11386records1173410points; exactfullscope, everypoint unique terminal fate, bothR0/final stage/indices/values andrawbreak/Pbudget checks',
            '22772actualtraces completely checked with externalraw oracle; frozen random and eachpresentcategory representatives independently Decimal/PROJ reprocessed',
            'Complete paired/aggregate/table/stratified/statistical derivations and committed code accounting;0recordmodelcalls/noerrors/nofallbacks',
            'Everypoint PROJ andrawneighborGeod check; actualstage counts full; independent S/D/P sensitivity onrandom/category plus allreported difference/extreme records',
            'Worstaddedcoverage case from allnew original identities independently reconstructed, including truefilter/Dremoval/Pinput causes',
            'Everyadded original identity independently attributed to actualR0 filter reasons, with length/count/intersection separated and eachfinalaction counted',
            'Samepredeclared finalS0; completeproduction descriptive only; no finaltestreuse asnewindependenttest or paramchange'],
        'unchecked_components':['Independent Decimal processing ofeveryrecord: only explicit random/category sample is claimed',
            'Independent alternate-model sensitivity ofeveryrecord: complete B verifiedexecution plus explicit independent sample is distinguished',
            'Source datum/noise truth/global population superiority','Notebooks/reports/package/publication andexternalGPTreview'],
        'processing_code_sha':m['code_sha'],'actual_records':n,'actual_points':points,
        'final_strategy':final,'record_model_calls':0,'failed_records':0,'record_fallbacks':0,
        'point_fates':r['point_fate_totals'],'full_descriptive_comparison':pair,
        'independent_category_math_records':category['unique_math_records'],
        'independent_sensitivity_records':len(coord['independent_sensitivity_record_ids']),
        'research_identity':'DESCRIPTIVE_FULL_PRODUCTION; independent confirmation conclusion remains separately frozen',
        'does_not_close_goal_or_external_review':True,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_production_closure.py','checker_sha256':sha(Path(__file__))}
    output=EV/'independent_c/production_closure_receipt.json'
    with output.open('x') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','records':n,'points':points,'receipt_sha256':sha(output)}))


if __name__=='__main__':main()
