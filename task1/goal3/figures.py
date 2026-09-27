"""Publication figures from complete, hash-bound Goal 3 runs and decisions."""
import argparse
from collections import Counter
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np

from task1.scripts.build_goal2_figures import FigureSet
from task1.workflow.io import ROOT, digest, read_json, write_json, now
from .data import EV
from .runtime import read_rows, assert_binding
from .freezes import verified_run


def run_source(writer, key):
    directory = EV/'runs'/writer.current[key]
    verified_run(writer.current[key])
    manifest = read_json(writer.source(directory/'manifest.json'))
    assert_binding(manifest['bindings'])
    receipt_path = EV/'independent_c'/(manifest['run_id']+'_receipt.json')
    receipt = read_json(writer.source(receipt_path))
    if receipt['status'] != 'VERIFIED' or not any(t['sha256'] == digest(directory/'manifest.json')
                                                for t in receipt['targets']):
        raise ValueError('FIGURES_REQUIRE_CURRENT_INDEPENDENT_REVIEW')
    return directory, manifest


def comparison_figure(writer):
    _, manifest = run_source(writer, 'development')
    names = [n for n in manifest['strategy_ids'] if n != 'R0']
    data = []
    for name in names:
        p = manifest['comparisons'][name+'|R0']
        own = manifest['record_metrics'][name]
        data.append({'strategy': name, 'coverage_delta': p['coverage_delta'],
                     'protected': p['protected_records'], 'gain_records': p['strict_gain_records'],
                     'failed': len(p['failure_records']), 'final_points': own['n_final'],
                     'maximum_P_error_work_m': own['dp_max_error'], 'status': p['status']})
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 5.0), layout='constrained', sharey=True)
    y = np.arange(len(names))
    for ax, field, title, color in zip(axes, ('coverage_delta', 'gain_records', 'failed'),
            ('Additional common coverage\n(original points)', 'Strict improvement\n(records)',
             'Any fixed protection failure\n(records)'), ('C1', 'C2', 'C3')):
        vals = [d[field] for d in data]
        ax.barh(y, vals, color=writer.p[color], height=.66)
        ax.set_title(title, loc='left')
        ax.set_yticks(y, names)
        ax.grid(axis='x'); ax.set_axisbelow(True)
        ax.set_xlim(0, max(vals + [1])*1.22)
        for pos, val in zip(y, vals):
            ax.text(val + max(vals + [1])*.025, pos, f'{val:,}', va='center', fontsize=9)
    axes[0].invert_yaxis()
    fig.suptitle(f"Development · {len(manifest['input_ids'])} exposed records · all comparisons against R0", fontsize=13)
    writer.save(fig, 'development_candidates', data,
                'All registered single/combination observations including rejected diagnostics; no weighted score.')


def point_fates(writer):
    final = writer.current['final_strategy']
    scopes = [('confirmation', 'FINAL_CONFIRM'), ('production', 'FULL_PRODUCTION')]
    fig, axes = plt.subplots(2, 2, figsize=(10.7, 6.7), layout='constrained')
    data = {}
    fields = [('n_filtered', 'S filtered', 'C3'), ('n_direction_removed', 'D removed', 'C4'),
              ('n_dp_removed', 'P simplified', 'C2'), ('n_final', 'Stored output', 'C1')]
    for row, (key, title) in enumerate(scopes):
        _, manifest = run_source(writer, key)
        names = list(dict.fromkeys(['R0', final]))
        # A failed new candidate remains separately visible in confirmation, even after R0 release.
        if key == 'confirmation':
            names = manifest['strategy_ids']
        summaries = manifest['record_metrics']; ax = axes[row, 0]
        bottom = np.zeros(len(names)); points = summaries['R0']['n_input']
        for field, label, color in fields:
            values = np.array([summaries[n][field] for n in names])
            ax.barh(names, values/points, left=bottom/points, label=label, color=writer.p[color])
            bottom += values
        if any(v != points for v in bottom):
            raise ValueError('PLOT_POINT_FATE_DENOMINATOR_MISMATCH')
        ax.set(xlim=(0, 1), xlabel='Fraction of all original points')
        ax.set_title(f'{title}: {len(manifest["input_ids"]):,} records / {points:,} points', loc='left')
        ax.grid(axis='x'); ax.set_axisbelow(True)
        coverage = [summaries[n]['common_covered_points'] for n in names]
        stored = [summaries[n]['n_final'] for n in names]
        y = np.arange(len(names)); other = axes[row, 1]
        other.barh(y-.16, coverage, height=.29, color=writer.p['C2'], label='Common raw coverage')
        other.barh(y+.16, stored, height=.29, color=writer.p['C1'], label='Explicit stored points')
        other.set(yticks=y, yticklabels=names, xlabel='Original point identities / stored points')
        other.set_xlim(0, max(coverage + stored + [1])*1.28)
        for yy, values, off in ((y, coverage, -.16), (y, stored, .16)):
            for pos, value in zip(yy, values):
                other.text(value + points*.015, pos+off, f'{value:,}', va='center', fontsize=9)
        other.grid(axis='x'); other.set_axisbelow(True)
        data[key] = {'records': len(manifest['input_ids']), 'raw_points': points,
                     'summaries': {n: summaries[n] for n in names}}
    axes[0, 0].legend(loc='lower left', bbox_to_anchor=(0, 1.22), ncol=4, fontsize=8)
    axes[0, 1].legend(loc='lower left', bbox_to_anchor=(0, 1.22), fontsize=8)
    writer.save(fig, 'point_fates_and_coverage', data,
                'Point terminal states sum to raw input. Coverage and stored output are distinct. Final sample and production are separate.')


def confirmation_pairs(writer):
    directory, manifest = run_source(writer, 'confirmation')
    proposed = read_json(writer.source(EV/'final_freeze.json'))['primary_strategy']
    pairs = [row['comparisons'][proposed+'|R0'] for row in read_rows(directory)]
    valid = [p for p in pairs if p['baseline_common_max'] is not None
             and p['candidate_max_on_baseline_covered'] is not None]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5), layout='constrained')
    x = [p['baseline_common_max'] for p in valid]
    y = [p['candidate_max_on_baseline_covered'] for p in valid]
    axes[0].scatter(x, y, alpha=.35, s=15, color=writer.p['C1'], rasterized=False)
    high = max(x+y+[1]); axes[0].plot([0, high], [0, high], '--', color=writer.p['Muted'], lw=1)
    axes[0].set(xlabel='R0 max error on R0-covered points (work m)',
                ylabel=f'{proposed} max on the same set (work m)',
                title=f'Comparable records: {len(valid)}; null/unavailable: {len(pairs)-len(valid)}')
    groups = sorted({p['stratum'] for p in pairs})
    counts = []
    for group in groups:
        selected = [p for p in pairs if p['stratum'] == group]
        counts.append({'stratum': group, 'n': len(selected),
            'gain': sum(p['feasible'] and p['strict_gain'] for p in selected),
            'unchanged': sum(p['feasible'] and not p['strict_gain'] for p in selected),
            'failed': sum(not p['feasible'] for p in selected)})
    bottom = np.zeros(len(groups))
    for field, label, color in [('gain', 'Protected improvement', 'C1'),
                                ('unchanged', 'Protected, no gain', 'C2'), ('failed', 'Protection failure', 'C3')]:
        vals = np.array([r[field] for r in counts])
        axes[1].barh(groups, vals, left=bottom, color=writer.p[color], label=label); bottom += vals
    axes[1].set(xlabel='Original records; descriptive strata', title='All confirmation records remain in the denominator')
    axes[1].legend(loc='lower left', bbox_to_anchor=(0, 1.1), fontsize=8)
    axes[1].grid(axis='x'); axes[1].set_axisbelow(True)
    fig.suptitle(f'Frozen {proposed} vs R0 · one final confirmation · no tuning on this sample', fontsize=13)
    writer.save(fig, 'final_confirmation_pairs', {'proposed': proposed, 'pairs': pairs, 'strata': counts},
                'All paired final-confirmation records; missing geometry is excluded only from scatter, never from coverage or guard counts.')


def selection_tradeoffs(writer):
    directory, manifest = run_source(writer, 'selection')
    names = [cid for cid in manifest['strategy_ids'] if cid != 'R0']
    rows = list(read_rows(directory))
    counts, failures = [], []
    for cid in names:
        pairs = [row['comparisons'][cid+'|R0'] for row in rows]
        counts.append({'strategy': cid, 'gain': sum(p['strict_gain'] for p in pairs),
                       'unchanged': sum(p['feasible'] and not p['strict_gain'] for p in pairs),
                       'failed': sum(not p['feasible'] for p in pairs)})
        failures.extend({'strategy': cid, **p} for p in pairs if not p['feasible'])
    fig, axes = plt.subplots(1, 2, figsize=(10.7, 4.5), layout='constrained')
    left = np.zeros(len(names))
    for field, label, color in [('gain', 'Protected improvement', 'C1'),
                                ('unchanged', 'Protected, no gain', 'C2'), ('failed', 'Protection failure', 'C3')]:
        values = np.array([p[field] for p in counts])
        axes[0].barh(names, values, left=left, color=writer.p[color], label=label)
        left += values
    axes[0].set(xlim=(0, len(rows)), xlabel='Original records; all fixed protections applied')
    axes[0].legend(loc='lower left', bbox_to_anchor=(0, 1.05), fontsize=8)
    # Every actual failure is shown, including equal failures in both rule-containing strategies.
    comparable = [p for p in failures if p['baseline_common_max'] is not None
                  and p['candidate_max_on_baseline_covered'] is not None]
    if comparable:
        for y, p in enumerate(comparable):
            x0, x1 = p['baseline_common_max'], p['candidate_max_on_baseline_covered']
            axes[1].plot([x0, x1], [y, y], color=writer.p['Muted'], lw=1.4)
            axes[1].scatter(x0, y, color=writer.p['C1'], s=25, label='R0' if y == 0 else None)
            axes[1].scatter(x1, y, color=writer.p['C3'], s=25, label='Candidate on same set' if y == 0 else None)
        axes[1].set(yticks=range(len(comparable)),
                    yticklabels=[p['strategy']+' / '+p['record_id'] for p in comparable],
                    xlabel='Max geometry error on R0-covered points (work m)')
        axes[1].legend(loc='lower left', bbox_to_anchor=(0, 1.05), fontsize=8)
    else:
        axes[1].text(.5, .5, 'No comparable geometric protection failures',
                     ha='center', va='center', transform=axes[1].transAxes)
    for ax in axes:
        ax.grid(axis='x'); ax.set_axisbelow(True)
    fig.suptitle(f'G3_SELECTION · {len(rows)} records · frozen shortlist; all observed failures retained', fontsize=13)
    writer.save(fig, 'selection_tradeoffs', {'counts': counts, 'all_failures': failures,
                'plotted_failures': len(comparable), 'noncomparable_failures': len(failures)-len(comparable)},
                'Fixed-protection failures cannot be offset by gains on other records; no parameter change follows these outcomes.')


def trajectory_cases(writer):
    directory, _ = run_source(writer, 'production'); final = writer.current['final_strategy']
    # Deterministic descriptions after deployment freeze; never inputs to tuning.
    selected = {}
    for row in read_rows(directory):
        t = row['traces'][row['strategy_configs'][final]]
        p = row['comparisons'][final+'|R0']; m = t['metrics']
        keys = {'largest_coverage_gain': (p['coverage_delta'], row['record_id']),
                'largest_raw_geometry_error': (m['common_max_error'] if m['common_max_error'] is not None else -1, row['record_id']),
                'largest_new_coverage_error': (p['newly_covered_max_error'] if p['newly_covered_max_error'] is not None else -1, row['record_id'])}
        for label, key in keys.items():
            if label not in selected or key > selected[label][0]:
                selected[label] = (key, row)
    fig, axes = plt.subplots(3, 3, figsize=(11.3, 10.2), layout='constrained')
    cases = []
    labels = {'largest_coverage_gain': 'Largest coverage gain',
              'largest_raw_geometry_error': 'Largest raw-to-final error',
              'largest_new_coverage_error': 'Largest added-coverage error · local raw window'}
    for i, (criterion, (score, row)) in enumerate(selected.items()):
        r = row['traces'][row['strategy_configs']['R0']]
        f = row['traces'][row['strategy_configs'][final]]
        xy = np.array(r['source_record']['xy'])
        bounds = [0] + [b['to_index'] for b in r['metrics']['raw_boundaries']] + [len(xy)]
        visible = list(range(len(xy))); witness = None
        if criterion == 'largest_new_coverage_error' and score[0] >= 0:
            before = {p['index'] for p in r['metrics']['common_point_errors'] if p['error'] is not None}
            added = [p for p in f['metrics']['common_point_errors'] if p['error'] is not None and p['index'] not in before]
            witness = max(added, key=lambda p: (p['error'], p['index']))
            a, b = next((a, b) for a, b in zip(bounds, bounds[1:]) if a <= witness['index'] < b)
            visible = list(range(a, b))
        origin = xy[visible[0]]; local = xy-origin; visible_set = set(visible)
        raw_segments = [local[[k for k in range(a, b) if k in visible_set]] for a, b in zip(bounds, bounds[1:])
                        if any(k in visible_set for k in range(a, b))]
        for j, (name, trace) in enumerate([('Raw (original windows)', r), ('R0', r), (final, f)]):
            ax = axes[i, j]
            for seg in raw_segments:
                ax.plot(seg[:, 0], seg[:, 1], '-', color=writer.p['Muted'], lw=.7, alpha=.55)
            if j == 0:
                ax.scatter(local[visible, 0], local[visible, 1], s=8, color=writer.p['Muted'])
                stored = len(visible)
            else:
                stored = 0
                for seg in trace['final_segments']:
                    indices = [k for k in seg['indices'] if k in visible_set]
                    if not indices:
                        continue
                    arr = local[indices]; stored += len(indices)
                    ax.plot(arr[:, 0], arr[:, 1], '.-', ms=3, color=writer.p['C1'] if j == 1 else writer.p['C2'], lw=1)
                for action, marker, color in [('filtered', 'x', 'C3'), ('denoised', '+', 'C4')]:
                    pts = [a['original_index'] for a in trace['point_actions']
                           if a['action'] == action and a['original_index'] in visible_set]
                    if pts:
                        ax.scatter(local[pts, 0], local[pts, 1], marker=marker, s=14, linewidths=.6,
                                   color=writer.p[color], label=action)
            limits = np.ptp(local[visible], axis=0); pad = max(float(limits.max())*.12, 1)
            ax.set(xlim=(local[visible, 0].min()-pad, local[visible, 0].max()+pad),
                   ylim=(local[visible, 1].min()-pad, local[visible, 1].max()+pad),
                   xlabel='East offset (work m)', ylabel='North offset (work m)')
            ax.set_aspect('equal', adjustable='box'); ax.tick_params(labelsize=7)
            ax.set_title(f'{name} · shown points {stored}', loc='left', fontsize=10)
            if witness:
                for k in visible:
                    ax.annotate(str(k), local[k], xytext=(4, 4), textcoords='offset points', fontsize=8)
        axes[i, 0].text(0, 1.2, f'{labels[criterion]} · record {row["record_id"]}', transform=axes[i, 0].transAxes, fontsize=10)
        cases.append({'criterion': criterion, 'record_id': row['record_id'], 'criterion_value': score[0],
                      'origin_ENU_work_m': origin.tolist(), 'raw_xy_work_m': xy.tolist(),
                      'display_original_indices': visible, 'new_coverage_witness': witness,
                      'raw_breaks': r['metrics']['raw_boundaries'], 'reference': r, 'final': f})
    fig.get_layout_engine().set(rect=(0, .055, 1, .945))
    fig.legend(handles=[
        Line2D([], [], marker='x', color=writer.p['C3'], linestyle='None', label='S filtered'),
        Line2D([], [], marker='+', color=writer.p['C4'], linestyle='None', label='D removed'),
        Line2D([], [], marker='.', color=writer.p['C1'], label='Stored output (R0 blue / S0 orange)')],
        loc='lower center', bbox_to_anchor=(.5, .004), ncol=3, fontsize=9, frameon=False)
    fig.suptitle('Production examples selected by fixed descriptive extrema · no basemap · gaps remain disconnected', fontsize=12)
    writer.save(fig, 'production_trajectory_cases', cases,
                'Three deterministic post-freeze extrema; third row zooms the complete raw window containing the worst newly covered point. Same origin/limits within each row; crosses S-filtered, plus signs D-removed. No line reconnects raw breaks.')


def architecture(writer):
    nodes = [('user', 'Approved scope / user', .1, 5.0, 2.3, .8, 'C1'),
             ('a', 'A: evidence → TaskPlan', .1, 3.5, 2.3, .8, 'C2'),
             ('ctl', 'Deterministic controller\nqueue · hashes · budgets', 3.0, 3.5, 3.1, .8, 'C1'),
             ('b', 'B-Run\nfrozen numerical tools', 6.8, 3.5, 2.7, .8, 'C2'),
             ('c', 'C: independent review\nraw / contracts / actual output', 6.8, 1.7, 2.7, 1.0, 'C4'),
             ('repair', 'B-Repair\npatch → tests → new run', 3.0, 1.7, 3.1, 1.0, 'C3'),
             ('release', 'Confirm → full production\nreports / notebooks / ZIP', 3.0, .1, 3.1, 1.0, 'C1'),
             ('external', 'External: identity\nEvidence Master / GPT review\nuser submission decision', 6.8, .1, 2.7, 1.0, 'Muted')]
    links = [('user', 'a'), ('a', 'ctl'), ('ctl', 'b'), ('b', 'c'), ('c', 'repair'),
             ('repair', 'ctl'), ('c', 'release'), ('release', 'external'), ('c', 'ctl'), ('ctl', 'a')]
    fig, ax = plt.subplots(figsize=(11.3, 7.0)); ax.set(xlim=(-.1, 9.9), ylim=(-.15, 6.1)); ax.axis('off')
    diagram = ET.Element('mxfile', host='app.diagrams.net'); page = ET.SubElement(diagram, 'diagram', name='Actual Goal 3 workflow')
    model = ET.SubElement(page, 'mxGraphModel'); root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0'); ET.SubElement(root, 'mxCell', id='1', parent='0')
    lookup = {n[0]: n for n in nodes}
    for ident, label, x, y, w, h, color in nodes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.025,rounding_size=.06',
                                   facecolor=writer.p['Panel'], edgecolor=writer.p[color], lw=1.6))
        ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=10)
        cell = ET.SubElement(root, 'mxCell', id=ident, value=label, vertex='1', parent='1',
            style=f'rounded=1;whiteSpace=wrap;html=0;fillColor={writer.p["Panel"]};strokeColor={writer.p[color]};fontSize=16;')
        ET.SubElement(cell, 'mxGeometry', x=str(x*100), y=str((6-y-h)*100), width=str(w*100), height=str(h*100), **{'as': 'geometry'})
    for i, (start, end) in enumerate(links):
        s, t = lookup[start], lookup[end]
        if (start, end) == ('c', 'ctl'):
            # Reviewed development results return through the actual root/controller.
            points = [(9.5, 2.2), (9.78, 2.2), (9.78, 4.62), (4.55, 4.62), (4.55, 4.3)]
            ax.plot(*zip(*points[:-1]), color=writer.p['Muted'], lw=1.15)
            ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle='-|>',
                mutation_scale=13, lw=1.15, color=writer.p['Muted']))
            ax.text(6.9, 4.75, 'Reviewed development results · before freeze',
                    fontsize=8.5, ha='center')
            cell = ET.SubElement(root, 'mxCell', id=f'edge{i}', value='Reviewed development results; before freeze',
                source=start, target=end, edge='1', parent='1',
                style='edgeStyle=orthogonalEdgeStyle;endArrow=block;exitX=1;exitY=0.5;entryX=0.5;entryY=0;html=0;')
            geom = ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
            array = ET.SubElement(geom, 'Array', **{'as': 'points'})
            for x, y in points[1:-1]:
                ET.SubElement(array, 'mxPoint', x=str(x*100), y=str((6-y)*100))
            continue
        if (start, end) == ('ctl', 'a'):
            a, b = (3.0, 4.1), (2.4, 4.1)
            ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=13,
                                        lw=1.15, color=writer.p['Muted']))
            ax.text(2.7, 4.33, 'next plan', fontsize=8, ha='center')
            cell = ET.SubElement(root, 'mxCell', id=f'edge{i}', value='Next development plan only',
                source=start, target=end, edge='1', parent='1',
                style='edgeStyle=orthogonalEdgeStyle;endArrow=block;exitX=0;exitY=0.25;entryX=1;entryY=0.25;html=0;')
            ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
            continue
        dx, dy = t[2]+t[4]/2-s[2]-s[4]/2, t[3]+t[5]/2-s[3]-s[5]/2
        if abs(dx) > abs(dy)*1.1:
            a = (s[2]+(s[4] if dx>0 else 0), s[3]+s[5]/2)
            b = (t[2]+(0 if dx>0 else t[4]), t[3]+t[5]/2)
        else:
            a = (s[2]+s[4]/2, s[3]+(s[5] if dy>0 else 0))
            b = (t[2]+t[4]/2, t[3]+(0 if dy>0 else t[5]))
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=13, lw=1.15, color=writer.p['Muted']))
        cell = ET.SubElement(root, 'mxCell', id=f'edge{i}', source=start, target=end, edge='1', parent='1',
                             style='edgeStyle=orthogonalEdgeStyle;endArrow=block;html=0;')
        ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
    ax.text(.1, 5.95, 'Actual governance roles; record processing remains deterministic', fontsize=14)
    ax.text(.1, -.07, 'FINAL_CONFIRM never feeds A. C does not author the reviewed core. External gaps block dependent deliverables.', fontsize=8.5)
    path = writer.output/'goal3_actual_workflow.drawio'
    ET.ElementTree(diagram).write(path, encoding='utf-8', xml_declaration=True)
    writer.save(fig, 'goal3_actual_workflow', {'nodes': nodes, 'edges': links, 'drawio_sha256': digest(path)},
                'Native editable diagram of actual role, deterministic controller, independent review and repair boundaries; not invented dialogue.')


def decision_path(writer):
    history = read_json(writer.source(EV/'decision_history.json'))
    events = history['events']
    fig, ax = plt.subplots(figsize=(10.6, max(4.0, len(events)*.92)))
    ax.set(xlim=(0, 10), ylim=(-.4, len(events))); ax.axis('off')
    for i, event in enumerate(events):
        y = len(events)-1-i
        ax.text(.1, y+.24, event['stage'], fontsize=10, va='center')
        ax.add_patch(FancyBboxPatch((2.2, y), 2.0, .52, boxstyle='round,pad=.02',
                                   facecolor=writer.p['Panel'], edgecolor=writer.p['C1'], lw=1.4))
        ax.text(3.2, y+.26, event['incumbent'], va='center', ha='center', fontsize=12)
        ax.text(4.55, y+.26, event['reading'], va='center', fontsize=9)
        if i:
            ax.add_patch(FancyArrowPatch((3.2, y+1), (3.2, y+.57), arrowstyle='-|>',
                                       mutation_scale=12, color=writer.p['Muted']))
    ax.set_title('Actual decision path · labels are gates and readings, not a quality score', loc='left', fontsize=13)
    writer.save(fig, 'incumbent_decision_path', history,
                'Version-bound actual autonomous decisions under the approved policy; engineering repair is not represented as quality gain.')


def build(output):
    writer = FigureSet(EV/'current_runs.json', output, 'Goal 3 conditional trajectory processing')
    writer.source(Path(__file__))
    writer.source(ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex')
    comparison_figure(writer); selection_tradeoffs(writer); point_fates(writer); confirmation_pairs(writer)
    trajectory_cases(writer); architecture(writer); decision_path(writer)
    write_json(writer.output/'figure_data.json', writer.data)
    result = {'created_at': now(), 'sources': writer.sources, 'figures': writer.figures,
              'figure_data_sha256': digest(writer.output/'figure_data.json'),
              'source_crs': 'UNVERIFIED', 'units': 'conditional working metres',
              'visual_inspection': 'PENDING_ACTUAL_IMAGE_REVIEW'}
    write_json(writer.output/'figure_manifest.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'task1/figures/goal3')
    args = parser.parse_args(); result = build(args.output)
    print({'figures': len(result['figures']), 'visual_inspection': result['visual_inspection']})
