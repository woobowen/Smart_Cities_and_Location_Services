"""C-only enumeration of added coverage and actual reference filter causes.

This is post-freeze descriptive verification, not a new metric or selection rule.
No production attribution or processing implementation is imported.
"""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

import pyproj

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.evidence.goal2.c_contract.independent_numeric import partition, length

EV = ROOT / 'task1/evidence/goal3'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def covered_from_output(trace, window_of):
    covered = set()
    for segment in trace['final_segments']:
        indices = segment['indices']
        covered.update(indices)
        for left, right in zip(indices, indices[1:]):
            assert left < right and window_of[left] == window_of[right]
            covered.update(range(left, right + 1))
    declared = {p['index'] for p in trace['metrics']['common_point_errors'] if p['error'] is not None}
    assert covered == declared
    return covered


def main():
    folder = EV / 'runs/g3-full-production-01'
    mp = folder / 'manifest.json'
    m = read(mp)
    fp = EV / 'production_freeze.json'
    freeze = read(fp)
    cp = ROOT / 'task1/config/goal3/contract.json'
    contract = read(cp)
    rp = ROOT / contract['raw_path']
    assert sha(rp) == contract['raw_sha256']
    raw = read(rp)
    ap = EV / 'full_filter_attribution.json'
    actual = read(ap)
    assert m['status'] == 'MACHINE_VERIFIED_PENDING_C' and m['partition'] == 'FULL_PRODUCTION'
    assert m['input_ids'] == freeze['input_ids'] and set(m['input_ids']) == set(raw)
    assert len(m['input_ids']) == len(set(m['input_ids'])) == len(raw)
    assert m['strategies'] == freeze['strategies']
    final = freeze['final_strategy']
    assert final == 'S0' and set(m['strategy_ids']) == {'R0', 'S0'}
    for name, value in actual['source_bindings'].items():
        assert sha(ROOT / name) == value
    model = contract['model']
    transform = pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+step +proj=topocentric +a={model["semi_major_m"]} +rf={model["inverse_flattening"]} '
        f'+lon_0={model["origin_lon_degrees"]} +lat_0={model["origin_lat_degrees"]} +h_0=0')
    counts, reasons_total, actions = Counter(), Counter(), Counter()
    records, seen, targets = [], [], []
    coordinate_max = 0.0
    points = 0
    for shard in m['shards']:
        path = folder / shard['path']
        assert sha(path) == shard['sha256']
        targets.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})
        shard_ids = []
        with gzip.open(path, 'rt') as handle:
            for line in handle:
                row = json.loads(line)
                rid = row['record_id']
                shard_ids.append(rid)
                times, angular = raw[rid]
                assert row['raw_record_sha256'] == object_sha(raw[rid])
                b = row['traces'][row['strategy_configs']['R0']]
                c = row['traces'][row['strategy_configs'][final]]
                for cid, trace in [('R0', b), (final, c)]:
                    assert trace['record_id'] == trace['source_record']['record_id'] == rid
                    assert trace['parameters'] == freeze['strategies'][cid]['parameters']
                    assert trace['source_record']['indices'] == list(range(len(times)))
                    assert trace['source_record']['timestamps'] == times
                assert b['source_record'] == c['source_record']
                xy = b['source_record']['xy']
                assert len(xy) == len(times) == len(angular)
                for a, p in zip(angular, xy):
                    coordinate_max = max(coordinate_max, math.dist(p, transform.transform(*a, model['assumed_height_m'])[:2]))
                points += len(times)
                groups, _ = partition(times, xy, list(range(len(times))), 30, 400)
                window_of = {i: j for j, group in enumerate(groups) for i in group}
                independently_filtered = {}
                for group in groups:
                    reasons = (['TOO_FEW_POINTS'] if len(group) < 5 else [])
                    if length(xy, group) < 65:
                        reasons.append('TOO_SHORT_LENGTH')
                    if reasons:
                        independently_filtered.update((i, set(reasons)) for i in group)
                sb = next(stage for stage in b['stages'] if stage['name'] == 'S')
                sc = next(stage for stage in c['stages'] if stage['name'] == 'S')
                all_s = lambda stage: [p['indices'] for op in stage['operations'] for p in op['segments']]
                assert all_s(sb) == all_s(sc) == groups
                before, after = covered_from_output(b, window_of), covered_from_output(c, window_of)
                assert before <= after
                added = after - before
                ledgers = [{p['original_index']: p for p in trace['point_actions']} for trace in (b, c)]
                assert all(set(ledger) == set(range(len(times))) for ledger in ledgers)
                local = Counter()
                for index in added:
                    bp, cpnt = (ledger[index] for ledger in ledgers)
                    for point in (bp, cpnt):
                        assert point['record_id'] == rid and point['timestamp'] == times[index] and point['xy'] == xy[index]
                    assert bp['action'] == 'filtered' and bp['stage_position'] == 1
                    expected_reasons = independently_filtered[index]
                    assert set(bp['reasons']) == expected_reasons
                    local['+'.join(sorted(expected_reasons))] += 1
                    reasons_total.update(expected_reasons)
                    assert cpnt['action'] in {'retained', 'denoised', 'simplified'}
                    actions[cpnt['action']] += 1
                counts.update(local)
                records.append({'record_id': rid, 'added_points': len(added),
                                'mutually_exclusive_reference_reason_counts': dict(local)})
        assert shard_ids == shard['input_ids']
        seen.extend(shard_ids)
        if len(seen) % 2000 == 0:
            print(json.dumps({'filter_attribution_C_records': len(seen)}), flush=True)
    assert seen == m['input_ids'] and actual['per_record'] == records
    assert coordinate_max <= model['coordinate_crosscheck_absolute_tolerance_m']
    assert actual['records'] == len(raw) == len(records)
    assert actual['newly_covered_points'] == sum(counts.values()) == m['comparisons'][final + '|R0']['coverage_delta']
    assert actual['mutually_exclusive_reference_reason_counts'] == dict(counts)
    assert actual['per_reason_counts_overlap_allowed'] == dict(reasons_total)
    assert actual['new_point_final_ledger_actions'] == dict(actions)
    assert actual['classification'] == 'POST_FREEZE_DESCRIPTIVE_FILTER_ATTRIBUTION'
    assert actual['method_or_parameter_change'] is False and actual['new_model_calls'] == 0
    assert actual['legacy_analysis_field']['actual_definition'] == 'len(S-segment indices) < 5 OR S-segment length < 65 working metres'
    assert actual['legacy_analysis_field']['historical_artifacts_rewritten'] is False
    for path in (mp, fp, cp, ap, rp, ROOT / 'task1/goal3/filter_diagnostics.py',
                 ROOT / 'task1/evidence/goal2/c_contract/independent_numeric.py'):
        targets.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})
    receipt = {'role_context': '/root/c_protocol', 'status': 'VERIFIED',
        'target_id': 'full_filter_attribution', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'targets': targets, 'source_hashes': dict(m['source_hashes'], **{
            'task1/goal3/filter_diagnostics.py': sha(ROOT / 'task1/goal3/filter_diagnostics.py')}),
        'checked_components': [
            'Complete original raw hash, record identity, timestamps and all-point independent PROJ coordinate check',
            'All actual R0/S0 S partitions independently reconstructed from raw-indexed time/working coordinates',
            'Added coverage identities reconstructed from final output edges in fixed raw windows; declared coverage cross-checked',
            'Each added original point has actual R0 filtered ledger fate and independently recalculated point-count/length filter reasons',
            'Every per-record diagnostic row and mutually exclusive reason bucket, overlapping reason total and final point-action count',
            'Legacy OR diagnostic retained as historical definition; this new attribution does not change metrics or decisions'],
        'unchecked_components': ['Noise truth or source datum', 'Whole-run numerical closure is a separate mandatory receipt'],
        'actual_records': len(records), 'actual_points': points, 'newly_covered_points': sum(counts.values()),
        'mutually_exclusive_reference_reason_counts': dict(counts),
        'per_reason_counts_overlap_allowed': dict(reasons_total),
        'new_point_final_ledger_actions': dict(actions),
        'independent_PROJ_max_work_m': coordinate_max, 'errors': [],
        'actual_command': '.venv/bin/python task1/evidence/goal3/independent_c/review_filter_attribution.py',
        'checker_sha256': sha(Path(__file__))}
    output = EV / 'independent_c/full_filter_attribution_receipt.json'
    with output.open('x') as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'status': 'VERIFIED', 'records': len(records), 'points': points,
                      'newly_covered_points': sum(counts.values()), 'receipt_sha256': sha(output)}))


if __name__ == '__main__':
    main()
