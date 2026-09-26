"""C-only equivalence check after a decision-provenance repair; never new evidence replication."""
import argparse
from copy import deepcopy
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import digest, object_hash, read_json, write_json, now
from review_development_runs import read_compressed, Audit


def normalize(batch):
    """Only per-run provenance changes. No numeric, identity or parameter field is removed."""
    value = deepcopy(batch)
    value.pop("provenance")
    for record in value["records"]:
        record.pop("provenance")
    return value


def review(old_id, new_id, output):
    start = time.perf_counter()
    directories = [ROOT / "task1/evidence/goal2/runs" / run_id for run_id in (old_id, new_id)]
    manifests = [read_json(p / "manifest.json") for p in directories]
    audit = Audit()
    old, new = manifests
    audit.check("new_run_complete", new["status"] == "REVIEW_PENDING")
    audit.check("different_code_epoch", old["source_tree_sha256"] != new["source_tree_sha256"])
    audit.same("same_partition_scope", [old["partition"], old["input_ids"]], [new["partition"], new["input_ids"]])
    audit.check("same_raw_contract_split", all(old[key] == new[key] for key in ("raw_sha256", "contract_sha256", "split_sha256")))
    entries = [{(e["config_id"], e["order"]): e for e in m["artifacts"].values()} for m in manifests]
    audit.check("exact_config_order_set", set(entries[0]) == set(entries[1]))
    rows = []
    for key, old_entry in entries[0].items():
        new_entry = entries[1][key]
        paths = [directories[0] / old_entry["file"], directories[1] / new_entry["file"]]
        for path, entry in zip(paths, (old_entry, new_entry)):
            audit.check("artifact_hash", digest(path) == entry["sha256"])
        batches = [read_compressed(path) for path in paths]
        hashes = [object_hash(normalize(batch)) for batch in batches]
        audit.check("identical_numeric_and_identity_payload", hashes[0] == hashes[1], {"config_order": key, "hashes": hashes})
        rows.append({"config_id": key[0], "order": key[1], "records": len(batches[0]["records"]),
                     "old_hash": digest(paths[0]), "new_hash": digest(paths[1]), "numeric_payload_hash": hashes[0], "identical": hashes[0] == hashes[1]})
    result = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "at": now(),
              "classification": "C_EPOCH_EQUIVALENCE_CHECK_NOT_ADDITIONAL_INDEPENDENT_EXPERIMENT", "old_run": old_id, "new_run": new_id,
              "normalized_fields": ["batch.provenance", "each_record.provenance"], "all_other_fields_compared": True,
              "checks": audit.check_count, "errors": audit.errors, "configurations": len(rows), "record_configurations": sum(r["records"] for r in rows),
              "targets": [{"path": str((p / "manifest.json").relative_to(ROOT)), "sha256": digest(p / "manifest.json")} for p in directories],
              "rows": rows, "new_model_calls": 0, "elapsed_seconds": time.perf_counter() - start,
              "audit_program": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))}}
    write_json(Path(__file__).with_name(output), result, exclusive=True)
    print({key: result[key] for key in ("status", "configurations", "record_configurations", "checks", "errors", "elapsed_seconds")})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("old_run")
    parser.add_argument("new_run")
    parser.add_argument("output")
    args = parser.parse_args()
    result = review(args.old_run, args.new_run, args.output)
    raise SystemExit(result["status"] != "VERIFIED")
