"""Bind C's actual source/content/image review to the submitted report leaves.

This does not compile/replot, rerun numerical experiments, or sign Evidence Lock.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
CLOSEOUT = HERE.parent
EV = ROOT / "task1/evidence/goal3"
FIG = ROOT / "task1/figures/goal3"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    submission_path = CLOSEOUT / "report_review_submissions.json"
    submission = read(submission_path)
    visual_path = HERE / "visual_content_receipt.json"
    visual = read(visual_path)
    assert len(visual["pages"]) == 34
    for page in visual["pages"]:
        assert page["actual_visual_inspection"] and page["content_read"] and page["status"] == "PASS"
        assert page["page_sha256"] == sha(ROOT / page["page_path"])
    current = read(EV / "current_runs.json")
    fm, fd = read(FIG / "figure_manifest.json"), read(FIG / "figure_data.json")
    assert fm["figure_data_sha256"] == sha(FIG / "figure_data.json")
    assert fm["source_crs"] == "UNVERIFIED"
    for path, expected in fm["sources"].items():
        assert sha(ROOT / path) == expected
    manifests = {key: read(EV / "runs" / current[key] / "manifest.json")
                 for key in ("development", "selection", "confirmation", "production")}
    # Directly compare plotted aggregate values to frozen source manifests.
    for row in fd["development_candidates"]:
        m = manifests["development"]
        p, own = m["comparisons"][row["strategy"] + "|R0"], m["record_metrics"][row["strategy"]]
        assert row == {"strategy": row["strategy"], "coverage_delta": p["coverage_delta"],
                       "protected": p["protected_records"], "gain_records": p["strict_gain_records"],
                       "failed": len(p["failure_records"]), "final_points": own["n_final"],
                       "maximum_P_error_work_m": own["dp_max_error"], "status": p["status"]}
    for key, row in fd["point_fates_and_coverage"].items():
        m = manifests[key]
        assert row["records"] == len(m["input_ids"])
        assert row["raw_points"] == m["record_metrics"]["R0"]["n_input"]
        for strategy, values in row["summaries"].items():
            assert values == m["record_metrics"][strategy]
            assert sum(values[k] for k in ("n_filtered", "n_direction_removed", "n_dp_removed", "n_final")) == row["raw_points"]
    for row in fd["selection_tradeoffs"]["counts"]:
        p = manifests["selection"]["comparisons"][row["strategy"] + "|R0"]
        assert row["gain"] == p["strict_gain_records"]
        assert row["failed"] == len(p["failure_records"])
        assert row["unchanged"] == p["protected_records"] - row["gain"]
    pairs = fd["final_confirmation_pairs"]["pairs"]
    cm = manifests["confirmation"]
    assert len(pairs) == len(cm["input_ids"]) == 600
    assert {p["record_id"] for p in pairs} == set(cm["input_ids"])
    assert sum(p["feasible"] and p["strict_gain"] for p in pairs) == cm["comparisons"]["S0|R0"]["strict_gain_records"] == 349
    assert sum(p["feasible"] for p in pairs) == 600
    for row in fd["final_confirmation_pairs"]["strata"]:
        selected = [p for p in pairs if p["stratum"] == row["stratum"]]
        assert len(selected) == row["n"]
        assert sum(p["strict_gain"] and p["feasible"] for p in selected) == row["gain"]
    assert fd["incumbent_decision_path"] == read(EV / "decision_history.json")
    arc = fd["goal3_actual_workflow"]
    assert arc["drawio_sha256"] == sha(FIG / "goal3_actual_workflow.drawio")
    cells = ET.parse(FIG / "goal3_actual_workflow.drawio").findall(".//mxCell")
    vertices = {c.attrib["id"]: c.attrib["value"] for c in cells if c.get("vertex") == "1"}
    edges = [[c.attrib["source"], c.attrib["target"]] for c in cells if c.get("edge") == "1"]
    assert vertices == {n[0]: n[1] for n in arc["nodes"]} and edges == arc["edges"]
    figure_views = []
    notes = {
        "development_candidates": "10 registered alternatives visible, including all failed diagnostics; labels and common R0 reference readable.",
        "selection_tradeoffs": "240-record denominator and all six strategy/record protection failures shown; no legend overlap.",
        "point_fates_and_coverage": "600-record confirmation and 11,386-record production separated; coverage and explicit storage distinguished; all values readable.",
        "final_confirmation_pairs": "345 comparable geometries and 255 unavailable cases explicitly separated; all 600 retain guard/coverage denominator.",
        "production_trajectory_cases": "All nine panels readable; record 352 point 105 marked D-deleted, common scales within row, no basemap/physical CRS implication.",
        "goal3_actual_workflow": "Actual governance versus deterministic tool boundary, C-to-repair and pre-freeze feedback paths readable. External identity is the input responsibility, not a present identity blocker; current report explicitly resolves identity.",
        "incumbent_decision_path": "Historical five-stage decisions and fallback S0 visible, not a weighted quality score or new user choices.",
    }
    for figure in fm["figures"]:
        for item in figure["formats"].values():
            assert sha(FIG / item["file"]) == item["sha256"]
        p = FIG / figure["pdf_render"]["file"]
        assert figure["pdf_render"]["dpi"] == 200 and sha(p) == figure["pdf_render"]["sha256"]
        figure_views.append({"figure": figure["name"], "path": str(p.relative_to(ROOT)),
                             "sha256": sha(p), "dpi": 200, "tool": "view_image(detail=original)",
                             "actual_visual_inspection": True, "status": "PASS", "notes": notes[figure["name"]]})
    tasks = {}
    for task, row in submission["tasks"].items():
        for target in row["targets"]:
            assert sha(ROOT / target["path"]) == target["sha256"], target["path"]
        for path, expected in row["source_hashes"].items():
            assert sha(ROOT / path) == expected, path
        checked = {
            "figures": ["Read all current figures.py/FigureSet source, hash-bound numeric manifests and actual figure values; independent report_numbers covers production/confirmation and record352 finite-segment witness.",
                        "Actual original-size views of all seven current 200dpi standalone figure renders and all report pages embedding them; no substituted thumbnails.",
                        "Every submitted format/source hash current; SVG/PDF/native draw.io structures retained; P2 shared color source unchanged.",
                        "Historical run independent receipts are inherited numeric evidence, not new C recomputation of every source record."],
            "experiment_report": ["Read both current full text/source and all 22 actual physical-page PNGs; current byte bindings preserved in visual_content_receipt.",
                                  "Identity authoritative-source regeneration and PDF metadata/cover checked; no unresolved citation/compile/glyph/crop issues.",
                                  "Direct frozen-manifest numeric checks, denominators, D2/finite-segment DP scope, source_crs UNVERIFIED and record352 D-stage counterexample verified.",
                                  "Cawley access-layer wording and table14 separation repaired by B and independently re-viewed; negatives/memory noncausal limits kept."],
            "process_report": ["Read current full source/text and all12 original-size200dpi pages; metadata/PDF/source bindings current.",
                               "PartI/PartII, actual A/B/C governance and historical repairs/decision evidence preserved; current identity resolved without rewriting historical prompts.",
                               "Teacher and task-owned inventories separate technical material from absent original Human-AI evidence; no original screenshot, spec, evidence anchor, or Lock invented.",
                               "Complete formal interactive-evidence acceptance remains externally blocked; technical draft/visual review does not constitute Evidence Master or user acceptance."],
        }[task]
        tasks[task] = {"status": "BLOCKED_EXTERNAL" if task == "process_report" else "VERIFIED",
                       "targets": row["targets"], "source_hashes": row["source_hashes"], "checked_components": checked}
        if task == "process_report":
            tasks[task]["external_dependencies"] = [
                "Required authentic historical conversation originals/screenshots or complete source text are absent from the approved task evidence scope.",
                "Evidence Master approved inclusion/narrative/annotation specification is absent; Codex cannot choose highlights/anchors/order as substitute.",
                "No matching Evidence/Block Lock exists. Lock requires actual materials plus Evidence Master review; internal C cannot issue it.",
            ]
    out = {"role_context": "/root/c_independent", "submission_sha256": sha(submission_path),
           "tasks": tasks, "standalone_figure_visual_views": figure_views,
           "linked_receipts": {p.name: sha(p) for p in [visual_path, HERE / "report_numbers_receipt.json", HERE / "frozen_identity_receipt.json", HERE / "result_summary_equivalence.json"]},
           "scope_limit": "C did not edit reviewed core/content/numeric results. Notebook FULL, final package and overall release have separate receipts. Understanding remains LEARNING; new GPT_SECOND_REVIEW remains PENDING; Submission remains NOT_READY."}
    (HERE / "report_tasks_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"tasks": {k: v["status"] for k,v in tasks.items()}, "actual_standalone_figure_views": len(figure_views)}))


if __name__ == "__main__":
    main()
