# Template warning verification

## Reproduced baseline

`reproduction/process-console.txt` and `reproduction/process-latex-log.txt` preserve this run's clean reproduction of the original Process template:

- `Overfull \hbox (21.9pt too wide)` at original source lines 48–56.
- `xdvipdfmx:warning: Object @page.1 already defined.`

The full-width cover rule started a paragraph with `\parindent=2em` (21.9 pt), so its total occupied width exceeded `\linewidth`. A local `\noindent` removes the unwanted indentation. The same cause existed in the Experiment cover. No global `\sloppy`, tolerance adjustment or warning suppression was used.

The unnumbered title page and the following contents page both had counter value 1. Hyperref therefore created the same page destination twice. Page anchors are disabled only while shipping the unnumbered cover, then restored before the contents page. Body numbering and contents links remain intact; this removes the duplicate destination rather than filtering its warning.

## Additional warning found during validation

The first repaired Experiment build succeeded but the strict audit stopped on two xeCJK font-family redefinition warnings. ctex first initialized Fandol main/sans families, which the template immediately replaced with its explicitly selected Noto families. Evidence is retained in `attempts/01-font-initialization/experiment/`.

Both templates now use `fontset=none` and explicitly retain Noto Serif CJK SC, Noto Sans CJK SC, and the previous FandolFang-Regular CJK monospace family. DejaVu Latin fonts are unchanged. This changes initialization, not the selected fonts. The five Experiment pages before/after this font repair are pixel-identical at 110 DPI.

## Final clean builds

Both final builds have latexmk return 0 and two captured XeLaTeX returns of 0. Final-pass logs contain no missing input files, undefined references/citations, missing glyph diagnostics, overfull/underfull boxes, font redefinition warnings or fatal errors. Neither complete final build console contains a duplicate page/object warning.

Initial-pass `.toc` absence and reference rerun messages are normal bootstrap events in an empty build directory; latexmk resolves them during the second pass. They are not unresolved final diagnostics.

All 15 pages were rendered and individually inspected without visible page overflow. Process pages 2–10 are pixel-identical to the locally compiled pre-repair template; the only raster difference on its cover is the corrected horizontal rule. See `visual-comparison.json` and `visual-inspection.json`.
