"""Independent C06 archive checks, using explicitly synthetic small raw inputs."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from task1.goal3 import runtime

ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def portable_root(tmp_path, monkeypatch):
    ev, cfg = tmp_path / "task1/evidence/goal3", tmp_path / "task1/config/goal3"
    ev.mkdir(parents=True)
    cfg.mkdir(parents=True)
    raw = {"C06_SYNTHETIC": [[0, 10, 20], [[121.34, 31.35], [121.3401, 31.35], [121.3402, 31.35]]]}
    (ev / "split_manifest.json").write_text(json.dumps({"partitions": {"SYNTHETIC": list(raw)},
        "raw_sha256": "SYNTHETIC", "g2_diagnostics_path": "cards.json"}))
    (cfg / "contract.json").write_text('{"classification":"SYNTHETIC_ENGINEERING_TEST"}')
    (ev / "a_candidate_plan.json").write_text('{}')
    (tmp_path / "cards.json").write_text(json.dumps({"C06_SYNTHETIC": {"stratum": "SYNTHETIC"}}))
    (tmp_path / "bound_source.py").write_text('# Synthetic source identity fixture\n')
    source = {"bound_source.py": hashlib.sha256((tmp_path / "bound_source.py").read_bytes()).hexdigest()}
    frozen = {"processing_code_sha": "a" * 40, "processing_source_hashes": source, "bindings": source}
    (ev / "production_freeze.json").write_text(json.dumps(frozen))
    definition = {"R0": {"parameters": {"dt": 30, "distance": 400, "min_points": 2,
        "min_length": 0, "direction": 35, "dp": 5}, "order": "S-D-P", "conditional_rule": None}}
    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    monkeypatch.setattr(runtime, "EV", ev)
    monkeypatch.setattr(runtime, "CFG", cfg)
    monkeypatch.setattr(runtime, "source_snapshot", lambda: deepcopy(source))
    monkeypatch.setattr(runtime, "definitions", lambda: deepcopy(definition))
    monkeypatch.setattr(runtime, "raw_data", lambda: deepcopy(raw))
    monkeypatch.setattr(runtime, "execution_gate", lambda *args: None)
    # Git is not patched: success proves this portable branch does not need it.
    return tmp_path, ev, source


def test_frozen_portable_full_processing_without_git(portable_root):
    root, ev, source = portable_root
    assert not (root / ".git").exists()
    m = runtime.evaluate("C06_SYNTHETIC_RECOMPUTE", "FULL_PRODUCTION", ["R0"],
                         output=ev / "recomputed", allow_recompute=True)
    assert m["status"] == "MACHINE_VERIFIED_PENDING_C"
    assert m["code_sha"] == "a" * 40 and m["code_identity_source"] == "FROZEN_SOURCE_BUNDLE"
    assert m["processing_evaluations"] == 1 and m["record_metrics"]["R0"]["n_input"] == 3
    assert m["new_record_model_calls"] == 0


def test_missing_freeze_rejected(portable_root):
    root, ev, source = portable_root
    (ev / "production_freeze.json").unlink()
    with pytest.raises(FileNotFoundError):
        runtime.code_identity(source, "FULL_PRODUCTION", True)


@pytest.mark.parametrize("value", ["not-a-sha", "a" * 39, 123, None])
def test_invalid_frozen_sha_rejected(portable_root, value):
    root, ev, source = portable_root
    p = ev / "production_freeze.json"
    frozen = json.loads(p.read_text())
    frozen["processing_code_sha"] = value
    p.write_text(json.dumps(frozen))
    with pytest.raises(ValueError, match="PORTABLE_PROCESSING_IDENTITY_MISMATCH"):
        runtime.code_identity(source, "FULL_PRODUCTION", True)


def test_wrong_frozen_source_map_rejected(portable_root):
    root, ev, source = portable_root
    with pytest.raises(ValueError, match="PORTABLE_PROCESSING_IDENTITY_MISMATCH"):
        runtime.code_identity({**source, "extra.py": "0" * 64}, "FULL_PRODUCTION", True)


def test_changed_frozen_source_bytes_rejected(portable_root):
    root, ev, source = portable_root
    (root / "bound_source.py").write_text('# Mutated source fixture\n')
    with pytest.raises(ValueError, match="SOURCE_OR_CONTRACT_CHANGED_NEW_RUN_REQUIRED"):
        runtime.code_identity(source, "FULL_PRODUCTION", True)


def test_portable_development_cannot_bypass_freeze(portable_root):
    root, ev, source = portable_root
    with pytest.raises(ValueError, match="PORTABLE_RECOMPUTE_REQUIRES_FROZEN_PRODUCTION"):
        runtime.code_identity(source, "G3_DEVELOPMENT", True)


def test_nonrecompute_does_not_fake_git_identity(portable_root):
    root, ev, source = portable_root
    with pytest.raises(subprocess.CalledProcessError):
        runtime.code_identity(source, "FULL_PRODUCTION", False)


def test_repository_run_records_actual_head():
    expected = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert runtime.code_identity(runtime.source_snapshot(), "G3_DEVELOPMENT", False) == {
        "code_sha": expected, "code_identity_source": "ACTUAL_LOCAL_GIT_HEAD"}
