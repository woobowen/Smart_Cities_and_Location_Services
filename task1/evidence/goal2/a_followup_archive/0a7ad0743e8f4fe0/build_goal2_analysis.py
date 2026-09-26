"""Derive Goal 2 tables and stage analysis from hash-bound current runs.

This command performs no candidate selection, processing or model calls. It reads
the already locked candidates and verified traces. Missing required runs produce
INCOMPLETE, while changed evidence is rejected. The output is a stage analysis,
not independent C acceptance, a final research method, or a submission report.

  .venv/bin/python -m task1.scripts.build_goal2_analysis \
      --current-runs task1/evidence/goal2/current_runs.json \
      --output-dir task1/evidence/goal2 \
      --document task1/docs/goal2/STAGE_ANALYSIS.md
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from itertools import combinations
import json
import math
import os
from pathlib import Path
import statistics
import sys

from task1.workflow.io import (DATA, ROOT, bound_path, digest, object_hash,
                               read_json, write_json, now)
from task1.workflow.g2_experiments import read_gzip, compact_metrics
from task1.workflow.g2_metrics import summarize
from task1.workflow.g2_selection import REFERENCE, GRID, compare, config_id


EVIDENCE = ROOT / "task1/evidence/goal2"
CONFIG = ROOT / "task1/config/goal2"
DOCUMENT = ROOT / "task1/docs/goal2/STAGE_ANALYSIS.md"
RUN_PARTITIONS = {
    "parameter_development": "DEVELOPMENT",
    "order_development": "DEVELOPMENT",
    "memory": "DEMO_MEMORY",
    "mode_development": "DEVELOPMENT",
    "evaluation_parameters": "G2_EVAL",
    "evaluation_orders": "G2_EVAL",
    "mode_evaluation": "G2_EVAL",
}
MODES = ("llm-only", "search-only", "llm+search", "llm+memory+search")
PAIR_METRICS = ("n_final", "n_filtered", "n_direction_removed", "n_dp_output",
                "point_retention", "common_covered_points", "common_coverage",
                "raw_break_crossings", "raw_windows_covered", "dp_saving",
                "dp_max_error", "common_max_error")
COUNT_FIELDS = ("n_input", "n_final", "n_filtered", "n_direction_removed", "n_dp_removed",
                "n_dp_input", "n_dp_output", "n_s_segments", "n_filtered_segments",
                "common_covered_points", "common_uncovered_points", "raw_break_crossings")


def relative(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name


def checked(path, expected_hash):
    if not expected_hash or digest(path) != expected_hash:
        raise ValueError("ANALYSIS_INPUT_HASH_MISMATCH:" + relative(path))
    return path


def numeric_summary(values):
    available = [float(value) for value in values if value is not None]
    if any(not math.isfinite(value) for value in available):
        raise ValueError("NONFINITE_ANALYSIS_INPUT")
    return {
        "denominator": len(values), "available": len(available),
        "unavailable": len(values) - len(available),
        "mean": statistics.fmean(available) if available else None,
        "median": statistics.median(available) if available else None,
        "min": min(available) if available else None,
        "max": max(available) if available else None,
        "sample_sd": statistics.stdev(available) if len(available) > 1 else None,
        "reason": None if available else "NO_AVAILABLE_VALUES",
        "sd_reason": None if len(available) > 1 else "FEWER_THAN_TWO_AVAILABLE_VALUES",
    }


def scalar_fields(value):
    return {key: item for key, item in value.items() if not isinstance(item, (dict, list))}


def covered(record):
    return {row["index"] for row in record["metrics"]["common_point_errors"]
            if row["error"] is not None}


def mask_signature(record):
    """Exact stage identity masks and terminal counts, not rounded metric plateaus."""
    return object_hash({
        "record_id": record["record_id"],
        "stage_masks": [{"name": stage["name"],
                         "input": [segment["indices"] for segment in stage["input"]],
                         "output": [segment["indices"] for segment in stage["output"]]}
                        for stage in record["stages"]],
        "common_covered_indices": sorted(covered(record)),
        "counts": {key: record["metrics"][key] for key in COUNT_FIELDS},
    })


def comparison_summary(comparisons):
    return {
        "n_records": len(comparisons),
        "feasible_records": sum(row["feasible"] for row in comparisons),
        "strict_gain_records": sum(row["strict_gain"] for row in comparisons),
        "feasible_all_records": bool(comparisons) and all(row["feasible"] for row in comparisons),
        "strict_gain_any_record": any(row["strict_gain"] for row in comparisons),
        "statuses": dict(Counter(row["status"] for row in comparisons)),
        "protection_failures": dict(Counter(reason for row in comparisons
                                             for reason in row["protection_failures"])),
        "quality_accepted": False,
    }


def research_status(comparisons):
    if not comparisons:
        return "INSUFFICIENT_EVIDENCE"
    if any(row["status"] == "REJECTED_BY_CONSTRAINT" for row in comparisons):
        return "REJECTED_BY_CONSTRAINT"
    if not all(row["feasible"] for row in comparisons):
        return "TRADEOFF"
    return "SUPPORTED_WITHIN_SCOPE" if any(row["strict_gain"] for row in comparisons) else "NO_DEMONSTRATED_GAIN"


def pair_reading(candidate, baseline):
    assessment = compare(candidate, baseline)
    before, after = baseline["metrics"], candidate["metrics"]
    row = {"record_id": candidate["record_id"], **assessment,
           "same_common_covered_mask": covered(candidate) == covered(baseline)}
    p_before = next(stage for stage in baseline["stages"] if stage["name"] == "P")["input"]
    p_after = next(stage for stage in candidate["stages"] if stage["name"] == "P")["input"]
    same_p_input = p_before == p_after
    row["same_dp_input_reference"] = same_p_input
    for metric in PAIR_METRICS:
        a, b = after[metric], before[metric]
        reason = None
        if a is None or b is None:
            reason = "UNAVAILABLE_IN_AT_LEAST_ONE_ARM"
        elif metric in ("dp_saving", "dp_max_error", "n_dp_output") and not same_p_input:
            reason = "DIFFERENT_DP_INPUT_REFERENCE"
        elif metric == "common_max_error" and not row["same_common_covered_mask"]:
            reason = "DIFFERENT_COMMON_COVERED_MASK_USE_BASELINE_MASK_READING"
        row["reference_" + metric] = b
        row["candidate_" + metric] = a
        row["delta_" + metric] = a - b if reason is None else None
        row["delta_" + metric + "_reason"] = reason
    return row


class Inputs:
    """Read current entries only after their complete parent/child binding checks."""

    def __init__(self, current_path):
        self.current_path = Path(current_path).resolve()
        self.evidence = self.current_path.parent
        self.current = read_json(self.current_path) if self.current_path.exists() else {}
        self.contract_path = CONFIG / "contract.json"
        self.contract = read_json(self.contract_path)
        self.contract_hash = digest(self.contract_path)
        self.split_path = self.evidence / "data/split_manifest.json"
        self.split = read_json(self.split_path)
        self.split_hash = digest(self.split_path)
        checked(DATA, self.split["raw_sha256"])
        diagnostics = checked(self.evidence / "data/raw_diagnostics.json", self.split["diagnostics_sha256"])
        self.cards = read_json(diagnostics)
        self.matrix = read_json(CONFIG / "experiment_matrix.json")
        self.lineage = {relative(self.contract_path): self.contract_hash,
                        relative(self.split_path): self.split_hash,
                        relative(diagnostics): digest(diagnostics),
                        relative(CONFIG / "experiment_matrix.json"): digest(CONFIG / "experiment_matrix.json")}
        if self.current_path.exists():
            self.lineage[relative(self.current_path)] = digest(self.current_path)
        self.missing = []
        self.manifests = {}
        for role, partition in RUN_PARTITIONS.items():
            run_id = self.current.get(role)
            if run_id is None:
                self.missing.append(role)
                continue
            if not isinstance(run_id, str) or Path(run_id).name != run_id:
                raise ValueError("CURRENT_RUN_ID_MUST_BE_A_SINGLE_NAME:" + role)
            directory = bound_path(self.evidence / "runs", run_id)
            path = directory / "manifest.json"
            manifest = read_json(path)
            if manifest["status"] not in ("REVIEW_PENDING", "VERIFIED"):
                raise ValueError("CURRENT_RUN_NOT_COMPLETE_OR_VALID:" + role)
            if manifest["run_id"] != run_id or manifest["partition"] != partition:
                raise ValueError("CURRENT_RUN_ID_OR_PARTITION_MISMATCH:" + role)
            if (manifest["contract_sha256"] != self.contract_hash or
                    manifest["split_sha256"] != self.split_hash or
                    manifest["raw_sha256"] != self.split["raw_sha256"] or
                    manifest["input_ids"] != self.split["splits"][partition]):
                raise ValueError("CURRENT_RUN_PARENT_SCOPE_MISMATCH:" + role)
            sources = manifest["source_hashes"]
            if not sources or object_hash(sources) != manifest["source_tree_sha256"]:
                raise ValueError("CURRENT_RUN_SOURCE_TREE_MISMATCH:" + role)
            for source, sha256 in sources.items():
                checked(bound_path(ROOT, source), sha256)
            for filename, sha256 in manifest.get("tables", {}).items():
                checked(bound_path(directory, filename), sha256)
            self.lineage[relative(path)] = digest(path)
            self.manifests[role] = (directory, manifest)
        self.lock = None
        self.freeze = None
        lock_path = self.evidence / "candidate_lock.json"
        freeze_path = self.evidence / "evaluation_freeze.json"
        if lock_path.exists():
            self.lock = read_json(lock_path)
            self.lineage[relative(lock_path)] = digest(lock_path)
            if (self.lock["source_partition"] != "DEVELOPMENT" or
                    self.lock["g2_eval_observed_for_selection"] or
                    self.lock["parameter_run_id"] != self.current.get("parameter_development") or
                    self.lock["order_run_id"] != self.current.get("order_development")):
                raise ValueError("CANDIDATE_LOCK_PARENT_MISMATCH")
        else:
            self.missing.append("candidate_lock")
        if freeze_path.exists():
            self.freeze = read_json(freeze_path)
            self.lineage[relative(freeze_path)] = digest(freeze_path)
            if (self.lock is None or self.freeze["candidate_lock_sha256"] != digest(lock_path) or
                    self.freeze["status"] != "LOCKED_BEFORE_G2_EVAL" or
                    self.freeze["contract_sha256"] != self.contract_hash or
                    self.freeze["split_sha256"] != self.split_hash or
                    self.freeze["selected_single_candidates"] != self.lock["selected_single_candidates"] or
                    self.freeze["eval_ids"] != self.split["splits"]["G2_EVAL"] or
                    self.freeze["eval_llm_ids"] != self.split["llm_subsets"]["G2_EVAL"]):
                raise ValueError("EVALUATION_FREEZE_BINDING_MISMATCH")
            checked(bound_path(ROOT, self.freeze["memory_path"]), self.freeze["memory_sha256"])
            for source, field in (("task1/workflow/g2_modes.py", "mode_implementation_sha256"),
                                  ("task1/workflow/g2_provider.py", "provider_implementation_sha256")):
                checked(bound_path(ROOT, source), self.freeze[field])
        else:
            self.missing.append("evaluation_freeze")
        if any(self.manifests.get(role) for role in ("evaluation_parameters", "evaluation_orders", "mode_evaluation")) and self.freeze is None:
            raise ValueError("EVALUATION_WITHOUT_FROZEN_PLAN")

    def load_batch(self, role, entry):
        directory, manifest = self.manifests[role]
        path = checked(bound_path(directory, entry["file"]), entry["sha256"])
        audit_path = checked(bound_path(directory, entry["review_file"]), entry["review_sha256"])
        result, audit = read_gzip(path), read_json(audit_path)
        ids = [row["record_id"] for row in result["records"]]
        if (ids != entry["input_ids"] or len(ids) != len(set(ids)) or
                not set(ids) <= set(manifest["input_ids"]) or
                result["parameters"] != entry["parameters"] or result["order"] != entry["order"] or
                config_id(result["parameters"]) != entry["config_id"] or
                result["contract_hash"] != self.contract_hash or
                result["summary"] != entry["summary"] or result["summary"] != summarize(result["records"])):
            raise ValueError("ANALYSIS_BATCH_SCOPE_CONFIG_OR_SUMMARY_MISMATCH:" + relative(path))
        if (audit["status"] != "VERIFIED" or entry["engineering_status"] != "VERIFIED" or
                audit["target_hash"] != object_hash(result)):
            raise ValueError("ANALYSIS_BATCH_REVIEW_TARGET_MISMATCH:" + relative(path))
        provenance = result["provenance"]
        expected = {"run_id": manifest["run_id"], "raw_sha256": manifest["raw_sha256"],
                    "partition": manifest["partition"], "scope_sha256": object_hash(ids),
                    "contract_sha256": self.contract_hash, "split_sha256": self.split_hash,
                    "source_tree_sha256": manifest["source_tree_sha256"]}
        if any(provenance.get(key) != value for key, value in expected.items()):
            raise ValueError("ANALYSIS_BATCH_PROVENANCE_MISMATCH")
        if len(audit["record_receipts"]) != len(ids):
            raise ValueError("ANALYSIS_BATCH_REVIEW_SCOPE_MISMATCH")
        for row, receipt in zip(result["records"], audit["record_receipts"]):
            if (receipt["record_id"] != row["record_id"] or receipt["status"] != "VERIFIED" or
                    receipt["target_hash"] != object_hash(row) or row["parameters"] != entry["parameters"] or
                    row["order"] != entry["order"] or row["provenance"] != provenance):
                raise ValueError("ANALYSIS_RECORD_REVIEW_BINDING_MISMATCH")
        self.lineage[relative(path)] = entry["sha256"]
        self.lineage[relative(audit_path)] = entry["review_sha256"]
        return result

    def episodes(self, role):
        directory, manifest = self.manifests[role]
        for entry in manifest.get("mode_episodes", []):
            path = checked(bound_path(directory, entry["path"]), entry["sha256"])
            episode = read_json(path)
            if (episode["mode"] != entry["mode"] or episode["episode"] != entry["episode"] or
                    episode["input_ids"] != entry["input_ids"] or
                    episode["contract_sha256"] != self.contract_hash or
                    episode["source_tree_sha256"] != manifest["source_tree_sha256"] or
                    [row["record_id"] for row in episode["records"]] != episode["input_ids"]):
                raise ValueError("ANALYSIS_EPISODE_SCOPE_OR_PARENT_MISMATCH")
            if not episode.get("artifact_hashes"):
                raise ValueError("ANALYSIS_EPISODE_CHILD_HASHES_REQUIRED")
            for filename, sha256 in episode["artifact_hashes"].items():
                checked(bound_path(path.parent, filename), sha256)
            self.lineage[relative(path)] = entry["sha256"]
            yield path.parent, episode


def batch_context(role, manifest, entry):
    return {"run_role": role, "run_id": manifest["run_id"], "partition": manifest["partition"],
            "experiment_key": entry["experiment_key"], "config_id": entry["config_id"],
            "order": entry["order"], **entry["parameters"], "result_sha256": entry["sha256"],
            "engineering_status": entry["engineering_status"]}


def stage_and_reason_tables(tables, context, record):
    rid = record["record_id"]
    for name, reading in record["metrics"]["stage_readings"].items():
        tables["stage_readings"].append({**context, "record_id": rid, "stage": name, **reading})
    for key in ("filter_reason_segments", "filter_reason_points", "direction_undefined_reasons"):
        for reason, count in record["metrics"][key].items():
            tables["processing_reasons"].append({**context, "record_id": rid,
                                                 "count_kind": key, "reason": reason, "count": count})


def parameter_analysis(inputs, tables, catalogs):
    for role in ("parameter_development", "evaluation_parameters"):
        if role not in inputs.manifests:
            continue
        _, manifest = inputs.manifests[role]
        entries = list(manifest["artifacts"].values())
        expected = ({row["config_id"] for row in inputs.matrix["parameter_configurations"]}
                    if role == "parameter_development" else
                    set(inputs.freeze["representative_config_ids"]) |
                    {row["config_id"] for row in inputs.freeze["selected_single_candidates"].values()})
        if (len(entries) != len(expected) or {entry["config_id"] for entry in entries} != expected or
                any(entry["input_ids"] != manifest["input_ids"] or entry["order"] != "S-D-P" for entry in entries)):
            raise ValueError("ANALYSIS_PARAMETER_MATRIX_INCOMPLETE:" + role)
        reference_entry = next(entry for entry in entries if entry["parameters"] == REFERENCE)
        baseline = {row["record_id"]: row for row in inputs.load_batch(role, reference_entry)["records"]}
        catalog = {}
        for entry in entries:
            result = inputs.load_batch(role, entry)
            context = batch_context(role, manifest, entry)
            pairs = [pair_reading(row, baseline[row["record_id"]]) for row in result["records"]]
            strata = defaultdict(list)
            compact = {}
            for row, pair in zip(result["records"], pairs):
                rid = row["record_id"]
                stratum = inputs.cards[rid]["stratum"]
                strata[stratum].append(row)
                tables["parameter_records"].append({**context, "stratum": stratum, **compact_metrics(row["metrics"])})
                tables["parameter_record_pairs"].append({**context, "stratum": stratum, **pair})
                stage_and_reason_tables(tables, {**context, "stratum": stratum}, row)
                compact[rid] = {"metrics": compact_metrics(row["metrics"]), "comparison": pair,
                                "mask_signature": mask_signature(row), "stratum": stratum}
            tables["parameter_configurations"].append({**context, "memberships": entry["experiment_ids"],
                                                       **result["summary"], **comparison_summary(pairs),
                                                       "research_status": research_status(pairs)})
            for stratum, records in sorted(strata.items()):
                these = [compact[row["record_id"]]["comparison"] for row in records]
                tables["parameter_by_stratum"].append({**context, "stratum": stratum,
                                                        **summarize(records), **comparison_summary(these),
                                                        "research_status": research_status(these)})
            catalog[entry["config_id"]] = {"context": context, "parameters": entry["parameters"],
                                           "records": compact, "summary": result["summary"],
                                           "research_status": research_status(pairs),
                                           "feasible": all(pair["feasible"] for pair in pairs)}
        catalogs[role] = catalog
    dev = catalogs.get("parameter_development", {})
    for parameter, grid in GRID.items():
        groups = []
        for value in grid:
            cid = config_id({**REFERENCE, parameter: value})
            if cid not in dev:
                continue
            signature = object_hash([(rid, item["mask_signature"]) for rid, item in dev[cid]["records"].items()])
            if groups and groups[-1]["signature"] == signature:
                groups[-1]["values"].append(value)
                groups[-1]["config_ids"].append(cid)
            else:
                groups.append({"signature": signature, "values": [value], "config_ids": [cid]})
        for group in groups:
            tables["stable_intervals"].append({"parameter": parameter,
                "observed_min": min(group["values"]), "observed_max": max(group["values"]),
                "registered_grid_values": group["values"], "config_ids": group["config_ids"],
                "identical_stage_masks_and_counts_hash": group["signature"],
                "stable_at_multiple_tested_values": len(group["values"]) > 1,
                "records": len(next(iter(dev.values()))["records"]) if dev else 0,
                "meaning": "Adjacent registered OAT values have identical per-record stage input/output masks, common coverage and terminal counts; untested intermediate values are not certified"})


def pareto_analysis(inputs, tables, catalogs):
    catalog = catalogs.get("parameter_development", {})
    if not catalog:
        return
    families = {"C-S": {"dt", "distance", "min_points", "min_length"},
                "C-D": {"direction"}, "C-P": {"dp"}}
    for family, parameters in families.items():
        domain = {cid: item for cid, item in catalog.items()
                  if all(item["parameters"][key] == REFERENCE[key] for key in REFERENCE if key not in parameters)}
        feasible = {cid: item for cid, item in domain.items() if item["feasible"]}

        def dominates(first, second):
            strict = False
            for rid, left in first["records"].items():
                right = second["records"][rid]
                a, b = left["comparison"], right["comparison"]
                eps = max(a["numerical_allowance"], b["numerical_allowance"])
                if not set(b["candidate_covered_indices"]) <= set(a["candidate_covered_indices"]):
                    return False
                if family == "C-P":
                    an, bn = left["metrics"]["n_dp_output"], right["metrics"]["n_dp_output"]
                    ae, be = left["metrics"]["dp_max_error"], right["metrics"]["dp_max_error"]
                    if an > bn:
                        return False
                    strict |= an < bn
                else:
                    ae, be = a["candidate_max_on_baseline_covered"], b["candidate_max_on_baseline_covered"]
                    strict |= a["candidate_covered_count"] > b["candidate_covered_count"]
                if (ae is None) != (be is None):
                    return False
                if ae is not None:
                    if ae > be + eps:
                        return False
                    strict |= ae < be - eps
            return strict

        for cid, item in domain.items():
            dominated_by = [other for other, candidate in feasible.items()
                            if other != cid and item["feasible"] and dominates(candidate, item)]
            locked = inputs.lock["selected_single_candidates"][family] if inputs.lock else None
            tables["feasible_pareto"].append({"family": family, "config_id": cid,
                **item["parameters"], "feasible_all_records": item["feasible"],
                "on_feasible_frontier": item["feasible"] and not dominated_by,
                "dominated_by": dominated_by, "research_status": item["research_status"],
                "selected_before_evaluation": locked is not None and locked["config_id"] == cid,
                "dimensions": ("each record: minimize immediate P output points and actual P max error; same P reference, fixed 5-work-metre budget"
                               if family == "C-P" else
                               "each record: maximize covered original-index identity set; minimize max error on fixed baseline-covered mask"),
                "selection_changed_by_this_analysis": False,
                "frontier_is_quality_acceptance": False})


def order_analysis(inputs, tables):
    for role in ("order_development", "evaluation_orders"):
        if role not in inputs.manifests:
            continue
        _, manifest = inputs.manifests[role]
        entries = list(manifest["artifacts"].values())
        expected = set(inputs.contract["orders"] if role == "order_development" else inputs.freeze["orders"])
        if (len(entries) != len(expected) or {entry["order"] for entry in entries} != expected or
                any(entry["parameters"] != REFERENCE or entry["input_ids"] != manifest["input_ids"] for entry in entries)):
            raise ValueError("ANALYSIS_ORDER_MATRIX_INCOMPLETE")
        reference_entry = next(entry for entry in entries if entry["order"] == "S-D-P")
        baseline = {row["record_id"]: row for row in inputs.load_batch(role, reference_entry)["records"]}
        for entry in entries:
            result = inputs.load_batch(role, entry)
            context = batch_context(role, manifest, entry)
            comparisons, failures = [], []
            for row in result["records"]:
                rid, metric = row["record_id"], row["metrics"]
                base = baseline[rid]
                comparison = pair_reading(row, base)
                lost = sorted(covered(base) - covered(row))
                safety_fail = bool(metric["raw_break_crossings"] or lost or
                                   (base["metrics"]["record_covered"] and not metric["record_covered"]) or
                                   metric["raw_windows_covered"] < base["metrics"]["raw_windows_covered"])
                comparisons.append(comparison)
                tables["order_records"].append({**context, "stratum": inputs.cards[rid]["stratum"],
                    **compact_metrics(metric), **comparison, "safety_failure": safety_fail,
                    "lost_baseline_covered_indices": lost})
                stage_and_reason_tables(tables, context, row)
                if safety_fail:
                    failures.append(rid)
                if (safety_fail or metric["direction_windows_across_raw_breaks"] or
                        metric["p_removed_raw_break_trigger_points"] or entry["order"].index("P") < entry["order"].index("D")):
                    p_stage = next(stage for stage in row["stages"] if stage["name"] == "P")
                    d_stage = next(stage for stage in row["stages"] if stage["name"] == "D")
                    baseline_d = next(stage for stage in base["stages"] if stage["name"] == "D")
                    d_before = [segment["indices"] for segment in baseline_d["input"]]
                    d_current = [segment["indices"] for segment in d_stage["input"]]
                    tables["order_failure_mechanisms"].append({**context, "record_id": rid,
                        "safety_failure": safety_fail, "lost_baseline_covered_indices": lost,
                        "crossing_edges": metric["breakpoint_crossing_edges"],
                        "D_windows_across_raw_breaks": metric["direction_window_crossing_details"],
                        "P_removed_original_trigger_indices": metric["p_removed_raw_break_trigger_indices"],
                        "P_before_S": p_stage["position"] < next(stage for stage in row["stages"] if stage["name"] == "S")["position"],
                        "P_before_D": p_stage["position"] < d_stage["position"],
                        "D_input_neighbourhood_changed_from_reference": d_before != d_current,
                        "reference_D_input_indices": d_before, "actual_D_input_indices": d_current,
                        "n_filtered": metric["n_filtered"], "all_filtered": metric["all_filtered"],
                        "no_output": metric["no_output"], "engineering_error_claim": False})
            tables["order_configurations"].append({**context, **result["summary"],
                **comparison_summary(comparisons), "safety_failure_records": len(failures),
                "safety_failure_record_ids": failures,
                "research_status": "REJECTED_BY_CONSTRAINT" if failures else research_status(comparisons),
                "eligible_order_for_frozen_evaluation": not failures,
                "geometric_guard_failures": sum("COMMON_GEOMETRIC_PROTECTION_DEGRADED" in item["protection_failures"] for item in comparisons)})


def candidate_analysis(inputs, tables, catalogs):
    if inputs.lock is None:
        return
    development = catalogs.get("parameter_development", {})
    evaluation = catalogs.get("evaluation_parameters", {})
    for name in ("C-S", "C-D", "C-P"):
        lock = inputs.lock["selected_single_candidates"][name]
        cid = lock["config_id"]
        if cid not in development or development[cid]["parameters"] != lock["parameters"]:
            raise ValueError("LOCKED_CANDIDATE_NOT_IN_VERIFIED_DEVELOPMENT")
        tables["candidate_development"].append({"candidate": name, **lock,
            "evaluation_was_used_for_selection": False, "source_run_id": inputs.lock["parameter_run_id"]})
        if cid not in evaluation:
            tables["candidate_evaluation"].append({"candidate": name, "config_id": cid,
                "parameters": lock["parameters"], "status": "INSUFFICIENT_EVIDENCE",
                "recommendation": "INSUFFICIENT", "reason": "LOCKED_CANDIDATE_EVALUATION_NOT_AVAILABLE"})
            continue
        item = evaluation[cid]
        if item["parameters"] != lock["parameters"]:
            raise ValueError("EVALUATED_CANDIDATE_DIFFERS_FROM_FROZEN_PARAMETERS")
        records = item["records"]
        comparisons = [row["comparison"] for row in records.values()]
        status = research_status(comparisons)
        reference_retained = lock["parameters"] == REFERENCE
        recommendation = ("KEEP" if status == "SUPPORTED_WITHIN_SCOPE" else
                          "TRADEOFF" if status == "TRADEOFF" else
                          "REJECT" if status in ("REJECTED_BY_CONSTRAINT", "NO_DEMONSTRATED_GAIN") else "INSUFFICIENT")
        if reference_retained and status == "NO_DEMONSTRATED_GAIN":
            recommendation = "KEEP"
        tables["candidate_evaluation"].append({"candidate": name, "config_id": cid,
            **lock["parameters"], "development_selection_reason": lock["selection_reason"],
            "development_research_status": lock["research_status"],
            "evaluation_status": status, "recommendation": recommendation,
            "reference_retained": reference_retained, **comparison_summary(comparisons),
            **item["summary"], "automatic_new_goal3_candidate": status == "SUPPORTED_WITHIN_SCOPE" and not reference_retained,
            "quality_accepted": False, "final_method_frozen": False,
            "reason": ("Retain the operational reference without claiming it is optimal" if reference_retained else
                       "Every record passes the frozen guards and at least one has a strict registered gain" if status == "SUPPORTED_WITHIN_SCOPE" else
                       "No post-evaluation tuning; retain the observed failure, tradeoff or insufficient gain")})
        strata = defaultdict(list)
        for rid, row in records.items():
            pair = row["comparison"]
            tables["candidate_record_pairs"].append({"candidate": name, "config_id": cid,
                                                      "stratum": row["stratum"], **pair})
            strata[row["stratum"]].append(pair)
        for stratum, rows in sorted(strata.items()):
            tables["candidate_by_stratum"].append({"candidate": name, "config_id": cid,
                "stratum": stratum, **comparison_summary(rows), "research_status": research_status(rows)})


def mode_analysis(inputs, tables):
    all_records = []
    for role in ("mode_development", "mode_evaluation"):
        if role not in inputs.manifests:
            continue
        _, manifest = inputs.manifests[role]
        partition = manifest["partition"]
        repeats = 1 if partition == "DEVELOPMENT" else 3
        expected_ids = inputs.split["llm_subsets"][partition]
        seen = set()
        for directory, episode in inputs.episodes(role):
            mode, repeat = episode["mode"], episode["episode"]
            if mode not in MODES or repeat not in range(1, repeats + 1) or not set(episode["input_ids"]) <= set(expected_ids):
                raise ValueError("MODE_EPISODE_NOT_IN_FROZEN_MATRIX")
            context = {"run_id": manifest["run_id"], "partition": partition, "mode": mode,
                       "episode": repeat, "episode_id": episode["episode_id"]}
            resources = episode["resources"]
            if mode == "search-only" and resources["experiment_model_dispatches"] != 0:
                raise ValueError("SEARCH_ONLY_HIDDEN_MODEL_DISPATCH")
            if mode != "search-only" and (resources["experiment_model_dispatches"] < 1 or episode["classification"] != "LIVE_EXPERIMENT"):
                raise ValueError("LLM_MODE_REQUIRES_ACTUAL_LIVE_DISPATCH_EVIDENCE")
            if (not episode["working_memory_reset_at_episode_start"] or
                    episode["working_memory_persisted_for_next_episode"]):
                raise ValueError("MODE_WORKING_MEMORY_NOT_ISOLATED")
            tables["mode_batch_resources"].append({**context, "records": len(episode["records"]),
                                                   **resources, "elapsed_seconds": episode["elapsed_seconds"],
                                                   "classification": episode["classification"]})
            receipt_count = 0
            for filename in episode["artifact_hashes"]:
                if filename.endswith("/receipt.json"):
                    receipt = read_json(directory / filename)
                    if receipt.get("classification") != "LIVE_CALL_ATTEMPT":
                        raise ValueError("MODE_MODEL_RECEIPT_IS_NOT_A_LIVE_CALL_ATTEMPT")
                    receipt_count += 1
                    usage = receipt.get("usage")
                    tables["model_calls"].append({**context, "receipt_path": relative(directory / filename),
                        "receipt_sha256": episode["artifact_hashes"][filename],
                        **scalar_fields(receipt), "usage": usage,
                        "input_tokens": usage.get("input_tokens") if isinstance(usage, dict) else None,
                        "cached_input_tokens": usage.get("cached_input_tokens") if isinstance(usage, dict) else None,
                        "output_tokens": usage.get("output_tokens") if isinstance(usage, dict) else None,
                        "tokens_reason": None if isinstance(usage, dict) else "PROVIDER_USAGE_UNAVAILABLE",
                        "visible_counts": receipt.get("visible_counts")})
            if receipt_count != resources["experiment_model_dispatches"]:
                raise ValueError("MODEL_DISPATCH_RECEIPT_COUNT_MISMATCH")
            retrievals = read_json(directory / "memory_retrieval.json") if mode == "llm+memory+search" else {}
            if mode == "llm+memory+search":
                if "memory" not in inputs.manifests:
                    raise ValueError("MEMORY_MODE_WITHOUT_CURRENT_DEMONSTRATION_SNAPSHOT")
                snapshot_hash = inputs.manifests["memory"][1]["memory_snapshot"]["sha256"]
                if episode["snapshot_after"] != snapshot_hash:
                    raise ValueError("MODE_DOES_NOT_USE_CURRENT_DEMONSTRATION_SNAPSHOT")
                if inputs.freeze and episode["snapshot_after"] != inputs.freeze["memory_sha256"]:
                    raise ValueError("MEMORY_CHANGED_ACROSS_EPISODES")
                for rid, retrieval in retrievals.items():
                    if retrieval["snapshot_sha256"] != snapshot_hash:
                        raise ValueError("RETRIEVAL_SNAPSHOT_DIFFERS_FROM_CURRENT_MEMORY")
                    tables["memory_retrieval"].append({**context, "record_id": rid,
                        "eligible_count": retrieval["eligible_count"], "delivered_count": len(retrieval["delivered"]),
                        "delivered_ids": [row["memory_id"] for row in retrieval["delivered"]],
                        "filtered_count": len(retrieval["filtered"]), "filtered": retrieval["filtered"],
                        "empty_reason": retrieval["empty_reason"],
                        "snapshot_before": retrieval["snapshot_sha256"], "snapshot_after": episode["snapshot_after"],
                        "hash_unchanged": retrieval["snapshot_sha256"] == episode["snapshot_after"]})
                    for entry in retrieval["delivered"]:
                        if entry["record_id"] == rid or entry["record_id"] not in inputs.split["splits"]["DEMO_MEMORY"]:
                            raise ValueError("MEMORY_SELF_OR_NONDEMO_RETRIEVAL")
                        tables["memory_delivered_entries"].append({**context, "query_record_id": rid,
                            "memory_id": entry["memory_id"], "memory_record_id": entry["record_id"],
                            "stratum": entry["stratum"], "retrieval_distance": entry["retrieval_distance"],
                            "selected_parameters": entry["selected_parameters"], "research_status": entry["research_status"]})
            for record in episode["records"]:
                rid = record["record_id"]
                key = (mode, repeat, rid)
                if key in seen:
                    raise ValueError("DUPLICATE_MODE_RECORD_EPISODE")
                seen.add(key)
                trace_name = rid + "_candidate_traces.json.gz"
                if trace_name not in episode["artifact_hashes"]:
                    raise ValueError("MODE_CANDIDATE_TRACE_UNREGISTERED")
                trace = read_gzip(directory / trace_name)
                candidates = trace["results"]
                if set(candidates) != set(record["candidate_ids"]) or set(trace["reviews"]) != set(candidates):
                    raise ValueError("MODE_CANDIDATE_SET_MISMATCH")
                reference_id, selected_id = record["reference_config_id"], record["selected_config_id"]
                selected, baseline = candidates[selected_id], candidates[reference_id]
                if mode == "llm+memory+search" and record["memory_snapshot_hash"] != snapshot_hash:
                    raise ValueError("MODE_RECORD_MEMORY_SNAPSHOT_MISMATCH")
                if (reference_id != config_id(REFERENCE) or
                        compact_metrics(selected["metrics"]) != record["selected_metrics"] or
                        compact_metrics(baseline["metrics"]) != record["reference_metrics"] or
                        selected["parameters"] != record["selected_parameters"] or
                        trace["post_lock_review"]["target_hash"] != object_hash(selected) or
                        trace["post_lock_review"]["status"] != "VERIFIED" or
                        record["engineering_status"] != "VERIFIED"):
                    raise ValueError("MODE_LOCKED_RESULT_BINDING_MISMATCH")
                for cid, candidate in candidates.items():
                    audit = trace["reviews"][cid]
                    expected_provenance = {"run_id": manifest["run_id"], "partition": partition,
                        "raw_sha256": manifest["raw_sha256"], "split_sha256": inputs.split_hash,
                        "contract_sha256": inputs.contract_hash, "scope_sha256": object_hash([rid]),
                        "source_tree_sha256": manifest["source_tree_sha256"], "episode_id": episode["episode_id"]}
                    if (candidate["record_id"] != rid or config_id(candidate["parameters"]) != cid or
                            audit["status"] != "VERIFIED" or audit["target_hash"] != object_hash(candidate) or
                            candidate["contract_hash"] != inputs.contract_hash or
                            any(candidate["provenance"].get(key) != value for key, value in expected_provenance.items())):
                        raise ValueError("MODE_CANDIDATE_REVIEW_BINDING_MISMATCH")
                    assessment = compare(candidate, baseline)
                    tables["mode_candidates"].append({**context, "record_id": rid, "config_id": cid,
                        **candidate["parameters"], **compact_metrics(candidate["metrics"]),
                        **assessment, "selected": cid == selected_id,
                        "reference": cid == reference_id,
                        "on_recorded_frontier": cid in record["selection"].get("frontier", []),
                        "frontier_reason": None if "frontier" in record["selection"] else "SINGLE_LOCKED_PROPOSAL_MODE"})
                if record["resources"]["unique_candidate_evaluations"] != len(candidates):
                    raise ValueError("MODE_CANDIDATE_BUDGET_COUNTER_MISMATCH")
                if mode != "llm-only" and len(candidates) > 20:
                    raise ValueError("MODE_CANDIDATE_BUDGET_EXCEEDED")
                if record["resources"]["decision_rounds"] > (1 if mode == "llm-only" else 3):
                    raise ValueError("MODE_DECISION_ROUND_BUDGET_EXCEEDED")
                pair = pair_reading(selected, baseline)
                if compare(selected, baseline) != record["research_assessment"]:
                    raise ValueError("MODE_SAVED_RESEARCH_ASSESSMENT_MISMATCH")
                row = {**context, "record_id": rid, "stratum": inputs.cards[rid]["stratum"],
                       "selected_config_id": selected_id, "selected_parameters": record["selected_parameters"],
                       "fallback": record["fallback"], "selection_reason": record["selection"]["reason"],
                       "memory_snapshot_hash": record["memory_snapshot_hash"],
                       **record["resources"], **pair}
                tables["mode_record_results"].append(row)
                row_internal = {**row, "selected_metrics": record["selected_metrics"],
                                "proposal_records": record["proposal_records"], "rounds": record["rounds"],
                                "selected_mask": covered(selected),
                                "selected_dp_input_hash": object_hash(next(stage for stage in selected["stages"] if stage["name"] == "P")["input"])}
                all_records.append(row_internal)
                for index, proposal in enumerate(record["proposal_records"], 1):
                    original = proposal.get("original", {})
                    prediction = proposal.get("prediction", {})
                    response_sources = []
                    for filename, sha256 in episode["artifact_hashes"].items():
                        if (filename.startswith(f"round{proposal['round']}_call/") and
                                filename.endswith("/response.json")):
                            response = read_json(directory / filename)
                            if any(action.get("record_id") == rid and original in action.get("proposals", [])
                                   for action in response.get("records", []) if isinstance(action, dict)):
                                response_sources.append({"path": relative(directory / filename), "sha256": sha256})
                    if original and not response_sources:
                        raise ValueError("PRESERVED_PROPOSAL_NOT_FOUND_IN_RAW_MODEL_RESPONSE")
                    if proposal["legal"] and proposal["executed"] and proposal["executed_config_id"] not in candidates:
                        raise ValueError("EXECUTED_MODEL_PROPOSAL_MISSING_CANDIDATE")
                    if mode == "llm-only" and sum("original" in item for item in record["proposal_records"]) > 1:
                        raise ValueError("LLM_ONLY_EXTRA_PROPOSAL")
                    tables["mode_proposals"].append({**context, "record_id": rid,
                        "proposal_number": index, "round": proposal["round"],
                        "original_proposal": original or None, "original_present": bool(original),
                        "candidate_id": original.get("candidate_id"), "parameters": original.get("parameters"),
                        "reason": original.get("reason"), "legal": proposal["legal"],
                        "executed": proposal["executed"], "executed_config_id": proposal.get("executed_config_id"),
                        "rejection_reason": proposal.get("rejection_reason", proposal.get("reason")),
                        "metric_id": original.get("metric_id"), "predicted_sign": original.get("predicted_sign"),
                        "prediction_status": prediction.get("status", "NOT_EXECUTED_OR_NO_PROPOSAL"),
                        "prediction_evaluable": prediction.get("evaluable", False),
                        "prediction_matches": prediction.get("prediction_matches"),
                        "observed_sign": prediction.get("observed_sign"), "delta": prediction.get("delta"),
                        "reference_handle": proposal.get("reference_handle_locked_before_execution"),
                        "prediction_reference_trace_hash": prediction.get("reference_handle"),
                        "prediction_candidate_trace_hash": prediction.get("candidate_handle"),
                        "raw_response_sources": response_sources,
                        "fallback_for_record": record["fallback"],
                        "proposal_is_selected_output": proposal.get("executed_config_id") == selected_id,
                        "raw_proposal_was_clamped": False})
                for decision in record["rounds"]:
                    tables["mode_rounds"].append({**context, "record_id": rid, **decision})
                    if "memory_consumption" in decision:
                        use = decision["memory_consumption"]
                        tables["memory_consumption"].append({**context, "record_id": rid,
                            "round": decision["round"], **use,
                            "delivered_count": len(use["delivered_ids"]),
                            "valid_citation_count": len(use["model_cited_valid"]),
                            "invalid_citation_count": len(use["model_cited_invalid"]),
                            "action_consistent_count": len(use["action_consistent"]),
                            "action_consistent_is_causal_benefit": False})
        expected = {(mode, repeat, rid) for mode in MODES for repeat in range(1, repeats + 1) for rid in expected_ids}
        if seen != expected:
            raise ValueError("MODE_MATRIX_INCOMPLETE:" + role)
    return all_records


def mode_statistics(tables, records):
    grouped = defaultdict(list)
    for row in records:
        grouped[(row["partition"], row["mode"], row["episode"])].append(row)
    for (partition, mode, repeat), rows in grouped.items():
        for metric in PAIR_METRICS:
            tables["mode_episode_distributions"].append({"partition": partition, "mode": mode,
                "episode": repeat, "metric": metric, "statistical_unit": "original_record",
                "reading": "locked_selected_value", **numeric_summary([row["selected_metrics"][metric] for row in rows])})
            tables["mode_episode_distributions"].append({"partition": partition, "mode": mode,
                "episode": repeat, "metric": metric, "statistical_unit": "original_record",
                "reading": "paired_delta_from_reference_on_comparable_domains",
                **numeric_summary([row["delta_" + metric] for row in rows])})
    repeats = defaultdict(list)
    for row in records:
        repeats[(row["partition"], row["mode"], row["record_id"])].append(row)
    for (partition, mode, rid), rows in repeats.items():
        for metric in PAIR_METRICS:
            tables["mode_record_repeat_distributions"].append({"partition": partition, "mode": mode,
                "record_id": rid, "metric": metric, "reading": "within_record_episode_distribution",
                "episodes": [row["episode"] for row in rows],
                **numeric_summary([row["selected_metrics"][metric] for row in rows])})
    indexed = {(row["partition"], row["episode"], row["record_id"], row["mode"]): row for row in records}
    scopes = sorted({key[:3] for key in indexed})
    for partition, repeat, rid in scopes:
        for first, second in combinations(MODES, 2):
            left, right = indexed[(partition, repeat, rid, first)], indexed[(partition, repeat, rid, second)]
            for metric in PAIR_METRICS:
                a, b = left["selected_metrics"][metric], right["selected_metrics"][metric]
                reason = None
                if a is None or b is None:
                    reason = "UNAVAILABLE_IN_AT_LEAST_ONE_ARM"
                elif metric == "common_max_error" and left["selected_mask"] != right["selected_mask"]:
                    reason = "DIFFERENT_COMMON_COVERED_MASK"
                elif metric in ("n_dp_output", "dp_saving", "dp_max_error") and left["selected_dp_input_hash"] != right["selected_dp_input_hash"]:
                    reason = "DIFFERENT_DP_INPUT_REFERENCE"
                tables["mode_pairwise"].append({"partition": partition, "episode": repeat,
                    "record_id": rid, "mode_a": first, "mode_b": second, "metric": metric,
                    "value_a": a, "value_b": b, "difference_b_minus_a": b - a if reason is None else None,
                    "unavailable_reason": reason, "statistical_unit": "original_record",
                    "causal_effect_claim": False})
        without = indexed[(partition, repeat, rid, "llm+search")]
        with_memory = indexed[(partition, repeat, rid, "llm+memory+search")]
        def first_parameters(row):
            return [p.get("original", {}).get("parameters") for p in row["proposal_records"] if p["round"] == 1]
        a, b = first_parameters(without), first_parameters(with_memory)
        available = bool(a and b and all(value is not None for value in a + b))
        tables["memory_independent_mode_comparison"].append({"partition": partition, "episode": repeat,
            "record_id": rid, "without_memory_initial_parameters": a, "with_memory_initial_parameters": b,
            "initial_proposal_changed": a != b if available else None,
            "comparison_reason": None if available else "MISSING_VALID_INITIAL_PROPOSAL_STRUCTURE",
            "selected_parameters_changed": without["selected_parameters"] != with_memory["selected_parameters"],
            "without_memory_selected": without["selected_parameters"], "with_memory_selected": with_memory["selected_parameters"],
            "memory_delivered_rounds": sum(bool(row.get("memory_consumption", {}).get("delivered_ids")) for row in with_memory["rounds"]),
            "memory_cited_rounds": sum(bool(row.get("memory_consumption", {}).get("model_cited_valid")) for row in with_memory["rounds"]),
            "memory_action_consistent_rounds": sum(bool(row.get("memory_consumption", {}).get("action_consistent")) for row in with_memory["rounds"]),
            "causal_benefit_proven": False,
            "interpretation": "Independent model episodes with equal registered conditions; a changed suggestion or citation is not isolated evidence of memory benefit"})
    for partition, mode in sorted({(row["partition"], row["mode"]) for row in records}):
        rows = [row for row in records if row["partition"] == partition and row["mode"] == mode]
        proposals = [row for row in tables["mode_proposals"] if row["partition"] == partition and row["mode"] == mode]
        original = [row for row in proposals if row["original_present"]]
        predictions = [row for row in proposals if row["prediction_evaluable"]]
        batches = [row for row in tables["mode_batch_resources"] if row["partition"] == partition and row["mode"] == mode]
        calls = [row for row in tables["model_calls"] if row["partition"] == partition and row["mode"] == mode]
        legal_n = sum(row["legal"] for row in original)
        dispatched = sum(row["experiment_model_dispatches"] for row in batches)
        summary = {"partition": partition, "mode": mode, "original_records": len({row["record_id"] for row in rows}),
            "episodes": len({row["episode"] for row in rows}), "record_episode_observations": len(rows),
            "valid_raw_proposal_denominator": len(original), "raw_legal_proposals": legal_n,
            "raw_legality_denominator_scope": "Preserved raw proposals with a record-bound action structure; rejected unbound/malformed actions reported separately, never counted as legal",
            "raw_legal_fraction": legal_n / len(original) if original else None,
            "raw_legal_fraction_reason": None if original else "NO_RAW_PROPOSALS_IN_THIS_MODE_OR_VALID_RESPONSE",
            "invalid_structure_record_actions": sum(not row["original_present"] for row in proposals),
            "executed_proposals": sum(row["executed"] for row in original),
            "executed_proposal_fraction": sum(row["executed"] for row in original) / len(original) if original else None,
            "rejection_reasons": dict(Counter(row["rejection_reason"] for row in proposals if row["rejection_reason"])),
            "evaluable_prediction_denominator": len(predictions),
            "matching_predictions": sum(row["prediction_matches"] is True for row in predictions),
            "prediction_agreement": sum(row["prediction_matches"] is True for row in predictions) / len(predictions) if predictions else None,
            "prediction_statuses": dict(Counter(row["prediction_status"] for row in proposals)),
            "fallback_records_episodes": sum(row["fallback"] for row in rows),
            "constraint_rejected_records_episodes": sum(row["status"] == "REJECTED_BY_CONSTRAINT" for row in rows),
            "tradeoff_records_episodes": sum(row["status"] == "TRADEOFF" for row in rows),
            "protected_gain_records_episodes": sum(row["strict_gain"] for row in rows),
            "experiment_model_dispatches": dispatched,
            "completed_model_turns": sum(row["completed_model_turns"] for row in batches),
            "candidate_evaluations": sum(row["candidate_evaluations"] for row in batches),
            "reference_assessments_outside_llm_only_decision": sum(row["reference_assessments_outside_llm_only_decision"] for row in batches),
            "deterministic_tool_calls": sum(row["deterministic_tool_calls"] for row in batches),
            "replay_or_cache_reads": sum(row["cache_reads"] for row in batches),
            "max_candidates_per_record_episode": max(row["unique_candidate_evaluations"] for row in rows),
            "max_decision_rounds_per_record_episode": max(row["decision_rounds"] for row in rows),
            "elapsed_batch_seconds_sum": sum(row["elapsed_seconds"] for row in batches),
            "provider_request_count": 0 if mode == "search-only" else "unknown",
            "governance_role_dispatches": 0,
            "governance_scope": "No governance roles inside experiment; external A/B/C cost is recorded separately by Goal controller",
            "cost_currency": "unavailable", "quality_accepted": False}
        for token_field in ("input_tokens", "cached_input_tokens", "output_tokens"):
            available = [row[token_field] for row in calls if row[token_field] is not None]
            summary[token_field + "_observed_sum"] = sum(available) if available or dispatched == 0 else None
            summary[token_field + "_available_call_receipts"] = len(available)
            summary[token_field + "_unavailable_call_receipts"] = len(calls) - len(available)
        tables["mode_summary"].append(summary)
        for metric in PAIR_METRICS:
            per_record = [row["mean"] for row in tables["mode_record_repeat_distributions"]
                          if row["partition"] == partition and row["mode"] == mode and row["metric"] == metric]
            tables["mode_original_record_summary"].append({"partition": partition, "mode": mode, "metric": metric,
                "aggregation": "mean episodes within each original record, then describe original records",
                "population_weighting": "none; stratified sample, not population mean", **numeric_summary(per_record)})


def memory_analysis(inputs, tables):
    if "memory" not in inputs.manifests:
        return None
    directory, manifest = inputs.manifests["memory"]
    info = manifest["memory_snapshot"]
    path = checked(bound_path(directory, info["path"]), info["sha256"])
    snapshot = read_json(path)
    entries = snapshot["entries"]
    if (len(entries) != 60 or {row["record_id"] for row in entries} != set(inputs.split["splits"]["DEMO_MEMORY"]) or
            snapshot["contract_sha256"] != inputs.contract_hash or snapshot["raw_sha256"] != inputs.split["raw_sha256"] or
            snapshot["split_sha256"] != object_hash(inputs.split) or snapshot["evaluation_policy"] != "READ_ONLY"):
        raise ValueError("MEMORY_SNAPSHOT_SCOPE_OR_VERSION_MISMATCH")
    inputs.lineage[relative(path)] = info["sha256"]
    for entry in entries:
        trace_path = checked(bound_path(ROOT, entry["trace_path"]), entry["trace_sha256"])
        review_path = checked(bound_path(ROOT, entry["review_path"]), entry["review_sha256"])
        trace, review = read_gzip(trace_path), read_json(review_path)
        if (review["status"] != "VERIFIED" or review["target_hash"] != object_hash(trace) or
                entry["engineering_status"] != "VERIFIED" or trace["record_id"] != entry["record_id"] or
                compact_metrics(trace["metrics"]) != entry["selected_metrics"]):
            raise ValueError("MEMORY_ENTRY_ADMISSION_BINDING_MISMATCH")
        tables["memory_entries"].append({key: value for key, value in entry.items() if key != "trusted_provenance"})
    return {"snapshot_path": relative(path), "snapshot_sha256": info["sha256"],
            "demonstration_records": len(entries), "research_status_counts": dict(Counter(row["research_status"] for row in entries)),
            "read_only_policy": snapshot["evaluation_policy"], "human_knowledge_entries": len(snapshot["human_knowledge"]),
            "human_knowledge_reason": snapshot["human_knowledge_reason"],
            "work_memory_persisted": snapshot["working_memory_persisted"], "new_memory_writes_by_analysis": 0}


def counterexample_analysis(inputs, tables):
    value = inputs.current.get("counterexamples")
    if not value:
        inputs.missing.append("counterexamples")
        return None
    directory = bound_path(ROOT, value)
    manifest = read_json(directory / "manifest.json")
    if (manifest["status"] != "ENGINEERING_VERIFIED" or
            manifest["g2_parent_contract_hash"] != inputs.contract_hash):
        raise ValueError("COUNTEREXAMPLE_PARENT_OR_STATUS_MISMATCH")
    if (manifest["raw_sha256"] != inputs.split["raw_sha256"] or
            manifest["pilot_scope"] != inputs.split["splits"]["PILOT_REGRESSION"]):
        raise ValueError("FORMAL_COUNTEREXAMPLE_RUN_MUST_INCLUDE_EXPOSED_PILOT_SCOPE")
    for source, sha256 in manifest["source_files"].items():
        checked(bound_path(ROOT, source), sha256)
    for filename, sha256 in manifest["artifacts"].items():
        checked(bound_path(directory, filename), sha256)
    inputs.lineage[relative(directory / "manifest.json")] = digest(directory / "manifest.json")
    synthetic = read_json(directory / "synthetic_cases.json")
    for case in synthetic["cases"]:
        if any(not row["passed"] for row in case["known_answer_checks"]):
            raise ValueError("COUNTEREXAMPLE_KNOWN_ANSWER_CHECK_FAILED")
        for name, execution in case["executions"].items():
            tables["counterexamples"].append({"case_id": case["case_id"], "execution": name,
                "classification": "SYNTHETIC_COUNTEREXAMPLE", **compact_metrics(execution["output"]["metrics"]),
                "parameters": execution["output"]["parameters"], "order": execution["output"]["order"],
                "synthetic_truth_counts": execution.get("synthetic_detection_counts"),
                "known_answer_checks": case["known_answer_checks"],
                "interpretation": case["interpretation"], "action": case["action"],
                "real_data_accuracy_claim": False})
    pilot_path = directory / "exposed_pilot_cases.json"
    if pilot_path.exists():
        pilot = read_json(pilot_path)
        for item in pilot["all_filtered_records_0_1_2"]:
            tables["exposed_pilot_filtering"].append(item)
        for item in pilot["direction_adjacency_cases"]:
            tables["exposed_pilot_direction"].append(item)
    return {"manifest_path": relative(directory / "manifest.json"),
            "synthetic_cases": len(synthetic["cases"]), "known_answer_checks": synthetic["known_answer_check_count"],
            "synthetic_pipeline_executions": manifest["synthetic_pipeline_executions"],
            "exposed_pilot_pipeline_executions": manifest["pilot_pipeline_executions"],
            "synthetic_truth_is_population_truth": False}


def actual_ai_critique(tables):
    examples = []
    coverage = {}
    for kind in ("ILLEGAL_PROPOSAL", "CORRECT_EVALUABLE_PREDICTION", "PREDICTION_MISMATCH",
                 "UNEVALUABLE_PREDICTION", "FALLBACK"):
        eligible = [row for row in tables["mode_proposals"] if row["original_present"] and
                    ((kind == "ILLEGAL_PROPOSAL" and not row["legal"]) or
                     (kind == "CORRECT_EVALUABLE_PREDICTION" and row["prediction_evaluable"] and row["prediction_matches"] is True) or
                     (kind == "PREDICTION_MISMATCH" and row["prediction_evaluable"] and row["prediction_matches"] is False) or
                     (kind == "UNEVALUABLE_PREDICTION" and not row["prediction_evaluable"]) or
                     (kind == "FALLBACK" and row["fallback_for_record"]))]
        eligible.sort(key=lambda row: (row["partition"], row["mode"], row["episode"], row["record_id"], row["round"], row["proposal_number"]))
        coverage[kind] = {"observed_count": len(eligible), "example_present": bool(eligible),
                          "absence_reason": None if eligible else "NO_ACTUAL_OBSERVATION_IN_VALID_CURRENT_RUNS"}
        if eligible:
            examples.append({"kind": kind, "selection_rule": "first observed matching proposal in stable partition/mode/episode/record/round order", **eligible[0]})
    return {"examples": examples, "category_coverage": coverage, "selection_rule_fixed_in_script": True,
            "no_observed_example_reason": None if examples else "No actual proposal available; no invented model quotations",
            "teacher_assumption_critique": "The archived teacher time-threshold explanation is checked arithmetically: 20 > 15, so dt=15 splits a 20-unit interval; this is not attributed to a current model response",
            "synthetic_risks_not_attributed_to_models": True}


def provider_cost_summary(rows, scope):
    """Visible dispatch evidence is not an exact count of underlying requests."""
    summary = {"scope": scope, "visible_experiment_model_dispatches": len(rows),
        "completed_calls": sum(row.get("status") == "VERIFIED_STRUCTURE_ONLY" for row in rows),
        "interrupted_or_failed_calls": sum(row.get("status") == "FAILED" for row in rows),
        "dispatches_without_final_receipt": sum(row.get("status") == "DISPATCHED_NO_FINAL_RECEIPT" for row in rows),
        "provider_request_count": "unknown" if rows else 0, "currency_cost": "unavailable",
        "count_unit": "controller dispatch evidenced by a provider receipt or unmatched dispatch record; not hidden provider requests",
        "counts_as_current_effectiveness_evidence": scope == "CURRENT_VALID_RUNS"}
    for field in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                  "output_tokens", "reasoning_output_tokens"):
        values = [row["usage"][field] for row in rows
                  if isinstance(row.get("usage"), dict) and field in row["usage"]]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in values):
            raise ValueError("INVALID_OBSERVED_TOKEN_USAGE")
        summary[field + "_known_sum"] = sum(values)
        summary[field + "_available_dispatches"] = len(values)
        summary[field + "_unknown_dispatches"] = len(rows) - len(values)
        summary[field + "_all_dispatch_total"] = sum(values) if len(values) == len(rows) else "unknown"
    elapsed = [row["elapsed_seconds"] for row in rows if isinstance(row.get("elapsed_seconds"), (int, float))]
    summary["elapsed_seconds_known_sum"] = math.fsum(elapsed)
    summary["elapsed_seconds_unknown_dispatches"] = len(rows) - len(elapsed)
    summary["elapsed_seconds_all_dispatch_total"] = math.fsum(elapsed) if len(elapsed) == len(rows) else "unknown"
    summary["usage_limit"] = "Token fields are reported separately; cached/reasoning counts may be subsets and are not added into a fabricated total. Known sums omit unknown usage and are not complete cost totals."
    return summary


def memory_admission_count(directory, manifest):
    if "memory_snapshot" not in manifest:
        return (None, "NO_COMPLETED_MEMORY_SNAPSHOT_ADMISSION_COUNT_UNKNOWN") if manifest["partition"] == "DEMO_MEMORY" else (0, "NOT_A_MEMORY_BUILD_RUN")
    info = manifest["memory_snapshot"]
    path = checked(bound_path(directory, info["path"]), info["sha256"])
    snapshot = read_json(path)
    ids = [entry["record_id"] for entry in snapshot["entries"]]
    if (len(ids) != len(set(ids)) or set(ids) != set(manifest["input_ids"]) or
            snapshot["contract_sha256"] != manifest["contract_sha256"] or
            snapshot["raw_sha256"] != manifest["raw_sha256"] or
            any(entry["engineering_status"] != "VERIFIED" for entry in snapshot["entries"])):
        raise ValueError("MEMORY_ADMISSION_RESOURCE_SCOPE_MISMATCH")
    return len(ids), "Completed hash-bound snapshot: build_snapshot calls review_record once for every admitted demonstration entry"


def historical_model_costs(inputs, tables, historical):
    """Read failed/superseded costs without accepting their results as current."""
    declaration_path = inputs.evidence / "interrupted_model_costs.json"
    declaration = read_json(declaration_path) if declaration_path.exists() else None
    if declaration:
        inputs.lineage[relative(declaration_path)] = digest(declaration_path)
        if declaration["run_id"] not in historical:
            raise ValueError("INTERRUPTED_COST_RUN_NOT_REGISTERED_SUPERSEDED")
    for run_id, (directory, manifest, entry) in historical.items():
        receipt_paths = list(directory.glob("modes/*/round*_call/attempt*/receipt.json"))
        dispatch_only = [path for path in directory.glob("modes/*/round*_call/attempt*/dispatch.json")
                         if not (path.parent / "receipt.json").exists()]
        for path in sorted(receipt_paths + dispatch_only):
            path = bound_path(directory, str(path.relative_to(directory)))
            receipt = read_json(path)
            if receipt.get("classification") != "LIVE_CALL_ATTEMPT":
                raise ValueError("HISTORICAL_COST_IS_NOT_AN_ACTUAL_LIVE_DISPATCH")
            is_final_receipt = path.name == "receipt.json"
            usage = receipt.get("usage")
            relpath = relative(path)
            inputs.lineage[relpath] = digest(path)
            tables["historical_model_calls"].append({"resource_scope": "HISTORICAL_SUPERSEDED_OR_INTERRUPTED",
                "run_id": run_id, "partition": manifest["partition"], "run_status": entry["status"],
                "receipt_path": relpath, "receipt_sha256": digest(path),
                "status": receipt.get("status") if is_final_receipt else "DISPATCHED_NO_FINAL_RECEIPT",
                "request_id": receipt.get("request_id"), "request_id_kind": "controller logical ID; not provider request ID",
                "thread_id": receipt.get("thread_id"), "requested_model": receipt.get("requested_model"),
                "provider_request_ids": receipt.get("provider_request_ids", "unavailable"),
                "underlying_requests": "unknown", "usage": usage if isinstance(usage, dict) else "unknown",
                "raw_usage_field": usage, "usage_availability": "observed" if isinstance(usage, dict) else "unknown",
                "started_at": receipt.get("started_at"), "ended_at": receipt.get("ended_at"),
                "elapsed_seconds": receipt.get("elapsed_seconds"), "error": receipt.get("error"),
                "reason_not_current": entry["reason"], "counts_as_current_effectiveness_evidence": False})
    if declaration:
        rows = [row for row in tables["historical_model_calls"] if row["run_id"] == declaration["run_id"]]
        observed = {row["receipt_path"]: row for row in rows}
        declared = {row["path"]: row for row in declaration["calls"]}
        if len(declared) != len(declaration["calls"]) or set(observed) != set(declared):
            raise ValueError("INTERRUPTED_MODEL_COST_RECEIPT_SCOPE_MISMATCH")
        for path, row in declared.items():
            actual = observed[path]
            raw_usage, declared_usage = actual["raw_usage_field"], row.get("usage")
            observed_known = raw_usage if isinstance(raw_usage, dict) else None
            declared_known = declared_usage if isinstance(declared_usage, dict) else None
            actual["declared_usage_field"] = declared_usage
            actual["usage_declaration_reason"] = ("No measured usage: an absent receipt field and an unavailable declaration both remain unknown"
                                                   if observed_known is None and declared_known is None else None)
            if any(actual.get(key) != row.get(key) for key in ("status", "request_id", "thread_id", "error")) or observed_known != declared_known:
                raise ValueError("INTERRUPTED_MODEL_COST_DECLARATION_DIFFERS_FROM_RECEIPT")
        if (len(rows) != declaration["all_visible_experiment_model_dispatches"] or
                sum(row["status"] == "VERIFIED_STRUCTURE_ONLY" for row in rows) != declaration["completed_calls"] or
                sum(row["status"] != "VERIFIED_STRUCTURE_ONLY" for row in rows) != declaration["interrupted_or_failed_calls"]):
            raise ValueError("INTERRUPTED_MODEL_COST_AGGREGATE_MISMATCH")
    return provider_cost_summary(tables["historical_model_calls"], "HISTORICAL_SUPERSEDED_OR_INTERRUPTED")


def resource_accounting(inputs, tables):
    scope_path = inputs.evidence / "c_contract/development_resource_scope.json"
    if scope_path.exists():
        scope_document = read_json(scope_path)
        inputs.lineage[relative(scope_path)] = digest(scope_path)
    else:
        scope_document = None
    superseded_path = inputs.evidence / "superseded_runs.json"
    historical = {}
    if superseded_path.exists():
        registry = read_json(superseded_path)
        inputs.lineage[relative(superseded_path)] = digest(superseded_path)
        current_ids = {manifest["run_id"] for _, manifest in inputs.manifests.values()}
        for entry in registry["runs"]:
            run_id = entry["run_id"]
            if not isinstance(run_id, str) or Path(run_id).name != run_id or run_id in historical or run_id in current_ids:
                raise ValueError("SUPERSEDED_RESOURCE_SCOPE_OVERLAPS_CURRENT_OR_DUPLICATE")
            directory = bound_path(inputs.evidence / "runs", run_id)
            path = checked(directory / "manifest.json", entry["original_manifest_sha256"])
            manifest = read_json(path)
            if manifest["run_id"] != run_id or entry["status"] not in ("SUPERSEDED", "INTERRUPTED_CHECKPOINT_SUPERSEDED"):
                raise ValueError("INVALID_SUPERSEDED_RESOURCE_REGISTRY")
            inputs.lineage[relative(path)] = entry["original_manifest_sha256"]
            historical[run_id] = (directory, manifest, entry)
    history_summary = historical_model_costs(inputs, tables, historical)
    current_summary = provider_cost_summary(tables["model_calls"], "CURRENT_VALID_RUNS")
    all_runs = [(role, directory, manifest, "CURRENT_VALID_RUNS", manifest["status"])
                for role, (directory, manifest) in inputs.manifests.items()]
    all_runs.extend(("historical_registered_run", directory, manifest,
                     "HISTORICAL_SUPERSEDED_OR_INTERRUPTED", entry["status"])
                    for directory, manifest, entry in historical.values())
    for role, directory, manifest, scope, status in all_runs:
        admission, admission_reason = memory_admission_count(directory, manifest)
        raw_calls, cache_reviews = manifest["deterministic_tool_calls"], manifest["cache_reads"]
        registered_calls = raw_calls + cache_reviews + admission if admission is not None else None
        provider_rows = tables["model_calls"] if scope == "CURRENT_VALID_RUNS" else tables["historical_model_calls"]
        observed_dispatches = sum(row["run_id"] == manifest["run_id"] for row in provider_rows)
        incomplete = status == "INTERRUPTED_CHECKPOINT_SUPERSEDED"
        row = {"resource_scope": scope, "run_role": role, "run_id": manifest["run_id"],
            "run_status": status, "partition": manifest["partition"],
            "manifest_path": relative(directory / "manifest.json"), "manifest_sha256": digest(directory / "manifest.json"),
            "candidate_evaluations_reported_manifest": manifest["candidate_evaluations"],
            "experiment_model_dispatches_reported_manifest": manifest["experiment_model_dispatches"],
            "visible_model_dispatches_audited_from_receipts": observed_dispatches,
            "deterministic_tool_calls_reported_manifest": raw_calls,
            "cache_hit_batch_verifier_calls": cache_reviews,
            "deterministic_tool_calls_with_cache_reviews": raw_calls + cache_reviews,
            "memory_admission_per_record_verifier_calls": admission,
            "memory_admission_count_basis": admission_reason,
            "registered_processing_verifier_calls": registered_calls,
            "registered_call_total_availability": "known" if registered_calls is not None else "unknown",
            "manifest_processing_scope_complete": not incomplete,
            "processing_scope_limit": ("Interrupted mode run: incomplete-batch processing absent from manifest remains unknown; provider receipts are audited across complete and incomplete batches"
                                       if incomplete else "Recorded production run and completed snapshot admission only"),
            "tool_count_unit": "registered processing/verifier function invocation, not all Python helper calls or CPU operations",
            "tool_count_scope": "Manifest new-candidate processing/review and mode post-lock review; plus one review_batch per ExperimentRun cache hit and one review_record per completed memory snapshot entry",
            "excluded_governance": "Candidate-lock rechecks, independent C audits, engineering tests, counterexample/coordinate diagnostics and report/replay work have separate evidence; not included in this registered-run total",
            "manifest_cache_reads": manifest["cache_reads"],
            "cache_counter_scope": "ExperimentRun batch cache hits; per-mode candidate cache reads separately in mode_summary",
            "started_at": manifest["started_at"], "ended_at": manifest.get("ended_at"),
            "underlying_provider_requests": "unknown" if observed_dispatches else 0,
            "governance_role_dispatches": "unavailable_in_experiment_manifest",
            "counts_as_current_effectiveness_evidence": scope == "CURRENT_VALID_RUNS"}
        if scope_document:
            documented = next((item for item in scope_document["runs"] if item["run_id"] == manifest["run_id"]), None)
            if documented:
                if (documented["manifest_sha256"] != row["manifest_sha256"] or
                        documented["instrumented_new_candidate_tool_calls"] != raw_calls or
                        documented["cache_hit_independent_verifier_calls"] != cache_reviews or
                        documented["memory_admission_per_record_verifier_calls"] != admission):
                    raise ValueError("C_RESOURCE_SCOPE_RECEIPT_MISMATCH")
                row["independent_C_resource_scope_evidence"] = relative(scope_path)
        tables["resource_totals"].append(row)
    tables["model_cost_scope_summary"].extend([current_summary, history_summary])
    return {"current_valid_model_costs": current_summary, "historical_model_costs": history_summary,
            "all_visible_experiment_model_dispatches": current_summary["visible_experiment_model_dispatches"] + history_summary["visible_experiment_model_dispatches"],
            "all_underlying_provider_requests": "unknown" if tables["model_calls"] or tables["historical_model_calls"] else 0,
            "historical_costs_are_current_effectiveness_results": False,
            "registered_current_processing_verifier_calls": sum(row["registered_processing_verifier_calls"] for row in tables["resource_totals"]
                if row["resource_scope"] == "CURRENT_VALID_RUNS" and row["registered_processing_verifier_calls"] is not None),
            "registered_historical_processing_verifier_calls_known": sum(row["registered_processing_verifier_calls"] for row in tables["resource_totals"]
                if row["resource_scope"] == "HISTORICAL_SUPERSEDED_OR_INTERRUPTED" and row["registered_processing_verifier_calls"] is not None),
            "historical_processing_incomplete_run_ids": [row["run_id"] for row in tables["resource_totals"] if not row["manifest_processing_scope_complete"]],
            "registered_call_unit": "Only named processing/verifier dispatches; not all helpers, OS tools, model-side hidden calls or governance computations"}


def write_tables(output_directory, tables):
    directory = Path(output_directory) / "tables"
    directory.mkdir(parents=True, exist_ok=True)
    registry = {}
    for name, rows in sorted(tables.items()):
        path = directory / (name + ".csv")
        fields = list(dict.fromkeys(key for row in rows for key in row)) or ["status"]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
                                 if isinstance(value, (dict, list)) else value for key, value in row.items()})
        registry[name] = {"path": relative(path), "sha256": digest(path), "rows": len(rows),
                          "null_encoding": "empty CSV cell; companion reason/denominator columns retain meaning"}
    return registry


def fmt(value):
    if value is None:
        return "不可用"
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


def render_document(summary, tables, path):
    lines = ["# Goal 2 阶段技术分析", "",
        "本文件由当前有效 run 的固定哈希产物生成；不调用模型、不修改参数、不重新选择候选。"
        "它是阶段分析，不替代独立 C 全验收、网页 GPT 二重验收或用户最终研究判断。", "",
        f"派生状态：**{summary['analysis_status']}**。原始 CRS 为 UNVERIFIED；距离和几何误差均为共同模型下的工作米。", ""]
    if summary["missing_requirements"]:
        lines.extend(["缺少的必需输入：" + "、".join(summary["missing_requirements"]) + "。以下仅陈述已有的有效计算，不宣称 Goal 2 完成。", ""])
    lines.extend(["## 数据与比较口径", "",
        "按原始记录分组，固定 seed=42，以原始跨度分位层、时间异常和相邻精确重复作描述性分层。"
        "低／中／高层不是标注运动真值；等额分层样本均值不代表总体均值。", "",
        "| 分区 | 记录数 | 用途 |", "|---|---:|---|"])
    purposes = {"PILOT_REGRESSION": "七条已暴露回归", "DEMO_MEMORY": "记忆构建",
                "DEVELOPMENT": "参数与选择", "G2_EVAL": "锁定后阶段评估", "G3_RESERVED": "本轮保留，不用于选择或评测"}
    for name, count in summary["data"]["partition_records"].items():
        lines.append(f"| {name} | {count} | {purposes.get(name, '')} |")
    lines.extend(["", "共同参考固定为原始 dt=30、distance=400 的窗口，不做短段过滤。覆盖由保留原始点或同一原始窗口内的原始索引包围边定义；"
        "未覆盖误差为 null，并保留原始分母。保护比较要求基线已覆盖点身份集合不丢失，防止以易点替换难点。"
        "不同 clean 的 P 局部误差不能证明整体质量更高。", "",
        "DP 省点率使用即时 P 输出／完整 P 输入；P 后续被 D/S 删除的点另计。空 P 输入不填 0。"
        "点保留、记录覆盖、全部由 S 过滤和最终无输出分别报告。长度、异常数与删点量均为描述性读数。", "",
        "## 参数实验与稳定性", ""])
    parameters = [row for row in tables["parameter_configurations"] if row["partition"] == "DEVELOPMENT"]
    if parameters:
        lines.append(f"DEVELOPMENT 实际计算 {len(parameters)} 个唯一配置，覆盖冻结的全部 OAT 与两个 5×5 网格；重复实验成员共用相同 experiment key。")
        reference = next(row for row in parameters if all(row[key] == value for key, value in REFERENCE.items()))
        lines.extend(["", f"参考链的 {reference['n_records']} 条记录共 {reference['n_input']} 原始点，保留 {reference['n_final']} 点；"
            f"S 过滤 {reference['n_filtered']} 点，D 删除 {reference['n_direction_removed']} 点，P 即时输入 {reference['n_dp_input']} 点，"
            f"即时输出 {reference['n_dp_output']} 点，省点率 {fmt(reference['dp_saving'])}。"
            f"全部由 S 过滤 {reference['n_all_filtered_records']} 条，最终无输出 {reference['n_no_output_records']} 条；"
            f"共同原始覆盖 {reference['common_covered_points']}/{reference['common_raw_points']}。", ""])
    else:
        lines.extend(["尚无完整参数运行可供陈述。", ""])
    intervals = [row for row in tables["stable_intervals"] if row["stable_at_multiple_tested_values"]]
    lines.append("稳定区间仅指相邻已测试 OAT 值具有完全相同的逐记录阶段索引集合、共同覆盖集合与去向计数；不对未测试的连续区间作保证。")
    if intervals:
        lines.extend(["", "| 参数 | 观察到的相同响应取值 |", "|---|---|"])
        lines.extend(f"| {row['parameter']} | {row['registered_grid_values']} |" for row in intervals)
    else:
        lines.append("当前有效表中没有两个相邻取值满足这一完整一致条件；不以近似平均数制造平台区间。")
    lines.extend(["", "各配置、分层、逐记录配对及完整可行集/Pareto 关系见 tables/parameter_*.csv、stable_intervals.csv 和 feasible_pareto.csv。"
        "C-S/C-D 比较共同覆盖及基线覆盖集合上的几何误差；C-P 在相同上游和固定 5 工作米预算内比较压缩。没有新加权质量分。", "",
        "## 顺序对照", "", "| 分区 | 顺序 | 安全失败记录 | 跨原始断点边 | D 跨断点窗口 | P 删除断点触发点 | 结论 |",
        "|---|---|---:|---:|---:|---:|---|"])
    for row in tables["order_configurations"]:
        lines.append(f"| {row['partition']} | {row['order']} | {row['safety_failure_records']} | {row['raw_break_crossings']} | "
                     f"{row['direction_windows_across_raw_breaks']} | {row['p_removed_raw_break_trigger_points']} | {row['research_status']} |")
    lines.extend(["", "S 的点数／长度过滤作用于当时输入；P 可能改变断点触发点，D 可能形成跨间断的方向窗口，P 在 D 前会改变邻域。"
        "order_failure_mechanisms.csv 保存实际索引、跨越边及邻域变化，不能仅凭顺序标签断言每条记录发生了同一种失败。"
        "安全失败的原始顺序保留为约束拒绝，不加隐藏预分段使其通过。评测只执行开发期已冻结的可行顺序。", "",
        "## 四种模式、预算与记忆", "",
        "同一分区的四模式共享固定 24 条记录。开发各 1 个 episode，正式评测各 3 个独立 episode；"
        "模型不能设置 seed 时记录 episode，不能声称模型完全可重复。llm-only 一次提议，搜索模式最多 20 候选、最多 3 决策回合；"
        "参考评分与 llm-only 决策之外的工作单列，批量 8 条记录的请求只计一次真实派发。", "",
        "| 分区 | 模式 | 记录×episode | 原始合法/有原始提议 | 执行提议 | 回退 | 实验模型派发 | 候选评估 |",
        "|---|---|---:|---:|---:|---:|---:|---:|"])
    for row in tables["mode_summary"]:
        lines.append(f"| {row['partition']} | {row['mode']} | {row['original_records']}×{row['episodes']} | "
                     f"{row['raw_legal_proposals']}/{row['valid_raw_proposal_denominator']} | {row['executed_proposals']} | "
                     f"{row['fallback_records_episodes']} | {row['experiment_model_dispatches']} | {row['candidate_evaluations']} |")
    lines.extend(["", "mode_pairwise.csv 保留同记录同 episode 的模式配对及不可比原因；mode_episode_distributions.csv 展示三次 episode 的分布。"
        "总体读数先在同一原始记录内汇总重复，再描述原始记录；重复、片段和点均不作为新增独立样本。"
        "这里只报告描述性分布，不将三次小样本胜负解释为稳定总体优势。", "",
        "model_calls.csv 保存真实回执、可见 tokens、耗时与可用请求标识；底层请求数与费用不可见时保持 unknown/unavailable。"
        "治理 A/B/C 调用另由控制器记录，不能充当 search-only 的实验模型调用。"
        "resource_totals.csv 区分 manifest 原始处理/审核计数、缓存命中后 review_batch、以及记忆快照逐条准入的 review_record；"
        "三者之和只称注册 processing/verifier 调用，不是全部 Python helper 或 CPU 操作。"
        "候选锁定和治理复验属于额外治理工作，不混入模式实验调用。", ""])
    costs = summary["resource_accounting"]
    historical = costs["historical_model_costs"]
    lines.extend([f"当前有效模型派发 {costs['current_valid_model_costs']['visible_experiment_model_dispatches']} 次；"
        f"历史已失效或中断运行另有 {historical['visible_experiment_model_dispatches']} 次真实可见派发，"
        f"其中 {historical['completed_calls']} 次完成、{historical['interrupted_or_failed_calls']} 次中断或失败。"
        "历史成本逐项回读原始 provider receipt，并与 interrupted_model_costs.json 对照；"
        "它们不进入当前模式效果、合法率或收益统计。缺失 usage 保持 unknown，已观察 tokens 的部分和不冒充完整总成本。"
        "详见 historical_model_calls.csv 与 model_cost_scope_summary.csv。", ""])
    memory = summary.get("memory")
    if memory:
        retrievals = tables["memory_retrieval"]
        uses = tables["memory_consumption"]
        lines.extend([f"示范记忆来自 {memory['demonstration_records']} 条 DEMO_MEMORY，冻结哈希 `{memory['snapshot_sha256']}`。"
            f"有效检索记录 episode 中，{sum(row['delivered_count'] > 0 for row in retrievals)}/{len(retrievals)} 有实际送达条目；"
            f"{sum(row['valid_citation_count'] > 0 for row in uses)}/{len(uses)} 个有记录的决策回合引用了有效条目，"
            f"{sum(row['action_consistent_count'] > 0 for row in uses)}/{len(uses)} 回合同时满足引用与参数一致。", "",
            "上述分母分别是检索机会和实际决策回合。命中、模型引用、参数一致、与无记忆独立 episode 的建议变化分别保存；"
            "均不能单独证明记忆改善质量。评测快照前后哈希必须相同，示范条目不包含评测记录。", ""])
    lines.extend(["## 已锁定的单项候选", "", "| 候选 | 配置 | 留出结论 | 建议 | 保护通过/记录 | 严格增益记录 |",
                  "|---|---|---|---|---:|---:|"])
    for row in tables["candidate_evaluation"]:
        lines.append(f"| {row['candidate']} | {row['config_id']} | {row.get('evaluation_status', row.get('status'))} | "
                     f"{row['recommendation']} | {row.get('feasible_records', 'NA')}/{row.get('n_records', 'NA')} | {row.get('strict_gain_records', 'NA')} |")
    lines.extend(["", "候选参数在 G2_EVAL 前锁定，本表只应用原保护规则；没有评测后重选。保留参考配置是操作性回退，不代表参考已证最优。"
        "支持进入 Goal 3 的对象仍是单项证据；本轮不叠加 C-S/C-D/C-P，不冻结最终方法。分层退化见 candidate_by_stratum.csv，"
        "逐记录保护失败见 candidate_record_pairs.csv。两个轻量结构类别按冻结合同登记 NOT_ADMITTED_WITH_REASON。", "",
        "## AI 建议与反例核验", ""])
    critique = summary["ai_critique"]
    for example in critique["examples"]:
        reason = json.dumps(example["reason"], ensure_ascii=False)
        source_links = ", ".join("[原始 response](" + os.path.relpath(ROOT / item["path"], Path(path).parent) + ")"
                                 for item in example["raw_response_sources"])
        lines.extend([f"实际 {example['kind']}：{example['partition']} / {example['mode']} / episode {example['episode']} / "
            f"记录 {example['record_id']} / round {example['round']}。模型原始理由：{reason}。"
            f"合法={example['legal']}，执行={example['executed']}；预测 {example['metric_id']} {example['predicted_sign']}，"
            f"实际 {example['observed_sign']}，差值 {fmt(example['delta'])}，预测状态 {example['prediction_status']}；"
            f"拒绝原因 {example['rejection_reason']}，是否成为锁定输出={example['proposal_is_selected_output']}。"
            f"执行前参考句柄 `{example['reference_handle']}`。来源：{source_links}；"
            "候选与参考 trace 的核验哈希在 mode_proposals.csv。这是可执行性和预测方向核对，不是真实质量验收。", ""])
    absent = [name for name, value in critique["category_coverage"].items() if not value["example_present"]]
    if absent:
        lines.extend(["未观察到以下类别，故没有对应模型引语：" + "、".join(absent) + "。", ""])
    if not critique["examples"]:
        lines.extend(["当前尚无可引用的真实提议；不虚构模型原话。", ""])
    lines.extend([critique["teacher_assumption_critique"] + "。", ""])
    counterexamples = summary.get("counterexamples")
    if counterexamples:
        lines.extend([f"构造反例实际执行 {counterexamples['synthetic_pipeline_executions']} 条处理链，"
            f"覆盖 {counterexamples['synthetic_cases']} 组、{counterexamples['known_answer_checks']} 项已知答案检查。"
            "正常转弯／毛刺、零位移／同时间异位置、断点信息损失、有限线段与阈值等号、删光与自有 clean 评价漏洞均有前后指标。"
            "这些是显式构造风险检验，不冒充自然数据错误或模型曾说过的话。", "",
            "记录 0、1、2 的过滤原因、方向删除后的邻接改变和近 DP 阈值区间见 exposed_pilot_* 表与反例目录 CASE_ANALYSIS.md；"
            "七条 pilot 已经暴露，不能称为新留出发现。", ""])
    lines.extend(["## 解释边界与复现", "",
        "所有几何结果条件于固定数学椭球、h=0 和共同 ENU 平面；坐标敏感性独立产物描述扩大空间范围内的实现误差、"
        "近似差异和实际阈值变化，不能由清洗分数反选坐标模型。没有真实噪声标签，因此不报告真实误删率、检测准确率或真值恢复率。", "",
        "bounded-search 是有限预算参考；没有冻结可比标量目标时，本轮不计算归一化 regret，也不称搜索为全局最优。"
        "负结果、约束拒绝与无收益是有效实验结果，与实现错误分别记录。", "",
        "复算入口：`python -m task1.scripts.build_goal2_analysis --current-runs task1/evidence/goal2/current_runs.json "
        "--output-dir task1/evidence/goal2 --document task1/docs/goal2/STAGE_ANALYSIS.md`。本脚本只重建分析表；"
        "从原始数据重建确定性处理和图请使用 Goal 2 工作 Notebook 的默认 RECOMPUTE 入口，真实新调用须显式 LIVE。", "",
        "输入哈希、每张表的哈希及行数均在 result_summary.json。GPT_SECOND_REVIEW=PENDING；Submission=NOT_READY。"
        "本文件不宣称最终报告定稿、Evidence Lock、用户 Understanding 通过或项目最终 PASS。", ""])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build(current_runs=EVIDENCE / "current_runs.json", output_directory=EVIDENCE, document=DOCUMENT):
    analysis_source_sha256 = digest(Path(__file__))
    inputs = Inputs(current_runs)
    tables = defaultdict(list)
    catalogs = {}
    parameter_analysis(inputs, tables, catalogs)
    pareto_analysis(inputs, tables, catalogs)
    order_analysis(inputs, tables)
    candidate_analysis(inputs, tables, catalogs)
    memory = memory_analysis(inputs, tables)
    records = mode_analysis(inputs, tables)
    mode_statistics(tables, records)
    counterexamples = counterexample_analysis(inputs, tables)
    resources = resource_accounting(inputs, tables)
    critique = actual_ai_critique(tables)
    tables["ai_critique_examples"] = critique["examples"]
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    summary = {
        "goal_id": inputs.contract["goal_id"], "generated_at": now(),
        "analysis_status": "INCOMPLETE" if inputs.missing else "COMPLETE_DERIVATION_FROM_VERIFIED_TRACES",
        "classification": "STAGE_ANALYSIS_NOT_INDEPENDENT_FINAL_ACCEPTANCE",
        "goal2_internal_engineering_status": "REQUIRES_INDEPENDENT_C_FULL_ACCEPTANCE",
        "GPT_SECOND_REVIEW": "PENDING", "submission": "NOT_READY", "source_crs": "UNVERIFIED",
        "missing_requirements": inputs.missing,
        "current_runs": inputs.current, "input_hashes": inputs.lineage,
        "analysis_source_sha256": analysis_source_sha256, "actual_command": list(sys.argv),
        "analysis_model_dispatches": 0, "analysis_candidate_evaluations": 0,
        "analysis_memory_writes": 0, "analysis_new_candidate_selection": False,
        "data": {"raw_sha256": inputs.split["raw_sha256"], "raw_records": inputs.split["raw_records"],
                 "raw_points": inputs.split["raw_points"], "partition_records": {key: len(value) for key, value in inputs.split["splits"].items()},
                 "llm_subset_records": {key: len(value) for key, value in inputs.split["llm_subsets"].items()},
                 "sample_weighting": inputs.split["sample_weighting"], "statistical_unit": "original_record",
                 "g3_reserved_used_for_selection_or_evaluation": False},
        "parameters": {"unique_development_configs": len(catalogs.get("parameter_development", {})),
                       "unique_evaluation_configs": len(catalogs.get("evaluation_parameters", {})),
                       "reference": REFERENCE, "grid": GRID},
        "orders": tables["order_configurations"], "single_candidates": tables["candidate_evaluation"],
        "structural_candidates": inputs.contract["structural_candidates"],
        "mode_summary": tables["mode_summary"], "memory": memory, "counterexamples": counterexamples,
        "resource_accounting": resources,
        "ai_critique": critique,
        "selection_after_evaluation": False, "final_method_frozen": False,
        "quality_accepted": False, "normalized_regret": None,
        "normalized_regret_reason": "No frozen comparable scalar objective or positive headroom; retain paired metric differences",
        "limits": ["source datum unverified; conditional working-plane geometry",
                   "stratified original-record sample does not estimate population accuracy",
                   "no real-data noise labels; no true false-deletion or restoration accuracy",
                   "provider underlying request counts and costs can be unavailable",
                   "independent episodes, memory citation and parameter agreement do not establish causal memory benefit",
                   "summary reads verified evidence; independent raw recomputation and full C acceptance are separate"],
    }
    if digest(Path(__file__)) != analysis_source_sha256:
        raise ValueError("ANALYSIS_SOURCE_CHANGED_DURING_DERIVATION")
    render_document(summary, tables, document)
    summary["tables"] = write_tables(output_directory, tables)
    summary["stage_analysis"] = {"path": relative(document), "sha256": digest(document)}
    write_json(output_directory / "result_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-runs", type=Path, default=EVIDENCE / "current_runs.json")
    parser.add_argument("--output-dir", type=Path, default=EVIDENCE)
    parser.add_argument("--document", type=Path, default=DOCUMENT)
    args = parser.parse_args()
    summary = build(args.current_runs, args.output_dir, args.document)
    print(json.dumps({"analysis_status": summary["analysis_status"],
                      "missing_requirements": summary["missing_requirements"],
                      "tables": len(summary["tables"]), "document": summary["stage_analysis"]["path"],
                      "new_model_dispatches": 0}, ensure_ascii=False))
    return 0 if not summary["missing_requirements"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
