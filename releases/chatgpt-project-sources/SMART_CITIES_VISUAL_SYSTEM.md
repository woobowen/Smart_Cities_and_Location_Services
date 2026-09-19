# Smart Cities & Location Services — Visual / LaTeX Design System v2.1

Status: **LOCKED for Experiment Report and Process Report**

This document defines the long-term visual identity, LaTeX baseline, evidence presentation language and technical-visualization rules for the 《智慧城市与位置服务》 project.

The visual system is stable. Task-specific section names, figures and page structures may adapt to the teacher's requirements, but the locked visual identity and evidence principles must not be silently redesigned.

---

## 1. Shared Identity

The Experiment Report and Process Report are two independent formal documents.

They share one visual identity but serve different information purposes:

- **Experiment Report** explains what was finally done, why it was done, and what the results mean.
- **Process Report** explains how the research workflow and experimental decisions were formed through real Human–AI interaction, evidence and experiments.

Shared baseline:

- Default engine: **XeLaTeX**
- Shared palette: **P2 · Cloud Sorbet Exact**
- Main text: dark Ink on warm Paper
- Visual quality comes from typography, spacing, hierarchy, evidence composition and restrained color
- Avoid decorative gradients, cyber/AI aesthetics, excessive card layouts and meaningless visual effects
- Technical evidence must come from real data, real code, real experiments or real interaction records

README is not a substitute for either formal report. It is used for project navigation, execution instructions and result indexing.

---

## 2. Exact P2 · Cloud Sorbet Palette

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

These values are exact and must not be silently replaced by visually similar alternatives.

The active single source of truth is:

`templates/latex/common/p2_cloud_sorbet_colors.tex`

Experiment Report and Process Report templates must both reference this common source rather than maintain independent color definitions.

If a real task exposes a genuine readability problem, revise the design system explicitly instead of silently modifying the palette inside one report.

---

## 3. Experiment Report Identity

The Experiment Report is the formal technical and experimental document.

It answers:

> **What was finally done, why was it done this way, and what do the results show?**

### 3.1 Visual direction

Locked direction:

**A · Modern Academic Minimal cover  
+  
B · Visual Research Report body**

Characteristics:

- restrained academic cover;
- figure-driven technical body;
- strong hierarchy;
- generous whitespace;
- high-quality maps, figures and tables as primary evidence;
- minimal decorative elements;
- consistent captions, typography, spacing and semantic color use.

Data, figures and maps are the main visual evidence.

Notebook, IDE and terminal screenshots are secondary and should only appear when they provide evidence that cannot be expressed more clearly as formal figures, tables or text.

### 3.2 Content principle

The Experiment Report may include:

- data description;
- preprocessing and methodology;
- parameter rationale;
- evaluation metrics;
- implementation details that matter scientifically;
- experiments and comparisons;
- sensitivity analysis;
- formal visualizations;
- result interpretation;
- limitations;
- conclusions;
- teacher-required AI/LLM technical critique.

The report must not reproduce the complete Human–AI conversation process.

### 3.3 Brainstorm / method-design rule

Experiment Report does **not** reproduce raw brainstorms or conversational history.

If the method space is genuinely complex and a design figure improves technical understanding, it may contain a highly distilled figure such as:

- `方法设计思路`
- `候选方案与最终选择`
- `评价指标设计框架`
- `最终方法结构`

Such figures represent the **final technical logic**, not the historical interaction process.

They must not simply copy:

- Process Report brainstorms;
- chat screenshots;
- v1/v2/v3 reasoning history;
- Human–AI decision-process diagrams.

---

## 4. Process Report Identity

The Process Report is the independent formal **AI-use / research-process document**.

Its purpose is not merely to show that AI was used.

It explains:

> **How did the user and AI progressively construct a reliable research workflow, and how did specific experimental decisions emerge from real interaction and evidence?**

The Process Report therefore contains two complementary layers.

---

## 5. Process Report Layer A — Workflow Construction

### 5.1 Purpose

Workflow Construction answers:

> **How was the Human–AI research workflow itself built step by step?**

A workflow decision may enter the formal Process Report when it materially changes:

- role boundaries;
- research governance;
- evidence requirements;
- uncertainty handling;
- reproducibility;
- engineering-review mechanisms;
- report architecture;
- formal deliverables;
- visualization production;
- project traceability.

Relevant examples include the real formation of:

- GPT / user / Codex role division;
- Human-in-the-loop decision authority;
- T1 / T2 / T3 / T4 task classification;
- Source Audit;
- CONFIRMED / CANDIDATE / UNRESOLVED;
- UNRESOLVED → fair parallel / ablation experiments;
- Experiment Report / Process Report separation;
- Human–AI Evidence mechanism;
- raw + annotated interaction evidence;
- Brainstorm responsibilities;
- Process Diagram Language;
- P2 visual identity;
- publication-plots integration;
- GitHub as a complete project engineering mirror;
- GitHub engineering archive vs teacher Submission Package;
- Codex push → GPT remote audit → user feedback workflow.

### 5.2 Inclusion criterion

The decision rule is **not**:

> “Is this topic related to GitHub, LaTeX, visualization or project management?”

The correct rule is:

> **Did this interaction materially change the research workflow, evidence chain, role structure, reproducibility strategy or formal output architecture?**

If yes, it may belong in Workflow Construction.

### 5.3 Housekeeping boundary

Pure technical housekeeping normally remains internal evidence and does not enter the formal Process Report body.

Examples:

- deleting `Zone.Identifier`;
- deleting cache files;
- ordinary path repairs;
- routine dependency troubleshooting;
- meaningless shell commands;
- temporary LaTeX warnings;
- trivial filename corrections;
- repeated build logs;
- routine Git status checks.

These may remain in the repository evidence archive if useful for traceability.

The Process Report should show **decisions**, not dump operational logs.

---

## 6. Process Report Layer B — Experiment Decision Process

Experiment Decision Process answers:

> **How were the concrete experimental methods, parameters, metrics and conclusions formed through Human–AI interaction and evidence?**

The core evidence cycle is:

`Idea → Interaction → Human Judgment → Evidence → Decision`

A strong process sequence should make clear:

1. what GPT initially proposed;
2. what the user noticed or questioned;
3. how the user interpreted the problem;
4. what concrete modification, rejection or alternative the user proposed;
5. what remained uncertain;
6. what literature, data, physical principle or experiment was used to verify it;
7. how the evidence changed the plan;
8. what the final decision was.

The human contribution should be visible as actual reasoning, not merely a final “agree” message.

---

## 7. Brainstorm Responsibilities

### 7.1 Process Report Brainstorm

Process Report may preserve multiple real brainstorm stages such as:

`v1 → challenge → v2 → evidence → v3 → final confirmation`

Brainstorm may document either:

### Workflow Construction

Examples:

- alternative GPT/user/Codex role models;
- report architecture alternatives;
- different evidence mechanisms;
- GitHub workflow alternatives;
- competing visualization-system concepts;
- alternative Human–AI decision procedures.

### Experiment Decision Process

Examples:

- preprocessing-method candidates;
- parameter strategies;
- evaluation metrics;
- AI critique ideas;
- visualization strategies;
- alternative experiment designs.

The purpose is to show genuine:

- divergence;
- questioning;
- modification;
- rejection;
- evidence gathering;
- convergence.

### 7.2 Experiment Report Brainstorm

Experiment Report may only preserve a distilled final technical structure when it improves understanding.

The same historical brainstorm must not simply appear unchanged in both reports.

A useful relationship is:

**Process Report:**  
how the ideas evolved

**Experiment Report:**  
what technical design remained after convergence

---

## 8. Interaction Evidence

Formal Process Report evidence must come from real Human–AI interaction.

### 8.1 Raw and annotated evidence

For important interaction evidence preserve:

- raw screenshot;
- annotated screenshot.

The raw screenshot must remain untouched.

Annotations may be positioned:

- above;
- beside;
- below;
- or locally over the screenshot when readability permits.

### 8.2 General process

General process interactions should also be preserved.

When individual interactions are not important enough for full-page treatment, they may be combined into a:

**Process Contact Sheet**

A Contact Sheet should show:

- several real screenshots;
- short stage labels;
- one concise explanation of what changed during the stage.

### 8.3 Core interaction

Core decisions may occupy as many pages as necessary.

There is no fixed 1–2 page limit.

Prefer page breaks at natural message boundaries and avoid cutting a single important message through the middle when possible.

Important decisions should include the real final confirmation.

### 8.4 Interaction Checkpoint

For future high-value decisions, a short 2–4 message Interaction Checkpoint may be used when it naturally improves traceability.

It must remain a real discussion rather than a scripted performance.

### 8.5 Historical recap

A later recap is allowed when useful, but it must be explicitly labeled as:

> **a current summary and confirmation of real historical decisions**

It must never be presented as if it were an original historical conversation.

### 8.6 Prohibited evidence

Do not:

- fabricate ChatGPT UI;
- fabricate user objections;
- create artificial AI mistakes for a richer report;
- rewrite user statements and present them as screenshots;
- invent historical decision sequences;
- treat template interactions as real evidence;
- present a retrospective summary as the original conversation.

---

## 9. Process Diagram Language

Three formal diagram grammars are locked.

### 9.1 Editorial Decision Board

Use for:

- stage summaries;
- compact decision reviews;
- background → judgment → evidence → next step;
- Workflow Construction milestones;
- experiment-stage summaries.

It should feel editorial and report-oriented rather than like a generic flowchart.

### 9.2 Human Reasoning → Evidence → Decision

This is the principal Human-in-the-loop diagram.

It must explicitly show:

**User Observation  
→ User Interpretation / Judgment  
→ User Proposal  
→ Evidence / Verification  
→ Final Decision**

GPT suggestions may appear as context, but the human reasoning chain must not disappear behind AI-generated content.

This grammar is suitable for both:

- Workflow Construction decisions;
- Experiment Decision Process decisions.

### 9.3 Horizontal Candidate Decision Tree

Use when multiple meaningful candidates exist:

- methods;
- parameters;
- metrics;
- workflow alternatives;
- report structures;
- technical approaches.

The horizontal structure may express:

- KEEP;
- MODIFY;
- TEST;
- HOLD;
- REJECT;
- PARALLEL EXPERIMENT;
- FINAL CHOICE.

### 9.4 Global evolution figures

A global workflow-evolution or experiment-evolution figure should combine the three locked diagram grammars as modules.

Do not introduce a new decorative diagram language simply to create visual variety.

### 9.5 Diagram construction rules

- Text belongs in clearly defined containers.
- Most nodes use white/off-white backgrounds.
- Borders, small tags and line styles carry much of the semantic structure.
- Large colored cards are rare.
- Color must not be the only distinction channel.
- Shape, border style, opacity, line style and labels should reinforce meaning.
- Simple default `box → arrow → box` chains are insufficient for major formal figures.
- Avoid unnecessarily complex diagrams that reduce readability.

---

## 10. Color Use in Process Report

Normal body text uses **Ink**.

P2 colors primarily serve as semantic highlights.

Recommended semantic roles:

- blue family: AI proposal / information / context;
- apricot family: human observation / judgment / proposal;
- rose family: risk / rejected assumption / conflict / problem;
- violet family: evidence / verification / convergence / final decision.

These roles are guidelines for consistency, not a requirement that every page use all four colors.

### Large-fill rule

A normal page should generally contain no more than:

- **1–2 large semantic fill colors**

Exceptional key pages may use up to 3 when necessary.

Additional P2 colors may appear in:

- translucent highlights;
- small labels;
- borders;
- arrows;
- annotation markers;
- side rules.

Avoid turning every logical element into a separate colored card.

---

## 11. Figure Palette and Scientific Plotting

Pastels may support backgrounds or light fills.

Data marks, boundaries, lines and annotations should use the corresponding deeper accents where stronger contrast is needed.

Every visual encoding must have analytical meaning.

Before producing formal scientific/data visualizations, read and follow:

`tools/skills/publication-plots/SKILL.md`

and relevant references when needed.

The relationship is:

**publication-plots**  
= publication-quality plotting baseline

**SMART_CITIES_VISUAL_SYSTEM**  
= project visual identity + document integration + Process Evidence language

Project-specific P2 identity takes precedence over generic palette defaults from the plotting skill.

`publication-plots.zip` is a distribution/archive copy, not the normal runtime source.

---

## 12. Signature Visualization

Each major analytical task should consider whether a **Signature Visualization** can materially improve understanding.

A Signature Visualization is not required merely for decoration.

It should answer an important research question more effectively than a basic chart.

Possible forms include:

- trajectory before/after maps;
- anomaly maps;
- road-network overlays;
- density / Hexbin / KDE / H3 maps;
- OD flow maps;
- hotspot or bivariate maps;
- ECDF;
- raincloud / ridgeline;
- small multiples;
- sensitivity heatmaps;
- contour / response surfaces;
- Pareto fronts;
- parallel coordinates;
- Sankey / Alluvial / Chord;
- temporal heatmaps;
- Space–Time Cube;
- coordinated linked views;
- interactive maps or dashboards.

The visualization type must follow the analytical problem.

Do not use advanced graphics simply because they appear more sophisticated.

---

## 13. Native and Reproducible Production

Technical visuals must be editable and reproducible.

Preferred tools include:

### Statistics / analytical graphics

- Matplotlib
- Plotly
- Altair when appropriate

### GIS / spatial visualization

- QGIS
- GeoPandas
- PyDeck / deck.gl
- Kepler.gl
- Folium
- Datashader when appropriate

### Networks

- NetworkX
- OSMnx
- Gephi / Cytoscape when appropriate

### Workflow / architecture / algorithm diagrams

- draw.io / diagrams.net
- Figma
- Graphviz
- PlantUML
- TikZ when appropriate

### Refinement / multi-panel assembly

- Figma
- Inkscape
- Illustrator / Affinity when available
- QGIS Layout for cartographic composition

### Advanced interactive visualization

- D3.js
- deck.gl

Recommended production flow:

`real data / real code  
→ plotting / GIS / diagram tool  
→ SVG / PDF  
→ optional visual refinement  
→ formal output`

Visual refinement may change:

- alignment;
- typography;
- annotation;
- whitespace;
- panel composition.

It must not change:

- data values;
- geometry;
- statistical relationships;
- experimental conclusions.

Preserve valuable editable sources such as:

- `.py`
- `.ipynb`
- `.qgz`
- `.drawio`
- `.svg`
- `.html`

where relevant.

---

## 14. Generative-Image Boundary

Do not use gpt-image-2 or another generative-image model to directly produce complete:

- data plots;
- statistical figures;
- maps;
- trajectory visualizations;
- flowcharts;
- architecture diagrams;
- algorithm diagrams;
- network diagrams;
- experimental-result figures.

These outputs must be grounded in real data or explicit technical structure and therefore require reproducible native production.

AI-generated imagery may only be used, when explicitly justified, as:

- local decorative material;
- non-data assets;
- non-evidence visual support.

It must never carry:

- experimental facts;
- quantitative relationships;
- technical structure;
- important labels;
- important numerical information.

---

## 15. Writing and Layout Principles

Formal reports should feel like careful student research reports rather than:

- engineering audit documents;
- white papers;
- AI-generated long-form answers;
- dashboards filled with cards.

Use:

- clear hierarchy;
- restrained visual emphasis;
- strong figure-caption integration;
- natural Chinese writing;
- English technical terminology where appropriate.

Avoid:

- redundant prose;
- excessive defensive wording;
- repeated explanation of information already obvious in figures;
- internal project-management vocabulary in final technical prose unless genuinely relevant to the Process Report Workflow Construction section.

Figures, tables and text should complement rather than mechanically duplicate one another.

---

## 16. Reference Files

Current installed sources:

- `docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`
- `templates/latex/common/p2_cloud_sorbet_colors.tex`
- `templates/latex/experiment-report/experiment_report_template.tex`
- `templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf`
- `templates/latex/process-report/process_report_template.tex`
- `templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf`
- `tools/skills/publication-plots/SKILL.md`

Template assets under:

`templates/latex/*/demo-assets/`

are synthetic/template assets only.

They must never be presented as:

- current experiment results;
- real ChatGPT evidence;
- real user decisions;
- real measurements.

Task-specific reports should be created from copies of the locked templates rather than overwriting the reference templates.

---

## 17. Lock State

### LOCKED

The following are stable unless the teacher or user explicitly changes them:

- **P2 · Cloud Sorbet Exact**
- **XeLaTeX** default
- Experiment Report:
  - A-style Modern Academic Minimal cover
  - B-style Visual Research body
- Process Report:
  - same P2 identity
  - Workflow Construction
  - Experiment Decision Process
  - real multi-page interaction evidence
  - raw + annotated screenshots
  - Contact Sheets
- Process Diagram Language:
  - Editorial Decision Board
  - Human Reasoning → Evidence → Decision
  - Horizontal Candidate Decision Tree
- distinct Brainstorm roles for Experiment vs Process Report
- native/reproducible technical visualization
- publication-plots as plotting-quality baseline
- Signature Visualization principle
- restrained P2 semantic-color use
- prohibition on generative images as technical/data evidence

### ADAPTIVE PER TASK

The following adapt to the teacher's actual task:

- report section names;
- number of sections;
- title metadata;
- specific charts and maps;
- page orientation;
- portrait / landscape inserts;
- appendix structure;
- references;
- exact number of Interaction Evidence pages;
- exact number of Brainstorm stages;
- which Workflow Construction decisions are worth formal inclusion;
- which experiment decisions require detailed evidence.

---

## 18. Process Report Inclusion Test

Before adding a workflow-related item to the formal Process Report, ask:

1. Did this interaction materially change the Human–AI workflow?
2. Did the user make a meaningful judgment, correction, rejection or selection?
3. Did it alter roles, evidence, reproducibility, research governance or formal output architecture?
4. Is there real interaction evidence supporting the change?
5. Would showing it help the reader understand how the final workflow was constructed?

If the answer is substantially yes, it may belong in **Workflow Construction**.

If the content is mainly:

- command execution;
- cache cleanup;
- ordinary debugging;
- path repair;
- build housekeeping;
- repeated confirmation with no substantive decision;

keep it in internal evidence instead.

The formal Process Report should explain the evolution of the research process, not reproduce the complete engineering log.