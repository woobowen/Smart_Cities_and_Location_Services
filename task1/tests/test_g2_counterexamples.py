"""Analytic counterexample content, provenance and no-model replay checks."""
from pathlib import Path

import pytest

from task1.scripts.goal2_counterexamples import run, synthetic_suite
from task1.workflow.io import digest, object_hash, read_json


def test_all_counterexample_families_have_actual_known_answer_results():
    suite = synthetic_suite(object_hash({"purpose": "ENGINEERING_TEST"}))
    assert suite["classification"] == "SYNTHETIC_COUNTEREXAMPLE"
    assert len(suite["cases"]) == 6
    assert suite["known_answer_check_count"] == 25
    assert all(check["passed"] for case in suite["cases"] for check in case["known_answer_checks"])
    assert all(execution["review"]["status"] == "VERIFIED" for case in suite["cases"]
               for execution in case["executions"].values())
    assert all(execution["output"]["classification"] == "SYNTHETIC_COUNTEREXAMPLE"
               for case in suite["cases"] for execution in case["executions"].values())
    assert suite["real_data_accuracy_claim"] is False


def test_true_labels_are_local_to_authored_fixture_and_not_invented_for_time_conflict():
    suite = synthetic_suite(object_hash({"purpose": "ENGINEERING_TEST"}))
    direction = suite["cases"][0]["executions"]
    assert direction["legitimate_zigzag"]["synthetic_detection_counts"]["false_positive"] == 2
    assert direction["injected_spike"]["synthetic_detection_counts"]["true_positive"] == 1
    assert direction["injected_spike"]["synthetic_detection_counts"]["false_positive"] == 1
    assert "synthetic_detection_counts" not in suite["cases"][1]["executions"]["zero_and_time_conflict"]


def test_written_counterexamples_bind_files_and_preserve_previous_run(tmp_path, monkeypatch):
    # An accidental experiment-model request is forbidden even during replay.
    import task1.workflow.provider as provider
    for name in ("LiveProvider", "CodexProvider", "NativeProvider"):
        if hasattr(provider, name):
            monkeypatch.setattr(provider, name, lambda *_args, **_kwargs: pytest.fail("unexpected model provider"))
    manifest = run(tmp_path, include_pilot=False, run_id="ENGINEERING_TEST")
    assert manifest["experiment_model_dispatches"] == 0
    assert manifest["synthetic_pipeline_executions"] == 19
    assert manifest["pilot_pipeline_executions"] == 0
    assert manifest["source_tree_hash"] == object_hash(manifest["source_files"])
    assert all(digest(tmp_path / name) == expected for name, expected in manifest["artifacts"].items())
    assert read_json(tmp_path / "manifest.json")["status"] == "ENGINEERING_VERIFIED"
    with pytest.raises(ValueError, match="OUTPUT_DIRECTORY_NOT_EMPTY"):
        run(tmp_path, include_pilot=False)
