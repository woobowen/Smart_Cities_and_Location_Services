"""Reconstruct saved batch orders and training-only driver priors independently."""
from pathlib import Path
import json
import re
import sys
import numpy as np
from verify_evolution import ROOT,digest

sys.path.insert(0,str(ROOT/'src'))
from dispatch_data import load_data


def main():
    data=load_data();reviewed=[]
    for p in sorted((ROOT/'results/evolution/batches').glob('*.npz')):
        match=re.fullmatch(r'(inner|validation|test)_hour(\d+)_batchseed(\d+)',p.stem)
        assert match,p
        partition,hour,seed=match[1],int(match[2]),int(match[3])
        trips={'inner':data.trips_train_inner,'validation':data.trips_validation,'test':data.trips_test}[partition]
        checkins=data.checkins_train if partition=='test' else data.checkins_train_inner
        b=dict(np.load(p));ids=b['trip_indices'].astype(int)
        sample=trips.loc[ids]
        assert (sample.minute//60==hour).all()
        assert np.array_equal(sample[['ox','oy']].to_numpy(),b['o_xy'])
        assert np.array_equal(sample[['dx','dy']].to_numpy(),b['d_xy'])
        assert np.array_equal(sample.fare.to_numpy(),b['fare'])
        hotspots=checkins[checkins.minute//60==hour][['x','y']].to_numpy()
        rng=np.random.default_rng(seed)
        drivers=hotspots[rng.integers(0,len(hotspots),len(b['drv']))]+rng.normal(0,1.,b['drv'].shape)
        assert np.array_equal(drivers,b['drv'])
        reviewed.append({'batch':p.stem,'sha256':digest(p),'partition':partition,
            'orders_source':str(sample.date.min())+' to '+str(sample.date.max()),
            'driver_prior_last_date':str(checkins.date.max()),
            'independently_recreated_driver_array_exact':True})
    receipt={'status':'PASS_SCOPE_LIMITED','reviewer':'/root/research_data','batches':reviewed,
        'source_sha256':data.audit['sha256'],'source_identity':data.audit['source_identity'],
        'rules':'source-trip indices and all OD/fare values exact; drivers reconstructed from training-only hourly checkins and fixed RNG; test never supplies driver prior',
        'limits':'This confirms source partitioning and artifact generation; final contract history is separately recorded by coordinator.'}
    (Path(__file__).parent/'batch_provenance_result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'batches':len(reviewed),'future_test_batches':sum(b['partition']=='test'for b in reviewed)},indent=2))


if __name__=='__main__':main()
