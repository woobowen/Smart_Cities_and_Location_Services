"""C-only full heldout deterministic audit; never chooses a new candidate."""
import argparse
import json
from pathlib import Path
import sys
import time

import pyproj

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import (Audit, read_compressed, record_check, summary_expected,
                                     sample_ids, config_id, SAMPLE_RULE)
from independent_numeric import audit_record
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS

EV = ROOT / "task1/evidence/goal2"
CFG = ROOT / "task1/config/goal2"
OUT = Path(__file__).parent


def review(kind, run_id, output):
    start = time.perf_counter()
    run = EV / "runs" / run_id
    manifest_path = run / "manifest.json"
    manifest_hash = digest(manifest_path)
    manifest = read_json(manifest_path)
    if manifest["status"] != "REVIEW_PENDING" or manifest["partition"] != "G2_EVAL":
        raise ValueError("COMPLETE_G2_EVAL_RUN_REQUIRED")
    freeze_path = EV / "evaluation_freeze.json"
    freeze_hash, freeze = digest(freeze_path), read_json(freeze_path)
    contract, split, matrix, cards = [read_json(p) for p in (CFG / "contract.json", EV / "data/split_manifest.json", CFG / "experiment_matrix.json", EV / "data/raw_diagnostics.json")]
    audit = Audit()
    audit.check("locked_before_evaluation", freeze["status"] == "LOCKED_BEFORE_G2_EVAL" and freeze["frozen_at"] <= manifest["started_at"])
    audit.check("unmodified_candidate_lock", digest(EV / "candidate_lock.json") == freeze["candidate_lock_sha256"])
    audit.check("freeze_contract_split", digest(CFG / "contract.json") == freeze["contract_sha256"] == manifest["contract_sha256"]
                and digest(EV / "data/split_manifest.json") == freeze["split_sha256"] == manifest["split_sha256"])
    ids = split["splits"]["G2_EVAL"]
    audit.same("locked_complete_scope", manifest["input_ids"], ids)
    audit.same("same_evaluation_ids", freeze["eval_ids"], ids)
    audit.check("conditional_scope", manifest["classification"] == "CURRENT_RUN_CONDITIONAL_ANALYSIS" and manifest["source_crs"] == "UNVERIFIED")
    expected_source = {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / "task1/workflow").glob("*.py")}
    expected_source["task1/scripts/goal2.py"] = digest(ROOT / "task1/scripts/goal2.py")
    audit.same("exact_code_epoch", manifest["source_hashes"], expected_source)
    audit.same("same_frozen_code_epoch", freeze["processing_source_hashes"], expected_source)
    audit.check("source_tree_hash", manifest["source_tree_sha256"] == object_hash(expected_source))
    raw_path = ROOT / contract["raw_path"]
    audit.check("trusted_raw_hash", digest(raw_path) == contract["raw_sha256"] == manifest["raw_sha256"])
    raw = read_json(raw_path)
    model = contract["model"]
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} +lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    coords = {rid: [transform.transform(*p, 0)[:2] for p in raw[rid][1]] for rid in ids}
    configs = {r["config_id"]: r["parameters"] for r in matrix["parameter_configurations"]}
    if kind == "parameters":
        selected = set(freeze["representative_config_ids"]) | {r["config_id"] for r in freeze["selected_single_candidates"].values()}
        expected = {(cid, "S-D-P"): configs[cid] for cid in selected}
        task, table_name = "evaluation_parameters", "evaluation_table.json"
    else:
        expected = {(config_id(contract["reference_parameters"]), order): contract["reference_parameters"] for order in freeze["orders"]}
        task, table_name = "evaluation_orders", "order_table.json"
    entries = list(manifest["artifacts"].values())
    audit.check("complete_frozen_configs", len(entries) == len(expected) and {(e["config_id"], e["order"]) for e in entries} == set(expected))
    provenance = {"goal_id": contract["goal_id"], "run_id": run_id, "raw_sha256": split["raw_sha256"], "partition": "G2_EVAL", "scope_sha256": object_hash(ids),
                  "source_tree_sha256": manifest["source_tree_sha256"], "contract_sha256": manifest["contract_sha256"], "split_sha256": manifest["split_sha256"], "adapter_version": model["adapter_version"]}
    reports, summaries, order_details = [], [], {}
    for entry in entries:
        parameters = expected[(entry["config_id"], entry["order"])]
        path, receipt_path = run / entry["file"], run / entry["review_file"]
        audit.check("artifact_and_review_hash", digest(path) == entry["sha256"] and digest(receipt_path) == entry["review_sha256"])
        batch, receipt = read_compressed(path), read_json(receipt_path)
        audit.check("review_target", receipt["status"] == entry["engineering_status"] == "VERIFIED" and receipt["target_hash"] == object_hash(batch))
        audit.same("entry_frozen_parameters", entry["parameters"], parameters)
        audit.same("entry_full_scope", entry["input_ids"], ids)
        audit.same("batch_full_scope", batch["record_scope"], ids)
        audit.same("record_full_scope", [r["record_id"] for r in batch["records"]], ids)
        audit.same("receipt_full_scope", [r["record_id"] for r in receipt["record_receipts"]], ids)
        audit.same("batch_provenance", batch["provenance"], provenance)
        audit.check("batch_raw_input_hash", batch["input_hash"] == object_hash([r["source_record"] for r in batch["records"]]))
        key = object_hash({"raw": split["raw_sha256"], "scope": ids, "code": manifest["source_tree_sha256"], "contract": manifest["contract_sha256"], "config": parameters, "order": entry["order"]})
        audit.check("experiment_key", entry["experiment_key"] == key and manifest["artifacts"].get(key) == entry)
        samples = sample_ids(batch["records"], parameters, cards, parameters == contract["reference_parameters"] or kind == "orders")
        rows, details, sampled = [], {}, []
        for target, record_receipt in zip(batch["records"], receipt["record_receipts"]):
            rid = target["record_id"]
            audit.check("record_review_target", record_receipt["status"] == "VERIFIED" and record_receipt["target_hash"] == object_hash(target)
                        and record_receipt["trusted_reference_hash"] == object_hash(target["source_record"]))
            result = record_check(audit, target, raw[rid], parameters, entry["order"], manifest["contract_sha256"], provenance, coords[rid])
            rows.append(result["metrics"])
            details[rid] = result
            if rid in samples:
                numerical = audit_record(target, raw[rid], parameters, entry["order"], model, manifest["contract_sha256"])
                audit.check("sampled_Decimal_full_DP_reconstruction", numerical["status"] == "VERIFIED", numerical["errors"])
                sampled.append({"record_id": rid, "selection_reasons": samples[rid], "checks": numerical["checks"], "status": numerical["status"]})
        summary = summary_expected(rows)
        audit.same("independent_full_aggregation", batch["summary"], summary, max(row["epsilon"] for row in details.values()))
        audit.same("manifest_summary", entry["summary"], batch["summary"])
        summaries.append({"config_id": entry["config_id"], "order": entry["order"], "independent_summary": summary})
        reports.append({"config_id": entry["config_id"], "order": entry["order"], "records_checked": len(ids), "sampled_DP_reconstructions": sampled})
        if kind == "orders":
            order_details[entry["order"]] = details
        print(json.dumps({"C_evaluation_audit": kind, "config_id": entry["config_id"], "order": entry["order"], "errors": len(audit.errors)}), flush=True)
    safety = {}
    if kind == "orders":
        baseline = order_details["S-D-P"]
        for order, rows in order_details.items():
            failures = [rid for rid, row in rows.items() if row["crossings"] or not set(baseline[rid]["covered"]) <= set(row["covered"])
                        or row["metrics"]["raw_windows_covered"] < baseline[rid]["metrics"]["raw_windows_covered"]
                        or baseline[rid]["metrics"]["record_covered"] and not row["metrics"]["record_covered"]]
            safety[order] = {"failing_records": failures, "engineering_correctness_distinct_from_outcome": True}
    table_path = run / table_name
    audit.check("table_hash", digest(table_path) == manifest["tables"][table_name])
    audit.same("full_table_entries", read_json(table_path), entries)
    audit.check("candidate_budget_count", manifest["candidate_evaluations"] == len(ids) * len(entries))
    audit.check("zero_model_count", manifest["experiment_model_dispatches"] == 0)
    audit.check("instrumented_candidate_tool_count", manifest["deterministic_tool_calls"] == 2 * len(entries))
    audit.check("read_only_targets_and_freeze", digest(manifest_path) == manifest_hash and digest(freeze_path) == freeze_hash)
    result = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": task, "run_id": run_id,
              "at": now(), "targets": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in (manifest_path, table_path, freeze_path)],
              "source_hashes": {p: digest(ROOT / p) for p in task_sources(task)},
              "checked_components": REQUIRED_COMPONENTS[task] + ["full_hash_scope_ledger", "independent_common_reference_denominators", "all_P_certificates", "sampled_full_Decimal_reconstruction"],
              "unchecked_components": ["ground_truth_quality", "full_recursive_DP_reconstruction_for_every_record_configuration", "full_Goal2_acceptance"],
              "check_count": audit.check_count, "errors": audit.errors, "record_configurations": len(entries) * len(ids),
              "artifact_reviews": reports, "independent_summaries": summaries, "order_safety": safety,
              "sampling_rule": SAMPLE_RULE, "new_model_calls": 0, "no_evaluation_reselection": True,
              "audit_program": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))},
              "elapsed_seconds": time.perf_counter() - start}
    write_json(OUT / output, result, exclusive=True)
    print({key: result[key] for key in ("status", "check_count", "record_configurations", "elapsed_seconds")}, flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("parameters", "orders"))
    parser.add_argument("run_id")
    parser.add_argument("output")
    args = parser.parse_args()
    result = review(args.kind, args.run_id, args.output)
    raise SystemExit(result["status"] != "VERIFIED")
