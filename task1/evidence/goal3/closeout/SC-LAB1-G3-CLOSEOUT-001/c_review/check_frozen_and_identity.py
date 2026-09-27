"""Independent C: frozen input/source and trusted identity verification only."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf8'))


def main():
    startup = read('task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/startup.json')
    protected = []
    for path, expected in startup['protected_files'].items():
        actual = sha((ROOT/path).read_bytes())
        protected.append({'path': path, 'sha256': actual, 'match': actual == expected})
    freeze = read('task1/evidence/goal3/production_freeze.json')
    source_rows = []
    for path, expected in freeze['processing_source_hashes'].items():
        actual = sha((ROOT/path).read_bytes())
        original = subprocess.check_output(['git', 'show', freeze['processing_code_sha']+':'+path], cwd=ROOT)
        source_rows.append({'path': path, 'sha256': actual,
                            'frozen_hash_match': actual == expected,
                            'numeric_commit_match': actual == sha(original)})
    bindings = []
    for path in ['contract_freeze.json', 'selection_freeze.json', 'final_freeze.json', 'production_freeze.json']:
        value = read('task1/evidence/goal3/'+path)
        for target, expected in value['bindings'].items():
            actual = sha((ROOT/target).read_bytes())
            bindings.append({'freeze': path, 'path': target, 'sha256': actual, 'match': actual == expected})
    identity = read('task1/config/assignment.json')
    identity_checks = {
        'trusted_name': identity['student_name'] == '吴博闻',
        'trusted_id_string': type(identity['student_id']) is str and identity['student_id'] == '10245102410',
        'understanding_learning': identity['understanding_status'] == 'LEARNING',
        'submission_not_ready': identity['submission_status'] == 'NOT_READY',
        'new_gpt_second_review_pending': identity['new_gpt_second_review'] == 'PENDING',
    }
    from task1.goal3.identity import write_report_metadata
    with tempfile.TemporaryDirectory(dir=OUT, prefix='metadata-probe-') as temporary:
        temporary = Path(temporary)
        (temporary/'task1/config').mkdir(parents=True)
        (temporary/'task1/reports').mkdir(parents=True)
        (temporary/'task1/config/assignment.json').write_text(json.dumps(identity, ensure_ascii=False), encoding='utf8')
        first = write_report_metadata(temporary).read_bytes()
        (temporary/'task1/reports/metadata.tex').write_text('待补姓名 / 待补学号', encoding='utf8')
        second = write_report_metadata(temporary).read_bytes()
        identity_checks['repeat_generation_identical'] = first == second
        identity_checks['current_metadata_matches_generator'] = second == (ROOT/'task1/reports/metadata.tex').read_bytes()
    notebooks = []
    for path in sorted((ROOT/'task1/notebooks/final').glob('*.ipynb')):
        value = json.loads(path.read_text(encoding='utf8'))
        intro = ''.join(value['cells'][0]['source'])
        expected = {'student_name': identity['student_name'], 'student_id': identity['student_id']}
        notebooks.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()),
            'metadata_match': value['metadata']['assignment_identity'] == expected,
            'intro_name_and_id_match': all(v in intro for v in expected.values()),
            'mode_full': value['metadata']['default_execution'] == 'FULL_RECOMPUTE',
            'live_disabled': value['metadata']['new_live_enabled'] is False})
    old_scope_changes = subprocess.check_output(['git', 'diff', '--name-only', startup['initial_head'], '--',
        'task1/evidence/goal1', 'task1/evidence/goal2', 'task1/evidence/goal3/runs',
        'task1/作业', 'task1/实验课1.pptx', 'task1/config/goal2', 'task1/config/goal3'], cwd=ROOT, text=True).splitlines()
    result = {'reviewer': 'independent C / c_independent; no implementation edits',
        'at': datetime.now(timezone.utc).isoformat(),
        'numeric_code_sha': freeze['processing_code_sha'],
        'source_crs': freeze['source_crs'], 'final_strategy': freeze['final_strategy'],
        'strategies': freeze['strategies'], 'protected_files': protected,
        'frozen_processing_sources': source_rows, 'contract_bindings': bindings,
        'identity_checks': identity_checks, 'notebooks': notebooks,
        'protected_historical_scope_git_changes': old_scope_changes,
        'scope_limit': 'Static frozen contract/source identity plus real repeated metadata generation. Does not claim FULL, PDF visual review, Evidence Lock or user review.'}
    ok = (all(r['match'] for r in protected+bindings)
          and all(r['frozen_hash_match'] and r['numeric_commit_match'] for r in source_rows)
          and all(identity_checks.values()) and not old_scope_changes
          and all(all(r[k] for k in ['metadata_match','intro_name_and_id_match','mode_full','live_disabled']) for r in notebooks)
          and len(notebooks) == 2 and freeze['source_crs'] == 'UNVERIFIED' and freeze['final_strategy'] == 'S0')
    result['status'] = 'PASS' if ok else 'FAIL'
    result['review_script_sha256'] = sha(Path(__file__).read_bytes())
    (OUT/'frozen_identity_receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'status': result['status'], 'protected_files':len(protected), 'processing_sources':len(source_rows),
                      'binding_checks':len(bindings), 'notebooks':len(notebooks), 'historical_scope_changes':old_scope_changes}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
