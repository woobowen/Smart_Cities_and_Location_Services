"""Reproduce the historical RNG-fix follow-up in a fresh output directory."""
from pathlib import Path
import argparse
try:
    from .experiment_cli import require_fresh_output
except ImportError:  # Direct-file invocation has no package context.
    from experiment_cli import require_fresh_output
TASK=Path(__file__).resolve().parents[1]


def parse_args(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',required=True,choices=['sensitivity','double'])
    p.add_argument('--output',type=Path,help='Explicit fresh output directory')
    args=p.parse_args(argv)
    args.output=require_fresh_output(p,args.output if args.output is not None else TASK/'results/rl'/f'{args.phase}_v2_rngfix')
    return args


def main(argv=None):
    args=parse_args(argv)
    root=args.output
    root.mkdir(parents=True,exist_ok=False)
    from dataclasses import replace
    import sys,json,argparse
    import pandas as pd
    sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
    from rl_dispatch import DEFAULT,region_long_term_value,make_q_km,greedy_nearest,km_fare
    from run_rl import fit,load_model,evaluate,sha,json_dump

    data=TASK/'results/data';train=pd.read_csv(data/'trips_train_inner.csv');val=pd.read_csv(data/'trips_validation.csv');init=pd.read_csv(data/'checkins_train_inner.csv')
    data_id={f.name:sha(f) for f in data.glob('*.csv')}
    json_dump(root/'resume_contract.json',dict(fix='independent Double update RNG; Q-only exact array parity verified',source_sha256=sha(TASK/'src/rl_dispatch.py'),runner_sha256=sha(__file__),scope='resume or rerun affected work; original valid Q-only identities retained',old_double_status='INVALID_FOR_FAIR_DOUBLE_COMPARE'))
    if args.phase=='sensitivity':
        for name,cfg in [('gamma08',replace(DEFAULT,gamma=.8)),('gamma095',replace(DEFAULT,gamma=.95)),('grid6',replace(DEFAULT,grid=6)),('grid10',replace(DEFAULT,grid=10)),('patience1',replace(DEFAULT,patience=1)),('patience3',replace(DEFAULT,patience=3))]:
            old=TASK/'results/rl/sensitivity_v1'/name
            if (old/'manifest.json').exists():
                json_dump(root/f'{name}_inherited.json',dict(path=str(old.relative_to(TASK)),model_sha256=sha(old/'model.npz'),identity='original valid Q-only result; no new training'))
                print('INHERIT',name,flush=True)
                continue
            qt=fit(root/name,train,init,val,n=300,config=cfg,data_identity=data_id)
            evaluate(root/(name+'_validation'),val,init,60,[('greedy',greedy_nearest,None),('km',km_fare,None),('qkm',make_q_km(region_long_term_value(qt.V,config=cfg)),None)],cfg)
    else:
        for seed in [2024,2025,2026,2027,2028]:
            for double in [False,True]:
                name=f'{"double" if double else "q"}_b1_s{seed}'
                old=TASK/'results/rl/double_validation_v1'/name
                if not double and (old/'manifest.json').exists():
                    qt,meta=load_model(old)
                    json_dump(root/f'{name}_inherited.json',dict(path=str(old.relative_to(TASK)),model_sha256=sha(old/'model.npz'),identity='original valid Q-only result; no new training'))
                else:qt=fit(root/name,train,init,val,seed=seed,n=300,beta=1,double=double,data_identity=data_id)
                LT=region_long_term_value(qt.V)
                evaluate(root/(name+'_validation'),val,init,60,[('km',km_fare,None),('beta05',make_q_km(LT,.5),None),('beta1',make_q_km(LT,1),None)])


if __name__=="__main__":
    main()
