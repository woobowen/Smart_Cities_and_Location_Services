"""Read both actual archives and extracted inputs; no numerical/model execution."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
CLOSEOUT = HERE.parent
NAME = "REVIEW_ONLY_10245102410_吴博闻_实验一.zip"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    previous = CLOSEOUT / "executed_package" / NAME
    final = ROOT / "task1/submission" / NAME
    extracted = Path("/tmp/sc-lab1-closeout-package")
    assert not (extracted / ".git").exists()
    changed, nonpdf, equal, extraction = [], {}, {}, {}
    with zipfile.ZipFile(previous) as old, zipfile.ZipFile(final) as new:
        assert old.testzip() is new.testzip() is None
        assert set(old.namelist()) == set(new.namelist())
        for member in sorted(old.namelist()):
            before, after = old.read(member), new.read(member)
            # Compare actual extracted bytes, not a builder's claimed hash.
            actual = extracted / member
            assert actual.is_file() and actual.read_bytes() == before, member
            extraction[member] = digest(before)
            if before != after:
                changed.append(member)
            else:
                equal[member] = digest(after)
                if member != "PACKAGE_MANIFEST.json" and not member.endswith(".pdf"):
                    nonpdf[member] = digest(after)
        assert changed == ["PACKAGE_MANIFEST.json", "task1/reports/experiment1/experiment1.pdf"]
        assert len(nonpdf) == 113
        assert "task1/reports/process1/process1.pdf" in equal
        for name in ("作业1轨迹数据预处理_完成版.ipynb", "任务3_LLM辅助评估清洗_完成版.ipynb"):
            member = "task1/notebooks/final/" + name
            assert new.read(member) == (ROOT / member).read_bytes()
    out = {
        "role_context": "/root/c_independent", "status": "PASS",
        "final_zip": str(final.relative_to(ROOT)), "final_zip_sha256": digest(final.read_bytes()),
        "actual_execution_zip": str(previous.relative_to(ROOT)), "actual_execution_zip_sha256": digest(previous.read_bytes()),
        "actual_extracted_directory": str(extracted), "extracted_members_compared_byte_for_byte": len(extraction),
        "changed_members": changed, "identical_non_pdf_payload_count": len(nonpdf),
        "identical_non_pdf_payload_sha256": nonpdf, "actual_extracted_archive_member_sha256": extraction,
        "claim": "All Notebook, Python, declared dependency, raw input, frozen configuration, saved proposals and historical-input bytes in the final ZIP equal the preserved ZIP actually extracted for isolated FULL. Only the Experiment PDF and package metadata changed. The Process PDF is also identical. This is inherited equivalent execution evidence, not a new execution; successful fresh-kernel run receipts remain a separate required check.",
        "new_numerical_runs": 0, "new_record_model_calls": 0,
    }
    (HERE / "package_execution_equivalence.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "compared_extracted_members": len(extraction), "identical_runtime_non_pdf_members": len(nonpdf), "changed_members": changed}))


if __name__ == "__main__":
    main()
