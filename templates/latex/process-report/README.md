# Process Report Template

This directory contains the locked LaTeX reference template for the formal
**Process Report / AI-Use and Research-Process Report**
of the Smart Cities & Location Services project.

The template follows:

**Smart Cities Visual / LaTeX Design System v2.1**

It shares the same P2 · Cloud Sorbet visual identity as the Experiment Report,
but the two reports have different information responsibilities.

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
- an annotated copy.

The raw screenshot must remain unchanged.

Annotations may appear:

- above the screenshot;
- beside it;
- below it;
- locally over it when readability permits.

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

- translucent highlights;
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

Do not overwrite the locked reference template for a specific assignment.

For each formal task:

1. copy the reference template into the task's report directory;
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