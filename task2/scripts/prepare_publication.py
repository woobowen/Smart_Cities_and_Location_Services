"""Apply the reviewed exact local-data inventory to task-scoped Git exclusions.

This never removes files, stages Git contents or certifies unlisted files safe.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def ignore_literal(path):
    for char in ('\\', '*', '?', '[', ']', '!', '#', ' '):
        path = path.replace(char, '\\' + char)
    return '/' + path


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    manifest_path = ROOT / 'task2/evidence/research_data/local_only_manifest_current.json'
    manifest = json.loads(manifest_path.read_text())
    unresolved = manifest.get('unresolved_classification_hash_changes', manifest['classified_file_hash_changes'])
    if unresolved:
        raise ValueError('Unresolved classified content changes in the current inventory')
    changes = manifest['classified_file_hash_changes']
    if changes and changes != manifest.get('authorized_replay_hash_changes', []):
        raise ValueError('Classified hash changes must have explicit matching replay authorization')
    rows = manifest['files']
    lines = [
        '# Generated exact local-only data paths; originals remain on disk.',
        '# Authority: explicit user publication boundary; see docs/PUBLICATION_DATA_BOUNDARY.md.',
        '# Source inventory: evidence/research_data/local_only_manifest_current.json.',
        '# Regenerate only after reviewing/classifying newly created per-record outputs.',
    ]
    for row in rows:
        path = ROOT / row['path']
        if not path.is_file() or sha(path) != row['sha256']:
            raise ValueError('Missing/changed local-only file: ' + row['path'])
        if row['path'].startswith('task2/'):
            lines.append(ignore_literal(row['path'][len('task2/'):]))
        elif row['path'] not in ('实验2(1).zip', '归档.zip'):
            raise ValueError('Unexpected exclusion outside task2: ' + row['path'])
    target = ROOT / 'task2/.gitignore'
    target.write_text('\n'.join(lines) + '\n')
    paths = [row['path'] for row in rows]
    result = subprocess.run(['git', 'check-ignore', '--stdin', '-z'], cwd=ROOT,
                            input=b'\0'.join(x.encode() for x in paths) + b'\0', capture_output=True, check=True)
    ignored = set(x.decode() for x in result.stdout.split(b'\0') if x)
    if ignored != set(paths):
        raise ValueError('Exact inventory not completely excluded: ' + str(set(paths) - ignored))
    evidence = ROOT / 'task2/evidence/publication'
    evidence.mkdir(parents=True, exist_ok=True)
    receipt = dict(status='EXACT_REVIEWED_INVENTORY_EXCLUDED_NO_FILES_DELETED',
                   inventory_path=str(manifest_path.relative_to(ROOT)), inventory_sha256=sha(manifest_path),
                   excluded_files=len(paths), excluded_bytes=sum(x['bytes'] for x in rows),
                   disclosed_authorized_replay_hash_changes=manifest.get('authorized_replay_hash_changes', []),
                   task_ignore_sha256=sha(target), root_ignore_sha256=sha(ROOT / '.gitignore'),
                   scope='Only known local-only files. Final staged contents still require independent content review.')
    (evidence / 'exclusion_receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
