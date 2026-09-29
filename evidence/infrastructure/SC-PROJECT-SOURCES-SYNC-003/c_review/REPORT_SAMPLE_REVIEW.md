# Independent C report build and visual sample

C independently extracted the immutable received Experiment archive into `c_review/build/clean_archive_source`, deliberately excluding `Experiment_Report.pdf`. The unchanged archive `build.sh` then ran two actual XeLaTeX passes with exit 0. C installed nothing; the process used the existing TeX Live 2026 plus B's recorded project-isolated `.venv/texmf` packages.

The output has 25 pages and the expected 吴博闻 / 10245102410 identity. Complete `pdftotext -layout` output is exactly equal to the approved PDF's extracted text. Rebuilt PDF SHA256 is `1a9d19adb725cd7ddd8cf2557b0a8f37404fe70ee1f36aa853c4b35e3c4b8ad4`, different from the approved original `2a940be5…`; this is not a byte-identical PDF claim. The scan's sole `Rerun` match is the package banner `Package: rerunfilecheck … Rerun checks for auxiliary files`, not a pending-rerun warning. The complete log has no fatal, missing-glyph, undefined-reference/citation, font-substitution or overfull-box diagnostic.

Evidence: [build result](independent-build-result.json), [console](independent-build-console.txt), [LaTeX log](independent-build-latex-log.txt), [extracted text](independent-rebuilt-text.txt), [PDF info](independent-rebuilt-pdfinfo.txt), [render commands/hashes](sample-render-receipt.json). The clean source and full rebuilt PDF are temporary build products under ignored `build/`; the original received/canonical PDF and ZIP were not overwritten.

C rendered and actually opened each of the following approved/rebuilt page pairs at 200 dpi, using `view_image` with original-detail request. Files are 1654 × 2339 pixels; the tool display resized them to 1334 × 1888, still displaying full readable pages rather than contact-sheet thumbnails. Hash comparisons were supporting evidence only; both sides of every listed pair were visually inspected.

| Physical page | Content actually inspected | Observation |
|---|---|---|
| 1 | Cover title, identity, date, palette strip and spacing | Same visible identity and layout; no lost glyphs or clipping. |
| 6 | DP finite-segment formula, coverage definition, metric table, max-error inequality | Formula symbols, table cells, bold limitations and page layout match; no newly missing or overflowing content. |
| 9 | 3D filter-response grid, axis labels/legend, caption and interpretation | Grid geometry, markers, labels and paragraph positions match; no new visual change. |
| 14 | Memory-consumption table and record 7764 discussion | Denominators, case values, prose, emphasis and breaks match. |
| 19 | Selection comparison table and three-record error-increase bar plot | Row values, bar labels, legend/axis/caption placement and conclusions match. |
| 25 | ECEF/ENU equations, coordinate caveats and reproduction appendix | Mathematical glyphs and units visible; paragraph breaks and placement match. |

This is an independent clean archive build plus six-page visual sample. It does not replace B's required 25-page visual pass, prove all figure redraws, rerun the numerical experiment, authenticate Process evidence or grant Evidence Lock. Final integrated generator and package checks are recorded separately when ready.
