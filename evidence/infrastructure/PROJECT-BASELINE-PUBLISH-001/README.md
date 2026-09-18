# Initial public baseline

Historical record: PROJECT-REPOSITORY-FULL-SYNC-001 supersedes the exclusions below. The current repository includes task1, teacher materials, ChatGPT upload copies and earlier infrastructure evidence. The original preparation record is retained below.

This baseline publishes project rules, the installed Design System and reference templates, the publication-plots Skill, canonical distribution ZIPs, and concise infrastructure verification evidence. It contains no task1 materials, real experimental results or real Human–AI interaction evidence.

## Scope and checks

- [Exact publication allowlist](public-baseline-files.txt)
- [Excluded local files and reasons](public-baseline-excluded.txt)
- [Pending task1 file manifest](task1-pending-files.txt)
- [Pre-commit Git state](pre-commit-status.txt)
- [Empty-remote check](remote-before.json)
- [Secret and path scan summary](secret-scan-summary.txt)
- [Historical clean template verification](template-verification.json)
- [Release payload verification](release-verification.json)
- [Staged content review](staged-review.txt)

The template verification records actual earlier clean builds from PROJECT-BASELINE-SYNC-001: both latexmk calls returned 0, all XeLaTeX passes returned 0, and the PDFs had 5 and 10 pages. Their source and Design System archive hashes are checked again before publication. These are historical infrastructure tests, not experiments performed during publication. The sources, assets, palette and Skill contents remain unchanged.

The Skill ZIP was repackaged solely to omit macOS `__MACOSX/` and AppleDouble metadata. All six effective Skill files are byte-identical to the installed Skill. The original distribution archive remains in the local, excluded ChatGPT upload bundle.

## Deferred materials

The provenance and public redistribution scope of task1 cannot be reliably separated file by file. All 106 existing files remain local and unchanged; none are staged. This includes teacher course slides, the original assignment ZIP, raw data, notebooks and historical outputs. Two `XSym` files named `node_modules` are included in this deferral. Their presence does not authorize recreating dependencies or running task1.

The four generated ChatGPT project-source files are also retained locally and excluded because canonical source/distribution paths are already published. Detailed prior infrastructure audits are local-only; this public record omits machine-specific build transcripts and inventories. The exact exclusions are listed above.

AGENTS.md's workspace locator is documentation, not an executable absolute-path dependency. Published templates and Skill configuration use relative paths or documented portable examples. No package installation, algorithm change, report redesign or task1 execution is part of this publication.

This document records publication preparation. The commit SHA and push verification are reported after the commit is created; final project approval belongs to the external reviewer and user.
