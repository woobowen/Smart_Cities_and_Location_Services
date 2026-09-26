"""Bounded, read-only checks for the candidate presentation repair."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


before, after = HERE / "before", HERE / "after"
old_tree = ast.parse((HERE / "generator_before.py").read_text())
new_text = (HERE / "generator_after.py").read_text()
compile(new_text, "generator_after.py", "exec")
new_tree = ast.parse(new_text)
old_defs = {n.name: ast.dump(n) for n in old_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
new_defs = {n.name: ast.dump(n) for n in new_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
assert set(old_defs) == set(new_defs)
changed = sorted(name for name in old_defs if old_defs[name] != new_defs[name])
assert changed == ["_draw_trajectory", "architecture", "case_figures"]
callers = [n.name for n in new_tree.body if isinstance(n, ast.FunctionDef)
           and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                   and c.func.id == "_draw_trajectory" for c in ast.walk(n))]
assert callers == ["case_figures"]
assert digest(ROOT / "task1/scripts/build_goal2_figures.py") == digest(HERE / "generator_after.py")

assert (before / "CASE_SELECTION.json").read_bytes() == (after / "CASE_SELECTION.json").read_bytes()
old_data, new_data = read(before / "figure_data.json"), read(after / "figure_data.json")
for key in ("real_trajectory_cases", "synthetic_metric_counterexamples"):
    assert old_data[key] == new_data[key]
old_graph, graph = old_data["goal2_actual_architecture"], new_data["goal2_actual_architecture"]
assert old_graph["edges"] == graph["edges"]
assert all(a[:-1] == b[:-1] for a, b in zip(old_graph["nodes"], graph["nodes"]))
assert {b[0] for a, b in zip(old_graph["nodes"], graph["nodes"]) if a[-1] != b[-1]} == {"C"}
assert next(n[-1] for n in graph["nodes"] if n[0] == "C") == "task1/evidence/goal2/c_contract/independent_numeric.py"
module_hashes = {n[-1]: digest(ROOT / n[-1]) for n in graph["nodes"] if n[-1]}

xml = ET.parse(after / graph["drawio_file"])
cells = xml.findall(".//mxCell")
assert len({c.get("id") for c in cells}) == len(cells)
vertices = {c.get("id"): c for c in cells if c.get("vertex") == "1"}
edges = [c for c in cells if c.get("edge") == "1"]
assert len(vertices) == len(graph["nodes"]) == 11
assert len(edges) == len(graph["edges"]) == 13
for ident, label, x, y, width, height, fill, module in graph["nodes"]:
    cell = vertices[ident]
    assert cell.get("value") == label and "image=" not in cell.get("style", "")
    geometry = cell.find("mxGeometry")
    assert float(geometry.get("x")) == x * 100
    assert float(geometry.get("y")) == (9 - y - height) * 100
    assert float(geometry.get("width")) == width * 100
    assert float(geometry.get("height")) == height * 100
for edge, (source, target, label, dashed) in zip(edges, graph["edges"]):
    assert source in vertices and target in vertices
    assert (edge.get("source"), edge.get("target"), edge.get("value")) == (source, target, label)
    assert ("dashed=1" in edge.get("style", "")) == dashed

manifest = read(after / "figure_manifest.json")
assert manifest["generator_sha256"] == digest(HERE / "generator_after.py")
assert manifest["figure_data_sha256"] == digest(after / "figure_data.json")
assert manifest["raster_check_status"] == "PASSED" and manifest["pdf_render_dpi"] == 200
for figure in manifest["figures"]:
    for output in [*figure["formats"].values(), figure["pdf_render"]]:
        assert digest(after / output["file"]) == output["sha256"]
pdf_text = {}
for name in ("real_trajectory_cases", "synthetic_metric_counterexamples", "goal2_actual_architecture"):
    text = subprocess.check_output(["pdftotext", str(after / (name + ".pdf")), "-"], text=True)
    pdf_text[name] = " ".join(text.split())
assert "No final output" in pdf_text["real_trajectory_cases"]
assert all(label in pdf_text["real_trajectory_cases"] for label in ("Raw points", "Final segments", "4.999598", "Tolerance = 5"))
assert all(value in pdf_text["synthetic_metric_counterexamples"] for value in ("crossings: 1", "0 working m", "0.447 working m"))
assert all(label in pdf_text["goal2_actual_architecture"] for label in ("B-Repair", "C · independent", "zero-model search", "GoalJournal"))
freeze = read(ROOT / "task1/evidence/goal2/evaluation_freeze.json")
assert all(digest(ROOT / path) == sha for path, sha in freeze["processing_source_hashes"].items())
print(json.dumps({"status": "PASSED", "changed_functions": changed,
                  "trajectory_helper_callers": callers, "parameter_and_mode_functions_unchanged": True,
                  "case_selection_bytes_unchanged": True, "numerical_figure_data_unchanged": True,
                  "drawio_native_editable_vertices": len(vertices), "drawio_connected_edges": len(edges),
                  "drawio_export_spec_matches": True, "drawio_GUI_roundtrip_tested": False,
                  "module_hashes": module_hashes, "all_export_hashes_valid": True,
                  "pdf_text_checked": list(pdf_text), "processing_epoch_unchanged": True,
                  "generator_sha256": digest(HERE / "generator_after.py")}, indent=2))
