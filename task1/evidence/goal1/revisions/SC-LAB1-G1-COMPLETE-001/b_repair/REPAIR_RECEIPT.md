# B-Repair C2-F02 execution receipt

Classification: **ENGINEERING_TEST / CONSTRUCTED_FIXTURE**. The issue source is
the external GPT review and C's recorded reproduction, not a claimed new model
discovery. This receipt records visible inputs, actions and outputs only.

## Inputs and authorized scope

- Read repository `AGENTS.md`, the current COMPLETE-001 Prompt and its §6 eight
  checks, production geometry/pipeline/evaluation, existing baseline tests, and
  `c_initial/initial_reference_probes.json`.
- First workspace command: `ls -la`. Reused the existing `.venv`.
- B owned `workflow/evaluation.py`, `workflow/pipeline.py`, the new
  `tests/test_baseline_trust.py`, and only the old baseline interface calls in
  `tests/test_repair.py`. Root owns coordinate definitions, contracts, policy,
  tools, controller and the overall Goal.
- Later user authorization was delivered by root: D2 approved, and conditional
  pilot analysis permitted while source CRS remains UNVERIFIED. B connected
  root's frozen `coordinates.registration()` through its allowlisted ID. B did
  not choose the coordinate model or alter its registration or parameter file.

## Actual changes

1. `review_baseline(candidate, trusted_complete_inputs, approved_contract,
   trusted_provenance)` rejects absent references. A detached constructed handle
   comes directly from caller inputs before any candidate exists.
2. Production output binds original/working records, raw and input hashes,
   contract/order/units, adapter version and parent hashes. Each record includes
   counts and an explicit terminal status; each point includes segment, action,
   reasons, values and parent hash.
3. The independent reviewer reads no candidate field as the original reference
   or tolerance. Direct predicates check strict cut boundaries, original index
   coverage, filtering reasons, direction windows including undefined retention,
   actual clean/final values, finite DP index intervals, zero-tolerance identity,
   actual ledger values, per-record counts and global summaries.
4. Empty and legally all-filtered tasks can verify structurally, with no output
   and quality limitations explicitly reported. Missing nonempty records reject.
5. Real references require a registered contract and verified original-file
   values. Conditional authorization preserves `source_crs=UNVERIFIED` and the
   `CURRENT_RUN_CONDITIONAL_ANALYSIS` label. D2 uses the archived decision's hash
   and contents, independently of the old overall processing-status flag.

No reviewer call invokes the production runner or production geometry functions
to manufacture its expected result. A regression patches those functions to
raise and proves the independent review still runs. A separately patched wrong
production filter is rejected.

## Executed verification

Working directory: repository root.

```sh
.venv/bin/python -m pytest task1/tests/test_baseline_trust.py task1/tests/test_repair.py::test_complete_constructed_runner_and_independent_review task1/tests/test_repair.py::test_constructed_approval_cannot_unlock_real_input task1/tests/test_geometry.py task1/tests/test_evaluation.py -q --junitxml=task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/b_repair/baseline_tests.xml
```

Actual final run: **109 passed in 0.83s**, exit 0. Earlier incremental runs passed
104 and 105 tests; these are not additional independent cases or full-suite runs.

```sh
.venv/bin/python -m task1.evidence.goal1.revisions.SC-LAB1-G1-COMPLETE-001.b_repair.run_reference_probes
git diff --check -- task1/workflow/evaluation.py task1/workflow/pipeline.py task1/tests/test_repair.py task1/tests/test_baseline_trust.py
```

Both exited 0. `reference_probes.json` records the explicit inputs, trusted
contract/provenance, source hashes and actual review output: the four-point
control verifies; only-final change, simultaneous clean/final translation,
record/ledger erasure, 999 summaries and a mismatched complete reference all
reject. The new tests also exercise the tool's different raw-scope case.

## Boundary and handoff

- B self-check is complete; C's independent closure decision is pending.
- Real production baseline runs by B: **0**. Provider calls: **0**. No commit or
  push. Raw teacher inputs and historical results were not edited.
- No packages, toolchains or shell configuration were installed or changed.
- This is the C2-F02 engineering handoff, not completion of the parent Goal or
  a claim of ground truth recovery, quality improvement, or final report status.
- Root must run the complete current work suite and align historical controller
  fixtures with the user's newly authorized conditional processing policy.
