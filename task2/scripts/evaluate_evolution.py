#!/usr/bin/env python3
"""Recompute canonical set metrics without overwriting immutable raw EA runs."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'task2/src'))
from front_metrics import evaluate_front


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'task2/results/evolution'
    rows = []
    for path in sorted(list((out/'runs').glob('*.json'))+list((out/'km').glob('*.json'))+list((out/'basic').glob('basic_nsga2_seed*.json'))):
        r = json.loads(path.read_text())
        is_km = 'runs' in r
        timing_recompute = out/'km_timing'/path.name
        timing = json.loads(timing_recompute.read_text()) if is_km and timing_recompute.exists() else {}
        F = [v['F'] for v in r['runs']] if is_km else r['F']
        metrics = evaluate_front(F, r['ideal'], r['nadir'])
        sensitivity = {str(d): evaluate_front(F, r['ideal'], r['nadir'], d) for d in [8, 12]}
        rows.append(dict(path=str(path.relative_to(ROOT)), raw_sha256=sha(path),
                         run_id=r.get('run_id', path.stem), stage=r.get('stage', 'weighted_km' if is_km else 'basic'),
                         algorithm='weighted_km' if is_km else r['algorithm'],
                         batch_id=r.get('batch_id', 'basic_synthetic_od'), n_obj=r.get('n_obj', 2),
                         seed=r.get('seed'), pop_size=r.get('pop_size'), n_gen=r.get('n_gen'),
                         n_eval=r.get('n_eval', r.get('objective_evals', r.get('exact_scalar_solves'))),
                         total_objective_evals=r.get('total_objective_evals', r.get('n_eval')),
                         runtime=r.get('runtime', r.get('solve_seconds', timing.get('solve_seconds'))),
                         total_runtime=r.get('total_runtime', r.get('runtime', r.get('solve_seconds', timing.get('solve_seconds')))),
                         timing_recompute_path=str(timing_recompute.relative_to(ROOT)) if timing else None,
                         timing_recompute_sha256=sha(timing_recompute) if timing else None,
                         runtime_scope=r.get('runtime_scope', timing.get('runtime_scope',
                             f"{r['exact_scalar_solves']} scalar assignments with objective sums and encoding; original elapsed time not captured; normalization timing separate and unrecorded"
                             if is_km else 'EA-only in original baseline; initialization absent')),
                         front_error=r.get('front_error'), ideal=r['ideal'], nadir=r['nadir'],
                         metrics=metrics, numerical_sensitivity=sensitivity))
    p = out/'metrics.json'
    p.write_text(json.dumps(dict(evaluator_sha256=sha(ROOT/'task2/src/front_metrics.py'),
        runner_sha256=sha(Path(__file__)), primary_decimals=10,
        rule='all methods round to 10 decimals, deduplicate, remove dominated points, then common normalized HV/Spacing',
        supersedes='raw-run HV/spacing fields are historical author metrics; use this uniformly recomputed packet',
        rows=rows), indent=2)+'\n')
    fields = ['run_id','stage','algorithm','batch_id','n_obj','seed','pop_size','n_gen','n_eval',
              'total_objective_evals','runtime','total_runtime','HV','Spacing_cv','canonical_nondominated','front_error']
    with (out/'summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            flat = {k: r.get(k) for k in fields}
            flat.update({k: r['metrics'][k] for k in ['HV','Spacing_cv','canonical_nondominated']})
            writer.writerow(flat)
    print('Canonical metric records', len(rows), flush=True)


if __name__ == '__main__':
    main()
