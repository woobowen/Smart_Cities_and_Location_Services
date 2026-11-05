# Multiobjective dispatch: measured result summary

Canonical metric packet SHA-256: `36f1387a2eb0153a1f269310c64e94411cd5505077930c4586a16ac2eb732faf`.
Every ± below is sample SD (`ddof=1`) across the stated five repetitions, not a confidence interval.
Raw runs/source snapshots are preserved; raw legacy HV/spacing fields are superseded by the uniformly recomputed canonical metrics.

## Separate basic-teacher NSGA-II task

The basic task was separately executed on20drivers/20synthetic OD requests in the10×10km PPT square,
with Euclidean pickup and delivered OD distance as the revenue proxy. It does not reuse advanced simulated fares.
Five EA seeds0..4, fixed synthetic input seed2024, optional matching over the full candidate graph.
Scalar utility is delivered-km minus λ×pickup-km; the same-instance exact optional KM supplies OPT/EA.
This is a static approximation ratio and cannot be a theoretical online competitive guarantee.

| λ | Mean OPT/EA | Range across five EA seeds |
|---:|---:|---:|
| 0 | 1.000000 | 1.000000–1.000000 |
| 0.25 | 1.002652 | 1.001152–1.006384 |
| 0.5 | 1.002955 | 1.002216–1.003834 |
| 1 | 1.000580 | 1.000000–1.001308 |
| 2 | 1.003160 | 1.000000–1.005972 |

## Part A baseline and geometry

Training-inner18h batchseed2024,40drivers/80orders,K6,radius3km; seeds0..4.
Two objectives use100population/300generations; three use the actual Notebook105population/105directions/300generations.
Common instance-prior normalization: exact maximum-revenue bound, pickup≤min(n,m)×radius and count≤min(n,m); ref1.1.
Normalized HV can exceed1 because the reference point is1.1. No method-specific normalizer is used.

| Problem | Algorithm | HV mean ± sampleSD | Mean Spacing CV | Mean EA seconds |
|---|---|---:|---:|---:|
| Dispatch2D | nsga2 | 1.090244 ± 0.004460 | 0.505364 | 2.455 |
| Dispatch2D | nsga3 | 1.077092 ± 0.009530 | 0.938251 | 3.601 |
| Dispatch3D | nsga2 | 1.014845 ± 0.010260 | 0.620843 | 2.560 |
| Dispatch3D | nsga3 | 1.012638 ± 0.005689 | 0.688450 | 4.220 |
| Integer DTLZ2 | nsga2 | 0.707111 ± 0.006190 | 0.480398 | 1.087 |
| Integer DTLZ2 | nsga3 | 0.744325 ± 0.000235 | 0.296525 | 1.841 |

Weighted KM18h2D canonical HV=1.098977, Spacing CV=0.662230;3D HV=1.023454.
DTLZ2 uses the teacher integer domainK200/nvar12/N92/G400. Five-seed results support NSGA-III on this benchmark;
three-objective dispatch gives a much smaller, variable difference and its fare/service projection remains correlated.
No universal dimensionality-only superiority is inferred.

## Single-factor controls, initialization, and combination

| Algorithm | Intervention | HV mean ± sampleSD | Mean Spacing | EA evals | Extra KM init solves | Mean EA+init seconds |
|---|---|---:|---:|---:|---:|---:|
| nsga2 | Teacher100×300 | 1.090244 ± 0.004460 | 0.505364 | 30100 | 0 | 2.455 |
| nsga3 | Teacher100×300 | 1.077092 ± 0.009530 | 0.938251 | 30100 | 0 | 3.601 |
| nsga2 | Population200×300 | 1.101432 ± 0.004523 | 0.617271 | 60200 | 0 | 4.294 |
| nsga3 | Population200×300 | 1.085327 ± 0.006452 | 1.179619 | 60200 | 0 | 5.651 |
| nsga2 | Generations100×600 | 1.094778 ± 0.006998 | 0.501365 | 60100 | 0 | 3.296 |
| nsga3 | Generations100×600 | 1.090552 ± 0.006213 | 0.931240 | 60100 | 0 | 4.504 |
| nsga2 | KM init100×300 | 1.111427 ± 0.000291 | 0.470140 | 30100 | 41 | 2.032 |
| nsga3 | KM init100×300 | 1.111494 ± 0.000169 | 0.901161 | 30100 | 41 | 3.021 |
| nsga2 | KM init+population200×300 | 1.112912 ± 0.000072 | 0.626300 | 60200 | 41 | 4.519 |
| nsga3 | KM init+population200×300 | 1.112072 ± 0.000085 | 1.228595 | 60200 | 41 | 5.939 |

These interventions were staged after observed results: baseline → single-factor population/generations → KM-only initialization → one justified KM+population combination.
The matching-to-gene roundtrip is tested, so hybrid means actual KM individuals in the initial population.
The combination adds only0.001485meanHV forII and0.000578forIII over KM-only, while doubling EA evaluations and worsening Spacing.
Retain the teacher-budget KM-only intervention for the isolated confirmation; keep combination as a documented quality/cost extension.
No further search is justified by a new mechanism question under the bounded120full-run budget.
Runtime is an actual observation under concurrent local work, not a controlled microbenchmark or a reliable claimed speedup.
Shared normalization cost is separate; initialization adds41scalar solves/41objective sums. Earlier untimed KM baselines have explicit TIMED_RECOMPUTE supplements.

## Five unseen future-pool input batches

The final contract was frozen before test outputs. Input seeds9010..9014 pair teacher-II and KM-initialized-II at100×300;
algorithm seeds10..14,18h future-date proxy pool, training-only driver prior, no post-test selection.

| Input seed | Teacher HV | KM-init HV | Paired change |
|---:|---:|---:|---:|
| 9010 | 1.042422 | 1.074096 | +0.031674 |
| 9011 | 1.052557 | 1.092004 | +0.039447 |
| 9012 | 1.067154 | 1.089801 | +0.022647 |
| 9013 | 1.059461 | 1.087311 | +0.027849 |
| 9014 | 1.072543 | 1.108278 | +0.035735 |

Mean paired HV change=0.031470, sampleSD=0.006573; all five observed changes are positive.
The statistical units here are five independently resampled future-pool inputs, unlike development seed comparisons on one fixed input.
This does not establish real taxi-platform effects or cover all future instances.

## Teacher Part A thought questions answered

1. Weighted KM is strong here because many useful trade-offs are supported by linear scalarization; the observed front is close to a convex-supported shape.
   It still misses unsupported nondominated points on nonconvex/discrete trade-offs. An actual one-driver counterexample with(revenue,pickup)=(3,1),(6,3),(9,4) has unsupported middle point:
   beating the first needs λ≤1.5, beating the last needs λ≥3, which is impossible. The exhaustive test verifies this, without claiming every observed EA point is an unsupported optimum.
2. In two-objective dispatchII is better at the teacher budget on this input; in three-objective dispatch means are close with variation.
   Crowding measures local separation, while reference niching seeks objective-space directions; many directions are unused on a thin/correlated front.
   On the sphere-like DTLZ2 frontIII has higher HV and lower Spacing in the actual five-seed experiment. Benchmark evidence cannot override dispatch outcomes.
3. The table separates more population, more generations, real KM initialization and their combination, including counts and timings. Initialization is the strongest low-budget intervention here.
4. Knee chooses geometric curvature after normalization, but is sensitive to endpoints/scaling and has no guaranteed operational acceptability.
   A fixed pickup constraint encodes an explicit service budget, but requires a defensible X and may be non-binding or infeasible.
   Our pre-fixed60km budget is non-binding on the illustrated batch, so it selects the highest-revenue EA solution, whereas the knee chooses a lower-distance compromise.
   Neither can be called universally best; deployment requires an actual service preference.

## Verification and traceability

- Ten mathematical author tests: exhaustive tiny matching/encoding, independent scalar enumeration, known+random2D/3DHV inclusion-exclusion+pymoo, DTLZ formula comparison, odd105offspring, degenerate metrics, unsupported counterexample.
- Independent research-data agent re-decoded baseline raw genes from NPZ, independently recomputed objective sums/historyHV, used a separate box-union reference, and verified tiny scalar matchings.
- That verifier found two real issues: omitted hybrid initialization cost and KM Spacing over dominated/near-duplicate points. Both were repaired before formal conclusions; raw old data remain historical.
- All methods use10decimal canonical reporting fronts;8/10/12sensitivity is retained per record. Raw EA selection remains unchanged.
- Code/input/batch hashes, exact genes/pairs/objectives/history/evaluation count/time are retained in raw JSON plus source snapshots.
-115full EA runs including the separate five basic runs;125canonical records also include ten exact-KM batch references. Pilots and mathematical tests are distinct.
- The glyph/placement check is figure-author work, and final PDF-page review is separately recorded by the report builder.

## Reproduction entries

Run from repository root using project `.venv/bin/python`:

```text
.venv/bin/python -m pytest -q task2/tests/test_evolution.py
.venv/bin/python task2/scripts/run_basic_multiobjective.py
.venv/bin/python task2/scripts/run_evolution.py --stage baseline
.venv/bin/python task2/scripts/run_evolution.py --stage scale
.venv/bin/python task2/scripts/run_evolution.py --stage hybrid
.venv/bin/python task2/scripts/run_evolution.py --stage combination
.venv/bin/python task2/scripts/run_evolution.py --stage confirmation --seeds 10,11,12,13,14
.venv/bin/python task2/scripts/evaluate_evolution.py
.venv/bin/python task2/scripts/summarize_evolution.py
.venv/bin/python task2/scripts/build_evolution_figures.py
```

Existing run IDs are preserved and checked against the EA source hash; archived source snapshots reproduce historical runs.
The runner recomputes/fixes batches from the source pool and checks exact array equality before reusing them.
Figure sidecars bind raw inputs, canonical metric packet, plotting source and exact common P2 palette.
