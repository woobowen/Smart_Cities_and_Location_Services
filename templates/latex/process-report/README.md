# Process Report template

This template is locked to the Smart Cities Visual Design System v2.

Use it for the formal Human-AI / research-process report.

Key rules:
- replace every demo screenshot and demo diagram with real project evidence;
- preserve raw screenshots separately and annotate a copy for the report;
- core interactions may span any number of pages needed for readability;
- general interactions may be summarized in contact sheets;
- brainstorm content in this report shows real method/metric/parameter reasoning evolution, not project-management setup;
- use the locked Editorial Decision Board, Human Reasoning -> Evidence -> Decision, and Horizontal Candidate Decision Tree grammars;
- do not invent user participation, chat UI, experiment outcomes or AI criticism.

`demo-assets/` are template-only assets and are not experimental evidence.

The exact palette is read from `../common/p2_cloud_sorbet_colors.tex`. The installed specification is `../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`, and the plotting Skill is `../../../tools/skills/publication-plots/SKILL.md`.

Compile from this directory with:

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build process_report_template.tex
```

`preview/Process_Report_P2_Locked_v1.pdf` is the rebuilt template reference, not interaction evidence. Use installed sources for normal work; ZIP files are distribution archives.
