"""Transparent tables from bound traces; this module never selects on final data."""
import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path

from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json, now
from .data import EV
from .runtime import read_rows, assert_binding
from .selection import aggregate_pairs


def csv_write(path, rows):
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', encoding='utf8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def analyze(directory, output=None):
    directory = Path(directory)
    manifest = read_json(directory/'manifest.json')
    if manifest['status'] != 'MACHINE_VERIFIED_PENDING_C':
        raise ValueError('COMPLETE_RUN_REQUIRED')
    assert_binding(manifest['bindings'])
    output = Path(output) if output else directory/'analysis'
    output.mkdir(parents=True, exist_ok=True)
    metrics, pairs, p_pairs, grouped = [], [], [], defaultdict(list)
    observed, groups = [], Counter()
    new_coverage = defaultdict(lambda: {'count': 0, 'errors': [], 'short_segments_points': 0,
                                      'zero_displacement_edge_endpoints': set()})
    for row in read_rows(directory):
        rid = row['record_id']; observed.append(rid)
        for cid, cfg in row['strategy_configs'].items():
            trace = row['traces'][cfg]; m = trace['metrics']
            summary = {k: v for k, v in m.items() if not isinstance(v, (dict, list))}
            summary.update(strategy=cid, runtime_group=row['runtime_groups'][cid], terminal_status=trace['terminal_status'],
                           trace_sha256=object_hash(trace))
            metrics.append(summary); groups[(cid, row['runtime_groups'][cid])] += 1
        for key, pair in row['comparisons'].items():
            compact = {k: v for k, v in pair.items() if not isinstance(v, (dict, list))}
            compact['protection_failures'] = ';'.join(pair['protection_failures'])
            pairs.append(compact)
            grouped[(key, pair['stratum'])].append(pair)
            added = pair['newly_covered_indices']
            if not added:
                continue
            a, _ = key.split('|'); trace = row['traces'][row['strategy_configs'][a]]
            item = new_coverage[key]; item['count'] += len(added)
            errors = {p['index']: p['error'] for p in trace['metrics']['common_point_errors']}
            item['errors'].extend(errors[i] for i in added)
            short = {i for stage in trace['stages'] if stage['name'] == 'S' for op in stage['operations']
                     for part in op['segments'] if len(part['indices']) < 5 or part['features']['length'] < 65
                     for i in part['indices']}
            item['short_segments_points'] += len(set(added) & short)
            source = trace['source_record']
            zero = {i for j, (x, y) in enumerate(zip(source['xy'], source['xy'][1:])) if x == y for i in (j, j+1)}
            item['zero_displacement_edge_endpoints'].update((rid, i) for i in set(added) & zero)
        for pair in row['P_comparisons'].values():
            compact = {k: v for k, v in pair.items() if not isinstance(v, (dict, list))}
            compact['protection_failures'] = ';'.join(pair['protection_failures']); p_pairs.append(compact)
    if observed != manifest['input_ids']:
        raise ValueError('SHARDED_COMPLETE_SCOPE_MISMATCH')
    csv_write(output/'record_metrics.csv', metrics)
    csv_write(output/'record_pairs.csv', pairs)
    csv_write(output/'P_record_pairs.csv', p_pairs)
    csv_write(output/'by_stratum.csv', ({'pair': k, 'stratum': s, **aggregate_pairs(rows)}
                                      for (k, s), rows in sorted(grouped.items())))
    addition = {key: {'newly_covered_points': value['count'],
                       'max_error_work_m': max(value['errors']),
                       'mean_error_work_m': sum(value['errors'])/len(value['errors']),
                       'from_segments_shorter_than_R0_filter': value['short_segments_points'],
                       'raw_exact_zero_displacement_adjacent_endpoints': len(value['zero_displacement_edge_endpoints']),
                       'noise_truth_claim': False} for key, value in new_coverage.items()}
    result = {'at': now(), 'manifest_sha256': digest(directory/'manifest.json'),
              'source_sha256': digest(__file__), 'actual_records': len(observed),
              'actual_strategy_observations': len(metrics), 'partition': manifest['partition'],
              'strategy_summaries': manifest['record_metrics'], 'comparisons': manifest['comparisons'],
              'P_comparisons': manifest['P_comparisons'], 'new_coverage': addition,
              'runtime_groups': [{'strategy': cid, 'group': group, 'records': n} for (cid, group), n in groups.items()],
              'tables': {p.name: digest(p) for p in sorted(output.glob('*.csv'))},
              'interpretation': 'geometry and coverage in conditional working metres; not noise classification accuracy',
              'independent_C_status': 'PENDING'}
    write_json(output/'summary.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = analyze(args.directory, args.output)
    print({k: result[k] for k in ('actual_records', 'actual_strategy_observations', 'partition')})
