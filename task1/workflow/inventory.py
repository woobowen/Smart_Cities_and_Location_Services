"""Reproducible full RAW structure inventory; never a full cleaning experiment."""
import csv
import hashlib
from pathlib import Path
import zipfile

from .io import ROOT, DATA, EVIDENCE, digest, read_json, write_json, now, relative
from .diagnostics import profile, aggregate


def run_inventory():
    out=EVIDENCE/'inventory'
    out.mkdir(parents=True,exist_ok=True)
    before=digest(DATA)
    raw=read_json(DATA)
    rows=[profile(k,v) for k,v in raw.items()]
    summary=aggregate(rows)
    summary.update(classification='FULL_DATASET_RAW_STRUCTURE_ONLY',raw_path=relative(DATA),
                   raw_sha256=before,created_at=now(),source_unit='Unix seconds SOURCE_DECLARED; CRS UNKNOWN',
                   exposure='All records structurally observed; no physical quality inference or method tuning')
    write_json(out/'structure_summary.json',summary)
    fields=[k for k in rows[0] if k not in ('dt_counts','issues')]
    with (out/'record_profiles.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields+['issues'])
        writer.writeheader()
        for row in rows:
            writer.writerow({k:('|'.join(row[k]) if k=='issues' else row[k]) for k in fields+['issues']})
    paths=[ROOT/'AGENTS.md', *sorted((ROOT/'docs').rglob('*.md')),
           ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex',
           ROOT/'templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf',
           ROOT/'templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf',
           *sorted((ROOT/'tools/skills/publication-plots').rglob('*.md')),
           ROOT/'task1/实验课1.pptx', ROOT/'task1/作业.zip',
           *sorted((ROOT/'task1/作业/作业').rglob('*'))]
    materials=[]
    for p in paths:
        if not p.is_file() or p.is_symlink() or any(x in p.parts for x in ('__pycache__','.pytest_cache','.ipynb_checkpoints')):
            continue
        if p.name.startswith('._') or p.name.endswith(':Zone.Identifier'):
            continue
        rel=relative(p)
        kind='ACTIVE_GOVERNANCE_OR_TEMPLATE'
        if rel.startswith('task1/'):
            kind='TEACHER_PROVIDED_PACKAGE'
            if '/demo_out/' in rel or '/figures/' in rel or '/build_ppt' in rel:
                kind='HISTORICAL_OR_PREGENERATED_STARTER'
            elif p.suffix in ('.py','.ipynb','.md'):
                kind='STARTER_SOURCE'
            elif p.name=='traj_dict.json':
                kind='TEACHER_PROVIDED_RAW_DATA'
        materials.append({'path':rel,'bytes':p.stat().st_size,'sha256':digest(p),'source_category':kind,
                          'read_status':'HASHED; detailed reading coverage in materials/reading_coverage.json'})
    write_json(out/'materials.json',materials)
    comparisons=[]
    with zipfile.ZipFile(ROOT/'task1/作业.zip') as z:
        for entry in z.infolist():
            if entry.is_dir():continue
            candidate=ROOT/'task1/作业'/entry.filename
            b=z.read(entry)
            comparisons.append({'zip_member':entry.filename,'sha256':hashlib.sha256(b).hexdigest(),
                                'bytes':len(b),'extracted_path':relative(candidate),
                                'exists':candidate.is_file(),'equal_bytes':candidate.is_file() and candidate.read_bytes()==b})
    write_json(out/'zip_byte_comparison.json',comparisons)
    duplicate=ROOT/'task1/作业/作业/utils/traj_dict.json'
    write_json(out/'raw_integrity.json',{'primary':relative(DATA),'duplicate':relative(duplicate),
               'sha256_before':before,'sha256_after':digest(DATA),'duplicate_sha256':digest(duplicate),
               'same_bytes':DATA.read_bytes()==duplicate.read_bytes()})
    return summary


if __name__=='__main__':
    summary=run_inventory()
    print({k:v for k,v in summary.items() if k!='dt_counts'})
