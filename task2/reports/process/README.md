# 实验二 Process Report

当前正式成品为 [16 页 PDF](Process_Report.pdf)，SHA-256：

`c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f`

本轮接管用户已认可的 GPT 成品；批准的内容修订仅为删除末尾“A 视频证据的来源、裁切与复现”附录及其目录项。没有重新撰写、润色或重排其他内容。入站独立 resend PDF 的 SHA 不符；从 SHA 已核验的入站源包中取得了精确匹配上述 SHA 的 `task2/reports/process/main.pdf`，按原字节安装，未用重编译 PDF 覆盖。

配对入站 ZIP 的 SHA-256 为 `f73432aef93abdad0c37757df03b13811ab0beb1b508f700562bb0edada1c55a`。11 个任务 `.tex` 已接入，只有 3 处图片路径替换；18 个 PNG 与入站文件逐字节一致，并与正式 PDF 内嵌图像一一对应。公共 `../common.tex`、P2、既有图表及 Experiment Report 均未改动。详细证据见 [接管记录](../../evidence/process_report_sync_20261106/integration.json) 和 [独立核验](../../evidence/process_report_sync_20261106/independent_review/REVIEW.md)。

完整入站 ZIP、16 个解码原帧、未使用裁片、原始时间码及裁切记录留在仓库外的私密暂存区；未收到原视频。公开源码只包含正式 PDF 实际引用的截图。用户认可报告不自动批准公开其他来源材料，也不新增 Evidence Lock。

## 构建与已知复现限制

仓库根目录执行：

```bash
.venv/bin/python -B task2/scripts/build_reports.py --kind process \
  --evidence-dir task2/reports/process/build/recheck
```

依赖沿用已有 XeLaTeX/latexmk、Poppler、Fontconfig、Noto CJK、DejaVu 和 Pillow。本轮没有安装依赖或修改全局配置。构建仅对该进程生成临时 Fontconfig 配置，使 CJK 自动粗体使用获批 PDF 的 Bold，而非本机竞争的 Black 字重；不改 TeX 字体声明或系统字体。

实测 XeLaTeX 返回 0，16 页、全文一致、无检查出的引用/字形/溢出问题。但 200 dpi 逐像素比较仍有差异：1、6、15 页相同，其他 13 页不完全相同。因此上述严格验证命令返回非零，不能记为整个验证通过。正式 PDF 始终保留获批字节。见 [首次比较](../../evidence/process_report_sync_20261106/installed_build/process_verification.json)、[字重修复后比较](../../evidence/process_report_sync_20261106/installed_build_fontfix/process_verification.json) 和 [独立差异测量](../../evidence/process_report_sync_20261106/independent_review/fontfix_render_measurements.json)。

原 [8 页技术交接稿](history/20261105_8page_handoff/Process_Report_Technical_Handoff_20261105_8p.pdf) 与原 `task2/releases/Dispatch_Reports_LaTeX_Source.zip` 保留历史配对身份，不能宣称旧包可重建当前正式报告。当前对外交接见 [GPT 外审材料](../../../evidence/infrastructure/SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md)，当前 Project Source 规范名为 `Experiment2_Process_Report.pdf`；此前 [16 项中间方案](../../review/PROCESS_REPORT_SYNC_20261106.md)保留原检查范围。
