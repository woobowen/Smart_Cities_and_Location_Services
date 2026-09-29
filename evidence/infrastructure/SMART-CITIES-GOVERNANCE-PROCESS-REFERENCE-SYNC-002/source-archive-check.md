# Source archive verification

SOURCE_ARCHIVE_BUILD: **PARTIAL**

The unchanged, user-approved ZIP is valid and the README build really produces 31 pages. It does not fully reproduce the accepted `REVISED.pdf` prose and annotation geometry. Prompt section 8 explicitly permits synchronization to continue when the archive is valid and the approved PDF exists; this result does not authorize rewriting either input.

## Archive and safety checks

- CRC test: PASS; 104 entries, including 13 `.tex` files (12 blocks plus a shared preamble) and 63 PNG Evidence assets.
- README and `build_31p.sh` provide the entry point: `latexmk -xelatex` for blocks 01–12, then `pdfunite`.
- No unsafe paths, duplicate members, symlinks, obvious cache/build junk or high-confidence credential-pattern matches were found in the scanned textual members. TeX sources contain no external-command invocation.
- The archive intentionally includes `WF_WorkflowConstruction_PreTask1_31p_compiled.pdf`; this is a reference artifact, not an auxiliary cache. It was moved outside the extracted source before the clean build. The original ZIP was never edited or repacked.
- Member paths, sizes and SHA256 values are in [the inventory](source-archive-inventory.json). Screenshots remain supplied evidence, not newly authenticated interaction records; this check does not confer Evidence Lock.

## Actual build

The ZIP was extracted under the unique `/tmp` workspace recorded in [preflight.json](preflight.json). The README entry point was executed as `bash build_31p.sh`; no `.tex`, screenshot or build-script content was changed.

1. Initial attempt: exit 12; `Noto Sans` was unavailable.
2. After making four Noto Sans fonts available through a process-local Fontconfig file: exit 12; `ragged2e.sty` was unavailable.
3. After installing `ragged2e` into a temporary TeX user tree and supplying process-local `TEXINPUTS`: exit 0; 31 pages.

Font files came from Ubuntu `fonts-noto-core` 20201225-2, downloaded and extracted only under `/tmp`. `ragged2e` 3.6 came from the verified TeX Live 2026 repository and was installed only into the temporary tree. The persistent TeX Live installation, system packages, Python environment and shell configuration were not changed. Exact commands, file hashes and environment overrides are in [environment-changes.json](environment-changes.json) and [source-build-result.json](source-build-result.json).

Final logs: 0 fatal errors, 0 missing assets, 0 undefined references, 0 font-substitution warnings, 0 pending reruns; 9 missing `→` glyph occurrences; 3 overfull boxes with maximum 1.44914 pt. None exceeds the reported 5 pt inspection threshold. The 9 missing glyphs are visible in the rebuilt page 28; this is a known quality limitation, not a clean-build PASS. Full logs are preserved in [source-build-latex-log.txt](source-build-latex-log.txt); the two failed attempts have separate logs.

## Comparison with the approved PDF

`pdfinfo` reports 31 pages for the approved PDF, the archive's embedded PDF and the freshly rebuilt PDF. Every approved and rebuilt page has nonempty extracted text. Whitespace-normalized text differs between the approved and rebuilt PDF on all 31 pages; these are content differences, not just PDF metadata hashes.

Representative visual comparison at 200 dpi:

- Page 1: title and introduction are present; substantial whitespace is retained, with the first Evidence group on page 2. This continuation is documented in the supplied README.
- Page 16: source output uses broader blue/violet boxes and older narrative wording; the approved PDF uses narrower boxes and revised first-person prose.
- Page 31: source output retains the older “Process Report生产系统完成冻结” title, while the approved PDF says “我把Process Report的基本做法先定下来”.
- Approved pages 1, 2, 16 and 31 and rebuilt pages 1, 16, 28 and 31 were rendered and inspected. Representative pages are structurally readable; the rebuilt glyph defect remains explicitly recorded.

The archive supports the 31-page Workflow Construction structure and assets, but full reproduction of the accepted revision remains unverified because the supplied source content differs. The approved PDF is the accepted reading reference. The archive is preserved as the user-approved source archive with this limitation; replacing or editing it would require a separate approved task.

Detailed machine checks: [source-reference-validation.json](source-reference-validation.json). Render evidence: [render/](render/). Neither the approved PDF nor either template preview was regenerated or overwritten.
