"""Read-only factual cross-check of the captured handoff documents.

This is an A presentation check, not C's independent numerical acceptance.
It writes only its own receipt and two already-executed proposal witnesses.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import json
import re
import subprocess


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "task1/evidence/goal2"
OUT = Path(__file__).resolve().parent
INPUTS = {}
CHECKS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    rel = path.relative_to(ROOT).as_posix()
    INPUTS[rel] = sha(path)
    return path


def read_json(path):
    return json.loads(bind(path).read_text())


def rows(name):
    return list(csv.DictReader(bind(BASE / "tables" / name).open()))


def check(label, actual, expected):
    CHECKS.append({"label": label, "actual": actual, "expected": expected,
                   "passed": actual == expected})


cutoff = read_json(OUT / "read_cutoff.json")
for doc in cutoff["documents"]:
    check(doc["path"] + " captured bytes", sha(bind(doc["snapshot_path"])), doc["sha256"])

summary = read_json(BASE / "result_summary.json")
current = read_json(BASE / "current_runs.json")
check("raw records and points", [summary["data"]["raw_records"], summary["data"]["raw_points"]], [11386, 1173410])
check("partition counts", summary["data"]["partition_records"],
      {"PILOT_REGRESSION": 7, "DEMO_MEMORY": 60, "DEVELOPMENT": 120, "G2_EVAL": 120, "G3_RESERVED": 11079})
check("fixed mode subsets", summary["data"]["llm_subset_records"], {"DEVELOPMENT": 24, "G2_EVAL": 24})
counts = {}
for role, run_id in current.items():
    if role == "counterexamples":
        continue
    manifest = read_json(BASE / "runs" / run_id / "manifest.json")
    counts[role] = manifest["candidate_evaluations"]
check("registered record-candidate evaluations", counts,
      {"parameter_development": 7080, "order_development": 720, "memory": 1200,
       "mode_development": 1218, "evaluation_parameters": 1680,
       "evaluation_orders": 240, "mode_evaluation": 3583})
check("total registered evaluations", sum(counts.values()), 15721)
table_rows = 0
for name, meta in summary["tables"].items():
    path = bind(meta["path"])
    check("table hash " + name, sha(path), meta["sha256"])
    n = sum(1 for _ in csv.DictReader(path.open()))
    check("table rows " + name, n, meta["rows"])
    table_rows += n
check("table count and rows", [len(summary["tables"]), table_rows], [39, 111053])

cs, cd, cp = summary["single_candidates"]
check("single candidate order", [x["candidate"] for x in (cs, cd, cp)], ["C-S", "C-D", "C-P"])
check("C-S registered counts", [cs[k] for k in ["n_records", "n_input", "feasible_records", "strict_gain_records", "common_covered_points", "n_no_output_records", "n_final"]],
      [120, 12173, 120, 53, 12162, 0, 2939])
check("C-D/C-P reference and negative conclusion",
      [[x["reference_retained"], x["evaluation_status"], x["strict_gain_records"]] for x in (cd, cp)],
      [[True, "NO_DEMONSTRATED_GAIN", 0], [True, "NO_DEMONSTRATED_GAIN", 0]])
param = rows("parameter_configurations.csv")
ref = next(x for x in param if x["partition"] == "G2_EVAL" and x["config_id"] == cd["config_id"])
check("C-S common baseline counts", [int(ref[k]) for k in ["common_covered_points", "n_no_output_records", "n_final"]], [8805, 32, 2748])
check("unsafe order record counts", {x["order"]: x["safety_failure_records"] for x in summary["orders"] if x["partition"] == "DEVELOPMENT"},
      {"S-D-P": 0, "S-P-D": 0, "D-S-P": 46, "D-P-S": 87, "P-S-D": 87, "P-D-S": 87})

mode = [x for x in rows("mode_summary.csv") if x["partition"] == "G2_EVAL"]
mode_readings = {x["mode"]: [int(x[k]) for k in ["record_episode_observations", "experiment_model_dispatches", "candidate_evaluations", "protected_gain_records_episodes"]] for x in mode}
check("formal mode table", mode_readings,
      {"llm-only": [72, 9, 109, 15], "search-only": [72, 0, 1440, 27],
       "llm+search": [72, 27, 1080, 47], "llm+memory+search": [72, 27, 954, 47]})
proposals = [x for x in rows("mode_proposals.csv") if x["partition"] == "G2_EVAL"]
check("formal proposals/legal/executed/evaluable/matching/fallback",
      [len(proposals), sum(x["legal"] == "True" for x in proposals), sum(x["executed"] == "True" for x in proposals),
       sum(x["prediction_evaluable"] == "True" for x in proposals),
       sum(x["prediction_evaluable"] == "True" and x["prediction_matches"] == "True" for x in proposals),
       sum(int(x["fallback_records_episodes"]) for x in mode)], [467, 467, 467, 185, 185, 0])
retrieval = [x for x in rows("memory_retrieval.csv") if x["partition"] == "G2_EVAL"]
consumption = [x for x in rows("memory_consumption.csv") if x["partition"] == "G2_EVAL"]
check("formal memory delivery and use denominators",
      [len(retrieval), sum(int(x["delivered_count"]) > 0 for x in retrieval), len(consumption),
       sum(int(x["valid_citation_count"]) > 0 for x in consumption), sum(int(x["action_consistent_count"]) > 0 for x in consumption)],
      [72, 72, 181, 43, 36])
check("memory no causal assertion", all(x["causal_benefit_proven"] == "False" for x in consumption), True)
check("counterexample counts", [summary["counterexamples"][k] for k in ["synthetic_cases", "synthetic_pipeline_executions", "known_answer_checks", "exposed_pilot_pipeline_executions"]], [6, 19, 25, 10])

coordinate = read_json(BASE / "coordinate_sensitivity/raw_preflight/coordinate_checks.json")
check("coordinate scope", [coordinate[k] for k in ["records_checked", "points_checked", "within_record_pairs_checked"]], [307, 30992, 1594527])
coordinate_readings = {k: coordinate[k]["max"] for k in ["coordinate_error_m", "pair_absolute_difference_m"]}
check("reported rounded coordinate maxima", [float(f"{coordinate_readings['coordinate_error_m']:.4g}"), round(coordinate_readings["pair_absolute_difference_m"], 3)], [4.823e-10, 3.504])
sensitivities = [read_json(BASE / "coordinate_sensitivity" / epoch / "summary.json") for epoch in ["development-02", "evaluation-01"]]
check("registered sensitivity trace counts", [sum(x["actual_traces_checked"] for x in d["runs"]) for d in sensitivities], [10218, 5503])
check("observed alternate threshold differences", sum(sum(r["sensitivity_difference_counts"].values()) for d in sensitivities for r in d["runs"]), 0)
ledger = read_json(BASE / "resource_ledger.json")
check("visible CLI scope counts", {x["scope"]: x["visible_dispatches"] for x in ledger["provider_scope_summaries"]},
      {"CURRENT_VALID_EXPERIMENT": 84, "ENGINEERING_PROVIDER_QUALIFICATION": 1, "HISTORICAL_SUPERSEDED_OR_INTERRUPTED_EXPERIMENT": 15})
check("visible CLI total", ledger["visible_cli_provider_attempts_all_scopes"], 100)
check("named processing/verifier count", summary["resource_accounting"]["registered_current_processing_verifier_calls"], 10249)
nb = read_json(BASE / "notebook_runs/fresh-01/b_self_check.json")
check("Notebook cells/recomputations/new calls", [nb[k] for k in ["total_code_cells", "total_candidate_record_recomputations", "new_model_calls"]], [21, 17401, 0])
execution = read_json(BASE / "notebook_execution.json")
check("Notebook memory stable", execution["memory_before_sha256"], execution["memory_after_sha256"])
log = bind(BASE / "logs/tests_final_sources.log").read_text()
check("actual pytest count and internal duration", "316 passed in 5.85s" in log, True)
figures = read_json(ROOT / "task1/figures/goal2/figure_manifest.json")
check("figure and export counts", [len(figures["figures"]), sum(len(x["formats"]) + int("pdf_render" in x) for x in figures["figures"])], [11, 44])

# This derives witnesses from stored traces, without invoking any processing or model.
tradeoffs = [x for x in rows("ai_legal_proposal_tradeoffs.csv") if x["partition"] == "G2_EVAL"]
check("formal legal proposal tradeoff count", len(tradeoffs), 2)
witnesses = []
for row in tradeoffs:
    folder = BASE / "runs" / row["run_id"] / "modes" / row["episode_id"]
    episode = read_json(folder / "episode.json")
    record = next(x for x in episode["records"] if x["record_id"] == row["record_id"])
    lock_path = bind(folder / (row["record_id"] + "_lock.json"))
    lock = read_json(lock_path)
    trace_path = bind(folder / (row["record_id"] + "_candidate_traces.json.gz"))
    bundle = json.loads(gzip.decompress(trace_path.read_bytes()))
    reference = bundle["results"][record["reference_config_id"]]
    candidate = bundle["results"][row["executed_config_id"]]
    before = {x["index"] for x in reference["metrics"]["common_point_errors"] if x["error"] is not None}
    after = {x["index"] for x in candidate["metrics"]["common_point_errors"] if x["error"] is not None}
    original = json.loads(row["original_proposal"])
    sources = json.loads(row["raw_response_sources"])
    found_original = False
    for source in sources:
        response_path = bind(source["path"])
        check(row["candidate_id"] + " response hash", sha(response_path), source["sha256"])
        response = read_json(response_path)
        found_original |= any(original in x["proposals"] for x in response["records"] if x["record_id"] == row["record_id"])
    check(row["candidate_id"] + " raw exact proposal", found_original, True)
    for p in [trace_path, lock_path]:
        check(row["candidate_id"] + " episode artifact binding " + p.name, sha(p), episode["artifact_hashes"][p.name])
    assessment = record["selection"]["assessments"][row["executed_config_id"]]
    check(row["candidate_id"] + " lost identity count", len(before - after), {"3420": 16, "955": 1}[row["record_id"]])
    check(row["candidate_id"] + " null on full baseline", assessment["candidate_max_on_baseline_covered"], None)
    check(row["candidate_id"] + " not locked", lock["selected_config_id"] != row["executed_config_id"], True)
    check(row["candidate_id"] + " reference retained without fallback", [lock["selected_config_id"], lock["fallback"]], [record["reference_config_id"], False])
    witnesses.append({
        "partition": row["partition"], "mode": row["mode"], "episode": int(row["episode"]),
        "episode_id": row["episode_id"], "record_id": row["record_id"], "round": int(row["round"]),
        "candidate_id": row["candidate_id"], "config_id": row["executed_config_id"],
        "raw_proposal": original, "raw_response_sources": sources,
        "episode_path": (folder / "episode.json").relative_to(ROOT).as_posix(),
        "episode_sha256": sha(folder / "episode.json"),
        "trace_path": trace_path.relative_to(ROOT).as_posix(), "trace_sha256": sha(trace_path),
        "lock_path": lock_path.relative_to(ROOT).as_posix(), "lock_sha256": sha(lock_path),
        "baseline_covered_count": len(before), "candidate_covered_count": len(after),
        "lost_baseline_covered_indices": sorted(before - after),
        "candidate_max_on_baseline_covered": None, "unavailable_reason": "BASELINE_COVERED_IDENTITIES_LOST",
        "own_coverage_error_values_are_comparable": False,
        "selected_config_id": lock["selected_config_id"], "fallback": lock["fallback"],
        "selection_reason": record["selection"]["reason"], "research_status": assessment["status"],
        "protection_failures": assessment["protection_failures"],
        "interpretation": "Legal executed exploration with a measured coverage tradeoff, excluded by frozen protection. Not illegal, hallucinated or a ground-truth quality error."
    })
(OUT / "formal_eval_tradeoff_witnesses.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2) + "\n")

# Markdown snapshots retain original bytes as .source.txt. Resolve links at their canonical source.
link_checks = []
receipt_hash_checks = []
for doc in cutoff["documents"]:
    content = (ROOT / doc["snapshot_path"]).read_text()
    parent = (ROOT / doc["path"]).parent
    for target in re.findall(r"\]\(([^)]+)\)", content):
        if target.startswith(("http:", "https:", "#")):
            continue
        path = (parent / target.split("#", 1)[0]).resolve()
        link_checks.append({"document": doc["path"], "target": target, "exists": path.exists()})
    for target, expected in re.findall(r"\]\(([^)]+\.json)\)，SHA256 `([0-9a-f]{64})`", content):
        path = bind(parent / target)
        receipt_hash_checks.append({"path": path.relative_to(ROOT).as_posix(), "passed": sha(path) == expected})
check("all captured relative link targets exist", all(x["exists"] for x in link_checks), True)
check("explicit process receipt hashes match", all(x["passed"] for x in receipt_hash_checks), True)
startup = read_json(BASE / "startup.json")
zip_states = []
for name, expected in startup["user_untracked"].items():
    path = bind(ROOT / name)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", name], cwd=ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    check("preserved ZIP " + name, sha(path), expected)
    zip_states.append({"path": name, "sha256": sha(path), "currently_tracked": tracked})
check("actual untracked handoff ZIP count", sum(not x["currently_tracked"] for x in zip_states), 2)
live_at_end = [{"path": d["path"], "cutoff_sha256": d["sha256"],
                "current_sha256": sha(ROOT / d["path"]),
                "changed_since_cutoff": sha(ROOT / d["path"]) != d["sha256"]} for d in cutoff["documents"]]
receipt = {
    "goal_id": "SC-LAB1-G2-EXPERIMENTS-001", "reviewer": "A /root/a_contract",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "status": "FACTUAL_CHECK_PASSED_WITH_NONBLOCKING_COMPLETENESS_NOTE" if all(x["passed"] for x in CHECKS) else "FACTUAL_CHECK_FAILED",
    "classification": "READ_ONLY_HANDOFF_FACT_CHECK_NOT_INDEPENDENT_C_ACCEPTANCE",
    "source_sha256": sha(Path(__file__)), "read_cutoff": cutoff,
    "checks": CHECKS, "check_count": len(CHECKS), "failures": [x for x in CHECKS if not x["passed"]],
    "input_hashes": INPUTS, "canonical_relative_link_checks": link_checks,
    "process_explicit_hash_checks": receipt_hash_checks, "user_zip_states": zip_states,
    "findings": [{"finding_id": "A-HANDOFF-COMPLETENESS-001", "severity": "NONBLOCKING_PRESENTATION_COMPLETENESS",
                  "target": "task1/evidence/goal2/FINAL_RESPONSE.md:51", "cutoff_sha256": cutoff["documents"][0]["sha256"],
                  "fact": "2 of 467 formal raw legal proposals have actual coverage tradeoffs (3420 lost16, 955 lost1); neither was selected. The captured summary illustrates this risk using DEVELOPMENT proposals but does not explicitly mention the two formal cases.",
                  "recommended_action": "Optionally add the formal 2/467 count and link to the bound witness/table. Do not call the suggestions illegal or compare geometric maxima across different coverage masks.",
                  "experiment_defect": False}],
    "narrative_review": {
        "numerical_or_denominator_error_found": False, "null_as_zero_or_numeric_comparison_found": False,
        "causal_memory_gain_overclaim_found": False, "true_quality_or_optimality_overclaim_found": False,
        "negative_results": "C-D/C-P no gain, unsafe orders, S-P-D tradeoff, actual DEV model tradeoff and unknown datum are explicit. Formal two-proposal tradeoff detail is the nonblocking completeness note.",
        "pending_statuses": "Captured docs explicitly remain prepublication/in-progress; later status updates require their own current evidence."
    },
    "checked_components": ["All three captured documents read in full", "Main frozen counts and table hash/row integrity", "Model and memory denominators", "Resource scope separation and unknown costs", "C-S heldout counts and no-gain C-D/C-P", "Coordinate and Notebook/test/figure numerical claims", "Process explicit receipt hashes", "Actual two formal proposal/trace/lock witnesses", "Conditional language and current handoff scope"],
    "unchecked_components": ["No independent raw-to-output numerical rerun", "No fresh visual inspection", "No full A01-A17 acceptance", "No remote publication verification", "No evaluation of later document edits", "No provider-hidden request count or true-label quality"],
    "new_model_calls": 0, "new_candidate_evaluations": 0, "new_memory_writes": 0,
    "bound_artifacts_or_source_modified": False, "live_documents_at_end": live_at_end,
}
(OUT / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": receipt["status"], "checks": len(CHECKS), "failures": receipt["failures"],
                  "receipt_sha256": sha(OUT / "receipt.json"), "witnesses_sha256": sha(OUT / "formal_eval_tradeoff_witnesses.json")}, ensure_ascii=False))
