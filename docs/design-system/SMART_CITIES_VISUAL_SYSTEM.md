# Smart Cities & Location Services - Visual / LaTeX Design System v2

Status: **LOCKED for Experiment Report v1 and Process Report v1**

## 1. Shared identity

- Default engine: **XeLaTeX**.
- Shared palette: **P2 · Cloud Sorbet (exact)**.
- Experiment Report and Process Report use the same visual identity but different information structures.
- Visual quality should come from typography, spacing, figure composition, restrained color and real evidence - not decorative gradients, cyber-style effects, excessive cards or AI-generated technical images.

## 2. Exact P2 palette

| Role | Hex |
|---|---|
| Paper | `#FCFAF7` |
| Ink | `#2D3238` |
| Muted | `#70757A` |
| Light blue | `#D3EAF5` |
| Apricot | `#F5D9B8` |
| Soft rose | `#E8C7D3` |
| Mist violet | `#D7D3EA` |
| Blue accent | `#5B9FBE` |
| Apricot accent | `#D49757` |
| Rose accent | `#B97589` |
| Violet accent | `#8177A8` |
| Rule | `#DDE3E7` |
| Panel | `#FFFDFC` |

Do not silently invent alternative variants. If readability problems appear in a real task, revise the design system explicitly.

## 3. Experiment Report identity

- Base direction: **B · Visual Research Report body + A · Modern Academic Minimal cover**.
- Data/figures/maps are the main visual evidence; Notebook/IDE/terminal screenshots are secondary.
- Each major task should consider at least one Signature Visualization when the research question supports it.
- Report content follows the teacher task, but typography, palette, captions, tables, headers/footers and figure quality remain consistent.

### Brainstorm / method-design rule

Experiment Report does **not** reproduce the raw brainstorm or Human-AI discussion. If the method space is genuinely complex, it may include a distilled technical figure such as `方法设计思路`, `候选方案与最终选择` or `评价指标设计框架`. This figure shows the final technical logic only.

## 4. Process Report identity

Process Report is the AI-use / research-process document. It explains how the final solution was formed through real Human-AI interaction, external evidence and experiments.

Core evidence cycle:

`Idea -> Interaction -> Human Judgment -> Evidence -> Decision`

It should show:
- what GPT proposed;
- what the user noticed, questioned, rejected, modified or selected;
- what remained uncertain;
- what literature/data/experiment was used to verify it;
- how the result changed the plan;
- the final confirmation.

### Brainstorm rule

Process Report may include **multiple real brainstorm stages** (v1/v2/v3) when they directly relate to the experimental method, parameters, metrics, AI critique or visualization design of the teacher task. It should show how ideas diverged and converged. Project management topics such as GitHub setup, report color selection or internal task states do not belong in the formal Process Report body.

The Experiment Report may contain a distilled final technical-design diagram derived from the same reasoning, but it must not copy the Process Report brainstorm figure or chat history.

## 5. Interaction evidence

- Core interactions may span as many pages as necessary for readability; do not impose a fixed 1-2 page limit.
- Use the user's real ChatGPT Web screenshots in the final report.
- Preserve a raw screenshot and an annotated copy.
- Annotation may appear above, beside or below the screenshot.
- Use dark Ink for normal text; P2 colors are mainly for translucent highlights, small labels, arrows, side rules and key annotations.
- A page should normally use no more than 1-2 large filled color areas; additional colors may appear as small highlights when semantically useful.
- General process also retains screenshots, but may be summarized as a contact sheet. Core decisions are expanded in detail.
- Final confirmations for important decisions should also be captured.

## 6. Process Diagram Language

Three diagram grammars are locked:

1. **Editorial Decision Board** - general stage summary, background / judgment / evidence / next step.
2. **Human Reasoning -> Evidence -> Decision** - the main Human-in-the-loop figure. Explicitly show what the user observed, how the user interpreted it, what the user proposed, how it was verified, and the final decision.
3. **Horizontal Candidate Decision Tree** - multiple candidate methods/parameters/metrics, showing retained / modified / rejected / experiment branches.

Global evolution figures should combine these modules rather than introduce a separate decorative visual grammar.

Diagram rules:
- text belongs in clear containers;
- most nodes use white/off-white fill and neutral borders;
- large colored cards are rare;
- use shape, border style, small tags, opacity and line style as semantic channels, not color alone;
- default simple `box -> arrow -> box` chains are not sufficient for formal key figures.

## 7. Figure palette use

Pastels can support background/fill; data marks, lines, boundaries and annotations use corresponding deeper accents when stronger contrast is required. Every visual channel must have meaning.

Read and follow the installed `tools/skills/publication-plots/SKILL.md` (repository-relative path). It is the plotting-quality baseline; this design system defines project identity and document integration. `publication-plots.zip` is a distribution archive, not the runtime source.

## 8. Native production

Technical visuals must be editable and reproducible. Prefer:
- statistics/data: Matplotlib, Plotly;
- GIS: QGIS, GeoPandas, deck.gl/PyDeck, Kepler.gl;
- networks: NetworkX, OSMnx, Gephi;
- workflow/architecture: draw.io, Figma, Graphviz, PlantUML;
- refinement/multi-panel: Figma, Inkscape;
- advanced interaction: D3.js, deck.gl.

Recommended flow:
`real data/code -> professional plotting/GIS -> SVG/PDF -> optional visual refinement -> final output`.

Refinement may change presentation only, never data meaning. Preserve useful sources such as `.py`, `.ipynb`, `.qgz`, `.drawio`, `.svg` and `.html`.

## 9. Generative-image boundary

Do not use gpt-image-2 for data plots, maps, trajectories, flowcharts, system architecture, algorithms, networks or experimental-result figures. It may only provide optional local non-data decorative assets and must never carry factual, numerical or technical evidence.

## 10. Reference files

- `templates/latex/common/p2_cloud_sorbet_colors.tex`
- `templates/latex/experiment-report/experiment_report_template.tex`
- `templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf`
- `templates/latex/process-report/process_report_template.tex`
- `templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf`
- `templates/latex/*/demo-assets/` are synthetic/template assets only and must never be reused as real experimental results.

## 11. Lock state

**LOCKED**
- P2 Cloud Sorbet exact palette;
- Experiment Report: A-style cover + B-style visual-research body;
- Process Report: P2 identity + multi-page annotated evidence + contact sheets + the three locked diagram grammars;
- XeLaTeX default;
- native/reproducible technical visualization;
- raw + annotated interaction evidence workflow;
- distinct brainstorm roles for Process vs Experiment reports.

**ADAPTIVE PER TASK**
- section names and count;
- title metadata required by the teacher;
- specific figures/maps;
- portrait/landscape pages;
- appendix/reference needs;
- how many brainstorm versions are actually useful.
