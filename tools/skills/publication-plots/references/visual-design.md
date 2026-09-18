# Visual design system

Use these defaults when the user has not supplied a journal template, brand system, or reference figure. User-provided requirements take priority.

## Palette roles

Use the following Paul Tol-derived qualitative colors in a stable order:

| Role | Hex |
| --- | --- |
| Category 1 | `#332288` |
| Category 2 | `#88CCEE` |
| Category 3 | `#44AA99` |
| Category 4 | `#DDCC77` |
| Category 5 | `#CC6677` |
| Threshold or alert | `#AA4499` |

For continuous values, use Viridis anchors:

`#440154`, `#3B528B`, `#21918C`, `#5EC962`, `#FDE725`

Supporting colors:

- primary text: `#25313C`
- axis: `#AAB4BC`
- grid: `#DCE3E8`
- optional panel fill: `#F7F9FB`
- page and plot background: white

Sources:

- Paul Tol color-blind-friendly guidance: https://www.nki.nl/about-us/responsible-research/guidelines-color-blind-friendly-figures
- Viridis package documentation: https://cran.r-project.org/package=viridisLite

## Typography and layout

- Use one sans-serif family throughout a multi-tool comparison when possible. Prefer Arial, Helvetica, or a metrically similar fallback.
- Make the title roughly 1.35 to 1.6 times the axis-label size. Use sentence case and left alignment where the tool supports it.
- Keep axis labels explicit about units. Avoid legends that repeat the title or an axis label.
- Use horizontal major grid lines for ordinary 2D comparisons. Remove minor grids unless they help exact reading.
- Remove top and right spines when they do not encode a scale.
- Put legends outside the plotting region when overlap is plausible. Preserve category order across figures.
- Use white space as structure; avoid boxes, shadows, gradients on bars, and decorative backgrounds.

## Chart-specific defaults

### Scatter

- Use opacity around 0.25 to 0.40 for hundreds of points.
- Draw fitted trends with higher saturation and a visibly heavier stroke.
- Show a threshold as a thin dashed line in the dedicated threshold color.
- Do not connect independent observations.

### Bar or dot comparison

- Start a quantitative bar axis at zero.
- Use direct value labels when the chart has only a few groups.
- Include `n` when group sizes differ materially.
- Use meaningful order: domain order, time order, or a documented ranking.

### Repeated-measure line plot

- Use both lines and markers when observations are sparse.
- Keep individual identity separate from analytical groups in the legend or label.
- Repeated observations at the same x value may form vertical segments; preserve them rather than silently aggregating unless aggregation is requested.

### 3D surface

- Use a perceptually ordered continuous palette and a colorbar.
- Keep a light mesh or sparse contours to reveal shape without dominating it.
- Fix camera and axis ranges before comparing renderers.
- Prefer a contour or heatmap companion when readers need precise lookup; the 3D view is for model shape.

## Export targets

- Screen/gallery PNG: at least 1600 x 1000 pixels.
- Print raster: 300 DPI at final placement size.
- Vector: PDF or SVG for axes, text, and line art. Expect WebGL 3D content to remain rasterized even inside a vector container.
- Use the same aspect ratio for every tool in a comparison.

Check both normal color and grayscale. Color must not be the only cue when categories overlap heavily; add marker or line-style differences if necessary.
