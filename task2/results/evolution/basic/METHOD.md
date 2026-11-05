# Basic NSGA-II: separately executed teacher task

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
