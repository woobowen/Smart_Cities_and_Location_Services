"""Read-only preparation of the final protocol review; never closes a task.

No numerical experiment is run. Current targets, historical repair consumption,
actual JUnit entries and run-resource counters are checked separately. Final
Notebook/report/package and publication acceptance remain explicitly pending.
"""
from collections import Counter
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'
OUT=EV/'independent_c'


def read(p):return json.loads(p.read_text())
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def objsha(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()


TEST_TOPICS={
    'raw_identity_values_full_scope_and_terminal_ledger':[
        'test_actual_clean_and_final_values_bound_to_external_parent',
        'test_removing_all_records_and_ledger_cannot_shrink_trusted_task',
        'test_missing_duplicate_and_foreign_record_rejected',
        'test_actual_terminal_ledger_checked_completely',
        'test_complete_scope_and_batch_summary_tampering_rejected'],
    'trusted_parent_parameters_geometric_reference_and_valid_empty':[
        'test_missing_trusted_arguments_fail_closed',
        'test_summaries_parameters_units_order_and_parent_versions_rejected',
        'test_float_allowance_cannot_silently_loosen_a_registered_parameter',
        'test_legitimate_empty_and_all_filtered_keep_quality_limit',
        'test_legal_four_point_control_and_detached_trust_handle'],
    'actual_review_target_scope_versions_and_source_invalidation':[
        'test_single_receipt_defect_rejected',
        'test_reviewed_artifact_mutation_invalidates_descendants',
        'test_reviewed_receipt_mutation_invalidates_parent',
        'test_changed_shard_cannot_reuse_old_manifest_receipt',
        'test_receipt_from_different_source_epoch_rejected',
        'test_processing_epoch_must_match_current_sources'],
    'final_partition_isolation_and_frozen_strategy_gate':[
        'test_development_gate_rejects_final_identity',
        'test_final_gate_requires_real_freeze',
        'test_final_gate_rejects_strategy_added_after_freeze'],
    'mode_permissions_episode_reset_memory_write_and_illegal_proposal':[
        'test_search_only_never_instantiates_a_model_or_reads_memory',
        'test_search_feedback_is_sequential_own_record_only_and_ephemeral',
        'test_memory_disk_write_detected_and_write_api_denied',
        'test_memory_ineligible_cases_are_not_delivered',
        'test_llm_only_preserves_illegal_original_without_clamping_or_revision'],
    'quality_claim_counterexamples_and_point_identity_comparison':[
        'test_changed_upstream_cannot_claim_dp_error_as_common_quality_gain',
        'test_empty_output_cannot_win_by_zero_error_or_compression',
        'test_equal_coverage_count_with_changed_point_identities_is_not_protected',
        'test_all_counterexample_families_have_actual_known_answer_results'],
    'repair_actual_consumption_parent_resume_and_recovery':[
        'test_actual_repair_consumption_independent_rejection_then_parent_resume',
        'test_genuine_issue_closure_resumes_parent_without_verifying_it',
        'test_one_issue_close_does_not_resume_parent_with_another_open_issue',
        'test_uncertain_operations_never_replayed_on_resume',
        'test_old_epoch_parent_rejected_then_new_run_resumes'],
    'full_shards_portable_scope_and_zip_engineering':[
        'test_full_scope_shard_and_summary_agree_on_synthetic_data',
        'test_parent_cache_rejects_extra_record_even_if_manifest_scope_claim_unchanged',
        'test_frozen_portable_full_processing_without_git',
        'test_changed_frozen_source_bytes_rejected',
        'test_real_zip_hash_tamper_and_overwrite_checks',
        'test_symlink_member_rejected'],
}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-name',default='final_acceptance_preparation.json')
    args=parser.parse_args()
    assert Path(args.output_name).name==args.output_name and args.output_name.endswith('.json')
    state_path=EV/'goal_state.json';state=read(state_path)
    observed_state_hash=objsha(state)
    previous='ROOT'
    for event in state['events']:
        assert event['previous_hash']==previous
        payload={k:v for k,v in event.items() if k!='hash'}
        assert objsha(payload)==event['hash']
        previous=event['hash']
    registered_c={r['context'] for r in state['role_dispatches'] if r['role']=='C'}
    current_checks={};hash_cache={}
    def check_target(t):
        p=(ROOT/t['path']).resolve()
        assert p.is_relative_to(ROOT) and p.is_file() and not p.is_symlink()
        if t['path'] not in hash_cache:hash_cache[t['path']]=sha(p)
        assert hash_cache[t['path']]==t['sha256'],t['path']
    for name,row in state['tasks'].items():
        if row['status'] not in {'VERIFIED','BLOCKED_EXTERNAL'}:continue
        assert row['verifier'] in registered_c and row['verifier']!=row['author']
        for t in row['targets']+[row['receipt']]:check_target(t)
        for path,h in row['source_hashes'].items():check_target({'path':path,'sha256':h})
        receipt=read(ROOT/row['receipt']['path']);part=receipt.get('tasks',{}).get(name,receipt)
        assert receipt['role_context']==row['verifier'] and part['status']==row['status']
        assert part['source_hashes']==row['source_hashes'] and part['checked_components']
        assert set(map(objsha,row['targets']))<=set(map(objsha,part['targets']))
        current_checks[name]={'status':row['status'],'targets':len(row['targets']),
            'sources':len(row['source_hashes']),'receipt':row['receipt']}
    repairs={}
    for name,issue in state['issues'].items():
        events=[(i,e['kind']) for i,e in enumerate(state['events']) if e.get('issue_id')==name]
        assert any(k=='ISSUE_OPENED_PARENT_PAUSED' for _,k in events)
        if issue['status']=='VERIFIED':
            check_target(issue['receipt']);receipt=read(ROOT/issue['receipt']['path'])
            assert receipt['role_context']==issue['verifier'] in registered_c
            assert issue['repairer']!=issue['verifier'] and receipt['status']=='VERIFIED'
            assert receipt['issue_id']==name and receipt['checked_components']
            assert set(map(objsha,issue['repair_targets']))<=set(map(objsha,receipt['targets']))
            kinds=[k for _,k in events]
            assert 'ACTUAL_B_REPAIR_SUBMITTED' in kinds
            assert any(k.startswith('INDEPENDENT_REPAIR_CLOSED_') for k in kinds)
            assert kinds.index('ACTUAL_B_REPAIR_SUBMITTED')>kinds.index('ISSUE_OPENED_PARENT_PAUSED')
        repairs[name]={'status':issue['status'],'attempts':issue['attempts'],
            'repairer':issue['repairer'],'verifier':issue.get('verifier'),
            'actual_event_kinds':[k for _,k in events],
            'historical_patch_note':'Older repaired file hashes may be superseded by separately reviewed later epochs; not claimed as current bytes.'}
    test_receipt_path=EV/'full_working_tests_final_receipt.json'
    if not test_receipt_path.exists():test_receipt_path=EV/'full_working_tests_receipt.json'
    old_test=read(test_receipt_path)
    xp=EV/('full_working_tests_final.xml' if 'final' in test_receipt_path.name else 'full_working_tests.xml')
    assert sha(xp)==old_test['junit_sha256']
    xml=ET.parse(xp);cases=xml.findall('.//testcase')
    suite_total=sum(int(s.get('tests')) for s in xml.findall('.//testsuite'))
    assert len(cases)==old_test['test_cases'] and len(cases)>=465
    assert suite_total==old_test['junit_counts']['tests']==len(cases)+old_test['passed_subtests']
    assert not any(list(c) for c in cases)
    names=[c.get('name') for c in cases]
    test_topics={}
    for topic,prefixes in TEST_TOPICS.items():
        matches={prefix:[n for n in names if n==prefix or n.startswith(prefix+'[')] for prefix in prefixes}
        assert all(matches.values()),topic
        test_topics[topic]={'tested_function_patterns':prefixes,
            'matching_passing_JUnit_entries':sum(len(v) for v in matches.values())}
    subjects={**old_test['processing_source_hashes'],**old_test['auxiliary_source_hashes']}
    stale={name:{'tested_hash':h,'current_hash':sha(ROOT/name)} for name,h in subjects.items() if sha(ROOT/name)!=h}
    assert not (set(stale)&set(old_test['processing_source_hashes']))
    new_tests=OUT/'final_information_boundaries.xml';new_xml=ET.parse(new_tests)
    new_cases=new_xml.findall('.//testcase')
    assert len(new_cases)==4 and not any(list(c) for c in new_cases)
    current_runs=['g3-development-parents-03','g3-development-routing-03','g3-development-interactions-01',
                  'g3-selection-01','g3-final-confirm-01','g3-full-production-01']
    retired_runs={'g3-development-parents-01','g3-development-routing-01','g3-development-parents-02'}
    run_counters=[];totals=Counter();retired=Counter()
    fields=['processing_evaluations','review_record_calls','cached_trace_rechecks',
            'reused_identical_configuration_observations','new_record_model_calls']
    source_frozen=read(EV/'production_freeze.json')['processing_source_hashes']
    for path in sorted((EV/'runs').glob('*/manifest.json')):
        m=read(path);rid=m['run_id']
        assert rid in current_runs or rid in retired_runs
        assert m['status']=='MACHINE_VERIFIED_PENDING_C'
        values={f:m[f] for f in fields}
        assert values['new_record_model_calls']==0
        if rid in current_runs:
            assert m['source_hashes']==source_frozen
            totals.update(values)
        else:retired.update(values)
        run_counters.append({'run_id':rid,'classification':'CURRENT_VALID_RESEARCH_OR_PRODUCTION' if rid in current_runs else 'HISTORICAL_SUPERSEDED_ENGINEERING_EPOCH',
            **values,'elapsed_seconds':m['elapsed_seconds'],'manifest_sha256':sha(path)})
    assert len(run_counters)==len(current_runs)+len(retired_runs)
    routing_failure=read(EV/'runs/g3-development-routing-02/failure.json')
    requirements=read(EV/'requirements.json')
    assert [r['id'] for r in requirements['requirements']]==[f'G3-A{i:02}' for i in range(1,21)]
    assert all(r['status'] in {'PASS','FAIL','BLOCKED','NOT_RUN'} for r in requirements['requirements'])
    assert {r['id'] for r in requirements['external_dependencies']}=={'META_DEPENDENCY','EVIDENCE_MASTER_DEPENDENCY'}
    assert requirements['GPT_SECOND_REVIEW']=='PENDING' and requirements['Submission']=='NOT_READY'
    gov=read(EV/'governance_tool_events.json');export=read(EV/'governance_export_receipt.json')
    assert sha(EV/'governance_tool_events.json')==export['export_sha256']
    assert gov['counts']==export['counts'] and len(gov['events'])==export['events']
    assert all(e['tool'] in {'spawn_agent','followup_task','send_message','interrupt_agent'} for e in gov['events'])
    out={'role_context':'/root/c_protocol','status':'PREPARATION_ONLY_NOT_ACCEPTANCE',
        'at':datetime.now(timezone.utc).isoformat(),'observed_journal_snapshot_sha256':observed_state_hash,
        'observed_last_event_hash':previous,'journal_hash_chain_events_checked':len(state['events']),
        'current_completed_task_bindings_checked':current_checks,'repair_history_checked':repairs,
        'working_tests':{'receipt_path':str(test_receipt_path.relative_to(ROOT)),
            'receipt_sha256':sha(test_receipt_path),'junit_sha256':sha(xp),
            'passing_JUnit_testcase_nodes':len(cases),'reported_suite_total_including_subtests':suite_total,
            'recorded_pytest_case_count':old_test['test_cases'],'recorded_subtests':old_test['passed_subtests'],
            'topic_coverage':test_topics,'current_source_changes_since_test':stale,
            'test_counts_are_not_method_experiment_counts':True},
        'additional_explicit_information_boundary_challenges':{'passing_cases':4,
            'test_source':{'path':str((OUT/'test_final_information_boundaries.py').relative_to(ROOT)),
                           'sha256':sha(OUT/'test_final_information_boundaries.py')},
            'junit_sha256':sha(new_tests),'scope':'synthetic only, no true selection/final examples or model calls'},
        'run_counters':run_counters,'current_run_totals':dict(totals),'retired_epoch_totals':dict(retired),
        'early_routing_failure_preserved':routing_failure,
        'cost_unavailable':'governance backend requests and billing unknown; C checks/Notebook computations/smokes are separate from above method-run counters',
        'governance_export_checked_through':gov['cutoff'],
        'requirements_observed':{r['id']:r['status'] for r in requirements['requirements']},
        'remaining_engineering_gates':['Actual two successful current-source fresh-kernel FULL Notebooks',
            'Final reports and required figures independent C with all-page200dpi inspection',
            'Both final handoffs and teacher task correspondence',
            'Actual REVIEW_ONLY ZIP with required inputs and two isolated extracted FULL Notebook executions',
            'Current changed auxiliary sources regression, final required status/resource/governance refresh',
            'Final actual artifact/secret/large-file/link/original-preservation review',
            'Independent internal_acceptance on exact new submitted targets, followed by push and remote reread'],
        'external_only_publication_policy':{'allowed_dependencies':['META_DEPENDENCY','EVIDENCE_MASTER_DEPENDENCY'],
            'all_autonomous_engineering_must_be_complete':True,
            'allowed_report_package_tasks':['experiment_report','process_report','package'],
            'notebooks_or_processing_failure_is_external':False,
            'goal_status':'PARTIAL_BLOCKED','technical_status':'VERIFIED only for independently closed scope',
            'package_status':'REVIEW_ONLY / NOT_READY','GPT_SECOND_REVIEW':'PENDING',
            'Submission':'NOT_READY; never SUBMITTED','Understanding':'USER_DETERMINED',
            'publication':'Explicitly labelled review checkpoint only after internal artifact acceptance'},
        'must_not_accept':['Prepared checker as completed review','Old C receipt for new target hash',
            'Engineering or Notebook failure relabelled external dependency','Missing required experiment or report relabelled N/A',
            'Current full production called an independent final test','Internal C presented as external GPT second review'],
        'does_not_close_any_task':True,'new_model_calls':0,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/prepare_final_acceptance.py --output-name '+args.output_name}
    p=OUT/args.output_name
    with p.open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':out['status'],'journal_events':len(state['events']),
        'current_tasks':list(current_checks),'current_run_processing_evaluations':totals['processing_evaluations'],
        'stale_test_auxiliary_sources':list(stale),'sha256':sha(p)}))


if __name__=='__main__':main()
