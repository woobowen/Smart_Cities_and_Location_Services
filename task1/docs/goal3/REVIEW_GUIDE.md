# 实验一四块复盘指南

Task：`SC-LAB1-G3-CLOSEOUT-001`；Parent Goal：`SC-LAB1-G3-FINAL-001`。本指南用于工程收尾后的讲解与核查，**用户尚未逐项理解验收**，`Understanding=LEARNING`，新一轮网页 `GPT_SECOND_REVIEW=PENDING`。它不记录口试成绩，也不代替要求总账、独立复验或 Evidence Master 的判断。

先打开 [当前审阅入口](../../evidence/goal3/REVIEW_PACKET.md)，再按下列四块阅读。要求与质量证据统一进入 [MASTER_REQUIREMENTS_REVIEW](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md)；[教师作业导航](../../evidence/goal3/teacher_delivery_mapping.md) 及其 [JSON](../../evidence/goal3/teacher_delivery_mapping.json) 保存 TD 交叉索引、Notebook stable cell ID/source hash 和最终 PDF **物理页码**。本指南以章节与 stable cell ID 定位，不沿用旧版 21/12 页页码。

下文 **B** 为 [轨迹预处理完成版 Notebook](../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb)，**L** 为 [LLM 辅助评估清洗完成版 Notebook](../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb)。单元序号从 0 开始，stable ID 用于内容定位；最终 source hash 以教师作业导航的当前构建记录为准。

## I. 任务与要求

教师基础任务包括分段、短段过滤、方向去噪、DP 简化、指标解释、AI 准确性与隐含假设批判，以及独立的实验报告和过程报告。教师选做的参数、换序、LLM 系统与思考讨论，在本项目已获用户授权纳入 T2 必做范围。新增的有限候选、选择、最终确认、全量生产与交付由各阶段授权约束，不能倒写成教师原文逐项规定。

| 核查内容 | 可打开的位置 | 阅读时保留的区别 |
|---|---|---|
| 教师基础、选做和提交条件 | [教师原件](../../实验课1.pptx) 第 5–6、17–26、37、42 页；[已核回原件的映射](../../evidence/goal3/teacher_mapping.json)；总账 T1-01—T1-13、T2-01—T2-08 | 教师原文、用户追加要求和已批准调整分别有来源；文件存在不构成完成证据。 |
| 教学方案与实际方案的差异 | 总账“教学差异”对应记录；Experiment Report“处理方法与明确约定”“评价：共同参考先于候选”；[Technical Handoff](TECHNICAL_HANDOFF.md) §3–5 | PPT 的 95 米示例、starter 的 400、条件化工作米的角色不同；D2 调度来自用户授权；没有运行的 regret、路网接口及教学扩展不能写成已验证。 |
| 授权怎样改变执行边界 | [G1 授权补充](../../evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md) §一、二、三；[G3 原批准 Prompt](../../evidence/goal3/USER_PROMPT.md)；总账 U03、U22、U25、U43—U44 | 旧阶段曾需要澄清，后续才批准 D2、条件化分析和规则内自主执行；本轮先收尾、后讲解，不把最新规则写成从始至终如此。 |
| 文献实际起了什么作用 | [literature_use_map](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/literature_use_map.md)；[历史合并稿](../research/Task1_Literature_Review_2025_2026_Merged.md)；[Source Audit](../research/Task1_Source_Audit_2025_2026_Merged.json) | 已检索、全文核读、思想借鉴、实现试验、未采用和事后对应不能互换；没有强制凑够若干论文算法。 |

理解核查问题：

1. **哪些任务来自教师，哪些原为选做但被用户纳入必做？** 对照教师第 5–6、26、37、42 页和总账 T1/T2；应能分别指出两份报告、三组参数、换序与四模式的实际入口。
2. **95、400 与 D2 各有什么来源，哪些属于批准后的实现选择？** 查看 G1 授权补充和总账差异记录；不得把参数写成已证物理真值，或把同时删除调度全部归给教师原文。
3. **为什么“读过论文”“参考某思想”和“实现某方法”是三种不同判断？** 挑 literature_use_map 中一项有真实使用位置的来源，再挑一项未采用或仅事后对应的来源，分别说明访问层级与证据能支持的命题。

## II. 数据处理与评价

原始输入为 11,386 条记录、1,173,410 点，记录键未被证实代表独立用户或完整行程。`source_crs=UNVERIFIED` 保留为来源事实；固定椭球、`h=0` 和 ECEF→ENU 是获批的条件化计算模型。距离、长度、DP 偏差使用“工作米”，独立公式核对不能认证源 datum 或绝对定位精度。

最终统一策略为 S0：`S-D-P`，按 `dt / distance / min_points / min_length / direction / dp` 为 `30 / 400 / 2 / 0 / 35 / 5`。R0 为 `30 / 400 / 5 / 65 / 35 / 5`。最终处理不再逐记录调用 LLM 或搜索，也没有逐记录的 S0→R0 回退。

| 要点 | 代码 / 单元 | 结果与报告入口 |
|---|---|---|
| 输入、时间与坐标 | [coordinates.py](../../workflow/coordinates.py)：`working_xy`、`conditional_adapter`；B 2–3，代码 cell `lab1-f7fe7424c6193f77` | [冻结合同](../../config/goal3/contract.json)；Experiment“数据、任务与结论边界”；TD-01 |
| S：异常边切分，再按点数/长度过滤 | [geometry.py](../../workflow/geometry.py)：`split_trajectory`、`filter_segments`；B 5，`lab1-70227bc1defb860d` | Experiment“ S：分段与短段过滤”；[全量过滤原因](../../evidence/goal3/full_filter_attribution.json)；TD-02 |
| D：一次完整标记、同时删除 | 同文件 `direction_candidates`、`denoise_trajectory`；B 7，`lab1-9d637e0bfc2f7ff6` | 首尾、必要方向不可算窗口保留并标记；不迭代至收敛；下游重算特征。Experiment“D：方向异常候选的单次同时删除”；TD-03 |
| P：有限线段 Douglas–Peucker | 同文件 `point_segment_distance`、`douglas_peucker_indices`；B 9，`lab1-5edb2858a06036d2` | Experiment“P：有限线段的 DP 简化”；P 的 5 工作米约束仅覆盖它的实际输入；TD-04 |
| 共同评价与点去向 | [g2_metrics.py](../../workflow/g2_metrics.py)：`common_reference_metrics`、`record_metrics`；[selection.py](../../goal3/selection.py)：`paired`；B 12、21–22，生产 cell `lab1-bd932b47abf15ad3` | Experiment“评价：共同参考先于候选”；[点去向与覆盖图](../../figures/goal3/point_fates_and_coverage.pdf)；[原生数据](../../figures/goal3/figure_data.json)；TD-05、TD-17 |

共同参考在原始输入上固定 30 秒/400 工作米窗口，不先按候选过滤。点必须被同一身份点或同一固定窗口内、原索引包围它的输出边表示；不借别处最近折线或跨窗口外推。**共同覆盖点、显式保留点、P 省去点与真实噪声准确率是不同量**。共同误差只在可覆盖点上有定义；空分母保留 `null` 与原因，不填零。P 专项比较还要求完整 P 输入相同，不能将 S/D 的覆盖变化写成 P 压缩收益。

理解核查问题：

1. **`source_crs=UNVERIFIED` 时为什么还能运行，哪些结论仍不能得出？** 对照合同、G1 授权补充和 [全量坐标独立回执](../../evidence/goal3/independent_c/g3-full-production-01_coordinates_receipt.json)；分别指出数据事实、模型假设、公式一致性与真实地理精度。
2. **S0 的共同覆盖 1,172,211 点为什么不等于显式保留 221,149 点？** 打开点去向图及 [result_summary.json](../../evidence/goal3/result_summary.json)，沿 `filtered / denoised / simplified / retained` 账本解释分母；再说明覆盖提高不能证明噪声识别准确率提高。
3. **record 352/index 105 的约 266.016754 工作米偏差，为什么不证明 DP 违反 5 工作米保证？** 查看 [独立边界核验](../../evidence/goal3/independent_c/new_coverage_boundary_receipt.json) 的 `witness` 和 [轨迹案例图](../../figures/goal3/production_trajectory_cases.pdf)：R0 因点数不足过滤四点窗口，S0 的 D 删除 105，局部 P 输入/输出均为 `[104,106,107]`；被 D 删除的点不在 P 输入保证内。

## III. 系统、实验与循环

A 提出有边界的计划并消费真实比较，B 实际运行与修复，C 在独立上下文核对原始参考与目标产物；确定性工具和控制器不是新增 LLM Agent。历史角色身份见 Technical Handoff §2，实际治理工具索引只支持已记录的工具事实，不恢复缺失的人类聊天原文。收尾的 A/B/C 动作与历史研究调用分账，本轮不会重跑历史 84 次模型调用来证明文档更新。

| 要点 | 可执行实现与 Notebook 定位 | 实验 / 审核证据 |
|---|---|---|
| 参数与六种顺序 | [g2_experiments.py](../../workflow/g2_experiments.py)；[g2_pipeline.py](../../workflow/g2_pipeline.py)：`run_record`；B 13–18，执行 cell `lab1-62885400114d7d2b`、顺序 cell `lab1-20337038d9968da1` | [G2 阶段分析](../goal2/STAGE_ANALYSIS.md)；Experiment“历史 G2 实验：参数、顺序与单项候选”；TD-06、TD-07 |
| 四模式与模型调用 | [g2_modes.py](../../workflow/g2_modes.py)：`run_batch_episode`；[reproduce.py](../../goal3/reproduce.py)：`recompute_historical`；L 4–6，执行 cell `lab1-c8644f76db1f9bfe` | `search-only / llm-only / llm+search / llm+memory+search`；[G2 current_runs](../../evidence/goal2/current_runs.json) 和 [四模式图](../../figures/goal2/four_mode_paired_results.pdf)；TD-09 |
| 示范记忆与只读留出 | [g2_memory.py](../../workflow/g2_memory.py)：`build_snapshot`、`FrozenMemory`、`consumption`；L 9–10，cell `lab1-95890264cce459cd` | [消费表](../../evidence/goal2/tables/memory_consumption.csv)、[独立模式比较](../../evidence/goal2/tables/memory_independent_mode_comparison.csv)；Experiment“记忆被使用，不等于产生因果收益”；TD-10 |
| 真正拒绝错误与修复恢复 | [g2_metrics.py](../../workflow/g2_metrics.py)：`review_record`；[control.py](../../goal3/control.py)：`Journal`；[freezes.py](../../goal3/freezes.py)：`verified_run`；L 2–3、13–14 | [C08 失败](../../evidence/goal3/independent_c/G3-C08_failure.json) → [修复影响](../../evidence/goal3/repairs/C08_impact.json) → [独立关闭](../../evidence/goal3/independent_c/G3-C08_closure.json)；[实际工作流及 draw.io 源](../../figures/goal3/goal3_actual_workflow.drawio)；Process“真实缺陷如何进入修复与恢复”；TD-13 |
| 单项、组合、选择与最终确认 | [selection.py](../../goal3/selection.py)：`paired`、`aggregate_pairs`、`choose`；[freezes.py](../../goal3/freezes.py)：`selection_decision`、`release_decision`；L 14，cell `lab1-16c26970dd41618a` | [A3 决定](../../evidence/goal3/A3_DECISION.json)、[选择决定](../../evidence/goal3/selection_decision.json)、[最终冻结](../../evidence/goal3/final_freeze.json)、[发布策略决定](../../evidence/goal3/release_decision.json)；[裁决路径图](../../figures/goal3/incumbent_decision_path.pdf)；TD-14—TD-16 |

开发组合 S0_G0 相对 S0 曾有 41 条几何改善，选择阶段却在 3017、9311、9534 三条违反共同保护，最终保持 S0。P2 未证明压缩收益，P10 超出共同预算；这些负结果没有删去。600 条、62,284 点的最终确认发生在冻结以后，349 条严格覆盖改善；随后 11,386 条的全量生产包含已开发记录，不能再算一批独立测试。详见 [Technical Handoff](TECHNICAL_HANDOFF.md) §5–7 与 [current_runs.json](../../evidence/goal3/current_runs.json)。

理解核查问题：

1. **四模式在能力上怎样不同，为什么 search-only 的新模型调用必须为 0？** 从 L“ 四模式与公平预算”和 `run_batch_episode` 追踪提议、搜索与记忆入口；区分历史 LIVE 请求、保存提议的 RECOMPUTE 和本轮治理角色调用。
2. **为什么记忆送达或被引用不能证明记忆有因果质量收益？** 从消费表找 `retrieved / eligible / delivered / model_cited / action_consistent` 的不同分母，再看独立模式比较；说清示范分区、留出只读与尚未证实的收益。
3. **组合为什么在开发阶段保留、在选择阶段退出；修复为何不能“修到它获胜”？** 对照 A3、选择决定及 [选择失败独立回执](../../evidence/goal3/independent_c/selection_failure_receipt.json)；区分实现不符合同需要修复和真实方法退化需要拒绝，并说明最终集不能重新调参。
4. **独立 C 具体拒绝过什么，怎样才允许恢复父任务？** 用 C08 的真实 1 通过/4 失败与修复后 5 项通过说明目标 hash、源码与回执身份校验；技术修复成功不是清洗质量提高，也不是用户逐次 Human Judgment。

## IV. 正式成果与收尾

两份报告职责独立：Experiment Report 解释最终方法、实验与限制；Process Report 保留 Part I Workflow Construction 和 Part II Experiment Decision Process，已有技术事实送审内容与正式互动呈现的完成状态分开。姓名“吴博闻”、学号字符串“10245102410”由本轮直接授权提供，当前元数据源为 [assignment.json](../../config/assignment.json)。2026-09-28 是报告修订日期，不改变旧实验/冻结时间。

| 成果 / 检查对象 | 当前入口 | 需要核查的内容 |
|---|---|---|
| 两份正式文档送审版本 | [Experiment PDF](../../reports/experiment1/experiment1.pdf) / [XeLaTeX](../../reports/experiment1/experiment1.tex)；[Process PDF](../../reports/process1/process1.pdf) / [XeLaTeX](../../reports/process1/process1.tex) | 封面、目录、正文、公式、图表、引用与负结果；Process 的互动证据缺项不能靠删除标识解决。 |
| 最终 PDF 页面与文本 | [Experiment 分页文本](../../evidence/goal3/report_build/experiment1_pages.txt)；[Process 分页文本](../../evidence/goal3/report_build/process1_pages.txt)；[build_receipt](../../evidence/goal3/report_build/build_receipt.json) | 按 manifest 打开对应报告每个 200 dpi 页面；图像 hash 或缩略图不代替逐页目视。导航物理页码以当前教师映射为准。 |
| Notebook 和实际复算 | B / L；[运行说明](../../README.md)；[reproduce.py](../../goal3/reproduce.py)；本次 [收尾记录目录](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/) | 逐一查看仓库与同一最终 ZIP 解压目录的新内核 FULL 回执；源码、输入和完整依赖的 hash 必须绑定有效内容。REPORT_BUILD、静态依赖 probe 和历史回执不替代新运行。 |
| 图的原始数据与可编辑源 | [figure_data.json](../../figures/goal3/figure_data.json)、[figure_manifest.json](../../figures/goal3/figure_manifest.json)、[figures.py](../../goal3/figures.py)、[draw.io](../../figures/goal3/goal3_actual_workflow.drawio) | 图中数据、caption 和原生数据一致；保持 P2 / XeLaTeX；技术图不是原生聊天 Evidence。 |
| 互动来源和工程交接 | [Technical Handoff](TECHNICAL_HANDOFF.md)；[Interaction Handoff](INTERACTION_HANDOFF.md)；[本次 Evidence 盘点](../../evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/b_handoff/evidence_inventory.md) | 原生截图/完整上下文、已批准 spec、Evidence/Block Lock 分别核实；现有模型 JSON、授权文本与工程回执不自动补齐这些条件。 |
| 新待审包与当前版本 | [submission 目录](../../submission/)；[当前审阅入口](../../evidence/goal3/REVIEW_PACKET.md) 的本次包与发布记录 | 本轮目标包 `REVIEW_ONLY_10245102410_吴博闻_实验一.zip`；核查成员、CRC/哈希、当前 PDF 与 Notebook 字节、真实解压 FULL 和 0 新实验模型调用。正式目标名仅在后续确认后才使用。 |

理解核查问题：

1. **拿到 ZIP 后，什么证据能证明 Notebook 实际独立运行，而不只是能导入或加载旧 CSV？** 打开本次两个解压 FULL 回执，指出原始输入、真实处理规模、新内核、隔离路径、源码身份与 Provider 调用观察；若采用字节等价继承，明确其证据范围。
2. **过程报告还缺什么，谁有权决定正式呈现？** 查本次 Evidence 盘点和 [Workflow Evidence Plan](../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)：已有原文可继续索引，缺原件需补原件；没有批准 spec 不自行选 anchor、画箭头、调序或 LOCK。身份已提供，不再列为外部缺项。
3. **为什么“内部工程可审”不等于“用户理解通过”或“作业已提交”？** 对照当前审阅入口的独立状态：Deliverable 待最终审核，Understanding=LEARNING，Submission=NOT_READY，新 GPT_SECOND_REVIEW=PENDING。教师材料第 26 页写“10 月 5 日前”和规定命名，未给具体截止时刻；本轮没有代发邮件或教学平台提交。

完成四块讲解后，由用户与网页 GPT 检查实际远程文件并决定后续动作。需要的新 Evidence Master 输入只解锁相关正式互动页面；本指南本身不赋予 Evidence Lock、最终 Deliverable PASS 或 Submission 权限。
