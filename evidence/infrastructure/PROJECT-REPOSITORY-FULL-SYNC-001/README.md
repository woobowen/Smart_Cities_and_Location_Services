# Complete project mirror

PROJECT-REPOSITORY-FULL-SYNC-001 explicitly authorizes GitHub to mirror all substantive project files. This supersedes the selective scope of the initial public baseline. Teacher submission packages will be prepared separately.

The mirror includes project rules, all docs, templates, installed Skills, release archives, the four ChatGPT upload files, all infrastructure evidence, and all 106 existing task1 files. Teacher slides, assignment ZIP, notebooks, data, auxiliary files and historical outputs are preserved byte for byte. Existing task1 results are historical supplied artifacts, not experiments performed or validated during this synchronization.

The two XSym files are regular ASCII files, not dependency directories or live symlinks. Each contains four header lines and whitespace padding, including an unavailable original-machine path. They are retained unchanged as harmless original artifacts; no dependency is installed or link restored. See `xsym-inspection.json` for type, size, SHA-256 and header evidence.

Only technical temporary files and actual secrets are eligible for exclusion. No task1 code or notebook is executed, no experiment is started, and no report design, P2 palette or Skill content is changed. Existing absolute paths in historical logs, scripts and XSym headers are preserved as historical content and are not newly introduced runtime configuration. Archive-internal packaging metadata is preserved inside the original teacher and Skill distribution ZIPs to avoid changing those originals.

## Verification records

- `starting-git-state.json`: branch, baseline commit, origin and live remote check.
- `starting-files.json`: SHA-256 and sizes of all pre-existing project files.
- `task1-before.sha256.json`, `task1-after.sha256.json`, `task1-integrity.json`: current hashes compared with PROJECT-BASELINE-SYNC-001.
- `full-project-files.txt`: complete publication file manifest, one repository-relative path per line.
- `full-project-excluded.txt`: actual remaining exclusions and reasons.
- `scan_project.py`, `secret-scan-summary.json`, `secret-scan-summary.txt`: read-only file/archive/PDF pattern scan and review of findings. A pattern scan cannot prove that no secret exists.
- `large-file-check.json`: sizes and GitHub ordinary-Git threshold checks.
- `staged-review.txt`: staged diff checks and immutable historical-file whitespace review, if applicable.

Commit and remote verification happen after these records are committed; their resulting SHAs and fresh remote-tree verification are reported to the user after push. No new experiment or template compilation is part of this mirror synchronization.
