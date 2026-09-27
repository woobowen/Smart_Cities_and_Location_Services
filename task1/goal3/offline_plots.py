"""Figures from this execution's raw-derived readings and new trace shards only."""
from collections import Counter, defaultdict
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from task1.workflow.io import ROOT, digest, read_json, write_json
from task1.workflow.g2_selection import REFERENCE

COUNTS = ('n_input', 'n_final', 'n_filtered', 'n_direction_removed', 'n_dp_removed',
          'n_dp_input', 'n_dp_output', 'common_covered_points', 'raw_break_crossings')
METRICS = COUNTS + ('n_records', 'n_no_output_records', 'n_all_filtered_records',
                   'common_coverage', 'point_retention', 'dp_saving', 'dp_max_error',
                   'common_max_error', 'no_output', 'all_filtered',
                   'direction_windows_across_raw_breaks', 'p_removed_raw_break_trigger_points')
MODES = ['llm-only', 'search-only', 'llm+search', 'llm+memory+search']


def compact_metrics(metrics):
    return {key: metrics[key] for key in METRICS if key in metrics}


def palette():
    path = ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex'
    colors = dict(re.findall(r'\\definecolor\{(\w+)\}\{HTML\}\{([0-9A-Fa-f]{6})\}', path.read_text()))
    if not {'Paper', 'Ink', 'Muted', 'Rule', 'C1', 'C2', 'C3', 'C4'} <= set(colors):
        raise ValueError('P2_PUBLIC_COLOR_DEFINITIONS_MISSING')
    return {key: '#'+value for key, value in colors.items()}, digest(path)


def theme(colors):
    return {'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 10,
            'axes.labelsize': 9, 'figure.titlesize': 13, 'text.color': colors['Ink'],
            'axes.labelcolor': colors['Ink'], 'xtick.color': colors['Ink'], 'ytick.color': colors['Ink'],
            'axes.spines.top': False, 'axes.spines.right': False,
            'grid.color': colors['Rule'], 'grid.linewidth': .6,
            'figure.facecolor': 'white', 'axes.facecolor': 'white',
            'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
            'svg.hashsalt': 'sc-lab1-offline-recompute-v1'}


def save_figure(figure, directory, name, caption):
    files = {}
    for suffix in ('svg', 'pdf', 'png'):
        path = directory/(name+'.'+suffix)
        metadata = {'Date': None} if suffix == 'svg' else {'CreationDate': None, 'ModDate': None} if suffix == 'pdf' else None
        figure.savefig(path, dpi=300, bbox_inches='tight', metadata=metadata)
        files[suffix] = {'path': path.name, 'sha256': digest(path), 'bytes': path.stat().st_size}
    plt.close(figure)
    return {'name': name, 'caption': caption, 'files': files}


def finish(directory, data, figures, palette_hash):
    write_json(directory/'plot_data.json', data)
    manifest = {'classification': 'NEW_FIGURES_FROM_THIS_RAW_RECOMPUTATION',
        'plot_data_path': 'plot_data.json', 'plot_data_sha256': digest(directory/'plot_data.json'),
        'palette_source': 'templates/latex/common/p2_cloud_sorbet_colors.tex',
        'palette_sha256': palette_hash, 'source_sha256': digest(__file__), 'figures': figures,
        'formats': ['SVG', 'PDF', 'PNG_300_DPI'], 'old_summary_or_figure_read_for_plotting': False,
        'units': 'conditional working metres, original point identities and stored points',
        'source_crs': 'UNVERIFIED', 'visual_inspection': 'NOT_CLAIMED_BY_GENERATOR'}
    write_json(directory/'figure_manifest.json', manifest)
    return {'figure_count': len(figures), 'manifest_path': 'figures/figure_manifest.json',
            'manifest_sha256': digest(directory/'figure_manifest.json'),
            'plot_data_sha256': manifest['plot_data_sha256'],
            'lineage': 'newly recomputed raw results; historical targets used only for equality checks'}


def fraction(numerator, denominator):
    return 100*numerator/denominator if denominator else np.nan


def parameter_figure(tasks, colors):
    phases = sorted({row['partition'] for row in tasks if 'parameters' in row['source_run_id']})
    if not phases:
        raise ValueError('NEW_PARAMETER_READINGS_REQUIRED')
    fig, axes = plt.subplots(len(phases), 3, figsize=(11.4, 3.35*len(phases)), squeeze=False, layout='constrained')
    for i, phase in enumerate(phases):
        rows = [r for r in tasks if r['partition'] == phase and 'parameters' in r['source_run_id']]
        reference = [r for r in rows if r['parameters'] == REFERENCE]
        for col, (group, keys) in enumerate([('S / filtering', {'dt', 'distance', 'min_points', 'min_length'}),
                                          ('D / direction', {'direction'}), ('P / simplification', {'dp'})]):
            ax = axes[i, col]
            selected = [r for r in rows if {k for k in REFERENCE if r['parameters'][k] != REFERENCE[k]} <= keys]
            if col == 0:
                for row in selected:
                    m = row['summary_from_new_raw_results']
                    is_r0 = row['parameters'] == REFERENCE
                    ax.scatter(fraction(m['n_final'], m['n_input']), fraction(m['common_covered_points'], m['n_input']),
                               s=58 if is_r0 else 28, marker='D' if is_r0 else 'o',
                               color=colors['Ink'] if is_r0 else colors['C1'], alpha=1 if is_r0 else .65)
                ax.set(xlabel='Explicit stored points (% raw)', ylabel='Common raw coverage (%)')
                ax.set_xlim(left=0); ax.set_ylim(0, 103)
                ax.text(.03, .04, 'Diamond: R0; circles: registered S settings', transform=ax.transAxes, fontsize=7)
            elif col == 1:
                selected.sort(key=lambda r: r['parameters']['direction'])
                for field, label, color, marker in [('common_covered_points', 'Common coverage', 'C1', 'o'),
                                                      ('n_final', 'Stored points', 'C2', 's')]:
                    ax.plot([r['parameters']['direction'] for r in selected],
                            [fraction(r['summary_from_new_raw_results'][field], r['summary_from_new_raw_results']['n_input']) for r in selected],
                            color=colors[color], marker=marker, label=label)
                ax.set(xlabel='Direction threshold (degrees)', ylabel='Fraction of original points (%)', ylim=(0, 103))
                ax.legend(fontsize=7, loc='lower right')
            else:
                for row in selected:
                    m = row['summary_from_new_raw_results']
                    if m['dp_max_error'] is None:
                        continue
                    x, y = m['dp_max_error'], fraction(m['n_dp_input']-m['n_dp_output'], m['n_dp_input'])
                    ax.scatter(x, y, marker='D' if row['parameters'] == REFERENCE else 'o',
                               s=42, color=colors['Ink'] if row['parameters'] == REFERENCE else colors['C4'])
                    ax.annotate(str(row['parameters']['dp']), (x, y), xytext=(4, 3), textcoords='offset points', fontsize=7)
                ax.axvline(5, linestyle='--', color=colors['C3'], linewidth=1)
                ax.set(xlabel='Actual immediate P max error (work m)', ylabel='P saving (% of complete P input)', ylim=(0, 103), xlim=(0, None))
                ax.text(.03, .04, 'Labels: dp; dashed: common 5 work m budget', transform=ax.transAxes, fontsize=7)
            count = reference[0]['summary_from_new_raw_results']['n_records'] if reference else rows[0]['summary_from_new_raw_results']['n_records']
            ax.set_title(f'{phase} · {group}\n{count} records; {len(selected)} configurations', loc='left')
            ax.grid(); ax.set_axisbelow(True)
    fig.suptitle('Historical parameter experiments · newly recomputed from raw')
    return fig


def order_figure(tasks, colors):
    rows = [r for r in tasks if 'orders' in r['source_run_id']]
    phases = sorted({r['partition'] for r in rows})
    if not phases:
        raise ValueError('NEW_ORDER_READINGS_REQUIRED')
    fig, axes = plt.subplots(len(phases), 2, figsize=(10.6, 3.5*len(phases)), squeeze=False, layout='constrained')
    for i, phase in enumerate(phases):
        group = [r for r in rows if r['partition'] == phase]
        names = [r['order'] for r in group]
        for j, (field, label, color) in enumerate([('common_covered_points', 'Common raw coverage (%)', 'C1'),
                                                 ('raw_break_crossings', 'Final edges crossing original breaks', 'C3')]):
            vals = [r['summary_from_new_raw_results'][field] for r in group]
            if j == 0:
                vals = [fraction(v, r['summary_from_new_raw_results']['n_input']) for v, r in zip(vals, group)]
            ax = axes[i, j]; ax.bar(names, vals, color=colors[color])
            ax.set(ylabel=label); ax.tick_params(axis='x', labelrotation=25)
            ax.set_ylim(0, max(vals+[1])*1.2); ax.grid(axis='y'); ax.set_axisbelow(True)
            for x, value in enumerate(vals):
                ax.text(x, value+max(vals+[1])*.025, f'{value:.1f}' if j == 0 else str(value), ha='center', fontsize=8)
            ax.set_title(f'{phase} · {group[0]["summary_from_new_raw_results"]["n_records"]} records per order', loc='left')
    fig.suptitle('Historical order experiments · only actually recomputed orders shown')
    return fig


def mode_figure(episodes, colors):
    groups = defaultdict(list)
    for row in episodes:
        groups[(row['partition'], row['mode'])].append(row)
    phases = sorted({key[0] for key in groups})
    if not phases:
        raise ValueError('NEW_SELECTED_EPISODE_READINGS_REQUIRED')
    pooled = []
    fig, axes = plt.subplots(len(phases), 3, figsize=(12.0, 3.6*len(phases)), squeeze=False, layout='constrained')
    for i, phase in enumerate(phases):
        modes = [m for m in MODES if (phase, m) in groups]
        totals = []
        for mode in modes:
            rows = groups[(phase, mode)]
            counts = {key: sum(r['new_selected_metrics'][key] for r in rows) for key in COUNTS}
            ref = {key: sum(r['new_R0_metrics'][key] for r in rows) for key in COUNTS}
            item = {'partition': phase, 'mode': mode, 'record_episode_observations': len(rows),
                    'original_records': len({r['record_id'] for r in rows}), 'selected': counts, 'R0': ref,
                    'strict_protected_gain': sum(r['new_comparison']['strict_gain'] for r in rows),
                    'protection_failed': sum(not r['new_comparison']['feasible'] for r in rows)}
            pooled.append(item); totals.append(item)
        labels = [m.replace('llm', 'LLM').replace('+', ' + ') for m in modes]
        for j, (field, label, color) in enumerate([('common_covered_points', 'Common raw coverage (%)', 'C1'),
                                                 ('n_final', 'Explicit stored points (% raw)', 'C2'),
                                                 ('strict_protected_gain', 'Strict protected gain (% observations)', 'C4')]):
            vals = [fraction(t['selected'][field], t['selected']['n_input']) if j < 2 else
                    fraction(t[field], t['record_episode_observations']) for t in totals]
            ax = axes[i, j]; ax.barh(labels, vals, color=colors[color]); ax.invert_yaxis()
            ax.set(xlabel=label, xlim=(0, 108)); ax.grid(axis='x'); ax.set_axisbelow(True)
            for y, value in enumerate(vals):
                ax.text(value+1, y, f'{value:.1f}', va='center', fontsize=8)
            ax.set_title(f'{phase} · n={totals[0]["record_episode_observations"]} per mode', loc='left')
    fig.suptitle('Four historical modes · recomputed retained episodes · no new model calls')
    return fig, pooled


def historical_plots(output, topic, tasks, episodes, provenance):
    directory = Path(output)/'figures'; directory.mkdir(parents=True, exist_ok=True)
    colors, color_hash = palette(); figures = []
    data = {'classification': 'ENGINEERING_PLOT_SMOKE_REAL_EXPOSED_INPUTS' if provenance.get('engineering_smoke') else 'HISTORICAL_G2_RAW_RECOMPUTE_NOT_NEW_LIVE',
            'provenance': provenance, 'tasks_from_new_results': tasks, 'episodes_from_new_results': episodes,
            'unavailable': 'null remains unavailable; never interpreted as zero geometry error'}
    with plt.rc_context(theme(colors)):
        def scope_label(figure):
            if provenance.get('engineering_smoke'):
                figure.suptitle('Engineering smoke · '+figure._suptitle.get_text(), fontsize=10)
            return figure
        if topic == 'parameters':
            figures.append(save_figure(scope_label(parameter_figure(tasks, colors)), directory, 'recomputed_parameters',
                'S coverage is not cleanliness; D fractions use raw points; P saving uses its complete immediate input. No noise truth.'))
            figures.append(save_figure(scope_label(order_figure(tasks, colors)), directory, 'recomputed_orders',
                'All historically run orders retained, including unsafe orders. Break counts and common coverage use fixed raw windows.'))
        elif topic == 'modes':
            figure, pooled = mode_figure(episodes, colors); data['pooled_mode_readings'] = pooled
            figures.append(save_figure(scope_label(figure), directory, 'recomputed_modes',
                'All originally selected record–episode outputs; repeated records are not independent samples; proposals remain historical.'))
        else:
            raise ValueError('UNKNOWN_RECOMPUTE_PLOT_TOPIC')
    return finish(directory, data, figures, color_hash)


def production_plots(output):
    from .runtime import read_rows
    output = Path(output); manifest = read_json(output/'manifest.json')
    if not manifest.get('recompute') or manifest['status'] != 'MACHINE_VERIFIED_PENDING_C':
        raise ValueError('NEW_COMPLETED_RECOMPUTE_TRACES_REQUIRED')
    if manifest['partition'] not in ('FULL_PRODUCTION', 'ENGINEERING_SMOKE_EXPOSED_PILOT'):
        raise ValueError('UNREGISTERED_RECOMPUTE_PLOT_SCOPE')
    engineering_smoke = manifest['partition'] == 'ENGINEERING_SMOKE_EXPOSED_PILOT'
    names = manifest['strategy_ids']; other = [name for name in names if name != 'R0']
    if 'R0' not in names or len(other) > 1:
        raise ValueError('PRODUCTION_REQUIRES_R0_AND_ONE_DEPLOYED_STRATEGY')
    final = other[0] if other else 'R0'
    totals = {name: Counter() for name in names}; readings = []; chosen = None; best = None
    for row in read_rows(output):
        trace_readings = {}
        for name in names:
            trace = row['traces'][row['strategy_configs'][name]]; m = trace['metrics']
            actions = Counter(p['action'] for p in trace['point_actions'])
            fate = {'n_filtered': actions['filtered'], 'n_direction_removed': actions['denoised'],
                    'n_dp_removed': actions['simplified'], 'n_final': actions['retained']}
            if any(fate[k] != m[k] for k in fate) or sum(fate.values()) != m['n_input']:
                raise ValueError('NEW_TRACE_POINT_FATE_MISMATCH')
            totals[name].update({key: m[key] for key in COUNTS}); totals[name]['n_records'] += 1
            trace_readings[name] = {key: m[key] for key in COUNTS}
        readings.append({'record_id': row['record_id'], 'new_trace_metrics': trace_readings})
        gain = row['comparisons'][final+'|R0']['coverage_delta']
        score = (gain, -int(row['record_id']))
        if best is None or score > best:
            best, chosen = score, row
    for name in names:
        if any(totals[name][key] != manifest['record_metrics'][name][key] for key in (*COUNTS, 'n_records')):
            raise ValueError('NEW_TRACE_PLOT_AGGREGATION_MISMATCH')
    if chosen is None:
        raise ValueError('NO_PRODUCTION_TRACE_FOR_PLOT')
    directory = output/'figures'; directory.mkdir(parents=True, exist_ok=True)
    colors, color_hash = palette(); figures = []
    data = {'classification': manifest['partition']+'_NEW_RAW_RECOMPUTE',
            'new_manifest_sha256': digest(output/'manifest.json'),
            'new_shard_sha256': [s['sha256'] for s in manifest['shards']],
            'record_readings_from_new_shards': readings, 'totals_from_new_shards': dict(totals),
            'case_selection': 'maximum new coverage versus R0, lowest numeric record ID tie; descriptive post-freeze display only',
            'case': {'record_id': chosen['record_id'], 'coverage_delta': best[0],
                     'R0': chosen['traces'][chosen['strategy_configs']['R0']],
                     'deployed_id': final, 'deployed': chosen['traces'][chosen['strategy_configs'][final]]}}
    with plt.rc_context(theme(colors)):
        fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.2), layout='constrained')
        raw_points = totals['R0']['n_input']; bottom = np.zeros(len(names))
        for field, label, color in [('n_filtered', 'S filtered', 'C3'), ('n_direction_removed', 'D removed', 'C4'),
                                     ('n_dp_removed', 'P simplified', 'C2'), ('n_final', 'Stored output', 'C1')]:
            vals = np.array([totals[n][field] for n in names])/raw_points*100
            axes[0].barh(names, vals, left=bottom, color=colors[color], label=label); bottom += vals
        axes[0].set(xlim=(0, 100), xlabel='All original points (%)')
        axes[0].legend(loc='upper center', bbox_to_anchor=(.5, 1.24), ncol=2, fontsize=8)
        y = np.arange(len(names))
        for field, label, color, offset in [('common_covered_points', 'Common raw coverage', 'C2', -.16),
                                          ('n_final', 'Explicit stored points', 'C1', .16)]:
            vals = [totals[n][field] for n in names]
            axes[1].barh(y+offset, vals, height=.28, color=colors[color], label=label)
        axes[1].set(yticks=y, yticklabels=names, xlabel='Original point identities / stored points')
        axes[1].legend(loc='upper center', bbox_to_anchor=(.5, 1.24), fontsize=8)
        for ax in axes: ax.grid(axis='x'); ax.set_axisbelow(True)
        scope_label = 'Engineering smoke' if engineering_smoke else 'New full recomputation'
        fig.suptitle(f'{scope_label} · {totals["R0"]["n_records"]:,} records / {raw_points:,} raw points')
        figures.append(save_figure(fig, directory, 'recomputed_point_fates',
            'Terminal counts are independently reduced from newly written point actions; coverage is distinct from explicit stored output.'))
        fig, axes = plt.subplots(1, 3, figsize=(11.3, 4.35), layout='constrained')
        r, f = data['case']['R0'], data['case']['deployed']; xy = np.array(r['source_record']['xy'])
        origin = xy[0]; local = xy-origin
        bounds = [0]+[b['to_index'] for b in r['metrics']['raw_boundaries']]+[len(xy)]
        for j, (label, trace) in enumerate([('Raw', r), ('R0', r), (final, f)]):
            ax = axes[j]
            for a, b in zip(bounds, bounds[1:]):
                ax.plot(local[a:b, 0], local[a:b, 1], '.-', ms=2, linewidth=.6, color=colors['Muted'], alpha=.55)
            if j:
                for segment in trace['final_segments']:
                    arr = np.array(segment['xy'])-origin
                    ax.plot(arr[:, 0], arr[:, 1], '.-', ms=4, linewidth=1, color=colors['C1' if j == 1 else 'C2'])
            span = np.ptp(local, axis=0); pad = max(float(span.max())*.06, 1)
            ax.set(xlabel='East offset (work m)', ylabel='North offset (work m)',
                   xlim=(local[:, 0].min()-pad, local[:, 0].max()+pad),
                   ylim=(local[:, 1].min()-pad, local[:, 1].max()+pad))
            ax.set_aspect('equal', adjustable='box'); ax.set_title(f'{label} · {len(xy) if j == 0 else trace["metrics"]["n_final"]} stored', loc='left')
        fig.suptitle(f'{"Engineering smoke" if engineering_smoke else "New raw / R0 / deployed trace"} · record {chosen["record_id"]} · original gaps stay disconnected')
        figures.append(save_figure(fig, directory, 'recomputed_trajectory_case',
            'One fixed descriptive case after production; identical origin/axis limits, no basemap, no bridging original raw breakpoints.'))
    return finish(directory, data, figures, color_hash)
