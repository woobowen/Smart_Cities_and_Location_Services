# RL visual research and author check

Actual producer: native reinforcement child. This is author inspection; independent agent/report-page inspection is separate.

Read installed `tools/skills/publication-plots/SKILL.md`, tool-routing and visual-design references, Visual System §§11–13, and publicP2 color source. Generic skill palette overridden by the lockedP2 source. Actual rendererMatplotlib3.10.8;2D PDF/SVG/300dpiPNG, no generative images or inferred basemap.

Primary official examples actually opened2026-11-05:

- https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html — supports native matrix/heatmap implementation and label/colorbar patterns; not evidence about dispatch quality.
- https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html — supports raw/summary uncertainty visualization patterns; bands do not create independent samples.
- https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_with_legend.html — supports explicit scatter encoding and legend construction; not causal evidence.

CandidateA `candidates/rl_value_maps`: true8×8region maps at8/13/18/22, fixed0–max value range and actual train-proxy-origin background, local teachingkm. Reveals adjacency needed by neighbor repositioning; no claim of geographic measurement precision. CandidateB `candidates/rl_value_time_zone`: all108×64estimated cells plus observed inner-train demand counts; exposes full temporal shape and zero states but row-major zoneID hides geographic adjacency. Both were actually generated and opened at fullsize. CandidateA selected for formal neighborhood mechanism;B retained as complementary full-time view. Black map dots are the same reproducibly sampled3000inner-training origins, not hour-specific demand or real taxi orders.

Actual full-size author views performed for all8initial formalRL figures plus both unique value candidates: learning/TD, value maps, beta/rejection, fleet validation, Double seed pairs, movement gross/empty/cost,2×2movement parent-removal, fusion estimatedfront/realizedeffect. Found that initial fusion legend covered the low-revenue NSGA-knee point; moved its legend outside both panels and regenerated from source, then opened corrected export. Kept adverse outcomes visible.

All initial rasters passed the actual publication-plots `check_figure_set.py` dimensions/nonblank test (e.g.2120×2134value maps,2735×1054three-panel seed/fleet figures); actual check output saved separately. Statistical units, day/training seeds, source/model/metricSHA256, raw versus smoothed curves, cost assumptions, and conditional coordinates are recorded in eachfigureJSON. No arbitrary aggregatequalityscore or generated data.

Final-heldout figures are added after finalrun actually completes; this record does not claim they were inspected before creation.

## Superseding publication revision: aggregate background

Research-data verifier independently found that initial scatter-based map SVGs embedded individual proxy coordinates while publication permissions were pending. Those initial exports are invalid for publication. Rebuilt **both** formal/candidate maps from unchangedV and unchangedseed0sampledn=3000origins:8×8zone counts only, circles fixed at teaching-cell centers with area proportional tocount, sizelegend25/100/500. Saved `figures/data/rl_value_origin_counts.csv`; actual64cellcountsum=3000verified in `value_map_aggregation_check.json`. No original row coordinates remain in these map exports. The earlier black-dot wording above describes superseded initial author checks only, not current figures.

Fresh-process rebuild completed after environmentMatplotlib3.10.8 namespace repair. Actually opened current aggregate map, current primary-final paired-tradeoff figure, current finalfleet figure, and movement-cost figure with explicit “repositionkm at1proxycurrency/km” label. Current primary-final graph shows the adverse day and its original5day interval crossingzero, rather than hiding uncertainty. Other2Dfigures retain unchangedvalues/layout from the already viewed versions. All currentRLrasters passed theactualdimension/nonblankchecker; output `figure_dimensions_final.log`. Parent/independent reviewers still own report-page and public-release acceptance.
