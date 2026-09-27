"""Independent locator/source checks after final report navigation refresh."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from check_review_snapshot import check_snapshot

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
A = HERE.parent / "a_diagnosis"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p: Path):
    return json.loads(p.read_text())


def file_refs(value):
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and "sha256" in value:
            yield value
        for child in value.values():
            yield from file_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from file_refs(child)


def main() -> None:
    snapshot = check_snapshot()
    manifest = read(ROOT / snapshot["manifest"]["path"])
    snapshot_sources = {r["active_path"]: r for r in manifest["sources"]}
    parent_requirements = read(ROOT / snapshot_sources["task1/evidence/goal3/requirements.json"]["snapshot_path"])
    parents = {r["id"]: r for r in parent_requirements["requirements"]}
    master = read(A / "MASTER_REQUIREMENTS_REVIEW.json")
    expected = {f"T1-{i:02d}" for i in range(1, 14)} | {f"T2-{i:02d}" for i in range(1, 9)} | {f"U{i:02d}" for i in range(1, 45)}
    assert {e["id"] for e in master["entries"]} == expected
    assert len(master["entries"]) == master["entry_count"] == 65
    assert master["derived_only"] is True and master["not_parallel_acceptance_matrix"] is True
    bindings = {}
    pdfs = {}
    cells = 0
    page_anchors = 0
    functions = 0
    stale_bindings = {}
    assert master["state_authority"] == manifest["active_state_links"]
    assert all(isinstance(p, str) for p in master["state_authority"])
    for ref in file_refs(master):
        assert ref["path"] not in snapshot_sources, "Mutable active state cannot be a hash-bound immutable source"
        p = ROOT / ref["path"]
        assert p.is_file(), ref
        actual = sha(p)
        if actual != ref["sha256"]:
            stale_bindings[ref["path"]] = {"bound_sha256": ref["sha256"], "current_sha256": actual}
        bindings[ref["path"]] = ref["sha256"]
        if "source_active_path" in ref:
            row = snapshot_sources[ref["source_active_path"]]
            assert ref["path"] == row["snapshot_path"] and ref["sha256"] == row["sha256"]
            assert ref["observed_at_utc"] == manifest["created_at"]
            assert ref["snapshot_manifest_path"] == snapshot["manifest"]["path"]
            assert ref["state_semantics"] == manifest["purpose"]
    for e in master["entries"]:
        assert "current_parent_status" not in e
        assert {r["id"] for r in e["parent_status_at_review_input_snapshot"]} == set(e["g3_requirement_ids"])
        for ref in e["parent_status_at_review_input_snapshot"]:
            assert ref["status"] == parents[ref["id"]]["status"]
            assert ref["scope"] == parents[ref["id"]].get("scope", "")
            assert ref["final_state_lookup"] == "task1/evidence/goal3/requirements.json"
        for key in ("requirement", "source_category", "current_authority", "actual_approach", "why", "comparison_and_checks", "reviews", "quality_supports", "does_not_prove", "status", "remaining"):
            assert key in e, (e["id"], key)
        assert "USER_RELAYED" in e["historical_web_review"]
        for ref in e["sources"] + e["implementation"] + e["evidence"] + e["reviews"] + e.get("current_closeout_reviews", []) + [e["current_authority"]]:
            p = ROOT / ref["path"]
            assert p.is_file(), (e["id"], ref["path"])
            actual = sha(p)
            if actual != ref["sha256"]:
                stale_bindings[ref["path"]] = {"bound_sha256": ref["sha256"], "current_sha256": actual}
            bindings[ref["path"]] = ref["sha256"]
            if "function" in ref:
                nodes = [n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == ref["function"]]
                assert nodes and any(n.lineno == ref["line"] for n in nodes), ref
                functions += 1
        for ref in e["reviews"]:
            assert ref["current_run"] is False, "historical C upgraded to new execution"
        for ref in e["notebook_locators"]:
            nb = read(ROOT / ref["path"])
            cell = nb["cells"][ref["physical_index_zero_based"]]
            assert cell["id"] == ref["stable_cell_id"] and cell["cell_type"] == ref["cell_type"]
            source = "".join(cell["source"])
            assert hashlib.sha256(source.encode()).hexdigest() == ref["source_sha256"]
            cells += 1
        for ref in e["report_locators"]:
            p = ROOT / ref["path"]
            assert sha(p) == ref["pdf_sha256"], (e["id"], "stale PDF")
            if ref["path"] not in pdfs:
                extracted = subprocess.check_output(["pdftotext", "-layout", str(p), "-"], text=True).split("\f")
                if not extracted[-1].strip():
                    extracted.pop()
                pdfs[ref["path"]] = extracted
            pages = pdfs[ref["path"]]
            assert len(pages) == ref["page_count"]
            anchor = re.sub(r"\s+", "", ref["text_anchor"])
            assert ref["physical_pages_one_based"], (e["id"], ref)
            for n in ref["physical_pages_one_based"]:
                assert anchor in re.sub(r"\s+", "", pages[n - 1]), (e["id"], n, anchor)
                page_anchors += 1

    literature = read(A / "literature_use_map.json")
    for ref in file_refs(literature):
        p = ROOT / ref["path"]
        assert p.is_file() and sha(p) == ref["sha256"], ref
        bindings[ref["path"]] = ref["sha256"]
    audit = read(ROOT / "task1/docs/research/Task1_Source_Audit_2025_2026_Merged.json")
    original = {s["id"]: s for s in audit["sources"]}
    assert len(literature["entries"]) == 28 and len(original) == 26
    for e in literature["entries"]:
        if e["id"] in original:
            old = original[e["id"]]
            for key in ("title", "authors", "year", "urls"):
                assert e[key] == old[key], (e["id"], key)
            assert e["historical_actual_reading"] == old["reading"] or e["id"] == "S10"
            assert e["source_audit"]["sha256"] == sha(ROOT / e["source_audit"]["path"])
    assert {e["id"] for e in literature["entries"]} - set(original) == {"REF-PROJ-CART", "REF-PROJ-TOPO"}

    by_id = {e["id"]: e for e in master["entries"]}
    assert "UPLOAD_BUNDLE" in by_id["U42"]["evidence_group_ids"]
    assert "REPORT_CURRENT" in by_id["T1-11"]["evidence_group_ids"]
    assert {"source_rows", "verify_bundle", "verify_manifest", "verify_skill"} <= {r["function"] for r in by_id["U42"]["implementation"]}
    assert any(r["path"].endswith("/upload_bundle_check_output.txt") for r in by_id["U42"]["evidence"])
    assert any(r["path"].endswith("/report_tasks_receipt.json") for r in by_id["T1-11"]["evidence"])

    links = 0
    md_paths = [A / "MASTER_REQUIREMENTS_REVIEW.md", A / "TEACHING_DIFFERENCES.md", A / "literature_use_map.md", ROOT / "task1/docs/goal3/REVIEW_GUIDE.md"]
    for md in md_paths:
        for target in re.findall(r"\]\(([^)]+)\)", md.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            target = unquote(target.split("#")[0].strip("<>"))
            assert (md.parent / target).resolve().exists(), (str(md), target)
            links += 1

    out = {
        "role_context": "/root/c_independent", "status": "BINDINGS_PENDING" if stale_bindings else "PASS_IN_STATED_SCOPE",
        "master_sha256": sha(A / "MASTER_REQUIREMENTS_REVIEW.json"),
        "literature_map_sha256": sha(A / "literature_use_map.json"),
        "stable_requirement_ids": sorted(expected), "source_bindings": bindings,
        "function_locators_checked": functions, "notebook_cell_locators_checked": cells,
        "actual_current_PDF_page_anchors_checked": page_anchors,
        "local_markdown_links_checked": links, "archived_literature_metadata_rows": 26,
        "extra_report_official_documents": 2,
        "stale_source_bindings": stale_bindings,
        "immutable_governance_input_check": {"path": str((HERE / "review_input_snapshot_receipt.json").relative_to(ROOT)), "sha256": sha(HERE / "review_input_snapshot_receipt.json")},
        "snapshot_status_semantics": "All65 parent-state crosswalks are observations at the actual snapshot time; mutable active requirements/goal_state/CL remain unique path-only current authorities.",
        "content_review": "C read all65 requirement/status/actual approach/why/nonproof rows and seven teaching differences; directly extracted teacher PPT17/18/24/26/28/33/34/36; confirmed source-kind and current authorization vs historical review separation. Source Audit metadata/read-level inherited with explicit limits, not newly claiming28 full-paper reads. Current formal cited propositions restricted to documented specified Cawley sections and PROJ conversion semantics.",
        "limits": "Source/locator consistency is not mathematical or empirical effect proof. New numerical/run evidence is in other C receipts; external Process Evidence, user Understanding and new webpageGPT acceptance remain pending.",
    }
    filename = "requirements_literature_locator_check_pending.json" if stale_bindings else "requirements_literature_receipt.json"
    (HERE / filename).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if isinstance(v, int) or k == "status"}))
    if stale_bindings:
        print(json.dumps({"stale_source_bindings": stale_bindings}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
