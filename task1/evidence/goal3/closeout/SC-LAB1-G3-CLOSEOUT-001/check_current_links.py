"""Check local paths in the current review/navigation documents."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent


def main():
    files = [ROOT/'task1/README.md', ROOT/'task1/reports/README.md',
             ROOT/'task1/evidence/goal3/REVIEW_PACKET.md',
             ROOT/'task1/evidence/goal3/teacher_delivery_mapping.md']
    files += [ROOT/'task1/docs/goal3'/name for name in
              ['TECHNICAL_HANDOFF.md','INTERACTION_HANDOFF.md','DEFENSE_NOTES.md','REVIEW_GUIDE.md']]
    files += [BASE/name for name in ['ACCEPTANCE_MATRIX.md','FINAL_RESPONSE.md',
              'a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md', 'a_diagnosis/literature_use_map.md',
              'a_diagnosis/TEACHING_DIFFERENCES.md','b_handoff/evidence_inventory.md']]
    issues = []; counts = {}
    for file in files:
        if not file.is_file():
            issues.append({'path':str(file.relative_to(ROOT)), 'kind':'MISSING_CURRENT_DOCUMENT'})
            continue
        count = 0
        for target in re.findall(r'\[[^\]\n]*\]\(([^\s)]+)\)',file.read_text()):
            parsed = urlsplit(target.strip('<>'))
            if parsed.scheme or not parsed.path:
                continue
            count += 1
            resolved = (file.parent/unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                issues.append({'path':str(file.relative_to(ROOT)), 'target':target,
                               'kind':'MISSING_OR_OUTSIDE_REPOSITORY'})
        counts[str(file.relative_to(ROOT))] = count
    result = {'at':datetime.now(timezone.utc).isoformat(), 'status':'PASS' if not issues else 'FAIL',
              'scope':'Local file/directory link targets in current navigation; cell IDs, functions and PDF anchors are independently checked by C; HTTP fixed-SHA readback is separate.',
              'documents':counts, 'checked_local_links':sum(counts.values()), 'issues':issues}
    (BASE/'CURRENT_LINKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','checked_local_links','issues']},ensure_ascii=False))
    raise SystemExit(bool(issues))


if __name__ == '__main__':
    main()
