"""Classify actual staged-format warnings without changing data or Git settings."""
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
EV = ROOT / 'task1/evidence/goal3'
HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    output = HERE / 'staged_diff_check_receipt.json'
    assert not output.exists()
    checks, errors = [], []
    def check(name, actual, expected=True):
        checks.append({'check': name, 'passed': actual == expected})
        if actual != expected: errors.append({'check': name, 'actual': actual, 'expected': expected})
    archive = EV / 'staged_diff_check.txt.gz'
    summary_path = EV / 'staged_diff_check_classification.json'
    summary = json.loads(summary_path.read_text())
    archived = gzip.decompress(archive.read_bytes())
    current = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, capture_output=True)
    check('independent cached diff returned its real warning status', current.returncode, 2)
    check('independent cached diff exactly equals archived output', sha(current.stdout), sha(archived))
    check('no stderr from cached diff', current.stderr, b'')
    check('exact archived decompressed bytes', len(archived), summary['output_bytes'])
    check('exact compressed archive binding', sha(archive.read_bytes()), summary['compressed_output']['sha256'])
    warning_pattern = re.compile(rb'^(.*):(\d+): (trailing whitespace\.|new blank line at EOF\.)\n$')
    warnings = defaultdict(list); kinds = Counter(); extensions = Counter(); unparsed = []
    for line in archived.splitlines(keepends=True):
        match = warning_pattern.fullmatch(line)
        if match:
            relative, number, kind = match[1].decode(), int(match[2]), match[3].decode()
            warnings[relative].append((number, kind)); kinds[kind] += 1; extensions[Path(relative).suffix] += 1
        elif line.startswith(b'+'):
            continue
        elif line.strip(): unparsed.append(sha(line))
    check('no unparsed warning records', unparsed, [])
    check('actual warnings by kind', dict(kinds), summary['warnings_by_kind'])
    check('actual warnings by extension', dict(extensions), summary['warnings_by_extension'])
    check('actual warning-file counts', {p:len(v) for p,v in warnings.items()}, summary['files'])
    check('actual warning count', sum(kinds.values()), 167289)
    check('actual warning files', len(warnings), 71)
    check('no Python Markdown or TeX source warning', set(extensions), {'.csv', '.svg', '.txt', '.patch'})

    manifest_path = HERE / 'publication_candidate_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    check('frozen independent manifest unchanged', sha(manifest_path.read_bytes()),
          '91848d44db7b67a4ba809f98adc31b35bab1947bc882002e6702a4f7b8e578b2')
    indexed = {}; index_total = 0
    process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for item in manifest['files']:
        process.stdin.write((':' + item['path'] + '\n').encode()); process.stdin.flush()
        header = process.stdout.readline().decode().strip().split()
        assert len(header) == 3 and header[1] == 'blob', ('NON_BLOB_INDEX_ENTRY', item['path'])
        size = int(header[2]); raw = process.stdout.read(size)
        assert len(raw) == size and process.stdout.read(1) == b'\n'
        check('actual staged blob equals frozen bytes:' + item['path'], sha(raw), item['sha256'])
        index_total += size
        if item['path'] in warnings: indexed[item['path']] = raw
    process.stdin.close(); check('actual index reader completion', process.wait(), 0)
    binding_path = EV / 'staged_candidate_binding.json'
    binding = json.loads(binding_path.read_text())
    check('independently repeated all staged bindings', len(manifest['files']), binding['checked_index_blobs'])
    check('independently repeated staged byte count', index_total, binding['checked_bytes'])
    check('all warned files were independently bound index blobs', set(indexed), set(warnings))
    classifications = []
    for relative, items in warnings.items():
        raw = indexed[relative]; lines = raw.splitlines(keepends=True)
        suffix = Path(relative).suffix
        check('warned worktree remains equal to staged blob:' + relative, sha((ROOT/relative).read_bytes()), sha(raw))
        invalid_trailing, invalid_eof = [], []
        for number, kind in items:
            line = lines[number-1]
            if kind == 'trailing whitespace.':
                if line.rstrip(b'\n') == line.rstrip(b'\n').rstrip(b' \t\r'):
                    invalid_trailing.append(number)
            else:
                if number != len(lines) or line != b'\n': invalid_eof.append(number)
        check('every actual warned trailing line verified:' + relative, invalid_trailing, [])
        check('every actual blank EOF line verified:' + relative, invalid_eof, [])
        if suffix == '.csv':
            check('CSV warning for every unchanged CRLF record:' + relative,
                  [n for n,k in items], list(range(1,len(lines)+1)))
            check('all CSV original line endings are CRLF:' + relative, all(line.endswith(b'\r\n') for line in lines))
            rows = list(csv.reader(io.StringIO(raw.decode(), newline='')))
            check('CSV parses all original rows:' + relative, len(rows), len(lines))
            check('CSV row widths agree:' + relative, all(len(row)==len(rows[0]) for row in rows))
            reason = 'Generated CSV retains its actual CRLF line endings; every warning is the CR before LF, with complete rows/columns parsed and exact frozen/index identity preserved.'
            category = 'GENERATED_CSV_CRLF'
        elif suffix == '.svg':
            svg = ET.fromstring(raw)
            check('actual valid SVG XML:' + relative, svg.tag, '{http://www.w3.org/2000/svg}svg')
            check('native Matplotlib generator metadata:' + relative, b'Matplotlib' in raw)
            category = 'GENERATED_MATPLOTLIB_SVG_WHITESPACE'
            reason = 'Whitespace in actual Matplotlib SVG serialization; valid native vector source, already accepted visual/data identity and staged bytes remain unchanged.'
        elif suffix == '.patch':
            check('all patch warnings are required blank context lines:' + relative,
                  all(lines[number-1] == b' \n' for number,kind in items))
            category = 'AUTHENTIC_UNIFIED_DIFF_CONTEXT'
            reason = 'Each warned line is a single unified-diff context prefix followed by newline. Removing it would change the stored repair patch evidence.'
        else:
            check('text warnings are exact known failure/compile logs:' + relative,
                  relative.endswith('/failure.txt') or relative.endswith('/experiment1_compile_output.txt')
                  or relative.endswith('/missing_optional_needspace.txt'))
            category = 'AUTHENTIC_FAILURE_OR_COMPILER_OUTPUT'
            reason = 'Actual failure/interrupt traceback or XeLaTeX output includes spaces/blank EOF lines; retained as execution evidence, not authored processing code.'
        classifications.append({'path':relative,'sha256':sha(raw),'warnings':len(items),
            'warning_line_list_sha256':sha(json.dumps(items,separators=(',',':')).encode()),
            'first_warning_line':items[0][0],'last_warning_line':items[-1][0],
            'complete_warning_line_source':str(archive.relative_to(ROOT)), 'classification':category,
            'reason':reason,'repair_or_recompute_required':False})
    protected = {'SC-LAB1-G1-COMPLETE-001_HANDOFF.zip', 'SC-LAB1-G1-CLOSURE-002_HANDOFF.zip'}
    staged_names = {n.decode() for n in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).split(b'\0') if n}
    check('protected untracked archives not staged', not (staged_names & protected))
    result = {'role_context':'/root/c_documents','target_id':'staged_diff_format_classification',
        'status':'VERIFIED' if not errors else 'REPAIR_REQUIRED','checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'targets':[file_ref(p) for p in [archive,summary_path,binding_path]],
        'source_hashes':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__).read_bytes()),
            str(manifest_path.relative_to(ROOT)):sha(manifest_path.read_bytes())},
        'actual_staged_command':{'command':'git diff --cached --check','exit_code':current.returncode,
            'output_bytes':len(current.stdout),'output_sha256':sha(current.stdout)},
        'warning_counts':dict(extensions),'warning_kinds':dict(kinds),
        'independent_index_check':{'blobs':len(manifest['files']),'bytes':index_total,'scope':'actual Git index, not future commit/remote'},
        'classifications':classifications,'checks':checks,'errors':errors,
        'checked_components':['Newly staged additions explicitly checked beyond earlier tracked-diff scope',
            'Independently regenerated complete warning output equals archived actual command output',
            'Every warning checked against its actual indexed line; all 157038 CSV/10220 SVG/20 patch/11 log warnings classified',
            'All 1049 actual index blobs independently read and hashed to the frozen manifest; no newline conversion/data substitution',
            'No Python/Markdown/TeX authored source warning, no original ZIP staging, no Git configuration change or artifact normalization'],
        'new_method_runs':0,'new_model_calls':0,'artifact_bytes_changed':False,'git_configuration_changed':False,
        'repair_or_method_rerun_required':bool(errors),'may_proceed_with_authorized_commit':not errors,
        'unchecked_components':['Actual commit/push/remote readback remains the subsequent publication gate'],
        'actual_command':'.venv/bin/python '+str(Path(__file__).relative_to(ROOT))}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'warnings':sum(kinds.values()),'files':len(warnings),
        'actual_index_blobs':len(manifest['files']),'actual_index_bytes':index_total,'checks':len(checks),
        'errors':errors,'receipt':file_ref(output)},ensure_ascii=False))


if __name__=='__main__':main()
