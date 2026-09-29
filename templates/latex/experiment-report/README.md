# Experiment Report LaTeX Template

This directory stores the locked v1 visual reference for the Smart Cities & Location Services Experiment Report.

- `experiment_report_template.tex`: template reference.
- `preview/Experiment_Report_P2_Exact.pdf`: rendered visual reference.
- `demo-assets/`: synthetic figures used only for template preview; never reuse as experimental results.

For a real assignment, copy/adapt the template into that task's report directory. Do not overwrite this locked reference with task content.

Formal experiments, course designs and assigned formal-report tasks use the project's independent Experiment and Process reports, as scoped in the [Report Writing Guide §1](../../../docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md#1-两份报告的读者与任务). The guide owns problem-led argumentation and W01–W22; ordinary questions do not trigger report production.

The user-accepted real-task exemplar is the [25-page Experiment 1 PDF](../../../reports/experiment-report/experiment1-reconstructed/Experiment_Report_吴博闻_10245102410.pdf) and its [source ZIP](../../../reports/experiment-report/experiment1-reconstructed/Experiment_Report_完整重构_源文件.zip), with the current source/build routed through [task reports](../../../task1/reports/README.md). Use it for writing and production reference, not as future data, parameters, conclusions or a page-count quota. Preserve both accepted originals and this synthetic preview separately.

Formal workflow/architecture figures retain editable `.drawio` and SVG/PDF exports under [Visual System §13](../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md#13-native-and-reproducible-production); statistics, GIS and mathematical figures use their appropriate native tools.

The exact palette is defined in `../common/p2_cloud_sorbet_colors.tex` and documented in `../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`.

Compile from this directory with:

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build experiment_report_template.tex
```

The installed template reads the common palette and resolves figures from `demo-assets/`. Use the installed plotting Skill at `../../../tools/skills/publication-plots/SKILL.md`; ZIP files are distribution archives. `preview/` contains the rebuilt template reference, not experimental results.
