"""Run predeclared online control variables; every row links to a saved input and matches."""
from pathlib import Path
import argparse
import csv
import datetime
import hashlib
import json
import subprocess
import time
from dataclasses import asdict, replace
import numpy as np
from task2.src.online import (SimulationEnvironment, Worker, Request, TBGAlgorithm, BBAlgorithm,
                             run_simulation, offline_reference, summarize, instance_ratios)

ROOT = Path(__file__).resolve().parents[2]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def configurations():
    base = dict(n_workers=20, n_requests=20, horizon=20., extent=10., speed=1.,
                worker_time_dist="uniform", request_time_dist="uniform", loc_dist="uniform",
                arrival_shift="none", units="km,min", source="synthetic")
    result = [("teacher", base)]
    for ratio in (.5, 1.5, 2.):
        result.append((f"supply_{ratio}", dict(base, n_workers=int(20*ratio))))
    result.append(("hotspot", dict(base, loc_dist="normal")))
    result.append(("workers_first", dict(base, arrival_shift="workers_first")))
    result.append(("requests_first", dict(base, arrival_shift="requests_first")))
    for n in (50, 100):
        result.append((f"size_{n}", dict(base, n_workers=n, n_requests=n)))
    result.append(("peaked_time", dict(base, worker_time_dist="normal", request_time_dist="normal")))
    result.append(("notebook", dict(base, n_workers=100, n_requests=100, horizon=2000.,
                                     extent=1000., units="space_unit,time_unit")))
    return result


def generate(config, seed):
    s = SimulationEnvironment(seed)
    s.generate_synthetic_data(config["n_workers"], config["n_requests"],
                              (0, config["horizon"]), (0, config["extent"]),
                              config["worker_time_dist"], config["request_time_dist"], config["loc_dist"])
    if config["arrival_shift"] == "workers_first":
        s.workers = [replace(w, arrival_time=w.arrival_time/2) for w in s.workers]
        s.requests = [replace(r, arrival_time=(r.arrival_time+config["horizon"])/2) for r in s.requests]
    elif config["arrival_shift"] == "requests_first":
        s.requests = [replace(r, arrival_time=r.arrival_time/2) for r in s.requests]
        s.workers = [replace(w, arrival_time=(w.arrival_time+config["horizon"])/2) for w in s.workers]
    return s.workers, s.requests


def run(output, confirmation=False, proxy=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "instances").mkdir()
    (output / "matches").mkdir()
    seeds = list(range(110, 115)) if confirmation else list(range(10, 15))
    configs = configurations()
    if proxy:
        configs = []  # appended after the shared data interface exists; a separate real-data run
        raise RuntimeError("Use run_online_proxy.py after data audit; never silently substitute synthetic data")
    source_files = [Path(__file__), ROOT/"task2/src/online.py", ROOT/"task2/docs/METHOD_AND_METRIC_SPEC.md"]
    manifest = {"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "identity": "current-run", "partition": "synthetic_confirmation" if confirmation else "synthetic_development",
                "seeds": seeds, "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in source_files},
                "git_head": subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                "configs": dict(configs), "semantics": "docs/METHOD_AND_METRIC_SPEC.md"}
    rows = []
    for scenario, config in configs:
        for seed in seeds:
            workers, requests = generate(config, seed)
            key = f"{scenario}_s{seed}"
            instance = output/"instances"/(key+".json")
            instance.write_text(json.dumps({"workers":[asdict(w) for w in workers],
                                           "requests":[asdict(r) for r in requests], "config":config}, indent=2))
            opt_sum = offline_reference(workers, requests, config["speed"], "sum")
            opt_max = offline_reference(workers, requests, config["speed"], "max")
            factor = 100 if scenario == "notebook" else 1
            methods = [(f"TBG_g{g*factor:g}", TBGAlgorithm(g*factor,config["speed"]))
                       for g in (.5,1,2,5,10)]
            methods += [(f"BB_{'recycle' if recycle else 'discard'}_t{theta*factor:g}",
                         BBAlgorithm(theta*factor,config["speed"],recycle))
                        for recycle in (True,False) for theta in (.5,1,2,5)]
            methods += [(f"BBmax_recycle_t{theta*factor:g}",
                         BBAlgorithm(theta*factor,config["speed"],True,"max"))
                        for theta in (.5,1,2,5)]
            for name, method in methods + [("offline_sum",None),("offline_max",None)]:
                t0 = time.perf_counter()
                a = (opt_sum if name=="offline_sum" else opt_max) if method is None else run_simulation(
                    workers,requests,method,config["horizon"])
                elapsed = time.perf_counter()-t0
                path = output/"matches"/(key+"_"+name+".json")
                path.write_text(json.dumps([asdict(x) for x in a], indent=2))
                row = {"scenario":scenario,"seed":seed,"method":name,"units":config["units"],
                       **summarize(a,len(requests),len(workers)), **instance_ratios(a,opt_sum,opt_max),
                       "discarded_requests":len(getattr(method,"discarded_requests",[])),
                       "runtime_seconds": elapsed, "runtime_scope":"dispatch_only_excludes_shared_offline_reference" if method is not None else "reference_lookup_only_not_solver_time",
                       "input":str(instance.relative_to(output)), "input_sha256":digest(instance),
                       "matches":str(path.relative_to(output)),"matches_sha256":digest(path)}
                rows.append(row)
            print(scenario,seed,"done",flush=True)
    with (output/"metrics.csv").open("w",newline="") as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    manifest.update(ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    n_metric_rows=len(rows),metrics_sha256=digest(output/"metrics.csv"))
    (output/"manifest.json").write_text(json.dumps(manifest,indent=2))
    return rows


if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);p.add_argument("--confirmation",action="store_true")
    args=p.parse_args();run(args.output,args.confirmation)
