"""C prepares exact reviewed target bindings; only parent B submits the Journal."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'
RUN='g3-full-production-01'


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    names=[RUN+'_'+s+'.json' for s in ['receipt','pairs_receipt','accounting_receipt',
        'freeze_boundary_receipt','categories_receipt','coordinates_receipt','analysis_receipt']]
    names+=['new_coverage_boundary_receipt.json','full_filter_attribution_receipt.json']
    targets={}
    for name in names:
        path=EV/'independent_c'/name;receipt=read(path)
        assert receipt['status']=='VERIFIED' and receipt['role_context']=='/root/c_protocol' and not receipt['errors']
        targets[str(path.relative_to(ROOT))]=sha(path)
        for t in receipt['targets']:
            p=(ROOT/t['path']).resolve()
            assert p.is_relative_to(ROOT) and sha(p)==t['sha256']
            assert t['path'] not in targets or targets[t['path']]==t['sha256']
            targets[t['path']]=t['sha256']
    manifest=read(EV/'runs'/RUN/'manifest.json');sources=dict(manifest['source_hashes'])
    for name in ['task1/goal3/freezes.py','task1/goal3/coordinates.py',
                 'task1/scripts/goal2_coordinate_sensitivity.py','task1/goal3/analysis.py',
                 'task1/goal3/filter_diagnostics.py']:
        sources[name]=sha(ROOT/name)
    assert len(sources)==37
    for name,h in sources.items():assert sha(ROOT/name)==h
    assert 'task1/evidence/goal3/goal_state.json' not in targets,'MUTABLE_JOURNAL_CANNOT_BE_ITS_OWN_TARGET'
    spec={'prepared_by':'/root/c_protocol','task':'production',
        'at':datetime.now(timezone.utc).isoformat(),
        'purpose':'Exact directly bound reviewed payload union; parent performs Journal.submit; no task closure claimed.',
        'targets':[{'path':p,'sha256':h} for p,h in sorted(targets.items())],
        'source_hashes':sources,'review_receipts':names,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/prepare_production_submission.py',
        'checker_sha256':sha(Path(__file__))}
    out=EV/'independent_c/production_review_submission.json'
    with out.open('x') as handle:json.dump(spec,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'targets':len(targets),'sources':len(sources),'spec_sha256':sha(out)}))


if __name__=='__main__':main()
