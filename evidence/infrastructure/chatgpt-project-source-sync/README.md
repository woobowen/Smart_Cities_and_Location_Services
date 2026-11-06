# ChatGPT Project Sources distribution

当前有效同步为 [SC-PROJECT-REFRESH-20261106](../SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md)：20 条登记、12 项 active、8 项历史 false，分发目录恰好 12 项。`--check` 返回 0、`UPLOAD BUNDLE READY`；全部 active 源、规范分发字节和登记 SHA 一致，见[机器回执](../SC-PROJECT-REFRESH-20261106/source_set_verification.json)。实际 UI 状态为 `USER_UI_ACTION_REQUIRED`，GPT 外审尚未执行。

唯一结构化批准清单：[sources.json](sources.json)。四份规范升级至 Evidence v2.9、Visual v2.8、Writing v1.4、AGENTS 2026-11-06；Research v1.3 保持原字节。保留既有有效参考，五份历史/重复材料仅退出分发，其权威原件和验证后的私密归档均保留；新增任务二 `Experiment2_Experiment_Report.pdf` 与 `Experiment2_Process_Report.pdf`。publication-plots 原批准发行字节未变。数量按清单推导，本轮 12 项不是脚本永久常量。

权威源 → 清单 → bundle。release 是上传准备目录，不是第二份编辑源。入站文件先在该目录外校验并私密暂存；完整源 ZIP、视频、raw 帧、未选截图和 Settings transfer TXT 不属于本轮分发集。Project Settings 仅由用户在 UI 维护。

```bash
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --plan
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
.venv/bin/python -B -m pytest evidence/infrastructure/chatgpt-project-source-sync/test_sync_sources.py -q
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py --index
```

`--plan` 和 `--check` 只读，后者不刷新 metadata；无参数才受控写同步。先验证全部权威来源、路径与 SHA，再暂存、替换 bundle 和两份派生 metadata；失败保留恢复记录并回滚已替换内容。unknown extra、目录或符号链接均拒绝，不自动删除。此次获准的五份退出副本、已知入站文件和五份下载元数据均逐项验证、保护后受控移出，未放宽安全检查。`--index` 另核验 Git 暂存字节。

[生成清单](SOURCE_MANIFEST.md)、[生成上传说明](UPLOAD_INSTRUCTIONS.md)、[当前 UI 交接](../SC-PROJECT-REFRESH-20261106/UI_HANDOFF.md)。此前未发布的 [16 项 Process 中间方案](../../../task2/review/PROCESS_REPORT_SYNC_20261106.md)、下载元数据阻塞及 2026-11-05 的历史同步回执保持原阶段身份，不描述当前 12 项状态。

以下仅是历史迁移记录，数量、当时清理行为和测试结果均不描述当前工具。

## Historical migration: SMART-CITIES-CHATGPT-PROJECT-SOURCES-UPLOAD-BUNDLE-002

Pre-flight: main, clean tree, local/remote baseline `eb9daccfd149ed00dfc2d83d41a5f4845aada54f`. Initial upload directory had twelve files: the approved eleven plus an internal manifest. That manifest was moved here and rewritten for upload-bundle semantics. No other real upload file needed removal. AGENTS and the design-system README were updated, then AGENTS was copied from its active source. Research/Evidence/Visual protocol content, P2, templates, canonical previews, teacher materials, notebooks, task1 code and installed Skill content are protected by baseline hash comparisons.

No active-like duplicate Markdown documents were found outside the canonical source plus allowed distribution copy. Old ignored Zone.Identifier sidecars outside the upload directory are download metadata, not active Markdown versions; they are not uploaded. Historical archive ZIPs remain intact.

Historical run 001 JSON/TXT records preserve the filenames, roles and hashes measured then. Those historical references are not current manifest links and are not rewritten to fabricate a different past result. Its README now routes current operations here. Earlier release-packaging scripts remain historical, not supported upload-sync entrypoints. Git retains prior versions; no parallel active governance files or versioned bundle directories are introduced.

## Historical verification records (unchanged)

- `preflight.json`: initial directory/hash inventory and protected original-file hashes.
- `sync-result.json`: actual sync output and final eleven hashes.
- `validation.json`: exact set, ordinary files, source bytes, internal manifest, known Skill hash/effective members, protected-file integrity, versions, duplicate detection, links, syntax and Git checks.
- `directory-listing.txt`, `bundle-sha256.txt`: actual find/sha256sum output.
- `publication-check.json`: credential-pattern, file-size and publication-scope review.

The validator exercises cleanup of extra ordinary metadata/suffix files, idempotency, stale-copy repair, and rejection of missing sources, wrong Skill hash, unexpected directories and symlinks in a temporary fixture. It verifies no mutation on those failures and no change to fixture active sources. It never executes notebooks or task1 code.

The publication scan covered the upload files and effective archive content. Two literal-credential candidates in the original assignment archive were reviewed as explicit Chinese placeholders, not real credentials; no high-confidence credential pattern matched. Original archives were not edited.

PPI and report visuals are unaffected because all template, palette and canonical preview bytes are unchanged. No LaTeX rebuild is required or performed. PDFs remain synthetic reference previews; supplied teacher/starter outputs remain historical/pre-generated. No current-run sample/full experiments or formal figures are created.

New system/language packages, fonts/toolchains and environment configuration changes: none. No Project Settings file is created; the UI is not accessed. After commit/push, the resulting SHA and fresh remote comparison are reported to the user. Stop and wait for GPT's independent remote audit; do not start Experiment 1.
