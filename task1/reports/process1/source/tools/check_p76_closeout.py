"""Verify the scoped p76 repair without experiments, OCR, or changing raw images.

Run after compilation. Optional historical inputs enable byte/pixel regression.
This is an author-side artifact check; it does not invent human acceptance/locks.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile
import fitz
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OLD_PDF_SHA = '45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83'
OLD_ZIP_SHA = '00cb7b641b37b2a71a552fc5bef47fc551a16ea7ce88bcf139f2e68a5f1451da'

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-pdf', type=Path)
    parser.add_argument('--baseline-source-zip', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'provenance/closeout_p76/artifact_check.json')
    args = parser.parse_args()
    checks: list[dict] = []
    def ck(name: str, okay: bool, details=None) -> None:
        checks.append({'check': name, 'passed': bool(okay), 'details': details})
    p = ROOT/'Process_Report_Revised.pdf'
    spec = json.loads((ROOT/'content/closing_evidence.json').read_text())
    mapping = json.loads((ROOT/'provenance/closing_crop_map.json').read_text())
    ck('Closing source SHA256 matches explicit contract', digest(ROOT/spec['source']) == spec['source_sha256'])
    ck('Closing crop SHA256 matches generated record', digest(ROOT/spec['image']) == mapping['crop_sha256'])
    crop_results = []
    regular = json.loads((ROOT/'provenance/crop_map.json').read_text())
    for row in regular + [spec]:
        with Image.open(ROOT/row['source']) as raw, Image.open(ROOT/row['image']) as cut:
            box = tuple(row['box'])
            bounded = 0 <= box[0] < box[2] <= raw.width and 0 <= box[1] < box[3] <= raw.height
            pixel_equal = np.array_equal(np.asarray(raw.crop(box).convert('RGB')), np.asarray(cut.convert('RGB')))
            crop_results.append({'image': row['image'], 'bounded': bounded, 'original_pixels_equal': pixel_equal})
    ck('Every regular crop and the closing crop is lossless', all(c['bounded'] and c['original_pixels_equal'] for c in crop_results), len(crop_results))
    ck('Full closing user bubble selected, reply excluded', spec['box'] == [186,68,510,263], 'Bounds approved from actual raw-image inspection; semantics also require visual review.')
    ck('Closing display width preserved', mapping['display_mm'][0] == 136.5)
    ck('Real effective PPI preserved as native-width approval', abs(mapping['effective_ppi']-324/(136.5/25.4))<1e-10 and mapping['resolution_status']=='APPROVED_NATIVE_WIDTH', mapping['effective_ppi'])
    tex = (ROOT/'chapters/pages.tex').read_text()
    ck('No new circles, boxes or translucent text overlays', not any(t in tex for t in ['fill opacity','draw opacity','\\fill[','\\filldraw',' circle (',' rectangle (']))
    doc = fitz.open(p)
    ck('Complete report remains 77 A4 pages', len(doc)==77 and all(abs(pg.rect.width-595.276)<2 and abs(pg.rect.height-841.89)<2 for pg in doc))
    ck('Compiled PDF and delivered PDF match', digest(ROOT/'build/main.pdf')==digest(p))
    log=(ROOT/'build/main.log').read_text(errors='replace')
    bad=[s for s in log.splitlines() if any(v in s for v in ['Missing character:','Undefined control sequence','Overfull \\hbox','Overfull \\vbox','undefined references','undefined citations'])]
    ck('No unresolved glyph, command, overflow or reference diagnostics', not bad, bad)
    previous_diff=[]
    if args.baseline_source_zip:
        ck('Historical source archive has expected immutable SHA256', digest(args.baseline_source_zip)==OLD_ZIP_SHA)
        with zipfile.ZipFile(args.baseline_source_zip) as z:
            ck('Historical source ZIP CRC', z.testzip() is None)
            root='Process_Report_Revised_Source/'
            for member in z.infolist():
                if member.is_dir(): continue
                rel=PurePosixPath(member.filename).relative_to(root).as_posix()
                target=ROOT/rel
                if not target.is_file() or target.read_bytes()!=z.read(member): previous_diff.append(rel)
            protected=[rel for rel in previous_diff if rel.startswith(('assets/raw/','assets/inherited/','provenance/accepted_experiment/','figures/')) or rel in ['main.tex','chapters/pages.tex','content/evidence_units.json','content/diagrams.json','provenance/crop_map.json','provenance/arrow_map.json','provenance/page_map.json','compile.sh','requirements-build.txt']]
            ck('Raw, inherited UI, complete text, 40-unit/85-arrow specs, six figures and experimental references unchanged', not protected, protected)
    page_comparison=[]
    if args.baseline_pdf:
        ck('Historical PDF has expected immutable SHA256', digest(args.baseline_pdf)==OLD_PDF_SHA)
        before=fitz.open(args.baseline_pdf)
        ck('All native PDF text and page geometry unchanged', len(before)==len(doc) and all(a.get_text()==b.get_text() and a.rect==b.rect for a,b in zip(before,doc)))
        for i,(a,b) in enumerate(zip(before,doc),1):
            ap=a.get_pixmap(dpi=200,alpha=False)
            bp=b.get_pixmap(dpi=200,alpha=False)
            aa=np.frombuffer(ap.samples,dtype=np.uint8).reshape(ap.height,ap.width,ap.n)
            bb=np.frombuffer(bp.samples,dtype=np.uint8).reshape(bp.height,bp.width,bp.n)
            changed=np.any(aa!=bb,axis=2)
            ys,xs=np.nonzero(changed)
            bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
            page_comparison.append({'page':i,'pixels_equal':not bool(len(xs)),'changed_pixels':int(len(xs)),'difference_bbox_pixels':bbox})
        changed_pages=[r['page'] for r in page_comparison if not r['pixels_equal']]
        ck('Only physical page 76 changes at 200 dpi', changed_pages==[76], changed_pages)
        r=page_comparison[75]
        bbox=r['difference_bbox_pixels']
        # The union of the old/new picture rectangles; leave 2 px for renderer rounding.
        permitted=[int(14/25.4*200)-2,int(74/25.4*200)-2,int(150.5/25.4*200)+3,int(182.0/25.4*200)+3]
        ck('Changed pixels remain inside the p76 screenshot rectangle', bbox is not None and bbox[0]>=permitted[0] and bbox[1]>=permitted[1] and bbox[2]<=permitted[2] and bbox[3]<=permitted[3],{'difference_bbox':bbox,'permitted_bbox':permitted})
    result={'task':'SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001','checked_at':datetime.now(timezone.utc).isoformat(),'role':'AUTHOR_SELF_CHECK','independent_review':'NOT_CLAIMED','pdf_sha256':digest(p),'page_count':len(doc),'regular_crops':len(regular),'closing_crops':1,'crop_checks':crop_results,'checks':checks,'changed_existing_source_members':previous_diff,'page_comparison_200dpi':page_comparison,'all_checks_pass':all(c['passed'] for c in checks),'historical_evidence_lock':'UNCHANGED_NOT_INFERRED_FROM_BUILD','new_model_calls':0,'new_trajectory_runs':0}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'all_checks_pass':result['all_checks_pass'],'checks':len(checks),'pdf_sha256':result['pdf_sha256'],'output':str(args.output)},ensure_ascii=False))
    if not result['all_checks_pass']: raise SystemExit(1)

if __name__=='__main__': main()
