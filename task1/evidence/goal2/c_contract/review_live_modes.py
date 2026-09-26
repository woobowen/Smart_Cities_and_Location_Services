"""Independent C evidence audit of genuine completed four-mode episodes.

Never dispatches a model or edits a run. Atomic completed episodes may be audited
while the parent run continues, but only a complete fixed-scope run gets a task
receipt. Numerical all-record checks reuse C's independent work-plane oracle.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys
import time

import pyproj

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import (Audit, read_compressed, record_check, config_id, independent_select,
                                     independent_features, OUT, EV, CFG)
from independent_numeric import audit_record
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS
from task1.workflow.g2_modes import PROMPT_TEMPLATE

MODES = ("llm-only", "search-only", "llm+search", "llm+memory+search")
CARD_FIELDS = ("record_id", "n_points", "span_work_m", "duration_seconds", "path_length_work_m", "zero_dt_edges",
               "negative_dt_edges", "dt_over_30_edges", "distance_over_400_edges", "raw_break_edges",
               "adjacent_duplicate_edges", "direction_unavailable_edges", "median_positive_dt", "stratum")


def compact(metric):
    return {key: value for key, value in metric.items() if not isinstance(value, (dict, list))}


def legality(parameters, grids):
    if not isinstance(parameters, dict) or set(parameters) != set(grids):
        return False, "PARAMETER_FIELDS_MISMATCH"
    for key, value in parameters.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value not in grids[key]:
            return False, "OUTSIDE_REGISTERED_GRID:" + key
    return True, None


def prediction(proposal, candidate, reference):
    key, sign = proposal["metric_id"], proposal["predicted_sign"]
    result = {"metric_id": key, "predicted_sign": sign, "reference_handle": object_hash(reference), "candidate_handle": object_hash(candidate)}
    if sign == "not_predicted":
        return {**result, "status": "NOT_PREDICTED", "evaluable": False}
    allowed = ("n_final", "common_covered_points", "common_max_error", "dp_saving", "raw_break_crossings", "n_direction_removed")
    if key not in allowed:
        return {**result, "status": "UNREGISTERED_PREDICTION_METRIC", "evaluable": False}
    cm, bm = candidate["metrics"], reference["metrics"]
    if cm[key] is None or bm[key] is None:
        return {**result, "status": "METRIC_UNAVAILABLE", "evaluable": False}
    if key == "dp_saving" and any(candidate["parameters"][k] != reference["parameters"][k] for k in reference["parameters"] if k != "dp"):
        return {**result, "status": "DIFFERENT_DP_REFERENCE", "evaluable": False}
    if key == "common_max_error":
        masks = [{r["index"] for r in row["metrics"]["common_point_errors"] if r["error"] is not None} for row in (candidate, reference)]
        if masks[0] != masks[1]:
            return {**result, "status": "DIFFERENT_COMMON_COVERAGE", "evaluable": False}
    epsilon = 0 if key in ("n_final", "common_covered_points", "raw_break_crossings", "n_direction_removed") else 1e-12 if key == "dp_saving" else cm["common_floating_allowance"]
    delta = cm[key] - bm[key]
    observed = "unchanged" if abs(delta) <= epsilon else "increase" if delta > 0 else "decrease"
    return {**result, "status": "NEAR_ZERO_OR_UNCHANGED" if observed == "unchanged" else "EVALUABLE",
            "delta": delta, "observed_sign": observed, "evaluable": observed != "unchanged", "prediction_matches": observed == sign}


def inspect_call(audit, path, context, contract):
    receipts, response, threads = [], None, []
    attempts = sorted(path.glob("attempt*"))
    audit.check(str(path.name) + ":retry_cap", 1 <= len(attempts) <= 3)
    for number, folder in enumerate(attempts):
        receipt = read_json(folder / "receipt.json")
        request = read_json(folder / "input.json")
        events = [json.loads(line) for line in (folder / "visible_events.jsonl").read_text().splitlines()]
        audit.check("call:live_classification", receipt["classification"] == "LIVE_CALL_ATTEMPT")
        audit.check("call:input_hash", digest(folder / "input.json") == receipt["input_sha256"])
        audit.check("call:events_hash", digest(folder / "visible_events.jsonl") == receipt["events_sha256"])
        audit.check("call:exact_prompt_context", request["prompt"] == PROMPT_TEMPLATE + "\n" + json.dumps(context, ensure_ascii=False, separators=(",", ":")))
        audit.check("call:model_configuration", receipt["requested_model"] == contract["modes"]["common_model"]["model"] and receipt["reasoning_effort"] == contract["modes"]["common_model"]["reasoning_effort"])
        audit.check("call:unknown_hidden_requests", receipt["underlying_requests"] == "unknown" and receipt["provider_request_ids"] == "unavailable")
        command = receipt["command"]
        audit.check("call:ephemeral_read_only", "--ephemeral" in command and "--ignore-user-config" in command and "--strict-config" in command
                    and command[command.index("--sandbox") + 1] == "read-only")
        for feature in ("shell_tool", "unified_exec", "code_mode_host", "apps", "plugins", "multi_agent", "hooks", "memories",
                        "shell_snapshot", "browser_use", "browser_use_external", "computer_use", "image_generation", "unbounded_connection_retries"):
            audit.check("call:disabled:" + feature, any(command[i:i + 2] == ["--disable", feature] for i in range(len(command) - 1)))
        audit.check("call:no_tools_observed", not any(event["type"] in ("unexpected_tool", "unexpected_event") for event in events))
        starts = [event["thread_id"] for event in events if event["type"] == "thread.started"]
        completed = [event for event in events if event["type"] == "turn.completed"]
        finals = [event["item"]["text"] for event in events if event["type"] == "item.completed" and event.get("item", {}).get("type") == "agent_message"]
        audit.check("call:completed_count", receipt["completed_turns"] == len(completed))
        if receipt["status"] == "VERIFIED_STRUCTURE_ONLY":
            audit.check("call:one_complete_response", len(starts) == len(completed) == len(finals) == 1 and receipt["exit_code"] == 0)
            response = read_json(folder / "response.json")
            audit.check("call:response_hash", digest(folder / "response.json") == receipt["response_sha256"])
            audit.same("call:actual_visible_response", json.loads(finals[0]), response)
            audit.same("call:actual_visible_usage", receipt["usage"], completed[0]["usage"])
            audit.check("call:actual_thread", receipt["thread_id"] == starts[0])
            audit.check("call:success_is_last_attempt", number == len(attempts) - 1)
        elif number < len(attempts) - 1:
            error = json.dumps(receipt).lower()
            audit.check("call:only_transient_retry", any(word in error for word in ("timeout", "timed out", "rate_limit", "rate limit", "429", "temporarily unavailable", "service unavailable", "connection reset", "connect error", "502", "503", "504"))
                        and not any(word in error for word in ("authentication", "unauthorized", "billing", "invalid_structured_response", "unexpected_tool")))
        else:
            audit.check("call:unusable_answer_not_fabricated", "invalid_structured_response" in json.dumps(receipt).lower() or "missing_or_ambiguous_final_event" in json.dumps(receipt).lower())
        receipts.append(receipt)
        threads.extend(starts)
    return response, receipts, threads


def validate_structure(response, active, round_number, mode):
    if not isinstance(response, dict) or not isinstance(response.get("records"), list):
        return {}
    rows = response["records"]
    ids = [row.get("record_id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or len(ids) != len(set(ids)) or set(ids) != set(active):
        return {}
    result = {}
    for row in rows:
        proposals = row.get("proposals")
        limit = 1 if mode == "llm-only" or round_number == 1 else 2
        if not isinstance(proposals, list) or len(proposals) > limit or round_number == 1 and len(proposals) != 1 or not proposals and not row.get("stop"):
            continue
        names = [p.get("candidate_id") for p in proposals if isinstance(p, dict)]
        if len(names) != len(proposals) or len(names) != len(set(names)):
            continue
        result[row["record_id"]] = row
    return result


def inspect_episode(manifest, episode_path, shared):
    contract, split, cards, raw, coords, memory_snapshot, memory_hash = shared
    audit = Audit()
    episode_hash = digest(episode_path)
    episode = read_json(episode_path)
    directory = episode_path.parent
    ids, mode = episode["input_ids"], episode["mode"]
    partition_name = manifest["partition"]
    ref_params = contract["reference_parameters"]
    refid = config_id(ref_params)
    fixed_ids = split["llm_subsets"][partition_name]
    offset = fixed_ids.index(ids[0])
    audit.check("episode:canonical_fixed_batch", offset % 8 == 0 and ids == fixed_ids[offset:offset + 8])
    audit.check("episode:identity", episode["episode_id"] == f'{partition_name}-{mode}-e{episode["episode"]}-b{offset // 8}')
    audit.check("episode:version", episode["contract_sha256"] == manifest["contract_sha256"] and episode["source_tree_sha256"] == manifest["source_tree_sha256"])
    audit.check("episode:classification", episode["classification"] == ("DETERMINISTIC_ZERO_MODEL_SEARCH" if mode == "search-only" else "LIVE_EXPERIMENT"))
    audit.check("episode:work_memory_reset", episode["working_memory_reset_at_episode_start"] is True and episode["working_memory_persisted_for_next_episode"] is False)
    audit.same("episode:row_scope", [row["record_id"] for row in episode["records"]], ids)
    for path, value in episode["artifact_hashes"].items():
        audit.check("episode:artifact_hash:" + path, digest(directory / path) == value)
    actual_files = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file() and p != episode_path}
    audit.check("episode:complete_file_manifest", actual_files == set(episode["artifact_hashes"]))
    traces = {rid: read_compressed(directory / f"{rid}_candidate_traces.json.gz") for rid in ids}
    row_by_id = {row["record_id"]: row for row in episode["records"]}
    states = {rid: {"schedule": {}, "stopped": False, "proposals": [], "cache_reads": 0, "rounds": 0} for rid in ids}
    for rid in ids:
        row = row_by_id[rid]
        audit.check("row:identity", row["mode"] == mode and row["episode_id"] == episode["episode_id"] and row["partition"] == partition_name and row["episode"] == episode["episode"])
        for cid, target in traces[rid]["results"].items():
            audit.check("candidate:id", cid == config_id(target["parameters"]))
            ok, _ = legality(target["parameters"], contract["parameter_grids"])
            audit.check("candidate:legal_domain", ok)
            provenance = {"goal_id": contract["goal_id"], "run_id": manifest["run_id"], "raw_sha256": split["raw_sha256"], "partition": partition_name,
                          "scope_sha256": object_hash([rid]), "source_tree_sha256": manifest["source_tree_sha256"], "contract_sha256": manifest["contract_sha256"],
                          "split_sha256": manifest["split_sha256"], "adapter_version": contract["model"]["adapter_version"], "episode_id": episode["episode_id"]}
            record_check(audit, target, raw[rid], target["parameters"], "S-D-P", manifest["contract_sha256"], provenance, coords[rid])
            receipt = traces[rid]["reviews"][cid]
            audit.check("candidate:independent_review_target", receipt["status"] == "VERIFIED" and receipt["target_hash"] == object_hash(target)
                        and receipt["trusted_reference_hash"] == object_hash(target["source_record"]))
            audit.same("candidate:reported_metrics", row["candidate_metrics"][cid], compact(target["metrics"]))
        audit.same("candidate:complete_reviews", sorted(traces[rid]["reviews"]), sorted(traces[rid]["results"]))

    def add(rid, parameters):
        cid = config_id(parameters)
        if cid in states[rid]["schedule"]:
            states[rid]["cache_reads"] += 1
        else:
            states[rid]["schedule"][cid] = parameters

    calls, threads, outputs, memory_consumption = [], [], [], []
    sequence = [row["parameters"] for row in contract["search"]["sequence"]]
    if mode == "search-only":
        audit.check("search_only:no_call_artifacts", not list(directory.glob("round*_call")) and not list(directory.glob("round*_context.json")))
        for rid in ids:
            for parameters in sequence:
                add(rid, parameters)
    else:
        retrievals = read_json(directory / "memory_retrieval.json")
        if mode != "llm+memory+search":
            audit.same("nonmemory:no_retrievals", retrievals, {})
        else:
            audit.check("memory:same_frozen_hash", episode["snapshot_after"] == memory_hash)
            demo = {entry["memory_id"]: entry for entry in memory_snapshot["entries"]}
            for rid in ids:
                retrieval = retrievals[rid]
                audit.check("memory:retrieval_version", retrieval["snapshot_sha256"] == memory_hash and retrieval["query_record_id"] == rid)
                eligible = []
                query_features = independent_features(cards[rid])
                for entry in demo.values():
                    if entry["record_id"] == rid or entry["record_content_sha256"] == cards[rid]["record_content_sha256"] or entry["stratum"] != cards[rid]["stratum"] or query_features is None or entry["features"] is None:
                        continue
                    distance = math.sqrt(sum(((a - b) / (scale["max"] - scale["min"])) ** 2 if scale["max"] != scale["min"] else 0
                                             for a, b, scale in zip(query_features, entry["features"], memory_snapshot["feature_scales"])))
                    eligible.append((distance, entry["memory_id"]))
                eligible.sort()
                audit.same("memory:exact_applicable_ids", [e["memory_id"] for e in retrieval["delivered"]], [mid for _, mid in eligible[:3]])
                audit.check("memory:eligible_count", retrieval["eligible_count"] == len(eligible))
                for entry in retrieval["delivered"]:
                    audit.same("memory:actual_delivered_content", {k: v for k, v in entry.items() if k != "retrieval_distance"}, demo[entry["memory_id"]])
        context_files = sorted(directory.glob("round*_context.json"))
        audit.check("model:round_cap", 1 <= len(context_files) <= (1 if mode == "llm-only" else 3))
        for round_number, path in enumerate(context_files, 1):
            context = read_json(path)
            active = [rid for rid in ids if not states[rid]["stopped"]]
            audit.check("round:sequence", path.name == f"round{round_number}_context.json" and context["decision_round"] == round_number)
            audit.check("round:mode_episode", context["mode"] == mode and context["episode_id"] == episode["episode_id"])
            audit.same("round:active_scope", [r["card"]["record_id"] for r in context["records"]], active)
            audit.same("round:own_consumed_budget", context["evaluations_already_consumed"], {rid: len(states[rid]["schedule"]) for rid in active})
            for observed in context["records"]:
                rid = observed["card"]["record_id"]
                handle = object_hash({"raw_sha256": split["raw_sha256"], "record_id": rid, "parameters": ref_params,
                                      "source_tree_sha256": manifest["source_tree_sha256"], "contract_sha256": manifest["contract_sha256"]})
                audit.same("round:raw_diagnostic_only", observed["card"], {**{key: cards[rid][key] for key in CARD_FIELDS}, "reference_handle": handle})
                audit.check("round:reference_handle", row_by_id[rid]["reference_handle"] == handle)
                if round_number == 1:
                    audit.check("round1:no_scoring_feedback", "own_candidate_feedback" not in observed and "own_prior_proposal_validation" not in observed)
                else:
                    audit.same("round:feedback_scope", [f["config_id"] for f in observed["own_candidate_feedback"]], list(states[rid]["schedule"]))
                    for feedback in observed["own_candidate_feedback"]:
                        target = traces[rid]["results"][feedback["config_id"]]
                        audit.same("round:feedback_actual_metrics", feedback["metrics"], compact(target["metrics"]))
                        audit.same("round:feedback_actual_parameters", feedback["parameters"], target["parameters"])
                        audit.check("round:feedback_own_record", feedback["selection_assessment"]["record_id"] == rid)
                    audit.same("round:feedback_prior_proposals", observed["own_prior_proposal_validation"], states[rid]["proposals"])
                if mode == "llm+memory+search":
                    delivered = retrievals[rid]["delivered"]
                    audit.same("round:delivered_memory_ids", [r["memory_id"] for r in observed["demonstration_memory"]], [r["memory_id"] for r in delivered])
                    for shown, entry in zip(observed["demonstration_memory"], delivered):
                        for key in ("memory_id", "record_id", "stratum", "selected_parameters", "research_status"):
                            audit.same("round:memory_field:" + key, shown[key], entry[key])
                        audit.same("round:memory_metrics", shown["verified_metrics"], {k: entry["selected_metrics"].get(k) for k in
                                   ("n_input", "n_final", "common_covered_points", "common_max_error", "dp_saving", "dp_max_error", "raw_break_crossings")})
                    audit.same("round:procedural_memory", observed["procedural_memory"], memory_snapshot["procedural_memory"])
                else:
                    audit.check("round:no_unauthorized_memory", "demonstration_memory" not in observed and "procedural_memory" not in observed)
            response, receipts, call_threads = inspect_call(audit, directory / f"round{round_number}_call", context, contract)
            calls.extend(receipts)
            threads.extend(call_threads)
            validation = read_json(directory / f"round{round_number}_validation.json")
            audit.same("round:original_unclamped_response", validation["original_response"], response)
            valid = validate_structure(response, active, round_number, mode)
            audit.same("round:accepted_structure_ids", validation["accepted_record_ids"], list(valid))
            for rid in active:
                state = states[rid]
                output = row_by_id[rid]
                rounds = [r for r in output["rounds"] if r["round"] == round_number]
                audit.check("round:exact_record_round", len(rounds) == 1)
                rd = rounds[0]
                audit.check("round:context_binding", rd["context_hash"] == object_hash(context))
                state["rounds"] += 1
                add(rid, ref_params)
                action = valid.get(rid)
                audit.same("round:raw_action", rd["raw_action"], action)
                actual_proposals = [p for p in output["proposal_records"] if p["round"] == round_number]
                if action is None:
                    audit.check("round:invalid_structure_accounted", len(actual_proposals) == 1 and not actual_proposals[0]["legal"] and not actual_proposals[0]["executed"])
                    state["proposals"].extend(actual_proposals)
                    state["stopped"] = mode == "llm-only"
                    continue
                audit.check("round:proposal_count", len(actual_proposals) == len(action["proposals"]))
                for original, actual in zip(action["proposals"], actual_proposals):
                    ok, reason = legality(original.get("parameters"), contract["parameter_grids"])
                    audit.same("proposal:preserve_original", actual["original"], original)
                    audit.check("proposal:raw_legality_and_execution", actual["legal"] == actual["executed"] == ok and actual["rejection_reason"] == reason)
                    audit.check("proposal:preexecution_reference", actual["reference_handle_locked_before_execution"] == output["reference_handle"])
                    if ok:
                        cid = config_id(original["parameters"])
                        add(rid, original["parameters"])
                        audit.check("proposal:actual_config", actual["executed_config_id"] == cid)
                        audit.same("proposal:prediction", actual["prediction"], prediction(original, traces[rid]["results"][cid], traces[rid]["results"][refid]))
                    state["proposals"].append(actual)
                if mode == "llm+memory+search":
                    delivered = {entry["memory_id"]: entry for entry in retrievals[rid]["delivered"]}
                    cited = action["memory_ids_used"]
                    consumption = rd["memory_consumption"]
                    audit.same("memory:valid_citations", consumption["model_cited_valid"], [mid for mid in cited if mid in delivered])
                    audit.same("memory:invalid_citations", consumption["model_cited_invalid"], [mid for mid in cited if mid not in delivered])
                    matched = [{"memory_id": mid, "candidate_id": p["candidate_id"], "kind": "CITED_AND_PARAMETERS_MATCH_VERIFIED_OUTCOME"}
                               for mid in cited if mid in delivered for p in action["proposals"] if p["parameters"] == delivered[mid]["selected_parameters"]]
                    audit.same("memory:action_consistency", consumption["action_consistent"], matched)
                    audit.check("memory:not_causal_quality_claim", consumption["causal_benefit_proven"] is False)
                    memory_consumption.append({"record_id": rid, "round": round_number, "delivered": list(delivered), "cited": cited,
                                               "matched": matched, "actual_reasons": [p["reason"] for p in action["proposals"]]})
                if mode != "llm-only" and not action["stop"]:
                    budget = {1: 8, 2: 14, 3: 20}[round_number]
                    for parameters in sequence:
                        if len(state["schedule"]) >= budget:
                            break
                        if config_id(parameters) not in state["schedule"]:
                            add(rid, parameters)
                state["stopped"] = bool(action["stop"]) or mode == "llm-only"
                audit.same("round:actual_frozen_fill_schedule", rd["candidate_ids_after"], list(state["schedule"]))
            checkpoint = read_json(directory / f"round{round_number}_checkpoint.json")
            audit.check("round:feedback_chronology", all(receipt["ended_at"] <= checkpoint["completed_at"] for receipt in receipts))
    decimal_samples = []
    for rid in ids:
        state, row, saved = states[rid], row_by_id[rid], traces[rid]
        audit.same("row:exact_candidate_schedule", row["candidate_ids"], list(state["schedule"]))
        audit.same("row:complete_trace_scope", sorted(saved["results"]), sorted(state["schedule"]))
        audit.check("row:budget", len(state["schedule"]) <= (2 if mode == "llm-only" else 20))
        selected = independent_select(saved["results"], refid)
        fallback = False
        if mode == "llm-only":
            executed = [p["executed_config_id"] for p in row["proposal_records"] if p["executed"]]
            selected = executed[0] if executed and not saved["results"][executed[0]]["metrics"]["raw_break_crossings"] else refid
            fallback = not executed or bool(saved["results"][executed[0]]["metrics"]["raw_break_crossings"])
        audit.check("row:independent_selection", row["selected_config_id"] == selected and row["fallback"] == fallback)
        audit.same("row:selected_actual_parameters", row["selected_parameters"], saved["results"][selected]["parameters"])
        audit.same("row:reference_actual_metrics", row["reference_metrics"], compact(saved["results"][refid]["metrics"]))
        audit.same("row:selected_actual_metrics", row["selected_metrics"], compact(saved["results"][selected]["metrics"]))
        lock = read_json(directory / f"{rid}_lock.json")
        audit.check("row:lock_binding", lock["selected_config_id"] == selected and lock["candidate_ids"] == row["candidate_ids"] and lock["fallback"] == fallback)
        audit.check("row:no_call_after_lock", all(call["ended_at"] <= lock["selected_at"] for call in calls))
        audit.check("row:post_lock_target", saved["post_lock_review"]["status"] == row["engineering_status"] == "VERIFIED" and saved["post_lock_review"]["target_hash"] == object_hash(saved["results"][selected]))
        audit.same("row:resources", row["resources"], {"unique_candidate_evaluations": len(state["schedule"]), "decision_proposals": sum("original" in p for p in row["proposal_records"]),
                   "cache_reads": state["cache_reads"], "decision_rounds": state["rounds"], "reference_scored": True})
        audit.check("row:memory_hash", row["memory_snapshot_hash"] == (memory_hash if mode == "llm+memory+search" else None))
        for cid in sorted({selected, refid}):
            target = saved["results"][cid]
            result = audit_record(target, raw[rid], target["parameters"], "S-D-P", contract["model"], manifest["contract_sha256"])
            audit.check("row:selected_reference_Decimal_reconstruction", result["status"] == "VERIFIED", result["errors"])
            decimal_samples.append({"record_id": rid, "config_id": cid, "status": result["status"], "checks": result["checks"]})
        outputs.append({"record_id": rid, "proposals": row["proposal_records"], "candidate_count": len(state["schedule"]), "selected": selected, "fallback": fallback})
    resources = episode["resources"]
    candidate_count = sum(len(s["schedule"]) for s in states.values())
    audit.check("resources:model_dispatches", resources["experiment_model_dispatches"] == len(calls))
    audit.check("resources:completed_turns", resources["completed_model_turns"] == sum(call["completed_turns"] for call in calls))
    audit.check("resources:candidates", resources["candidate_evaluations"] == candidate_count)
    audit.check("resources:deterministic_calls", resources["deterministic_tool_calls"] == 2 * candidate_count + len(ids))
    audit.check("resources:cache_reads", resources["cache_reads"] == sum(s["cache_reads"] for s in states.values()))
    audit.check("resources:governance_separate", resources["governance_role_dispatches"] == 0 and resources["provider_requests"] == "unknown")
    audit.check("episode:unchanged_target", digest(episode_path) == episode_hash)
    return {"status": "REJECTED" if audit.errors else "VERIFIED", "episode_id": episode["episode_id"], "target_sha256": episode_hash,
            "check_count": audit.check_count, "errors": audit.errors, "mode": mode, "episode": episode["episode"], "input_ids": ids,
            "calls": [{"request_id": r["request_id"], "thread_id": r.get("thread_id"), "status": r["status"], "usage": r.get("usage"),
                       "started_at": r["started_at"], "ended_at": r["ended_at"]} for r in calls], "thread_ids": threads,
            "candidate_evaluations": candidate_count, "record_results": outputs, "memory_consumption": memory_consumption,
            "independent_Decimal_reconstructions": decimal_samples, "new_model_calls_in_review": 0}


def review(run_id, output_name, episode_name=None):
    started = time.perf_counter()
    output = OUT / output_name
    if output.exists():
        raise ValueError("C_REVIEW_EXISTS_NO_OVERWRITE")
    run = EV / "runs" / run_id
    manifest_path = run / "manifest.json"
    manifest = read_json(manifest_path)
    if episode_name is None and manifest["status"] != "REVIEW_PENDING":
        raise ValueError("RUN_NOT_COMPLETE_NO_TASK_ACCEPTANCE")
    contract, split, cards = read_json(CFG / "contract.json"), read_json(EV / "data/split_manifest.json"), read_json(EV / "data/raw_diagnostics.json")
    raw = read_json(ROOT / contract["raw_path"])
    master = Audit()
    master.check("raw_hash", digest(ROOT / contract["raw_path"]) == contract["raw_sha256"] == manifest["raw_sha256"])
    master.check("parent_versions", digest(CFG / "contract.json") == manifest["contract_sha256"] and digest(EV / "data/split_manifest.json") == manifest["split_sha256"])
    for path, expected in manifest["source_hashes"].items():
        master.check("source:" + path, digest(ROOT / path) == expected)
    current = read_json(EV / "current_runs.json")
    memory_run = EV / "runs" / current["memory"]
    memory_info = read_json(memory_run / "manifest.json")["memory_snapshot"]
    memory_path = memory_run / memory_info["path"]
    memory_hash = digest(memory_path)
    master.check("frozen_memory_hash", memory_hash == memory_info["sha256"])
    memory_snapshot = read_json(memory_path)
    model = contract["model"]
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} +lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    ids = split["llm_subsets"][manifest["partition"]]
    coords = {rid: [transform.transform(*p, 0)[:2] for p in raw[rid][1]] for rid in ids}
    shared = contract, split, cards, raw, coords, memory_snapshot, memory_hash
    paths = [run / "modes" / episode_name / "episode.json"] if episode_name else [run / ref["path"] for ref in manifest["mode_episodes"]]
    episode_reports = []
    for path in paths:
        report = inspect_episode(manifest, path, shared)
        episode_reports.append(report)
        print(json.dumps({"C_live_review": report["episode_id"], "status": report["status"], "checks": report["check_count"], "errors": len(report["errors"])}), flush=True)
    threads = [thread for result in episode_reports for thread in result["thread_ids"]]
    master.check("distinct_ephemeral_model_threads", len(threads) == len(set(threads)))
    task = "development_modes" if manifest["partition"] == "DEVELOPMENT" else "evaluation_modes"
    if episode_name is None:
        repetitions = 1 if manifest["partition"] == "DEVELOPMENT" else 3
        expected = {(mode, episode, batch): ids[batch * 8:(batch + 1) * 8] for mode in MODES for episode in range(1, repetitions + 1) for batch in range(3)}
        observed = {(row["mode"], row["episode"], ids.index(row["input_ids"][0]) // 8): row["input_ids"] for row in episode_reports}
        master.check("complete_mode_scope_and_repetitions", observed == expected and len(episode_reports) == len(expected))
        for ref, path in zip(manifest["mode_episodes"], paths):
            master.check("episode_reference_hash", ref["sha256"] == digest(path))
        master.check("manifest_model_count", manifest["experiment_model_dispatches"] == sum(len(row["calls"]) for row in episode_reports))
        master.check("manifest_candidate_count", manifest["candidate_evaluations"] == sum(row["candidate_evaluations"] for row in episode_reports))
    master.check("memory_readonly_hash_after", digest(memory_path) == memory_hash)
    targets = [manifest_path] if episode_name is None else paths
    receipt = {"status": "VERIFIED" if not master.errors and all(r["status"] == "VERIFIED" for r in episode_reports) else "REJECTED",
               "role_context": "/root/c_contract", "task": task if episode_name is None else None,
               "classification": "COMPLETE_C_MODE_REVIEW" if episode_name is None else "PARTIAL_C_EPISODE_REVIEW_NOT_TASK_ACCEPTANCE",
               "run_id": run_id, "at": now(), "targets": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in targets],
               "source_hashes": {path: digest(ROOT / path) for path in task_sources(task)},
               "checked_components": REQUIRED_COMPONENTS[task] + ["raw_response_binding", "unclamped_proposal_legality", "frozen_search_schedule", "actual_feedback_provenance", "final_lock_no_feedback", "full_candidate_common_reference_and_ledger", "selected_reference_Decimal_reconstruction"],
               "unchecked_components": ["hidden_provider_request_count", "source_datum_truth", "ground_truth_quality", "causal_memory_benefit", "full_goal_acceptance"],
               "errors": master.errors, "check_count": master.check_count + sum(r["check_count"] for r in episode_reports),
               "episode_reports": episode_reports, "new_model_calls_in_review": 0, "elapsed_seconds": time.perf_counter() - started,
               "audit_program": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))}}
    write_json(output, receipt, exclusive=True)
    print(json.dumps({key: receipt[key] for key in ("status", "classification", "check_count", "elapsed_seconds")}), flush=True)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("output_name")
    parser.add_argument("--episode")
    args = parser.parse_args()
    result = review(args.run_id, args.output_name, args.episode)
    raise SystemExit(0 if result["status"] == "VERIFIED" else 1)
