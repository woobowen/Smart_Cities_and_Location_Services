"""C-only low-cost paired-derived values and explicit shard target receipt."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same(a, b):
    if isinstance(b, dict):
        return isinstance(a, dict) and set(a) == set(b) and all(same(a[k], v) for k, v in b.items())
    if isinstance(b, list):
        return isinstance(a, list) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if type(b) is float:
        return type(a) in (int, float) and math.isclose(a, b, rel_tol=2e-12, abs_tol=1e-10)
    return type(a) is type(b) and a == b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    prior_path = OUT / (manifest["run_id"] + "_receipt.json")
    prior = json.loads(prior_path.read_text())
    assert prior["status"] == "VERIFIED"
    assert prior["targets"][0]["sha256"] == sha(manifest_path)
    errors, all_rows, seen = [], defaultdict(list), []
    targets = [{"path": str(manifest_path.relative_to(ROOT)), "sha256": sha(manifest_path)},
               {"path": str(prior_path.relative_to(ROOT)), "sha256": sha(prior_path)}]
    for shard in manifest["shards"]:
        path = run / shard["path"]
        assert sha(path) == shard["sha256"]
        targets.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
        with gzip.open(path, "rt", encoding="utf8") as handle:
            shard_seen = []
            for line in handle:
                row = json.loads(line)
                seen.append(row["record_id"])
                shard_seen.append(row["record_id"])
                for family in ("comparisons", "P_comparisons"):
                    for key, reported in row[family].items():
                        a, b = key.split("|")
                        c = row["traces"][row["strategy_configs"][a]]["metrics"]
                        r = row["traces"][row["strategy_configs"][b]]["metrics"]
                        before = {x["index"]: x["error"] for x in r["common_point_errors"] if x["error"] is not None}
                        after = {x["index"]: x["error"] for x in c["common_point_errors"] if x["error"] is not None}
                        new = sorted(set(after) - set(before))
                        eps = max(c["common_floating_allowance"], r["common_floating_allowance"])
                        expected = {
                            "baseline_covered_count": len(before), "candidate_covered_count": len(after),
                            "coverage_delta": len(after) - len(before), "baseline_common_max": max(before.values(), default=None),
                            "candidate_max_on_baseline_covered": max((after[i] for i in before), default=None) if set(before) <= set(after) else None,
                            "newly_covered_indices": new, "newly_covered_count": len(new),
                            "newly_covered_error_sum": math.fsum(after[i] for i in new),
                            "newly_covered_max_error": max((after[i] for i in new), default=None),
                            "n_final_delta": c["n_final"] - r["n_final"],
                            "n_P_output_delta": c["n_dp_output"] - r["n_dp_output"],
                            "candidate_dp_max": c["dp_max_error"], "comparator_dp_max": r["dp_max_error"],
                            "numerical_allowance": eps,
                            "equivalent_readings": set(before) == set(after) and all(abs(after[i] - before[i]) <= eps for i in before)
                                and all(c[k] == r[k] for k in ("n_input", "n_final", "n_filtered", "n_direction_removed",
                                                              "n_dp_removed", "n_dp_input", "n_dp_output", "raw_windows_covered")),
                        }
                        for field, value in expected.items():
                            if not same(reported[field], value):
                                errors.append({"record_id": row["record_id"], "family": family, "pair": key, "field": field})
                        all_rows[(family, key)].append(reported)
            if shard_seen != shard["input_ids"] or len(shard_seen) != shard["records"]:
                errors.append({"shard": shard["path"], "field": "exact_scope"})
    if seen != manifest["input_ids"]:
        errors.append({"field": "complete_scope"})
    for (family, key), rows in all_rows.items():
        failures = [r for r in rows if not r["feasible"]]
        hard_names = {"RAW_BREAKPOINT_CROSSED", "DP_CONTRACT_FAILED", "COMMON_DP_BUDGET_EXCEEDED",
                      "DP_REFERENCE_CHANGED", "DP_REFERENCE_COUNT_CHANGED"}
        hard = any(hard_names & set(r["protection_failures"]) for r in rows)
        gain = sum(r["n_P_output_delta"] for r in rows) < 0 if family == "P_comparisons" else any(r["strict_gain"] for r in rows)
        expected = {"n_records": len(rows), "protected_records": len(rows) - len(failures),
            "failure_records": [r["record_id"] for r in failures], "strict_gain_records": sum(r["strict_gain"] for r in rows),
            "status": "REJECTED_BY_CONSTRAINT" if hard else "TRADEOFF" if failures else "SUPPORTED_WITHIN_SCOPE" if gain else "NO_DEMONSTRATED_GAIN",
            "all_guards_pass": bool(rows) and not failures,
            "replacement_supported": bool(rows) and not failures and gain,
            "coverage_delta": sum(r["coverage_delta"] for r in rows),
            "final_point_delta": sum(r["n_final_delta"] for r in rows),
            "P_output_delta": sum(r["n_P_output_delta"] for r in rows),
            "all_equivalent_readings": bool(rows) and all(r["equivalent_readings"] for r in rows),
            "new_coverage_max_error": max((r["newly_covered_max_error"] for r in rows if r["newly_covered_max_error"] is not None), default=None),
            "failures_by_reason": dict(Counter(reason for row in failures for reason in row["protection_failures"]))}
        if not same(manifest[family][key], expected):
            errors.append({"family": family, "pair": key, "field": "aggregate"})
    paired_path = run / "paired_summary.json"
    check = json.loads(paired_path.read_text())
    if check != {"all_pairs": manifest["comparisons"], "P_pairs": manifest["P_comparisons"]}:
        errors.append({"field": "paired_summary_mirror"})
    targets.append({"path": str(paired_path.relative_to(ROOT)), "sha256": sha(paired_path)})
    receipt = {"role_context": "/root/c_protocol", "status": "VERIFIED" if not errors else "REJECTED",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(), "target_id": manifest["run_id"],
        "targets": targets, "source_hashes": manifest["source_hashes"],
        "checked_components": ["explicit immutable shard targets", "all paired coverage identities and geometric derived values",
            "all paired stage-count differences", "pointwise equivalence", "all paired aggregate decisions", "paired summary mirror"],
        "unchecked_components": ["source datum", "new mathematical rerun; use prior bound run receipt", "new algorithm selection"],
        "records": len(seen), "paired_rows": sum(map(len, all_rows.values())), "errors": errors,
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_pair_derivatives.py " + str(run.relative_to(ROOT))}
    (OUT / (manifest["run_id"] + "_pairs_receipt.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "target_id", "records", "paired_rows", "errors")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
