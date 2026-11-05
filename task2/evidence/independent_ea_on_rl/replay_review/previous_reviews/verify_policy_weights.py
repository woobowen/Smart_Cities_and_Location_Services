"""Supplement independent event replay with actual QKM weights and fusion selections."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import math
import sys
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import t as student_t

from verify_rl import ROOT,TASK,OUT,sha,near,replay,independent_lt


def expected_row(directory,policy,seed):
    rows=json.loads((directory/'day_metrics.json').read_text())
    return next(r for r in rows if r['policy']==policy and r['day_seed']==seed)


def weighted_policy_checks():
    cases=[('double_v2_rngfix/double_b1_s2024_validation','double_v2_rngfix/double_b1_s2024',1.),
           ('double_v2_rngfix/q_b1_s2024_validation','double_validation_v1/q_b1_s2024',1.)]
    receipt=[]
    for directory,model,beta in cases:
        dr=TASK/'results/rl'/directory
        mp=TASK/'results/rl'/model/'model.npz'
        V=np.load(mp)['V']
        assert np.isfinite(V).all() and np.array_equal(V[-1],np.zeros(64))
        LT=independent_lt(V)
        tr=dr/'trace_beta1_50000.json';ep=dr/'episode_50000.npz'
        _,contexts=replay(ep,tr,expected_row(dr,'beta1',50000),LT=LT,beta=beta,check_max_weight=True)
        receipt.append(dict(trace=str(tr.relative_to(ROOT)),trace_sha256=sha(tr),model_sha256=sha(mp),
                            time_slices=len(contexts),independent_maximum_weight_check=True))
    return receipt


def knee_reference(F):
    F=np.asarray(F,float)
    scale=np.maximum(F.max(0)-F.min(0),1e-12)
    normalized=(F-F.min(0))/scale
    a,b=normalized[F[:,0].argmin()],normalized[F[:,0].argmax()]
    chord=b-a
    distances=np.abs(chord[0]*(normalized[:,1]-a[1])-chord[1]*(normalized[:,0]-a[0]))/(np.sqrt((chord**2).sum())+1e-12)
    return int(np.argmax(distances))


def fusion_checks():
    receipt=[]
    for phase in ['fusion_validation_v1','final_v1']:
        dr=TASK/'results/rl'/phase
        mapping=json.loads((dr/'front_episode_mapping.json').read_text())
        fronts_path=TASK/mapping['source_front_path']
        assert sha(fronts_path)==mapping['source_front_sha256']
        collections=json.loads(fronts_path.read_text())
        model=(TASK/'results/rl/development_v1/q_f60_s2024/model.npz' if phase=='fusion_validation_v1'
               else TASK/'results/rl/final_v1/q_f60/model.npz')
        if not model.exists():
            model=TASK/'results/rl/final_v1/q_f60_s2024/model.npz'
        LT=independent_lt(np.load(model)['V'])
        grouped={}
        for item in mapping['rows']:
            grouped.setdefault((item['policy'],item['day_seed']),[]).append(item)
        verified=0
        for (policy,seed),items in grouped.items():
            ep,trace=TASK/items[0]['episode_path'],TASK/items[0]['trace_path']
            assert sha(ep)==items[0]['episode_sha256'] and sha(trace)==items[0]['trace_sha256']
            _,contexts=replay(ep,trace,expected_row(trace.parent,policy,seed),LT=LT,beta=.5)
            times=[x['t'] for x in items]
            assert all(a<b for a,b in zip(times,times[1:]))
            for item in items:
                f=collections[item['front_collection']][item['front_ordinal']]
                c=contexts[item['t']]
                assert f['t']==c['t'] and f['selected']==item['selected']
                pairs=list(map(tuple,f['pairs']))
                assert set(pairs)==set(c['local_pairs'])
                assert len({a for a,b in pairs})==len(pairs) and len({b for a,b in pairs})==len(pairs)
                assert all(c['feas'][a,b] and c['weights'][a,b]>0 for a,b in pairs)
                F=np.asarray(f['F'])
                observed=[-sum(c['weights'][a,b] for a,b in pairs),sum(c['pickup'][a,b] for a,b in pairs)]
                near(F[f['selected']],observed,'selected dynamic front objective')
                assert f['n_eval']==40*31
                if policy.endswith('knee'):
                    assert f['selected']==knee_reference(F)
                else:
                    W=np.where(c['feas'],np.maximum(c['weights'],0),0)
                    ii,jj=linear_sum_assignment(-W)
                    budget=.6*sum(c['pickup'][a,b] for a,b in zip(ii,jj) if W[a,b]>0)
                    eligible=np.flatnonzero(F[:,1]<=budget+1e-9)
                    choice=int(eligible[np.argmin(F[eligible,0])]) if len(eligible) else int(F[:,1].argmin())
                    assert choice==f['selected']
                verified+=1
        receipt.append(dict(phase=phase,frames=verified,mapping_sha256=sha(dr/'front_episode_mapping.json'),
                            source_front_sha256=sha(fronts_path),model_sha256=sha(model),
                            scope='All mapped local pairs, true context weights, objective sums, preference selection and evaluation budgets independently reconstructed.'))
    return receipt


def confidence_checks():
    rows=[]
    for phase in ['final_v1/enhancements','final_montecarlo_v1']:
        p=TASK/'results/rl'/phase/'day_metrics.json';d=json.loads(p.read_text())
        q={r['day_seed']:r for r in d if r['policy']=='qkm'}
        move={r['day_seed']:r for r in d if r['policy']=='km_move3'}
        assert set(q)==set(move)
        seeds=sorted(q)
        assert all(q[s]['episode_sha256']==move[s]['episode_sha256'] for s in seeds)
        gross=np.array([move[s]['revenue']-q[s]['revenue'] for s in seeds])
        empty=np.array([move[s]['empty_km']-q[s]['empty_km'] for s in seeds])
        net=gross-empty
        def interval(x):
            sem=x.std(ddof=1)/np.sqrt(len(x));half=student_t.ppf(.975,len(x)-1)*sem
            return dict(n=len(x),mean=float(x.mean()),sample_sd=float(x.std(ddof=1)),
                        paired_t95=[float(x.mean()-half),float(x.mean()+half)])
        rows.append(dict(phase=phase,metrics_sha256=sha(p),gross_gain=interval(gross),
                         extra_empty_km=interval(empty),diagnostic_net_at_hypothetical_cost1_per_km=interval(net),
                         scope='Conditional on frozen learned model and proxy-order resampling pool; not actual operational days, training uncertainty or fuel prices. No post-test method selection.'))
    return rows


def main():
    result=dict(reviewer='/root/evolution',role='independent RL policy/metric verification',
                verifier_sha256=sha(__file__),started_utc=datetime.now(timezone.utc).isoformat(),
                weighted_policies=weighted_policy_checks(),fusion=fusion_checks(),
                paired_statistics=confidence_checks(),
                source_code_sha256={str(p.relative_to(ROOT)):sha(p) for p in
                    [TASK/'src/rl_dispatch.py',TASK/'src/rl_extensions.py',TASK/'src/rl_fusion.py']},
                status='PASS_IN_STATED_SCOPE',completed_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'policy_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['paired_statistics'],indent=2))
    print('fusion frames',result['fusion'])


if __name__=='__main__':
    main()
