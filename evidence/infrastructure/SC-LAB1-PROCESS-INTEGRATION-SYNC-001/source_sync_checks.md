# 项目源同步与 UI 差异

用户报告 Project Settings 与项目源已更新，登记 `USER_REPORTED_UPDATED`。Codex没有操作UI。本轮最终release逐文件与用户Prompt的独立SHA256基准比较：名称集合完全一致，15项全部同字节，差异列表为空。**本次无需再次上传这些文件，也无需重贴Settings。**这不把用户报告状态写成Codex实际UI核验。

唯一结构化清单：[sources.json](../chatgpt-project-source-sync/sources.json)；生成说明：[SOURCE_MANIFEST](../chatgpt-project-source-sync/SOURCE_MANIFEST.md) / [UPLOAD_INSTRUCTIONS](../chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md)。完整hash与传输关系见 [transfer_map.json](transfer_map.json)。

实际真实目录检查见 [execution.json](source_sync_checks/execution.json)。首次plan如实列出缺少的新Process两项和授权可移出的三项旧参考；完成历史hash核对后精确移出，未清空目录。写同步只增加Process PDF/ZIP并更新两份生成说明。随后check成功，第二次sync的updated为空；内容与mtime均未变。plan/check在正式操作前后均以hash/mtime快照证实只读。

同步器[37项隔离用例](source_sync_agent/check_1.txt)由执行者运行，又由独立审查上下文重跑；覆盖缺来源、坏hash、同数量错成员、未知extra、目录/链接、越界、自引用、installed Skill不一致、失败回滚、幂等以及实际CLI只读性。故障用例没有操作真实release。

release最终成员（数量从集合计算）：

- `AGENTS.md`
- `SMART_CITIES_RESEARCH_PROTOCOL.md`
- `SMART_CITIES_REPORT_WRITING_GUIDE.md`
- `SMART_CITIES_VISUAL_SYSTEM.md`
- `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md`
- `实验课1.pptx`
- `作业.zip`
- `作业1轨迹数据预处理.ipynb`
- `任务3_LLM辅助评估清洗.ipynb`
- `publication-plots.zip`
- `Experiment_Report_P2_Exact.pdf`
- `Experiment_Report_吴博闻_10245102410.pdf`
- `Experiment_Report_完整重构_源文件.zip`
- `Process_Report_Revised.pdf`
- `Process_Report_Revised_LaTeX_Source.zip`

三个旧分发件只改变上传成员身份：PreTask PDF/ZIP保留在reports/process-report/pre-task1/；原Process模板preview保存在模板preview/history/，新的合成preview仍在原模板体系，不成为本轮上传成员。

四个Zone.Identifier为完整盘点发现的额外项，已逐个保护至仓库外私密快照，仅移出release；没有其他未知extra。publication-plots批准原件以原字节保存到releases/skills/publication-plots-approved-original.zip，旧不同hash归档未覆盖。
