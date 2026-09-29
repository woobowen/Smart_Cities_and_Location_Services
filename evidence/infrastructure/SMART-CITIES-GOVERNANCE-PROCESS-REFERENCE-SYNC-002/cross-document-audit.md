# Cross-document audit

Scope: Governance / Process Report Reference / Project Source Sync only. This is an engineering audit, not an Evidence Master Lock or research conclusion.

| Check | Result | Evidence |
|---|---|---|
| First-person narrative | PASS | Protocol §§16.1, 35, 39; Visual §§4.1, 15; AGENTS §§12, 16 require “我”, restrict “我们” to actual joint work and prohibit mechanically replacing the approved voice with “用户”. |
| Terminology ownership | PASS | Protocol §§3, 9, 16.1; Visual §4.1; AGENTS §16 preserve who introduced a term and when. |
| Phrase / Box / Arrow precision | PASS | Protocol §§24.3–24.4 and §30 include minimum sufficient scope, PHRASE MATCH, BOX RANGE, ARROW RELATION, ARROW ENDPOINT and SOURCE RESOLUTION. Visual §8.7 and AGENTS §13 require final-render verification. |
| Evidence Master / Codex authority | PASS | Protocol §24.5 and AGENTS §13 assign phrase, box range and relationship decisions to Evidence Master; Codex implements the approved specification. No new relationships or locks were authored. |
| Template vs real reference | PASS | Visual §16, Process README §10 and the manifest distinguish the unchanged Visual / Layout Template Reference from the accepted 31-page real-content reference. The source archive's PARTIAL reproduction is disclosed separately. |
| 13-file consistency | PASS | AGENTS §18, existing sync and validation tools, SOURCE_MANIFEST, UPLOAD_INSTRUCTIONS and the actual bundle all use 13. All roles are PROJECT_SOURCE. |
| Source authority | PASS | The five user-approved release inputs were hashed before writes. Protocol was copied exactly; AGENTS received only four 11→13 substitutions; Visual received only the reference block and verification note. Final copies flow active → bundle. |
| Research and Task 1 boundary | PASS | Research Protocol, Task 1, teacher materials, notebooks, template sources/previews and installed plotting Skill are protected by preflight hashes. No research code or notebook was executed. |
| Settings/UI boundary | PASS | No Project Settings file was created; no ChatGPT UI tool was used. The user's prior manual UI update is recorded as user-provided information, not independently verified UI state. |

The approved-input-to-active diff is [approved-input-mechanical-changes.diff](approved-input-mechanical-changes.diff). It intentionally excludes the user's already-approved governance changes relative to old Git HEAD.

## Current references vs historical facts

Current 11-file references were updated in AGENTS, the two existing tools, the generated manifest, upload instructions, `docs/design-system/README.md`, and the current-operation portions of the infrastructure READMEs. Only the routing header changed in the historical run 001 README.

Historical run 001 records, the prior upload migration's prose, its eleven-hash evidence, historical validation JSON and archived distributions were preserved. [legacy-eleven-classification.txt](legacy-eleven-classification.txt) lists the remaining prose matches. The old release-packaging scripts remain historical entry points; only the established `sync_sources.py` is the current sync tool.

Canonical active Markdown sources remain root AGENTS, `docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md`, and `docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md`. Their release copies are distribution only. No duplicate active document was introduced. Historical ZIP contents are not active governance.

## Reference verification limit

[Source archive check](source-archive-check.md): the unchanged source builds 31 pages, but does not fully reproduce revised wording/box geometry and has nine missing arrow glyphs. SOURCE_ARCHIVE_BUILD is PARTIAL. Prompt §8 permits synchronization with that recorded limitation. This audit's governance-rule PASS is not a claim that all historical reference pages have been re-audited or relocked against those rules.
