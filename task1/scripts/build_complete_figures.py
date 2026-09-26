"""P2 figures from one registered current conditional pilot, without model calls.

The architecture's draw.io XML is the geometry source for SVG/PDF/PNG. Trajectory
lines come only from actual processed segments; no raw points are joined across
cuts, records or filtered segments. Existing historical figures are preserved.
"""
from pathlib import Path
import argparse
import json
import re
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import MaxNLocator

from task1.workflow.io import ROOT, DATA, CONFIG, EVIDENCE, digest, object_hash, read_json, write_json, bound_path

REVISION = EVIDENCE / 'revisions/SC-LAB1-G1-COMPLETE-001'
FIGURE_NAMES = ('conditional_pilot_trajectories', 'point_terminal_counts', 'goal1_execution_structure')


def palette():
    text = (ROOT / 'templates/latex/common/p2_cloud_sorbet_colors.tex').read_text()
    return {name: '#' + value for name, value in re.findall(r'\\definecolor\{(\w+)\}\{HTML\}\{([A-F0-9]+)\}', text)}


def load_current(pointer=None):
    pointer = Path(pointer) if pointer is not None else REVISION / 'current_run.json'
    current = read_json(pointer)
    manifest_path = bound_path(ROOT, current['manifest'])
    manifest = read_json(manifest_path)
    if current['run_id'] != manifest['run_id']:
        raise ValueError('CURRENT_RUN_POINTER_MISMATCH')
    artifact = manifest['artifacts']['baseline']
    baseline_path = bound_path(ROOT, artifact['path'])
    if digest(baseline_path) != artifact['sha256']:
        raise ValueError('BASELINE_BYTES_CHANGED')
    baseline = read_json(baseline_path)
    if object_hash(baseline) != artifact['output_sha256'] or not artifact['valid']:
        raise ValueError('BASELINE_BINDING_INVALID')
    if baseline['status'] != 'VERIFIED' or baseline['classification'] != 'CURRENT_RUN_CONDITIONAL_ANALYSIS':
        raise ValueError('CURRENT_CONDITIONAL_BASELINE_REQUIRED')
    if baseline['contract']['source_crs'] != 'UNVERIFIED':
        raise ValueError('CONDITIONAL_DATUM_LIMITATION_REQUIRED')
    if digest(DATA) != manifest['input_sha256'] or digest(CONFIG) != manifest['policy_sha256']:
        raise ValueError('CURRENT_INPUT_OR_POLICY_CHANGED')
    for path, expected in artifact['source_hashes'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('BASELINE_SOURCE_CHANGED:' + path)
    if [r['record_id'] for r in baseline['records']] != manifest['record_scope']:
        raise ValueError('BASELINE_RECORD_SCOPE_CHANGED')
    review_entry = manifest['reviews']['baseline']
    if digest(ROOT / review_entry['path']) != review_entry['sha256']:
        raise ValueError('BASELINE_REVIEW_CHANGED')
    review = read_json(ROOT / review_entry['path'])['result']
    if (review['status'] != 'VERIFIED' or review['unchecked_components']
            or review['target_artifact_hash'] != artifact['sha256']):
        raise ValueError('BASELINE_REVIEW_INCOMPLETE')
    return current, manifest, baseline


def theme(colors):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'text.color': colors['Ink'], 'axes.labelcolor': colors['Ink'],
                         'axes.edgecolor': colors['Rule'], 'axes.titleweight': 'medium',
                         'axes.facecolor': colors['Panel'], 'figure.facecolor': colors['Paper'],
                         'xtick.color': colors['Muted'], 'ytick.color': colors['Muted'],
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'SC-G1-P2-COMPLETE',
                         'pdf.fonttype': 42, 'savefig.facecolor': colors['Paper']})


def export(fig, out, name):
    for suffix in ('svg', 'pdf', 'png'):
        fig.savefig(out / (name + '.' + suffix), dpi=300)
    plt.close(fig)


def plot_trajectories(baseline, out, colors):
    fig, axes = plt.subplots(4, 2, figsize=(12.6, 15.2))
    fig.subplots_adjust(left=.085, right=.975, top=.91, bottom=.055, hspace=.39, wspace=.22)
    fig.suptitle('Conditional pilot: original samples and baseline output', x=.085, y=.975,
                 ha='left', fontsize=18, fontweight='medium')
    fig.text(.085, .944, 'Seven fixed records · local working coordinates (km) · source datum unverified',
             fontsize=10.5, color=colors['Muted'])
    for ax, row in zip(axes.flat, baseline['records']):
        raw_xy = row['source_record']['xy']
        if raw_xy:
            ax.scatter([p[0] / 1000 for p in raw_xy], [p[1] / 1000 for p in raw_xy],
                       s=11, color=colors['Muted'], alpha=.48, linewidths=0, zorder=2)
        for segment in row['processed_segments']:
            clean, final = segment['denoise']['record'], segment['output']
            ax.plot([p[0] / 1000 for p in clean['xy']], [p[1] / 1000 for p in clean['xy']],
                    color=colors['C1'], linewidth=1.2, linestyle='--', alpha=.9, zorder=3)
            ax.plot([p[0] / 1000 for p in final['xy']], [p[1] / 1000 for p in final['xy']],
                    color=colors['C3'], linewidth=1.55, marker='o', markersize=3.4,
                    markerfacecolor=colors['Panel'], markeredgewidth=.85, zorder=4)
        counts = row['stage_counts']
        clean_n = counts['input'] - counts['filtered'] - counts['denoised']
        ax.set_title('Record ' + row['record_id'] + '  |  ' + str(counts['input']) + ' input → ' +
                     str(clean_n) + ' clean → ' + str(counts['retained']) + ' retained', loc='left', fontsize=10.8)
        ax.set(xlabel='Local easting (km)', ylabel='Local northing (km)')
        ax.set_aspect('equal', adjustable='datalim')
        ax.margins(.10)
        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.yaxis.set_major_locator(MaxNLocator(4))
        ax.grid(True, color=colors['Rule'], linewidth=.55, zorder=0)
    key = axes.flat[-1]
    key.axis('off')
    handles = [Line2D([], [], marker='.', linestyle='none', markersize=8, color=colors['Muted'], label='Original points in working coordinates'),
               Line2D([], [], linestyle='--', linewidth=1.5, color=colors['C1'], label='Clean points, within actual segments'),
               Line2D([], [], marker='o', markerfacecolor=colors['Panel'], color=colors['C3'], markersize=4, label='DP output, within actual segments')]
    key.legend(handles=handles, loc='upper left', bbox_to_anchor=(.0, .98), frameon=False, fontsize=10,
               handlelength=2.6, labelspacing=1.5)
    key.text(.04, .44, 'Raw points are not connected.\nLines never bridge a split or a filtered segment.\n\nPanels use independent limits and equal x/y scale.\nCounts describe processing, not accuracy or recovery.',
             transform=key.transAxes, fontsize=10, color=colors['Muted'], va='top', linespacing=1.65)
    export(fig, out, FIGURE_NAMES[0])


def plot_terminal_counts(baseline, out, colors):
    fig, ax = plt.subplots(figsize=(12.6, 6.8))
    fig.subplots_adjust(left=.12, right=.94, top=.79, bottom=.17)
    fig.suptitle('Every input point has one terminal action', x=.12, y=.97, ha='left', fontsize=18)
    categories = [('filtered', 'Filtered', 'C2', '//'), ('denoised', 'Direction-deleted', 'C3', 'xx'),
                  ('simplified', 'DP-omitted', 'C4', '..'), ('retained', 'Retained', 'C1', '')]
    rows = baseline['records']
    totals = [r['stage_counts']['input'] for r in rows]
    if sum(totals) != len(baseline['point_actions']):
        raise ValueError('PLOT_POINT_ACCOUNTING_MISMATCH')
    left = [0] * len(rows)
    for field, label, color, hatch in categories:
        values = [r['stage_counts'][field] for r in rows]
        ax.barh(range(len(rows)), values, left=left, height=.58, label=label,
                color=colors[color], edgecolor=colors['Paper'], linewidth=.7, hatch=hatch)
        for pos, value in enumerate(values):
            if value >= max(totals) * .035:
                ax.text(left[pos] + value / 2, pos, str(value), ha='center', va='center',
                        color=colors['Ink'], fontsize=9)
            left[pos] += value
    if left != totals:
        raise ValueError('PLOT_TERMINAL_TOTAL_MISMATCH')
    for pos, value in enumerate(totals):
        ax.text(value + max(totals) * .018, pos, 'n=' + str(value), va='center', fontsize=9.5)
    ax.set_yticks(range(len(rows)), ['Record ' + r['record_id'] for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel('Original input points (absolute count)')
    ax.set_xlim(0, max(totals) * 1.16)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis='x', color=colors['Rule'], linewidth=.6)
    ax.set_axisbelow(True)
    ax.legend(ncol=4, frameon=False, loc='lower left', bbox_to_anchor=(0, 1.025), fontsize=10)
    fig.text(.12, .054, 'All ' + str(sum(totals)) + ' points counted once. Filtering and direction deletion are separate from DP savings.',
             color=colors['Muted'], fontsize=10)
    export(fig, out, FIGURE_NAMES[1])


def architecture_xml(run_id, state, out, colors):
    width, height = 1440, 1000
    mx = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(mx, 'diagram', name='Current Goal 1 execution structure')
    model = ET.SubElement(diagram, 'mxGraphModel', page='1', pageWidth=str(width), pageHeight=str(height))
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def node(name, text, x, y, w, h, *, fill='Panel', size=20, dashed=False):
        style = f'rounded=1;html=0;fillColor={colors.get(fill, fill)};strokeColor={colors["Rule"]};fontColor={colors["Ink"]};fontSize={size};dashed={int(dashed)};'
        cell = ET.SubElement(root, 'mxCell', id=name, parent='1', vertex='1', value=text, style=style)
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})

    def edge(name, source, target, points, *, label='', label_xy=(0, 0), dashed=False):
        cell = ET.SubElement(root, 'mxCell', id=name, parent='1', edge='1', source=source, target=target,
                             value=label, style=f'endArrow=block;strokeColor={colors["C1"]};dashed={int(dashed)};')
        geometry = ET.SubElement(cell, 'mxGeometry', relative='1', labelX=str(label_xy[0]), labelY=str(label_xy[1]), **{'as': 'geometry'})
        ET.SubElement(geometry, 'mxPoint', x=str(points[0][0]), y=str(points[0][1]), **{'as': 'sourcePoint'})
        mids = ET.SubElement(geometry, 'Array', **{'as': 'points'})
        for x, y in points[1:-1]:
            ET.SubElement(mids, 'mxPoint', x=str(x), y=str(y))
        ET.SubElement(geometry, 'mxPoint', x=str(points[-1][0]), y=str(points[-1][1]), **{'as': 'targetPoint'})

    node('title', 'Goal 1 · actual roles, tools and repair return', 60, 10, 1320, 65, fill='none', size=30)
    node('subtitle', 'Native role sessions; deterministic execution and reviews are recorded separately', 60, 77, 1320, 45, fill='none', size=18)
    node('A', 'A · plan and follow-up\nApproved method space\nEvidence-based next action', 80, 160, 340, 130, fill='P1')
    node('B', 'B-Run · seven fixed records\nSplit / filter → denoise → DP\nRaw values remain available', 550, 160, 340, 130)
    node('C', 'C · independent review\nTrusted inputs and contract\nSpecific artifact / hash / scope', 1020, 160, 340, 130, fill='P4')
    node('journal', 'Deterministic Goal journal\nPending tasks · dependencies · registered artifacts · audit coverage · recoverable state\nCurrent run: ' + run_id,
         80, 395, 1280, 125, size=20)
    node('issue', 'Actual external issues\nC2-F01 / C2-F02\nBlocking parent task recorded', 80, 635, 275, 125, size=18)
    node('repair', 'B-Repair\nConsume task → change code\nTargeted tests and receipt', 415, 635, 275, 125, size=18)
    node('verify', 'C regression\nIndependent counterexamples\nApprove or reopen issue', 750, 635, 275, 125, size=18)
    node('rebuild', 'Rebuild and resume\nInvalidate affected results\nFix code version → rerun', 1085, 635, 275, 125, size=18)
    node('later', 'Later scope · not executed here\nGoal 2: parameter / order comparisons    |    Goal 3: final reports and submission',
         80, 885, 1280, 85, size=19, dashed=True)
    edge('A_to_B', 'A', 'B', [(420, 225), (550, 225)])
    edge('B_to_C', 'B', 'C', [(890, 225), (1020, 225)])
    edge('C_to_journal', 'C', 'journal', [(1190, 290), (1190, 395)], label='review result', label_xy=(1210, 350))
    edge('journal_to_A', 'journal', 'A', [(80, 450), (35, 450), (35, 225), (80, 225)], label='next task', label_xy=(48, 355))
    edge('journal_to_issue', 'journal', 'issue', [(215, 520), (215, 635)], label='defect found', label_xy=(240, 582))
    edge('issue_to_repair', 'issue', 'repair', [(355, 698), (415, 698)])
    edge('repair_to_verify', 'repair', 'verify', [(690, 698), (750, 698)])
    edge('verify_to_rebuild', 'verify', 'rebuild', [(1025, 698), (1085, 698)])
    edge('rebuild_to_parent', 'rebuild', 'journal', [(1225, 635), (1225, 520)], label='resume parent', label_xy=(1035, 582))
    edge('reopen', 'verify', 'repair', [(885, 760), (885, 815), (550, 815), (550, 760)], label='failed regression → repair again', label_xy=(610, 844))
    ET.indent(mx)
    path = out / (FIGURE_NAMES[2] + '.drawio')
    ET.ElementTree(mx).write(path, encoding='utf-8', xml_declaration=True)
    required = {'ISSUE_OPENED', 'B_REPAIR_CONSUMED', 'REPAIR_SUBMITTED', 'C_VERIFIED_PARENT_RESUMED', 'RUN_STARTED', 'TOOL_EXECUTED'}
    events = [{k: v for k, v in event.items() if k in ('sequence', 'kind', 'issue_id', 'parent_task', 'run_id', 'operation', 'hash')}
              for event in state['events'] if event['kind'] in required]
    return path, events


def render_architecture(path, out, colors):
    """Render all formats by parsing the same editable mxGeometry and labels."""
    document = ET.parse(path)
    model = document.find('.//mxGraphModel')
    width, height = float(model.get('pageWidth')), float(model.get('pageHeight'))
    fig, ax = plt.subplots(figsize=(14.4, 10))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, width), ylim=(height, 0), aspect='equal')
    ax.axis('off')
    for cell in document.findall('.//mxCell'):
        geometry = cell.find('mxGeometry')
        if geometry is None:
            continue
        style = dict(item.split('=', 1) for item in cell.get('style', '').split(';') if '=' in item)
        if cell.get('vertex') == '1':
            x, y, w, h = [float(geometry.get(k)) for k in ('x', 'y', 'width', 'height')]
            if style['fillColor'] != 'none':
                ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=6',
                             facecolor=style['fillColor'], edgecolor=style['strokeColor'], linewidth=1.15,
                             linestyle='--' if style.get('dashed') == '1' else '-'))
            size = float(style['fontSize'])
            for index, line in enumerate(cell.get('value', '').split('\n')):
                ax.text(x + 17, y + 32 + index * (size + 10), line, fontsize=size * .72,
                        color=style['fontColor'], va='baseline')
        elif cell.get('edge') == '1':
            nodes = [geometry.find("mxPoint[@as='sourcePoint']"), *geometry.findall('Array/mxPoint'),
                     geometry.find("mxPoint[@as='targetPoint']")]
            points = [(float(p.get('x')), float(p.get('y'))) for p in nodes]
            ax.plot(*zip(*points), color=style['strokeColor'], linewidth=1.55,
                    linestyle='--' if style.get('dashed') == '1' else '-')
            ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle='-|>',
                                        mutation_scale=13, color=style['strokeColor'], linewidth=0))
            if cell.get('value'):
                ax.text(float(geometry.get('labelX')), float(geometry.get('labelY')), cell.get('value'),
                        fontsize=11.2, color=colors['Ink'], va='baseline')
    export(fig, out, FIGURE_NAMES[2])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', type=Path, default=REVISION / 'current_run.json')
    parser.add_argument('--out', type=Path, default=REVISION / 'figures')
    args = parser.parse_args()
    current, manifest, baseline = load_current(args.current)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    colors = palette()
    theme(colors)
    plot_trajectories(baseline, out, colors)
    plot_terminal_counts(baseline, out, colors)
    state = read_json(REVISION / 'goal_state.json')
    drawing, actual_events = architecture_xml(current['run_id'], state, out, colors)
    render_architecture(drawing, out, colors)
    paths = [out / (name + '.' + suffix) for name in FIGURE_NAMES for suffix in ('svg', 'pdf', 'png')]
    paths.append(drawing)
    report = {'classification': baseline['classification'], 'source_crs': 'UNVERIFIED',
              'run_id': current['run_id'], 'code_sha': manifest['code_sha'],
              'baseline': manifest['artifacts']['baseline'], 'new_model_calls': 0,
              'renderer': 'Matplotlib; draw.io mxGeometry parsed for all architecture exports',
              'palette_source': 'templates/latex/common/p2_cloud_sorbet_colors.tex',
              'palette_sha256': digest(ROOT / 'templates/latex/common/p2_cloud_sorbet_colors.tex'),
              'generator': 'task1/scripts/build_complete_figures.py', 'generator_sha256': digest(Path(__file__)),
              'figure_count': len(FIGURE_NAMES), 'raster_dpi': 300,
              'record_scope': manifest['record_scope'], 'stage_counts': baseline['stage_counts'],
              'actual_repair_event_evidence': actual_events,
              'claims_not_supported': ['SOURCE_DATUM_IDENTIFIED', 'ACCURACY', 'GROUND_TRUTH_RECOVERY', 'QUALITY_IMPROVEMENT'],
              'files': [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p)} for p in paths]}
    write_json(out / 'figure_manifest.json', report)
    print(json.dumps({'run_id': current['run_id'], 'figures': len(FIGURE_NAMES), 'files': len(paths),
                      'manifest': str((out / 'figure_manifest.json').relative_to(ROOT))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
