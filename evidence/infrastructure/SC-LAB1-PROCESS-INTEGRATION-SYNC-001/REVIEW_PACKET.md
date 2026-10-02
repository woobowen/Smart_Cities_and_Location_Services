# SC-LAB1-PROCESS-INTEGRATION-SYNC-001

本轮为一次性工程接管与同步，不是新研究Goal。用户已验收完整Process文稿；网页GPT工程二审=`PENDING`，逐条Evidence Lock/Understanding/教师Submission不由本轮升级。开始SHA：`6527945ad8e526fa606b2c09835f2e51291fa4d0`，分支main。

当前状态：**Engineering PASS**。报告源/项目源接入、统一构建、内部独立核验及真实远程发布回读通过。被审内容提交：`e1fb621aa40acc167f4ed84c0c7992a5ff0a4abe`；[发布回执](PUBLICATION_RECEIPT.json)记录从全新独立Git对象库取得的真实远程字节，15成员及30个active/release路径实例全部同用户基准。内容提交后仅追加本轮回执/交接记录，并修复验证辅助脚本复用浅克隆时的本地ref更新；报告、同步生产代码和release保持内容提交版本。[修复实测](REMOTE_CHECK_HELPER_FIX.json)、[追加独立核验](REMOTE_CHECK_HELPER_REVIEW.md)，最终HEAD见对话回报。网页GPT二审PENDING。

## 精确输入与成果

- [独立输入基准](approved_input_sha256.txt)、[重新计算结果](input_hash_checks.json)、[传输映射](transfer_map.json)、[完整初始盘点](initial_inventory.json)。15项基准全部匹配，四份规范原文受控反向导入后恢复单向分发。
- [批准Process PDF](../../../reports/process-report/experiment1-revised/Process_Report_Revised.pdf) / [批准ZIP](../../../reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip)：原始hash为45f3b86f…与00cb7b641…。根目录用户原件仍保留。
- [当前阅读PDF](../../../task1/reports/process1/process1.pdf)、[唯一主源](../../../task1/reports/process1/source/main.tex)、[规格](../../../task1/reports/process1/source/content/evidence_units.json)、[六图规格](../../../task1/reports/process1/source/content/diagrams.json)、[构建入口](../../../task1/reports/build_reports.py)。工作源343成员逐hash保留批准原字节，适配发生在包外。
- [Experiment批准件](../../../reports/experiment-report/experiment1-reconstructed/)、[当前双报告导航](../../../task1/reports/README.md)。科学成果、原始数据、冻结规则和旧运行保持原身份。
- [旧12页草稿](../../../task1/reports/process1/history/technical-draft-12p/) / [历史PreTask](../../../reports/process-report/pre-task1/)。旧检查PENDING/PARTIAL仍对应旧输入。
- [显式source清单](../chatgpt-project-source-sync/sources.json)、[release](../../../releases/chatgpt-project-sources/)、[当前UI差异](source_sync_checks.md)。批准15项全部同基准，用户报告UI已更新，本次无需再次上传。

## 构建与工程检查

静态路线A在新隔离副本运行 `bash compile.sh`；完整路线B依次执行 `python tools/make_diagrams.py`、`python tools/build_report.py`、`bash compile.sh`、`python tools/render_review.py`、`python tools/audit_report.py`。所有操作仅为报告图/页面重建；没有参数搜索、全量轨迹处理或新模型调用。

原件中预置主PDF/build先移除，保留图PDF；两次XeLaTeX、输出hash、环境及真实日志见 [build_checks](build_checks/)。局部报告Python依赖、Noto Sans及ragged2e按实际缺项补齐，科学numpy/Pillow未升级。原先字体字重选择差异通过报告进程专用fontconfig修复，无报告文字/规格修改。

完整[构建与目视记录](build_and_visual_checks.md)、[最终中文回报](FINAL_RESPONSE.md)和[独立内部结论](INTERNAL_REVIEW.md)供审核读取。

最终两路线均77页，逐页文本包含空白完全一致；同PyMuPDF 1.26.7在200dpi比较，71页像素完全相等，其余6幅图所在页只有极小栅格差异。逐页实看范围与最终记录分别由构建实施者和独立审查上下文登记；不把原包作者audit重放当独立审核。

同步器37项隔离用例和真实目录plan/check/两次sync见 [同步检查](source_sync_checks.md)，独立复验见 [INTERNAL_REVIEW](INTERNAL_REVIEW.md)。另19项报告集成回归通过，6071个受保护既有文件字节未变。所有真实release成员与独立Prompt基准匹配。

## 复现入口

在仓库根目录，用已有环境（依赖说明见报告README）：

```bash
.venv/bin/python task1/reports/build_reports.py --report process --render --evidence-output /tmp/sc-process-static
.venv/bin/python task1/reports/build_reports.py --report process --regenerate --render --evidence-output /tmp/sc-process-full
.venv/bin/python -m task1.goal3 REPORT_BUILD --output /tmp/REVIEW_ONLY_实验一_双报告.zip --evidence-output /tmp/sc-review-build
.venv/bin/python evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
```

报告构建输出目录和REVIEW_ONLY包选新路径。已有包不覆盖。批准PDF是当前阅读/打包件，真实重建PDF单独留作工程证据，不能声称与批准件hash相等。

## 保留边界与审核身份

[变更与保护边界](change_and_preservation.md)记录私密快照、原件保护、确切移出授权及用户未提交输入。仓库外快照和全页200dpi渲染不进入release；仓库保留实际检查、必要差异页及新构建PDF。

- 文稿：用户在本轮Prompt已验收，绑定批准PDF/ZIP hash。
- 工程制作与自检：root主线程、process_build与source_sync真实分工。
- 内部独立检查：独立只读上下文independent_review，范围、发现及复验单独记录。
- Evidence：沿用真实原件/spec及明确APPROVED_NATIVE_WIDTH；不补造逐条Lock。
- 网页GPT工程二审：PENDING，等待真实远程读取。
- 教师提交：NOT_READY；没有发送邮件、代交作业或修改教师端。
