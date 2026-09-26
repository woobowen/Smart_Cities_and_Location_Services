# Actual pilot direction-roundoff repair

Issue: `NUMERIC:g1-complete-pilot-01:baseline`. Root assigned B-Repair after the
runtime independent review rejected the actual conditional pilot. This is an
actual numerical-review failure, distinct from the earlier constructed C2 probes.

The two differences are both in record 246, segment 0:

| Original index | Field | Production value (degrees) | Independent value (degrees) |
|---|---|---:|---:|
| 38 | previous difference | 1.1670533768196947 | 1.1670533768196378 |
| 38 | following difference | 8.793643352415529 | 8.793643352415472 |
| 64 | previous difference | 3.926916060978101 | 3.926916060978158 |
| 64 | following difference | 3.7674557901295884 | 3.7674557901295316 |

Every difference has magnitude `5.684341886080802e-14` degrees. The complete
input windows, normalized bearings, candidate/reason fields and before-source
hash are recorded in `root_cause.json`. Both windows have `candidate=false` in
both implementations. There is no deletion disagreement.

The production circular formula adds/subtracts a half turn and applies modulo;
the independent formula takes the shorter of the two normalized angular gaps.
Floating cancellation therefore scales with the normalized input angle, not only
the small final residual. The previous generic relative comparison used the
residual scale and falsely rejected ordinary roundoff.

`evaluation.py` now checks only the two reported angular-difference fields with
the fixed allowance

`64 × binary64 epsilon × 360 degrees = 5.115907697472721e-12 degrees`.

The pre-existing engineering factor 64 is applied to the fixed one-turn domain,
not chosen from the observed mismatch. Reported values must still be finite and
within `[0, 180]`. Candidate Boolean type/value, original index, undefined reason,
deleted indices, strict `>35°` predicate and actual clean/final values remain
strictly checked. No production direction function, coordinate model, method
parameter or DP tolerance/verification rule was changed.

Executed from repository root:

```sh
.venv/bin/python -m pytest task1/tests/test_baseline_trust.py task1/tests/test_geometry.py task1/tests/test_evaluation.py -q --junitxml=task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/b_repair/direction_roundoff/tests.xml
.venv/bin/python -m task1.evidence.goal1.revisions.SC-LAB1-G1-COMPLETE-001.b_repair.direction_roundoff.recheck_candidate
git diff --check -- task1/workflow/evaluation.py task1/tests/test_baseline_trust.py
```

Actual results: **124 passed in 0.17 s**; the unchanged pilot-01 candidate has a
new independent numeric inspection `VERIFIED`; diff check passed. Tests include
the two explicitly labeled derived engineering windows, circular known answers,
exact threshold protection, wrong candidate types, wrong identities, undefined
windows, invalid unsigned angles, and errors larger than the fixed allowance.

The old candidate and its old `REJECTED` review remain byte-identical. Their
hashes and the new source hash are in `candidate_recheck.json`. This reinspection
is diagnostic and does not rehabilitate old code lineage; root must fix the new
CODE_SHA and rebuild a new run after C review. B did not close its own issue.

Provider calls: 0. Production reruns by B: 0. No installs, commits or pushes.
The frozen Notebook/figure generators were not modified during this repair.
