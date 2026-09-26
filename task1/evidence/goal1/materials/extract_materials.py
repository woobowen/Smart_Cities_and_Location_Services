"""Read-only extraction of supplied PPTX, notebooks, and relevant starter sources.
Outputs in this evidence directory only. Notebook image bytes are hashed, not copied.
"""
from pathlib import Path
import json, hashlib, re, zipfile, posixpath, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def sha(b): return hashlib.sha256(b).hexdigest()
def all_text(data):
    root=ET.fromstring(data)
    return [''.join(p.itertext()) for p in root.findall('.//a:p',NS)]
def paragraphs(data):
    root=ET.fromstring(data)
    return [''.join(t.text or '' for t in p.iter() if t.tag.rsplit('}',1)[-1]=='t') for p in root.findall('.//a:p',NS)]
index=[]
for n,path in enumerate(sorted((ROOT/'task1').rglob('*.pptx'))):
    rel=path.relative_to(ROOT).as_posix()
    lines=[f'# PPTX source extraction: {rel}',f'Source SHA256: {sha(path.read_bytes())}', 'Classification: supplied teacher/starter material; saved outputs are historical, not current-run.', 'XML text and notes extraction preserves presentation slide order. Raster content requires separate visual inspection.','']
    with zipfile.ZipFile(path) as z:
        pres=ET.fromstring(z.read('ppt/presentation.xml'))
        rels={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
        for i,s in enumerate(pres.findall('.//p:sldId',NS),1):
            target=rels[s.attrib['{'+NS['r']+'}id']]
            sp=posixpath.normpath(posixpath.join('ppt',target))
            lines += [f'## Slide {i}: {sp}', '\n'.join(paragraphs(z.read(sp))),'']
            rp=posixpath.join(posixpath.dirname(sp),'_rels',posixpath.basename(sp)+'.rels')
            if rp in z.namelist():
                rlist=list(ET.fromstring(z.read(rp)))
                media=[]
                for r in rlist:
                    ty=r.attrib.get('Type','')
                    t=r.attrib.get('Target','')
                    targetp=posixpath.normpath(posixpath.join(posixpath.dirname(sp),t))
                    if ty.endswith('/notesSlide'):
                        lines += ['### Speaker notes','\n'.join(paragraphs(z.read(targetp))),'']
                    elif ty.endswith('/image'):
                        media.append(targetp if targetp in z.namelist() else '[external/missing image relationship; source target withheld from public extract]')
                if media: lines += ['### Embedded images', '\n'.join(f'- `{m}` SHA256={sha(z.read(m)) if m in z.namelist() else 'unavailable'}' for m in media),'']
    dest=OUT/f'pptx_{n+1:02d}_text_and_notes.md'
    dest.write_text('\n'.join(lines),encoding='utf-8')
    index.append({'source':rel,'sha256':sha(path.read_bytes()),'extract':dest.relative_to(ROOT).as_posix(),'type':'pptx','status':'EXTRACTED_REQUIRES_READ_AND_VISUAL'})
base=ROOT/'task1/作业/作业'
for n,path in enumerate(sorted(base.glob('*.ipynb'))):
    rel=path.relative_to(ROOT).as_posix(); nb=json.loads(path.read_text())
    lines=[f'# Notebook extraction: {rel}', f'Source SHA256: {sha(path.read_bytes())}', 'Classification: teacher/starter source; all saved execution counts and outputs are HISTORICAL.',f'Notebook metadata: {json.dumps(nb.get("metadata",{}),ensure_ascii=False)}','']
    for i,c in enumerate(nb['cells']):
        lines += [f'## Cell {i} ({c["cell_type"]}), execution_count={c.get("execution_count")}',f'Cell metadata: {json.dumps(c.get("metadata",{}),ensure_ascii=False)}','```python' if c['cell_type']=='code' else '```text',''.join(c.get('source',[])),'```']
        for j,o in enumerate(c.get('outputs',[])):
            lines += [f'### Output {j}: {o.get("output_type")}',f'execution_count={o.get("execution_count")}']
            for k,v in o.items():
                if k=='data':
                    for mime,content in v.items():
                        joined=''.join(content) if isinstance(content,list) else content
                        if mime.startswith('image/') or mime=='application/pdf':
                            raw=joined.encode() if isinstance(joined,str) else json.dumps(joined).encode()
                            lines.append(f'{mime}: binary/base64 payload omitted from readable copy; characters={len(raw)}, SHA256={sha(raw)}; original remains in source notebook.')
                        else: lines += [f'{mime}:','```',str(joined),'```']
                elif k not in ('output_type','execution_count'):
                    lines += [f'{k}:','```', ''.join(v) if isinstance(v,list) else str(v),'```']
    dest=OUT/f'notebook_{n+1:02d}_source_outputs.md';dest.write_text('\n'.join(lines),encoding='utf-8')
    index.append({'source':rel,'sha256':sha(path.read_bytes()),'extract':dest.relative_to(ROOT).as_posix(),'type':'notebook','cells':len(nb['cells']),'status':'EXTRACTED_REQUIRES_READ_AND_VISUAL'})
files=[p for p in base.rglob('*') if p.is_file() and p.suffix in ('.py','.md','.json','.ini','.mjs') and p.name!='traj_dict.json' and not any(part in p.parts for part in ('node_modules','.pytest_cache','__pycache__','.mplcache','.cache'))]
# Keep the supplied source in place: catalogue it instead of duplicating the starter tree.
import ast
lines=['# Starter source catalogue',
       'All listed text was read in full by this extractor and hashed. Python was parsed with ast.parse without importing or executing it.',
       'The catalogue is reading coverage, not proof that every branch is correct. Focused source checks are recorded in findings.md.', '']
for p in sorted(files):
    content=p.read_text(encoding='utf-8'); rel=p.relative_to(ROOT).as_posix()
    item={'source':rel,'sha256':sha(p.read_bytes()),'type':'starter_text','lines':len(content.splitlines()),'extract':'task1/evidence/goal1/materials/source_catalogue.md','status':'FULL_TEXT_READ_AND_CATALOGUED'}
    lines += [f'## {rel}',f'SHA256: {item["sha256"]}; lines: {item["lines"]}.']
    if p.suffix=='.py':
        tree=ast.parse(content,filename=rel)
        item['syntax_parse']='PASS'
        item['functions']=[{'name':n.name,'line':n.lineno,'end_line':n.end_lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
        doc=ast.get_docstring(tree)
        if doc: lines += ['Module summary: '+doc.splitlines()[0]]
        lines += [', '.join(f'{f["name"]}:L{f["line"]}' for f in item['functions']) or '(No functions.)']
    elif p.suffix=='.json':
        value=json.loads(content)
        item['json_parse']='PASS'
        item['top_level_keys']=list(value) if isinstance(value,dict) else None
        lines += ['JSON keys: '+', '.join(item['top_level_keys'] or [])]
    else:
        lines += ['Text source read; claims are historical/source declarations until independently verified.']
    lines += ['']
    index.append(item)
(OUT/'source_catalogue.md').write_text('\n'.join(lines),encoding='utf-8')
(OUT/'extraction_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entries':len(index),'pptx':sum(i['type']=='pptx' for i in index),'notebooks':sum(i['type']=='notebook' for i in index),'output_dir':str(OUT.relative_to(ROOT))},ensure_ascii=False))
