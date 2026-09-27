"""C independently checks frozen result identity and key report table numbers."""
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf8'))


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def main():
    table_fields = ['n_records', 'n_input', 'n_filtered', 'n_direction_removed',
                    'n_dp_removed', 'n_final', 'common_covered_points',
                    'raw_windows_covered', 'n_no_output_records', 'raw_break_crossings']
    targets = {}
    checked = []
    for run, fragment, partition in [
        ('g3-final-confirm-01', 'confirmation_generated.tex', 'FINAL_CONFIRM'),
        ('g3-full-production-01', 'production_generated.tex', 'FULL_PRODUCTION')]:
        base = 'task1/evidence/goal3/runs/'+run+'/'
        manifest = read(base+'manifest.json')
        analysis = read(base+'analysis/summary.json')
        pairs = read(base+'paired_summary.json')['all_pairs']['S0|R0']
        tex_path = 'task1/reports/experiment1/'+fragment
        tex = (ROOT/tex_path).read_text(encoding='utf8')
        assert manifest['partition'] == analysis['partition'] == partition
        assert sha(base+'manifest.json') == analysis['manifest_sha256']
        assert manifest['record_metrics'] == analysis['strategy_summaries']
        assert manifest['code_sha'] == 'e12f8a27944210adb452730be92a0674dfc6b84b'
        assert manifest['new_record_model_calls'] == 0
        assert manifest['failed_records'] == []
        assert manifest['input_ids'] == manifest['completed_record_ids']
        numbers = {}
        for key in table_fields:
            vals = [analysis['strategy_summaries'][s][key] for s in ('R0', 'S0')]
            assert f'{vals[0]:,} & {vals[1]:,}' in tex, (fragment, key, vals)
            numbers[key] = vals
        for s, metrics in analysis['strategy_summaries'].items():
            assert metrics['n_input'] == sum(metrics[k] for k in ('n_filtered','n_direction_removed','n_dp_removed','n_final'))
            assert metrics['common_coverage'] == metrics['common_covered_points']/metrics['n_input']
            assert metrics['point_retention'] == metrics['n_final']/metrics['n_input']
        assert pairs['all_guards_pass'] and not pairs['failure_records']
        assert f"{pairs['strict_gain_records']:,}" in tex
        checked.append({'partition': partition, 'source_run': run, 'numbers': numbers,
                        'strict_gain_records': pairs['strict_gain_records'],
                        'scope': 'Current report table against bound frozen manifest and actual saved analysis; not a new experiment'})
        for p in [base+'manifest.json',base+'analysis/summary.json',base+'paired_summary.json',tex_path]:
            targets[p] = sha(p)
    shard='task1/evidence/goal3/runs/g3-full-production-01/traces-0000.jsonl.gz'
    targets[shard] = sha(shard)
    with gzip.open(ROOT/shard, 'rt', encoding='utf8') as stream:
        for line in stream:
            row = json.loads(line)
            if row['record_id'] == '352':
                break
        else:
            raise AssertionError('BOUNDARY_RECORD_MISSING')
    ref = row['traces'][row['strategy_configs']['R0']]
    chosen = row['traces'][row['strategy_configs']['S0']]
    assert ref['point_actions'][105]['action'] == 'filtered'
    assert ref['point_actions'][105]['reasons'] == ['TOO_FEW_POINTS']
    assert chosen['point_actions'][105]['action'] == 'denoised'
    assert chosen['point_actions'][105]['reasons'] == ['DIRECTION_RULE']
    local_d = next(s for s in chosen['stages'][1]['input'] if 105 in s['indices'])
    local_p_in = next(s for s in chosen['stages'][2]['input'] if 104 in s['indices'])
    local_p_out = next(s for s in chosen['stages'][2]['output'] if 104 in s['indices'])
    assert local_d['indices'] == [104,105,106,107]
    assert local_p_in['indices'] == local_p_out['indices'] == [104,106,107]
    with localcontext() as ctx:
        ctx.prec = 50
        xy = chosen['source_record']['xy']
        a,p,b = [[Decimal(str(n)) for n in xy[i]] for i in (104,105,106)]
        vector = [b[i]-a[i] for i in range(2)]
        offset = [p[i]-a[i] for i in range(2)]
        u = max(Decimal(0), min(Decimal(1), sum(x*y for x,y in zip(offset,vector))/sum(x*x for x in vector)))
        distance = sum((offset[i]-u*vector[i])**2 for i in range(2)).sqrt()
    assert abs(float(distance)-chosen['metrics']['common_max_error']) < 1e-8
    assert format(distance, '.6f') == '266.016754'
    result = {'role_context':'/root/c_independent','status':'PASS',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':targets,
        'table_checks':checked,
        'boundary_check':{'record_id':'352','index':105,'reference_reason':ref['point_actions'][105]['reasons'],
            'final_action':chosen['point_actions'][105]['action'],'D_input_indices':local_d['indices'],
            'P_input_indices':local_p_in['indices'],'P_output_indices':local_p_out['indices'],
            'independent_decimal_distance_from_saved_work_coordinates':str(distance),
            'coordinate_fact_boundary':'Saved conditional work coordinates; this arithmetic is not source datum verification.',
            'record_P_max_error':chosen['metrics']['dp_max_error']},
        'scope_limit':'Major current generated tables and one reported boundary arithmetic/trace check. Full mathematical production audit is inherited via unchanged frozen sources and separately checked FULL receipts.',
        'new_research_experiments':0,'new_record_model_calls':0,'source_sha256':sha(str(Path(__file__).relative_to(ROOT)))}
    (OUT/'report_numbers_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','tables':len(checked),'boundary_distance':str(distance)},ensure_ascii=False))


if __name__ == '__main__':
    main()
