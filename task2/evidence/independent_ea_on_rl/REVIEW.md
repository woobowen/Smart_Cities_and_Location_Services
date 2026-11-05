# Independent RL verification by the evolutionary-methods agent

Reviewer: native child `/root/evolution`. RL author: native child
`/root/reinforcement`. This is a separate role/context and independently written
reference, not the RL author re-running their own simulator. Evidence is
`result.json`, `policy_result.json`, the two actual executed verification scripts
and logs in this directory, with exact source/input/trace/model hashes.

## Actual checks and outcome

- **375 raw validation/final/MonteCarlo traces:** an independent discrete-event
  replay reads original episode NPZ arrays. It never calls `run_episode`.
  Each driver's availability and release position, pickup radius, actual trip
  time, unique requests, patience cancellation, horizon categories and order
  conservation are reconstructed. Every real reposition movement must go to an
  adjacent region center, consume its Manhattan km and ceil travel time, and
  block the driver until release. Recomputed accepted/completed fare, pickup,
  response, cancellation, empty km/minutes and terminal ledger agree with the
  corresponding saved per-day metrics.
- **Mathematics:** independently hand-computed Q/Double targets verify
  `avail∪WAIT`, exclusion of a deliberately high infeasible action, visit-count
  learning rate, terminal transition, both Double update branches, cross-table
  selection/evaluation and the explicitly implemented symmetric V estimator.
  The entire regional LT table also agrees with a separate nested-loop formula.
- **Actual β=1 policies:** one valid Q trajectory and one valid corrected-Double
  trajectory use their saved V models. Independently computed LT/weights and
  exact same-context scalar maxima agree with every recorded dispatch. The
  nonpositive-edge counters are additionally checked on these two trajectories.
- **Static fusion:** all125front solutions across five seeds are independently
  decoded from genes with original candidate edges and directly summed edge
  values/pickup. Exhaustive2040partial matchings of the sparse eight-driver
  graph verify all41weighted scalar references. This is an exact check of this
  captured instance, not proof of global NSGA optimality.
- **Dynamic fusion:** all1064validation and1060final saved NSGA frames are bound
  to raw episodes via the appended actual-order mapping. Local pairs are
  reconstructed from independently replayed idle/active identities, selected
  objective values are recomputed from true weights/distances, knee or fixed
  0.6-parent-pickup constraint selection is checked, and actual1240EA evaluations
  per solved time slice agree with the40×30budget.
- **Paired uncertainty:** saved per-day raw metrics independently reproduce
  mean/sampleSD/paired t95 intervals. In the20episode fixed-model MonteCarlo
  confirmation, KM+move3 minus QKM gives accepted-fare change435.454758,
  t95[141.684455,729.225061], and extra empty848.079160km. At explicitly
  hypothetical cost1fare-unit/km, paired diagnostic net change is−412.624402,
  t95[−717.029509,−108.219296]. A positive net-return claim is unsupported.

All these checks passed in their stated scope. The metric intervals are
conditional on the frozen model and fixed historical proxy pool; simulated
episodes are not actual operational dates, and they do not incorporate learned
model uncertainty or real fuel prices.

## Review feedback and real repairs

The combined dynamic-front file originally lacked day IDs. Review identified
this traceability gap; the author appended a mapping using the actual fixed
evaluation loop order, strict within-day time increase, four time resets and
per-frame raw-trace cardinality checks. The verifier then independently checked
all mapped pairs, objective values and selections. Original F/pairs were not
rewritten, and no claim is made that the day tag was present in the original run.

The verifier's first raw replay attempt repeatedly decompressed NPZ members on
every scalar access. Inspection of the installed NumPy `NpzFile.__getitem__`
source located the cost. That attempt was stopped before any result receipt;
its log is `attempt1_uncached_npz.log`. The successful attempt materializes each
episode once, keeping reference mathematics and inputs unchanged. This is a
verifier engineering repair, not an RL experiment failure or a new experiment.

## Limits

This review does not independently retrain all300episode models or certify a
general-purpose optimal policy. It checks the actual listed raw artifacts,
mathematics, selected policies, physical simulation and metrics. Runtime values
remain the author's real measurements; the reference is not a timing benchmark.
No user-understanding acceptance, teacher submission, external GPT audit or
Process Evidence Lock is declared. PDF text/placement is outside this packet.
