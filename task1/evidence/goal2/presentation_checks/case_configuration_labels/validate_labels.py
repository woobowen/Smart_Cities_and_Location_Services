"""Read-only binding checks for the real-case configuration-label repair."""
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


old_text = (HERE / "generator_before.py").read_text()
new_text = (HERE / "generator_after.py").read_text()
compile(new_text, "generator_after.py", "exec")
old_defs = {n.name: ast.dump(n) for n in ast.parse(old_text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
new_defs = {n.name: ast.dump(n) for n in ast.parse(new_text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
assert set(old_defs) == set(new_defs)
changed = sorted(key for key in old_defs if old_defs[key] != new_defs[key])
assert changed == ["case_figures"]
assert digest(ROOT / "task1/scripts/build_goal2_figures.py") == digest(HERE / "generator_after.py")
for name in ("CASE_SELECTION.json", "figure_data.json"):
    assert (HERE / "before" / name).read_bytes() == (HERE / "after" / name).read_bytes()
selection = read(HERE / "after/CASE_SELECTION.json")
run = ROOT / "task1/evidence/goal2/runs" / selection["source_run"]
manifest = read(run / "manifest.json")
assert manifest["partition"] == "G2_EVAL"
reference = read(ROOT / "task1/config/goal2/contract.json")["reference_parameters"]
units = {"dt": ("dt", "s"), "distance": ("distance", "working m"),
         "min_points": ("min points", ""), "min_length": ("min length", "working m"),
         "direction": ("direction", "deg"), "dp": ("DP", "working m")}
labels, cache, bound_cases = [], {}, []
for case in selection["cases"]:
    entry = next(e for e in manifest["artifacts"].values() if e["config_id"] == case["config_id"])
    assert digest(run / entry["file"]) == entry["sha256"]
    if entry["file"] not in cache:
        with gzip.open(run / entry["file"], "rt") as stream:
            cache[entry["file"]] = {r["record_id"]: r for r in json.load(stream)["records"]}
    row = cache[entry["file"]][case["record_id"]]
    assert row["parameters"] == entry["parameters"]
    changed_parameters = {key: row["parameters"][key] for key in reference if row["parameters"][key] != reference[key]}
    pieces = []
    for key, value in changed_parameters.items():
        name, unit = units[key]
        pieces.append(f"{name} = {value:g}" + (" " + unit if unit else ""))
    label = "; ".join(pieces) if pieces else "Reference"
    labels.append(label)
    bound_cases.append({"record_id": row["record_id"], "configuration_label": label,
                        "actual_parameters": row["parameters"], "config_id": case["config_id"],
                        "source_trace_sha256": entry["sha256"]})
text = " ".join(subprocess.check_output(["pdftotext", str(HERE / "after/real_trajectory_cases.pdf"), "-"], text=True).split())
assert "G2_EVAL" in text and "Common reference: S-D-P" in text
for label, count in Counter(labels).items():
    assert text.count(label) == count, (label, count)
for key, value in reference.items():
    name, unit = units[key]
    expected = f"{name} = {value:g}" + (" " + unit if unit else "")
    assert expected in text
assert "other parameters use the reference" in text
freeze = read(ROOT / "task1/evidence/goal2/evaluation_freeze.json")
assert all(digest(ROOT / path) == sha for path, sha in freeze["processing_source_hashes"].items())
figure_manifest = read(HERE / "after/figure_manifest.json")
figure = next(row for row in figure_manifest["figures"] if row["name"] == "real_trajectory_cases")
for output in [*figure["formats"].values(), figure["pdf_render"]]:
    assert digest(HERE / "after" / output["file"]) == output["sha256"]
print(json.dumps({"status": "PASSED", "changed_functions": changed,
                  "case_selection_bytes_unchanged": True, "figure_data_bytes_unchanged": True,
                  "processing_source_epoch_unchanged": True, "dynamic_labels_bound_to_actual_trace": bound_cases,
                  "partition_caption_checked": True, "reference_parameters_and_units_checked": True,
                  "all_relevant_export_hashes_checked": True,
                  "generator_sha256": digest(HERE / "generator_after.py")}, indent=2))
