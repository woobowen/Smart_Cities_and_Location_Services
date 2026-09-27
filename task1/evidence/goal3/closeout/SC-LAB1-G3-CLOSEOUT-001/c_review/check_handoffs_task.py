"""Check current requirement/guide/technical handoff delivery and task binding."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return re.sub(r"\s+", "", text)


def main():
    packet_path = BASE / "handoffs_review_submission.json"
    packet = read(packet_path)
    state = read(ROOT / "task1/evidence/goal3/goal_state.json")
    submitted = state["tasks"]["handoffs"]
    assert submitted["status"] == "REVIEW_PENDING"
    assert packet["targets"] == submitted["targets"] and packet["source_hashes"] == submitted["source_hashes"]
    for row in packet["targets"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    for path, expected in packet["source_hashes"].items():
        assert sha(ROOT / path) == expected, path
    previous_guide = read(HERE / "guide_interaction_receipt.json")
    for row in previous_guide["targets"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    assert previous_guide["question_count_by_block"] == [3, 3, 4, 3]
    requirements = read(HERE / "requirements_literature_receipt.json")
    assert requirements["status"] == "PASS_IN_STATED_SCOPE"
    assert requirements["master_sha256"] == sha(BASE / "a_diagnosis/MASTER_REQUIREMENTS_REVIEW.json")
    assert requirements["literature_map_sha256"] == sha(BASE / "a_diagnosis/literature_use_map.json")
    for path, expected in requirements["source_bindings"].items():
        assert sha(ROOT / path) == expected, path

    nav = read(ROOT / "task1/evidence/goal3/teacher_delivery_mapping.json")
    assert len(nav["entries"]) == 22
    for row in nav["sources"].values():
        assert sha(ROOT / row["path"]) == row["sha256"]
    reports, nb_sources = {}, {}
    for key, row in nav["reports"].items():
        assert sha(ROOT / row["path"]) == row["pdf_sha256_at_navigation"]
        assert sha(ROOT / row["text_path"]) == row["text_sha256"]
        actual_text = subprocess.check_output(["pdftotext", "-layout", str(ROOT / row["path"]), "-"], text=True)
        assert actual_text == (ROOT / row["text_path"]).read_text()
        pages = actual_text.split("\f")
        if not pages[-1].strip():
            pages.pop()
        assert len(pages) == row["pages"]
        stem = "experiment1" if key == "E" else "process1"
        for n, text in enumerate(pages, 1):
            assert hashlib.sha256(text.encode()).hexdigest() == row["page_text_sha256"][str(n)]
            png = ROOT / "task1/evidence/goal3/report_build/render200" / stem / f"page-{n:02d}.png"
            assert sha(png) == row["page_render_sha256"][str(n)]
        assert row["render_dpi"] == 200 and "page_render_sha256_at_B_visual_review" not in row
        reports[key] = pages
    for key, row in nav["notebooks"].items():
        path = ROOT / row["path"]
        assert sha(path) == row["file_sha256"]
        nb_sources[key] = read(path)["cells"]
        assert len(nb_sources[key]) == row["cell_count"]
    mapped_cells, mapped_page_anchors = 0, 0
    for entry in nav["entries"]:
        for row in entry["notebooks"]:
            for loc in row["cells"]:
                cell = nb_sources[row["notebook"]][loc["index_zero_based"]]
                assert cell["id"] == loc["cell_id"] and cell["cell_type"] == loc["cell_type"]
                assert hashlib.sha256("".join(cell["source"]).encode()).hexdigest() == loc["source_sha256"]
                mapped_cells += 1
        for row in entry["reports"]:
            # A locator can cover a section plus continuation/figure pages.
            # Its identifying anchor must occur within that actual page range,
            # but need not be repeated verbatim on every continuation page.
            anchor_pages = []
            for n in row["pdf_pages_one_based"]:
                assert 1 <= n <= len(reports[row["report"]])
                if compact(row["verified_text_anchor"]) in compact(reports[row["report"]][n - 1]):
                    anchor_pages.append(n)
                    mapped_page_anchors += 1
            assert anchor_pages, (entry["id"], row["pdf_pages_one_based"], row["verified_text_anchor"])

    technical = ROOT / "task1/docs/goal3/TECHNICAL_HANDOFF.md"
    text = technical.read_text()
    for row in read(HERE / "notebook_runs_receipt.json")["executions"]:
        assert f'{row["elapsed_seconds"]:.2f}秒' in text
        assert row["execution_receipt"].replace("task1/", "../../", 1) in text
    for marker in ("本次四次新内核 FULL 均已实际完成", "113 个非 PDF payload", "SIGTERM/143", "触发来源仍未确认"):
        assert marker in text, marker
    for marker in ("BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK", "FINAL_REVIEW", "LEARNING", "NOT_READY", "PENDING", "source_crs=UNVERIFIED", "266.016754"):
        assert marker in text

    response_path = BASE / "FINAL_RESPONSE.md"
    response = response_path.read_text()
    assert "合并内部验收和真实发布正在收尾" in response
    assert "不预填未来提交SHA" in response
    for row in read(HERE / "notebook_runs_receipt.json")["executions"]:
        assert f'{row["elapsed_seconds"]:.2f}秒' in response
    package = read(HERE / "package_receipt.json")
    assert package["zip_sha256"] in response and package["package_content_id"] in response
    links = 0
    for path in [ROOT / t["path"] for t in packet["targets"] if t["path"].endswith(".md")] + [response_path]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            assert (path.parent / unquote(target.split("#")[0].strip("<>"))).resolve().exists(), (path, target)
            links += 1
    receipt_names = ["requirements_literature_receipt.json", "review_input_snapshot_receipt.json",
                     "guide_interaction_receipt.json", "notebook_runs_receipt.json", "package_task_receipt.json",
                     "visual_content_receipt.json", "report_numbers_receipt.json", "upload_bundle_receipt.json"]
    out = {
        "role_context": "/root/c_independent", "checked_at": datetime.now(timezone.utc).isoformat(),
        "tasks": {"handoffs": {"status": "VERIFIED", "targets": packet["targets"], "source_hashes": packet["source_hashes"],
            "checked_components": [
                "C read all65 requirement rows, their methods/why/denominators/status/nonproof and all seven teaching differences; original teacher XML and frozen approval/actual result checks distinguish teacher examples, starter details and later approved implementation.",
                "All28 literature-use rows preserve archived reading/access limits; S10 direct-report versus prior-audit reading distinguished; causal influence is not inferred from code similarity; current formal cited claims stay within documented original text or official conversion semantics.",
                "Immutable governance inputs are real byte snapshots after leaf acceptance;143 snapshot events verified as active prefix, real timestamp boundary checked, all20 historical previous_acceptance preserved exactly. MASTER snapshots are not a second active state and all current source hashes are checked.",
                "Complete four-block guide13 evidence-linked questions,24 functions and10 stable cells reviewed; no imaginary user answers, oral exam grade, Understanding PASS or Evidence Lock.",
                "Current Technical Handoff read fully; four actual FULL durations/paths/scopes, interrupted attempts, final/executed ZIP equivalence and document/numeric provenance match independently inspected outputs. Original Interaction Handoff remains exact historical byte prefix with a truthful current append.",
                "All22 TD entries directly checked against actual current PDFs, every registered page-text/render hash and mapped cell source. A section/figure range must contain its identifying anchor; continuation pages are not falsely required to repeat the section heading. C read/viewed the actual ranges. Navigation does not substitute for executed Notebook or real visual review.",
                "Task-owned interaction inventory/spec/Lock limits preserved; identity dependency resolved separately. Formal Process evidence remains externally blocked and new webpageGPT/user/submission states remain pending.",
            ]}},
        "submission": {"path": str(packet_path.relative_to(ROOT)), "sha256": sha(packet_path)},
        "linked_C_receipts": [{"path": str((HERE / name).relative_to(ROOT)), "sha256": sha(HERE / name)} for name in receipt_names],
        "teacher_navigation": {"entries": len(nav["entries"]), "mapped_cells_checked": mapped_cells, "mapped_actual_PDF_page_anchors_checked": mapped_page_anchors, "report_pages_current_text_and_png_hashes": 34},
        "local_md_links_checked": links,
        "prepublication_response_observation": {"path": str(response_path.relative_to(ROOT)), "observed_sha256": sha(response_path), "scope": "C read the entire prepublication response and checked its factual run/artifact/source claims and paths. It truthfully leaves combined internal acceptance and future push pending; this observation is not acceptance of subsequent publication edits or future remote consistency."},
        "limit": "Current handoff engineering is VERIFIED. This does not close Process Evidence, user Understanding, new GPT_SECOND_REVIEW, final Deliverable or submission gates. Active CL/current-state/publication deltas are reviewed separately.",
    }
    (HERE / "handoffs_task_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "VERIFIED", "task": "handoffs", "targets": len(packet["targets"]), "sources": len(packet["source_hashes"]), "local_md_links_checked": links, "TD_actual_page_anchors": mapped_page_anchors}))


if __name__ == "__main__":
    main()
