"""Independent delivery-boundary checks; no production trajectories are run.

All deliberate mutations below affect in-memory/synthetic fixtures only. The
canonical source, raw data, frozen evidence and Notebook files are read-only.
"""
import ast
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from unittest.mock import patch

import nbformat

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from task1.goal3 import __main__ as entry
from task1.goal3 import package, reproduce, offline_plots
from task1.workflow.g2_provider import ExperimentProvider
from task1.workflow.provider import CodexProvider

FILES = [
    'task1/goal3/reproduce.py', 'task1/goal3/offline_plots.py',
    'task1/goal3/notebooks.py', 'task1/goal3/execute_notebook.py',
    'task1/goal3/package.py', 'task1/goal3/__main__.py',
    'task1/goal3/PACKAGE_README.md', 'task1/goal3/requirements-recompute.txt',
    *package.NOTEBOOKS,
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = {path: digest(ROOT/path) for path in FILES}
    checks = []

    def check(name, success, scope=None):
        checks.append({'check': name, 'passed': bool(success), 'scope': scope})
        if not success:
            raise AssertionError(name)

    def rejects(name, func, message):
        try:
            func()
        except (ValueError, RuntimeError) as exc:
            check(name, message in str(exc), str(exc))
        else:
            check(name, False, 'unexpectedly accepted')

    for relative in FILES:
        if relative.endswith('.py'):
            ast.parse((ROOT/relative).read_text(), filename=relative)
            check('python_ast:'+relative, True)

    notebook_counts = {}
    for relative in package.NOTEBOOKS:
        notebook = nbformat.read(ROOT/relative, as_version=4)
        nbformat.validate(notebook)
        code = [c for c in notebook.cells if c.cell_type == 'code']
        for i, cell in enumerate(code):
            compile(cell.source, relative+':code'+str(i), 'exec')
        check('notebook_schema_and_all_code_compile:'+relative, True)
        check('notebook_is_unexecuted_source:'+relative,
              all(c.execution_count is None and not c.outputs for c in code))
        check('no_personal_path_or_secret_in_source_notebook:'+relative,
              package.content_issues(relative, (ROOT/relative).read_bytes()) == [])
        notebook_counts[relative] = {'code_cells': len(code), 'execution_status': 'NOT_RUN_BY_THIS_REVIEW'}

    report, payload = package.closure(ROOT)
    check('actual_closure_has_no_safety_or_frozen_hash_errors', report['errors'] == [])
    check('pending_inputs_are_explicit_not_fabricated',
          report['status'] == ('NOT_READY' if report['missing'] else 'STATIC_CLOSURE_COMPLETE'))
    for path in payload:
        parsed = Path(path)
        check('allowlist_path:'+path,
              not parsed.is_absolute() and '..' not in parsed.parts
              and not any(part in package.FORBIDDEN_PARTS for part in parsed.parts)
              and parsed.suffix.lower() not in package.FORBIDDEN_SUFFIXES)
    by_path = {item['path']: item for item in report['members']}
    transformed = [path for path, item in by_path.items() if item['transformations']]
    check('only_designated_historical_metadata_is_transformed',
          transformed == ['task1/evidence/goal2/result_summary.json'])
    path = transformed[0]
    before = json.loads((ROOT/path).read_bytes())
    after = json.loads(payload[path]); provenance = after.pop('_package_provenance')
    after['actual_command'][0] = before['actual_command'][0]
    check('all_historical_numbers_and_proposals_byte_values_unchanged', before == after)
    check('metadata_derivative_binds_original_hash',
          provenance['source_sha256'] == digest(ROOT/path))
    for path, item in by_path.items():
        if path in transformed:
            continue
        source = ROOT/item.get('source_path', path)
        check('unchanged_archive_input:'+path, payload[path] == source.read_bytes())

    raw_bytes = payload['task1/作业/作业/traj_dict.json']
    raw = json.loads(raw_bytes)
    check('actual_raw_sha256', hashlib.sha256(raw_bytes).hexdigest() ==
          'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3')
    check('raw_time_coordinate_arrays_aligned',
          all(len(record) == 2 and len(record[0]) == len(record[1]) for record in raw.values()))
    counts = {'records': len(raw), 'points': sum(len(record[0]) for record in raw.values())}
    check('actual_raw_full_structure_counts', counts == {'records': 11386, 'points': 1173410})

    isolated = package.static_probe(payload)
    check('actual_isolated_no_git_gate', isolated.get('status') == 'VERIFIED'
          and isolated.get('root_is_isolated') is True and isolated.get('git_present') is False
          and isolated.get('production_gate') == 'VERIFIED'
          and isolated.get('trajectory_runs') == isolated.get('new_model_calls') == 0)
    mutated = dict(payload)
    mutation_target = 'task1/workflow/g2_pipeline.py'
    mutated[mutation_target] += b'\n# SYNTHETIC_INDEPENDENT_FROZEN_SOURCE_MUTATION\n'
    rejected = package.static_probe(mutated)
    check('isolated_changed_frozen_source_is_rejected', rejected.get('status') == 'FAILED'
          and 'SOURCE_OR_CONTRACT_CHANGED_NEW_RUN_REQUIRED' in rejected.get('stderr', ''))

    # A fixture representing a successful executed notebook leaking a cwd must
    # be rejected by the exact packaging scanner. No real path is emitted.
    unsafe_notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('print("fixture")')])
    unsafe_notebook.cells[0].outputs = [nbformat.v4.new_output(
        'stream', name='stdout', text='/'+'home/synthetic-user/private-workspace\n')]
    check('executed_notebook_stdout_path_is_rejected', 'PERSONAL_ABSOLUTE_PATH' in
          package.content_issues('fixture.ipynb', nbformat.writes(unsafe_notebook).encode()))
    compressed = gzip.compress(json.dumps({'synthetic': 'ghp_'+'A'*36}).encode())
    check('compressed_registry_secret_is_rejected', 'POSSIBLE_SECRET' in
          package.content_issues('fixture.json.gz', compressed))

    with tempfile.TemporaryDirectory(prefix='independent-delivery-boundary-', dir=HERE) as temp:
        temp = Path(temp)
        occupied = temp/'occupied'; occupied.mkdir(); marker = occupied/'user.txt'
        marker.write_text('SYNTHETIC_USER_FILE_PRESERVE')
        rejects('full_recompute_refuses_existing_output', lambda: entry.full_recompute(occupied),
                'NEW_OUTPUT_DIRECTORY_REQUIRED')
        check('existing_output_is_unchanged', marker.read_text() == 'SYNTHETIC_USER_FILE_PRESERVE')
        rejects('live_is_explicit_opt_in', lambda: entry.live('SYNTHETIC_NOT_RUN', False),
                'LIVE_REQUIRES_ENABLE_LIVE')
        rejects('not_ready_zip_is_not_written',
                lambda: package.build(temp/'REVIEW_ONLY_SYNTHETIC.zip', {'status':'NOT_READY'}, {}),
                'PACKAGE_INPUTS_NOT_READY')
        check('no_not_ready_archive_created', not (temp/'REVIEW_ONLY_SYNTHETIC.zip').exists())

        original = ExperimentProvider.call, CodexProvider.call
        attempted = []

        def deliberate_boundary_probe(*args, **kwargs):
            attempted.append('provider_method_invoked_under_offline_guard')
            ExperimentProvider.call(None)

        with patch.object(reproduce, 'recompute_historical', side_effect=deliberate_boundary_probe):
            rejects('actual_full_entry_blocks_provider_before_transport',
                    lambda: entry.full_recompute(temp/'guard_probe'),
                    'FULL_RECOMPUTE_FORBIDS_NEW_MODEL_CALLS')
        check('boundary_probe_ran_once', len(attempted) == 1)
        check('provider_methods_restored_after_failure',
              (ExperimentProvider.call, CodexProvider.call) == original)
        check('failed_boundary_probe_has_no_success_receipt',
              not (temp/'guard_probe/FULL_RECOMPUTE_RECEIPT.json').exists())

        for label, fixture, error in (
            ('running_production', {'recompute':True, 'status':'RUNNING', 'partition':'FULL_PRODUCTION'},
             'NEW_COMPLETED_RECOMPUTE_TRACES_REQUIRED'),
            ('archived_non_recomputed', {'recompute':False, 'status':'MACHINE_VERIFIED_PENDING_C', 'partition':'FULL_PRODUCTION'},
             'NEW_COMPLETED_RECOMPUTE_TRACES_REQUIRED'),
            ('undeclared_sample', {'recompute':True, 'status':'MACHINE_VERIFIED_PENDING_C', 'partition':'SAMPLE'},
             'UNREGISTERED_RECOMPUTE_PLOT_SCOPE')):
            folder = temp/label; folder.mkdir()
            (folder/'manifest.json').write_text(json.dumps(fixture))
            rejects('plot_gate:'+label, lambda folder=folder: offline_plots.production_plots(folder), error)
            check('no_figure_on_rejected_scope:'+label, not (folder/'figures').exists())

    end = {path: digest(ROOT/path) for path in FILES}
    changed = [path for path in FILES if start[path] != end[path]]
    receipt = {
        'role_context':'/root/c_documents', 'target_id':'portable_delivery_source_preflight',
        'status':'VERIFIED_WITHIN_CHECKED_SCOPE' if not changed else 'SOURCE_ADVANCED_DURING_REVIEW',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'classification':'SOURCE_AND_SYNTHETIC_BOUNDARY_REVIEW; no formal FULL production recomputation',
        'targets':[{'path':p, 'sha256':start[p]} for p in FILES],
        'sources_changed_during_review':changed, 'check_count':len(checks), 'checks':checks,
        'actual_closure_status':report['status'], 'actual_closure_member_count':report['member_count'],
        'missing_actual_inputs':report['missing'], 'actual_raw_structure':counts,
        'isolated_no_git_probe':isolated,
        'changed_source_probe':{'classification':'SYNTHETIC_IN_MEMORY_MUTATION_ONLY',
            'mutated_path':mutation_target, 'status':rejected['status'],
            'expected_rejection':'SOURCE_OR_CONTRACT_CHANGED_NEW_RUN_REQUIRED'},
        'notebooks':notebook_counts,
        'checked_components':[
            'raw -> adapt -> run_record -> trusted review -> exact trace and summary target comparisons in historical recomputation',
            'all actual registered historical tasks and original selected episode reconstruction remain distinct from new LIVE calls',
            'production default calls evaluate with all frozen FULL_PRODUCTION input IDs and no parent cache; new shard hashes/metrics are compared',
            'native new plot data flow uses recomputed metrics/new verified shards; archived figures remain explicitly labelled separately',
            'model tripwire at actual top-level offline entry; failure restores providers and does not emit a success receipt',
            'fresh output protection; no-.git isolated binding gate; changed frozen source refusal',
            'actual package allowlist, exact frozen bytes, narrowly documented historical metadata-only derivative, raw count/hash',
            'current Notebook schema/all code compilation and no secret/personal absolute path in unexecuted sources',
            'executed-Notebook stdout and compressed-registry synthetic leak rejection',
            'source executor preserves real outputs/errors; its internal absolute cwd/interpreter evidence is outside package allowlist',
        ],
        'unchecked_components':[
            'actual complete FULL_RECOMPUTE on completed production; RUNNING production was not rerun',
            'actual successful full Notebook outputs, cell counts, zero-model sentinel and post-execution path/secret scan',
            'actual final ZIP construction, fresh extraction and complete recomputation',
            'newly installed dependency environment; existing authorized Python environment was reused',
            'final report numbers, latest development/selection prose, final all-page >=200dpi visual review',
            'REPORT_BUILD package-producing repair; old entry missing ZIP step recorded separately',
        ],
        'trajectory_recomputations':0, 'new_model_transport_calls':0,
        'synthetic_blocked_model_entry_attempts':1,
        'installed_dependencies':[], 'actual_command':
            '.venv/bin/python task1/evidence/goal3/independent_documents/review_portable_sources.py',
        'review_harness_corrections':[
            'Explicit repository import path added after direct script import initially failed.',
            'Raw-count assertion corrected to count the aligned timestamp array in the actual [times, coordinates] record schema.',
            'Mutation assertion corrected to the observed declared runtime exception SOURCE_OR_CONTRACT_CHANGED_NEW_RUN_REQUIRED.',
        ],
    }
    (HERE/'portable_sources_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','check_count','actual_closure_status',
                    'actual_closure_member_count','trajectory_recomputations','new_model_transport_calls',
                    'synthetic_blocked_model_entry_attempts','sources_changed_during_review')},ensure_ascii=False))


if __name__ == '__main__':
    main()
