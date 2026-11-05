"""Independent report-cell check against run records, not the table generator.

This is a report audit. Mathematical verification of raw EA/online/RL outputs
is recorded separately by the actual independent reviewers.
"""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
seen = {}
checks = []


def path(rel):
    p = ROOT / rel
    seen[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return p


def records(rel):
    return pd.DataFrame(json.loads(path(rel).read_text()))


def table_rows(name):
    text = path(f'task2/reports/generated/{name}.tex').read_text()
    return [line.removesuffix(r'\\').split(' & ') for line in text.splitlines()
            if ' & ' in line and line.endswith(r'\\')]


def fmt(value, digits):
    return '--' if pd.isna(value) else f'{value:,.{digits}f}'


def compare(label, actual, wanted):
    if actual != wanted:
        raise AssertionError((label, actual, wanted))
    checks.append(label)


def main():
    for phase in ('development', 'confirmation'):
        d = pd.read_csv(path(f'task2/results/online/{phase}_v1/metrics.csv'))
        d = d[d.scenario.eq('teacher')]
        methods = ['TBG_g2', 'TBG_g5', 'BB_recycle_t1', 'BBmax_recycle_t1',
                   'BB_discard_t0.5', 'offline_sum', 'offline_max']
        printed = table_rows(f'online_{phase}_table')
        compare(phase + ': row count', len(printed), len(methods))
        for row, method in zip(printed, methods):
            a = d[d.method.eq(method)]
            compare(phase + method + ': seed count', len(a), 5)
            for cell, col, decimals in zip(row[1:],
                    ['match_rate', 'avg_delay', 'max_delay', 'p95_delay', 'ratio_max'],
                    [2, 3, 3, 3, 3]):
                compare(phase + method + col, cell, fmt(a[col].mean(), decimals))

    e = json.loads(path('task2/results/evolution/metrics.json').read_text())['rows']
    for row in table_rows('evolution_table'):
        problem, algorithm = row[:2]
        n_obj = 2 if problem == '派单2D' else 3
        a = [r for r in e if r['stage'] == 'baseline'
             and r['algorithm'] == {'NSGA-II': 'nsga2', 'NSGA-III': 'nsga3',
                                    'NSGA-2': 'nsga2', 'NSGA-3': 'nsga3'}[algorithm]
             and r['n_obj'] == n_obj
             and (r['batch_id'].startswith('dtlz') if problem == 'DTLZ2'
                  else r['batch_id'] == 'inner_hour18_batchseed2024')]
        compare(problem + algorithm + ': five runs', len(a), 5)
        hv = np.array([r['metrics']['HV'] for r in a])
        wanted = f'{hv.mean():.6f} $\\pm$ {hv.std(ddof=1):.6f}'
        compare(problem + algorithm + ': HV', row[2], wanted)
        compare(problem + algorithm + ': spacing', row[3],
                fmt(np.mean([r['metrics']['Spacing_cv'] for r in a]), 3))
        compare(problem + algorithm + ': EA time', row[4],
                fmt(np.mean([r['runtime'] for r in a]), 3))
    for row in table_rows('evolution_confirmation_table'):
        seed = row[0]
        a = [r for r in e if r['batch_id'] == 'test_hour18_batchseed' + seed
             and r['algorithm'] == 'nsga2']
        compare('future' + seed + ': pair', len(a), 2)
        by = {}
        for r in a:
            raw = json.loads(path(r['path']).read_text())
            by['hybrid' if raw['initialization'].startswith('km') else 'teacher'] = r['metrics']['HV']
        for index, key in [(1, 'teacher'), (2, 'hybrid')]:
            compare('future' + seed + key, row[index], fmt(by[key], 6))
        compare('future' + seed + ': difference', row[3], f"{by['hybrid']-by['teacher']:+.6f}")

    conditions = {'基线': ('baseline', 100, 300), '种群200': ('scale', 200, 300),
                  '代数600': ('scale', 100, 600), 'KM初始': ('hybrid', 100, 300),
                  'KM+种群': ('combination', 200, 300)}
    for row in table_rows('evolution_budget_table'):
        algorithm = 'nsga2' if row[0] == 'II' else 'nsga3'
        stage, pop, gen = conditions[row[1]]
        a = [r for r in e if r['algorithm'] == algorithm and r['stage'] == stage
             and r['batch_id'] == 'inner_hour18_batchseed2024'
             and r['n_obj'] == 2 and r['pop_size'] == pop and r['n_gen'] == gen]
        compare('budget' + row[0] + row[1] + ': n5', len(a), 5)
        for cell, metric, decimals in [(row[2], 'HV', 6), (row[3], 'Spacing_cv', 3)]:
            compare('budget' + row[0] + row[1] + metric,
                    cell, fmt(np.mean([r['metrics'][metric] for r in a]), decimals))
        nfe = {r['n_eval'] for r in a}
        extra = {r['total_objective_evals'] - r['n_eval'] for r in a}
        assert len(nfe) == len(extra) == 1
        wanted = f'{nfe.pop():,}'
        add = extra.pop()
        if add:
            wanted += f'(+{add})'
        compare('budget' + row[0] + row[1] + ': objective evals', row[4], wanted)
        compare('budget' + row[0] + row[1] + ': total time', row[5],
                fmt(np.mean([r['total_runtime'] for r in a]), 3))

    policy_map = {'最近': 'greedy', 'KM即时': 'km', 'Q-KM': 'qkm'}
    for row in table_rows('rl_fleet_table'):
        fleet = int(row[0])
        d = records(f'task2/results/rl/final_v1/fleet{fleet}/day_metrics.json')
        a = d[d.policy.eq(policy_map[row[1]])]
        compare('RL fleet' + row[0] + row[1] + ': days', len(a), 5)
        for cell, col, decimals in zip(row[2:],
                ['revenue', 'answer_rate', 'avg_pickup', 'completed_revenue'], [2, 4, 3, 2]):
            compare('RL fleet' + row[0] + row[1] + col, cell, fmt(a[col].mean(), decimals))
    enhancement = records('task2/results/rl/final_v1/enhancements/day_metrics.json')
    labels = {'Q-KM参考': 'qkm', 'KM父项': 'km', 'KM+调度3': 'km_move3',
              'Q-KM+调度3': 'qkm_move3', 'Q-KM+调度5': 'qkm_move5',
              'Q(beta1)': 'q_beta1', 'Double(beta1)': 'double_beta1',
              '融合膝点': 'qnsga_knee', '融合约束': 'qnsga_constraint'}
    for row in table_rows('rl_enhancement_table'):
        a = enhancement[enhancement.policy.eq(labels[row[0]])]
        compare(row[0] + ': n5', len(a), 5)
        for cell, col, decimals in zip(row[1:], ['revenue', 'answer_rate', 'avg_pickup', 'empty_km'], [2, 4, 3, 2]):
            compare(row[0] + col, cell, fmt(a[col].mean(), decimals))

    sensitivity = {
        '原参考': 'development_v1/baseline_f60_s2024',
        'gamma=.8': 'sensitivity_v1/gamma08_validation',
        'gamma=.95': 'sensitivity_v1/gamma095_validation',
        'grid=6': 'sensitivity_v1/grid6_validation',
        'grid=10': 'sensitivity_v2_rngfix/grid10_validation',
        'patience=1': 'sensitivity_v2_rngfix/patience1_validation',
        'patience=3': 'sensitivity_v2_rngfix/patience3_validation',
    }
    for row in table_rows('rl_sensitivity_table'):
        d = records(f'task2/results/rl/{sensitivity[row[0]]}/day_metrics.json')
        a = d[d.policy.eq('qkm')]
        compare(row[0] + ': validation n5', len(a), 5)
        for cell, col, decimals in zip(row[1:], ['revenue', 'answer_rate', 'avg_pickup'], [2, 4, 3]):
            compare(row[0] + col, cell, fmt(a[col].mean(), decimals))
    for row, rel in zip(table_rows('offset_table'),
            ['development_v1/baseline_f60_s2024', 'offset_robustness_v1/validation']):
        d = records(f'task2/results/rl/{rel}/day_metrics.json')
        a = d[d.policy.eq('qkm')]
        for cell, col, decimals in zip(row[1:], ['revenue', 'answer_rate', 'avg_pickup'], [2, 4, 3]):
            compare(row[0] + col, cell, fmt(a[col].mean(), decimals))

    # The two Monte Carlo samples are paired independently and never pooled.
    effects = {}
    for name, d in [('first5', enhancement), ('additional20', records('task2/results/rl/final_montecarlo_v1/day_metrics.json'))]:
        a = d[d.policy.eq('km_move3')].set_index('day_seed')
        b = d[d.policy.eq('qkm')].set_index('day_seed')
        assert a.index.equals(b.index)
        diff = a.revenue - b.revenue
        margin = t.ppf(.975, len(diff)-1) * diff.std(ddof=1) / np.sqrt(len(diff))
        effects[name] = dict(n=len(diff), mean=float(diff.mean()),
                            lower=float(diff.mean()-margin), upper=float(diff.mean()+margin),
                            extra_empty_km=float(a.empty_km.mean()))
    expected = {'first5': ['640.81', '-64.07', '1345.68', '826.55'],
                'additional20': ['435.45', '141.68', '729.23', '848.08']}
    for name, wanted in expected.items():
        a = effects[name]
        compare(name + ': prose mean/CI/movement',
                [f'{a[k]:.2f}' for k in ('mean', 'lower', 'upper', 'extra_empty_km')], wanted)
    # The second table includes the explicitly hypothetical cost diagnostic.
    mc_rows = table_rows('rl_montecarlo_table')
    for offset, (name, d) in enumerate([
            ('first5', enhancement),
            ('additional20', records('task2/results/rl/final_montecarlo_v1/day_metrics.json'))]):
        a = d[d.policy.eq('km_move3')].set_index('day_seed')
        b = d[d.policy.eq('qkm')].set_index('day_seed')
        for index, net in enumerate([False, True]):
            row = mc_rows[offset * 2 + index]
            diff = a.revenue - b.revenue
            if net:
                diff -= a.empty_km - b.empty_km
            margin = t.ppf(.975, len(diff)-1) * diff.std(ddof=1) / np.sqrt(len(diff))
            compare(name + str(net) + ': table n', row[1], str(len(diff)))
            compare(name + str(net) + ': table effect', row[3], fmt(diff.mean(), 2))
            compare(name + str(net) + ': table CI', row[4],
                    '[' + fmt(diff.mean()-margin, 2) + ', ' + fmt(diff.mean()+margin, 2) + ']')
    # Narrative percentages refer to corresponding fleet's immediate KM.
    percentages = {}
    for fleet in (40, 60, 100):
        d = records(f'task2/results/rl/final_v1/fleet{fleet}/day_metrics.json')
        means = d.groupby('policy').revenue.mean()
        percentages[fleet] = float(100 * (means.qkm / means.km - 1))
    compare('fleet60 percent', f'{percentages[60]:.2f}', '2.47')
    compare('fleet100 percent', f'{percentages[100]:.2f}', '-3.59')
    receipt = dict(actual_utc=datetime.now(timezone.utc).isoformat(),
                   reviewer='/root/research_data', status='NUMERICAL_CELLS_PASS',
                   scope='10 generated tables and selected RL narrative effects; mathematical raw-run audits remain separately attributed',
                   checks_count=len(checks), checks=checks, effects=effects,
                   fleet_relative_percent=percentages, input_sha256=seen,
                   verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'report_numbers_round2.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(json.dumps({k:receipt[k] for k in ['status','checks_count','effects','fleet_relative_percent']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
