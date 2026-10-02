# Process Report Template

This directory contains the locked LaTeX reference template for the formal
**Process Report / AI-Use and Research-Process Report**
of the Smart Cities & Location Services project.

The template follows:

**Smart Cities Visual / LaTeX Design System v2.6**

It shares the same P2 · Cloud Sorbet visual identity as the Experiment Report,
but the two reports have different information responsibilities.

The [Report Writing Guide v1.2](../../../docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md) defines project-wide formal dual-report scope and later-task Process continuity. Later tasks introduce or cite the real shared foundation as needed for independent reading, then focus on their actual additions, corrections, rejected directions and Experiment Decision Process. Preserve source scope and Lock state; do not copy the entire earlier report or create new disputes to imply iteration. Evidence Master is explicitly appointed by the user under [Evidence Protocol §4.1](../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md#41-evidence-master--master-planning-conversation).

---

## 1. Purpose

The Process Report explains how the project was developed through
**real Human–AI interaction, evidence, experiments and user decisions**.

It is not merely a record showing that AI was used.

The report contains two complementary layers:

### A. Workflow Construction

Explains how the Human–AI research workflow itself was progressively built.

Examples of decisions that may belong here include:

- GPT / user / Codex role division;
- Human-in-the-loop decision authority;
- T1 / T2 / T3 / T4 task classification;
- Source Audit;
- CONFIRMED / CANDIDATE / UNRESOLVED;
- fair parallel / ablation experiments for unresolved questions;
- Experiment Report / Process Report separation;
- Human–AI Evidence rules;
- Brainstorm responsibilities;
- Process Diagram Language;
- Visual System decisions;
- `publication-plots` integration;
- GitHub as the complete project engineering mirror;
- separation between the GitHub project and the teacher Submission Package;
- Codex push → GPT remote review → user feedback workflow.

A workflow-related item belongs in the formal report when it has
**real decision value** and materially changes the research process,
evidence chain, reproducibility, responsibility structure or formal output.

### B. Experiment Decision Process

Explains how concrete experimental choices were formed, including:

- methods;
- assumptions;
- parameters;
- evaluation metrics;
- AI criticism;
- comparisons and ablations;
- interpretation of experimental evidence;
- final research decisions.

The core evidence cycle is:

`Idea → Interaction → Human Judgment → Evidence → Decision`

---

## 2. Relationship to the Experiment Report

The two reports are independent formal documents.

### Experiment Report

Answers:

> What was finally done, why was it done this way, and what do the results show?

It contains the final technical method, parameter rationale, metrics,
experiments, visualizations, results, limitations and conclusions.

It does not reproduce the complete Human–AI interaction history.

### Process Report

Answers:

> How were the workflow and research decisions actually formed?

It preserves the real development process, including user observations,
questions, corrections, rejections, selections, evidence and final confirmations.

The same real research history may support both reports,
but the same Brainstorm figure, chat screenshot or process diagram
should not simply be copied into both documents.

---

## 3. Brainstorm Policy

The Process Report may preserve genuine multi-stage Brainstorm evolution,
for example:

`v1 → challenge → v2 → evidence → v3 → final confirmation`

Brainstorm may concern either:

### Workflow Construction

Examples:

- role allocation;
- evidence mechanisms;
- workflow alternatives;
- report architecture;
- GitHub workflow;
- visualization-system choices;
- Human–AI decision rules.

### Experiment Decision Process

Examples:

- preprocessing methods;
- parameter strategies;
- metric design;
- AI critique;
- experimental comparisons;
- visualization strategies.

The report should show genuine:

- divergence;
- questioning;
- modification;
- rejection;
- evidence gathering;
- convergence.

The Experiment Report may contain only a distilled final technical-design
figure when such a figure genuinely improves technical understanding.

---

## 4. Interaction Evidence

Every formal interaction shown in the Process Report must come from
**real project history**.

For important interactions preserve:

- a raw screenshot;
- a lossless crop or reproducible LaTeX trim specification;
- an annotated copy or editable LaTeX/TikZ source plus PDF overlay.

The raw screenshot must remain unchanged.

Annotations may appear:

- above the screenshot;
- beside it;
- below it;
- in adjacent whitespace as precise arrows without covering chat text.

### General interactions

General process interactions should also be preserved.

Several related interactions may be summarized as a
**Process Contact Sheet** containing:

- real screenshots;
- concise stage labels;
- a short explanation of what changed.

### Core interactions

Important decisions may span as many pages as needed.

There is no fixed one-page or two-page limit.

Prefer natural message boundaries when splitting screenshots.

Important decisions should include the real final confirmation.

### Historical recap

A later recap is allowed only when it is clearly identified as:

> a current summary and confirmation of real historical decisions

It must never be presented as if it were the original historical conversation.

### Prohibited evidence

Do not:

- fabricate ChatGPT UI;
- fabricate user objections;
- invent Human–AI interaction;
- deliberately create AI mistakes for a richer report;
- rewrite user statements and present them as screenshots;
- invent historical decision sequences;
- present retrospective summaries as original history;
- use template interactions as real evidence;
- fabricate experimental outcomes or AI criticism.

---

## 5. Formal Process Diagram Language

Three diagram grammars are locked.

Formal workflow/architecture diagrams retain real editable `.drawio` nodes, connectors and labels plus SVG/PDF exports under [Visual System §13](../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md#13-native-and-reproducible-production). This delivery rule does not turn screenshot annotations or statistical/GIS/mathematical figures into draw.io tasks, and does not require redrawing accepted reference pages.

### 1. Editorial Decision Board

Use for:

- general stage summaries;
- Workflow Construction milestones;
- experiment-stage summaries;
- compact background / judgment / evidence / next-step layouts.

### 2. Human Reasoning → Evidence → Decision

This is the primary Human-in-the-loop diagram.

It should explicitly show:

`User Observation`
→ `User Interpretation / Judgment`
→ `User Proposal`
→ `Evidence / Verification`
→ `Final Decision`

GPT proposals may provide context,
but the user's reasoning must remain visible.

### 3. Horizontal Candidate Decision Tree

Use when several meaningful alternatives exist, such as:

- methods;
- parameters;
- metrics;
- workflow mechanisms;
- report structures;
- technical approaches.

Typical branch states include:

- KEEP;
- MODIFY;
- TEST;
- HOLD;
- REJECT;
- PARALLEL EXPERIMENT;
- FINAL CHOICE.

Global evolution figures should combine these established grammars
instead of introducing a separate decorative diagram language.

---

## 6. Housekeeping Boundary

The Process Report records meaningful decisions,
not the complete engineering log.

Pure housekeeping normally remains in internal evidence, for example:

- `Zone.Identifier` removal;
- cache cleanup;
- ordinary path repair;
- routine dependency troubleshooting;
- temporary LaTeX warnings;
- trivial filename fixes;
- repeated shell commands;
- routine Git status checks;
- other non-decision Debug details.

A GitHub, LaTeX, visualization or project-management topic is **not**
automatically excluded.

The correct test is:

> Did this interaction materially change the Human–AI workflow,
> evidence mechanism, reproducibility strategy, role structure
> or formal output architecture?

If yes, it may belong in **Workflow Construction**.

---

## 7. Visual Rules

The template uses the locked:

**P2 · Cloud Sorbet Exact**

Normal body text uses dark Ink.

P2 colors are primarily used for:

- translucent highlights in separate technical diagrams/page elements only, never over conversation screenshots;
- small semantic labels;
- arrows;
- side rules;
- borders;
- annotations.

A normal page should generally use no more than
**1–2 large filled semantic color areas**.

Most text containers should use white/off-white backgrounds
and neutral borders.

Avoid:

- excessive colored cards;
- cyber/AI aesthetics;
- decorative gradients;
- meaningless visual effects;
- generic `box → arrow → box` diagrams for major formal decisions.

---

## 8. Demo Assets

`demo-assets/` contains template-only synthetic assets.

The current multi-page layout uses the plain LaTeX specimens in
`demo-assets/multipage_specimens.tex`. They are explicitly **NOT CHAT UI** and
contain placement instructions, not invented conversation. The older
`interaction_part1.png`, `interaction_part2.png` and `interaction_part3.png`
are preserved historical demo assets and are not used by the current template.

They exist only to demonstrate:

- layout;
- page composition;
- evidence placement;
- diagram integration.

They are **not**:

- experimental results;
- real ChatGPT interactions;
- real user decisions;
- real project evidence.

Every demo screenshot and diagram must be replaced by real project material
before producing a formal task report.

---

## 9. Installed Sources

Use the installed project sources as the authoritative runtime references.

### Visual specification

`../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`

### Shared P2 palette

`../common/p2_cloud_sorbet_colors.tex`

### Publication plotting skill

`../../../tools/skills/publication-plots/SKILL.md`

When producing formal analytical figures,
read the installed `publication-plots` skill and relevant references.

Distribution ZIP files are archives,
not the normal runtime source.

---

## 10. Creating a Task-Specific Report

### Template and accepted real-content reference

- Visual / Layout Template Reference: [Process_Report_P2_Locked_v1.pdf](preview/Process_Report_P2_Locked_v1.pdf), at `templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf`.
- Historical preview before the arrow-only migration: [2026-09-29 snapshot](preview/history/Process_Report_P2_Locked_v1_20260929.pdf). It is retained for provenance and is not a competing active preview.
- Current user-accepted complete reference: [Process_Report_Revised.pdf](../../../reports/process-report/experiment1-revised/Process_Report_Revised.pdf) and [paired source](../../../reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip).
- Historical PreTask foundation: [PDF](../../../reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_REVISED.pdf) / [source](../../../reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip). Its [historical PARTIAL reproduction](../../../evidence/infrastructure/SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md) remains unchanged; it is no longer the active layout exemplar.

The complete accepted reference shows real user-UI openings, screenshot-dominant composition and arrow-only annotation. Preserve its task-specific evidence and actual approval scope. Neither the synthetic template preview nor whole-document acceptance grants new per-evidence Lock. The current template preview remains synthetic and is not a Project Source in this task.

Do not overwrite the locked reference template for a specific assignment.

For each formal task:

1. copy the reference template and its `components/` directory into the task's report directory; keep inputs project-relative and point the palette input to the existing common source;
2. keep the shared P2 palette and locked visual language;
3. replace all demo content with real task content;
4. insert genuine screenshots and interaction evidence;
5. use real data, real experiments and real decisions;
6. preserve necessary editable figure sources;
7. compile and validate the task-specific report independently.

Task-specific section names may adapt to the teacher's requirements.

The locked visual identity and evidence principles should remain unchanged.

---

## 11. Compilation

Compile from this directory with XeLaTeX through `latexmk`:

```bash
latexmk -xelatex \
  -interaction=nonstopmode \
  -file-line-error \
  -halt-on-error \
  -outdir=build \
  process_report_template.tex
```

## 12. Phrase-level Interaction Evidence authoring

Required reads: [Evidence Protocol v2.7](../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md), [Visual System v2.6](../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md), [Report Writing Guide v1.2](../../../docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md), [AGENTS](../../../AGENTS.md), and the user-designated Evidence Master's approved annotation specification. Research governance lives in [Research Protocol](../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md).

Production chain:

raw screenshot → Evidence Master annotation spec → lossless crop → direct LaTeX embed → TikZ Micro Trace → XeLaTeX → 200-dpi render inspection → User UI / Phrase / Arrow / Readability Audit → Evidence Lock.

Evidence Master selects the real user-UI entry, exact phrases, relations, order and captions. Codex implements approved geometry and wording. Keep raw files unchanged, preserve crop parameters and annotated LaTeX/PDF. Review the Interaction Window; temporal adjacency alone never supports a relation.

`components/interaction_evidence.tex` uses the existing shared P2 palette. The parent loads TikZ with `arrows.meta,calc` and the common palette before loading this component. It contains no screenshot-specific coordinates.

| API | Usage |
|---|---|
| `\IEScreenshot[graphicx options]{path}{width}` | Direct PNG include; `trim={left bottom right top},clip` supported. |
| `interactionevidence[graphicx options]{path}{width}` | Image with normalized coordinates: (0,0) bottom left, (1,1) top right of displayed crop. |
| `\IEAnchor{name}{x,y}` | Named approved phrase endpoint. |
| `\IECurvedArrow[style]{from}{to}` | Curved phrase-to-phrase connector. |
| `\IERoutedArrow[style]{TikZ path}` | Explicit route through whitespace. |
| `\IESideNote[style]{x,y}{text}` | Physical-size text beside image; default 34 mm width. |
| `\IEProvenance[style]{x,y}{label}` | Provenance label. |
| `\IEAssetLabel{x,y}{raw/crop/annotated}` | Asset-layer label. |

Styles: `ie before` = Light Blue; `ie user` = Apricot; `ie user rose` = Soft Rose; `ie after` = Mist Violet; connector = Blue accent; body = Ink. Arrow semantics come from the spec. Keep evidence coordinates in each task page, not the reusable component. Cropping changes the coordinate basis; recalculate endpoints against the displayed crop.

Use approximately 70%–80% of the image-and-note width for the visible screenshot and about 20% for concise commentary. Each new interaction opens with the corresponding real user UI; continuation pages carry that same interaction forward. Place the heading, brief introduction and first screenshot together. The template uses plain synthetic specimens to demonstrate geometry, never fabricated ChatGPT UI.

Effective PPI = displayed-region pixels / physical display inches, taking the smaller horizontal/vertical value. Normally target >=180, preferably >=200. An explicitly accepted source and layout may retain `APPROVED_NATIVE_WIDTH` with its actual dimensions/PPI and approval scope. Do not demand a repeat recapture of the same accepted material. Rendering at 200 dpi does not improve source detail. Never AI-upscale or redraw UI.

Check USER UI ENTRY, ANNOTATION MODE, PHRASE MATCH, ARROW RELATION, ARROW ENDPOINT, PAGE READABILITY and SOURCE RESOLUTION against the final PDF render. Conversation overlays are arrow-only, without circles, boxes, fills, underlines or numbered overlays. The retired box/marker APIs deliberately are not provided by the current component. Technical diagram node borders remain legitimate. Evidence Master performs the actual final review/Lock; engineering checks do not grant it. Historical box checks remain historical. Global Workflow Evolution Map production follows the actual Evidence Lock prerequisite.

## 13. Synthetic fixture and canonical preview

The template contains a minimal `interactionevidence` example. All sample phrases and arrows are **SYNTHETIC / TEMPLATE ONLY**, not historical interaction. The raster background is a plain typeset specimen, not reconstructed ChatGPT UI. `demo-assets/micro_trace_specimen.tex` is its editable source. Generate its native PNG at 300 dpi, then include it directly; TikZ overlays remain vector in the final PDF.

From `demo-assets/`:

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build micro_trace_specimen.tex
pdftoppm -f 1 -singlefile -r 300 -png build/micro_trace_specimen.pdf micro_trace_specimen
```

From the process-report directory, clean with `latexmk -C -outdir=build process_report_template.tex`, then run the compilation command in section 11. Render the fresh PDF:

```bash
pdftoppm -r 200 -png build/process_report_template.pdf build/process-page
```

Inspect every page and the full-resolution Micro Trace page for phrase accuracy, endpoints, side-note clipping, readable raster text and vector overlay. After validation refresh the sole [canonical preview](preview/Process_Report_P2_Locked_v1.pdf); `v1` is its locked visual identity filename, not the governance version. Do not create parallel active previews.

The Experiment Report preview remains independent. Historical distribution ZIPs do not supersede installed sources.
