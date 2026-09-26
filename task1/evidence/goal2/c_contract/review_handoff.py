"""Independent C handoff review. Only this directory receives new files.

Reuses the already reviewed G1 independent Decimal/PROJ checker without changing
its source or the G1 outputs. This is a current regression of historical data,
not a new held-out experiment or a claim that G2 is complete.
"""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import pyproj

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REV = ROOT / "task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001"
ANCHOR = "a45d89f49f2041477b16485f535adc508c32f8ea"
RAW = ROOT / "task1/作业/作业/traj_dict.json"
RAW_HASH = "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    started = time.perf_counter()
    original = REV / "c_acceptance/independent_probe.py"
    spec = importlib.util.spec_from_file_location("g1_independent_reference", original)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.main("g1-complete-pilot-03")
    # A separate current production recomputation must also match the old run.
    sys.path.insert(0, str(ROOT))
    from task1.scripts.complete_goal1 import recompute_saved
    recomputed = recompute_saved("g1-complete-pilot-03")
    write("g1_recompute_current_code.json", recomputed)

    historical = read(ROOT / "task1/evidence/goal1/validation/original_integrity.json")
    protected = []
    for item in historical["files"]:
        if item["path"].startswith("task1/作业") or item["path"] == "task1/实验课1.pptx":
            actual = sha(ROOT / item["path"])
            protected.append({"path": item["path"], "sha256": actual,
                              "expected_sha256": item["sha256_after"],
                              "unchanged": actual == item["sha256_after"]})
    preserved_user_files = []
    for name in ("SC-LAB1-G1-CLOSURE-002_HANDOFF.zip", "SC-LAB1-G1-COMPLETE-001_HANDOFF.zip"):
        preserved_user_files.append({"path": name, "sha256": sha(ROOT / name),
                                     "bytes": (ROOT / name).stat().st_size})
    diff = subprocess.check_output(["git", "diff", "--name-only", ANCHOR, "--",
                                   "task1/evidence/goal1", "task1/config/goal1.json",
                                   "task1/config/conditional_planar.json", "task1/作业",
                                   "task1/作业.zip", "task1/实验课1.pptx"], cwd=ROOT, text=True)
    integrity = {"status": "VERIFIED" if not diff and all(p["unchanged"] for p in protected) else "REJECTED",
                 "anchor": ANCHOR, "teacher_and_starter_files": protected,
                 "compared_file_count": len(protected), "changed_protected_paths": diff.splitlines(),
                 "user_untracked_zip_snapshot": preserved_user_files}
    write("protected_integrity.json", integrity)

    raw = read(RAW)
    model = read(ROOT / "task1/config/conditional_planar.json")["analysis_model"]
    projection = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    rows = []
    duplicates = defaultdict(list)
    schema_errors = []
    for record_id, value in raw.items():
        times, coordinates = value
        if len(times) != len(coordinates) or any(not math.isfinite(t) for t in times) or any(
                len(p) != 2 or any(not math.isfinite(v) for v in p) for p in coordinates):
            schema_errors.append(record_id)
        east, north, _ = projection.transform(*zip(*coordinates), [0] * len(coordinates))
        radii = [math.hypot(e, n) for e, n in zip(east, north)]
        rows.append({"record_id": record_id, "points": len(coordinates), "max_enu_radius_m": max(radii),
                     "points_beyond_g1_40000m_guard": sum(radius > 40000 for radius in radii)})
        key = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        duplicates[key].append(record_id)
    inventory = {"classification": "READ_ONLY_FULL_SOURCE_INVENTORY_NOT_CANDIDATE_PROCESSING",
                 "raw_sha256": sha(RAW), "raw_expected_sha256": RAW_HASH,
                 "records": len(raw), "points": sum(row["points"] for row in rows),
                 "schema_error_record_ids": schema_errors,
                 "max_enu_radius_m": max(row["max_enu_radius_m"] for row in rows),
                 "records_beyond_g1_40000m_guard": sum(bool(row["points_beyond_g1_40000m_guard"]) for row in rows),
                 "points_beyond_g1_40000m_guard": sum(row["points_beyond_g1_40000m_guard"] for row in rows),
                 "exact_duplicate_record_groups": [ids for ids in duplicates.values() if len(ids) > 1],
                 "higher_entity_linkage": "UNAVAILABLE: no external person/vehicle/trip identity inferred",
                 "rows": rows}
    write("raw_extent_inventory.json", inventory)
    independent = read(OUT / "g1-complete-pilot-03_independent.json")
    receipt = {"role_context": "/root/c_contract", "classification": "CURRENT_INDEPENDENT_C_HANDOFF_REVIEW",
               "at_utc": datetime.now(timezone.utc).isoformat(), "command": ".venv/bin/python task1/evidence/goal2/c_contract/review_handoff.py",
               "review_script_sha256": sha(__file__), "reused_independent_probe_sha256": sha(original),
               "targets": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in
                           (REV / "runs/g1-complete-pilot-03/baseline.json", RAW, ROOT / "task1/config/conditional_planar.json")],
               "checked_components": ["raw_sha256", "full_raw_structure_count", "exact_record_duplicates", "raw_extent",
                                      "teacher_starter_bytes", "G1_protected_paths", "seven_record_independent_geometry",
                                      "G1_current_production_recompute_exact_match"],
               "unchecked_components": ["G2_contract", "G2_split", "G2_experiments", "G2_modes", "G2_final_acceptance"],
               "status": "VERIFIED" if independent["status"] == recomputed["status"] == integrity["status"] == "VERIFIED"
                         and not schema_errors and sha(RAW) == RAW_HASH else "REJECTED",
               "independent_check_count": independent["check_count"], "stage_counts": independent["stage_counts"],
               "max_dp_error_working_m": max(row["max_error_m"] for row in independent["dp_checks"]),
               "new_model_calls": 0, "elapsed_s": time.perf_counter() - started,
               "limits": ["G1 exposed pilot regression, not new held-out evidence", "source_crs remains UNVERIFIED",
                          "Expanded extent requires separate G2 numerical and threshold sensitivity verification"]}
    write("handoff_receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "independent_checks": independent["check_count"],
                      "raw_records": inventory["records"], "raw_points": inventory["points"],
                      "protected_files": len(protected), "elapsed_s": receipt["elapsed_s"]}))


if __name__ == "__main__":
    main()
