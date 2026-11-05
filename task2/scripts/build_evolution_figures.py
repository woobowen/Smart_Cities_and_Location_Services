#!/usr/bin/env python3
"""Native P2 multiobjective figures from actual paired runs and canonical metrics."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'task2/src'))
from evolution import knee_point, constraint_choice
from front_metrics import canonical_front, evaluate_front
from build_figures import P, PALETTE_PATH

RESULTS = ROOT/'task2/results/evolution'
FIGURES = ROOT/'task2/figures'
PUBLIC_RESULTS = ROOT/'task2/public_results/evolution'
METRIC_PATH = (PUBLIC_RESULTS/'metrics.json' if (PUBLIC_RESULTS/'metrics.json').is_file()
               else RESULTS/'metrics.json')
COLORS = {'nsga2': P['C1'], 'nsga3': P['C2'], 'weighted_km': P['C4']}
LABELS = {'nsga2': 'NSGA-II', 'nsga3': 'NSGA-III', 'weighted_km': 'Weighted KM'}
MARKERS = {'nsga2': 'o', 'nsga3': '^', 'weighted_km': 's'}
plt.rcParams.update({'font.size': 11, 'axes.labelsize': 11, 'axes.titlesize': 12})


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(fig, name, inputs, claim, selection='formal'):
    path = FIGURES/selection/name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    # Matplotlib3.6's Axes3D tight bbox can omit an outward z-axis label.
    axis_labels = []
    for ax in fig.axes:
        axis_labels.extend([ax.xaxis.label, ax.yaxis.label])
        if hasattr(ax, 'zaxis'):
            axis_labels.append(ax.zaxis.label)
    for extension in ['pdf', 'svg', 'png']:
        fig.savefig(path.with_suffix('.'+extension), dpi=300, bbox_inches='tight',
                    bbox_extra_artists=axis_labels, facecolor=P['Paper'])
    plt.close(fig)
    meta = dict(figure=name, claim_scope=claim, author='/root/evolution',
                input_sha256={str(Path(p).relative_to(ROOT)):sha(p) for p in sorted(set(inputs))},
                script_sha256=sha(__file__), shared_theme_sha256=sha(ROOT/'task2/scripts/build_figures.py'),
                palette_sha256=sha(PALETTE_PATH), raster_dpi=300,
                native='Matplotlib data-native PDF/SVG and 300dpi PNG; all marks are actual points')
    path.with_suffix('.json').write_text(json.dumps(meta, indent=2)+'\n')


def grid(ax):
    ax.grid(color=P['Rule'], linewidth=.7, axis='y')
    ax.set_axisbelow(True)


def rows():
    return json.loads(METRIC_PATH.read_text())['rows']


def selected(all_rows, **wanted):
    return [r for r in all_rows if all(r.get(k) == v for k, v in wanted.items())]


def raw(record):
    return json.loads(record_path(record).read_text())


def record_path(record):
    path=ROOT/record['path']
    # Public canonical rows already point at their aggregate projection. Local
    # canonical rows may also use projections when available. Synthetic basic
    # sources remain independently reproducible and publicly permitted.
    relative=Path(record['path'])
    parts=relative.parts
    if len(parts)>=5 and parts[:3]==('task2','results','evolution') and parts[3] in ['runs','km']:
        projected=PUBLIC_RESULTS/parts[3]/relative.name
        if projected.is_file():
            return projected
    if not path.is_file():
        raise FileNotFoundError(f'Missing aggregate plotting input: {record["path"]}')
    return path


def inputs(records):
    return [METRIC_PATH]+[record_path(r) for r in records]


def plot_front(ax, F, algo, alpha=.85, label=True):
    F = np.asarray(F)
    ax.scatter(F[:, 1], -F[:, 0], s=22, marker=MARKERS[algo], color=COLORS[algo],
               alpha=alpha, linewidths=.4, label=LABELS[algo] if label else None)


def front_and_convergence(all_rows):
    bid = 'inner_hour18_batchseed2024'
    base = selected(all_rows, batch_id=bid, n_obj=2, stage='baseline')
    km = selected(all_rows, batch_id=bid, n_obj=2, algorithm='weighted_km')[0]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4), layout='constrained')
    for algo in ['nsga2', 'nsga3']:
        rr = selected(base, algorithm=algo, seed=0)[0]
        plot_front(axes[0], rr['metrics']['front'], algo)
    Fkm = np.asarray(km['metrics']['front'])
    axes[0].plot(Fkm[:, 1], -Fkm[:, 0], color=COLORS['weighted_km'], lw=.8, alpha=.55)
    plot_front(axes[0], Fkm, 'weighted_km', alpha=.8)
    rr = selected(base, algorithm='nsga2', seed=0)[0]
    F = np.asarray(rr['metrics']['front'])
    ki, ci = knee_point(F), constraint_choice(F, 60.)
    axes[0].scatter(F[ki, 1], -F[ki, 0], s=135, facecolors='none', edgecolors=P['C3'], lw=1.6)
    axes[0].annotate('Knee', (F[ki, 1], -F[ki, 0]), xytext=(12, -22), textcoords='offset points',
                     fontsize=9, color=P['C3'], arrowprops=dict(arrowstyle='-', color=P['C3'], lw=.7))
    axes[0].scatter(F[ci, 1], -F[ci, 0], s=70, marker='D', color=P['Ink'])
    axes[0].annotate('Budget 60 km\n(non-binding)', (F[ci, 1], -F[ci, 0]),
                     xytext=(-88, -35), textcoords='offset points', fontsize=8.5,
                     arrowprops=dict(arrowstyle='-', color=P['Ink'], lw=.7))
    axes[0].set(xlabel='Total pickup distance (km)', ylabel='Simulated fare units',
                title='A  Trade-offs on one fixed batch')
    axes[0].legend(fontsize=8.5, frameon=False, loc='lower right')
    for algo in ['nsga2', 'nsga3']:
        group = sorted(selected(base, algorithm=algo), key=lambda r:r['seed'])
        curves, xx = [], None
        for rec in group:
            r = raw(rec)
            xx = np.array([h['generation'] for h in r['history']])*r['pop_size']+r['pop_size']
            yy = [evaluate_front(h['F'], r['ideal'], r['nadir'])['HV'] for h in r['history']]
            curves.append(yy)
        arr = np.asarray(curves)
        axes[1].fill_between(xx/1000, arr.min(0), arr.max(0), alpha=.18, color=COLORS[algo])
        axes[1].plot(xx/1000, arr.mean(0), color=COLORS[algo], lw=1.8, label=LABELS[algo],
                     ls='-' if algo == 'nsga2' else '--')
    axes[1].axhline(km['metrics']['HV'], color=P['C4'], lw=1.1, ls=':', label='KM: 41 scalar solves')
    axes[1].set(xlabel='Objective evaluations (thousands)', ylabel='Hypervolume',
                title='B  Five paired algorithm seeds')
    axes[1].legend(fontsize=8.5, frameon=False, loc='lower right')
    for ax in axes:
        grid(ax)
    save(fig, 'evolution_front_and_convergence', inputs(base+[km]),
         '40 drivers/80 requests, training-inner18h batchseed2024. Front illustration uses pre-fixed seed0. '
         'All methods share K6/radius3km and prior feasible-bound normalization/ref1.1. Convergence mean and '
         'min-max band across five algorithm seeds0..4 on the same input, not independent traffic samples. '
         'Polyline between KM points only guides reading. Constraint budget60km is explicitly non-binding.')


def three_objective_candidates(all_rows):
    base = selected(all_rows, batch_id='inner_hour18_batchseed2024', n_obj=3, stage='baseline', seed=0)
    fig = plt.figure(figsize=(10.4, 4.9), layout='constrained')
    for i, algo in enumerate(['nsga2', 'nsga3']):
        r = selected(base, algorithm=algo)[0]
        F = np.asarray(r['metrics']['front'])
        ax = fig.add_subplot(1, 2, i+1, projection='3d')
        ax.scatter(F[:, 1], -F[:, 0], -F[:, 2], color=COLORS[algo], marker=MARKERS[algo], s=20, alpha=.8)
        ax.set(xlabel='Pickup (km)', ylabel='Fare units', zlabel='Served requests',
               xlim=(0, 65), ylim=(0, 900), zlim=(0, 40), title=LABELS[algo])
        ax.view_init(elev=23, azim=-56)
        ax.set_box_aspect((1, 1, .85))
    save(fig, 'evolution_three_objectives_3d', inputs(base),
         'Actual three-objective dispatch front, seed0, both N105/G300. Shared axes/camera. '
         'Third axis is actual service count, not decorative depth. Integer count and fare are correlated.', 'candidates')
    # Projection candidate keeps all three pairwise relationships legible without occlusion.
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 4.1), layout='constrained')
    for algo in ['nsga2', 'nsga3']:
        F = np.asarray(selected(base, algorithm=algo)[0]['metrics']['front'])
        xyz = [F[:, 1], -F[:, 0], -F[:, 2]]
        for ax, (a, b) in zip(axes, [(0, 1), (0, 2), (1, 2)]):
            ax.scatter(xyz[a], xyz[b], color=COLORS[algo], marker=MARKERS[algo], s=17, alpha=.65,
                       label=LABELS[algo])
    for ax, labels in zip(axes, [('Pickup (km)', 'Fare units'), ('Pickup (km)', 'Served requests'), ('Fare units', 'Served requests')]):
        ax.set(xlabel=labels[0], ylabel=labels[1]);grid(ax)
    axes[0].legend(fontsize=8, frameon=False)
    save(fig, 'evolution_three_objectives_projections', inputs(base),
         'Exactly the same seed0 three-objective sets as the 3D candidate. Pairwise projections reveal '
         'fare/service correlation but do not create new Pareto solutions.', 'candidates')
    # Parallel coordinates emphasize objective alignment; no composite score is created.
    fig, ax = plt.subplots(figsize=(10.4, 4.1), layout='constrained')
    for algo in ['nsga2', 'nsga3']:
        rec = selected(base, algorithm=algo)[0]
        F = np.asarray(rec['metrics']['front'])
        benefit = np.c_[-F[:, 0]/(-rec['ideal'][0]), 1-F[:, 1]/rec['nadir'][1], -F[:, 2]/40]
        for row in benefit:
            ax.plot(range(3), row, color=COLORS[algo], alpha=.10, lw=.8)
        ax.plot([], [], color=COLORS[algo], lw=2, label=LABELS[algo])
    ax.set(xticks=range(3), xticklabels=['Fare / feasible maximum', '1 - pickup / bound', 'Served / 40'],
           ylabel='Separate normalized benefits (higher is better)', ylim=(-.03, 1.03))
    ax.legend(frameon=False, fontsize=9);grid(ax)
    save(fig, 'evolution_three_objectives_parallel', inputs(base),
         'Same raw sets, axes normalized using frozen feasible bounds, not a combined score. '
         'Lines join objectives of one matching, not time series. Dense overlap is retained.', 'candidates')
    # Formal selection combines 3D shape and its most informative projection.
    fig = plt.figure(figsize=(10.4, 4.7), layout='constrained')
    ax3 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2)
    for algo in ['nsga2', 'nsga3']:
        F = np.asarray(selected(base, algorithm=algo)[0]['metrics']['front'])
        ax3.scatter(F[:, 1], -F[:, 0], -F[:, 2], color=COLORS[algo], marker=MARKERS[algo], s=15, alpha=.65)
        ax2.scatter(-F[:, 2], -F[:, 0], color=COLORS[algo], marker=MARKERS[algo], s=22, alpha=.7, label=LABELS[algo])
    ax3.set(xlabel='Pickup (km)', ylabel='Fare units', zlabel='Served', xlim=(0, 65), ylim=(0, 900), zlim=(0, 40))
    ax3.view_init(elev=23, azim=-56);ax3.set_box_aspect((1, 1, .85))
    ax2.set(xlabel='Served requests', ylabel='Simulated fare units', title='Service and fare remain correlated')
    ax2.legend(frameon=False, fontsize=9);grid(ax2)
    save(fig, 'evolution_three_objective_geometry', inputs(base),
         'Formal choice after rendering three candidate layouts: 3D shows actual third objective while '
         'the service-fare projection makes degeneracy readable. Pre-fixed seed0; five-seed summary in tables.')


def dtlz_and_hours(all_rows):
    dtlz = selected(all_rows, batch_id='dtlz2_integer_teacher')
    fig = plt.figure(figsize=(10.4, 4.8), layout='constrained')
    for i, algo in enumerate(['nsga2', 'nsga3']):
        rec = selected(dtlz, algorithm=algo, seed=0)[0]
        F = np.asarray(rec['metrics']['front'])
        ax = fig.add_subplot(1, 2, i+1, projection='3d')
        ax.scatter(*F.T, s=18, marker=MARKERS[algo], color=COLORS[algo], alpha=.8)
        # Analytic reference is clearly a theory wireframe, not another experiment.
        u, v = np.meshgrid(np.linspace(0, np.pi/2, 12), np.linspace(0, np.pi/2, 12))
        ax.plot_wireframe(np.cos(u)*np.cos(v), np.cos(u)*np.sin(v), np.sin(u), color=P['Muted'], lw=.35, alpha=.35)
        ax.set(xlabel='f1', ylabel='f2', zlabel='f3', xlim=(0, 1.05), ylim=(0, 1.05), zlim=(0, 1.05), title=LABELS[algo])
        ax.view_init(elev=25, azim=43);ax.set_box_aspect((1, 1, 1))
    save(fig, 'evolution_dtlz2_geometry', inputs(dtlz),
         'Teacher integer DTLZ2 K200/nvar12, N92/G400. Seed0 illustrations; five-seed summaries separate. '
         'Gray wireframe is the analytic positive-octant unit sphere, not measured data; identical camera/ranges.')
    recs = []
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.4), layout='constrained', sharex=True, sharey=True)
    for ax, hour in zip(axes.flat, [8, 13, 18, 23]):
        bid = f'inner_hour{hour}_batchseed2024'
        for algo in ['nsga2', 'nsga3', 'weighted_km']:
            rec = selected(all_rows, batch_id=bid, n_obj=2, algorithm=algo,
                           **({} if algo == 'weighted_km' else dict(stage='baseline', seed=0)))[0]
            recs.append(rec);plot_front(ax, rec['metrics']['front'], algo, alpha=.65)
        ax.set(title=f'{hour:02d}:00 source-local hour', xlabel='Pickup distance (km)', ylabel='Fare units')
        grid(ax)
    axes.flat[0].legend(frameon=False, fontsize=8.5)
    save(fig, 'evolution_hourly_fronts', inputs(recs),
         'Each hour is its own training-inner resampled batchseed2024, same 40/80 counts, K6/radius3km. '
         'Seed0 illustrates geometry; five algorithm seeds per hour are available. Shared physical axes; '
         'this is not observed taxi demand or a claim that batch instances are identical across hours.')


def scale_and_hybrid(all_rows):
    bid = 'inner_hour18_batchseed2024'
    candidates = [('baseline', 100, 300, 'Baseline\n100 x 300'), ('scale', 200, 300, 'Population\n200 x 300'),
                  ('scale', 100, 600, 'Generations\n100 x 600'), ('hybrid', 100, 300, 'KM seeds\n100 x 300'),
                  ('combination', 200, 300, 'KM + population\n200 x 300')]
    available = [(s, n, g, label) for s, n, g, label in candidates
                 if len(selected(all_rows, batch_id=bid, stage=s, n_obj=2, pop_size=n, n_gen=g)) == 10]
    if len(available) < 3:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.8), layout='constrained')
    used = []
    stage_colors = [P['Muted'], P['C2'], P['C4'], P['C3'], P['C1']]
    for algo in ['nsga2', 'nsga3']:
        groups = []
        for si, (stage, n, g, label) in enumerate(available):
            group = sorted(selected(all_rows, batch_id=bid, stage=stage, n_obj=2, algorithm=algo, pop_size=n, n_gen=g), key=lambda r:r['seed'])
            groups.append(group);used.extend(group)
            xx = np.array([r['total_runtime'] for r in group]);yy = np.array([r['metrics']['HV'] for r in group])
            axes[1].scatter(xx, yy, marker=MARKERS[algo], color=stage_colors[si], s=35, alpha=.8,
                            label=label.replace('\n', ' ') if algo == 'nsga2' else None)
        arr = np.array([[r['metrics']['HV'] for r in group] for group in groups])
        for seed in range(arr.shape[1]):
            axes[0].plot(range(len(available)), arr[:, seed], color=COLORS[algo], alpha=.2, lw=.7)
        axes[0].plot(range(len(available)), arr.mean(1), marker=MARKERS[algo], color=COLORS[algo], lw=2, label=LABELS[algo])
    km = selected(all_rows, batch_id=bid, n_obj=2, algorithm='weighted_km')[0]
    axes[0].axhline(km['metrics']['HV'], color=P['C4'], lw=.8, ls=':', label='Weighted KM')
    axes[0].set(xticks=range(len(available)), xticklabels=[x[3] for x in available], ylabel='Hypervolume', title='A  Paired quality controls')
    axes[0].tick_params(axis='x', labelsize=8)
    axes[0].legend(fontsize=8.5, frameon=False, loc='lower right')
    axes[1].set(xlabel='EA + KM-initialization time (s)', ylabel='Hypervolume', title='B  Quality and measured cost')
    axes[1].legend(fontsize=7.8, frameon=False, loc='lower right')
    for ax in axes:
        grid(ax)
    save(fig, 'evolution_budget_and_initialization', inputs(used+[km]),
         'Same inner18h input, paired seeds0..4, lines connect the same seed across controls; thick line=mean. '
         'No confidence interval. Runtime includes actual41KM initialization solves for hybrid, with normalization '
         'common cost separately recorded. Circle=II/triangle=III; colors at right encode intervention. '
         'N200/G300 and N100/G600 have similar ~60k EA evaluations; initialization adds41 objective sums.')


def basic_scalar_boundary(all_rows):
    recs = selected(all_rows, stage='basic')
    if len(recs) != 5:
        return
    base = raw(selected(recs, seed=0)[0])
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), layout='constrained')
    F = np.asarray(selected(recs, seed=0)[0]['metrics']['front'])
    axes[0].scatter(F[:, 1], -F[:, 0], color=P['C1'], s=23, label='NSGA-II, seed0')
    for c in base['scalar_comparisons']:
        axes[0].scatter(c['exact_F'][1], -c['exact_F'][0], marker='x', color=P['C4'], s=65, lw=1.5)
    axes[0].scatter([], [], marker='x', color=P['C4'], s=55, label='Exact scalar KM optima')
    axes[0].legend(frameon=False, fontsize=8.5, loc='lower right')
    axes[0].set(xlabel='Euclidean pickup distance (km)', ylabel='Delivered OD distance (income proxy, km)',
                title='A  Separate basic-teacher task')
    rr = [raw(r) for r in sorted(recs, key=lambda x:x['seed'])]
    lam = np.array([x['lam'] for x in rr[0]['scalar_comparisons']])
    ratios = np.array([[c['ratio'] if c['ratio'] is not None else np.nan for c in r['scalar_comparisons']] for r in rr])
    for i in range(5):
        axes[1].plot(range(len(lam)), ratios[i], color=P['C1'], alpha=.25, lw=.8)
    axes[1].plot(range(len(lam)), np.nanmean(ratios, axis=0), color=P['C1'], marker='o', lw=1.8)
    axes[1].axhline(1., color=P['C4'], ls=':', lw=1.)
    axes[1].set(xticks=range(len(lam)), xticklabels=[str(x) for x in lam], xlabel='Fixed utility weight lambda',
                ylabel='Exact utility / EA utility', title='B  Static-instance approximation')
    for ax in axes:
        grid(ax)
    save(fig, 'evolution_basic_scalar_reference', inputs(recs),
         'Synthetic20/20 OD on10x10km square, full feasible graph, revenue=Euclidean delivery km. '
         'Five EA seeds on fixed batchseed2024. Utility=deliverykm-lambda*pickupkm. Exact optional KM is '
         'a static scalar reference; this ratio is NOT an online competitive guarantee. Thin lines are seeds, '
         'thick line is their mean. No zero cases hidden.')


def final_confirmation(all_rows):
    teacher = selected(all_rows, stage='confirmation_teacher')
    initialized = selected(all_rows, stage='confirmation_km')
    if len(teacher) != 5 or len(initialized) != 5:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), layout='constrained')
    used, differences = [], []
    for index, base in enumerate(sorted(teacher, key=lambda r:r['seed'])):
        init = selected(initialized, batch_id=base['batch_id'], seed=base['seed'])[0]
        used += [base, init]
        hv = [base['metrics']['HV'], init['metrics']['HV']]
        axes[0].plot([0, 1], hv, color=P['Muted'], alpha=.5, lw=1)
        axes[0].scatter([0, 1], hv, c=[P['C1'], P['C3']], s=45, zorder=3)
        differences.append(hv[1]-hv[0])
    axes[0].set(xticks=[0, 1], xticklabels=['Teacher NSGA-II', 'KM initialization'],
                ylabel='Hypervolume', title='A  Five unseen future-pool batches', xlim=(-.2, 1.2))
    axes[1].scatter(range(5), differences, color=P['C3'], s=45)
    axes[1].axhline(0, color=P['Muted'], lw=.8)
    axes[1].axhline(np.mean(differences), color=P['C3'], lw=1, ls=':', label=f'Mean {np.mean(differences):.4f}')
    axes[1].set(xticks=range(5), xticklabels=[str(9010+i) for i in range(5)],
                xlabel='Frozen input batch seed', ylabel='Paired HV change: KM init - teacher', title='B  Every paired input is retained')
    axes[1].legend(frameon=False, fontsize=9)
    for ax in axes:
        grid(ax)
    save(fig, 'evolution_future_confirmation', inputs(used)+[ROOT/'task2/evidence/evolution/FINAL_CONFIRMATION_CONTRACT.json'],
         'Methods, seeds and metrics frozen before test. Five future-date-pool18h resampled input batches9010..9014, '
         'paired algorithm seeds10..14. Driver prior uses training only. Each pair shares its own precomputed '
         'feasible-bound normalization. No post-test selection. Lines connect paired inputs; all five differences shown.')


def main():
    rr = rows()
    front_and_convergence(rr)
    three_objective_candidates(rr)
    dtlz_and_hours(rr)
    scale_and_hybrid(rr)
    basic_scalar_boundary(rr)
    final_confirmation(rr)
    print('evolution figure set generated from', len(rr), 'canonical metric records')


if __name__ == '__main__':
    main()
