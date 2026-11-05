"""Safely extract teacher archives and preserve original member identities."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import stat
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT / 'task2'
OUT = TASK / 'teacher_materials'
EVIDENCE = TASK / 'evidence' / 'material_audit'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def decode_name(name, utf8=False):
    if utf8:
        return name, 'utf8-flag'
    try:
        raw = name.encode('cp437')
    except UnicodeError:
        return name, 'already-unicode'
    for codec in ['utf-8', 'gb18030']:
        try:
            return raw.decode(codec), 'cp437-to-' + codec
        except UnicodeError:
            pass
    return name, 'cp437-unresolved'


def valid(name):
    p = PurePosixPath(name.replace('\\', '/'))
    if p.is_absolute() or '..' in p.parts or any(':' in t for t in p.parts):
        raise ValueError('Unsafe archive member: ' + name)
    return p


def noise(p):
    return any(x == '__MACOSX' or x.startswith('._') for x in p.parts)


def write_member(base, name, b, record):
    p = valid(name)
    if noise(p):
        record['status'] = 'FILTERED_OS_METADATA'
    else:
        dst = base.joinpath(*p.parts)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and dst.read_bytes() != b:
            raise ValueError('Collision: ' + str(dst))
        dst.write_bytes(b)
        record.update(status='EXTRACTED', path=str(dst.relative_to(ROOT)), size=len(b), sha256=sha(b))
    return record


def extract_zip(path, base, records):
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist()) > 2_000_000_000:
            raise ValueError('Archive exceeds bounded extraction budget')
        for member in z.infolist():
            name, codec = decode_name(member.filename, bool(member.flag_bits & 0x800))
            p = valid(name)
            rec = dict(archive=str(path.relative_to(ROOT)), original_name=member.filename, decoded_name=name, codec=codec)
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError('Symlink member: ' + name)
            if member.is_dir():
                continue
            records.append(write_member(base, name, z.read(member), rec))


def extract_rar(path, base, records):
    import libarchive
    with libarchive.file_reader(str(path)) as archive:
        for entry in archive:
            name = entry.pathname
            if entry.issym or entry.islnk:
                raise ValueError('RAR link: ' + name)
            valid(name)
            if entry.isdir:
                continue
            b = b''.join(entry.get_blocks())
            rec = dict(archive=str(path.relative_to(ROOT)), original_name=name, decoded_name=name, codec='libarchive-unicode')
            records.append(write_member(base, name, b, rec))


def audit_content():
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    for ppt in sorted(OUT.rglob('*.pptx')):
        slides = []
        with zipfile.ZipFile(ppt) as z:
            names = [n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            names.sort(key=lambda s: int(s.rsplit('slide', 1)[1].split('.')[0]))
            for k, name in enumerate(names, 1):
                root = ET.fromstring(z.read(name))
                txt = '\n'.join(t.text or '' for t in root.findall('.//a:t', ns))
                slides.append(f'## Slide {k}\n\n{txt}\n')
        (EVIDENCE / (ppt.stem + '_slides.md')).write_text('\n'.join(slides), encoding='utf-8')
    for nb in sorted(OUT.rglob('*.ipynb')):
        data = json.loads(nb.read_text(encoding='utf-8'))
        cells = []
        for k, cell in enumerate(data['cells']):
            src = ''.join(cell.get('source', []))
            cells.append(f'## Cell {k} ({cell["cell_type"]})\n\n{src}\n')
        (EVIDENCE / (nb.stem + '_cells.md')).write_text('\n'.join(cells), encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, sub in [('实验2(1).zip', 'basic'), ('归档.zip', 'advanced')]:
        p = ROOT / filename
        records.append(dict(archive=str(p.relative_to(ROOT)), status='ORIGINAL_ARCHIVE', size=p.stat().st_size, sha256=sha(p.read_bytes())))
        extract_zip(p, OUT / sub, records)
    for path in list(OUT.rglob('*.zip')):
        extract_zip(path, path.parent / (path.stem + '_expanded'), records)
    for path in list(OUT.rglob('*.rar')):
        extract_rar(path, path.parent / (path.stem + '_expanded'), records)
    groups = {}
    for r in records:
        if r.get('status') == 'EXTRACTED':
            groups.setdefault(r['sha256'], []).append(r['path'])
    duplicate = {h: paths for h, paths in groups.items() if len(paths) > 1}
    (EVIDENCE / 'archive_manifest.json').write_text(json.dumps(dict(records=records, content_duplicates=duplicate), ensure_ascii=False, indent=2), encoding='utf-8')
    audit_content()
    print(json.dumps(dict(records=len(records), duplicates=duplicate, audit_files=[str(p.relative_to(ROOT)) for p in EVIDENCE.glob('*md')]), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
