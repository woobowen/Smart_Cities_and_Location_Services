# 实验二 Process Report 同步：GPT 二次审核入口

本文件是被新批准范围承接的 **16 项中间方案历史记录**，未按该方案独立 commit/push。用户随后明确授权元数据迁出并批准四份规范升级和 12 项精简；当前清单、阻塞处理结果与外审入口以 [SC-PROJECT-REFRESH-20261106](../../evidence/infrastructure/SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md)为准。以下原检查、旧数量和当时状态均只描述原阶段，不表示当前 release 或 UI 状态。

当前最终复核状态：分发目录出现 5 个清单外 `:Zone.Identifier`，较早的 16 项 `--check` 成功回执保留历史身份；当前重验为 `BLOCKED_UNKNOWN_EXTRAS / NOT_READY`。已逐字节备份，原位等待用户授权移出，不删除未知 extra、不放宽同步器。解除后必须另保存最终重验回执。

任务：`SC-LAB2-PROCESS-SYNC-20261106`。本轮只接管、同步及发布用户已认可的文档，最终状态为 `READY_FOR_GPT_REVIEW`；不是新的研究 Goal，不新增实验、优化、算法结论或报告改写。

## 审核对象与内容边界

正式文件：[Process_Report.pdf](../reports/process/Process_Report.pdf)，16 页，6,139,844 字节，SHA-256：

`c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f`

用户转交的批准范围是：仅删除末尾“A 视频证据的来源、裁切与复现”附录及目录项，保留其余正文、结论、原生截图、TikZ 箭头和排版。Codex 没有编辑这些内容；正式 PDF 为精确获批字节的副本。未取得删除附录前的完整 PDF，故没有独立宣称做过该前后版本的全文差分。

实际入站名称为 `Process_Report_Experiment2_FINAL_resend.pdf` 和 `Process_Report_Experiment2_SOURCE_resend.zip`。独立 PDF 的 SHA 为 `399970a96f63d70fd2b978b56058f85f692a77c7099f38005eee792f60a3525e`，未作为正式版本；其全文与获批 PDF 相同。源包精确匹配预期 SHA，且其内部 `task2/reports/process/main.pdf` 精确匹配预期 PDF SHA，因此从该已验证入站包恢复指定字节。原件均保留，见 [intake.json](../evidence/process_report_sync_20261106/intake.json)。

## 配对源码与构建

源包 SHA：`f73432aef93abdad0c37757df03b13811ab0beb1b508f700562bb0edada1c55a`。64 个成员的路径、CRC 和全部 63 条成员哈希通过；安全解压后进行了隔离 XeLaTeX 编译。[当前源码与构建说明](../reports/process/README.md)。

- 11 个 `.tex` 已接入：9 个保留原字节，另 2 个仅作 3 处图片相对路径替换。
- 公开 17 个被引用裁片及 1 个已在获批 PDF 出现的原弹窗；18 个 PNG 与原包字节及 PDF 内嵌图像对应。16 个来源原帧、未选裁片和完整入站 ZIP 留私密。
- 公共模板、P2、`common.tex`、Experiment Report、算法与结果保持基准提交 `b7fd9ee522905c11ddcea760470e7a5f0c1be9f0` 的字节。原 8 页稿另存历史，旧源包保持原身份。
- 源码实际编译返回 0，页数与全文通过。首次自动粗体误选 Black；进程临时 Fontconfig 改为原稿 Bold 后，1、6、15 页的 200 dpi 像素相同，其余 13 页仍有差异。严格完整验证命令因此返回非零，源码状态为 `COMPILE_AND_TEXT_VERIFIED / PIXEL_RENDER_DIFFERENCE_RECORDED`，不宣称像素等价或二进制复现。

证据：[集成](../evidence/process_report_sync_20261106/integration.json)、[原包隔离编译](../evidence/process_report_sync_20261106/source_build.json)、[首次完整比较](../evidence/process_report_sync_20261106/installed_build/process_verification.json)、[字重修复后比较](../evidence/process_report_sync_20261106/installed_build_fontfix/process_verification.json)、[独立核验全文](../evidence/process_report_sync_20261106/independent_review/REVIEW.md)。没有使用重编译结果覆盖正式 PDF。

## 页面检查

Codex 集成线程实际查看了获批 PDF 全部 16 页的 200 dpi 完整页面，检查目录、末页、正文、截图、箭头与页面边界，记录在 [page_review.json](../evidence/process_report_sync_20261106/page_review.json)。这项检查是接管工程检查，不重新授予 Evidence Lock。重编译 PDF 全部 16 页做了自动像素比较，实际目视比较包括第 1、7 页；独立 Agent 另实际查看第 7 页两份完整渲染。未把自动比较或缩略图冒称所有重编译页的人工检查。

## Project Sources 与 UI

当时规范名称：`Experiment2_Process_Report_吴博闻_10245102410.pdf`。权威路径：`task2/reports/process/Process_Report.pdf`。该分发名后按新批准范围迁移为 [Experiment2_Process_Report.pdf](../../releases/chatgpt-project-sources/Experiment2_Process_Report.pdf)，字节保持不变。

[sources.json](../../evidence/infrastructure/chatgpt-project-source-sync/sources.json) 当前明确批准 **16 项**。仅新增上述 PDF；原 15 项的成员元数据与源/分发字节保持不变，实验一 Process PDF/源包未被替换。新版源包 ZIP 不是 Project Source。

已真实执行现有同步器 `--plan` → 无参数写同步 → `--check`。计划仅新增该 PDF、刷新两份派生 metadata，无 unknown extra/unsafe/missing；写入 removed=[]；最终 `--check` 返回 0、`UPLOAD BUNDLE READY`、file_count=16。全部 16 项按名称、集合、权威字节、分发字节与 SHA 核对，详见 [同步结果与完整清单](../evidence/process_report_sync_20261106/sources_verification.json)。

**待用户在 ChatGPT UI 操作**：新增上述规范 PDF，保留其余 15 项有效来源；不上传完整入站 ZIP、原始视频或原帧。实际 UI 上传状态是 `USER_UI_ACTION_REQUIRED`，本轮未操作或验证 UI 上传。2026-11-05 的五份规范 UI 更新报告只保留其原适用范围。

## 固定 Git 提交与公开边界

Repository：`https://github.com/woobowen/Smart_Cities_and_Location_Services`；branch：`main`。本文件随成果提交；实际完整 local HEAD、remote SHA、固定链接与远程字节回读记录在发布后生成的外部交接材料 `REVIEW_PACKET.md` / `REMOTE_VERIFICATION.json`，避免在 Git 文件中嵌入其自身 SHA。审核时采用最终交接提供的固定 SHA，不用移动的 main 推定已审对象。

本轮只公开正式 PDF、必要源码、已被正式 PDF 引用的 PNG、历史 8 页稿及工程检查记录。原始视频未收到；完整入站 ZIP、解码原帧、未选截图与 OS 下载 metadata 留在仓库外私密目录。没有扩大既有 Foursquare 数据公开范围；没有执行研究、模型训练、Notebook 重算、图表重画或无关清理。

GPT 外审应实际读取固定远程 PDF、源码及上述回执，重点复核精确 PDF 身份、未变成果、源码适配、渲染限制、16 项清单及公开边界。内部接管通过、GitHub 同步、Upload Bundle Ready、UI 实际上传、GPT 外审、用户最终确认与教师提交分别判断；本记录不宣告 GPT 外审通过。
