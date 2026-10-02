# 实验一 Goal 3 当前成果入口

## 2026-10-02 当前 Process 接管

用户已验收77页完整Process；本轮接入真实工作源、两条报告构建及当前PDF/打包路径。新增工程核验与范围见 [SC-LAB1-PROCESS-INTEGRATION-SYNC-001](../../../evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/REVIEW_PACKET.md)。网页GPT本轮二审=PENDING，Submission=NOT_READY；不升级逐条Evidence Lock或Understanding。Experiment成品及科学结果保持此前验收范围。

当前 [Process PDF](../../reports/process1/process1.pdf) / [唯一工作源](../../reports/process1/source/main.tex)；[旧12页稿](../../reports/process1/history/technical-draft-12p/process1.pdf)及PreTask均保留历史身份。新的审阅包以本轮REVIEW_PACKET列出的具名文件为准，旧包不覆盖。

以下为原版本交接全文，保留其当时的“当前”、委派状态和旧路径；历史路径应结合对应固定提交读取，不代表本轮检查或未完成项。

---

## 当前状态：非Process范围收尾

当前Experiment为用户已验收的**25页重构版**。用户已确认本对话复盘与该文稿；[SYNC-003网页GPT二审接收记录](../../../evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review/REVIEW_RECEIPT.md)承接被审`89371f6597f92f7dac9abf61f6f6b18e29ed76cc`的范围通过，当前来源为用户转交，原审核附件尚未入库。原18项测试/16项依赖恢复/报告编译是历史检查，不是本轮新运行。

本轮[SC-LAB1-NONPROCESS-CLOSEOUT-001](../../../evidence/infrastructure/SC-LAB1-NONPROCESS-CLOSEOUT-001/REVIEW_PACKET.md)只做治理同步、范围收尾与技术交接。NC验收后非Process任务可以独立关闭；本轮新提交仍为`CURRENT_CHANGE_GPT_REVIEW=PENDING`。技术处理、规定实验、有限候选比较、最终确认及全量结果保留原验收范围，不重新评为全局最优。

- [当前Experiment PDF](../../reports/experiment1/experiment1.pdf) · [权威章节源](../../reports/experiment1/Experiment_Report.tex) · [构建说明](../../reports/README.md)。批准原PDF/源ZIP及生成器保持，本轮不重编、不重画。
- Process交由用户指定的另一对话，状态`DELEGATED_NOT_COMPLETED`；[原12页待审稿](../../reports/process1/process1.pdf)、源及[Interaction Handoff](../../docs/goal3/INTERACTION_HANDOFF.md)不改。前期31页源复现保持PARTIAL，Evidence规格和Lock由指定责任方处理。
- [当前完整审阅包](../../submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip)仍为`REVIEW_ONLY` / `NOT_READY`。待最终Process到位，再合并、核验和取得用户提交确认；本轮不重打包。
- [技术交接](../../docs/goal3/TECHNICAL_HANDOFF.md)提供冻结合同、数值CODE_SHA、现有构建/复算命令和历史证据。原始CRS未知、无噪声真值等限制保留；[教师定位](teacher_delivery_mapping.md)及两个Notebook未变。

整体Deliverable=`FINAL_REVIEW`；Understanding保留原`LEARNING`，不由本轮同步自动转为PASS。没有新增Evidence Lock、VIVA签署或教师提交。本轮实验模型调用/研究数值运行均为0；下面历史正文及其当时PENDING按原字节保留，不与当前范围状态混写。

---

## 历史：SC-LAB1-G3-CLOSEOUT-001 收尾审阅记录

以下正文原样保留，文中的“本次/当前”均指当时22+12页、旧具名ZIP和旧发布提交；其中的构建/目视/FULL检查不冒称针对后来导入的25页报告。旧PDF版本可由Git基线 `4483f520eabb5358d1f35cf5c33a81d3b01e47e0` 回读。原导航包含可变工作路径时，以此版本限定其历史事实。

# 历史收尾记录正文

本次任务：`SC-LAB1-G3-CLOSEOUT-001`，承接 `SC-LAB1-G3-FINAL-001`。这是实验一 Goal 3 的交付收尾，未新增 Goal 4 或重新搜索研究方案。旧交付锚点为 `1a5e26b43189aef64a46f8986b3cc442fa50d2c5`；其历史回执只沿用原核验范围。

身份 **吴博闻 / 字符串 10245102410** 已写入唯一元数据源、生成器、两份报告、Notebook 及新待审包，并通过重建回归，`IDENTITY_PENDING` 已关闭。2026-09-28 是报告修订日期，原实验与冻结时间不变。当前两报告为 **22 + 12 页**，C 已对当前全部 34 页真实逐页查看；关键数值与旧产物一致。当前两个Notebook在仓库和同一ZIP解压目录各一次新内核FULL均已完成并由C核验（12/8/12/8代码单元），新增记录级模型调用0；旧四次FULL仍仅作历史。

**当前可自主工程与真实发布均已完成，整体PARTIAL_BLOCKED仅保留正式互动Evidence外部缺项。** [CL01—CL16状态](closeout/SC-LAB1-G3-CLOSEOUT-001/ACCEPTANCE_MATRIX.md)、[完整回复](closeout/SC-LAB1-G3-CLOSEOUT-001/FINAL_RESPONSE.md)和实际发布记录统一从本次收尾目录读取。真实互动原件、Evidence Master 批准的呈现规格与 Lock 仍未齐备；本轮不将技术事实送审稿称为完整正式 Process Evidence，也不替用户签理解验收或发送教师。

## 1. 深入讲解与审核入口

1. [四块 REVIEW_GUIDE](../../docs/goal3/REVIEW_GUIDE.md)：任务与要求 → 数据处理与评价 → 系统、实验与循环 → 正式成果与收尾；其中问题供随后讲解，用户尚未逐项验收。
2. [唯一父要求登记](requirements.json) → [65 项要求与质量证据对账](closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md) / [JSON](closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.json)。总账是 G1/G2/G3/TD 的交叉索引，不是另一套最终 PASS 表。
3. [教学差异](closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/TEACHING_DIFFERENCES.md)与[文献实际使用](closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/literature_use_map.md)：教师示例、获批调整、已读/采用/试验/事后对应分别注明。
4. [教师交付定位](teacher_delivery_mapping.md)：当前 stable cell ID、source hash、PDF 物理页码和 anchor；[Technical Handoff](../../docs/goal3/TECHNICAL_HANDOFF.md) / [Interaction Handoff](../../docs/goal3/INTERACTION_HANDOFF.md)分别交接技术事实与真实互动来源。
5. [Experiment PDF](../../reports/experiment1/experiment1.pdf) / [XeLaTeX](../../reports/experiment1/experiment1.tex)；[Process PDF](../../reports/process1/process1.pdf) / [XeLaTeX](../../reports/process1/process1.tex)。过程报告保持明确待补的送审身份。
6. [当前报告构建清单](report_build/build_receipt.json)绑定两 PDF、源文件、分页文本与全部 200dpi 页图；[Experiment 分页文本](report_build/experiment1_pages.txt)、[Process 分页文本](report_build/process1_pages.txt)、[Experiment 页图](report_build/render200/experiment1/)、[Process 页图](report_build/render200/process1/)，可直接逐页检查；[C 当前全文与视觉回执](closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/visual_content_receipt.json)限定实际已查范围。
7. [新待审 ZIP](../../submission/REVIEW_ONLY_10245102410_吴博闻_实验一.zip)与[包验证/字节等价证据](closeout/SC-LAB1-G3-CLOSEOUT-001/PACKAGE_VALIDATION.json)。包为 REVIEW_ONLY / NOT_READY；只在后续用户确认后才考虑教师候选名 `10245102410_吴博闻_实验一.zip`。

## 2. 当前有效实验与结果

[current_runs.json](current_runs.json) 只指向有效的开发、选择、最终确认和全量生产。[result_summary.json](result_summary.json) 按实际原件/合同/分区/源码/独立回执哈希生成；完整原始点终态在全量 run 的 285 个确定性压缩分片内，可由完成版 Notebook 从 raw 重算。

| 阶段 | 实际范围与身份 | 核心结果 | 独立闭合 |
|---|---|---|---|
| 开发 | 240 条已暴露记录 | S0 增加 6,704 点覆盖；S0_G0 相对 S0 有 41 条几何改善，父项/移除/负结果保留 | [开发](independent_c/development_closure_receipt.json) |
| 选择 | 240 条预登记选择记录 | S0 全保护、103 条覆盖改善；G0/组合在同样 3 条记录退化，选择 S0 | [选择](independent_c/selection_closure_receipt.json) |
| 最终确认 | 冻结后一次运行 600 条、62,284 点 | S0 全保护、349 条覆盖改善；共同覆盖 35,868→62,220，存储点 10,991→12,114 | [确认](independent_c/confirmation_closure_receipt.json) |
| 全量生产 | 全部 11,386 条、1,173,410 点，包含开发记录 | R0/S0 22,772 次真实处理；共同覆盖 671,899→1,172,211，存储点 200,470→221,149；0 处理失败/0 逐记录回退 | [全量](independent_c/production_closure_receipt.json) |

最终策略为统一确定性 **S-D-P：30 / 400 / 2 / 0 / 35 / 5**，参数顺序为 `dt / distance / min_points / min_length / direction / dp`。R0 的 `min_points/min_length=5/65`，其余相同。最终记录级处理新增模型调用为 0；治理 A/B/C 的实际调用另计，隐藏后端请求与费用保持 unknown。

选择、确认与生产数值 CODE_SHA：`e12f8a27944210adb452730be92a0674dfc6b84b`。后续报告、图和 Notebook 兼容性修复没有改写这些数值运行的代码身份。历史数值 ARTIFACT_SHA 为 `fd559e451291b9d424682853ef0909aa5eb94b32`；[历史发布记录](PUBLICATION_RECORD.json) 保留当时核对。本次文档构建代码为 `3912f4da2a21ea9da26f75acb6434d889e480462`，包内容身份见本次 [PACKAGE_VALIDATION.json](closeout/SC-LAB1-G3-CLOSEOUT-001/PACKAGE_VALIDATION.json)。本次核心交付 ARTIFACT_SHA=`029aa30bfb00253173de8284468f8964e5e17ce3`，已正常push并由主线程和独立C分别回读10个固定SHA关键文件。[本次发布回执](closeout/SC-LAB1-G3-CLOSEOUT-001/PUBLICATION_RECORD.json)明确已发生的远程一致；随后仅记录metadata，不用文档HEAD改写数值CODE_SHA。

## 3. 不能省略的限制与负结果

- `source_crs=UNVERIFIED`。固定椭球/h=0/ENU 是批准的条件化数学模型；PROJ 一致与敏感性检查不认证源 datum。
- 共同覆盖不是最终存储点数；没有噪声真值，不能声称清洗准确率提高。全量统计是本数据集产出描述，不是第二次独立测试。
- 最差新增覆盖点为 record 352 / index 105，偏差 **266.016754 工作米**。其四点原窗口被 R0 因点数不足过滤；S0 经过 D 后删除该点，局部 P 没有再删点。[独立边界核验](independent_c/new_coverage_boundary_receipt.json) 与[全量过滤原因](independent_c/full_filter_attribution_receipt.json) 单列此限制。
- D60、P2/P10、条件方向组合的失败及不采用原因均保留。[收敛复盘](CONVERGENCE_REVIEW.md) 解释有限预算下停止；没有预定最复杂方案或 S0 必胜。
- 全量 22,772 份实际轨迹通过外部 raw oracle；独立 Decimal/PROJ 重算为随机/类别合并 50 条记录、100 份轨迹。独立阶段坐标敏感性覆盖 56 条、112 份，不冒称全部记录的第二次数学实现重算。

## 4. 本次收尾、复现与外部边界

[当前授权摘录及边界](closeout/SC-LAB1-G3-CLOSEOUT-001/AUTHORIZATION.md)明确是本次用户授权与归并索引，并非补造完整历史聊天。[原 Goal 3 Prompt](USER_PROMPT.md)、[旧最终回复](FINAL_RESPONSE.md)和[旧发布记录](PUBLICATION_RECORD.json)保留当时事实；旧“身份未提供”、旧 21/12 页与旧 ZIP 只属于当时版本。

本次 A 为 `/root/a_requirements`，B 文档协作为 `/root/b_review_guide`，主线程实际编辑、构建、复现与修复；C 为只读检查主体的 `/root/c_independent`。 [goal_state.json](goal_state.json)记录真实问题—修复—复验—父任务恢复。当前包状态、引用访问层级、导航链接、过程报告措辞与执行成本表均已实际修正；C 逐项回执在 [c_review](closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/)。

本轮新增实验记录级模型调用为 0；没有重跑历史 84 次模型调用。Notebook 使用历史真实提议做 FULL 离线复算，实际结果在[本次 Notebook 记录](closeout/SC-LAB1-G3-CLOSEOUT-001/notebooks/)。两次进程中断的部分输出明确保存在[中断记录](closeout/SC-LAB1-G3-CLOSEOUT-001/notebook_interruptions.json)，不计入 FULL 成功；新内核重试另用新目录。最终报告排版修订只改变包内 Experiment PDF 和 manifest，**113 个非 PDF payload 成员完全相同，Process PDF 也未变**；通过此关系继承对应实际解压执行证据，不能称为又一次新执行。

[Evidence 盘点](closeout/SC-LAB1-G3-CLOSEOUT-001/b_handoff/evidence_inventory.md)检查了授权工作区现有原件与候选。可用授权文字和历史模型/工程事实已索引；未找到完整原生互动截图/上下文及其获批入选、annotation、Report Order、Evidence/Block Lock。缺项只阻断相关正式互动呈现，姓名不再是依赖。PDF 页图是报告检查产物，不是原生聊天截图。

Deliverable 保持 `FINAL_REVIEW`，Understanding 保持 `LEARNING`，Submission 保持 `NOT_READY`，新 `GPT_SECOND_REVIEW=PENDING`。老师材料第26页规定“10月5日前”、学号_姓名_实验一命名和邮箱；本轮没有代发邮件、上传教学平台、代签或设为 SUBMITTED。
