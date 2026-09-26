"""Independent C verification of the repaired three-figure preview only."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import Audit, read_compressed
from task1.workflow.io import read_json, write_json, digest, now
from task1.scripts.build_goal2_figures import FigureSet

EV = ROOT / "task1/evidence/goal2"
OUT = Path(__file__).parent
PREVIEW = EV / "presentation_checks/candidate_preview_02"
NAMES = ["real_trajectory_cases", "synthetic_metric_counterexamples", "goal2_actual_architecture"]


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def main():
    audit = Audit()
    issue = read_json(EV / "goal_state.json")["issues"]["G2-B-CANDIDATE-FIGURE-001"]
    audit.check("actual_issue_repair_submitted", issue["status"] == "REGRESSION_PENDING")
    for target in issue["repair_evidence"]:
        audit.check("repair_target_current", digest(ROOT / target["path"]) == target["sha256"])
    before, after = PREVIEW / "before", PREVIEW / "after"
    data = read_json(after / "figure_data.json")
    old_data = read_json(before / "figure_data.json")
    source = ROOT / "task1/scripts/build_goal2_figures.py"
    audit.check("generator_source_epoch", digest(source) == digest(PREVIEW / "generator_after.py"))
    defs = []
    for filename in ("generator_before.py", "generator_after.py"):
        tree = ast.parse((PREVIEW / filename).read_text())
        defs.append({node.name: ast.dump(node) for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))})
    audit.same("function_set_unchanged", sorted(defs[0]), sorted(defs[1]))
    audit.same("bounded_display_repair", sorted(k for k in defs[0] if defs[0][k] != defs[1][k]), ["_draw_trajectory", "architecture", "case_figures"])
    audit.check("case_selection_bytes_unchanged", (before / "CASE_SELECTION.json").read_bytes() == (after / "CASE_SELECTION.json").read_bytes())
    for key in NAMES[:2]:
        audit.same("numeric_figure_data_unchanged:" + key, data[key], old_data[key])
    selection = read_json(after / "CASE_SELECTION.json")
    manifest = read_json(EV / "runs" / selection["source_run"] / "manifest.json")
    candidates = {entry["config_id"]: read_compressed(EV / "runs" / selection["source_run"] / entry["file"])["records"] for entry in manifest["artifacts"].values()}
    baseline = {row["record_id"]: row for row in candidates["cfg-b15b8281b73592fb"]}
    cards = read_json(EV / "data/raw_diagnostics.json")
    audit.same("heldout_case_scope", selection["scope"], manifest["input_ids"])
    audit.same("render_selection_data", selection["cases"], data["real_trajectory_cases"])
    for case in selection["cases"]:
        cid, rid = case["config_id"], case["record_id"]
        if case["role"].startswith("Representative "):
            level = case["role"].split()[-1]
            group = [x for x in baseline if cards[x]["stratum"].startswith(level + "_")]
            median = statistics.median(cards[x]["span_work_m"] for x in group)
            expected = min(group, key=lambda x: (abs(cards[x]["span_work_m"] - median), x))
            audit.check("representative_raw_span_rule:" + level, rid == expected and cid == "cfg-b15b8281b73592fb")
        elif case["role"] == "Largest covered-point loss":
            ranked = sorted((-(baseline[row["record_id"]]["metrics"]["common_covered_points"] - row["metrics"]["common_covered_points"]), row["record_id"], key)
                            for key, records in candidates.items() for row in records)
            audit.check("worst_coverage_rule", (-case["criterion_value"], rid, cid) == ranked[0])
        elif case["role"] == "Largest available raw error":
            ranked = sorted((-row["metrics"]["common_max_error"], row["record_id"], key) for key, records in candidates.items()
                            for row in records if row["metrics"]["common_max_error"] is not None)
            audit.check("worst_available_common_error_rule", (-case["criterion_value"], rid, cid) == ranked[0])
        else:
            ranked = sorted((abs(row["parameters"]["dp"] - point["error"]), row["record_id"], key, point["index"])
                            for key, records in candidates.items() for row in records for stage in row["stages"] if stage["name"] == "P"
                            for op in stage["operations"] for point in op["runtime_dp_check"]["error_by_original_index"]
                            if point["error"] > 0 and abs(row["parameters"]["dp"] - point["error"]) > 0)
            audit.check("near_threshold_original_case_rule", (case["criterion_value"], rid, cid, case["original_index"]) == ranked[0])
    suite = read_json(EV / "counterexamples/formal-02/synthetic_cases.json")
    for row in data["synthetic_metric_counterexamples"]:
        example = next(item for item in suite["cases"] if item["case_id"] == row["case_id"])
        audit.same("synthetic_actual_metrics", row["metrics"], example["executions"][row["execution"]]["output"]["metrics"])
        audit.check("synthetic_explicit_classification", row["classification"] == "SYNTHETIC_COUNTEREXAMPLE")
    graph = data[NAMES[2]]
    old_graph = old_data[NAMES[2]]
    audit.same("unchanged_architecture_edges", graph["edges"], old_graph["edges"])
    audit.same("unchanged_architecture_roles", [node[:-1] for node in graph["nodes"]], [node[:-1] for node in old_graph["nodes"]])
    expected_paths = {"C": "task1/evidence/goal2/c_contract/independent_numeric.py", "modes": "task1/workflow/g2_modes.py", "root": "task1/workflow/g2_journal.py"}
    for node in graph["nodes"]:
        if node[-1]:
            audit.check("actual_module:" + node[0], (ROOT / node[-1]).is_file())
        if node[0] in expected_paths:
            audit.check("role_implementation:" + node[0], node[-1] == expected_paths[node[0]])
    cells = ET.parse(after / graph["drawio_file"]).findall(".//mxCell")
    vertices = {node.get("id"): node for node in cells if node.get("vertex") == "1"}
    edges = [node for node in cells if node.get("edge") == "1"]
    audit.check("native_editable_topology", len(vertices) == 11 and len(edges) == 13 and len({c.get("id") for c in cells}) == len(cells))
    for ident, label, x, y, w, h, fill, module in graph["nodes"]:
        node = vertices[ident]
        geom = node.find("mxGeometry")
        audit.check("native_vertex:" + ident, node.get("value") == label and "image=" not in node.get("style", "")
                    and [float(geom.get(k)) for k in ("x", "y", "width", "height")] == [x * 100, (9 - y - h) * 100, w * 100, h * 100])
    for edge, (start, end, label, dashed) in zip(edges, graph["edges"]):
        audit.check("native_edge", [edge.get(k) for k in ("source", "target", "value")] == [start, end, label]
                    and start in vertices and end in vertices and ("dashed=1" in edge.get("style", "")) == dashed)
    figure_manifest = read_json(after / "figure_manifest.json")
    audit.check("figure_generator_hash", figure_manifest["generator_sha256"] == digest(source))
    audit.check("figure_data_hash", figure_manifest["figure_data_sha256"] == digest(after / "figure_data.json"))
    audit.check("P2_palette", figure_manifest["palette_sha256"] == digest(ROOT / "templates/latex/common/p2_cloud_sorbet_colors.tex"))
    rendered = []
    render_directory = OUT / "candidate_figure_pdf_renders"
    render_directory.mkdir(exist_ok=True)
    for figure in figure_manifest["figures"]:
        for info in [*figure["formats"].values(), figure["pdf_render"]]:
            audit.check("actual_export_hash", digest(after / info["file"]) == info["sha256"])
        path = render_directory / figure["name"]
        subprocess.run(["pdftoppm", "-r", "200", "-singlefile", "-png", str(after / figure["formats"]["pdf"]["file"]), str(path)], check=True, capture_output=True)
        png = path.with_suffix(".png")
        audit.check("independent_PDF_render_bytes", digest(png) == figure["pdf_render"]["sha256"])
        rendered.append(bound(png))
    # Actual visual defects were inspected and rejected; a separate deterministic
    # table-binding fault verifies that changed evidence cannot be accepted.
    with tempfile.TemporaryDirectory(dir=OUT, prefix="figure-target-test-") as temporary:
        directory = Path(temporary)
        path = directory / "table.json"
        write_json(path, [1])
        writer = FigureSet.__new__(FigureSet)
        writer.sources = {}
        binding = {"tables": {"table.json": digest(path)}}
        audit.same("valid_receipt_accepted", writer.table(directory, binding, "table.json"), [1])
        write_json(path, [2])
        error = None
        try:
            writer.table(directory, binding, "table.json")
        except ValueError as exc:
            error = str(exc)
        audit.check("fault_rejected", bool(error and "UNBOUND_OR_CHANGED_PLOT_TABLE" in error))
    freeze = read_json(EV / "evaluation_freeze.json")
    for path, sha in freeze["processing_source_hashes"].items():
        audit.check("processing_source_epoch", digest(ROOT / path) == sha)
    receipt = {"issue_id": "G2-B-CANDIDATE-FIGURE-001", "parent_task": "figures", "status": "VERIFIED" if not audit.errors else "REJECTED", "at": now(),
               "role_context": "/root/c_contract", "targets": deepcopy(issue["repair_evidence"]), "source_hashes": deepcopy(issue["repair_source_hashes"]),
               "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch", "three_actual_PDF_renders", "actual_before_after_visual_comparison",
                                      "selection_and_numbers_unchanged", "independent_case_selection_reconstruction", "native_drawio_editability", "real_role_module_mapping"],
               "unchecked_components": ["full_11_figure_final_set", "diagrams_net_GUI_roundtrip", "complete_A15_acceptance"],
               "check_count": audit.check_count, "errors": audit.errors, "audit_program": bound(Path(__file__)), "rendered_evidence": rendered,
               "actual_viewed_images": [bound(after / "pdf-render-200dpi" / (name + ".png")) for name in NAMES] + [bound(before / "pdf-render-200dpi" / (name + ".png")) for name in NAMES[:2]],
               "visual_observations": {"real_trajectory_cases": "C viewed before/after: narrow axis/tick collision and no-output legend obstruction removed; six equal-scale panels, external complete legend, index2 residual4.999598/tolerance5 annotation clear.",
                                       "synthetic_metric_counterexamples": "C viewed before/after: horizontal axis no longer collapsed; indices0,1,2 separated; authored-data label, crossing1 and distinct own-clean0/common0.447 metrics legible.",
                                       "goal2_actual_architecture": "C viewed corrected export: governance/runtime separated, feedback/repair routes and actual role labels readable without clipping; independent C metadata points to C oracle. Eleven native vertices/thirteen connected edges parsed."},
               "plotting_skill": "tools/skills/publication-plots/SKILL.md", "new_model_calls": 0,
               "scope_limit": "Closes these actual preview display defects. No final all-figure acceptance or model-result conclusion.",
               "auditor_local_repair": {"previous_receipt": bound(OUT / "candidate_figure_closure_receipt.json"),
                                        "previous_source": bound(OUT / "review_candidate_figures_before_tuple_fix.py"),
                                        "fact": "Three equal tuples were incorrectly rejected by a JSON-only recursive comparison helper. Fixed three calls to explicit tuple equality; other checks and production files unchanged."}}
    write_json(OUT / "candidate_figure_closure_receipt_v2.json", receipt, exclusive=True)
    print({key: receipt[key] for key in ("status", "check_count", "errors")})


if __name__ == "__main__":
    main()
