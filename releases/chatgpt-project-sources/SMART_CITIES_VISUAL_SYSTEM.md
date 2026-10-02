# Smart Cities & Location Services — Visual / LaTeX Design System v2.6

Status: **LOCKED for Experiment Report and Process Report**  
Revision: **2026-10-02 · Screenshot-dominant Process pages / arrow-only annotation / accepted exemplars**  
Canonical repository path: `docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`

This document defines the long-term visual identity, LaTeX baseline, report identities, evidence presentation language and technical-visualization rules for the 《智慧城市与位置服务》 project. Detailed prose and argumentation rules are maintained in the Report Writing Guide, not duplicated in Project Settings.

The visual system is stable. Task-specific section names, figures and page structures may adapt to the teacher's requirements, but the locked visual identity and evidence principles must not be silently redesigned.

---

Document routing: [Research Protocol](../research/SMART_CITIES_RESEARCH_PROTOCOL.md) owns research governance; [Report Writing Guide](../report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md) owns detailed report organization, argumentation and prose; [Interaction Evidence Protocol](../process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) owns authenticity, historical recovery, Process narrative ownership, audit and lock; [AGENTS](../../AGENTS.md) owns production, integration and engineering. This file owns visual identity and grammar. Project Settings remains user-maintained in ChatGPT UI. A supplied settings text is a transfer copy, not a second active repository setting.

## 1. Shared Identity

The Experiment Report and Process Report are two independent formal documents.

Their project-wide formal-delivery scope and ordinary-question exclusions are defined in [Report Writing Guide §1](../report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md#1-两份报告的读者与任务); they are not limited to Experiment 1.

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

The Experiment Report is a **teacher-facing course experiment report** with precise technical methods and evidence. It is not a pure engineering audit, project-management record or repository manual.

It answers:

> **What was finally done, why was it done this way, and what do the results show?**

### 3.1 Visual direction

Locked direction:

**A · Modern Academic Minimal cover\
+\
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

The report must not reproduce the complete Human–AI conversation process. It should still explain the actual technical workflow, verification conditions, comparative experiments and evidence-based choices when these are part of the task. Moving chat history out of the report must not remove the system method or the basis for accepting a result.

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

### 3.4 Problem-led writing, with a direct opening

Use a concise, direct overview, conventional section titles and clear essential definitions. In the main body, connect real problems to methods, verification, fair comparison, observed results and technical choices. This is a reasoning structure, not a mandatory sequence of repeated cards or question-mark headings.

Detailed requirements, including the 22 editing categories, are in the [Report Writing Guide](../report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md). Preserve scientifically relevant assumptions, units, uncertainty and negative results while moving hashes, execution permissions, internal status codes and submission operations out of the main narrative unless the teacher specifically requires them.

The writing may explain a final design logically; it must not invent the historical origin of that design. A problem-driven explanation is not permission to retrofit earlier human observations or claim a paper caused a decision without evidence.

### 3.5 Technical verification / workflow diagrams

An Experiment Report diagram may show shared raw input, reference and candidate branches, tools, independent evaluation, acceptance conditions, feedback and stopping. Make data flow, control flow and decision conditions distinguishable and label the relationships that matter.

Do not reduce a major verification figure to unexplained `proposal → check → accept`, but do not add nodes merely for complexity. Show only implemented or explicitly labeled candidate capabilities; distinguish experiment governance, evaluated per-request modes and final deployed processing.

A human observation/challenge node is allowed only when it actually occurred and is supported. The Process-specific Human Reasoning grammar in section 9 is not a template to be imposed on every automated technical check. Local algorithm validity, whole-pipeline effect and final adoption remain different judgments. Dashed feedback or fallback edges must identify their actual applicable modes and whether they were exercised in the illustrated run.

---

## 4. Process Report Identity

The Process Report is the independent formal **AI-use / research-process document**.

Its purpose is not merely to show that AI was used.

It explains:

> **How did I use AI, evidence and experiments to progressively construct a reliable research workflow and make specific experimental decisions?**

The Process Report therefore contains two complementary layers.

### 4.1 Narrative voice

The formal Process Report body uses a **first-person research-retrospective voice** by default.

Use:

- **“我”** for the user's own observation, judgment, challenge, modification, selection and confirmation;
- **“我们”** only when an action was genuinely completed jointly by the user and GPT;
- **GPT** and **Codex** directly when naming the AI research assistant and engineering executor.

Do not make the default body voice sound like a third-party audit by repeatedly writing:

- “用户提出……”;
- “本项目形成……”;
- “系统建立……”.

`User / Human Judgment / Evidence Master` remain valid in diagrams, labels, protocol definitions and generic methodological descriptions, but they are not the default narrative subject of the formal report.

The preferred writing mix is:

- natural first-person research narrative for the main body;
- the user's natural wording for important Human Judgment;
- concise technical language for definitions, states and formal terms.

Professional terminology must respect historical ownership. If GPT later formalized a user's natural-language idea as `UNRESOLVED`, `Source Audit`, or another term, the report may explain that transition, but must not rewrite the earlier user as if the term had originally been theirs.

### 4.2 Section aggregation

Internal production units are not formal report sections.

`Block 01 / Block 02 / Evidence E-xx` may be used internally, but the formal Process Report should aggregate related Decision Units into larger narrative sections such as:

- task understanding and requirement confirmation;
- Human–AI workflow construction;
- research and review mechanisms;
- Multi-Agent system construction;
- Experiment Decision Process;
- document / evidence / visualization system;
- overall workflow reflection.

The exact section structure adapts to the real task. Do not mechanically map one rule, one Decision Unit, or one Evidence ID to one formal section.

### 4.3 Opening and evidence-led pagination

The opening identifies both the user's collaboration with GPT in evolving the workflow and the progress of the actual experiment/task. Keep it concise; place detailed Part/section introductions after the contents, following Report Writing Guide §12. Include the factual screenshot-acquisition note once near the beginning, as specified in Evidence Protocol §5.7.

A Process narrative section or interaction block does not receive a title-only separator page. Place its heading, brief introduction and first relevant screenshot/content together. When space is insufficient, move the heading and its first evidence together rather than leaving an isolated heading or shrinking the screenshot. This rule does not remove the normal cover or contents pages.

Each new interaction block opens with a visible real user message in the ChatGPT UI, as defined in Evidence Protocol §5.6. Continuation pages may carry the same interaction forward without repeating that user message. Summary diagrams and contents are not replacement UI evidence. Use the screenshot-dominant layout in §8.7; avoid treating side commentary as the main page content.


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

The human contribution should be visible as actual reasoning, not merely a final “agree” message. This does not require fabricating a human action in every technical or automated episode: decisions made autonomously within previously approved rules must be identified as such. Policy approval and later per-record choices are different historical facts.

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

**Process Report:**\
how the ideas evolved

**Experiment Report:**\
what technical design remained after convergence

---

## 8. Interaction Evidence

Formal Process Report evidence must come from real Human–AI interaction.

### 8.1 Raw and annotated evidence

For important interaction evidence preserve:

- raw screenshot;
- lossless crop or reproducible LaTeX trim specification;
- annotated screenshot or editable LaTeX/TikZ source plus PDF overlay.

The raw screenshot must remain untouched.

Annotations may be positioned:

- above;
- beside;
- below;
- in the screenshot-side whitespace for precisely targeted vector arrows, without covering chat text.

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

Important decisions should include the real final confirmation. At the start of each new interaction block, preserve the corresponding real user UI message; response-only excerpts may continue that established block but must not become an unanchored new block. Necessary earlier GPT context may appear in its true order alongside the user message.

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
- substitute a screenshot/rasterization of an old LaTeX or PDF report page for the original chat UI;
- present a retrospective summary as the original conversation.

---

### 8.7 Interaction Evidence Visual Grammar

**Original Evidence First.** Work from the user's real ChatGPT Web screenshots, including user-supplied native long captures and their split images. A long capture may be cropped and paginated into formal evidence when the relevant conversation is intact and readable. Preserve **raw / crop / annotated** with direct image embedding and editable TikZ/PDF vector arrows; do not substitute an old report page or redraw the UI. Acquisition, source mapping, effective PPI and explicitly approved native-width use are governed by Evidence Protocol §§5.3—5.7.

**Screenshot-dominant composition.** For a side-by-side interaction page, devote approximately **70%–80% of the usable image-and-note area to the screenshot pane**, with about **20% for right-side commentary** and the remaining space for a narrow gutter/arrow routing. These proportions describe layout allocation, not a requirement to distort or manufacture screenshot pixels. Keep the visible screenshot substantial within that pane; do not satisfy the ratio using a wide empty frame around a tiny image. Reduce commentary or split long evidence before reducing chat readability.

Preserve the aspect ratio and actual available width of approved source images. There is no universal minimum pixel width. When the user has explicitly accepted the existing native-width material and an actual sample/final layout, use it within that approved scope under Evidence Protocol §5.4; do not repeatedly demand wider recaptures merely to match a template. A new layout that makes a crucial phrase unreadable still needs adjustment. Long images are divided vertically at message/paragraph boundaries, with continuation made clear.

An **Interaction Trace** represents one decision interaction. A **Micro Trace** is one phrase correspondence. The **USER anchor** remains the visual and semantic center among relevant GPT-before / User / GPT-after phrases; the start of each new block visibly includes the real user UI, not only a text paraphrase. Necessary prior context stays in its true order.

**Arrow-only annotation on conversation screenshots.** Use precise vector arrows; do not add fluorescent circles, colored outlines/boxes, translucent fills, underlines or circled-number overlays to mark chat text. Remove the former box/highlight requirement from current page components. Native UI features inside the original screenshot remain untouched. The prohibition concerns chat-image annotation, not legitimate nodes/borders in separately drawn technical diagrams or statistical figures.

Each arrow expresses an Evidence-Master-approved relationship between exact phrases, or explicitly points from a concise side note to the phrase it explains. Identify the arrow's meaning and direction; do not make a note-pointer look like a historical causal link. Endpoints terminate at or immediately beside the intended phrase, not at an arbitrary bubble edge. Use whitespace and margins, minimize crossings and never obscure text. Real one-to-one, one-to-many and many-to-one relations are allowed; symmetry and time adjacency are not sufficient evidence. Split a dense set of relationships across pages rather than adding more decoration.

| Interaction role | P2 encoding outside chat text |
|---|---|
| USER anchor / judgment | Apricot accent or Rose accent for its arrow or brief side label |
| GPT before / proposal / context | Blue accent for its arrow or brief side label |
| GPT after / adoption / revision | Violet accent or restrained Blue accent |
| Neutral connector | Ink or Blue accent |
| Body / page | Paper / Panel / Ink |

These roles apply to arrows and concise adjacent labels, not screenshot fills. Preserve the source UI colors. Relation wording or a side-note label reinforces meaning so that color alone does not determine the interpretation.

Side Notes briefly explain the user's action, the following GPT change and, when useful, its later significance. Normally about 40–80 Chinese characters is enough; this is guidance, not a word quota. Use the first-person voice where describing the user's judgment. Do not repeat long chat passages, crowd the page with Micro Trace headings or shrink the screenshot to fit commentary.

A core page normally shows one principal Interaction Trace, optionally a supporting trace, with only the phrase relations needed for its claim. There is no fixed arrow or page quota. A Contact Sheet supports context and lower-tier evidence; it cannot replace a readable core interaction or the required user UI at a new block's start. Arrows are optional when there is no relationship to annotate.

After final XeLaTeX/PDF rendering, inspect the actual page for the user UI entry, screenshot/aside balance, phrase visibility, arrow direction/endpoints, cropping and text occlusion. Follow Evidence Protocol §30.H for the audit fields and source-resolution decision. Preserve approved narrow-source exceptions honestly rather than labeling them as higher-resolution originals. PDF rendering at 200 dpi is an inspection step, not an increase in source resolution.

Prohibited: generated or redrawn chat UI; painting out/editing original words; artificial pixel upscaling or fake sharpening presented as original detail; rasterizing a whole report page and reusing it as chat evidence; arbitrary arrow connections; restoring circles/boxes under another annotation name.

---

## 9. Process Diagram Language

Three formal diagram grammars are locked for **Process Report historical/decision evidence**. Their use must follow actual human reasoning and approved evidence. Experiment Report technical architecture and verification diagrams follow section 3.5; they must not invent human turns to resemble these historical grammars.

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

**User Observation\
→ User Interpretation / Judgment\
→ User Proposal\
→ Evidence / Verification\
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

P2 colors primarily serve as semantic accents. Conversation screenshots follow the arrow-only rule in §8.7; the general fill/border guidance below applies to separate diagrams and page elements, not overlays on chat text.

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

- translucent highlights in separate technical/summary diagrams only, never over conversation screenshots;
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

**publication-plots**\
= publication-quality plotting baseline

**SMART_CITIES_VISUAL_SYSTEM**\
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

Do not use advanced graphics simply because they appear more sophisticated. No task is required to repeat a particular approved report's chart types, number of figures or three-dimensional effect.

### 12.1 Analytical eligibility of advanced charts

| Form | Required meaning and checks |
|---|---|
| **3D space–time trajectory** | The third axis is an actual time or other measured variable, labeled with units; it is not implied altitude. Keep original breaks and equal-time observations. Use comparable views/ranges across methods, and provide a planar projection or sufficient static context when occlusion matters. Display scaling does not alter the processing distance definition. |
| **Parameter response grid / surface** | Display actual tested combinations. Mark untested cells as missing; a mesh joining measured points is a visual aid, not new measurement. Smoothing, interpolation or contours must be explicit and cannot create evidence of an untested optimum or stable region. Keep precise parameter values available. |
| **Sankey / alluvial / state flow** | Flow widths come from real counts or stated weights over consistent identities and populations. Verify conservation and mutually exclusive partitions. Overlapping quantities such as represented coverage and explicit retained points must not be placed beside one another as exclusive terminal states. |
| **Histogram / ECDF / raincloud** | State the statistical unit and denominator. Preserve zeros, missingness, repeated episodes and group dependence. Do not use density smoothing to hide atoms or imply observed values between discrete measurements; record bins/bandwidth when relevant. |
| **Paired change / candidate matrix** | Compare the same records and compatible references. Distinguish development, selection and final confirmation, absent runs, constraint rejection and trade-offs. Normalization must not silently become a new composite score. |
| **Map / density / network** | Use a supported spatial reference and actual underlying data. No invented basemap alignment, road connectivity or population meaning from sample point density. Match spatial scale and disclose aggregation. |
| **Verification / framework figure** | Show real inputs, candidate/reference relations, actual checks and applicable decision/feedback branches. Arrow meaning cannot be inferred merely from layout; implementation and historical human evidence remain separate. |

These conditions guide re-expression of approved evidence, not authorization to add new experiments, classifiers, geographic conversions or methods. If a chart requires a new derived table, preserve its generating code, scope and relationship to the underlying valid runs.

### 12.2 Figure selection and page integration

Choose a small complementary set according to the questions, not one different chart per available library function. A readable histogram may be preferable to a smoothed violin; a paired plot may be better than an unnecessary 3D view. Conversely, a genuine temporal axis or state-flow mapping should be used when it materially clarifies the problem.

Captions identify the object, sample, units, conditions and encoding, then give at most the main supported finding and needed limitation. The prose explains mechanism or choice rather than reading every plotted value. Use representative, adverse and boundary cases under a recorded selection basis; do not illustrate only favorable examples.

Interactive HTML is supplementary unless explicitly required. Essential evidence must remain understandable in the static formal PDF. Check labels, units, view angle, contrast and legends at the actual final size; vector output alone does not guarantee legibility.

---

## 13. Native and Reproducible Production

Technical visuals must be editable and reproducible. When current tools and real inputs permit, GPT may directly author plots, diagrams, LaTeX and complete reports under the user's authorization. Codex may produce them under an approved design or integrate user-accepted GPT artifacts. Tool availability is verified in the actual environment, not assumed from this preferred list.

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

Formal workflow and system-architecture diagrams throughout this project use **draw.io / diagrams.net as the primary editable delivery**. Preserve a real `.drawio` file with editable nodes, connectors and labels, together with corresponding SVG/PDF exports. Embedding a whole-diagram bitmap in draw.io does not meet this requirement.

Statistics, GIS and mathematical/geometric figures use the appropriate reproducible native tools; they do not all require `.drawio`. The tools below may support suitable algorithm or mathematical figures and refinement, but do not replace the primary `.drawio` delivery for formal workflow/system-architecture diagrams. This scope rule adds no unrelated drawing task and does not require redrawing accepted report pages.

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

`real data / real code\
→ plotting / GIS / diagram tool\
→ SVG / PDF\
→ optional visual refinement\
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

### 13.1 Approved-source handoff and review

Preserve an accepted report/figure together with its editable source and real figure inputs or resolvable input identifiers. Integrate the source into the actual generator, rather than only replacing a PDF that a subsequent build will overwrite. Do not silently downgrade an accepted composition or replace approved prose with old template boilerplate.

The author verifies source/data correspondence and renders the actual PDF; independent verification names its real scope and reviewer. GPT's self-review of GPT-authored work is author review, not independent review. User acceptance of a document, research validity, repository integration, evidence lock and submission are separate statuses.

Pure wording/layout changes require content, figure, render and build checks over their impact, not automatic re-execution of every experiment. Changes to algorithms, metrics, data or feedback invalidate affected results and return to research/engineering governance.

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

For **Process Report** prose specifically:

- default to first-person **“我”** when describing the user's own research process;
- use **“我们”** only for genuinely joint work;
- name **GPT** and **Codex** directly when needed;
- preserve the user's natural judgment style at key turning points;
- introduce formal terminology after the real problem appears, rather than writing the whole history as if the terminology existed from the start;
- aggregate related decisions into a coherent research story instead of presenting a stack of internal rules or Blocks.

Avoid:

- redundant prose;
- excessive defensive wording;
- repeated explanation of information already obvious in figures;
- third-person audit-style Process Report narration such as repeated “用户提出 / 本项目形成 / 系统建立”;
- internal project-management vocabulary in final technical prose unless genuinely relevant to the Process Report Workflow Construction section.

Figures, tables and text should complement rather than mechanically duplicate one another.

Detailed Experiment Report prose, content allocation, the 22 editing categories and cross-report writing boundaries are defined once in the [Report Writing Guide](../report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md). For Process Report, the first-person and historical ownership rules in Evidence Protocol §16.1—16.2 remain authoritative. Process opening, closing and the relocation of repetitive production/submission disclaimers follow Report Writing Guide §12. Preserve substantive limits at the relevant point; put build/check records in the source package rather than repeating defensive statements across formal pages.

A concise overview and necessary definitions may be direct; the Experiment body normally introduces an actual problem before a method, then shows verification, comparison and evidence-based choice. Reader-facing language replaces internal status vocabulary, not the underlying assumptions or limits. Do not infer a lexical ban from a few disliked phrases; inspect the whole paragraph's meaning and relevance.

Formal review must inspect the actual PDF page by page at a readable scale. At least 200-dpi rendering is the engineering inspection baseline, not proof of source image resolution. Text extraction, contact sheets and compile logs support but do not replace page inspection. Record unperformed checks honestly.

---

## 16. Reference Files

### 16.1 Rules and reusable templates

Canonical repository locations:

- `docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`
- `docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md`
- `templates/latex/common/p2_cloud_sorbet_colors.tex`
- `templates/latex/experiment-report/experiment_report_template.tex`
- `templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf`
- `templates/latex/process-report/process_report_template.tex`
- `templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf`
- `tools/skills/publication-plots/SKILL.md`

These are routing locations. Listing a path is not proof of installation or synchronization; integration status must be established by actual files and checks.

Template assets under `templates/latex/*/demo-assets/` remain **synthetic/template assets**. They must not be presented as current results, real ChatGPT evidence, user decisions or measurements. Task reports are authored in their own sources using approved shared components, not by overwriting the reference template.

### 16.2 Approved / supplied report references

Use the following canonical attachment names to locate the corresponding reference; maintain actual repository paths and verified hashes in the internal Source Manifest rather than inventing a path here.

| Reference files | Role and allowed use | Scope boundary |
|---|---|---|
| `Experiment_Report_吴博闻_10245102410.pdf` + `Experiment_Report_完整重构_源文件.zip` | **User-accepted Experiment Report exemplar**: teacher-facing problem-led writing, integrated method/verification/comparison, figure composition and editable production | Actual Experiment 1 work, not synthetic; its data, parameters, history and conclusions cannot be reused as a new task's results. User document acceptance does not prove repository integration, teacher grading or submission. |
| `Process_Report_Revised.pdf` + `Process_Report_Revised_LaTeX_Source.zip` | **User-accepted full Process Report exemplar**: integrated Workflow Construction and Experiment Decision Process; first-person retrospective, real user UI at each interaction opening, screenshot-dominant pages, arrow-only correspondence and editable production | Use its real narrative and construction choices as a reference, not as new-task history. Preserve the accepted pair; record actual source hashes, build checks and per-evidence approval scope in the internal manifest/ledger. |
| `WF_WorkflowConstruction_PreTask1_REVISED.pdf` + `WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip` | **Historical pre-Task-1 Process foundation**: retained for the provenance of earlier Workflow Construction | Superseded by the accepted full Process pair as the current writing/layout exemplar. Keep historical originals and approval records in the repository; old boxes, narrow-image layouts and title-only pages are not the current production standard. |
| `Experiment_Report_P2_Exact.pdf` | **Synthetic visual/template preview**, P2 and reusable page-language reference | Not experiment evidence or a competing version of the accepted real report. |
| `Process_Report_P2_Locked_v1.pdf` | **Process template preview** with its recorded scope | The template name does not lock real interactions or prove all new pages accepted. |

Read the exemplar PDF to understand the result and its paired source to reuse production choices. The approved exemplar is the concrete writing/layout reference where old boilerplate is less specific, but cannot silently override current teacher instructions, research validity, P2 identity or Evidence authenticity. For Project Sources, the current full Process PDF/source pair replaces the earlier PreTask pair as the active presentation reference through the approved manifest; the earlier files remain historical repository materials. This reference registration does not itself move or delete files. Existing synthetic previews retain their template role; future rebuilds use the current visual rules.

### 16.3 Pair integrity, reference scope and changes

Record each pair's canonical filenames, real source locations, file hashes, approval source/scope and superseded versions in the existing internal source/reference manifest. Keep missing files or unverified pairings explicit. Do not assert that a ZIP can reproduce a PDF unless that build or a precisely stated narrower check actually occurred.

A changed PDF/source requires renewed pairing and impact review. Store older versions as history; only one specifically identified current task report or reference version may serve as the active exemplar. A renamed file is not automatically newer.

Stable identity/components may be generalized into templates after approval; do not put the exemplar's real measurements or conclusions into synthetic placeholders. The exemplar's page count, chapter count and chart count remain task-specific.

### 16.4 Project Sources distribution

Formal exemplar PDFs and their matching source ZIPs may be included in Project Sources when explicitly approved, with roles distinct from normative Markdown and synthetic templates. Key rules remain readable Markdown, not hidden solely in a ZIP. Broad source archives must not include font binaries, secrets or unrelated personal files.

The upload set and its count come from the current approved [structured manifest](../../evidence/infrastructure/chatgpt-project-source-sync/sources.json), with no permanent file-count constant. Membership checks, stable names and byte equality remain mandatory; detailed distribution/migration rules are in AGENTS §18. Do not remove an existing teacher file or valid reference merely to restore an old count, and do not claim UI upload from local file generation.

---

## 17. Lock State

### LOCKED

The following are stable unless the teacher or user explicitly changes them:

- **P2 · Cloud Sorbet Exact**
- **XeLaTeX** default
- Original Evidence First
- raw/crop/annotated
- phrase-level Micro Trace and exact phrase correspondence
- arrow-only phrase annotation on conversation screenshots; no fluorescent circles, boxes or fills
- real user UI at each new interaction block opening
- screenshot-dominant evidence pages with concise side notes and headings attached to content
- render-level User UI / Phrase / Arrow / Readability Audit
- first-person Process Report narrative
- Report Writing Guide as the detailed prose/argumentation entry
- author review, independent verification and user acceptance distinguished
- precisely routed vector arrows, using only the length required by the real relationship
- direct high-resolution PNG embedding
- TikZ/PDF vector annotation
- multi-page evidence
- Phrase / Arrow Audit
- Experiment Report:
  - A-style Modern Academic Minimal cover
  - B-style Visual Research body
  - teacher-facing, problem-led technical argumentation with a direct overview
  - actual methods, checks, comparisons and result-driven choices rather than management slogans
- Process Report:
  - same P2 identity
  - Workflow Construction
  - Experiment Decision Process
  - real multi-page interaction evidence
  - raw / crop / annotated assets
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

- report section names and problem groupings;
- task page, figure and table counts;
- which advanced chart types materially help the current task;
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
