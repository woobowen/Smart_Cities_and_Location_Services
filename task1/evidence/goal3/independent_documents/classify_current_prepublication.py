"""Classify the completed, hash-pinned prepublication marker scan without edits."""
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCAN_SHA = 'ddef6b73a28fa819db5ee01d1bc847dedef743bd0421b0b438cd649d134f6a42'
ASSET = 'task1/figures/goal2/goal2_actual_architecture.png'
ASSET_SHA = '06e5deea0f1022fec93f969fca7aee6819b0b2ea1909aafa4332742cd70ff3c9'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def leaves(value, pointer=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, pointer + '/' + str(key).replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from leaves(child, pointer + '/' + str(index))
    elif isinstance(value, str):
        yield pointer, value


def path_reason(relative):
    if relative.endswith('_compile_output.txt') or relative.endswith('missing_optional_needspace.txt'):
        return 'Actual XeLaTeX invocation/package-resolution output, including a preserved earlier failed build; toolchain paths document execution and are not packaged runtime requirements.'
    if relative.endswith('goal_state.json') or '/logs/' in relative or relative.endswith('report_build_entry_receipt.json'):
        return 'Actual journal/command or execution traceback provenance; these internal records are outside the teacher ZIP.'
    if relative.endswith('isolated_launches.json') or relative.endswith('isolated_package_system_full_receipt.json'):
        return 'Actual independent isolated-run launch/checker command path; no credential value is recorded. It is not a teacher-package dependency.'
    if '/deliberate_synthetic_failure/' in relative:
        return 'Explicitly labelled synthetic executor failure/test provenance, including real interpreter/traceback paths; not a fabricated research or human-interaction result.'
    if relative.endswith('execution_receipt.json') or relative.endswith('notebook_receipt.json'):
        return 'Actual interpreter, kernel working directory or failure provenance in an internal execution receipt. Canonical completed Notebook outputs and the teacher ZIP are checked separately.'
    if relative.endswith('C07_initial_failure.xml') or 'NB01' in relative or relative.endswith('failure.txt'):
        return 'Preserved actual engineering failure traceback or error output, kept as historical repair evidence and excluded from the teacher ZIP.'
    raise ValueError('UNCLASSIFIED_PATH:' + relative)


def main():
    scan_path = HERE / 'prepublication_current_preflight.json'
    assert digest(scan_path.read_bytes()) == SCAN_SHA, 'scan changed; this classification must be reviewed again'
    scan = json.loads(scan_path.read_text())
    assert not scan['issues']
    assert len(scan['candidate_findings']) == 31
    scanner_path = HERE / 'prepublication_scan.py'
    spec = importlib.util.spec_from_file_location('scoped_marker_rules', scanner_path)
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    assert digest(scanner_path.read_bytes()) == scan['unchanged_scanner_sha256']
    assert digest((ROOT / ASSET).read_bytes()) == ASSET_SHA
    zip_path = ROOT / 'task1/submission/REVIEW_ONLY_实验一.zip'
    with zipfile.ZipFile(zip_path) as archive:
        package_members = set(archive.namelist())
    classifications = []
    for finding in scan['candidate_findings']:
        path = ROOT / finding['path']
        raw = path.read_bytes()
        assert digest(raw) == finding['sha256'], 'scanned finding changed:' + finding['path']
        item = dict(finding)
        categories = set(finding['categories'])
        parsed = json.loads(raw) if path.suffix in {'.json', '.ipynb'} else None
        if categories == {'PERSONAL_ABSOLUTE_PATH'}:
            assert finding['internal_evidence']
            assert finding['path'] not in package_members
            item.update(classification='AUTHENTIC_INTERNAL_ENGINEERING_PATH',
                        reason=path_reason(finding['path']),
                        in_actual_teacher_zip=False,
                        repair_required=False)
            if parsed is not None:
                item['matched_field_pointers'] = [pointer for pointer, value in leaves(parsed)
                    if scanner.PERSONAL.search(value.encode())]
                assert item['matched_field_pointers']
            else:
                item['matched_line_numbers'] = [number for number, line in enumerate(raw.splitlines(), 1)
                    if scanner.PERSONAL.search(line)]
                assert item['matched_line_numbers']
        elif categories == {'OPAQUE_PLATFORM_CIPHERTEXT'}:
            matches = [(pointer, value) for pointer, value in leaves(parsed)
                       if scanner.OPAQUE.search(value.encode())]
            assert len(matches) == 1
            pointer, encoded = matches[0]
            assert pointer == '/cells/3/outputs/1/data/image~1png'
            decoded = base64.b64decode(encoded, validate=True)
            assert decoded.startswith(b'\x89PNG\r\n\x1a\n')
            assert digest(decoded) == ASSET_SHA
            with Image.open(io.BytesIO(decoded)) as im:
                assert im.format == 'PNG'
                dimensions = im.size
                im.verify()
            assert dimensions == (4200, 2880)
            item.update(classification='FALSE_POSITIVE_NATIVE_PNG_BASE64',
                        reason='Marker occurs inside a valid image/png MIME value. Complete decoded bytes equal the existing native Goal 2 architecture PNG; no ciphertext payload is present or recovered.',
                        matched_field_pointers=[pointer], decoded_png_sha256=ASSET_SHA,
                        decoded_png_dimensions=list(dimensions),
                        exact_original_asset=ASSET, in_actual_teacher_zip=finding['path'] in package_members,
                        repair_required=False)
        else:
            raise ValueError('UNCLASSIFIED_CATEGORIES:' + finding['path'])
        classifications.append(item)
    assert sum(x['classification'] == 'AUTHENTIC_INTERNAL_ENGINEERING_PATH' for x in classifications) == 27
    assert sum(x['classification'] == 'FALSE_POSITIVE_NATIVE_PNG_BASE64' for x in classifications) == 4
    for entry in scan['previous_scan_preserved']:
        assert digest((ROOT / entry['original']).read_bytes()) == entry['sha256']
        assert digest((ROOT / entry['snapshot']).read_bytes()) == entry['sha256']
    targets = [ref(scan_path), ref(scanner_path), ref(Path(__file__)), ref(ROOT / ASSET), ref(zip_path)]
    targets += [ref(HERE / name) for name in [
        'actual_zip_static_receipt.json', 'report_entry_delta_receipt.json',
        'full_report_review_receipt.json', 'figures_current_closure.json']]
    result = {
        'role_context': '/root/c_documents',
        'target_id': 'current_prepublication_content_classification',
        'status': 'READY_WITHIN_CURRENT_SCOPED_PREFLIGHT',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'scan_cutoff_utc': scan['at_utc'],
        'targets': targets,
        'scanned_target_manifest': ref(scan_path),
        'content_scanned_or_hash_bound_targets': scan['content_scanned_or_hash_bound_targets'],
        'scanned_text_or_decompressed_bytes': scan['scanned_text_or_decompressed_bytes'],
        'proposed_worktree_inventory': scan['proposed_worktree_inventory'],
        'classifications': classifications,
        'genuine_secret_findings': [], 'ciphertext_or_reasoning_export_findings': [],
        'font_paper_cache_findings': [], 'unresolved_issues': [],
        'checked_components': [
            'Completed scan binds 1008 changed/proposed files since accepted Goal 2 anchor and scans 6971598166 actual plaintext/decompressed bytes with recorded marker rules.',
            'All 31 marker-hit files rehashed; 27 internal execution-path records manually classified and confirmed absent from the actual teacher ZIP.',
            'All four ciphertext-marker hits occur in valid base64 PNG MIME output; independent decode/image verification and exact native-asset SHA256 comparison classify false positives.',
            'Canonical Notebook outputs, both current PDFs and actual ZIP have separate current-byte checks; actual ZIP closed 1805 static checks including isolated no-Git import/freeze probe.',
            'Independent current-PDF rerender matches all 7 figure and 33 report rasters already visually reviewed; this is explicit equality rebinding, not claimed repeated eyesight.',
            'Governance export schema/source/hash checked: 198 metadata events, zero message bodies, no auth/reasoning/ciphertext-body export; original session log was not read.',
            'No proposed >=100MiB file or symlink, font binary, full-paper import, cache or token-pattern finding within the recorded scope.',
            'First preflight and scope receipt preserved byte-for-byte. All three original user ZIPs unchanged; both originally untracked archives remain untracked and excluded.'
        ],
        'governance_export_review': scan['governance_export_review'],
        'protected_original_zip_status': scan['protected_original_zip_status'],
        'previous_scan_preserved': scan['previous_scan_preserved'],
        'unchecked_components': scan['unchecked_components'],
        'final_delta_scan_required': True,
        'formal_publication_acceptance': False,
        'isolated_full_package_acceptance': 'PENDING_SEPARATE_NUMERICAL_REVIEW',
        'submission_status': 'NOT_READY_NOT_SUBMITTED',
        'no_session_auth_or_unrelated_history_read': True,
        'no_source_artifact_or_infrastructure_evidence_modified': True,
        'new_processing_or_model_calls': 0, 'installed_dependencies': [],
        'actual_command': '.venv/bin/python task1/evidence/goal3/independent_documents/classify_current_prepublication.py'
    }
    output = HERE / 'prepublication_current_scope_receipt.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'classified_files': len(classifications),
                      'issues': [], 'receipt': ref(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
