# PROJECT-BASELINE-SYNC-001 evidence

Scope: directory cleanup, Design System technical-release sync, and a proposed first Git baseline. No task1 code/notebook/algorithm was modified or executed. No git add, commit or push was performed.

## Release verification

The v2.1 ZIP contains 24 byte-identical installed specification/template/asset/preview files plus MANIFEST.md. Both templates were compiled from a fresh extraction of that ZIP, not from the installed tree and not using old build caches. Experiment: 5 pages; Process: 10 pages. Both latexmk returns and all four actual XeLaTeX returns were zero; final logs have no missing input files, undefined references, overfull or duplicate page warnings.

- [Release manifest and SHA-256](release.json)
- [Package payload hashes](package-files.sha256.json)
- [Clean smoke results](smoke-results.json)
- [Experiment console](experiment/build-console.txt), [final LaTeX log](experiment/latex-log.txt), [PDF metadata](experiment/pdfinfo.txt)
- [Process console](process/build-console.txt), [final LaTeX log](process/latex-log.txt), [PDF metadata](process/pdfinfo.txt)
- [ChatGPT source file hashes](chatgpt-sources.sha256.json)
- [Skill archive/installed equality](skill-verification.json)

`release_and_verify.py` records the packaging and clean verification procedure. It refuses to overwrite an existing release. Installed template/specification/asset bytes were not changed during this sync. The original Skill ZIP was moved intact to releases/skills; its four-file upload copy is intentional. Metadata inside the original ZIP was preserved rather than silently altering that distribution.

## Cleanup

47 obsolete/archive/duplicate/cache files were deleted, totaling 20,324,515 bytes. This includes the v1 ZIP and extracted tree, the pre-repair v2 ZIP, historical source/PDF snapshots, duplicate build PDFs and per-page render caches from the earlier repair evidence. Historical logs, hashes, diffs and two montage images remain; they provide the repair record without keeping alternate runtime sources. The root Skill ZIP was moved, not discarded.

- [Per-file cleanup ledger](cleanup.json)
- [Pre-sync file hashes](pre-sync-files.json)
- [Final two-level tree](repository-tree.txt)
- [Final checks](final-verification.json)

## Protected task1 materials

All 106 substantive task1 files are byte-identical before/after and match the preceding repair baseline. Teacher materials, notebooks, historical result files and data remain in place, including the two identical traj_dict.json files. Their duplicate storage is not a reason to remove a path that existing starter code may depend on.

- [Before hashes](task1-before.sha256.json)
- [After hashes](task1-after.sha256.json)
- [Integrity result](task1-integrity.json)

Two existing regular files named `node_modules`, under `task1/作业/作业/build_ppt/` and `build_ppt_agent/`, have an `XSym` header and are not actual dependency directories. Their intended use is unverified. They remain untouched and are excluded from the baseline recommendation pending human review. No attempt was made to restore dependencies or run their associated code.

## Baseline recommendation

- [Candidate file list](baseline-candidate-files.txt)
- [Excluded file list and reasons](baseline-excluded-files.txt)
- [Counts and scope](baseline-summary.json)
- [Initial Git state](git-before.json)
- [Final Git state](git-final.json)

The candidate list is a recommendation for future tracking, not the current index: the repository still has zero tracked files and zero commits. It includes long-term rules, installed sources, the canonical v2.1 and Skill distribution ZIPs, 104 of 106 protected task1 files, and the retained infrastructure evidence. All retained evidence is included so its audit index remains reviewable after a future checkout.

Excluded current working-tree files are exactly the four generated ChatGPT upload copies and the two unresolved XSym entries. Git-internal metadata is outside the candidate/excluded working-file universe; deleted files are separately listed in cleanup.json. The four upload files remain available locally, and canonical source/distribution paths remain in the candidate list. Cache rules continue to apply through .gitignore.

No dependencies were installed. The only current non-evidence text updates were the obsolete ignore entries and the Design System installation/release README. AGENTS.md, the Visual System specification, P2, all template sources/assets and the Skill were unchanged.
