# CODEX-INFRA-REPAIR-001 evidence

These files document infrastructure repair and template smoke tests only. Template diagrams, screenshots and numeric examples are not real experimental results or Interaction Evidence.

- [Repair summary](repair-summary.md)
- [Warning causes and resolution](warning-summary.md)
- [Exact source diff](repair.diff)
- [Complete file change inventory](files-changed.json)
- [Pre-repair file hashes](pre-repair-files.json)
- [Task1 before hashes](task1-before.sha256.json), [after hashes](task1-after.sha256.json), [integrity result](task1-integrity.json)
- [Installed source/Skill/ignore verification](installed-verification.json)
- [Cleanup item list](cleanup-summary.json), [hygiene verification](hygiene-verification.json)
- [ZIP/PDF archive relocation](archive-relocation.json), [preview refresh](preview-refresh.json)
- [Read-only remote check](git-remote-check.json), [Git initialization](git-working-tree.json), [final Git state](git-final-state.json)
- [Clean smoke-test results](smoke-results.json), [tool versions](tool-versions.json)
- Experiment: [montage](experiment/montage.jpg), [build console](experiment/build-console.txt), [LaTeX log](experiment/latex-log.txt), [PDF metadata](experiment/pdfinfo.txt), [extracted text](experiment/pdf-text.txt)
- Process: [montage](process/montage.jpg), [build console](process/build-console.txt), [LaTeX log](process/latex-log.txt), [PDF metadata](process/pdfinfo.txt), [extracted text](process/pdf-text.txt)
- [Visual comparison](visual-comparison.json), [page inspection record](visual-inspection.json)
- [Original warning reproduction](reproduction/), [intermediate diagnostic attempt](attempts/01-font-initialization/)
- [Final infrastructure state](final-state.json)

During PROJECT-BASELINE-SYNC-001, obsolete `baseline/` source/PDF copies, duplicate compiled PDFs, input-recorder copies and per-page PNG caches were removed. Their historical hashes, repair diff, compilation logs and montage evidence remain. See the [cleanup ledger](../PROJECT-BASELINE-SYNC-001/cleanup.json). Historical reports and JSON paths describe the state at that earlier audit, not the current file inventory.

Runtime templates remain under `templates/latex/`. Current release and upload verification is indexed in [PROJECT-BASELINE-SYNC-001](../PROJECT-BASELINE-SYNC-001/README.md).

`build_and_render.py` records the compile/render workflow and captures actual XeLaTeX return codes. It refuses to mix new output with existing final evidence. It does not execute task1. Every clean build uses a new temporary directory.
