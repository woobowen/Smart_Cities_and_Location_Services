"""Reinspect the unchanged failed pilot-01 candidate; do not replace its review."""
from pathlib import Path

from task1.workflow.evaluation import review_baseline, DIRECTION_FLOAT_ALLOWANCE_DEGREES
from task1.workflow.io import ROOT, DATA, CONFIG, EVIDENCE, digest, read_json, write_json, now
from task1.workflow.pipeline import trusted_real_reference


def main():
    revision = EVIDENCE / 'revisions/SC-LAB1-G1-COMPLETE-001'
    run = revision / 'runs/g1-complete-pilot-01'
    candidate_path, review_path = run / 'baseline.json', run / 'baseline_review.json'
    before = {'candidate_sha256': digest(candidate_path), 'old_review_sha256': digest(review_path)}
    candidate = read_json(candidate_path)
    reference = trusted_real_reference(read_json(DATA), candidate['provenance']['record_scope'], read_json(CONFIG))
    reviewed = review_baseline(candidate, *reference)
    assert before == {'candidate_sha256': digest(candidate_path), 'old_review_sha256': digest(review_path)}
    report = {'at': now(), 'classification': 'CURRENT_RUN_CONDITIONAL_ANALYSIS_DIAGNOSTIC',
              'action': 'Independent reinspection of unchanged failed-run candidate, not a new production run',
              'source_run': 'g1-complete-pilot-01', **before,
              'original_review_status': read_json(review_path)['status'],
              'new_review': reviewed, 'provider_calls': 0, 'production_runs': 0,
              'evaluation_sha256': digest(ROOT / 'task1/workflow/evaluation.py'),
              'production_geometry_sha256': digest(ROOT / 'task1/workflow/geometry.py'),
              'angle_allowance_degrees': DIRECTION_FLOAT_ALLOWANCE_DEGREES,
              'angle_allowance_derivation': '64 * binary64 epsilon * one normalized turn (360 degrees); numerical arithmetic only',
              'method_predicate_changed': False, 'dp_changed': False,
              'old_failed_candidate_and_review_unchanged': True,
              'lineage_note': 'Parent task must rebuild under fixed new CODE_SHA; this diagnostic cannot rehabilitate old run provenance.'}
    write_json(Path(__file__).with_name('candidate_recheck.json'), report)
    print('Old review:', report['original_review_status'])
    print('New independent numeric inspection:', reviewed['status'])
    print('Fixed angle arithmetic allowance (degrees):', DIRECTION_FLOAT_ALLOWANCE_DEGREES)
    print('Old candidate/review unchanged:', report['old_failed_candidate_and_review_unchanged'])
    if reviewed['status'] != 'VERIFIED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
