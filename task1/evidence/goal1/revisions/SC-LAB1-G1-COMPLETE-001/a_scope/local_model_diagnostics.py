"""Fixed-model scale diagnosis only: no segmentation, deletion or DP execution."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

import pyproj
from pyproj import Geod, Transformer

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
RAW_PATH = "task1/作业/作业/traj_dict.json"
IDS = ["0", "1", "2", "246", "256", "306", "352"]
A = 6378137.0
RF = 298.257223563
LON0 = 121.343555
LAT0 = 31.3561015
raw_bytes = (ROOT / RAW_PATH).read_bytes()
raw_hash = hashlib.sha256(raw_bytes).hexdigest()
assert raw_hash == "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3"
raw = json.loads(raw_bytes)
coordinates = [point for rid in IDS for point in raw[rid][1]]
bbox = {
    "lon_min": min(p[0] for p in coordinates),
    "lon_max": max(p[0] for p in coordinates),
    "lat_min": min(p[1] for p in coordinates),
    "lat_max": max(p[1] for p in coordinates),
}
assert (bbox["lon_min"] + bbox["lon_max"]) / 2 == LON0
assert (bbox["lat_min"] + bbox["lat_max"]) / 2 == LAT0
pipeline = (f"+proj=pipeline +step +proj=cart +a={A} +rf={RF} "
            f"+step +proj=topocentric +a={A} +rf={RF} "
            f"+lon_0={LON0} +lat_0={LAT0} +h_0=0")
transformer = Transformer.from_pipeline(pipeline)
geod = Geod(a=A, rf=RF)
points = []
edges = []
record_summary = []
dt_equal_30 = []
for rid in IDS:
    times, coords = raw[rid]
    enu = [transformer.transform(*point, 0) for point in coords]
    points.extend({"record_id": rid, "index": i, "enu": point}
                  for i, point in enumerate(enu))
    record_edges = []
    for i in range(len(coords) - 1):
        model_d = math.hypot(enu[i+1][0] - enu[i][0], enu[i+1][1] - enu[i][1])
        geographic_d = geod.inv(*coords[i], *coords[i+1])[2]
        dt = times[i+1] - times[i]
        row = {
            "record_id": rid, "left_index": i, "right_index": i+1,
            "dt_source_seconds": dt,
            "enu_model_distance_m": model_d,
            "same_ellipsoid_geodesic_m": geographic_d,
            "enu_minus_geodesic_m": model_d - geographic_d,
            "relative_difference": None if geographic_d == 0 else (model_d-geographic_d)/geographic_d,
            "margin_to_400_model_m": abs(model_d - 400),
            "distance_only_threshold_disagreement": (model_d > 400) != (geographic_d > 400),
            "combined_time_space_threshold_disagreement": ((dt > 30) or (model_d > 400)) != ((dt > 30) or (geographic_d > 400)),
        }
        if dt == 30:
            dt_equal_30.append({"record_id": rid, "left_index": i, "right_index": i+1})
        edges.append(row)
        record_edges.append(row)
    record_summary.append({
        "record_id": rid, "points": len(coords),
        "raw_bbox": {"lon_min": min(p[0] for p in coords), "lon_max": max(p[0] for p in coords),
                     "lat_min": min(p[1] for p in coords), "lat_max": max(p[1] for p in coords)},
        "raw_neighbor_edges": len(record_edges),
        "zero_displacement_edges": sum(e["same_ellipsoid_geodesic_m"] == 0 for e in record_edges),
        "zero_dt_edges": sum(e["dt_source_seconds"] == 0 for e in record_edges),
        "dt_over_30_edges": sum(e["dt_source_seconds"] > 30 for e in record_edges),
    })

phi0 = math.radians(LAT0)
corner_normal_cosines = []
for lon in [bbox["lon_min"], bbox["lon_max"]]:
    for lat in [bbox["lat_min"], bbox["lat_max"]]:
        phi = math.radians(lat)
        value = math.sin(phi0)*math.sin(phi) + math.cos(phi0)*math.cos(phi)*math.cos(math.radians(lon-LON0))
        corner_normal_cosines.append({"lon": lon, "lat": lat, "normal_dot_origin_normal": value})
min_cos = min(item["normal_dot_origin_normal"] for item in corner_normal_cosines)
nonzero = [edge for edge in edges if edge["same_ellipsoid_geodesic_m"] > 0]
assert len(points) == 783 and len(edges) == 776
assert all(math.isfinite(value) for point in points for value in point["enu"])
result = {
    "classification": "CURRENT_RAW_PILOT_CONDITIONAL_GEOMETRY_DIAGNOSIS_ONLY",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "not_a_processing_result": True,
    "source_crs": "UNVERIFIED",
    "raw_path": RAW_PATH,
    "raw_sha256": raw_hash,
    "model_selection_basis": "Main controller fixed ECEF-to-ENU using raw pilot extent before cleaning scores; this diagnostic does not compare or select methods.",
    "model": {"a_m": A, "inverse_flattening": RF, "height_m": 0,
              "center_lon_degrees": LON0, "center_lat_degrees": LAT0,
              "working_axes": ["E", "N"], "units": "conditional_model_meters", "epsg": None,
              "pipeline_for_independent_calculation": pipeline},
    "software": {"python": sys.version.split()[0], "pyproj": pyproj.__version__, "PROJ": pyproj.proj_version_str,
                 "installation_note": "Existing shared .venv; main controller manages any installation log. A installed nothing."},
    "raw_bbox": bbox,
    "points": len(points),
    "per_record": record_summary,
    "working_extent": {
        "E_range_m": [min(p["enu"][0] for p in points), max(p["enu"][0] for p in points)],
        "N_range_m": [min(p["enu"][1] for p in points), max(p["enu"][1] for p in points)],
        "U_range_m": [min(p["enu"][2] for p in points), max(p["enu"][2] for p in points)],
        "maximum_horizontal_radius_m": max(math.hypot(p["enu"][0], p["enu"][1]) for p in points),
        "maximum_same_ellipsoid_geodesic_radius_m": max(geod.inv(LON0, LAT0, *point)[2] for point in coordinates),
    },
    "local_differential_scale": {
        "corner_normal_cosines": corner_normal_cosines,
        "maximum_normal_tilt_degrees": math.degrees(math.acos(min_cos)),
        "minimum_singular_value": min_cos,
        "maximum_singular_value": 1.0,
        "maximum_local_length_shrink_fraction": 1-min_cos,
        "scope": "Orthogonal projection of each mathematical ellipsoid tangent plane onto the origin EN plane has singular values 1 and abs(n dot n0). In this small symmetric lon/lat rectangle the smallest dot product is at a corner. This is a local differential bound, not a theorem bounding finite DP chord-to-point error or unknown source-datum error.",
    },
    "raw_edge_comparison": {
        "edges": len(edges), "nonzero_edges": len(nonzero), "zero_edges": len(edges)-len(nonzero),
        "maximum_absolute_difference_m": max(abs(e["enu_minus_geodesic_m"]) for e in edges),
        "maximum_relative_difference": max(abs(e["relative_difference"]) for e in nonzero),
        "maximum_absolute_difference_edge": max(edges, key=lambda e: abs(e["enu_minus_geodesic_m"])),
        "nearest_400_edges": sorted(edges, key=lambda e: e["margin_to_400_model_m"])[:5],
        "distance_threshold_disagreements": sum(e["distance_only_threshold_disagreement"] for e in edges),
        "combined_threshold_disagreements": sum(e["combined_time_space_threshold_disagreement"] for e in edges),
        "smallest_nonzero_edge": min(nonzero, key=lambda e: e["same_ellipsoid_geodesic_m"]),
        "dt_equals_30_edges": dt_equal_30,
        "scope": "All original in-record neighbor edges before any segmentation or removal; post-removal neighbor edges and DP chords are not covered by this aggregate.",
    },
    "unexecuted_checks": ["65m actual post-split segment length sensitivity", "35 degree actual pre-denoise window sensitivity", "5m actual clean-to-final interval DP residual sensitivity", "actual baseline independent audit"],
    "claim_limits": ["No datum identification or offset conversion", "No absolute positioning/road matching/ground truth error", "The U coordinate reflects curvature under h=0, not measured terrain elevation", "Model agreement does not bound all unknown source errors", "No segmentation/deletion/DP processing took place in this diagnostic"],
}
path = OUT / "local_model_diagnostics.json"
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"path": str(path.relative_to(ROOT)), "pilot_points": len(points), "raw_edges": len(edges),
                  "maximum_horizontal_radius_m": result["working_extent"]["maximum_horizontal_radius_m"],
                  "maximum_raw_edge_difference_m": result["raw_edge_comparison"]["maximum_absolute_difference_m"],
                  "threshold_400_disagreements": result["raw_edge_comparison"]["distance_threshold_disagreements"],
                  "source_crs": "UNVERIFIED"}, ensure_ascii=False))
