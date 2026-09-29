"""Read-only validation of the current declared bundle; historical receipts are untouched."""
import argparse
import json
import subprocess
import sync_sources as sync


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', action='store_true', help='Also compare staged bytes against validated files')
    args = parser.parse_args()
    rows = sync.verify_bundle(sync.ROOT)
    sync.verify_manifest(sync.ROOT, rows)
    if args.index:
        paths = {r['source'] for r in rows} | {r['bundle'] for r in rows}
        paths |= {str(sync.DECLARATION_PATH), str(sync.INTERNAL_PATH / 'SOURCE_MANIFEST.md'),
                  str(sync.INTERNAL_PATH / 'UPLOAD_INSTRUCTIONS.md')}
        for path in sorted(paths):
            staged = subprocess.check_output(['git', 'show', ':' + path], cwd=sync.ROOT)
            sync.require(staged == (sync.ROOT / path).read_bytes(), f'Index differs: {path}')
    print(json.dumps(dict(status='PASS', declared_members=len(rows), index_checked=args.index,
                          writes=False, numerical_experiments=0), indent=2))


if __name__ == '__main__':
    main()
