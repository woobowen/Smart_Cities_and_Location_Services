"""Independent C synchronization probes; never mutate the real bundle."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REL_SCRIPT = Path("evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py")
REL_META = Path("evidence/infrastructure/chatgpt-project-source-sync")
REL_BUNDLE = Path("releases/chatgpt-project-sources")
SOURCE_SCRIPT = ROOT / REL_SCRIPT
commands = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = {"kind": "symlink", "target": str(path.readlink())}
        elif path.is_file():
            st = path.stat()
            result[relative] = {"kind": "file", "sha256": sha(path.read_bytes()),
                                "size": st.st_size, "mtime_ns": st.st_mtime_ns}
        elif path.is_dir():
            result[relative] = {"kind": "directory"}
        else:
            result[relative] = {"kind": "other"}
    return result


def run(root, mode):
    argv = [sys.executable, "-I", "-B", str(root / REL_SCRIPT)]
    if mode:
        argv.append(mode)
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=60)
    record = {"command": argv, "cwd": str(root), "exit_code": proc.returncode,
              "stdout": proc.stdout, "stderr": proc.stderr}
    commands.append(record)
    return record


def make_fixture(root):
    (root / REL_META).mkdir(parents=True)
    (root / REL_BUNDLE).mkdir(parents=True)
    (root / REL_SCRIPT).parent.mkdir(parents=True)
    shutil.copy2(SOURCE_SCRIPT, root / REL_SCRIPT)
    shutil.copytree(ROOT / "tools/skills/publication-plots",
                    root / "tools/skills/publication-plots",
                    ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*:Zone.Identifier"))
    shutil.copy2(ROOT / REL_BUNDLE / "publication-plots.zip",
                 root / REL_BUNDLE / "publication-plots.zip")
    sources = []
    for name, data in [("alpha.md", b"independent C alpha\n"),
                       ("beta.md", b"independent C beta\n")]:
        path = Path("active") / name
        (root / path).parent.mkdir(exist_ok=True)
        (root / path).write_bytes(data)
        sources.append({"canonical_name": name, "active_path": path.as_posix(),
            "project_source": True, "semantic_role": "independent_synthetic_fixture",
            "scope": "independent safety probe only", "version": "fixture",
            "sha256": sha(data), "pair_id": None, "approval_scope": "C isolated probe",
            "supersedes": None})
    skill = root / REL_BUNDLE / "publication-plots.zip"
    sources.append({"canonical_name": skill.name,
        "active_path": (REL_BUNDLE / skill.name).as_posix(),
        "project_source": True, "semantic_role": "skill_original_archive",
        "scope": "preserved original used in isolated probe", "version": "approved original",
        "sha256": sha(skill.read_bytes()), "pair_id": None,
        "approval_scope": "C isolated probe", "supersedes": None})
    declaration = {"schema_version": 1, "approval": "INDEPENDENT_C_FIXTURE",
                   "revision_date": "2026-09-29", "sources": sources}
    (root / REL_META / "sources.json").write_text(
        json.dumps(declaration, ensure_ascii=False, indent=2) + "\n")
    return declaration


def write_declaration(root, declaration):
    (root / REL_META / "sources.json").write_text(
        json.dumps(declaration, ensure_ascii=False, indent=2) + "\n")


def main():
    temp = Path(tempfile.mkdtemp(prefix="sc-lab1-nonprocess-independent-c-"))
    result = {"role": "Independent C / nonprocess_c", "temp_root": str(temp),
              "source_script": REL_SCRIPT.as_posix(),
              "source_script_sha256": sha(SOURCE_SCRIPT.read_bytes()),
              "fixture_scope": "3 explicitly declared members; current real 16-member bundle checked separately",
              "results": [], "commands": commands, "issues": [],
              "cleanup": "Preserved own uniquely created fixtures for inspection"}
    try:
        positive = temp / "success"
        declaration = make_fixture(positive)
        before = snapshot(positive)
        plan = run(positive, "--plan")
        assert plan["exit_code"] == 0
        assert json.loads(plan["stdout"])["safe_to_sync"] is True
        assert before == snapshot(positive)
        first = run(positive, "")
        first_data = json.loads(first["stdout"])
        assert first["exit_code"] == 0 and first_data["file_count"] == 3
        assert len(first_data["updated"]) == 4 and first_data["removed"] == []
        before_check = snapshot(positive)
        check = run(positive, "--check")
        assert check["exit_code"] == 0
        assert before_check == snapshot(positive)
        again = run(positive, "")
        again_data = json.loads(again["stdout"])
        assert again["exit_code"] == 0
        assert again_data["updated"] == [] and again_data["removed"] == []
        assert before_check == snapshot(positive)
        result["results"].append({"case": "success_plan_write_check_second_write",
            "status": "PASS", "root": str(positive), "file_count": 3,
            "first_updated": first_data["updated"],
            "check_and_second_write_preserved_all_file_hashes_and_mtimes": True})

        for case in ("missing_source", "wrong_hash", "unknown_extra"):
            fixture = temp / case
            declaration = make_fixture(fixture)
            baseline = run(fixture, "")
            assert baseline["exit_code"] == 0
            alpha = fixture / "active/alpha.md"
            alpha.write_bytes(b"new alpha should not reach existing target if validation rejects\n")
            declaration["sources"][0]["sha256"] = sha(alpha.read_bytes())
            if case == "missing_source":
                (fixture / "active/beta.md").unlink()
                needle = "Missing source"
            elif case == "wrong_hash":
                declaration["sources"][1]["sha256"] = "0" * 64
                needle = "SHA256 mismatch"
            else:
                (fixture / REL_BUNDLE / "unapproved-extra.txt").write_bytes(
                    b"must preserve this unknown file\n")
                needle = "extra"
            write_declaration(fixture, declaration)
            before = snapshot(fixture)
            case_records = []
            for mode in ("--plan", "", "--check"):
                command = run(fixture, mode)
                assert command["exit_code"] == 1, (case, mode, command)
                assert snapshot(fixture) == before, (case, mode, "mutation detected")
                if mode == "--plan":
                    parsed = json.loads(command["stdout"])
                    assert parsed["safe_to_sync"] is False
                    if case == "unknown_extra":
                        assert parsed["unexpected"] == ["unapproved-extra.txt"]
                    else:
                        assert any(needle in error for error in parsed["errors"])
                else:
                    assert needle in command["stderr"], (case, mode, command)
                case_records.append({"mode": mode or "write", "exit_code": 1,
                                     "entire_fixture_hash_mtime_and_member_set_preserved": True})
            result["results"].append({"case": case, "status": "PASS", "root": str(fixture),
                "older_target_with_new_source_preserved": True, "checks": case_records})
    except Exception:
        result["issues"].append(traceback.format_exc())
    result["overall"] = "PASS" if not result["issues"] and len(result["results"]) == 4 else "FAIL"
    (OUT / "independent-probes.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("overall", "temp_root", "source_script_sha256",
                                                   "results", "issues")}, ensure_ascii=False, indent=2))
    return 0 if result["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
