# SC-LAB1-G3-CLOSEOUT-001 收尾验收矩阵

此表是当前 Prompt 的 CL 验收记录；父要求仍由 `task1/evidence/goal3/requirements.json` 统一登记。PASS 只限所写工程范围，不代表用户理解、Evidence Lock、网页 GPT 最终验收或作业提交。

| ID | 对象 | 状态 | 实际范围、命令/动作和结果 | 证据 | 剩余动作 |
|---|---|---|---|---|---|
| CL01 | 工作区与冻结边界 | PASS | main承接1a5e26b；原件/旧run/用户ZIP保护；32数值源未改；ls -la、git状态/远端核对；C check_frozen_and_identity.py；7启动保护文件、32数值源、132合同绑定一致 | [startup.json](startup.json)<br>[frozen_identity_receipt.json](c_review/frozen_identity_receipt.json) | 无；启动7项保护文件与原有用户ZIP当前仍一致 |
| CL02 | 身份完整同步 | PASS | 唯一assignment.json → metadata/两报告PDF/Notebook/ZIP；学号字符串；两次REPORT_BUILD；重复metadata生成；pytest identity/package回归；吴博闻/10245102410一致；12测试+10子测试；历史身份缺项未倒写 | [identity_package_retest.xml](identity_package_retest.xml)<br>[frozen_identity_receipt.json](c_review/frozen_identity_receipt.json)<br>[PACKAGE_VALIDATION.json](PACKAGE_VALIDATION.json) | 无身份外部缺项 |
| CL03 | 教师T1/T2覆盖 | PASS | 13项T1与8项T2实际入口、来源、数值与边界；C check_review_snapshot.py、check_review_maps.py及实际全项内容核读；65项含全部13T1/8T2与44U，C逐项读来源/做法/状态/限制并核教师PPT指定原页；311函数、386cells、676当前PDF页锚点与2073链接核验通过。 | [requirements_literature_receipt.json](c_review/requirements_literature_receipt.json)<br>[review_input_snapshot_receipt.json](c_review/review_input_snapshot_receipt.json) | 用户/网页GPT随后深入审核；T1-12正式互动外部缺项保留 |
| CL04 | 用户U01—U44对账 | PASS | 44项归并索引，不伪称逐字聊天；授权演变/剩余限制分开；C check_review_snapshot.py、check_review_maps.py及实际全项内容核读；U01—U44全部核对来源类型、授权演变、可证明与不能证明内容；真实送审快照和20条历史验收原样性通过C。 | [requirements_literature_receipt.json](c_review/requirements_literature_receipt.json)<br>[review_input_snapshot_receipt.json](c_review/review_input_snapshot_receipt.json) | 用户/网页GPT随后深入审核；T1-12正式互动外部缺项保留 |
| CL05 | 教学差异和文献使用 | PASS | 7类教学差异，28源阅读/采用/试验/事后对应；C check_review_snapshot.py、check_review_maps.py及实际全项内容核读；7项教学差异逐项核对；26归档源题录/访问层级加2官方转换文档，不倒推论文影响，不补造regret或28篇全文阅读。 | [requirements_literature_receipt.json](c_review/requirements_literature_receipt.json)<br>[review_input_snapshot_receipt.json](c_review/review_input_snapshot_receipt.json) | 用户/网页GPT随后深入审核；T1-12正式互动外部缺项保留 |
| CL06 | 科学表述 | PASS | 冻结S0/D2/ENU、分母、共同覆盖/P输入保证、负结果和record352边界；C check_report_numbers.py；与1a5e26b result_summary深比较；10组表数字对原件；50位Decimal重算266.016754425…；summary仅/at变化 | [report_numbers_receipt.json](c_review/report_numbers_receipt.json)<br>[result_summary_equivalence.json](c_review/result_summary_equivalence.json) | 无研究变更；来源CRS仍UNVERIFIED |
| CL07 | Experiment Report | PASS | 22页当前正文、引用、教学差异、图表及正式身份；XeLaTeX编译；当前C全文和逐页目视；表14间距修复重建；无未解决编译诊断；正文数字和限制通过限定范围核验 | [visual_content_receipt.json](c_review/visual_content_receipt.json)<br>[CL-C02_closure.json](c_review/CL-C02_closure.json) | 新网页GPT最终文档验收PENDING |
| CL08 | Process真实性与权限 | BLOCKED | 12页技术事实送审稿已精修；Part I/II保留；身份已同步；授权工作区原件/spec/Lock盘点；C全文逐页检查；可做工程通过；真实完整互动原件、批准spec和Evidence/Block Lock未齐 | [evidence_inventory.json](b_handoff/evidence_inventory.json)<br>[visual_content_receipt.json](c_review/visual_content_receipt.json) | Evidence Master提供对应真实原件/批准呈现spec并按协议审核Lock；不自行补造 |
| CL09 | PDF实际视觉验收 | PASS | 当前22+12全部34页200dpi；变动2页重看，共36次页视；C tools.view_image(detail=original)，逐页实际检查；哈希绑定当前PDF/文本/页图；无缺字、裁切或表14数字连读；源截图分辨率未伪装提高 | [visual_content_receipt.json](c_review/visual_content_receipt.json) | 页面内容再变更则重新审受影响页 |
| CL10 | Notebook与复现 | PASS | 仓库与同一实际解压包各basic/system新内核FULL；默认0模型调用；execute_notebook 仓库/同一解压目录各两本；C查实际cell输出、注册表和新分片；Journal.accept notebooks；4次新内核FULL：12/8/12/8代码单元；2次各285生产分片和全部原始点独立核对；记录级Provider尝试0。 | [notebook_runs_receipt.json](c_review/notebook_runs_receipt.json)<br>[notebooks_task_receipt.json](c_review/notebooks_task_receipt.json)<br>[package_execution_equivalence.json](c_review/package_execution_equivalence.json) | 无；报告修订包继承同字节运行闭包证据，未冒称再次执行 |
| CL11 | 提交包 | PASS | 当前116成员；安全路径/CRC/身份/PDF/完整依赖已核；C成员/CRC/路径/身份/当前PDF/完整闭包及新内核FULL；Journal.accept package；当前116成员、15,776,719bytes，新ZIP真实构建/静态解压/两本隔离FULL和113非PDFpayload等价证据齐全；工程已C接受。 | [PACKAGE_VALIDATION.json](PACKAGE_VALIDATION.json)<br>[package_task_receipt.json](c_review/package_task_receipt.json)<br>[package_execution_equivalence.json](c_review/package_execution_equivalence.json) | 包保持REVIEW_ONLY/NOT_READY；正式互动Evidence和最终用户/网页审核未闭合 |
| CL12 | 复盘指南与Handoff | PASS | 4块/13理解问题、两份Handoff、当前Notebook/PDF/图源定位；C check_handoffs_task.py及真实全文阅读；Journal.accept handoffs；21targets/134sources，22TD当前cell/PDF定位、34页text/render绑定通过；四块13理解问题不预设用户通过。 | [handoffs_task_receipt.json](c_review/handoffs_task_receipt.json)<br>[guide_interaction_receipt.json](c_review/guide_interaction_receipt.json) | 后续用户与网页GPT实际深入讲解/审核 |
| CL13 | 持续内部修复 | PASS | 普通包状态、引用、链接、措辞、表格已修；两次中断的同源新内核重试已独立闭合并恢复父任务；真实issue→修复/同源重试→回归/重建→独立C→Journal.close_issue；CL-C01/02/03均独立闭合并恢复父任务；辅助送审schema错误最小修复后真实提交成功且C核实。 | [CL-C01_closure.json](c_review/CL-C01_closure.json)<br>[CL-C02_closure.json](c_review/CL-C02_closure.json)<br>[CL-C03_closure.json](c_review/CL-C03_closure.json)<br>[controller_submission_repair.json](controller_submission_repair.json)<br>[notebooks_task_receipt.json](c_review/notebooks_task_receipt.json) | 无普通工程阻碍；SIGTERM发起原因unknown保留，不假称数学修复 |
| CL14 | 当前版本一致 | PASS | 源码/报告/图/文本/包/导航分开绑定；数值CODE_SHA不改；当前六项叶任务的C回执与Journal.current检查；不可变治理快照及包内容等价绑定；源码/冻结结果/报告/34页图/两Notebook/116成员包/TD导航均绑定当前有效内容；旧回执与新执行范围分开。 | [handoffs_task_receipt.json](c_review/handoffs_task_receipt.json)<br>[notebooks_task_receipt.json](c_review/notebooks_task_receipt.json)<br>[package_task_receipt.json](c_review/package_task_receipt.json)<br>[review_input_snapshot_receipt.json](c_review/review_input_snapshot_receipt.json) | 最终实际发布SHA由CL16单列；不预造文件自身SHA |
| CL15 | 安全与范围 | PASS | 无新调参、外部数据、LIVE；不发教师、不分发字体/论文全文；完整当前task1变更预检、C包安全路径/成员核验、11-file --check、当前导航检查、diff空白分类；294个变更/新增文件无凭据/大文件/越界；2396本地链接通过；未打包字体/私密材料，未发教师，未改变source_crs及标准。 | [PREFLIGHT.json](PREFLIGHT.json)<br>[CURRENT_LINKS.json](CURRENT_LINKS.json)<br>[WHITESPACE_CHECK.json](WHITESPACE_CHECK.json)<br>[package_receipt.json](c_review/package_receipt.json)<br>[upload_bundle_receipt.json](c_review/upload_bundle_receipt.json) | 仅正式Evidence与用户/网页审核；无新增安装或持久环境配置 |
| CL16 | 发布 | NOT_RUN | 内部实际范围验收后发布准确PARTIAL_BLOCKED待审点；预检main实际远端仍1a5e26b；尚未push；没有提前签远程一致或最终PASS |  | 内部验收后push main并固定SHA回读 |

独立状态：

- Identity：`VERIFIED`。
- Closeout Engineering：`PARTIAL_BLOCKED; INTERNAL_EXECUTABLE_SCOPE_VERIFIED; PUBLICATION_PENDING`。
- Process Evidence：`BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK`。
- Deliverable：`FINAL_REVIEW`。
- Understanding：`LEARNING`。
- Submission：`NOT_READY`。
- New GPT_SECOND_REVIEW：`PENDING`。

环境新增：系统包、语言包、工具链、字体及持久环境配置均为 0。

本轮新增记录级实验模型调用为 0。治理 A/B/C 为真实上下文协作；底层模型请求数和费用不可观察，保持 unknown。
