"""C-owned isolated fault probes; never mutates the actual G2 journal or code."""
import json
from pathlib import Path
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import task1.workflow.g2_journal as subject
from task1.workflow.io import digest


@pytest.fixture
def context():
    with tempfile.TemporaryDirectory(prefix="control-fixture-", dir=OUT) as temporary:
        directory = Path(temporary)
        journal = subject.G2Journal(directory / "journal")
        journal.dispatch_role("C", "/root/c_fixture", "test", "ENGINEERING_TEST")
        artifact = directory / "artifact.json"
        artifact.write_text("{}")
        yield journal, directory, artifact


def valid_receipt(journal, directory, artifact, task="handoff"):
    value = {"role_context": "/root/c_fixture", "status": "VERIFIED",
             "checked_components": subject.REQUIRED_COMPONENTS[task],
             "source_hashes": {path: digest(ROOT / path) for path in subject.task_sources(task)},
             "targets": [journal.attach(artifact)]}
    path = directory / "review.json"
    path.write_text(json.dumps(value))
    return path, value


def test_genuine_target_receipt_accepts(context):
    journal, directory, artifact = context
    journal.submit("handoff", [artifact])
    path, _ = valid_receipt(journal, directory, artifact)
    journal.accept("handoff", path, "C:/root/c_fixture")
    assert journal.state["tasks"]["handoff"]["status"] == "VERIFIED"
    assert journal.checkpoint() == "IMPLEMENTING"


@pytest.mark.parametrize("change", ["missing_component", "wrong_epoch", "wrong_actor", "wrong_target", "empty_targets"])
def test_single_receipt_defect_rejected(context, change):
    journal, directory, artifact = context
    journal.submit("handoff", [artifact])
    path, value = valid_receipt(journal, directory, artifact)
    if change == "missing_component":
        value["checked_components"] = value["checked_components"][:-1]
    elif change == "wrong_epoch":
        first = next(iter(value["source_hashes"]))
        value["source_hashes"][first] = "0" * 64
    elif change == "wrong_actor":
        value["role_context"] = "/root/not_registered"
    elif change == "wrong_target":
        other = directory / "other.json"
        other.write_text("{}")
        value["targets"] = [journal.attach(other)]
    else:
        value["targets"] = []
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        journal.accept("handoff", path, "C:/root/c_fixture")


def test_empty_submission_rejected(context):
    journal, _, _ = context
    with pytest.raises(ValueError):
        journal.submit("handoff", [])


def test_unmet_dependency_rejected(context):
    journal, _, artifact = context
    with pytest.raises(ValueError):
        journal.submit("contract", [artifact])


def test_wrong_state_rejected(context):
    journal, directory, artifact = context
    journal.submit("handoff", [artifact])
    path, _ = valid_receipt(journal, directory, artifact)
    journal.state["tasks"]["handoff"]["status"] = "PENDING"
    with pytest.raises(ValueError):
        journal.accept("handoff", path, "C:/root/c_fixture")


def test_real_source_change_rejected_before_accept(context, monkeypatch):
    journal, directory, artifact = context
    controlled_source = directory / "source.py"
    controlled_source.write_text("value = 1\n")
    relative = str(controlled_source.relative_to(ROOT))
    monkeypatch.setattr(subject, "task_sources", lambda task: [relative])
    journal.submit("handoff", [artifact])
    path, _ = valid_receipt(journal, directory, artifact)
    controlled_source.write_text("value = 2\n")
    with pytest.raises(ValueError):
        journal.accept("handoff", path, "C:/root/c_fixture")


def test_real_source_change_rejected_at_checkpoint(context, monkeypatch):
    journal, directory, artifact = context
    controlled_source = directory / "source.py"
    controlled_source.write_text("value = 1\n")
    relative = str(controlled_source.relative_to(ROOT))
    monkeypatch.setattr(subject, "task_sources", lambda task: [relative])
    journal.submit("handoff", [artifact])
    path, _ = valid_receipt(journal, directory, artifact)
    journal.accept("handoff", path, "C:/root/c_fixture")
    controlled_source.write_text("value = 2\n")
    with pytest.raises(ValueError):
        journal.checkpoint()


def test_added_source_requires_new_review(context, monkeypatch):
    journal, directory, artifact = context
    controlled_source = directory / "source.py"
    controlled_source.write_text("value = 1\n")
    sources = [str(controlled_source.relative_to(ROOT))]
    monkeypatch.setattr(subject, "task_sources", lambda task: sources.copy())
    journal.submit("handoff", [artifact])
    path, _ = valid_receipt(journal, directory, artifact)
    journal.accept("handoff", path, "C:/root/c_fixture")
    new_source = directory / "new_dependency.py"
    new_source.write_text("value = 2\n")
    sources.append(str(new_source.relative_to(ROOT)))
    with pytest.raises(ValueError):
        journal.checkpoint()


def test_publication_requires_all_required_tasks(context):
    journal, _, _ = context
    # Even a purported final-review marker cannot replace the full task registry.
    for row in journal.state["tasks"].values():
        row["status"] = "VERIFIED"
    journal.state["tasks"]["publication"]["status"] = "PENDING"
    journal.state["tasks"]["evaluation_orders"]["status"] = "PENDING"
    assert not journal.ready("publication")


def test_issue_repair_requires_nonempty_targets(context):
    journal, _, _ = context
    journal.issue("FIXTURE", "handoff", "synthetic", "test", [], "B:fixture", "C:test")
    with pytest.raises(ValueError):
        journal.repair("FIXTURE", [])


def issue_receipt(journal, directory, artifact):
    value = {"role_context": "/root/c_fixture", "status": "VERIFIED", "issue_id": "FIXTURE",
             "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch"],
             "source_hashes": dict(journal.state["issues"]["FIXTURE"]["repair_source_hashes"]),
             "targets": [journal.attach(artifact)]}
    path = directory / "issue_review.json"
    path.write_text(json.dumps(value))
    return path, value


def test_genuine_issue_closure_resumes_parent_without_verifying_it(context):
    journal, directory, artifact = context
    journal.issue("FIXTURE", "handoff", "synthetic", "test", [journal.attach(artifact)], "B:fixture", "C:test")
    journal.repair("FIXTURE", [artifact])
    path, _ = issue_receipt(journal, directory, artifact)
    journal.close_issue("FIXTURE", path, "C:/root/c_fixture")
    assert journal.state["issues"]["FIXTURE"]["status"] == "VERIFIED"
    assert journal.state["tasks"]["handoff"]["status"] == "PENDING"


@pytest.mark.parametrize("change", ["wrong_actor", "missing_component", "wrong_epoch"])
def test_issue_closure_checks_actor_coverage_epoch(context, change):
    journal, directory, artifact = context
    journal.issue("FIXTURE", "handoff", "synthetic", "test", [journal.attach(artifact)], "B:fixture", "C:test")
    journal.repair("FIXTURE", [artifact])
    path, value = issue_receipt(journal, directory, artifact)
    if change == "wrong_actor":
        value["role_context"] = "/root/not_registered"
    elif change == "missing_component":
        value["checked_components"] = ["unrelated_dummy_check"]
    else:
        value["source_hashes"][next(iter(value["source_hashes"]))] = "0" * 64
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        journal.close_issue("FIXTURE", path, "C:/root/c_fixture")
