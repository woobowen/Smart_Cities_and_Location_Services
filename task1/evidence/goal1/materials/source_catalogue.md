# Starter source catalogue
All listed text was read in full by this extractor and hashed. Python was parsed with ast.parse without importing or executing it.
The catalogue is reading coverage, not proof that every branch is correct. Focused source checks are recorded in findings.md.

## task1/作业/作业/ABLATION_REPORT.md
SHA256: b1e51e74b77d5be6ae588bd64f56c572825e69d49361d8093da3455831510ae9; lines: 112.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/DECISIONS.md
SHA256: 3a797e79dc31d1251c23651607bf9d641dc9229453f8fb6c96f119d76feffd8e; lines: 170.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/README.md
SHA256: f54830f2e671bb59375d9dbd990ab9643789e29e521b2a03313fe180014b27f7; lines: 141.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/build_ppt/build_deck.mjs
SHA256: 9c0e5a93e684000d7245af12cbb94cdb68a6bfcf21d9199b0a73836c913d2217; lines: 529.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/build_ppt/inspect_deck.py
SHA256: 5803c5d2ea477f55e01468b01ad2679ab04a8c9c5c5502a7ce3dbe43b181df57; lines: 99.
Module summary: 程序化校验 pptx：解析内部 XML，检查几何越界、字号、图片与文本完整性。
px:L18, main:L22

## task1/作业/作业/build_ppt/make_charts.py
SHA256: 8397e844682dca3d6c07e0f65f3deb206ffc47c39dd218f96a083cf9ff46cc8b; lines: 118.
Module summary: 生成讲义配图。全部基于真实数据，不用示意图冒充真实结果。
save:L28

## task1/作业/作业/build_ppt_agent/build_deck.mjs
SHA256: c80fdf7ad115ef71c82f787dae86ab7ef6130d64d2720b16917b4e9ffaba752a; lines: 414.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/build_ppt_agent/build_native.mjs
SHA256: 3fb622ffdca2970354219f55183f98502c198d37efa27e9b6057b12921c97737; lines: 532.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/build_ppt_agent/make_diagrams.py
SHA256: b3be6b07ae93b46daa7d752856c41efc2dcea421fc7665a68e4e4d85e9883482; lines: 206.
Module summary: 为「LLM 辅助轨迹清洗评估智能体」框架生成配图。
box:L25, arrow:L33, blank:L39, save:L45

## task1/作业/作业/demo_out/ablation.json
SHA256: b75ab34fdcee11700879e292dadff1f71f0d364086612c791d8612af7390cfe6; lines: 117.
JSON keys: rows, demo_vehicles, holdout_vehicles, memory_stats, baseline_accuracy, caveats, n_cases

## task1/作业/作业/demo_out/ecnu_token_report.md
SHA256: 31658da03a33b30a82057eebb6cab45ddcad47cd228283563922c6c8e83d3c67; lines: 51.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/demo_out/summary.json
SHA256: 6b6a4273d9fcc64728f461743b4a99faf79764905bbd39df30306d0094c43b7b; lines: 474.
JSON keys: dataset, single_case, figures, knee, curve, anomaly_histogram, ablation, ablation_cases, memory, regions, elapsed_s

## task1/作业/作业/douglas_peucker.py
SHA256: 8a35429b9007012e8e2c2b62560968e49dc75749ba22ac73025a8feeb4e6a4cb; lines: 70.
point2LineDistance:L10, __init__:L22, diluting:L28, reduction:L57

## task1/作业/作业/examples/run_demo.py
SHA256: 19c4708d0184571e1ff0167d2cdaa576d0a52ba50c9757581f0b07ef7442fecd; lines: 213.
Module summary: 端到端演示：一次跑出全部报告产物。
section:L48, main:L54

## task1/作业/作业/pytest.ini
SHA256: 666d06c66366dae7657aa05b10b303cb21ee49e6978c218f0848120ebdffae1b; lines: 4.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/tests/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/tests/conftest.py
SHA256: 5d918913f73b843330e9846db7a4d2c5275117f849d5d68f2663a2d41abd78b3; lines: 134.
Module summary: 共享测试夹具：手造小轨迹（已知答案）+ 真实数据抽样。
pt:L33, straight_traj:L39, dup_traj:L47, jump_traj:L55, illegal_traj:L63, timegap_traj:L77, nonmonotonic_traj:L85, u_turn_traj:L93, stationary_traj:L102, speed_spike_traj:L111, real_raw:L120, real_ids:L129

## task1/作业/作业/tests/test_agent.py
SHA256: 38c1b47ecda23e5534ddfb7bf134a1dda6ec36cd6d3350bff83fbd58ff1ee285; lines: 440.
Module summary: 智能体层：循环、预算、provider 回退、结构化输出解析、消融模式。
test_build_provider_defaults_to_mock_without_key:L16, test_build_provider_honours_explicit_name:L24, test_provider_status_does_not_leak_key:L29, test_openai_provider_reports_unavailable_without_key:L36, test_openai_provider_parses_tool_calls_from_fake_client:L42, test_openai_provider_wraps_client_errors:L89, test_mock_advances_one_step_per_chat:L103, test_mock_skips_split_when_timeline_unusable:L125, test_mock_proposal_is_structurally_valid:L143, test_proposal_from_code_block:L159, test_proposal_from_bare_json_with_prose:L165, test_proposal_from_final_wrapper:L170, test_proposal_returns_none_without_params:L175, test_proposal_handles_nested_braces_in_strings:L180, test_parse_text_action_variants:L186, test_system_message_contains_key_sections:L196, test_system_message_never_contains_coordinates:L206, agent:L218, test_agent_runs_full_loop:L227, test_agent_trace_records_every_phase:L238, test_agent_writes_memory_even_when_rejected:L248, test_agent_admits_stationary_by_constraint:L256, test_agent_result_is_json_serializable:L263, test_agent_unknown_vehicle_fails_gracefully:L268, test_agent_respects_tool_budget:L274, test_agent_handles_provider_failure:L286, test_agent_without_memory_still_runs:L302, test_agent_without_search_uses_baseline:L311, test_agent_measures_against_cleaned_reference:L321, test_tool_call_accounting_distinguishes_budget_from_total:L328, test_agent_run_many_creates_run_record:L341, test_memory_accumulates_and_is_retrievable:L351, test_ablation_modes_are_structurally_distinct:L371, test_search_disabled_marks_caveat:L420, test_prior_only_proposal_does_not_use_llm:L432, create:L69, chat:L288, create:L94

## task1/作业/作业/tests/test_anomalies.py
SHA256: 5c9139ffd6d1fbf74115606189ae1880b8ad1ee4cd624b269b72651a862c5af5; lines: 286.
Module summary: 异常检测：每条规则都用手造轨迹断言到精确点索引。
pt:L15, test_illegal_coords_exact_indices:L21, test_illegal_coords_accepts_custom_bbox:L25, test_duplicate_points_exact_indices:L33, test_duplicate_runs_span_exact:L38, test_nonconsecutive_revisit_is_not_duplicate:L42, test_duplicate_detection_on_stationary_real_data:L50, test_nonpositive_dt_exact_indices:L58, test_time_gaps_exact_index:L64, test_space_jumps_exact_indices:L69, test_space_jump_skips_illegal_coords:L73, test_speed_spike_detected_on_isolated_outlier:L78, test_clean_straight_trajectory_has_no_speed_anomaly:L85, test_sustained_over_limit_is_not_spike:L93, test_dt_artifact_distinguishes_from_coord_glitch:L103, test_u_turn_detected_on_real_fold_back:L114, test_turn_angle_noise_floor_blocks_jitter_false_positive:L120, test_stationary_trajectory_has_no_turn_or_u_turn:L135, test_drift_curvature_criterion_separates_spike_from_road_curvature:L142, test_drift_criterion_is_scale_free_with_respect_to_speed:L170, test_drift_detects_genuine_outlier_spike:L193, test_drift_regression_on_real_trajectory_306:L207, test_drift_skips_stationary_trajectory:L222, test_detect_anomalies_flags_align_with_reasons:L228, test_detect_anomalies_no_duplicate_reason_per_point:L236, test_anomaly_counts_and_histogram:L242, test_all_reasons_are_documented:L250, test_rule_params_from_params_maps_dist_threshold:L256, test_to_dict_is_json_safe:L262, test_real_data_regimes:L272, test_real_data_fast_driving_no_drift_false_positive:L278, build:L178

## task1/作业/作业/tests/test_architecture.py
SHA256: 6700ab805bae24a626c6aed7e22890b155b6b74ef7391d2ed5833631357207e1; lines: 89.
Module summary: 架构护栏：核心算法层不得依赖 LLM / 网络 / 智能体。
_core_files:L29, _imports:L35, test_core_files_exist:L47, test_core_does_not_import_forbidden_modules:L52, test_core_does_not_import_agent_layer_transitively:L61, test_no_network_imports_anywhere_in_core_source:L74, test_layer_dependency_direction:L86

## task1/作业/作业/tests/test_clean.py
SHA256: 60dfd76b5ac811ed25377e069c739569626a727fe285394cf05a12845dd7a483; lines: 186.
Module summary: 去噪：动作精确性、原因字段完整性、以及「不清洗真实行为」的边界。
test_drop_duplicates_keeps_last_of_each_run:L11, test_drop_duplicates_on_stationary_real_data:L28, test_drop_illegal_removes_exact_points:L37, test_drop_nonpositive_dt:L45, test_fix_dt_artifact_does_not_delete_points:L52, test_median_smooth_pulls_in_isolated_spike:L69, test_median_smooth_leaves_untargeted_points_alone:L76, test_median_smooth_window_forced_odd_and_min_3:L82, test_denoise_records_reasons_for_every_dropped_point:L89, test_denoise_report_arithmetic_is_consistent:L108, test_denoise_preserves_behavior_declaration:L121, test_denoise_does_not_delete_genuine_u_turn:L129, test_denoise_is_idempotent_on_clean_trajectory:L136, test_denoise_empty_trajectory_does_not_crash:L143, test_denoise_single_point_does_not_crash:L151, test_clean_config_from_params:L157, test_custom_config_can_disable_actions:L165, test_report_merge:L171, test_reasons_field_length_always_matches_points:L180

## task1/作业/作业/tests/test_geo.py
SHA256: 22a9b086c7aee2ddb9cf20fbb5598a91c6bc2dde9488358d850fa69145b4a443; lines: 260.
Module summary: geo 模块的已知答案测试。
test_haversine_known_city_pair:L22, test_haversine_identical_points_is_zero:L28, test_haversine_symmetric:L32, test_haversine_one_degree_latitude:L37, test_local_projection_is_self_consistent_across_spans:L46, test_local_projection_matches_ellipsoidal_meridian_arc:L63, test_local_projection_is_not_web_mercator:L89, test_segment_distance_perpendicular_is_finite:L105, test_segment_distance_uses_segment_not_infinite_line:L112, test_segment_distance_on_segment_is_zero:L121, test_segment_distance_degenerate_segment:L126, test_illegal_lonlat_detects_null_island_and_nan:L135, test_illegal_lonlat_outside_china_bbox:L145, test_path_length_matches_local_distance_sum:L153, test_path_length_single_point_is_zero:L159, test_bearing_cardinal_directions:L163, test_angle_diff_wraps_around_360:L178, test_turn_angles_u_turn_detected:L185, test_turn_angles_length_matches_points:L192, test_sinuosity_straight_line:L197, test_sinuosity_go_and_return_returns_one_by_contract:L202, test_sinuosity_l_shaped_detour_exceeds_one:L212, test_sinuosity_single_point:L218, test_quantile_matches_known_values:L222, test_is_bimodal_on_realistic_dt_distribution:L231, test_is_bimodal_needs_enough_samples:L238, test_consecutive_differences_alignment:L242, test_bbox_of:L249, test_finite_or_none:L255

## task1/作业/作业/tests/test_memory.py
SHA256: 0f9e74431fb3fb66eb24a2c37c01e7149a49cfa65299a084d3d450017faff561; lines: 293.
Module summary: 记忆层：特征、检索、蒸馏、以及「只有核验器能写」的约束。
card_moving:L16, card_stationary:L22, store:L28, _seed:L34, test_feature_vector_length_and_range:L58, test_features_differ_between_regimes:L64, test_features_are_deterministic:L72, test_feature_dict_has_names:L76, test_similarity_identical_is_one:L81, test_similarity_handles_zero_vector:L87, test_dt_cv_proxy_monotone:L93, test_write_and_count:L105, test_rejected_cases_are_recorded_but_not_retrievable:L114, test_recent_lists_newest_first:L122, test_retrieve_returns_most_similar_first:L130, test_retrieve_excludes_self_by_default:L143, test_retrieve_is_regime_gated:L154, test_retrieve_skips_mismatched_feature_length:L167, test_rebuild_procedural_only_uses_admitted:L179, test_rebuild_procedural_needs_min_samples:L189, test_procedural_uses_iqr_not_minmax:L194, test_procedural_upsert_is_idempotent:L207, test_prior_cold_start:L217, test_prior_with_no_store:L223, test_prior_available_after_seeding:L229, test_prior_caution_on_low_similarity:L239, test_explain_neighbors_is_serializable:L248, test_region_hint_text_empty:L256, test_region_hint_text_renders:L261, test_run_bookkeeping:L270, test_persistence_roundtrip:L281

## task1/作业/作业/tests/test_metrics.py
SHA256: 16813846c77dab4bd06923080fbe7bf5d1f198c7a57556c3bd06aa7127b8a858; lines: 208.
Module summary: 指标：已知答案的距离值、退化输入、以及对比表输出。
test_identical_trajectories_have_zero_distance:L12, test_hausdorff_known_value:L18, test_hausdorff_is_symmetric:L31, test_hausdorff_directed_can_differ:L37, test_frechet_detects_ordering_difference:L46, test_frechet_upper_bounds_hausdorff_for_same_ordering:L55, test_dtw_zero_for_identical_and_positive_for_shifted:L61, test_empty_inputs_return_zero:L68, test_subsample_keeps_endpoints:L76, test_long_trajectory_does_not_explode:L85, test_compute_metrics_basic_fields:L93, test_compute_metrics_with_reference:L103, test_compute_metrics_can_skip_distances:L111, test_compute_metrics_records_runtime:L116, test_metrics_to_dict_is_json_safe:L121, test_comparison_table_accumulates_rows:L126, test_comparison_table_empty_format:L136, test_comparison_table_renders_none_as_dash:L140, test_hausdorff_matches_dp_deviation_bound:L149, test_frechet_exceeds_hausdorff_for_sparse_simplification:L172, test_point_to_polyline_known_value:L195, test_point_to_polyline_degenerate_inputs:L202

## task1/作业/作业/tests/test_report.py
SHA256: cbd40b8954d9c98bcd33209013d17cfd9acfaf3d95c019f02fd48f77fa7c0c74; lines: 281.
Module summary: 出图与导出：文件产出、被删点判据、以及内容可校验性。
tmp_fig:L19, prepared:L24, test_dropped_points_matches_clean_report:L33, test_dropped_points_handles_duplicate_coordinates:L48, test_dropped_points_empty_when_nothing_removed:L59, test_cjk_font_available_or_warned:L65, test_cjk_glyphs_actually_exist:L73, _assert_png:L94, test_clean_overlay_renders:L102, test_clean_overlay_without_reference:L109, test_anomaly_scatter_renders:L116, test_anomaly_scatter_on_clean_trajectory:L122, test_heatmap_renders:L130, test_quality_compression_curve_renders:L137, test_sensitivity_heatmap_renders:L149, test_sensitivity_heatmap_rejects_empty:L157, test_ablation_chart_renders:L162, test_render_dispatch:L169, test_render_rejects_unknown_kind:L176, test_plot_contains_all_points:L183, test_export_preview_has_review_checklist:L197, test_export_writes_only_to_inbox:L219, test_export_refuses_to_overwrite_by_default:L242, test_export_skips_when_vault_missing:L265

## task1/作业/作业/tests/test_segment.py
SHA256: d5586d9473aa1f4fb210c7bd0fee89e9cc58571c99dbc979a88054a2bcf06039; lines: 195.
Module summary: 轨迹分段：已知答案测试。
test_no_cut_on_clean_straight_trajectory:L10, test_time_gap_cuts_at_exact_index:L18, test_space_jump_cuts_at_exact_index:L29, test_both_triggers_recorded_on_same_cut:L48, test_nonpositive_dt_cuts:L63, test_min_points_moves_short_seg_to_dropped:L70, test_min_length_moves_short_seg_to_dropped:L81, test_illegal_coords_do_not_trigger_space_jump:L94, test_thresholds_zero_cut_everywhere:L118, test_huge_thresholds_never_cut:L124, test_segment_index_assigned_sequentially:L131, test_segment_points_partition_original:L137, test_negative_threshold_raises:L145, test_tiny_trajectory_does_not_crash:L150, test_trigger_counts_aggregate:L168, test_sweep_returns_full_grid:L175, test_real_data_stationary_trajectory_is_all_dropped:L181, test_real_data_moving_trajectory_is_kept:L190

## task1/作业/作业/tests/test_simplify.py
SHA256: 72312c110a256927a3396cf50f5c4fd109c387eb1517743855bc228ec018f36d; lines: 140.
Module summary: DP 简化：正确性、误差界、以及与原始有 bug 实现的对照。
test_straight_line_collapses_to_endpoints:L12, test_endpoints_always_kept:L18, test_indices_are_strictly_increasing_and_unique:L26, test_deviation_never_exceeds_tolerance:L32, test_reported_deviation_matches_independent_global_search:L49, test_zero_tolerance_keeps_everything:L59, test_two_point_trajectory_unchanged:L64, test_vertical_segment_bug_regression:L71, test_distance_metric_differs_from_infinite_line:L81, test_perp_algorithm_runs_and_is_sane:L103, test_unknown_algorithm_raises:L109, test_all_registered_algorithms_are_callable:L114, test_uniform_sample_indices_respects_ratio:L120, test_compression_monotone_in_tolerance:L126, test_sweep_returns_one_result_per_tolerance:L135

## task1/作业/作业/tests/test_tools.py
SHA256: 06fd2bffe48b19154bde5f2b3a45c8035a214258b1f326989e7bc42da8e5c279; lines: 293.
Module summary: 工具层：schema 完整性、坐标不外泄、副作用标注、参数越界处理。
registry:L15, test_every_tool_has_openai_schema:L22, test_tool_schemas_are_json_serializable:L32, test_expected_tools_present:L36, test_no_memory_write_tool_exists:L46, test_unknown_tool_returns_error_not_raises:L54, test_responses_never_contain_raw_coordinates:L61, test_diagnosis_card_has_no_coordinates:L77, test_full_chain_produces_handles:L86, test_lineage_recorded:L103, test_unknown_handle_returns_error:L113, test_simplify_clamps_out_of_range_tolerance:L119, test_call_json_parses_arguments:L127, test_call_json_handles_bad_json:L134, test_call_log_records_elapsed:L139, test_find_knee_returns_param_value:L146, test_find_knee_rejects_bad_json:L161, test_find_knee_rejects_empty_array:L166, test_road_constraint_produces_handle:L172, test_road_constraint_rejects_degenerate_road:L180, test_roads_from_trajectory_refuses_short_polyline:L197, test_road_match_rate_on_real_trajectory_is_meaningful:L204, test_compare_handles_includes_metric_caveat:L219, test_hausdorff_matches_dp_bound_via_tools:L228, test_playbook_loads_stub_notes:L241, test_playbook_frontmatter_dates_are_json_safe:L247, test_playbook_is_read_only:L255, test_playbook_missing_vault_returns_empty:L260, test_playbook_parses_wikilinks:L266, test_playbook_digest_filters_by_param:L272, test_state_hash_differs_for_different_content:L278, test_store_never_overwrites_handle:L286

## task1/作业/作业/tests/test_verifier.py
SHA256: 50c83c96869f16effc647f40404c2d718855af79427e212ad37e51eae6711f3e; lines: 310.
Module summary: 核验器：regret 口径、knee point、约束与准入闸门。
test_regret_normalized:L12, test_regret_zero_when_matching_best:L18, test_regret_capped_at_one:L23, test_regret_small_headroom_falls_back_to_absolute:L28, test_regret_not_applicable_returns_zero:L39, test_regret_unnormalized:L46, test_objective_compression_and_fidelity_bounds:L53, test_objective_flags_length_loss_as_infeasible:L62, test_objective_flags_deviation_beyond_tolerance:L70, test_short_trajectory_is_not_applicable:L78, test_applicable_flag_survives_to_dict:L92, test_knee_point_on_synthetic_curve:L102, test_knee_point_edge_cases:L109, test_knee_point_handles_unsorted_input:L115, test_pareto_front_excludes_dominated:L121, _mk_result:L132, test_grid_search_covers_all_combinations:L140, test_coordinate_descent_improves_over_start:L147, test_search_records_baseline_fields:L157, test_linspace_integer_dedupes:L165, test_search_stays_within_param_bounds:L170, test_search_clamps_and_records_violations:L181, test_direction_check_agreement:L189, test_direction_check_disagreement:L198, test_direction_accuracy_none_when_no_valid_checks:L204, test_direction_ignores_keys_not_in_both_dicts:L210, test_admission_gate_rejects_high_regret:L217, test_admission_gate_accepts_good_proposal:L229, test_admission_gate_accepts_inapplicable_by_constraint_only:L241, test_admission_gate_rejects_out_of_range_params:L254, test_regret_uses_trace_baseline_not_proposal_baseline:L266, test_ablation_summary_groups_by_mode:L283, test_evals_to_reach:L297, _obj:L303, ev:L148

## task1/作业/作业/traj_agent/__init__.py
SHA256: c92ed39010e62ccbae521e39e63f672e84bf05546b316ea4c147f3e1a021e3b9; lines: 23.
Module summary: traj_agent：LLM 辅助的轨迹清洗评估工作流。
(No functions.)

## task1/作业/作业/traj_agent/agent/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/traj_agent/agent/loop.py
SHA256: 9fcc26e5dc8f938ec07859abdd5e1ce5c1868ea171e9914c31b630df06d630b4; lines: 632.
Module summary: ReAct 主循环：诊断 → 检索 → 提议 → 执行 → 核验 → 记忆。
to_dict:L71, to_dict:L120, __init__:L156, attach_dataset:L201, run:L206, _elicit_proposal:L309, _prior_only_proposal:L434, _execute:L464, _objective_of:L488, _evaluate_and_verify:L501, _run_search:L581, _step:L618, run_many:L623, evaluator:L586

## task1/作业/作业/traj_agent/agent/prompts.py
SHA256: 14be6648e2e438b549727319efefff5b8cca20e72bd9d60b88287e39633a0644; lines: 233.
Module summary: 提示词：把诊断卡、物理先验、人类知识、记忆先验组织成 LLM 的输入。
diagnosis_block:L49, param_bounds_block:L57, playbook_block:L68, memory_block:L84, tool_catalog_block:L113, build_system_message:L126, proposal_from_text:L148, _balanced_objects:L188, parse_text_action:L218

## task1/作业/作业/traj_agent/agent/provider.py
SHA256: 9348a12346b3527ca70dc6eb5b1d510723dfe117501791fb5373f110d7bffc21; lines: 428.
Module summary: LLM provider：OpenAI 兼容接口 + 离线 Mock。
_obs_text:L354, _last_handle:L361, _extract_curve:L374, _extract_knee:L388, build_provider:L402, provider_status:L419, to_dict:L31, has_tool_calls:L48, to_dict:L51, __init__:L75, available:L102, _get_client:L105, chat:L123, describe:L178, __init__:L207, available:L215, chat:L218, observe:L244, _next_actions:L248, seed:L286, _call:L292, _propose:L299, describe:L349

## task1/作业/作业/traj_agent/core/__init__.py
SHA256: ff9ac5d27efda4216924c2a68f93e9f6fcf6af07a46d97ee251082d2901d4446; lines: 14.
Module summary: core：纯确定性算法层。
(No functions.)

## task1/作业/作业/traj_agent/core/anomalies.py
SHA256: 24a597e848463275bdd44249f87b6cc82f9f1bfeb90141b205caa5a390a4888e; lines: 547.
Module summary: 异常点规则：速度突变、非法坐标、连续重复点、明显漂移。
mark_illegal_coords:L131, mark_duplicate_points:L136, mark_duplicate_runs:L150, mark_nonpositive_dt:L166, mark_time_gaps:L176, mark_space_jumps:L182, _displacement_outlier:L194, mark_position_outliers:L208, mark_speed_anomalies:L244, mark_dt_artifacts:L305, mark_turn_anomalies:L338, mark_drift:L359, mark_drift_sequence:L413, mark_stationary_drift:L434, detect_u_turns:L464, detect_anomalies:L486, anomaly_histogram:L541, from_params:L81, n_points:L102, counts:L105, point_reason_map:L108, to_dict:L115, add:L493

## task1/作业/作业/traj_agent/core/clean.py
SHA256: 89030cc9a656a5dcddd2b97f41f45022f1821c770d1cf6fa9014cb2f305413ad; lines: 413.
Module summary: 去噪：把异常点规则的结果转成实际动作，并保留原因字段。
_point_keys:L110, _diff_dropped:L116, _select:L137, drop_consecutive_duplicates:L145, drop_illegal_coords:L170, drop_nonpositive_dt:L180, drop_jump_artifacts:L195, fix_dt_artifacts:L215, median_smooth:L251, denoise_trajectory:L297, from_params:L55, drop_ratio:L79, to_dict:L84, merge:L97, record_dropped:L313, apply_drop:L333

## task1/作业/作业/traj_agent/core/diagnosis.py
SHA256: 6dbcec6648c6a215a67e0ae49e7a840a13f4ab407bdc07f2a01472755e48168e; lines: 304.
Module summary: 诊断卡：喂给 LLM 的唯一数据视图。
classify_timeline:L122, classify_regime:L146, diagnose:L165, _observations:L230, diagnose_many:L288, dataset_regime_summary:L293, to_dict:L75, to_json:L117

## task1/作业/作业/traj_agent/core/geo.py
SHA256: 9ff0049b1d7ea2c73c5525ad93b5587f99638c9cf427ac6c4190d76c3ebaf792; lines: 306.
Module summary: 几何与坐标工具。
haversine_m:L34, lonlat_to_mercator:L52, mercator_to_lonlat:L61, _m_per_deg:L84, local_xy:L98, project:L103, equirect_relative_error:L108, unproject:L123, euclid:L128, is_legal_lonlat:L133, segment_distance_m:L151, local_distance_m:L173, path_length_m:L178, bearing_deg:L185, angle_diff_deg:L195, turn_angles_deg:L201, bbox_of:L217, sinuosity:L226, quantile:L241, median:L258, is_bimodal:L262, consecutive_differences:L287, finite_or_none:L298

## task1/作业/作业/traj_agent/core/metrics.py
SHA256: 2231a445f396e590f4e0582a0c4f4fdfb4f9e8cbafc032ed79c95f4048692b7e; lines: 255.
Module summary: 评价指标：点数、轨迹长度、Hausdorff / Fréchet / DTW 距离、运行时间。
_xy:L35, point_to_polyline_m:L41, hausdorff_m:L51, frechet_m:L76, _subsample:L107, dtw_m:L114, compute_metrics:L177, _fmt:L250, to_dict:L158, add:L225, to_dict:L232, format_text:L235

## task1/作业/作业/traj_agent/core/params.py
SHA256: 3e8ebef30e147ac24e45046a720e6f764a8e34d9043c6a3d33ff2da2ff81e055; lines: 252.
Module summary: 参数空间：物理先验、合法区间、默认值。
get_spec:L129, default_params:L135, clamp_params:L139, validate_params:L162, param_bounds_table:L177, data_driven_priors:L182, jump_lower_bound:L245, physical_jump_threshold:L250, clamp:L32, in_range:L36, to_dict:L43

## task1/作业/作业/traj_agent/core/segment.py
SHA256: ca572f244da17123a519c985476c45e6f7456b1c08361832e254fbc10a982de4; lines: 150.
Module summary: 轨迹分段：按车辆 ID、时间间隔、空间跳跃阈值切分。
split_trajectory:L58, split_all:L117, sweep_split_thresholds:L130, n_segments:L31, n_points_kept:L35, trigger_counts:L38, summary:L45

## task1/作业/作业/traj_agent/core/simplify.py
SHA256: 25e0308896177535eeff32d36331e32009fca40e657337c5436657c26907879f; lines: 272.
Module summary: 轨迹简化：Douglas-Peucker。
douglas_peucker_indices:L30, douglas_peucker:L78, douglas_peucker_broken:L90, uniform_sample_indices:L136, perp_distance_indices:L152, simplify_trajectory:L212, max_deviation_m:L243, sweep_dp_tolerance:L265, broken_point_line_distance:L100, n_before:L189, compression_ratio:L195, to_dict:L200

## task1/作业/作业/traj_agent/core/traj.py
SHA256: 5e585bed1b33c52c090a2ec9e10bc7ace72a8c81d6856b0e6a39b36e844b3368; lines: 257.
Module summary: 轨迹数据模型与载入。
load_raw:L141, normalize_raw:L151, _as_pairs:L163, traj_from_raw:L201, iter_trajs:L206, dataset_stats:L216, _mode:L251, __post_init__:L31, __len__:L43, seg_id:L47, duration_s:L51, bbox:L57, length_m:L61, positions:L64, time_deltas:L75, space_deltas_m:L79, speeds_mps:L87, accelerations_mps2:L104, is_stationary:L118, to_points:L126, summary:L129

## task1/作业/作业/traj_agent/memory/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/traj_agent/memory/export.py
SHA256: a41743debd7ee862cd2bed63a67aefb3b73ed5f830b978fecd14f4e8fe276e33; lines: 152.
Module summary: 单向导出：SQLite（L1/L2）→ Obsidian markdown（L3 候选）。
_slug:L38, _frontmatter:L44, export_param_region_note:L57, export_note:L103, export_regions:L119, preview_export:L145, to_dict:L33

## task1/作业/作业/traj_agent/memory/features.py
SHA256: a195f3d24739de17aac6dba7af14c1e80928353ea97a98dd1f28b61e35f34f31; lines: 162.
Module summary: 诊断卡 → 归一化特征向量。
_safe_log1p:L57, dt_coefficient_of_variation:L67, featurize:L80, featurize_with_regime:L105, regime_of:L115, vector_to_dict:L119, feature_table:L123, cosine_similarity:L136, euclidean:L147, similarity:L153

## task1/作业/作业/traj_agent/memory/retrieve.py
SHA256: af37d9a7a594146dc7b6d432726b4310548b037743fc0ab221ad7b307d43dea6; lines: 130.
Module summary: 面向 LLM 的记忆检索：把 L1/L2 组织成可直接使用的先验。
prior_for:L43, explain_neighbors:L85, region_hint_text:L121, to_dict:L30

## task1/作业/作业/traj_agent/memory/store.py
SHA256: 17485179eea1f367844cd42f0e65ad6ffd17c2d64f14cbfffb97854fa80514f1; lines: 477.
Module summary: 记忆存储：SQLite 承载机器校准（L1 情景记忆 + L2 程序记忆）。
_load_json:L446, _collect_param_names:L458, _quantile:L467, to_dict:L96, to_dict:L127, __init__:L144, close:L157, write_case:L162, start_run:L204, finish_run:L211, count:L218, retrieve:L225, retrieve_similar:L288, all_features:L308, rebuild_procedural:L322, query_regions:L388, stats:L412, recent:L432

## task1/作业/作业/traj_agent/report/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/traj_agent/report/figures.py
SHA256: 04f8bf4cba2fe9d8069fc64a394b9f40e07a83137772dc2a972219ab3ffc84ae; lines: 441.
Module summary: 可视化：清洗前后叠加图、异常点分布图、热力图、曲线与消融表。
setup_style:L44, _ensure_style:L71, lab:L78, _has_cjk:L83, _out_path:L90, dropped_points:L95, _lonlat_arrays:L120, plot_clean_overlay:L131, plot_anomaly_scatter:L182, plot_heatmap:L234, plot_quality_compression:L276, plot_sensitivity_heatmap:L334, plot_ablation:L379, render:L429

## task1/作业/作业/traj_agent/road/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/traj_agent/road/matcher.py
SHA256: 580ce3ca7e500affa3e65e74b6311b4ab1dcb5faddd42ee041f3b3251fc04996; lines: 248.
Module summary: 路网匹配与道路约束接口。
roads_from_trajectory:L217, road_constraint_report:L241, n_points:L31, match_rate:L35, stats:L40, match:L56, snap:L59, distance_to_road_m:L62, match:L72, snap:L79, distance_to_road_m:L82, available:L86, distance_m:L99, project:L114, __init__:L154, available:L162, nearest:L165, match:L175, snap:L194, distance_to_road_m:L198, speed_limit_at:L202

## task1/作业/作业/traj_agent/tools/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/traj_agent/tools/playbook.py
SHA256: c5e838106549125891942d33caab7cb28fe3af81804326c2534a1d552d9f48fb; lines: 217.
Module summary: Obsidian vault 只读挂载：人类知识层（L3）。
_jsonify:L89, _parse_frontmatter:L107, resolve_vault_dir:L129, load_notes:L140, notes_for_params:L181, playbook_digest:L190, vault_status:L205, param:L61, scope:L66, note_type:L71, to_dict:L75

## task1/作业/作业/traj_agent/tools/registry.py
SHA256: e498e46f52f98bdf36393ec99cc898f48b7ace5ba3cc69ef3eb48a1de1fcc7b8; lines: 697.
Module summary: 工具注册表：core 的 JSON-Schema 封装，LLM 唯一能接触的层。
_obj:L51, _rule_params:L679, _replace:L684, attach_dataset:L689, attach_memory:L695, to_openai_schema:L40, log:L73, __init__:L87, names:L93, spec:L96, openai_tools:L101, catalog:L111, call:L122, call_json:L141, register:L156, _register_all:L159, _register_source:L170, _register_inspect:L207, _register_transform:L288, _register_evaluate:L435, _register_memory_read:L601, _register_render:L648, load_trajectory:L171, profile_trajectory:L208, detect_anomalies:L213, suggest_param_range:L236, split_trajectory:L289, clean_trajectory:L309, simplify_trajectory:L332, apply_road_constraint:L352, evaluate:L436, compare_handles:L448, run_search:L481, find_knee:L512, query_memory:L602, query_playbook:L618, render:L649

## task1/作业/作业/traj_agent/tools/store.py
SHA256: e211489bb4cfcc43c3774852d8bac210623ec446517c7dfd8481e994ef641792; lines: 165.
Module summary: 会话存储：轨迹句柄 → 实际数据。
state_hash:L153, n_points:L32, line:L35, __init__:L50, new_handle:L57, put:L62, _root_of:L89, get:L98, record:L102, try_get:L110, exists:L115, lineage:L119, handles:L134, n_handles:L138, stats:L142

## task1/作业/作业/traj_agent/verifier/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/traj_agent/verifier/ablation.py
SHA256: 8a13c5e36030078d3e7a943f6fb5e45e624074c66e3947d62eadb1efb040d5b4; lines: 150.
Module summary: 消融实验：先在示范集上积累记忆，再在**留出集**上评测。
run_ablation:L65, to_dict:L53

## task1/作业/作业/traj_agent/verifier/objective.py
SHA256: 90f079e29106494284fe25cdd59a32db6e4ba64141840b117e6cbe81cb6f6ee7; lines: 285.
Module summary: 目标函数与 knee point：把「清洗得好不好」变成一个可比较的标量。
compression_ratio:L84, fidelity_from_deviation:L90, compute_objective:L107, find_knee_point:L204, knee_from_results:L257, pareto_front:L267, to_dict:L61, to_dict:L193

## task1/作业/作业/traj_agent/verifier/search.py
SHA256: 5f7804eafd76db133d32fbafc4410a8878b43e8fcbcde6bba447e1e576f3ce1b; lines: 219.
Module summary: 有界确定性搜索：为 LLM 的提议提供 ground-truth 参照。
_clamp:L72, linspace:L76, grid_search:L89, coordinate_descent:L122, sweep_quality_compression:L205, record:L47, to_dict:L54, rec:L102

## task1/作业/作业/traj_agent/verifier/verify.py
SHA256: b1b3108f7299db9fa368dd19b1841f41c87c3ea9c2b1bd5700d646fc26d4db5e; lines: 352.
Module summary: 核验器：把 LLM 的建议变成一个可判分的数字。
_sign_word:L42, check_direction:L51, direction_accuracy:L73, compute_regret:L147, evals_to_reach:L177, verify_proposal:L192, ablation_summary:L289, _num:L347, to_dict:L33, to_dict:L118, mean:L310

## task1/作业/作业/utils/__init__.py
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; lines: 0.
(No functions.)

## task1/作业/作业/utils/util.py
SHA256: 8c935fff8947eb3329d5812764256d7bf9b44d41f2d06d074f38c3278a3bf3f3; lines: 329.
utm_to_wgs84:L8, _transform_lat:L20, _transform_lng:L28, out_of_china:L36, wgs84_to_gcj02:L46, gcj02_to_wgs84:L66, wgs84_to_mercator:L87, mercator_to_wgs84:L94, transform_points_wgs84_to_mercator:L101, transform_points_mercator_to_wgs84:L108, transform_points_wgs84_to_gcj02:L115, transform_points_gcj02_to_wgs84:L122, get_angle_to_north:L130, calculate_angle_diff:L141, get_cos_value:L149, detect_u_turn:L157, projection_direction:L163, eucl_distance:L180, haversine_distance:L184, judge_frechet:L195, frechet_distance:L220, get_by_index:L226, duplicate_removal:L232, filter_adjacent_redundant_index:L243, get_velocity:L253, get_direction:L266, get_distance_diff:L274, get_time_diff:L283, get_point_in_range:L291, get_b_spline:L299, geo_distance:L327

## task1/作业/作业/utils/visualization.py
SHA256: d7e6d9cda5d63aff723d75d83771a9fcf5019e89674d6f67b3b51ccb3ecdca4b; lines: 47.
geo_json_generate_traj_from_dict:L6, visual_raw_traj:L32

## task1/作业/作业/vault_stub/dp-tolerance.md
SHA256: 4853890e519f87c5d6e9cd7a6e038f7f24d5b3f335a88f061281ecbb92b50560; lines: 27.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/vault_stub/dt-threshold.md
SHA256: 879c8bdbdf78583985fabbc9b1a05fe2e99dd1a88e5d9d712fd6564aaba99dfa; lines: 25.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/vault_stub/regime-stationary.md
SHA256: abc5a52d95368e6933cad7fac217aa068b807e031e7098793bf3e2374c6a5122; lines: 29.
Text source read; claims are historical/source declarations until independently verified.

## task1/作业/作业/使用说明.md
SHA256: 9016a34adecd9d5e0db5c2ed5608a67569b1b8b5d1eb727c873c7ff4e7065f8e; lines: 374.
Text source read; claims are historical/source declarations until independently verified.
