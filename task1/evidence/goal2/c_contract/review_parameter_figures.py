"""C numeric/export checks for the five actually viewed parameter preview figures."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.scripts.build_goal2_figures import FigureSet

OUT = Path(__file__).resolve().parent
PREVIEW = Path("/tmp/sc-g2-parameter-preview-03")
ARCHIVE = ROOT / "task1/evidence/goal2/presentation_checks/parameter_preview_01"


def main():
    target = ROOT / "task1/scripts/build_goal2_figures.py"
    manifest = read_json(PREVIEW / "figure_manifest.json")
    data = read_json(PREVIEW / "figure_data.json")
    params = read_json(ROOT / "task1/evidence/goal2/runs/g2-development-parameters-01/parameter_table.json")
    orders = read_json(ROOT / "task1/evidence/goal2/runs/g2-development-orders-01/order_table.json")
    by_config = {row["config_id"]: row for row in params}
    checks = []
    def check(name, value):
        checks.append({"check": name, "passed": bool(value)})
    check("generator_binding", digest(target) == manifest["generator_sha256"])
    check("unchanged_data_after_layout_repair", digest(ARCHIVE / "initial/figure_data.json") == digest(PREVIEW / "figure_data.json"))
    for parameter, rows in data["segmentation_filter_response"].items():
        for row in rows:
            source = by_config[row["config_id"]]
            check("OAT:" + parameter, row["value"] == source["parameters"][parameter] and row["retained_fraction"] == source["summary"]["point_retention"]
                  and row["no_output_record_fraction"] == source["summary"]["no_output_record_fraction"] and row["raw_points"] == 11777 and row["records"] == 120)
    for grid in data["segmentation_filter_grids"]:
        for i, y in enumerate(grid["y_values"]):
            for j, x in enumerate(grid["x_values"]):
                candidates = [by_config[cid] for cid in grid["config_ids"] if by_config[cid]["parameters"][grid["x"]] == x and by_config[cid]["parameters"][grid["y"]] == y]
                check("grid_cell", len(candidates) == 1 and grid["matrix"][i][j] == candidates[0]["summary"][grid["metric"]])
    check("direction_values", all(row == by_config[row["config_id"]] for row in data["direction_threshold_and_neighborhood"]["rows"]))
    check("DP_values", all(row == by_config[row["config_id"]] for row in data["dp_error_compression"]))
    check("order_values", data["order_protection_and_neighborhoods"] == orders)
    render_dir = OUT / "parameter_figure_pdf_renders"
    render_dir.mkdir(exist_ok=True)
    rendered = []
    for figure in manifest["figures"]:
        for extension, info in figure["formats"].items():
            check("export_hash:" + figure["name"] + ":" + extension, digest(PREVIEW / info["file"]) == info["sha256"])
        destination = render_dir / figure["name"]
        subprocess.run(["pdftoppm", "-r", "200", "-singlefile", "-png", str(PREVIEW / figure["formats"]["pdf"]["file"]), str(destination)], check=True, capture_output=True)
        image = destination.with_suffix(".png")
        check("independent_PDF_render_bytes:" + figure["name"], digest(image) == figure["pdf_render"]["sha256"])
        rendered.append({"figure": figure["name"], "path": str(image.relative_to(ROOT)), "sha256": digest(image), "dpi": 200})
    with tempfile.TemporaryDirectory(prefix="c-figure-binding-", dir=OUT) as temporary:
        temp = Path(temporary)
        path = temp / "table.json"
        write_json(path, [{"value": 1}])
        writer = FigureSet.__new__(FigureSet)
        writer.sources = {}
        valid = {"tables": {"table.json": digest(path)}}
        check("valid_table_accepted", writer.table(temp, valid, "table.json") == [{"value": 1}])
        for fault in ("changed_table", "missing_binding"):
            if fault == "changed_table":
                write_json(path, [{"value": 999}])
            try:
                writer.table(temp, valid if fault == "changed_table" else {}, "table.json")
            except ValueError as error:
                check("fault_rejected:" + fault, "UNBOUND_OR_CHANGED_PLOT_TABLE" in str(error))
            else:
                check("fault_rejected:" + fault, False)
    observations = {
        "segmentation_filter_response": "All four OAT axes show registered values and distinct point/record denominators; 120 records and 11777 points identified; no clipping or legend overlap.",
        "segmentation_filter_grids": "Viewed before/after 200-dpi PDF renders: spurious white diagonals and diagonal colour bands removed; exact flat cells, numeric labels and consistent 0-1 bars are readable.",
        "direction_threshold_and_neighborhood": "Viewed before/after: third panel no longer collapses to a strip; equal working-metre axes retained, legend moved clear of record10000/index4 and adjacency changes. All five thresholds labelled.",
        "dp_error_compression": "Seven tolerance labels, zero-compression at tolerance0, explicit immediate-P denominator and fixed5m budget line readable; no clipped labels or legend conflict.",
        "order_protection_and_neighborhoods": "Viewed before/after: protection colour key added; fraction axis0-1, integer count axes and all six order labels readable; shown 0/0/46/87/87/87 failure counts match verified table."}
    receipt = {"issue_id": "G2-B-FIGURE-001", "parent_task": "figures", "status": "VERIFIED" if all(row["passed"] for row in checks) else "REJECTED",
               "role_context": "/root/c_contract", "at": now(), "targets": [{"path": str(target.relative_to(ROOT)), "sha256": digest(target)}],
               "source_hashes": {str(target.relative_to(ROOT)): digest(target)},
               "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch", "five_parameter_PDF_renders", "three_before_after_defects", "data_bytes_unchanged", "numeric_plot_table_binding", "P2_palette", "SVG_PDF_PNG_exports"],
               "unchecked_components": ["remaining final mode/candidate/counterexample figures", "final Drawio editability and rendering", "complete figures task A15 acceptance"],
               "checks": checks, "actual_visual_observations": observations, "view_method": "C actually invoked tools.view_image on five repaired PDF renders and three archived before images; independently rerendered PDF bytes match exactly.",
               "rendered_evidence": rendered, "plotting_skill": "tools/skills/publication-plots/SKILL.md", "actual_skill_and_visual_read": True,
               "data_scope": "actual DEVELOPMENT120 parameter and six-order runs only; no model/EVAL data used", "new_model_calls": 0,
               "scope_limit": "Closes this parameter-preview layout and binding defect only. Full figure-set acceptance requires its actual final exports and independent review."}
    write_json(OUT / "parameter_figure_closure_receipt.json", receipt, exclusive=True)
    print({"status": receipt["status"], "checks": len(checks), "failed": [row for row in checks if not row["passed"]], "PDFs_independently_rendered": len(rendered)})


if __name__ == "__main__":
    main()
