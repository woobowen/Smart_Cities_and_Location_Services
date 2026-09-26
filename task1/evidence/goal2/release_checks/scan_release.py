"""Bounded, read-only Goal 2 publication checks; no research-acceptance claim.

Adapted from the existing Goal 1 release_checks.py.  The only writes are new
receipts below this directory.  Use a new output directory for every snapshot.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
from importlib import metadata
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "task1/evidence/goal2/release_checks"
EV = ROOT / "task1/evidence/goal2"
ANCHOR = "a45d89f49f2041477b16485f535adc508c32f8ea"
BUNDLE_SCRIPT = "evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py"
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsonl", ".log", ".xml", ".ipynb", ".csv", ".yaml", ".yml", ".toml", ".svg", ".drawio", ".html", ".tex", ".diff", ".pem", ".key", ".env"}
PATTERNS = {
    "api_token": re.compile(r"(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{32,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential_url": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "bearer_token": re.compile(r"(?i)\bbearer[ \t]+[A-Za-z0-9_.~-]{24,}"),
    "credential_assignment": re.compile(r'''(?i)\b(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|AZURE_OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|ACCESS_TOKEN|PASSWORD)["']?\s*[:=]\s*["'][A-Za-z0-9_./+~=-]{20,}["']'''),
}
ABSOLUTE = re.compile(r"/(?:home|Users)/[^/\s\"'<>]+/[^\s\"'<>]+|/(?:tmp|mnt/data|workspace)/[^\s\"'<>]+|[A-Z]:\\(?:Users|Temp)\\[^\s\"'<>]+")
MD = MarkdownIt("commonmark")


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    def redact(item):
        if isinstance(item, str):
            for pattern in PATTERNS.values():
                item = pattern.sub("[REDACTED_CREDENTIAL_PATTERN]", item)
        elif isinstance(item, list):
            item = [redact(v) for v in item]
        elif isinstance(item, dict):
            item = {redact(k): redact(v) for k, v in item.items()}
        return item
    path.write_text(json.dumps(redact(value), ensure_ascii=False, indent=2) + "\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def relative(path):
    return path.relative_to(ROOT).as_posix()


def cache_file(path):
    return (bool({"__pycache__", ".pytest_cache", ".ipynb_checkpoints"} & set(path.parts))
            or path.suffix in {".pyc", ".pyo", ".swp", ".tmp"}
            or path.name in {".DS_Store", "core"} or path.name.endswith(("~", ":Zone.Identifier")))


def scope(output):
    paths = set()
    for folder in ("task1/evidence/goal2", "task1/config/goal2", "task1/docs/goal2", "task1/notebooks/goal2", "task1/figures/goal2"):
        directory = ROOT / folder
        if directory.exists():
            paths.update(p for p in directory.rglob("*") if (p.is_file() or p.is_symlink()) and not p.is_relative_to(output))
    source_roots = ("task1/workflow", "task1/scripts", "task1/tests", "task1/config", "task1/notebooks", "task1/docs")
    changed = git("diff", "--name-only", "-z", ANCHOR, "--", *source_roots)
    untracked = git("ls-files", "--others", "--exclude-standard", "-z", "--", *source_roots)
    for name in (changed + untracked).decode().split("\0"):
        p = ROOT / name
        if name and (p.is_file() or p.is_symlink()):
            paths.add(p)
    for folder in ("task1/workflow", "task1/scripts", "task1/tests"):
        paths.update(p for p in (ROOT / folder).rglob("*") if p.is_file() and cache_file(p))
    return sorted(paths)


def scan_text(path):
    """Scan all plaintext / decompressed JSON text; never retain matching values."""
    secrets, absolute = set(), set()
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
        tail, lines_read, chars_read = "", 0, 0
        while block := stream.read(65536):
            combined = tail + block
            origin = chars_read - len(tail)
            line_origin = lines_read - tail.count("\n")
            for kind, pattern in PATTERNS.items():
                for match in pattern.finditer(combined):
                    secrets.add((kind, origin + match.start(), line_origin + combined[:match.start()].count("\n") + 1))
            for match in ABSOLUTE.finditer(combined):
                absolute.add(line_origin + combined[:match.start()].count("\n") + 1)
            chars_read += len(block)
            lines_read += block.count("\n")
            tail = combined[-4096:]
    return [{"type": kind, "character_offset": offset, "line": line} for kind, offset, line in sorted(secrets)], sorted(absolute), chars_read


def local_links(path):
    checked, missing = [], []
    tokens = MD.parse(path.read_text())
    for token in tokens:
        for child in token.children or []:
            destination = child.attrGet("href") if child.type == "link_open" else child.attrGet("src") if child.type == "image" else None
            if not destination:
                continue
            url = urlsplit(destination)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            # Local file existence is checked; fragments and external URLs are not fetched.
            row = {"source": relative(path), "destination": destination, "exists": target.exists()}
            checked.append(row)
            if not target.exists():
                missing.append(row)
    return checked, missing


def protection():
    prefixes = ("task1/evidence/goal1", "task1/docs/goal1", "task1/notebooks", "task1/作业", "task1/作业.zip", "task1/实验课1.pptx", "task1/config/goal1.json", "task1/config/pilot.json", "task1/config/conditional_planar.json", "task1/config/goal1_sources.json", "task1/config/requirements-goal1.txt")
    tree = git("ls-tree", "-r", "-z", ANCHOR, "--", *prefixes)
    object_format = git("rev-parse", "--show-object-format").decode().strip()
    rows = []
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        header, name = entry.split(b"\t", 1)
        mode, kind, expected = header.decode().split()
        name = name.decode()
        if kind != "blob":
            continue
        path = ROOT / name
        actual = None
        if path.is_file() and not path.is_symlink():
            h = hashlib.new(object_format)
            h.update(b"blob " + str(path.stat().st_size).encode() + b"\0")
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
            actual = h.hexdigest()
        rows.append({"path": name, "anchor_git_blob": expected, "current_git_blob": actual, "unchanged": actual == expected})
    startup = json.loads((EV / "startup.json").read_text())
    tracked = set(git("ls-files", "-z").decode().split("\0"))
    zips = []
    for name, expected in startup["user_untracked"].items():
        path = ROOT / name
        actual = sha(path) if path.is_file() else None
        zips.append({"path": name, "startup_sha256": expected, "current_sha256": actual, "unchanged": actual == expected, "currently_git_tracked": name in tracked})
    return {"anchor": ANCHOR, "git_object_format": object_format, "tracked_protected_files": rows, "user_supplied_zip_files": zips}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--final", action="store_true", help="Require a stable snapshot and no running non-superseded run; still not C acceptance.")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(BASE) or output == BASE:
        raise ValueError("OUTPUT_MUST_BE_NEW_SUBDIRECTORY_OF_RELEASE_CHECKS")
    output.mkdir(parents=True, exist_ok=False)
    started = now()
    paths = scope(output)
    names = [relative(p) for p in paths]
    tracked = set(git("ls-files", "-z").decode().split("\0"))
    ignored_result = subprocess.run(["git", "check-ignore", "-z", "--stdin"], cwd=ROOT, input=b"\0".join(n.encode() for n in names) + b"\0", capture_output=True)
    if ignored_result.returncode not in (0, 1):
        raise RuntimeError("GIT_IGNORE_CHECK_FAILED")
    ignored = set(ignored_result.stdout.decode().split("\0"))
    inventory, secrets, absolute, broken, links, caches, symlinks, moving, notebook_errors, portable = [], [], [], [], [], [], [], [], [], []
    skipped_binary, text_chars = Counter(), 0
    for path in paths:
        name = relative(path)
        if path.is_symlink():
            symlinks.append(name)
            continue
        try:
            before = path.stat()
            row = {"path": name, "bytes": before.st_size, "sha256": sha(path), "tracked": name in tracked, "ignored": name in ignored}
            if cache_file(path):
                row["classification"] = "CACHE_NOT_SUBSTANTIVE"
                caches.append({"path": name, "tracked": name in tracked, "ignored": name in ignored})
            else:
                row["classification"] = "PROPOSED_G2_SUBSTANTIVE_FILE"
                if path.suffix in TEXT_SUFFIXES or path.name.endswith((".json.gz", ".jsonl.gz")):
                    found, absolute_lines, chars = scan_text(path)
                    text_chars += chars
                    secrets.extend({"path": name, **item} for item in found)
                    if absolute_lines:
                        category = "HISTORICAL_OR_CURRENT_EXECUTION_EVIDENCE" if name.startswith("task1/evidence/") else "REPRODUCTION_SOURCE_REQUIRES_REVIEW"
                        if path.suffix == ".ipynb":
                            notebook = json.loads(path.read_text())
                            code_cells = [i for i, cell in enumerate(notebook.get("cells", [])) if cell.get("cell_type") == "code" and ABSOLUTE.search("".join(cell.get("source", [])))]
                            category = "NOTEBOOK_CODE_DEPENDENCY" if code_cells else "NOTEBOOK_MARKDOWN_OR_RECORDED_OUTPUT"
                        item = {"path": name, "lines": absolute_lines, "classification": category}
                        absolute.append(item)
                        if category in {"REPRODUCTION_SOURCE_REQUIRES_REVIEW", "NOTEBOOK_CODE_DEPENDENCY"}:
                            portable.append(item)
                else:
                    skipped_binary[path.suffix or "no_extension"] += 1
                if path.suffix == ".md":
                    checked, failed = local_links(path)
                    links.extend(checked)
                    broken.extend(failed)
                if name.startswith("task1/notebooks/goal2/") and path.suffix == ".ipynb":
                    notebook = json.loads(path.read_text())
                    for i, cell in enumerate(notebook.get("cells", [])):
                        if any(out.get("output_type") == "error" for out in cell.get("outputs", [])):
                            notebook_errors.append({"path": name, "cell": i})
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                moving.append(name)
            inventory.append(row)
        except (FileNotFoundError, OSError, EOFError, json.JSONDecodeError) as exc:
            moving.append(name)
            inventory.append({"path": name, "scan_error_type": type(exc).__name__, "reason": "File changed or could not be read during bounded snapshot; recheck required."})
    protected = protection()
    write(output / "protected_bytes.json", protected)
    write(output / "scope_inventory.json", inventory)
    bundle = subprocess.run([sys.executable, BUNDLE_SCRIPT, "--check"], cwd=ROOT, text=True, capture_output=True)
    # The existing bundle command prints no credentials; redact patterns defensively.
    bundle_output = bundle.stdout + bundle.stderr
    for pattern in PATTERNS.values():
        bundle_output = pattern.sub("[REDACTED_CREDENTIAL_PATTERN]", bundle_output)
    (output / "bundle_check.txt").write_text(bundle_output)
    environment = json.loads((EV / "environment_record.json").read_text())
    package_checks = []
    for package, recorded in environment["packages"].items():
        expected = recorded.get("version") if isinstance(recorded, dict) else recorded
        try:
            actual = metadata.version(package)
        except metadata.PackageNotFoundError:
            actual = None
        package_checks.append({"package": package, "recorded": expected, "installed": actual, "matches": actual == expected})
    added_during_scan = sorted(relative(p) for p in set(scope(output)) - set(paths))
    running = []
    superseded = json.loads((EV / "superseded_runs.json").read_text()) if (EV / "superseded_runs.json").exists() else {}
    superseded_text = json.dumps(superseded)
    for path in (EV / "runs").glob("*/manifest.json"):
        try:
            manifest = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("status") == "RUNNING":
            running.append({"run_id": manifest["run_id"], "listed_in_superseded_registry": manifest["run_id"] in superseded_text})
    over_50 = [row for row in inventory if row.get("bytes", 0) > 50 * 1024 * 1024]
    over_100 = [row for row in over_50 if row["bytes"] > 100 * 1024 * 1024]
    changed_protected = [row for row in protected["tracked_protected_files"] + protected["user_supplied_zip_files"] if not row["unchanged"]]
    ignored_substantive = [row["path"] for row in inventory if row.get("ignored") and row.get("classification") == "PROPOSED_G2_SUBSTANTIVE_FILE"]
    blockers = {"secret_pattern_findings": len(secrets), "over_100MiB_files": len(over_100), "symlinks_requiring_review": len(symlinks), "broken_local_links": len(broken), "reproduction_absolute_path_findings": len(portable), "protected_byte_changes": len(changed_protected), "tracked_cache_files": sum(row["tracked"] for row in caches), "notebook_error_cells": len(notebook_errors), "bundle_check_failed": int(bundle.returncode != 0), "dependency_inventory_mismatches": sum(not row["matches"] for row in package_checks)}
    if args.final:
        blockers["unstable_snapshot"] = len(moving) + len(added_during_scan)
        blockers["active_running_runs"] = sum(not row["listed_in_superseded_registry"] for row in running)
    has_findings = any(blockers.values())
    report = {"classification": "FINAL_STATIC_PUBLICATION_CHECK" if args.final else "NONFINAL_PUBLICATION_PREPARATION_SNAPSHOT", "status": "FINDINGS_REQUIRE_REVIEW" if has_findings else "STATIC_CHECKS_PASS" if args.final else "SNAPSHOT_CHECKS_PASS_FINAL_RECHECK_REQUIRED", "started_at": started, "ended_at": now(), "head": git("rev-parse", "HEAD").decode().strip(), "branch": git("branch", "--show-current").decode().strip(), "command": ".venv/bin/python " + relative(Path(__file__)) + " --output " + relative(output) + (" --final" if args.final else ""), "scanner_sha256": sha(Path(__file__)), "adapted_from": "task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/release_checks.py", "checked_files": len(inventory), "plaintext_and_decompressed_characters_scanned": text_chars, "secret_scan_policy": "Values are never included in findings or logs. Explicit credential formats only; no account/session directories, decryption, network fetching, binary OCR or general secret-absence guarantee.", "binary_formats_hash_and_size_only": dict(skipped_binary), "blocking_counts": blockers, "secret_pattern_findings": secrets, "over_50MiB_files": over_50, "over_100MiB_files": over_100, "symlinks": symlinks, "absolute_path_findings": absolute, "absolute_path_note": "Evidence records retain observed command/trace paths. Only reproduction sources and Notebook code require portability review; no evidence was altered.", "local_link_scope": "Parsed CommonMark links and images: local file existence checked; fragments and external URLs not fetched.", "local_links_checked": len(links), "broken_local_links": broken, "cache_files": caches, "ignored_substantive_files_need_explicit_staging_review": ignored_substantive, "notebook_error_cells": notebook_errors, "protected_tracked_files": len(protected["tracked_protected_files"]), "protected_user_zip_files": protected["user_supplied_zip_files"], "changed_protected_files": changed_protected, "protected_receipt_sha256": sha(output / "protected_bytes.json"), "inventory_sha256": sha(output / "scope_inventory.json"), "bundle_check": {"command": ".venv/bin/python " + BUNDLE_SCRIPT + " --check", "exit_code": bundle.returncode, "output_sha256": sha(output / "bundle_check.txt")}, "dependency_record": {"path": "task1/evidence/goal2/environment_record.json", "sha256": sha(EV / "environment_record.json"), "registered_installations": {key: environment[key] for key in ["new_system_packages", "new_language_packages", "new_toolchains", "shell_or_environment_config_changes"]}, "package_version_checks": package_checks, "scanner_extra_existing_dependency": {"markdown-it-py": metadata.version("markdown-it-py")}}, "mutated_during_read": moving, "created_during_scan": added_during_scan, "running_runs": running, "remaining_final_checks": ["Repeat this script after all real mode/evaluation runs and current artifacts are frozen.", "Independently verify complete acceptance, final Notebook Run All, figure source/version bindings and actual visual review.", "Recheck final diff and staged contents, including substantive ignored logs; never stage caches or user ZIPs implicitly.", "Verify fixed CODE_SHA/ARTIFACT_SHA and actual pushed remote files after authorized publication."], "scope_limits": ["Static engineering publication preparation is not scientific acceptance or permission to publish.", "Cache files are reported and left untouched; original files and archives are only read.", "Package inventory is checked against the recorded reused environment; this script performs no installations."]}
    write(output / "release_check.json", report)
    print(json.dumps({"status": report["status"], "checked_files": len(inventory), "blocking_counts": blockers, "ignored_substantive_files": len(ignored_substantive), "protected_files": len(protected["tracked_protected_files"]), "report": relative(output / "release_check.json")}, ensure_ascii=False))
    return 1 if has_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
