"""C-only read audit. Writes results only beside this script; no implementation imports."""
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
TASK = OUT.parent
EXPECTED = {
    "SMART_CITIES_RESEARCH_PROTOCOL.md": (11981, "332741175630b1329387a0d69acf0061c6278c82bb27596f1d4629c2aa13a378"),
    "SMART_CITIES_REPORT_WRITING_GUIDE.md": (24040, "abc729c5f7f764021ae1417dc6e8fcb1997eb3632747e46c8d0d53166642ff37"),
    "SMART_CITIES_VISUAL_SYSTEM.md": (42569, "fbba109a796cff5ffe09848986a75b749248e5d609860c54eb2004b839fd9cbc"),
    "WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md": (44284, "2385583504caa7c4a7708cd12602c2f692dfd6bb217e1b6ffdd3558b25a22fbd"),
    "AGENTS.md": (33593, "aec7864126d07644ab2d8a724aad7357d146b9adf000ff3e8a3a70b2b644d171"),
    "Experiment_Report_吴博闻_10245102410.pdf": (907540, "2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0"),
    "Experiment_Report_完整重构_源文件.zip": (3515637, "6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd"),
}


def digest(b):
    return hashlib.sha256(b).hexdigest()


def main():
    results = {"role": "independent C", "scope": "initial read-only verification"}
    inputs = []
    for name, (size, expected) in EXPECTED.items():
        p = TASK / "received" / name
        data = p.read_bytes()
        inputs.append({"name": name, "size": len(data), "sha256": digest(data),
                       "expected_size": size, "expected_sha256": expected,
                       "baseline_match": len(data) == size and digest(data) == expected,
                       "regular_file": p.is_file() and not p.is_symlink()})
    results["received"] = inputs
    results["actual_remote"] = subprocess.check_output(
        ["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True).strip()
    results["local_and_tracking_sha"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD", "origin/main"], cwd=ROOT, text=True).splitlines()
    inventory = json.loads((TASK / "received-release-inventory.json").read_text())
    results["received_release_inventory"] = {
        "count": len(inventory), "types": dict(Counter(x["type"] for x in inventory)),
        "unique_paths": len({x["path"] for x in inventory}),
        "suffix_duplicates": [x["path"] for x in inventory if re.search(r"\([0-9]+\)\.[^.]+$", x["path"])],
    }
    protected = json.loads((TASK / "starting-protection-inventory.json").read_text())
    mismatches = []
    for item in protected:
        p = ROOT / item["path"]
        if item["type"] != "file":
            continue
        if not p.is_file() or p.is_symlink() or digest(p.read_bytes()) != item["sha256"]:
            mismatches.append(item["path"])
    results["starting_inventory_count"] = len(protected)
    results["currently_changed_from_start"] = mismatches
    zpath = TASK / "received" / "Experiment_Report_完整重构_源文件.zip"
    with zipfile.ZipFile(zpath) as z:
        entries = z.infolist()
        unsafe = []
        fonts = []
        execution_hits = []
        credential_hits = []
        members = []
        for info in entries:
            name = PurePosixPath(info.filename)
            if name.is_absolute() or ".." in name.parts or "\\" in info.filename or stat.S_ISLNK(info.external_attr >> 16):
                unsafe.append(info.filename)
            if name.suffix.lower() in {".ttf", ".otf", ".ttc", ".woff", ".woff2"}:
                fonts.append(info.filename)
            data = z.read(info)
            members.append({"name": info.filename, "size": len(data), "sha256": digest(data)})
            if name.suffix.lower() in {".py", ".tex", ".sh", ".json", ".md", ".txt"}:
                text = data.decode("utf-8", errors="replace")
                for pat in [r"\\write18", r"shell-escape", r"os\.system", r"subprocess\.", r"\beval\(", r"\bexec\(", r"curl\s", r"wget\s", r"rm\s+-rf", r"rmtree"]:
                    if re.search(pat, text):
                        execution_hits.append({"name": info.filename, "pattern": pat})
                if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{20,}|\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}", text):
                    credential_hits.append(info.filename)
        names = [x.filename for x in entries]
        results["experiment_archive"] = {
            "entries": len(entries), "crc_error": z.testzip(),
            "duplicates": [n for n, count in Counter(names).items() if count > 1],
            "unsafe": unsafe, "font_binaries": fonts,
            "execution_review_hits": execution_hits, "high_confidence_credential_hits": credential_hits,
            "roots": sorted({PurePosixPath(n).parts[0] for n in names}),
            "embedded_pdf_matches_approved": z.read("Experiment_Report_source/Experiment_Report.pdf") ==
                (TASK / "received" / "Experiment_Report_吴博闻_10245102410.pdf").read_bytes(),
        }
        (OUT / "experiment-archive-members.json").write_text(json.dumps(members, ensure_ascii=False, indent=2) + "\n")
    process_paths = [
        "reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_REVISED.pdf",
        "reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip",
        "evidence/infrastructure/SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md",
    ]
    anchor = "4483f520eabb5358d1f35cf5c33a81d3b01e47e0"
    results["process_anchor_preservation"] = []
    for path in process_paths:
        before = subprocess.check_output(["git", "show", f"{anchor}:{path}"], cwd=ROOT)
        current = (ROOT / path).read_bytes()
        results["process_anchor_preservation"].append({"path": path, "sha256": digest(current), "matches_anchor": current == before})
    (OUT / "initial-independent-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
