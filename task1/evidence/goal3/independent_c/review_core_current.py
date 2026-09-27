"""C-only validation execution and source-bound controller receipts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.goal3.runtime import source_snapshot

OUT = Path(__file__).resolve().parent
CONTEXT = "/root/c_protocol"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attachment(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    before = source_snapshot()
    test_path = OUT / "test_goal3_independent.py"
    test_hash = sha(test_path)
    xml_path = OUT / "core_final_regression.xml"
    command = [str(ROOT / ".venv/bin/python"), "-m", "pytest", "-q", "task1/tests",
        "task1/evidence/goal2/c_contract/test_control_independent.py",
        "task1/evidence/goal2/c_contract/test_g2_modes_independent.py",
        "task1/evidence/goal2/c_contract/test_g2_provenance_independent.py",
        "task1/evidence/goal3/independent_c/test_goal3_independent.py",
        "--junitxml=" + str(xml_path.relative_to(ROOT))]
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    elapsed = time.perf_counter() - started
    (OUT / "core_final_regression.log").write_text(result.stdout + result.stderr)
    after = source_snapshot()
    errors = []
    if result.returncode:
        errors.append("TEST_FAILURE")
    if before != after or sha(test_path) != test_hash:
        errors.append("SOURCE_CHANGED_DURING_REVIEW")
    suites = ET.parse(xml_path).getroot().findall("testsuite")
    counts = {key: sum(int(s.attrib.get(key, 0)) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    status = "VERIFIED" if not errors else "REJECTED"
    scope = ["G3-C01 equivalent simplicity and pointwise equality",
             "G3-C02 development identity boundary and missing/frozen FINAL gate",
             "G3-C03 source record/value/contract comparability",
             "G3-C04 target/receipt invalidation and multi-issue parent recovery",
             "G3-C05 cache provenance, shard exact scope, exhaustion and recheck",
             "raw routing positive/undefined/invalid cases",
             "S/D versus P-specific comparison and fixed/incumbent protection",
             "synthetic complete scope/shard/summary and genuine trace cache recheck",
             "407 inherited trusted-reference, modes, recovery and tamper regressions"]
    receipt = {"role_context": CONTEXT, "reviewer_role": "Independent C, no core authorship",
               "checked_at_utc": datetime.now(timezone.utc).isoformat(), "status": status,
               "checked_components": scope,
               "unchecked_components": ["actual G3 candidate runs", "selection/final effects",
                                        "full production outputs", "reports/package/publication"],
               "source_hashes": before,
               "targets": [attachment(ROOT / p) for p in before] + [attachment(test_path), attachment(xml_path)],
               "actual_command": " ".join(str(Path(x).relative_to(ROOT)) if x.startswith(str(ROOT)) else x for x in command),
               "exit_code": result.returncode, "elapsed_seconds": elapsed,
               "test_counts": counts, "errors": errors,
               "classification": "ENGINEERING_TEST; no G3 real candidate processing",
               "new_record_model_calls": 0}
    write("core_receipt.json", receipt)
    if status != "VERIFIED":
        print(json.dumps({"status": status, "counts": counts, "errors": errors}))
        return

    state = json.loads((ROOT / "task1/evidence/goal3/goal_state.json").read_text())
    for issue_id in ("G3-C01", "G3-C02", "G3-C03", "G3-C04", "G3-C05"):
        issue = state["issues"][issue_id]
        assert issue["status"] == "REGRESSION_PENDING"
        for target in issue["repair_targets"]:
            assert sha(ROOT / target["path"]) == target["sha256"]
        write(issue_id + "_closure.json", {
            "role_context": CONTEXT, "issue_id": issue_id, "status": "VERIFIED",
            "checked_at_utc": receipt["checked_at_utc"], "targets": issue["repair_targets"],
            "checked_components": [s for s in scope if issue_id in s] + ["current source epoch full regression"],
            "test_receipt": attachment(OUT / "core_receipt.json"),
            "actual_test_result": counts, "implementation_author": "B:root",
            "reviewer_is_implementation_author": False,
            "scope": "pre-experiment wrapper repair; no G3 experimental artifacts need invalidation"})

    request = json.loads((ROOT / "task1/evidence/goal3/initial_controller_review_targets.json").read_text())
    prior = json.loads((OUT / "contract_split_receipt.json").read_text())
    assert prior["status"] == "VERIFIED"
    parts = {}
    for task, row in request["tasks"].items():
        for target in row["targets"]:
            assert sha(ROOT / target["path"]) == target["sha256"]
        for path, value in row["source_hashes"].items():
            assert sha(ROOT / path) == value
        parts[task] = {"status": "VERIFIED", "targets": row["targets"], "source_hashes": row["source_hashes"],
                       "checked_components": (["actual startup branch/HEAD/remote origin and current remote SHA",
                                                "unchanged original protected ZIP bytes", "raw scope/hash",
                                                "actual user authorization and stage acceptance source identity"] if task == "handoff"
                                               else prior["checked"]),
                       "unchecked_components": ["external webpage tool logs not supplied", "source datum", "future experimental effects"]}
    startup = json.loads((ROOT / "task1/evidence/goal3/startup.json").read_text())
    protected = {p: sha(ROOT / p) == value for p, value in startup["untracked_protected"].items()}
    assert all(protected.values())
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True).strip()
    local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True).strip()
    assert remote.split()[0] == local == startup["head"]
    assert origin == startup["remote_url"]
    write("contract_controller_receipt.json", {"role_context": CONTEXT, "status": "VERIFIED",
        "checked_at_utc": receipt["checked_at_utc"], "tasks": parts,
        "prior_evidence": [attachment(OUT / "initial_inventory_receipt.json"), attachment(OUT / "contract_split_receipt.json")],
        "actual_startup_recheck": {"local_head": local, "remote_ls_remote": remote, "origin": origin,
                                   "protected_bytes_unchanged": protected},
        "not_new_human_approval": True})
    print(json.dumps({"status": status, "counts": counts, "elapsed_seconds": elapsed,
                      "closures": ["G3-C01", "G3-C02", "G3-C03", "G3-C04", "G3-C05"],
                      "controller_tasks": list(parts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
