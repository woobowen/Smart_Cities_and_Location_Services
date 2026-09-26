"""Bind C's completed independent checks to nine internal tasks; no journal writes."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[6]
REV = ROOT/'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001'
OUT = REV/'c_acceptance'
RUN = REV/'runs/g1-complete-pilot-03'
CODE = 'f229d9a4113bcc0dd763e1b410f1f5fb73903a62'


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(path.relative_to(ROOT))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def bind(paths):
    return [{'path': rel(p), 'sha256': sha(p)} for p in sorted(set(paths))]


def main():
    manifest = read(RUN/'manifest.json')
    state = read(REV/'goal_state.json')
    assert manifest['run_id'] == state['current_run'] == read(REV/'current_run.json')['run_id'] == 'g1-complete-pilot-03'
    assert manifest['code_sha'] == state['current_code_sha'] == CODE
    assert state['inflight'] is None
    assert all(i['status'] == 'VERIFIED' for i in state['issues'].values())
    own_reports = ['g1-complete-pilot-03_independent.json', 'g1-complete-pilot-03_diagnostics.json', 'followup_review.json',
                   'summary_review.json', 'notebook_review.json', 'figure_review.json', 'entry_review.json',
                   'validation_review.json', 'workflow_trace_review.json']
    for name in own_reports:
        assert read(OUT/name)['status'] == 'VERIFIED', name
    raw = ROOT/'task1/作业/作业/traj_dict.json'
    assert sha(raw) == manifest['input_sha256']
    original = read(REV/'initial_protected_hashes.json')
    allowed = {'task1/evidence/goal1/requirements.json', 'task1/evidence/goal1/REVIEW_PACKET.md', 'task1/evidence/goal1/acceptance.json'}
    changed = [{'path': p, 'before_sha256': h, 'after_sha256': sha(ROOT/p)} for p,h in original.items() if sha(ROOT/p) != h]
    assert all(row['path'] in allowed for row in changed)
    workflow = sorted((ROOT/'task1/workflow').glob('*.py'))
    for p in workflow:
        ast.parse(p.read_text())
        committed = subprocess.check_output(['git', 'show', CODE+':'+rel(p)], cwd=ROOT)
        assert hashlib.sha256(committed).hexdigest() == sha(p), rel(p)
    recovery = read(REV/'handoff/link_recovery.json')
    with zipfile.ZipFile(ROOT/recovery['source_archive']) as z:
        assert z.read(recovery['member']) == (ROOT/recovery['target']).read_bytes()
    assert sha(ROOT/recovery['source_archive']) == recovery['source_archive_sha256']
    write(OUT/'final_bindings_review.json', {'status': 'VERIFIED', 'classification': 'INDEPENDENT_C_FINAL_BINDING_CHECK',
          'run_id': manifest['run_id'], 'code_sha': CODE, 'protected_total': len(original),
          'authorized_changed_entries': changed, 'unauthorized_changed_entries': [],
          'current_raw_sha256': sha(raw), 'all_processing_workflow_files_match_CODE': True,
          'no_inflight_operation': True, 'all_five_actual_issues_verified': True,
          'historical_link_exact_original_zip_bytes': True, 'evidence': bind([REV/'initial_protected_hashes.json',
              REV/'handoff/link_recovery.json', ROOT/recovery['target'], OUT/'review_time_goal_snapshot.json']),
          'publication_status': 'NOT_RUN', 'mutable_state_not_added_to_task_evidence': True})

    common = [raw, ROOT/'task1/config/goal1.json', ROOT/'task1/config/conditional_planar.json',
              REV/'AUTHORIZATION_SUPPLEMENT.md', REV/'USER_DECISIONS.json']
    governance = [ROOT/'AGENTS.md', ROOT/'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md',
        ROOT/'task1/docs/goal1/CONTRACTS.md', ROOT/'task1/docs/goal1/README.md', ROOT/'task1/docs/goal1/ARCHITECTURE.md',
        REV/'handoff/SC-LAB1-G1-COMPLETE-001_CODEX_PROMPT.md', REV/'a_scope/TaskPlan.json',
        REV/'a_scope/source_audit.json', REV/'a_scope/release_scope_check.json', REV/'a_scope/release_scope_check.md',
        REV/'bundle_sync.json', REV/'workspace_initial.json', REV/'initial_protected_hashes.json',
        OUT/'reviewed_requirements.json', OUT/'final_bindings_review.json',
        REV/'prepublication_check.snapshot_before_acceptance.json'] + common
    c2 = REV/'c_combined_review/round2/combined_closure.json'
    validation = [REV/'validation_pilot03.json', REV/'tests_pilot03.xml', OUT/'validation_review.json']
    trust = common + [ROOT/'task1/workflow/pipeline.py', ROOT/'task1/workflow/evaluation.py',
        ROOT/'task1/workflow/coordinates.py', ROOT/'task1/workflow/geometry.py', c2,
        OUT/'direction_roundoff_receipt.json', OUT/'g1-complete-pilot-03_independent.json', OUT/'independent_probe.py'] + validation
    controls = [ROOT/'task1/workflow/goal.py', ROOT/'task1/workflow/artifact_review.py', ROOT/'task1/workflow/tools.py',
        ROOT/'task1/workflow/controller.py', c2, OUT/'workflow_trace_review.json', OUT/'review_time_goal_snapshot.json',
        OUT/'review_time_resources_snapshot.json', OUT/'g1-complete-pilot-03_diagnostics.json'] + validation
    def actions(names):
        return [ROOT/manifest[which][name]['path'] for which in ['artifacts', 'reviews'] for name in names]
    diagnostics = actions(['profile_pilot', 'time_boundaries', 'duplicate_details']) + common + [RUN/'manifest.json',
        OUT/'g1-complete-pilot-03_diagnostics.json', OUT/'remaining_probe.py', OUT/'time_scope_receipt.json',
        ROOT/'task1/workflow/diagnostics.py', ROOT/'task1/workflow/artifact_review.py']
    baseline = actions(['baseline']) + common + [RUN/'manifest.json', RUN/'point_actions.jsonl',
        OUT/'g1-complete-pilot-03_independent.json', OUT/'independent_probe.py', OUT/'summary_review.json',
        REV/'result_summary.json', REV/'recompute_verification.json']
    feedback = actions(['baseline']) + common + [RUN/'coordinate_sensitivity.json', OUT/'followup_request_run03.json',
        OUT/'followup_review.json', OUT/'remaining_probe.py', OUT/'coordinate_issue_receipt.json',
        ROOT/'task1/workflow/coordinate_review.py', ROOT/'task1/workflow/coordinates.py',
        ROOT/'task1/workflow/evaluation.py', REV/'followup_execution.json', REV/'a_scope/local_model_contract.json']
    notebooks = [ROOT/'task1/notebooks/01_baseline_and_audit.ipynb', ROOT/'task1/notebooks/02_agent_loop_recompute.ipynb',
        ROOT/'task1/scripts/build_goal1_notebooks.py', ROOT/'task1/scripts/complete_goal1.py',
        REV/'b_run/notebook_execution.json', REV/'b_run/notebook_verification.json', OUT/'notebook_review.json',
        OUT/'final_evidence_probe.py', RUN/'manifest.json']
    fm = read(REV/'figures/figure_manifest.json')
    figures = [ROOT/e['path'] for e in fm['files']] + [REV/'figures/figure_manifest.json',
        ROOT/'task1/scripts/build_complete_figures.py', ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex',
        REV/'b_run/figure_verification.json', OUT/'figure_review.json']
    for e in fm['files']: assert sha(ROOT/e['path']) == e['sha256']
    groups = {'governance': governance, 'review_targets': controls, 'trusted_baseline': trust,
              'diagnostics': diagnostics, 'real_baseline': baseline, 'processing_feedback': feedback,
              'notebooks': notebooks, 'figures': figures}

    gc_details = [
      ('GC01', 'governance', 'workspace/protected-file checks; A initial Git blob audit; git status --short --branch',
       'main and user data/history preserved; only authorized working entries change',
       '273 initial protected evidence entries checked; teacher/starter/raw/template/old outputs 150-file audit preserved; user ZIPs preserved; no force/reset'),
      ('GC02', 'governance', 'A source audit; read active R01–R16; sync_sources.py --check',
       'one active requirements list, latest authority, limited governance diff, exactly 11 identical distribution files',
       'R01–R16 retained; latest conditional and D2 authority consumed; AGENTS +23/Protocol +13; bundle EXACTLY11 and bytes/hash pass'),
      ('GC03', 'review_targets', 'read actual A/B/C handoffs and resource/journal snapshots; firsthand C role messages',
       'independent actual role contexts and explicit main-thread execution ownership',
       'A, B, two separate C contexts plus main actually worked; resources distinguish 13 native dispatches from historical 4+6 CLI; hidden requests unknown'),
      ('GC04', 'review_targets', 'read goal.py; C gate regressions; 79-event snapshot trace review',
       'mandatory tasks/dependencies and valid target reviews control completion beyond phase five',
       'task DAG, open issue blocking, current code/run binding and additional actual sensitivity work exercised; not phase==5 completion'),
      ('GC05', 'review_targets', 'read all five actual repair transitions and scoped independent issue receipts',
       'real issue -> repair consumption -> regression -> invalidate/rebuild -> parent resume',
       'all five issues VERIFIED; failed run01 and superseded run02 preserved; run03 regenerated under fixed code'),
      ('GC06', 'diagnostics', 'remaining_probe.py g1-complete-pilot-03; C2 diagnostic manual controls',
       'all required events/partitions/summaries and exact target/hash/scope/components verified',
       '64 raw diagnostics/version checks pass; all four registered target reviews have complete checked and empty unchecked scope'),
      ('GC07', 'trusted_baseline', 'C2 37 manual attacks; independent_probe.py; roundoff scoped regression',
       'trusted candidate-external raw/contract, actual values and structure reject self-consistency attacks',
       'manual adversarial baseline cases preserved; current actual raw and approved contract independently recomputed with 383 checks'),
      ('GC08', 'trusted_baseline', 'teacher ZIP/XML exact excerpts; raw hash; authorization and local-model contract check',
       'unknown datum preserved; fixed conditional model and approved D2 govern actual pilot',
       'source_crs UNVERIFIED; source EPSG absent, datum conversion absent; raw unchanged; user authority distinct from factual source proof'),
      ('GC09', 'real_baseline', 'independent raw partitions/filter; outgoing direction; recursive DP and Decimal finite intervals',
       'exact approved order, strict thresholds, simultaneous D2, no cross-break adjacency and proper clean DP reference',
       'all 30 segments and 461 clean-point actual intervals pass; near5m case 4.938319812632412m; fixed numerical allowance independent of candidate'),
      ('GC10', 'real_baseline', 'independent_probe.py; summary_review; external point_actions.jsonl membership',
       'all fixed seven real records and 783 points processed and accounted once',
       '309 filtered +13 direction-deleted +273 DP-omitted +188 retained =783; 0 unprocessed; 7 filtered/23 processed segments'),
      ('GC11', 'processing_feedback', 'C actual near5m request -> execute_followup; remaining_probe.py followup review',
       'real processing feedback consumed and resulting target completely independently reviewed',
       'actual coordinate_sensitivity bound to baseline/request/trigger/code; 1322 checks and all9 components verified; no threshold disagreement'),
      ('GC12', 'review_targets', 'read cumulative resources/guardrails; C stop/recovery/epoch controls; actual failed run receipt',
       'mode/permissions/resource scopes explicit and ambiguous operations not blindly repeated',
       'native vs CLI and deterministic calls separated; 1 real numeric refusal preserved; inflight/old epoch guards tested; no inflight now'),
      ('GC13', 'notebooks', '261-test final JUnit; B two fresh kernels; C notebook/figure/independent artifact reviews',
       'effective core test suite, real reproducibility and honest inspected figures pass',
       '261 passed; each notebook8 cells without errors; four fresh outputs exact; three figures inspected at200dpi; starter292/1 remains historical'),
      ('GC14', 'real_baseline', 'read artifacts, notebooks, entry snapshots, resource labels; C raw/summary review',
       'no fixture/history mislabeled real, no unsupported accuracy/optimization/full-data claim',
       'current real conditional fixed pilot distinct from ENGINEERING_TEST, historical CLI and RECOMPUTE; removal and conditional geometry are descriptive'),
      ('GC15', 'review_targets', 'all issues and latest authorization reviewed; actual rebuilt outputs and followup complete',
       'ordinary authorized repairs completed in same Goal, no obsolete datum blanket block or new prompt deferral',
       'all authorized internal tasks have evidence and all five issues closed; no further engineering or research decision is required for scoped Goal1'),
      ('GC16', 'governance', 'C internal total report/receipt; fixed source and artifact hashes; local entry/link checks',
       'internally reviewable package ready; later actual safe push and remote identity checked separately',
       'internal processing/artifact lineage and reviewed claims verified; publication NOT_RUN in this receipt; GPT second review PENDING'),
    ]
    aplan = read(REV/'a_scope/TaskPlan.json')
    standards = {r['id']: r['close_standard'] for r in aplan['gc_closure_map']}
    gc = []
    for ident, task, command, expected, result in gc_details:
        paths = list(groups[task])
        if ident == 'GC05': paths += [OUT/'coordinate_issue_receipt.json', OUT/'direction_roundoff_receipt.json', OUT/'time_scope_receipt.json']
        if ident == 'GC13': paths += figures + validation
        if ident in ('GC14','GC16'): paths += [OUT/'entry_review.json', OUT/'reviewed_FINAL_RESPONSE.md.txt', OUT/'reviewed_REVIEW_PACKET.md.txt']
        gc.append({'id': ident, 'status': 'INTERNAL_VERIFIED_PUBLICATION_NOT_RUN' if ident == 'GC16' else 'VERIFIED',
                   'scope': standards[ident], 'verification_method_or_command': command, 'expected': expected,
                   'actual': result, 'evidence': bind(paths)})
    previous = {r['id']: r for r in read(REV/'historical_acceptance_before_complete.json')['original_g1_acceptance']}
    g1 = []
    for mapping in aplan['original_g1_map']:
        ident = mapping['id']; rows = [r for r in gc if r['id'] in mapping['gc_ids']]
        g1.append({'id': ident, 'requirement': previous[ident]['requirement'],
                   'status': 'INTERNAL_VERIFIED_PUBLICATION_NOT_RUN' if ident == 'G1-A18' else 'VERIFIED',
                   'gc_ids': mapping['gc_ids'], 'scope': mapping['inheritance'],
                   'current_actual_scope': 'Current conditional pilot; publication is separately pending' if ident == 'G1-A18'
                       else 'Current approved Goal1 internal scope verified; no geographic truth or G2/G3 claim',
                   'actual': [r['actual'] for r in rows],
                   'evidence': list({(e['path'],e['sha256']): e for r in rows for e in r['evidence']}.values())})
    matrix = {'classification': 'INDEPENDENT_C_ACCEPTANCE_NOT_SECOND_REQUIREMENTS_TABLE',
              'goal_id': state['goal_id'], 'execution': state['execution'], 'run_id': manifest['run_id'],
              'processing_code_sha': CODE, 'internal_status': 'VERIFIED', 'publication_status': 'NOT_RUN',
              'gpt_second_review': 'PENDING', 'submission': 'NOT_READY', 'goal2_goal3': 'NOT_RUN',
              'GC': gc, 'original_G1': g1}
    write(OUT/'acceptance_matrix.json', matrix)
    groups['internal_review'] = [OUT/'C_INTERNAL_REVIEW.md', OUT/'acceptance_matrix.json', OUT/'final_bindings_review.json',
        OUT/'reviewed_FINAL_RESPONSE.md.txt', OUT/'reviewed_REVIEW_PACKET.md.txt', OUT/'reviewed_requirements.json',
        OUT/'review_time_goal_snapshot.json', OUT/'review_time_resources_snapshot.json', Path(__file__)] + \
        [OUT/name for name in own_reports] + validation + workflow
    tasks = {k: {'status': 'VERIFIED', 'evidence': bind(v)} for k,v in groups.items()}
    for name in ['diagnostics','real_baseline','processing_feedback']: tasks[name]['run_id'] = manifest['run_id']
    tasks['processing_feedback']['followup_review'] = bind([OUT/'followup_review.json'])[0]
    audit = read(OUT/'followup_review.json')
    assert audit['target_sha256'] == sha(RUN/'coordinate_sensitivity.json') and audit['unchecked_components'] == []
    tree = ast.parse((ROOT/'task1/workflow/goal.py').read_text())
    required = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'FOLLOWUP_COMPONENTS' for t in n.targets))
    assert set(required) == set(audit['checked_components'])
    for name, names in {'diagnostics':['profile_pilot','time_boundaries','duplicate_details'],
                        'real_baseline':['baseline'], 'processing_feedback':['baseline']}.items():
        actual = {(e['path'],e['sha256']) for e in tasks[name]['evidence']}
        assert all((manifest[k][a]['path'],manifest[k][a]['sha256']) in actual for k in ['artifacts','reviews'] for a in names)
    receipt = {'classification': 'INDEPENDENT_C_INTERNAL_GOAL_ACCEPTANCE', 'reviewer': 'C:/root/c_acceptance',
               'goal_id': state['goal_id'], 'execution': state['execution'], 'status': 'VERIFIED',
               'run_id': manifest['run_id'], 'processing_code_sha': CODE, 'source_crs': 'UNVERIFIED',
               'source_datum_proven': False, 'tasks': tasks, 'publication_status': 'NOT_RUN',
               'gpt_second_review': 'PENDING', 'submission': 'NOT_READY', 'goal2_goal3': 'NOT_RUN',
               'interpretation': 'Authorizes journal registration of verified internal scope, not a claim that push or GPT remote acceptance has occurred.',
               'mutable_active_entries_are_not_hash_dependencies': True,
               'independent_commands': [
                   '.venv/bin/python '+rel(OUT/'independent_probe.py')+' g1-complete-pilot-03',
                   '.venv/bin/python '+rel(OUT/'remaining_probe.py')+' g1-complete-pilot-03',
                   '.venv/bin/python '+rel(OUT/'final_evidence_probe.py'),
                   '.venv/bin/python '+rel(Path(__file__))]}
    for item in tasks.values():
        for e in item['evidence']: assert sha(ROOT/e['path']) == e['sha256']
    forbidden = {rel(REV/'goal_state.json'),rel(REV/'resources.json'),rel(ROOT/'task1/evidence/goal1/requirements.json'),
                 rel(ROOT/'task1/evidence/goal1/acceptance.json'),rel(ROOT/'task1/evidence/goal1/REVIEW_PACKET.md'),rel(REV/'FINAL_RESPONSE.md')}
    assert not any(e['path'] in forbidden for item in tasks.values() for e in item['evidence'])
    write(OUT/'review_receipt.json', receipt)
    print('C TOTAL VERIFIED:', len(tasks), 'tasks;', len(gc), 'GC;', len(g1), 'original G1; publication NOT_RUN')
    print('receipt SHA256:', sha(OUT/'review_receipt.json'))


if __name__ == '__main__': main()
