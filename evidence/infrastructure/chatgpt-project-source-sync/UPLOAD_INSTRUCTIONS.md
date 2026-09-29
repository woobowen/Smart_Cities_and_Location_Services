# Project Sources 差异更新说明

当前批准集合由 [sources.json](sources.json) 定义，共 16 项；完整来源、角色和 SHA256 见 [manifest](SOURCE_MANIFEST.md)。
1. 修改权威文件后，经批准更新清单的版本和 SHA256，再运行同步工具 `--plan` 查看差异。
2. 运行写同步及 `--check`；所有来源完整、安全且 hash 正确才写入。未知 extra、目录、符号链接不会被删除。
3. 发布并实际回读固定远程版本后，按 [本次 UI 差异表](../SC-PROJECT-SOURCES-SYNC-003/handoff/UI_SOURCE_DIFF.md) 逐项更新 UI。
4. 内容变化的同名文档逐个替换；保留未变有效资料。不删除全部当前 Project Sources，不重复上传未变 PDF/ZIP。
5. 后续任务应重新核对当次 UI 基准；本次差异表只对应 SC-PROJECT-SOURCES-SYNC-003 输入。

生成文件、本地同步、远程核验、UPLOAD_BUNDLE READY、用户实际 UI 上传是五种不同状态。工具只负责前述仓库步骤。
Project Settings 最小补丁是 [TRANSFER_COPY / USER_UI_ACTION_REQUIRED](../SC-PROJECT-SOURCES-SYNC-003/handoff/PROJECT_SETTINGS_SCOPE_PATCH.md)，不是第二份 active Settings。

| Canonical upload filename | Semantic role |
|---|---|
| `SMART_CITIES_RESEARCH_PROTOCOL.md` | governance |
| `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md` | governance |
| `SMART_CITIES_REPORT_WRITING_GUIDE.md` | governance |
| `SMART_CITIES_VISUAL_SYSTEM.md` | governance |
| `AGENTS.md` | engineering_governance |
| `Process_Report_P2_Locked_v1.pdf` | synthetic_template |
| `Experiment_Report_P2_Exact.pdf` | synthetic_template |
| `WF_WorkflowConstruction_PreTask1_REVISED.pdf` | accepted_partial_history |
| `WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip` | historical_source_archive |
| `实验课1.pptx` | teacher_material |
| `作业.zip` | teacher_material |
| `任务3_LLM辅助评估清洗.ipynb` | starter |
| `作业1轨迹数据预处理.ipynb` | starter |
| `publication-plots.zip` | skill_original_archive |
| `Experiment_Report_吴博闻_10245102410.pdf` | accepted_experiment_report |
| `Experiment_Report_完整重构_源文件.zip` | accepted_source_archive |
