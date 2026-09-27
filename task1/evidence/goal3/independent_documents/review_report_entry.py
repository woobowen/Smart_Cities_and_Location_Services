"""Independent source-repair check; all build inputs below are synthetic.

This exercises the real REPORT_BUILD orchestration, but substitutes its
scientific-data/report stages. It never runs the formal report integration.
"""
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from task1.goal3 import __main__ as entry
from task1.goal3 import control, freezes, summarize, figures, package

EXPECTED = {
    'task1/goal3/__main__.py': '35b62e69cb05d224d88d750e7a1c31229a6ad351766bfc58024a120e582f0c1d',
    'task1/goal3/figures.py': '050223d644a1bb0ba7dfc95ff093f40e6e06a31ed8d3372c0a16c7b75e7f52fa',
    'task1/goal3/summarize.py': 'fca49199bfe68fab084cfd8b04ca89ba87bd647b241967ca9e1967ad777b653b',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert {p: sha(ROOT/p) for p in EXPECTED} == EXPECTED
    checks, cases = [], []

    def check(label, condition):
        checks.append({'check':label, 'passed':bool(condition)})
        if not condition:
            raise AssertionError(label)

    with tempfile.TemporaryDirectory(prefix='report-entry-synthetic-', dir=HERE) as temporary:
        base = Path(temporary)

        def exercise(name, *, output_case='new', missing=None, rejected_task=False,
                     rejected_run=None, failing_command=None, default_output=False):
            root = base/name; root.mkdir()
            (root/'.git').mkdir()
            report_source = root/'task1/reports/build_reports.py'
            report_source.parent.mkdir(parents=True)
            report_source.write_text('# SYNTHETIC_REPORT_SOURCE_ONLY\n')
            old_report = root/'task1/reports/SYNTHETIC_REPORT_MARKER.txt'
            old_report.write_text('ORIGINAL_SYNTHETIC_REPORT')
            initial_report = sha(old_report)
            ev = root/'task1/evidence/goal3'; ev.mkdir(parents=True)
            current = {key:'SYNTHETIC_'+key for key in
                       ('development','selection','confirmation','production')}
            (ev/'current_runs.json').write_text(json.dumps(current))
            output = root/'REVIEW_ONLY_SYNTHETIC.zip'
            if default_output:
                output = root/'task1/submission/REVIEW_ONLY_实验一.zip'
            if output_case == 'existing_zip':
                output.write_bytes(b'SYNTHETIC_USER_ARCHIVE_PRESERVE')
            elif output_case == 'existing_tmp':
                output.with_suffix('.zip.tmp').write_bytes(b'SYNTHETIC_INTERRUPTED_ARCHIVE_PRESERVE')
            elif output_case == 'bad_prefix':
                output = root/'student_name.zip'
            elif output_case == 'bad_suffix':
                output = root/'REVIEW_ONLY_SYNTHETIC.txt'
            if missing == 'git':
                (root/'.git').rmdir()
            elif missing == 'report_source':
                report_source.unlink()
            elif missing == 'current_index':
                (ev/'current_runs.json').unlink()
            events = []

            class SyntheticJournal:
                def invalidate_changed(self):
                    events.append('invalidate_changed')

            def task_gate(topic):
                events.append('verified_task:'+topic)
                if rejected_task:
                    raise ValueError('SYNTHETIC_UNVERIFIED_PRODUCTION')

            def run_gate(run_id):
                events.append('verified_run:'+run_id)
                if run_id == rejected_run:
                    raise ValueError('SYNTHETIC_STALE_OR_CHANGED_RUN')

            def summary_stage():
                events.append('build_summary')

            def figures_stage(output):
                events.append('build_figures')

            def command_stage(argv, **kwargs):
                check(name+':subprocess_cwd_and_check', kwargs == {'cwd':root, 'check':True})
                if argv[1] == str(report_source):
                    check(name+':report_render_requested', argv[2:] == ['--render'])
                    events.append('report_compile_render')
                    if failing_command == 'report':
                        raise subprocess.CalledProcessError(17, ['SYNTHETIC_REPORT_FAILURE'])
                    old_report.write_text('REBUILT_SYNTHETIC_REPORT')
                else:
                    check(name+':actual_package_cli_arguments',
                          argv[1:4] == ['-m','task1.goal3.package','--build'] and
                          Path(argv[4]) == output and argv[5:] == ['--probe'])
                    events.append('package_build_probe')
                    if failing_command == 'package':
                        raise subprocess.CalledProcessError(19, ['SYNTHETIC_PACKAGE_FAILURE'])
                    # Exercise the real ZIP writer with an explicitly synthetic
                    # one-file payload; this is not a teacher submission package.
                    payload = {'SYNTHETIC_ENGINEERING_ONLY.txt':b'No experiment data or report in this fixture.\n'}
                    members = [{'path':p, 'bytes':len(data),
                                'source_sha256':package.sha(data), 'archive_sha256':package.sha(data)}
                               for p,data in payload.items()]
                    package.build(output, {'status':'STATIC_CLOSURE_COMPLETE',
                                           'classification':'SYNTHETIC_ENGINEERING_ONLY',
                                           'members':members}, payload)
                return subprocess.CompletedProcess(['SYNTHETIC'], 0)

            with ExitStack() as stack:
                for module, attr, value in (
                    (entry,'ROOT',root), (entry,'EV',ev),
                    (control,'Journal',SyntheticJournal),
                    (freezes,'verified_task',task_gate), (freezes,'verified_run',run_gate),
                    (summarize,'build',summary_stage), (figures,'build',figures_stage),
                    (entry.subprocess,'run',command_stage)):
                    stack.enter_context(patch.object(module, attr, value))
                outcome, message = None, None
                try:
                    outcome = entry.report_build(None if default_output else output)
                except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
                    message = type(exc).__name__+':'+str(exc).replace(str(root),'<synthetic-root>')

            if output_case != 'new' or missing or rejected_task or rejected_run:
                check(name+':rejected', outcome is None and message is not None)
                check(name+':before_any_report_or_summary_rewrite',
                      not set(events) & {'build_summary','build_figures','report_compile_render','package_build_probe'}
                      and sha(old_report) == initial_report)
                if output_case == 'existing_zip':
                    check(name+':user_archive_unchanged', output.read_bytes() == b'SYNTHETIC_USER_ARCHIVE_PRESERVE')
                elif output_case == 'existing_tmp':
                    check(name+':interrupted_archive_unchanged',
                          output.with_suffix('.zip.tmp').read_bytes() == b'SYNTHETIC_INTERRUPTED_ARCHIVE_PRESERVE')
                else:
                    check(name+':no_archive_created', not output.exists())
            elif failing_command:
                check(name+':subprocess_failure_propagated', outcome is None and message.startswith('CalledProcessError:'))
                check(name+':no_archive_claimed_or_created', not output.exists())
                if failing_command == 'report':
                    check(name+':package_not_attempted_after_failed_report', 'package_build_probe' not in events)
            else:
                expected = ['invalidate_changed','verified_task:production'] + [
                    'verified_run:SYNTHETIC_'+key for key in
                    ('development','selection','confirmation','production')] + [
                    'build_summary','build_figures','report_compile_render','package_build_probe','invalidate_changed']
                check(name+':all_gates_before_report_and_actual_zip_call', events == expected)
                check(name+':new_review_archive_created', output.is_file() and output.read_bytes()[:2] == b'PK')
                check(name+':returned_actual_hash_and_explicit_review_limits',
                      outcome['status'] == 'REVIEW_ONLY_REBUILT'
                      and outcome['package_sha256'] == sha(output)
                      and outcome['submission_status'] == 'NOT_SUBMITTED'
                      and outcome['independent_visual_and_isolated_full_package_review'] == 'REQUIRED_FOR_THIS_NEW_BUILD')
                with zipfile.ZipFile(output) as archive:
                    check(name+':synthetic_archive_crc_and_identity', archive.testzip() is None and
                          set(archive.namelist()) == {'SYNTHETIC_ENGINEERING_ONLY.txt','PACKAGE_MANIFEST.json'})
                extracted = root/'synthetic_extracted'; extracted.mkdir()
                with zipfile.ZipFile(output) as archive:
                    archive.extractall(extracted)
                check(name+':synthetic_archive_exact_hash_verification',
                      package.verify_directory(extracted)['status'] == 'VERIFIED')
            cases.append({'case':name, 'events':events, 'outcome':outcome,
                          'expected_failure':message is not None, 'failure_category':message,
                          'classification':'SYNTHETIC_ORCHESTRATION_ONLY'})

        for kind in ('existing_zip','existing_tmp','bad_prefix','bad_suffix'):
            exercise(kind, output_case=kind)
        for missing in ('git','report_source','current_index'):
            exercise('missing_'+missing, missing=missing)
        exercise('unverified_production', rejected_task=True)
        for topic in ('development','selection','confirmation','production'):
            exercise('unverified_'+topic+'_run', rejected_run='SYNTHETIC_'+topic)
        exercise('report_subprocess_failure', failing_command='report')
        exercise('package_subprocess_failure', failing_command='package')
        exercise('successful_explicit_archive')
        exercise('successful_default_archive', default_output=True)

        # Direct generator entry points must also call the stronger shared gate
        # before loading that stage's report data, even when not called via CLI.
        writer = Mock(); writer.current = {'development':'SYNTHETIC_DEVELOPMENT'}
        with patch.object(figures,'verified_run',side_effect=ValueError('SYNTHETIC_HASH_REJECTED')) as gate:
            with patch.object(figures,'read_json') as reader:
                try:
                    figures.run_source(writer,'development')
                except ValueError as exc:
                    check('figure_source_real_gate_precedes_loading', str(exc) == 'SYNTHETIC_HASH_REJECTED'
                          and gate.call_count == 1 and reader.call_count == writer.source.call_count == 0)
                else:
                    check('figure_source_real_gate_precedes_loading', False)
        current = {'development':'SYNTHETIC_DEVELOPMENT'}
        with patch.object(summarize,'read_json',return_value=current), \
             patch.object(summarize,'verified_run',side_effect=ValueError('SYNTHETIC_HASH_REJECTED')) as gate, \
             patch.object(summarize,'write_json') as writer:
            try:
                summarize.build()
            except ValueError as exc:
                check('summary_real_gate_precedes_writing', str(exc) == 'SYNTHETIC_HASH_REJECTED'
                      and gate.call_count == 1 and writer.call_count == 0)
            else:
                check('summary_real_gate_precedes_writing', False)

    check('reviewed_sources_unchanged_during_review', {p:sha(ROOT/p) for p in EXPECTED} == EXPECTED)
    receipt = {
        'role_context':'/root/c_documents', 'target_id':'REPORT_BUILD_MISSING_ARCHIVE_SOURCE_REPAIR',
        'status':'VERIFIED', 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'targets':[{'path':p,'sha256':h} for p,h in EXPECTED.items()],
        'reference':{'requirement':'Current Goal 3 prompt §12.1: REPORT_BUILD produces reports and the submission package.',
                     'previous_entry_sha256':'a052acce796cd8ea9ce58a29ad1d442f63ce773a13a0dc069e2b019a0c70ee77'},
        'checked_components':[
            'existing ZIP and .tmp preservation and filename/full-repository prerequisites reject before report rewrite',
            'production task and all four complete independently verified runs are checked before summary/figures/reports',
            'shared verified_run source implementation checks bound source, exact manifest target, every independent-review target and actual shards',
            'figures.run_source and summarize.build reuse the shared gate before reading/writing stage data',
            'successful orchestration requests report render and package --build --probe in that order',
            'two synthetic successful paths create an actual isolated synthetic ZIP using the real writer, verify CRC/hash after extraction',
            'return value binds actual ZIP hash and explicitly retains REVIEW_ONLY, NOT_SUBMITTED and required independent review',
            'subprocess failures propagate without a claimed archive/success result',
            'changed deliverable audit state is invalidated after successful rebuild',
        ],
        'unchecked_components':[
            'formal REPORT_BUILD integration on completed/independently verified production: NOT_RUN',
            'true report generation, actual submission payload/ZIP dependency closure and isolated full recomputation: NOT_RUN',
            'final report numerical consistency, source citations and all-page >=200dpi visual review: NOT_RUN',
            'full successful Notebook executed outputs/paths/zero-model count: NOT_RUN',
        ],
        'classification':'INDEPENDENT_SOURCE_REPAIR_AND_SYNTHETIC_ORCHESTRATION; not a final report/package acceptance',
        'checks':checks, 'check_count':len(checks), 'synthetic_cases':cases,
        'formal_report_build_calls':0, 'trajectory_recomputations':0,
        'new_model_calls':0, 'synthetic_archives_created_and_removed':2,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_documents/review_report_entry.py',
        'installed_dependencies':[],
    }
    path = HERE/'report_build_source_closure.json'
    path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','check_count','formal_report_build_calls',
                    'trajectory_recomputations','new_model_calls','synthetic_archives_created_and_removed')}))


if __name__ == '__main__':
    main()
