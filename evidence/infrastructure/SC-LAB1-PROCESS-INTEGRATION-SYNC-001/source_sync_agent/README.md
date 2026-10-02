# Source sync implementation and self-check

Task: SC-LAB1-PROCESS-INTEGRATION-SYNC-001. Context: delegated `source_sync` implementer. This is implementation evidence and author self-check, not independent internal review.

The existing synchronizer already calculated member counts from the declaration, rejected unknown entries, staged writes and rolled back caught update failures. The initial existing suite passed: 19 tests. The substantive defect was the Skill verifier reading its input from the distribution directory regardless of `active_path`; generated guidance also treated old Process/PreTask identities as current.

The change is limited to the existing `sync_sources.py` and its safety tests:

- Read the approved original Skill archive from its declared independent source, retain its fixed approved SHA256 and compare effective members against the installed Skill. Missing or corrupt distribution copies can now be restored from that source.
- Reject any declaration that uses the upload directory as an active source. Accept explicit `project_source=false` history, validate its source bytes, list it separately, and calculate upload membership only from `true` entries.
- Generate current manifest guidance from source metadata, remove fixed old preview/Process descriptions, and explain `USER_REPORTED_UPDATED` without claiming UI access or requiring unchanged files to be uploaded again.
- Preserve the existing controlled replacement and rollback mechanism; no unknown file deletion was added.

The final recorded run passed **37 tests**. [execution.json](execution.json) contains exact commands, timestamps, tool versions, exit codes and source/test SHA256; [check_1.txt](check_1.txt) lists each executed case. [implementation.diff](implementation.diff) is the exact implementation/test diff at that run; [check_2.txt](check_2.txt) records the successful whitespace check. Python syntax was also parsed with `ast.parse` for both changed files.

Coverage includes dynamic membership, non-upload history, source hash validation, missing sources, same-count wrong members, unknown extras, file/parent/declaration/metadata symlinks, directories, traversal/absolute paths, archive identity, installed-Skill content disagreement and distribution self-reference. The actual copied CLI was invoked with `--plan` and `--check` against ready, wrong-member, missing-source and stale-metadata fixtures, with file content and nanosecond mtime snapshots before/after. A second write leaves bytes/mtimes unchanged. Injected mid-update errors verify restoration of existing bytes/mtimes, removal of only the transaction-created new files, and retained `ROLLED_BACK` recovery records. Failing CLI checks do not print READY.

All mutation tests use isolated temporary roots. This context did not write the real release directory, edit `sources.json`, alter any report or scientific input, install dependencies or commit files. The parent thread owns the actual manifest/release synchronization and independent approved-input comparisons; independent review is a separate context and remains outside this self-check.
