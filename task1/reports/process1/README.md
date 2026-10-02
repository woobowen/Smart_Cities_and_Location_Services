# 已验收完整 Process Report

当前唯一工作源是 [source/main.tex](source/main.tex)，静态正文为 [source/chapters/pages.tex](source/chapters/pages.tex)，规格为 [evidence_units.json](source/content/evidence_units.json) 和 [diagrams.json](source/content/diagrams.json)。整个工作源由批准ZIP逐成员校验后接入。不要手改生成TeX来绕过真正生成器。

- [批准PDF](../../../reports/process-report/experiment1-revised/Process_Report_Revised.pdf) / [批准ZIP](../../../reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip)：不可变、用户已验收；根目录用户输入仍保留。
- [兼容阅读PDF](process1.pdf)：保持批准原字节；构建输出另存工程证据，不覆盖批准件。
- [接管任务](../../../evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/REVIEW_PACKET.md)：实际两路线、逐页比较、环境与独立审查。
- [历史12页草稿](history/technical-draft-12p/)及[历史PreTask](../../../reports/process-report/pre-task1/)保留原来源，不作为当前构建输入。旧脚本输出的 `*_generated.tex` 是历史链，当前生成器只读取 `source/`。

运行仓库统一入口见 [上级README](../README.md)。在已准备好报告局部Python依赖、指定字体和TeX宏包的源根中，原始直接入口是 `bash compile.sh`；完整链依次为 `python tools/make_diagrams.py`、`python tools/build_report.py`、`bash compile.sh`、`python tools/render_review.py`、`python tools/audit_report.py`。统一适配层在隔离副本执行这些入口，并管理局部依赖；不要在不可变参考目录运行。

公共P2色值唯一可编辑源为 `templates/latex/common/p2_cloud_sorbet_colors.tex`。包内颜色定义保留受控便携副本身份，由构建检查映射，不能自由形成第二套配色。文稿验收、工程复现、内部独立审查、逐条Evidence Lock、Understanding和教师Submission分别记录；接管不补造历史签署。

为保留旧审核记录中的源文件链接，根目录原 `process1.tex`、`*_generated.tex` 和 `components/` 仍保留历史原字节；它们已退出当前构建，不能直接用于新版报告。历史快照目录用于固定旧PDF配对，当前唯一主源仍为 `source/main.tex`。
