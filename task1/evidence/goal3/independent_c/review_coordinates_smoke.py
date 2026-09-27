"""C engineering smoke on eight already-exposed development records only."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.goal3.coordinates import check_run

OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    source_dir = args.run.resolve()
    mp = source_dir / "manifest.json"
    manifest = read(mp)
    assert manifest["partition"] == "G3_DEVELOPMENT", "Only already-exposed development effects permitted"
    if manifest["status"] != "MACHINE_VERIFIED_PENDING_C":
        print(json.dumps({"status": "NOT_RUN", "reason": "DEVELOPMENT_RUN_NOT_COMPLETE"}))
        return
    first = manifest["shards"][0]
    original_shard = source_dir / first["path"]
    assert sha(original_shard) == first["sha256"]
    with gzip.open(original_shard, "rt", encoding="utf8") as handle:
        sampled = [json.loads(next(handle)) for _ in range(min(8, first["records"]))]
    assert [r["record_id"] for r in sampled] == manifest["input_ids"][:len(sampled)]
    expected = Counter(records_checked=len(sampled))
    for row in sampled:
        reference = next(iter(row["traces"].values()))["source_record"]
        expected.update(points_checked=len(reference["indices"]), raw_adjacent_edges=max(0, len(reference["indices"]) - 1),
                        unique_actual_traces_checked=len(row["traces"]))
        for trace in row["traces"].values():
            for stage in trace["stages"]:
                if stage["name"] == "S":
                    expected["S_distance_edges"] += sum(max(0, len(seg["indices"]) - 1) for seg in stage["input"])
                    expected["S_actual_segments_length"] += sum(len(op["segments"]) for op in stage["operations"])
                elif stage["name"] == "D":
                    expected["D_windows"] += sum(len(seg["indices"]) for seg in stage["input"])
                    expected["D_undefined_windows"] += sum(d["reason"] is not None for op in stage["operations"] for d in op["decisions"])
                elif stage["name"] == "P":
                    expected["P_complete_input_points"] += sum(len(seg["indices"]) for seg in stage["input"])
                    expected["P_immediate_output_points"] += sum(len(seg["indices"]) for seg in stage["output"])
                    expected["P_segments"] += len(stage["input"])
    output = OUT / (manifest["run_id"] + "_coordinate_smoke")
    with tempfile.TemporaryDirectory(prefix="coordinate-smoke-fixture-", dir=OUT) as name:
        fixture = Path(name)
        shard = fixture / "sample.jsonl.gz"
        shard.write_bytes(gzip.compress(("\n".join(json.dumps(r, ensure_ascii=False) for r in sampled) + "\n").encode(), mtime=0))
        m = deepcopy(manifest)
        m["input_ids"] = m["completed_record_ids"] = [r["record_id"] for r in sampled]
        m["classification"] = "C_ENGINEERING_SUBSET_FIXTURE; not a new or full dataset experiment"
        m["shards"] = [{"path": shard.name, "sha256": sha(shard), "records": len(sampled), "input_ids": m["input_ids"]}]
        (fixture / "manifest.json").write_text(json.dumps(m, ensure_ascii=False))
        result = check_run(fixture, output)
        # Preserve exact fixture manifest so the output target hash remains readable.
        (output / "engineering_scope_fixture_manifest.json").write_bytes((fixture / "manifest.json").read_bytes())
    errors = []
    if result["implementation_status"] != "VERIFIED":
        errors.append("coordinate_formula_or_domain_failed")
    if result["counts"] != dict(expected):
        errors.append({"count_mismatch": {"actual": result["counts"], "expected": dict(expected)}})
    with gzip.open(output / "threshold_differences.jsonl.gz", "rt", encoding="utf8") as handle:
        differences = [json.loads(line) for line in handle]
    if dict(Counter(x["kind"] for x in differences)) != result["difference_counts"]:
        errors.append("difference_count_mismatch")
    assert result["source_crs"] == "UNVERIFIED" and not result["source_datum_proven"] and not result["ground_truth_accuracy_claim"]
    targets = [mp, original_shard, ROOT / "task1/goal3/coordinates.py",
               ROOT / "task1/scripts/goal2_coordinate_sensitivity.py", ROOT / "task1/config/goal3/contract.json",
               output / "coordinate_checks.json", output / "threshold_differences.jsonl.gz", output / "engineering_scope_fixture_manifest.json"]
    receipt = {"role_context": "/root/c_protocol", "status": "VERIFIED" if not errors else "REJECTED",
        "target_id": "coordinate_helper_development_smoke", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "8-record DEVELOPMENT engineering smoke; explicitly NOT full production coordinate acceptance",
        "targets": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in targets],
        "checked_components": ["fixed-ellipsoid h=0 ENU vs independent PROJ", "raw adjacent Geod distances",
            "actual S distance/length, D windows, P full input/output intervals and same-ellipsoid AEQD sensitivity",
            "independent stage cardinality reduction equals every reported count", "difference log aggregation"],
        "unchecked_components": ["full original dataset coordinate check", "source datum", "source physical accuracy",
            "full processing correctness; separately bound run C receipt required"],
        "counts": result["counts"], "difference_counts": result["difference_counts"],
        "max_PROJ_error_work_m": result["extrema"]["PROJ_implementation_error_work_m"]["value"],
        "errors": errors, "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_coordinates_smoke.py " + str(source_dir.relative_to(ROOT))}
    (OUT / (manifest["run_id"] + "_coordinates_smoke_receipt.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "classification", "counts", "difference_counts", "max_PROJ_error_work_m", "errors")}))


if __name__ == "__main__":
    main()
