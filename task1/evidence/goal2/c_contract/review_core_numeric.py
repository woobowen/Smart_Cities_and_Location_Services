"""Execute G2's six orders on exposed pilot, then independently reconstruct them.

The oracle imports no production processing or metrics; target creation does.
This is C engineering validation, never developmental/heldout selection evidence.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from independent_numeric import audit_record
from task1.workflow.g2_pipeline import run_record
from task1.workflow.g2_metrics import review_record
from task1.workflow.g2_data import raw_data, adapt
from task1.workflow.io import read_json, write_json, digest, object_hash, now


def main():
    started = time.perf_counter()
    output = Path(__file__).with_name("core_numeric_current.json")
    if output.exists():
        raise ValueError("REVIEW_EXISTS_DO_NOT_OVERWRITE")
    contract_path = ROOT / "task1/config/goal2/contract.json"
    contract = read_json(contract_path)
    chash = digest(contract_path)
    raw = raw_data()
    ids = ["0", "1", "2", "246", "256", "306", "352"]
    rows = []
    for rid in ids:
        trusted = adapt(rid, raw[rid])
        for order in contract["orders"]:
            parameters = contract["reference_parameters"]
            provenance = {"source_kind": "ENGINEERING_TEST", "purpose": "INDEPENDENT_C_EXPOSED_PILOT_REGRESSION"}
            target = run_record(trusted, parameters, order, contract_hash=chash, provenance=provenance)
            independent = audit_record(target, raw[rid], parameters, order, contract["model"], chash)
            production = review_record(target, trusted, expected_parameters=parameters, expected_order=order,
                                       contract_hash=chash, trusted_provenance=provenance)
            rows.append({"record_id": rid, "order": order, "target_sha256": object_hash(target),
                         "independent": {key: value for key, value in independent.items()
                                         if key not in ("final_groups", "common_reference")},
                         "common_independent_summary": {key: independent["common_reference"][key]
                                                        for key in ("max_error", "mean_error", "crossed_edges")},
                         "production_review_status": production["status"], "production_errors": production["errors"]})
    paths = ["task1/workflow/" + name + ".py" for name in ("g2_pipeline", "g2_metrics", "g2_data")]
    receipt = {"status": "VERIFIED" if all(x["independent"]["status"] == x["production_review_status"] == "VERIFIED" for x in rows) else "REJECTED",
               "classification": "C_ENGINEERING_PROBE_ON_EXPOSED_G1_PILOT_NOT_G2_SELECTION",
               "role_context": "/root/c_contract", "created_at": now(), "records": 7, "order_runs": len(rows),
               "source_hashes": {p: digest(ROOT / p) for p in paths},
               "oracle_sha256": digest(Path(__file__).with_name("independent_numeric.py")),
               "contract_sha256": chash, "raw_sha256": "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3",
               "checked_components": ["six_orders", "independent_metrics", "point_accounting", "stage_features", "PROJ_coordinates", "full_DP_input", "common_raw_reference"],
               "unchecked_components": ["formal_development_grid", "formal_G2_EVAL", "all_selected_coordinate_sensitivity", "full_goal_acceptance"],
               "checks": rows, "total_checks": sum(x["independent"]["checks"] for x in rows),
               "elapsed_seconds": time.perf_counter() - started, "new_model_calls": 0}
    write_json(output, receipt, exclusive=True)
    print({key: receipt[key] for key in ("status", "records", "order_runs", "total_checks", "elapsed_seconds", "new_model_calls")})


if __name__ == "__main__":
    main()
