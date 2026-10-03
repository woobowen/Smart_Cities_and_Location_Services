# 完整 Process Report：第76页授权修正版

当前唯一工作源是 [source/main.tex](source/main.tex)，静态正文为 [source/chapters/pages.tex](source/chapters/pages.tex)，规格为 [evidence_units.json](source/content/evidence_units.json) 和 [diagrams.json](source/content/diagrams.json)。整个工作源由批准ZIP逐成员校验后接入。不要手改生成TeX来绕过真正生成器。

- [当前PDF](../../../reports/process-report/experiment1-revised/Process_Report_Revised.pdf) / [配对ZIP](../../../reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip)：保持2026-10-03用户交接原字节；承接此前全文验收，第76页按本轮明确授权修正，本次新PDF逐页用户复核另记。根目录用户输入仍保留。
- [兼容阅读PDF](process1.pdf)：保持批准原字节；构建输出另存工程证据，不覆盖批准件。
- [当前收尾任务](../../../evidence/infrastructure/SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001/REVIEW_PACKET.md)：两条实际构建、135裁片、逐页比较、同环境旧构建、独立审查及真实教师包终检。
- [旧批准PDF/ZIP](../../../reports/process-report/experiment1-revised/history/accepted-20261002/)及[上轮审核](../../../evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/REVIEW_PACKET.md)按原范围保护。
- [历史12页草稿](history/technical-draft-12p/)及[历史PreTask](../../../reports/process-report/pre-task1/)保留原来源，不作为当前构建输入。旧脚本输出的 `*_generated.tex` 是历史链，当前生成器只读取 `source/`。

运行仓库统一入口见 [上级README](../README.md)。在已准备好报告局部Python依赖、指定字体和TeX宏包的源根中，原始直接入口是 `bash compile.sh`；完整链依次为 `python tools/make_diagrams.py`、`python tools/build_report.py`、`bash compile.sh`、`python tools/render_review.py`、`python tools/audit_report.py`、`python tools/check_p76_closeout.py`。第76页规格见[source/content/closing_evidence.json](source/content/closing_evidence.json)。397个工作源文件逐一保持输入ZIP字节；统一适配层只在隔离副本构建，输出另存工程证据。

公共P2色值唯一可编辑源为 `templates/latex/common/p2_cloud_sorbet_colors.tex`。包内颜色定义保留受控便携副本身份，由构建检查映射，不能自由形成第二套配色。文稿验收、工程复现、内部独立审查、逐条Evidence Lock、Understanding和教师Submission分别记录；接管不补造历史签署。

为保留旧审核记录中的源文件链接，根目录原 `process1.tex`、`*_generated.tex` 和 `components/` 仍保留历史原字节；它们已退出当前构建，不能直接用于新版报告。历史快照目录用于固定旧PDF配对，当前唯一主源仍为 `source/main.tex`。
