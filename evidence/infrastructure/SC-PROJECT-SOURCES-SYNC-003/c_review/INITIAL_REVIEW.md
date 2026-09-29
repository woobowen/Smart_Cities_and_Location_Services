# Independent C initial review

Reviewer: the real `/root/independent_c` agent context. Scope: initial input/protection/remote/archive/role inspection for SC-PROJECT-SOURCES-SYNC-003. This is not final C acceptance or the later web GPT review.

## Actions and observations

- First shell command was `ls -la`. It showed the existing `.venv`, governance/docs/reports/releases/tools/task1 directories and the user's root ZIP inputs. No environment was installed or changed. A bare `python` command was unavailable (exit 127); the subsequent audit used the existing `.venv/bin/python`.
- Read the complete approved Prompt, current AGENTS, received Research and Writing Guide, the relevant received Visual/Evidence/AGENTS scope and integrity sections, and the existing Process archive limitation record.
- Independently calculated all seven received byte lengths and SHA256 hashes from the actual files, using baseline constants copied from the approved Prompt rather than trusting B's `match` values. All seven match.
- Read all 72 Experiment ZIP member names; ran CRC, duplicate/path/symlink/font/high-confidence-credential checks; read README and build.sh. The embedded PDF equals the received approved PDF. The only executable-text scan hit is the historical compiler line `restricted \\write18 enabled.` in `checks/final_build_pass2.txt`; it is not a source invocation. Build.sh only runs two XeLaTeX passes and copies its output locally. Native `.drawio` and plotting sources are present; their presence alone does not prove redraw reproducibility.
- Independently executed `git ls-remote origin refs/heads/main`: actual remote, HEAD and origin/main were `4483f520eabb5358d1f35cf5c33a81d3b01e47e0`. No reset or remote change was performed.
- Recomputed the hashes of the entire 5,982-file starting protection inventory. At this initial check, there were no changed or missing listed files.
- Independently read Process PDF, source ZIP and `source-archive-check.md` from Git's fixed anchor and compared them to current disk bytes. All three match. The existing `SOURCE_ARCHIVE_BUILD: PARTIAL` describes an actual 31-page rebuild with prose/annotation differences and missing-arrow glyph limitations. This remains a historical limitation; it is not a new obligation to rewrite Process content or lock evidence.

Machine details and member hashes: [initial-independent-results.json](initial-independent-results.json), [experiment-archive-members.json](experiment-archive-members.json). Reproduction command: `.venv/bin/python evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/c_review/initial_independent_checks.py`.

## Migration risks to close in the final review

These are confirmed baseline migration requirements, not claims that the unfinished new implementation has failed.

1. The old sync tool hard-codes 13 in source cardinality, output text, manifest verification and return metadata. Its write mode copies members and then unlinks all extra regular files. It must not run against the received release before migration.
2. The received release inventory contains 23 regular files: the 16 approved uploads and seven Windows `:Zone.Identifier` sidecars. Those metadata sidecars are outside the upload set. Keep their identification/protection evidence and use an explicitly documented, reversible disposition; do not treat them as permission for generic deletion of extra files.
3. P1 must be explicit in the Writing Guide; P2 in Research; P3 in Writing/Evidence; P4 in Visual. AGENTS should route and enforce these requirements without creating competing long-form definitions. W01–W22, precise P2/XeLaTeX, first-person ownership, original wording, minimum box/arrow/PPI and Lock controls must remain intact.
4. Received Evidence §4.1 says “当前长期规划对话” and §§6/28 say “从Experiment 1…”. These are known scope/role ambiguities to correct. User designation, not reading a new conversation, determines Evidence Master.
5. The Experiment source package README explicitly identifies its numerical basis as historical commit `718e6d9…`; report rebuilding does not create a new experimental run or update that numerical CODE_SHA. A normal report build must use the imported chapters and avoid regenerating Process or old 22-page text.

## Pending independent checks

Final active/bundle contents and minimal diffs; explicit list/manifest semantics; read-only/idempotent/error-safe sync fixtures; clean report rebuild and rendered sample comparison; normal generation routing; package hash correspondence; frozen artifacts; and the final review packet/publication evidence are pending B's ready notification. Final status is **REVIEW_IN_PROGRESS**.
