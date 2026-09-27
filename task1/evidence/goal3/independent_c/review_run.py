"""Read-only C verification of a frozen G3 run from original raw inputs.

All traces are reconstructed with the pre-existing candidate-external G2 oracle.
The sampled stronger check uses the separate C-only Decimal/PROJ implementation.
That distinction is recorded explicitly in each receipt.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.g2_data import adapt
from task1.workflow.g2_metrics import review_record, summarize
from task1.evidence.goal2.c_contract.independent_numeric import audit_record

OUT = Path(__file__).resolve().parent


def hash_bytes(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def read(path):
    return json.loads(path.read_text())


def rank(group, salt="SC_LAB1_G3_C_RAW_RECHECK_V1"):
    return hashlib.sha256(("42|" + salt + "|" + group).encode()).hexdigest()


def independent_route(definition, raw_record):
    params = deepcopy(definition["parameters"])
    params["min_points"] = int(params["min_points"])
    if definition["conditional_rule"] is None:
        return params, "UNIFORM"
    assert definition["conditional_rule"]["rule_id"] == "TIME_REGULAR_DIRECTION60_V1"
    t = raw_record[0]
    valid = len(t) > 1 and all(type(x) in (int, float) and math.isfinite(x) for x in t)
    regular = valid and all(0 < right - left <= 30 for left, right in zip(t, t[1:]))
    params["direction"] = 60 if regular else 35
    return params, "TIME_REGULAR" if regular else "TIME_FLAGGED_OR_UNAVAILABLE"


def config_id(params):
    return "cfg-" + object_hash({k: float(v) for k, v in params.items()})[:16]


def close(a, b, tolerance=1e-10):
    if isinstance(b, dict):
        return isinstance(a, dict) and set(a) == set(b) and all(close(a[k], v, tolerance) for k, v in b.items())
    if isinstance(b, list):
        return isinstance(a, list) and len(a) == len(b) and all(close(x, y, tolerance) for x, y in zip(a, b))
    if type(b) is float:
        return type(a) in (int, float) and math.isfinite(a) and math.isclose(a, b, rel_tol=2e-12, abs_tol=tolerance)
    return type(a) is type(b) and a == b


def independent_pair(candidate, reference, p_only=False):
    c, b = candidate["metrics"], reference["metrics"]
    before = {x["index"]: x["error"] for x in b["common_point_errors"] if x["error"] is not None}
    after = {x["index"]: x["error"] for x in c["common_point_errors"] if x["error"] is not None}
    eps = max(c["common_floating_allowance"], b["common_floating_allowance"])
    windows_before = {x["reference_window"] for x in b["common_point_errors"] if x["error"] is not None}
    windows_after = {x["reference_window"] for x in c["common_point_errors"] if x["error"] is not None}
    base_max = max(before.values(), default=None)
    after_base = max((after[i] for i in before), default=None) if set(before) <= set(after) else None
    failures = []
    if not set(before) <= set(after): failures.append("COMMON_COVERED_IDENTITIES_LOST")
    if not windows_before <= windows_after: failures.append("RAW_WINDOW_IDENTITIES_LOST")
    if c["raw_windows_covered"] < b["raw_windows_covered"]: failures.append("RAW_WINDOW_COVERAGE_LOST")
    if b["record_covered"] and not c["record_covered"]: failures.append("RECORD_COVERAGE_LOST")
    if c["raw_break_crossings"]: failures.append("RAW_BREAKPOINT_CROSSED")
    if not c["dp_checks_passed"] or c["n_dp_exceedances"]: failures.append("DP_CONTRACT_FAILED")
    if c["dp_max_error"] is not None and c["dp_max_error"] > 5 + eps: failures.append("COMMON_DP_BUDGET_EXCEEDED")
    if not p_only and base_max is not None and (after_base is None or after_base > base_max + eps):
        failures.append("COMMON_GEOMETRIC_PROTECTION_DEGRADED")
    if p_only:
        p_before = next(s for s in reference["stages"] if s["name"] == "P")["input"]
        p_after = next(s for s in candidate["stages"] if s["name"] == "P")["input"]
        if p_before != p_after: failures.append("DP_REFERENCE_CHANGED")
        gain = c["n_dp_output"] < b["n_dp_output"]
    else:
        gain = len(after) > len(before) or (after_base is not None and base_max is not None and after_base < base_max - eps)
    return {"feasible": not failures, "strict_gain": bool(gain and not failures),
            "coverage_delta": len(after) - len(before),
            "candidate_max_on_baseline_covered": after_base,
            "protection_failures": sorted(set(failures))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--math-all", action="store_true", help="independent Decimal audit of every trace; development only by deliberate request")
    args = parser.parse_args()
    run = args.run.resolve()
    assert run.is_relative_to(ROOT)
    manifest_path = run / "manifest.json"
    manifest_hash = hash_bytes(manifest_path)
    manifest = read(manifest_path)
    contract_path = ROOT / "task1/config/goal3/contract.json"
    contract = read(contract_path)
    split = read(ROOT / "task1/evidence/goal3/split_manifest.json")
    raw_path = ROOT / contract["raw_path"]
    assert hash_bytes(raw_path) == contract["raw_sha256"]
    raw = read(raw_path)
    plan = read(ROOT / "task1/evidence/goal3/a_candidate_plan.json")
    definitions = {d["candidate_id"]: d for d in plan["candidate_definitions"]}
    partition = manifest["partition"]
    expected_ids = (sum(split["partitions"].values(), []) if partition == "FULL_PRODUCTION" else split["partitions"][partition])
    # Enforce C's information boundary even if directly invoked by a caller.
    if partition in ("FINAL_CONFIRM", "FULL_PRODUCTION"):
        frozen = read(ROOT / "task1/evidence/goal3/final_freeze.json")
        assert all(hash_bytes(ROOT / p) == h for p, h in frozen["bindings"].items())
    ids = manifest["strategy_ids"]
    problems, trace_reviews, decimal_reviews = [], 0, []
    def check(name, condition, detail=None):
        if not condition: problems.append({"check": name, "detail": detail})
    check("valid_terminal_run_status", manifest["status"] == "MACHINE_VERIFIED_PENDING_C")
    check("complete_exact_scope", manifest["input_ids"] == expected_ids == manifest["completed_record_ids"])
    check("no_processing_failures", not manifest["failed_records"])
    check("strategy_definitions", manifest["strategies"] == {cid: definitions[cid] for cid in ids})
    check("source_bindings", all(hash_bytes(ROOT / p) == h for p, h in manifest["bindings"].items()))
    check("partition_hash", manifest["provenance"]["scope_sha256"] == object_hash(expected_ids))
    check("contract_binding", manifest["provenance"]["contract_sha256"] == hash_bytes(contract_path))
    sample = set(expected_ids if args.math_all else sorted(expected_ids, key=lambda rid: (rank(split["group_for_record"][rid]), rid))[:40])
    scalars = {cid: [] for cid in ids}
    all_pairs, all_ppairs = defaultdict(list), defaultdict(list)
    observed_ids = []
    started = time.perf_counter()
    total_raw_points, fate_totals = 0, {cid: Counter() for cid in ids}
    for shard in manifest["shards"]:
        path = run / shard["path"]
        assert path.is_relative_to(run) and not path.is_symlink()
        check("shard_hash:" + shard["path"], hash_bytes(path) == shard["sha256"])
        shard_ids = []
        with gzip.open(path, "rt", encoding="utf8") as handle:
            for line in handle:
                row = json.loads(line)
                rid = row["record_id"]
                observed_ids.append(rid)
                shard_ids.append(rid)
                if rid not in raw:
                    problems.append({"check": "EXTRA_RAW_RECORD", "detail": rid})
                    continue
                total_raw_points += len(raw[rid][0])
                check("raw_record_hash:" + rid, row["raw_record_sha256"] == object_hash(raw[rid]))
                trusted = adapt(rid, raw[rid])
                expected_configs, expected_routes = {}, {}
                for cid in ids:
                    params, route = independent_route(definitions[cid], raw[rid])
                    cfg = config_id(params)
                    expected_configs[cid], expected_routes[cid] = cfg, route
                    target = row["traces"][cfg]
                    metrics = target["metrics"]
                    scalars[cid].append({"metrics": {k: v for k, v in metrics.items() if not isinstance(v, (dict, list))
                        or k in ("filter_reason_segments", "filter_reason_points", "direction_undefined_reasons")}})
                    fate_totals[cid].update(x["action"] for x in target["point_actions"])
                check("exact_configs_and_groups:" + rid, row["strategy_configs"] == expected_configs
                      and row["runtime_groups"] == expected_routes
                      and set(row["traces"]) == set(expected_configs.values()))
                for cfg, target in row["traces"].items():
                    cid = next(cid for cid in ids if expected_configs[cid] == cfg)
                    params, _ = independent_route(definitions[cid], raw[rid])
                    review = review_record(target, trusted, expected_parameters=params, expected_order="S-D-P",
                        contract_hash=hash_bytes(contract_path), trusted_provenance=manifest["provenance"])
                    trace_reviews += 1
                    check("external_raw_trace:" + rid + ":" + cfg, review["status"] == "VERIFIED", review["errors"])
                    stored = row["machine_reviews"][cfg]
                    check("actual_review_target:" + rid + ":" + cfg,
                          stored["status"] == "VERIFIED" and stored["target_hash"] == object_hash(target)
                          and stored["trusted_reference_hash"] == object_hash(trusted))
                    if rid in sample:
                        independent = audit_record(target, raw[rid], params, "S-D-P", contract["model"], hash_bytes(contract_path))
                        check("Decimal_PROJ:" + rid + ":" + cfg, independent["status"] == "VERIFIED", independent["errors"])
                        decimal_reviews.append({k: v for k, v in independent.items() if k not in ("common_reference", "final_groups")})
                for group_name, accumulator, p_only in (("comparisons", all_pairs, False), ("P_comparisons", all_ppairs, True)):
                    for key, reported in row[group_name].items():
                        a, b = key.split("|")
                        expected = independent_pair(row["traces"][expected_configs[a]], row["traces"][expected_configs[b]], p_only)
                        check("paired:" + rid + ":" + group_name + ":" + key,
                              all(close(reported[k], v) for k, v in expected.items()))
                        accumulator[key].append(reported)
        check("shard_exact_scope:" + shard["path"], shard_ids == shard["input_ids"] and len(shard_ids) == shard["records"])
    check("complete_payload_scope", observed_ids == expected_ids and len(observed_ids) == len(set(observed_ids)))
    for cid in ids:
        rebuilt = summarize(scalars[cid])
        check("summary_reduction:" + cid, close(manifest["record_metrics"][cid], rebuilt))
        check("point_accounting_total:" + cid, sum(fate_totals[cid].values()) == total_raw_points)
        check("point_fate_summary:" + cid, fate_totals[cid] == Counter({"filtered": rebuilt["n_filtered"],
              "denoised": rebuilt["n_direction_removed"], "simplified": rebuilt["n_dp_removed"], "retained": rebuilt["n_final"]}))
    for group_name, all_rows in (("comparisons", all_pairs), ("P_comparisons", all_ppairs)):
        for key, rows in all_rows.items():
            expected_failures = [r["record_id"] for r in rows if not r["feasible"]]
            summary = manifest[group_name][key]
            check("pair_aggregate:" + group_name + ":" + key, summary["n_records"] == len(expected_ids)
                  and summary["failure_records"] == expected_failures
                  and summary["strict_gain_records"] == sum(r["strict_gain"] for r in rows)
                  and summary["coverage_delta"] == sum(r["coverage_delta"] for r in rows)
                  and summary["P_output_delta"] == sum(r["n_P_output_delta"] for r in rows))
    check("manifest_unchanged", hash_bytes(manifest_path) == manifest_hash)
    receipt = {"role_context": "/root/c_protocol", "status": "VERIFIED" if not problems else "REJECTED",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(), "target_id": manifest["run_id"],
        "targets": [{"path": str(manifest_path.relative_to(ROOT)), "sha256": manifest_hash}],
        "source_hashes": manifest["source_hashes"], "partition": partition, "strategy_ids": ids,
        "checked_components": ["raw byte and record identity", "complete ordered shard/payload scope", "independent rule routing",
            "each actual trace reconstructed against original raw with candidate-external G2 oracle",
            "stored receipt bound to actual trace", "complete terminal ledger and summaries",
            "independent pair decision recomputation", "separate Decimal/PROJ mathematical sample"],
        "unchecked_components": ["source datum", "noise identification accuracy", "reports/package/publication",
            "category representatives not included unless this explicit invocation uses --math-all"],
        "counts": {"raw_records": len(expected_ids), "raw_points": total_raw_points,
                   "distinct_config_trace_reviews": trace_reviews, "Decimal_PROJ_trace_reviews": len(decimal_reviews)},
        "Decimal_PROJ_record_ids": sorted(sample), "decimal_reviews": decimal_reviews,
        "point_fate_totals": {k: dict(v) for k, v in fate_totals.items()},
        "errors": problems, "elapsed_seconds": time.perf_counter() - started,
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_run.py " + str(run.relative_to(ROOT))
                          + (" --math-all" if args.math_all else ""),
        "not_experiment_rerun": "C recomputation only; no new model call or candidate selection",
        "shared_oracle_limit": "All trace checks reuse inherited G2 candidate-external oracle; sampled Decimal/PROJ implementation is separate."}
    output = OUT / (manifest["run_id"] + "_receipt.json")
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "target_id": receipt["target_id"], "counts": receipt["counts"],
                      "errors": problems[:10], "elapsed_seconds": receipt["elapsed_seconds"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
