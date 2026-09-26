"""Independent C fault injection into disposable G2 journal fixtures only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from task1.workflow.g2_journal import G2Journal


def main():
    reports = []
    for case in ("unmet_dependency", "empty_evidence", "missing_required_coverage", "stale_source_receipt"):
        with tempfile.TemporaryDirectory(prefix="journal-fixture-", dir=OUT) as temporary:
            directory = Path(temporary)
            journal = G2Journal(directory / "journal")
            target = directory / "target.json"
            target.write_text("{}")
            paths = [] if case == "empty_evidence" else [target]
            task = "publication" if case == "unmet_dependency" else "core"
            try:
                journal.submit(task, paths)
                receipt = directory / "receipt.json"
                receipt.write_text(json.dumps({
                    "status": "VERIFIED", "checked_components": ["unrelated_dummy_check"],
                    "targets": [journal.attach(path) for path in paths],
                    "source_hashes": {"task1/workflow/g2_pipeline.py": "0" * 64},
                }))
                journal.accept(task, receipt, "C:synthetic_test_context")
                accepted, reason = True, None
            except Exception as exc:
                accepted, reason = False, str(exc)
            reports.append({"test": case, "classification": "ENGINEERING_TEST_FAULT_INJECTION",
                            "accepted": accepted, "expected": "REJECTED",
                            "actual_status": journal.state["tasks"][task]["status"], "reason": reason,
                            "pending_dependencies": [name for name in journal.state["tasks"][task]["depends_on"]
                                                     if journal.state["tasks"][name]["status"] != "VERIFIED"]})
    source = ROOT / "task1/workflow/g2_journal.py"
    summary = {
        "status": "ISSUE_OPEN" if any(row["accepted"] for row in reports) else "FAULT_INJECTIONS_REJECTED",
        "issue_id": "G2-C-CONTROL-001", "parent_task": "core",
        "classification": "ENGINEERING_TEST_FINDING_NOT_PRODUCTION_RUN",
        "fact": "Initial G2Journal.accept accepts empty target sets, unrelated check coverage, unsatisfied task prerequisites and a wrong source-hash claim.",
        "violated_clause": "Prompt sections 6,15,17 A12/A14; preserve target-specific review closure guards",
        "target_path": str(source.relative_to(ROOT)), "target_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "tests": reports, "repairer": "B-Repair:root", "verifier": "C:/root/c_contract",
        "affected_artifacts": ["future G2 task closure and final acceptance"],
        "closure_standard": ["nonempty exact submitted targets", "ready dependencies and expected transition",
                             "task-specific mandatory coverage", "real registered independent actor",
                             "frozen source/contract/split version binding checked at accept/checkpoint",
                             "fault injections reject and genuine target receipt succeeds"],
        "checked_components": ["current accept path combined fault injections"],
        "unchecked_components": ["full Goal controller behavior", "individual isolation of each missing guard after repair"],
        "probe_development_note": "The first probe used an external /tmp target and was correctly rejected by EVIDENCE_PATH_REQUIRED; fixtures now live inside the assigned C evidence directory.",
    }
    destination = OUT / ("issue_control_001.json" if summary["status"] == "ISSUE_OPEN" else "control_regression_combined.json")
    if destination.exists() and summary["status"] == "ISSUE_OPEN":
        raise RuntimeError("Preserve the original issue evidence instead of overwriting it")
    destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "results": reports, "output": str(destination.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
