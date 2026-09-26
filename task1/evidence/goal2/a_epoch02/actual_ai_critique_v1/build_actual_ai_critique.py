"""Link verified development model suggestions to actual synthetic risk tests.

Reads the immutable development registry and formal-02 counterexamples only.
No model, candidate pipeline, tuning or concurrently running holdout-mode input
is accessed. A model hypothesis with a tradeoff is not called an illegal action
or hallucination; synthetic risks are never invented quotations.
"""
from collections import Counter, defaultdict
from pathlib import Path
from time import perf_counter
import os

from task1.scripts.build_goal2_analysis import (
    EVIDENCE, Inputs, actual_ai_critique, compact_metrics, counterexample_analysis,
    mode_analysis, read_gzip, relative,
)
from task1.workflow.io import ROOT, digest, now, object_hash, read_json, write_json


def binding(path):
    return {"path": relative(path), "sha256": digest(path)}


def main():
    started, timer = now(), perf_counter()
    directory = Path(__file__).resolve().parent
    output = directory / "actual_ai_critique.json"
    if output.exists():
        raise ValueError("ACTUAL_AI_CRITIQUE_EXISTS_PRESERVE_ORIGINAL")
    snapshot_path = EVIDENCE / "a_epoch02_development_registry_snapshot.json"
    snapshot = read_json(snapshot_path)
    assert not any(key.startswith("evaluation_") or key == "mode_evaluation" for key in snapshot)
    assert snapshot["counterexamples"] == "task1/evidence/goal2/counterexamples/formal-02"
    inputs = Inputs(snapshot_path)
    analysis = ROOT / "task1/scripts/build_goal2_analysis.py"
    analysis_hash = digest(analysis)
    tables = defaultdict(list)
    records = mode_analysis(inputs, tables)
    actual = actual_ai_critique(tables)
    counterexample_summary = counterexample_analysis(inputs, tables)
    formal = ROOT / snapshot["counterexamples"]
    synthetic = read_json(formal / "synthetic_cases.json")
    by_id = {case["case_id"]: case for case in synthetic["cases"]}
    assert len(by_id) == 6 and synthetic["known_answer_check_count"] == 25
    assert all(check["passed"] for case in by_id.values() for check in case["known_answer_checks"])
    receipts = {}
    for filename in ("development_modes_epoch02_receipt.json", "counterexamples_epoch02_receipt.json"):
        path = EVIDENCE / "c_contract" / filename
        receipt = read_json(path)
        assert receipt["status"] == "VERIFIED" and not receipt["errors"]
        for target in receipt["targets"]:
            assert digest(ROOT / target["path"]) == target["sha256"]
        for source, sha256 in receipt.get("source_hashes", {}).items():
            assert digest(ROOT / source) == sha256
        receipts[filename] = {**binding(path), "checked_components": receipt["checked_components"],
            "unchecked_components": receipt["unchecked_components"], "status": receipt["status"]}
    raw_cases = [{"kind": "LEGAL_PROPOSAL_TRADEOFF", **row}
                 for row in tables["ai_legal_proposal_tradeoffs"]]
    raw_cases += [row for row in actual["examples"] if row["kind"] != "LEGAL_PROPOSAL_TRADEOFF"]
    assert len(tables["ai_legal_proposal_tradeoffs"]) == 4
    citations = []
    for ordinal, row in enumerate(raw_cases, 1):
        response = row["raw_response_sources"][0]
        response_path = ROOT / response["path"]
        assert digest(response_path) == response["sha256"]
        raw_response = read_json(response_path)
        assert any(action["record_id"] == row["record_id"] and
                   row["original_proposal"] in action["proposals"] for action in raw_response["records"])
        episode_dir = response_path.parents[2]
        episode_path = episode_dir / "episode.json"
        episode = read_json(episode_path)
        record = next(item for item in episode["records"] if item["record_id"] == row["record_id"])
        trace_path = episode_dir / (row["record_id"] + "_candidate_traces.json.gz")
        assert digest(trace_path) == episode["artifact_hashes"][trace_path.name]
        trace = read_gzip(trace_path)
        before = trace["results"][record["reference_config_id"]]
        after = trace["results"][row["executed_config_id"]]
        assert object_hash(before) == row["prediction_reference_trace_hash"]
        assert object_hash(after) == row["prediction_candidate_trace_hash"]
        for cid in (record["reference_config_id"], row["executed_config_id"]):
            assert trace["reviews"][cid]["status"] == "VERIFIED"
            assert trace["reviews"][cid]["target_hash"] == object_hash(trace["results"][cid])
        assert row["proposal_is_selected_output"] == (row["executed_config_id"] == record["selected_config_id"])
        if row["kind"] == "LEGAL_PROPOSAL_TRADEOFF":
            assert row["legal"] and row["executed"] and not row["proposal_is_selected_output"]
            adjudication = "Legal proposal executed successfully; common geometric protection degraded, so it was not selected. Retain it as an actual tradeoff, not an illegal action, hallucination or evidence of real misclassification."
            connection = {"case_id": "CE06_OWN_CLEAN_IS_NOT_COMMON_TRUTH",
                "link_type": "SAME_EVALUATION_RISK_DEMONSTRATED_ON_TWO_SEPARATE_INPUTS",
                "reason": "The actual candidate satisfies its own DP certificate while its common-reference geometric protection worsens. The synthetic example independently demonstrates why own-clean DP error cannot establish cross-method improvement.",
                "model_claimed_own_clean_proves_quality": False,
                "synthetic_truth_transferred_to_real_data": False}
        elif row["kind"] == "CORRECT_EVALUABLE_PREDICTION":
            adjudication = "The pre-execution direction prediction matches this measured metric difference. Correct sign is not a claim of real cleaning accuracy or proof that this proposal should be selected."
            connection = {"case_id": "CE01_DIRECTION_AMBIGUITY",
                "link_type": "LIMIT_ON_INTERPRETING_A_DESCRIPTIVE_DIRECTION_COUNT",
                "reason": "A correct change in the number of direction deletions does not say which real points are noise. The authored normal/spike fixtures supply truth only for their own constructed inputs.",
                "model_claimed_real_noise_accuracy": False, "synthetic_truth_transferred_to_real_data": False}
        else:
            adjudication = "The model did not commit an evaluable prediction here. Preserve not_predicted/null and its denominator; do not score it as either an incorrect or a correct prediction."
            connection = {"case_id": None, "link_type": "NO_SPECIFIC_SYNTHETIC_MATCH_ASSERTED",
                "reason": "Uncertainty in a model prediction is distinct from zero-time/empty-output numeric undefinedness; no artificial one-to-one equivalence is asserted."}
        citations.append({"citation_id": f"AI-DEV-{ordinal:02d}", "classification": "ACTUAL_LIVE_DEVELOPMENT_MODEL_PROPOSAL",
            "kind": row["kind"], "partition": row["partition"], "mode": row["mode"],
            "episode": row["episode"], "episode_id": row["episode_id"], "record_id": row["record_id"],
            "round": row["round"], "candidate_id": row["candidate_id"],
            "verbatim_model_reason": row["original_proposal"]["reason"],
            "original_proposal": row["original_proposal"], "raw_response": response,
            "episode_artifact": binding(episode_path), "candidate_trace_file": binding(trace_path),
            "pre_execution_prediction": {"metric_id": row["metric_id"], "predicted_sign": row["predicted_sign"],
                "reference_handle_locked_before_execution": row["reference_handle"]},
            "actual_metric_check": {key: row[key] for key in ("prediction_status", "prediction_evaluable",
                "prediction_matches", "observed_sign", "delta", "prediction_reference_trace_hash", "prediction_candidate_trace_hash")},
            "reference_config_id": record["reference_config_id"], "candidate_config_id": row["executed_config_id"],
            "reference_parameters": before["parameters"], "candidate_parameters": after["parameters"],
            "reference_metrics": compact_metrics(before["metrics"]), "candidate_metrics": compact_metrics(after["metrics"]),
            "registered_comparison": row.get("actual_execution_comparison"),
            "legal": row["legal"], "executed": row["executed"], "raw_proposal_clamped": False,
            "proposal_became_locked_output": row["proposal_is_selected_output"],
            "actual_locked_config_id": record["selected_config_id"], "fallback": record["fallback"],
            "A_adjudication": adjudication, "synthetic_connection": connection,
            "real_noise_truth_available": False, "human_approval_claimed": False})
    risks = []
    for case in synthetic["cases"]:
        executions = []
        for label, execution in case["executions"].items():
            result, review = execution["output"], execution["review"]
            assert review["status"] == "VERIFIED" and review["target_hash"] == object_hash(result)
            executions.append({"execution": label, "record_id": result["record_id"],
                "parameters": result["parameters"], "order": result["order"],
                "result_hash": object_hash(result), "review_status": review["status"],
                "metrics": compact_metrics(result["metrics"]),
                "synthetic_truth_counts": execution.get("synthetic_detection_counts"),
                "truth_scope": "Only this authored fixture; never real-data accuracy"})
        related = [item["citation_id"] for item in citations if item["synthetic_connection"]["case_id"] == case["case_id"]]
        risks.append({"case_id": case["case_id"], "classification": "SYNTHETIC_COUNTEREXAMPLE",
            "source": binding(formal / "synthetic_cases.json"), "case_object_hash": object_hash(case),
            "family": case["family"], "known_answer_checks": case["known_answer_checks"],
            "actual_executions": executions, "before_after": case["before_after"],
            "interpretation": case["interpretation"], "treatment": case["action"],
            "related_actual_citation_ids": related,
            "attributed_as_actual_model_error": False,
            "association_boundary": "Synthetic input is separate from the real proposal record. An association states a metric/interpretation risk; it is not a fabricated model quote or evidence that the model made the risky claim."})
    result = {"goal_id": inputs.contract["goal_id"], "classification": "ACTUAL_AI_CITATIONS_AND_SYNTHETIC_RISK_LINKS",
        "status": "REVIEW_PENDING", "started_at": started, "ended_at": now(),
        "elapsed_seconds": perf_counter() - timer,
        "actual_command": ".venv/bin/python -m task1.evidence.goal2.a_epoch02.actual_ai_critique.build_actual_ai_critique",
        "generator": binding(Path(__file__)), "analysis_source": binding(analysis),
        "read_scope_registry": binding(snapshot_path), "independent_input_reviews": receipts,
        "raw_sha256": inputs.split["raw_sha256"], "contract_sha256": inputs.contract_hash,
        "split_sha256": inputs.split_hash, "source_crs": "UNVERIFIED", "unit": "working_metre",
        "actual_scope": {"run_id": snapshot["mode_development"], "record_episode_observations": len(records),
            "visible_experiment_model_dispatches": len(tables["model_calls"]),
            "preserved_original_proposals": sum(row["original_present"] for row in tables["mode_proposals"]),
            "category_coverage": actual["category_coverage"],
            "evaluable_prediction_denominator": sum(row["prediction_evaluable"] for row in tables["mode_proposals"]),
            "no_current_development_illegal_proposal_or_fallback_or_evaluable_prediction_mismatch": all(
                actual["category_coverage"][kind]["observed_count"] == 0
                for kind in ("ILLEGAL_PROPOSAL", "FALLBACK", "PREDICTION_MISMATCH"))},
        "case_selection": "All4 actual legal tradeoffs retained; correct/unevaluable prediction representatives use the existing stable partition/mode/episode/record/round/proposal order. No holdout episode was read for selection.",
        "actual_ai_citations": citations, "synthetic_counterexamples": risks,
        "counterexample_run": counterexample_summary,
        "synthetic_fixture_contract": synthetic["fixture_contract"],
        "synthetic_fixture_contract_hash": synthetic["fixture_contract_hash"],
        "input_hashes": inputs.lineage,
        "checks": {"original_quotes_match_actual_response_json": True,
            "reference_candidate_objects_match_prediction_hashes": True,
            "all_candidate_reviews_match_exact_objects": True,
            "actual_locked_output_flags_checked": True,
            "all25_synthetic_known_answer_checks_passed": True,
            "synthetic_actual_execution_bindings_checked": True,
            "no_synthetic_risk_attributed_as_unobserved_model_error": True},
        "new_model_calls": 0, "new_candidate_processing_runs": 0, "new_counterexample_runs": 0,
        "G2_EVAL_mode_artifacts_read": False, "G2_EVAL_parameter_results_read_in_this_task": False,
        "frozen_sources_or_selection_changed": False,
        "limits": ["Real model proposals and synthetic fixtures have distinct provenance and denominators", "Valid execution and prediction sign do not establish real noise classification accuracy", "Legal tradeoff suggestions are hypotheses with observed limitations, not illegal actions or hallucinations", "No final method, combination, Human Approval or GPT final acceptance is claimed"]}
    assert digest(analysis) == analysis_hash
    write_json(output, result, exclusive=True)
    lines = ["# 实际 AI 提议与构造反例", "",
        "本记录引用已经独立核验的 DEVELOPMENT LIVE 响应，关联已经真实执行的 formal-02 构造反例。未读取尚在运行的正式模式、未新增模型或处理调用。它补充 actual_ai_citations，等待独立审查；不改变方法、指标或参数。", "",
        "开发期148条原始提议均合法执行，0回退；70条可评价方向预测均一致，另78条不可评价。下面保留全部4条合法但出现 TRADEOFF 的建议，另按既有稳定排序引用一条一致预测和一条未承诺预测。权衡不是非法动作或幻觉，构造风险也不代表模型曾作过对应错误断言。", ""]
    for item in citations:
        source = os.path.relpath(ROOT / item["raw_response"]["path"], directory)
        before, after = item["reference_metrics"], item["candidate_metrics"]
        prediction = item["pre_execution_prediction"]
        lines += [f"## {item['citation_id']} · {item['kind']} · 记录 {item['record_id']}", "",
            f"{item['mode']}，episode {item['episode']}，round {item['round']}；[原始 response]({source})。响应SHA256：`{item['raw_response']['sha256']}`。", "",
            "> " + item["verbatim_model_reason"], "",
            f"执行前预测：`{prediction['metric_id']}` / `{prediction['predicted_sign']}`，参考句柄 `{prediction['reference_handle_locked_before_execution']}`。"
            f"实测预测状态 `{item['actual_metric_check']['prediction_status']}`，差值 `{item['actual_metric_check']['delta']}`；是否锁定为最终输出：{item['proposal_became_locked_output']}。", "",
            "| 已执行读数 | 共同参考配置 | 实际提议 |", "|---|---:|---:|",
            f"| 原始点分母 | {before['n_input']} | {after['n_input']} |",
            f"| 共同覆盖点 | {before['common_covered_points']} | {after['common_covered_points']} |",
            f"| 共同几何最大误差／工作米 | {before['common_max_error']} | {after['common_max_error']} |",
            f"| 本次DP完整输入点 | {before['n_dp_input']} | {after['n_dp_input']} |",
            f"| 本次DP最大误差／工作米 | {before['dp_max_error']} | {after['dp_max_error']} |",
            f"| 方向删除点 | {before['n_direction_removed']} | {after['n_direction_removed']} |", "",
            item["A_adjudication"], "", item["synthetic_connection"]["reason"], ""]
        comparison = item["registered_comparison"]
        if comparison:
            guards = comparison["registered_protection_readings"]
            lines += [f"冻结保护：`{guards['protection_failures']}`；基线已覆盖身份集合上的误差 {guards['baseline_common_max']} → {guards['candidate_max_on_baseline_covered']} 工作米。"
                "候选自身DP合格不覆盖这个跨方法比较。完整参数、共同参考单位、记录/阶段hash及锁定配置见JSON。", ""]
    lines += ["## 已执行构造风险", "",
        "六组反例共19条构造处理链、25项已知答案核验；另有10条已暴露pilot处理链，均是已有正式运行，本关联工作没有新增运行。", "",
        "| 反例 | 实际核验内容 | 与模型的关系 |", "|---|---|---|"]
    for risk in risks:
        related = ", ".join(risk["related_actual_citation_ids"]) or "无对应实际模型断言"
        lines.append(f"| {risk['case_id']} | {risk['family']}；{len(risk['known_answer_checks'])}项已知答案通过 | {related}；仅机制/解释边界关联 |")
    lines += ["", "CE01表明正常几何也可能被方向谓词删除；只有构造输入可称误删。CE02保留不可计算速度/方向的明确原因。CE03保存P提前消除断点触发信息的实际失败。CE04拒绝人为注入的无限直线捷径，验证有限线段与阈值等号。CE05空输出仍保留原始分母，误差与DP省点率是null。CE06两条自身DP误差均为0的链，共同原始误差分别为0.4472135955和0，说明阶段内证书不能证明整体更好。", "",
        "这些构造结论不外推真实噪声真值；没有原始响应支持的模型错误不作归因。真实四条建议提出的是可检验假设，确定性保护发现权衡后未将其选入，体现实际建议—执行—核验流程。", ""]
    document = directory / "ACTUAL_AI_CRITIQUE.md"
    document.write_text("\n".join(lines), encoding="utf-8")
    targets = [binding(output), binding(document), binding(Path(__file__))]
    write_json(directory / "review_targets.json", {"status": "REVIEW_PENDING",
        "classification": "ACTUAL_AI_CITATIONS_SUBMISSION_TARGETS", "targets": targets,
        "self_not_in_targets_to_avoid_hash_self_reference": True}, exclusive=True)
    print({"status": result["status"], "output": relative(output), "sha256": digest(output),
        "citations": len(citations), "legal_tradeoffs": 4, "synthetic_cases": len(risks),
        "targets_sha256": digest(directory / "review_targets.json"), "elapsed_seconds": result["elapsed_seconds"]})


if __name__ == "__main__":
    main()
