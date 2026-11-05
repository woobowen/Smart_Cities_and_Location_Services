"""Result-triggered threshold diagnosis and a separately identified Foursquare proxy extension."""
from pathlib import Path
from dataclasses import asdict
import argparse
import csv
import datetime
import hashlib
import json
import time
import numpy as np
from task2.src.online import (Worker,Request,TBGAlgorithm,BBAlgorithm,offline_reference,
                             run_simulation,summarize,instance_ratios)
from task2.scripts.run_online import generate,configurations

ROOT=Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def execute(out,study):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    (out/"inputs").mkdir();(out/"matches").mkdir()
    inputs=[]
    if study=="threshold":
        for scenario,config in configurations():
            if scenario in ("teacher","workers_first","requests_first"):
                for seed in range(10,15):
                    w,r=generate(config,seed)
                    inputs.append((scenario,seed,w,r,20.,{"identity":"synthetic_development", "config":config}))
    else:
        from task2.src.dispatch_data import load_data
        b=load_data();ck=b.checkins_train_inner
        for hour in (8,13,18,23):
            pool=b.trips_train_inner[(b.trips_train_inner.minute>=60*hour)&(b.trips_train_inner.minute<60*(hour+1))]
            for seed in range(10,15):
                rng=np.random.default_rng(seed)
                origins=pool.iloc[rng.choice(len(pool),20,replace=len(pool)<20)]
                driver_ck=ck.iloc[rng.choice(len(ck),20,replace=False)]
                w=[Worker(i,(float(row.x),float(row.y)),float(rng.uniform(0,60))) for i,(_,row) in enumerate(driver_ck.iterrows())]
                r=[Request(i,(float(row.ox),float(row.oy)),float(row.minute-60*hour)) for i,(_,row) in enumerate(origins.iterrows())]
                provenance={"identity":"resampled_checkin_proxy_origins_not_taxi_orders","source_partition":"train_inner",
                            "hour":hour,"units":"conditional km,min","speed":1.,"horizon":60.,
                            "worker_source_rows":driver_ck.source_row.astype(int).tolist(),
                            "request_origin_source_rows":origins.origin_source_row.astype(int).tolist(),
                            "request_destination_source_rows":origins.destination_source_row.astype(int).tolist(),
                            "source_csv_sha256":b.audit["sha256"],"data_audit":b.audit}
                inputs.append((f"proxy_hour{hour}",seed,w,r,60.,provenance))
    rows=[]
    for scenario,seed,w,r,horizon,provenance in inputs:
        key=f"{scenario}_s{seed}";ip=out/"inputs"/(key+".json")
        ip.write_text(json.dumps({"workers":[asdict(x) for x in w],"requests":[asdict(x) for x in r],"provenance":provenance},indent=2))
        start=time.perf_counter();os=offline_reference(w,r,1,"sum");sum_time=time.perf_counter()-start
        start=time.perf_counter();om=offline_reference(w,r,1,"max");max_time=time.perf_counter()-start
        if study=="threshold":
            methods=[(f"TBG_g{g}",TBGAlgorithm(g)) for g in (2,3,4,5,6,8,10,15)]
        else:
            methods=[(f"TBG_g{g}",TBGAlgorithm(g)) for g in (2,5,15)]
            methods += [(f"BB_recycle_t{t}",BBAlgorithm(t)) for t in (1,2,5)]
            methods += [("BBmax_recycle_t2",BBAlgorithm(2,objective="max")),("BB_discard_t2",BBAlgorithm(2,recycle=False))]
        for name,method in methods+[("offline_sum",None),("offline_max",None)]:
            start=time.perf_counter()
            a=(os if name=="offline_sum" else om) if method is None else run_simulation(w,r,method,horizon)
            elapsed=time.perf_counter()-start if method is not None else sum_time if name=="offline_sum" else max_time
            mp=out/"matches"/(key+"_"+name+".json");mp.write_text(json.dumps([asdict(x) for x in a],indent=2))
            row={"scenario":scenario,"seed":seed,"method":name,**summarize(a,len(r),len(w)),
                 **instance_ratios(a,os,om),"finalization_fraction":sum(x.phase=="finalize" for x in a)/len(a) if a else None,
                 "runtime_seconds":elapsed,"input":str(ip.relative_to(out)),"input_sha256":sha(ip),
                 "matches":str(mp.relative_to(out)),"matches_sha256":sha(mp)}
            rows.append(row)
    with (out/"metrics.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    sources=[Path(__file__),ROOT/"task2/src/online.py",ROOT/"task2/src/dispatch_data.py"]
    (out/"manifest.json").write_text(json.dumps({"study":study,"time_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_sha256":{str(p.relative_to(ROOT)):sha(p) for p in sources},"metrics_sha256":sha(out/"metrics.csv"),"rows":len(rows),
        "trigger":"development_v1: gamma .5/1/2 finalized17%, gamma5 7%; local threshold diagnosis" if study=="threshold" else "teacher real-data bonus; historical spatial demand distribution, no true ride-hailing claim"},indent=2))
    print(study,len(rows),"real rows")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("study",choices=["threshold","proxy"]);p.add_argument("--output",required=True)
    a=p.parse_args();execute(a.output,a.study)
