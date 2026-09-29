# SC-PROJECT-SOURCES-SYNC-003 · 唯一审阅入口

本轮只执行项目治理、已验收报告接管、分发及发布核验；新增记录级实验模型调用为0，不重跑参数/组合/四模式/确认/全量清洗。数值结果保留真实历史run与CODE_SHA。报告/包及SYNC-01—13已完成内部工程验证；SYNC-14工程提交发布和380项固定SHA远程字节回读均通过。

## 输入、范围与分发

- [批准Prompt](APPROVED_PROMPT.md)、[起始工作区/remote](starting-workspace.json)、[收到的完整release清单](received-release-inventory.json)。
- [7份核心输入核验](received-input-checks.json)及[原字节received快照](received/)；[5982项起始保护清单](starting-protection-inventory.json)。
- [7项OS下载元数据保留与迁移](metadata-relocation.json)：原字节base64、hash和本地隔离路径齐备，未删除有效文件。
- [P1—P4范围审核](governance/SCOPE_REVIEW.md)、[最小修订说明](governance/DOCUMENT_CHANGES.md)、[逐文档input→active diff](governance/input-to-active/)。
- 唯一分发定义：[sources.json](../chatgpt-project-source-sync/sources.json)；[生成manifest与最终hash](../chatgpt-project-source-sync/SOURCE_MANIFEST.md)；[差异上传说明](../chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md)。
- [UI Source差异](handoff/UI_SOURCE_DIFF.md)及[最小Settings补丁](handoff/PROJECT_SETTINGS_SCOPE_PATCH.md)。仅5份Markdown需再次替换，11项字节未变；UI动作由用户完成。

## 工程验证

- 同步器在原路径迁移，先校验所有输入、拒绝extra/不安全路径、受控写入并可回滚；`--check`只读且重复同步不改变mtime。
- [19项专项测试](sync/tests.xml)、[实际正向同步](sync/forward-sync.json)、[治理/链接/保护检查](governance/document-validation.json)。
- [Experiment源包检查](report/source-archive-check.json)、[干净编译结果](report/clean-build-result.json)、[依赖记录](report/environment-changes.json)。
- [报告集成总结与真实命令](report/REPORT_INTEGRATION.md)、[最终中文A—H交付说明](FINAL_RESPONSE.md)。
- [独立C初审](c_review/INITIAL_REVIEW.md)、[C独立编译](c_review/independent-build-result.json)、[C独立同步器测试](c_review/independent-sync-results.json)、[C元数据迁移复核](c_review/metadata-independent-checks.json)。
- [独立C最终审核](c_review/C_REVIEW.md)、[固定实物与结论](c_review/C_FINAL_RESULT.json)：INTERNAL_C_VERIFIED_FOR_REVIEWED_ARTIFACTS，未关闭工程Issue为0；内部C结论不替代网页GPT远程二审。

## 角色与边界

A为真实governance子上下文的范围核对；B由主线程、governance和report_integration按文件职责执行。C为未参与工程实现的独立子上下文，实读输入/active/bundle、另做干净编译与临时异常测试。作者目视与C抽查分别留痕，不互相冒称。

Process前期PDF/ZIP保持原件，保留[既有PARTIAL复现限制](../SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md)；task1 Process仍是独立待审稿。未制作新Evidence、未改变截图/框选/箭头、未重新Lock，未覆盖合成模板。

最终GPT真实远程二审仍为PENDING；UI_SCOPE_UPDATE为USER_ACTION_PENDING；实验一Submission仍为NOT_READY，未代发教师或代用户确认Understanding。

## 报告、包和验收矩阵

- [逐项验收矩阵 SYNC-01—14](ACCEPTANCE_MATRIX.json)：对象、实际动作、期望、结果、范围和证据逐项记录，SYNC-14已记录实际发布与回读；独立C记录中的PENDING_PUBLICATION保留其发布前时间范围。
- [正常入口第一次构建](report/normal-build-1/build_receipt.json)、[第二次构建](report/normal-build-2/build_receipt.json)及[第二次命令输出](report/normal-build-2-command.txt)均确认25页且Process不变。
- 作者逐页目视：[1—12页](report/visual-pages-01-12.md)、[13—18页](governance/report-pages-13-18-visual.json)、[19—25页](report/root-pages-19-25-visual.json)；[C独立抽查与观测绑定](c_review/visual-coverage-independent-check.json)。批准PDF与重建PDF不宣称字节/像素完全一致；文本逐字相同、布局已经实际查看。
- [当前具名REVIEW_ONLY包](../../../task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip)，SHA256 `231ce92475fdfe7ed12fa1c7e3304c22d6fd56ce39a0b53b43fee87103334a63`；[包回执](report/normal-build-2/package/package_build_receipt.json)及[C逐成员/隔离入口验证](c_review/independent-package-review.json)。116成员中，对旧当前包/旧实际FULL执行包均有112项完全相同；变化为manifest、README、REPORT_BUILD所在CLI文件、Experiment PDF。数值函数AST与32源身份独立核验，不能笼统声称所有运行文件字节未变。本轮未新增FULL复算。
- [报告专项测试](report/targeted-tests.txt)：17 tests + 10 subtests；[最终起始文件保护](protection-check.json)；[422条当前导航检查](current-navigation-links.json)；[发布文件扫描](publication-audit.json)。

正常报告编译不重画十幅图。两幅.drawio及SVG/PDF、绘图代码和冻结输入保留在[当前Experiment源](../../../task1/reports/experiment1/)；仅实际验证源包/可编辑结构/嵌图和编译，不声称完成全部绘图或全实验复算。新依赖仅隔离TeX包placeins 2.2、needspace 1.3e；无系统包、Python包、字体或全局配置新增。原安装stdout未独立落盘的限制明确记录，已补包元信息、sty hash与实际kpsewhich核验。

新包manifest的`metadata`完整继承旧实际FULL包，包含冻结`task1/config/assignment.json`的所有原字段及既有`evidence_master_spec_and_lock=NOT_AVAILABLE`。其中`report_revision_date=2026-09-28`与默认`review_package_name`是历史身份来源记录，不是当前Experiment修订日期或实际新ZIP名称；当前封面/章节源为2026-09-29，实际归档名称与hash以上述当前包及构建回执为准。冻结配置和Process原件保持不变。

## 实际发布

- 工程/产物提交：`87fc7db1ced9fd394d0cdda2113c5608205dce03`，Repository `woobowen/Smart_Cities_and_Location_Services`，Branch `main`。Local HEAD、origin/main和实际remote在回读时一致。
- [发布记录](PUBLICATION_RECORD.json)、[380个文件实际HTTPS raw字节/hash](publication-verification.json)、[push原输出](artifact-push.txt)、[回读原输出](artifact-remote-command.txt)。覆盖全部16项bundle、权威源、报告PDF/ZIP、实际源码、同步器、manifest、检查记录与当前导航，全部匹配。
- [TLS中断及有界重试](remote-retry-note.json)如实保留；成功回读后的冗余HEAD查询三次失败后已停止，未把失败说成成功，也未改变TLS、认证或全局配置。
- 承载本段的后续提交只整理交付记录，不改已验收工程、报告、bundle或包。为避免自引用，最终发布记录提交与实际远程SHA由最后聊天给出；本文件只引用已存在的工程提交与回读事实。

REPOSITORY_SYNC=VERIFIED；UPLOAD_BUNDLE=READY；EXPERIMENT_REPORT_INTEGRATION=VERIFIED。Process复现仍为PARTIAL，用户UI与网页GPT二审仍待后续动作，Submission仍为NOT_READY。
