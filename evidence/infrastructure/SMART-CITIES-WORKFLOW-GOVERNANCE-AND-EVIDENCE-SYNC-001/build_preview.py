"""Clean-build and render the approved Process template; does not refresh the canonical preview automatically."""
from pathlib import Path
import subprocess,json,shutil
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001'; wd=root/'templates/latex/process-report';records=[]
for cmd,name in [(['latexmk','-C','-outdir=build','process_report_template.tex'],'clean-console.txt'),(['latexmk','-xelatex','-interaction=nonstopmode','-file-line-error','-halt-on-error','-outdir=build','process_report_template.tex'],'build-console.txt')]:
 r=subprocess.run(cmd,cwd=wd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/name).write_text('\n'.join(line.rstrip() for line in r.stdout.splitlines()).rstrip() + ('\n' if r.stdout else ''));records.append({'cwd':'templates/latex/process-report','command':cmd,'exit_code':r.returncode});print(name,r.returncode)
 if r.returncode:print(r.stdout[-2500:]);raise SystemExit(r.returncode)
(out/'compile-commands.json').write_text(json.dumps(records,indent=2)+'\n');(out/'latex-log.txt').write_text('\n'.join(line.rstrip() for line in (wd/'build/process_report_template.log').read_text().splitlines()).rstrip()+'\n')
pdf=wd/'build/process_report_template.pdf';dest=wd/'build/render';dest.mkdir(exist_ok=True);records=[]
for cmd,name in [(['pdfinfo',str(pdf)],'pdfinfo.txt'),(['pdftotext','-layout',str(pdf),'-'],'pdf-text.txt'),(['pdfimages','-list',str(pdf)],'pdf-images.txt'),(['pdftoppm','-r','200','-png',str(pdf),str(dest/'page')],'render-console.txt'),(['pdftocairo','-f','5','-l','5','-svg',str(pdf),str(dest/'micro-trace.svg')],'vector-console.txt')]:
 r=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/name).write_text('\n'.join(line.rstrip() for line in r.stdout.splitlines()).rstrip() + ('\n' if r.stdout else ''));records.append({'command':cmd,'exit_code':r.returncode});print(cmd[0],r.returncode)
 if r.returncode:raise SystemExit(r.returncode)
(out/'render-commands.json').write_text(json.dumps(records,indent=2)+'\n')
pages=sorted(dest.glob('page-*.png'));thumbs=[]
for p in pages:
 im=Image.open(p).convert('RGB');im.thumbnail((414,586));tile=Image.new('RGB',(434,616),'#dddddd');tile.paste(im,((434-im.width)//2,20));ImageDraw.Draw(tile).text((12,599),p.stem,fill='black');thumbs.append(tile)
for start in range(0,len(thumbs),6):
 board=Image.new('RGB',(434*3,616*2),'white')
 for i,t in enumerate(thumbs[start:start+6]):board.paste(t,((i%3)*434,(i//3)*616))
 board.save(out/f'pages-{start+1:02}-{min(start+6,len(thumbs)):02}.jpg',quality=90)
shutil.copyfile(dest/'page-05.png',out/'micro-trace-200dpi.png')
print('rendered_pages',len(pages))
