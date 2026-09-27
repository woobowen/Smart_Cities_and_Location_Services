"""Bounded C engineering smoke of real raw recompute, never a full-result claim."""
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.goal3 import reproduce
from task1.workflow.g2_provider import ExperimentProvider

OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    original = ROOT / "task1/evidence/goal3/historical_recompute_registry.json.gz"
    registry = json.loads(gzip.decompress(original.read_bytes()))
    fixture = deepcopy(registry)
    fixture["classification"] = "C_ENGINEERING_SUBSET_FIXTURE_NOT_FULL_RECOMPUTE"
    fixture["topics"] = {"parameters": [], "modes": []}
    fixture["episode_selections"] = []
    # One actual record from each original batch covers all configurations/orders.
    for topic in ("parameters", "modes"):
        for task in registry["topics"][topic]:
            if "episode_id" in task:
                continue
            t = deepcopy(task)
            t["records"] = [t["records"][0]]
            t.pop("summary", None)  # A sample cannot claim a full-batch summary.
            fixture["topics"][topic].append(t)
    seen_modes = set()
    for episode in registry["episode_selections"]:
        if episode["mode"] in seen_modes:
            continue
        seen_modes.add(episode["mode"])
        e = deepcopy(episode)
        e["trace_tasks"] = []
        for i in episode["trace_tasks"]:
            e["trace_tasks"].append(len(fixture["topics"]["modes"]))
            fixture["topics"]["modes"].append(deepcopy(registry["topics"]["modes"][i]))
        fixture["episode_selections"].append(e)
    processing, reviewing, model = 0, 0, 0
    original_run, original_review = reproduce.run_record, reproduce.review_record

    def traced_run(*args, **kwargs):
        nonlocal processing
        processing += 1
        return original_run(*args, **kwargs)

    def traced_review(*args, **kwargs):
        nonlocal reviewing
        reviewing += 1
        return original_review(*args, **kwargs)

    def forbidden_model(*args, **kwargs):
        nonlocal model
        model += 1
        raise AssertionError("OFFLINE_RECOMPUTE_ATTEMPTED_MODEL_CALL")

    with tempfile.TemporaryDirectory(prefix="historical-smoke-fixture-", dir=OUT) as folder:
        temp = Path(folder)
        registry_path = temp / "registry.json.gz"
        registry_path.write_bytes(gzip.compress(json.dumps(fixture, ensure_ascii=False).encode(), mtime=0))
        binding = {"path": str(registry_path.relative_to(ROOT)), "sha256": sha(registry_path),
            "counts": {k: sum(len(t["records"]) for t in tasks) for k, tasks in fixture["topics"].items()},
            "classification": "C_ENGINEERING_SUBSET_FIXTURE_NOT_FULL_RECOMPUTE"}
        (temp / "historical_recompute_registry_binding.json").write_text(json.dumps(binding))
        results = {}
        with patch.object(reproduce, "EV", temp), patch.object(reproduce, "run_record", traced_run), \
             patch.object(reproduce, "review_record", traced_review), patch.object(ExperimentProvider, "call", forbidden_model):
            for topic in ("parameters", "modes"):
                result = reproduce.recompute_historical(topic, temp / topic)
                assert result["candidate_record_recomputations"] == binding["counts"][topic]
                results[topic] = {k: result[k] for k in ("status", "candidate_record_recomputations", "elapsed_seconds", "selections")}
            binding["sha256"] = "0" * 64
            (temp / "historical_recompute_registry_binding.json").write_text(json.dumps(binding))
            try:
                reproduce.recompute_historical("parameters", temp / "tamper")
            except ValueError as exc:
                assert str(exc) == "RECOMPUTE_REGISTRY_CHANGED"
                tamper_rejected = True
            else:
                tamper_rejected = False
        assert processing == reviewing == sum(v["candidate_record_recomputations"] for v in results.values())
        assert model == 0 and tamper_rejected
    receipt = {"role_context": "/root/c_protocol", "status": "VERIFIED", "target_id": "historical_recompute_smoke",
        "classification": "BOUNDED_REAL_RAW_ENGINEERING_SMOKE; not full G2/G3 experiment",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": [{"path": str(original.relative_to(ROOT)), "sha256": sha(original)},
            {"path": "task1/goal3/reproduce.py", "sha256": sha(ROOT / "task1/goal3/reproduce.py")}],
        "checked_components": ["actual raw run_record + independent review_record for one record in every historical batch configuration/order",
            "actual record episode candidate recomputation and selection for one episode in each of four modes",
            "registry hash mutation rejection before any added processing", "provider call tripwire not activated"],
        "unchecked_components": ["all 15721 historical tasks; actual full Notebook still required", "full-batch summary rebuilding in this sampled smoke"],
        "results": results, "observed_run_record_calls": processing, "observed_review_record_calls": reviewing,
        "observed_provider_calls": model, "tamper_rejected": tamper_rejected,
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/smoke_historical_recompute.py"}
    (OUT / "historical_recompute_smoke_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "observed_run_record_calls", "observed_review_record_calls", "observed_provider_calls", "tamper_rejected")}))


if __name__ == "__main__":
    main()
