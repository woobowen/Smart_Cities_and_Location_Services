from pathlib import Path
import subprocess,os,re,json,sys,traceback
R=Path(__file__).resolve().parents[1];(R/'build').mkdir(exist_ok=True)
env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1790899200',FORCE_SOURCE_DATE='1')
steps=[]
def run(cmd):
 p=subprocess.run(cmd,cwd=R,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 steps.append(dict(command=cmd,returncode=p.returncode,tail=p.stdout[-5000:]))
 (R/'provenance/final_build_steps.json').write_text(json.dumps(steps,ensure_ascii=False,indent=2))
 return p
try:
 for script in ['recover_assets.py','make_diagrams.py','build_report.py']:
  p=run([sys.executable,'tools/'+script])
  if p.returncode:raise RuntimeError(script+'\n'+p.stdout[-4000:])
 tex=R/'chapters/pages.tex';s=tex.read_text();s=re.sub(r'\\selectfont(?=[^\\\s])',r'\\selectfont ',s);tex.write_text(s)
 # Compile, with an explicit whitespace repair and local-font fallback if needed.
 for attempt in range(3):
  p=run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'])
  (R/'build/compile_stdout_final.log').write_text(p.stdout)
  if p.returncode==0:break
  if 'font' in p.stdout.lower() and ('cannot be found' in p.stdout or 'not found' in p.stdout):
   main=R/'main.tex';t=main.read_text().replace('{Noto Sans CJK SC}','{FandolHei-Regular.otf}').replace('{Noto Sans}','{TeX Gyre Heros}');main.write_text(t)
  elif 'selectfont' in p.stdout:
   s=tex.read_text().replace('\\selectfont','\\selectfont ');tex.write_text(s)
  else:raise RuntimeError('XeLaTeX failed\n'+p.stdout[-4000:])
 if p.returncode:raise RuntimeError('Cannot compile after repair attempts')
 p=run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex']);assert p.returncode==0,p.stdout[-3000:]
 p=run([sys.executable,'tools/render_review.py']);assert p.returncode==0,p.stdout[-3000:]
 p=run([sys.executable,'tools/audit_report.py']);assert p.returncode==0,p.stdout[-3000:]
 import fitz
 doc=fitz.open(R/'build/main.pdf');assert len(doc)>50
 (R/'provenance/BUILD_COMPLETE.json').write_text(json.dumps(dict(complete=True,pages=len(doc),all_pages_rendered=True),indent=2))
 print('BUILD_COMPLETE',len(doc))
except Exception:
 (R/'provenance/BUILD_FAILURE.txt').write_text(traceback.format_exc());raise
