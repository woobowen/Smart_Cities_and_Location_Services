"""Independent C acceptance of two concrete implementation repairs, not new LIVE runs."""
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import digest, read_json, write_json, now
from task1.workflow.g2_journal import task_sources

HERE = Path(__file__).parent


def bound(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def main():
    before = read_json(HERE / "core_receipt.json")
    current = {p: digest(ROOT / p) for p in task_sources("core")}
    changed = [p for p in current if current[p] != before["source_hashes"].get(p)]
    assert set(current) == set(before["source_hashes"])
    assert changed == ["task1/workflow/g2_modes.py"]
    target = ROOT / changed[0]
    assert digest(target) == "31e936448918b943dca3cfdc8e4590eb64da2c48b262899040862d7b1533704e"
    tree = ET.parse(HERE / "core_epoch02_tests.xml")
    cases = tree.findall(".//testcase")
    assert len(cases) == 91 and all(not list(c) for c in cases)

    historical_issue = read_json(HERE / "issue_context_001.json")
    old_episode = ROOT / historical_issue["affected_artifacts"][0]["path"]
    assert digest(old_episode) == historical_issue["affected_artifacts"][0]["sha256"]
    assert historical_issue["observed_failed_bindings"] == 13
    superseded = ROOT / "task1/evidence/goal2/superseded_runs.json"
    supersession = read_json(superseded)
    assert len(supersession["runs"]) == 4
    for row in supersession["runs"]:
        manifest = ROOT / "task1/evidence/goal2/runs" / row["run_id"] / "manifest.json"
        assert digest(manifest) == row["original_manifest_sha256"]
        assert "SUPERSEDED" in row["status"]
    interrupted = ROOT / ("task1/evidence/goal2/runs/g2-development-modes-01/modes/"
                          "DEVELOPMENT-llm+memory+search-e1-b0/round3_call/attempt01/receipt.json")
    old_diagnostic = read_json(interrupted)
    assert old_diagnostic["error"] == "KeyboardInterrupt:"
    old_log = ROOT / "task1/evidence/goal2/logs/g2-development-modes-01.log"
    assert "EXTERNAL_AUTH_PERMISSION_OR_BILLING_BLOCKED" in old_log.read_text()

    shared = {
        "status": "VERIFIED", "role_context": "/root/c_contract", "reviewed_at": now(),
        "classification": "INDEPENDENT_IMPLEMENTATION_REPAIR_ACCEPTANCE_NOT_FORMAL_EXPERIMENT_ACCEPTANCE",
        "targets": [bound(target)], "source_hashes": {changed[0]: digest(target)},
        "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch"],
        "tests": {"passed": len(cases), "failed": 0,
                  "result": bound(HERE / "core_epoch02_tests.xml"),
                  "program": bound(HERE / "test_g2_modes_independent.py")},
        "real_model_calls_during_review": 0,
        "independence": "Root repaired production; C independently authored and executed fixtures and read-only actual-failure checks.",
        "unchecked_components": ["new source epoch formal experiments and LIVE episodes", "parent development_modes acceptance"],
        "parent_recovery_condition": "Implementation defect is repaired. Parent must remain unverified until new code is committed, fresh deterministic runs and new LIVE episodes complete, and independent run receipts are accepted.",
        "superseded_old_runs": bound(superseded),
    }
    context = dict(shared, issue_id="G2-C-CONTEXT-001", parent_task="development_modes",
                   historical_failure=bound(HERE / "issue_context_001.json"),
                   historical_episode_preserved=bound(old_episode),
                   repair="Deep-copy prior proposal history and compute a single immutable context hash before dispatch.",
                   regression="Two synthetic records, three causally sequential feedback rounds, two fresh episodes; every recorded hash equals exact serialized provider prompt context. Old actual 13-mismatch evidence remains preserved.")
    context["checked_components"] = shared["checked_components"] + ["serialized_prompt_context_binding", "all_rows_share_pre_dispatch_hash", "old_actual_failure_preserved"]
    write_json(HERE / "context_closure_epoch02.json", context, exclusive=True)
    retry = dict(shared, issue_id="G2-B-RETRY-CLASSIFIER-001", parent_task="core",
                 actual_interrupted_receipt=bound(interrupted), original_misclassified_log=bound(old_log),
                 actual_failure="A KeyboardInterrupt was incorrectly classified as AUTH by matching an unrelated full-receipt numeric substring; this was not an external authentication failure.",
                 repair="Classify only explicit error, stderr and error/turn.failed event fields; interruption precedes service classification; numeric statuses require boundaries.",
                 regression="Archived real interrupt receipt read-only replay is INTERRUPTED with one diagnostic read and zero model requests. Identity/hash/usage digits cannot create authorization or retry signals; ordinary model payload cannot turn a schema rejection into an auth block. Real auth, protocol and transient controls remain verified.")
    retry["checked_components"] = shared["checked_components"] + ["actual_archived_interrupt_classification", "hash_usage_nonerror_payload_exclusion", "bounded_transient_retry", "no_auth_retry"]
    write_json(HERE / "retry_classifier_closure_epoch02.json", retry, exclusive=True)

    core = dict(before)
    core.update(reviewed_at=now(), source_hashes=current,
                targets=[bound(target), bound(HERE / "core_epoch02_tests.xml"),
                         bound(HERE / "core_numeric_current.json"), bound(HERE / "core_boundary_tests.xml"),
                         bound(HERE / "context_closure_epoch02.json"), bound(HERE / "retry_classifier_closure_epoch02.json")],
                source_change_assessment={"changed": changed,
                    "unchanged_mathematical_dependency_hashes": {p: h for p, h in current.items() if p not in changed},
                    "reused_unchanged_core_evidence": "42 independently reconstructed exposed-pilot/order runs and 89 numerical boundary tests; byte-identical mathematical implementation and contract. These remain implementation probes, not new experiments."},
                tests=[before["tests"][0], {"suite": "independent modes/memory/selection, provenance, controller plus actual interruption classifier regression", "passed": 91, "path": "task1/evidence/goal2/c_contract/core_epoch02_tests.xml"}],
                issue_closure_receipts=["context_closure_epoch02.json", "retry_classifier_closure_epoch02.json"],
                closure_condition="Root must consume the two current implementation closure receipts and resume pending parent tasks; this receipt enables fresh epoch execution and does not accept any new formal run.",
                supersedes="core_receipt.json")
    core["checked_components"] = before["checked_components"] + ["immutable_feedback_context_hash", "truthful_interrupt_classification", "actual_failure_preservation"]
    write_json(HERE / "core_receipt_epoch02.json", core, exclusive=True)
    print(json.dumps({"status": "VERIFIED", "independent_tests": len(cases), "changed_sources": changed,
                      "receipts": ["context_closure_epoch02.json", "retry_classifier_closure_epoch02.json", "core_receipt_epoch02.json"], "new_model_calls": 0}))


if __name__ == "__main__":
    main()
