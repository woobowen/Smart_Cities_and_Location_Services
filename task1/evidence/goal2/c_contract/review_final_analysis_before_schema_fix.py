"""Independent C analysis audit using previously raw-verified immutable traces.

No production analysis, aggregation or selection function is imported. Full
record/candidate, pair, stage, null, grouped distribution and cost checks are
reconstructed from the original bound artifacts; mathematical processing was
already independently verified by the cited C run reviews.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import csv
from itertools import combinations
import json
import math
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS
from review_development_runs import Audit, read_compressed, summary_expected, COUNT_FIELDS
from review_live_modes_epoch02 import assessment, prediction, compact, MODES
from review_single_confirmation import paired, outcomes, status, check_csv, PAIR_METRICS

OUT = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def describe(values):
    available = [float(v) for v in values if v is not None]
    n = len(available)
    return {"denominator": len(values), "available": n, "unavailable": len(values) - n,
            "mean": statistics.fmean(available) if n else None, "median": statistics.median(available) if n else None,
            "min": min(available) if n else None, "max": max(available) if n else None,
            "sample_sd": statistics.stdev(available) if n > 1 else None,
            "reason": None if n else "NO_AVAILABLE_VALUES", "sd_reason": None if n > 1 else "FEWER_THAN_TWO_AVAILABLE_VALUES"}


def covered(row):
    return {r["index"] for r in row["metrics"]["common_point_errors"] if r["error"] is not None}


def main():
    started = time.perf_counter()
    audit = Audit()
    state = read_json(EV / "goal_state.json")
    submitted = deepcopy(state["tasks"]["analysis"]["evidence"])
    for entry in submitted:
        audit.check("submitted_target_hash", digest(ROOT / entry["path"]) == entry["sha256"])
    summary = read_json(EV / "result_summary.json")
    for path, sha in summary["input_hashes"].items():
        audit.check("analysis_input_binding", digest(ROOT / path) == sha)
    audit.check("current_analysis_source", summary["analysis_source_sha256"] == digest(ROOT / "task1/scripts/build_goal2_analysis.py"))
    audit.check("limits_and_no_reselection", not summary["selection_after_evaluation"] and not summary["final_method_frozen"] and not summary["quality_accepted"]
                and summary["normalized_regret"] is None and summary["source_crs"] == "UNVERIFIED" and summary["GPT_SECOND_REVIEW"] == "PENDING" and summary["submission"] == "NOT_READY")
    audit.check("all_derived_inputs_complete", summary["missing_requirements"] == [] and summary["analysis_model_dispatches"] == summary["analysis_candidate_evaluations"] == summary["analysis_memory_writes"] == 0)
    tables, consumed = {}, defaultdict(set)
    for name, entry in summary["tables"].items():
        path = ROOT / entry["path"]
        audit.check("table_hash", digest(path) == entry["sha256"])
        with path.open(newline="", encoding="utf8") as stream:
            tables[name] = list(csv.DictReader(stream))
        audit.check("table_denominator", len(tables[name]) == entry["rows"])
    audit.check("all39_tables111053rows", len(tables) == 39 and sum(map(len, tables.values())) == 111053)
    indexes = {}
    def index(name, fields):
        if name not in indexes:
            mapping = {tuple(row[k] for k in fields): (i, row) for i, row in enumerate(tables[name])}
            audit.check(name + ":unique_key", len(mapping) == len(tables[name]))
            indexes[name] = mapping
        return indexes[name]
    def verify(name, fields, key, expected):
        lookup = index(name, fields)
        normalized = tuple(str(v) for v in key)
        audit.check(name + ":row_present", normalized in lookup, normalized)
        if normalized in lookup:
            i, row = lookup[normalized]
            consumed[name].add(i)
            check_csv(audit, row, expected, name)
    basekeys = ("run_id", "config_id", "order", "record_id")
    current = summary["current_runs"]
    contract = read_json(ROOT / "task1/config/goal2/contract.json")
    cards = read_json(EV / "data/raw_diagnostics.json")
    ref = contract["reference_parameters"]
    catalogs = {}
    for role, prefix in (("parameter_development", "parameter"), ("evaluation_parameters", "parameter"), ("order_development", "order"), ("evaluation_orders", "order")):
        directory = EV / "runs" / current[role]
        manifest = read_json(directory / "manifest.json")
        entries = list(manifest["artifacts"].values())
        ref_entry = next(e for e in entries if e["parameters"] == ref and e["order"] == "S-D-P")
        references = {r["record_id"]: r for r in read_compressed(directory / ref_entry["file"])["records"]}
        catalog = {}
        for entry in entries:
            batch = read_compressed(directory / entry["file"])
            audit.check("bound_actual_batch", digest(directory / entry["file"]) == entry["sha256"])
            cid, order, runid = entry["config_id"], entry["order"], manifest["run_id"]
            context = {"run_role": role, "run_id": runid, "partition": manifest["partition"], "experiment_key": entry["experiment_key"],
                       "config_id": cid, "order": order, **entry["parameters"], "result_sha256": entry["sha256"], "engineering_status": entry["engineering_status"]}
            comparisons, records, strata, failures, signatures = [], {}, defaultdict(list), [], []
            for row in batch["records"]:
                rid, m = row["record_id"], row["metrics"]
                pair = paired(row, references[rid])
                comparisons.append(pair)
                stratum = cards[rid]["stratum"]
                strata[stratum].append(row)
                key = (runid, cid, order, rid)
                lost = sorted(covered(references[rid]) - covered(row))
                fail = bool(m["raw_break_crossings"] or lost or references[rid]["metrics"]["record_covered"] and not m["record_covered"]
                            or m["raw_windows_covered"] < references[rid]["metrics"]["raw_windows_covered"])
                expected = {**context, "stratum": stratum, **compact(m)}
                if prefix == "order":
                    expected.update(pair, safety_failure=fail, lost_baseline_covered_indices=lost)
                    if fail: failures.append(rid)
                verify(prefix + "_records", basekeys, key, expected)
                if prefix == "parameter":
                    verify("parameter_record_pairs", basekeys, key, {**context, "stratum": stratum, **pair})
                for stage, reading in m["stage_readings"].items():
                    verify("stage_readings", basekeys + ("stage",), key + (stage,), {**context, "record_id": rid, "stage": stage, **reading})
                for kind in ("filter_reason_segments", "filter_reason_points", "direction_undefined_reasons"):
                    for reason, count in m[kind].items():
                        verify("processing_reasons", basekeys + ("count_kind", "reason"), key + (kind, reason), {**context, "record_id": rid, "count_kind": kind, "reason": reason, "count": count})
                if prefix == "order" and (fail or m["direction_windows_across_raw_breaks"] or m["p_removed_raw_break_trigger_points"] or order.index("P") < order.index("D")):
                    stage_map = {s["name"]: s for s in row["stages"]}
                    before_d = [s["indices"] for s in next(s for s in references[rid]["stages"] if s["name"] == "D")["input"]]
                    after_d = [s["indices"] for s in stage_map["D"]["input"]]
                    verify("order_failure_mechanisms", basekeys, key, {**context, "record_id": rid, "safety_failure": fail, "lost_baseline_covered_indices": lost,
                           "crossing_edges": m["breakpoint_crossing_edges"], "D_windows_across_raw_breaks": m["direction_window_crossing_details"],
                           "P_removed_original_trigger_indices": m["p_removed_raw_break_trigger_indices"], "P_before_S": order.index("P") < order.index("S"), "P_before_D": order.index("P") < order.index("D"),
                           "D_input_neighbourhood_changed_from_reference": before_d != after_d, "reference_D_input_indices": before_d, "actual_D_input_indices": after_d,
                           "n_filtered": m["n_filtered"], "all_filtered": m["all_filtered"], "no_output": m["no_output"], "engineering_error_claim": False})
                mask = object_hash({"record_id": rid, "stage_masks": [{"name": s["name"], "input": [q["indices"] for q in s["input"]], "output": [q["indices"] for q in s["output"]]} for s in row["stages"]],
                                    "common_covered_indices": sorted(covered(row)), "counts": {k: m[k] for k in COUNT_FIELDS}})
                signatures.append((rid, mask))
                records[rid] = {"metrics": compact(m), "comparison": pair, "stratum": stratum}
            aggregate = summary_expected([r["metrics"] for r in batch["records"]])
            expected = {**context, **aggregate, **outcomes(comparisons), "research_status": "REJECTED_BY_CONSTRAINT" if prefix == "order" and failures else status(comparisons)}
            if prefix == "order":
                expected.update(safety_failure_records=len(failures), safety_failure_record_ids=failures, eligible_order_for_frozen_evaluation=not failures,
                                geometric_guard_failures=sum("COMMON_GEOMETRIC_PROTECTION_DEGRADED" in p["protection_failures"] for p in comparisons))
            else:
                expected["memberships"] = entry["experiment_ids"]
                for stratum, rows in strata.items():
                    ps = [records[r["record_id"]]["comparison"] for r in rows]
                    verify("parameter_by_stratum", ("run_id", "config_id", "stratum"), (runid, cid, stratum),
                           {**context, "stratum": stratum, **summary_expected([r["metrics"] for r in rows]), **outcomes(ps), "research_status": status(ps)})
            verify(prefix + "_configurations", ("run_id", "config_id", "order"), (runid, cid, order), expected)
            catalog[cid] = {"parameters": entry["parameters"], "records": records, "feasible": all(p["feasible"] for p in comparisons), "status": status(comparisons), "signature": object_hash(signatures)}
        if prefix == "parameter": catalogs[role] = catalog
        print("C analysis bound records", role, len(entries), "errors", len(audit.errors), flush=True)
    # Complete feasible domains, including no-gain configurations and ties.
    dev = catalogs["parameter_development"]
    lock = read_json(EV / "candidate_lock.json")
    for family, changed in {"C-S": {"dt", "distance", "min_points", "min_length"}, "C-D": {"direction"}, "C-P": {"dp"}}.items():
        domain = {cid: r for cid, r in dev.items() if all(r["parameters"][k] == ref[k] for k in ref if k not in changed)}
        feasible = {cid: r for cid, r in domain.items() if r["feasible"]}
        def dominates(left, right):
            strict = False
            for rid, x in left["records"].items():
                y = right["records"][rid]
                a, b = x["comparison"], y["comparison"]
                eps = max(a["numerical_allowance"], b["numerical_allowance"])
                if not set(b["candidate_covered_indices"]) <= set(a["candidate_covered_indices"]): return False
                if family == "C-P":
                    na, nb = x["metrics"]["n_dp_output"], y["metrics"]["n_dp_output"]
                    if na > nb: return False
                    strict |= na < nb
                    ea, eb = x["metrics"]["dp_max_error"], y["metrics"]["dp_max_error"]
                else:
                    strict |= a["candidate_covered_count"] > b["candidate_covered_count"]
                    ea, eb = a["candidate_max_on_baseline_covered"], b["candidate_max_on_baseline_covered"]
                if (ea is None) != (eb is None) or ea is not None and ea > eb + eps: return False
                strict |= ea is not None and ea < eb - eps
            return strict
        for cid, row in domain.items():
            dominated = [other for other, x in feasible.items() if other != cid and row["feasible"] and dominates(x, row)]
            verify("feasible_pareto", ("family", "config_id"), (family, cid), {"family": family, "config_id": cid, **row["parameters"],
                   "feasible_all_records": row["feasible"], "on_feasible_frontier": row["feasible"] and not dominated, "dominated_by": dominated,
                   "research_status": row["status"], "selected_before_evaluation": lock["selected_single_candidates"][family]["config_id"] == cid,
                   "selection_changed_by_this_analysis": False, "frontier_is_quality_acceptance": False})
    for i, row in enumerate(tables["stable_intervals"]):
        cids = json.loads(row["config_ids"])
        audit.check("stable_mask_signature", all(dev[cid]["signature"] == row["identical_stage_masks_and_counts_hash"] for cid in cids))
        audit.check("stable_only_tested_values", row["stable_at_multiple_tested_values"] == str(len(cids) > 1))
        consumed["stable_intervals"].add(i)
    audit.check("no_fabricated_stability_plateau", all(r["stable_at_multiple_tested_values"] == "False" for r in tables["stable_intervals"]))
    # Previously independently verified named single-candidate confirmation is
    # identical and shares calculation objects; it is not a second experiment.
    singles = read_json(EV / "a_epoch02/heldout_single_confirmation/single_candidate_confirmation.json")
    for item in summary["single_candidates"]:
        previous = next(r for r in singles["candidate_results"] if r["candidate"] == item["candidate"])
        audit.same("named_candidate_summary_unchanged", item, {k: previous[k] for k in item})
        verify("candidate_evaluation", ("candidate",), (item["candidate"],), item)
    for name in ("candidate_record_pairs", "candidate_by_stratum", "candidate_development"):
        candidates = list((EV / "a_epoch02/heldout_single_confirmation").rglob(name + ".csv"))
        audit.check("prior_single_table_found", len(candidates) == 1)
        if candidates:
            with candidates[0].open(newline="", encoding="utf8") as f: prior = list(csv.DictReader(f))
            audit.check("prior_single_table_exact", tables[name] == prior)
            consumed[name].update(range(len(tables[name])))
    # Mode trace -> raw proposal / selected output / per-record repeated statistics.
    mode_records, mode_batches, mode_calls = [], [], []
    mode_keys = ("episode_id", "record_id")
    for role in ("mode_development", "mode_evaluation"):
        d = EV / "runs" / current[role]
        manifest = read_json(d / "manifest.json")
        for registered in manifest["mode_episodes"]:
            ep_path = d / registered["path"]
            episode = read_json(ep_path)
            context = {"run_id": manifest["run_id"], "partition": manifest["partition"], "mode": episode["mode"], "episode": episode["episode"], "episode_id": episode["episode_id"]}
            resources = {**context, **episode["resources"], "elapsed_seconds": episode["elapsed_seconds"]}
            mode_batches.append(resources)
            verify("mode_batch_resources", ("episode_id",), (episode["episode_id"],), {**resources, "records": len(episode["records"]), "classification": episode["classification"]})
            for filename, sha in episode["artifact_hashes"].items():
                if filename.endswith("/receipt.json"):
                    path = ep_path.parent / filename
                    receipt = read_json(path)
                    audit.check("actual_provider_receipt", digest(path) == sha)
                    expected = {**context, **compact(receipt), "receipt_path": str(path.relative_to(ROOT)), "receipt_sha256": sha, "usage": receipt["usage"],
                                "visible_counts": receipt.get("visible_counts"), **{k: receipt["usage"].get(k) for k in ("input_tokens", "cached_input_tokens", "output_tokens")}, "tokens_reason": None}
                    verify("model_calls", ("receipt_path",), (str(path.relative_to(ROOT)),), expected)
                    mode_calls.append(expected)
            retrievals = read_json(ep_path.parent / "memory_retrieval.json") if episode["mode"] == "llm+memory+search" else {}
            for rid, retrieval in retrievals.items():
                delivered = retrieval["delivered"]
                verify("memory_retrieval", mode_keys, (episode["episode_id"], rid), {**context, "record_id": rid, "eligible_count": retrieval["eligible_count"],
                       "delivered_count": len(delivered), "delivered_ids": [r["memory_id"] for r in delivered], "filtered_count": len(retrieval["filtered"]), "filtered": retrieval["filtered"],
                       "empty_reason": retrieval["empty_reason"], "snapshot_before": retrieval["snapshot_sha256"], "snapshot_after": episode["snapshot_after"], "hash_unchanged": retrieval["snapshot_sha256"] == episode["snapshot_after"]})
                for item in delivered:
                    verify("memory_delivered_entries", ("episode_id", "query_record_id", "memory_id"), (episode["episode_id"], rid, item["memory_id"]),
                           {**context, "query_record_id": rid, "memory_id": item["memory_id"], "memory_record_id": item["record_id"], "stratum": item["stratum"], "retrieval_distance": item["retrieval_distance"], "selected_parameters": item["selected_parameters"], "research_status": item["research_status"]})
            for record in episode["records"]:
                rid = record["record_id"]
                traces = read_compressed(ep_path.parent / (rid + "_candidate_traces.json.gz"))["results"]
                reference, selected = traces[record["reference_config_id"]], traces[record["selected_config_id"]]
                for cid, candidate in traces.items():
                    compare = assessment(candidate, reference)
                    verify("mode_candidates", mode_keys + ("config_id",), (episode["episode_id"], rid, cid), {**context, "record_id": rid, "config_id": cid,
                           **candidate["parameters"], **compact(candidate["metrics"]), **compare, "selected": cid == record["selected_config_id"], "reference": cid == record["reference_config_id"],
                           "on_recorded_frontier": cid in record["selection"].get("frontier", []), "frontier_reason": None if "frontier" in record["selection"] else "SINGLE_LOCKED_PROPOSAL_MODE"})
                pair = paired(selected, reference)
                row = {**context, "record_id": rid, "stratum": cards[rid]["stratum"], "selected_config_id": record["selected_config_id"], "selected_parameters": record["selected_parameters"],
                       "fallback": record["fallback"], "selection_reason": record["selection"]["reason"], "memory_snapshot_hash": record["memory_snapshot_hash"], **record["resources"], **pair}
                verify("mode_record_results", mode_keys, (episode["episode_id"], rid), row)
                row.update(selected_metrics=selected["metrics"], selected_mask=covered(selected), selected_dp_hash=object_hash(next(s["input"] for s in selected["stages"] if s["name"] == "P")),
                           proposal_records=record["proposal_records"], rounds=record["rounds"])
                mode_records.append(row)
                for number, proposal in enumerate(record["proposal_records"], 1):
                    original = proposal["original"]
                    predicted = prediction(original, traces[proposal["executed_config_id"]], reference)
                    expected = {**context, "record_id": rid, "proposal_number": number, "round": proposal["round"], "original_proposal": original, "original_present": True,
                                "candidate_id": original["candidate_id"], "parameters": original["parameters"], "reason": original["reason"], "legal": proposal["legal"], "executed": proposal["executed"],
                                "executed_config_id": proposal["executed_config_id"], "rejection_reason": proposal["rejection_reason"], "metric_id": original["metric_id"], "predicted_sign": original["predicted_sign"],
                                "prediction_status": predicted["status"], "prediction_evaluable": predicted["evaluable"], "prediction_matches": predicted.get("prediction_matches"), "observed_sign": predicted.get("observed_sign"), "delta": predicted.get("delta"),
                                "reference_handle": proposal["reference_handle_locked_before_execution"], "prediction_reference_trace_hash": predicted["reference_handle"], "prediction_candidate_trace_hash": predicted["candidate_handle"],
                                "fallback_for_record": record["fallback"], "proposal_is_selected_output": proposal["executed_config_id"] == record["selected_config_id"], "raw_proposal_was_clamped": False}
                    verify("mode_proposals", mode_keys + ("proposal_number",), (episode["episode_id"], rid, number), expected)
                for decision in record["rounds"]:
                    verify("mode_rounds", mode_keys + ("round",), (episode["episode_id"], rid, decision["round"]), {**context, "record_id": rid, **decision})
                    if "memory_consumption" in decision:
                        use = decision["memory_consumption"]
                        verify("memory_consumption", mode_keys + ("round",), (episode["episode_id"], rid, decision["round"]), {**context, "record_id": rid, "round": decision["round"], **use,
                               "delivered_count": len(use["delivered_ids"]), "valid_citation_count": len(use["model_cited_valid"]), "invalid_citation_count": len(use["model_cited_invalid"]),
                               "action_consistent_count": len(use["action_consistent"]), "action_consistent_is_causal_benefit": False})
        print("C analysis complete mode trace bindings", role, "errors", len(audit.errors), flush=True)
    by_episode, by_record, by_mode = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in mode_records:
        by_episode[(row["partition"], row["mode"], row["episode"])].append(row)
        by_record[(row["partition"], row["mode"], row["record_id"])].append(row)
        by_mode[(row["partition"], row["mode"])].append(row)
    for (partition, mode, episode), rows in by_episode.items():
        for metric in PAIR_METRICS:
            for reading, values in (("locked_selected_value", [r["selected_metrics"][metric] for r in rows]), ("paired_delta_from_reference_on_comparable_domains", [r["delta_" + metric] for r in rows])):
                verify("mode_episode_distributions", ("partition", "mode", "episode", "metric", "reading"), (partition, mode, episode, metric, reading), {"statistical_unit": "original_record", **describe(values)})
    for (partition, mode, rid), rows in by_record.items():
        for metric in PAIR_METRICS:
            verify("mode_record_repeat_distributions", ("partition", "mode", "record_id", "metric"), (partition, mode, rid, metric), {"episodes": [r["episode"] for r in rows], **describe([r["selected_metrics"][metric] for r in rows])})
    for (partition, mode), rows in by_mode.items():
        for metric in PAIR_METRICS:
            values = [describe([r["selected_metrics"][metric] for r in group])["mean"] for key, group in by_record.items() if key[:2] == (partition, mode)]
            verify("mode_original_record_summary", ("partition", "mode", "metric"), (partition, mode, metric), describe(values))
        proposals = [p for r in rows for p in r["proposal_records"]]
        batches = [r for r in mode_batches if (r["partition"], r["mode"]) == (partition, mode)]
        calls = [r for r in mode_calls if (r["partition"], r["mode"]) == (partition, mode)]
        evaluated = [p for p in proposals if p["prediction"]["evaluable"]]
        expected = {"original_records": len({r["record_id"] for r in rows}), "episodes": len({r["episode"] for r in rows}), "record_episode_observations": len(rows),
                    "valid_raw_proposal_denominator": len(proposals), "raw_legal_proposals": sum(p["legal"] for p in proposals), "raw_legal_fraction": sum(p["legal"] for p in proposals) / len(proposals) if proposals else None,
                    "raw_legal_fraction_reason": None if proposals else "NO_RAW_PROPOSALS_IN_THIS_MODE_OR_VALID_RESPONSE", "invalid_structure_record_actions": 0,
                    "executed_proposals": sum(p["executed"] for p in proposals), "executed_proposal_fraction": sum(p["executed"] for p in proposals) / len(proposals) if proposals else None,
                    "rejection_reasons": {}, "evaluable_prediction_denominator": len(evaluated), "matching_predictions": sum(p["prediction"].get("prediction_matches") is True for p in evaluated),
                    "prediction_agreement": sum(p["prediction"].get("prediction_matches") is True for p in evaluated) / len(evaluated) if evaluated else None,
                    "prediction_statuses": dict(Counter(p["prediction"]["status"] for p in proposals)), "fallback_records_episodes": sum(r["fallback"] for r in rows),
                    "constraint_rejected_records_episodes": sum(r["status"] == "REJECTED_BY_CONSTRAINT" for r in rows), "tradeoff_records_episodes": sum(r["status"] == "TRADEOFF" for r in rows),
                    "protected_gain_records_episodes": sum(r["strict_gain"] for r in rows), "max_candidates_per_record_episode": max(r["unique_candidate_evaluations"] for r in rows),
                    "max_decision_rounds_per_record_episode": max(r["decision_rounds"] for r in rows), "elapsed_batch_seconds_sum": sum(r["elapsed_seconds"] for r in batches),
                    "provider_request_count": 0 if mode == "search-only" else "unknown", "governance_role_dispatches": 0, "cost_currency": "unavailable", "quality_accepted": False}
        for field in ("experiment_model_dispatches", "completed_model_turns", "candidate_evaluations", "reference_assessments_outside_llm_only_decision", "deterministic_tool_calls"):
            expected[field] = sum(r[field] for r in batches)
        expected["replay_or_cache_reads"] = sum(r["cache_reads"] for r in batches)
        for token in ("input_tokens", "cached_input_tokens", "output_tokens"):
            expected.update({token + "_observed_sum": sum(r[token] for r in calls), token + "_available_call_receipts": len(calls), token + "_unavailable_call_receipts": 0})
        verify("mode_summary", ("partition", "mode"), (partition, mode), expected)
        actual = next(r for r in summary["mode_summary"] if (r["partition"], r["mode"]) == (partition, mode))
        audit.same("summary_mode_aggregates", {k: actual[k] for k in expected}, expected, 1e-8)
    lookup = {(r["partition"], r["episode"], r["record_id"], r["mode"]): r for r in mode_records}
    for key in sorted({k[:3] for k in lookup}):
        for first, second in combinations(MODES, 2):
            left, right = lookup[key + (first,)], lookup[key + (second,)]
            for metric in PAIR_METRICS:
                a, b = left["selected_metrics"][metric], right["selected_metrics"][metric]
                reason = "UNAVAILABLE_IN_AT_LEAST_ONE_ARM" if a is None or b is None else "DIFFERENT_COMMON_COVERED_MASK" if metric == "common_max_error" and left["selected_mask"] != right["selected_mask"] else "DIFFERENT_DP_INPUT_REFERENCE" if metric in ("n_dp_output", "dp_saving", "dp_max_error") and left["selected_dp_hash"] != right["selected_dp_hash"] else None
                verify("mode_pairwise", ("partition", "episode", "record_id", "mode_a", "mode_b", "metric"), key + (first, second, metric),
                       {"value_a": a, "value_b": b, "difference_b_minus_a": None if reason else b - a, "unavailable_reason": reason, "statistical_unit": "original_record", "causal_effect_claim": False})
        left, right = lookup[key + ("llm+search",)], lookup[key + ("llm+memory+search",)]
        a, b = [[p["original"]["parameters"] for p in r["proposal_records"] if p["round"] == 1] for r in (left, right)]
        verify("memory_independent_mode_comparison", ("partition", "episode", "record_id"), key,
               {"without_memory_initial_parameters": a, "with_memory_initial_parameters": b, "initial_proposal_changed": a != b, "comparison_reason": None,
                "selected_parameters_changed": left["selected_parameters"] != right["selected_parameters"], "without_memory_selected": left["selected_parameters"], "with_memory_selected": right["selected_parameters"],
                "memory_delivered_rounds": sum(bool(r.get("memory_consumption", {}).get("delivered_ids")) for r in right["rounds"]),
                "memory_cited_rounds": sum(bool(r.get("memory_consumption", {}).get("model_cited_valid")) for r in right["rounds"]),
                "memory_action_consistent_rounds": sum(bool(r.get("memory_consumption", {}).get("action_consistent")) for r in right["rounds"]), "causal_benefit_proven": False})
    # Synthetic, exposed pilot and memory snapshots are separately independently reviewed.
    synthetic = read_json(EV / "counterexamples/formal-02/synthetic_cases.json")
    for case in synthetic["cases"]:
        for name, execution in case["executions"].items():
            verify("counterexamples", ("case_id", "execution"), (case["case_id"], name), {**compact(execution["output"]["metrics"]), "parameters": execution["output"]["parameters"], "order": execution["output"]["order"],
                   "classification": "SYNTHETIC_COUNTEREXAMPLE", "synthetic_truth_counts": execution.get("synthetic_detection_counts"), "known_answer_checks": case["known_answer_checks"], "real_data_accuracy_claim": False})
    pilot = read_json(EV / "counterexamples/formal-02/exposed_pilot_cases.json")
    for tab, key in (("exposed_pilot_filtering", "all_filtered_records_0_1_2"), ("exposed_pilot_direction", "direction_adjacency_cases")):
        items = pilot[key]
        if isinstance(items, dict): items = list(items.values())
        for item in items: verify(tab, ("record_id",), (item["record_id"],), item)
    memory = read_json(ROOT / summary["memory"]["snapshot_path"])
    for entry in memory["entries"]:
        verify("memory_entries", ("record_id",), (entry["record_id"],), {k: v for k, v in entry.items() if k != "trusted_provenance"})
    # All actual legal tradeoffs, including holdout observations, remain present.
    candidate_table = index("mode_candidates", ("episode_id", "record_id", "config_id"))
    expected_tradeoffs = []
    for number, proposal in enumerate(tables["mode_proposals"]):
        key = (proposal["episode_id"], proposal["record_id"], proposal["executed_config_id"])
        if candidate_table[key][1]["status"] == "TRADEOFF": expected_tradeoffs.append(proposal)
        for source in json.loads(proposal["raw_response_sources"]):
            audit.check("table_quote_actual_response_hash", digest(ROOT / source["path"]) == source["sha256"])
    audit.check("complete6_actual_tradeoffs", len(expected_tradeoffs) == len(tables["ai_legal_proposal_tradeoffs"]) == 6)
    for tab in ("ai_legal_proposal_tradeoffs", "ai_critique_examples"):
        for number, row in enumerate(tables[tab]):
            key = (row["episode_id"], row["record_id"], row["proposal_number"])
            source = index("mode_proposals", mode_keys + ("proposal_number",))[key][1]
            audit.check("actual_AI_table_fields", all(row[k] == v for k, v in source.items()))
            consumed[tab].add(number)
    # Visible model costs are read from actual receipt files, not role dispatches.
    ledger = read_json(EV / "resource_ledger.json")
    audit.check("resource_ledger_summary_parent", ledger["analysis_summary_sha256"] == digest(EV / "result_summary.json") and ledger["generator_sha256"] == digest(EV / "refresh_resource_ledger.py"))
    discovered = {str(p.relative_to(ROOT)) for p in EV.rglob("receipt.json") if "requested_model" in read_json(p)}
    audit.check("all100_visible_provider_attempts", discovered == {r["receipt"] for r in ledger["attempts"]} and len(discovered) == ledger["visible_cli_provider_attempts_all_scopes"] == 100)
    cost_groups = defaultdict(list)
    for entry in ledger["attempts"]:
        path = ROOT / entry["receipt"]
        receipt = read_json(path)
        audit.check("receipt_dispatch_actual_hash", digest(path) == entry["sha256"] and digest(path.with_name("dispatch.json")) == entry["dispatch_sha256"])
        for key in ("status", "thread_id", "requested_model", "usage", "started_at", "ended_at", "elapsed_seconds"):
            audit.same("ledger:" + key, entry[key], receipt.get(key))
        cost_groups[entry["scope"]].append(entry)
    for group in ledger["provider_scope_summaries"]:
        rows = cost_groups[group["scope"]]
        usage = [r["usage"] for r in rows if r["usage"] is not None]
        keys = {k for u in usage for k in u}
        audit.same("provider_scoped_usage", group["observed_usage_sums"], {k: sum(u.get(k, 0) for u in usage) for k in keys})
        audit.check("provider_unknown_costs", group["visible_dispatches"] == len(rows) and group["usage_unavailable_dispatches"] == len(rows) - len(usage)
                    and group["complete_usage_total_available"] == (len(rows) == len(usage)) and group["underlying_request_total"] == "unknown" and group["cost_currency"] == "unavailable")
    audit.check("provider_scope_class_counts", {k: len(v) for k, v in cost_groups.items()} == {"CURRENT_VALID_EXPERIMENT": 84, "HISTORICAL_SUPERSEDED_OR_INTERRUPTED_EXPERIMENT": 15, "ENGINEERING_PROVIDER_QUALIFICATION": 1})
    for number, row in enumerate(tables["historical_model_calls"]):
        p = ROOT / row["receipt_path"]; receipt = read_json(p)
        audit.check("historical_receipt_hash", digest(p) == row["receipt_sha256"])
        check_csv(audit, row, {"usage": receipt.get("usage"), "status": receipt["status"], "counts_as_current_effectiveness_evidence": False}, "historical_cost")
        consumed["historical_model_calls"].add(number)
    for number, row in enumerate(tables["resource_totals"]):
        path = ROOT / row["manifest_path"]; manifest = read_json(path)
        audit.check("registered_resource_manifest", digest(path) == row["manifest_sha256"])
        admission = 60 if "memory_snapshot" in manifest else 0
        expected = {"candidate_evaluations_reported_manifest": manifest["candidate_evaluations"], "experiment_model_dispatches_reported_manifest": manifest["experiment_model_dispatches"],
                    "deterministic_tool_calls_reported_manifest": manifest["deterministic_tool_calls"], "cache_hit_batch_verifier_calls": manifest["cache_reads"],
                    "memory_admission_per_record_verifier_calls": admission, "registered_processing_verifier_calls": manifest["deterministic_tool_calls"] + manifest["cache_reads"] + admission}
        check_csv(audit, row, expected, "registered_resource_counter")
        consumed["resource_totals"].add(number)
    for number, row in enumerate(tables["model_cost_scope_summary"]):
        field = "current_valid_model_costs" if row["scope"] == "CURRENT_VALID_RUNS" else "historical_model_costs"
        check_csv(audit, row, summary["resource_accounting"][field], "model_scope_summary")
        consumed["model_cost_scope_summary"].add(number)
    for name in tables:
        audit.check("complete_table_numeric_coverage:" + name, len(consumed[name]) == len(tables[name]), [len(consumed[name]), len(tables[name])])
    document = (ROOT / "task1/docs/goal2/STAGE_ANALYSIS.md").read_text()
    audit.check("stage_document_limits", all(word in document for word in ("UNVERIFIED", "三次", "原始记录", "不代表总体均值", "不能单独证明记忆改善质量", "不冻结最终方法", "NOT_READY", "GPT_SECOND_REVIEW=PENDING")))
    execution = read_json(EV / "a_epoch02/final_analysis/build_execution.json")
    audit.check("actual_analysis_execution", execution["exit_code"] == 0 and execution["status"] == "COMPLETED")
    result = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": "analysis", "at": now(), "targets": submitted,
              "source_hashes": {p: digest(ROOT / p) for p in task_sources("analysis")}, "checked_components": REQUIRED_COMPONENTS["analysis"] + ["all_table_hashes_and_denominators", "full_trace_metrics_and_pairs", "null_comparability_reasons", "complete_feasible_Pareto", "original_record_repeat_statistics", "actual_provider_scopes", "read_stage_analysis"],
              "unchecked_components": ["hidden_provider_requests", "true_noise_labels", "final_Goal2_acceptance", "final_figures_and_Notebooks"], "errors": audit.errors, "check_count": audit.check_count,
              "tables": {name: {"rows": len(rows), "numeric_binding_rows_checked": len(consumed[name])} for name, rows in tables.items()},
              "prior_math_evidence": [bound(OUT / name) for name in ("development_parameters_epoch02_receipt.json", "development_orders_epoch02_receipt.json", "memory_epoch02_receipt.json", "development_modes_epoch02_receipt.json", "evaluation_parameters_bound_receipt.json", "evaluation_orders_bound_receipt.json", "evaluation_modes_complete_receipt.json", "single_candidate_confirmation_receipt.json", "counterexamples_complete_receipt.json")],
              "audit_program": bound(Path(__file__)), "new_model_calls": 0, "new_candidate_experiments": 0, "elapsed_seconds": time.perf_counter() - started}
    write_json(OUT / "analysis_complete_receipt.json", result, exclusive=True)
    print({k: result[k] for k in ("status", "check_count", "errors", "elapsed_seconds")})
    return result


if __name__ == "__main__":
    result = main()
    raise SystemExit(result["status"] != "VERIFIED")
