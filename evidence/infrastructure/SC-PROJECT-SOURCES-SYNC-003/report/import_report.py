"""Verify the received archive before controlled import; never repack the pair."""
from pathlib import Path, PurePosixPath
import ast, collections, hashlib, json, re, shutil, stat, tempfile, zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
EV=Path(__file__).resolve().parent
RECEIVED=EV.parent/'received'
PDF='Experiment_Report_吴博闻_10245102410.pdf'
ZIP='Experiment_Report_完整重构_源文件.zip'
EXPECTED={PDF:'2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0',ZIP:'6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd'}
def sha(b):return hashlib.sha256(b).hexdigest()
for n,h in EXPECTED.items():assert sha((RECEIVED/n).read_bytes())==h
canonical=ROOT/'reports/experiment-report/experiment1-reconstructed'
source=ROOT/'task1/reports/experiment1'
records=[]; unsafe=[]; secret=[]; tex_exec=[]; fonts=[]; drawings=[]; python_imports={}
with zipfile.ZipFile(RECEIVED/ZIP) as z:
 names=z.namelist(); duplicate=[n for n,c in collections.Counter(names).items() if c>1]
 assert len(names)==72 and not duplicate and z.testzip() is None
 for i in z.infolist():
  name=i.filename;p=PurePosixPath(name);mode=(i.external_attr>>16)&0xffff;b=z.read(i)
  if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or p.parts[0]!='Experiment_Report_source' or stat.S_ISLNK(mode):unsafe.append(name)
  if p.suffix.lower() in {'.otf','.ttf','.woff','.woff2','.ttc'}:fonts.append(name)
  if p.suffix in {'.md','.tex','.py','.sh','.json','.csv','.svg','.drawio','.txt'}:
   t=b.decode('utf8')
   patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'\bgh[pousr]_[A-Za-z0-9]{30,}',r'\bgithub_pat_[A-Za-z0-9_]{40,}',r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}']
   if any(re.search(q,t) for q in patterns):secret.append(name)
   if p.suffix=='.tex' and re.search(r'\\(?:write18|immediate\s*\\write18|openout|input\s*\|)|shell-escape',t):tex_exec.append(name)
   if p.suffix=='.py':
    tree=ast.parse(t);python_imports[name]=sorted({getattr(v,'module',None) or a.name for v in ast.walk(tree) if isinstance(v,(ast.Import,ast.ImportFrom)) for a in v.names})
   if p.suffix=='.drawio':
    root=ET.fromstring(t);cells=root.findall('.//mxCell');vertices=[c for c in cells if c.get('vertex')=='1'];edges=[c for c in cells if c.get('edge')=='1']
    assert vertices and edges
    drawings.append({'path':name,'vertices':len(vertices),'edges':len(edges),'editable_xml':True})
  records.append({'path':name,'bytes':len(b),'sha256':sha(b),'mode':oct(mode)})
 assert not any([unsafe,secret,tex_exec,fonts])
 assert z.read('Experiment_Report_source/Experiment_Report.pdf')==(RECEIVED/PDF).read_bytes()
 local=z.read('Experiment_Report_source/source/p2_cloud_sorbet_colors.tex').decode()
 public=(ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex').read_text()
 colors=lambda s:dict(re.findall(r'\\definecolor\{([^}]+)\}\{HTML\}\{([A-Fa-f0-9]+)\}',s))
 assert colors(local)==colors(public)
 clean=Path(tempfile.mkdtemp(prefix='sc-report-source-003-'))/'Experiment_Report_source'
 clean.mkdir()
 for i in z.infolist():
  relative=PurePosixPath(i.filename).relative_to('Experiment_Report_source')
  if str(relative)=='Experiment_Report.pdf':continue
  dest=clean/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(i))
 canonical.mkdir(parents=True,exist_ok=True)
 for n in EXPECTED:
  target=canonical/n
  if target.exists():assert target.read_bytes()==(RECEIVED/n).read_bytes()
  else:shutil.copyfile(RECEIVED/n,target)
 # Keep all supplied editable sources and historical author checks, except the
 # embedded reading PDF; its exact bytes live once as canonical reference.
 for p in clean.rglob('*'):
  if not p.is_file():continue
  target=source/p.relative_to(clean);target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():raise FileExistsError(target)
  shutil.copyfile(p,target)
 result={'status':'VERIFIED','archive':ZIP,'members':records,'crc':'PASS','duplicates':duplicate,'unsafe_paths_or_symlinks':unsafe,'font_binaries':fonts,'credential_matches':secret,'tex_external_execution':tex_exec,'python_imports':python_imports,'build_script_review':'Two xelatex passes, ordinary mkdir/cp, no shell-escape/network/model calls; optional Python figures are local data-to-figure writers and not executed during report build.','embedded_pdf_equals_approved':True,'pair_sha256':EXPECTED,'palette_values_match':colors(local),'editable_drawings':drawings,'canonical_path':str(canonical.relative_to(ROOT)),'authoritative_chapters':str((source/'chapters').relative_to(ROOT)),'clean_source_directory':str(clean),'clean_source_contains_prebuilt_report_pdf':False,'new_model_calls':0,'new_method_runs':0}
 (EV/'source-archive-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'clean_source_directory':str(clean),'members':len(records),'drawings':drawings},ensure_ascii=False))
