# Experiment Report LaTeX Template

This directory stores the locked v1 visual reference for the Smart Cities & Location Services Experiment Report.

- `experiment_report_template.tex`: template reference.
- `preview/Experiment_Report_P2_Exact.pdf`: rendered visual reference.
- `demo-assets/`: synthetic figures used only for template preview; never reuse as experimental results.

For a real assignment, copy/adapt the template into that task's report directory. Do not overwrite this locked reference with task content.

The exact palette is defined in `../common/p2_cloud_sorbet_colors.tex` and documented in `../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`.

Compile from this directory with:

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build experiment_report_template.tex
```

The installed template reads the common palette and resolves figures from `demo-assets/`. Use the installed plotting Skill at `../../../tools/skills/publication-plots/SKILL.md`; ZIP files are distribution archives. `preview/` contains the rebuilt template reference, not experimental results.
