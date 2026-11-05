# RL canonical result index

39 registered run identities; 36 active day-metric tables. All dates/partitions and seeds retained separately.

Author: native reinforcement child. Author tests are not independent review; independent audit is stored under evidence/independent_ea_on_rl.

Primary data = teacher-local-clock Foursquare check-in proxy, conditional localkm/Manhattan teaching model. Accepted fare is dispatch-time proxy income; completed and outstanding counts are distinct.

Canonical machine index: ACTIVE_RUNS.json. Canonical numerical summary: SUMMARY.csv. Never rglob old experiment files into an aggregate.

|Run|Identity|Active|Day metrics|
|---|---|---|---|
|pilot|development|True|results/rl/pilot_v1/pilot_validation/day_metrics.json|
|baseline_f40|development|True|results/rl/development_v1/baseline_f40_s2024/day_metrics.json|
|baseline_f60|development|True|results/rl/development_v1/baseline_f60_s2024/day_metrics.json|
|baseline_f100|development|True|results/rl/development_v1/baseline_f100_s2024/day_metrics.json|
|beta_validation_v1|development|True|results/rl/beta_validation_v1/day_metrics.json|
|reposition_validation_v1|development|True|results/rl/reposition_validation_v1/day_metrics.json|
|reposition_cost_validation_v1|development|True|results/rl/reposition_cost_validation_v1/day_metrics.json|
|component_ablation_v1|development|True|results/rl/component_ablation_v1/day_metrics.json|
|sensitivity_gamma08|development|True|results/rl/sensitivity_v1/gamma08_validation/day_metrics.json|
|sensitivity_gamma095|development|True|results/rl/sensitivity_v1/gamma095_validation/day_metrics.json|
|sensitivity_grid6|development|True|results/rl/sensitivity_v1/grid6_validation/day_metrics.json|
|sensitivity_grid10|development|True|results/rl/sensitivity_v2_rngfix/grid10_validation/day_metrics.json|
|sensitivity_patience1|development|True|results/rl/sensitivity_v2_rngfix/patience1_validation/day_metrics.json|
|sensitivity_patience3|development|True|results/rl/sensitivity_v2_rngfix/patience3_validation/day_metrics.json|
|fair_q_b1_s2024|development|True|results/rl/double_v2_rngfix/q_b1_s2024_validation/day_metrics.json|
|old_q_b1_s2024|historical_equivalent|False|results/rl/double_validation_v1/q_b1_s2024_validation/day_metrics.json|
|fair_double_b1_s2024|development|True|results/rl/double_v2_rngfix/double_b1_s2024_validation/day_metrics.json|
|old_double_b1_s2024|invalid|False|results/rl/double_validation_v1/double_b1_s2024_validation/day_metrics.json|
|fair_q_b1_s2025|development|True|results/rl/double_v2_rngfix/q_b1_s2025_validation/day_metrics.json|
|old_q_b1_s2025|historical_equivalent|False|results/rl/double_validation_v1/q_b1_s2025_validation/day_metrics.json|
|fair_double_b1_s2025|development|True|results/rl/double_v2_rngfix/double_b1_s2025_validation/day_metrics.json|
|fair_q_b1_s2026|development|True|results/rl/double_v2_rngfix/q_b1_s2026_validation/day_metrics.json|
|fair_double_b1_s2026|development|True|results/rl/double_v2_rngfix/double_b1_s2026_validation/day_metrics.json|
|fair_q_b1_s2027|development|True|results/rl/double_v2_rngfix/q_b1_s2027_validation/day_metrics.json|
|fair_double_b1_s2027|development|True|results/rl/double_v2_rngfix/double_b1_s2027_validation/day_metrics.json|
|fair_q_b1_s2028|development|True|results/rl/double_v2_rngfix/q_b1_s2028_validation/day_metrics.json|
|fair_double_b1_s2028|development|True|results/rl/double_v2_rngfix/double_b1_s2028_validation/day_metrics.json|
|movement_trainseed_2024|development|True|results/rl/movement_trainseed_confirmation_v1/validation_s2024/day_metrics.json|
|movement_trainseed_2025|development|True|results/rl/movement_trainseed_confirmation_v1/validation_s2025/day_metrics.json|
|movement_trainseed_2026|development|True|results/rl/movement_trainseed_confirmation_v1/validation_s2026/day_metrics.json|
|movement_trainseed_2027|development|True|results/rl/movement_trainseed_confirmation_v1/validation_s2027/day_metrics.json|
|movement_trainseed_2028|development|True|results/rl/movement_trainseed_confirmation_v1/validation_s2028/day_metrics.json|
|offset_robustness|development|True|results/rl/offset_robustness_v1/validation/day_metrics.json|
|fusion_dynamic|development|True|results/rl/fusion_validation_v1/dynamic/day_metrics.json|
|final_fleet40|final|True|results/rl/final_v1/fleet40/day_metrics.json|
|final_fleet60|final|True|results/rl/final_v1/fleet60/day_metrics.json|
|final_fleet100|final|True|results/rl/final_v1/fleet100/day_metrics.json|
|final_enhancements|final|True|results/rl/final_v1/enhancements/day_metrics.json|
|final_secondary_montecarlo|final|True|results/rl/final_montecarlo_v1/day_metrics.json|

## Frozen held-out confirmation

Candidates were frozen in evidence/rl/FINAL_SELECTION.json before held-out outcomes were opened. Each row below averages five paired sampled simulated days; the dates are held out, the simulations are not five real operating days. Fare is accepted-at-dispatch proxy currency.

|Fleet/run|Policy|Fare mean|Response|Pickup km|Empty reposition km|
|---|---|---:|---:|---:|---:|
|final_fleet40|greedy|13333.15|0.52053|1.660|0.00|
|final_fleet40|km|12437.18|0.40693|1.901|0.00|
|final_fleet40|qkm|13994.90|0.51693|1.916|0.00|
|final_fleet60|greedy|17102.75|0.67493|1.530|0.00|
|final_fleet60|km|16757.42|0.60720|1.907|0.00|
|final_fleet60|qkm|17170.85|0.66027|1.928|0.00|
|final_fleet100|greedy|20716.17|0.81547|1.291|0.00|
|final_fleet100|km|20793.01|0.80800|1.912|0.00|
|final_fleet100|qkm|20046.49|0.77947|1.953|0.00|
|final_enhancements|double_beta1|14336.25|0.57280|1.945|0.00|
|final_enhancements|greedy|17102.75|0.67493|1.530|0.00|
|final_enhancements|km|16757.42|0.60720|1.907|0.00|
|final_enhancements|km_move3|17811.65|0.68613|1.929|826.55|
|final_enhancements|q_beta1|13995.18|0.60293|1.960|0.00|
|final_enhancements|qkm|17170.85|0.66027|1.928|0.00|
|final_enhancements|qkm_move3|17280.52|0.68173|1.931|685.44|
|final_enhancements|qkm_move5|17573.25|0.68747|1.942|278.01|
|final_enhancements|qnsga_constraint|16932.91|0.64933|1.360|0.00|
|final_enhancements|qnsga_knee|14750.38|0.53960|1.053|0.00|
|final_secondary_montecarlo|km|16957.28|0.60637|1.912|0.00|
|final_secondary_montecarlo|km_move3|18070.72|0.68707|1.920|848.08|
|final_secondary_montecarlo|qkm|17635.27|0.67147|1.919|0.00|
|final_secondary_montecarlo|qkm_move5|18017.47|0.69270|1.935|273.51|

No retuning follows these held-out observations. The selected gross-revenue candidate may lose on other metrics; see empty distance, response, and pickup separately. Hypothetical diagnostic net revenue is not measured real profitability.

## Double Q development replication

Five distinct training seeds, each evaluated on five common validation simulations. Independent behavior/update random streams; old shared-stream Double results excluded.

|Learner at beta1|Mean across training-seed day means|Response|Nonpositive feasible-edge fraction|
|---|---:|---:|---:|
|q|14173.08|0.57176|0.35556|
|double|14771.95|0.53797|0.44964|

Double improves beta1 revenue here but lowers response. DescriptiveV minus realized-policy-return gap averages42.00 forQ vs2.89 forDouble; policies and visited states differ, so this is not an unbiased optimal-value error estimate.

## Independent verification

Native independent context `/root/evolution` verified the listed375rawtrace simulations with its own event reconstruction, fullLT/Double hand calculations, actual weightedpolicy and NSGA selection/objectives, and primary/secondarypaired statistics. Reports bind actual source/model/trace hashes; the status is limited to their stated scope.
- [evidence/independent_ea_on_rl/result.json](../../evidence/independent_ea_on_rl/result.json): PASS_IN_STATED_SCOPE
- [evidence/independent_ea_on_rl/policy_result.json](../../evidence/independent_ea_on_rl/policy_result.json): PASS_IN_STATED_SCOPE

Interpretation and all teacher thought-question answers: `../../evidence/rl/TEACHER_QUESTIONS_AND_LIMITS.md`; result-triggered decisions: `../../evidence/rl/DECISIONS.md`.

The final confirmation section is added only when final_v1 actually exists. Original Q-only results retain their execution hash; exact Q/V/N/NV/curve/TD/episode-array parity under the Double-only RNG fix is recorded in evidence/rl/history_rngfix/parity.json. Old shared-RNG Double outputs are explicitly invalid for the fair comparison.
