"""C-only synthetic archive fixture; Git invocation itself is deliberately real."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.goal3 import runtime


def main():
    original = ROOT / "task1/goal3/runtime.py"
    with tempfile.TemporaryDirectory(prefix="g3-c06-archive-") as folder:
        root = Path(folder)
        ev, cfg = root / "task1/evidence/goal3", root / "task1/config/goal3"
        ev.mkdir(parents=True)
        cfg.mkdir(parents=True)
        raw = {"SYNTHETIC": [[0, 10], [[121.34, 31.35], [121.341, 31.35]]]}
        (ev / "split_manifest.json").write_text(json.dumps({"partitions": {"SYNTHETIC": list(raw)},
            "raw_sha256": "SYNTHETIC", "g2_diagnostics_path": "cards.json"}))
        (cfg / "contract.json").write_text('{}')
        (ev / "a_candidate_plan.json").write_text('{}')
        (root / "cards.json").write_text(json.dumps({"SYNTHETIC": {"stratum": "SYNTHETIC"}}))
        definition = {"R0": {"parameters": {"dt": 30, "distance": 400, "min_points": 2,
            "min_length": 0, "direction": 35, "dp": 5}, "order": "S-D-P", "conditional_rule": None}}
        observed = {"role_context": "/root/c_protocol", "issue_id": "G3-C06",
            "classification": "SYNTHETIC_ARCHIVE_ENGINEERING_TEST; no dataset experiment",
            "target": {"path": "task1/goal3/runtime.py", "sha256": hashlib.sha256(original.read_bytes()).hexdigest()},
            "fixture_scope": "temporary non-Git root; source/partition/raw fixtures; real subprocess Git call",
            "new_model_calls": 0}
        with patch.multiple(runtime, ROOT=root, EV=ev, CFG=cfg, definitions=lambda: definition,
                            source_snapshot=lambda: {}, raw_data=lambda: raw, execution_gate=lambda *args: None):
            try:
                runtime.evaluate("SYNTHETIC_RECOMPUTE", "FULL_PRODUCTION", ["R0"],
                                 output=ev / "recompute", allow_recompute=True)
            except subprocess.CalledProcessError as exc:
                observed.update(status="REPRODUCED", error_type=type(exc).__name__,
                                command=exc.cmd, returncode=exc.returncode,
                                before_any_processing=True)
            except Exception as exc:
                observed.update(status="DIFFERENT_BEHAVIOR", error_type=type(exc).__name__, message=str(exc))
            else:
                observed.update(status="NOT_REPRODUCED")
        observed["closure_requirements"] = [
            "A source-bound portable FULL_RECOMPUTE succeeds without .git and records honest frozen-source identity",
            "Absent or mismatched frozen source binding is rejected; no unverified code SHA fabrication",
            "A normal repository run records actual Git HEAD",
            "Dependent previous-epoch runs remain historical; affected valid runs are rebuilt and independently reviewed",
            "Final ZIP isolated full Notebook recomputation actually succeeds"]
        out = Path(__file__).with_name("G3-C06_failure.json")
        if out.exists():
            raise RuntimeError("Historical failure evidence already exists; do not overwrite")
        out.write_text(json.dumps(observed, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(observed, ensure_ascii=False))


if __name__ == "__main__":
    main()
