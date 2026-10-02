# Independent internal review — SC-LAB1-PROCESS-INTEGRATION-SYNC-001

Reviewer context: `/root/independent_review`, delegated by the main execution thread. This context does not edit production files. Its only writes are review scripts and findings under this directory. This is independent engineering review, not Evidence Master Lock, user understanding approval, teacher submission or the later web GPT review.

## Initial read-only inspection

The first shell command was `ls -la` in the repository. It showed the two supplied Process files, the supplied Experiment source ZIP, historical HANDOFF archives, an existing `.venv`, and the report/template trees. I read the root and supplied release AGENTS rules, the current Process template/components/README, the source manifest, and the `latex-writing` skill. Initial HEAD: `6527945ad8e526fa606b2c09835f2e51291fa4d0`.

Executed `.venv/bin/python evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/independent_review/audit_inputs.py` (exit 0). The script independently transcribes the user's approved hash baseline rather than deriving expectations from the implementation's manifest. See `initial_input_archive_audit.json` for each actual member/hash.

- All 15 approved inputs were located at the user-designated release/root locations with matching SHA256. The initial check enumerates 19 path instances, of which 17 existed and matched; its two false entries are the not-yet-created release copies of the new Process PDF/ZIP, whose root originals do match. This is initial migration state, not an input hash conflict.
- The Process ZIP contains 343 file members and one nested PreTask source ZIP (79 files). The embedded `Process_Report_Revised.pdf` has SHA256 `45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83`, identical to the approved standalone PDF.
- ZIP CRC, duplicate member names, absolute/traversing paths, Windows-style paths, Unix symlink mode, font-file extensions, credential filenames and common real-token/private-key/literal credential patterns were checked without extraction or execution. No candidates were found in the Process ZIP, nested historical ZIP, root Experiment ZIP or the two initially untracked historical HANDOFF ZIPs. This is a scoped content scan, not a claim that pattern matching can prove all possible secrets absent.
- The two initially untracked `SC-LAB1-G1-CLOSURE-002_HANDOFF.zip` and `SC-LAB1-G1-COMPLETE-001_HANDOFF.zip` contain substantive historical review reports, prompts, probes and (for CLOSURE) code snapshots. They warrant preserved historical identity in the engineering mirror; they are not new run evidence or new project-source members.
- Both approved historical PreTask files remain present with their original hashes. The old 12-page current Process and the template preview were separately hashed before their authorized routing/template migration.

## Initial template findings sent to the implementation thread

These findings are against the pre-migration working tree, not a final verdict:

1. `components/interaction_evidence.tex` defines phrase-fill, outline and numbered-circle commands (`IEHighlight`, `IEOutline`, `IEMarker`), and the live template calls them. This would reproduce an annotation mode explicitly superseded by the supplied v2.6/v2.7 rules. The current live fixture and defaults require an arrow-only migration while retaining historical records.
2. The Micro Trace fixture uses 110 mm image width plus 40 mm notes and an additional gap; the multi-page fixture uses `.68` / `.28` widths. The screenshot allocation and brief commentary must follow the new screenshot-dominant default without fabricating a ChatGPT UI or modifying real accepted evidence.
3. The README still recommends translucent highlights, BOX RANGE as a current gate and the older Visual/Evidence/Writing version labels. The current component documentation and preview need to reflect the new defaults. Normal technical diagram borders remain allowed.
4. The template and README already label fixtures SYNTHETIC / TEMPLATE ONLY. This identity must remain explicit through preview regeneration.

No production changes were made by this reviewer. Build integration, final source sync safety checks, final protection comparison, full-image visual inspection and final independent verdict remain pending at this initial checkpoint.

## Independent regression and intermediate visual findings

Executed the implemented sync regression suite independently with `.venv/bin/python -m pytest -vv -p no:cacheprovider evidence/infrastructure/chatgpt-project-source-sync/test_sync_sources.py --junitxml=evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/independent_review/sync_pytest.xml`; exit 0, **37 passed**. See `sync_pytest.txt` and XML. I read the test definitions as well as running them. Coverage includes changing declared membership, same-count/wrong-name membership, independently sourced Skill copies, unsafe inputs, actual `--plan`/`--check` subprocess invariance, and failure injection restoring both existing files and transaction-created files. Real final release checks are separate and pending.

`pdfinfo` independently reported 77 A4 pages for the approved root PDF. `pdftotext -f 1 -l 1` confirmed both opening purposes and the original ShareX/image-splitter acquisition sentence. A first read-only metadata probe importing `fitz` failed with `ModuleNotFoundError`; I installed nothing and used existing Poppler for that metadata/text read. The build role handles the authorized isolated report dependencies. The portable source palette maps exactly to the public P2 values (Blue=C1, Orange=C2, Rose=C3, Violet=C4; Paper/Ink/Muted/Rule unchanged).

I actually opened the first regenerated synthetic template's 200-dpi PNGs for physical pages **4, 5, 6, 7, 8** using `view_image(detail="original")`. Page 5's new arrow-only plain text fixture was readable with no highlighted phrase rectangles. Pages 6–8 still embedded the old `interaction_part1/2/3.png` raster fixtures containing colored highlights over chat-like placeholder rows, despite the surrounding new arrow-only instruction; page 7 was also crowded near the bottom. This was sent to the implementation thread as an unresolved current-preview defect. The designated template implementation role is replacing those active fixtures with clearly synthetic, non-ChatGPT-UI layout specimens, preserving the old assets historically. The README's unqualified legacy "translucent highlights" wording was separately reported. The initial preview is not approved by this review; final replacement preview inspection is still required.

The Process build role identified actual font-weight/environment differences in its first successful PDFs and is repairing the isolated environment. I have deliberately not recorded those first render pages as final Process visual approval; final images/hash remain pending.

## Final independent result

The later final check resolved the preceding intermediate pending state. The reviewer wrote [the final independent review](../INTERNAL_REVIEW.md) after independently running the final 19 report tests and 37 sync tests, verifying the real `--plan` / `--check` mtime invariance, checking all approved source/release/index hashes and 6071 protected initial files, independently rerendering/comparing all 77 Process pages, actually viewing pages40–77 plus1/9/34, and rechecking the corrected synthetic template. The six tiny vector-page differences have maximum channel error1/255; all text, dimensions and embedded screenshots match. Final adapter PDF and all77 page PNGs were independently byte-matched to the inspected B output. The root review states the exact artifact hashes, findings, repairs and scope limits; remote publication remains the parent thread's separately recorded step.

Initial `sync_pytest.log` and `report_integration_pytest.log` were renamed to `.txt` without changing their bytes so the repository's log ignore rule does not omit the actual independent test output. Final suite evidence is `final_report_pytest.txt` / XML. The earlier7 report tests are a subset of the final19, not an additional independent test count. This review context installed no dependencies and changed no production files.
