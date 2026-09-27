"""Independently verify the actual REVIEW_ONLY ZIP; does not run FULL."""
import ast
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
ZIP = 'task1/submission/REVIEW_ONLY_实验一.zip'
EXPECTED = '97d5dbe2d7a5c87d09bcb21ae5798fa0b76374fabdd03f25447fb87c4f27c447'
CHECKS = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(name, actual, expected=True):
    CHECKS.append({'name': name, 'actual': actual, 'expected': expected, 'passed': actual == expected})


def main():
    zip_bytes = (ROOT / ZIP).read_bytes()
    check('actual ZIP pinned identity', sha(zip_bytes), EXPECTED)
    check('actual ZIP size', len(zip_bytes), 21418989)
    prohibited_parts = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
                        '.ipynb_checkpoints', 'node_modules', '.ssh', '.codex', '.config', 'build'}
    prohibited_ext = {'.ttf', '.otf', '.woff', '.woff2', '.pyc', '.pyo', '.pem', '.key', '.zip'}
    private_path = re.compile(r'/(?:home|Users)/[^/\s"<>]+/|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/]')
    actual_secret = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b|\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b')
    scan = []
    with ZipFile(ROOT / ZIP) as archive:
        names = archive.namelist()
        check('archive CRC test', archive.testzip(), None)
        check('no duplicate ZIP names', len(names), len(set(names)))
        check('113 actual ZIP members', len(names), 113)
        payload = {name: archive.read(name) for name in names}
        manifest = json.loads(payload['PACKAGE_MANIFEST.json'])
        listed = {x['path']: x for x in manifest['members']}
        check('112 exact declared files plus manifest', set(names), set(listed) | {'PACKAGE_MANIFEST.json'})
        # Keep sets serializable without hiding the actual membership check.
        CHECKS[-1]['actual'] = sorted(names)
        CHECKS[-1]['expected'] = sorted(set(listed) | {'PACKAGE_MANIFEST.json'})
        check('review-only manifest', manifest['package_status'], 'REVIEW_ONLY')
        check('no submitted claim', manifest['submission_status'], 'NOT_SUBMITTED')
        check('metadata absent honestly', manifest['metadata'],
              {'student_name': 'NOT_AVAILABLE', 'student_id': 'NOT_AVAILABLE', 'evidence_master_spec_and_lock': 'NOT_AVAILABLE'})
        check('builder not claiming FULL', manifest['isolated_full_recompute'], 'NOT_RUN_BY_BUILDER')
        check('actual uncompressed total', sum(len(payload[p]) for p in listed), manifest['total_uncompressed_bytes'])
        transformations = []
        for info in archive.infolist():
            rel = info.filename; p = PurePosixPath(rel)
            check(rel + ': relative safe file name', not p.is_absolute() and '..' not in p.parts and '\\' not in rel and ':' not in rel)
            check(rel + ': no excluded directory', not any(x in prohibited_parts or x.startswith('.env') for x in p.parts))
            check(rel + ': no excluded binary/font/cache/archive', p.suffix.lower() not in prohibited_ext)
            check(rel + ': regular file not symbolic link', stat.S_ISREG(info.external_attr >> 16))
            data = payload[rel]
            if rel in listed:
                row = listed[rel]
                check(rel + ': actual member bytes', len(data), row['bytes'])
                check(rel + ': declared archive hash', sha(data), row['archive_sha256'])
                original = (ROOT / row.get('source_path', rel)).read_bytes()
                check(rel + ': actual source hash', sha(original), row['source_sha256'])
                if not row['transformations']:
                    check(rel + ': exact original bytes', sha(data), sha(original))
                else:
                    transformations.append(rel)
                    check(rel + ': only approved derivative', rel, 'task1/evidence/goal2/result_summary.json')
                    before, after = json.loads(original), json.loads(data)
                    provenance = after.pop('_package_provenance')
                    check(rel + ': original hash retained', provenance['source_sha256'], sha(original))
                    check(rel + ': only command field transformation',
                          [x['field'] for x in row['transformations']], ['actual_command[0]'])
                    check(rel + ': relative command value', after['actual_command'][0], 'task1/scripts/build_goal2_analysis.py')
                    after['actual_command'][0] = before['actual_command'][0]
                    check(rel + ': every other original JSON value unchanged', after, before)
                    CHECKS[-1]['actual'] = sha(json.dumps(after, ensure_ascii=False, sort_keys=True).encode())
                    CHECKS[-1]['expected'] = sha(json.dumps(before, ensure_ascii=False, sort_keys=True).encode())
            if rel.endswith('.png'):
                scan.append({'path': rel, 'scope': 'native figure raster; filename/member checks only'})
                continue
            if rel.endswith('.pdf'):
                data = subprocess.run(['pdftotext', '-', '-'], input=data, capture_output=True, check=True).stdout
            if rel.endswith('.json.gz'):
                data = gzip.decompress(data)
            text = data.decode('utf8')
            check(rel + ': no personal absolute paths in source/output/PDF text', private_path.search(text) is None)
            check(rel + ': no actual credential/private-key pattern', actual_secret.search(text) is None)
            scan.append({'path': rel, 'bytes_scanned': len(data), 'scope': 'complete decoded JSON/source/notebook outputs or extracted PDF text'})
            if rel.endswith('.py'):
                ast.parse(text)
                check(rel + ': actual Python AST parses', True)
        check('exactly one documented metadata-only derivative', transformations, ['task1/evidence/goal2/result_summary.json'])
        check('only the two required report PDFs', sorted(p for p in names if p.endswith('.pdf')),
              ['task1/reports/experiment1/experiment1.pdf', 'task1/reports/process1/process1.pdf'])
        raw_rel = 'task1/作业/作业/traj_dict.json'
        check('original raw exact SHA256', sha(payload[raw_rel]), 'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3')
        raw = json.loads(payload[raw_rel])
        check('actual raw records present', len(raw), 11386)
        check('actual raw schema preserves paired time/coordinate arrays',
              all(isinstance(v, list) and len(v) == 2 and len(v[0]) == len(v[1]) for v in raw.values()))
        check('actual raw points present', sum(len(v[0]) for v in raw.values()), 1173410)
        for rel in [p for p in names if p.endswith('.ipynb')]:
            notebook = json.loads(payload[rel])
            code = [c for c in notebook['cells'] if c['cell_type'] == 'code']
            check(rel + ': source and executed outputs exact current canonical bytes', sha(payload[rel]), sha((ROOT / rel).read_bytes()))
            check(rel + ': saved code outputs not unexecuted', all(c.get('execution_count') is not None for c in code))
            check(rel + ': saved outputs contain no error objects',
                  not any(o.get('output_type') == 'error' for c in code for o in c.get('outputs', [])))
            body = '\n'.join(''.join(c['source']) for c in notebook['cells'])
            check(rel + ': exact FULL default and offline disable', "MODE = 'FULL_RECOMPUTE'" in body and 'ENABLE_LIVE = False' in body)
            check(rel + ': both registered providers guarded',
                  'ExperimentProvider.call = forbid_provider' in body and 'CodexProvider.call = forbid_provider' in body)
        def exact_bindings(label, mapping):
            for rel, h in mapping.items():
                check(label + ': bound dependency is present:' + rel, rel in payload)
                if rel in payload: check(label + ': bound dependency actual bytes:' + rel, sha(payload[rel]), h)
        registry = json.loads(gzip.decompress(payload[EV + 'historical_recompute_registry.json.gz']))
        exact_bindings('historical executable binding', registry['bindings'])
        exact_bindings('historical source identity', registry['processing_bindings'])
        frozen = json.loads(payload[EV + 'production_freeze.json'])
        exact_bindings('production executable binding', frozen['bindings'])
        exact_bindings('production source identity without Git', frozen['processing_source_hashes'])
        for rel in names:
            if rel.startswith(EV) and rel.endswith('_freeze.json'):
                exact_bindings(rel, json.loads(payload[rel]).get('bindings', {}))

    # Independently unpack the actual ZIP (not the builder payload), use the same
    # installed interpreter but prevent imports from the original workspace.
    probe_code = r'''
import gzip,json,socket,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
def forbidden(*a,**k):raise RuntimeError('INDEPENDENT_STATIC_PROBE_DISALLOWS_NETWORK_OR_MODEL')
socket.create_connection=forbidden
from task1.workflow.io import ROOT,read_json
from task1.workflow.g2_provider import ExperimentProvider
from task1.workflow.provider import CodexProvider
ExperimentProvider.call=forbidden;CodexProvider.call=forbidden
from task1.workflow.g2_journal import source_snapshot
from task1.workflow.coordinates import registration
from task1.goal3 import reproduce,offline_plots
from task1.goal3.runtime import definitions,assert_binding,execution_gate,code_identity,source_snapshot as new_snapshot
assert ROOT==root and not (root/'.git').exists()
registration(); plan=definitions()
with gzip.open(root/'task1/evidence/goal3/historical_recompute_registry.json.gz','rt') as f: registry=json.load(f)
assert_binding(registry['bindings']);assert source_snapshot()==registry['processing_bindings']
frozen=read_json(root/'task1/evidence/goal3/production_freeze.json')
execution_gate('FULL_PRODUCTION',frozen['input_ids'],frozen['strategy_ids'])
code_identity(new_snapshot(),'FULL_PRODUCTION',True)
print(json.dumps({'status':'VERIFIED','project_modules_from_fresh_actual_zip':ROOT==root,
 'git_present':False,'frozen_full_scope_records':len(frozen['input_ids']),
 'registered_strategies':len(plan),'trajectory_processing_calls':0,'new_model_calls':0}))
'''
    with tempfile.TemporaryDirectory(prefix='c-actual-lab1-zip-') as temp:
        temp = Path(temp); extracted = temp / 'payload'; extracted.mkdir()
        with ZipFile(ROOT / ZIP) as archive: archive.extractall(extracted)
        check('independent actual ZIP no Git metadata', (extracted / '.git').exists(), False)
        for rel, data in payload.items():
            check('independent extracted bytes:' + rel, sha((extracted / rel).read_bytes()), sha(data))
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'MPLBACKEND': 'Agg',
               'MPLCONFIGDIR': str(temp / 'mpl'), 'IPYTHONDIR': str(temp / 'ipython'),
               'JUPYTER_CONFIG_DIR': str(temp / 'jupyter')}
        result = subprocess.run([sys.executable, '-I', '-B', '-c', probe_code, str(extracted)],
                                cwd=extracted, env=env, capture_output=True, text=True, timeout=60)
        check('independent actual-ZIP import/binding probe exit', result.returncode, 0)
        if result.returncode:
            probe = {'status': 'FAILED', 'stderr': result.stderr.replace(str(temp), '<independent-temporary-root>')[-3000:]}
        else:
            probe = json.loads(result.stdout.strip().splitlines()[-1])
        check('independent actual ZIP frozen full binding (no processing)', probe.get('status'), 'VERIFIED')
    errors = [c for c in CHECKS if not c['passed']]
    receipt = {'role_context': '/root/c_documents', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
               'status': 'VERIFIED_ACTUAL_ZIP_STATIC_CLOSURE_PENDING_FULL' if not errors else 'REPAIR_REQUIRED',
               'targets': [{'path': ZIP, 'sha256': EXPECTED}],
               'checks': CHECKS, 'errors': errors, 'scan_scope': scan, 'independent_fresh_zip_probe': probe,
               'checked_components': ['actual ZIP CRC and all 113 members', 'all 112 current source/archive identities',
                                      'two report PDFs and two executed Notebook files exact current bytes',
                                      'only recorded historical command-path metadata derivative; numeric values/proposals untouched',
                                      'all frozen executable dependency/source bindings and original complete raw range',
                                      'complete textual outputs/metadata scanned; no personal absolute paths or credential matches',
                                      'no virtualenv/Git/cache/auth/fonts/full-paper PDFs/unrelated ZIPs',
                                      'independent extraction from real ZIP into new no-Git root, module imports/frozen gates verified without processing'],
               'unchecked_components': ['full isolated Notebook computations already running in separate kernels',
                                        'final parent acceptance and remote GitHub publication',
                                        'missing identity/Evidence Master inputs and external GPT review'],
               'package_status': 'REVIEW_ONLY', 'submission_status': 'NOT_READY_NOT_SUBMITTED',
               'new_method_runs': 0, 'new_model_calls': 0, 'parent_task_closed': False,
               'actual_command': '.venv/bin/python task1/evidence/goal3/independent_documents/review_actual_zip.py',
               'checker_sha256': sha(Path(__file__).read_bytes())}
    (OUT / 'actual_zip_static_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'checks': len(CHECKS), 'errors': errors,
                      'zip_sha256': EXPECTED, 'isolated_probe': probe}, ensure_ascii=False))


if __name__ == '__main__':
    main()
