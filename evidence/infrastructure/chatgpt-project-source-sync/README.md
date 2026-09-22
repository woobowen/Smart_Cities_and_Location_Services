# ChatGPT Project Sources Upload-Ready Bundle

Run: SMART-CITIES-CHATGPT-PROJECT-SOURCES-UPLOAD-BUNDLE-002.

The [upload directory](../../../releases/chatgpt-project-sources/) contains exactly eleven ordinary files. Every file is intended for upload, including AGENTS. The user can select all files; internal metadata is stored here instead. This is repository preparation only, not an assertion that ChatGPT UI files have been uploaded.

- [Upload Bundle Manifest](SOURCE_MANIFEST.md): eleven PROJECT_SOURCE rows, canonical filenames, active paths, bundle paths, hashes, byte equality and verification date. Previous display names are historical mapping only.
- [Upload instructions](UPLOAD_INSTRUCTIONS.md): user refresh procedure and exact upload list.
- [Existing sync tool](../SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py): upgraded in place; no second sync implementation.
- [Existing validation tool](../SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py): current bundle checks, without rebuilding PDFs or altering historical run 001 results.

## Operation

Update the active repo sources first, then run from repository root:

```bash
python3 evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py
python3 evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
python3 evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py
find releases/chatgpt-project-sources -maxdepth 1 -type f -printf '%f\n' | sort
test "$(find releases/chatgpt-project-sources -maxdepth 1 -type f | wc -l)" -eq 11
sha256sum releases/chatgpt-project-sources/*
git diff --check
```

Before commit, stage the intended files and use `validate_sync.py --index` to compare staged source and bundle bytes as well. All tool output/metadata remains outside the upload directory.

The sync tool validates every source and the approved original Skill archive before copying or cleaning. It copies bytes, deletes only direct ordinary files outside the exact allowlist, and writes the internal manifest. It does not modify active sources. Unexpected subdirectories/symlinks cause a failure before mutation; it does not recursively delete them. The original Skill ZIP must already exist and match the approved hash and installed effective members; it is never regenerated or silently replaced by the metadata-sanitized archive.

## This migration

Pre-flight: main, clean tree, local/remote baseline `eb9daccfd149ed00dfc2d83d41a5f4845aada54f`. Initial upload directory had twelve files: the approved eleven plus an internal manifest. That manifest was moved here and rewritten for upload-bundle semantics. No other real upload file needed removal. AGENTS and the design-system README were updated, then AGENTS was copied from its active source. Research/Evidence/Visual protocol content, P2, templates, canonical previews, teacher materials, notebooks, task1 code and installed Skill content are protected by baseline hash comparisons.

No active-like duplicate Markdown documents were found outside the canonical source plus allowed distribution copy. Old ignored Zone.Identifier sidecars outside the upload directory are download metadata, not active Markdown versions; they are not uploaded. Historical archive ZIPs remain intact.

Historical run 001 JSON/TXT records preserve the filenames, roles and hashes measured then. Those historical references are not current manifest links and are not rewritten to fabricate a different past result. Its README now routes current operations here. Earlier release-packaging scripts remain historical, not supported upload-sync entrypoints. Git retains prior versions; no parallel active governance files or versioned bundle directories are introduced.

## Verification records

- `preflight.json`: initial directory/hash inventory and protected original-file hashes.
- `sync-result.json`: actual sync output and final eleven hashes.
- `validation.json`: exact set, ordinary files, source bytes, internal manifest, known Skill hash/effective members, protected-file integrity, versions, duplicate detection, links, syntax and Git checks.
- `directory-listing.txt`, `bundle-sha256.txt`: actual find/sha256sum output.
- `publication-check.json`: credential-pattern, file-size and publication-scope review.

The validator exercises cleanup of extra ordinary metadata/suffix files, idempotency, stale-copy repair, and rejection of missing sources, wrong Skill hash, unexpected directories and symlinks in a temporary fixture. It verifies no mutation on those failures and no change to fixture active sources. It never executes notebooks or task1 code.

The publication scan covered the upload files and effective archive content. Two literal-credential candidates in the original assignment archive were reviewed as explicit Chinese placeholders, not real credentials; no high-confidence credential pattern matched. Original archives were not edited.

PPI and report visuals are unaffected because all template, palette and canonical preview bytes are unchanged. No LaTeX rebuild is required or performed. PDFs remain synthetic reference previews; supplied teacher/starter outputs remain historical/pre-generated. No current-run sample/full experiments or formal figures are created.

New system/language packages, fonts/toolchains and environment configuration changes: none. No Project Settings file is created; the UI is not accessed. After commit/push, the resulting SHA and fresh remote comparison are reported to the user. Stop and wait for GPT's independent remote audit; do not start Experiment 1.
