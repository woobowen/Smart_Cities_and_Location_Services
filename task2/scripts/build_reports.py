"""Compile both task-specific XeLaTeX reports, extract/check text, render every page at200dpi.

Rendering is recorded as rendering. Human/agent visual inspection is a separate
receipt and is never auto-invented by this script.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    evidence=ROOT/'task2/evidence/report_build';evidence.mkdir(parents=True,exist_ok=True)
    records=[]
    for kind in ['experiment','process']:
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
