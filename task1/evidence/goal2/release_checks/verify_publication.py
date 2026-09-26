"""Read actual GitHub refs, tree and fixed-commit file bytes after a push.

No push, credential read, working-tree edit or model invocation occurs here.
An optional new output directory stores observations of an already existing
commit. Without --output, only the session receives the verification record.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

from task1.workflow.io import ROOT, now, write_json

REPOSITORY = "woobowen/Smart_Cities_and_Location_Services"


def run(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"COMMAND_FAILED exit={result.returncode} command={args!r}")
    return result.stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--paths", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.sha):
        raise ValueError("EXACT_COMMIT_SHA_REQUIRED")
    paths = json.loads(args.paths.read_text())
    if not isinstance(paths, list) or not paths or len(paths) != len(set(paths)):
        raise ValueError("NONEMPTY_UNIQUE_PATH_LIST_REQUIRED")
    for path in paths:
        if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError("REPOSITORY_RELATIVE_PATH_REQUIRED")
    output = (ROOT / args.output).resolve() if args.output else None
    if output and (not output.is_relative_to(ROOT / "task1/evidence/goal2/publication") or output.exists()):
        raise ValueError("NEW_GOAL2_PUBLICATION_OUTPUT_DIRECTORY_REQUIRED")
    started = now()
    head = run(["git", "rev-parse", "HEAD"]).decode().strip()
    tracking = run(["git", "rev-parse", "origin/main"]).decode().strip()
    branch = run(["git", "branch", "--show-current"]).decode().strip()
    remote_url = run(["git", "remote", "get-url", "origin"]).decode().strip()
    remote_before = run(["git", "ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
    if branch != "main" or {head, tracking, remote_before} != {args.sha}:
        raise ValueError("LOCAL_TRACKING_ACTUAL_REMOTE_MISMATCH")
    if remote_url != f"https://github.com/{REPOSITORY}.git":
        raise ValueError("UNEXPECTED_REPOSITORY")
    tree_raw = run(["gh", "api", f"repos/{REPOSITORY}/git/trees/{args.sha}?recursive=1"])
    remote_tree = json.loads(tree_raw)
    if remote_tree.get("truncated"):
        raise ValueError("REMOTE_TREE_TRUNCATED")
    remote_blobs = {row["path"]: (row["mode"], row["sha"]) for row in remote_tree["tree"] if row["type"] == "blob"}
    local_blobs = {}
    for row in run(["git", "ls-tree", "-r", "-z", args.sha]).split(b"\0"):
        if not row:
            continue
        fields, path = row.split(b"\t", 1)
        mode, kind, blob = fields.decode().split()
        if kind == "blob":
            local_blobs[path.decode()] = (mode, blob)
    if remote_blobs != local_blobs:
        raise ValueError("FULL_COMMITTED_FILE_TREE_MISMATCH")
    files = []
    for path in paths:
        expected = run(["git", "show", f"{args.sha}:{path}"])
        actual = run(["gh", "api", "-H", "Accept: application/vnd.github.raw+json",
                      f"repos/{REPOSITORY}/contents/{quote(path, safe='/')}?ref={args.sha}"])
        if actual != expected:
            raise ValueError(f"REMOTE_FILE_BYTES_MISMATCH:{path}")
        files.append({"path": path, "bytes": len(actual), "sha256": sha(actual),
                      "git_blob": local_blobs[path][1], "actual_remote_read": True,
                      "url": f"https://github.com/{REPOSITORY}/blob/{args.sha}/{quote(path, safe='/')}"})
    remote_after = run(["git", "ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
    if remote_after != args.sha:
        raise ValueError("REMOTE_ADVANCED_DURING_READBACK")
    report = {"status": "PUBLISHED_VERIFIED", "started_at": started, "ended_at": now(),
              "repository": remote_url, "branch": branch, "verified_commit": args.sha,
              "local_head": head, "origin_main": tracking, "actual_remote_before": remote_before,
              "actual_remote_after": remote_after, "local_remote_equal": True,
              "full_remote_tree_blob_count": len(remote_blobs), "full_committed_tree_equal": True,
              "remote_tree_response_sha256": sha(tree_raw), "fixed_sha_readbacks": files,
              "verification_script_sha256": sha(Path(__file__).read_bytes()),
              "readback_path_list_sha256": sha(args.paths.read_bytes()),
              "self_reference_boundary": "This record observes an already existing commit; it is not claimed to be inside that same commit."}
    if output:
        output.mkdir(parents=True)
        write_json(output / "remote_tree.json", remote_tree)
        write_json(output / "verification.json", report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
