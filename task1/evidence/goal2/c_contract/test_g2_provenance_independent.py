"""C-owned ephemeral provenance fault injections; synthetic data, no LLM.

The actual ExperimentRun/controller code executes against a temporary C-owned
registry. This never changes production splits, runs, contract or source files.
"""
from copy import deepcopy
from pathlib import Path
import tempfile

import pytest

from task1.workflow import g2_experiments as experiments
from task1.workflow.g2_selection import REFERENCE
from task1.workflow.io import ROOT, read_json, write_json, digest, object_hash


OUT = ROOT / "task1/evidence/goal2/c_contract"


@pytest.fixture
def isolated(monkeypatch):
    with tempfile.TemporaryDirectory(prefix="provenance-fixture-", dir=OUT) as folder:
        directory = Path(folder)
        ev = directory / "evidence"
        cfg = directory / "config"
        write_json(cfg / "contract.json", read_json(ROOT / "task1/config/goal2/contract.json"))
        write_json(cfg / "experiment_matrix.json", read_json(ROOT / "task1/config/goal2/experiment_matrix.json"))
        split = {"raw_sha256": object_hash({"purpose": "ENGINEERING_TEST"}),
                 "splits": {"DEVELOPMENT": ["DEV"], "DEMO_MEMORY": ["DEMO"], "G3_RESERVED": ["G3"]},
                 "llm_subsets": {"DEVELOPMENT": ["DEV"]}}
        write_json(ev / "data/split_manifest.json", split)
        source = directory / "controlled_source.py"
        source.write_text("fixture = 1\n")
        source_paths = [source]
        raw = {rid: {"record_id": rid, "indices": list(range(12)), "timestamps": list(range(12)),
                     "xy": [[i * 10, (i % 3) * 0.5] for i in range(12)]}
               for rid in ("DEV", "DEMO", "G3")}
        monkeypatch.setattr(experiments, "EV", ev)
        monkeypatch.setattr(experiments, "CFG", cfg)
        monkeypatch.setattr(experiments, "raw_data", lambda: deepcopy(raw))
        monkeypatch.setattr(experiments, "adapt", lambda rid, value: deepcopy(value))
        monkeypatch.setattr(experiments, "source_snapshot", lambda: {str(p.relative_to(ROOT)): digest(p) for p in source_paths})
        real_provenance = experiments.ExperimentRun.provenance
        monkeypatch.setattr(experiments.ExperimentRun, "provenance", lambda self, ids:
                            {**real_provenance(self, ids), "source_kind": "ENGINEERING_TEST"})
        yield directory, ev, cfg, source_paths


def new_run(run_id="engineer-parameters"):
    return experiments.ExperimentRun(run_id, "DEVELOPMENT", classification="ENGINEERING_TEST")


def complete_inputs():
    parameter = new_run()
    experiments.parameter_development(parameter)
    order = new_run("engineer-orders")
    experiments.order_development(order)
    return parameter, order


def test_resume_rejects_changed_partition(isolated):
    run = new_run()
    with pytest.raises(ValueError, match="SCOPE_OR_PARTITION"):
        experiments.ExperimentRun(run.run_id, "DEMO_MEMORY", resume=True)


@pytest.mark.parametrize("field,value", [("input_ids", []), ("raw_sha256", "wrong"), ("source_tree_sha256", "wrong")])
def test_resume_rejects_forged_manifest_bindings(isolated, field, value):
    run = new_run()
    run.manifest[field] = value
    run.save()
    with pytest.raises(ValueError):
        experiments.ExperimentRun(run.run_id, "DEVELOPMENT", resume=True)


def test_new_dependency_requires_new_run(isolated):
    directory, _, _, sources = isolated
    run = new_run()
    extra = directory / "new_dependency.py"
    extra.write_text("fixture = 2\n")
    sources.append(extra)
    with pytest.raises(ValueError, match="DEPENDENCY_SET_CHANGED"):
        run.assert_epoch()


def test_g3_reserved_is_not_executable(isolated):
    with pytest.raises(ValueError, match="G3_NOT_AUTHORIZED"):
        experiments.ExperimentRun("forbidden", "G3_RESERVED")


def test_valid_complete_synthetic_candidates_and_orders_can_lock(isolated):
    parameter, order = complete_inputs()
    result = experiments.candidate_lock(parameter.run_id, order.run_id)
    assert set(result["selected_single_candidates"]) == {"C-S", "C-D", "C-P"}
    assert len(result["all_config_assessments"]) == 59
    assert result["source_partition"] == "DEVELOPMENT" and not result["g2_eval_observed_for_selection"]


@pytest.mark.parametrize("change", ["artifact_bytes", "review_bytes", "review_target", "manifest_summary", "manifest_engineering_status", "missing_grid", "wrong_scope"])
def test_candidate_lock_rejects_single_corruption(isolated, change):
    parameter, order = complete_inputs()
    entry = next(iter(parameter.manifest["artifacts"].values()))
    if change == "artifact_bytes":
        with (parameter.directory / entry["file"]).open("ab") as stream:
            stream.write(b"tamper")
    elif change == "review_bytes":
        (parameter.directory / entry["review_file"]).write_text("{}")
    elif change == "review_target":
        receipt_path = parameter.directory / entry["review_file"]
        receipt = read_json(receipt_path)
        receipt["target_hash"] = "wrong"
        write_json(receipt_path, receipt)
        entry["review_sha256"] = digest(receipt_path)
        parameter.save()
    elif change == "manifest_summary":
        entry["summary"]["n_dp_output"] = -999
        parameter.save()
    elif change == "manifest_engineering_status":
        entry["engineering_status"] = "REJECTED"
        parameter.save()
    elif change == "missing_grid":
        parameter.manifest["artifacts"].pop(next(iter(parameter.manifest["artifacts"])))
        parameter.save()
    elif change == "wrong_scope":
        entry["input_ids"] = []
        parameter.save()
    with pytest.raises(ValueError):
        experiments.candidate_lock(parameter.run_id, order.run_id)


@pytest.mark.parametrize("change", ["review_bytes", "review_status", "review_target"])
def test_cache_reuse_requires_current_bound_review(isolated, change):
    run = new_run()
    _, entry = run.evaluate_batch(REFERENCE)
    path = run.directory / entry["review_file"]
    if change == "review_bytes":
        path.write_text("{}")
    else:
        receipt = read_json(path)
        receipt["status" if change == "review_status" else "target_hash"] = "wrong"
        write_json(path, receipt)
        entry["review_sha256"] = digest(path)
    with pytest.raises(ValueError):
        run.evaluate_batch(REFERENCE)


def test_order_table_alone_cannot_override_actual_safety(isolated):
    parameter, order = complete_inputs()
    path = order.directory / "order_table.json"
    table = read_json(path)
    table[0]["research_status"] = "REJECTED_BY_CONSTRAINT" if table[0]["research_status"] == "FEASIBLE_FOR_STAGE_EVALUATION" else "FEASIBLE_FOR_STAGE_EVALUATION"
    write_json(path, table)
    order.manifest["tables"]["order_table.json"] = digest(path)
    order.save()
    with pytest.raises(ValueError, match="FEASIBILITY_TABLE_MISMATCH"):
        experiments.candidate_lock(parameter.run_id, order.run_id)


def evaluation_fixture(isolated):
    directory, ev, cfg, _ = isolated
    split = read_json(ev / "data/split_manifest.json")
    split["splits"]["G2_EVAL"] = ["DEV"]
    split["llm_subsets"]["G2_EVAL"] = ["DEV"]
    write_json(ev / "data/split_manifest.json", split)
    write_json(ev / "candidate_lock.json", {"purpose": "ENGINEERING_TEST_BINDINGS_ONLY"})
    memory = directory / "memory.json"
    memory.write_text('{"purpose":"ENGINEERING_TEST_BINDINGS_ONLY"}')
    freeze = {"status": "LOCKED_BEFORE_G2_EVAL", "contract_sha256": digest(cfg / "contract.json"),
              "split_sha256": digest(ev / "data/split_manifest.json"),
              "candidate_lock_sha256": digest(ev / "candidate_lock.json"), "eval_ids": ["DEV"], "eval_llm_ids": ["DEV"],
              "mode_implementation_sha256": digest(ROOT / "task1/workflow/g2_modes.py"),
              "provider_implementation_sha256": digest(ROOT / "task1/workflow/g2_provider.py"),
              "memory_path": str(memory.relative_to(ROOT)), "memory_sha256": digest(memory),
              "processing_source_hashes": experiments.source_snapshot()}
    return freeze


def test_eval_cannot_open_without_frozen_protocol(isolated):
    evaluation_fixture(isolated)
    with pytest.raises(ValueError, match="EVALUATION_NOT_FROZEN"):
        experiments.ExperimentRun("fixture-eval", "G2_EVAL", classification="ENGINEERING_TEST")


def test_valid_evaluation_version_bindings_open(isolated):
    _, ev, _, _ = isolated
    write_json(ev / "evaluation_freeze.json", evaluation_fixture(isolated))
    run = experiments.ExperimentRun("fixture-eval", "G2_EVAL", classification="ENGINEERING_TEST")
    assert run.ids == ["DEV"] and run.partition == "G2_EVAL"


@pytest.mark.parametrize("field", ["contract_sha256", "split_sha256", "candidate_lock_sha256", "eval_ids", "eval_llm_ids",
                                   "memory_sha256", "mode_implementation_sha256", "provider_implementation_sha256", "processing_source_hashes"])
def test_eval_rejects_each_frozen_binding_mismatch(isolated, field):
    _, ev, _, _ = isolated
    freeze = evaluation_fixture(isolated)
    freeze[field] = [] if field.endswith("ids") else {} if field == "processing_source_hashes" else "wrong"
    write_json(ev / "evaluation_freeze.json", freeze)
    with pytest.raises(ValueError):
        experiments.ExperimentRun("fixture-eval", "G2_EVAL", classification="ENGINEERING_TEST")
