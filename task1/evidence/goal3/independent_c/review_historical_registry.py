"""C-only exact historical mapping and independent saved-episode selection review.

This scans original G2 artifacts. It does not call a model or open G3 selection
or final records. Full raw recomputation remains a later Notebook acceptance.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def gz(path):
    with gzip.open(path, "rt", encoding="utf8") as handle:
        return json.load(handle)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def oh(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def cfg(parameters):
    return "cfg-" + oh({k: float(v) for k, v in parameters.items()})[:16]


def assessment(target, ref):
    a, b = target["metrics"], ref["metrics"]
    before = {v["index"]: v["error"] for v in b["common_point_errors"] if v["error"] is not None}
    after = {v["index"]: v["error"] for v in a["common_point_errors"] if v["error"] is not None}
    eps = max(a["common_floating_allowance"], b["common_floating_allowance"])
    covered = set(before) <= set(after)
    old = max(before.values(), default=None)
    new = max((after[i] for i in before), default=None) if covered else None
    safe = (covered and not a["raw_break_crossings"] and a["dp_checks_passed"]
        and a["n_dp_exceedances"] == 0 and (not b["record_covered"] or a["record_covered"])
        and a["raw_windows_covered"] >= b["raw_windows_covered"])
    p_only = (target["order"] == ref["order"] == "S-D-P" and
        all(target["parameters"][k] == ref["parameters"][k] for k in target["parameters"] if k != "dp"))
    if p_only:
        a_input = next(s["input"] for s in target["stages"] if s["name"] == "P")
        b_input = next(s["input"] for s in ref["stages"] if s["name"] == "P")
        safe = safe and a_input == b_input and a["n_dp_input"] == b["n_dp_input"]
        safe = safe and (a["dp_max_error"] is None or a["dp_max_error"] <= 5 + eps)
        gain = a["n_dp_output"] < b["n_dp_output"]
    else:
        safe = safe and (old is None or new is not None and new <= old + eps)
        gain = len(after) > len(before) or old is not None and new is not None and new < old - eps
    return {"gain": bool(safe and gain), "p_only": p_only, "covered": len(after), "max": new, "eps": eps}


def independently_select(episode, traces):
    reference = cfg({"dt": 30, "distance": 400, "min_points": 5,
                     "min_length": 65, "direction": 35, "dp": 5})
    if episode["mode"] == "llm-only":
        legal = [p["executed_config_id"] for p in episode["proposal_records"] if p.get("executed")]
        assert len(legal) <= 1
        return legal[0] if legal and not traces[legal[0]]["metrics"]["raw_break_crossings"] else reference
    assessed = {cid: assessment(traces[cid], traces[reference]) for cid in episode["candidate_ids"]}
    gains = [cid for cid in episode["candidate_ids"] if assessed[cid]["gain"]]
    if not gains:
        return reference
    if all(assessed[cid]["p_only"] for cid in gains):
        return min(gains, key=lambda cid: (traces[cid]["metrics"]["n_dp_output"],
            traces[cid]["metrics"]["dp_max_error"] or 0, traces[cid]["parameters"]["dp"], cid))

    def dominates(first, second):
        a, b = assessed[first], assessed[second]
        if a["p_only"] != b["p_only"]:
            return False
        if a["max"] is None or b["max"] is None:
            return a["max"] is b["max"] is None and a["covered"] > b["covered"]
        eps = max(a["eps"], b["eps"])
        return a["covered"] >= b["covered"] and a["max"] <= b["max"] + eps and (
            a["covered"] > b["covered"] or a["max"] < b["max"] - eps)
    frontier = [cid for cid in gains if not any(dominates(other, cid) for other in gains if cid != other)]
    return frontier[0] if len(frontier) == 1 else reference


def main():
    started = time.perf_counter()
    ev, old = ROOT / "task1/evidence/goal3", ROOT / "task1/evidence/goal2"
    binding_path = ev / "historical_recompute_registry_binding.json"
    binding = read(binding_path)
    registry_path = ROOT / binding["path"]
    assert sha(registry_path) == binding["sha256"]
    r = gz(registry_path)
    index = read(old / "current_runs.json")
    sources, failures, counts, targets = {}, [], Counter(), []
    def check(label, condition):
        if not condition:
            failures.append(label)
    def target(path):
        targets.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    target(binding_path)
    target(registry_path)
    target(ROOT / "task1/goal3/reproduce.py")
    offsets = {"parameters": 0, "modes": 0}
    for key in ("parameter_development", "order_development", "evaluation_parameters", "evaluation_orders", "memory"):
        folder = old / "runs" / index[key]
        mp = folder / "manifest.json"
        m = read(mp)
        sources[str(mp.relative_to(ROOT))] = sha(mp)
        check(key + ":processing_source", m["source_hashes"] == r["processing_bindings"])
        topic = "modes" if key == "memory" else "parameters"
        for entry in m["artifacts"].values():
            path = folder / entry["file"]
            check(str(path) + ":sha", sha(path) == entry["sha256"])
            batch = gz(path)
            task = r["topics"][topic][offsets[topic]]
            expected = {"source_run_id": m["run_id"], "source_result_path": str(path.relative_to(ROOT)),
                "source_result_sha256": entry["sha256"], "parameters": entry["parameters"], "order": entry["order"],
                "contract_hash": batch["contract_hash"], "provenance": batch["provenance"],
                "records": [{"record_id": row["record_id"], "target_hash": oh(row)} for row in batch["records"]],
                "summary": batch["summary"]}
            check(f"{topic}:{offsets[topic]}:complete_mapping", task == expected)
            check(f"{topic}:{offsets[topic]}:complete_input", [x["record_id"] for x in batch["records"]] == m["input_ids"])
            offsets[topic] += 1
            counts[topic] += len(batch["records"])
            counts["source_trace_files"] += 1
        print(json.dumps({"checked_source": key, "record_hash_checks": counts["parameters"] + counts["modes"]}), flush=True)
    episode_number, proposal_sources, mode_counts = 0, [], Counter()
    for key in ("mode_development", "mode_evaluation"):
        folder = old / "runs" / index[key]
        mp = folder / "manifest.json"
        m = read(mp)
        sources[str(mp.relative_to(ROOT))] = sha(mp)
        check(key + ":processing_source", m["source_hashes"] == r["processing_bindings"])
        for ep_ref in m["mode_episodes"]:
            ep_path = folder / ep_ref["path"]
            check(str(ep_path) + ":sha", sha(ep_path) == ep_ref["sha256"])
            ep = read(ep_path)
            check(str(ep_path) + ":scope", ep["input_ids"] == [x["record_id"] for x in ep["records"]] == ep_ref["input_ids"])
            for name, digest in ep["artifact_hashes"].items():
                check(str(ep_path.parent / name) + ":artifact_hash", sha(ep_path.parent / name) == digest)
                counts["episode_artifact_hash_checks"] += 1
            for row in ep["records"]:
                path = ep_path.parent / (row["record_id"] + "_candidate_traces.json.gz")
                traces = gz(path)["results"]
                check(str(path) + ":candidate_scope", list(traces) == row["candidate_ids"])
                selected = r["episode_selections"][episode_number]
                expected = {"source_episode": str(ep_path.relative_to(ROOT)), "source_episode_sha256": ep_ref["sha256"],
                    "record_id": row["record_id"], "episode_id": row["episode_id"], "mode": row["mode"],
                    "selected_config_id": row["selected_config_id"], "candidate_ids": row["candidate_ids"],
                    "original_proposals": row["proposal_records"], "original_rounds": row["rounds"], "trace_tasks": []}
                path_hash = sha(path)
                for cid in row["candidate_ids"]:
                    t = traces[cid]
                    task = r["topics"]["modes"][offsets["modes"]]
                    expected_task = {"source_run_id": m["run_id"], "source_result_path": str(path.relative_to(ROOT)),
                        "source_result_sha256": path_hash, "parameters": t["parameters"], "order": t["order"],
                        "contract_hash": t["contract_hash"], "provenance": t["provenance"],
                        "records": [{"record_id": row["record_id"], "target_hash": oh(t)}],
                        "episode_id": row["episode_id"], "config_id": cid}
                    check(f"mode_task:{offsets['modes']}:complete_mapping", task == expected_task)
                    check(f"mode_task:{offsets['modes']}:config_identity", cfg(t["parameters"]) == cid)
                    expected["trace_tasks"].append(offsets["modes"])
                    offsets["modes"] += 1
                    counts["modes"] += 1
                check(f"episode:{episode_number}:complete_proposals_and_index", selected == expected)
                check(f"episode:{episode_number}:independent_choice", independently_select(row, traces) == row["selected_config_id"])
                episode_number += 1
                mode_counts[row["mode"]] += 1
                counts["source_trace_files"] += 1
            proposal_sources.append({"path": str(ep_path.relative_to(ROOT)), "sha256": ep_ref["sha256"]})
        print(json.dumps({"checked_source": key, "episode_selections": episode_number}), flush=True)
    check("source_registry_exact", sources == r["source_registry"] == binding["source_registry"])
    check("proposal_sources_exact", proposal_sources == r["proposal_sources"])
    check("complete_task_scope", offsets == {k: len(v) for k, v in r["topics"].items()})
    check("complete_episodes", episode_number == len(r["episode_selections"]) == 384)
    check("counts", {k: counts[k] for k in ("parameters", "modes")} == binding["counts"] == {"parameters": 9720, "modes": 6001})
    check("zero_new_model_calls", r["new_model_calls"] == binding["new_model_calls"] == 0)
    expected_bindings = {**r["processing_bindings"], "task1/config/goal2/contract.json": sha(ROOT / "task1/config/goal2/contract.json"),
                         "task1/evidence/goal2/data/split_manifest.json": sha(old / "data/split_manifest.json")}
    check("processing_binding_set", r["bindings"] == expected_bindings)
    check("processing_binding_bytes", all(sha(ROOT / p) == value for p, value in r["bindings"].items()))
    receipt = {"role_context": "/root/c_protocol", "target_id": "historical_recompute_registry",
        "status": "VERIFIED" if not failures else "REJECTED", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": targets, "source_hashes": r["bindings"], "original_source_manifests": sources,
        "checked_components": ["all original G2 trace object hashes and task parameters/order/provenance",
            "all 7 original manifests and exact ordered record scopes", "all 48 episode artifact hash maps",
            "all 384 original proposals/rounds and complete trace task index mapping",
            "independently reimplemented historical record-level selection for 384 saved episodes",
            "historical processing source hashes still match actual code", "9720 parameter/order and 6001 memory/mode processing tasks"],
        "unchecked_components": ["full raw recomputation of all 15721 tasks; later Notebook run required",
            "fresh LIVE model generation", "G3 selection/final effects", "portable production runtime (separate G3-C06)",
            "package file closure; later isolated extraction required"],
        "counts": dict(counts), "record_episode_selections": episode_number, "mode_counts": dict(mode_counts),
        "new_model_calls": 0, "errors": failures, "elapsed_seconds": time.perf_counter() - started,
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_historical_registry.py"}
    (OUT / "historical_registry_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "counts", "record_episode_selections", "errors", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
