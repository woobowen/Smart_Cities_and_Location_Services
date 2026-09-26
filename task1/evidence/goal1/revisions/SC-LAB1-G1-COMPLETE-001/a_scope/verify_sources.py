"""Read-only, targeted source check for the A-role handoff; no model calls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
REV = "task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001"


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def slide_text(path, member):
    with zipfile.ZipFile(ROOT / path) as archive:
        element = ET.fromstring(archive.read(member))
    return "\n".join(node.text or "" for node in element.iter()
                     if node.tag.rsplit("}", 1)[-1] == "t")


index = json.loads((ROOT / "task1/evidence/goal1/materials/extraction_index.json").read_text())
historical = {entry["source"]: entry["sha256"] for entry in index}
source_paths = [
    "task1/实验课1.pptx",
    "task1/作业/作业/作业1轨迹数据预处理.ipynb",
    "task1/作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx",
    "task1/作业/作业/utils/util.py",
    "task1/作业/作业/traj_agent/core/geo.py",
    "task1/作业/作业/DECISIONS.md",
]
source_checks = [dict(path=path, sha256=digest(path),
                      historical_extract_sha256=historical.get(path),
                      bytes_match_historical_extract=digest(path) == historical.get(path))
                 for path in source_paths]
assert all(row["bytes_match_historical_extract"] for row in source_checks)

prior_excerpts_path = "task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/source_excerpts.json"
prior_excerpts = json.loads((ROOT / prior_excerpts_path).read_text())
excerpts = []
for key in ["teacher:13:body", "teacher:13:notes", "teacher:20"]:
    prior = prior_excerpts[key]
    current = slide_text(prior["path"], prior["member"])
    exact = current == prior["excerpt"]
    assert exact, key
    excerpts.append(dict(id=key, path=prior["path"], member=prior["member"],
                         source_sha256=digest(prior["path"]),
                         saved_excerpt_exact_match=exact, excerpt=current,
                         claim_status=prior["claim_status"]))
for page in [17, 18, 22, 24, 26, 37, 42]:
    path = "task1/实验课1.pptx"
    member = f"ppt/slides/slide{page}.xml"
    excerpts.append(dict(id=f"teacher:{page}", path=path, member=member,
                         source_sha256=digest(path), excerpt=slide_text(path, member)))
path = source_paths[2]
excerpts.append(dict(id="supplement:4", path=path, member="ppt/slides/slide4.xml",
                     source_sha256=digest(path), excerpt=slide_text(path, "ppt/slides/slide4.xml"),
                     claim_status="LON_LAT_DEGREES_UNIX_SECONDS_DECLARED_NOT_DATUM"))

notebook_path = source_paths[1]
notebook = json.loads((ROOT / notebook_path).read_text())
for cell in [1, 4, 6, 8, 10, 12, 14, 16]:
    excerpts.append(dict(id=f"notebook:{cell}", path=notebook_path,
                         cell_index_zero_based=cell, source_sha256=digest(notebook_path),
                         excerpt="".join(notebook["cells"][cell]["source"])))

raw_path = "task1/作业/作业/traj_dict.json"
expected_raw = "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3"
assert digest(raw_path) == expected_raw
raw = json.loads((ROOT / raw_path).read_text())
pilot = ["0", "1", "2", "246", "256", "306", "352"]
pilot_counts = {record: len(raw[record][1]) for record in pilot}
assert sum(pilot_counts.values()) == 783

snapshot_paths = [
    "AGENTS.md", "docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md",
    f"{REV}/handoff/SC-LAB1-G1-COMPLETE-001_CODEX_PROMPT.md",
    "task1/evidence/goal1/requirements.json", "task1/evidence/goal1/acceptance.json",
    "task1/evidence/goal1/REVIEW_PACKET.md", "task1/docs/goal1/CONTRACTS.md",
    "task1/config/goal1.json", "task1/config/goal1_sources.json",
    "task1/workflow/controller.py", "task1/workflow/pipeline.py",
    "task1/docs/goal1/ARCHITECTURE.md", "task1/docs/goal1/README.md",
    "task1/scripts/build_goal1_notebooks.py", prior_excerpts_path,
]
policy = json.loads((ROOT / "task1/config/goal1.json").read_text())
supplement_path = f"{REV}/AUTHORIZATION_SUPPLEMENT.md"
decisions_path = f"{REV}/USER_DECISIONS.json"
decisions = json.loads((ROOT / decisions_path).read_text())
assert decisions["D2"]["status"] == "USER_APPROVED"
assert decisions["D1"]["conditional_analysis"] == "AUTHORIZED"
assert digest(supplement_path) == decisions["D1"]["sha256"]
snapshot_paths.extend([supplement_path, decisions_path])
research_paths = [f"task1/docs/research/{name}" for name in [
    "Task1_Literature_Review_2025_2026_Merged.md",
    "Task1_Source_Audit_2025_2026_Merged.json",
    "Task1_Stage01_Readonly_Audit.md",
]]
record = {
    "classification": "A_ROLE_CURRENT_READ_ONLY_SOURCE_AUDIT_NOT_EXPERIMENT_ACCEPTANCE",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "head_at_read": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_checks": source_checks,
    "targeted_excerpts": excerpts,
    "raw_integrity": {"path": raw_path, "sha256": digest(raw_path), "expected_sha256": expected_raw,
                      "matches": True, "operation": "read-only hash and fixed-pilot point counts"},
    "pilot_record_ids": pilot,
    "pilot_point_counts": pilot_counts,
    "pilot_points": sum(pilot_counts.values()),
    "D1": {
        "file_bound_datum_source_found_in_checked_sources": False,
        "coordinate_fact_status": "UNVERIFIED",
        "configuration_status_at_read": policy["semantics"]["crs"]["status"],
        "conditional_analysis": "AUTHORIZED_BY_CURRENT_USER_SUPPLEMENT",
        "conclusion": "The datum fact remains unverified. The later explicit user authorization permits a fixed, traceable local model for conditional real-pilot analysis; datum uncertainty no longer blocks every real operation.",
    },
    "D2": {
        "new_explicit_user_approval_found_in_checked_sources": True,
        "status": decisions["D2"]["status"],
        "source": decisions_path,
        "source_sha256": digest(decisions_path),
        "conclusion": "The actual current user decision approves one-pass complete marking and simultaneous deletion, preserving endpoints/undefined windows and recomputing downstream features; no repeat approval is needed.",
    },
    "checked_approval_entries": [
        supplement_path,
        decisions_path,
        f"{REV}/handoff/SC-LAB1-G1-COMPLETE-001_CODEX_PROMPT.md#7",
        f"{REV}/handoff/README.md",
        f"{REV}/handoff/reference_only/GPT_SECOND_REVIEW_ROUND2.md",
        "task1/docs/goal1/CONTRACTS.md",
        "task1/config/goal1.json",
        "task1/config/goal1_sources.json",
        "task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/SEMANTICS.md",
        "task1/作业/作业/DECISIONS.md",
    ],
    "search_scope_limit": "Targeted active/handoff entries, saved source excerpts, original matching PPT/Notebook/source bytes, and approval-like filenames under task1. This is not an assertion about unprovided user messages or external data-provider replies.",
    "naming_collision": "Starter DECISIONS.md D1/D2 are historical algorithm decisions, not the current user-approval gates; its direction/curvature/noise-floor rules are not authorization for this G1.",
    "previously_missing_research_files_now_present": [{"path": path, "exists": (ROOT / path).is_file(), "sha256": digest(path)} for path in research_paths],
    "source_snapshot_sha256": {path: digest(path) for path in snapshot_paths},
    "new_packages": [],
    "external_provider_calls": 0,
    "new_agents_spawned": 0,
    "full_slide_rerender": False,
    "real_spatial_processing": "NOT_RUN",
}
(OUT / "source_audit.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"source_files_match": len(source_checks), "saved_excerpts_match": 3,
                  "pilot_records": len(pilot), "pilot_points": sum(pilot_counts.values()),
                  "D1": "FACT_UNVERIFIED_CONDITIONAL_ANALYSIS_AUTHORIZED", "D2": "USER_APPROVED", "output": str((OUT / "source_audit.json").relative_to(ROOT))}, ensure_ascii=False))
