"""Explicit offline, report-build and opt-in live entry points for Experiment 1."""
import argparse
from pathlib import Path
import subprocess
import sys

from task1.workflow.io import ROOT, read_json, write_json, digest, now
from .data import EV


def full_recompute(output):
    from task1.workflow.g2_provider import ExperimentProvider
    from task1.workflow.provider import CodexProvider
    from .reproduce import recompute_historical, recompute_production
    if output.exists():
        raise ValueError('NEW_OUTPUT_DIRECTORY_REQUIRED')
    output.mkdir(parents=True)
    stage = read_json(ROOT/'task1/evidence/goal2/result_summary.json')
    memory = ROOT/stage['memory']['snapshot_path']
    original_hash = digest(memory); calls = []

    def forbidden(*args, **kwargs):
        calls.append(now())
        raise RuntimeError('FULL_RECOMPUTE_FORBIDS_NEW_MODEL_CALLS')

    original = ExperimentProvider.call, CodexProvider.call
    ExperimentProvider.call = CodexProvider.call = forbidden
    try:
        receipts = [recompute_historical('parameters', output/'parameters'),
                    recompute_historical('modes', output/'modes'),
                    recompute_production(output/'production')]
        if digest(memory) != original_hash or calls:
            raise ValueError('OFFLINE_MODEL_OR_READ_ONLY_MEMORY_BOUNDARY_FAILED')
        result = {'status': 'VERIFIED', 'mode': 'FULL_RECOMPUTE', 'new_model_calls': 0,
                  'memory_sha256_before': original_hash, 'memory_sha256_after': digest(memory),
                  'runs': receipts, 'at': now()}
        write_json(output/'FULL_RECOMPUTE_RECEIPT.json', result)
        return result
    finally:
        ExperimentProvider.call, CodexProvider.call = original


def live(run_id, enabled):
    """New G2 development episodes; never replace accepted experiment indexes."""
    if not enabled or not run_id or not (ROOT/'.git').exists():
        raise ValueError('LIVE_REQUIRES_ENABLE_LIVE_NEW_RUN_ID_AND_FULL_GIT_CHECKOUT')
    if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in run_id):
        raise ValueError('LIVE_RUN_ID_MUST_BE_A_SIMPLE_NAME')
    from task1.workflow.g2_experiments import ExperimentRun
    from task1.scripts.goal2 import run_modes
    old_index = ROOT/'task1/evidence/goal2/current_runs.json'
    old_hash = digest(old_index)
    run = ExperimentRun(run_id, 'DEVELOPMENT', classification='USER_REQUESTED_NEW_LIVE_DEVELOPMENT')
    run_modes(run, 1, enable_live=True)
    if digest(old_index) != old_hash:
        raise ValueError('ACCEPTED_HISTORICAL_INDEX_CHANGED')
    return {'mode': 'LIVE', 'status': run.manifest['status'], 'run_id': run_id,
            'accepted_results_replaced': False,
            'scope': 'historical development subset; new outputs are not a new final confirmation',
            'requests_and_cost': 'actual provider receipts; hidden backend requests and billing unknown'}


def report_build(output, evidence_output=None):
    """Compile the accepted Experiment source and package existing frozen inputs.

    Report integration does not reopen numerical production or regenerate the
    independently scoped Process draft. The package's read-only dependency
    probe still checks exact frozen inputs before publishing a new archive.
    """
    from .identity import read_identity
    target = output or ROOT/'task1/submission'/read_identity(ROOT)['review_package_name']
    if target.exists() or target.with_suffix('.zip.tmp').exists():
        raise ValueError('EXISTING_PACKAGE_PROTECTED; use --output with a new REVIEW_ONLY_*.zip path')
    if not target.name.startswith('REVIEW_ONLY_') or target.suffix != '.zip':
        raise ValueError('REPORT_BUILD_REQUIRES_REVIEW_ONLY_ZIP_FILENAME')
    if not (ROOT/'.git').exists() or not (ROOT/'task1/reports/build_reports.py').is_file():
        raise ValueError('REPORT_BUILD_REQUIRES_COMPLETE_REPOSITORY_AND_REPORT_SOURCES')
    evidence = evidence_output or ROOT/'task1/evidence/goal3/report_build/accepted'
    subprocess.run([sys.executable, str(ROOT/'task1/reports/build_reports.py'), '--render',
                    '--evidence-output', str(evidence)],
                   cwd=ROOT, check=True)
    subprocess.run([sys.executable, '-m', 'task1.goal3.package', '--build', str(target), '--probe',
                    '--receipt', str(evidence/'package/source_closure.json')],
                   cwd=ROOT, check=True)
    return {'status': 'REVIEW_ONLY_REBUILT', 'package_sha256': digest(target),
            'new_model_calls': 0, 'new_numerical_runs': 0, 'process_report_regenerated': False,
            'submission_status': 'NOT_READY', 'sent_to_teacher': False,
            'independent_review': 'REQUIRED; unchanged execution inputs may inherit specifically bound FULL evidence'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['FULL_RECOMPUTE', 'REPORT_BUILD', 'LIVE'])
    parser.add_argument('--output', type=Path, help='new recompute directory, or new REVIEW_ONLY_*.zip for REPORT_BUILD')
    parser.add_argument('--evidence-output', type=Path, help='REPORT_BUILD compile/render/package evidence directory')
    parser.add_argument('--run-id')
    parser.add_argument('--enable-live', action='store_true')
    args = parser.parse_args()
    if args.mode == 'FULL_RECOMPUTE':
        if args.output is None:
            parser.error('FULL_RECOMPUTE requires --output with a new directory')
        result = full_recompute(args.output)
        print({'status': result['status'], 'new_model_calls': result['new_model_calls']})
    elif args.mode == 'REPORT_BUILD':
        print(report_build(args.output, args.evidence_output))
    else:
        print(live(args.run_id, args.enable_live))


if __name__ == '__main__':
    main()
