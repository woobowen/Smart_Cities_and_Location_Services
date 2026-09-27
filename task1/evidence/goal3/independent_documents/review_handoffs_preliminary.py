"""Read-only check of completed Handoff facts before full delivery is frozen."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = ROOT/'task1/evidence/goal3'
TARGETS = ['task1/docs/goal3/TECHNICAL_HANDOFF.md',
           'task1/docs/goal3/INTERACTION_HANDOFF.md',
           'task1/evidence/goal3/interaction_candidates.json',
           'task1/evidence/goal3/append_postfreeze_interaction_facts.py']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    targets = [{'path':p,'sha256':sha(ROOT/p)} for p in TARGETS]
    checks, sources, issues = [], {}, []

    def check(name, actual, expected=True):
        good = actual == expected
        checks.append({'check':name,'passed':good,'actual':actual,'expected':expected})
        if not good:
            issues.append({'check':name,'actual':actual,'expected':expected})

    def load(relative):
        path = ROOT/relative
        sources[relative] = sha(path)
        return json.loads(path.read_text())

    def rows(run, name):
        path = EV/'runs'/run/'analysis'/name
        sources[str(path.relative_to(ROOT))] = sha(path)
        with path.open() as stream:
            return list(csv.DictReader(stream))

    data = load('task1/evidence/goal3/interaction_candidates.json')
    technical = (ROOT/TARGETS[0]).read_text()
    interaction = (ROOT/TARGETS[1]).read_text()
    references, quotes = [], []

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'),str) and re.fullmatch('[0-9a-f]{64}',str(value.get('sha256',''))):
                references.append(value)
            if isinstance(value.get('verbatim'),str) and isinstance(value.get('source'),dict):
                quotes.append(value)
            for child in value.values():
                walk(child)
        elif isinstance(value,list):
            for child in value:
                walk(child)

    walk(data)
    for ref in references:
        path = ROOT/ref['path']
        check('source_hash:'+ref['path'], sha(path), ref['sha256'])
        sources[ref['path']] = sha(path)
    for i, quote in enumerate(quotes):
        text = (ROOT/quote['source']['path']).read_text()
        check('verbatim_exact_source:'+str(i), quote['verbatim'] in text)
        match = re.fullmatch(r'lines (\d+)-(\d+)',quote['source'].get('locator',''))
        if match:
            check('verbatim_exact_lines:'+str(i),
                  '\n'.join(text.splitlines()[int(match[1])-1:int(match[2])]),quote['verbatim'])
    candidates = data['candidates']; by_id = {c['candidate_id']:c for c in candidates}
    check('18_unique_candidates', len(by_id),18)
    check('root_postfreeze_entries_are_last_three', [c['candidate_id'] for c in candidates[-3:]],
          ['IH-G3-C08','IH-G3-SELECTION','IH-G3-FINAL-CONFIRM'])
    for candidate in candidates:
        cid = candidate['candidate_id']
        for field in ('Tier','screenshot_spec','annotation_spec','report_order'):
            check(cid+':no_assigned_'+field,candidate[field],None)
        check(cid+':no_Evidence_LOCK',candidate['Evidence_Lock'],'NOT_ASSIGNED_BY_THIS_HANDOFF')
        check(cid+':no_formal_admission',candidate['formal_evidence_selection'],'NOT_ASSIGNED_BY_THIS_HANDOFF')
        check(cid+':markdown_entry_exists',('## '+cid+' · ') in interaction)
        if candidate['Human_Judgment']['status'] == 'NOT_AVAILABLE':
            check(cid+':no_human_verbatim_filled',candidate['Human_Judgment']['verbatim'],None)
            check(cid+':no_human_meaning_filled',candidate['Human_Judgment']['meaning'],None)
        if cid in ('IH-G3-C08','IH-G3-SELECTION','IH-G3-FINAL-CONFIRM'):
            check(cid+':root_authorship',candidate['Available_message_range']['root_context'],'/root')
            check(cid+':no_per_decision_user_quote',candidate['User_verbatim_and_source']['status'],'NOT_AVAILABLE')
            check(cid+':system_decision_only',candidate['Actual_decision']['type'],
                  'SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES')
    check('A_original_scope_and_root_append_are_distinguished',
          'Original A-authored' in data['scope'] and 'root-authored' in data['scope']
          and data['append_author_role'].startswith('root/controller'))
    check('native_event_metadata_is_not_verbatim_dialogue',
          'not recovered verbatim' in data['native_message_limits'])
    check('original_A_candidates_do_not_link_final_results',
          all('g3-final-confirm' not in json.dumps(c['Referenced_materials_and_experiments'])
              and 'release_decision' not in json.dumps(c['Referenced_materials_and_experiments'])
              for c in candidates[:15]))

    calibration = by_id['IH-G2-CALIBRATION']['GPT_or_Agent_proposal']
    for name,ref in zip(('round1','round2'),calibration['source_refs']):
        response = load(ref['path'])
        record = next(r for r in response['records'] if r['record_id']=='10232')
        actual = next(p for p in record['proposals'] if p['candidate_id']==calibration[name]['candidate_id'])
        check('historical_model_proposal_exact:'+name,actual,calibration[name])
    tradeoff = by_id['IH-G2-TRADEOFF']['GPT_or_Agent_proposal']
    response = load(tradeoff['source_ref']['path'])
    record = next(r for r in response['records'] if r['record_id']=='7764')
    actual = next(p for p in record['proposals'] if p['candidate_id']==tradeoff['proposal']['candidate_id'])
    check('historical_model_tradeoff_proposal_exact',actual,tradeoff['proposal'])
    critique = load('task1/evidence/goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json')
    cited = next(c for c in critique['actual_ai_citations'] if c['candidate_id']=='7764-r2-a')
    claim = by_id['IH-G2-TRADEOFF']['Actual_decision']
    check('historical_tradeoff_registered_readings',claim['registered_readings'],
          cited['registered_comparison']['registered_protection_readings'])
    check('historical_tradeoff_own_DP',claim['own_dp_max'],cited['candidate_metrics']['dp_max_error'])
    check('historical_tradeoff_not_selected',cited['proposal_became_locked_output'],False)
    for name,expected in (('G3-C06',450),('G3-C07',452)):
        closure = load('task1/evidence/goal3/independent_c/'+name+'_closure.json')
        check(name+':actual_regression_test_count',closure['actual_test_result']['tests'],expected)
        check(name+':independent_status',closure['status'],'VERIFIED')
    def g2_table(name):
        path = ROOT/'task1/evidence/goal2/tables'/name
        sources[str(path.relative_to(ROOT))] = sha(path)
        with path.open() as stream:
            return list(csv.DictReader(stream))
    memory = g2_table('memory_consumption.csv')
    check('memory_observed_round_denominator',len(memory),241)
    check('memory_record_episode_denominator',len({(r['episode_id'],r['record_id']) for r in memory}),96)
    check('memory_delivered_to_each_observation',all(int(r['delivered_count'])>0 for r in memory))
    check('memory_cited_rounds',sum(int(r['valid_citation_count'])>0 for r in memory),60)
    check('memory_action_consistent_rounds',sum(int(r['action_consistent_count'])>0 for r in memory),49)
    check('historical_valid_G2_model_calls',len(g2_table('model_calls.csv')),84)

    split = load('task1/evidence/goal3/split_manifest.json')
    counts = {key:len(value) for key,value in split['partitions'].items()}
    check('actual_partition_counts',counts,{'PILOT_REGRESSION':7,'DEMO_MEMORY':60,'G3_DEVELOPMENT':240,
          'G3_SELECTION':240,'FINAL_CONFIRM':600,'PRODUCTION_REMAINDER':10239})
    check('all_partition_records',sum(counts.values()),11386)
    check('no_duplicate_complete_record_groups',split['duplicate_groups'],[])
    check('split_hash_in_technical',sha(EV/'split_manifest.json') in technical)
    check('raw_point_count',split['raw_points'],1173410)
    check('conditional_model_in_technical',all(str(x) in technical for x in
          (6378137,298.257223563,121.343555,31.3561015)))
    convergence = load('task1/evidence/goal3/CONVERGENCE_REVIEW.json')
    check('new_single_count',convergence['new_candidate_definitions']['single'],1)
    check('new_combination_count',convergence['new_candidate_definitions']['combination'],3)
    check('A_convergence_did_not_consume_final',convergence['FINAL_CONFIRM_results_read'],False)
    check('A_convergence_did_not_consume_selection',convergence['selection_results_read'],False)
    check('selection_shortlist',convergence['shortlist_order'],['R0','S0','G0','S0_G0'])

    def paired(run,cid,rid,p_only=False):
        source = rows(run,'P_record_pairs.csv' if p_only else 'record_pairs.csv')
        selected = [r for r in source if r['candidate_id']==cid and r['reference_id']==rid]
        return {'records':len(selected),'protected':sum(r['feasible']=='True' for r in selected),
                'strict':sum(r['strict_gain']=='True' for r in selected),
                'coverage_delta':sum(int(r['coverage_delta']) for r in selected),
                'stored_delta':sum(int(r['n_final_delta']) for r in selected),
                'failure_ids':sorted(r['record_id'] for r in selected if r['feasible']!='True'),
                'budget_failures':sum('COMMON_DP_BUDGET_EXCEEDED' in r['protection_failures'] for r in selected),
                'new_max':max((float(r['newly_covered_max_error']) for r in selected if r['newly_covered_max_error']),default=None)}

    dev = 'g3-development-interactions-01'
    for cid,rid,expectations,p_only in (
        ('S0','R0',{'records':240,'protected':240,'strict':107,'coverage_delta':6704},False),
        ('G0','R0',{'records':240,'protected':240,'strict':41,'coverage_delta':0},False),
        ('G0','S0',{'coverage_delta':-6704,'protected':133},False),
        ('S0_G0','S0',{'records':240,'protected':240,'strict':41,'coverage_delta':0},False),
        ('S0_G0','R0',{'strict':142,'coverage_delta':6704,'new_max':6.685988483195381},False),
        ('S0','S0_G0',{'protected':199,'coverage_delta':0},False),
        ('G0','S0_G0',{'protected':133,'coverage_delta':-6704},False),
        ('P2','R0',{'stored_delta':1946,'strict':0},True),
        ('S0_P2','S0',{'stored_delta':2010,'strict':0},True),
        ('S0_P2','S0',{'protected':231},False),
        ('S0_P2','S0_G0',{'protected':197},False),
        ('P10','R0',{'budget_failures':173},True),
        ('S0_P10','S0',{'budget_failures':178},True),
    ):
        actual = paired(dev,cid,rid,p_only)
        for field,value in expectations.items():
            check(('P-only:' if p_only else 'chain:')+cid+'|'+rid+':'+field,actual[field],value)

    selection = paired('g3-selection-01','S0','R0')
    for field,value in {'records':240,'protected':240,'strict':103,'coverage_delta':6625}.items():
        check('selection_S0:'+field,selection[field],value)
    for cid,rid in (('G0','R0'),('S0_G0','R0'),('S0_G0','S0')):
        check('selection_failures:'+cid+'|'+rid,paired('g3-selection-01',cid,rid)['failure_ids'],
              ['3017','9311','9534'])
    decision = load('task1/evidence/goal3/selection_decision.json')
    check('selected_incumbent',decision['incumbent'],'S0')
    check('no_final_feedback_used_for_selection',decision['final_feedback_used'],False)
    freeze = load('task1/evidence/goal3/final_freeze.json')
    check('frozen_at_in_technical',freeze['frozen_at'] in technical)
    check('freeze_hash_in_technical',sha(EV/'final_freeze.json') in technical)
    check('code_sha_in_technical',freeze['processing_code_sha'] in technical)
    check('only_R0_S0_frozen',freeze['strategy_ids'],['R0','S0'])
    check('primary_and_predeclared_fallback',[freeze['primary_strategy'],freeze['fallback_strategy']],['S0','R0'])
    check('no_final_results_before_freeze',freeze['final_results_read_before_freeze'],False)
    check('A_receives_no_final_effects',freeze['A_research_context_receives_final_effects'],False)
    check('A_current_decision_before_final_freeze',convergence['at_utc'] < freeze['frozen_at'])
    final_pairs = paired('g3-final-confirm-01','S0','R0')
    for field,value in {'records':600,'protected':600,'strict':349,'coverage_delta':26352,
                        'stored_delta':1123,'new_max':6.087101997252068}.items():
        check('final_pair:'+field,final_pairs[field],value)
    final_rows = rows('g3-final-confirm-01','record_metrics.csv')
    for cid,expectations in {'R0':{'n_input':62284,'common_covered_points':35868,'n_final':10991,'no_output':255},
                             'S0':{'n_input':62284,'common_covered_points':62220,'n_final':12114,'no_output':0}}.items():
        group = [r for r in final_rows if r['strategy']==cid]
        check('final_'+cid+':records',len(group),600)
        for field,value in expectations.items():
            actual = sum(r[field]=='True' for r in group) if field=='no_output' else sum(int(r[field]) for r in group)
            check('final_'+cid+':'+field,actual,value)
        for field,value in {'dp_max_error':4.9971311138733405,'common_max_error':280.69670439064976}.items():
            check('final_'+cid+':'+field,max(float(r[field]) for r in group if r[field]),value)
    audit = load('task1/evidence/goal3/independent_c/g3-final-confirm-01_receipt.json')
    check('final_trace_audit_count',audit['counts']['distinct_config_trace_reviews'],1200)
    check('final_independent_math_trace_count',audit['counts']['Decimal_PROJ_trace_reviews'],80)
    check('final_independent_math_record_count',len(audit['Decimal_PROJ_record_ids']),40)
    check('final_full_pair_rows',len(rows('g3-final-confirm-01','record_pairs.csv')),2400)
    release = load('task1/evidence/goal3/release_decision.json')
    check('final_release',release['final_strategy'],'S0')
    check('no_fallback_triggered',release['predeclared_fallback_used'],False)
    check('no_final_retuning',release['retuning_or_new_winner_selection_on_final'],False)
    c08_failure = load('task1/evidence/goal3/independent_c/G3-C08_failure.json')
    check('C08_real_synthetic_failure_counts',[c08_failure['actual_result']['passed'],c08_failure['actual_result']['failed']],[1,4])
    c08 = load('task1/evidence/goal3/independent_c/G3-C08_closure.json')
    check('C08_actual_development_shards',sum(x['shards'] for x in c08['actual_development_gate_checks']),18)
    check('C08_closed_before_selection_freeze',c08['checked_at_utc'] < load('task1/evidence/goal3/selection_freeze.json')['frozen_at'])

    for phrase in ('source_crs=UNVERIFIED','几何保护不是噪声识别准确率','共同覆盖不是最终存储点数',
                   '不代替 Tier','等待完整产物和独立核验','当前待最终全量、Notebook、报告和包验收',
                   'REVIEW_ONLY / NOT_READY','GPT_SECOND_REVIEW=PENDING','Understanding 由用户决定'):
        check('technical_scope_phrase:'+phrase,phrase in technical)
    expected_future = {'task1/evidence/goal3/REVIEW_PACKET.md',
                       'task1/figures/goal3','task1/evidence/goal3/PUBLICATION_RECORD.json'}
    pending_links = []
    for relative in TARGETS[:2]:
        path = ROOT/relative
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            dest = (path.parent/target.split('#',1)[0]).resolve()
            if not dest.exists():
                rel = str(dest.relative_to(ROOT)); pending_links.append({'document':relative,'target':rel})
                check('missing_link_is_pending_final_artifact:'+rel,rel in expected_future)
    check('targets_unchanged',all(sha(ROOT/t['path'])==t['sha256'] for t in targets))
    receipt = {'role_context':'/root/c_documents','target_id':'handoff_completed_facts_preliminary',
        'status':'VERIFIED_WITHIN_CHECKED_SCOPE' if not issues else 'REPAIR_REQUIRED',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':targets,
        'checked_components':[
            'Technical Handoff §§1–6 historical/development/selection/final facts against actual source tables and frozen artifacts',
            '18 structured interaction candidates, 105 source-reference occurrences/61 unique referenced paths and 11 exact quoted source spans',
            'historical user authorization vs actual model proposal vs system decision versus unavailable human judgment identities',
            'three cited G2 model proposals exactly match original responses; real tradeoff readings and memory/call denominators match source artifacts',
            '15 original A historical/development entries separated from 3 root postfreeze entries; original A artifacts predate final freeze',
            'full development P/combination/removal negative results and exact paired outcomes retained',
            '600-record confirmation metrics independently reduced from source CSV, actual C scope and fixed release identity',
            'no Evidence admission, Tier, screenshot/annotation/order or LOCK decisions in the index',
            'pending full production/reproduction/publication references remain explicit',
        ],
        'unchecked_components':[
            'final full-production terminal counts, enlarged coordinate/category audit and completed Technical §§7–9',
            'actual full Notebook executions, final reports, real package and remote publication',
            'Evidence Master admission/presentation specification/LOCK and user Understanding',
            'unavailable original web message IDs/screenshots or encrypted native message plaintext',
            'absence of all undocumented private context exposure; audit establishes recorded artifacts/timing and declared role boundaries only',
        ],
        'source_bindings':sources,'reference_occurrences':len(references),
        'quoted_source_span_occurrences':len(quotes),'checks':checks,'check_count':len(checks),
        'issues':issues,'pending_links':pending_links,'new_processing_or_model_calls':0,
        'not_final_handoff_acceptance':True,'Evidence_Lock':'NOT_ASSIGNED_BY_THIS_REVIEW',
        'review_harness_correction':'Historical tradeoff comparison uses the nested registered_protection_readings object; the initial broader object comparison was a checker mismatch, not a Handoff defect.',
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_documents/review_handoffs_preliminary.py'}
    (HERE/'handoff_preliminary_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','check_count','reference_occurrences',
                    'quoted_source_span_occurrences','issues','pending_links')},ensure_ascii=False))


if __name__ == '__main__':
    main()
