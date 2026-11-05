#!/usr/bin/env python3
"""Result-triggered RL follow-ups, validation only; no held-out test selection."""
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
TASK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
from run_rl import load_model,evaluate,json_dump,sha
from rl_dispatch import DEFAULT,make_q_km,region_long_term_value,make_repositioner,km_fare,greedy_nearest,zone_of


def value_diagnostics(trace,V,config=DEFAULT):
    """Descriptive V minus realized policy return; not unbiased optimal-value error."""
    rides=trace['assignments'];moves=trace['movements'];initial=np.array(trace['initial'])
    points=[]
    for d in range(len(initial)):
        dr=[a for a in rides if a['driver']==d];events=sorted(dr+[a for a in moves if a['driver']==d],key=lambda x:x['t'])
        for t in range(config.T):
            current=initial[d];busy=False
            for event in events:
                if event['t']<=t<event['release']:
                    # A dispatch at t observes the pre-action state, so include t itself.
                    if event['t']<t:busy=True
                    break
                if event['release']<=t:current=np.array(event['destination'])
            if busy:continue
            z=int(zone_of(current[0],current[1],config))
            realized=sum(config.gamma**(a['t']-t)*a['fare'] for a in dr if a['t']>=t)
            points.append([t,z,float(V[t,z]),float(realized)])
    p=np.array(points)
    gap=p[:,2]-p[:,3]
    return dict(n_idle_states=len(p),mean_estimate=float(p[:,2].mean()),mean_policy_return=float(p[:,3].mean()),
                optimism_gap=float(gap.mean()),mae_to_policy_return=float(np.abs(gap).mean())),p


def main():
    a=argparse.ArgumentParser();a.add_argument('--phase',choices=['beta','reposition','diagnostics'],required=True)
    a.add_argument('--model',type=Path,required=True);a.add_argument('--run',required=True)
    a.add_argument('--data',type=Path,default=TASK/'results/data');args=a.parse_args()
    args.model=args.model.resolve()
    qt,meta=load_model(args.model);cfg=qt.config;LT=region_long_term_value(qt.V,config=cfg)
    val=pd.read_csv(args.data/'trips_validation.csv');init=pd.read_csv(args.data/'checkins_train_inner.csv')
    out=TASK/'results/rl'/args.run;out.mkdir(parents=True,exist_ok=True)
    json_dump(out/'followup_manifest.json',dict(phase=args.phase,parent_model=str(args.model.relative_to(TASK)),
              parent_sha=sha(args.model/'model.npz'),runner_sha=sha(__file__),
              trigger='300episode development baseline: QKM improves revenue over KM, pickup exceeds greedy and nonpositive edge weights remain; test not used',
              reference_contract='task2/evidence/rl/METHOD_SPEC.md',split='validation'))
    if args.phase=='beta':
        policies=[(f'beta{b:g}',make_q_km(LT,b),None) for b in [0,.2,.4,.5,.6,.8,1]]
        evaluate(out,val,init,meta['fleet'],policies,cfg)
    elif args.phase=='reposition':
        reposition=make_repositioner(qt.V,cfg)
        policies=[('km',km_fare,None),('qkm',make_q_km(LT,.5),None),
                  ('km_reposition',km_fare,reposition),('qkm_reposition',make_q_km(LT,.5),reposition)]
        evaluate(out,val,init,meta['fleet'],policies,cfg)
    else:
        source=TASK/'results/rl/development_v1'/f'baseline_f{meta["fleet"]}_s{meta["seed"]}'
        rows=[]
        for name in ['km','greedy','qkm']:
            for seed in range(50000,50005):
                tr=json.loads((source/f'trace_{name}_{seed}.json').read_text())
                bias,p=value_diagnostics(tr,qt.V,cfg)
                np.savez_compressed(out/f'value_samples_{name}_{seed}.npz',samples=p)
                matches=tr['assignments']
                rows.append(dict(policy=name,day_seed=seed,**bias,
                                 mean_trip=float(np.mean([x['trip'] for x in matches])),
                                 mean_occupied_steps=float(np.mean([x['release']-x['t'] for x in matches])),
                                 served=len(matches)))
        json_dump(out/'diagnostics.json',rows)
        print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
