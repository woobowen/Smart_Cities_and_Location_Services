"""C-only predeclared full-production category sampling and Decimal/PROJ review.

No run is opened until the actual production freeze and preceding whole-scope
C receipt have been checked. Category representatives are not all-category audits.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.evidence.goal2.c_contract.independent_numeric import audit_record

OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(group, salt):
    return hashlib.sha256(("42|" + salt + "|" + group).encode()).hexdigest()


def rows(path):
    with gzip.open(path, "rt", encoding="utf8") as stream:
        for line in stream:
            yield json.loads(line)


def category_values(row, final):
    """Only actual stage inputs/windows/residuals; never an invented threshold."""
    traces = row["traces"]
    ref = traces[row["strategy_configs"]["R0"]]
    target = traces[row["strategy_configs"][final]]
    s_margin, d_margin, p_margin = [], [], []
    for trace in traces.values():
        params = trace["parameters"]
        for stage in trace["stages"]:
            if stage["name"] == "S":
                s_margin.extend(abs(e["distance"] - 400) for seg in stage["input"] for e in seg["features"]["edges"])
                s_margin.extend(abs(seg["features"]["length"] - params["min_length"])
                                for op in stage["operations"] for seg in op["segments"])
            elif stage["name"] == "D":
                for op in stage["operations"]:
                    for decision in op["decisions"]:
                        values = [decision["previous_difference_degrees"], decision["following_difference_degrees"]]
                        if all(value is not None for value in values):
                            d_margin.extend(abs(value - params["direction"]) for value in values)
            elif stage["name"] == "P":
                p_margin.extend(abs(item["error"] - 5) for op in stage["operations"]
                                for item in op["runtime_dp_check"]["error_by_original_index"])
    xy = ref["source_record"]["xy"]
    span = math.hypot(max(p[0] for p in xy) - min(p[0] for p in xy),
                      max(p[1] for p in xy) - min(p[1] for p in xy)) if xy else 0
    before = {x["index"] for x in ref["metrics"]["common_point_errors"] if x["error"] is not None}
    after = {x["index"] for x in target["metrics"]["common_point_errors"] if x["error"] is not None}
    # Current approved runtime has no record-level verifier fallback path.
    # An unexpected future schema is not silently treated as zero fallbacks.
    if row.get("fallback") or row.get("fallbacks"):
        raise ValueError("UNREGISTERED_FALLBACK_SCHEMA_REQUIRES_EXPLICIT_RECEIPT_REVIEW")
    return {"all_filtered_R0": 1 if ref["metrics"]["all_filtered"] else None,
        "no_output_final": 1 if target["metrics"]["no_output"] else None,
        "fallback": None, "failure": None,
        "near_S_threshold": min(s_margin, default=None),
        "near_D_threshold": min(d_margin, default=None),
        "near_P_threshold": min(p_margin, default=None),
        "extreme_span": span, "new_coverage": len(after - before) or None,
        "worst_common_error": target["metrics"]["common_max_error"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    folder = args.run.resolve()
    mp = folder / "manifest.json"
    frozen_path = ROOT / "task1/evidence/goal3/production_freeze.json"
    frozen = read(frozen_path)
    assert all(sha(ROOT / p) == h for p, h in frozen["bindings"].items())
    manifest = read(mp)
    assert manifest["partition"] == "FULL_PRODUCTION"
    assert manifest["strategy_ids"] == frozen["strategy_ids"]
    assert manifest["input_ids"] == frozen["input_ids"]
    assert not manifest["failed_records"], "All unresolved failure receipts require repair; cannot certify full success"
    previous_path = OUT / (manifest["run_id"] + "_receipt.json")
    previous = read(previous_path)
    assert previous["status"] == "VERIFIED" and previous["targets"][0]["sha256"] == sha(mp)
    contract_path = ROOT / "task1/config/goal3/contract.json"
    contract = read(contract_path)
    spec = contract["full_audit"]["independent_math_sample"]
    split = read(ROOT / "task1/evidence/goal3/split_manifest.json")
    raw_path = ROOT / contract["raw_path"]
    assert sha(raw_path) == contract["raw_sha256"]
    raw = read(raw_path)
    assert set(manifest["input_ids"]) == set(raw)
    candidates = [cid for cid in manifest["strategy_ids"] if cid != "R0"]
    assert "R0" in manifest["strategy_ids"] and len(candidates) <= 1
    final = candidates[0] if candidates else "R0"
    groups = defaultdict(list)
    for rid in manifest["input_ids"]:
        groups[split["group_for_record"][rid]].append(rid)
    order = lambda rid: (rank(split["group_for_record"][rid], spec["salt"]), rid)
    random_ids = []
    for group in sorted(groups, key=lambda g: (rank(g, spec["salt"]), g)):
        random_ids.extend(groups[group])
        if len(random_ids) >= spec["random_records"]:
            break
    values, observed = {}, []
    for shard in manifest["shards"]:
        path = folder / shard["path"]
        assert sha(path) == shard["sha256"]
        ids = []
        for row in rows(path):
            rid = row["record_id"]
            ids.append(rid)
            assert rid not in values
            values[rid] = category_values(row, final)
        assert ids == shard["input_ids"]
        observed.extend(ids)
    assert observed == manifest["input_ids"]
    selected, category_details = set(random_ids), {}
    descending = {"extreme_span", "new_coverage", "worst_common_error"}
    units = {"near_S_threshold": "work_m", "near_D_threshold": "degrees", "near_P_threshold": "work_m",
             "extreme_span": "work_m", "new_coverage": "original_points", "worst_common_error": "work_m"}
    for category in spec["categories"]:
        available = [rid for rid in observed if values[rid][category] is not None]
        if category in {"all_filtered_R0", "no_output_final", "fallback", "failure"}:
            sorted_ids = sorted(available, key=order)
        else:
            sorted_ids = sorted(available, key=lambda rid: ((-1 if category in descending else 1) * values[rid][category], *order(rid)))
        picked, picked_groups = [], set()
        for rid in sorted_ids:
            group = split["group_for_record"][rid]
            if group in picked_groups:
                continue
            picked_groups.add(group)
            picked.extend(groups[group])
            if len(picked_groups) >= spec["representatives_per_present_category"]:
                break
        selected.update(picked)
        category_details[category] = {"available_records": len(available), "selected_records": picked,
            "scores": {rid: values[rid][category] for rid in picked},
            "scope": "at most two group representatives; not all records in the category",
            "score_unit": units.get(category, "category_membership"),
            "absence_reason": None if available else "NO_PRESENT_CATEGORY_OR_CALCULABLE_VALUE",
            "rule": spec["category_selection"][category]}
    checked, failures, shard_targets = [], [], []
    for shard in manifest["shards"]:
        if not selected.intersection(shard["input_ids"]):
            continue
        path = folder / shard["path"]
        assert sha(path) == shard["sha256"]
        shard_targets.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
        for row in rows(path):
            rid = row["record_id"]
            if rid not in selected:
                continue
            for cfg, trace in row["traces"].items():
                result = audit_record(trace, raw[rid], trace["parameters"], "S-D-P", contract["model"], sha(contract_path))
                checked.append({"record_id": rid, "configuration": cfg, "status": result["status"]})
                if result["status"] != "VERIFIED":
                    failures.append({"record_id": rid, "configuration": cfg, "errors": result["errors"]})
    assert {r["record_id"] for r in checked} == selected
    scalar_path = OUT / (manifest["run_id"] + "_category_readings.json.gz")
    scalar_path.write_bytes(gzip.compress(json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    targets = [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in
               (mp, frozen_path, contract_path, previous_path, scalar_path)]
    receipt = {"role_context": "/root/c_protocol", "status": "VERIFIED" if not failures else "REJECTED",
        "target_id": manifest["run_id"] + ":category_math", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": targets + shard_targets, "source_hashes": manifest["source_hashes"],
        "checked_components": ["whole-dataset frozen category scalar enumeration and exact record scope",
            "contract-prescribed stable whole-group random sample", "two representatives of each present category",
            "separate C-only Decimal stage/interval math and independent PROJ coordinates on all sampled traces"],
        "unchecked_components": ["Decimal recomputation of every record", "source datum verification", "true noise identification accuracy"],
        "final_strategy": final, "whole_dataset_records_categorized": len(values),
        "random_records": random_ids, "categories": category_details, "unique_math_records": len(selected),
        "distinct_configuration_math_checks": len(checked), "math_checks": checked, "errors": failures,
        "all_failure_receipts": {"observed": 0, "checked": 0, "basis": "preceding full-scope C receipt and empty manifest.failed_records"},
        "all_fallback_receipts": {"observed": 0, "checked": 0, "basis": "frozen runtime contains no record-level fallback; every full row explicitly checked for fallback fields"},
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_full_categories.py " + str(folder.relative_to(ROOT))}
    (OUT / (manifest["run_id"] + "_categories_receipt.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "whole_dataset_records_categorized", "unique_math_records", "distinct_configuration_math_checks", "errors")}))


if __name__ == "__main__":
    main()
