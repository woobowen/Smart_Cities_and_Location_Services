# E-A-001 · Multi-objective dispatch contract

Author: native child agent `/root/evolution`; input: approved Master Prompt,
advanced Notebook cells 5–24 and PPT slides 4–13/24. Implementation follows the
teacher's integer-encoded NSGA-II / NSGA-III, not a claim of reproducing every
detail of the original continuous-optimization algorithms.

## Mathematical definition fixed before results

Each request selects zero or one of its closest K=6 drivers within 3 km Manhattan
pickup distance. Requests are decoded in source order; conflicts rotate through
that request's candidate list; no driver/request is reused. Every tested method
uses this exact candidate graph. Objectives to minimize are (-simulated fare,
total pickup km), with -matched count as the third objective. Fare=5+2*trip_km is
a teaching proxy, not actual taxi income. Zero dispatch is a valid endpoint.

NSGA-II uses nondominated sorting, per-front crowding, binary tournaments,
uniform crossover probability .9 and reset mutation probability 1/m. NSGA-III
uses the teacher's random mating, extreme-point/intercept normalization and
reference-direction niching. Two objectives: population 100 and 100 directions;
three: Notebook cell19 population 105 and 105 directions (H=13). This differs
from PPT slide9's general population100 reference and is recorded explicitly.
Odd populations generate exactly N offspring, correcting starter variation's
one-offspring truncation; evaluation counts include initial population.

Weighted KM maximizes fare-lambda*pickup over the same edges, with optional
unmatched vertices via zero/dummy weights. It solves each scalarized sum exactly;
it is neither a bottleneck solver nor a proof of the complete Pareto set.

HV uses one fixed instance-derived normalization for every method and iteration:
fare upper bound = exact maximum-revenue candidate matching; pickup upper bound
= min(n,m)*radius; count upper bound=min(n,m). Ideal=(-fare_bound,0,-count_bound),
nadir=(0,pickup_bound,0); reference=(1.1,...). This conservative normalization is
frozen before algorithms run, avoiding method-dependent/post-selection scaling.
DTLZ2 uses ideal0/nadir1 and the same reference. Spacing is the teacher's nearest
L1-distance coefficient of variation on distinct normalized front points;
fewer than two distinct points or zero mean separation gives explicit NA.

KM initialization actually converts a feasible matching into a gene and checks
decode equality. Hybrid inserts at most ten distinct KM genes while preserving
the nearest-driver and empty seeds. Knee=largest perpendicular distance from
endpoint chord; constraint selection maximizes revenue subject to a fixed
pickup budget 0.5*min(n,m)*radius. These are differing preference rules, not
claims that one selection is universally best.

## Data, comparisons and budget

Use shared dispatch_data conditional local-km geometry and chronological splits.
Primary experiments use training-inner trip pool and only training-inner
checkin hotspots; validation and final test are separately labeled. No future
checkin hotspot is used in training. Driver arrival locations are synthetic
hotspot+jitter and batch orders resample proxy trips; this is not real dispatch.

Stages: mathematical/unit checks -> pilot runtime -> two/three objective five
seed baselines and teacher DTLZ2/hour comparisons -> inspect verified results ->
population-only/generation-only controls -> KM-only initialization -> justified
combination or recorded rejection. Primary seeds0..4 are paired. Runtime and
objective evaluation count accompany quality. Additional experiments are chosen
after observed results; all teacher requirements take priority. Default bounded
research budget: <=120 full EA runs, <=4 worker processes, BLAS threads1; stop
exploration when no specific new hypothesis remains or this budget is reached.
Data/code hashes and exact parameters are saved with every raw run.

## Verification references actually consulted

- Deb et al. (2002), [original NSGA-II paper](https://doi.org/10.1109/4235.996017):
  nondominance, elite parent/offspring selection and crowding; not dispatch gains.
- [pymoo official NSGA-III](https://pymoo.org/algorithms/moo/nsga3.html), accessed
  2026-11-05: reference association/niching and reference counts; no guarantee
  NSGA-III wins this instance. Web docs currently0.6.2, installed verifier0.6.1.6.
- [pymoo indicators](https://pymoo.org/misc/indicators.html): independent HV API.
- [pymoo DTLZ](https://pymoo.org/problems/many/dtlz.html): benchmark definition.

Small exhaustive matchings verify feasible graph, nondominance and scalar sums;
box inclusion-exclusion verifies 2D/3D HV independently, with pymoo as an extra
cross-check. Original teacher code is preserved untouched. This agent's own
tests are author checks; later cross-agent review is separately attributed.
