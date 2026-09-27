"""Bind a stable publication candidate using actual previous scan plus a delta."""
import ast
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
PREFIX = EV + 'independent_documents/'
OUTPUTS = {PREFIX + name for name in [
    'publication_candidate_manifest.json', 'publication_delta_scan.json',
    'publication_preflight_receipt.json']}
BASE_SHA = 'ddef6b73a28fa819db5ee01d1bc847dedef743bd0421b0b438cd649d134f6a42'
BASE_CLASS_SHA = 'cb75ae31b704baba6160bb68458c9d262d74f21616975a5fe921d7fc3d8b2d4e'


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): value.update(block)
    return value.hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def ref(relative):
    return {'path': relative, 'sha256': sha(ROOT / relative)}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def names(*args):
    return [name.decode() for name in git(*args).split(b'\0') if name]


def leaves(value, pointer=''):
    if isinstance(value, dict):
        for key, child in value.items(): yield from leaves(child, pointer + '/' + str(key))
    elif isinstance(value, list):
        for number, child in enumerate(value): yield from leaves(child, pointer + '/' + str(number))
    elif isinstance(value, str): yield pointer, value


def main():
    for output in OUTPUTS:
        assert not (ROOT / output).exists(), 'DO_NOT_OVERWRITE_COMPLETED_PUBLICATION_AUDIT:' + output
    base_path = HERE / 'prepublication_current_preflight.json'
    classification_path = HERE / 'prepublication_current_scope_receipt.json'
    assert sha(base_path) == BASE_SHA and sha(classification_path) == BASE_CLASS_SHA
    base, classified = json.loads(base_path.read_text()), json.loads(classification_path.read_text())
    assert classified['status'] == 'READY_WITHIN_CURRENT_SCOPED_PREFLIGHT' and not base['issues']
    old_files = {entry['path']: entry for entry in base['targets']}
    old_hits = {entry['path']: entry for entry in classified['classifications']}
    scanner_path = HERE / 'prepublication_scan.py'
    spec = importlib.util.spec_from_file_location('previous_scoped_publication_rules', scanner_path)
    scanner = importlib.util.module_from_spec(spec); spec.loader.exec_module(scanner)
    assert sha(scanner_path) == base['unchanged_scanner_sha256']
    aggregate_source = ROOT / (EV + 'independent_c/review_internal_acceptance.py')
    tree = ast.parse(aggregate_source.read_text())
    mutable = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'MUTABLE_CLOSEOUT' for t in node.targets))
    assert len(mutable) == 9
    protected = scanner.PROTECTED_UNTRACKED
    tracked = set(names('ls-files', '-z'))
    untracked = set(names('ls-files', '--others', '--exclude-standard', '-z'))
    changed = set(names('diff', '--name-only', '-z', base['anchor'], '--'))
    proposed = sorted((tracked | untracked) - protected)
    scope = sorted((changed | untracked) - protected - mutable - OUTPUTS)
    checks, errors, files, delta, inherited_hits = [], [], [], [], []

    def check(label, condition):
        checks.append({'check': label, 'passed': bool(condition)})
        if not condition: errors.append({'check': label})

    inventory = {'regular_files': 0, 'regular_bytes': 0, 'symlinks': [], 'files_at_least_100MiB': []}
    for relative in proposed:
        path = ROOT / relative
        if path.is_symlink(): inventory['symlinks'].append(relative)
        elif path.is_file():
            inventory['regular_files'] += 1; inventory['regular_bytes'] += path.stat().st_size
            if path.stat().st_size >= 100 * 1024 * 1024:
                inventory['files_at_least_100MiB'].append({'path': relative, 'bytes': path.stat().st_size})
    check('no proposed symlinks', not inventory['symlinks'])
    check('no file reaches GitHub ordinary 100MiB threshold', not inventory['files_at_least_100MiB'])
    inherited_count, scanned_bytes, inherited_rasters = 0, 0, 0
    known_rasters = {entry['sha256']: entry['path'] for entry in base['targets'] if entry['path'].endswith('.png')}
    for relative in scope:
        path = ROOT / relative
        if not path.exists():
            errors.append({'path': relative, 'issue': 'PROPOSED_DELETION_REQUIRES_REVIEW'}); continue
        check('regular proposed file:' + relative, path.is_file() and not path.is_symlink())
        check('no font/cache/auth/build artifact:' + relative,
              not any(p in scanner.FORBIDDEN_PARTS or p.startswith('.env') for p in Path(relative).parts)
              and path.suffix.lower() not in scanner.FORBIDDEN_SUFFIXES)
        before = path.stat(); digest = sha(path)
        entry = {'path': relative, 'sha256': digest}
        files.append(entry)
        if relative in old_files and old_files[relative]['sha256'] == digest:
            inherited_count += 1
            if relative in old_hits: inherited_hits.append(old_hits[relative])
            continue
        record = {**entry, 'bytes': before.st_size, 'previous_sha256': old_files.get(relative, {}).get('sha256')}
        suffix = path.suffix.lower()
        if suffix == '.gz':
            with gzip.open(path, 'rb') as stream: categories, n = scanner.scan_stream(stream)
        elif suffix in scanner.TEXT_SUFFIXES or path.name in {'README', '.gitignore'}:
            with path.open('rb') as stream: categories, n = scanner.scan_stream(stream)
        elif suffix == '.pdf':
            extracted = subprocess.run(['pdftotext', str(path), '-'], capture_output=True, timeout=30)
            check('new PDF text extracts:' + relative, extracted.returncode == 0)
            categories, n = scanner.scan_stream(io.BytesIO(extracted.stdout))
            record['PDF_text_sha256'] = hashlib.sha256(extracted.stdout).hexdigest()
        else:
            categories, n = {}, 0
            record['binary_scope'] = 'metadata/hash only; actual ZIP and final visuals have separate independent review'
            if suffix == '.png':
                check('new FULL raster equals previously reviewed artifact:' + relative, digest in known_rasters)
                record['exact_previous_raster'] = known_rasters.get(digest)
                inherited_rasters += 1
            else:
                check('no new unreviewed binary import:' + relative, False)
        record['scanned_text_bytes'] = n; scanned_bytes += n
        record['marker_categories'] = categories
        if categories:
            # This round is limited to actual immutable independent-review and
            # execution receipts; do not grant a generic future-file exemption.
            allowed_paths = {
                EV + 'independent_c/delivery_incomplete_gate_rejection.json',
                EV + 'independent_c/internal_acceptance_incomplete_rejection.json',
                EV + 'independent_c/isolated_package_basic_full_receipt.json',
                EV + 'notebook_verification/isolated_basic_full_01/execution_receipt.json',
            }
            check('new marker finding is exact reviewed internal path provenance:' + relative,
                  set(categories) == {'PERSONAL_ABSOLUTE_PATH'} and relative in allowed_paths)
            if set(categories) == {'PERSONAL_ABSOLUTE_PATH'} and relative in allowed_paths:
                record['classification'] = 'AUTHENTIC_INTERNAL_EXECUTION_COMMAND_OR_TRACEBACK'
                record['reason'] = 'Actual executor/interpreter path or historical refusal traceback; not in teacher ZIP or canonical Notebook outputs, no secret value.'
                value = json.loads(path.read_text())
                record['matched_field_pointers'] = [pointer for pointer, text in leaves(value)
                    if scanner.PERSONAL.search(text.encode())]
        after = path.stat()
        check('delta file stable while read:' + relative,
              (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns))
        delta.append(record)

    # Actual diff inspection distinguishes preserved original bytes from source defects.
    name_status = git('diff', '--name-status', base['anchor'], '--').decode()
    check('no deleted/type-changed existing project files', all(line.startswith(('A\t', 'M\t')) for line in name_status.splitlines()))
    whitespace = subprocess.run(['git', 'diff', '--check', base['anchor'], '--'], cwd=ROOT, capture_output=True)
    whitespace_files = Counter()
    messages = whitespace.stdout.decode().splitlines()
    for line in messages:
        if line.endswith('trailing whitespace.'): whitespace_files[line.rsplit(':', 2)[0]] += 1
    unexpected = [line for line in messages if line and not line.startswith('+') and not line.endswith('trailing whitespace.')]
    expected_whitespace = {EV + 'USER_PROMPT.md': 504,
        EV + 'independent_c/C07_initial_failure.xml': 8,
        EV + 'independent_c/core_initial_challenges.xml': 2}
    check('diff-check findings are only preserved source/failure whitespace',
          dict(whitespace_files) == expected_whitespace and not unexpected and whitespace.returncode == 2)
    diff_review = {'actual_command': 'git diff --check ' + base['anchor'] + ' --',
        'returncode': whitespace.returncode, 'stdout_sha256': hashlib.sha256(whitespace.stdout).hexdigest(),
        'name_status_sha256': hashlib.sha256(name_status.encode()).hexdigest(),
        'whitespace_findings': dict(whitespace_files),
        'classification': '504 CRLF lines in verbatim USER_PROMPT plus ten whitespace lines in authentic pytest failure XML; preserve evidence bytes, no author-source defect.',
        'existing_project_deletions_or_type_changes': []}

    links = []
    # Mutable navigation is observed for links now, but its current hashes are
    # intentionally excluded from the stable candidate used by acceptance.
    for relative in sorted(set(scope) | {p for p in mutable if p.endswith('.md') and (ROOT/p).exists()}):
        path = ROOT / relative
        if path.suffix not in {'.md', '.ipynb'} or relative == EV + 'USER_PROMPT.md': continue
        if path.suffix == '.ipynb':
            value = json.loads(path.read_text())
            texts = [('cell:' + str(i), ''.join(c['source'])) for i, c in enumerate(value['cells']) if c['cell_type'] == 'markdown']
        else: texts = [('markdown', path.read_text())]
        for location, text in texts:
            text = re.sub(r'(?ms)^```[^\n]*\n.*?^```[^\n]*$', '', text)
            for destination in re.findall(r'!?\[[^\]\n]*\]\(([^\n]+?)\)', text):
                destination = destination.strip().split(' "', 1)[0].strip('<>')
                url = urlsplit(destination)
                if url.scheme or url.netloc: continue
                check('no unchecked local fragment:' + relative + ':' + destination, not url.fragment)
                if not url.path: continue
                target = (path.parent / unquote(url.path)).resolve()
                passed = target.exists() and target.is_relative_to(ROOT)
                check('local link:' + relative + ':' + destination, passed)
                links.append({'from': relative, 'location': location, 'target': destination, 'exists': passed})
    startup = read(EV + 'startup.json')
    original_protection = []
    for name, expected in startup['untracked_protected'].items():
        actual = sha(ROOT / name)
        check('protected original remains byte exact:' + name, actual == expected)
        if name in protected: check('protected original remains untracked:' + name, name in untracked and name not in tracked)
        original_protection.append({'path': name, 'sha256': actual, 'untracked': name in untracked})

    events = read(EV + 'governance_tool_events.json'); export = read(EV + 'governance_export_receipt.json')
    exporter = 'task1/goal3/export_governance.py'
    check('current metadata-only governance source unchanged', sha(ROOT/exporter) == base['governance_export_review']['source_sha256'])
    check('current export exact bytes', sha(ROOT/(EV+'governance_tool_events.json')) == export['export_sha256'])
    check('current export correct source', export['source_sha256'] == sha(ROOT/exporter) == events['source_sha256'])
    allowed_event_keys = {'at', 'event', 'tool', 'call_id', 'source_event_sha256', 'arguments_metadata',
        'message_availability', 'stored_message_payload_sha256', 'stored_message_payload_bytes',
        'stored_output_payload_sha256', 'stored_output_payload_bytes', 'availability', 'output'}
    check('current governance metadata schema forbids bodies/auth/reasoning/ciphertext',
          all(set(e) <= allowed_event_keys and 'message' not in e for e in events['events']))
    check('current governance allowed argument metadata', all(set(e.get('arguments_metadata', {})) <=
          {'task_name', 'target', 'fork_turns', 'model', 'reasoning_effort'} for e in events['events']))
    check('current governance allowed clear output', all('output' not in e or
          (isinstance(e['output'], dict) and set(e['output']) == {'task_name'} and e['output']['task_name'].startswith('/root/'))
          or e['output'] == 'collab tool failed: agent thread limit reached' for e in events['events']))
    check('current governance stored payloads only SHA256', all(re.fullmatch('[0-9a-f]{64}', str(v))
          for e in events['events'] for k, v in e.items() if k.endswith('_sha256')))
    check('current governance count matches receipt', len(events['events']) == export['events'])
    mutable_observations = [ref(p) for p in sorted(mutable) if (ROOT/p).is_file()]
    # No author artifact is changed, including the canonical ZIP and PDFs.
    for receipt_name in ['handoffs_current_closure.json', 'actual_zip_static_receipt.json',
                         'report_entry_delta_receipt.json', 'figures_current_closure.json',
                         'experiment_report_current_closure.json', 'process_report_current_closure.json']:
        check('actual prior independent receipt exists:' + receipt_name, (HERE/receipt_name).is_file())

    detail = {'role_context': '/root/c_documents', 'at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'VERIFIED' if not errors else 'REPAIR_REQUIRED',
        'base_scan': ref(PREFIX+'prepublication_current_preflight.json'),
        'base_manual_classification': ref(PREFIX+'prepublication_current_scope_receipt.json'),
        'unchanged_current_files_inherited_by_exact_hash': inherited_count,
        'inherited_marker_classifications': inherited_hits, 'delta_files': delta,
        'delta_scanned_text_bytes': scanned_bytes, 'delta_exact_previous_rasters': inherited_rasters,
        'checks': checks, 'errors': errors, 'metadata_inventory': inventory, 'diff_review': diff_review,
        'local_links': links, 'protected_originals': original_protection,
        'mutable_observations_not_frozen_targets': mutable_observations,
        'current_governance_events_observed': len(events['events']),
        'current_governance_function_calls_observed': sum(e['event']=='function_call' for e in events['events']),
        'governance_limits': 'Only exported metadata and exporter code examined; original auth/session/reasoning/ciphertext bodies were not opened or recovered.',
        'original_first_and_second_scans_preserved': True,
        'actual_command': '.venv/bin/python '+PREFIX+'review_publication_preflight.py'}
    delta_path = HERE / 'publication_delta_scan.json'
    delta_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2)+'\n')
    if errors:
        print(json.dumps({'status': 'REPAIR_REQUIRED', 'errors': errors}, ensure_ascii=False)); return
    manifest = {'at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Stable current files added/modified since accepted Goal2 anchor; unmodified historical project files retain existing repository identity.',
        'anchor': base['anchor'], 'observed_git_head': git('rev-parse', 'HEAD').decode().strip(),
        'files': files, 'excluded_mutable_closeout_paths': sorted(mutable),
        'excluded_self_referential_audit_outputs': sorted(OUTPUTS),
        'protected_untracked_user_archives_excluded': sorted(protected),
        'later_delta_required': 'Actual internal-acceptance snapshot/receipt and publication facts created after this cutoff require separate bounded publication review; no future hash is claimed.'}
    manifest_path = HERE / 'publication_candidate_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    source_paths = [PREFIX+'review_publication_preflight.py', PREFIX+'prepublication_scan.py',
        PREFIX+'prepublication_current_preflight.json', PREFIX+'prepublication_current_scope_receipt.json',
        PREFIX+'actual_zip_static_receipt.json', PREFIX+'report_entry_delta_receipt.json',
        PREFIX+'handoffs_current_closure.json', EV+'independent_c/review_internal_acceptance.py', exporter]
    receipt = {'role_context': '/root/c_documents', 'target_id': 'publication_preflight', 'status': 'VERIFIED',
        'at_utc': datetime.now(timezone.utc).isoformat(),
        'checks': {name: 'VERIFIED' for name in ['diff', 'secret_scan', 'large_files', 'original_protection', 'local_links']},
        'candidate_manifest_path': str(manifest_path.relative_to(ROOT)), 'candidate_manifest_sha256': sha(manifest_path),
        'targets': [ref(str(manifest_path.relative_to(ROOT))), ref(str(delta_path.relative_to(ROOT)))],
        'source_hashes': {p: sha(ROOT/p) for p in source_paths}, 'errors': [],
        'checked_components': [
            'Actual stable publication candidate hashes; existing completed 1008-file/6971598166-byte scan inherited only where current bytes match, with new/changed content scanned independently.',
            'Current Git diff and file inventory inspected; verbatim Prompt CRLF and authentic failed-test whitespace retained and specifically classified, no author source defect or project deletion.',
            'Recorded secret/token/ciphertext/absolute-path markers, new PDFs text, exact previous PNG identity, no font/full-paper/cache/auth import; actual teacher ZIP has separate independent static/full checks.',
            'Every proposed ordinary file remains below GitHub size threshold; protected original ZIP bytes exact and two original user archives stay untracked.',
            'All explicit local Markdown and Notebook navigation links resolve; current mutable navigation observed but not misbound as frozen source.',
            'Current governance export preserves metadata-only schema and SHA256 payload references; final report keeps its separate original fixed snapshot.'
        ],
        'unchecked_components': ['Later internal-acceptance and actual publication artifacts and mutable closeout bytes require their separate delta gate',
            'Actual push, remote equality and fixed-SHA readback have not yet happened',
            'Unmodified pre-Goal3 content was not rescanned; arbitrary unrecognizable secret formats are outside marker-based scan guarantees',
            'Missing external identity/Evidence Master inputs, webpage GPT review, user Understanding and actual teacher submission'],
        'new_processing_or_model_calls': 0, 'installed_dependencies': [],
        'formal_remote_publication_acceptance': False,
        'actual_command': '.venv/bin/python '+PREFIX+'review_publication_preflight.py'}
    receipt_path = HERE / 'publication_preflight_receipt.json'
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': 'VERIFIED', 'candidate_files': len(files), 'inherited_exact_files': inherited_count,
        'delta_files': len(delta), 'delta_scanned_text_bytes': scanned_bytes, 'local_links': len(links),
        'receipt': ref(str(receipt_path.relative_to(ROOT))), 'candidate_manifest': ref(str(manifest_path.relative_to(ROOT)))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
