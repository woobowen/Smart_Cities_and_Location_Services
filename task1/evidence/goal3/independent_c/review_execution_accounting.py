"""Read-only C check of processing/cache accounting and committed processing code."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_rows(folder, manifest):
    seen = []
    for shard in manifest["shards"]:
        path = folder / shard["path"]
        assert sha(path) == shard["sha256"]
        ids = []
        with gzip.open(path, "rt", encoding="utf8") as handle:
            for line in handle:
                row = json.loads(line)
                ids.append(row["record_id"])
                yield row
        assert ids == shard["input_ids"] and len(ids) == shard["records"]
        seen.extend(ids)
    assert seen == manifest["input_ids"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    folder = args.run.resolve()
    path = folder / "manifest.json"
    manifest = read(path)
    previous_path = OUT / (manifest["run_id"] + "_receipt.json")
    prior = read(previous_path)
    assert prior["status"] == "VERIFIED" and prior["targets"][0]["sha256"] == sha(path)
    assert manifest["status"] == "MACHINE_VERIFIED_PENDING_C"
    source_checks = {}
    for name, expected in manifest["source_hashes"].items():
        content = subprocess.check_output(["git", "show", manifest["code_sha"] + ":" + name], cwd=ROOT)
        source_checks[name] = hashlib.sha256(content).hexdigest()
        assert source_checks[name] == expected
    targets = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)},
               {"path": str(previous_path.relative_to(ROOT)), "sha256": sha(previous_path)}]
    parent = None
    if manifest["parent_cache"] is not None:
        parent_path = ROOT / manifest["parent_cache"]["path"]
        mp = parent_path / "manifest.json"
        assert sha(mp) == manifest["parent_cache"]["sha256"]
        pm = read(mp)
        assert pm["input_ids"] == manifest["input_ids"] and pm["bindings"] == manifest["bindings"]
        assert pm["provenance"] == manifest["provenance"]
        parent = iter(checked_rows(parent_path, pm))
        targets.append({"path": str(mp.relative_to(ROOT)), "sha256": sha(mp)})
    unique, cached, observations = 0, 0, 0
    for row in checked_rows(folder, manifest):
        p = next(parent) if parent is not None else None
        if p is not None:
            assert p["record_id"] == row["record_id"]
        assert set(row["strategy_configs"]) == set(manifest["strategy_ids"])
        assert set(row["traces"]) == set(row["strategy_configs"].values())
        observations += len(row["strategy_configs"])
        unique += len(row["traces"])
        if p is not None:
            for cfg, trace in row["traces"].items():
                if cfg in p["traces"]:
                    assert trace == p["traces"][cfg]
                    cached += 1
    if parent is not None:
        assert next(parent, None) is None
    expected = {"strategy_record_observations": observations, "review_record_calls": unique,
        "cached_trace_rechecks": cached, "processing_evaluations": unique - cached,
        "reused_identical_configuration_observations": observations - unique,
        "new_record_model_calls": 0}
    errors = [{"field": key, "observed": manifest.get(key), "derived": value}
              for key, value in expected.items() if manifest.get(key) != value]
    assert observations == len(manifest["input_ids"]) * len(manifest["strategy_ids"])
    receipt = {"role_context": "/root/c_protocol", "target_id": manifest["run_id"] + ":execution_accounting",
        "status": "VERIFIED" if not errors else "REJECTED", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": targets, "source_hashes": manifest["source_hashes"], "committed_code_sha": manifest["code_sha"],
        "checked_components": ["every processing source byte matches the recorded Git commit", "all current and parent shard scopes and hashes",
            "complete unchanged parent trace equality", "distinct configs, actual cache opportunities and reported cost counter arithmetic"],
        "unchecked_components": ["hidden provider requests or monetary costs", "governance model calls", "source datum", "new mathematical review; preceding C receipt supplies that scope"],
        "derived_counts": expected, "errors": errors,
        "cost_scope": "record processing counters; governance is a different ledger",
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_execution_accounting.py " + str(folder.relative_to(ROOT))}
    (OUT / (manifest["run_id"] + "_accounting_receipt.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "target_id", "derived_counts", "errors")}))


if __name__ == "__main__":
    main()
