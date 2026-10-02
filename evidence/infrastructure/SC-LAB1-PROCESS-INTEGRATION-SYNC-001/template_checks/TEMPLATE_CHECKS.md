# Process template integration checks

Role: delegated `source_sync` context, template implementer and author self-check. Independent internal review belongs to a different context. These are checks of a synthetic reusable template, not a review of real interaction evidence and not Evidence Lock.

The parent thread made the initial arrow-only API, width and documentation updates and ran the initial isolated build. That run is preserved in `build.json` / `compile-output.txt`. The follow-up review used the active Report Writing Guide v1.2, Visual System v2.6 (Process/interaction/layout/reference sections), Evidence Protocol v2.7 (screenshot, arrow and render-audit sections), shared P2 source, template README and the `latex-writing` skill.

## Findings and repairs

The initial 12-page build completed, but actual page inspection found colored highlights baked into all three old `interaction_part*.png` assets on physical pages 6–8. Removing overlay macros alone did not fix those defaults. The current template now uses `demo-assets/multipage_specimens.tex`: plain LaTeX placement instructions explicitly marked **SYNTHETIC / NOT CHAT UI**, without message bubbles, screenshot boxes or highlighted text. The old PNGs remain byte-identical historical assets and are absent from the current source and actual final `.fls` input list. [Before page 6](before-page-06.png) and [after page 6](after-page-06.png) retain the actual rendered difference.

The first structure diagram had adjacent nodes colliding; bounded text widths and explicit breaks fixed that layout without changing its relationships. The final usage section now begins with its content on a fresh page, avoiding the previous split introduction. The narrow aside uses ragged-right text, removing its underfull warning. The README limits highlights to separate technical diagrams/page elements and distinguishes the preserved history from the active preview.

The immutable previous preview remains at `templates/latex/process-report/preview/history/Process_Report_P2_Locked_v1_20260929.pdf`, SHA256 `3903042ef7935a722d32871a9f55ba973b1262ee0fe290363b0a6c3bda09dcfa`. The sole current preview is `templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf`, **12 pages**, SHA256 `b53d70a8945f10d5911a1f2ea43278172d1df9987f504a97d2b4b392c3688fc0`. The preview remains synthetic and is not an upload member for this task.

## Actual validation

The declared XeLaTeX/latexmk command ran in the isolated template copy with exit code 0. Exact invocations and times are in `repaired-build.json` and `final-build.json`; the final TeX transcript is `final-template-log.txt`. The final log contains no fatal errors, undefined references, font substitution/missing characters, overfull or underfull boxes. `api_probe.tex` was actually compiled with XeLaTeX: `IEHighlight`, `IEOutline`, and `IEMarker` are absent, and the supported arrow/anchor/note APIs exist. Its command and exit 0 are in `final-build.json` and output in `api-compile-output.txt`.

Poppler rendered the final PDF at **200 dpi**, 1654 × 2339 pixels per A4 page. All 12 repaired pages were individually displayed and inspected, not merely combined into a contact sheet. The last change only adjusted page 3 line breaks; all other final page PNGs were byte-identical to those already inspected, and final page 3 was displayed again. `final-render.json` preserves this page-by-page comparison and image hashes.

| Physical page | Actual visual check |
|---|---|
| 1 | Cover hierarchy, synthetic disclaimer and table readable; no clipping. |
| 2 | Contents readable; final usage section points to printed page 11. |
| 3 | Heading with its body/diagram; neighboring text nodes separated; final line breaks rechecked. |
| 4 | Contact-sheet placeholders retain explicit synthetic caption; image and page elements readable. |
| 5 | Direct 130 mm PNG with 34 mm aside; two vector arrows terminate in whitespace next to the intended example phrases; no text occlusion or former boxes/fills. |
| 6 | New neutral native specimen and short side notes; heading and first content together; 0.76/0.20 allocation retained. |
| 7 | Continuation identified; neutral specimen and caption readable; no baked highlights or recreated chat UI. |
| 8 | Closing continuation and real-confirmation placement instruction readable; no clipping. |
| 9 | Existing Human Reasoning synthetic technical diagram and caption readable; legitimate technical node borders retained. |
| 10 | Existing candidate-tree synthetic technical diagram and caption readable. |
| 11 | Existing editorial-board synthetic technical diagram with explanatory content; no isolated following heading. |
| 12 | Usage heading and full section together; readable text without overflow. |

[The inspected arrow-only page](arrow-only-page-05.png) is preserved. The original specimen is 1300 × 1182 pixels; at 130 mm width its effective PPI is 254 (also confirmed by the embedded-image inspection in `pdfimages.txt`). The 200-dpi review render is not claimed to increase source resolution. The multi-page native specimens are placement demonstrations, so they are not described as real user UI, original screenshots or approved Evidence.

`verification.json` binds source/preview hashes, actual inspection scope, preservation of the common P2 palette and three historical demo PNGs, and the input-list check. No dependencies were installed by this context. Actual reports, accepted PDF/ZIP pairs, scientific code/data/results and public color definitions were not edited by this template task.
