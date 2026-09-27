"""Independent, read-only validation of the final review archive.

No package code is imported or executed. FULL execution is audited separately.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
ZIP = ROOT / "task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一.zip"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    findings = []
    with zipfile.ZipFile(ZIP) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), "duplicate members"
        assert archive.testzip() is None, "CRC failed"
        for item in archive.infolist():
            p = PurePosixPath(item.filename)
            assert not p.is_absolute() and ".." not in p.parts
            assert "\\" not in item.filename and str(p) == item.filename
            assert not stat.S_ISLNK(item.external_attr >> 16), "symlink"
            assert not any(x in p.parts for x in (".git", ".venv", "__pycache__"))
            assert p.suffix.lower() not in (".ttf", ".otf", ".woff", ".woff2", ".zip")
            assert not re.search(r"(^|/)(?:\.env|id_rsa|id_ed25519|auth\.json|credentials)(?:$|/)", item.filename)

        manifest = json.loads(archive.read("PACKAGE_MANIFEST.json"))
        members = manifest["members"]
        assert set(names) == {m["path"] for m in members} | {"PACKAGE_MANIFEST.json"}
        assert len(members) == manifest["member_count"]
        assert manifest["package_status"] == "REVIEW_ONLY"
        assert manifest["submission_status"] == "NOT_READY"
        assert manifest["sent_to_teacher"] is False
        identity = manifest["metadata"]
        assert identity["student_name"] == "吴博闻"
        assert type(identity["student_id"]) is str and identity["student_id"] == "10245102410"
        for key, expected in {
            "identity_status": "VERIFIED", "understanding_status": "LEARNING",
            "submission_status": "NOT_READY", "new_gpt_second_review": "PENDING",
            "evidence_master_spec_and_lock": "NOT_AVAILABLE",
        }.items():
            assert identity[key] == expected, (key, identity[key])

        transforms = []
        for member in members:
            raw = archive.read(member["path"])
            assert len(raw) == member["bytes"]
            assert sha(raw) == member["archive_sha256"]
            source = ROOT / member.get("source_path", member["path"])
            source_raw = source.read_bytes()
            assert sha(source_raw) == member["source_sha256"], member["path"]
            if not member["transformations"]:
                assert raw == source_raw, member["path"]
            else:
                # The package records the one allowed command-provenance
                # normalization; all scientific fields must remain identical.
                assert member["path"] == "task1/evidence/goal2/result_summary.json"
                current = json.loads(source_raw)
                packaged = json.loads(raw)
                assert packaged["actual_command"][1:] == current["actual_command"][1:]
                assert packaged["actual_command"][0] == "task1/scripts/build_goal2_analysis.py"
                assert sha(current["actual_command"][0].encode()) == member["transformations"][0]["original_value_sha256"]
                packaged["actual_command"][0] = current["actual_command"][0]
                # The exact added provenance key is inspected, not ignored wholesale.
                extra = set(packaged) - set(current)
                assert len(extra) == 1, extra
                key = extra.pop()
                assert key == "_package_provenance", key
                provenance = packaged.pop(key)
                assert provenance["source_sha256"] == sha(source_raw)
                assert provenance["numeric_results_and_proposals_changed"] is False
                assert packaged == current, "scientific JSON changed in package"
                transforms.append({"path": member["path"], "recorded_transformations": member["transformations"], "added_provenance": provenance})
            findings.append({"path": member["path"], "sha256": sha(raw), "bytes": len(raw)})

        for kind in ("experiment1", "process1"):
            relative = f"task1/reports/{kind}/{kind}.pdf"
            assert archive.read(relative) == (ROOT / relative).read_bytes()
            metadata = subprocess.check_output(["pdfinfo", str(ROOT / relative)], text=True)
            assert "吴博闻" in metadata and "10245102410" in metadata
            cover = subprocess.check_output(["pdftotext", "-f", "1", "-l", "1", str(ROOT / relative), "-"], text=True)
            assert "吴博闻" in cover and "10245102410" in cover

        content = {m["path"]: m["archive_sha256"] for m in members}
        content_id = sha(json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode())
        out = {
            "role_context": "/root/c_independent", "status": "PASS",
            "zip_path": str(ZIP.relative_to(ROOT)), "zip_sha256": sha(ZIP.read_bytes()),
            "zip_bytes": ZIP.stat().st_size, "members_including_manifest": len(names),
            "package_content_id": content_id,
            "content_id_definition": "SHA256 compact sorted UTF8 JSON map of manifest member path to archive_sha256, excluding manifest self-reference",
            "all_member_checks": findings, "transformations": transforms,
            "scope": "Independent CRC, safe path/symlink/duplicates, every member hash+length, current source equality, allowed provenance-only transformation, current PDF byte equality, PDF metadata/cover identity and state boundaries. No FULL run claimed by this static check.",
        }
        (OUT / "package_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({k: v for k, v in out.items() if k not in ("all_member_checks", "transformations")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
