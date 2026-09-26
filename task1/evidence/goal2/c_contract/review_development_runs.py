"""Independent C review of completed G2 deterministic development runs.

No processing, metric, selection or raw-adapter implementation is imported.
All files are read-only except new C-owned reports. Full checks cover byte/hash
bindings, ordered scope, original values, S/D operations, P certificates, ledger,
common-reference errors, denominators and aggregation. Decimal DP reconstruction
is sampled by a rule fixed here before the formal results are read.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import pyproj

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from independent_numeric import audit_record, directions, partition, length, allowance
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from task1.workflow.g2_journal import task_sources, REQUIRED_COMPONENTS

OUT = Path(__file__).resolve().parent
EV = ROOT / "task1/evidence/goal2"
CFG = ROOT / "task1/config/goal2"
KINDS = {"parameters": ("development_parameters", "DEVELOPMENT", 59, "parameter_table.json"),
         "orders": ("development_orders", "DEVELOPMENT", 6, "order_table.json"),
         "memory": ("memory", "DEMO_MEMORY", 20, None)}
SAMPLE_RULE = {
    "every_artifact": ["first all-filtered record by stable ID", "maximum common error; stable ID tie",
                       "closest actual DP error to positive tolerance; stable ID tie", "largest raw point count; stable ID tie"],
    "reference_config_and_every_order": "one minimum SHA256(42|C-review|record_id) record per frozen descriptive stratum",
    "purpose": "independent audit sampling only; never candidate selection or representative population estimation"}
COUNT_FIELDS = ("n_input", "n_final", "n_filtered", "n_direction_removed", "n_dp_removed", "n_dp_input", "n_dp_output",
                "n_dp_exceedances", "n_s_segments", "n_filtered_segments", "common_raw_points", "common_covered_points",
                "common_uncovered_points", "common_over_5_points", "raw_break_count", "raw_break_crossings", "raw_breaks_crossed",
                "raw_break_trigger_points_removed", "raw_windows", "raw_windows_covered", "direction_candidate_points",
                "direction_undefined_points", "direction_windows_across_raw_breaks", "p_removed_raw_break_trigger_points")


def read_compressed(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def finite(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    wx, wy = p[0] - a[0], p[1] - a[1]
    denominator = vx * vx + vy * vy
    fraction = min(1.0, max(0.0, (wx * vx + wy * vy) / denominator)) if denominator else 0.0
    return math.hypot(wx - fraction * vx, wy - fraction * vy)


def quantile(values, q):
    if not values:
        return None
    values = sorted(values)
    position = q * (len(values) - 1)
    left = int(position)
    return values[left] + (values[min(left + 1, len(values) - 1)] - values[left]) * (position - left)


def rank(rid):
    return hashlib.sha256(("42|C-review|" + rid).encode()).hexdigest(), rid


def config_id(p):
    return "cfg-" + object_hash({key: float(value) for key, value in p.items()})[:16]


class Audit:
    def __init__(self):
        self.check_count = 0
        self.errors = []

    def check(self, label, condition, details=None):
        self.check_count += 1
        if not condition:
            self.errors.append({"check": label, "details": details})
            if len(self.errors) >= 100:
                raise ValueError("C_ERROR_LIMIT_REACHED; first 100 failures retained")

    def same(self, label, actual, expected, eps=0):
        if isinstance(expected, dict):
            self.check(label + ":fields", isinstance(actual, dict) and set(actual) == set(expected))
            if isinstance(actual, dict):
                for key in expected.keys() & actual.keys():
                    self.same(label + ":" + str(key), actual[key], expected[key], eps)
        elif isinstance(expected, list):
            self.check(label + ":length", isinstance(actual, list) and len(actual) == len(expected))
            if isinstance(actual, list):
                for number, (a, b) in enumerate(zip(actual, expected)):
                    self.same(label + ":" + str(number), a, b, eps)
        elif expected is None or isinstance(expected, (str, bool, int)):
            self.check(label, type(actual) is type(expected) and actual == expected, [actual, expected] if actual != expected else None)
        else:
            self.check(label, isinstance(actual, (float, int)) and not isinstance(actual, bool)
                       and math.isfinite(actual) and abs(actual - expected) <= eps, [actual, expected])


def common(times, xy, final):
    windows, boundaries = partition(times, xy, list(range(len(times))), 30, 400)
    window_of = {index: number for number, indices in enumerate(windows) for index in indices}
    retained = {index for indices in final for index in indices}
    values = {index: 0.0 for index in retained}
    crossed = []
    for indices in final:
        for a, b in zip(indices, indices[1:]):
            if window_of[a] != window_of[b]:
                crossed.append({"from_index": a, "to_index": b, "cuts": [row["to_index"] for row in boundaries if a < row["to_index"] <= b]})
            else:
                for index in range(a + 1, b):
                    values[index] = finite(xy[index], xy[a], xy[b])
    return windows, boundaries, window_of, retained, values, crossed


def record_check(audit, record, raw, parameters, order, chash, provenance, expected_xy):
    rid = record["record_id"]
    label = rid + "/" + order
    times, _ = raw
    source = record["source_record"]
    xy = source["xy"]
    audit.same(label + ":source_indices", source["indices"], list(range(len(times))))
    audit.same(label + ":timestamps", source["timestamps"], times)
    audit.check(label + ":PROJ_all_points", len(xy) == len(expected_xy) and all(math.dist(p, q) <= 1e-6 for p, q in zip(xy, expected_xy)))
    audit.check(label + ":source_hash", record["source_record_hash"] == object_hash(source))
    for field, value in {"parameters": parameters, "order": order, "contract_hash": chash, "provenance": provenance,
                         "source_crs": "UNVERIFIED", "modified_values": 0,
                         "classification": "CURRENT_RUN_CONDITIONAL_ANALYSIS", "working_unit": "conditional_working_metre"}.items():
        audit.same(label + ":binding:" + field, record[field], value)
    eps = allowance(xy, max(5, parameters["dp"]))
    current = [list(range(len(times)))] if times else []
    fates, counts = {}, Counter()
    dp_errors, dp_in, dp_out = [], [], []
    all_parts, direction_rows, direction_input = [], [], []

    def segment_values(segment, indices, name):
        audit.check(name + ":record", segment["record_id"] == rid)
        audit.same(name + ":indices", segment["indices"], indices)
        audit.same(name + ":times", segment["timestamps"], [times[index] for index in indices])
        audit.same(name + ":xy", segment["xy"], [xy[index] for index in indices])

    audit.check(label + ":three_stages", len(record["stages"]) == 3)
    for position, (stage, name) in enumerate(zip(record["stages"], order.split("-")), 1):
        tag = label + ":stage" + str(position)
        audit.check(tag + ":identity", stage["name"] == name and stage["position"] == position)
        audit.check(tag + ":input_groups", len(stage["input"]) == len(current) == len(stage["operations"]))
        for number, (segment, indices) in enumerate(zip(stage["input"], current)):
            segment_values(segment, indices, tag + ":input" + str(number))
        output = []
        if name == "D":
            direction_input = deepcopy(current)
        if name == "P":
            dp_in = deepcopy(current)
        for number, (indices, operation) in enumerate(zip(current, stage["operations"])):
            if name == "S":
                groups, boundaries = partition(times, xy, indices, parameters["dt"], parameters["distance"])
                audit.same(tag + ":breaks" + str(number), [{k: r[k] for k in ("from_index", "to_index", "reasons")} for r in operation["boundaries"]], boundaries)
                audit.check(tag + ":parts" + str(number), len(operation["segments"]) == len(groups))
                for group, part in zip(groups, operation["segments"]):
                    reasons = (["TOO_FEW_POINTS"] if len(group) < parameters["min_points"] else [])
                    if length(xy, group) < parameters["min_length"]:
                        reasons.append("TOO_SHORT_LENGTH")
                    segment_values(part, group, tag + ":part")
                    audit.same(tag + ":filter_reasons", part["filter_reasons"], reasons)
                    all_parts.append((group, reasons))
                    if reasons:
                        fates.update((index, ("filtered", position, reasons)) for index in group)
                    else:
                        output.append(group)
            elif name == "D":
                decisions = directions(xy, indices, parameters["direction"])
                deleted = [row["index"] for row in decisions if row["candidate"] is True]
                audit.same(tag + ":deleted" + str(number), operation["deleted_indices"], deleted)
                audit.check(tag + ":once_simultaneous", operation["passes"] == 1 and operation["method"] == "single_pass_simultaneous_keep_undefined")
                audit.same(tag + ":decision_flags", [{k: r[k] for k in ("index", "candidate", "reason")} for r in operation["decisions"]],
                           [{k: r[k] for k in ("index", "candidate", "reason")} for r in decisions])
                direction_rows.extend(decisions)
                fates.update((index, ("denoised", position, ["DIRECTION_RULE"])) for index in deleted)
                output.append([index for index in indices if index not in deleted])
            else:
                kept = stage["output"][number]["indices"]
                audit.check(tag + ":P_ordered_subsequence", kept == sorted(set(kept)) and set(kept) <= set(indices))
                audit.check(tag + ":P_endpoints", not indices or kept[0] == indices[0] and kept[-1] == indices[-1])
                if parameters["dp"] == 0:
                    audit.same(tag + ":zero_DP_keeps_all", kept, indices)
                values = {index: 0.0 for index in kept}
                for left, right in zip(kept, kept[1:]):
                    for index in indices:
                        if left < index < right:
                            values[index] = finite(xy[index], xy[left], xy[right])
                audit.check(tag + ":complete_P_reference", set(values) == set(indices))
                audit.check(tag + ":P_budget", all(v <= parameters["dp"] + eps for v in values.values()))
                dp_errors.extend(values.values())
                dp_out.append(kept)
                fates.update((index, ("simplified", position, ["DP_WITHIN_TOLERANCE"])) for index in indices if index not in kept)
                output.append(kept)
        audit.check(tag + ":output_groups", len(stage["output"]) == len(output))
        for number, (segment, indices) in enumerate(zip(stage["output"], output)):
            segment_values(segment, indices, tag + ":output" + str(number))
        current = output
    audit.check(label + ":final_groups", len(record["final_segments"]) == len(current))
    for number, (segment, indices) in enumerate(zip(record["final_segments"], current)):
        segment_values(segment, indices, label + ":final" + str(number))
        fates.update((index, ("retained", 4, ["FINAL_OUTPUT"])) for index in indices)
    audit.same(label + ":ledger_scope", [r["original_index"] for r in record["point_actions"]], list(range(len(times))))
    for row in record["point_actions"]:
        index = row["original_index"]
        audit.check(label + ":ledger_values", row["record_id"] == rid and row["timestamp"] == times[index] and row["xy"] == xy[index])
        audit.check(label + ":ledger_fate", (row["action"], row["stage_position"], row["reasons"]) == fates[index])
        counts[row["action"]] += 1
    windows, boundaries, window_of, retained, errors, crossings = common(times, xy, current)
    values = list(errors.values())
    p_in, p_out = set(index for group in dp_in for index in group), set(index for group in dp_out for index in group)
    triggers = {i for row in boundaries for i in (row["from_index"], row["to_index"])}
    d_crossings = sum(any(group[pos - 1] < cut["to_index"] <= group[pos + 2] for cut in boundaries)
                      for group in direction_input for pos in range(1, len(group) - 2))
    n = len(times)
    actual = record["metrics"]
    expected = {"n_input": n, "n_final": len(retained), "n_filtered": counts["filtered"], "n_direction_removed": counts["denoised"],
                "n_dp_removed": counts["simplified"], "n_dp_input": len(p_in), "n_dp_output": len(p_out), "n_dp_exceedances": 0,
                "dp_checks_passed": True, "n_s_segments": len(all_parts), "n_filtered_segments": sum(bool(reasons) for _, reasons in all_parts),
                "all_filtered": bool(n and counts["filtered"] == n), "no_output": bool(n and not retained), "record_covered": bool(retained),
                "point_retention": len(retained) / n if n else None, "dp_saving": 1 - len(p_out) / len(p_in) if p_in else None,
                "dp_error_denominator": len(p_in), "dp_max_error": max(dp_errors, default=None),
                "dp_mean_error": math.fsum(dp_errors) / len(dp_errors) if dp_errors else None,
                "common_raw_points": n, "common_covered_points": len(errors), "common_uncovered_points": n - len(errors),
                "common_error_denominator": len(errors), "common_coverage": len(errors) / n if n else None,
                "common_max_error": max(values, default=None), "common_mean_error": math.fsum(values) / len(values) if values else None,
                "common_p95_error": quantile(values, .95), "common_over_5_points": sum(v > 5 + eps for v in values),
                "raw_break_count": len(boundaries), "raw_break_crossings": len(crossings),
                "raw_breaks_crossed": len({cut for edge in crossings for cut in edge["cuts"]}),
                "raw_break_trigger_points_removed": len(triggers - retained), "raw_windows": len(windows),
                "raw_windows_covered": len({window_of[index] for index in errors}),
                "p_removed_raw_break_trigger_points": len((triggers & p_in) - p_out),
                "direction_candidate_points": sum(row["candidate"] is True for row in direction_rows),
                "direction_undefined_points": sum(row["reason"] is not None for row in direction_rows),
                "direction_windows_across_raw_breaks": d_crossings,
                "filter_reason_segments": dict(Counter(reason for _, reasons in all_parts for reason in reasons)),
                "filter_reason_points": {reason: sum(len(group) for group, reasons in all_parts if reason in reasons) for reason in {r for _, reasons in all_parts for r in reasons}},
                "direction_undefined_reasons": dict(Counter(row["reason"] for row in direction_rows if row["reason"] is not None))}
    for q in (.5, .9, .95, .99):
        expected["dp_p" + str(int(q * 100)) + "_error"] = quantile(dp_errors, q)
    for field, value in expected.items():
        audit.same(label + ":metric:" + field, actual[field], value, eps)
    audit.same(label + ":common_point_scope", [row["index"] for row in actual["common_point_errors"]], list(range(n)))
    for row in actual["common_point_errors"]:
        index = row["index"]
        audit.same(label + ":common_point_error", row["error"], errors.get(index), eps)
        audit.check(label + ":null_reason", row["reason"] is None if index in errors else bool(row["reason"]))
        audit.check(label + ":window_id", row["reference_window"] == window_of[index])
    audit.check(label + ":null_DP_reason", bool(actual["dp_saving_reason"]) if not p_in else actual["dp_saving_reason"] is None)
    audit.check(label + ":null_common_reason", bool(actual["common_error_reason"]) if not errors else actual["common_error_reason"] is None)
    terminal = "EMPTY_INPUT" if not n else "ALL_FILTERED" if counts["filtered"] == n else "NO_OUTPUT_AFTER_STAGE_FILTERING" if not retained else "PROCESSED"
    audit.same(label + ":terminal", record["terminal_status"], terminal)
    return {"epsilon": eps, "metrics": expected, "covered": sorted(errors), "common_errors": errors,
            "P_input": dp_in, "crossings": crossings, "raw_points": n}


def summary_expected(rows):
    result = {name: sum(row[name] for row in rows) for name in COUNT_FIELDS}
    result.update(n_records=len(rows), n_records_covered=sum(row["record_covered"] for row in rows),
                  n_all_filtered_records=sum(row["all_filtered"] for row in rows), n_no_output_records=sum(row["no_output"] for row in rows))
    ratios = {"point_retention": (result["n_final"], result["n_input"]), "record_coverage": (result["n_records_covered"], len(rows)),
              "all_filtered_record_fraction": (result["n_all_filtered_records"], len(rows)), "no_output_record_fraction": (result["n_no_output_records"], len(rows)),
              "common_coverage": (result["common_covered_points"], result["common_raw_points"])}
    for name, (n, d) in ratios.items():
        result[name] = n / d if d else None
        result[name + "_reason"] = None if d else "EMPTY_DENOMINATOR"
    result["dp_saving"] = 1 - result["n_dp_output"] / result["n_dp_input"] if result["n_dp_input"] else None
    result["dp_saving_reason"] = None if result["n_dp_input"] else "EMPTY_DP_REFERENCE_DENOMINATOR"
    for name in ("dp_max_error", "common_max_error"):
        values = [row[name] for row in rows if row[name] is not None]
        result[name], result[name + "_reason"] = (max(values), None) if values else (None, "NO_AVAILABLE_REFERENCE")
    for name in ("point_retention", "dp_saving", "common_coverage", "common_max_error", "common_mean_error"):
        values = [row[name] for row in rows if row[name] is not None]
        result["record_mean_" + name] = math.fsum(values) / len(values) if values else None
        result["record_mean_" + name + "_denominator"] = len(values)
        result["record_mean_" + name + "_unavailable_records"] = len(rows) - len(values)
    for name in ("filter_reason_segments", "filter_reason_points", "direction_undefined_reasons"):
        counts = Counter()
        for row in rows:
            counts.update(row[name])
        result[name] = dict(counts)
    result["dp_checks_passed"] = all(row["dp_checks_passed"] for row in rows)
    result["aggregation_unit"] = "original_record; pooled counts explicitly identified"
    return result


def sample_ids(records, parameters, cards, extra_strata):
    groups = defaultdict(list)
    for record in records:
        groups[cards[record["record_id"]]["stratum"]].append(record["record_id"])
    selected = {}
    def add(record, reason):
        selected.setdefault(record["record_id"], []).append(reason)
    filtered = [r for r in records if r["metrics"]["all_filtered"]]
    if filtered:
        add(min(filtered, key=lambda r: r["record_id"]), "all_filtered")
    computable = [r for r in records if r["metrics"]["common_max_error"] is not None]
    if computable:
        add(min(computable, key=lambda r: (-r["metrics"]["common_max_error"], r["record_id"])), "worst_common_error")
    dp_rows = [r for r in records if r["metrics"]["dp_max_error"] is not None and parameters["dp"] > 0]
    if dp_rows:
        add(min(dp_rows, key=lambda r: (abs(r["metrics"]["dp_max_error"] - parameters["dp"]), r["record_id"])), "near_DP_threshold")
    add(min(records, key=lambda r: (-r["metrics"]["n_input"], r["record_id"])), "largest_record")
    if extra_strata:
        for ids in groups.values():
            selected.setdefault(min(ids, key=rank), []).append("descriptive_stratum_representative")
    return selected


def independent_select(candidates, reference_id):
    reference = candidates[reference_id]
    bm = reference["metrics"]
    before = {row["index"]: row["error"] for row in bm["common_point_errors"] if row["error"] is not None}
    assessments = {}
    for cid, row in candidates.items():
        cm = row["metrics"]
        after = {r["index"]: r["error"] for r in cm["common_point_errors"] if r["error"] is not None}
        eps = max(bm["common_floating_allowance"], cm["common_floating_allowance"])
        good = (set(before) <= set(after) and not cm["raw_break_crossings"] and cm["dp_checks_passed"]
                and not cm["n_dp_exceedances"] and not (bm["record_covered"] and not cm["record_covered"])
                and cm["raw_windows_covered"] >= bm["raw_windows_covered"])
        baseline_max = max(before.values(), default=None)
        current_max = max((after[index] for index in before), default=None) if set(before) <= set(after) else None
        cp = all(row["parameters"][k] == reference["parameters"][k] for k in reference["parameters"] if k != "dp")
        if cp:
            p1 = next(s for s in row["stages"] if s["name"] == "P")["input"]
            p2 = next(s for s in reference["stages"] if s["name"] == "P")["input"]
            good = good and p1 == p2 and cm["n_dp_input"] == bm["n_dp_input"] and (cm["dp_max_error"] is None or cm["dp_max_error"] <= 5 + eps)
            gain = cm["n_dp_output"] < bm["n_dp_output"]
        else:
            good = good and (baseline_max is None or current_max is not None and current_max <= baseline_max + eps)
            gain = len(after) > len(before) or current_max is not None and baseline_max is not None and current_max < baseline_max - eps
        assessments[cid] = {"good": good, "gain": good and gain, "cp": cp, "coverage": len(after), "error": current_max, "eps": eps}
    gains = [cid for cid, a in assessments.items() if a["gain"]]
    if not gains:
        return reference_id
    if all(assessments[cid]["cp"] for cid in gains):
        return min(gains, key=lambda cid: (candidates[cid]["metrics"]["n_dp_output"], candidates[cid]["metrics"]["dp_max_error"] or 0,
                                          candidates[cid]["parameters"]["dp"], cid))
    def dominates(first, second):
        a, b = assessments[first], assessments[second]
        if a["cp"] != b["cp"]:
            return False
        if a["error"] is None or b["error"] is None:
            return a["error"] is b["error"] is None and a["coverage"] > b["coverage"]
        eps = max(a["eps"], b["eps"])
        return a["coverage"] >= b["coverage"] and a["error"] <= b["error"] + eps and (a["coverage"] > b["coverage"] or a["error"] < b["error"] - eps)
    frontier = [cid for cid in gains if not any(dominates(other, cid) for other in gains if cid != other)]
    return frontier[0] if len(frontier) == 1 else reference_id


def independent_features(card):
    edges = card["n_points"] - 1
    if edges <= 0 or card["median_positive_dt"] is None:
        return None
    return [math.log1p(card["n_points"]), math.log1p(card["span_work_m"]), math.log1p(card["median_positive_dt"]),
            card["zero_dt_edges"] / edges, card["adjacent_duplicate_edges"] / edges, card["raw_break_edges"] / edges]


def review_memory(audit, run, manifest, split, cards, contract_hash, candidate_by_id):
    from task1.workflow.g2_memory import FrozenMemory
    info = manifest["memory_snapshot"]
    path = run / info["path"]
    before_hash = digest(path)
    audit.check("memory:snapshot_hash", before_hash == info["sha256"])
    snapshot = read_json(path)
    ids = split["splits"]["DEMO_MEMORY"]
    audit.same("memory:exact_ordered_demo_scope", [e["record_id"] for e in snapshot["entries"]], ids)
    audit.check("memory:versions", snapshot["raw_sha256"] == split["raw_sha256"] and snapshot["contract_sha256"] == contract_hash and snapshot["split_sha256"] == object_hash(split))
    audit.check("memory:no_fabricated_human", snapshot["human_knowledge"] == [] and snapshot["working_memory_persisted"] is False and snapshot["evaluation_policy"] == "READ_ONLY")
    vectors = []
    for entry in snapshot["entries"]:
        rid, cid = entry["record_id"], entry["selected_config_id"]
        target = candidate_by_id[cid][rid]
        audit.check("memory:entry_parent", entry["partition"] == "DEMO_MEMORY" and entry["raw_sha256"] == split["raw_sha256"] and entry["contract_sha256"] == contract_hash)
        audit.check("memory:raw_content", entry["record_content_sha256"] == cards[rid]["record_content_sha256"] and entry["stratum"] == cards[rid]["stratum"])
        trace_path, receipt_path = ROOT / entry["trace_path"], ROOT / entry["review_path"]
        audit.check("memory:admission_hashes", digest(trace_path) == entry["trace_sha256"] and digest(receipt_path) == entry["review_sha256"])
        admitted, receipt = read_compressed(trace_path), read_json(receipt_path)
        audit.check("memory:selected_actual_trace", admitted == target and receipt["target_hash"] == object_hash(target) and receipt["status"] == entry["engineering_status"] == "VERIFIED")
        audit.check("memory:admission_metrics", entry["selected_metrics"] == {k: v for k, v in target["metrics"].items() if not isinstance(v, (dict, list))})
        audit.check("memory:parameters", entry["selected_parameters"] == target["parameters"] and entry["candidate_evaluations"] == 20)
        selected = independent_select({key: values[rid] for key, values in candidate_by_id.items()}, config_id(read_json(CFG / "contract.json")["reference_parameters"]))
        audit.check("memory:independent_selection", cid == selected, {"record_id": rid, "actual": cid, "expected": selected})
        feature = independent_features(cards[rid])
        audit.same("memory:features", entry["features"], feature, 1e-14)
        if feature is not None:
            vectors.append(feature)
    scales = [{"min": min(v[i] for v in vectors), "max": max(v[i] for v in vectors)} for i in range(6)]
    audit.same("memory:DEMO_only_scales", snapshot["feature_scales"], scales, 1e-14)
    for parameter, procedure in snapshot["procedural_memory"].items():
        values = sorted({entry["selected_parameters"][parameter] for entry in snapshot["entries"]})
        audit.check("memory:verified_procedures", procedure["values"] == values and procedure["min"] == min(values) and procedure["max"] == max(values))
    memory = FrozenMemory(path, before_hash, contract_hash, split)
    queries = split["splits"]["DEVELOPMENT"] + ids
    retrieval_rows = []
    for rid in queries:
        query = cards[rid]
        vector = independent_features(query)
        eligible = []
        for entry in snapshot["entries"]:
            if entry["record_id"] == rid or entry["record_content_sha256"] == query["record_content_sha256"] or entry["stratum"] != query["stratum"] or vector is None or entry["features"] is None:
                continue
            distance = math.sqrt(sum(((a - b) / (scale["max"] - scale["min"])) ** 2 if scale["max"] != scale["min"] else 0
                                     for a, b, scale in zip(vector, entry["features"], scales)))
            eligible.append((distance, entry["memory_id"]))
        eligible.sort()
        actual = memory.retrieve(query)
        expected_ids = [mid for _, mid in eligible[:3]]
        audit.same("memory:retrieval:" + rid, [e["memory_id"] for e in actual["delivered"]], expected_ids)
        audit.check("memory:eligible_count", actual["eligible_count"] == len(eligible))
        audit.check("memory:self_excluded", all(e["record_id"] != rid and e["record_content_sha256"] != query["record_content_sha256"] for e in actual["delivered"]))
        retrieval_rows.append({"record_id": rid, "partition": "DEMO_MEMORY_SELF_LEAKAGE_TEST" if rid in ids else "DEVELOPMENT",
                               "eligible": len(eligible), "delivered": expected_ids, "empty_reason": actual["empty_reason"]})
    try:
        memory.write({"engineering_test": "read-only rejection must occur before any write"})
    except PermissionError:
        audit.check("memory:write_denied", True)
    else:
        audit.check("memory:write_denied", False)
    memory2 = FrozenMemory(path, before_hash, contract_hash, split)
    audit.check("memory:fresh_context_same_retrieval", memory.retrieve(cards[queries[0]]) == memory2.retrieve(cards[queries[0]]))
    audit.check("memory:before_after_hash", memory.verify_unchanged() == memory2.verify_unchanged() == digest(path) == before_hash)
    return {"snapshot_sha256": before_hash, "demo_entries": len(ids), "retrieval_checks": retrieval_rows,
            "model_consumption": "NOT_CHECKED_UNTIL_REAL_MODE_RUNS", "writes_rejected": True}


def review(kind, run_id, output_name):
    started = time.perf_counter()
    task, partition_name, expected_artifacts, table_name = KINDS[kind]
    output = OUT / output_name
    if output.exists():
        raise ValueError("C_REVIEW_EXISTS_NO_OVERWRITE")
    run = EV / "runs" / run_id
    manifest_path = run / "manifest.json"
    manifest_hash = digest(manifest_path)
    manifest = read_json(manifest_path)
    if manifest["status"] != "REVIEW_PENDING":
        raise ValueError("RUN_NOT_COMPLETE_NO_ACCEPTANCE")
    audit = Audit()
    contract, split = read_json(CFG / "contract.json"), read_json(EV / "data/split_manifest.json")
    matrix, cards = read_json(CFG / "experiment_matrix.json"), read_json(EV / "data/raw_diagnostics.json")
    chash = digest(CFG / "contract.json")
    raw_path = ROOT / contract["raw_path"]
    audit.check("raw:hash", digest(raw_path) == contract["raw_sha256"] == split["raw_sha256"] == manifest["raw_sha256"])
    raw = read_json(raw_path)
    ids = split["splits"][partition_name]
    audit.same("run:scope", manifest["input_ids"], ids)
    audit.check("run:partition", manifest["partition"] == partition_name)
    audit.check("run:conditional_scope", manifest["classification"] == "CURRENT_RUN_CONDITIONAL_ANALYSIS" and manifest["source_crs"] == "UNVERIFIED")
    audit.check("run:contract_split", manifest["contract_sha256"] == chash and manifest["split_sha256"] == digest(EV / "data/split_manifest.json"))
    for path, expected in manifest["source_hashes"].items():
        audit.check("run:source:" + path, digest(ROOT / path) == expected)
    audit.check("run:source_tree", object_hash(manifest["source_hashes"]) == manifest["source_tree_sha256"])
    current_sources = {str(p.relative_to(ROOT)) for p in (ROOT / "task1/workflow").glob("*.py")} | {"task1/scripts/goal2.py"}
    audit.check("run:exact_computation_dependencies", set(manifest["source_hashes"]) == current_sources)
    model = contract["model"]
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} +lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    coords = {rid: [transform.transform(*point, 0)[:2] for point in raw[rid][1]] for rid in ids}
    provenance = {"goal_id": contract["goal_id"], "run_id": run_id, "raw_sha256": split["raw_sha256"], "partition": partition_name,
                  "scope_sha256": object_hash(ids), "source_tree_sha256": manifest["source_tree_sha256"], "contract_sha256": chash,
                  "split_sha256": digest(EV / "data/split_manifest.json"), "adapter_version": model["adapter_version"]}
    entries = list(manifest["artifacts"].values())
    audit.check("run:artifact_count", len(entries) == expected_artifacts)
    if kind == "parameters":
        expected = {(config["config_id"], "S-D-P"): config["parameters"] for config in matrix["parameter_configurations"]}
    elif kind == "orders":
        expected = {(config_id(contract["reference_parameters"]), order): contract["reference_parameters"] for order in contract["orders"]}
    else:
        expected = {(config_id(row["parameters"]), row["order"]): row["parameters"] for row in contract["search"]["sequence"]}
    audit.same("run:complete_configs", sorted([list((entry["config_id"], entry["order"])) for entry in entries]), sorted([list(key) for key in expected]))
    reports, all_summaries, details_by_order, candidate_by_id = [], [], {}, {}
    for number, entry in enumerate(entries):
        tag = entry["config_id"] + "/" + entry["order"]
        parameters = expected[(entry["config_id"], entry["order"])]
        audit.same(tag + ":parameters", entry["parameters"], parameters)
        audit.same(tag + ":input_scope", entry["input_ids"], ids)
        artifact, review_path = run / entry["file"], run / entry["review_file"]
        audit.check(tag + ":artifact_hash", digest(artifact) == entry["sha256"])
        audit.check(tag + ":review_hash", digest(review_path) == entry["review_sha256"])
        batch, receipt = read_compressed(artifact), read_json(review_path)
        audit.check(tag + ":engineering_review", receipt["status"] == entry["engineering_status"] == "VERIFIED" and receipt["target_hash"] == object_hash(batch))
        audit.same(tag + ":batch_scope", batch["record_scope"], ids)
        audit.same(tag + ":record_scope", [row["record_id"] for row in batch["records"]], ids)
        audit.same(tag + ":review_scope", [row["record_id"] for row in receipt["record_receipts"]], ids)
        audit.check(tag + ":batch_input_hash", batch["input_hash"] == object_hash([row["source_record"] for row in batch["records"]]))
        audit.same(tag + ":provenance", batch["provenance"], provenance)
        key = object_hash({"raw": split["raw_sha256"], "scope": ids, "code": manifest["source_tree_sha256"], "contract": chash,
                           "config": parameters, "order": entry["order"]})
        audit.check(tag + ":experiment_key", entry["experiment_key"] == key and manifest["artifacts"].get(key) == entry)
        expected_rows, full_rows = [], {}
        samples = sample_ids(batch["records"], parameters, cards, parameters == contract["reference_parameters"] or kind == "orders")
        sample_reports = []
        for record, record_receipt in zip(batch["records"], receipt["record_receipts"]):
            rid = record["record_id"]
            audit.check(tag + ":record_receipt", record_receipt["status"] == "VERIFIED" and record_receipt["target_hash"] == object_hash(record)
                        and record_receipt["trusted_reference_hash"] == object_hash(record["source_record"]) and record_receipt["contract_hash"] == chash)
            data = record_check(audit, record, raw[rid], parameters, entry["order"], chash, provenance, coords[rid])
            expected_rows.append(data["metrics"])
            full_rows[rid] = data
            if rid in samples:
                result = audit_record(record, raw[rid], parameters, entry["order"], model, chash)
                audit.check(tag + ":Decimal_full_reconstruction:" + rid, result["status"] == "VERIFIED", result["errors"])
                sample_reports.append({"record_id": rid, "reasons": samples[rid], "status": result["status"], "checks": result["checks"],
                                       "errors": result["errors"], "target_sha256": object_hash(record)})
        summary = summary_expected(expected_rows)
        eps = max(data["epsilon"] for data in full_rows.values())
        audit.same(tag + ":independent_aggregation", batch["summary"], summary, eps)
        audit.same(tag + ":manifest_summary", entry["summary"], batch["summary"])
        all_summaries.append({"config_id": entry["config_id"], "order": entry["order"], "independent_summary": summary})
        if kind == "orders":
            details_by_order[entry["order"]] = full_rows
        if kind == "memory":
            candidate_by_id[entry["config_id"]] = {r["record_id"]: r for r in batch["records"]}
        reports.append({"config_id": entry["config_id"], "order": entry["order"], "records_fully_checked": len(ids),
                        "raw_points_per_config": sum(row["n_input"] for row in expected_rows), "sampled_full_DP_reconstructions": sample_reports})
        print(json.dumps({"C_audit": kind, "artifact": number + 1, "of": len(entries), "errors": len(audit.errors)}), flush=True)
    audit.check("run:resource_candidate_count", manifest["candidate_evaluations"] == len(ids) * len(entries))
    audit.check("run:zero_model_calls", manifest["experiment_model_dispatches"] == 0)
    audit.check("run:deterministic_calls", manifest["deterministic_tool_calls"] == 2 * len(entries))
    targets = [manifest_path]
    additional = {}
    if table_name:
        path = run / table_name
        targets.append(path)
        audit.check("table:hash", digest(path) == manifest["tables"][table_name])
        table = read_json(path)
        audit.check("table:complete_scope", len(table) == len(entries) and {row["experiment_key"] for row in table} == set(manifest["artifacts"]))
        if kind == "parameters":
            audit.same("parameter:table_entries", table, entries)
        else:
            safety = {}
            reference = details_by_order["S-D-P"]
            for row in table:
                failures = []
                for rid, target in details_by_order[row["order"]].items():
                    before = reference[rid]
                    unsafe = (target["crossings"] or not set(before["covered"]) <= set(target["covered"])
                              or target["metrics"]["raw_windows_covered"] < before["metrics"]["raw_windows_covered"]
                              or before["metrics"]["record_covered"] and not target["metrics"]["record_covered"])
                    if unsafe:
                        failures.append(rid)
                audit.same("orders:failure_ids:" + row["order"], sorted(r["record_id"] for r in row["safety_failures"]), sorted(failures))
                audit.check("orders:status:" + row["order"], row["research_status"] == ("REJECTED_BY_CONSTRAINT" if failures else "FEASIBLE_FOR_STAGE_EVALUATION"))
                safety[row["order"]] = {"failing_records": failures, "failing_record_count": len(failures), "research_status": row["research_status"]}
            additional["order_safety"] = safety
    else:
        targets.append(run / manifest["memory_snapshot"]["path"])
        additional["memory"] = review_memory(audit, run, manifest, split, cards, chash, candidate_by_id)
    audit.check("run:manifest_unchanged_during_C_review", digest(manifest_path) == manifest_hash)
    result = {"status": "REJECTED" if audit.errors else "VERIFIED", "role_context": "/root/c_contract", "task": task,
              "run_id": run_id, "reviewed_at": now(), "targets": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path)} for path in targets],
              "source_hashes": {path: digest(ROOT / path) for path in task_sources(task)}, "raw_sha256": digest(raw_path),
              "contract_sha256": chash, "split_sha256": digest(EV / "data/split_manifest.json"),
              "checked_components": REQUIRED_COMPONENTS[task] + ["full_artifact_hashes", "full_ledger_and_common_reference", "independent_DP_certificates", "independent_summary", "sampled_Decimal_DP_reconstruction"],
              "unchecked_components": ["source_datum_truth", "ground_truth_quality", "full_exact_recursive_DP_rerun_for_every_record_configuration", "real_model_consumption", "heldout_G2_EVAL", "final_Goal2_acceptance"],
              "audit_program": {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))},
              "oracle_sha256": digest(OUT / "independent_numeric.py"), "sampling_rule": SAMPLE_RULE,
              "check_count": audit.check_count, "errors": audit.errors, "artifact_count": len(entries), "record_configurations": len(entries) * len(ids),
              "sampled_DP_record_configurations": sum(len(r["sampled_full_DP_reconstructions"]) for r in reports),
              "artifact_reviews": reports, "independent_summaries": all_summaries, **additional,
              "elapsed_seconds": time.perf_counter() - started, "new_model_calls": 0}
    write_json(output, result, exclusive=True)
    print(json.dumps({key: result[key] for key in ("status", "run_id", "check_count", "artifact_count", "record_configurations", "sampled_DP_record_configurations", "elapsed_seconds")}), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=KINDS)
    parser.add_argument("run_id")
    parser.add_argument("output_name")
    args = parser.parse_args()
    value = review(args.kind, args.run_id, args.output_name)
    raise SystemExit(0 if value["status"] == "VERIFIED" else 1)
