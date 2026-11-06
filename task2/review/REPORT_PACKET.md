# 双报告与来源包

|成品|实际文件与构建|
|---|---|
|Experiment Report|[26页PDF](../reports/experiment/Experiment_Report.pdf)、[main.tex](../reports/experiment/main.tex)及chapters；方法/对照/结果/负例/思考题/局限|
|Process Report|[16 页正式 PDF](../reports/process/Process_Report.pdf)、[main.tex](../reports/process/main.tex)及任务章节、TikZ 和 18 个正式引用 PNG；接管用户认可的 GPT 成品，仅删除来源附录及目录项，PDF 保留指定 SHA 的原字节|
|当前配对源码|[来源与构建说明](../reports/process/README.md)；入站 ZIP SHA 为 `f73432ae…1c55a`，完整包及原帧私密保留，当前 `.tex`/正式引用截图已集成；源码编译/全文通过但严格渲染比较未全部通过|
|历史可编辑源包|[Dispatch_Reports_LaTeX_Source.zip](../releases/Dispatch_Reports_LaTeX_Source.zip)及[原回执](../evidence/report_source_package.json)仅保留原 26+8 页配对，不冒称当前 16 页源码包|
|构建|`../scripts/build_reports.py --kind process` 仅隔离编译、比较，不覆盖获批 PDF；既有 Experiment 构建与表/图源未改。依赖沿用 XeLaTeX/latexmk、Poppler、Fontconfig、Pillow、Noto CJK/DejaVu|
|真实检查|[当前规范升级与 12 项同步材料](../../evidence/infrastructure/SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md)、[独立接管核验](../evidence/process_report_sync_20261106/independent_review/REVIEW.md)与[16 页目视记录](../evidence/process_report_sync_20261106/page_review.json)；原 `report_build/` 和 `independent_report_review/` 保留旧版本真实范围|

源码范围是**报告编译**，不含原始签到。完整仓库还提供公开聚合重画与作者原数据获取后实验重算入口；三项分别验收。当前生成器已接入新版 Process 源码和正式引用素材，并对正式 PDF 增加不覆盖保护；本机重新生成存在明确记录的渲染差异，不能宣称重建 PDF 与获批 PDF 像素相同。

本轮已接管成品内的真实 UI 与作者既定箭头，不重新选择 Evidence、修改原话或自行授予 Lock。整篇用户认可、工程内部核验、Project Sources bundle、实际 UI 上传、GPT 二审与教师提交分别登记。既有 Experiment Report 与研究结果保持原身份；无重训或新实验。
