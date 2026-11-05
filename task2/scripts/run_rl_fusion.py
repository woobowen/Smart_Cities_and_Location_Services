"""Static and dynamic QKM plus NSGA-II validation."""
from pathlib import Path
try:
    from .experiment_cli import fixed_output_args
except ImportError:  # Direct-file invocation has no package context.
    from experiment_cli import fixed_output_args
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    return fixed_output_args(TASK/"results/rl/fusion_validation_v1",__doc__,argv)


def main(argv=None):
    args=parse_args(argv)
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    import sys,json,time
    import numpy as np
    import pandas as pd
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from run_rl import load_model,sha,json_dump,evaluate
    from rl_dispatch import DEFAULT,region_long_term_value,make_q_km,sample_episode,run_episode,greedy_nearest,km_fare
    from rl_fusion import NSGADispatch
    from evolution import EdgeDispatchProblem,run_nsga,knee_point,weighted_km
    qt,meta=load_model(TASK/'results/rl/development_v1/q_f60_s2024');LT=region_long_term_value(qt.V)
    val=pd.read_csv(TASK/'results/data/trips_validation.csv');init=pd.read_csv(TASK/'results/data/checkins_train_inner.csv')
    ep=sample_episode(val,60,50000,init)
    capture={};parent=make_q_km(LT,.5)
    def capture_policy(ctx):
        if ctx['t']==72:capture.update({k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in ctx.items()})
        return parent(ctx)
    run_episode(ep,capture_policy)
    if not capture:raise ValueError('no dispatch context at18:00')
    W=capture['fare'][None]+.5*LT[72][capture['drv_zone'][:,None],capture['dest_zone'][None]]
    feas=capture['feas'] & (W>0)
    np.savez_compressed(out/'static_input.npz',weights=W,pickup=capture['pickup'],feas=feas,**{k:v for k,v in capture.items() if k not in ['pickup','feas']})
    p=EdgeDispatchProblem(W,capture['pickup'],feas,K=None)
    static=[]
    for seed in range(5):
        r=run_nsga(p,pop_size=100,n_gen=300,seed=seed)
        np.savez_compressed(out/f'static_seed{seed}.npz',F=r['F'],genes=r['genes'])
        static.append(dict(seed=seed,F=r['F'].tolist(),pairs=r['pairs'],n_eval=r['n_eval'],runtime=r['runtime'],knee=int(knee_point(r['F']))))
        print('STATIC',seed,'nfront',len(r['F']),'seconds',r['runtime'],flush=True)
    json_dump(out/'static_fronts.json',static)
    json_dump(out/'static_weighted_km.json',[dict(lam=x['lam'],pairs=x['pairs'],F=x['F'].tolist()) for x in weighted_km(p,np.linspace(0,20,41))])
    json_dump(out/'fusion_contract.json',dict(trigger='verified QKM improves gross income but pickup remains higher than nearest; verified standalone NSGA front can expose tradeoff',
               source_sha256={str(x.relative_to(TASK)):sha(x) for x in [Path(__file__),TASK/'src/rl_fusion.py',TASK/'src/evolution.py']},
               candidate_graph='full radius-feasible positive-QKM-edge graph; K=None for all methods',
               objectives=['negative estimated QKM edge value','pickup km'],static=dict(pop=100,gen=300,seeds=list(range(5))),
               dynamic=dict(pop=40,gen=30,choice=['knee','constraint'],constraint='pickup <= .6 * same-context QKM pickup total'),
               split='validation',static_context='18:00 of actual validation QKM trajectory, seed50000',
               boundary='Estimated LT-weighted score is not realized income; dynamic simulations separately measure income/served/pickup'))
    knee=NSGADispatch(LT,seed=2024,choice='knee')
    constrained=NSGADispatch(LT,seed=2024,choice='constraint')
    evaluate(out/'dynamic',val,init,60,[('greedy',greedy_nearest,None),('km',km_fare,None),('qkm',make_q_km(LT,.5),None),('qnsga_knee',knee,None),('qnsga_constraint',constrained,None)],seeds=range(50000,50005))
    json_dump(out/'dynamic_nsga_fronts.json',dict(knee=knee.fronts,constraint=constrained.fronts))


if __name__=="__main__":
    main()
