"""All-point formula check and actual-edge/stage sensitivity without all pairs."""
import argparse
from collections import Counter
import gzip
import json
import math
from pathlib import Path
import time

import numpy as np
import pyproj

from task1.workflow.g2_data import raw_data, adapt
from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json, now
from task1.scripts.goal2_coordinate_sensitivity import inspect_trace
from .data import CFG
from .runtime import read_rows, assert_binding


def check_run(directory, output):
    directory, output = Path(directory), Path(output)
    if output.exists():
        raise ValueError('COORDINATE_OUTPUT_EXISTS')
    manifest = read_json(directory/'manifest.json')
    assert_binding(manifest['bindings'])
    if manifest['status'] != 'MACHINE_VERIFIED_PENDING_C':
        raise ValueError('COMPLETE_PRODUCTION_REQUIRED')
    raw = raw_data(); model = read_json(CFG/'contract.json')['model']
    a, rf = model['semi_major_m'], model['inverse_flattening']
    lon0, lat0 = model['origin_lon_degrees'], model['origin_lat_degrees']
    proj = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={a} +rf={rf} '
        f'+step +proj=topocentric +a={a} +rf={rf} +lon_0={lon0} +lat_0={lat0} +h_0=0')
    aeqd = pyproj.Proj(proj='aeqd', a=a, rf=rf, lon_0=lon0, lat_0=lat0, units='m')
    geod = pyproj.Geod(a=a, rf=rf)
    counts, differences = Counter(), Counter()
    maxima, records, problems = {}, [], []
    output.mkdir(parents=True)
    started = time.perf_counter()

    def extreme(key, value, witness):
        if key not in maxima or value > maxima[key]['value']:
            maxima[key] = {'value': float(value), **witness}

    with (output/'threshold_differences.jsonl.gz').open('xb') as binary:
        with gzip.GzipFile(filename='', mode='wb', fileobj=binary, mtime=0) as stream:
            for row in read_rows(directory):
                rid = row['record_id']; trusted = adapt(rid, raw[rid])
                t, ll = raw[rid]; ll = np.asarray(ll, float); enu = np.asarray(trusted['xy'])
                e, n, _ = proj.transform(ll[:, 0], ll[:, 1], np.zeros(len(ll)), errcheck=True)
                ax, ay = aeqd(ll[:, 0], ll[:, 1], errcheck=True)
                alt = np.column_stack((ax, ay))
                residual = np.hypot(enu[:, 0]-e, enu[:, 1]-n)
                radius = np.hypot(*enu.T)
                error = float(residual.max())
                counts.update(points_checked=len(t), records_checked=1, raw_adjacent_edges=max(0, len(t)-1))
                extreme('PROJ_implementation_error_work_m', error, {'record_id': rid, 'index': int(residual.argmax())})
                extreme('max_ENU_radius_work_m', radius.max(), {'record_id': rid})
                if error > model['coordinate_crosscheck_absolute_tolerance_m'] or radius.max() > model['domain_max_radius_m']:
                    problems.append({'record_id': rid, 'coordinate_error': error, 'radius': float(radius.max())})
                _, _, gd = geod.inv(ll[:-1, 0], ll[:-1, 1], ll[1:, 0], ll[1:, 1])
                gd = np.asarray(gd); distance = np.linalg.norm(np.diff(enu, axis=0), axis=1)
                difference = np.abs(distance-gd)
                if len(difference):
                    ix = int(difference.argmax())
                    extreme('raw_adjacent_geod_absolute_difference_work_m', difference[ix],
                            {'record_id': rid, 'left_index': ix, 'right_index': ix+1})
                    valid = gd > 0
                    if np.any(valid):
                        relative = difference[valid]/gd[valid]
                        extreme('raw_adjacent_geod_relative_difference', relative.max(), {'record_id': rid})
                context = {'raw': {rid: raw[rid]}, 'enu': {rid: trusted['xy']}, 'aeqd': {rid: alt.tolist()},
                           'geod': geod, 'model': model}
                for cfg, trace in row['traces'].items():
                    if trace['source_record'] != trusted:
                        raise ValueError('TRUSTED_RAW_PROJECTION_MISMATCH')
                    check = inspect_trace(trace, context)
                    counts.update(check['counts']); counts['unique_actual_traces_checked'] += 1
                    differences.update(check['difference_counts'])
                    for name, item in check['extrema'].items():
                        extreme(name, item['value'], {**item, 'config_id': cfg})
                    for item in check['differences']:
                        stream.write((json.dumps(item, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n').encode())
                records.append({'record_id': rid, 'points': len(t), 'coordinate_error_max_work_m': error,
                                'raw_adjacent_geod_difference_max_work_m': float(difference.max()) if len(difference) else None,
                                'actual_traces_checked': len(row['traces'])})
                if len(records) % 200 == 0:
                    print(json.dumps({'coordinate_records': len(records), 'seconds': round(time.perf_counter()-started, 2)}), flush=True)
    if [r['record_id'] for r in records] != manifest['input_ids']:
        raise ValueError('COORDINATE_COMPLETE_SCOPE_MISMATCH')
    result = {'at': now(), 'implementation_status': 'VERIFIED' if not problems else 'REJECTED',
              'run_id': manifest['run_id'], 'partition': manifest['partition'],
              'input_record_count': len(manifest['input_ids']),
              'classification': 'FULL_PRODUCTION_COORDINATE_CHECK' if manifest['partition'] == 'FULL_PRODUCTION'
                                else 'DEVELOPMENT_COORDINATE_CHECK_NOT_FULL_DATASET',
              'source_crs': 'UNVERIFIED', 'source_datum_proven': False, 'ground_truth_accuracy_claim': False,
              'counts': dict(counts), 'difference_counts': dict(differences), 'extrema': maxima,
              'implementation_failures': problems, 'per_record': records,
              'scope': 'ALL points; ALL raw adjacent edges; ALL actual S lengths/D windows/P intervals and alternate DP keep-set sensitivity; no all-pairs computation',
              'input_manifest_sha256': digest(directory/'manifest.json'), 'source_sha256': digest(__file__),
              'source_bindings': {**manifest['source_hashes'],
                  'task1/goal3/coordinates.py': digest(__file__),
                  'task1/scripts/goal2_coordinate_sensitivity.py': digest(ROOT/'task1/scripts/goal2_coordinate_sensitivity.py')},
              'pyproj': pyproj.__version__, 'PROJ': pyproj.proj_version_str,
              'threshold_differences_sha256': digest(output/'threshold_differences.jsonl.gz'),
              'elapsed_seconds': time.perf_counter()-started,
              'interpretation': 'Alternative-model decisions disclose conditional sensitivity; no model choice or parameter change follows.'}
    write_json(output/'coordinate_checks.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = check_run(args.directory, args.output)
    print({k: result[k] for k in ('implementation_status', 'counts', 'difference_counts', 'elapsed_seconds')})
