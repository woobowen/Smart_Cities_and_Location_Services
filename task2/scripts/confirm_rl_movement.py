"""Frozen movement validation across training seeds."""
from pathlib import Path
try:
    from .experiment_cli import fixed_output_args
except ImportError:  # Direct-file invocation has no package context.
    from experiment_cli import fixed_output_args
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    return fixed_output_args(TASK/"results/rl/movement_trainseed_confirmation_v1",__doc__,argv)


def main(argv=None):
    args=parse_args(argv)
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    import sys
    import pandas as pd
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from run_rl import fit,evaluate,json_dump,sha,load_model
    from rl_dispatch import region_long_term_value,make_q_km,km_fare
    from rl_extensions import cost_aware_repositioner
    data=TASK/'results/data';train=pd.read_csv(data/'trips_train_inner.csv');val=pd.read_csv(data/'trips_validation.csv');init=pd.read_csv(data/'checkins_train_inner.csv')
    json_dump(out/'contract.json',dict(trigger='Single-seed removal of LT edge weighting improves gross revenue withV-motion; determine stability before final held-out evaluation',seeds=list(range(2024,2029)),candidate='KM vsQKM crossed with none vslambda3Vmotion; sameV within each seed',selection='mean gross validation fare, response >=teacherQKM-.01; report empty cost separately, do not call economic optimum',source_sha256=sha(__file__),data_identity={f.name:sha(f) for f in [data/'trips_train_inner.csv',data/'trips_validation.csv',data/'checkins_train_inner.csv']}))
    for seed in range(2024,2029):
     if seed==2024:
      qt,_=load_model(TASK/'results/rl/development_v1/q_f60_s2024')
     else:qt=fit(out/f'q_s{seed}',train,init,val,n=300,seed=seed,data_identity={f.name:sha(f) for f in [data/'trips_train_inner.csv',data/'trips_validation.csv']})
     LT=region_long_term_value(qt.V)
     evaluate(out/f'validation_s{seed}',val,init,60,[('km',km_fare,None),('qkm',make_q_km(LT,.5),None),('km_move3',km_fare,cost_aware_repositioner(qt.V,3)),('qkm_move3',make_q_km(LT,.5),cost_aware_repositioner(qt.V,3))])


if __name__=="__main__":
    main()
