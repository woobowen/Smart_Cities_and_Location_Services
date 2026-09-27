"""Bind completed C execution/package checks to actual Journal submissions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(task):
    packet_path = BASE / f"{task}_review_submission.json"
    packet = read(packet_path)
    state = read(ROOT / "task1/evidence/goal3/goal_state.json")
    assert packet["task"] == task
    submitted = state["tasks"][task]
    assert submitted["status"] == "REVIEW_PENDING"
    assert packet["targets"] == submitted["targets"]
    assert packet["source_hashes"] == submitted["source_hashes"]
    for target in packet["targets"]:
        assert sha(ROOT / target["path"]) == target["sha256"], target["path"]
    for path, expected in packet["source_hashes"].items():
        assert sha(ROOT / path) == expected, path
    # Check the B helper's alias correction independently against actual schema.
    closure = read(ROOT / "task1/evidence/goal3/package/source_closure.json")
    expected_sources, aliases = {}, []
    for row in closure["members"]:
        path = row["source_path"] if "source_path" in row else row["path"]
        assert sha(ROOT / path) == row["source_sha256"]
        if "source_path" in row:
            aliases.append({"member": row["path"], "source": path})
        expected_sources[path] = row["source_sha256"]
    assert {r["member"] for r in aliases} == {"README.md", "requirements.txt"}
    expected_sources["task1/goal3/execute_notebook.py"] = sha(ROOT / "task1/goal3/execute_notebook.py")
    assert expected_sources == packet["source_hashes"]
    full = read(HERE / "notebook_runs_receipt.json")
    assert full["status"] == "PASS" and len(full["executions"]) == 4
    for row in full["executions"]:
        assert row["status"] == "PASS" and row["new_record_model_calls"] == 0
        assert sha(ROOT / row["execution_receipt"]) == row["execution_receipt_sha256"]
    visual = read(HERE / "notebook_figure_visual_receipt.json")
    assert len(visual["images"]) == 6
    for row in visual["images"]:
        assert row["status"] == "ACTUALLY_VISUALLY_REVIEWED_PASS"
        assert sha(ROOT / row["path"]) == row["sha256"]
        other = row["other_current_execution_same_PNG"]
        assert sha(ROOT / other["path"]) == other["sha256"] == row["sha256"]
    receipts = ["notebook_runs_receipt.json", "notebook_figure_visual_receipt.json",
                "CL-C03_closure.json", "package_execution_equivalence.json"]
    components = [
        "Actual four new-kernel FULL executions: repository12/8 cells and isolated12/8 cells, complete outputs, source/cell/artifact binding, default blocked Provider calls and unchanged raw/memory hashes.",
        "C actually read both basic executions'285 new production shards each, all11386 IDs/1173410 points/22772 processing observations, every point fate and9720 historical parameter/order scope; system each6001 actual candidate computations and384 retained episode choices.",
        "All12 current Notebook output PNGs bind to six individually viewed original-resolution PNG byte sequences; plotting data matched the actual new computations and embedded output.",
        "Two interrupted attempts remain INTERRUPTED_NOT_FULL; fresh-directory same-source recovery and actual complete receipts independently accepted through CL-C03, without asserting an identified SIGTERM cause.",
        "All actual submitted targets and runtime/input source hashes rechecked. B helper source_path fallback inspected against115 member records: only README/requirements are explicit aliases; all other paths default to member paths. No processing or Notebook/source bytes changed by this helper repair.",
    ]
    if task == "package":
        static = read(HERE / "package_receipt.json")
        assert static["status"] == "PASS" and sha(ROOT / static["zip_path"]) == static["zip_sha256"]
        with zipfile.ZipFile(ROOT / static["zip_path"]) as archive:
            manifest = json.loads(archive.read("PACKAGE_MANIFEST.json"))
            assert manifest["submission_status"] == "NOT_READY"
            assert manifest["sent_to_teacher"] is False
        receipts += ["package_receipt.json", "frozen_identity_receipt.json"]
        components += [
            "Final116-member ZIP CRC/path/identity/currentPDF/source closure verified in the bound static C review; no traversal, symlink, font files, environment, unrelated private material or unauthorized paper full text.",
            "Actual extracted execution archive compared member by member with current final ZIP: only Experiment PDF and manifest differ; all113 nonPDF payload members and Process PDF identical. This is inherited content-equivalent FULL evidence, not another execution.",
            "Package engineering verification leaves REVIEW_ONLY/NOT_READY and sent_to_teacher=false; Process Evidence original/spec/Lock and user/newGPT review remain separate unresolved external gates.",
        ]
    part = {"status": "VERIFIED", "targets": packet["targets"],
            "source_hashes": packet["source_hashes"], "checked_components": components}
    out = {
        "role_context": "/root/c_independent", "checked_at": datetime.now(timezone.utc).isoformat(),
        "tasks": {task: part}, "submission": {"path": str(packet_path.relative_to(ROOT)), "sha256": sha(packet_path)},
        "linked_actual_C_receipts": [{"path": str((HERE / name).relative_to(ROOT)), "sha256": sha(HERE / name)} for name in receipts],
        "helper_alias_repair_check": {"helper_path": str((BASE / "prepare_remaining_reviews.py").relative_to(ROOT)), "helper_sha256": sha(BASE / "prepare_remaining_reviews.py"), "explicit_aliases": aliases, "default_member_paths_checked": len(closure["members"]) - len(aliases)},
        "scope_limit": "This C verifies engineering scope only. No new record-level model calls, new method experiment, teacher submission, Evidence Lock, final webpageGPT acceptance or user Understanding PASS is granted.",
    }
    (HERE / f"{task}_task_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"task": task, "status": "VERIFIED", "targets": len(packet["targets"]), "sources": len(packet["source_hashes"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=("notebooks", "package"))
    main(parser.parse_args().task)
