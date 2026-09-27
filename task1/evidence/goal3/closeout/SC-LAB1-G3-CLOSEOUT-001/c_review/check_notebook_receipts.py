"""Read actual execution artifacts and bind four successful FULL runs.

Does not launch a fifth equivalent numerical run. Interrupted attempts stay
separately recorded and never satisfy a completed-run assertion.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import argparse
import base64
import gzip
import importlib.util

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
CLOSEOUT = HERE.parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p: Path):
    return json.loads(p.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution", choices=("repository_basic", "repository_system", "isolated_basic", "isolated_system"))
    args = parser.parse_args()
    # Reuse only these read-only, inspected verification functions. The old
    # all-in-one entrypoint has an obsolete identity assertion and is not run.
    helper_path = ROOT / "task1/evidence/goal3/independent_c/review_full_notebook.py"
    spec = importlib.util.spec_from_file_location("historical_full_review_helpers", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    rows = []
    for location in ("repository", "isolated"):
        for kind, name, count in (
            ("basic", "作业1轨迹数据预处理_完成版.ipynb", 12),
            ("system", "任务3_LLM辅助评估清洗_完成版.ipynb", 8),
        ):
            execution_id = f"{location}_{kind}"
            if args.execution and args.execution != execution_id:
                continue
            folder_name = {
                ("repository", "basic"): "repository_basic_retry",
                ("repository", "system"): "repository_system",
                ("isolated", "basic"): "isolated_basic",
                ("isolated", "system"): "isolated_system_retry",
            }[(location, kind)]
            folder = CLOSEOUT / "notebooks" / folder_name
            receipt_path = folder / "execution_receipt.json"
            ex = read(receipt_path)
            current = ROOT / "task1/notebooks/final" / name
            executed = folder / name
            assert ex["status"] == "VERIFIED" and ex["failure"] is None
            assert ex["started_from_clean_outputs_and_new_kernel"] is True
            assert ex["executed_code_cells"] == ex["total_code_cells"] == count
            assert ex["notebook_source_sha256"] == sha(current)
            assert ex["executed_notebook_sha256"] == sha(executed)
            assert ex["source_sha256"] == sha(ROOT / "task1/goal3/execute_notebook.py")
            before, after = read(current), read(executed)
            assert len(before["cells"]) == len(after["cells"])
            for b, a in zip(before["cells"], after["cells"]):
                assert (b["id"], b["cell_type"], b["source"]) == (a["id"], a["cell_type"], a["source"])
                if a["cell_type"] == "code":
                    assert a["execution_count"] is not None
                    assert not any(x["output_type"] == "error" for x in a["outputs"])
            cell_events = read(folder / "cells.json")
            code_indices = [i for i, c in enumerate(before["cells"]) if c["cell_type"] == "code"]
            assert [e["cell_index"] for e in cell_events] == code_indices
            assert [e["execution_count"] for e in cell_events] == list(range(1, count + 1))
            assert all(e["kernel_status"] == "ok" for e in cell_events)
            for artifact in ex["preserved_artifacts"]:
                assert sha(folder / artifact["path"]) == artifact["sha256"]
            assert {str((folder / x["path"]).resolve()) for x in ex["preserved_artifacts"]} == {
                str(p.resolve()) for p in (folder / "artifacts").rglob("*") if p.is_file()}

            nb_path = folder / "artifacts/notebook_receipt.json"
            nb = read(nb_path)
            assert nb["status"] == "VERIFIED" and nb["mode"] == "FULL_RECOMPUTE"
            assert nb["new_model_call_attempts_observed"] == 0
            assert nb["memory_sha256_before"] == nb["memory_sha256_after"]
            assert nb["raw_sha256_unchanged"] is True
            assert nb["module_root_matches_current_project"] is True
            assert nb["historical_recompute_is_new_live"] is False
            if location == "isolated":
                assert Path(ex["kernel_cwd"]).resolve() != ROOT
                assert not (Path(ex["kernel_cwd"]) / ".git").exists()
            else:
                assert Path(ex["kernel_cwd"]).resolve() == ROOT
            execution_root = Path(ex["kernel_cwd"]).resolve()
            work = Path(ex["temporary_work_directory"])
            assert work.resolve() != execution_root and execution_root not in work.resolve().parents
            code = [c for c in after["cells"] if c["cell_type"] == "code"]
            all_code = "\n".join("".join(c["source"]) for c in code)
            for required in ("MODE = 'FULL_RECOMPUTE'", "ENABLE_LIVE = False",
                             "ExperimentProvider.call = forbid_provider", "CodexProvider.call = forbid_provider",
                             "provider_observation['attempted_new_calls'] == 0", "MODULE_ROOT.resolve() == ROOT"):
                assert required.replace(" ", "") in all_code.replace(" ", "")
            embedded_pngs = {hashlib.sha256(base64.b64decode("".join(o["data"]["image/png"]))).hexdigest()
                for c in code for o in c.get("outputs", []) if "image/png" in o.get("data", {})}
            final_text = "".join("".join(o.get("text", "")) for o in code[-1]["outputs"])
            embedded_receipt, _ = json.JSONDecoder().raw_decode(final_text.lstrip())
            assert embedded_receipt == nb
            registry_path = execution_root / "task1/evidence/goal3/historical_recompute_registry.json.gz"
            binding = read(execution_root / "task1/evidence/goal3/historical_recompute_registry_binding.json")
            assert sha(registry_path) == binding["sha256"]
            registry = json.loads(gzip.decompress(registry_path.read_bytes()))
            for path, expected in registry["bindings"].items():
                assert sha(execution_root / path) == expected
            raw_sha = sha(execution_root / "task1/作业/作业/traj_dict.json")
            assert raw_sha == "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3"
            stage = read(execution_root / "task1/evidence/goal2/result_summary.json")
            assert sha(execution_root / stage["memory"]["snapshot_path"]) == nb["memory_sha256_before"] == stage["memory"]["snapshot_sha256"]
            history = helper.historical_check(execution_root, folder, "parameters" if kind == "basic" else "modes", registry, embedded_pngs)
            production, demonstration = None, None

            scopes = {}
            if kind == "basic":
                assert nb["production_raw_records"] == 11386
                assert nb["production_record_evaluations"] == 22772
                assert nb["historical_record_candidate_recomputations"] == 9720
                assert nb["synthetic_pipeline_recomputations"] == 19
                assert nb["known_exposed_pilot_runs"] == 1
                scopes = {k: nb[k] for k in (
                    "production_raw_records", "production_record_evaluations",
                    "historical_record_candidate_recomputations", "synthetic_pipeline_recomputations",
                    "known_exposed_pilot_runs",
                )}
                production = helper.production_check(execution_root, folder, work, embedded_pngs)
                demonstration = helper.basic_demonstration_check(execution_root, folder, after, nb, production.pop("pilot_reference_trace"))
                assert production["raw_records"] == 11386 and production["raw_points"] == 1173410
                assert production["record_candidate_recomputations"] == 22772
                assert history["record_candidate_recomputations"] == 9720
            else:
                modes = read(folder / "artifacts/modes/recompute_receipt.json")
                assert nb["historical_record_candidate_recomputations"] == modes["candidate_record_recomputations"] == 6001
                assert nb["recomputed_original_record_episode_selections"] == len(modes["selections"]) == 384
                assert sum(c["records"] for c in modes["checks"]) == 6001
                assert all(c["raw_recomputed_hash_and_review"] == "VERIFIED" for c in modes["checks"])
                assert all(s["selection_match"] is True for s in modes["selections"])
                assert modes["new_model_calls"] == 0
                scopes = {"historical_record_candidate_recomputations": 6001, "recomputed_original_record_episode_selections": 384}
            rows.append({
                "execution": f"{location}_{kind}", "execution_receipt": str(receipt_path.relative_to(ROOT)),
                "actual_attempt_directory": folder_name,
                "execution_receipt_sha256": sha(receipt_path), "current_notebook_sha256": sha(current),
                "executed_notebook_sha256": sha(executed), "notebook_receipt_sha256": sha(nb_path),
                "executed_code_cells": count, "elapsed_seconds": ex["elapsed_seconds"],
                "kernel_cwd": ex["kernel_cwd"], "first_cell_at": cell_events[0]["at"],
                "last_cell_at": cell_events[-1]["at"], "new_record_model_calls": 0,
                "scope": scopes, "status": "PASS",
                "historical_registry_and_new_plot_scope": history,
                "actual_full_production_shards_and_point_fates": production,
                "synthetic_and_pilot": demonstration,
                "review_helpers": {"path": str(helper_path.relative_to(ROOT)), "sha256": sha(helper_path),
                    "functions": ["historical_check", "figure_check"] + (["production_check", "basic_demonstration_check"] if kind == "basic" else []),
                    "old_top_level_audit_or_identity_assertion_executed": False},
            })
    out = {
        "role_context": "/root/c_independent", "status": "PASS", "executions": rows,
        "claim": "C independently reads each listed real fresh-kernel execution receipt, every code-cell event/source/output, all artifact hashes, every registered historical task/episode and newly plotted values. For each basic run C reads all285 actual new /tmp production shards, compares their actual hashes with canonical frozen trace hashes, reduces every original point fate and11386 IDs/1173410 points/22772 processing observations, and checks9720 parameter/order scope. System FULL is complete registered historical modes/memory scope. C launches no numerical processing or model calls.",
        "package_equivalence": "Final ZIP source/dependency/input equivalence is separately checked; a report-only repack is inherited equivalent execution evidence, not a new execution.",
    }
    filename = f"notebook_run_{args.execution}.json" if args.execution else "notebook_runs_receipt.json"
    (HERE / filename).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "successful_FULL_executions": len(rows), "code_cells": [r["executed_code_cells"] for r in rows], "new_record_model_calls": 0}))


if __name__ == "__main__":
    main()
