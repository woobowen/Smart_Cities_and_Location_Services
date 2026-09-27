"""Portable full raw recomputation; compact historical hashes are comparison targets."""
import argparse
import gzip
import json
from pathlib import Path
import time

from task1.workflow.io import ROOT, digest, object_hash, read_json, write_json, now
from task1.workflow.g2_data import raw_data, adapt
from task1.workflow.g2_pipeline import run_record
from task1.workflow.g2_metrics import review_record
from task1.workflow.g2_selection import config_id, select_record, compare, REFERENCE
from task1.workflow.g2_experiments import read_gzip, write_gzip
from .data import EV, G2, CFG
from .runtime import evaluate, assert_binding


def build_historical_registry():
    """Read already accepted G2 traces once; preserve every actually run proposal."""
    index = read_json(G2/'current_runs.json')
    registry = {'classification': 'HISTORICAL_G2_RECOMPUTE_TARGETS; not new model calls or G3 experiments',
                'created_at': now(), 'source_registry': {}, 'topics': {'parameters': [], 'modes': []},
                'episode_selections': [], 'proposal_sources': [], 'new_model_calls': 0}
    for key in ('parameter_development', 'order_development', 'evaluation_parameters', 'evaluation_orders', 'memory'):
        directory = G2/'runs'/index[key]
        manifest = read_json(directory/'manifest.json')
        registry['source_registry'][str((directory/'manifest.json').relative_to(ROOT))] = digest(directory/'manifest.json')
        registry['processing_bindings'] = manifest['source_hashes']
        topic = 'modes' if key == 'memory' else 'parameters'
        for entry in manifest['artifacts'].values():
            path = directory/entry['file']
            if digest(path) != entry['sha256']:
                raise ValueError('HISTORICAL_RESULT_HASH_MISMATCH')
            batch = read_gzip(path)
            registry['topics'][topic].append({'source_run_id': manifest['run_id'],
                'source_result_path': str(path.relative_to(ROOT)), 'source_result_sha256': entry['sha256'],
                'parameters': entry['parameters'], 'order': entry['order'], 'contract_hash': batch['contract_hash'],
                'provenance': batch['provenance'], 'records': [{'record_id': row['record_id'],
                    'target_hash': object_hash(row)} for row in batch['records']], 'summary': batch['summary']})
    for key in ('mode_development', 'mode_evaluation'):
        directory = G2/'runs'/index[key]
        manifest = read_json(directory/'manifest.json')
        registry['source_registry'][str((directory/'manifest.json').relative_to(ROOT))] = digest(directory/'manifest.json')
        for ep_ref in manifest['mode_episodes']:
            episode_path = directory/ep_ref['path']
            if digest(episode_path) != ep_ref['sha256']:
                raise ValueError('HISTORICAL_EPISODE_HASH_MISMATCH')
            episode = read_json(episode_path)
            for row in episode['records']:
                path = episode_path.parent/(row['record_id']+'_candidate_traces.json.gz')
                if digest(path) != episode['artifact_hashes'][path.name]:
                    raise ValueError('HISTORICAL_CANDIDATE_TRACE_HASH_MISMATCH')
                saved = read_gzip(path)['results']
                if set(saved) != set(row['candidate_ids']):
                    raise ValueError('HISTORICAL_EPISODE_SCOPE_MISMATCH')
                selection = {'source_episode': str(episode_path.relative_to(ROOT)),
                    'source_episode_sha256': ep_ref['sha256'], 'record_id': row['record_id'],
                    'episode_id': row['episode_id'], 'mode': row['mode'], 'selected_config_id': row['selected_config_id'],
                    'candidate_ids': row['candidate_ids'], 'original_proposals': row['proposal_records'],
                    'original_rounds': row['rounds'], 'trace_tasks': []}
                for cid in row['candidate_ids']:
                    trace = saved[cid]
                    selection['trace_tasks'].append(len(registry['topics']['modes']))
                    registry['topics']['modes'].append({'source_run_id': manifest['run_id'],
                        'source_result_path': str(path.relative_to(ROOT)), 'source_result_sha256': digest(path),
                        'parameters': trace['parameters'], 'order': trace['order'], 'contract_hash': trace['contract_hash'],
                        'provenance': trace['provenance'], 'records': [{'record_id': row['record_id'],
                            'target_hash': object_hash(trace)}], 'episode_id': row['episode_id'], 'config_id': cid})
                registry['episode_selections'].append(selection)
            registry['proposal_sources'].append({'path': str(episode_path.relative_to(ROOT)),
                                                  'sha256': ep_ref['sha256']})
    registry['bindings'] = {**registry['processing_bindings'],
        'task1/config/goal2/contract.json': digest(ROOT/'task1/config/goal2/contract.json'),
        'task1/evidence/goal2/data/split_manifest.json': digest(G2/'data/split_manifest.json')}
    path = EV/'historical_recompute_registry.json.gz'
    write_gzip(path, registry)
    write_json(EV/'historical_recompute_registry_binding.json', {'path': str(path.relative_to(ROOT)),
        'sha256': digest(path), 'source_registry': registry['source_registry'],
        'counts': {topic: sum(len(t['records']) for t in tasks) for topic, tasks in registry['topics'].items()},
        'independent_C_status': 'PENDING', 'new_model_calls': 0})
    return path


def recompute_historical(topic, output):
    from task1.workflow.g2_metrics import summarize
    from .offline_plots import compact_metrics, historical_plots
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    binding = read_json(EV/'historical_recompute_registry_binding.json')
    path = ROOT/binding['path']
    if digest(path) != binding['sha256']:
        raise ValueError('RECOMPUTE_REGISTRY_CHANGED')
    registry = read_gzip(path); assert_binding(registry['bindings'])
    raw = raw_data(); records = {}; completed = []; start = time.perf_counter()
    episode_trace_tasks = {i for e in registry['episode_selections'] for i in e['trace_tasks']} if topic == 'modes' else set()
    episode_results, selections = {}, []
    plot_tasks, plot_episodes = [], []
    episode_ends = {e['trace_tasks'][-1]: e for e in registry['episode_selections']} if topic == 'modes' else {}
    for i, task in enumerate(registry['topics'][topic]):
        rebuilt = []
        for ref in task['records']:
            rid = ref['record_id']
            if rid not in records:
                records[rid] = adapt(rid, raw[rid])
            result = run_record(records[rid], task['parameters'], task['order'],
                                contract_hash=task['contract_hash'], provenance=task['provenance'])
            if object_hash(result) != ref['target_hash']:
                raise ValueError('FULL_HISTORICAL_RAW_RECOMPUTE_MISMATCH:' + rid)
            review = review_record(result, records[rid], expected_parameters=task['parameters'],
                expected_order=task['order'], contract_hash=task['contract_hash'], trusted_provenance=task['provenance'])
            if review['status'] != 'VERIFIED':
                raise ValueError('HISTORICAL_RECOMPUTE_REVIEW_FAILED:' + rid)
            rebuilt.append(result)
        new_summary = summarize(rebuilt)
        if 'summary' in task and new_summary != task['summary']:
            raise ValueError('HISTORICAL_SUMMARY_MISMATCH')
        plot_tasks.append({'task': i, 'source_run_id': task['source_run_id'],
            'partition': task['provenance']['partition'], 'parameters': task['parameters'],
            'order': task['order'], 'record_ids': [r['record_id'] for r in rebuilt],
            'summary_from_new_raw_results': compact_metrics(new_summary)})
        if i in episode_trace_tasks:
            episode_results[i] = rebuilt[0]
        if i in episode_ends:
            episode = episode_ends[i]
            results = {cid: episode_results[j] for cid, j in zip(episode['candidate_ids'], episode['trace_tasks'])}
            if episode['mode'] == 'llm-only':
                legal = [p['executed_config_id'] for p in episode['original_proposals'] if p.get('executed')]
                selected = legal[0] if legal and not results[legal[0]]['metrics']['raw_break_crossings'] else config_id(REFERENCE)
            else:
                selected, _ = select_record(results, config_id(REFERENCE))
            if selected != episode['selected_config_id']:
                raise ValueError('HISTORICAL_SELECTION_RECOMPUTE_MISMATCH')
            selections.append({'episode_id': episode['episode_id'], 'record_id': episode['record_id'],
                               'selected_config_id': selected, 'selection_match': True})
            assessment = compare(results[selected], results[config_id(REFERENCE)])
            plot_episodes.append({'episode_id': episode['episode_id'], 'record_id': episode['record_id'],
                'partition': task['provenance']['partition'], 'mode': episode['mode'],
                'selected_config_id': selected, 'candidate_evaluations': len(results),
                'new_selected_metrics': compact_metrics(results[selected]['metrics']),
                'new_R0_metrics': compact_metrics(results[config_id(REFERENCE)]['metrics']),
                'new_comparison': {k: assessment[k] for k in
                    ('status', 'feasible', 'strict_gain', 'coverage_delta', 'protection_failures')}})
            for j in episode['trace_tasks']:
                del episode_results[j]
        completed.append({'task': i, 'source_run_id': task['source_run_id'], 'records': len(task['records']),
                          'raw_recomputed_hash_and_review': 'VERIFIED'})
        if i % 10 == 0:
            print(json.dumps({'topic': topic, 'task': i+1, 'total_tasks': len(registry['topics'][topic]),
                              'record_recomputations': sum(c['records'] for c in completed)}), flush=True)
    plots = historical_plots(output, topic, plot_tasks, plot_episodes,
        {'registry_sha256': binding['sha256'], 'raw_sha256': digest(ROOT/'task1/作业/作业/traj_dict.json'),
         'recompute_source_sha256': digest(__file__),
         'candidate_record_recomputations': sum(c['records'] for c in completed)})
    result = {'status': 'VERIFIED', 'mode': 'FULL_RECOMPUTE_HISTORICAL_G2', 'topic': topic,
              'new_model_calls': 0, 'candidate_record_recomputations': sum(c['records'] for c in completed),
              'at': now(), 'elapsed_seconds': time.perf_counter()-start, 'checks': completed, 'selections': selections,
              'registry_sha256': binding['sha256'], 'source_sha256': digest(__file__),
              'raw_recomputed_plots': plots}
    write_json(output/'recompute_receipt.json', result)
    return result


def recompute_production(output):
    from .offline_plots import production_plots
    current = read_json(EV/'current_runs.json')
    original = read_json(EV/'runs'/current['production']/'manifest.json')
    result = evaluate('FULL_RECOMPUTE', 'FULL_PRODUCTION', original['strategy_ids'],
                      output=Path(output), allow_recompute=True)
    if ([s['sha256'] for s in result['shards']] != [s['sha256'] for s in original['shards']]
            or result['record_metrics'] != original['record_metrics'] or result['comparisons'] != original['comparisons']):
        raise ValueError('PRODUCTION_FULL_RECOMPUTE_MISMATCH')
    plots = production_plots(Path(output))
    receipt = {'status': 'VERIFIED', 'mode': 'FULL_RECOMPUTE', 'new_model_calls': 0,
               'raw_records': len(result['input_ids']), 'record_evaluations': result['processing_evaluations'],
               'actual_full_shard_hash_equality': True, 'source_sha256': digest(__file__),
               'raw_recomputed_plots': plots}
    write_json(Path(output)/'recompute_receipt.json', receipt)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic', choices=['build-registry', 'parameters', 'modes', 'production'])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.topic == 'build-registry':
        print(build_historical_registry())
    elif args.topic == 'production':
        print(recompute_production(args.output))
    else:
        print(recompute_historical(args.topic, args.output))
