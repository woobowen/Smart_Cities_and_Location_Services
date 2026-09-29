# Protection scan: navigation changes reviewed

The first final scan flagged three additional changed paths because its original exact allowlist omitted them: `task1/docs/goal3/DEFENSE_NOTES.md`, `task1/docs/goal3/TECHNICAL_HANDOFF.md`, `task1/goal3/PACKAGE_README.md`.

Root inspected the actual Git diff. Changes only correct REPORT_BUILD behavior, point to the new named 25-page REVIEW_ONLY package, distinguish historical 22/34-page checks, and preserve Process/Submission boundaries. No research values or runtime numerical code changed. These are current reader/package navigation adaptations explicitly authorized by Prompt §11. The exact allowlist is extended only for these paths; no broad task1 exclusion is introduced. The original flagged scan is retained in `protection-navigation-review.json`, then the full scan is rerun.
