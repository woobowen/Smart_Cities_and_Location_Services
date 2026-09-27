"""Bind final reporting numbers to actual complete runs and independent receipts."""
from task1.workflow.io import ROOT, digest, read_json, write_json, now
from .data import EV, CFG
from .runtime import assert_binding, definitions
from .freezes import verified_run


def build():
    current = read_json(EV/'current_runs.json')
    sources, runs = {}, {}

    def source(path):
        sources[str(path.relative_to(ROOT))] = digest(path)
        return read_json(path)

    for topic in ('development', 'selection', 'confirmation', 'production'):
        verified_run(current[topic])
        path = EV/'runs'/current[topic]/'manifest.json'
        manifest = source(path); assert_binding(manifest['bindings'])
        if (manifest['status'] != 'MACHINE_VERIFIED_PENDING_C' or manifest['failed_records']
                or manifest['input_ids'] != manifest['completed_record_ids']):
            raise ValueError('INCOMPLETE_REPORT_INPUT:' + topic)
        receipt = source(EV/'independent_c'/(manifest['run_id']+'_receipt.json'))
        if receipt['status'] != 'VERIFIED' or not any(t['sha256'] == digest(path) for t in receipt['targets']):
            raise ValueError('INDEPENDENT_REPORT_INPUT_NOT_CURRENT:' + topic)
        runs[topic] = manifest
    freeze = source(EV/'final_freeze.json')
    release = source(EV/'release_decision.json')
    production_freeze = source(EV/'production_freeze.json')
    coordinate = source(EV/'coordinates/coordinate_checks.json')
    if coordinate['implementation_status'] != 'VERIFIED':
        raise ValueError('COORDINATE_IMPLEMENTATION_NOT_VERIFIED')
    full_math = source(EV/'independent_c'/(current['production']+'_categories_receipt.json'))
    if full_math['status'] != 'VERIFIED':
        raise ValueError('PRODUCTION_CATEGORY_REVIEW_REQUIRED')
    final = current['final_strategy']; proposed = freeze['primary_strategy']
    if release['final_strategy'] != final or production_freeze['final_strategy'] != final:
        raise ValueError('FINAL_DEPLOYMENT_IDENTITY_MISMATCH')
    primary_pair = runs['confirmation']['comparisons'][proposed+'|R0']
    production = runs['production']; c = read_json(CFG/'contract.json')
    result = {'at': now(), 'source_bindings': sources, 'source_sha256': digest(__file__),
        'classification': 'CURRENT_G3_FINAL_CONFIRMATION_AND_DESCRIPTIVE_FULL_PRODUCTION',
        'source_crs': 'UNVERIFIED', 'working_model': c['model'],
        'data': {'raw_sha256': c['raw_sha256'], 'records': len(production['input_ids']),
                 'points': production['record_metrics']['R0']['n_input'],
                 'independent_people_or_trips': 'NOT_ESTABLISHED'},
        'final_strategy': final, 'definition': definitions()[final],
        'record_runtime': {'mode': 'DETERMINISTIC_CONDITIONAL_RULE' if definitions()[final].get('conditional_rule')
                           else 'DETERMINISTIC_FIXED_PARAMETERS', 'new_model_calls': 0,
                           'read_only_memory_used_for_record_decisions': False,
                           'per_record_verifier_fallback': False},
        'confirmation': {'records': len(runs['confirmation']['input_ids']),
                         'points': runs['confirmation']['record_metrics']['R0']['n_input'],
                         'primary_strategy': proposed, 'pair': primary_pair,
                         'summaries': runs['confirmation']['record_metrics'],
                         'release': release,
                         'scope_limit': 'One fixed record-group sample; no documented prior method exposure, not independent people or universal accuracy.'},
        'production': {'records_attempted': len(production['input_ids']),
                       'records_with_terminal_state': len(production['completed_record_ids']),
                       'processing_failures': production['failed_records'],
                       'summaries': production['record_metrics'],
                       'final_vs_R0': production['comparisons'][final+'|R0'],
                       'scope_limit': 'All partitions including exposed development; descriptive dataset output, not an independent final test.'},
        'coordinate_check': {k: coordinate[k] for k in ('implementation_status', 'counts', 'difference_counts', 'extrema', 'scope')},
        'code_sha': production['code_sha'],
        'run_costs': {key: {k: run[k] for k in ('run_id', 'elapsed_seconds', 'processing_evaluations',
                                              'cached_trace_rechecks', 'strategy_record_observations',
                                              'reused_identical_configuration_observations', 'new_record_model_calls')}
                     for key, run in runs.items()},
        'scientific_limitations': ['No noise labels or noise-identification accuracy.',
            'Source datum remains unverified; alternative-model sensitivity does not establish geolocation truth.',
            'More common raw coverage does not prove newly covered points are clean.',
            'Common coverage is distinct from the number of stored output points.',
            'P comparison uses complete identical immediate inputs and five working metres, not a candidate-defined truth.'],
        'GPT_SECOND_REVIEW': 'PENDING', 'Understanding': 'USER_DETERMINED', 'Submission': 'NOT_READY'}
    write_json(EV/'result_summary.json', result)
    return result


if __name__ == '__main__':
    summary = build()
    print({k: summary[k] for k in ('final_strategy', 'data', 'code_sha')})
