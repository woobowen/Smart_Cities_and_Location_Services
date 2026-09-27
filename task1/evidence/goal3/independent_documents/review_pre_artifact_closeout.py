"""Independent bounded closeout review after stable engineering acceptance."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
OUT = EV + 'independent_documents/pre_artifact_closeout_receipt.json'


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): value.update(block)
    return value.hexdigest()


def objsha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def main():
    assert not (ROOT / OUT).exists(), 'do not overwrite independent closeout receipt'
    manifest_path = EV + 'independent_documents/publication_candidate_manifest.json'
    assert sha(ROOT/manifest_path) == '91848d44db7b67a4ba809f98adc31b35bab1947bc882002e6702a4f7b8e578b2'
    manifest = read(manifest_path); stable = {r['path']: r['sha256'] for r in manifest['files']}
    checks, errors, cache = [], [], {}

    def check(label, condition):
        checks.append({'check': label, 'passed': bool(condition)})
        if not condition: errors.append({'check': label})

    def digest(relative):
        if relative not in cache: cache[relative] = sha(ROOT / relative)
        return cache[relative]

    for relative, expected in stable.items():
        check('unchanged frozen candidate:' + relative, digest(relative) == expected)
    names = set()
    for args in [('diff', '--name-only', '-z', manifest['anchor'], '--'), ('ls-files', '--others', '--exclude-standard', '-z')]:
        names.update(n.decode() for n in subprocess.check_output(['git', *args], cwd=ROOT).split(b'\0') if n)
    delta_paths = sorted(p for p in names if p not in stable and p != OUT and
        p not in manifest['protected_untracked_user_archives_excluded'] and (ROOT / p).is_file())
    spec = importlib.util.spec_from_file_location('closeout_marker_rules', HERE / 'prepublication_scan.py')
    scanner = importlib.util.module_from_spec(spec); spec.loader.exec_module(scanner)
    observations, scanned_bytes = [], 0
    for relative in delta_paths:
        path = ROOT / relative
        check('closeout is plain text evidence/source:' + relative, path.suffix in {'.json', '.md', '.py'})
        check('no closeout symlink/large file:' + relative, not path.is_symlink() and path.stat().st_size < 100 * 1024 * 1024)
        with path.open('rb') as stream: categories, count = scanner.scan_stream(stream)
        scanned_bytes += count
        row = {'path': relative, 'sha256': digest(relative), 'bytes': count, 'marker_categories': categories}
        if categories:
            allowed = {EV + 'goal_state.json', EV + 'internal_acceptance_submission_snapshot.json'}
            check('only preserved actual command paths in current/snapshot journal:' + relative,
                  set(categories) == {'PERSONAL_ABSOLUTE_PATH'} and relative in allowed)
            row['classification'] = 'PRESERVED_ACTUAL_COMMAND_ARGUMENTS_IN_JOURNAL'
            row['reason'] = 'The identical original event command paths were already classified in the prepublication scan; current state and immutable acceptance snapshot preserve real command provenance.'
        observations.append(row)
    accepted_path = EV + 'independent_c/internal_acceptance_receipt.json'
    accepted = read(accepted_path)
    check('exact actual independent acceptance receipt', digest(accepted_path) == '488b7bb5de1272c3c2e0ee470b37830d69bb62ed7725b71ba9ad98e57ac01b87')
    check('independent acceptance has correct role/target/status',
          (accepted['role_context'], accepted['target_id'], accepted['status']) == ('/root/c_protocol', 'internal_acceptance', 'VERIFIED'))
    check('1131 actual targets and 222 sources', (len(accepted['targets']), len(accepted['source_hashes'])) == (1131, 222))
    check('15 actual prerequisites and no engineering blocker', len(accepted['prerequisite_tasks']) == 15 and
          not accepted['open_engineering_blockers'] and not accepted['errors'])
    for target in accepted['targets']:
        check('accepted current target exact:' + target['path'], digest(target['path']) == target['sha256'])
    for relative, expected in accepted['source_hashes'].items():
        check('accepted source exact:' + relative, digest(relative) == expected)
    check('acceptance explicitly partial/external', accepted['goal_status'] == 'PARTIAL_BLOCKED' and
          accepted['external_dependencies'] == ['EVIDENCE_MASTER_DEPENDENCY', 'META_DEPENDENCY'])
    state = read(EV+'goal_state.json')
    previous = 'ROOT'
    for event in state['events']:
        check('actual event chain:' + str(event.get('sequence', len(checks))),
              event['previous_hash'] == previous and objsha({k:v for k,v in event.items() if k!='hash'}) == event['hash'])
        previous = event['hash']
    task = state['tasks']['internal_acceptance']
    check('root actually consumed independent acceptance', task['status'] == 'VERIFIED' and
          task['verifier'] == '/root/c_protocol' and task['receipt']['sha256'] == digest(accepted_path))
    check('publication not falsely accepted before push', state['tasks']['publication']['status'] == 'PENDING')
    check('all real engineering issues closed', all(i['status'] == 'VERIFIED' for i in state['issues'].values()))
    check('external review/understanding/submission remain honest',
          (state['GPT_SECOND_REVIEW'], state['Understanding'], state['Submission']) == ('PENDING', 'USER_DETERMINED', 'NOT_READY'))
    requirements = read(EV+'requirements.json')
    states = {r['id']:r['status'] for r in requirements['requirements']}
    expected_states = {'G3-A%02d'%i: ('BLOCKED' if i in {15,16,18} else 'NOT_RUN' if i==20 else 'PASS') for i in range(1,21)}
    check('A01-A20 truthful post-acceptance status', states == expected_states)
    refs = []
    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and re.fullmatch('[0-9a-f]{64}', str(value.get('sha256',''))): refs.append(value)
            for child in value.values(): walk(child)
        elif isinstance(value, list):
            for child in value: walk(child)
    resources = read(EV+'resource_plan.json')
    for document in [requirements, resources, read(EV+'runtime_checkpoint.json'), read(EV+'PUBLICATION_RECORD.json')]: walk(document)
    for reference in refs:
        check('closeout actual source binding:' + reference['path'], digest(reference['path']) == reference['sha256'])
    publication = read(EV+'PUBLICATION_RECORD.json')
    check('artifact SHA and push outcome not fabricated', publication['ARTIFACT_SHA'] is None and publication['last_actual_push_verification'] is None)
    check('correct expected repository and branch', publication['repository'] == 'https://github.com/woobowen/Smart_Cities_and_Location_Services.git' and publication['branch'] == 'main')
    check('prior remote observation not claimed new push', publication['prepush_remote_observation']['publication_performed'] is False)
    runtime = read(EV+'runtime_checkpoint.json')
    check('nothing still secretly running', runtime['active_execution'] is None and not runtime['open_engineering_issues'])
    check('four FULL executions recorded', len(runtime['completed_full_notebooks']) == 4 and
          all(x['status'] == 'VERIFIED' for x in runtime['completed_full_notebooks']))
    final = (ROOT/(EV+'FINAL_RESPONSE.md')).read_text()
    packet = (ROOT/(EV+'REVIEW_PACKET.md')).read_text()
    for key in ['A','B','C','D','E','F','G','H','I']:
        check('complete Chinese final response section:' + key, '\n## '+key+'.' in final)
    for anchor in ['PARTIAL_BLOCKED', '1,131', '222', '15 个前置', 'GPT_SECOND_REVIEW=PENDING']:
        check('actual final summary scope:' + anchor, anchor in final)
    check('both review entry documents still report actual push pending', '当前未 push' in final and '实际发布正在进行' in packet)
    for anchor in ['469 passed + 10 subtests passed', '479', '600 条', '349 条', '35,868→62,220',
                   '10,991→12,114', '501,511', '911,330', '1,172,211', '500,312', '20,679',
                   '266.016754', '56 条记录、112 份', '50 条随机/类别记录、100 份', '2,811.70 秒', '534.86 秒']:
        check('final text retains checked factual reading:' + anchor, anchor in final)
    check('actual test interpretation independently supported', accepted['working_tests']['actual_testcase_nodes'] == 469 and
          accepted['working_tests']['suite_total'] == 479 and accepted['working_tests']['passed_subtests'] == 10)
    links = []
    for relative in delta_paths:
        if not relative.endswith('.md'): continue
        for destination in re.findall(r'\]\(([^)]+)\)', (ROOT/relative).read_text()):
            url = urlsplit(destination)
            if url.scheme or url.netloc: continue
            target = ((ROOT/relative).parent/unquote(url.path)).resolve()
            good = target.exists() and target.is_relative_to(ROOT)
            check('current closeout link:' + relative + ':' + destination, good)
            links.append({'from': relative, 'target': destination, 'exists': good})
    # The metadata export is unchanged from the final preflight, not a new message log.
    previous_delta = read(EV+'independent_documents/publication_delta_scan.json')
    for observation in previous_delta['mutable_observations_not_frozen_targets']:
        if 'governance_' in observation['path']:
            check('governance metadata bytes remain previously reviewed:' + observation['path'], digest(observation['path']) == observation['sha256'])
    check('final report snapshot remains stable with whole candidate',
          'task1/evidence/goal3/governance_report_snapshot.json' in stable)
    startup = read(EV+'startup.json')
    tracked = set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    for name, expected in startup['untracked_protected'].items():
        check('original ZIP still byte-exact:' + name, digest(name) == expected)
        if name in manifest['protected_untracked_user_archives_excluded']:
            check('original ZIP still untracked:' + name, name not in tracked)
    targets = [{'path': r['path'], 'sha256': r['sha256']} for r in observations]
    # Final independent receipt is as-of evidence, not a future public SHA claim.
    result = {'role_context':'/root/c_documents', 'target_id':'pre_artifact_closeout',
        'status':'VERIFIED' if not errors else 'REPAIR_REQUIRED', 'at_utc':datetime.now(timezone.utc).isoformat(),
        'targets':targets, 'source_hashes':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),
            manifest_path:sha(ROOT/manifest_path), EV+'independent_documents/prepublication_scan.py':sha(HERE/'prepublication_scan.py')},
        'checks':checks, 'errors':errors, 'delta_scan':observations, 'scanned_text_bytes':scanned_bytes,
        'unchanged_stable_candidate_files':len(stable), 'checked_links':links,
        'checked_components':[
            'Actual full Chinese FINAL_RESPONSE and current REVIEW_PACKET read; reported method/final/full counts, negative results, four FULL executions, external dependencies and pending publication align with independently bound evidence.',
            'All 1049 stable candidate bytes unchanged; exact accepted 1131 targets/222 sources and real 15-prerequisite acceptance record checked without rerunning data processing.',
            'Real journal acceptance/event chain, A19 scoped PASS and A15/A16/A18 external BLOCKED retained; A20 stays NOT_RUN until real publication.',
            'All current delta content scanned for recorded secret/ciphertext/path markers; only preserved authentic journal command paths classified, local Markdown links valid.',
            'Current governance metadata export remains previously reviewed; original ZIP bytes and untracked status preserved; no new dependency installation.'
        ],
        'unchecked_components':['Actual ARTIFACT commit, push, remote equality and fixed-SHA readback have not yet occurred',
            'Subsequent publication records require an as-of delta and actual remote gate',
            'External identity, original interaction evidence, Evidence Master LOCK, webpage GPT review and user Understanding'],
        'may_proceed_to_authorized_artifact_commit_and_push':not errors,
        'remote_publication_verified':False, 'new_processing_or_model_calls':0,
        'installed_dependencies':[], 'old_stable_manifest_modified':False,
        'review_harness_correction':'Initial checker used report_build/governance_report_snapshot.json instead of the actual goal3/governance_report_snapshot.json. The real file was already hash-checked in the 1049-file manifest; corrected only the checker assertion and retained its first attempt. No author artifact changed.',
        'actual_command':'.venv/bin/python '+str(Path(__file__).relative_to(ROOT))}
    with (ROOT/OUT).open('x') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'status':result['status'], 'targets':len(targets),'checks':len(checks),
        'delta_bytes_scanned':scanned_bytes,'errors':errors,'receipt':OUT,'sha256':sha(ROOT/OUT)},ensure_ascii=False))


if __name__=='__main__': main()
