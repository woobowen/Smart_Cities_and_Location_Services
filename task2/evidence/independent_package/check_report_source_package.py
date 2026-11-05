"""Independent isolated compile and200dpi content comparison of an explicit sourceZIP."""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,concurrent.futures,hashlib,json,shutil,stat,subprocess,zipfile
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle',type=Path,required=True);parser.add_argument('--run',type=Path,required=True);args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[3]
if args.run.exists():parser.error('Use a fresh review directory; existing review evidence is retained')
run=args.run.resolve();build=run/'build';extracted=build/'source';reference=build/'reference';run.mkdir(parents=True);reference.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with zipfile.ZipFile(args.bundle) as z:
 members=z.infolist();seen=set()
 for info in members:
  p=PurePosixPath(info.filename)
  if p.is_absolute() or '..' in p.parts or info.filename in seen or stat.S_ISLNK(info.external_attr>>16):raise RuntimeError('Unsafe archive member')
  if p.suffix.lower() in {'.otf','.ttf','.ttc','.woff','.woff2'}:raise RuntimeError('Fontbinarydisallowedinsourcepackage')
  seen.add(info.filename)
 z.extractall(extracted)
for folder,label in [('experiment','Experiment_Report'),('process','Process_Report')]:
 p=extracted/f'task2/reports/{folder}/{label}.pdf';shutil.copyfile(p,reference/(label+'.pdf'))
manifest=json.loads((extracted/'SOURCE_PACKAGE_MANIFEST.json').read_text())
(run/'archive_inspection.json').write_text(json.dumps(dict(bundle=str(args.bundle),sha256=sha(args.bundle),members=len(members),member_paths=sorted(seen),package_manifest=manifest),ensure_ascii=False,indent=2))

def execute(folder,label):
 cwd=extracted/f'task2/reports/{folder}'
 cmd=['latexmk','-xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-jobname='+label,'main.tex']
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);(run/(label+'_compile.log')).write_text(p.stdout+'\n'+p.stderr)
 if p.returncode:raise RuntimeError(label+'compile failed; see actual log')
 rebuilt=cwd/(label+'.pdf');original=reference/(label+'.pdf')
 texts={}
 for identity,pdf in [('reference',original),('rebuilt',rebuilt)]:
  text=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,check=True).stdout;texts[identity]=text;(run/(label+'_'+identity+'.txt')).write_bytes(text)
  pngdir=build/label/identity;pngdir.mkdir(parents=True)
  subprocess.run(['pdftoppm','-r','200','-png',str(pdf),str(pngdir/'page')],capture_output=True,check=True)
 from PIL import Image,ImageChops
 left=sorted((build/label/'reference').glob('page-*.png'));right=sorted((build/label/'rebuilt').glob('page-*.png'))
 assert len(left)==len(right)
 pages=[]
 for i,(a,b) in enumerate(zip(left,right),1):
  with Image.open(a) as x,Image.open(b) as y:
   equal=x.size==y.size and ImageChops.difference(x.convert('RGB'),y.convert('RGB')).getbbox() is None
   pages.append(dict(page=i,size=list(x.size),pixels_equal=equal,reference_png_sha256=sha(a),rebuilt_png_sha256=sha(b),rebuilt_path=str(b.relative_to(ROOT))))
 texlog=(cwd/(label+'.log')).read_text(errors='replace')
 warnings=[line for line in texlog.splitlines() if any(x in line.lower() for x in ['undefined reference','undefined citation','missing character','overfull','font warning','fatal error'])]
 return dict(label=label,compile_command=cmd,returncode=p.returncode,reference_pdf_sha256=sha(original),rebuilt_pdf_sha256=sha(rebuilt),binary_pdf_equal=sha(original)==sha(rebuilt),full_text_equal=texts['reference']==texts['rebuilt'],pages=len(pages),dpi=200,page_comparisons=pages,material_log_matches=warnings)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda item:execute(*item),[('experiment','Experiment_Report'),('process','Process_Report')]))
assert all(r['full_text_equal'] and all(p['pixels_equal'] for p in r['page_comparisons']) for r in results)
report=dict(reviewer='/root/reinforcement, independent ofreportauthor/generator',bundle_sha256=sha(args.bundle),scope='Actualisolatedtrustedsourcecompilationwithoutoriginalrepositoryfigures,dataorpersonalabsoluteinputpaths; fulltext/pagecount/200dpipixelscompared. Humanvisualinspectionisrecordedseparatelyafteropeningpages.',actual_utc=datetime.now(timezone.utc).isoformat(),reports=results,status='COMPILED_TEXT_AND_RENDER_EQUIVALENT_VISUAL_REVIEW_PENDING')
(run/'compile_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({r['label']:dict(pages=r['pages'],text=r['full_text_equal'],all_pixels_equal=all(p['pixels_equal'] for p in r['page_comparisons']),pdf_binary_equal=r['binary_pdf_equal']) for r in results},indent=2))
