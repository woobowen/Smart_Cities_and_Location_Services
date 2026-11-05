#!/usr/bin/env python3
"""Staged, resumable teacher Part A experiments; later stages are explicit."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import time
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'task2/src'))
from evolution import (DispatchProblem, DTLZ2, make_batch, run_nsga, weighted_km,
    km_initial_genes, hypervolume, spacing, knee_point, constraint_choice, das_dennis)
from dispatch_data import load_data, source_path

OUT = ROOT/'task2/results/evolution'
LAMBDAS = np.concatenate([[0.], np.geomspace(.05, 60., 40)])


def jsonable(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.integer, np.floating)):
        return x.item()
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    return x


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_batch(bundle, hour=18, partition='inner', seed=2024):
    if partition == 'inner':
        trips, ck = bundle.trips_train_inner, bundle.checkins_train_inner
    elif partition == 'validation':
        trips = bundle.trips_validation
        # A realistic training-only driver prior, frozen without validation locations.
        ck = bundle.checkins_train_inner
    elif partition == 'test':
        trips, ck = bundle.trips_test, bundle.checkins_train
    else:
        raise ValueError(partition)
    batch = make_batch(trips, ck, hour=hour, seed=seed)
    batch_id = f'{partition}_hour{hour}_batchseed{seed}'
    path = OUT/'batches'/f'{batch_id}.npz'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with np.load(path) as previous:
            if any(not np.array_equal(previous[k], batch[k]) for k in batch):
                raise RuntimeError('Existing batch differs; preserve it under its old identity')
    else:
        np.savez_compressed(path, **batch)
    return batch_id, batch, path


def save_run(problem, batch_id, batch_path, stage, seed, algo, pop, generations,
             n_obj, provenance, hybrid=False):
    run_id = f'{stage}_{batch_id}_{algo}_M{n_obj}_N{pop}_G{generations}_s{seed}'
    path = OUT/'runs'/f'{run_id}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        old = json.loads(path.read_text())
        if old['provenance']['evolution_sha256'] != provenance['evolution_sha256']:
            raise RuntimeError(f'{run_id} used another source version; invalidate explicitly')
        print('EXISTS', run_id, flush=True)
        return old
    normalization_start = time.perf_counter()
    ideal, nadir = (problem.normalization() if hasattr(problem, 'normalization')
                    else (np.zeros(n_obj), np.ones(n_obj)))
    normalization_seconds = time.perf_counter()-normalization_start
    initialization_start = time.perf_counter()
    initial = km_initial_genes(problem, LAMBDAS) if hybrid else None
    initialization_seconds = time.perf_counter()-initialization_start
    refs = das_dennis(n_obj, 99 if n_obj == 2 else (12 if isinstance(problem, DTLZ2) else 13))
    result = run_nsga(problem, algo=algo, pop_size=pop, n_gen=generations, seed=seed,
                      ref_dirs=refs, initial_genes=initial)
    F = result['F']
    result.update(run_id=run_id, stage=stage, batch_id=batch_id,
                  batch_path=str(batch_path.relative_to(ROOT)) if batch_path else None,
                  batch_sha256=sha(batch_path) if batch_path else None,
                  n_obj=n_obj, initialization='km_10_max' if hybrid else 'teacher_random_nearest_empty',
                  initial_genes=initial, reference_directions=len(refs) if algo == 'nsga3' else None,
                  initialization_seconds=initialization_seconds,
                  initialization_scalar_solves=len(LAMBDAS) if hybrid else 0,
                  initialization_objective_evals=len(LAMBDAS) if hybrid else 0,
                  inserted_km_genes=len(initial) if initial is not None else 0,
                  normalization_seconds=normalization_seconds,
                  normalization_scalar_solves=1 if hasattr(problem, 'normalization') else 0,
                  runtime_scope='runtime=EA only; total_runtime=initialization+EA; common normalization separate',
                  total_runtime=result['runtime']+initialization_seconds,
                  total_objective_evals=result['n_eval']+(len(LAMBDAS) if hybrid else 0),
                  HV=hypervolume(F, ideal, nadir), spacing=spacing(F, ideal, nadir),
                  ideal=ideal, nadir=nadir, ref=np.full(n_obj, 1.1),
                  provenance=provenance, completed_utc=datetime.now(timezone.utc).isoformat())
    if isinstance(problem, DTLZ2):
        result['front_error'] = float(np.abs(np.linalg.norm(F, axis=1)-1).mean())
    else:
        result['knee_index'] = knee_point(F)
        result['pickup_budget'] = .5*min(problem.n_drivers, problem.n_var)*problem.radius
        result['constraint_index'] = constraint_choice(F, result['pickup_budget'])
        result['greedy_F'] = problem.evaluate_one(np.ones(problem.n_var, int))
    for h in result['history']:
        h['HV'] = hypervolume(h['F'], ideal, nadir)
    path.write_text(json.dumps(jsonable(result), ensure_ascii=False, indent=2)+'\n')
    print(run_id, 'HV', result['HV'], 'runtime', result['runtime'], flush=True)
    return result


def write_km(problem, batch_id, batch_path, provenance):
    start = time.perf_counter()
    values = weighted_km(problem, LAMBDAS)
    solve_seconds = time.perf_counter()-start
    start = time.perf_counter()
    ideal, nadir = problem.normalization()
    normalization_seconds = time.perf_counter()-start
    F = np.asarray([r['F'] for r in values])
    item = dict(batch_id=batch_id, n_obj=problem.n_obj, runs=values,
                HV=hypervolume(F, ideal, nadir), spacing=spacing(F, ideal, nadir),
                ideal=ideal, nadir=nadir, batch_sha256=sha(batch_path), provenance=provenance,
                exact_scalar_solves=len(LAMBDAS), scope='same K-nearest candidate graph')
    item.update(solve_seconds=solve_seconds, normalization_seconds=normalization_seconds,
                objective_evals=len(LAMBDAS), normalization_scalar_solves=1,
                runtime_scope='solve_seconds includes 41 scalar assignments, objective sums and encoding; normalization separate')
    p = OUT/'km'/f'{batch_id}_M{problem.n_obj}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        # Preserve the original baseline record. Explicit timed recomputation is
        # supplementary evidence, rather than retrospectively timing an old run.
        original = json.loads(p.read_text())
        if not np.allclose([x['F'] for x in original['runs']], F, atol=1e-10, rtol=0):
            raise RuntimeError('KM recomputation differs from preserved baseline')
        item.update(identity='TIMED_RECOMPUTE', original_path=str(p.relative_to(ROOT)),
                    original_sha256=sha(p))
        timing_path = OUT/'km_timing'/p.name
        timing_path.parent.mkdir(exist_ok=True)
        timing_path.write_text(json.dumps(jsonable(item), ensure_ascii=False, indent=2)+'\n')
    else:
        p.write_text(json.dumps(jsonable(item), ensure_ascii=False, indent=2)+'\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', choices=['baseline', 'scale', 'hybrid', 'combination', 'confirmation'], required=True)
    ap.add_argument('--seeds', default='0,1,2,3,4')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    provenance = dict(evolution_sha256=sha(ROOT/'task2/src/evolution.py'),
                      runner_sha256=sha(Path(__file__)),
                      data_code_sha256=sha(ROOT/'task2/src/dispatch_data.py'),
                      source_data_sha256=sha(source_path()), data_identity='Foursquare proxy trips; local clock',
                      geometry='teacher conditional NYC local km; source_crs=UNVERIFIED')
    snapshots = OUT/'source_snapshots'
    snapshots.mkdir(exist_ok=True)
    for code in [ROOT/'task2/src/evolution.py', ROOT/'task2/src/dispatch_data.py', Path(__file__)]:
        dst = snapshots/f'{code.stem}_{sha(code)[:12]}.py'
        if not dst.exists():
            dst.write_bytes(code.read_bytes())
    bundle = load_data()
    seeds = [int(x) for x in args.seeds.split(',')]
    if args.stage == 'baseline':
        for hour in [18, 8, 13, 23]:
            bid, batch, bp = prepare_batch(bundle, hour)
            p = DispatchProblem(batch)
            write_km(p, bid, bp, provenance)
            for seed in seeds:
                for algo in ['nsga2', 'nsga3']:
                    save_run(p, bid, bp, 'baseline', seed, algo, 100, 300, 2, provenance)
        bid, batch, bp = prepare_batch(bundle, 18)
        p = DispatchProblem(batch, n_obj=3)
        write_km(p, bid, bp, provenance)
        for seed in seeds:
            for algo in ['nsga2', 'nsga3']:
                save_run(p, bid, bp, 'baseline', seed, algo, 105, 300, 3, provenance)
        for seed in seeds:
            for algo in ['nsga2', 'nsga3']:
                save_run(DTLZ2(), 'dtlz2_integer_teacher', None, 'baseline', seed, algo, 92, 400, 3, provenance)
    else:
        partition = 'test' if args.stage == 'confirmation' else 'inner'
        bid, batch, bp = prepare_batch(bundle, 18, partition=partition)
        p = DispatchProblem(batch)
        write_km(p, bid, bp, provenance)
        settings = {'scale': [(200, 300, False), (100, 600, False)],
                    'hybrid': [(100, 300, True)], 'combination': [(100, 600, True)],
                    'confirmation': [(100, 300, False), (100, 300, True)]}[args.stage]
        for pop, gen, hybrid in settings:
            for seed in seeds:
                for algo in ['nsga2', 'nsga3']:
                    stage = args.stage+('_km' if hybrid and args.stage == 'confirmation' else '')
                    save_run(p, bid, bp, stage, seed, algo, pop, gen, 2, provenance, hybrid=hybrid)


if __name__ == '__main__':
    main()
