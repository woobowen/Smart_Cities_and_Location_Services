"""Actual exposed-input plot smoke; explicitly not production or a new mode test."""
import argparse
import gzip
import json
from pathlib import Path

from task1.workflow.io import ROOT, digest, object_hash, write_json
from task1.workflow.g2_data import raw_data, adapt
from task1.workflow.g2_pipeline import run_record, ORDERS
from task1.workflow.g2_metrics import summarize, review_record
from task1.workflow.g2_selection import REFERENCE, config_id, compare
from task1.workflow.g2_experiments import read_gzip
from task1.goal3.offline_plots import compact_metrics, historical_plots, production_plots, MODES


def smoke(output):
    output = Path(output)
    if output.exists():
        raise ValueError('NEW_SMOKE_DIRECTORY_REQUIRED')
    output.mkdir(parents=True)
    raw = raw_data(); pilot = adapt('246', raw['246'])
    contract = digest(ROOT/'task1/config/goal2/contract.json')
    count = 0

    def process(record, parameters, order, provenance, contract_hash=contract):
        nonlocal count
        result = run_record(record, parameters, order, contract_hash=contract_hash, provenance=provenance)
        check = review_record(result, record, expected_parameters=parameters, expected_order=order,
                              contract_hash=contract_hash, trusted_provenance=provenance)
        assert check['status'] == 'VERIFIED'; count += 1
        return result

    tasks = []; pilot_results = {}
    parameters = [REFERENCE, {**REFERENCE, 'min_points': 2, 'min_length': 0},
                  {**REFERENCE, 'direction': 15}, {**REFERENCE, 'direction': 60},
                  {**REFERENCE, 'dp': 0}, {**REFERENCE, 'dp': 10}, {**REFERENCE, 'dp': 20}]
    for kind, pairs in [('parameters', [(p, 'S-D-P') for p in parameters]),
                        ('orders', [(REFERENCE, order) for order in ORDERS])]:
        for p, order in pairs:
            result = process(pilot, p, order, {'classification': 'ENGINEERING_SMOKE_EXPOSED_PILOT'})
            tasks.append({'source_run_id': 'engineering-'+kind, 'partition': 'PILOT_ENGINEERING_ONLY',
                'parameters': p, 'order': order, 'record_ids': ['246'],
                'summary_from_new_raw_results': compact_metrics(summarize([result]))})
            if kind == 'parameters' and p in parameters[:2]:
                pilot_results['R0' if p == REFERENCE else 'S0'] = result
    provenance = {'engineering_smoke': True, 'raw_sha256': digest(ROOT/'task1/作业/作业/traj_dict.json'),
                  'source_sha256': digest(__file__), 'not_full': True, 'new_model_calls': 0}
    parameter_figures = historical_plots(output/'parameters', 'parameters', tasks, [], provenance)

    registry = read_gzip(ROOT/'task1/evidence/goal3/historical_recompute_registry.json.gz')
    episodes = []
    for mode in MODES:
        episode = next(e for e in registry['episode_selections'] if e['mode'] == mode and e['episode_id'].startswith('DEVELOPMENT-'))
        selected, reference = None, None
        for index in episode['trace_tasks']:
            task = registry['topics']['modes'][index]
            if task['config_id'] not in {episode['selected_config_id'], config_id(REFERENCE)}:
                continue
            ref = task['records'][0]
            result = process(adapt(ref['record_id'], raw[ref['record_id']]), task['parameters'], task['order'],
                             task['provenance'], task['contract_hash'])
            assert object_hash(result) == ref['target_hash']
            if task['config_id'] == episode['selected_config_id']: selected = result
            if task['config_id'] == config_id(REFERENCE): reference = result
        assessment = compare(selected, reference)
        episodes.append({'episode_id': episode['episode_id'], 'record_id': episode['record_id'],
            'partition': 'DEVELOPMENT_SMOKE_SUBSET', 'mode': mode,
            'new_selected_metrics': compact_metrics(selected['metrics']),
            'new_R0_metrics': compact_metrics(reference['metrics']),
            'new_comparison': {key: assessment[key] for key in ('status', 'feasible', 'strict_gain', 'coverage_delta', 'protection_failures')}})
    mode_figures = historical_plots(output/'modes', 'modes', [], episodes, provenance)

    directory = output/'production_path_smoke'; directory.mkdir()
    refs = {name: config_id(t['parameters']) for name, t in pilot_results.items()}
    traces = {refs[name]: trace for name, trace in pilot_results.items()}
    row = {'record_id': '246', 'strategy_configs': refs, 'traces': traces,
           'comparisons': {'S0|R0': compare(pilot_results['S0'], pilot_results['R0'])}}
    path = directory/'traces-0000.jsonl.gz'
    with path.open('wb') as binary:
        with gzip.GzipFile(filename='', fileobj=binary, mode='wb', mtime=0) as stream:
            stream.write((json.dumps(row, ensure_ascii=False)+'\n').encode())
    manifest = {'partition': 'ENGINEERING_SMOKE_EXPOSED_PILOT', 'recompute': True,
                'status': 'MACHINE_VERIFIED_PENDING_C', 'strategy_ids': ['R0', 'S0'], 'input_ids': ['246'],
                'record_metrics': {name: summarize([trace]) for name, trace in pilot_results.items()},
                'shards': [{'path': path.name, 'sha256': digest(path), 'records': 1, 'input_ids': ['246']}]}
    write_json(directory/'manifest.json', manifest)
    production_figures = production_plots(directory)
    # A changed summary must be rejected even when the trace hash is unchanged.
    manifest['record_metrics']['R0']['n_final'] += 1
    write_json(directory/'manifest.json', manifest)
    try:
        production_plots(directory)
    except ValueError as exc:
        assert str(exc) == 'NEW_TRACE_PLOT_AGGREGATION_MISMATCH'
    else:
        raise AssertionError('TAMPERED_SUMMARY_NOT_REJECTED')
    manifest['record_metrics']['R0']['n_final'] -= 1
    write_json(directory/'manifest.json', manifest)
    receipt = {'status': 'VERIFIED', 'scope': 'ENGINEERING_SMOKE_ONLY; exposed pilot246 and four real historical DEVELOPMENT record-episode pairs',
        'actual_raw_pipeline_evaluations': count, 'new_model_calls': 0,
        'figures': [parameter_figures, mode_figures, production_figures],
        'point_ledger_to_new_summary_check': 'VERIFIED', 'tampered_new_summary': 'REJECTED',
        'full_notebook_execution': 'NOT_RUN', 'final_confirmation_accessed': False}
    write_json(output/'smoke_receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    smoke(parser.parse_args().output)
