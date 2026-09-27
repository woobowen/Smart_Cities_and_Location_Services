"""Finite, version-bound execution with compressed, complete per-record traces."""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
import math
from pathlib import Path
import re
import subprocess
import time

from task1.workflow.g2_data import raw_data, adapt
from task1.workflow.g2_pipeline import run_record
from task1.workflow.g2_metrics import review_record, summarize
from task1.workflow.g2_selection import config_id, execution_parameters
from task1.workflow.g2_journal import source_snapshot as inherited_sources
from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json, now, bound_path
from .data import EV, CFG, GOAL
from .selection import paired, aggregate_pairs


def source_snapshot():
    paths = ['data.py', 'runtime.py', 'selection.py', 'control.py']
    return {**inherited_sources(), **{f'task1/goal3/{p}': digest(ROOT/'task1/goal3'/p) for p in paths}}


def resolve_parameters(strategy, raw_record):
    p = execution_parameters(strategy['parameters'])
    if strategy['order'] != 'S-D-P':
        raise ValueError('UNREGISTERED_G3_ORDER')
    rule = strategy.get('conditional_rule')
    if rule is None:
        return p, 'UNIFORM'
    if (rule.get('rule_id') != 'TIME_REGULAR_DIRECTION60_V1' or rule.get('group_count') != 2
            or rule.get('raw_record_id_in_predicate') is not False
            or rule.get('method_result_or_final_feedback_in_predicate') is not False):
        raise ValueError('UNREGISTERED_ROUTING_RULE')
    times = raw_record[0]
    finite = len(times) >= 2 and all(isinstance(t, (int, float)) and not isinstance(t, bool)
                                  and math.isfinite(t) for t in times)
    regular = finite and all(0 < b-a <= 30 for a, b in zip(times, times[1:]))
    return {**p, 'direction': 60 if regular else 35}, 'TIME_REGULAR' if regular else 'TIME_FLAGGED_OR_UNAVAILABLE'


def definitions():
    plan = read_json(EV/'a_candidate_plan.json')
    for path, h in plan['evidence_sha256'].items():
        if digest(ROOT/path) != h:
            raise ValueError('A_EVIDENCE_CHANGED:' + path)
    result = {row['candidate_id']: row for row in plan['candidate_definitions']}
    if len(result) != len(plan['candidate_definitions']):
        raise ValueError('DUPLICATE_STRATEGY_ID')
    contract = read_json(CFG/'contract.json')
    for key, field in [('new_single_definitions_max', 'new_single_definition_count'),
                       ('combination_definitions_max', 'new_combination_definition_count')]:
        if sum(r[field] for r in result.values()) > contract['budget'][key]:
            raise ValueError('CANDIDATE_BUDGET_EXCEEDED')
    for row in result.values():
        resolve_parameters(row, [[], []])
    return result


def assert_binding(binding):
    for path, sha in binding.items():
        if digest(ROOT/path) != sha:
            raise ValueError('SOURCE_OR_CONTRACT_CHANGED_NEW_RUN_REQUIRED:' + path)


def code_identity(source, partition, allow_recompute):
    """A portable bundle carries its verified processing revision, not a local Git claim."""
    if allow_recompute and not (ROOT/'.git').exists():
        if partition != 'FULL_PRODUCTION':
            raise ValueError('PORTABLE_RECOMPUTE_REQUIRES_FROZEN_PRODUCTION')
        frozen = read_json(EV/'production_freeze.json')
        assert_binding(frozen['bindings'])
        sha = frozen.get('processing_code_sha', '')
        if (frozen.get('processing_source_hashes') != source
                or not isinstance(sha, str) or re.fullmatch('[0-9a-f]{40}', sha) is None):
            raise ValueError('PORTABLE_PROCESSING_IDENTITY_MISMATCH')
        return {'code_sha': sha, 'code_identity_source': 'FROZEN_SOURCE_BUNDLE'}
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    return {'code_sha': sha, 'code_identity_source': 'ACTUAL_LOCAL_GIT_HEAD'}


def execution_gate(partition, ids, strategy_ids):
    split = read_json(EV/'split_manifest.json')
    expected = ([rid for part in split['partitions'].values() for rid in part] if partition == 'FULL_PRODUCTION'
                else split['partitions'].get(partition))
    if expected is None or ids != expected:
        raise ValueError('TRUSTED_PARTITION_SCOPE_MISMATCH')
    registered = definitions()
    if not strategy_ids or len(set(strategy_ids)) != len(strategy_ids) or not set(strategy_ids) <= set(registered):
        raise ValueError('UNREGISTERED_STRATEGY_SCOPE')
    receipt = read_json(EV/'contract_freeze.json')
    if receipt['status'] != 'INDEPENDENT_C_VERIFIED':
        raise ValueError('CONTRACT_REVIEW_REQUIRED')
    assert_binding(receipt['bindings'])
    if partition == 'G3_DEVELOPMENT':
        if 'S0_G0' in strategy_ids:
            admission = read_json(EV/'development_admission.json')
            assert_binding(admission['bindings'])
            if not {'S0', 'G0'} <= set(admission['independently_supported_parents']):
                raise ValueError('COMBINATION_PARENTS_NOT_ADMITTED')
        return
    if partition == 'G3_SELECTION':
        freeze = read_json(EV/'selection_freeze.json')
    elif partition == 'FINAL_CONFIRM':
        freeze = read_json(EV/'final_freeze.json')
    elif partition == 'FULL_PRODUCTION':
        freeze = read_json(EV/'production_freeze.json')
    else:
        raise ValueError('UNREGISTERED_PARTITION')
    assert_binding(freeze['bindings'])
    if freeze['input_ids'] != ids or freeze['strategy_ids'] != strategy_ids:
        raise ValueError('FROZEN_SCOPE_OR_STRATEGY_MISMATCH')


def read_rows(directory):
    directory = Path(directory)
    manifest = read_json(directory/'manifest.json')
    flattened = [rid for shard in manifest['shards'] for rid in shard.get('input_ids', [])]
    if (flattened != manifest['input_ids'] or len(flattened) != len(set(flattened))
            or any(shard['records'] != len(shard.get('input_ids', [])) for shard in manifest['shards'])):
        raise ValueError('SHARD_MANIFEST_COMPLETE_SCOPE_MISMATCH')
    for shard in manifest['shards']:
        path = bound_path(directory, shard['path'])
        if digest(path) != shard['sha256']:
            raise ValueError('SHARD_HASH_MISMATCH')
        with gzip.open(path, 'rt', encoding='utf8') as f:
            count = 0
            for line in f:
                row = json.loads(line)
                if count >= len(shard['input_ids']) or row.get('record_id') != shard['input_ids'][count]:
                    raise ValueError('SHARD_PAYLOAD_ORDERED_SCOPE_MISMATCH')
                count += 1
                yield row
        if count != shard['records']:
            raise ValueError('SHARD_RECORD_COUNT_MISMATCH')


def evaluate(run_id, partition, strategy_ids, *, output=None, allow_recompute=False, parent=None):
    directory = Path(output) if output else EV/'runs'/run_id
    existed = directory.exists()
    try:
        return _evaluate(run_id, partition, strategy_ids, output=output,
                         allow_recompute=allow_recompute, parent=parent)
    except BaseException as exc:
        if not existed and (directory/'manifest.json').is_file():
            manifest = read_json(directory/'manifest.json')
            manifest.update(status='INTERRUPTED_CHECKPOINT', interrupted_at=now(),
                            failure_reason=str(exc), automatic_retry=False,
                            remaining_record_ids=[rid for rid in manifest['input_ids']
                                                  if rid not in manifest['completed_record_ids']])
            write_json(directory/'manifest.json', manifest)
        raise


def _evaluate(run_id, partition, strategy_ids, *, output=None, allow_recompute=False, parent=None):
    directory = Path(output) if output else EV/'runs'/run_id
    if directory.exists():
        raise ValueError('RUN_EXISTS_USE_NEW_RUN_OR_EXPLICIT_RECOVERY')
    split = read_json(EV/'split_manifest.json')
    ids = ([rid for part in split['partitions'].values() for rid in part] if partition == 'FULL_PRODUCTION'
           else split['partitions'][partition])
    if not strategy_ids or len(strategy_ids) != len(set(strategy_ids)):
        raise ValueError('EMPTY_OR_DUPLICATE_STRATEGIES')
    registry = definitions()
    selected = {cid: registry[cid] for cid in strategy_ids}
    execution_gate(partition, ids, strategy_ids)
    source = source_snapshot()
    identity = code_identity(source, partition, allow_recompute)
    binding = {**source, 'task1/config/goal3/contract.json': digest(CFG/'contract.json'),
               'task1/evidence/goal3/split_manifest.json': digest(EV/'split_manifest.json'),
               'task1/evidence/goal3/a_candidate_plan.json': digest(EV/'a_candidate_plan.json')}
    contract_hash = digest(CFG/'contract.json')
    raw = raw_data()
    cards = read_json(ROOT/split['g2_diagnostics_path'])
    if object_hash(ids) != object_hash(list(dict.fromkeys(ids))):
        raise ValueError('DUPLICATE_RAW_SCOPE')
    directory.mkdir(parents=True)
    started = time.perf_counter()
    provenance = {'goal_id': GOAL, 'raw_sha256': split['raw_sha256'], 'partition': partition,
                  'scope_sha256': object_hash(ids), 'contract_sha256': contract_hash,
                  'split_sha256': digest(EV/'split_manifest.json'), 'source_tree_sha256': object_hash(source),
                  'source_kind': 'CURRENT_RUN_CONDITIONAL_ANALYSIS'}
    inherited_rows = None
    parent_manifest = None
    if parent is not None:
        parent = Path(parent)
        parent_manifest = read_json(parent/'manifest.json')
        if (parent_manifest['status'] != 'MACHINE_VERIFIED_PENDING_C' or parent_manifest['bindings'] != binding
                or parent_manifest['provenance'] != provenance or parent_manifest['input_ids'] != ids):
            raise ValueError('PARENT_CACHE_SCOPE_OR_EPOCH_MISMATCH')
        inherited_rows = iter(read_rows(parent))
    manifest = {'goal_id': GOAL, 'run_id': run_id, 'partition': partition, 'started_at': now(),
                'status': 'RUNNING', 'input_ids': ids, 'strategy_ids': strategy_ids, 'strategies': selected,
                'bindings': binding, 'source_hashes': source, **identity,
                'provenance': provenance, 'shards': [], 'record_metrics': {}, 'comparisons': {},
                'new_record_model_calls': 0, 'processing_evaluations': 0, 'strategy_record_observations': 0,
                'reused_identical_configuration_observations': 0, 'review_record_calls': 0,
                'cached_trace_rechecks': 0,
                'parent_cache': None if parent is None else {'path': str(parent.relative_to(ROOT)),
                                                            'sha256': digest(parent/'manifest.json')},
                'failed_records': [], 'completed_record_ids': [], 'recompute': allow_recompute}
    write_json(directory/'manifest.json', manifest)
    metrics = {cid: [] for cid in strategy_ids}
    pairs = {a+'|'+b: [] for a in strategy_ids for b in strategy_ids}
    p_pairs = {a+'|'+b: [] for a in strategy_ids for b in strategy_ids
               if selected[a]['parameters']['dp'] != 5 and selected[b]['parameters']['dp'] == 5
               and selected[a].get('conditional_rule') == selected[b].get('conditional_rule')
               and all(selected[a]['parameters'][k] == selected[b]['parameters'][k]
                       for k in selected[a]['parameters'] if k != 'dp')}
    for offset in range(0, len(ids), 40):
        assert_binding(binding)
        scope = ids[offset:offset+40]
        path = directory/f'traces-{offset//40:04d}.jsonl.gz'
        shard_ids = []
        with path.open('xb') as binary:
            with gzip.GzipFile(filename='', mode='wb', fileobj=binary, mtime=0) as stream:
                for rid in scope:
                    traces, refs, routes, reviews = {}, {}, {}, {}
                    try:
                        trusted = adapt(rid, raw[rid])
                        cached = next(inherited_rows) if inherited_rows is not None else None
                        if cached is not None and cached['record_id'] != rid:
                            raise ValueError('PARENT_RECORD_SCOPE_MISMATCH')
                        for cid, definition in selected.items():
                            params, route = resolve_parameters(definition, raw[rid])
                            cfg = config_id(params)
                            refs[cid], routes[cid] = cfg, route
                            if cfg not in traces:
                                if cached is not None and cfg in cached['traces']:
                                    trace = cached['traces'][cfg]
                                    manifest['cached_trace_rechecks'] += 1
                                else:
                                    trace = run_record(trusted, params, 'S-D-P', contract_hash=contract_hash, provenance=provenance)
                                    manifest['processing_evaluations'] += 1
                                review = review_record(trace, trusted, expected_parameters=params, expected_order='S-D-P',
                                                       contract_hash=contract_hash, trusted_provenance=provenance)
                                manifest['review_record_calls'] += 1
                                if review['status'] != 'VERIFIED':
                                    write_json(directory/f'failure-{rid}.json', {'trace': trace, 'review': review})
                                    raise ValueError('INDEPENDENT_MACHINE_REVIEW_FAILED:' + rid)
                                traces[cfg], reviews[cfg] = trace, review
                            else:
                                manifest['reused_identical_configuration_observations'] += 1
                            manifest['strategy_record_observations'] += 1
                            metrics[cid].append({'metrics': {k: v for k, v in traces[cfg]['metrics'].items()
                                if not isinstance(v, (dict, list)) or k in
                                ('filter_reason_segments', 'filter_reason_points', 'direction_undefined_reasons')}})
                        paired_rows = {}
                        for key in pairs:
                            a, b = key.split('|')
                            row = paired(traces[refs[a]], traces[refs[b]])
                            row.update(stratum=cards[rid]['stratum'], candidate_id=a, reference_id=b)
                            pairs[key].append(row); paired_rows[key] = row
                        specialized = {}
                        for key in p_pairs:
                            a, b = key.split('|')
                            row = paired(traces[refs[a]], traces[refs[b]], p_only=True)
                            row.update(stratum=cards[rid]['stratum'], candidate_id=a, reference_id=b)
                            p_pairs[key].append(row); specialized[key] = row
                        row = {'record_id': rid, 'raw_record_sha256': object_hash(raw[rid]),
                               'strategy_configs': refs, 'runtime_groups': routes, 'traces': traces,
                               'machine_reviews': reviews, 'comparisons': paired_rows, 'P_comparisons': specialized}
                        stream.write((json.dumps(row, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n').encode())
                        shard_ids.append(rid); manifest['completed_record_ids'].append(rid)
                    except Exception as exc:
                        manifest['failed_records'].append({'record_id': rid, 'reason': str(exc), 'status': 'NEEDS_REPAIR'})
                        manifest['status'] = 'INTERRUPTED_CHECKPOINT'
                        manifest['uncertain_shard'] = path.name
                        write_json(directory/'manifest.json', manifest)
                        raise
        manifest['shards'].append({'path': path.name, 'sha256': digest(path), 'records': len(shard_ids),
                                    'input_ids': shard_ids, 'bytes': path.stat().st_size})
        write_json(directory/'manifest.json', manifest)
        print(json.dumps({'run': run_id, 'records_done': len(manifest['completed_record_ids']),
                          'records_total': len(ids), 'unique_evaluations': manifest['processing_evaluations'],
                          'seconds': round(time.perf_counter()-started, 2)}), flush=True)
    assert_binding(binding)
    if inherited_rows is not None:
        try:
            next(inherited_rows)
        except StopIteration:
            pass
        else:
            raise ValueError('PARENT_CACHE_HAS_EXTRA_RECORDS')
    for cid in strategy_ids:
        manifest['record_metrics'][cid] = summarize(metrics[cid])
    for key, rows in pairs.items():
        manifest['comparisons'][key] = aggregate_pairs(rows)
    manifest['P_comparisons'] = {key: aggregate_pairs(rows) for key, rows in p_pairs.items()}
    manifest.update(status='MACHINE_VERIFIED_PENDING_C', ended_at=now(), elapsed_seconds=time.perf_counter()-started)
    write_json(directory/'manifest.json', manifest)
    # Paired raw readings stay in shards; compact tables are for inspection only.
    write_json(directory/'paired_summary.json', {'all_pairs': manifest['comparisons'], 'P_pairs': manifest['P_comparisons']})
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--partition', required=True)
    parser.add_argument('--strategies', nargs='+', required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--parent', type=Path)
    args = parser.parse_args()
    result = evaluate(args.run_id, args.partition, args.strategies, output=args.output, parent=args.parent)
    print(json.dumps({k: result[k] for k in ('status', 'elapsed_seconds', 'processing_evaluations')}))
