# Multiobjective figure research and selection

Author: native `/root/evolution`; task E-A/P-002. Actually read installed
`tools/skills/publication-plots/SKILL.md`, `references/tool-routing.md`,
`references/visual-design.md`, project Visual System §§11–14, and common P2 TeX.
User P2 takes precedence over the skill's optional Tol palette. No generated
bitmap, screenshot collage, fabricated UI, or arbitrary 3D dimension is used.

## Sources actually opened on 2026-11-05

| Primary source | Exact support and limitation |
|---|---|
| [Deb et al.2002, NSGA-II](https://doi.org/10.1109/4235.996017) | Nondominance/crowding/elite selection and the need for a solution set; does not establish any dispatch advantage in our data. |
| [pymoo scatter documentation](https://pymoo.org/visualization/scatter.html) | Objective-space scatter and projections as multiobjective visualization; does not justify a fitted continuous front between discrete matchings. |
| [pymoo parallel coordinates](https://pymoo.org/visualization/pcp.html) | Multiple objectives can be shown as separate aligned axes; not authorization to form a combined performance score. |
| [Matplotlib fill-between example](https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html) | Native uncertainty-band rendering. Here the band is the observed five-seed min–max, explicitly not a confidence interval. |
| [Matplotlib3D scatter example](https://matplotlib.org/stable/gallery/mplot3d/scatter3d.html) | A reproducible headless3D scatter; our third axis is actual matched count and comparisons share camera/ranges. |
| [pymoo DTLZ definition](https://pymoo.org/problems/many/dtlz.html) | DTLZ2 benchmark and positive unit-sphere front; analytic wireframe is distinguished from computed outcomes. |

Web documentation was currently Matplotlib3.11.2/pymoo0.6.2; installed actual
pilot rendering used Matplotlib3.6.3; final exports use the main coordinator's
project-local Matplotlib3.10.8 repair, and numerical cross-checks pymoo0.6.1.6. Only APIs
actually executed successfully here are claimed. The consulted sources informed
the visualization step, not a retroactive claim about earlier experiment causes.

## Candidates and question contracts

| Candidate | Inputs / encoding / question | Potential misleading effect | Cost / decision |
|---|---|---|---|
| Two-objective scatter + five-seed HV against objective evaluations | Actual distinct nondominated revenue–pickup points; seed0 fixed in advance for geometry. Common normalizer; convergence mean/min–max over seeds0..4. Asks whether an algorithm explores useful trade-offs faster. | Connecting weighted scalar solutions is only a reading guide; no point between them is asserted feasible. Five EA seeds share one traffic batch and are not five independent urban demand samples. | Low; formal `evolution_front_and_convergence`. |
| Three-objective side-by-side3D | Actual pickup/fare/served coordinates, fixed axis limits/camera and two marker shapes. Asks whether the third objective fills a surface. | Occlusion can hide the fare–count relation. Perspective does not establish Pareto dominance. | Low; actually generated `candidates/evolution_three_objectives_3d`. |
| Three-objective pairwise projection grid | Same exact points in three pairwise views. No interpolation or deletion. Reveals service–fare correlation and sparse geometry. | Different3D solutions can overlap in a projection; a projected dominated point need not be dominated in3D. | Low; actually generated `candidates/evolution_three_objectives_projections`. |
| Three-objective parallel coordinates | Same points transformed to separate normalized benefits: fare/max,1−pickup/bound,count/40. Higher is better on each axis. | Dense crossing can obscure individual points; area/line height is not a composite score. | Low; actually generated `candidates/evolution_three_objectives_parallel`. |
| Formal3D + service/fare projection | Preserve actual third objective and provide the clearest projection for the observed near-degenerate front. | A single fixed seed cannot replace five-seed metric tables. | Selected for geometry; formal `evolution_three_objective_geometry`; all three candidates retained. |
| DTLZ2 computed scatter + analytic wireframe | Actual integer-coded results with separate gray unit-sphere reference. Same camera/ranges in both panels. | Theory wireframe is not sampled evidence; teacher integer benchmark differs from a continuous-domain search. | Formal `evolution_dtlz2_geometry`. |
| Four-hour small multiples | Fixed source-local8/13/18/23, common driver/order counts, physical axis units/ranges, actual fronts. | Different hours are different synthetic proxy batches; no claim of actual taxi high/low peaks follows automatically. | Formal `evolution_hourly_fronts`. |
| Paired intervention plot + measured cost plane | Five seed-level lines across baseline/population/generations/KM initialization/any justified combination. Right view uses actual EA+initialization runtime. | Connecting interventions expresses pairing, not a monotonic timeline; additional components are not inherently better. | Formal `evolution_budget_and_initialization`, only completed five-seed groups included. |
| Basic-task front + exact scalar ratio | Independent20/20 synthetic OD geometry; revenue is trip-km, exact optional scalar KM reference. | Static approximation ratio must never become an online theoretical competitive guarantee. Zero cases stay explicit. | Formal `evolution_basic_scalar_reference`. |

Density-smoothed Pareto fronts and interpolated3D surfaces were rejected at
design because matching outputs are discrete and neither data nor interpolation
supports new feasible solutions. No decorative surface is produced.

## Production and check contract

`task2/scripts/build_evolution_figures.py` reads preserved raw runs and the
uniformly recomputed `results/evolution/metrics.json`; every output's sidecar
records source file hashes, plotting script hash, common palette hash, actual
native formats and claim boundary. Outputs are vector PDF/SVG and300dpi PNG.
Raw front metrics use the independent-review repair: all algorithms round to
10decimals, deduplicate and discard dominated points before HV/Spacing. Source
matching coordinates are never redrawn or modified by styling.

The author will inspect actual exported figures, record issues/corrections and
run the installed figure checker. Other-agent figure/data review is separately
attributed. Report-page inspection remains the report builder's responsibility;
figure exports alone do not certify the final page's readable placement size.
