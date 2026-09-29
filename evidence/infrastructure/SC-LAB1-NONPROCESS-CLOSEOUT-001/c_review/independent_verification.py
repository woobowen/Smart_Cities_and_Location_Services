"""Independent C read-only audit of the accepted non-Process closeout."""
from pathlib import Path
import ast
import base64
import collections
import hashlib
import json
import re
import runpy
import subprocess
import sys
import traceback
import urllib.parse

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
TASK = OUT.parent
BASE = "89371f6597f92f7dac9abf61f6f6b18e29ed76cc"
SYNC = Path("evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py")
META = Path("evidence/infrastructure/chatgpt-project-source-sync")
BUNDLE = Path("releases/chatgpt-project-sources")
EXT = Path("evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review")
INPUTS = [
    ("SMART_CITIES_RESEARCH_PROTOCOL.md", "docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md", 13264, "19f9bb4670bc3a485b064854f3d035d2a50a192386be53396851443ee5654a3f"),
    ("SMART_CITIES_REPORT_WRITING_GUIDE.md", "docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md", 25025, "49cb8ac101420a3262734b9ac246451fbb61b9716e8263db2dd8802bd78f5d55"),
    ("SMART_CITIES_VISUAL_SYSTEM.md", "docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md", 43680, "9fbbd62543da77c7cecc31f4e07a95c2570c245693a9817d17652286340d291f"),
    ("WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md", "docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md", 44829, "c3113ff2f8b6a02c95e6e1cfc9db749773fd080d212b8331eb8177557d2f8912"),
    ("AGENTS.md", "AGENTS.md", 38260, "24f2f2b1abe7fafce0d76e7de2baeec630aba8105b19228ef288f66284540534"),
]
ALLOWED_CHANGED = {
    "AGENTS.md", "README.md", "task1/README.md", "task1/reports/README.md",
    "task1/evidence/goal3/REVIEW_PACKET.md", "task1/docs/goal3/TECHNICAL_HANDOFF.md",
    "evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md",
    str(SYNC), str(META / "sources.json"), str(META / "SOURCE_MANIFEST.md"),
    str(META / "UPLOAD_INSTRUCTIONS.md"),
}
commands = []
artifacts = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(relative):
    path = ROOT / relative
    data = path.read_bytes()
    artifacts[str(relative)] = {"sha256": sha(data), "size": len(data)}
    return data


def git_old(relative):
    argv = ["git", "show", BASE + ":" + str(relative)]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True)
    commands.append({"command": argv, "cwd": str(ROOT), "exit_code": proc.returncode,
                     "stdout_sha256": sha(proc.stdout), "stderr": proc.stderr.decode()})
    assert proc.returncode == 0
    return proc.stdout


def current_stat(relative):
    path = ROOT / relative
    st = path.stat()
    return {"sha256": sha(path.read_bytes()), "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def validate_history(result):
    rel = "evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md"
    result["sync003_append_only"] = read(rel).startswith(git_old(rel))
    rel = "task1/evidence/goal3/REVIEW_PACKET.md"
    old, current = git_old(rel), read(rel)
    marker = "\n## 历史：".encode()
    result["goal3_historical_body_exact"] = old.split(marker, 1)[1] == current.split(marker, 1)[1]
    rel = "task1/docs/goal3/TECHNICAL_HANDOFF.md"
    old, current = git_old(rel), read(rel)
    marker = "Parent Goal：".encode()
    result["technical_historical_body_exact"] = old.split(marker, 1)[1] == current.split(marker, 1)[1]
    assert all(result.values())


def main():
    result = {"role": "Independent C / nonprocess_c", "base": BASE,
              "scope": "NC01-NC07 local engineering; NC08 and external GPT/UI/Process remain outside this C verdict",
              "commands": commands, "issues": []}
    try:
        rows_before = json.loads((TASK / "starting-protection-inventory.json").read_text())["files"]
        baseline_by_path = {r["path"]: r for r in rows_before}
        input_results = []
        for name, active, size, expected in INPUTS:
            received = read(TASK.relative_to(ROOT) / "received" / name)
            active_bytes = read(active)
            bundle_bytes = read(BUNDLE / name)
            old = git_old(active)
            item = {"name": name, "active_path": active, "sha256": sha(received), "size": len(received),
                    "expected_match": sha(received) == expected and len(received) == size,
                    "received_active_bundle_bytes_equal": received == active_bytes == bundle_bytes,
                    "base_bytes_unchanged": old == active_bytes,
                    "active_mtime_unchanged_from_start": (ROOT / active).stat().st_mtime_ns == baseline_by_path[active]["mtime_ns"]}
            assert item["expected_match"] and item["received_active_bundle_bytes_equal"]
            if name != "AGENTS.md":
                assert item["base_bytes_unchanged"] and item["active_mtime_unchanged_from_start"]
            input_results.append(item)
        assert [x["name"] for x in input_results if not x["base_bytes_unchanged"]] == ["AGENTS.md"]
        result["input_checks"] = input_results

        declaration = json.loads(read(META / "sources.json"))
        prior = json.loads(git_old(META / "sources.json"))
        current_rows = {r["canonical_name"]: r for r in declaration["sources"]}
        prior_rows = {r["canonical_name"]: r for r in prior["sources"]}
        assert set(current_rows) == set(prior_rows) and len(current_rows) == 16
        changed_rows = [name for name in current_rows if current_rows[name] != prior_rows[name]]
        assert changed_rows == ["AGENTS.md"]
        entries = list((ROOT / BUNDLE).iterdir())
        assert set(p.name for p in entries) == set(current_rows)
        assert all(p.is_file() and not p.is_symlink() for p in entries)
        member_results = []
        for name, row in current_rows.items():
            active = read(row["active_path"])
            payload = read(BUNDLE / name)
            old_payload = git_old(BUNDLE / name)
            assert active == payload and sha(active) == row["sha256"]
            if name != "AGENTS.md":
                assert payload == old_payload
            member_results.append({"name": name, "sha256": sha(active), "size": len(active),
                                   "active_bundle_equal": True, "unchanged_from_base": payload == old_payload})
        result["bundle"] = {"members": member_results, "count": 16, "changed_manifest_rows": changed_rows,
                            "other_15_rows_exact": True, "only_normal_files": True}

        old_tree = ast.parse(git_old(SYNC))
        current_tree = ast.parse(read(SYNC))
        old_functions = {n.name: ast.dump(n, include_attributes=False) for n in old_tree.body if isinstance(n, ast.FunctionDef)}
        current_functions = {n.name: ast.dump(n, include_attributes=False) for n in current_tree.body if isinstance(n, ast.FunctionDef)}
        changed_functions = sorted(k for k in old_functions if old_functions[k] != current_functions[k])
        assert set(old_functions) == set(current_functions)
        assert changed_functions == ["instructions_text"]
        for tree in (old_tree, current_tree):
            tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == "instructions_text")]
        assert ast.dump(old_tree, include_attributes=False) == ast.dump(current_tree, include_attributes=False)
        result["source_ast"] = {"syntax": "PASS", "changed_functions": changed_functions,
                                "all_other_syntax_exact": True}

        module = runpy.run_path(str(ROOT / SYNC))
        verified = module["verify_bundle"](ROOT)
        module["verify_manifest"](ROOT, verified)
        expected_metadata = module["metadata_bytes"](ROOT, verified)
        for relative, data in expected_metadata.items():
            assert read(relative) == data
        target_paths = sorted(set([r["active_path"] for r in declaration["sources"]] +
                                 [str(BUNDLE / r["canonical_name"]) for r in declaration["sources"]] +
                                 [str(META / x) for x in ("sources.json", "SOURCE_MANIFEST.md", "UPLOAD_INSTRUCTIONS.md")]))
        before_check = {p: current_stat(p) for p in target_paths}
        for mode in ("--plan", "--check"):
            argv = [sys.executable, "-I", "-B", str(ROOT / SYNC), mode]
            proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=60)
            commands.append({"command": argv, "cwd": str(ROOT), "exit_code": proc.returncode,
                             "stdout": proc.stdout, "stderr": proc.stderr})
            assert proc.returncode == 0
            parsed = json.loads(proc.stdout)
            if mode == "--plan":
                assert parsed["safe_to_sync"] is True
                assert all(parsed[key] == [] for key in ("add", "change", "missing", "unexpected", "unsafe", "errors", "metadata_change"))
            assert before_check == {p: current_stat(p) for p in target_paths}
        result["real_readonly"] = {"status": "PASS", "target_count": len(target_paths),
                                   "plan_check_preserve_bytes_and_mtimes": True,
                                   "metadata_matches_actual_generator": True,
                                   "skill_effective_members": module["verify_skill"](ROOT)}

        relocation = json.loads(read(TASK.relative_to(ROOT) / "metadata-relocation.json"))["records"]
        moved = {r["source"]: r for r in relocation}
        assert len(moved) == 5
        for row in relocation:
            data = read(row["preserved_path"])
            old_row = baseline_by_path[row["source"]]
            assert sha(data) == row["sha256"] == old_row["sha256"]
            assert len(data) == row["size"] == old_row["size"]
            assert data == base64.b64decode(row["base64"])
            assert (ROOT / row["preserved_path"]).stat().st_mtime_ns == row["mtime_ns"] == old_row["mtime_ns"]
            assert not (ROOT / row["source"]).exists()
            decoded = data.decode("gb18030")
            assert decoded.startswith("[ZoneTransfer]") and "ZoneId=3" in decoded
        result["sidecars"] = {"count": len(moved), "bytes_base64_hash_mtime_match_start": True,
                              "classification": "ZoneTransfer download metadata", "removed_from_bundle_only": True}

        changes, unchanged, symbolic = [], 0, []
        for row in rows_before:
            p = ROOT / row["path"]
            if row["type"] == "symlink":
                assert p.is_symlink(), row["path"]
                target = str(p.readlink())
                st = p.lstat()
                assert st.st_size == row["size"] and st.st_mtime_ns == row["mtime_ns"], row["path"]
                symbolic.append({"path": row["path"], "current_target": target,
                    "type_size_mtime_preserved": True,
                    "baseline_target": "Not recorded in starting inventory; no exact target-byte comparison claimed"})
                unchanged += 1
                continue
            if row["path"] in moved:
                changes.append({"path": row["path"], "kind": "approved_sidecar_relocation"})
                continue
            assert p.exists() and p.is_file() and not p.is_symlink(), row["path"]
            current = current_stat(row["path"])
            if current["sha256"] != row["sha256"] or current["mtime_ns"] != row["mtime_ns"]:
                assert row["path"] in ALLOWED_CHANGED, ("unexpected_change", row["path"])
                changes.append({"path": row["path"], "kind": "authorized_engineering_file",
                                "before_sha256": row["sha256"], "after": current})
            else:
                unchanged += 1
        result["protection"] = {"count": len(rows_before), "unchanged_count": unchanged,
                                "authorized_changes": changes, "symlinks": symbolic,
                                "unexpected_changes": [], "comparison": "All baseline ordinary files read; symlink lstat type/size/mtime checked without following it",
                                "protected_venv_texmf_count": sum(r["path"].startswith(".venv/texmf/") for r in rows_before)}

        pdf = read("reports/experiment-report/experiment1-reconstructed/Experiment_Report_吴博闻_10245102410.pdf")
        archive = read("reports/experiment-report/experiment1-reconstructed/Experiment_Report_完整重构_源文件.zip")
        current_pdf = read("task1/reports/experiment1/experiment1.pdf")
        assert sha(pdf) == "2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0"
        assert sha(archive) == "6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd"
        assert current_pdf == pdf
        result["approved_report"] = {"pdf_sha256": sha(pdf), "source_zip_sha256": sha(archive),
                                     "current_pdf_exact": True, "compile_or_render_performed": False}
        result["historical_preservation"] = {}
        validate_history(result["historical_preservation"])

        history = json.loads(read(EXT / "RECEPTION_HISTORY.json"))
        assert history[-1]["source_type"] == "USER_RELAYED_PRIOR_REVIEW"
        assert history[-1]["original_report_imported"] is False and history[-1]["original_archive_imported"] is False
        assert history[-1]["reviewed_commit"] == BASE and history[-1]["current_change_gpt_review"] == "PENDING"
        for path in ("REVIEW_RECEIPT.md", "USER_RELAYED_PRIOR_REVIEW.md"):
            read(EXT / path)
        result["external_review_source"] = {"identity": "USER_RELAYED_PRIOR_REVIEW", "originals_imported": False,
                                            "reviewed_commit": BASE, "current_review": "PENDING",
                                            "originals_gap_is_disclosed": True}

        docs = [Path(a) for _, a, _, _ in INPUTS]
        docs += [Path(x) for x in ALLOWED_CHANGED if x.endswith(".md")]
        docs += [EXT / "REVIEW_RECEIPT.md", EXT / "USER_RELAYED_PRIOR_REVIEW.md",
                 TASK.relative_to(ROOT) / "UI_HANDOFF.md", TASK.relative_to(ROOT) / "REVIEW_PACKET.md"]
        links = []
        missing = []
        for path in sorted(set(docs)):
            body = read(path).decode()
            for target in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", body):
                target = target.strip("<>")
                parsed = urllib.parse.urlsplit(target)
                if parsed.scheme:
                    prefix = "/woobowen/Smart_Cities_and_Location_Services/blob/main/"
                    if parsed.netloc == "github.com" and parsed.path.startswith(prefix):
                        destination = ROOT / urllib.parse.unquote(parsed.path[len(prefix):])
                    else:
                        continue
                elif parsed.path:
                    destination = (ROOT / path).parent / urllib.parse.unquote(parsed.path)
                else:
                    destination = ROOT / path
                exists = destination.exists()
                item = {"document": path.as_posix(), "target": target, "path_exists": exists}
                links.append(item)
                if not exists:
                    missing.append(item)
        assert not missing, missing
        result["navigation"] = {"local_and_repository_link_count": len(links), "missing": [],
                                 "scope": "Path existence for local/repository Markdown links; prose and current/history scope read by C",
                                 "links": links}
    except Exception:
        result["issues"].append(traceback.format_exc())
    result["overall"] = "PASS" if not result["issues"] else "FAIL"
    (OUT / "independent-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (OUT / "reviewed-artifacts.json").write_text(json.dumps({"base": BASE, "artifacts": artifacts,
        "boundary": "Engineering/source/history hashes at C read time; current task status/NC08 publication facts may be appended after C"}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("commands", "navigation")}, ensure_ascii=False, indent=2))
    if "navigation" in result:
        print(json.dumps({k: v for k, v in result["navigation"].items() if k != "links"}, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
