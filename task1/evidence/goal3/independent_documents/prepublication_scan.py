"""Read-only, scoped publication preflight; never print suspected secret values."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ANCHOR = '6fad8420b09ba123fe0658a5cd805cb7b7b9e67b'
OUTPUT = HERE/'prepublication_preflight.json'
PROTECTED_UNTRACKED = {'SC-LAB1-G1-COMPLETE-001_HANDOFF.zip',
                       'SC-LAB1-G1-CLOSURE-002_HANDOFF.zip'}
SECRET = re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                    rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b|'
                    rb'\bgithub_pat_[A-Za-z0-9_]{40,}\b|'
                    rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b|'
                    rb'\bAKIA[0-9A-Z]{16}\b')
OPAQUE = re.compile(rb'\bgAAAA[A-Za-z0-9_-]{80,}={0,2}')
PERSONAL = re.compile(rb'/(?:home|Users)/[^/\s"<>]+/|[A-Za-z]:(?:\\\\|\\|/)Users(?:\\\\|\\|/)[^\\/\s]+')
FORBIDDEN_PARTS = {'.git','.venv','venv','__pycache__','.pytest_cache','.mypy_cache',
                   '.ruff_cache','.mplcache','.ipynb_checkpoints','node_modules','.ssh','.codex','__MACOSX'}
FORBIDDEN_SUFFIXES = {'.pyc','.pyo','.ttf','.otf','.woff','.woff2','.pem','.key','.aux',
                      '.fls','.fdb_latexmk','.toc','.synctex'}
TEXT_SUFFIXES = {'.py','.md','.json','.csv','.tex','.bib','.txt','.xml','.svg','.ipynb','.patch','.yml','.yaml','.toml'}


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def names(*args):
    return [value.decode('utf8') for value in git(*args).split(b'\0') if value]


def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def scan_stream(stream):
    counts = Counter(); tail = b''; n = 0
    while True:
        block = stream.read(1024*1024)
        if not block:
            break
        n += len(block); data = tail+block
        tests = [('POSSIBLE_SECRET',SECRET,(b'PRIVATE KEY',b'ghp_',b'gho_',b'ghu_',b'ghs_',b'ghr_',
                                          b'github_pat_',b'sk-',b'AKIA')),
                 ('OPAQUE_PLATFORM_CIPHERTEXT',OPAQUE,(b'gAAAA',)),
                 ('PERSONAL_ABSOLUTE_PATH',PERSONAL,(b'/home/',b'Users'))]
        for name,pattern,markers in tests:
            # Counts are only candidate occurrences; boundary overlap may repeat
            # a hit. No matched value is stored or printed.
            if any(marker in data for marker in markers):
                counts[name] += len(pattern.findall(data))
        tail = data[-256:]
    return {k:v for k,v in counts.items() if v},n


def main():
    start_head = git('rev-parse','HEAD').decode().strip()
    index = git('ls-files','--stage','-z')
    tracked = names('ls-files','-z')
    changed = names('diff','--name-only','-z',ANCHOR,'--')
    untracked = names('ls-files','--others','--exclude-standard','-z')
    proposed = sorted(set(tracked+untracked)-PROTECTED_UNTRACKED)
    scope = sorted((set(changed)|set(untracked))-PROTECTED_UNTRACKED-{str(OUTPUT.relative_to(ROOT))})
    startup = json.loads((ROOT/'task1/evidence/goal3/startup.json').read_text())
    checks,targets,hits,skipped,issues = [],[],[],[],[]

    def check(label, condition):
        checks.append({'check':label,'passed':bool(condition)})
        if not condition:
            issues.append({'category':'FAILED_CHECK','check':label})

    protected = {}
    for name,expected in startup['untracked_protected'].items():
        actual = sha_file(ROOT/name)
        protected[name] = {'sha256':actual,'unchanged_since_start':actual==expected,
                           'tracked':name in tracked,'untracked':name in untracked}
        check('original_zip_unchanged:'+name,actual==expected)
    check('two_user_archives_still_untracked',all(name in untracked and name not in tracked for name in PROTECTED_UNTRACKED))
    check('two_user_archives_excluded_from_proposed_additions',not PROTECTED_UNTRACKED & set(scope))
    metadata = {'regular_files':0,'regular_bytes':0,'symlinks':[],'files_at_least_100_MB':[]}
    for relative in proposed:
        path = ROOT/relative
        if path.is_symlink():
            metadata['symlinks'].append(relative)
        elif path.is_file():
            size = path.stat().st_size
            metadata['regular_files'] += 1; metadata['regular_bytes'] += size
            if size >= 100*1024*1024:
                metadata['files_at_least_100_MB'].append({'path':relative,'bytes':size})
    check('no_proposed_symlinks',not metadata['symlinks'])
    check('no_Git_100MiB_files',not metadata['files_at_least_100_MB'])

    text_bytes, pdfs = 0, []
    for relative in scope:
        path = ROOT/relative
        if not path.exists():
            skipped.append({'path':relative,'reason':'deleted or not present in current worktree'})
            continue
        if path.is_symlink() or not path.is_file():
            issues.append({'path':relative,'category':'NON_REGULAR_PROPOSED_INPUT'}); continue
        if any(p in FORBIDDEN_PARTS or p.startswith('.env') for p in path.relative_to(ROOT).parts) or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            issues.append({'path':relative,'category':'FONT_CACHE_AUTH_OR_BUILD_ARTIFACT'})
        start = path.stat(); digest = sha_file(path)
        targets.append({'path':relative,'sha256':digest,'bytes':start.st_size})
        categories = {}
        if path.suffix == '.gz':
            with gzip.open(path,'rb') as stream:
                categories,n = scan_stream(stream); text_bytes += n
        elif path.suffix.lower() in TEXT_SUFFIXES or path.name in ('README','.gitignore'):
            with path.open('rb') as stream:
                categories,n = scan_stream(stream); text_bytes += n
        elif path.suffix.lower() == '.pdf':
            result = subprocess.run(['pdftotext',str(path),'-'],capture_output=True,timeout=30)
            check('PDF_text_extract:'+relative,result.returncode==0)
            import io
            categories,n = scan_stream(io.BytesIO(result.stdout)); text_bytes += n
            pdfs.append(relative)
        elif path.suffix.lower() == '.png':
            skipped.append({'path':relative,'reason':'native figure/render raster content; binary bytes hash-bound, final visual review pending'})
        else:
            skipped.append({'path':relative,'reason':'binary/nontext type; metadata and hash checked only'})
        if categories:
            hits.append({'path':relative,'categories':categories,'sha256':digest,
                         'internal_evidence':relative.startswith('task1/evidence/')})
        end = path.stat()
        if (end.st_size,end.st_mtime_ns)!=(start.st_size,start.st_mtime_ns):
            issues.append({'path':relative,'category':'CHANGED_DURING_SCAN_RECHECK_REQUIRED'})

    event_path = ROOT/'task1/evidence/goal3/governance_tool_events.json'
    export_path = ROOT/'task1/evidence/goal3/governance_export_receipt.json'
    export_source = ROOT/'task1/goal3/export_governance.py'
    events = json.loads(event_path.read_text()); export = json.loads(export_path.read_text())
    check('export_receipt_binds_actual_event_bytes',export['export_sha256']==sha_file(event_path))
    check('export_receipt_binds_actual_source',export['source_sha256']==sha_file(export_source)==events['source_sha256'])
    check('only_allowed_collaboration_tools',all(e['tool'] in {'spawn_agent','followup_task','send_message','interrupt_agent'} for e in events['events']))
    check('only_call_or_output_events',all(e['event'] in {'function_call','function_call_output'} for e in events['events']))
    check('no_exported_message_body',all('message' not in e for e in events['events']))
    allowed_event_keys = {'at','event','tool','call_id','source_event_sha256','arguments_metadata',
        'message_availability','stored_message_payload_sha256','stored_message_payload_bytes',
        'stored_output_payload_sha256','stored_output_payload_bytes','availability','output'}
    check('event_schema_has_no_reasoning_ciphertext_auth_field',all(set(e)<=allowed_event_keys for e in events['events']))
    check('allowed_argument_metadata_only',all(set(e.get('arguments_metadata',{})) <=
        {'task_name','target','fork_turns','model','reasoning_effort'} for e in events['events']))
    clear_outputs = [e['output'] for e in events['events'] if 'output' in e]
    check('clear_tool_outputs_are_only_agent_names_or_thread_limit',all(
        (isinstance(value,dict) and set(value)=={'task_name'} and value['task_name'].startswith('/root/'))
        or value=='collab tool failed: agent thread limit reached' for value in clear_outputs))
    check('all_stored_payload_digests_are_sha256',all(re.fullmatch('[0-9a-f]{64}',value)
        for e in events['events'] for key,value in e.items() if key.endswith('_sha256')))
    check('actual_export_event_count',len(events['events'])==export['events'])

    result = {'role_context':'/root/c_documents','target_id':'scoped_prepublication_inventory',
        'status':'CANDIDATE_FINDINGS_REQUIRE_MANUAL_CLASSIFICATION' if hits or issues else 'READY_WITHIN_PRELIMINARY_SCOPE',
        'at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Git changed paths since accepted G2 anchor plus all current nonignored untracked proposed additions; index/proposed metadata checked without reading Git auth/config or unrelated user history.',
        'anchor':ANCHOR,'head_at_start':start_head,'head_at_end':git('rev-parse','HEAD').decode().strip(),
        'git_index_stage_sha256':hashlib.sha256(index).hexdigest(),
        'tracked_index_paths':len(tracked),'changed_since_anchor':len(changed),
        'proposed_new_nonignored_paths':len(set(untracked)-PROTECTED_UNTRACKED),
        'content_scanned_or_hash_bound_targets':len(targets),'targets':targets,
        'proposed_worktree_inventory':metadata,'protected_original_zip_status':protected,
        'scanned_text_or_decompressed_bytes':text_bytes,'PDF_text_extracted':pdfs,
        'candidate_findings':hits,'issues':issues,'checks':checks,'binary_scope_limits':skipped,
        'governance_export_review':{'event_sha256':sha_file(event_path),'receipt_sha256':sha_file(export_path),
            'source_sha256':sha_file(export_source),'events':len(events['events']),
            'message_bodies_exported':0,'clear_metadata_tool_outputs':len(clear_outputs),
            'session_log_read_by_this_review':False,'encrypted_payload_recovered':False,
            'source_scope':'source filter and exported actual schema; original session/auth/reasoning not opened'},
        'unchecked_components':['new final reports, actual ZIP and executed Notebook outputs after this timestamp',
            'binary image visual content and all-page final report review',
            'all immutable pre-G3 file contents; metadata/index checked only',
            'arbitrary secret formats without recognizable markers; no absence guarantee beyond recorded scan rules',
            'remote push and fixed-SHA reread; this is not publication acceptance'],
        'no_infrastructure_scanner_run':True,'no_original_file_modified':True,
        'scanner_execution_note':'An earlier read-only attempt was stopped before completion after observing slow regex scans over numeric traces. This completed attempt uses logically necessary literal-marker prefilters before identical regexes; no incomplete pass result was retained.',
        'installed_dependencies':[],'actual_command':
            '.venv/bin/python task1/evidence/goal3/independent_documents/prepublication_scan.py'}
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','tracked_index_paths','changed_since_anchor',
        'proposed_new_nonignored_paths','content_scanned_or_hash_bound_targets','scanned_text_or_decompressed_bytes',
        'issues')},ensure_ascii=False))
    print(json.dumps({'candidate_findings':hits},ensure_ascii=False))


if __name__ == '__main__':
    main()
