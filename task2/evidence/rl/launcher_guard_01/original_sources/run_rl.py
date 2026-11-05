#!/usr/bin/env python3
"""Reproducible staged RL experiments. Each stage retains raw model and day data."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK/"src"))
from rl_dispatch import (DEFAULT, Config, QTable, DoubleQTable, sample_episode,
                         train_q_km, run_episode, make_q_km, region_long_term_value,
                         make_repositioner, greedy_nearest, km_fare)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_dump(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=True))


def identity():
    files=[TASK/"src/rl_dispatch.py",Path(__file__)]
    return {str(p.relative_to(TASK)):sha(p) for p in files}


def save_model(path, qt, curve, td, episodes, seconds, metadata):
    path.mkdir(parents=True,exist_ok=True)
    arrays=dict(V=qt.V,NV=qt.NV,curve=curve,td=td,episodes=episodes)
    if isinstance(qt,DoubleQTable):
        arrays.update(A=qt.A,B=qt.B,NA=qt.NA,NB=qt.NB)
    else:
        arrays.update(Q=qt.Q,N=qt.N)
    np.savez_compressed(path/"model.npz",**arrays)
    json_dump(path/"manifest.json",dict(**metadata,config=asdict(qt.config),runtime=seconds,
              created=datetime.now(timezone.utc).isoformat(),code_hashes=identity(),
              model_sha256=sha(path/"model.npz"),real_training_episodes=len(td)))


def load_model(path):
    meta=json.loads((path/"manifest.json").read_text())
    qt=DoubleQTable(Config(**meta["config"])) if meta["double"] else QTable(Config(**meta["config"]))
    with np.load(path/"model.npz") as a:
        for k in ["V","NV","A","B","NA","NB"] if meta["double"] else ["V","NV","Q","N"]:
            setattr(qt,k,a[k])
    return qt,meta


def fit(path, trips, initial, validation, fleet=60, seed=2024, n=300,beta=.5,
        config=DEFAULT,double=False,data_identity=None):
    if path.exists() and (path/"manifest.json").exists():
        qt,meta=load_model(path)
        requested=(fleet,seed,n,beta,asdict(config),double)
        actual=(meta["fleet"],meta["seed"],meta["real_training_episodes"],meta["beta"],meta["config"],meta["double"])
        if requested!=actual or meta["code_hashes"]!=identity():
            raise ValueError(f"existing run identity mismatch; retain and use a new run path: {path}")
        print("REUSE",path.name,flush=True)
        return qt
    print("TRAIN",path.name,flush=True)
    qt,curve,td,ep_log,seconds=train_q_km(trips,initial,fleet,n,beta,seed,validation,config,double,verbose=True)
    save_model(path,qt,curve,td,ep_log,seconds,dict(fleet=fleet,seed=seed,beta=beta,double=double,
               split_identity=data_identity))
    print("TRAINED",path.name,"seconds",round(seconds,2),flush=True)
    return qt


def evaluate(path, trip_pool, initial_pool, fleet, policies, config=DEFAULT,seeds=range(50000,50005),
             split="validation", trace=True):
    path.mkdir(parents=True,exist_ok=True)
    rows=[]
    for day_seed in seeds:
        ep=sample_episode(trip_pool,fleet,int(day_seed),initial_pool,config)
        ep_path=path/f"episode_{day_seed}.npz"
        np.savez_compressed(ep_path,drivers=ep[1],**ep[0])
        for name,policy,reposition in policies:
            metrics,_=run_episode(ep,policy,config=config,reposition=reposition,trace=trace)
            if trace:
                json_dump(path/f"trace_{name}_{day_seed}.json",metrics.pop("trace"))
            rows.append(dict(policy=name,fleet=fleet,day_seed=int(day_seed),split=split,
                             episode_sha256=sha(ep_path),**metrics))
    json_dump(path/"day_metrics.json",rows)
    json_dump(path/"manifest.json",dict(code_hashes=identity(),split=split,config=asdict(config),
               fleet=fleet,seeds=list(seeds),policies=[p[0] for p in policies]))
    summary={name:{k:float(np.nanmean([r[k] for r in rows if r["policy"]==name]))
                       for k in ["revenue","answer_rate","avg_pickup","empty_km","nonpositive_fraction"]}
             for name,_,_ in policies}
    json_dump(path/"summary.json",summary)
    print("EVAL",path.name,json.dumps(summary),flush=True)
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",required=True,choices=["pilot","baseline","sensitivity","double","final"])
    parser.add_argument("--run",required=True,help="unique output dir below results/rl")
    parser.add_argument("--data",type=Path,required=True,help="directory containing audited split CSVs and driver pool")
    parser.add_argument("--episodes",type=int,default=300)
    parser.add_argument("--seeds",default="2024")
    args=parser.parse_args()
    import pandas as pd
    # Coordinator-approved export of dispatch_data, kept explicit for review.
    data=args.data
    train=pd.read_csv(data/"trips_train_inner.csv")
    validation=pd.read_csv(data/"trips_validation.csv")
    initial=pd.read_csv(data/"checkins_train_inner.csv")
    data_id={p.name:sha(p) for p in data.glob("*.csv")}
    root=TASK/"results/rl"/args.run
    root.mkdir(parents=True,exist_ok=True)
    train_seeds=[int(s) for s in args.seeds.split(",")]
    if args.phase=="pilot":
        qt=fit(root/"pilot_q",train,initial,validation,n=args.episodes,data_identity=data_id)
        evaluate(root/"pilot_validation",validation,initial,60,
                 [("greedy",greedy_nearest,None),("km",km_fare,None),
                  ("qkm",make_q_km(region_long_term_value(qt.V)),None)],seeds=range(20000,20003))
    elif args.phase=="baseline":
        for fleet in [40,60,100]:
            for seed in train_seeds:
                qt=fit(root/f"q_f{fleet}_s{seed}",train,initial,validation,fleet,seed,args.episodes,data_identity=data_id)
                evaluate(root/f"baseline_f{fleet}_s{seed}",validation,initial,fleet,
                         [("greedy",greedy_nearest,None),("km",km_fare,None),
                          ("qkm",make_q_km(region_long_term_value(qt.V)),None)])
    elif args.phase=="sensitivity":
        conditions=[("gamma08",replace(DEFAULT,gamma=.8)),("gamma095",replace(DEFAULT,gamma=.95)),
                    ("grid6",replace(DEFAULT,grid=6)),("grid10",replace(DEFAULT,grid=10)),
                    ("patience1",replace(DEFAULT,patience=1)),("patience3",replace(DEFAULT,patience=3))]
        for name,cfg in conditions:
            qt=fit(root/name,train,initial,validation,n=args.episodes,config=cfg,data_identity=data_id)
            evaluate(root/(name+"_validation"),validation,initial,60,
                     [("greedy",greedy_nearest,None),("km",km_fare,None),
                      ("qkm",make_q_km(region_long_term_value(qt.V,config=cfg)),None)],config=cfg)
    elif args.phase=="double":
        for seed in train_seeds:
            for double in [False,True]:
                name=f'{"double" if double else "q"}_b1_s{seed}'
                qt=fit(root/name,train,initial,validation,seed=seed,n=args.episodes,beta=1,double=double,data_identity=data_id)
                LT=region_long_term_value(qt.V)
                evaluate(root/(name+"_validation"),validation,initial,60,
                         [("km",km_fare,None),("beta05",make_q_km(LT,.5),None),("beta1",make_q_km(LT,1),None)])
    else:
        raise RuntimeError("Final test must follow frozen validation selection; use explicit reviewed final runner")


if __name__=="__main__":
    main()
