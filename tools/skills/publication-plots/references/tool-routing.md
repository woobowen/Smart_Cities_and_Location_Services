# Tool routing

Use this table to choose a renderer after honoring explicit user choices.

| Tool | Prefer for | 3D approach | Static export notes |
| --- | --- | --- | --- |
| Python / Matplotlib | General scientific figures, numerical workflows, full layout control | `mplot3d` surface, wireframe, scatter | Reliable headless PNG/PDF/SVG; centralize `rcParams` |
| R / ggplot2 | Statistical graphics, layered grammar, faceting | Base `persp`, lattice, Plotly, or rgl | `ggsave` is reliable for 2D; base/lattice is safer than OpenGL in headless static jobs |
| JavaScript / Plotly.js | Interactive charts, browser-native presentation | WebGL `surface` or `mesh3d` | Always inspect headless exports; use SVG/D3 projection when WebGL is blank and interactivity is not required |
| TeX / PGFPlots | Publication-native vector output and exact TeX typography | `\addplot3[surf]` from sampled tables | Excellent PDF integration; precompute large datasets and rasterize only for gallery previews |
| Racket / Plot | Functional-programming comparison, scriptable PNG/PDF/SVG | `surface3d` or `contour-intervals3d` | Use `plot/no-gui` for automation; some categorical styles require one renderer per color |

## Selection rules

- Default to Matplotlib for a one-off static scientific figure when no ecosystem preference exists.
- Default to ggplot2 when faceting, statistical transformations, or an existing R analysis dominates.
- Use Plotly.js when browser interactivity is part of the deliverable; do not choose it solely for a static 3D image without testing the export path.
- Use PGFPlots when the target is a TeX paper and vector consistency outweighs render time.
- Use Racket Plot when Racket itself is in scope or the comparison explicitly includes it.

## Fair comparison protocol

For renderer comparisons, create:

1. a canonical tidy dataset for raw points;
2. separate derived tables for aggregations, fitted lines, trajectories, and surface grids;
3. a shared chart contract containing titles, labels, units, axis limits, ticks, category order, palette, aspect ratio, output dimensions, and camera settings.

Let each tool express its native rendering character, but do not let defaults change the data or semantic encodings. Document meaningful fallbacks such as Plotly WebGL to SVG projection in the final handoff.
