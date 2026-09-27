"""Bind the four actual per-execution C reviews without re-running computation."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    rows, inputs = [], []
    for execution in ("repository_basic", "repository_system", "isolated_basic", "isolated_system"):
        path = HERE / f"notebook_run_{execution}.json"
        own = read(path)
        assert own["status"] == "PASS" and own["role_context"] == "/root/c_independent"
        assert len(own["executions"]) == 1
        row = own["executions"][0]
        assert row["execution"] == execution and row["status"] == "PASS"
        receipt_path = ROOT / row["execution_receipt"]
        assert sha(receipt_path) == row["execution_receipt_sha256"]
        receipt = read(receipt_path)
        assert receipt["status"] == "VERIFIED" and receipt["failure"] is None
        source_name = "作业1轨迹数据预处理_完成版.ipynb" if execution.endswith("basic") else "任务3_LLM辅助评估清洗_完成版.ipynb"
        assert sha(ROOT / "task1/notebooks/final" / source_name) == row["current_notebook_sha256"]
        assert sha(receipt_path.parent / source_name) == row["executed_notebook_sha256"]
        assert sha(receipt_path.parent / "artifacts/notebook_receipt.json") == row["notebook_receipt_sha256"]
        assert receipt["source_sha256"] == sha(ROOT / "task1/goal3/execute_notebook.py")
        for artifact in receipt["preserved_artifacts"]:
            assert sha(receipt_path.parent / artifact["path"]) == artifact["sha256"]
        helper = row["review_helpers"]
        assert sha(ROOT / helper["path"]) == helper["sha256"]
        assert row["new_record_model_calls"] == 0
        rows.append(row)
        inputs.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path),
            "kind": "ACTUAL_CURRENT_TURN_INDEPENDENT_C_PER_EXECUTION_REVIEW"})
    assert [r["executed_code_cells"] for r in rows] == [12, 8, 12, 8]
    equivalent = read(HERE / "package_execution_equivalence.json")
    assert equivalent["status"] == "PASS"
    out = {
        "role_context": "/root/c_independent", "status": "PASS",
        "assembled_at": datetime.now(timezone.utc).isoformat(), "executions": rows,
        "current_per_execution_C_receipts": inputs,
        "claim": "Four actual new-kernel FULL executions were individually checked in this C context. Each basic execution included independently reading all285 real production shards and every raw point fate, as recorded in the exact bound per-run C receipt. This aggregate rechecks the current execution/source/output/preserved-artifact bytes and collects those checks; it does not claim another execution or repeat the numerical algorithm.",
        "package_equivalence": {"path": str((HERE / "package_execution_equivalence.json").relative_to(ROOT)), "sha256": sha(HERE / "package_execution_equivalence.json"),
            "meaning": "Final ZIP differs from the actually executed ZIP only in Experiment PDF and package manifest; all113 non-PDF payload bytes and the Process PDF are identical. This is inherited content-equivalent execution evidence, not a second extracted execution."},
        "new_record_model_calls": 0, "interrupted_attempts_counted_as_success": False,
    }
    (HERE / "notebook_runs_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "actual_successful_FULL_executions": len(rows), "code_cells": [r["executed_code_cells"] for r in rows], "new_record_model_calls": 0}))


if __name__ == "__main__":
    main()
