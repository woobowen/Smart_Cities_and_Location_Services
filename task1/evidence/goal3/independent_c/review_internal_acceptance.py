"""Strict read-only aggregate review of stable pre-publication Goal3 artifacts.

prepare: records actual checks and missing prerequisites; never accepts a task.
accept: requires a real current Journal submission and every prerequisite closed.
Publication/remote facts are later checked separately, avoiding future-SHA cycles.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
EV = ROOT/'task1/evidence/goal3'
RAW_SHA = 'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'
CONTRACT_SHA = 'fcf5b3962c4c5a2a59f42ae1f167fa180bfc2b9798fca85e256bcc8ccb3c558d'
SPLIT_SHA = 'c20747b7e2869b5e3ce755601764336dcd5e42ed4643e99d5e56be7a0ebba2f0'
PROCESSING_CODE = 'e12f8a27944210adb452730be92a0674dfc6b84b'
NOTEBOOK_CODE = '0b20be8e4142e8e62246e9357993e83951833e4f'
EXTERNAL = {'META_DEPENDENCY', 'EVIDENCE_MASTER_DEPENDENCY'}
EXTERNAL_TASKS = {'experiment_report', 'process_report', 'package'}
MUTABLE_CLOSEOUT = {
    'task1/evidence/goal3/goal_state.json', 'task1/evidence/goal3/requirements.json',
    'task1/evidence/goal3/FINAL_RESPONSE.md', 'task1/evidence/goal3/PUBLICATION_RECORD.json',
    'task1/evidence/goal3/REVIEW_PACKET.md', 'task1/evidence/goal3/runtime_checkpoint.json',
    'task1/evidence/goal3/resource_plan.json', 'task1/evidence/goal3/governance_tool_events.json',
    'task1/evidence/goal3/governance_export_receipt.json'}
PREREQUISITES = ('handoff', 'contract_split', 'implementation', 'development', 'selection_freeze',
    'selection', 'final_freeze', 'confirmation', 'production', 'figures', 'notebooks',
    'experiment_report', 'process_report', 'handoffs', 'package')
RUNS = ('g3-development-parents-03', 'g3-development-routing-03', 'g3-development-interactions-01',
        'g3-selection-01', 'g3-final-confirm-01', 'g3-full-production-01')
NOTEBOOK_RECEIPTS = ('repository_basic_full_02_receipt.json', 'repository_system_full_02_current_receipt.json',
                    'isolated_package_basic_full_receipt.json', 'isolated_package_system_full_receipt.json')


def read(path):
    return json.loads(Path(path).read_text())


def objsha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        allow_nan=False, separators=(',', ':')).encode()).hexdigest()


class Review:
    def __init__(self):
        self.cache = {}; self.targets = {}; self.sources = {}; self.blockers = []

    def digest(self, path):
        path = Path(path).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
        if path not in self.cache:
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''): digest.update(block)
            self.cache[path] = digest.hexdigest()
        return self.cache[path]

    def check(self, name, expected=None, *, source=False, collect=True):
        path = (ROOT/name).resolve(); actual = self.digest(path)
        if expected is not None: assert actual == expected, ('STALE_ACTUAL_FILE', name)
        relative = str(path.relative_to(ROOT))
        if collect:
            assert relative not in MUTABLE_CLOSEOUT, ('MUTABLE_CLOSEOUT_NEEDS_SNAPSHOT', relative)
            mapping = self.sources if source else self.targets
            assert mapping.get(relative, actual) == actual
            mapping[relative] = actual
        return actual

    def mapping(self, values, *, source=False):
        for name, expected in values.items(): self.check(name, expected, source=source)

    def target_rows(self, rows):
        for row in rows: self.check(row['path'], row['sha256'])

    def receipt(self, path, roles, task_name=None, expected_status='VERIFIED'):
        receipt = read(path); self.check(path)
        part = receipt.get('tasks', {}).get(task_name, receipt) if task_name else receipt
        assert receipt['role_context'] in roles and part['status'] == expected_status
        assert part.get('checked_components') and not part.get('errors')
        self.target_rows(part['targets']); self.mapping(part['source_hashes'], source=True)
        return receipt, part


def perform(args):
    review = Review(); state = read(EV/'goal_state.json')
    assert state['goal_id'] == 'SC-LAB1-G3-FINAL-001'
    assert state['GPT_SECOND_REVIEW'] == 'PENDING' and state['Submission'] == 'NOT_READY'
    assert state['Understanding'] == 'USER_DETERMINED'
    previous = 'ROOT'
    for event in state['events']:
        assert event['previous_hash'] == previous and objsha({k:v for k,v in event.items() if k!='hash'}) == event['hash']
        previous = event['hash']
    roles = {r['context'] for r in state['role_dispatches'] if r['role'] == 'C'}
    assert '/root/c_protocol' in roles and '/root/c_documents' in roles
    assert {'A','B','C'} <= {r['role'] for r in state['role_dispatches']}
    task_findings = {}; external = set()
    for name in PREREQUISITES:
        row = state['tasks'][name]
        if row['status'] not in {'VERIFIED', 'BLOCKED_EXTERNAL'}:
            review.blockers.append({'kind':'TASK_NOT_CLOSED','task':name,'actual_status':row['status']}); continue
        assert row['author'] != row['verifier'] in roles
        review.target_rows(row['targets']); review.target_rows([row['receipt']]); review.mapping(row['source_hashes'], source=True)
        whole, part = review.receipt(ROOT/row['receipt']['path'], roles, name, row['status'])
        assert whole['role_context'] == row['verifier'] and part['source_hashes'] == row['source_hashes']
        assert set(map(objsha,row['targets'])) <= set(map(objsha,part['targets']))
        if row['status'] == 'BLOCKED_EXTERNAL':
            deps = set(part['external_dependencies'])
            assert name in EXTERNAL_TASKS and deps and deps <= EXTERNAL
            assert part.get('available_engineering_status', part.get('engineering_status')) == 'VERIFIED'
            external |= deps
        for dep in row['depends_on']:
            assert state['tasks'][dep]['status'] in {'VERIFIED','BLOCKED_EXTERNAL'}, ('OPEN_CLOSED_TASK_DEPENDENCY',name,dep)
        task_findings[name] = {'status':row['status'],'targets':len(row['targets']),
            'sources':len(row['source_hashes']),'independent_context':row['verifier'],'receipt':row['receipt']}
    for name, issue in state['issues'].items():
        if issue['status'] != 'VERIFIED':
            review.blockers.append({'kind':'OPEN_ENGINEERING_ISSUE','issue':name}); continue
        review.target_rows([issue['receipt']]); receipt = read(ROOT/issue['receipt']['path'])
        assert receipt['role_context'] == issue['verifier'] in roles and issue['verifier'] != issue['repairer']
        assert receipt['issue_id'] == name and receipt['status'] == 'VERIFIED'
        assert set(map(objsha,issue['repair_targets'])) <= set(map(objsha,receipt['targets']))
        # Repair hashes are historical as-of references. Later audited epochs and
        # Notebook output promotion do not make that real repair disappear.
        events = [e['kind'] for e in state['events'] if e.get('issue_id') == name]
        assert 'ACTUAL_B_REPAIR_SUBMITTED' in events and any(e.startswith('INDEPENDENT_REPAIR_CLOSED_') for e in events)
    if state['inflight'] is not None: review.blockers.append({'kind':'JOURNAL_INFLIGHT_NOT_CLOSED'})

    raw_path = ROOT/'task1/作业/作业/traj_dict.json'; review.check(raw_path, RAW_SHA)
    raw = read(raw_path); points = sum(len(row[0]) for row in raw.values())
    assert len(raw) == 11386 and points == 1173410
    assert all(len(row)==2 and len(row[0])==len(row[1]) for row in raw.values())
    review.check('task1/config/goal3/contract.json', CONTRACT_SHA)
    review.check(EV/'split_manifest.json', SPLIT_SHA)
    split = read(EV/'split_manifest.json'); flattened = [rid for ids in split['partitions'].values() for rid in ids]
    assert len(flattened) == len(set(flattened)) == len(raw) and set(flattened) == set(raw)
    freeze = read(EV/'production_freeze.json'); review.check(EV/'production_freeze.json')
    core = freeze['processing_source_hashes']; assert len(core)==32 and freeze['processing_code_sha']==PROCESSING_CODE
    assert freeze['source_crs']=='UNVERIFIED' and freeze['final_strategy']=='S0'
    assert freeze['strategy_ids']==['R0','S0'] and freeze['input_ids']==flattened
    review.mapping(core, source=True)
    for code in (PROCESSING_CODE, NOTEBOOK_CODE):
        for name, expected in core.items():
            blob=subprocess.check_output(['git','show',code+':'+name],cwd=ROOT)
            assert hashlib.sha256(blob).hexdigest()==expected,('CODE_IDENTITY_SOURCE_DIFF',code,name)
    run_findings=[]; totals=Counter(); manifests={}
    counters=('processing_evaluations','review_record_calls','cached_trace_rechecks',
              'reused_identical_configuration_observations','new_record_model_calls')
    for run_id in RUNS:
        path=EV/'runs'/run_id/'manifest.json'; m=read(path); review.check(path); manifests[run_id]=m
        assert m['status']=='MACHINE_VERIFIED_PENDING_C' and m['input_ids']==m['completed_record_ids']
        assert m['source_hashes']==core and not m['failed_records'] and m['new_record_model_calls']==0
        totals.update({k:m[k] for k in counters})
        run_findings.append({'run_id':run_id,'records':len(m['input_ids']),'code_sha':m['code_sha'],
                            'manifest_sha256':review.digest(path),**{k:m[k] for k in counters}})
    selection=manifests['g3-selection-01']; confirm=manifests['g3-final-confirm-01']; full=manifests['g3-full-production-01']
    for name,manifest in [('selection_freeze.json',selection),('final_freeze.json',confirm),('production_freeze.json',full)]:
        path=EV/name; frozen=read(path);review.check(path)
        assert datetime.fromisoformat(frozen['frozen_at'])<datetime.fromisoformat(manifest['started_at'])
        assert frozen['input_ids']==manifest['input_ids'] and frozen['strategy_ids']==manifest['strategy_ids']
        assert frozen['processing_source_hashes']==core and frozen['source_crs']=='UNVERIFIED'
        review.mapping(frozen['bindings'])
    choice, release = read(EV/'selection_decision.json'), read(EV/'release_decision.json')
    review.check(EV/'selection_decision.json');review.check(EV/'release_decision.json')
    assert choice['incumbent']=='S0' and choice['final_feedback_used'] is False
    assert release['final_strategy']=='S0' and release['status']=='SUPPORTED_WITHIN_SCOPE'
    assert not release['predeclared_fallback_used'] and not release['retuning_or_new_winner_selection_on_final']
    assert datetime.fromisoformat(confirm['ended_at']) < datetime.fromisoformat(release['at']) < datetime.fromisoformat(freeze['frozen_at'])
    for manifest,n in [(selection,240),(confirm,600),(full,len(raw))]:
        pair=manifest['comparisons']['S0|R0']
        assert len(manifest['input_ids'])==n==pair['n_records']==pair['protected_records']
        assert pair['all_guards_pass'] and pair['replacement_supported'] and pair['strict_gain_records']>0
        assert not pair['failure_records']
    assert full['processing_evaluations']==22772 and len(full['shards'])==285
    for strategy in ['R0','S0']:
        m=full['record_metrics'][strategy]
        assert m['n_input']==points and m['n_records']==len(raw)
        assert sum(m[k] for k in ('n_filtered','n_direction_removed','n_dp_removed','n_final'))==points

    test_path=EV/'full_working_tests_final_receipt.json'; tests=read(test_path);review.check(test_path)
    xml_path=EV/'full_working_tests_final.xml';review.check(xml_path,tests['junit_sha256'])
    xml=ET.parse(xml_path);cases=xml.findall('.//testcase');suites=xml.findall('.//testsuite')
    assert len(cases)==tests['test_cases']==469 and not any(list(c) for c in cases)
    assert sum(int(s.get('tests')) for s in suites)==tests['junit_counts']['tests']==479
    assert tests['passed_subtests']==10 and all(int(s.get(k))==0 for s in suites for k in ('errors','failures','skipped'))
    review.mapping(tests['processing_source_hashes'],source=True);review.mapping(tests['auxiliary_source_hashes'],source=True)
    review.receipt(EV/'independent_c/final_working_tests_review.json', roles)

    notebook_findings=[]
    for name in NOTEBOOK_RECEIPTS:
        path=EV/'independent_c'/name
        if not path.is_file():
            review.blockers.append({'kind':'FULL_NOTEBOOK_RECEIPT_MISSING','path':str(path.relative_to(ROOT))});continue
        whole, receipt=review.receipt(path,roles)
        assert receipt['new_provider_attempts_observed']==0 and receipt['raw_sha256']==RAW_SHA
        kind='basic' if 'basic' in name else 'system'
        isolated=name.startswith('isolated_')
        assert receipt['executed_code_cells']==(12 if kind=='basic' else 8)
        assert receipt['history']['record_candidate_recomputations']==(9720 if kind=='basic' else 6001)
        if kind=='basic':
            p=receipt['production'];assert (p['raw_records'],p['raw_points'],p['record_candidate_recomputations'])==(11386,1173410,22772)
            assert p['new_shards_actual_hash_checked']==285 and p['cached_trace_rechecks']==0
            assert p['code_identity_source']==('FROZEN_SOURCE_BUNDLE' if isolated else 'ACTUAL_LOCAL_GIT_HEAD')
            assert p['code_sha']==(PROCESSING_CODE if isolated else NOTEBOOK_CODE)
            assert receipt['demonstration']['synthetic_processing_chains']==19
        else: assert receipt['history']['record_episode_selections']==384
        if isolated:
            assert receipt['isolated_package']['isolated_import_probe']['all_imported_task1_modules_from_extracted_package']
            assert receipt['isolated_package']['isolated_import_probe']['new_trajectory_processing']==0
        notebook_findings.append({'receipt':str(path.relative_to(ROOT)), 'sha256':review.digest(path),
            'kind':kind,'isolated':isolated,'record_candidate_recomputations':receipt['history']['record_candidate_recomputations']})
    archive_path=EV/'independent_c/isolated_archive_binding_receipt.json'
    if archive_path.is_file():review.receipt(archive_path,roles)
    else:review.blockers.append({'kind':'ACTUAL_ZIP_BINDING_RECEIPT_MISSING'})

    requirements=read(EV/'requirements.json')
    assert [r['id'] for r in requirements['requirements']]==[f'G3-A{i:02}' for i in range(1,21)]
    assert requirements['GPT_SECOND_REVIEW']=='PENDING' and requirements['Submission']=='NOT_READY'
    assert {r['id'] for r in requirements['external_dependencies']}==EXTERNAL
    for item in requirements['requirements']:
        assert item['status'] in {'PASS','FAIL','BLOCKED','NOT_RUN'}
        for evidence in item['evidence']:review.check(evidence['path'],evidence['sha256'],collect=False)
    startup=read(EV/'startup.json');review.check(EV/'startup.json')
    for name,digest in startup['untracked_protected'].items():review.check(name,digest,collect=False)
    for name in startup['untracked_initial']:
        found=subprocess.run(['git','ls-files','--error-unmatch','--',name],cwd=ROOT,capture_output=True)
        assert found.returncode!=0,('USER_UNTRACKED_FILE_ADDED_TO_INDEX',name)
    bundle=read(EV/'source_bundle_final_check.json');review.check(EV/'source_bundle_final_check.json')
    folder=ROOT/'releases/chatgpt-project-sources';actual=[p for p in folder.iterdir() if p.is_file() and not p.is_symlink()]
    assert len(actual)==len(bundle['files'])==11
    assert {str(p.relative_to(ROOT)) for p in actual}=={r['path'] for r in bundle['files']}
    review.target_rows(bundle['files'])
    if args.prepublication_receipt:
        _, preflight = review.receipt(args.prepublication_receipt, roles)
        assert preflight['target_id']=='publication_preflight'
        required_checks={'diff','secret_scan','large_files','original_protection','local_links'}
        assert required_checks<=set(preflight['checks'])
        assert all(preflight['checks'][key]=='VERIFIED' for key in required_checks)
        manifest_name=preflight['candidate_manifest_path']
        review.check(manifest_name,preflight['candidate_manifest_sha256'])
        candidate_manifest=read(ROOT/manifest_name)
        assert candidate_manifest['files'], 'EXACT_PROPOSED_PUBLICATION_SCOPE_REQUIRED'
        review.target_rows(candidate_manifest['files'])
    else:
        review.blockers.append({'kind':'FINAL_PREPUBLICATION_INDEPENDENT_REVIEW_MISSING',
            'scope':'actual diff/secret/large-file/original-protection/local-link scan bound to exact proposed stable files'})
    review.check(__file__,source=True)

    requirements_states={r['id']:r['status'] for r in requirements['requirements']}
    data={'role_context':'/root/c_protocol','target_id':'internal_acceptance',
        'status':'PREPARATION_ONLY_NOT_ACCEPTANCE','at':datetime.now(timezone.utc).isoformat(),
        'observed_journal_sha256':objsha(state),'observed_journal_last_event_hash':previous,
        'journal_hash_chain_events_checked':len(state['events']),'prerequisite_tasks':task_findings,
        'closed_repair_issues':[n for n,i in state['issues'].items() if i['status']=='VERIFIED'],
        'requirements_statuses_observed_not_used_as_oracle':requirements_states,
        'raw_reference':{'sha256':RAW_SHA,'records':len(raw),'points':points,'contract_sha256':CONTRACT_SHA,'split_sha256':SPLIT_SHA},
        'current_runs':run_findings,'current_run_resource_totals':dict(totals),
        'code_identities':{'final_method_and_production_CODE_SHA':PROCESSING_CODE,
            'repository_basic_FULL_actual_CODE_SHA':NOTEBOOK_CODE,'both_commits_same_processing_sources':len(core),
            'isolated_package_identity':'FROZEN_SOURCE_BUNDLE; no local Git claim'},
        'working_tests':{'actual_testcase_nodes':469,'suite_total':479,'passed_subtests':10,'junit_sha256':tests['junit_sha256']},
        'full_notebooks':notebook_findings,'external_dependencies':sorted(external),
        'open_engineering_blockers':review.blockers,
        'suggested_stable_targets':[{'path':p,'sha256':h} for p,h in sorted(review.targets.items())],
        'suggested_source_hashes':review.sources,
        'mutable_closeout_reviewed_separately_at_publication':sorted(MUTABLE_CLOSEOUT),
        'publication_policy':{'allowed_checkpoint':'PARTIAL_BLOCKED only after all autonomous engineering is independently accepted',
            'future_remote_SHA_not_required_by_prepublication_gate':True,
            'subsequent_actual_publication_record_and_remote_readback_have_separate_receipt':True,
            'GPT_SECOND_REVIEW':'PENDING','Submission':'NOT_READY; never SUBMITTED','Understanding':'USER_DETERMINED'},
        'new_method_runs':0,'new_model_calls':0,'does_not_close_any_task':True}
    if args.mode=='accept':
        assert not review.blockers,('INCOMPLETE_ENGINEERING',review.blockers)
        task=state['tasks']['internal_acceptance'];assert task['status']=='REVIEW_PENDING'
        assert args.snapshot, 'ACTUAL_IMMUTABLE_PRE_SUBMISSION_JOURNAL_SNAPSHOT_REQUIRED'
        snapshot=read(args.snapshot)
        assert snapshot['goal_id']==state['goal_id']
        for name in PREREQUISITES:assert snapshot['tasks'][name]==state['tasks'][name],('SNAPSHOT_TASK_DIFF',name)
        assert snapshot['issues']==state['issues'] and snapshot['inflight'] is None
        assert state['events'][:len(snapshot['events'])]==snapshot['events']
        review.check(args.snapshot)
        review.check(__file__,source=True)
        assert not (set(MUTABLE_CLOSEOUT)&{t['path'] for t in task['targets']}), 'DO_NOT_BIND_MUTABLE_FUTURE_CLOSEOUT'
        review.target_rows(task['targets']);review.mapping(task['source_hashes'],source=True)
        supplied={t['path']:t['sha256'] for t in task['targets']}
        assert review.targets.items()<=supplied.items(),('MISSING_STABLE_REVIEW_TARGETS',sorted(set(review.targets)-set(supplied)))
        assert review.sources.items()<=task['source_hashes'].items(), 'DEPENDENCY_SOURCE_BINDINGS_MISSING'
        assert external and external<=EXTERNAL and state['tasks']['package']['status']=='BLOCKED_EXTERNAL'
        assert all(requirements_states[f'G3-A{i:02}']=='PASS' for i in list(range(1,15))+[17])
        assert all(requirements_states[f'G3-A{i:02}']=='BLOCKED' for i in [15,16,18])
        assert requirements_states['G3-A20']=='NOT_RUN', 'PUBLICATION_MUST_BE_ACTUALLY_CHECKED_LATER'
        data.update(status='VERIFIED',targets=task['targets'],source_hashes=task['source_hashes'],
            scope='ALL_AUTONOMOUS_STABLE_ENGINEERING_ACCEPTED_FOR_PARTIAL_BLOCKED_PUBLICATION_CHECKPOINT',
            goal_status='PARTIAL_BLOCKED',technical_status='VERIFIED',research_status=release['status'],
            reports_status='BLOCKED_EXTERNAL',package_status='REVIEW_ONLY; BLOCKED_EXTERNAL',
            publication_status='PENDING_ACTUAL_PUSH_AND_REMOTE_CHECK',GPT_SECOND_REVIEW='PENDING',Submission='NOT_READY',
            checked_components=['Actual raw byte identity, record/point scope and immutable approved contract/split',
                'All prerequisite task targets/receipts/source bytes and independent role identity; no requirements PASS used as oracle',
                'Every actual issue has independent repair consumption, with historical as-of hashes separated from current artifact promotion',
                'Frozen selection/confirmation/production scopes, chronology, current full ledger totals and independent production evidence',
                'Actual469testcase+10subtests record and current tested source bindings',
                'All four actual FULL Notebook receipts, real ZIP member binding, complete production shard checks and Provider0 boundaries',
                'Independent figure/report/Handoff/package closures cover exact submitted artifacts; only named identity/EvidenceMaster external inputs remain',
                'e12processing,0b20repository recompute and no-Git frozen-source package identities remain explicit',
                'All stable prepublication targets are concrete and current; actual later publication facts have a separate gate'],
            unchecked_components=['Actual push/remote equality and fixed-SHA readback have not happened at this gate',
                'Missing official student identity, original approved interaction evidence and EvidenceMaster LOCK',
                'External GPT second review, user Understanding and teacher submission'],errors=[])
    return data


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['prepare','accept'],default='prepare')
    parser.add_argument('--snapshot',type=Path)
    parser.add_argument('--prepublication-receipt',type=Path,
                        help='Actual independent publication_preflight receipt with exact stable candidate manifest and five required checks')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=perform(args)
    result['actual_command']=' '.join(__import__('sys').argv)
    with args.output.open('x') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'status':result['status'],'current_tasks':len(result['prerequisite_tasks']),
        'known_stable_targets':len(result['suggested_stable_targets']),
        'open_engineering_blockers':result['open_engineering_blockers'],
        'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
