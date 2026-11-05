# Weighted-KM runtime metadata correction

The canonical evaluator incorrectly used the historical EA timing description
for five development weighted-KM records. This is a descriptive metadata defect;
the stored objectives, geometry, costs and elapsed values were unchanged.

The18h two-objective record now inherits the existing `TIMED_RECOMPUTE` scope:
41 scalar assignments, objective sums and encoding; normalization is separately
timed. Its existing elapsed value remains0.006669564000048922seconds. The other
four development KM records have no original elapsed measurement; their scope
now explicitly states41 scalar assignments with objective sums/encoding,
uncaptured original elapsed time, and separate unrecorded normalization timing.
Their elapsed fields remain null. The five future KM scopes were already
correct and did not change.

`before/` preserves the old evaluator, local/public canonical packets, summary,
public manifest and ten figure sidecars. `before.json` records their hashes and
the protected-artifact hashes. The evaluator was run once to recompute canonical
metrics, followed by the unchanged original public projection producer once.
No matching solver, EA generation, model training, figure rendering or report
build was run.

`result.json` and `verify_metadata_update.py` record the exact differences:

- Local canonical:5 scope strings and evaluator-runner SHA changed.
- Public canonical:the same6 changes plus its local-source SHA.
- Public manifest:only that canonical binding's source/public SHA pair changed;
  the other123 bindings remain identical.
- All125 records'81,980 numeric leaves (paths, types and values),375 complete
  metric dictionaries at8/10/12decimals, and summary.csv bytes remain identical.
- The evaluator AST is identical except for the `runtime_scope` expression.
- Ten MOO sidecars now bind the current input SHA and explicitly identify this
  as metadata inheritance without a figure rebuild. Their original sidecars
  remain in `before/`. The other418 protected artifacts, including raw runs,
  figures and reports, retained their bytes during this scoped correction.

This is an appended author check. Earlier independent reviews retain their old
artifact hashes. R's separate follow-up certifies the new metadata inheritance;
it does not claim a new EA experiment or overwrite the original mathematical
review. Later root report-source provenance updates are outside this snapshot's
actual execution window and need their own current hashes.
