# Revision notes

This package contains the revised 31-page pre-Task-1 Workflow Construction report source.

## Language
- The narrative is written from my first-person perspective (`我`) instead of third-party labels such as “用户”.
- Main prose uses a natural research-reflection style.
- Key Human Judgments retain a slightly more conversational tone close to the original wording.
- Technical names such as CANDIDATE / UNRESOLVED / Source Audit remain concise definitions rather than being rewritten as casual prose.

## Interaction Evidence
- Every colored annotation box used in the current report was re-audited against the original screenshot content.
- Broad section boxes were narrowed where the arrow actually refers to a specific phrase or subsection.
- Arrow endpoints were checked against the highlighted phrase/section rather than simple message adjacency.
- Original screenshots were not rewritten or regenerated; the colored boxes/arrows are LaTeX/TikZ overlays.

## Build

```bash
./build_31p.sh
```

Expected result:
`build/WF_WorkflowConstruction_PreTask1_31p.pdf` (31 A4 pages)
