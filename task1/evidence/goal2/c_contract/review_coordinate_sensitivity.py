"""Independent C verification of existing coordinate diagnostics, no production math imports.

All 307 selected records are rebuilt from raw angular values using PROJ/Geod.
Binary64 ENU values come from already independently reviewed actual traces.
The four registered runs are inspected completely on their actual stage inputs.
No alternate cleaning chain, model request, parameter selection or memory write.
"""
from collections import Counter, defaultdict
import gzip
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pyproj

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, write_json, digest, object_hash, now
from review_development_runs import Audit, read_compressed, finite, config_id
from independent_numeric import directions, allowance

OUT = Path(__file__).resolve().parent
EV = ROOT / "task1/evidence/goal2"


def bound(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}


def dist_stats(values, empty_reason="EMPTY_DENOMINATOR"):
    x = np.asarray(values, dtype=float)
    if len(x) == 0:
        return {"count": 0, **{k: None for k in ("min", "mean", "q50", "q90", "q95", "q99", "max")}, "reason": empty_reason}
    q = np.quantile(x, [0, .5, .9, .95, .99, 1], method="linear")
    return {"count": len(x), "min": float(q[0]), "mean": float(np.mean(x)), "q50": float(q[1]),
            "q90": float(q[2]), "q95": float(q[3]), "q99": float(q[4]), "max": float(q[5]), "reason": None}


def alternate_dp(xy, ids, threshold):
    # Recursive earliest-maximum split, independent of the target's iterative implementation.
    if len(ids) < 3 or threshold == 0:
        return list(ids)
    errors = [finite(xy[i], xy[ids[0]], xy[ids[-1]]) for i in ids[1:-1]]
    maximum = max(errors)
    if maximum <= threshold:
        return [ids[0], ids[-1]]
    mid = errors.index(maximum) + 1
    return alternate_dp(xy, ids[:mid + 1], threshold)[:-1] + alternate_dp(xy, ids[mid:], threshold)


def main():
    started = time.perf_counter()
    audit = Audit()
    contract_path = ROOT / "task1/config/goal2/contract.json"
    split_path = EV / "data/split_manifest.json"
    contract, split = read_json(contract_path), read_json(split_path)
    raw_path = ROOT / contract["raw_path"]
    raw = read_json(raw_path)
    audit.check("trusted_raw_hash", digest(raw_path) == contract["raw_sha256"] == split["raw_sha256"])
    ids = [rid for part in ("PILOT_REGRESSION", "DEMO_MEMORY", "DEVELOPMENT", "G2_EVAL") for rid in split["splits"][part]]
    audit.check("307_unique_nonreserved", len(ids) == len(set(ids)) == 307 and not set(ids).intersection(split["splits"]["G3_RESERVED"]))
    directories = [EV / "coordinate_sensitivity" / name for name in ("raw_preflight", "development-02")]
    summaries = [read_json(d / "summary.json") for d in directories]
    targets = [contract_path, split_path, ROOT / "task1/scripts/goal2_coordinate_sensitivity.py"]
    for directory, summary in zip(directories, summaries):
        targets.append(directory / "summary.json")
        audit.check("diagnostic_versions", summary["raw_sha256"] == contract["raw_sha256"] and summary["contract_sha256"] == digest(contract_path)
                    and summary["split_sha256"] == digest(split_path) and summary["source_sha256"] == digest(targets[2]))
        audit.check("no_geodetic_claim", summary["source_crs"] == "UNVERIFIED" and summary["source_datum_proven"] is False)
        audit.check("diagnostics_only", summary["new_candidate_evaluations"] == summary["new_model_calls"] == summary["memory_writes"] == 0)
        audit.check("scope_binding", summary["selected_record_count"] == len(ids) and summary["raw_scope_hash"] == object_hash({rid: raw[rid] for rid in ids}))
        for entry in summary["artifacts"].values():
            p = directory / entry["path"]
            targets.append(p)
            audit.check("diagnostic_artifact_hash", digest(p) == entry["sha256"])
        with gzip.open(directory / "all_threshold_differences.jsonl.gz", "rt") as stream:
            audit.check("registered_difference_file_empty", list(stream) == [])
    audit.check("preflight_does_not_claim_stage_runs", summaries[0]["runs"] == [])
    audit.check("same_coordinate_scope_bytes", digest(directories[0] / "coordinate_checks.json") == digest(directories[1] / "coordinate_checks.json"))
    actual_sources = {}
    pilot = read_json(EV / "counterexamples/formal-02/exposed_pilot_cases.json")
    for rid in split["splits"]["PILOT_REGRESSION"]:
        actual_sources[rid] = pilot["executions"][rid]["output"]["source_record"]
    for run in ("g2-demo-memory-02", "g2-development-parameters-02", "g2-evaluation-parameters-01"):
        d = EV / "runs" / run
        manifest = read_json(d / "manifest.json")
        entry = next(iter(manifest["artifacts"].values()))
        audit.check("source_trace_hash", digest(d / entry["file"]) == entry["sha256"])
        for row in read_compressed(d / entry["file"])["records"]:
            actual_sources[row["record_id"]] = row["source_record"]
    audit.check("complete_coordinate_input", set(actual_sources) == set(ids))
    model = contract["model"]
    a, rf, lon0, lat0 = [model[k] for k in ("semi_major_m", "inverse_flattening", "origin_lon_degrees", "origin_lat_degrees")]
    proj = pyproj.Transformer.from_pipeline(f"+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=cart +a={a} +rf={rf} +step +proj=topocentric +a={a} +rf={rf} +lon_0={lon0} +lat_0={lat0} +h_0=0")
    geod = pyproj.Geod(a=a, rf=rf)
    aeqd = pyproj.Proj(proj="aeqd", a=a, rf=rf, lon_0=lon0, lat_0=lat0, units="m")
    report = read_json(directories[1] / "coordinate_checks.json")
    audit.same("ordered_scope", report["record_ids"], ids)
    global_values = defaultdict(list)
    coordinate_context, edge_rows, pair_total, zero_total = {}, [], 0, 0
    for rid, expected in zip(ids, report["per_record"]):
        times, angular = raw[rid]
        xy = actual_sources[rid]["xy"]
        audit.check("raw_alignment", actual_sources[rid]["indices"] == list(range(len(times))) and actual_sources[rid]["timestamps"] == times)
        independent = [proj.transform(*p, 0)[:2] for p in angular]
        alternate = [aeqd(*p) for p in angular]
        n = len(times)
        ii, jj = np.triu_indices(n, 1)
        ang, enu = np.asarray(angular), np.asarray(xy)
        en = np.hypot(enu[jj, 0] - enu[ii, 0], enu[jj, 1] - enu[ii, 1])
        gd = np.asarray(geod.inv(ang[ii, 0], ang[ii, 1], ang[jj, 0], ang[jj, 1])[2])
        positive = gd > 0
        values = {"coordinate_error_m": [math.dist(p, q) for p, q in zip(xy, independent)],
                  "aeqd_coordinate_offset_m": [math.dist(p, q) for p, q in zip(xy, alternate)],
                  "pair_enu_distance_m": en, "pair_geod_distance_m": gd,
                  "pair_absolute_difference_m": abs(en - gd), "pair_relative_difference": abs(en[positive] - gd[positive]) / gd[positive]}
        audit.check("PROJ_allpoints", max(values["coordinate_error_m"], default=0) <= 1e-6)
        audit.check("fixed_domain_guard", max((math.hypot(*p) for p in xy), default=0) <= model["domain_max_radius_m"])
        audit.check("record_denominators", expected["record_id"] == rid and expected["point_count"] == n and expected["pair_count"] == n * (n - 1) // 2 and expected["raw_edge_count"] == n - 1)
        audit.same("radius", expected["max_enu_radius_m"], max((math.hypot(*p) for p in xy), default=0), 1e-8)
        for key, array in values.items():
            audit.same(rid + ":" + key, expected[key], dist_stats(array, "NO_POSITIVE_GEOD_DISTANCES" if key == "pair_relative_difference" else "EMPTY_DENOMINATOR"), 1e-8)
            global_values[key].extend(array)
        for i in range(n - 1):
            u, v, w = math.dist(xy[i], xy[i + 1]), geod.inv(*angular[i], *angular[i + 1])[2], math.dist(alternate[i], alternate[i + 1])
            diffs = [t for t in contract["parameter_grids"]["distance"] if len({u > t, v > t, w > t}) > 1]
            edge_rows.append({"record_id": rid, "left_index": i, "right_index": i + 1, "enu_m": u, "geod_m": v, "aeqd_m": w,
                              "absolute_difference_m": abs(u - v), "relative_difference": abs(u - v) / v if v else None,
                              "relative_reason": None if v else "ZERO_GEOD_REFERENCE", "threshold_differences": diffs})
        pair_total += len(en)
        zero_total += int((~positive).sum())
        coordinate_context[rid] = {"enu": xy, "alternate": alternate, "angular": angular, "times": times}
    for key, values in global_values.items():
        audit.same("aggregate:" + key, report[key], dist_stats(values), 1e-8)
    for key, field in (("raw_edge_enu_distance_m", "enu_m"), ("raw_edge_geod_distance_m", "geod_m"), ("raw_edge_absolute_difference_m", "absolute_difference_m")):
        audit.same(key, report[key], dist_stats([r[field] for r in edge_rows]), 1e-8)
    audit.check("pair_denominators", pair_total == report["within_record_pairs_checked"] == 1594527 and zero_total == report["zero_geod_pair_denominator"] == 55362)
    audit.check("zero_reference_null", report["zero_geod_pair_relative_value"] is None and report["zero_geod_pair_reason"] == "ZERO_GEOD_REFERENCE")
    with gzip.open(directories[1] / "raw_edges.jsonl.gz", "rt") as stream:
        actual_edges = [json.loads(line) for line in stream]
    audit.same("all_raw_edges", actual_edges, edge_rows, 1e-8)
    audit.check("all_raw_distance_grid_decisions", all(not x["threshold_differences"] for x in edge_rows))
    print("C coordinate/raw-edge reconstruction completed", audit.check_count, flush=True)
    run_results = []
    for reported in summaries[1]["runs"]:
        d = EV / "runs" / reported["run_id"]
        manifest_path = d / "manifest.json"
        manifest = read_json(manifest_path)
        audit.check("sensitivity_run_hash", digest(manifest_path) == reported["manifest_sha256"])
        audit.check("run_source_epoch", reported["run_source_tree_sha256"] == object_hash(manifest["source_hashes"]))
        for name, sha in manifest["source_hashes"].items():
            audit.check("current_processing_source", digest(ROOT / name) == sha)
        counts, thresholds, maxima = Counter(), defaultdict(set), {}
        scope, traces = set(), 0

        def consume(row):
            nonlocal traces
            rid, p = row["record_id"], row["parameters"]
            traces += 1; scope.add(rid)
            context = coordinate_context[rid]
            en, ae, ll, ts = [context[k] for k in ("enu", "alternate", "angular", "times")]
            audit.check("trace_actual_input", row["source_record"] == actual_sources[rid] and rid in manifest["input_ids"])
            for key in ("distance", "min_length", "direction", "dp"):
                thresholds[key].add(p[key])
            def extreme(key, value):
                maxima[key] = max(maxima.get(key, -1), value)
            for stage in row["stages"]:
                for number, (seg, op) in enumerate(zip(stage["input"], stage["operations"])):
                    indices = seg["indices"]
                    audit.check("stage_parent", object_hash(seg) == op["parent_hash"])
                    if stage["name"] == "S":
                        for i, j in zip(indices, indices[1:]):
                            u, v, w = math.dist(en[i], en[j]), math.dist(ae[i], ae[j]), geod.inv(*ll[i], *ll[j])[2]
                            counts["S_distance_edges"] += 1
                            audit.check("S_distance_model_decision", len({u > p["distance"], v > p["distance"], w > p["distance"]}) == 1)
                            extreme("S_max_abs_aeqd_distance_change_m", abs(v - u)); extreme("S_max_abs_geod_distance_change_m", abs(w - u))
                        for part in op["segments"]:
                            q = part["indices"]
                            u, v = [math.fsum(math.dist(points[i], points[j]) for i, j in zip(q, q[1:])) for points in (en, ae)]
                            w = math.fsum(geod.inv(*ll[i], *ll[j])[2] for i, j in zip(q, q[1:]))
                            counts["S_actual_segments_length"] += 1
                            audit.check("S_length_model_decision", len({u < p["min_length"], v < p["min_length"], w < p["min_length"]}) == 1)
                            extreme("S_max_abs_geod_length_change_m", abs(w - u))
                    elif stage["name"] == "D":
                        den, dae = directions(en, indices, p["direction"]), directions(ae, indices, p["direction"])
                        for u, v, actual in zip(den, dae, op["decisions"]):
                            counts["D_windows"] += 1; counts["D_undefined_windows"] += u["reason"] is not None
                            audit.check("D_model_decision", u["candidate"] == v["candidate"] == actual["candidate"] and u["reason"] == v["reason"] == actual["reason"])
                            if u["deltas"] is not None and v["deltas"] is not None:
                                extreme("D_max_abs_aeqd_angle_change_degrees", max(abs(x - y) for x, y in zip(u["deltas"], v["deltas"])))
                    else:
                        kept = stage["output"][number]["indices"]
                        counts["P_segments"] += 1; counts["P_complete_input_points"] += len(indices); counts["P_immediate_output_points"] += len(kept)
                        audit.check("P_alternate_index_set", alternate_dp(ae, indices, p["dp"]) == kept)
                        errors = {i: (0.0, 0.0) for i in kept}
                        for first, last in zip(kept, kept[1:]):
                            for i in indices:
                                if first < i < last:
                                    errors[i] = (finite(en[i], en[first], en[last]), finite(ae[i], ae[first], ae[last]))
                        audit.check("P_complete_reference", set(errors) == set(indices))
                        epen, epae = allowance([en[i] for i in indices], p["dp"]), allowance([ae[i] for i in indices], p["dp"])
                        for u, v in errors.values():
                            audit.check("P_fixed_output_model_decision", u <= p["dp"] + epen and (u > p["dp"]) == (v > p["dp"]) and (u > p["dp"] + epen) == (v > p["dp"] + epae))
                            extreme("P_max_aeqd_error_of_actual_output_m", v); extreme("P_max_abs_aeqd_error_change_m", abs(v - u))
        for binding in reported["artifact_bindings"]:
            if "file" in binding:
                path = d / binding["file"]
                audit.check("batch_binding", digest(path) == binding["sha256"])
                batch = read_compressed(path)
                audit.same("binding_scope", batch["record_scope"], binding["input_ids"])
                for row in batch["records"]:
                    audit.check("config_binding", config_id(row["parameters"]) == binding["config_id"] and row["order"] == binding["order"])
                    consume(row)
            else:
                path = d / binding["trace_file"]
                audit.check("mode_trace_binding", digest(path) == binding["trace_sha256"])
                payload = read_compressed(path)
                audit.check("candidate_ids", set(payload["results"]) == set(binding["candidate_ids"]))
                for cid, row in payload["results"].items():
                    audit.check("mode_config", config_id(row["parameters"]) == cid)
                    consume(row)
        audit.same("trace_count", reported["actual_traces_checked"], traces)
        audit.same("full_stage_denominators", reported["stage_check_counts"], dict(counts))
        audit.same("thresholds", reported["actual_threshold_values"], {k: sorted(v) for k, v in thresholds.items()})
        audit.same("actual_scope", reported["actual_trace_record_ids"], sorted(scope))
        audit.same("explicit_unchecked_scope", reported["unchecked_record_ids"], sorted(set(manifest["input_ids"]) - scope))
        for key, value in maxima.items():
            audit.same("extreme:" + key, reported["measured_extrema"][key]["value"], value, 1e-8)
        audit.check("reported_no_differences", reported["sensitivity_difference_counts"] == {})
        run_results.append({"run_id": reported["run_id"], "manifest": bound(manifest_path), "traces": traces, "independent_stage_counts": dict(counts), "independent_extrema": maxima})
        print("C full sensitivity", reported["run_id"], traces, "errors", len(audit.errors), flush=True)
    receipt = {"status": "VERIFIED" if not audit.errors else "REJECTED", "role_context": "/root/c_contract", "task": None, "at": now(),
               "classification": "INDEPENDENT_C_COORDINATE_AND_ACTUAL_TRACE_SENSITIVITY_REVIEW", "targets": [bound(p) for p in targets],
               "checked_components": ["trusted_raw_selected_scope", "all307_PROJ_coordinates", "all1594527_Geod_pairs", "all30685_raw_edges_grid_thresholds", "all10218_actual_trace_stage_sensitivity", "stage_denominators_and_extrema", "conditional_model_claims"],
               "unchecked_components": ["source_datum", "ground_truth_location_accuracy", "G3_RESERVED_processing", "evaluation_stage_sensitivity_runs_not_listed_in_reviewed_report", "full_goal_acceptance"],
               "records": 307, "points": 30992, "pair_denominator": pair_total, "zero_geod_pair_denominator": zero_total, "runs": run_results,
               "check_count": audit.check_count, "errors": audit.errors, "new_model_calls": 0, "new_processing_experiments": 0, "memory_writes": 0,
               "interpretation": "PROJ agreement verifies the fixed ENU formula. Geod/AEQD differences quantify that conditional model's approximation. No observed threshold difference within these exact inputs establishes neither a source datum nor accuracy outside this scope.",
               "elapsed_seconds": time.perf_counter() - started, "audit_program": bound(Path(__file__)), "numeric_oracle": bound(OUT / "independent_numeric.py"), "C_program_correction": {"prior_receipt": bound(OUT / "coordinate_sensitivity_receipt.json"), "fact": "One selected record has no positive Geod pairs. Target correctly records NO_POSITIVE_GEOD_DISTANCES; the first C implementation used generic EMPTY_DENOMINATOR. C now verifies the specific reason; all numerical and stage checks passed before this C-only correction."}}
    write_json(OUT / "coordinate_sensitivity_receipt_v2.json", receipt, exclusive=True)
    print({k: receipt[k] for k in ("status", "check_count", "errors", "elapsed_seconds")})
    return receipt


if __name__ == "__main__":
    result = main()
    raise SystemExit(result["status"] != "VERIFIED")
