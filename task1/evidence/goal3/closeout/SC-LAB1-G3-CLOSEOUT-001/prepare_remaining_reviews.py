"""Submit concrete closeout artifacts to the existing Journal; never grant C acceptance."""
import argparse
import json
from pathlib import Path

from task1.goal3.control import Journal
from task1.workflow.io import digest, now, write_json

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
RUNS = ['repository_basic_retry', 'repository_system', 'isolated_basic', 'isolated_system_retry']


def read(path):
    return json.loads(Path(path).read_text())


def main(task):
    journal = Journal()
    paths = []; sources = {}
    if task in {'notebooks', 'package'}:
        for row in read(ROOT/'task1/evidence/goal3/package/source_closure.json')['members']:
            path = row.get('source_path', row['path'])
            actual = digest(ROOT/path)
            assert actual == row['source_sha256'], path
            sources[path] = actual
        sources['task1/goal3/execute_notebook.py'] = digest(ROOT/'task1/goal3/execute_notebook.py')
        for run in RUNS:
            receipt = BASE/'notebooks'/run/'execution_receipt.json'
            assert read(receipt)['status'] == 'VERIFIED'
    if task == 'notebooks':
        paths = sorted((ROOT/'task1/notebooks/final').glob('*.ipynb'))
        for run in RUNS:
            paths += [p for p in (BASE/'notebooks'/run).rglob('*') if p.is_file()]
        paths += [BASE/'c_review/notebook_runs_receipt.json', BASE/'notebook_interruptions.json',
                  BASE/'c_review/CL-C03_closure.json']
    elif task == 'package':
        package = read(BASE/'PACKAGE_VALIDATION.json')
        paths = [ROOT/package['zip_path'], ROOT/package['equivalent_executed_archive'],
                 BASE/'PACKAGE_VALIDATION.json', BASE/'c_review/package_receipt.json',
                 BASE/'c_review/package_execution_equivalence.json', BASE/'c_review/notebook_runs_receipt.json',
                 ROOT/'task1/evidence/goal3/package/source_closure.json',
                 ROOT/'task1/evidence/goal3/package/package_build_receipt.json']
    elif task == 'handoffs':
        paths = [ROOT/'task1/docs/goal3'/name for name in
                 ['TECHNICAL_HANDOFF.md','INTERACTION_HANDOFF.md','DEFENSE_NOTES.md','REVIEW_GUIDE.md']]
        paths += [ROOT/'task1/evidence/goal3'/name for name in
                  ['teacher_delivery_mapping.json','teacher_delivery_mapping.md','interaction_candidates.json']]
        paths += [BASE/'a_diagnosis'/name for name in ['MASTER_REQUIREMENTS_REVIEW.json',
                  'MASTER_REQUIREMENTS_REVIEW.md','literature_use_map.json','literature_use_map.md',
                  'TEACHING_DIFFERENCES.md','A_SELF_CHECK.json','citation_access_receipt.json',
                  'teacher_source_recheck.json']]
        paths += [BASE/'review_input_snapshot'/name for name in
                  ['goal_state.json','requirements.json','SNAPSHOT_MANIFEST.json']]
        paths += [BASE/'b_handoff/evidence_inventory.json', BASE/'b_handoff/evidence_inventory.md',
                  BASE/'c_review/guide_interaction_receipt.json']

        def walk(value):
            if isinstance(value, dict):
                path, expected = value.get('path'), value.get('sha256')
                if path and expected and not path.startswith(('http:', 'https:')):
                    assert digest(ROOT/path) == expected
                    sources[path] = expected
                for child in value.values(): walk(child)
            elif isinstance(value, list):
                for child in value: walk(child)
        walk(read(BASE/'a_diagnosis/MASTER_REQUIREMENTS_REVIEW.json'))
        walk(read(BASE/'a_diagnosis/literature_use_map.json'))
    elif task == 'internal_acceptance':
        for name in ['figures','notebooks','experiment_report','process_report','handoffs','package']:
            row = journal.state['tasks'][name]
            assert row['status'] in {'VERIFIED','BLOCKED_EXTERNAL'} and journal.current(row)
            paths += [ROOT/t['path'] for t in row['targets']]
            paths.append(ROOT/row['receipt']['path'])
            for path, expected in row['source_hashes'].items():
                assert path not in sources or sources[path] == expected
                sources[path] = expected
    else:
        raise ValueError('Unsupported closeout review scope')
    paths = sorted(set(paths))
    packet = {'at':now(),'author':'B:root','task':task,
              'targets':[journal.attach(p) for p in paths], 'source_hashes':sources,
              'mutable_status_boundary':'The current requirements, CL matrix, Review Packet, publication records and goal_state remain status/navigation outputs; immutable review snapshots and the substantive leaf deliverables are bound above. C checks final status deltas separately.'}
    write_json(BASE/(task+'_review_submission.json'), packet)
    journal.submit(task, paths, sources)
    print(json.dumps({'task':task,'targets':len(paths),'sources':len(sources),'status':'REVIEW_PENDING'}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('task',choices=['notebooks','package','handoffs','internal_acceptance'])
    main(parser.parse_args().task)
