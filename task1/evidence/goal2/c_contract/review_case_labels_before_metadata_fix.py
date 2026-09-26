"""C's independent label/geometry-provenance review; no production changes."""
import ast
from collections import Counter
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from review_development_runs import Audit, read_compressed
from task1.workflow.io import read_json, write_json, digest, now

OUT = Path(__file__).parent
EV = ROOT / "task1/evidence/goal2"
PREVIEW = EV / "presentation_checks/case_configuration_labels"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def main():
    audit = Audit()
    issue = read_json(EV / "goal_state.json")["issues"]["G2-B-CASE-CONFIG-001"]
    audit.check("registered_repair", issue["status"] == "REGRESSION_PENDING")
    for target in issue["repair_evidence"]:
        audit.check("exact_repair_target", digest(ROOT / target["path"]) == target["sha256"])
    before, after = PREVIEW / "before", PREVIEW / "after"
    old_defs, new_defs = [{n.name: ast.dump(n) for n in ast.parse((PREVIEW / name).read_text()).body
                           if isinstance(n, (ast.FunctionDef, ast.ClassDef))} for name in ("generator_before.py", "generator_after.py")]
    audit.check("same_definitions", set(old_defs) == set(new_defs))
    audit.same("only_case_labels_changed", sorted(k for k in old_defs if old_defs[k] != new_defs[k]), ["case_figures"])
    audit.check("active_generator_binding", digest(ROOT / "task1/scripts/build_goal2_figures.py") == digest(PREVIEW / "generator_after.py"))
    prior = read_json(OUT / "candidate_figure_closure_receipt_v2.json")
    prior_target = next(t for t in prior["targets"] if t["path"] == "task1/scripts/build_goal2_figures.py")
    audit.check("previous_closed_source_archived", digest(PREVIEW / "generator_before.py") == prior_target["sha256"])
    for name in ("CASE_SELECTION.json", "figure_data.json"):
        audit.check("unchanged_" + name, (before / name).read_bytes() == (after / name).read_bytes())
    for name in ("synthetic_metric_counterexamples.png", "goal2_actual_architecture.png"):
        audit.check("unaffected_image_bytes", (before / name).read_bytes() == (after / name).read_bytes())
    selection = read_json(after / "CASE_SELECTION.json")
    directory = EV / "runs" / selection["source_run"]
    manifest = read_json(directory / "manifest.json")
    reference = read_json(ROOT / "task1/config/goal2/contract.json")["reference_parameters"]
    units = {"dt": ("dt", "s"), "distance": ("distance", "working m"), "min_points": ("min points", ""),
             "min_length": ("min length", "working m"), "direction": ("direction", "deg"), "dp": ("DP", "working m")}
    def parameter_label(key, value):
        label, unit = units[key]
        return f"{label} = {value:g}" + (" " + unit if unit else "")
    labels, checked_cases = [], []
    for case in selection["cases"]:
        entry = next(e for e in manifest["artifacts"].values() if e["config_id"] == case["config_id"])
        audit.check("actual_trace_hash", digest(directory / entry["file"]) == entry["sha256"])
        row = next(r for r in read_compressed(directory / entry["file"])["records"] if r["record_id"] == case["record_id"])
        audit.same("actual_record_parameters", row["parameters"], entry["parameters"])
        changed = [parameter_label(k, value) for k, value in row["parameters"].items() if value != reference[k]]
        label = "; ".join(changed) if changed else "Reference"
        labels.append(label)
        checked_cases.append({"record_id": row["record_id"], "config_id": entry["config_id"], "parameters": row["parameters"], "expected_label": label})
    def pdf_text(path):
        return " ".join(subprocess.check_output(["pdftotext", str(path), "-"], text=True).split())
    old_text, text = [pdf_text(p / "real_trajectory_cases.pdf") for p in (before, after)]
    required = [manifest["partition"], "Common reference: S-D-P", "other parameters use the reference", "conditional working plane"] + [parameter_label(k, v) for k, v in reference.items()]
    def labels_complete(value):
        return all(value.count(label) == count for label, count in Counter(labels).items()) and all(label in value for label in required)
    audit.check("fault_rejected_original_unlabelled_PDF", not labels_complete(old_text))
    audit.check("valid_receipt_accepted_actual_labelled_PDF", labels_complete(text))
    audit.check("fault_rejected_changed_parameter_label", not labels_complete(text.replace("distance = 95 working m", "distance = 400 working m")))
    audit.check("partition_G2_EVAL", manifest["partition"] == "G2_EVAL")
    audit.check("residual_and_no_output_preserved", "P residual = 4.999598 working m" in text and text.count("No final output") == 2)
    figure_manifest = read_json(after / "figure_manifest.json")
    audit.check("generator_epoch", figure_manifest["generator_sha256"] == digest(PREVIEW / "generator_after.py"))
    audit.check("data_binding", figure_manifest["figure_data_sha256"] == digest(after / "figure_data.json"))
    for figure in figure_manifest["figures"]:
        for export in [*figure["formats"].values(), figure["pdf_render"]]:
            audit.check("all_export_hashes", digest(after / export["file"]) == export["sha256"])
    destination = OUT / "case_label_pdf_render_200dpi"
    subprocess.run(["pdftoppm", "-r", "200", "-singlefile", "-png", str(after / "real_trajectory_cases.pdf"), str(destination)], check=True, capture_output=True)
    rendered = destination.with_suffix(".png")
    audit.check("independent_PDF_render", digest(rendered) == digest(after / "pdf-render-200dpi/real_trajectory_cases.png"))
    for path, sha in read_json(EV / "evaluation_freeze.json")["processing_source_hashes"].items():
        audit.check("frozen_processing_unchanged", digest(ROOT / path) == sha)
    # The B validator was read above and is additionally executed, without writes.
    validation = subprocess.run([str(ROOT / ".venv/bin/python"), str(PREVIEW / "validate_labels.py")], cwd=ROOT, text=True, capture_output=True)
    audit.check("B_metadata_reproducible", validation.returncode == 0)
    if validation.returncode == 0:
        import json
        audit.same("B_metadata_actual_checks", json.loads(validation.stdout), read_json(PREVIEW / "deterministic_validation.json"))
    receipt = {"issue_id": "G2-B-CASE-CONFIG-001", "parent_task": "figures", "status": "VERIFIED" if not audit.errors else "REJECTED",
               "role_context": "/root/c_contract", "at": now(), "targets": deepcopy(issue["repair_evidence"]), "source_hashes": deepcopy(issue["repair_source_hashes"]),
               "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch", "six_actual_trace_labels", "reference_partition_work_units", "actual_PNG_and_PDF_view", "previous_source_preserved", "unchanged_case_data"],
               "unchecked_components": ["full_11_figure_final_set", "full_Goal2_acceptance"], "check_count": audit.check_count, "errors": audit.errors,
               "checked_case_labels": checked_cases, "audit_program": bound(Path(__file__)), "independent_render": bound(rendered),
               "actual_viewed_images": [bound(after / "real_trajectory_cases.png"), bound(after / "pdf-render-200dpi/real_trajectory_cases.png")],
               "visual_observations": "C actually viewed both new native PNG and 200dpi PDF raster: top three panels explicitly Reference; lower row shows distance95 and direction15 twice, matching trace parameters. G2_EVAL and six reference parameter/unit caption legible. Existing axis, legend, no-output and residual4.999598 annotation remain clear without overlap or clipping.",
               "scope_limit": "Presentation labels only; preceding preview source/figures remain archived. Final complete figure task pending.", "new_model_calls": 0}
    write_json(OUT / "case_config_closure_receipt.json", receipt, exclusive=True)
    print({key: receipt[key] for key in ("status", "check_count", "errors")})


if __name__ == "__main__":
    main()
