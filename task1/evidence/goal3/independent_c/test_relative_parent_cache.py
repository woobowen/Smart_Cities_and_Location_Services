"""C07 real relative-path and source-epoch recovery checks on synthetic records."""
from pathlib import Path

import pytest

from task1.goal3 import runtime
from task1.workflow.io import digest
from task1.evidence.goal3.independent_c.test_goal3_independent import synthetic_runtime


def test_actual_relative_parent_cache_is_portable(synthetic_runtime, monkeypatch):
    monkeypatch.chdir(runtime.ROOT)
    original = synthetic_runtime / "original"
    runtime.evaluate("C07_ORIGINAL", "G3_DEVELOPMENT", ["R0"], output=original)
    relative_parent = original.relative_to(runtime.ROOT)
    assert not relative_parent.is_absolute()
    replay = runtime.evaluate("C07_RELATIVE", "G3_DEVELOPMENT", ["R0"],
        output=synthetic_runtime / "replay", parent=relative_parent)
    assert replay["processing_evaluations"] == 0 and replay["cached_trace_rechecks"] == 2
    assert replay["parent_cache"]["path"] == str(relative_parent)


def test_old_epoch_parent_rejected_then_new_run_resumes(synthetic_runtime, monkeypatch):
    monkeypatch.chdir(runtime.ROOT)
    original = synthetic_runtime / "original"
    runtime.evaluate("C07_OLD", "G3_DEVELOPMENT", ["R0"], output=original)
    changed_source = runtime.ROOT / "changed_source_fixture.py"
    changed_source.write_text('# Synthetic new source epoch\n')
    monkeypatch.setattr(runtime, "source_snapshot", lambda: {changed_source.name: digest(changed_source)})
    with pytest.raises(ValueError, match="PARENT_CACHE_SCOPE_OR_EPOCH_MISMATCH"):
        runtime.evaluate("C07_STALE", "G3_DEVELOPMENT", ["R0"],
            output=synthetic_runtime / "rejected_old_cache", parent=original.relative_to(runtime.ROOT))
    fresh = synthetic_runtime / "fresh"
    current = runtime.evaluate("C07_FRESH", "G3_DEVELOPMENT", ["R0"], output=fresh)
    assert current["processing_evaluations"] == 2 and current["cached_trace_rechecks"] == 0
    replay = runtime.evaluate("C07_RESUMED", "G3_DEVELOPMENT", ["R0"],
        output=synthetic_runtime / "resumed", parent=fresh.relative_to(runtime.ROOT))
    assert replay["processing_evaluations"] == 0 and replay["cached_trace_rechecks"] == 2
