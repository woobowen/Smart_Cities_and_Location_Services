# E-A actual research decisions

## Initial pilot and author checks

20-generation paired pilot: NSGA-II0.1919s/NSGA-III0.1979s, N100; extrapolated
~3s per300-generation run. Bounded60-run primary baseline was feasible on one
CPU process/BLAS1. Ten mathematical tests now pass. The initial .28 exact-float
assertion failed by ~5e-17; the test tolerance was corrected to1e-12 without
changing the algorithm. Independent box inclusion/exclusion and pymoo HV agree.

## Baseline observed before scale controls

All60primary runs completed. On inner-training18h, five-seed canonical HV mean
± sampleSD: NSGA-II1.090244±0.004460, NSGA-III1.077092±0.009530; scalar KM1.098977.
Three-objective dispatch HV: II1.014845±0.010260, III1.012638±0.005689. On integer
DTLZ2: II0.707111±0.006190, III0.744325±0.000235. These are measured results;
PPT numerical examples were never used as current outputs.

The high-revenue endpoint gap and higher NSGA-III spread motivate the teacher's
population-only N200/G300 and generations-only N100/G600 controls on the same
18h input and paired seeds0..4. The question is whether extra evaluations close
the gap before introducing initialization. Both have ~60k objective evaluations,
so compare n_eval and measured runtime rather than just calling either larger.
No test input has entered candidate selection.

## Independent V feedback before hybrid

Research-data agent independently found (a) hybrid runtime omitted its41KM
initializations, before any hybrid was run; (b) KM Spacing included dominated
scalar solutions and ~1e-13 summation-order duplicates. Fix(a): runner now records
initialization time,41scalar solves/41objective sums, EA-only time, total time,
and shared normalization separately. Fix(b): keep original raw results/source
snapshots; derive reporting fronts uniformly by round10decimals→unique→ND filter.
Independent feedback accepted this as numerical reporting repair, without
changing EA selection. Precision sensitivity8/10/12digits across70records gave
max HV change1.67e-9 and max Spacing change6.55e-9. Original raw fields remain
historical; authoritative canonical metrics live in results/evolution/metrics.json.

Original baseline scalar-solver timings were not measured. Later timings are
explicit TIMED_RECOMPUTE supplements, not retroactive claims about old runtime.

## Population/generation controls observed before KM initialization

Twenty control runs completed under the unchanged EA core. NSGA-II meanHV:
N100/G3001.090244 → N200/G3001.101432 / N100/G6001.094778.
NSGA-III:1.077092 →1.085327 /1.090552. Population and generation increases each
cost ~60k EA objective evaluations but have different effects. II/N200 exceeds
scalar KM's1.098977, so the entire-front gap cannot be reduced to just revenue.
The initial hypothesis is only partly supported: the favorable intervention
varies by algorithm. No universal NSGA-III advantage is inferred from3objectives.

Next teacher-required isolated intervention: insert at most10distinct exactly
encoded KM genes into the original N100/G300 population (nearest/empty seeds
remain). Compare both algorithms over the same5paired seeds. No increase in
population/generations is combined at this stage. This isolates whether better
supported endpoints help low-budget EA explore unsampled trade-offs, with41
extra scalar solves/objective sums and actual initialization time recorded.

## Isolated KM initialization observed before combination

Five-seed canonical HV after only injecting up to10KM genes: II1.111427±0.000291;
III1.111494±0.000169 (sampleSD). Both exceed scalar KM1.098977 and the tested
single-factor scale controls, with the same30100EA evaluations plus41scalar
solves/objective sums; measured initialization~.011s. Lower seed variation is
an observation on this shared input, not a confidence guarantee for new traffic.

Since increased population improved II more than extra generations and KM seeds
supply supported endpoints rather than more independent individuals, test one
limited complementary combination: KM initialization+N200/G300, both algorithms,
seeds0..4. Compare baseline, population-only, KM-only and their combination; this
is also a removal/ablation comparison. Extra generations are not simultaneously
added. The old unexecuted runner option100/G600 was changed before any combination
run, following this actual result-driven choice.

## Final confirmation contract frozen before test outputs

Final confirmation will compare NSGA-II teacher N100/G300 versus exactly the
same EA plus KM initialization, using five independent future-pool18h batches
(batchseeds9010..9014, algorithmseeds10..14), with the same training-only driver
prior and candidate graph within each pair. No test output has been read for
method selection. Weighted KM is computed on each input as a common reference.
This confirms the isolated intervention at the teacher budget; larger-budget
combination remains an explicit quality/cost extension, not a secretly selected
winner. No coefficient, normalizer rule or initialization count is tuned on
those final inputs. Total primary/full EA runs remain115including5basic runs,
within the initial120cap; pilots/mathematical tests are separately identified.

## Combination, stopping, and frozen future confirmation

The one bounded combinationKM+N200/G300 reached meanHV1.112912(II) and1.112072(III),
only+0.001485/+0.000578over KM-only100/G300, while doubling EA evaluations and
raising SpacingCV. Both original parents and their removal comparison are
present, so this is not an unsupported multi-mechanism gain. Retain KM-only at
the teacher budget as the isolated confirmed intervention; preserve the larger
population as an explicit quality/cost extension. Further search stops because
there is no new specific mechanism hypothesis and the required questions have
been answered within115full EA runs including5basic, under the120cap.

The pre-frozen5future input batches9010..9014 then gave paired HV changes
+0.031674,+0.039447,+0.022647,+0.027849,+0.035735. Mean+0.031470, sampleSD0.006573.
All5were kept. This estimates the isolated intervention under the specified
proxy resampling model, not taxi-platform profit or a universal Pareto guarantee.

Independent research-data verification appended checks for all110advanced EA
runs,10KMbatches and125canonical records including5basic. The raw-CSV batch
provenance reconstruction matched9batches exactly, including training-only driver
priors for all5future batches. The original baseline receipt remains versioned.
