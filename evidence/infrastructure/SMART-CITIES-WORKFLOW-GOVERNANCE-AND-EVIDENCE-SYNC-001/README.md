# Workflow governance and evidence synchronization

Run: SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001\
Scope: one-time governance, reusable Process template and Project Sources synchronization. No Experiment 1 implementation, notebook execution, parameter search or formal result production.

## Authorization and baseline

The user explicitly cleared BLOCKED_USER_CHANGES and identified the untracked v2.2 file as the authoritative upgrade baseline. Its pre-modification SHA256 is:

`2630c5abf99f7ff78dfeb85042f87693d1629d580bd0d79ba46f1e9cb32e648c`

The canonical path did not exist. A read-only backup was saved outside the repository at `/tmp/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL_v2_2_preupgrade.md`; it is not committed. The original filename was removed after migration. `baseline-retention.json` records a content-line comparison after equivalent Markdown hard-break normalization: only the version content changed; all other v2.2 content, including its 39 numbered sections, was retained. Two trailing spaces were changed to backslash hard breaks to pass the staged whitespace check. This is preservation evidence, not a second active protocol.

`preflight.json` records main, starting SHA, initial status, palette hash and hashes for all 106 tracked task1 files. The first command was `ls -la`; the root contained `.git`, `.gitignore`, `AGENTS.md`, `docs`, `evidence`, `releases`, `task1`, `templates`, `tools`.

## Active responsibilities and consistency review

| Pair / issue | Review and resulting rule |
|---|---|
| Research Protocol ↔ AGENTS | Research v1.0 owns T1–T4, sources, uncertainty, fair comparison, spatiotemporal semantics, parameters, metrics and AI critique. AGENTS links to those definitions and retains engineering gates. Removed duplicated long lists are covered by Research §§A, F, G or Visual §§3–15, not discarded policy. |
| Evidence Protocol ↔ Visual System | Evidence v2.3 owns authenticity, history, relationships, audit and lock. Visual v2.2 owns phrase-centered encoding and layout. Original First, multi-page priority, raw/crop/annotated, >=180 PPI (prefer >=200), direct PNG, no generated/redrawn UI or upscale agree. |
| Evidence Master ↔ Codex | Master chooses exact phrases, relations, order, text and inclusion; Codex implements approved geometry and checks. No real screenshot/spec was supplied this run, so no real Evidence Lock is asserted. |
| Visual System ↔ LaTeX | Shared palette unchanged; before P1/C1, User P2/C2 (P3/C3 optional), after P4/C4, connector C1, body Ink. No component color redefinitions. |
| Active sources ↔ mirror | Installed governance/templates remain active. Eleven canonical payloads are hash-checked; Project Settings and internal Evidence Plan are excluded. |
| Single active versions | Research v1.0, Evidence v2.3, Visual v2.2. No v2_2/v2_3 parallel filenames; preview keeps its existing locked-identity filename. Historical v2.1 ZIP is explicitly archive-only. |

Project Settings was neither accessed nor changed; its routing responsibilities are those supplied in the approved prompt, not a claimed audit of current UI contents.

## Process template and validation

Added `components/interaction_evidence.tex` with direct include, trim/clip, highlight, outline, anchor, numbered marker, curved/routed arrows, side note, provenance/asset labels and P2 styles. Coordinates remain per page. README contains API and production chain. The new synthetic PNG comes from `demo-assets/micro_trace_specimen.tex`: native 300-dpi rasterization of a plain text specimen, with no ChatGPT UI reconstruction. Overlay remains vector.

The initial specimen build failed because the preceding edit used the wrong working directory and the unapplied draft still referenced unavailable `standalone.cls`. `specimen-initial-failure.txt` preserves that failure. One correction applied the intended existing `article` + geometry setup and corrected the edit directory; the specimen then compiled. No dependency installation or engine change was needed. Later visual refinement tightened phrase bounds/arrow endpoints and fixed existing sidebar top alignment; a fresh clean build followed.

Actual validation commands:

```bash
# In templates/latex/process-report/demo-assets
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build micro_trace_specimen.tex
pdftoppm -f 1 -singlefile -r 300 -png build/micro_trace_specimen.pdf micro_trace_specimen
# In templates/latex/process-report
latexmk -C -outdir=build process_report_template.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build process_report_template.tex
pdfinfo build/process_report_template.pdf
pdftotext -layout build/process_report_template.pdf -
pdfimages -list build/process_report_template.pdf
pdftoppm -r 200 -png build/process_report_template.pdf build/render/page
pdftocairo -f 5 -l 5 -svg build/process_report_template.pdf build/render/micro-trace.svg
# From repository root
python3 evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py
python3 evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py
git diff --check
```

`build_preview.py` reproduces the final clean build/render, without automatically replacing the canonical preview. After visual review the fresh PDF was copied to the existing preview path, then mirrored. `compile-commands.json` records real exit codes. `build-console.txt`, `latex-log.txt`, `pdfinfo.txt`, `pdf-text.txt`, `pdf-images.txt`, `render-commands.json` and render/vector console files preserve results. `visual-inspection.json`, the two page contact sheets and `micro-trace-200dpi.png` record visual checking. Final template: 12 pages; all five embedded rasters >=238 PPI, new specimen 300 PPI. SVG inspection verified three translucent vector highlights and two connector paths over one raster specimen. These are template engineering checks, not audits of real historical evidence.

`whitespace-normalization.json` records equivalent Markdown hard-break formatting and removal of trailing log whitespace after the first staged check flagged them. Raw tool output remains in ignored build logs; committed text captures preserve all substantive output.

The pre-push clean-worktree gate found that AGENTS and Visual System hard-break normalization had not yet been staged. The initial local commit had not been pushed. Both files were staged, an index-to-mirror byte comparison was added, and the local commit was amended only after checks passed. No remote history was rewritten.

`validation.json` is the measured result for versions, original-file integrity, archive provenance, links/anchors, manifests, compile log, PPI, scope and syntax. `publication-check.json` records the commit-scope file/secret/size review. `source-inventory.json` and `mirror-sha256.txt` record all eleven payload hashes; the manifest itself is not self-hashed.

## Source provenance

Teacher slides were inspected as OOXML (43 slides, opening course/assessment slide). The two notebooks have 33 and 19 cells and exactly match their assignment ZIP members. No notebook or task1 script was executed. All supplied task1 outputs are historical/pre-generated, not current-run sample or full experiments.

The existing original Project Source `publication-plots.zip` was retained at its established path. Its SHA256 matches the previous baseline record and its six effective files match installed Skill sources. The sanitized `releases/skills/publication-plots.zip` differs only in packaging metadata. No archive was regenerated. The unchanged Experiment template/preview are independently checked against the starting Git commit. Process preview and all template assets remain synthetic, not formal Experiment or Process evidence.

## Limits, environment and handoff

No real Evidence page or formal report body was authored; the Evidence Plan is an empty schema awaiting Master-approved raw/spec. No research decision, experimental parameter, result, P2 hex or teacher original was changed. No Project Settings file was created. No missing logical source was substituted with a guessed version. Local mirror synchronization does not upload files to ChatGPT.

New system packages: none. New language packages: none. New toolchain/fonts: none. Shell/environment configuration changes: none. Existing Linux XeLaTeX/latexmk, Poppler, Python and Pillow were used. Build intermediates stay in ignored build directories. The optional external read-only backup remains outside Git.

After successful checks, publish one logical commit to origin/main, without force push. The exact commit and freshly queried remote SHA are reported after push; storing that commit's own SHA in its tree would be self-referential. Engineering verification does not replace GPT's independent remote repository audit. Stop after publication and wait for that audit; do not continue Experiment 1.
