#!/usr/bin/env python3
"""Separate basic-teacher NSGA-II task on the PPT spatial scale, with exact scalar references."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'task2/src'))
from evolution import DispatchProblem, run_nsga, weighted_km, hypervolume, spacing, knee_point


def convert(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.integer, np.floating)):
        return x.item()
    if isinstance(x, dict):
        return {k: convert(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [convert(v) for v in x]
    return x


def main():
    out = ROOT/'task2/results/evolution/basic'
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2024)
    drv, origin, dest = (rng.uniform(0, 10, (20, 2)) for _ in range(3))
    pickup = np.linalg.norm(drv[:, None]-origin[None], axis=-1)
    trip_km = np.linalg.norm(dest-origin, axis=1)
    batch = dict(drv=drv, o_xy=origin, d_xy=dest, pickup=pickup, fare=trip_km)
    np.savez_compressed(out/'basic_synthetic_od.npz', **batch)
    p = DispatchProblem(batch, K=20, radius=np.sqrt(200))
    ideal, nadir = p.normalization()
    lambdas = np.array([0., .25, .5, 1., 2.])
    references = weighted_km(p, lambdas)
    provenance = dict(identity='current-run synthetic OD, basic teacher geometry',
                      driver_count=20, request_count=20, space_km=[10, 10],
                      source_sha256=hashlib.sha256((ROOT/'task2/src/evolution.py').read_bytes()).hexdigest(),
                      runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      batch_sha256=hashlib.sha256((out/'basic_synthetic_od.npz').read_bytes()).hexdigest(),
                      revenue='Euclidean OD distance in km, no currency interpretation',
                      pickup='Euclidean km', batch_seed=2024,
                      matching='optional; full candidate graph, all requests/drivers visible',
                      ratio='exact maximum utility / chosen maximum utility, static instance approximation ratio; not an online competitive guarantee')
    for seed in range(5):
        r = run_nsga(p, pop_size=100, n_gen=300, seed=seed)
        ratios = []
        for lam, ref in zip(lambdas, references):
            utility = -r['F'][:, 0]-lam*r['F'][:, 1]
            k = int(utility.argmax())
            optimal, obtained = -ref['F'][0]-lam*ref['F'][1], max(float(utility[k]), 0.)
            ratio = float(optimal/obtained) if obtained > 0 else None
            state = 'FINITE' if obtained > 0 else ('ZERO_BOTH' if optimal == 0 else 'INFINITE')
            ratios.append(dict(lam=lam, chosen_F=r['F'][k], exact_F=ref['F'],
                               exact_utility=optimal, obtained_utility=obtained,
                               ratio=ratio, state=state))
        r.update(provenance=provenance, ideal=ideal, nadir=nadir,
                 HV=hypervolume(r['F'], ideal, nadir), spacing=spacing(r['F'], ideal, nadir),
                 scalar_comparisons=ratios, knee_index=knee_point(r['F']))
        (out/f'basic_nsga2_seed{seed}.json').write_text(json.dumps(convert(r), indent=2)+'\n')
        print(seed, 'HV',r['HV'],'time',r['runtime'], flush=True)
    (out/'METHOD.md').write_text('''# Basic NSGA-II: separately executed teacher task

Twenty drivers and twenty synthetic OD requests occupy the PPT 10x10 km square.
Pickup and trip lengths use Euclidean km; income is delivered OD km, as requested
by the basic teacher materials, without adding the advanced 5+2*km fare model.
All candidate edges are available and matching is optional. No dispatch can
serve the same driver/request twice. This snapshot isolates the base multiobjective
question; the event-driven TBG/BB experiments remain separately evaluated.

The five paired EA seeds0..4 use population100/generations300. The common batch
seed2024 and exact utility weights lambda0,.25,.5,1,2 are fixed before outcomes.
For each weight, the returned front's maximum utility is compared with exact
maximum-weight optional bipartite matching on the same instance. Ratio=OPT/EA
for a maximization problem; zero cases are explicit. This empirical static
approximation ratio cannot be described as an online theoretical competitive
ratio. A Pareto front has no single scalar competitive ratio until preferences,
constraints and benchmark objectives are defined. This is the applicability
boundary of the teacher's request, alongside the separate online-delay ratios.
''')


if __name__ == '__main__':
    main()
