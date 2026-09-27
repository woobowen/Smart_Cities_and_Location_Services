"""Compile the two honest review reports from local, verified inputs."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT/'task1/reports'
EVIDENCE = ROOT/'task1/evidence/goal3/report_build'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true', help='Render every PDF page at 200 dpi into the report evidence directory.')
    args=parser.parse_args()
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(REPORTS/'build_history_sources.py')],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(REPORTS/'build_goal3_sources.py')],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(REPORTS/'build_selection_sources.py')],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(REPORTS/'build_final_sources.py')],cwd=ROOT,check=True)
    receipt={'started_at':datetime.now(timezone.utc).isoformat(),'classification':'REPORT_BUILD_NOT_METHOD_EXECUTION','new_model_calls':0,'new_method_runs':0,'reports':[],'installed_dependencies':[],'visual_inspection':'NOT_PERFORMED_BY_THIS_SCRIPT'}
    for folder,stem in [('experiment1','experiment1'),('process1','process1')]:
        cwd=REPORTS/folder
        cmd=['latexmk','-xelatex','-interaction=nonstopmode','-file-line-error','-halt-on-error','-outdir=build',stem+'.tex']
        result=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
        (EVIDENCE/(stem+'_compile_output.txt')).write_text(result.stdout+result.stderr)
        if result.returncode: raise RuntimeError(f'{stem}: latexmk exit {result.returncode}')
        log=(cwd/'build'/f'{stem}.log').read_text(errors='replace')
        forbidden=[x for x in log.splitlines() if re.search(r'^!|Missing character|undefined|Overfull|LaTeX Font Warning|There were undefined',x)]
        if forbidden: raise RuntimeError(f'{stem}: unresolved report diagnostics: {forbidden}')
        pdf=cwd/'build'/f'{stem}.pdf'
        shutil.copyfile(pdf,cwd/f'{stem}.pdf')
        subprocess.run(['pdftotext','-layout',str(pdf),str(EVIDENCE/(stem+'_text.txt'))],check=True)
        info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True).stdout
        pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        record={'report':folder,'pdf':str((cwd/f'{stem}.pdf').relative_to(ROOT)),'sha256':sha(pdf),'pages':pages,'command':cmd,'compile_exit_code':result.returncode,'unresolved_diagnostics':forbidden,'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(cwd.rglob('*')) if p.is_file() and 'build' not in p.parts and p.suffix in {'.tex','.bib'}},'render':None}
        if args.render:
            render=EVIDENCE/'render200'/folder
            render.mkdir(parents=True,exist_ok=True)
            for old in render.glob('page-*.png'): old.unlink()
            subprocess.run(['pdftoppm','-r','200','-png',str(pdf),str(render/'page')],check=True)
            images=sorted(render.glob('page-*.png'))
            if len(images)!=pages: raise RuntimeError(f'{stem}: render page mismatch')
            record['render']={'dpi':200,'pages':len(images),'page_sha256':{str(p.relative_to(ROOT)):sha(p) for p in images}}
        receipt['reports'].append(record)
    receipt['shared_source_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [REPORTS/'metadata.tex',REPORTS/'history_values.tex',ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex']}
    receipt['finished_at']=datetime.now(timezone.utc).isoformat()
    (EVIDENCE/'build_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'COMPILED_REVIEW_REPORTS','reports':[(r['report'],r['pages']) for r in receipt['reports']],'render200':args.render,'new_model_calls':0},ensure_ascii=False))

if __name__=='__main__': main()
