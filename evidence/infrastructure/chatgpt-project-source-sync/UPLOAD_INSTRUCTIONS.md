# Project Sources 差异更新说明

当前批准集合由 [sources.json](sources.json) 定义，共 15 项；完整来源、角色和 SHA256 见 [manifest](SOURCE_MANIFEST.md)。
1. 修改权威文件后，经批准更新清单的版本和 SHA256，再运行同步工具 `--plan` 查看差异。
2. 运行写同步及 `--check`；所有来源完整、安全且 hash 正确才写入。未知 extra、目录、符号链接不会被删除。
3. 发布并实际回读固定远程版本后，按 [当前 UI 交接说明](../SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001/source_sync_checks.md) 核对用户实际 UI 版本，再逐项更新。
4. 内容变化的同名文档逐个替换；保留未变有效资料。不删除全部当前 Project Sources，不重复上传未变 PDF/ZIP。
5. UI版本未知时记录 USER_CONFIRMATION_REQUIRED；用户报告已更新时记录 USER_REPORTED_UPDATED，逐项比对其批准输入与最终分发字节。无内容差异时不要求重复上传。

生成文件、本地同步、远程核验、UPLOAD_BUNDLE READY、用户实际 UI 上传是五种不同状态。工具只负责前述仓库步骤。
历史 [SYNC-003 UI差异表](../SC-PROJECT-SOURCES-SYNC-003/handoff/UI_SOURCE_DIFF.md) 及 [Settings transfer补丁](../SC-PROJECT-SOURCES-SYNC-003/handoff/PROJECT_SETTINGS_SCOPE_PATCH.md) 仅说明当时输入与交付，不代表当前UI状态或本轮需要重复套用。
Project Settings由用户在UI维护；当前交接不生成第二份active设置或新的长稿。

| Canonical upload filename | Semantic role |
|---|---|
| `SMART_CITIES_RESEARCH_PROTOCOL.md` | governance |
| `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md` | governance |
| `SMART_CITIES_REPORT_WRITING_GUIDE.md` | governance |
| `SMART_CITIES_VISUAL_SYSTEM.md` | governance |
| `AGENTS.md` | engineering_governance |
| `Experiment_Report_P2_Exact.pdf` | synthetic_template |
| `实验课1.pptx` | teacher_material |
| `作业.zip` | teacher_material |
| `任务3_LLM辅助评估清洗.ipynb` | starter |
| `作业1轨迹数据预处理.ipynb` | starter |
| `publication-plots.zip` | skill_original_archive |
| `Experiment_Report_吴博闻_10245102410.pdf` | accepted_experiment_report |
| `Experiment_Report_完整重构_源文件.zip` | accepted_source_archive |
| `Process_Report_Revised.pdf` | accepted_full_process_report |
| `Process_Report_Revised_LaTeX_Source.zip` | accepted_process_source_archive |
