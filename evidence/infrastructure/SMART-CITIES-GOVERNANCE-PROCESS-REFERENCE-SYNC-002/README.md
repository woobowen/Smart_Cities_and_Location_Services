# Governance / Process Reference Sync 002

Run: SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002. One-time synchronization under the user's supplied prompt; no design doc or implementation plan was created.

The five approved release inputs were hashed before changes, then the three governance documents and two immutable report artifacts were copied to their canonical repository paths. AGENTS was mechanically updated from 11 to 13 files. Visual System and the Process template README now distinguish the layout template from the accepted real-content reference and disclose its source-reproduction limitation. The established sync/validation scripts were updated in place; no second sync implementation was created.

Active sources were then synchronized back into the strict 13-file bundle. The manifest has 13 PROJECT_SOURCE rows and freshly calculated SHA256 values. Protocol remains exactly the supplied v2.4 bytes; Visual is v2.3. Approved-to-active mechanical differences are captured separately from the user's own governance revision.

## Verification and limitation

- [Preflight](preflight.json): branch, starting local/remote SHA, command outputs, authorized/unrelated dirty files, concurrency check and 5,722 protected-file hashes.
- [Approved hashes](approved-input-sha256.txt), [final bundle hashes](bundle-sha256.txt), [directory listing](directory-listing.txt), [sync check](sync-check.txt).
- [Cross-document audit](cross-document-audit.md), [governance markers](governance-version-check.txt), [historical-reference classification](legacy-eleven-classification.txt).
- [Source archive check](source-archive-check.md): **SOURCE_ARCHIVE_BUILD: PARTIAL**. The unchanged source actually compiles to 31 pages, but all 31 pages have text differences from the approved revised PDF, representative annotations differ, and nine arrow glyphs are missing. This explicitly permitted limitation does not block synchronization; neither approved input was edited.
- [Machine reference checks](source-reference-validation.json), [visual inspection](visual-inspection.json), [200-dpi renders](render/), [final LaTeX log](source-build-latex-log.txt), and separate failed-attempt logs preserve the actual checks. The first page's substantial whitespace and page-2 continuation were inspected and recorded, not silently redesigned.
- [Current validation](validation.json): bundle/mapping/manifest integrity, immutable approved reference bytes, representative PDF inspection, recorded build limitation, protected files, governance versions, links, syntax, cleanup/idempotency/failure cases and Git checks. The final `--index` run also verifies staged bytes. Historical validation JSON remains unchanged.

Representative verification only establishes the recorded engineering properties. It does not independently authenticate every historical screenshot, certify every screenshot's source PPI or grant Evidence Master Lock. Governance-rule consistency and full archive reproduction are separate results.

## Actual verification entry points

From repository root, using the existing environment:

```bash
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py --index
test "$(find releases/chatgpt-project-sources -maxdepth 1 -type f | wc -l)" -eq 13
sha256sum releases/chatgpt-project-sources/*
git diff --check
git diff --cached --check
```

Reference verification used `pdfinfo`, `pdftotext -layout`, the archive's `bash build_31p.sh` (XeLaTeX/latexmk then pdfunite), and `pdftoppm -r 200`. Exact temporary paths, dependency hashes and process-local overrides are in [environment-changes.json](environment-changes.json), [source-build-result.json](source-build-result.json) and [render-commands.json](render-commands.json). Committed text logs remove trailing whitespace only; raw build intermediates stay under the recorded `/tmp` directory.

## Scope and publication

The three unrelated initial root ZIPs remain untracked and unchanged. Research Protocol, all existing Task 1 files, teacher materials, notebooks, P2 colors, template sources/previews, installed plotting Skill and prior validation records are protected. No Task 1 code, experiment, parameter scan, Notebook or sample/full research run was executed. No new formal research figure or report body was authored. The existing accepted Process reference is historical/user-approved; the temporary rebuilt PDF is current engineering verification only.

No persistent system package, language package, font/toolchain or configuration change was made. Temporary Noto Sans fonts and `ragged2e` remain under `/tmp` for inspection and can be cleaned separately.

Codex did NOT modify ChatGPT Project Settings or Project Sources UI. User had already performed the UI update manually. This run produces **UPLOAD BUNDLE READY**, not a new UI upload claim.

After validation, only this run's scoped files are committed and pushed to `origin/main`. The final response records the commit and a fresh remote SHA comparison; the tree cannot contain its own commit hash without self-reference. GitHub review by GPT remains independent of this engineering verification.
