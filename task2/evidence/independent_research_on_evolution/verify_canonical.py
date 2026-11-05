"""Independent canonical metrics audit; no execution metric routines used."""
from pathlib import Path
import hashlib
import json
import numpy as np
from verify_evolution import ROOT, box_union, digest


def exact_metrics(F, ideal, nadir, decimals):
    unique = np.unique(np.round(F,decimals),axis=0)
    # Deliberately explicit pairwise reference, independent of sorting implementation.
    front = []
    for a in unique:
        if not any(np.all(b<=a) and np.any(b<a) for b in unique):
            front.append(a)
    front = np.array(front)
    norm = (front-ideal)/np.maximum(nadir-ideal,1e-12)
    hv = box_union(norm,np.full(len(ideal),1.1))
    if len(norm)<2:
        sp=None
    else:
        nearest=np.array([min(np.abs(a-b).sum() for k,b in enumerate(norm) if k!=j) for j,a in enumerate(norm)])
        sp=float(nearest.std()/nearest.mean()) if nearest.mean()>0 else None
    return {'HV':hv,'Spacing_cv':sp,'front':front,'canonical_nondominated':len(front)}


def main():
    packet_path=ROOT/'results/evolution/metrics.json'
    packet_bytes=packet_path.read_bytes()
    packet_hash=hashlib.sha256(packet_bytes).hexdigest()
    snapshot=Path(__file__).parent/('metrics_input_'+packet_hash[:12]+'.json')
    if not snapshot.exists():snapshot.write_bytes(packet_bytes)
    packet=json.loads(packet_bytes)
    reviewed=[]
    for row in packet['rows']:
        raw_path=ROOT.parent/row['path']
        assert digest(raw_path)==row['raw_sha256']
        raw=json.loads(raw_path.read_text())
        F=np.array([i['F'] for i in raw['runs']]) if 'runs'in raw else np.array(raw['F'])
        ideal,nadir=np.array(raw['ideal']),np.array(raw['nadir'])
        for decimals in [8,10,12]:
            expected=exact_metrics(F,ideal,nadir,decimals)
            actual=row['metrics'] if decimals==10 else row['numerical_sensitivity'][str(decimals)]
            assert abs(expected['HV']-actual['HV'])<1e-9
            assert expected['Spacing_cv']==actual['Spacing_cv'] if expected['Spacing_cv'] is None else abs(expected['Spacing_cv']-actual['Spacing_cv'])<1e-9
            assert expected['canonical_nondominated']==actual['canonical_nondominated']
            assert np.array_equal(expected['front'],actual['front'])
        reviewed.append({'path':row['path'],'raw_sha256':row['raw_sha256']})
    receipt={'reviewer':'/root/research_data','status':'PASS_SCOPE_LIMITED','packet_sha256':packet_hash,
             'packet_snapshot':str(snapshot.relative_to(ROOT.parent)),
             'evaluator_sha256':packet['evaluator_sha256'],'records':len(reviewed),'precisions':[8,10,12],
             'expected_implementation':'explicit pairwise dominance and coordinate-compressed union of boxes',
             'reviewed':reviewed,'limits':['Only this exact metric packet and indexed raw hashes reviewed; later stages require additive audit.']}
    destination=Path(__file__).parent/'canonical_result.json'
    if destination.exists():
        history=destination.with_name('canonical_result_previous_'+digest(destination)[:12]+'.json')
        if not history.exists():history.write_bytes(destination.read_bytes())
    destination.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','records','precisions']},indent=2))


if __name__=='__main__':
    main()
