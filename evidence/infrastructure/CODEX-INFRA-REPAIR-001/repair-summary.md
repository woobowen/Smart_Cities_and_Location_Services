# CODEX-INFRA-REPAIR-001 repair summary

Scope: infrastructure repair only. No task1 code, notebook, algorithm, trajectory processing, parameter scan, LLM experiment or formal report content was executed or produced. All PDFs/images here are template smoke-test evidence.

## Baseline and integrity

- Initial directory was not a Git working tree; `git status` returned 128.
- Baseline recorded 282 files and 106 substantive task1 files.
- Substantive task1 files remain 106, with identical per-file SHA-256 values.
- The before/after task1 manifest SHA-256 is `ea08c718e99bf196e0d5b42579dfb8a26aca790ecdd47ad69408e12f57f4825d`.
- AGENTS.md was read in full and remains byte-identical. Its existing long-term paths are valid, so no rule changes were made.

## Source repairs

- Experiment uses `\graphicspath{{demo-assets/}}` and filename-only figure references; no asset duplication.
- Experiment's 13 inline P2 definitions were replaced by `\input{../common/p2_cloud_sorbet_colors.tex}`. Process already used this input.
- The common palette is unchanged: SHA-256 `2aa820c3f68ba6c14cf1b52082b12336071d77bb5466db2b05b2fab6890aa243`.
- Both covers use local `\noindent` for their full-width rule and generate no page anchor on the unnumbered cover.
- Explicit font initialization eliminates redundant ctex/xeCJK definitions without changing rendered typography.
- Visual System line 97 now points to the installed Skill and identifies the ZIP as a distribution archive. No frozen visual or research rule changed.
- Both template READMEs document installed dependencies and the compile command. `docs/design-system/README.md` records runtime paths and LEGACY/archive status.
- The current previews were refreshed from this run's PDFs. Original installed previews and the extra duplicate Process PDF were preserved under `baseline/`; the redundant root Process PDF was moved there, not destroyed.

## Final verification

The script `build_and_render.py` copied installed common/Experiment/Process directories into a newly created temporary tree, excluded old caches, and ran from each template's own directory:

```text
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build experiment_report_template.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build process_report_template.tex
```

The script captures each actual XeLaTeX subprocess return code. Experiment: latexmk 0, XeLaTeX [0, 0], 5 pages. Process: latexmk 0, XeLaTeX [0, 0], 10 pages. Both PDFs passed pdfinfo, pdftotext and all-page pdftoppm rendering. All 15 rendered pages were individually inspected. Each report has `pages/` and `montage.jpg` for external review.

The first repaired Experiment attempt exposed pre-existing font redefinition warnings and is retained. The final run resolved them. An ignore-rule check also caught the shallow `*/build/` glob; it was corrected to `**/build/`, and all 14 cache/deliverable-path checks succeeded. No failed attempt was presented as the final result.

## Cleanup and archives

- Deleted 130 allowed junk files: 122 Zone.Identifier files (including two inside cache directories), two AppleDouble files, two other cache payloads, and four LaTeX cache files.
- Removed two emptied cache directories: task1 `.mplcache/` and `.ipynb_checkpoints/`.
- Of those 130 files, 112 were task1 junk; no substantive task1 file was removed.
- Renamed `smart_cities_design_system_v2 .zip` to `smart_cities_design_system_v2.zip` without changing SHA-256: `e66f70dccc6b8e98782fd442cbd74473fbb61b1459ebb242c9a816181401d39b`.
- Retained v1 ZIP and extracted directory as LEGACY; retained all original distribution ZIPs. Archives remain historical and do not contain this repair. Installed sources are the runtime authority.
- `.gitignore` excludes explicit distribution paths and technical caches, not arbitrary ZIPs, source, notebooks, figures or report PDFs. Evidence build logs are preserved as `.txt` so they remain reviewable.

## Git

Read-only `git ls-remote https://github.com/woobowen/Smart_Cities_and_Location_Services.git` returned 0 with empty stdout/stderr. No refs were advertised. The authorized empty-remote route was used: `git init -b main`, then origin was configured to that URL.

Final state: main, zero commits, empty staging index, no commit/push/PR. `git diff --check` is empty because files are untracked; it is not a substitute for the preserved `repair.diff` and file manifests.

## Environment and limits

No packages, fonts or toolchains were installed, and no shell/global environment configuration changed. New repository-local configuration consists of `.gitignore` and `.git/` metadata. Temporary clean-build directories remain under `/tmp/codex-infra-repair-001-*`; persistent evidence is in this directory.

Task1's earlier provenance remains unverified; existing substantive materials were preserved and not treated as this run's results. No infrastructure blocker remains. External GPT/user review is pending; this document does not declare final project approval.
