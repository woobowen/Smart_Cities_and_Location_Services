# 2026-11-06 规范升级与 Project Sources 精简：GPT 外审入口

任务：`SC-PROJECT-REFRESH-20261106`。本轮是受限文档接管、规范替换、成员精简及 GitHub 同步，不是新研究 Goal。审核对象为最终交接提供的固定 Git 提交；仓库 `woobowen/Smart_Cities_and_Location_Services`，分支 `main`，基准 `b7fd9ee522905c11ddcea760470e7a5f0c1be9f0`。为避免自身提交身份循环，本文件不嵌入自身 SHA；发布后的外部审核包 `FIXED_COMMIT.json` 和 `REMOTE_VERIFICATION.json` 提供实测 local/remote SHA 及逐文件回读。

本地当前状态：`UPLOAD_BUNDLE_READY`；ChatGPT UI：`USER_UI_ACTION_REQUIRED`；GPT 外审：`NOT_PERFORMED`。只有普通 push 和固定版本实际回读成功后，最终交接才报告 `READY_FOR_GPT_EXTERNAL_REVIEW`。内部检查、GitHub 同步、上传包就绪、UI 实际操作、GPT 外审、Evidence Lock 和教师提交分别判断。

## 实际输入、四份规范与差异

实际入站包名为 `Smart_Cities_Project_Sources_Video_Workflow_Update_20261106.zip`，而非提示词中的建议名称。SHA-256：`5012d8643f7a59208b89dc5be803b65b8701e9c55a85cb8c345767adf55dae13`。10 个成员通过安全路径、文件类型及 CRC 检查；入站 ZIP 及 Settings transfer TXT 在仓库外私密保存。[入站回执](intake.json)。

四份权威文件与批准包逐字节一致：Evidence v2.9、Visual v2.8、Writing v1.4、AGENTS 2026-11-06。先实际比较旧→新全文，再写入；[完整实际 diff](governance.diff)与[批准版本/SHA](approved_versions.json)可复查。Research v1.3 未改字节。目标 JSON 只是批准名单，[active sources.json](../chatgpt-project-source-sync/sources.json)按实际结构和已有改动更新，没有用计划 JSON 覆盖。

## 精确 12 项 Project Sources

20 条登记中 12 条 true、8 条 false；这是本轮目标检查，现有同步器没有永久数量常量。规范名、权威路径、版本、语义身份和实际 SHA 由结构化清单维护，分发目录仅存下表 12 项。

| 规范文件名 | 版本 / 身份 | SHA-256 |
|---|---|---|
| `SMART_CITIES_RESEARCH_PROTOCOL.md` | v1.3 | `ec43f4ceab061ff6d4f1cccdec401f2f7a514aa5a5ba5963a1bcc7254c1d1b98` |
| `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md` | v2.9 | `bec2a66770da9dc80991e84aebc67e2284310f9980671129200f706576db01fc` |
| `SMART_CITIES_REPORT_WRITING_GUIDE.md` | v1.4 | `4aef6e48c79efe87e49d2173f9975d65d8bf6716a3f2f0dd04308b2daee90f18` |
| `SMART_CITIES_VISUAL_SYSTEM.md` | v2.8 | `d109b1072cb05a5309c96e3f5aa1337d0e2a67614a1e7cbc0a62fa50253b45a8` |
| `AGENTS.md` | 2026-11-06 | `98b6b7063042b3b3e3e6b8b49d8460a514bd0ed1af0965fdb739c54d6c0694d7` |
| `publication-plots.zip` | approved original | `b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041` |
| `Experiment_Report_吴博闻_10245102410.pdf` | accepted 25-page reconstruction | `2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0` |
| `Experiment_Report_完整重构_源文件.zip` | accepted 25-page reconstruction | `6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd` |
| `Process_Report_Revised.pdf` | 2026-10-03 authorized p76 revision of prior accepted 77-page report | `dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23` |
| `Process_Report_Revised_LaTeX_Source.zip` | 2026-10-03 authorized p76 revision of prior accepted 77-page report | `831d61baa7de160796827b60f29e1ada9f1b3809c2a87aa4acd6b98703e352ef` |
| `Experiment2_Experiment_Report.pdf` | Experiment 2 technical review, 26 pages | `7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101` |
| `Experiment2_Process_Report.pdf` | 2026-11-06 approved 16-page video-evidence PDF | `c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f` |

完整权威路径与字节数见 [source_set_verification.json](source_set_verification.json)；每个 active 源、分发副本与登记 SHA 均相同，`set(actual)==set(approved)`。[生成清单](../chatgpt-project-source-sync/SOURCE_MANIFEST.md)与[上传说明](../chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md)由同一清单推导。

## 五份退出材料及历史保护

以下仅将 `project_source` 改为 false，并将已经核实等于权威源的 release 副本迁出至仓库外归档、另存备份。权威原件仍在原路径且 SHA 不变：

| 退出分发名称 | 保留的仓库权威原件 | SHA-256 |
|---|---|---|
| `Experiment_Report_P2_Exact.pdf` | [templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf](../../../templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf) | `6fd543f5123ba4d67985193d5658802ae820c6585dc3f509071b8b2d39b323dd` |
| `实验课1.pptx` | [task1/实验课1.pptx](../../../task1/实验课1.pptx) | `cf5fdbdd0e116818f4bf195e8761dd55c4733443d7c360c986cf1cdfddfda075` |
| `作业.zip` | [task1/作业.zip](../../../task1/作业.zip) | `818d483cf719aeb1145ea97b551b2648913559ed1fca0be220ed41eff8ba42cc` |
| `任务3_LLM辅助评估清洗.ipynb` | [task1/作业/作业/任务3_LLM辅助评估清洗.ipynb](../../../task1/作业/作业/任务3_LLM辅助评估清洗.ipynb) | `4ecffe64024e002c0cffe7830e18b5f6ded04cd5aa9dd645d6798fc9b0715add` |
| `作业1轨迹数据预处理.ipynb` | [task1/作业/作业/作业1轨迹数据预处理.ipynb](../../../task1/作业/作业/作业1轨迹数据预处理.ipynb) | `8601d1dfecaef062fef553992cc9774d3a0eb551751c70536f5b52f1343b158a` |

[逐项迁出与备份回执](release_retirement.json)。原已 false 的 `Process_Report_P2_Locked_v1.pdf`、`WF_WorkflowConstruction_PreTask1_REVISED.pdf`、`WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip` 保持原身份与元数据。publication-plots 原发行包哈希未变。五个下载元数据按用户先前逐名授权移出并保留旧备份，见[独立阶段回执](metadata_relocation.json)。没有清空 release 或放宽 unknown-extra 安全检查。

## 实验二正式 PDF 与源码真实范围

| 成品 | 权威路径 | 页数 | SHA-256 |
|---|---|---|---|
| Experiment | [Experiment_Report.pdf](../../../task2/reports/experiment/Experiment_Report.pdf) | 26 | `7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101` |
| Process | [Process_Report.pdf](../../../task2/reports/process/Process_Report.pdf) | 16 | `c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f` |

Process 采用此前已接管且匹配用户指定 SHA 的唯一字节版本：从 SHA `f73432aef93abdad0c37757df03b13811ab0beb1b508f700562bb0edada1c55a` 的配对入站源 ZIP 内 `task2/reports/process/main.pdf` 取得；standalone resend PDF 的 SHA 是 `399970a96f63d70fd2b978b56058f85f692a77c7099f38005eee792f60a3525e`，两者不能称为相同字节。其全文提取相同；此前 GPT 转交的全页渲染等价结论保留为转交范围，不冒称本轮独立做过两个入站版本的全页像素检查。[原接管回执](../../../task2/evidence/process_report_sync_20261106/intake.json)。

用户批准的内容变化仅删除末尾《视频证据的来源、裁切与复现》附录及目录项；Codex 没有改写、重排或用重编译输出覆盖成品。未取得删附录前完整批准 PDF，因此不声称独立完成其前后全文差分。原 8 页稿保留[历史身份](../../../task2/reports/process/history/20261105_8page_handoff/README.md)。

源码接管已在此前阶段完成：11 个任务 `.tex`，9 个原字节、2 个只作 3 处图片路径替换，18 个已在正式 PDF 出现的 PNG 原字节集成。源 ZIP 的 64 个成员安全检查与 CRC、63 条哈希均通过。隔离 XeLaTeX 编译返回 0、16 页、全文相同；临时进程 Fontconfig 使粗体恢复 Bold 后，200 dpi 比较只有第 1、6、15 页像素完全相同，其余 13 页仍不同，严格验证返回非零。状态为 `COMPILE_AND_TEXT_VERIFIED / PIXEL_RENDER_DIFFERENCE_RECORDED`，不能声称像素或二进制重建通过。[源与构建说明](../../../task2/reports/process/README.md)、[实际比较](../../../task2/evidence/process_report_sync_20261106/installed_build_fontfix/process_verification.json)、[独立测量](../../../task2/evidence/process_report_sync_20261106/independent_review/fontfix_render_measurements.json)。

此前集成线程已实际查看批准 PDF 全部 16 页的 200 dpi 完整渲染，[逐页记录](../../../task2/evidence/process_report_sync_20261106/page_review.json)。这不是新的 Evidence Lock。Experiment 正式 PDF、源、结果和既有技术二审范围保持原身份；本次仅核验页数与冻结字节，没有重新编译或重跑任何研究。旧 `Dispatch_Reports_LaTeX_Source.zip` 保留原 26+8 页配对，不能用来宣称完整重建当前 26+16 页。

## 同步与内部验证

真实顺序为 `--plan` → 逐项受控归档/规范名迁移 → 再次 `--plan` → 无参数写同步 → `--check`。脚本没有独立 `--sync` 参数，未猜测接口。初始计划的精确已知 extras、受控归档和安全计划均保留：[原计划](sync_plan_before_archive.json)、[安全计划](sync_plan_safe.json)、[实际写入](sync_write.json)、[check](sync_check.json)。最终 check 返回 0，`UPLOAD BUNDLE READY`、file_count=12，无 unknown extra；写同步 removed=[]。

现有同步器安全回归 37 项通过，未修改或弱化安全脚本。暂存后另实际执行 `validate_sync.py --index`、最终只读 plan/check、Git diff 和公开边界审查，回执追加到本目录。已有[独立初核](independent_review/INITIAL_REVIEW.md)核验了批准包、实际 diff、冻结成果和原 Process 检查继承范围；最终检查须读取对应追加回执，不能把初核时中间状态当作最终集合。

最终回执：[无变更只读计划](final_plan.json)、[12 项 check](final_check.json)、[暂存索引验证](index_validation.json)、[实际暂存公开边界审计](staged_publication_audit.json)及[独立最终核验](independent_review/FINAL_REFRESH_REVIEW.md)。源/文档 whitespace 检查通过；整包 `git diff --cached --check` 返回 2，仅来自两份原始编译日志及准确 `governance.diff` 中保留的原始空格/Markdown 换行与 diff 上下文，没有为格式检查改写这些真实回执。远程发布后使用[固定版本回读工具](verify_remote.py)，验证全部登记权威原件、12 份分发件及所有新增/修改 Git blob 的实际 HTTPS 字节、SHA-256 和 Git blob ID。

## 公开边界与尚未检查事项

公开内容包括四份完整规范、结构化及派生清单、两份正式任务二 PDF、已集成的必要 Process `.tex`/正式引用 PNG、旧 8 页历史稿和最小工程审核记录。完整输入源 ZIP、原视频、16 个解码原帧、未入选裁片、私密母件和 Settings TXT 均未发布；原视频实际未收到。仅公布正式 PDF 内已出现的截图不能扩展为原始来源公开授权。原始时间码和裁切原记录在私密备份保留，未因删附录销毁。

最终独立核验发现，旧阶段尚未提交的 `integration.json` 含 17 个裁片的详细来源时码、原帧哈希及裁切坐标。完整原回执已按原字节私密保留并记录 SHA；公开同路径回执明确标为最小脱敏摘要，删去这 51 个字段值，既有核验结论不变。原始记录的历史哈希继续指向私密原件，不能拿来验证公开摘要。[公开范围收窄回执](publication_projection.json)。正式 PDF、源、截图与 raw 原件未改动。

Research、P2、教师材料权威原件、实验一、实验二算法/模型/原始及聚合结果、既有图表和 Experiment Report 保持基准字节；没有扩大 Foursquare 逐条数据公开范围。待提交文本进行实际密钥模式、PNG metadata/内嵌图像、数据排除集及许可边界检查；检查范围和限制由最终回执说明，不声称穷尽所有历史 Git 对象或外部服务。

未执行 ChatGPT UI Settings 粘贴、UI 源成员替换/去重、GPT 外部二审、用户最终验收或教师提交。[UI_HANDOFF.md](UI_HANDOFF.md)给出准确操作清单。当前规范不会强制追改历史报告或恢复来源附录。
