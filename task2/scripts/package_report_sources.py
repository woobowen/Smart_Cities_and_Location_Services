"""Package the actual report sources and vector assets, without source records."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'task2/releases/Dispatch_Reports_LaTeX_Source.zip')
    parser.add_argument('--replace', action='store_true', help='explicitly replace an existing package')
    args = parser.parse_args()
    if args.output.exists() and not args.replace:
        parser.error('output exists; choose a new path or explicitly use --replace')
    files = set((ROOT / 'task2/reports').rglob('*.tex'))
    files.update((ROOT / 'task2/reports').glob('*/*_Report.pdf'))
    for extension in ('*.pdf', '*.svg'):
        files.update((ROOT / 'task2/figures/formal').glob(extension))
    for extension in ('*.drawio', '*.pdf', '*.svg'):
        files.update((ROOT / 'task2/diagrams').glob(extension))
    files.update([
        ROOT / 'templates/latex/common/p2_cloud_sorbet_colors.tex',
        ROOT / 'task2/scripts/build_reports.py',
        ROOT / 'task2/reports/generated/sources.json',
        ROOT / 'task2/docs/ENVIRONMENT_CHANGELOG.md',
    ])
    records = []
    payload = {}
    for file in sorted(files):
        if 'build' in file.relative_to(ROOT).parts:
            continue
        data = file.read_bytes()
        name = file.relative_to(ROOT).as_posix()
        payload[name] = data
        records.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    readme = '''# Dispatch reports: paired editable sources

Extract while preserving the relative `task2/` and `templates/` directories.
Run from this extracted root with Python 3 and XeLaTeX/latexmk, Poppler tools,
DejaVu Serif/Sans and Noto Serif/Sans/Mono CJK SC installed:

    python3 task2/scripts/build_reports.py

Alternatively run `latexmk -g -xelatex -outdir=build main.tex` inside each
`task2/reports/{experiment,process}` directory. The included PDFs are the actual
paired delivery PDFs, not a replacement for rebuilding their source.

This is a report-compilation source package. It includes editable LaTeX,
generated tables, vector figures, editable draw.io nodes/edges, and the exact
common P2 source copied for distribution. In the repository that common file
remains the sole editable color source. No font binaries or Foursquare records
are distributed. Scientific plots can be regenerated separately from the public
repository scripts/aggregate inputs; experiment recomputation uses the author's
verified public download and fixed input hashes documented in the repository.

Process Report is a text/technical-material handoff. New native ChatGPT UI
screenshots, presentation specification and Evidence Master Lock remain external.
Compilation does not establish data recomputation or visual acceptance.
'''
    payload['README_SOURCE_PACKAGE.md'] = readme.encode('utf-8')
    payload['SOURCE_PACKAGE_MANIFEST.json'] = json.dumps({
        'scope': 'paired report compilation sources and vector assets; no raw records or font binaries',
        'files': records,
    }, ensure_ascii=False, indent=2).encode('utf-8')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 11, 5, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(json.dumps(dict(path=str(args.output), members=len(payload), bytes=args.output.stat().st_size, sha256=digest), indent=2))


if __name__ == '__main__':
    main()
