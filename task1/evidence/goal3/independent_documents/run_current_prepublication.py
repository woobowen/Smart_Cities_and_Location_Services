"""Repeat the scoped read-only scan, preserving the first completed preflight."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    archive = HERE / 'prepublication_initial_snapshot'
    archive.mkdir(exist_ok=True)
    preserved = []
    for name in ['prepublication_preflight.json', 'prepublication_scope_receipt.json']:
        original, copy = HERE / name, archive / name
        if copy.exists():
            if sha(copy) != sha(original): raise ValueError('REFUSE_TO_REPLACE_INITIAL_SCAN:' + name)
        else:
            shutil.copyfile(original, copy)
        preserved.append({'original': str(original.relative_to(ROOT)), 'snapshot': str(copy.relative_to(ROOT)),
                          'sha256': sha(copy)})
    scanner = HERE / 'prepublication_scan.py'
    spec = importlib.util.spec_from_file_location('independent_existing_scoped_scanner', scanner)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.OUTPUT = HERE / 'prepublication_current_preflight.json'
    started = datetime.now(timezone.utc).isoformat()
    with redirect_stdout(io.StringIO()):
        module.main()
    data = json.loads(module.OUTPUT.read_text())
    data['round'] = 'CURRENT_POST_REPORT_BUILD_AND_ACTUAL_ZIP'
    data['previous_scan_preserved'] = preserved
    data['actual_command'] = '.venv/bin/python task1/evidence/goal3/independent_documents/run_current_prepublication.py'
    data['wrapper_sha256'] = sha(Path(__file__))
    data['unchanged_scanner_sha256'] = sha(scanner)
    data['wrapper_started_at'] = started
    data['unchecked_components'] = [
        'isolated FULL outputs and final summary/handoff/publication files created after this scan cutoff; require bounded delta scan',
        'immutable pre-G3 content bytes (only index/metadata checked)',
        'arbitrary unrecognizable secret formats; no universal absence guarantee',
        'remote publication and fixed-SHA reread; not final publication acceptance']
    data['scanner_execution_note'] = 'Same completed read-only scanner reused with a new output path. First completed scan and scope preserved byte-for-byte; no old evidence overwritten.'
    data['separate_actual_artifact_reviews'] = [
        {'path': str((HERE / name).relative_to(ROOT)), 'sha256': sha(HERE / name)}
        for name in ['report_entry_delta_receipt.json', 'actual_zip_static_receipt.json',
                     'full_report_review_receipt.json', 'figures_current_closure.json']]
    module.OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: data[k] for k in ['status', 'content_scanned_or_hash_bound_targets',
                     'scanned_text_or_decompressed_bytes', 'issues']}, ensure_ascii=False))
    print(json.dumps({'candidate_findings_count': len(data['candidate_findings']),
                      'candidate_categories': sorted({k for row in data['candidate_findings'] for k in row['categories']}),
                      'report_path': str(module.OUTPUT.relative_to(ROOT)), 'report_sha256': sha(module.OUTPUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
