"""Refresh old data patterns plus the independent content classification.

This only inventories local files. It never mutates a run or Git's index.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    original = HERE / 'local_only_manifest.json'
    classification = ROOT / 'task2/evidence/independent_package/sensitive_classification.json'
    old = json.loads(original.read_text())
    audit = json.loads(classification.read_text())
    reasons = {}
    for pattern in old['patterns']:
        for p in ROOT.glob(pattern):
            if p.is_file():
                reasons.setdefault(str(p.relative_to(ROOT)), []).append('Original input/per-record pattern: ' + pattern)
    # Membership bindings can expose individual records even without coordinate
    # keys. These exclusions come from actual content and a rank probe.
    expected = {}
    for row in audit['new_local_only_files']:
        rel = row['path']
        reasons.setdefault(rel, []).append(row['classification'] + ': ' + row['reason'])
        expected[rel] = row['sha256']
    replay_path = ROOT/'task2/evidence/rl/replay_recovery/cli_help_replay_01/replay_sensitive_classification.json'
    replay = json.loads(replay_path.read_text()) if replay_path.is_file() else None
    if replay:
        for row in replay['new_sensitive_files']:
            rel = row['path']
            reasons.setdefault(rel, []).append(row['classification'] + ': ' + row['reason'])
            expected[rel] = row['sha256']
    staged_addendum = ROOT/'task2/evidence/independent_package/staged_sensitive_addendum.json'
    staged_record = json.loads(staged_addendum.read_text()) if staged_addendum.is_file() else None
    if staged_record:
        rel = staged_record['path']
        reasons.setdefault(rel, []).append(staged_record['classification'] + ': ' + staged_record['reason'])
        expected[rel] = staged_record['sha256']
    rows = []
    changes = []
    authorized_replay_changes = []
    for rel in sorted(reasons):
        p = ROOT / rel
        if not p.is_file():
            raise FileNotFoundError(rel)
        actual = sha(p)
        if rel in expected and actual != expected[rel]:
            change = dict(path=rel, classified_sha256=expected[rel], current_sha256=actual)
            allowed = replay['canonical_sensitive_file_changed'] if replay else {}
            if rel == allowed.get('path') and actual == allowed.get('current_sha256'):
                authorized_replay_changes.append({**change, 'reason': allowed['reason'],
                    'authority': 'Root disclosed same-model accidental REPLAY and instructed current hash rebinding; independent replay receipt confirms science unchanged',
                    'evidence': str(replay_path.relative_to(ROOT))})
            else:
                changes.append(change)
        rows.append(dict(path=rel, bytes=p.stat().st_size, sha256=actual, reasons=reasons[rel]))
    result = dict(
        actual_utc=datetime.now(timezone.utc).isoformat(),
        status='LOCAL_ONLY_CURRENT_CONTENT_AND_PATTERN_SNAPSHOT',
        authority='Latest explicit user: no additional data license; local originals and reconstructable per-record derivatives remain local, code/reports/aggregates public',
        original_proposal_preserved='task2/evidence/research_data/local_only_manifest.json',
        original_proposal_sha256=sha(original),
        independent_classification='task2/evidence/independent_package/sensitive_classification.json',
        independent_classification_sha256=sha(classification),
        replay_classification=str(replay_path.relative_to(ROOT)) if replay else None,
        replay_classification_sha256=sha(replay_path) if replay else None,
        staged_content_addendum=str(staged_addendum.relative_to(ROOT)) if staged_record else None,
        staged_content_addendum_sha256=sha(staged_addendum) if staged_record else None,
        authorized_replay_hash_changes=authorized_replay_changes,
        classified_file_hash_changes=authorized_replay_changes + changes,
        unresolved_classification_hash_changes=changes,
        files_count=len(rows), bytes=sum(r['bytes'] for r in rows), files=rows,
        limit='Exact local exclusion inventory only. Newly generated files and final staged Git contents still require publication review. Does not certify that every unlisted file is safe.',
    )
    (HERE / 'local_only_manifest_current.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: result[k] for k in ('status', 'files_count', 'bytes', 'classified_file_hash_changes', 'unresolved_classification_hash_changes')}, ensure_ascii=False))
    if changes:
        raise SystemExit('Classified content changed: retain local, request independent reclassification')


if __name__ == '__main__':
    main()
