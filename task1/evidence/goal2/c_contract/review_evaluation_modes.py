"""Independent C heldout mode review anchored to the previously verified freeze.

Uses the unchanged, hash-bound episode oracle from development, with explicit
freeze-parent, scope, memory, prompt/provider/code and three-episode checks.
"""
import argparse
import json
from pathlib import Path
import sys
import time

import pyproj

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_live_modes_epoch02 import inspect_episode, PROMPT_TEMPLATE, MODES
from review_development_runs import Audit
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS

EV = ROOT / "task1/evidence/goal2"
CFG = ROOT / "task1/config/goal2"
OUT = Path(__file__).parent


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def review(run_id, output_name, episode_name=None):
    started = time.perf_counter()
    output = OUT / output_name
    if output.exists():
        raise ValueError("C_REVIEW_EXISTS_NO_OVERWRITE")
    directory = EV / "runs" / run_id
    manifest_path = directory / "manifest.json"
    manifest_hash, manifest = digest(manifest_path), read_json(manifest_path)
    if manifest["partition"] != "G2_EVAL" or episode_name is None and manifest["status"] != "REVIEW_PENDING":
        raise ValueError("HELDOUT_COMPLETE_RUN_REQUIRED_FOR_TASK_ACCEPTANCE")
    audit = Audit()
    freeze_path = EV / "evaluation_freeze.json"
    freeze_hash, freeze = digest(freeze_path), read_json(freeze_path)
    independent_parent_path = OUT / "evaluation_freeze_epoch02_receipt.json"
    independent_parent = read_json(independent_parent_path)
    trusted_target = [row for row in independent_parent["targets"] if row["path"] == str(freeze_path.relative_to(ROOT))]
    audit.check("freeze:previous_independent_parent", independent_parent["status"] == "VERIFIED" and independent_parent["role_context"] == "/root/c_contract"
                and len(trusted_target) == 1 and trusted_target[0]["sha256"] == freeze_hash)
    audit.check("freeze:status_and_time", freeze["status"] == "LOCKED_BEFORE_G2_EVAL" and freeze["frozen_at"] <= manifest["started_at"])
    audit.check("freeze:three_repetitions", freeze["evaluation_episodes"] == 3)
    audit.check("freeze:immutable_candidate_lock", digest(EV / "candidate_lock.json") == freeze["candidate_lock_sha256"])
    contract, split, cards = [read_json(path) for path in (CFG / "contract.json", EV / "data/split_manifest.json", EV / "data/raw_diagnostics.json")]
    audit.check("freeze:contract_split", digest(CFG / "contract.json") == freeze["contract_sha256"] == manifest["contract_sha256"]
                and digest(EV / "data/split_manifest.json") == freeze["split_sha256"] == manifest["split_sha256"])
    audit.same("freeze:complete120", manifest["input_ids"], freeze["eval_ids"])
    audit.same("freeze:split120", split["splits"]["G2_EVAL"], freeze["eval_ids"])
    ids = freeze["eval_llm_ids"]
    audit.check("freeze:120_and24_unique", len(freeze["eval_ids"]) == len(set(freeze["eval_ids"])) == 120 and len(ids) == len(set(ids)) == 24 and set(ids) <= set(freeze["eval_ids"]))
    audit.same("freeze:fixed24", split["llm_subsets"]["G2_EVAL"], ids)
    audit.check("freeze:partition_isolation", not set(ids) & (set(split["splits"]["DEMO_MEMORY"]) | set(split["splits"]["DEVELOPMENT"]) | set(split["splits"]["G3_RESERVED"])))
    audit.check("freeze:exact_prompt", object_hash(PROMPT_TEMPLATE) == freeze["prompt_template_sha256"])
    for path, key in ((ROOT / "task1/workflow/g2_modes.py", "mode_implementation_sha256"), (ROOT / "task1/workflow/g2_provider.py", "provider_implementation_sha256")):
        audit.check("freeze:" + key, digest(path) == freeze[key])
    sources = {str(path.relative_to(ROOT)): digest(path) for path in (ROOT / "task1/workflow").glob("*.py")}
    sources["task1/scripts/goal2.py"] = digest(ROOT / "task1/scripts/goal2.py")
    audit.same("freeze:exact_processing_sources", freeze["processing_source_hashes"], sources)
    audit.same("run:actual_processing_sources", manifest["source_hashes"], sources)
    audit.check("run:source_tree", manifest["source_tree_sha256"] == object_hash(sources))
    current = read_json(EV / "current_runs.json")
    audit.check("freeze:all_development_dependencies", set(freeze["development_manifest_hashes"]) == {"parameter_development", "order_development", "memory", "mode_development"})
    for name, sha in freeze["development_manifest_hashes"].items():
        path = EV / "runs" / current[name] / "manifest.json"
        audit.check("freeze:dependency_hash:" + name, digest(path) == sha)
    memory_path = ROOT / freeze["memory_path"]
    memory_hash = digest(memory_path)
    memory_snapshot = read_json(memory_path)
    audit.check("freeze:memory_hash", memory_hash == freeze["memory_sha256"])
    memory_manifest = read_json(EV / "runs" / current["memory"] / "manifest.json")
    audit.check("freeze:memory_parent", (EV / "runs" / current["memory"] / memory_manifest["memory_snapshot"]["path"]).resolve() == memory_path.resolve()
                and memory_manifest["memory_snapshot"]["sha256"] == memory_hash)
    audit.check("freeze:DEMO_only_entries", {r["record_id"] for r in memory_snapshot["entries"]} == set(split["splits"]["DEMO_MEMORY"])
                and all(r["partition"] == "DEMO_MEMORY" for r in memory_snapshot["entries"]))
    raw_path = ROOT / contract["raw_path"]
    audit.check("raw:trusted_hash", digest(raw_path) == contract["raw_sha256"] == freeze.get("raw_sha256", contract["raw_sha256"]) == manifest["raw_sha256"])
    raw = read_json(raw_path)
    model = contract["model"]
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} +lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    coords = {rid: [transform.transform(*point, 0)[:2] for point in raw[rid][1]] for rid in ids}
    shared = contract, split, cards, raw, coords, memory_snapshot, memory_hash
    expected = {f"G2_EVAL-{mode}-e{episode}-b{batch}": (mode, episode, ids[8 * batch:8 * (batch + 1)])
                for mode in MODES for episode in range(1, 4) for batch in range(3)}
    references = {Path(ref["path"]).parent.name: ref for ref in manifest.get("mode_episodes", [])}
    if episode_name is not None:
        if episode_name not in expected or episode_name not in references:
            raise ValueError("COMPLETE_REGISTERED_FROZEN_EPISODE_REQUIRED")
        names = [episode_name]
    else:
        audit.check("run:36_batches", len(manifest["mode_episodes"]) == 36 and set(references) == set(expected))
        audit.check("run:no_unregistered_episode_directories", {p.name for p in (directory / "modes").iterdir() if p.is_dir()} == set(expected))
        names = list(references)
    reports = []
    for name in names:
        ref = references[name]
        path = directory / ref["path"]
        audit.check("episode:registered_target_hash", digest(path) == ref["sha256"])
        result = inspect_episode(manifest, path, shared)
        reports.append(result)
        mode, episode, scope = expected[name]
        audit.check("episode:frozen_identity_scope", result["mode"] == mode and result["episode"] == episode and result["input_ids"] == scope)
        audit.check("episode:calls_after_freeze", all(call["started_at"] >= freeze["frozen_at"] for call in result["calls"]))
        print(json.dumps({"C_heldout_mode_audit": name, "status": result["status"], "checks": result["check_count"], "errors": len(result["errors"])}), flush=True)
    threads = [thread for report in reports for thread in report["thread_ids"]]
    audit.check("mode:fresh_independent_threads", len(threads) == len(set(threads)))
    if episode_name is None:
        audit.check("run:all_visible_model_dispatches", manifest["experiment_model_dispatches"] == sum(len(r["calls"]) for r in reports))
        audit.check("run:all_candidate_evaluations", manifest["candidate_evaluations"] == sum(r["candidate_evaluations"] for r in reports))
        physical_receipts = list((directory / "modes").glob("*/round*_call/attempt*/receipt.json"))
        audit.check("run:no_hidden_unregistered_attempt", len(physical_receipts) == manifest["experiment_model_dispatches"])
        audit.check("run:manifest_unchanged", digest(manifest_path) == manifest_hash)
    audit.check("freeze:unchanged_after_review", digest(freeze_path) == freeze_hash)
    audit.check("memory:unchanged_after_review", digest(memory_path) == memory_hash)
    targets = ([manifest_path] if episode_name is None else [directory / references[name]["path"] for name in names]) + [freeze_path, memory_path, independent_parent_path]
    result = {"status": "VERIFIED" if not audit.errors and all(r["status"] == "VERIFIED" for r in reports) else "REJECTED",
              "role_context": "/root/c_contract", "task": "evaluation_modes" if episode_name is None else None, "run_id": run_id,
              "classification": "COMPLETE_C_HELDOUT_MODE_REVIEW" if episode_name is None else "PARTIAL_C_HELDOUT_EPISODE_REVIEW",
              "at": now(), "targets": [bound(path) for path in targets], "source_hashes": {p: digest(ROOT / p) for p in task_sources("evaluation_modes")},
              "checked_components": REQUIRED_COMPONENTS["evaluation_modes"] + ["independently_verified_freeze_parent", "actual_prompt_memory_provider_processing_bindings", "raw_response_feedback_and_prediction", "complete_candidate_ledgers", "paired_original_record_unit"],
              "unchecked_components": ["hidden_provider_requests", "ground_truth_quality", "causal_memory_benefit", "full_Goal2_acceptance"],
              "check_count": audit.check_count + sum(r["check_count"] for r in reports), "errors": audit.errors, "episode_reports": reports,
              "freeze_sha256": freeze_hash, "memory_sha256": memory_hash, "no_evaluation_reselection": True,
              "statistical_unit": "original_record; three episodes are within-record repeated observations",
              "new_model_calls_in_review": 0, "elapsed_seconds": time.perf_counter() - started,
              "audit_program": bound(Path(__file__)), "unchanged_episode_oracle": bound(OUT / "review_live_modes_epoch02.py")}
    write_json(output, result, exclusive=True)
    print({key: result[key] for key in ("status", "classification", "check_count", "elapsed_seconds")}, flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("output_name")
    parser.add_argument("--episode")
    args = parser.parse_args()
    result = review(args.run_id, args.output_name, args.episode)
    raise SystemExit(result["status"] != "VERIFIED")
