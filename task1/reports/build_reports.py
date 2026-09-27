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
sys.path.insert(0, str(ROOT))
from task1.goal3.identity import write_report_metadata
REPORTS = ROOT/'task1/reports'
EVIDENCE = ROOT/'task1/evidence/goal3/report_build'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true', help='Render every PDF page at 200 dpi into the report evidence directory.')
    args=parser.parse_args()
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    write_report_metadata(ROOT)
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
        (EVIDENCE/(stem+'_pdfinfo.txt')).write_text(info, encoding='utf8')
        extracted=EVIDENCE/(stem+'_text.txt')
        page_text=extracted.read_text(encoding='utf8').split('\f')
        if page_text and not page_text[-1].strip(): page_text.pop()
        if len(page_text)!=pages: raise RuntimeError(f'{stem}: text page mismatch')
        from task1.goal3.identity import read_identity
        identity=read_identity(ROOT)
        for field in ('student_name','student_id'):
            if identity[field] not in page_text[0] or identity[field] not in info:
                raise RuntimeError(f'{stem}: missing cover/PDF metadata identity {field}')
        if any(token in page_text[0] for token in ('待补姓名','待补学号','正式身份待补')):
            raise RuntimeError(f'{stem}: stale identity placeholder')
        paginated=EVIDENCE/(stem+'_pages.txt')
        paginated.write_text('\n'.join(f'===== PDF物理页 {i} =====\n{text}' for i,text in enumerate(page_text,1)),encoding='utf8')
        record={'report':folder,'pdf':str((cwd/f'{stem}.pdf').relative_to(ROOT)),'sha256':sha(pdf),'pages':pages,'command':cmd,'compile_exit_code':result.returncode,'unresolved_diagnostics':forbidden,'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(cwd.rglob('*')) if p.is_file() and 'build' not in p.parts and p.suffix in {'.tex','.bib'}},'render':None}
        record['text']={'path':str(extracted.relative_to(ROOT)),'sha256':sha(extracted),
            'paginated_path':str(paginated.relative_to(ROOT)),'paginated_sha256':sha(paginated),
            'command':['pdftotext','-layout',str((cwd/f'{stem}.pdf').relative_to(ROOT)),str(extracted.relative_to(ROOT))],
            'page_text_sha256':{str(i):hashlib.sha256(t.encode('utf8')).hexdigest() for i,t in enumerate(page_text,1)}}
        record['identity_check']='VERIFIED_COVER_AND_PDF_METADATA'
        if args.render:
            render=EVIDENCE/'render200'/folder
            render.mkdir(parents=True,exist_ok=True)
            for old in render.glob('page-*.png'): old.unlink()
            subprocess.run(['pdftoppm','-r','200','-png',str(pdf),str(render/'page')],check=True)
            images=sorted(render.glob('page-*.png'))
            if len(images)!=pages: raise RuntimeError(f'{stem}: render page mismatch')
            record['render']={'dpi':200,'pages':len(images),'page_sha256':{str(p.relative_to(ROOT)):sha(p) for p in images}}
            record['render']['command']=['pdftoppm','-r','200','-png',record['pdf'],str((render/'page').relative_to(ROOT))]
            record['render']['visual_review_status']='NOT_VISUALLY_REVIEWED_BY_BUILD_SCRIPT'
        receipt['reports'].append(record)
    receipt['shared_source_sha256']={str(p.relative_to(ROOT)):sha(p) for p in [REPORTS/'metadata.tex',REPORTS/'history_values.tex',ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex']}
    receipt['finished_at']=datetime.now(timezone.utc).isoformat()
    (EVIDENCE/'build_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'COMPILED_REVIEW_REPORTS','reports':[(r['report'],r['pages']) for r in receipt['reports']],'render200':args.render,'new_model_calls':0},ensure_ascii=False))

if __name__=='__main__': main()
