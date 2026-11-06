"""Compile both task-specific XeLaTeX reports, extract/check text, render every page at200dpi.

Rendering is recorded as rendering. Human/agent visual inspection is a separate
receipt and is never auto-invented by this script.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from xml.sax.saxutils import escape

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[2]


def verify_approved_process(evidence):
    """Compile to an isolated output directory and preserve the accepted PDF."""
    folder=ROOT/'task2/reports/process'
    approved=folder/'Process_Report.pdf'
    approved_bytes=approved.read_bytes()
    render=evidence/'build/process'
    render.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='smartcities-process-') as temporary:
        build=Path(temporary)
        # XeTeX can resolve the automatic CJK bold face to Black when that
        # extra weight is installed. The accepted PDF embeds Bold. Filter only
        # the competing Black file in this process; keep the TeX and system
        # font configuration unchanged.
        font_files=subprocess.check_output(['fc-list','-f','%{file}\n'],text=True).splitlines()
        excluded=sorted({path for path in font_files if Path(path).name=='NotoSansCJK-Black.ttc'})
        config=build/'fonts.conf'
        base_config=os.environ.get('FONTCONFIG_FILE','/etc/fonts/fonts.conf')
        config.write_text('<?xml version="1.0"?>\n<fontconfig><include ignore_missing="no">'+
            escape(base_config)+'</include><selectfont><rejectfont>'+''.join(
            '<pattern><patelt name="file"><string>'+escape(path)+
            '</string></patelt></pattern>' for path in excluded)+
            '</rejectfont></selectfont></fontconfig>\n')
        environment=dict(os.environ,FONTCONFIG_FILE=str(config))
        command=['latexmk','-norc','-g','-xelatex','-latexoption=-no-shell-escape',
                 '-interaction=nonstopmode','-file-line-error','-halt-on-error',
                 '-outdir='+str(build),'main.tex']
        run=subprocess.run(command,cwd=folder,env=environment,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        # The temporary directory is deliberately not part of the public log.
        (evidence/'process_compile.txt').write_text(run.stdout.replace(str(build),'<isolated-build>'))
        if run.returncode:
            raise RuntimeError('Process compilation failed; see process_compile.txt')
        compiled=build/'main.pdf'
        log=(build/'main.log').read_text(errors='replace')
        issues=[line for line in log.splitlines() if re.search(
            r'^!|undefined references|undefined citations|Citation .*undefined|Reference .*undefined|Missing character:|Overfull \\hbox|Overfull \\vbox|Font .*substitut|Rerun to get',line,re.I)]
        texts=[];pages=[]
        for label,pdf in [('approved',approved),('compiled',compiled)]:
            info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
            (evidence/('process_'+label+'_pdfinfo.txt')).write_text(info)
            pages.append(int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1)))
            text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'])
            texts.append(text)
            (evidence/('process_'+label+'_text.txt')).write_bytes(text)
            destination=render/label;destination.mkdir(exist_ok=True)
            subprocess.run(['pdftoppm','-r','200','-png',str(pdf),str(destination/'page')],check=True)
        comparisons=[]
        for number in range(1,pages[0]+1):
            name='page-'+str(number).zfill(len(str(pages[0])))+'.png'
            with Image.open(render/'approved'/name) as left,Image.open(render/'compiled'/name) as right:
                equal=left.size==right.size and ImageChops.difference(left.convert('RGB'),right.convert('RGB')).getbbox() is None
                comparisons.append(dict(page=number,pixels=list(left.size),rgb_pixels_equal=equal))
        record=dict(kind='process',command=[part.replace(str(build),'<isolated-build>') for part in command],
            returncode=run.returncode,pages=pages[0],compiled_pages=pages[1],
            pdf=str(approved.relative_to(ROOT)),sha256=hashlib.sha256(approved_bytes).hexdigest(),
            compiled_pdf_sha256=hashlib.sha256(compiled.read_bytes()).hexdigest(),
            font_environment=dict(scope='Temporary config for this compile process only',
                excluded_competing_weights=[Path(path).name for path in excluded],
                reason='Match the Noto Sans CJK Bold embedded in the accepted PDF'),
            approved_pdf_unchanged=approved.read_bytes()==approved_bytes,
            full_text_equal=texts[0]==texts[1],render_dpi=200,page_comparisons=comparisons,
            log_issues=issues,visual_inspection='PENDING_SEPARATE_ACTUAL_PAGE_REVIEW',
            recorded_utc=datetime.now(timezone.utc).isoformat())
        (evidence/'process_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        if (issues or pages[0]!=pages[1] or texts[0]!=texts[1] or
                not record['approved_pdf_unchanged'] or not all(row['rgb_pixels_equal'] for row in comparisons)):
            raise RuntimeError('Process source/PDF verification differs; accepted PDF was preserved')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=['experiment','process','both'],default='both')
    parser.add_argument('--evidence-dir',type=Path,default=ROOT/'task2/evidence/report_build')
    args=parser.parse_args()
    evidence=args.evidence_dir.resolve();evidence.mkdir(parents=True,exist_ok=True)
    records=[]
    for kind in (['experiment','process'] if args.kind=='both' else [args.kind]):
        if kind=='process':
            records.append(verify_approved_process(evidence))
            print('process: approved PDF preserved; isolated source, text and 200-dpi pixels match',flush=True)
            continue
        folder=ROOT/'task2/reports'/kind
        command=['latexmk','-g','-xelatex','-interaction=nonstopmode','-file-line-error','-halt-on-error','-outdir=build','main.tex']
        run=subprocess.run(command,cwd=folder,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (evidence/(kind+'_compile.txt')).write_text(run.stdout)
        if run.returncode:
            print(kind,'compilation FAILED; see',evidence/(kind+'_compile.txt'));raise SystemExit(run.returncode)
        log=(folder/'build/main.log').read_text(errors='replace')
        issues=[line for line in log.splitlines() if re.search(r'undefined references|undefined citations|Citation .*undefined|Reference .*undefined|Missing character:|Overfull \\hbox|Overfull \\vbox|Font .*substitut',line,re.I)]
        target=folder/('Experiment_Report.pdf' if kind=='experiment' else 'Process_Report.pdf')
        shutil.copyfile(folder/'build/main.pdf',target)
        info=subprocess.check_output(['pdfinfo',str(target)],text=True)
        (evidence/(kind+'_pdfinfo.txt')).write_text(info)
        subprocess.run(['pdftotext','-layout',str(target),str(evidence/(kind+'_text.txt'))],check=True)
        render=ROOT/'task2/evidence/report_render'/kind;render.mkdir(parents=True,exist_ok=True)
        subprocess.run(['pdftoppm','-r','200','-png',str(target),str(render/'page')],check=True)
        pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        images=sorted(render.glob('page-*.png'))
        if len(images)!=pages:raise ValueError('render/page count mismatch')
        records.append(dict(kind=kind,command=command,returncode=run.returncode,pages=pages,
           pdf=str(target.relative_to(ROOT)),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
           render_dpi=200,rendered_pages=len(images),log_issues=issues,
           visual_inspection='PENDING_SEPARATE_ACTUAL_PAGE_REVIEW',recorded_utc=datetime.now(timezone.utc).isoformat()))
        print(kind,pages,'pages; log issues',len(issues),flush=True)
    (evidence/'build_receipt.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    if any(x['log_issues'] for x in records):raise SystemExit('Resolve the recorded typography/reference issues before acceptance')


if __name__=='__main__':main()
