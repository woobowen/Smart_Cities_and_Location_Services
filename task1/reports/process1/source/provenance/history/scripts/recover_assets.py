from pathlib import Path
from zipfile import ZipFile
import re,sys,shutil,json,hashlib
sys.path.insert(0,str(Path(__file__).parent))
from editorial import ROOT,UNITS
mount=Path('/mnt/data');archive=mount/'WF_WorkflowConstruction_PreTask1_REVISED_LaTeX_Source(2).zip'
assert archive.exists(),archive
with ZipFile(archive) as z:
 assert z.testzip() is None
 members=z.namelist();missing=[];recoveries=[]
 for u in UNITS:
  for p in u['panels']:
   dst=ROOT/'assets'/p['src']
   if dst.exists():continue
   dst.parent.mkdir(parents=True,exist_ok=True)
   if p['src'].startswith('inherited/'):
    parts=Path(p['src']).parts;tail=f'{parts[1]}/assets/{parts[-1]}'
    matches=[n for n in members if n.endswith(tail)]
    if matches:dst.write_bytes(z.read(matches[0]));recoveries.append([str(dst.relative_to(ROOT)),str(archive.name)+':'+matches[0]]);continue
   else:
    name=Path(p['src']).name;exact=mount/name
    if exact.exists():shutil.copyfile(exact,dst);continue
    norm=lambda s:re.sub(r'\(\d+\)(?=\.png$)','',s)
    hits=[f for f in mount.rglob('*.png') if norm(f.name)==norm(name) and 'Process_Report_Final_Source' not in str(f)]
    if hits:
     from PIL import Image
     hits.sort(key=lambda f:(abs(Image.open(f).height-2048),-Image.open(f).width,len(str(f))))
     shutil.copyfile(hits[0],dst);recoveries.append([str(dst.relative_to(ROOT)),str(hits[0])]);continue
   missing.append([u['id'],p['src']])
 (ROOT/'provenance/asset_recovery.json').write_text(json.dumps(dict(authoritative_archive=archive.name,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),recovered=recoveries,missing=missing),ensure_ascii=False,indent=2))
 assert not missing,missing
 # Preserve supplied authorial source texts without distributing any fonts.
 for n in members:
  if n.endswith(('.tex','.md','.py','.sh')):
   out=ROOT/'provenance/pretask_source_snapshot'/Path(n).relative_to(Path(n).parts[0]);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(n))
print('All selected original UI and inherited source images are available.')
