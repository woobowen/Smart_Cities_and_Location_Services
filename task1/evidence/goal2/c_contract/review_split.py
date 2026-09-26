"""Independently recompute raw descriptive strata and exact record allocations."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

import pyproj

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = "task1/作业/作业/traj_dict.json"
SPLIT = "task1/evidence/goal2/data/split_manifest.json"
DIAGNOSTICS = "task1/evidence/goal2/data/raw_diagnostics.json"
PILOT = ["0", "1", "2", "246", "256", "306", "352"]


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def object_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def quantile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    left, right = math.floor(position), math.ceil(position)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


def ranking(identifier, purpose):
    return hashlib.sha256(f"42|{purpose}|{identifier}".encode()).hexdigest()


def select(pool, size, strata, purpose):
    buckets = defaultdict(list)
    for identifier in pool:
        buckets[strata[identifier]].append(identifier)
    names = sorted(buckets)
    for name in names:
        buckets[name] = sorted(buckets[name], key=lambda identifier: (ranking(identifier, purpose), identifier))
    quotas = {name: size // len(names) + int(index < size % len(names)) for index, name in enumerate(names)}
    result, shortfalls = [], {}
    for name in names:
        allocated = min(quotas[name], len(buckets[name]))
        result.extend(buckets[name][:allocated])
        buckets[name] = buckets[name][allocated:]
        if allocated < quotas[name]:
            shortfalls[name] = quotas[name] - allocated
    while len(result) < size:
        for name in names:
            if buckets[name]:
                result.append(buckets[name].pop(0))
            if len(result) == size:
                break
    return result, {"nominal_quota": quotas, "shortfalls": shortfalls, "realized": dict(Counter(strata[r] for r in result))}


def main():
    start = time.perf_counter()
    raw, manifest, cards = read(RAW), read(SPLIT), read(DIAGNOSTICS)
    contract = read("task1/config/goal2/contract.json")
    checks, errors = [], []
    def check(name, condition, detail=None):
        checks.append(name)
        if not condition:
            errors.append({"check": name, "detail": detail})
    check("raw_hash", sha(RAW) == contract["raw_sha256"] == manifest["raw_sha256"])
    check("diagnostics_hash", sha(DIAGNOSTICS) == manifest["diagnostics_sha256"])
    check("split_source_hash", sha("task1/workflow/g2_data.py") == manifest["source_sha256"])
    check("exact_raw_counts", len(raw) == 11386 and sum(len(value[0]) for value in raw.values()) == 1173410)
    check("exact_diagnostic_scope", set(cards) == set(raw))
    model = contract["model"]
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    independent, groups = {}, defaultdict(list)
    maximum_descriptor_difference = 0.0
    for identifier, (times, coordinates) in raw.items():
        east, north, _ = transform.transform(*zip(*coordinates), [0] * len(coordinates))
        xy = list(zip(east, north))
        span = math.hypot(max(east) - min(east), max(north) - min(north))
        dt = [right - left for left, right in zip(times, times[1:])]
        distances = [math.dist(a, b) for a, b in zip(xy, xy[1:])]
        duplicate = sum(a == b for a, b in zip(coordinates, coordinates[1:]))
        values = {"n_points": len(times), "zero_dt_edges": dt.count(0), "negative_dt_edges": sum(v < 0 for v in dt),
                  "dt_over_30_edges": sum(v > 30 for v in dt), "distance_over_400_edges": sum(v > 400 for v in distances),
                  "adjacent_duplicate_edges": duplicate, "direction_unavailable_edges": distances.count(0),
                  "speed_unavailable_edges": sum(v <= 0 for v in dt), "time_flag": any(v <= 0 or v > 30 for v in dt),
                  "duplicate_flag": bool(duplicate), "record_content_sha256": object_sha(raw[identifier])}
        check(identifier + ":raw_descriptors", all(cards[identifier][name] == value for name, value in values.items()))
        for name, expected in (("span_work_m", span), ("path_length_work_m", math.fsum(distances)),
                               ("max_radius_work_m", max(math.hypot(e, n) for e, n in xy)),
                               ("duration_seconds", times[-1] - times[0])):
            difference = abs(cards[identifier][name] - expected)
            maximum_descriptor_difference = max(maximum_descriptor_difference, difference)
            check(identifier + ":" + name, difference <= 1e-6, difference if difference > 1e-6 else None)
        independent[identifier] = {"span": span, "time": values["time_flag"], "dup": values["duplicate_flag"]}
        groups[values["record_content_sha256"]].append(identifier)
    duplicates = [ids for ids in groups.values() if len(ids) > 1]
    check("exact_record_grouping", not duplicates, duplicates)
    quantiles = [quantile([value["span"] for value in independent.values()], q) for q in (1 / 3, 2 / 3)]
    check("tertile_values", all(abs(a - b) <= 1e-6 for a, b in zip(quantiles, manifest["quantiles"])))
    strata = {}
    for identifier, value in independent.items():
        level = "LOW" if value["span"] <= quantiles[0] else "MID" if value["span"] <= quantiles[1] else "HIGH"
        strata[identifier] = f'{level}_T{int(value["time"])}_D{int(value["dup"])}'
        check(identifier + ":stratum", strata[identifier] == cards[identifier]["stratum"])
    check("population_strata", dict(Counter(strata.values())) == manifest["population_strata"])
    expected_splits = {"PILOT_REGRESSION": PILOT}
    remaining = set(raw) - set(PILOT)
    for name, count in (("DEMO_MEMORY", 60), ("DEVELOPMENT", 120), ("G2_EVAL", 120)):
        selected, allocation = select(remaining, count, strata, name)
        expected_splits[name] = selected
        check(name + ":stable_selection", selected == manifest["splits"][name])
        check(name + ":quota_shortfall_accounting", allocation == manifest["allocation"][name])
        remaining -= set(selected)
    expected_splits["G3_RESERVED"] = sorted(remaining, key=lambda identifier: (ranking(identifier, "reserved"), identifier))
    check("reserved_exact", expected_splits["G3_RESERVED"] == manifest["splits"]["G3_RESERVED"])
    check("complete_all_record_partition", Counter(identifier for ids in manifest["splits"].values() for identifier in ids) == Counter(raw.keys()))
    check("pilot_exact", manifest["splits"]["PILOT_REGRESSION"] == PILOT)
    for name in ("DEVELOPMENT", "G2_EVAL"):
        selected, allocation = select(expected_splits[name], 24, strata, name + "_LLM")
        check(name + ":LLM_stable_subset", selected == manifest["llm_subsets"][name])
        check(name + ":LLM_allocation", allocation == manifest["allocation"][name + "_LLM"])
    check("no_false_population_or_datum_claim", manifest["source_crs"] == "UNVERIFIED"
          and "not population" in manifest["sample_weighting"])
    target_paths = [SPLIT, DIAGNOSTICS]
    receipt = {"role_context": "/root/c_contract", "status": "REJECTED" if errors else "VERIFIED",
               "at_utc": datetime.now(timezone.utc).isoformat(), "classification": "INDEPENDENT_C_RAW_SPLIT_RECOMPUTATION",
               "targets": [{"path": path, "sha256": sha(path)} for path in target_paths],
               "source_hashes": {path: sha(path) for path in ("task1/workflow/g2_data.py", "task1/config/goal2/contract.json")},
               "checked_components": ["raw_hash", "exact_scope", "record_isolation", "strata_recomputation", "stable_selection",
                                      "reserved_protection", "complete_full_raw_descriptors", "all_quota_shortfalls", "exact_LLM_subsets"],
               "unchecked_components": ["future_actual_G3_use", "external_higher_entity_identity", "source_datum_truth",
                                        "candidate_processing", "expanded_domain_threshold_sensitivity"],
               "check_count": len(checks), "errors": errors, "raw_records": len(raw), "raw_points": 1173410,
               "partition_sizes": {name: len(ids) for name, ids in manifest["splits"].items()},
               "llm_sizes": {name: len(ids) for name, ids in manifest["llm_subsets"].items()},
               "independent_quantiles": quantiles, "maximum_descriptor_difference_m": maximum_descriptor_difference,
               "shortfalls": {name: allocation["shortfalls"] for name, allocation in manifest["allocation"].items()},
               "sampling_claim": "Descriptive stratified record sample; not population means or labeled movement classes",
               "new_model_calls": 0, "elapsed_s": time.perf_counter() - start}
    (OUT / "split_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "check_count", "partition_sizes", "llm_sizes", "errors", "elapsed_s")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
