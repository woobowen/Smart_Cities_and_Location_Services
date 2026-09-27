"""Independent C read-only Git/HTTP check of the actually published artifact."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
from urllib.parse import quote
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPOSITORY = "https://github.com/woobowen/Smart_Cities_and_Location_Services.git"
ARTIFACT = "029aa30bfb00253173de8284468f8964e5e17ce3"


def read(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def verify_remote_file(row):
    path = row["path"]
    url = ("https://raw.githubusercontent.com/woobowen/"
           "Smart_Cities_and_Location_Services/" + ARTIFACT + "/" + quote(path))
    assert url == row["fixed_url"]
    expected = git("show", ARTIFACT + ":" + path)
    with urlopen(url, timeout=60) as response:
        actual = response.read()
        status = response.status
        actual_url = response.url
    assert status == 200 and actual_url == url and actual == expected, path
    assert digest(actual) == row["sha256"] and len(actual) == row["bytes"], path
    extra = {}
    if path.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(actual)) as archive:
            assert archive.testzip() is None
            assert len(archive.namelist()) == len(set(archive.namelist())) == 116
            manifest = json.loads(archive.read("PACKAGE_MANIFEST.json"))
            assert manifest["submission_status"] == "NOT_READY"
            assert manifest["sent_to_teacher"] is False
            for report in ("experiment1", "process1"):
                member = f"task1/reports/{report}/{report}.pdf"
                assert archive.read(member) == git("show", ARTIFACT + ":" + member)
            extra = {"remote_ZIP_CRC": "PASS", "members": 116,
                     "remote_ZIP_PDFs_equal_same_commit_reports": True,
                     "remote_ZIP_submission": "NOT_READY", "sent_to_teacher": False}
    return {"path": path, "fixed_url": url, "http_status": status,
            "bytes": len(actual), "sha256": digest(actual),
            "equals_committed_blob": True, **extra}


def main():
    output = HERE / "publication_task_receipt.json"
    assert not output.exists(), "Do not overwrite an original C publication receipt"
    packet_path = BASE / "publication_review_submission.json"
    packet = read(packet_path)
    state = read(ROOT / "task1/evidence/goal3/goal_state.json")
    current = state["tasks"]["publication"]
    assert packet["task"] == "publication" and packet["artifact_commit"] == ARTIFACT
    assert current["status"] == "REVIEW_PENDING" and current["author"] == "B:root"
    assert current["targets"] == packet["targets"]
    assert current["source_hashes"] == packet["source_hashes"]
    for target in packet["targets"]:
        assert sha(ROOT / target["path"]) == target["sha256"], target["path"]
    for path, expected in packet["source_hashes"].items():
        assert sha(ROOT / path) == expected, path
        assert digest(git("show", ARTIFACT + ":" + path)) == expected, path
    internal = read(HERE / "internal_acceptance_receipt.json")
    accepted = state["tasks"]["internal_acceptance"]
    assert accepted["status"] == "BLOCKED_EXTERNAL"
    assert accepted["verifier"] == "/root/c_independent"
    assert accepted["receipt"]["sha256"] == sha(HERE / "internal_acceptance_receipt.json")
    assert internal["tasks"]["internal_acceptance"]["engineering_checks"] == "PASS"
    internal_part = internal["tasks"]["internal_acceptance"]
    for row in internal_part["targets"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    for path, expected in internal_part["source_hashes"].items():
        assert sha(ROOT / path) == expected, path

    record = read(BASE / "PUBLICATION_RECORD.json")
    local = git("rev-parse", "HEAD").decode().strip()
    tracking = git("rev-parse", "origin/main").decode().strip()
    remote_lines = git("ls-remote", "--exit-code", "origin", "refs/heads/main").decode().splitlines()
    assert len(remote_lines) == 1
    remote, remote_ref = remote_lines[0].split()
    assert remote_ref == "refs/heads/main" and local == tracking == remote == ARTIFACT
    assert git("branch", "--show-current").decode().strip() == "main"
    assert git("remote", "get-url", "origin").decode().strip() == REPOSITORY
    assert record["repository"] == REPOSITORY and record["branch"] == "main"
    for key in ("CLOSEOUT_ARTIFACT_SHA", "local_HEAD_at_check", "origin_main_at_check", "actual_remote_main_at_check"):
        assert record[key] == ARTIFACT, key
    assert record["NUMERIC_CODE_SHA"] == "e12f8a27944210adb452730be92a0674dfc6b84b"
    assert record["DOCUMENT_BUILD_CODE_SHA"] == "3912f4da2a21ea9da26f75acb6434d889e480462"
    assert record["historical_numeric_ARTIFACT_SHA"] == "fd559e451291b9d424682853ef0909aa5eb94b32"
    assert record["GPT_SECOND_REVIEW"] == "PENDING" and record["Understanding"] == "LEARNING"
    assert record["Submission"] == "NOT_READY" and record["sent_to_teacher"] is False
    assert len(record["files"]) == len({r["path"] for r in record["files"]}) == 10
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(verify_remote_file, record["files"]))
    # The artifact remains the same actual branch tip at the end of this check.
    assert git("rev-parse", "HEAD").decode().strip() == ARTIFACT
    assert git("ls-remote", "--exit-code", "origin", "refs/heads/main").decode().split()[0] == ARTIFACT
    part = {
        "status": "VERIFIED", "targets": packet["targets"],
        "source_hashes": packet["source_hashes"], "checked_components": [
            "Actual independent Git checks: exact approved repository/main and Local HEAD=origin/main=actual remote main=already published artifact029aa30bfb00253173de8284468f8964e5e17ce3, both before and after HTTP verification.",
            "All2 submitted targets and10 immutable sources checked against current bytes; source bytes also match the actual artifact commit. Internal C220 targets/258 sources remain unchanged and its limited engineering PASS was actually accepted before publication.",
            "Independent fresh HTTP GETs for all10 fixed-commit files, including both complete PDFs, both Notebooks and the15.78MB ZIP: all200 and byte-identical to committed blobs and the publisher record. This does not rely on B's HTTP result alone.",
            "The remote ZIP itself reopened in memory: all116 members unique, CRC passes, both bundled PDF bytes match the same remote commit reports, Submission NOT_READY and sent_to_teacher=false.",
            "NUMERIC_CODE_SHA, historical numeric ARTIFACT_SHA, document build3912f4d, package content ID and current closeout artifact are kept distinct. No new numerical/model execution was used for publication verification.",
            "No Evidence Lock, final course PASS, new webpageGPT acceptance, user Understanding acceptance or teacher submission is implied. The later metadata commit is not predicted; final actual HEAD/remote must be verified after that publication.",
        ],
    }
    receipt = {
        "role_context": "/root/c_independent",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "tasks": {"publication": part},
        "submission": {"path": str(packet_path.relative_to(ROOT)), "sha256": sha(packet_path)},
        "repository": REPOSITORY, "branch": "main", "artifact_commit": ARTIFACT,
        "local_HEAD_at_check": local, "origin_main_at_check": tracking,
        "actual_remote_main_at_check": remote, "remote_files": results,
        "fresh_internal_binding_check": {"targets": len(internal_part["targets"]),
                                          "sources": len(internal_part["source_hashes"]),
                                          "C_receipt_sha256": sha(HERE / "internal_acceptance_receipt.json")},
        "observed_mutable_Journal_sha256": sha(ROOT / "task1/evidence/goal3/goal_state.json"),
        "checker": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": sha(Path(__file__))},
        "independent_states": internal["independent_states"],
        "scope_limit": "Publication engineering VERIFIED. Process Evidence still externally blocked; FINAL_REVIEW/LEARNING/NOT_READY and newGPTsecond PENDING. Future metadata publication and its final SHA are outside this already completed artifact check.",
    }
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"task": "publication", "status": "VERIFIED", "remote_files": len(results),
                      "artifact_commit": ARTIFACT, "targets": len(packet["targets"]),
                      "sources": len(packet["source_hashes"])}))


if __name__ == "__main__":
    main()
