"""Build a closed, hash-checked REVIEW_ONLY package without modifying evidence.

Only exact runtime bindings are followed. Historical provenance links do not
recursively pull large archived traces into an offline recomputation package.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
EV = 'task1/evidence/goal3/'
G2 = 'task1/evidence/goal2/'
NOTEBOOKS = ['task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb',
             'task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb']
REPORTS = ['task1/reports/experiment1/experiment1.pdf',
           'task1/reports/process1/process1.pdf']
G2_FIGURES = ['segmentation_filter_grids', 'direction_threshold_and_neighborhood',
              'dp_error_compression', 'order_protection_and_neighborhoods',
              'synthetic_metric_counterexamples', 'goal2_actual_architecture',
              'four_mode_paired_results', 'four_mode_failures_and_cost',
              'memory_coverage_and_consumption']
G3_FIGURES = ['development_candidates', 'point_fates_and_coverage',
              'final_confirmation_pairs', 'production_trajectory_cases',
              'goal3_actual_workflow', 'incumbent_decision_path', 'selection_tradeoffs']
EXCLUSIONS = [
    {'paths': '.git; .venv; caches; build directories', 'reason': 'local state, not reproducible inputs'},
    {'paths': 'G2 historical run manifests/traces; G3 production traces',
     'reason': 'raw is recomputed; compact registry preserves genuine proposals, source-manifest hashes and target hashes; production manifest is included'},
    {'paths': 'font binaries; paper full texts', 'reason': 'not necessary inputs; no new redistribution'},
    {'paths': 'unrelated root ZIPs; account/auth files', 'reason': 'outside the teacher package dependency closure'},
    {'paths': 'LaTeX sources; editable figure sources; complete historical evidence; teacher originals',
     'reason': 'preserved in full GitHub project; package supplies completed Notebook/PDF and actual runtime inputs'}]
FORBIDDEN_PARTS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', '.ipynb_checkpoints',
                   'node_modules', '.ssh', '.codex', '.config'}
FORBIDDEN_SUFFIXES = {'.pyc', '.pyo', '.ttf', '.otf', '.woff', '.woff2', '.pem', '.key', '.zip'}
PERSONAL_PATH = re.compile(r'(?:/' + r'home/[^/\s"<>]+/|/' + r'Users/[^/\s"<>]+/|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/])')
SECRET_PATTERNS = [re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                   re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
                   re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
                   re.compile(r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def relative_path(value):
    if not isinstance(value, str) or '\\' in value:
        raise ValueError('INVALID_PACKAGE_PATH')
    path = PurePosixPath(value)
    if path.is_absolute() or ':' in value or str(path) != value or any(p in ('', '.', '..') for p in path.parts):
        raise ValueError('UNSAFE_PACKAGE_PATH:' + value)
    if any(p in FORBIDDEN_PARTS or p.startswith('.env') for p in path.parts) or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise ValueError('EXCLUDED_PACKAGE_PATH:' + value)
    return path


def read_json(root, path):
    return json.loads((root / path).read_text(encoding='utf8'))


def content_issues(path, data):
    """Report categories/paths only, never emit a potential secret value."""
    if path.endswith('.json.gz'):
        data = gzip.decompress(data)
    if path.endswith('.pdf'):
        result = subprocess.run(['pdftotext', '-', '-'], input=data, capture_output=True, timeout=30)
        if result.returncode:
            return ['PDF_TEXT_EXTRACTION_FAILED']
        data = result.stdout
    if Path(path).suffix.lower() in {'.png', '.svg'}:
        return []
    try:
        text = data.decode('utf8')
    except UnicodeDecodeError:
        return ['UNEXPECTED_BINARY']
    issues = []
    if PERSONAL_PATH.search(text):
        issues.append('PERSONAL_ABSOLUTE_PATH')
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        issues.append('POSSIBLE_SECRET')
    return issues


def closure(root=ROOT):
    root = Path(root).resolve()
    reasons, required_hashes, missing, errors = {}, {}, set(), []

    def add(path, reason, expected=None):
        relative_path(path)
        reasons.setdefault(path, set()).add(reason)
        if expected:
            if path in required_hashes and required_hashes[path] != expected:
                errors.append({'path': path, 'error': 'CONFLICTING_FROZEN_HASHES'})
            required_hashes[path] = expected
        target = root / path
        if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != root.parent):
            raise ValueError('SYMLINK_INPUT_REJECTED:' + path)
        if not target.is_file():
            missing.add(path)

    def bindings(mapping, origin):
        if not isinstance(mapping, dict):
            raise ValueError('BINDINGS_MUST_BE_MAP:' + origin)
        for path, expected in mapping.items():
            if not re.fullmatch('[0-9a-f]{64}', str(expected)):
                raise ValueError('INVALID_BINDING_HASH:' + origin)
            add(path, 'exact binding from ' + origin, expected)

    def load(path):
        return read_json(root, path) if (root/path).is_file() else None

    static = NOTEBOOKS + REPORTS + [
        'task1/作业/作业/traj_dict.json', 'task1/config/conditional_planar.json',
        'task1/config/goal1.json', 'task1/config/goal2/contract.json',
        'task1/config/goal2/experiment_matrix.json', 'task1/config/goal3/contract.json',
        'task1/scripts/goal2.py', 'templates/latex/common/p2_cloud_sorbet_colors.tex',
        G2+'result_summary.json', G2+'a_epoch02/actual_ai_critique/actual_ai_critique.json',
        G2+'counterexamples/formal-02/synthetic_cases.json', G2+'tables/memory_consumption.csv',
        EV+'historical_recompute_registry_binding.json', EV+'historical_recompute_registry.json.gz',
        EV+'a_candidate_plan.json', EV+'split_manifest.json', EV+'current_runs.json',
        EV+'contract_freeze.json', EV+'implementation_freeze.json', EV+'selection_freeze.json',
        EV+'final_freeze.json', EV+'production_freeze.json']
    static += ['task1/goal3/'+name+'.py' for name in
               ('__init__', '__main__', 'data', 'runtime', 'selection', 'control', 'reproduce', 'offline_plots', 'package')]
    static += [str(p.relative_to(root)) for p in sorted((root/'task1/workflow').glob('*.py'))]
    static += ['task1/figures/goal2/'+n+'.png' for n in G2_FIGURES]
    static += ['task1/figures/goal3/'+n+'.png' for n in G3_FIGURES]
    for path in static:
        add(path, 'offline Notebook/FULL_RECOMPUTE input or review deliverable')

    contract = load('task1/config/conditional_planar.json')
    if contract:
        approval = contract['approval_source']
        add(approval['path'], 'conditional coordinate authorization', approval['sha256'])
        decisions = load(approval['path'])
        if decisions:
            add(decisions['D1']['source'], 'conditional authorization original supplement', decisions['D1']['sha256'])
    plan = load(EV+'a_candidate_plan.json')
    if plan:
        bindings(plan['evidence_sha256'], EV+'a_candidate_plan.json')
    stage = load(G2+'result_summary.json')
    if stage:
        add(stage['memory']['snapshot_path'], 'Notebook frozen read-only memory', stage['memory']['snapshot_sha256'])
    historical = load(EV+'historical_recompute_registry_binding.json')
    if historical:
        add(historical['path'], 'compact genuine historical proposals and raw target hashes', historical['sha256'])
        if (root/historical['path']).is_file():
            with gzip.open(root/historical['path'], 'rt', encoding='utf8') as stream:
                registry = json.load(stream)
            bindings(registry['bindings'], 'historical recompute registry')
            # source_registry is preserved inside this exact compact registry.
            # Its original manifests are provenance references, not read inputs;
            # they also contain historical machine-specific executable paths.

    # These maps are actually checked by the execution gate. Do not follow every
    # provenance string in arbitrary JSON: that would pull all historical traces.
    processed = set()
    while True:
        todo = [p for p in reasons if p.startswith(EV) and p.endswith('_freeze.json') and p not in processed]
        if not todo:
            break
        for path in todo:
            processed.add(path)
            value = load(path)
            if value:
                bindings(value.get('bindings', {}), path)
                if path == EV+'production_freeze.json':
                    bindings(value['processing_source_hashes'], path+' processing_source_hashes')
                    if not re.fullmatch('[0-9a-f]{40}', value.get('processing_code_sha', '')):
                        errors.append({'path': path, 'error': 'INVALID_PROCESSING_CODE_SHA'})

    current = load(EV+'current_runs.json')
    if current:
        production_id = current.get('production')
        if not isinstance(production_id, str):
            errors.append({'path': EV+'current_runs.json', 'error': 'PRODUCTION_RUN_ID_REQUIRED'})
        for role, run_id in current.items():
            if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', run_id):
                continue
            base = EV+'runs/'+run_id+'/'
            manifest_path = base+'manifest.json'
            if not (root/manifest_path).is_file() and role != 'production':
                continue
            add(manifest_path, 'current '+role+' run manifest, no trace duplication')
            value = load(manifest_path)
            if value and value.get('partition') in ('FINAL_CONFIRM', 'FULL_PRODUCTION'):
                add(base+'paired_summary.json', 'current '+value['partition']+' paired summary')
                add(base+'analysis/summary.json', 'current '+value['partition']+' analysis summary')

    payload, members = {}, []
    for path in sorted(reasons):
        if path in missing:
            continue
        source = (root/path).read_bytes()
        source_hash = sha(source)
        if path in required_hashes and source_hash != required_hashes[path]:
            errors.append({'path': path, 'error': 'FROZEN_HASH_MISMATCH',
                           'expected': required_hashes[path], 'actual': source_hash})
        data, transformations = source, []
        if path == G2+'result_summary.json':
            value = json.loads(source)
            # Only this exact historical metadata field is authorized for a
            # package-only path change; never recursively rewrite results.
            command = value.get('actual_command')
            if isinstance(command, list) and command and isinstance(command[0], str) and PERSONAL_PATH.search(command[0]):
                prefix, marker, suffix = command[0].partition('/task1/')
                if not marker or suffix != 'scripts/build_goal2_analysis.py' or path in required_hashes:
                    raise ValueError('UNAPPROVED_METADATA_TRANSFORMATION:' + path)
                command[0] = 'task1/'+suffix
                transformations = [{'field': 'actual_command[0]',
                    'operation': 'replace workspace-specific prefix with project-relative path',
                    'original_value_sha256': sha((prefix+marker+suffix).encode()), 'new_value': command[0]}]
                value['_package_provenance'] = {'source_path': path, 'source_sha256': source_hash,
                    'classification': 'PACKAGE_METADATA_ONLY_DERIVATIVE', 'transformations': transformations,
                    'numeric_results_and_proposals_changed': False}
                data = json_bytes(value)
        issues = content_issues(path, data)
        errors.extend({'path': path, 'error': issue} for issue in issues)
        if path.endswith('.pdf') and not data.startswith(b'%PDF-'):
            errors.append({'path': path, 'error': 'INVALID_PDF_HEADER'})
        payload[path] = data
        members.append({'path': path, 'bytes': len(data), 'source_sha256': source_hash,
                        'archive_sha256': sha(data), 'reasons': sorted(reasons[path]),
                        'transformations': transformations})
    for source, destination in [('task1/goal3/PACKAGE_README.md', 'README.md'),
                                ('task1/goal3/requirements-recompute.txt', 'requirements.txt')]:
        data = (root/source).read_bytes()
        errors.extend({'path': source, 'error': e} for e in content_issues(source, data))
        payload[destination] = data
        members.append({'path': destination, 'bytes': len(data), 'source_path': source,
                        'source_sha256': sha(data), 'archive_sha256': sha(data),
                        'reasons': ['portable package instructions/dependencies'], 'transformations': []})
    result = {'status': 'STATIC_CLOSURE_COMPLETE' if not missing and not errors else 'NOT_READY',
              'package_status': 'REVIEW_ONLY', 'submission_status': 'NOT_SUBMITTED',
              'member_count': len(members), 'total_uncompressed_bytes': sum(m['bytes'] for m in members),
              'members': sorted(members, key=lambda m: m['path']), 'missing': sorted(missing),
              'errors': errors, 'exclusions': EXCLUSIONS,
              'runtime_scope': 'offline FULL_RECOMPUTE and two completed Notebooks; no LIVE or REPORT_BUILD dependency claim',
              'isolated_full_recompute': 'NOT_RUN_BY_BUILDER', 'new_model_calls': 0,
              'metadata': {'student_name': 'NOT_AVAILABLE', 'student_id': 'NOT_AVAILABLE',
                           'evidence_master_spec_and_lock': 'NOT_AVAILABLE'}}
    return result, payload


def verify_directory(directory):
    directory = Path(directory).resolve()
    if (directory/'PACKAGE_MANIFEST.json').is_symlink():
        raise ValueError('SYMLINK_PACKAGE_MANIFEST')
    manifest = read_json(directory, 'PACKAGE_MANIFEST.json')
    seen = set()
    for item in manifest['members']:
        path = item['path']; relative_path(path)
        if path in seen:
            raise ValueError('DUPLICATE_MANIFEST_MEMBER:' + path)
        seen.add(path)
        target = directory/path
        if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != directory.parent):
            raise ValueError('SYMLINK_PACKAGE_MEMBER:' + path)
        data = target.read_bytes()
        if len(data) != item['bytes'] or sha(data) != item['archive_sha256']:
            raise ValueError('PACKAGE_FILE_HASH_MISMATCH:' + path)
    return {'status': 'VERIFIED', 'verified_members': len(seen),
            'scope': 'declared original package files; new recomputation outputs may coexist',
            'full_recompute': 'NOT_EXECUTED_BY_THIS_CHECK'}


def static_probe(payload):
    """Exercise imports and exact gate dependencies, with no trajectory run."""
    code = r'''
import gzip, json, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root))
from task1.workflow.io import ROOT, read_json
from task1.workflow.coordinates import registration
from task1.workflow.g2_journal import source_snapshot
from task1.workflow.g2_provider import ExperimentProvider
from task1.workflow.provider import CodexProvider
from task1.goal3 import reproduce, offline_plots
from task1.goal3.runtime import definitions, assert_binding, execution_gate, code_identity, source_snapshot as g3_sources
assert ROOT==root and not (root/'.git').exists()
def forbidden(*args,**kwargs): raise AssertionError('UNEXPECTED_MODEL_CALL')
ExperimentProvider.call=forbidden; CodexProvider.call=forbidden
registration(); registered=definitions()
frozen=read_json(root/'task1/evidence/goal3/contract_freeze.json'); assert_binding(frozen['bindings'])
with gzip.open(root/'task1/evidence/goal3/historical_recompute_registry.json.gz','rt',encoding='utf8') as f: registry=json.load(f)
assert_binding(registry['bindings']); assert source_snapshot()==registry['processing_bindings']
production=root/'task1/evidence/goal3/production_freeze.json'
gate='PENDING_PRODUCTION_FREEZE'
if production.exists():
    frozen=read_json(production)
    execution_gate('FULL_PRODUCTION',frozen['input_ids'],frozen['strategy_ids'])
    code_identity(g3_sources(),'FULL_PRODUCTION',True); gate='VERIFIED'
print(json.dumps({'status':'VERIFIED','root_is_isolated':True,'git_present':False,'new_model_calls':0,
 'historical_binding_check':'VERIFIED','contract_and_A_plan_check':'VERIFIED','production_gate':gate,
 'trajectory_runs':0,'registered_strategy_count':len(registered)}))
'''
    with tempfile.TemporaryDirectory(prefix='g3-package-closure-') as work:
        directory = Path(work)
        for path, data in payload.items():
            target = directory/path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        result = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(directory)],
                                cwd=directory, capture_output=True, text=True, timeout=60)
        if result.returncode:
            # Strip transient locations; errors are engineering evidence, not
            # hidden fallback to imports from the source workspace.
            cleaned = result.stderr.replace(str(directory), '<isolated-package>')
            return {'status': 'FAILED', 'returncode': result.returncode, 'stderr': cleaned[-10000:]}
        return json.loads(result.stdout.splitlines()[-1])


def build(output, report, payload):
    if report['status'] != 'STATIC_CLOSURE_COMPLETE':
        raise ValueError('PACKAGE_INPUTS_NOT_READY; inspect source_closure.json')
    output = Path(output)
    if not output.name.startswith('REVIEW_ONLY_') or output.suffix != '.zip':
        raise ValueError('REVIEW_ONLY_FILENAME_REQUIRED')
    if output.exists():
        raise ValueError('REFUSE_TO_OVERWRITE_EXISTING_ZIP')
    output.parent.mkdir(parents=True, exist_ok=True)
    archive_manifest = {**report, 'built_at': datetime.now(timezone.utc).isoformat(),
                        'manifest_self_hash': 'intentionally omitted to avoid self-reference'}
    contents = {**payload, 'PACKAGE_MANIFEST.json': json_bytes(archive_manifest)}
    temporary = output.with_suffix('.zip.tmp')
    if temporary.exists():
        raise ValueError('PACKAGE_TEMP_EXISTS')
    try:
        with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in sorted(contents):
                relative_path(path)
                info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, contents[path])
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None or sorted(archive.namelist()) != sorted(contents):
                raise ValueError('ZIP_MEMBER_OR_CRC_CHECK_FAILED')
            for path, data in contents.items():
                if sha(archive.read(path)) != sha(data):
                    raise ValueError('ZIP_ARCHIVE_HASH_MISMATCH:' + path)
        os.replace(temporary, output)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
    return {'status': 'REVIEW_ONLY', 'zip_name': output.name, 'zip_sha256': sha(output.read_bytes()),
            'zip_bytes': output.stat().st_size, 'members_including_manifest': len(contents),
            'archive_crc_and_sha256': 'VERIFIED', 'isolated_full_recompute': 'NOT_RUN_BY_BUILDER',
            'submission_status': 'NOT_SUBMITTED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='actual closure/hash/safety check; no ZIP')
    mode.add_argument('--build', type=Path, metavar='REVIEW_ONLY_NAME.zip')
    mode.add_argument('--verify-dir', type=Path, help='verify an already extracted package')
    parser.add_argument('--probe', action='store_true', help='isolated no-Git imports/bindings; no method runs')
    parser.add_argument('--receipt', type=Path, default=ROOT/EV/'package/source_closure.json')
    args = parser.parse_args()
    if args.verify_dir:
        print(json.dumps(verify_directory(args.verify_dir), ensure_ascii=False, indent=2)); return
    report, payload = closure()
    if args.probe or args.build:
        report['isolated_static_probe'] = static_probe(payload)
        if report['isolated_static_probe']['status'] != 'VERIFIED':
            report['status'] = 'NOT_READY'
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(json_bytes(report))
    if args.build:
        receipt = build(args.build, report, payload)
        args.receipt.with_name('package_build_receipt.json').write_bytes(json_bytes(receipt))
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({k: report[k] for k in ('status', 'member_count', 'total_uncompressed_bytes', 'missing', 'errors')},
                         ensure_ascii=False, indent=2))
        if args.probe:
            print(json.dumps(report['isolated_static_probe'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
