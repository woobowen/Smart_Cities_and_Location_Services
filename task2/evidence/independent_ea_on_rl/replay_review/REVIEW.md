# Appended verification of the fixed-model final replay

Task V-REPLAY-004; reviewer `/root/evolution`, separate from RL author
`/root/reinforcement`. The coordinator reported that `run_rl_final.py --help`
entered the former script's ordinary evaluation path because it had no argument
parser. This was a **REPLAY/RECOMPUTE with the same frozen models, inputs,
parameters and test seeds**. It supplies no additional independent test sample.
The reviewer did not train, dispatch a new episode, or select a candidate.

The original independent `result.json`, `policy_result.json`, review text and
verification source remain unchanged; exact hashes and complete snapshots are
in `previous_review_hashes.json` and `previous_reviews/`. Their old artifact
hashes are historical, not substitutes for new replayed hashes.

## New independent checks actually executed

`verify_replay.py` reads the controlled recovery snapshot and current outputs.
It independently reconstructs all95affected final trajectories from original
episode NPZ arrays, without calling the author's simulator. It verifies actual
driver positions/busy periods, neighbor moves and travel costs, order identity,
arrival/cancellation/conservation, horizon categories and saved metrics.

- All95episode and95trace hashes match the original independent receipt exactly.
- All five model NPZ and original training-manifest hashes match the pre-replay
  active registry. They were reused; no new training is claimed.
- The19affected policy summaries retain all scientific means and sample SDs.
- All25saved paired-comparison rows retain every individual simulated-day
  difference, mean, sample SD and descriptive t95 interval.
- All1060selected dynamic fusion frames were independently checked again using
  the original model V, true current idle/active context, selected local pairs,
  objective sums, knee/constraint rule and1240evaluation budget.

Actual evidence: `result.json`, `verify_replay.py`, `run.log`. Current per-day
timing summaries are identified as REPLAY timing. The four original complete
day-metric files and their per-seed runtime bytes were not available; their
old hashes and surviving aggregate timing summaries are retained honestly.

## Additional recovered-byte check

After the main replay check, the RL author recovered the original complete
`fusion_fronts.json` using surviving public per-frame timing values and the
unchanged scientific fields. `compare_recovered_front.py` independently confirms
that those recovered bytes have exactly the original SHA-256 recorded by the
earlier independent audit. This is actual hash-verified recovery of that one
file; it does not recover the four original day-metric files.

Comparing the recovered original with the current replay confirms5300non-runtime
fields exactly equal, including the complete F vectors, selected local pairs,
point indices, times and evaluation counts. The1060frame runtime values changed.
Evidence: `recovered_front_result.json`, `recovered_front.log`.

## Consequences and remaining integration

Scientific result/figure conclusions may inherit their verified numerical
scope, because the scientific inputs and values are unchanged. Affected active
raw, derived and public-projection hashes must be rebound to their actual
current bytes. Original hashes, reviews and any valid earlier timings retain
their historical identity. CLI parsing/overwrite-guard repair and publication
binding updates are recorded by their actual implementers; this appended
verification does not silently overwrite those artifacts.

MOO, development experiments and the separate20episode MonteCarlo confirmation
were unaffected and were not rerun. The original5episode and separate20episode
statistics are not pooled, and this duplicate evaluation cannot increase n.

## Actual CLI and public-binding closure

The reviewer separately read the repaired parser and actually executed
`--help` (exit0) plus the default existing-output invocation (exit2) in the
real workspace. All145protected final artifacts and original review files kept
their hashes. The parser rejects existing output before importing the experiment
stack. Evidence: `cli_guard_independent.json`.

After the RL author explicitly fixed the replay sources and supplied the refresh
list, the unchanged original public-projection producer was executed exactly
once. Precisely one of124public bindings changed: `rl/final_fronts.json`.
Its1060changed scalar fields are all actual replay runtimes; every scientific
field remains exactly equal to the previous public file. The other123public
bindings, including all MOO projections, remain byte-identical. The public
manifest differs only in that binding's source/public SHA values. The producer
and original independent public-projection audit remain unchanged.

`public_binding_result.json` explicitly identifies the current artifact as
REPLAY/RECOMPUTE and binds its current raw/public hashes to the preserved prior
audit. It is the appended current binding receipt; earlier audits retain their
original scope. Registry, statistical-summary and other source-index refreshes
are the RL author's separate integration responsibility.
