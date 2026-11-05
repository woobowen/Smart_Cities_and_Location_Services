# E-B-001 RL / figures / independent-online-review handoff

Status: current RL implementation, all teacher PartB tasks+bonuses, development/control/parent/ablation experiments, frozen held-out confirmation, scientific figures and stated-scope independent checks are executed. Parent Goal remains responsible for report integration, whole-project review and authorized publication; this is a subtask handoff, not overall task acceptance.

## Canonical entries

- `task2/results/rl/ACTIVE_RUNS.json`:39registeredidentities/36active metric tables; explicit oldDouble invalid status; parentmodel/source/metricsSHA256. Neverrglob oldruns into conclusions.
- `task2/results/rl/SUMMARY.csv` / `SUMMARY.md`: all active run-policy means/sampleSD and separate final identities. Finalprimaryfivepairedsimulations distinct fromsecondarytwentyfreshresamplingseeds.
- `task2/results/rl/{final_v1,final_montecarlo_v1}/paired_differences.json`: reproducible paired differences/conditionalt intervals; not real operatingday populationCI.
- `task2/results/rl/COST_SCENARIOS.csv/.json`: separately charged reposition and totalempty(pickup+reposition) cost diagnostics; no trueprofit claim.
- `task2/evidence/rl/METHOD_SPEC.md`, `FINAL_SELECTION.json`, `DECISIONS.md`, `TEACHER_QUESTIONS_AND_LIMITS.md`, `notebook_integration.json`: mathematical/data/selection/teacherthoughtquestion/Notebook integration contracts.

## Main actual held-out observations

Primary n5: fleet40 QKM13994.90 vsKM12437.18; fleet60 QKM17170.85 vsKM16757.42; fleet100 QKM20046.49 <KM20793.01. Response andpickup are separate, shown inrawtables/figures.

Full70trained60fleet candidates: selectedgross-fareKM+lambda3movement17811.65 /response.68613 /pickup1.929km /extraempty826.55km; QKM17170.85/.66027/1.928/0. Primarygrossdifference640.81,descriptivet95[-64.07,1345.68]. Secondary20freshseeds, samefixedmodel: grossdifference435.45,[141.68,729.23]; extra848.08km. At hypotheticalrepositioncost1/km the secondary difference is **−412.62,[−717.03,−108.22]**. Gross-fare improvement is not net improvement; no post-test parameter or winner switch occurred.

Double atbeta1: primary14336.25 vsQ13995.18, butresponse.5728 vs.60293. Development5trainingseeds show same tradeoff and a lower descriptiveV/realized-policyreturngap; not a generaloptimal-value guarantee. NSGAconstraint16932.91/response.64933/pickup1.360 vsQ17170.85/.66027/1.928; lowerpickup trades service/fare. Knee more severe negative tradeoff retained.

## Verification and repair

- Author12meaningfultests passed; teacherCells31/33assertions preserved exactly in meaningful tests. Shared environment repairs done byparent; RLchild installedzero packages.
- Fixed Doubleupdate/behaviorRNG mixing with stoppedownprocesses, immutableoldsource, oldinvalidDouble status, validQ-only exactarrayparity and affectedreruns. No hot-source modification.
- Independent `/root/evolution` reports `evidence/independent_ea_on_rl/{result,policy_result}.json`:375rawtraces, independentdriver/order/event/distance/accounting reconstruction; handQ/Double/fullLT; actual108stepweightedpolicy;1064validation+1060finaldynamicNSGAframes;125staticfrontsolutions and2040partialmatching exactenumeration; pairedstatistics. Scope/hashbound, not authorselfPASS.
- This RLchild separately independently verified parent'sonline code/results: `evidence/independent_rl_on_online/{verify_online.py,result.json,execution.log}`;200exactsmallmatrices,55sourceinstances/1045runs/35190assignments, LPsum/customaugmentingbottleneck reference.
- Frontdayidentity metadata gap fixed by lossless `front_episode_mapping.json` appended tooriginalfronts; independentEA verified allmappedframes; oldFunchanged.

## Figures and privacy fix

`task2/scripts/build_rl_figures.py --final` produces10formalRLfigures andtwoactualvaluecandidates, vectorPDF/SVG+300dpiPNG, allsource/model/metric/P2hashes. Fullsizeauthor views anddimension/nonblankchecks recorded. IndependentRfoundinitialorigin-pointmapSVG exposedrowcoordinates; currentformal/candidate maps rebuilt to8×8aggregates only, same seed0sampledn3000, verified64cellcountsum3000. Orangecirclearea encodescounts atfixedteachingcenters. `figures/data/rl_value_origin_counts.csv` plus`evidence/rl/value_map_aggregation_check.json`. Do not use oldblackdotcaption. SourceV/metrics unchanged.

Independent visual/report-page/publication acceptance belongs toparent andotherreviewers. Primaryfixed5dayuncertaintyandadversecase remain visible in `rl_final_tradeoffs`.

## Rebuild / reproduction

From repository root, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python task2/scripts/run_rl.py --phase baseline --run recompute_baseline_01 --data task2/results/data --episodes 300`; choose a fresh run name for a new experiment. Staged commands are recorded in actual logs. `run_rl_final.py` checks the fixed contract and refuses a different existing model identity; it uses the fixed `final_v1` output path, so full reproduction must run in an isolated clean source package to preserve accepted artifacts and independent audit hashes.

Postprocessors: `index_rl_results.py`, `summarize_rl_costs.py`, `summarize_rl_pairs.py`, `map_rl_fusion_fronts.py`, then `build_rl_figures.py --final`. Rawsource andindividualtraces remain subject topendingredistributionpermission boundaries; publicfigures contain aggregates.
