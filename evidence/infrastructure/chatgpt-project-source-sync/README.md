# ChatGPT Project Sources distribution

当前同步记录：[SC-LAB1-PROCESS-INTEGRATION-SYNC-001](../SC-LAB1-PROCESS-INTEGRATION-SYNC-001/REVIEW_PACKET.md)；[SYNC-003](../SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md)保留历史身份。
唯一结构化批准清单：[sources.json](sources.json)。程序按清单推导数量，角色、适用范围、版本、配对、批准范围与hash汇总在生成的 [SOURCE_MANIFEST.md](SOURCE_MANIFEST.md)。

权威源 → 清单 → bundle。用户本轮在release提供的四份规范已先保存在仓库外不可变私密快照，再逐字节导入权威位置；位置与hash记录在本轮任务目录，仅本次受控导入允许反向迁移。Project Settings仅在UI维护。

```bash
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --plan
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
.venv/bin/python -B -m pytest evidence/infrastructure/chatgpt-project-source-sync/test_sync_sources.py -q
.venv/bin/python -B evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py --index
```

`--plan`和`--check`只读；`--check`不创建或刷新manifest。经批准的active修改须同步更新sources.json对应版本/hash。写同步先校验全部来源、路径和hash，再暂存并受控替换bundle和生成metadata；失败保留恢复记录并回滚已替换文件。未知extra一律拒绝，不默认删除。重复运行无内容变化则不修改mtime或日期。`--index`用于暂存后核验Git索引。

publication-plots从独立的releases/skills/publication-plots-approved-original.zip原字节分发，固定hash和installed effective members双重验证；所有成员从manifest指定的canonical active路径分发，禁止release自引用来源。不执行Notebook或实验、不修改Process原件、不重新打包Skill。

UI按[差异更新说明](UPLOAD_INSTRUCTIONS.md)操作，仅替换实际变化文档，保留未变有效资料。bundle就绪不代表UI已更新。用户本轮已报告UI更新，记录USER_REPORTED_UPDATED；最终15项均同批准输入，当前无再次上传动作。

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
