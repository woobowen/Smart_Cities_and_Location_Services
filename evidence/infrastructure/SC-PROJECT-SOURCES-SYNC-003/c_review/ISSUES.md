# Independent C issues and follow-up

This log records actual findings in this agent context, not manufactured review errors. Baseline hazards are documented separately in [INITIAL_REVIEW.md](INITIAL_REVIEW.md).

| ID | Finding / affected scope | Author response | C re-verification | Status |
|---|---|---|---|---|
| C-001 | `sources.json` described the AGENTS version as `2026-09-29 · Project scope / source synchronization`, while the actual active `Revision` was `2026-09-29 · Project-wide P1–P4 scope / manifest-driven source distribution`. Manifest/version traceability was imprecise. | Root corrected the structured declaration and regenerated only its manifest; active AGENTS and bundle bytes did not change. | C independently parsed the active Revision and declaration version and confirmed exact equality; the real bundle check also succeeded without changing source/bundle/metadata bytes or mtimes. | CLOSED |

The report/entry/package/navigation evidence requirement is now CLOSED within
the reviewed artifact scope. C had requested that historical FULL inheritance
distinguish changed `goal3/__main__.py` from unchanged numerical dependencies.
The actual final ZIP is `231ce92475fdfe7ed12fa1c7e3304c22d6fd56ce39a0b53b43fee87103334a63`.
C compared all 116 members with both the prior current ZIP and the actual
historical FULL execution ZIP: 112 members match; only manifest, README,
`__main__.py`, and Experiment PDF differ. C verified unchanged FULL/LIVE function
AST and ran seven isolated entry/CLI boundary checks, frozen contract/production
gates and all 32 numerical source bindings, with zero model attempts or trajectory
runs. [Actual results](independent-package-review.json) preserve the original
`e12f8a27944210adb452730be92a0674dfc6b84b` processing identity. This is not a new FULL
execution and was an evidence requirement, not a reproduced numerical defect.

Both normal builds were bound independently to their actual PDFs, all 25 page
renders and all 51 current source hashes; both have approved-exact text and page
count. The current report and package preserve the approved PDF bytes. The seven
current navigation documents were read and their 246 local targets exist. See
[build verification](normal-builds-independent-check.json) and
[navigation links](current-navigation-links.json). Final publication and web GPT
review remain outside this prepublication C conclusion.

No synchronization bug was found in the independent fixtures: see [13 independent probes](independent-sync-results.json), including rollback after both payload files had already been replaced but before manifest replacement.
