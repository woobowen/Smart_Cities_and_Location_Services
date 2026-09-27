# 实验一完整要求复盘总账

任务 `SC-LAB1-G3-CLOSEOUT-001`；A 来源与要求诊断。共 65 个稳定复盘 ID。

本文件从原 G1/G2/G3 requirements、TD 导航和真实结果派生，作为后续四块讲解的入口，不新建另一套“全部通过”状态表。原要求与审核范围保持原身份。U01–U44 是用户本轮归并索引，不是原始聊天逐字稿。历史网页 GPT 结论仅按用户转交范围登记；本轮 A 的源定位不能替代 C、PDF目视、Notebook执行或用户验收。

唯一父要求入口：[requirements.json](../../../requirements.json)；其中 `previous_acceptance` 原样保存 1a5e26b 历史范围，当前状态另记。本轮 CL 矩阵由主线程在 `../ACCEPTANCE_MATRIX.json` 登记；不因目录/文件存在宣称验收通过。

本表中的父状态与工作流治理输入固定为送审输入快照：观察时点 `2026-09-27T17:47:18.410070+00:00`，[真实复制与哈希清单](../review_input_snapshot/SNAPSHOT_MANIFEST.json)。两份快照严格核验字节，缺失或不符时生成失败；快照不是第二 active source。最终发布状态查 [active requirements](../../../requirements.json)、[active goal_state](../../../goal_state.json) 与 CL 入口，合法后续状态推进不倒写本次观察。

当前身份由用户直接给出，姓名/学号不再列外部缺项。正式互动原件/spec/Lock、新网页 GPT 审核和用户深入理解仍按各自状态登记。总账会在最终 PDF 构建后刷新实际页码和字节绑定；物理页含封面，Notebook编号从0开始。

配套：[七项教学差异](TEACHING_DIFFERENCES.md) · [文献使用对账](literature_use_map.md) · [本轮具体工作项](DIAGNOSIS.md)。

当前绑定：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf)（22页，SHA256 `5a7f01b64be6a9bc424b1e8cc90ccae9306e21a9959ff674363fcc4c046d7606`）, [process1.pdf](../../../../../reports/process1/process1.pdf)（12页，SHA256 `9ff0fc21b2c843156b3d2bb648441dd19f51569dc451975d531a029971a34a88`）。

| ID | 当前要求 | 状态 | 交叉入口 |
|---|---|---|---|
| [T1-01](#t101) | 异常时间/空间连接识别与分段 | 有实现与结果证据，待用户审核 | TD-02；G3-A02、G3-A08 |
| [T1-02](#t102) | 分段后的短距离/少点数片段处理和原因 | 批准调整实现，范围内覆盖收益已获历史证据支持 | TD-02、TD-17；G3-A02、G3-A03、G3-A08 |
| [T1-03](#t103) | 教师方向关系去噪及获批删除调度 | 批准补充调度，待用户审核 | TD-03；G3-A02、G3-A10 |
| [T1-04](#t104) | 有限线段 Douglas–Peucker 简化及边界 | 有实现与结果证据，待用户审核 | TD-04；G3-A02、G3-A10 |
| [T1-05](#t105) | 评价指标定义、参考与分母 | 有实现与结果证据，待用户审核 | TD-05；G3-A02、G3-A07、G3-A08 |
| [T1-06](#t106) | 指标设计逻辑和真实结果分析 | 有实现与结果证据，待用户审核 | TD-05、TD-16、TD-17；G3-A07、G3-A08 |
| [T1-07](#t107) | 基础Notebook空缺、处理程序与实际可运行入口 | 有实现与结果证据，待用户审核 | TD-02、TD-03、TD-04、TD-12；G3-A02、G3-A13 |
| [T1-08](#t108) | AI生成内容准确性批判 | 有实现与结果证据，待用户审核 | TD-11；G3-A02、G3-A10 |
| [T1-09](#t109) | 至少一组明确反例、真实修改前后指标和拒绝原因 | 有实现与结果证据，待用户审核 | TD-11；G3-A02、G3-A10 |
| [T1-10](#t110) | AI隐含假设及其失效情形 | 有实现与结果证据，待用户审核 | TD-11；G3-A02、G3-A10 |
| [T1-11](#t111) | 独立的数据处理评估报告 | 当前Experiment全文/视觉限定内部C审核完成；新网页GPT与用户待审 | TD-12、TD-17；G3-A15 |
| [T1-12](#t112) | 包含AI批判的实验过程报告 | 部分完成；互动Evidence外部待补 | TD-11、TD-19、TD-20；G3-A16 |
| [T1-13](#t113) | Notebook/报告ZIP、规定命名与教师提交条件 | 待审包工程与隔离FULL已获本轮C限定核验；Submission NOT_READY | TD-22；G3-A18、G3-A20 |
| [T2-01](#t201) | 分段/过滤参数实验 | 有实现与结果证据，待用户审核 | TD-06；G3-A02、G3-A03 |
| [T2-02](#t202) | 方向阈值参数实验 | 实验完成；无统一新赢家 | TD-06；G3-A02、G3-A03 |
| [T2-03](#t203) | DP容差实验 | 实验完成；无统一新赢家 | TD-06；G3-A02、G3-A03 |
| [T2-04](#t204) | 三步换序讨论及必要实际比较 | 有实现与结果证据，待用户审核 | TD-07；G3-A02、G3-A03 |
| [T2-05](#t205) | 基于助教系统的实际LLM辅助质量提升工作流 | 批准调整实现；方法收益按结果限定 | TD-08、TD-09、TD-13；G3-A02、G3-A11、G3-A12 |
| [T2-06](#t206) | 结构性不同的四模式及真实search-only零模型调用 | 有实现与结果证据，待用户审核 | TD-09；G3-A02、G3-A12 |
| [T2-07](#t207) | 示范记忆、留出只读、泄漏隔离及收益检验 | 实验完成；记忆因果收益未获证实 | TD-10；G3-A02、G3-A06、G3-A12 |
| [T2-08](#t208) | 更实用系统的思考与本项目获批增强 | 批准增强已实现；仍待用户审核 | TD-08、TD-13、TD-14；G3-A03、G3-A04、G3-A11 |
| [U01](#u01) | 教师基础和附加任务优先 | 有工程/来源证据，待用户审核 | TD-02、TD-06、TD-12；G3-A02 |
| [U02](#u02) | 所有增强针对实验一，不脱离轨迹任务 | 有工程/来源证据，待用户审核 | TD-08、TD-14；G3-A03、G3-A11 |
| [U03](#u03) | 研究先于实现，重要规则先确认 | 有工程/来源证据，待用户审核 | TD-01、TD-03、TD-15；G3-A03、G3-A06 |
| [U04](#u04) | 检索与实验相关的高质量论文，不泛查Multi-Agent | 有工程/来源证据，待用户审核 | 来源研究；G3-A03 |
| [U05](#u05) | 更新2025/2026来源并与旧研究整合 | 有工程/来源证据，待用户审核 | 来源研究；G3-A03 |
| [U06](#u06) | 说明各来源与任务关联、可迁移点及风险 | 有工程/来源证据，待用户审核 | 来源研究；G3-A03 |
| [U07](#u07) | 少量有用文献，不强制复现、采用或数量凑数 | 有工程/来源证据，待用户审核 | 来源研究；G3-A03 |
| [U08](#u08) | 多候选实际尝试，以结果选择 | 有工程/来源证据，待用户审核 | TD-06、TD-14、TD-15；G3-A03、G3-A05 |
| [U09](#u09) | 单项验证先于组合 | 有工程/来源证据，待用户审核 | TD-14；G3-A03、G3-A04 |
| [U10](#u10) | 有益保留、退化拒绝/回退 | 有工程/来源证据，待用户审核 | TD-14、TD-15；G3-A04、G3-A05 |
| [U11](#u11) | 共同评选尺度与方法专项审核并存 | 有工程/来源证据，待用户审核 | TD-04、TD-05、TD-14；G3-A05、G3-A10 |
| [U12](#u12) | 参数、方法、审核和结论有来源或实验证据 | 有工程/来源证据，待用户审核 | TD-01、TD-05、TD-06、TD-15；G3-A03、G3-A10 |
| [U13](#u13) | 不换指标、挑样本、隐瞒失败追求漂亮结果 | 有工程/来源证据，待用户审核 | TD-05、TD-07、TD-15；G3-A04、G3-A06 |
| [U14](#u14) | 不要求复杂方案、论文方法、记忆机制必然获胜 | 有工程/来源证据，待用户审核 | TD-10、TD-14、TD-15；G3-A04、G3-A12 |
| [U15](#u15) | 工作流涵盖研究、执行、审核、优化及交付全过程 | 有工程/来源证据，待用户审核 | TD-08、TD-13、TD-19；G3-A11、G3-A19 |
| [U16](#u16) | Agent实际组织计算与实验，不只提出建议 | 有工程/来源证据，待用户审核 | TD-08、TD-13；G3-A11 |
| [U17](#u17) | Agent宁少勿滥，不将普通函数改名冒充Agent | 有工程/来源证据，待用户审核 | TD-08、TD-13；G3-A11 |
| [U18](#u18) | 角色输入输出、工具、状态、权限和交接明确 | 有工程/来源证据，待用户审核 | TD-08、TD-13、TD-21；G3-A11、G3-A17 |
| [U19](#u19) | Verifier真正检查可信参考与目标产物，能拒绝错误 | 有工程/来源证据，待用户审核 | TD-05、TD-13；G3-A10、G3-A11 |
| [U20](#u20) | 修复是工作流一部分，不能发现问题就返回 | 有工程/来源证据，待用户审核 | TD-13；G3-A11、G3-A19 |
| [U21](#u21) | 对完整父Goal持续负责，不把局部任务结束当完成 | 有工程/来源证据，待用户审核 | TD-13、TD-19；G3-A11、G3-A19 |
| [U22](#u22) | 最小必要人工介入，批准规则后自主执行 | 有工程/来源证据，待用户审核 | TD-13、TD-15；G3-A05、G3-A11 |
| [U23](#u23) | 不凭主观直接选最优，由有效比较裁决 | 有工程/来源证据，待用户审核 | TD-14、TD-15、TD-16；G3-A05、G3-A07 |
| [U24](#u24) | 迭代有范围、预算和停止理由，不无限搜索 | 有工程/来源证据，待用户审核 | TD-14、TD-15；G3-A03、G3-A04 |
| [U25](#u25) | 总体三个大Goal，减少反复转发；保留早期真实返工历史 | 有工程/来源证据，待用户审核 | TD-13、TD-19；G3-A01、G3-A11 |
| [U26](#u26) | retry/fallback/escalation/stop与恢复真实，不只画图 | 有工程/来源证据，待用户审核 | TD-13、TD-15；G3-A04、G3-A11 |
| [U27](#u27) | 原始材料、starter、原始数据和历史有效结果保留 | 有工程/来源证据，待用户审核 | TD-01、TD-22；G3-A01 |
| [U28](#u28) | 尊重但核查starter、默认数值、Mock及历史演示 | 有工程/来源证据，待用户审核 | TD-02、TD-04、TD-08；G3-A02、G3-A10 |
| [U29](#u29) | 不伪造运行、模型输出、截图、用户判断或决策历史 | 有工程/来源证据，待用户审核 | TD-11、TD-19、TD-20；G3-A11、G3-A16 |
| [U30](#u30) | 时空语义、单位、不可计算性与样本边界明确 | 有工程/来源证据，待用户审核 | TD-01、TD-05、TD-16、TD-17；G3-A06、G3-A09 |
| [U31](#u31) | 内部审核后发布，网页GPT读取真实远程二重验收 | 有工程/来源证据，待用户审核 | TD-21；G3-A19、G3-A20 |
| [U32](#u32) | GitHub完整工程与教师最小提交包分开 | 有工程/来源证据，待用户审核 | TD-22；G3-A18、G3-A20 |
| [U33](#u33) | 用户工作区、依赖环境、安全和原有文件受保护 | 有工程/来源证据，待用户审核 | TD-22；G3-A01、G3-A18 |
| [U34](#u34) | Notebook新内核可运行，LIVE/复算/历史分开 | 有工程/来源证据，待用户审核 | TD-12、TD-22；G3-A13、G3-A18 |
| [U35](#u35) | 图表回答问题，真实、清晰、可复现和可编辑 | 有工程/来源证据，待用户审核 | TD-18；G3-A14 |
| [U36](#u36) | draw.io结构源、publication-plots、固定P2及XeLaTeX | 有工程/来源证据，待用户审核 | TD-18；G3-A14、G3-A15、G3-A16 |
| [U37](#u37) | Experiment/Process两份报告职责独立，不机械复制 | 有工程/来源证据，待用户审核 | TD-12、TD-19；G3-A15、G3-A16 |
| [U38](#u38) | 文档自然具体清楚，避免内部日志与空泛AI口吻堆砌 | 有工程/来源证据，待用户审核 | TD-12、TD-19；G3-A15、G3-A16 |
| [U39](#u39) | Original Evidence First，真实人类贡献可追溯 | 外部待补：正式互动证据未闭合 | TD-20；G3-A16 |
| [U40](#u40) | Evidence Master与Research Conversation/工程职责分离 | 外部待补：正式互动证据未闭合 | TD-20；G3-A16、G3-A17 |
| [U41](#u41) | 技术与互动两份Handoff | 有工程/来源证据，待用户审核 | TD-19、TD-20、TD-21；G3-A17 |
| [U42](#u42) | 11文件分发集与普通任务附件分开，不冒称UI已上传 | 有工程/来源证据，待用户审核 | TD-22；G3-A01、G3-A20 |
| [U43](#u43) | Deliverable、Understanding、Submission相互独立 | 状态已分离；理解/最终提交待用户 | TD-20、TD-21、TD-22；G3-A16、G3-A18、G3-A20 |
| [U44](#u44) | 当前先工程收尾，再按四板块讲解由用户审核，最后决定提交 | 最新授权顺序已确认；后续用户审核PENDING | TD-12、TD-19、TD-21、TD-22；G3-A17、G3-A19、G3-A20 |

<a id="t101"></a>

## T1-01 异常时间/空间连接识别与分段

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第17–18页；18页异常边p2→p3及两侧点归属；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/4/10/12–13；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/7.2/8.1；[实验课1.pptx](../../../../../实验课1.pptx) 物理第17页 / ppt/slides/slide17.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第18页 / ppt/slides/slide18.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 先阻断异常连接，避免后续D/P跨越固定原始边界。 同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::split_trajectory（L146）；[geometry.py](../../../../../workflow/geometry.py)::filter_segments（L185）
真实证据：[result_summary.json](../../../result_summary.json)；[full_filter_attribution.json](../../../full_filter_attribution.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-59e8941bd6d66ace`, `lab1-70227bc1defb860d`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3,4（分段与短段过滤）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页18（仅长度不足）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- S：分段与过滤点数；点终态分母全部1,173,410原始点；记录分母11,386。 预期：同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 实际：R0/S0均25,963段；过滤501,511 / 1,199点。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** R0/S0均25,963段；过滤501,511 / 1,199点。 可恢复几何覆盖不等于恢复干净轨迹；source_crs未认证。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A08 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t102"></a>

## T1-02 分段后的短距离/少点数片段处理和原因

**性质/状态：** TEACHER_REQUIRED_T1；批准调整实现，范围内覆盖收益已获历史证据支持。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第17–18页；18页异常边p2→p3及两侧点归属；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/4/10/12–13；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/7.2/8.1；[实验课1.pptx](../../../../../实验课1.pptx) 物理第17页 / ppt/slides/slide17.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第18页 / ppt/slides/slide18.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 保留R0过滤规则与独立原因，S0放宽过滤是经过比较的最终策略，不能取消教学实现。 同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::split_trajectory（L146）；[geometry.py](../../../../../workflow/geometry.py)::filter_segments（L185）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[result_summary.json](../../../result_summary.json)；[full_filter_attribution.json](../../../full_filter_attribution.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-59e8941bd6d66ace`, `lab1-70227bc1defb860d`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3,4（分段与短段过滤）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页18（仅长度不足）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,17（冻结策略下的全部原始记录生产）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（生产与交付继续按冻结策略执行）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- S：分段与过滤点数；点终态分母全部1,173,410原始点；记录分母11,386。 预期：同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 实际：R0/S0均25,963段；过滤501,511 / 1,199点。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** R0/S0均25,963段；过滤501,511 / 1,199点。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 可恢复几何覆盖不等于恢复干净轨迹；source_crs未认证。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A08 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t103"></a>

## T1-03 教师方向关系去噪及获批删除调度

**性质/状态：** TEACHER_REQUIRED_T1；批准补充调度，待用户审核。

**来源与授权：** 原PPT未写尽调度；G1 USER_DECISIONS D2真实答复随后批准一次标记同时删除。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第19–20页；20页明确p3方向=p3→p4；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 2/6/10/14–15；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.1/5.2/8.1；[实验课1.pptx](../../../../../实验课1.pptx) 物理第19页 / ppt/slides/slide19.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第20页 / ppt/slides/slide20.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 固定D2使邻域/删除集合唯一；保留不可计算条件。 教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::direction_candidates（L242）；[geometry.py](../../../../../workflow/geometry.py)::denoise_trajectory（L277）；[geometry.py](../../../../../workflow/geometry.py)::recompute_features（L74）
真实证据：[USER_DECISIONS.json](../../../../goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json)；[exposed_pilot_direction.csv](../../../../goal2/tables/exposed_pilot_direction.csv)；[result_summary.json](../../../result_summary.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-36a4e3074ee2fa99`, `lab1-9d637e0bfc2f7ff6`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（方向异常候选的单次同时删除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（方向规则的计算顺序先确认，再执行）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- D：D删除与不可计算原因逐点保存；方向角单位度，几何工作米。 预期：教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。 实际：全量R0/S0 D删除36,056 / 39,732。记录352/index105由D删除。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量R0/S0 D删除36,056 / 39,732。记录352/index105由D删除。 删除仅是规则动作，没有真实噪声标签；D前点不属于P误差保证。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t104"></a>

## T1-04 有限线段 Douglas–Peucker 简化及边界

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第21–23页；22页线段距离及严格大于阈值；23页16帧演示；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/2/8/10/16–18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/5.3/8.1–8.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第21页 / ppt/slides/slide21.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第22页 / ppt/slides/slide22.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 修正无限直线/浮点反查索引等starter风险，遵守教师有限线段定义。 有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::point_segment_distance（L51）；[geometry.py](../../../../../workflow/geometry.py)::douglas_peucker_indices（L206）
真实证据：[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[result_summary.json](../../../result_summary.json)；[g3-full-production-01_categories_receipt.json](../../../independent_c/g3-full-production-01_categories_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-cd82900c2901ee9f`, `lab1-5edb2858a06036d2`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（有限线段的 DP 简化）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（P 的局部指标与整体指标分开）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- P：P省点率=1-N_P_out/N_P_in；误差只对完整即时P输入，不是raw真值误差。 预期：有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 实际：全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。 不能把5工作米预算用于被D先删的原始点或证明真实定位精度。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t105"></a>

## T1-05 评价指标定义、参考与分母

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第26页必做第2项；第24–25页示例保留比例；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.3/5.4/8.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第24页 / ppt/slides/slide24.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第25页 / ppt/slides/slide25.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 共同原始身份约束防止候选用自身clean自证，null不变零。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。

**审核范围：** 历史内部C回执：[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[confirmation_closure_receipt.json](../../../independent_c/confirmation_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A07 `INHERITED_NUMERIC_EVIDENCE`；G3-A08 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t106"></a>

## T1-06 指标设计逻辑和真实结果分析

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第26页必做第2项；第24–25页示例保留比例；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.3/5.4/8.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第24页 / ppt/slides/slide24.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第25页 / ppt/slides/slide25.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 同时报告覆盖、显式存储、几何和新增覆盖边界，收益与限制分别说明。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,16（先冻结，再执行一次性最终确认）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（最终确认：执行预设门控，不再选参数）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,17（冻结策略下的全部原始记录生产）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（生产与交付继续按冻结策略执行）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[confirmation_closure_receipt.json](../../../independent_c/confirmation_closure_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A07 `INHERITED_NUMERIC_EVIDENCE`；G3-A08 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t107"></a>

## T1-07 基础Notebook空缺、处理程序与实际可运行入口

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第17–18页；18页异常边p2→p3及两侧点归属；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/4/10/12–13；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/7.2/8.1；[实验课1.pptx](../../../../../实验课1.pptx) 物理第17页 / ppt/slides/slide17.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第18页 / ppt/slides/slide18.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 完成版有可调用S/D/P与原始索引，原starter保持原样；新内核复算核依赖。 同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。 有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::split_trajectory（L146）；[geometry.py](../../../../../workflow/geometry.py)::filter_segments（L185）；[geometry.py](../../../../../workflow/geometry.py)::direction_candidates（L242）；[geometry.py](../../../../../workflow/geometry.py)::denoise_trajectory（L277）；[geometry.py](../../../../../workflow/geometry.py)::recompute_features（L74）；[geometry.py](../../../../../workflow/geometry.py)::point_segment_distance（L51）；[geometry.py](../../../../../workflow/geometry.py)::douglas_peucker_indices（L206）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[result_summary.json](../../../result_summary.json)；[full_filter_attribution.json](../../../full_filter_attribution.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[USER_DECISIONS.json](../../../../goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json)；[exposed_pilot_direction.csv](../../../../goal2/tables/exposed_pilot_direction.csv)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[g3-full-production-01_categories_receipt.json](../../../independent_c/g3-full-production-01_categories_receipt.json)；[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-59e8941bd6d66ace`, `lab1-70227bc1defb860d`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-36a4e3074ee2fa99`, `lab1-9d637e0bfc2f7ff6`, `lab1-cd82900c2901ee9f`, `lab1-5edb2858a06036d2`, `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3,4（分段与短段过滤）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页18（仅长度不足）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（方向异常候选的单次同时删除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（方向规则的计算顺序先确认，再执行）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（有限线段的 DP 简化）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（P 的局部指标与整体指标分开）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- S：分段与过滤点数；点终态分母全部1,173,410原始点；记录分母11,386。 预期：同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 实际：R0/S0均25,963段；过滤501,511 / 1,199点。
- D：D删除与不可计算原因逐点保存；方向角单位度，几何工作米。 预期：教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。 实际：全量R0/S0 D删除36,056 / 39,732。记录352/index105由D删除。
- P：P省点率=1-N_P_out/N_P_in；误差只对完整即时P输入，不是raw真值误差。 预期：有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 实际：全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** R0/S0均25,963段；过滤501,511 / 1,199点。 全量R0/S0 D删除36,056 / 39,732。记录352/index105由D删除。 全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 可恢复几何覆盖不等于恢复干净轨迹；source_crs未认证。 删除仅是规则动作，没有真实噪声标签；D前点不属于P误差保证。 不能把5工作米预算用于被D先删的原始点或证明真实定位精度。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)（当前两Notebook各在仓库和同一ZIP解压目录新内核FULL，12/8/12/8单元；C分别读全部285分片、逐点终态和历史注册表，新增记录级调用0。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（当前两Notebook各在仓库和同一ZIP解压目录新内核FULL，12/8/12/8单元；C分别读全部285分片、逐点终态和历史注册表，新增记录级调用0。）；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)（当前两Notebook各在仓库和同一ZIP解压目录新内核FULL，12/8/12/8单元；C分别读全部285分片、逐点终态和历史注册表，新增记录级调用0。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A13 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t108"></a>

## T1-08 AI生成内容准确性批判

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第6页单位/经纬度/插值示例及反例、前后指标、拒绝原因要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §8/9/10；[WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) 真实互动证据及Evidence Master边界；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页 / ppt/slides/slide6.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 依据实际响应与可信同集合指标，区分合法提议、执行成功与保护失败。 引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::validate_response（L51）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）
真实证据：[actual_ai_critique.json](../../../../goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[ai_legal_proposal_tradeoffs.csv](../../../../goal2/tables/ai_legal_proposal_tradeoffs.csv)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-02361194ac55bb28`, `lab1-2eaa006465170263`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-02de2176540c11fb`, `lab1-e4e3f3e47d311987`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,11（AI 建议的技术批判与可复验反例）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,8（一次真实 AI 建议怎样变成负结果）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- AI：记录7764同122个共同覆盖点的max；6组合成例、19处理链、25已知答案检查不作为总体样本。 预期：引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 实际：真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。

**审核范围：** 历史内部C回执：[counterexamples_epoch02_receipt.json](../../../../goal2/c_contract/counterexamples_epoch02_receipt.json)；[counterexamples_complete_receipt.json](../../../../goal2/c_contract/counterexamples_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。 原模型没有承诺真值准确率；不伪造用户拒绝、非法提议或自然噪声标签。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t109"></a>

## T1-09 至少一组明确反例、真实修改前后指标和拒绝原因

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第6页单位/经纬度/插值示例及反例、前后指标、拒绝原因要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §8/9/10；[WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) 真实互动证据及Evidence Master边界；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页 / ppt/slides/slide6.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 真实7764负结果与合成机制反例互补；不能制造人机争论。 引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::validate_response（L51）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）
真实证据：[actual_ai_critique.json](../../../../goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[ai_legal_proposal_tradeoffs.csv](../../../../goal2/tables/ai_legal_proposal_tradeoffs.csv)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-02361194ac55bb28`, `lab1-2eaa006465170263`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-02de2176540c11fb`, `lab1-e4e3f3e47d311987`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,11（AI 建议的技术批判与可复验反例）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,8（一次真实 AI 建议怎样变成负结果）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- AI：记录7764同122个共同覆盖点的max；6组合成例、19处理链、25已知答案检查不作为总体样本。 预期：引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 实际：真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。

**审核范围：** 历史内部C回执：[counterexamples_epoch02_receipt.json](../../../../goal2/c_contract/counterexamples_epoch02_receipt.json)；[counterexamples_complete_receipt.json](../../../../goal2/c_contract/counterexamples_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。 原模型没有承诺真值准确率；不伪造用户拒绝、非法提议或自然噪声标签。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t110"></a>

## T1-10 AI隐含假设及其失效情形

**性质/状态：** TEACHER_REQUIRED_T1；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第6页单位/经纬度/插值示例及反例、前后指标、拒绝原因要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §8/9/10；[WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) 真实互动证据及Evidence Master边界；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页 / ppt/slides/slide6.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 用P自身误差不能保护D前raw、丢覆盖造成null、正常折返与毛刺混淆揭示假设。 引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::validate_response（L51）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）
真实证据：[actual_ai_critique.json](../../../../goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[ai_legal_proposal_tradeoffs.csv](../../../../goal2/tables/ai_legal_proposal_tradeoffs.csv)；[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-02361194ac55bb28`, `lab1-2eaa006465170263`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-02de2176540c11fb`, `lab1-e4e3f3e47d311987`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,11（AI 建议的技术批判与可复验反例）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,8（一次真实 AI 建议怎样变成负结果）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- AI：记录7764同122个共同覆盖点的max；6组合成例、19处理链、25已知答案检查不作为总体样本。 预期：引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 实际：真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。

**审核范围：** 历史内部C回执：[counterexamples_epoch02_receipt.json](../../../../goal2/c_contract/counterexamples_epoch02_receipt.json)；[counterexamples_complete_receipt.json](../../../../goal2/c_contract/counterexamples_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 原模型没有承诺真值准确率；不伪造用户拒绝、非法提议或自然噪声标签。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t111"></a>

## T1-11 独立的数据处理评估报告

**性质/状态：** TEACHER_REQUIRED_T1；当前Experiment全文/视觉限定内部C审核完成；新网页GPT与用户待审。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 独立Experiment Report完整解释定义、实验、真实结论和边界，不让README替代。 当前Experiment正文、表图数值与来源及200dpi全部22物理页由独立C核对；修订变页重新查看。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）
真实证据：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)；[visual_content_receipt.json](../c_review/visual_content_receipt.json)；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)；[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,17（冻结策略下的全部原始记录生产）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（生产与交付继续按冻结策略执行）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- REPORT_CURRENT：22/22当前Experiment物理页实际视觉覆盖，回执绑定最终PDF和每页PNG；数值核对按实际源表/分母而非图页存在。 预期：当前Experiment正文、表图数值与来源及200dpi全部22物理页由独立C核对；修订变页重新查看。 实际：本轮Experiment全文、视觉和对应报告任务的限定内部审核已完成；C回执记录当前有效字节和核查范围。
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[experiment_report_current_closure.json](../../../independent_documents/experiment_report_current_closure.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮Experiment全文、视觉和对应报告任务的限定内部审核已完成；C回执记录当前有效字节和核查范围。 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 内部C不能代替新网页GPT二重审核或用户逐项理解；不据此关闭Process真实互动证据或Submission门槛。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。

**剩余动作：** 用户与网页GPT按四块指南继续核查；内部C通过不替代最终Deliverable或Understanding判断。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A15 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t112"></a>

## T1-12 包含AI批判的实验过程报告

**性质/状态：** TEACHER_REQUIRED_T1；部分完成；互动Evidence外部待补。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第6页单位/经纬度/插值示例及反例、前后指标、拒绝原因要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §8/9/10；[WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) 真实互动证据及Evidence Master边界；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页 / ppt/slides/slide6.xml；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18。详细原句/版本SHA见同名JSON。

**做法与理由：** Part I组织工作流、Part II解释真实实验决定；有源技术正文可交审，真实互动呈现仍必需。 引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::validate_response（L51）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）
真实证据：[actual_ai_critique.json](../../../../goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[ai_legal_proposal_tradeoffs.csv](../../../../goal2/tables/ai_legal_proposal_tradeoffs.csv)；[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-02361194ac55bb28`, `lab1-2eaa006465170263`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-02de2176540c11fb`, `lab1-e4e3f3e47d311987`, `lab1-65870bb6cd4183c2`, `lab1-f711eb1ab5723d3f`, `lab1-b9a7a9bb893c339f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,11（AI 建议的技术批判与可复验反例）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,8（一次真实 AI 建议怎样变成负结果）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1（吴博闻）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,11（互动证据仍需哪些真实输入）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- AI：记录7764同122个共同覆盖点的max；6组合成例、19处理链、25已知答案检查不作为总体样本。 预期：引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 实际：真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[counterexamples_epoch02_receipt.json](../../../../goal2/c_contract/counterexamples_epoch02_receipt.json)；[counterexamples_complete_receipt.json](../../../../goal2/c_contract/counterexamples_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 原模型没有承诺真值准确率；不伪造用户拒绝、非法提议或自然噪声标签。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** 需要真实原件/完整消息范围、Evidence Master呈现spec及最终Lock；继续保留当前送审报告。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A16 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t113"></a>

## T1-13 Notebook/报告ZIP、规定命名与教师提交条件

**性质/状态：** TEACHER_REQUIRED_T1；待审包工程与隔离FULL已获本轮C限定核验；Submission NOT_READY。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第26页压缩包、邮箱、命名、10月5日前；第43页联系邮箱；[AGENTS.md](../../../../../../AGENTS.md) §18 GitHub与Submission Package分工；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §4/R16/13；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 构建含运行闭包的新REVIEW_ONLY身份包；教师正式目标名与发送门槛分开。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json)；[package_closure_receipt.json](../../../independent_c/package_closure_receipt.json)；[actual_zip_static_receipt.json](../../../independent_documents/actual_zip_static_receipt.json)；[isolated_archive_binding_receipt.json](../../../independent_c/isolated_archive_binding_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 当前包与实际解压FULL的内容等价已核实；剩余为真实Evidence原件/spec/Lock及网页GPT/用户最终审核，未发送教学邮箱。

本轮实际C限定范围：[package_task_receipt.json](../c_review/package_task_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A18 `BLOCKED`；G3-A20 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t201"></a>

## T2-01 分段/过滤参数实验

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 12/14/16题目；13/15/17为空代码单元；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1/4/R06/9；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 四S参数分开及两小网格验证，允许无效候选保留。 规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::split_trajectory（L146）；[geometry.py](../../../../../workflow/geometry.py)::filter_segments（L185）
真实证据：[manifest.json](../../../../goal2/runs/g2-development-parameters-02/manifest.json)；[parameter_records.csv](../../../../goal2/tables/parameter_records.csv)；[stable_intervals.csv](../../../../goal2/tables/stable_intervals.csv)；[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[result_summary.json](../../../result_summary.json)；[full_filter_attribution.json](../../../full_filter_attribution.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-b1bbb223150ba3f1`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,6（三组参数实验）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- PARAM：开发120记录，59唯一配置；评估120记录，14代表配置；重复配置不算新独立样本。 预期：规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 实际：C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。
- S：分段与过滤点数；点终态分母全部1,173,410原始点；记录分母11,386。 预期：同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 实际：R0/S0均25,963段；过滤501,511 / 1,199点。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。 R0/S0均25,963段；过滤501,511 / 1,199点。 完整参数实验不是任一参数普遍最优的证明；未新增本轮调参。 可恢复几何覆盖不等于恢复干净轨迹；source_crs未认证。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t202"></a>

## T2-02 方向阈值参数实验

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；实验完成；无统一新赢家。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 12/14/16题目；13/15/17为空代码单元；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1/4/R06/9；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 同输入改变direction，数量趋势与噪声准确率分开。 规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::direction_candidates（L242）；[geometry.py](../../../../../workflow/geometry.py)::denoise_trajectory（L277）；[geometry.py](../../../../../workflow/geometry.py)::recompute_features（L74）
真实证据：[manifest.json](../../../../goal2/runs/g2-development-parameters-02/manifest.json)；[parameter_records.csv](../../../../goal2/tables/parameter_records.csv)；[stable_intervals.csv](../../../../goal2/tables/stable_intervals.csv)；[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[USER_DECISIONS.json](../../../../goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json)；[exposed_pilot_direction.csv](../../../../goal2/tables/exposed_pilot_direction.csv)；[result_summary.json](../../../result_summary.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-b1bbb223150ba3f1`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,6（三组参数实验）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- PARAM：开发120记录，59唯一配置；评估120记录，14代表配置；重复配置不算新独立样本。 预期：规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 实际：C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。
- D：D删除与不可计算原因逐点保存；方向角单位度，几何工作米。 预期：教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。 实际：全量R0/S0 D删除36,056 / 39,732。记录352/index105由D删除。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。 全量R0/S0 D删除36,056 / 39,732。记录352/index105由D删除。 完整参数实验不是任一参数普遍最优的证明；未新增本轮调参。 删除仅是规则动作，没有真实噪声标签；D前点不属于P误差保证。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t203"></a>

## T2-03 DP容差实验

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；实验完成；无统一新赢家。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 12/14/16题目；13/15/17为空代码单元；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1/4/R06/9；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 固定上游比较完整P输入下的误差与省点；共同预算仍5工作米。 规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::point_segment_distance（L51）；[geometry.py](../../../../../workflow/geometry.py)::douglas_peucker_indices（L206）
真实证据：[manifest.json](../../../../goal2/runs/g2-development-parameters-02/manifest.json)；[parameter_records.csv](../../../../goal2/tables/parameter_records.csv)；[stable_intervals.csv](../../../../goal2/tables/stable_intervals.csv)；[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[result_summary.json](../../../result_summary.json)；[g3-full-production-01_categories_receipt.json](../../../independent_c/g3-full-production-01_categories_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-b1bbb223150ba3f1`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,6（三组参数实验）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- PARAM：开发120记录，59唯一配置；评估120记录，14代表配置；重复配置不算新独立样本。 预期：规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 实际：C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。
- P：P省点率=1-N_P_out/N_P_in；误差只对完整即时P输入，不是raw真值误差。 预期：有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 实际：全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。 全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。 完整参数实验不是任一参数普遍最优的证明；未新增本轮调参。 不能把5工作米预算用于被D先删的原始点或证明真实定位精度。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t204"></a>

## T2-04 三步换序讨论及必要实际比较

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第42页问题；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 10 split→denoise→simplify；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1/4/R07/5.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第42页 / ppt/slides/slide42.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第42页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 原始断点和即时/最终参考不混淆，保留六排列真实负结果。 六排列实际执行；不在S之前暗加切分；核原断点跨越、触发点、方向邻域与最终误差。

**可打开实现和成果：** [g2_pipeline.py](../../../../../workflow/g2_pipeline.py)::run_record（L53）
真实证据：[manifest.json](../../../../goal2/runs/g2-development-orders-02/manifest.json)；[order_configurations.csv](../../../../goal2/tables/order_configurations.csv)；[result_summary.json](../../../../goal2/result_summary.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-861c05af527d8bc1`, `lab1-20337038d9968da1`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,9（六种顺序）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页8（四种危险顺序被拒绝）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- ORDER：DEVELOPMENT每顺序120记录；失败按记录，跨边/窗口另按事件，不混分母。 预期：六排列实际执行；不在S之前暗加切分；核原断点跨越、触发点、方向邻域与最终误差。 实际：D-S-P、D-P-S、P-S-D、P-D-S各有46/87/87/87条安全失败；S-P-D保留为权衡，最终S-D-P。

**审核范围：** 历史内部C回执：[development_orders_epoch02_receipt.json](../../../../goal2/c_contract/development_orders_epoch02_receipt.json)；[evaluation_orders_bound_receipt.json](../../../../goal2/c_contract/evaluation_orders_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json)；[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** D-S-P、D-P-S、P-S-D、P-D-S各有46/87/87/87条安全失败；S-P-D保留为权衡，最终S-D-P。 失败顺序被正确执行；拒绝是规则内研究结果，不修成胜出。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t205"></a>

## T2-05 基于助教系统的实际LLM辅助质量提升工作流

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；批准调整实现；方法收益按结果限定。

**来源与授权：** 教师第26页选做，本项目用户把T2转为必做；具体15/9/12等差异见教学差异表。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第30页 / ppt/slides/slide30.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 继承诊断卡/工具/核验思想，按明确用户合同实现范围内可拒绝的真实工作流。 llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::dispatch（L93）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）；[control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[mode_summary.csv](../../../../goal2/tables/mode_summary.csv)；[model_calls.csv](../../../../goal2/tables/model_calls.csv)；[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`, `lab1-9885083c7a42fa5b`, `lab1-fbec25cdd2a5714e`, `lab1-c8644f76db1f9bfe`, `lab1-93ca26ffa375da77`, `lab1-c3dd4c205df157b5`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,9（四种结构与相同预算）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- MODES：开发24记录×1episode；评估24记录×3episode=每模式72观测，非72独立记录；有效模型派发84批。 预期：llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。 实际：评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 预算上限相同不等于实耗相同；新增记忆没有已证因果收益。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A11 `PASS`；G3-A12 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t206"></a>

## T2-06 结构性不同的四模式及真实search-only零模型调用

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；有实现与结果证据，待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第37页四模式、search-only不调LLM、示范/留出隔离；38页历史结果；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.3/4/R09/8.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第37页 / ppt/slides/slide37.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第37页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 模式的信息权限、反馈与记忆结构不同，search-only用Provider哨兵拒绝调用。 llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::dispatch（L93）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[mode_summary.csv](../../../../goal2/tables/mode_summary.csv)；[model_calls.csv](../../../../goal2/tables/model_calls.csv)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9885083c7a42fa5b`, `lab1-fbec25cdd2a5714e`, `lab1-c8644f76db1f9bfe`, `lab1-93ca26ffa375da77`, `lab1-c3dd4c205df157b5`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,9（四种结构与相同预算）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- MODES：开发24记录×1episode；评估24记录×3episode=每模式72观测，非72独立记录；有效模型派发84批。 预期：llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。 实际：评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。 预算上限相同不等于实耗相同；新增记忆没有已证因果收益。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A12 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t207"></a>

## T2-07 示范记忆、留出只读、泄漏隔离及收益检验

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；实验完成；记忆因果收益未获证实。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第37页四模式、search-only不调LLM、示范/留出隔离；38页历史结果；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.3/4/R09/8.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第37页 / ppt/slides/slide37.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第36页；[实验课1.pptx](../../../../../实验课1.pptx) 物理第37页；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 记忆从60DEMO构建，留出只读；检索消费与因果收益分开。 60条DEMO构建、六特征尺度只从DEMO，完整分区/关联组排除、snapshot hash与写拒绝检查。

**可打开实现和成果：** [g2_memory.py](../../../../../workflow/g2_memory.py)::feature_vector（L8）；[g2_memory.py](../../../../../workflow/g2_memory.py)::build_snapshot（L17）；[g2_memory.py](../../../../../workflow/g2_memory.py)::FrozenMemory（L66）；[g2_memory.py](../../../../../workflow/g2_memory.py)::retrieve（L88）；[g2_memory.py](../../../../../workflow/g2_memory.py)::consumption（L116）
真实证据：[memory_snapshot.json](../../../../goal2/runs/g2-demo-memory-02/memory_snapshot.json)；[memory_consumption.csv](../../../../goal2/tables/memory_consumption.csv)；[memory_independent_mode_comparison.csv](../../../../goal2/tables/memory_independent_mode_comparison.csv)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-629af8a136b6ff25`, `lab1-95890264cce459cd`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,10（记忆被使用，不等于产生因果收益）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页8（不宣称因果质量收益）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- MEMORY：retrieved→eligible→delivered→model_cited→action_consistent分别统计；评估按24记录×3重复。 预期：60条DEMO构建、六特征尺度只从DEMO，完整分区/关联组排除、snapshot hash与写拒绝检查。 实际：60条记忆含26条范围内收益、34无收益；人类知识条目0；评估带/不带记忆均47/72支持输出。

**审核范围：** 历史内部C回执：[memory_epoch02_receipt.json](../../../../goal2/c_contract/memory_epoch02_receipt.json)；[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[navigation_interaction_receipt.json](../../../independent_documents/navigation_interaction_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 60条记忆含26条范围内收益、34无收益；人类知识条目0；评估带/不带记忆均47/72支持输出。 送达或动作一致不证明因果收益，独立真实调用间差异不能只归因记忆。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A06 `INHERITED_NUMERIC_EVIDENCE`；G3-A12 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="t208"></a>

## T2-08 更实用系统的思考与本项目获批增强

**性质/状态：** TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2；批准增强已实现；仍待用户审核。

**来源与授权：** 教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第30页 / ppt/slides/slide30.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 候选/组合/回退、冻结生产、恢复机制和可复算包解决本实验问题；不新增平台。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`；[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A04 `INHERITED_NUMERIC_EVIDENCE`；G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u01"></a>

## U01 教师基础和附加任务优先

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第17–18页；18页异常边p2→p3及两侧点归属；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/4/10/12–13；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/7.2/8.1；[实验课1.pptx](../../../../../实验课1.pptx) 物理第17页 / ppt/slides/slide17.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第18页 / ppt/slides/slide18.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 先覆盖教师要求，用户T2必做范围保留。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-59e8941bd6d66ace`, `lab1-70227bc1defb860d`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-b1bbb223150ba3f1`, `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3,4（分段与短段过滤）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页18（仅长度不足）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,6（三组参数实验）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

父要求送审输入快照时状态：G3-A02 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u02"></a>

## U02 所有增强针对实验一，不脱离轨迹任务

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 不因Task3文件名开展其他课程实验。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`；[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u03"></a>

## U03 研究先于实现，重要规则先确认

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第10–15页；第13页正文和备注；[轨迹数据清洗_学生讲义.pptx](../../../../../作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx) 第4页 JSON 样例与字段/Unix秒声明；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/2/11；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.1/7.1；[实验课1.pptx](../../../../../实验课1.pptx) 第19–20页；20页明确p3方向=p3→p4。详细原句/版本SHA见同名JSON。

**做法与理由：** 历史未知与后续批准分开，不倒写全程已有规则。 26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[Task1_Source_Audit_2025_2026_Merged.json](../../../../../docs/research/Task1_Source_Audit_2025_2026_Merged.json)；[Task1_Literature_Review_2025_2026_Merged.md](../../../../../docs/research/Task1_Literature_Review_2025_2026_Merged.md)；[A_CANDIDATE_RATIONALE.md](../../../A_CANDIDATE_RATIONALE.md)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-808a658dbf451d38`, `lab1-f7fe7424c6193f77`, `lab1-36a4e3074ee2fa99`, `lab1-9d637e0bfc2f7ff6`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3（时间、坐标与可计算性）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,18（扩大范围的工作坐标核验与限制）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（坐标来源缺失没有被假标签补齐）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（方向异常候选的单次同时删除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（方向规则的计算顺序先确认，再执行）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- SOURCE：来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。 预期：26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 实际：正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A06 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u04"></a>

## U04 检索与实验相关的高质量论文，不泛查Multi-Agent

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 已归档研究围绕轨迹质量/简化/指标与选择偏差，没有本轮通用Agent检索。 26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。

**可打开实现和成果：** 本条为文献/治理要求，不编造算法函数。
真实证据：[Task1_Source_Audit_2025_2026_Merged.json](../../../../../docs/research/Task1_Source_Audit_2025_2026_Merged.json)；[Task1_Literature_Review_2025_2026_Merged.md](../../../../../docs/research/Task1_Literature_Review_2025_2026_Merged.md)；[A_CANDIDATE_RATIONALE.md](../../../A_CANDIDATE_RATIONALE.md)。

**对照、分母与实际结果：**
- SOURCE：来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。 预期：26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 实际：正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。

**审核范围：** 历史内部C回执：[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。 正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u05"></a>

## U05 更新2025/2026来源并与旧研究整合

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 旧22论文/4官方文档索引保留出版年/会议年和访问限制，不重开广泛搜索。 26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。

**可打开实现和成果：** 本条为文献/治理要求，不编造算法函数。
真实证据：[Task1_Source_Audit_2025_2026_Merged.json](../../../../../docs/research/Task1_Source_Audit_2025_2026_Merged.json)；[Task1_Literature_Review_2025_2026_Merged.md](../../../../../docs/research/Task1_Literature_Review_2025_2026_Merged.md)；[A_CANDIDATE_RATIONALE.md](../../../A_CANDIDATE_RATIONALE.md)。

**对照、分母与实际结果：**
- SOURCE：来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。 预期：26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 实际：正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。

**审核范围：** 历史内部C回执：[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。 正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u06"></a>

## U06 说明各来源与任务关联、可迁移点及风险

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** literature_use_map逐项区分支持命题、实际位置、未采用与风险。 26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。

**可打开实现和成果：** 本条为文献/治理要求，不编造算法函数。
真实证据：[Task1_Source_Audit_2025_2026_Merged.json](../../../../../docs/research/Task1_Source_Audit_2025_2026_Merged.json)；[Task1_Literature_Review_2025_2026_Merged.md](../../../../../docs/research/Task1_Literature_Review_2025_2026_Merged.md)；[A_CANDIDATE_RATIONALE.md](../../../A_CANDIDATE_RATIONALE.md)。

**对照、分母与实际结果：**
- SOURCE：来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。 预期：26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 实际：正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。

**审核范围：** 历史内部C回执：[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。 正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u07"></a>

## U07 少量有用文献，不强制复现、采用或数量凑数

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 正式报告仅引用真正支持命题的来源，未为凑2–4篇新增算法。 26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。

**可打开实现和成果：** 本条为文献/治理要求，不编造算法函数。
真实证据：[Task1_Source_Audit_2025_2026_Merged.json](../../../../../docs/research/Task1_Source_Audit_2025_2026_Merged.json)；[Task1_Literature_Review_2025_2026_Merged.md](../../../../../docs/research/Task1_Literature_Review_2025_2026_Merged.md)；[A_CANDIDATE_RATIONALE.md](../../../A_CANDIDATE_RATIONALE.md)。

**对照、分母与实际结果：**
- SOURCE：来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。 预期：26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 实际：正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。

**审核范围：** 历史内部C回执：[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。 正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u08"></a>

## U08 多候选实际尝试，以结果选择

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 12/14/16题目；13/15/17为空代码单元；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1/4/R06/9；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则。详细原句/版本SHA见同名JSON。

**做法与理由：** 历史开发/选择真实比较，并非主观直接指定S0。 规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[manifest.json](../../../../goal2/runs/g2-development-parameters-02/manifest.json)；[parameter_records.csv](../../../../goal2/tables/parameter_records.csv)；[stable_intervals.csv](../../../../goal2/tables/stable_intervals.csv)；[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-b1bbb223150ba3f1`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,6（三组参数实验）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- PARAM：开发120记录，59唯一配置；评估120记录，14代表配置；重复配置不算新独立样本。 预期：规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。 实际：C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 完整参数实验不是任一参数普遍最优的证明；未新增本轮调参。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A05 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u09"></a>

## U09 单项验证先于组合

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** G0单项经C核验准入后再组合；S两个过滤父项有移除对照。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[development_closure_receipt.json](../../../independent_c/development_closure_receipt.json)；[selection_failure_receipt.json](../../../independent_c/selection_failure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A04 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u10"></a>

## U10 有益保留、退化拒绝/回退

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 选择集组合三条保护失败后回退S0，不把开发获胜固化。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A04 `INHERITED_NUMERIC_EVIDENCE`；G3-A05 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u11"></a>

## U11 共同评选尺度与方法专项审核并存

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第21–23页；22页线段距离及严格大于阈值；23页16帧演示；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/2/8/10/16–18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/5.3/8.1–8.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第21页 / ppt/slides/slide21.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第22页 / ppt/slides/slide22.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 共同覆盖/几何/断点保护之外，P另审完整即时输入预算。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）；[geometry.py](../../../../../workflow/geometry.py)::point_segment_distance（L51）；[geometry.py](../../../../../workflow/geometry.py)::douglas_peucker_indices（L206）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[g3-full-production-01_categories_receipt.json](../../../independent_c/g3-full-production-01_categories_receipt.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-cd82900c2901ee9f`, `lab1-5edb2858a06036d2`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（有限线段的 DP 简化）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（P 的局部指标与整体指标分开）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。
- P：P省点率=1-N_P_out/N_P_in；误差只对完整即时P输入，不是raw真值误差。 预期：有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 实际：全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。 不能把5工作米预算用于被D先删的原始点或证明真实定位精度。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A05 `INHERITED_NUMERIC_EVIDENCE`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u12"></a>

## U12 参数、方法、审核和结论有来源或实验证据

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第10–15页；第13页正文和备注；[轨迹数据清洗_学生讲义.pptx](../../../../../作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx) 第4页 JSON 样例与字段/Unix秒声明；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/2/11；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.1/7.1；[实验课1.pptx](../../../../../实验课1.pptx) 第26页必做第2项；第24–25页示例保留比例。详细原句/版本SHA见同名JSON。

**做法与理由：** 来源、批准合同和当前真实产物分层绑定。 26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[Task1_Source_Audit_2025_2026_Merged.json](../../../../../docs/research/Task1_Source_Audit_2025_2026_Merged.json)；[Task1_Literature_Review_2025_2026_Merged.md](../../../../../docs/research/Task1_Literature_Review_2025_2026_Merged.md)；[A_CANDIDATE_RATIONALE.md](../../../A_CANDIDATE_RATIONALE.md)；[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-808a658dbf451d38`, `lab1-f7fe7424c6193f77`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`, `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-b1bbb223150ba3f1`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3（时间、坐标与可计算性）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,18（扩大范围的工作坐标核验与限制）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（坐标来源缺失没有被假标签补齐）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,6（三组参数实验）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- SOURCE：来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。 预期：26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。 实际：正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u13"></a>

## U13 不换指标、挑样本、隐瞒失败追求漂亮结果

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页必做第2项；第24–25页示例保留比例；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.3/5.4/8.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第24页 / ppt/slides/slide24.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第25页 / ppt/slides/slide25.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 分区/指标预冻结，危险顺序、DP负结果与266工作米边界保留。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 六排列实际执行；不在S之前暗加切分；核原断点跨越、触发点、方向邻域与最终误差。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）；[g2_pipeline.py](../../../../../workflow/g2_pipeline.py)::run_record（L53）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[manifest.json](../../../../goal2/runs/g2-development-orders-02/manifest.json)；[order_configurations.csv](../../../../goal2/tables/order_configurations.csv)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`, `lab1-a9f52ff7ca75f7f2`, `lab1-62885400114d7d2b`, `lab1-861c05af527d8bc1`, `lab1-20337038d9968da1`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,9（六种顺序）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页8（四种危险顺序被拒绝）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。
- ORDER：DEVELOPMENT每顺序120记录；失败按记录，跨边/窗口另按事件，不混分母。 预期：六排列实际执行；不在S之前暗加切分；核原断点跨越、触发点、方向邻域与最终误差。 实际：D-S-P、D-P-S、P-S-D、P-D-S各有46/87/87/87条安全失败；S-P-D保留为权衡，最终S-D-P。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[development_orders_epoch02_receipt.json](../../../../goal2/c_contract/development_orders_epoch02_receipt.json)；[evaluation_orders_bound_receipt.json](../../../../goal2/c_contract/evaluation_orders_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 D-S-P、D-P-S、P-S-D、P-D-S各有46/87/87/87条安全失败；S-P-D保留为权衡，最终S-D-P。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。 失败顺序被正确执行；拒绝是规则内研究结果，不修成胜出。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A04 `INHERITED_NUMERIC_EVIDENCE`；G3-A06 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u14"></a>

## U14 不要求复杂方案、论文方法、记忆机制必然获胜

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第37页四模式、search-only不调LLM、示范/留出隔离；38页历史结果；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.3/4/R09/8.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第37页 / ppt/slides/slide37.xml；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则。详细原句/版本SHA见同名JSON。

**做法与理由：** 无统一方向/DP赢家、记忆未证增益和组合退化都保留。 60条DEMO构建、六特征尺度只从DEMO，完整分区/关联组排除、snapshot hash与写拒绝检查。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [g2_memory.py](../../../../../workflow/g2_memory.py)::feature_vector（L8）；[g2_memory.py](../../../../../workflow/g2_memory.py)::build_snapshot（L17）；[g2_memory.py](../../../../../workflow/g2_memory.py)::FrozenMemory（L66）；[g2_memory.py](../../../../../workflow/g2_memory.py)::retrieve（L88）；[g2_memory.py](../../../../../workflow/g2_memory.py)::consumption（L116）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[memory_snapshot.json](../../../../goal2/runs/g2-demo-memory-02/memory_snapshot.json)；[memory_consumption.csv](../../../../goal2/tables/memory_consumption.csv)；[memory_independent_mode_comparison.csv](../../../../goal2/tables/memory_independent_mode_comparison.csv)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-629af8a136b6ff25`, `lab1-95890264cce459cd`, `lab1-1b0102fcff5af1af`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`；[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,10（记忆被使用，不等于产生因果收益）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页8（不宣称因果质量收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- MEMORY：retrieved→eligible→delivered→model_cited→action_consistent分别统计；评估按24记录×3重复。 预期：60条DEMO构建、六特征尺度只从DEMO，完整分区/关联组排除、snapshot hash与写拒绝检查。 实际：60条记忆含26条范围内收益、34无收益；人类知识条目0；评估带/不带记忆均47/72支持输出。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[memory_epoch02_receipt.json](../../../../goal2/c_contract/memory_epoch02_receipt.json)；[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 60条记忆含26条范围内收益、34无收益；人类知识条目0；评估带/不带记忆均47/72支持输出。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 送达或动作一致不证明因果收益，独立真实调用间差异不能只归因记忆。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A04 `INHERITED_NUMERIC_EVIDENCE`；G3-A12 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u15"></a>

## U15 工作流涵盖研究、执行、审核、优化及交付全过程

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 父任务维护依赖、修复、重建与发布；局部回执不是结束条件。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)；[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`, `lab1-b9a7a9bb893c339f`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（本轮独立C：当前Experiment22页和Process12页实际200dpi逐页查看与关键内容核查；不代Evidence Master或网页GPT。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`；G3-A19 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u16"></a>

## U16 Agent实际组织计算与实验，不只提出建议

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 原生A/B/C任务与工具/控制器真实记录绑定实际run。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u17"></a>

## U17 Agent宁少勿滥，不将普通函数改名冒充Agent

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 只有三个治理职责，确定性工具和控制器不称LLM Agent。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u18"></a>

## U18 角色输入输出、工具、状态、权限和交接明确

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页选做；第28–40页助教系统；[任务3_LLM辅助评估清洗.ipynb](../../../../../作业/作业/任务3_LLM辅助评估清洗.ipynb) Cell 6/21显式Mock；Cell 30环境切换说明；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §6/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第28页 / ppt/slides/slide28.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** TaskPlan、回执、目标哈希、拒绝及恢复由接口限定。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（网页 GPT 二重审核）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json)；[evaluation_modes_complete_receipt.json](../../../../goal2/c_contract/evaluation_modes_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`；G3-A17 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u19"></a>

## U19 Verifier真正检查可信参考与目标产物，能拒绝错误

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页必做第2项；第24–25页示例保留比例；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.3/5.4/8.2；[实验课1.pptx](../../../../../实验课1.pptx) 物理第24页 / ppt/slides/slide24.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第25页 / ppt/slides/slide25.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 独立C读raw/合同/trace，故障注入和真实目标绑定拒绝均留证。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）；[control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[context_closure_epoch02.json](../../../../goal2/c_contract/context_closure_epoch02.json)；[retry_classifier_closure_epoch02.json](../../../../goal2/c_contract/retry_classifier_closure_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A10 `PASS`；G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u20"></a>

## U20 修复是工作流一部分，不能发现问题就返回

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.2/6.2/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 第30/35/37页工具与核验思想；当前三角色为用户要求；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 历史哈希/Notebook/图形修复均回归再恢复；本轮普通问题留本任务消化。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[context_closure_epoch02.json](../../../../goal2/c_contract/context_closure_epoch02.json)；[retry_classifier_closure_epoch02.json](../../../../goal2/c_contract/retry_classifier_closure_epoch02.json)；[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[ai_null_closure_receipt.json](../../../../goal2/c_contract/ai_null_closure_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（本轮独立C：当前Experiment22页和Process12页实际200dpi逐页查看与关键内容核查；不代Evidence Master或网页GPT。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`；G3-A19 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u21"></a>

## U21 对完整父Goal持续负责，不把局部任务结束当完成

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.2/6.2/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 第30/35/37页工具与核验思想；当前三角色为用户要求；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11。详细原句/版本SHA见同名JSON。

**做法与理由：** 三阶段G3收尾仍属父Goal，不新增Goal4或NEXT_PROMPT。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)；[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`, `lab1-b9a7a9bb893c339f`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（本轮独立C：当前Experiment22页和Process12页实际200dpi逐页查看与关键内容核查；不代Evidence Master或网页GPT。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`；G3-A19 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u22"></a>

## U22 最小必要人工介入，批准规则后自主执行

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.2/6.2/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 第30/35/37页工具与核验思想；当前三角色为用户要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 已批准候选预算/保护内自动裁决；研究定义变化才升级。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`；[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-bd932b47abf15ad3`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A05 `INHERITED_NUMERIC_EVIDENCE`；G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u23"></a>

## U23 不凭主观直接选最优，由有效比较裁决

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 冻结选择规则后读真实选择/确认结果；不宣称全局最优。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`, `lab1-1f19e084af1084c5`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,16（先冻结，再执行一次性最终确认）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（最终确认：执行预设门控，不再选参数）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A05 `INHERITED_NUMERIC_EVIDENCE`；G3-A07 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u24"></a>

## U24 迭代有范围、预算和停止理由，不无限搜索

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 11策略定义、1新结构单项和3组合；第二删除保护因无合理定义未准入。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-62885400114d7d2b`, `lab1-af84ab9d9153c3c7`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（未证明单项统一收益）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,13（单项先行，再检查组合与移除）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（接受实际组合，拒绝无贡献的附加项）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A03 `INHERITED_NUMERIC_EVIDENCE`；G3-A04 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u25"></a>

## U25 总体三个大Goal，减少反复转发；保留早期真实返工历史

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.2/6.2/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 第30/35/37页工具与核验思想；当前三角色为用户要求；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11。详细原句/版本SHA见同名JSON。

**做法与理由：** G1/G2/G3仍同实验，早期revisions与失败回执不覆盖。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`, `lab1-b9a7a9bb893c339f`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A01 `PASS`；G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u26"></a>

## U26 retry/fallback/escalation/stop与恢复真实，不只画图

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.2/6.2/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 第30/35/37页工具与核验思想；当前三角色为用户要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.1–0.3/5.4/9；[SMART_CITIES_RESEARCH_PROTOCOL.md](../../../../../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md) §§E–F及来源/UNRESOLVED规则；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 真实中断/错误分类修复与选择回退留证；未触发R0最终发布门控不说曾触发。 真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [control.py](../../../../../goal3/control.py)::submit（L69）；[control.py](../../../../../goal3/control.py)::accept（L78）；[control.py](../../../../../goal3/control.py)::issue（L102）；[control.py](../../../../../goal3/control.py)::repair（L110）；[control.py](../../../../../goal3/control.py)::close_issue（L120）；[control.py](../../../../../goal3/control.py)::invalidate_changed（L138）；[control.py](../../../../../goal3/control.py)::checkpoint（L152）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[PROCESS_RECORD.md](../../../../goal2/PROCESS_RECORD.md)；[goal_state.json](../review_input_snapshot/goal_state.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[NB01_attempt2_impact.json](../../../repairs/NB01_attempt2_impact.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`；[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-bd932b47abf15ad3`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,5（真实缺陷如何进入修复与恢复）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（G3 的实际推进与最终决定）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,14（选择集上的保护失败使开发组合退出）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页16（数据划分先于本轮方法比较保存）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,9（选择阶段：开发中有支持的组件仍可退出）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- WORKFLOW：审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。 预期：真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。 实际：历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[candidate_lock_epoch02_receipt.json](../../../../goal2/c_contract/candidate_lock_epoch02_receipt.json)；[single_candidate_confirmation_receipt.json](../../../../goal2/c_contract/single_candidate_confirmation_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A04 `INHERITED_NUMERIC_EVIDENCE`；G3-A11 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u27"></a>

## U27 原始材料、starter、原始数据和历史有效结果保留

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第10–15页；第13页正文和备注；[轨迹数据清洗_学生讲义.pptx](../../../../../作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx) 第4页 JSON 样例与字段/Unix秒声明；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/2/11；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.1/7.1；[实验课1.pptx](../../../../../实验课1.pptx) 第26页压缩包、邮箱、命名、10月5日前；第43页联系邮箱。详细原句/版本SHA见同名JSON。

**做法与理由：** 新完成版/新ZIP与旧教师文件分开；原件哈希核验。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-808a658dbf451d38`, `lab1-f7fe7424c6193f77`, `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3（时间、坐标与可计算性）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,18（扩大范围的工作坐标核验与限制）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（坐标来源缺失没有被假标签补齐）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json)；[initial_inventory_receipt.json](../../../independent_c/initial_inventory_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A01 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u28"></a>

## U28 尊重但核查starter、默认数值、Mock及历史演示

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第17–18页；18页异常边p2→p3及两侧点归属；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/4/10/12–13；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.2/7.2/8.1；[实验课1.pptx](../../../../../实验课1.pptx) 物理第17页 / ppt/slides/slide17.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第18页 / ppt/slides/slide18.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** TODO/索引/直线投影/Mock/类型统计疑点按来源核查，不盲继承。 同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。

**可打开实现和成果：** [geometry.py](../../../../../workflow/geometry.py)::split_trajectory（L146）；[geometry.py](../../../../../workflow/geometry.py)::filter_segments（L185）；[geometry.py](../../../../../workflow/geometry.py)::point_segment_distance（L51）；[geometry.py](../../../../../workflow/geometry.py)::douglas_peucker_indices（L206）；[g2_modes.py](../../../../../workflow/g2_modes.py)::dispatch（L93）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）
真实证据：[result_summary.json](../../../result_summary.json)；[full_filter_attribution.json](../../../full_filter_attribution.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[g3-full-production-01_categories_receipt.json](../../../independent_c/g3-full-production-01_categories_receipt.json)；[result_summary.json](../../../../goal2/result_summary.json)；[mode_summary.csv](../../../../goal2/tables/mode_summary.csv)；[model_calls.csv](../../../../goal2/tables/model_calls.csv)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-59e8941bd6d66ace`, `lab1-70227bc1defb860d`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-cd82900c2901ee9f`, `lab1-5edb2858a06036d2`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-e4873cb18864735b`, `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3,4（分段与短段过滤）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页18（仅长度不足）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,4（有限线段的 DP 简化）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（P 的局部指标与整体指标分开）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,4（治理角色、处理工具与控制器怎样分工）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,6（Native 协作证据只按实际可读范围保存）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- S：分段与过滤点数；点终态分母全部1,173,410原始点；记录分母11,386。 预期：同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。 实际：R0/S0均25,963段；过滤501,511 / 1,199点。
- P：P省点率=1-N_P_out/N_P_in；误差只对完整即时P输入，不是raw真值误差。 预期：有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。 实际：全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。
- MODES：开发24记录×1episode；评估24记录×3episode=每模式72观测，非72独立记录；有效模型派发84批。 预期：llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。 实际：评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。

**审核范围：** 历史内部C回执：[development_parameters_epoch02_receipt.json](../../../../goal2/c_contract/development_parameters_epoch02_receipt.json)；[evaluation_parameters_bound_receipt.json](../../../../goal2/c_contract/evaluation_parameters_bound_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[development_modes_epoch02_receipt.json](../../../../goal2/c_contract/development_modes_epoch02_receipt.json)；[evaluation_freeze_epoch02_receipt.json](../../../../goal2/c_contract/evaluation_freeze_epoch02_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** R0/S0均25,963段；过滤501,511 / 1,199点。 全量R0/S0 P删除435,373 / 911,330；两者即时max=4.999963549工作米。 评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。 可恢复几何覆盖不等于恢复干净轨迹；source_crs未认证。 不能把5工作米预算用于被D先删的原始点或证明真实定位精度。 预算上限相同不等于实耗相同；新增记忆没有已证因果收益。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（本轮身份/包12测试及10子测试、四FULL全部单元与来源闭包、真实修复独立核对；数值数学正确性历史证据保持继承。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A02 `PENDING`；G3-A10 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u29"></a>

## U29 不伪造运行、模型输出、截图、用户判断或决策历史

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第6页单位/经纬度/插值示例及反例、前后指标、拒绝原因要求；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §8/9/10；[WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md](../../../../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) 真实互动证据及Evidence Master边界；[实验课1.pptx](../../../../../实验课1.pptx) 物理第6页 / ppt/slides/slide6.xml；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则。详细原句/版本SHA见同名JSON。

**做法与理由：** 真实AI响应、合成反例、系统裁决和用户授权分别标记。 引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** [g2_modes.py](../../../../../workflow/g2_modes.py)::validate_response（L51）；[g2_modes.py](../../../../../workflow/g2_modes.py)::run_batch_episode（L136）
真实证据：[actual_ai_critique.json](../../../../goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json)；[manifest.json](../../../../goal2/counterexamples/formal-02/manifest.json)；[ai_legal_proposal_tradeoffs.csv](../../../../goal2/tables/ai_legal_proposal_tradeoffs.csv)；[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-02361194ac55bb28`, `lab1-2eaa006465170263`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-02de2176540c11fb`, `lab1-e4e3f3e47d311987`, `lab1-65870bb6cd4183c2`, `lab1-f711eb1ab5723d3f`, `lab1-b9a7a9bb893c339f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,11（AI 建议的技术批判与可复验反例）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,8（一次真实 AI 建议怎样变成负结果）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1（吴博闻）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,11（互动证据仍需哪些真实输入）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- AI：记录7764同122个共同覆盖点的max；6组合成例、19处理链、25已知答案检查不作为总体样本。 预期：引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。 实际：真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[counterexamples_epoch02_receipt.json](../../../../goal2/c_contract/counterexamples_epoch02_receipt.json)；[counterexamples_complete_receipt.json](../../../../goal2/c_contract/counterexamples_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 原模型没有承诺真值准确率；不伪造用户拒绝、非法提议或自然噪声标签。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[CL-C01_closure.json](../c_review/CL-C01_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C02_closure.json](../c_review/CL-C02_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[CL-C03_closure.json](../c_review/CL-C03_closure.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（三项CL问题已独立闭合；SIGTERM触发来源unknown，同源新内核真实重试成功，不将中断说成数学缺陷。）；[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A11 `PASS`；G3-A16 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u30"></a>

## U30 时空语义、单位、不可计算性与样本边界明确

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第10–15页；第13页正文和备注；[轨迹数据清洗_学生讲义.pptx](../../../../../作业/作业/build_ppt/out/轨迹数据清洗_学生讲义.pptx) 第4页 JSON 样例与字段/Unix秒声明；[作业1轨迹数据预处理.ipynb](../../../../../作业/作业/作业1轨迹数据预处理.ipynb) Cell 1/2/11；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §5.1/7.1；[实验课1.pptx](../../../../../实验课1.pptx) 第26页必做第2项；第24–25页示例保留比例。详细原句/版本SHA见同名JSON。

**做法与理由：** source_crs UNVERIFIED、固定条件化ENU、raw记录非独立用户，null保存原因。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。

**可打开实现和成果：** [g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）；[selection.py](../../../../../goal3/selection.py)::paired（L7）；[selection.py](../../../../../goal3/selection.py)::aggregate_pairs（L62）；[selection.py](../../../../../goal3/selection.py)::choose（L83）
真实证据：[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)；[A3_DECISION.json](../../../A3_DECISION.json)；[selection_freeze.json](../../../selection_freeze.json)；[selection_decision.json](../../../selection_decision.json)；[final_freeze.json](../../../final_freeze.json)；[release_decision.json](../../../release_decision.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-808a658dbf451d38`, `lab1-f7fe7424c6193f77`, `lab1-3d2a4363f7210eab`, `lab1-b319a6d191116aea`, `lab1-2eea667361800a14`, `lab1-1f19e084af1084c5`, `lab1-bd932b47abf15ad3`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-f711eb1ab5723d3f`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,3（时间、坐标与可计算性）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,18（扩大范围的工作坐标核验与限制）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（坐标来源缺失没有被假标签补齐）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,5（原始窗口、覆盖与几何偏差）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页8（共同覆盖点）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页17（全量实际尝试）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,16（先冻结，再执行一次性最终确认）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（最终确认：执行预设门控，不再选参数）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,17（冻结策略下的全部原始记录生产）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,10（生产与交付继续按冻结策略执行）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。
- SELECT：开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。 预期：单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。 实际：S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。

**审核范围：** 历史内部C回执：[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json)；[coordinate_complete_receipt.json](../../../../goal2/c_contract/coordinate_complete_receipt.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[contract_split_receipt.json](../../../independent_c/contract_split_receipt.json)；[g3-final-confirm-01_freeze_boundary_receipt.json](../../../independent_c/g3-final-confirm-01_freeze_boundary_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。 冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A06 `INHERITED_NUMERIC_EVIDENCE`；G3-A09 `INHERITED_NUMERIC_EVIDENCE`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u31"></a>

## U31 内部审核后发布，网页GPT读取真实远程二重验收

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §11–13/15；[AGENTS.md](../../../../../../AGENTS.md) §§18/20；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 本轮内部验收与新网页GPT待审分开，旧技术接受不补签新PDF/ZIP。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（网页 GPT 二重审核）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json)；[internal_acceptance_receipt.json](../../../independent_c/internal_acceptance_receipt.json)；[publication_preflight_receipt.json](../../../independent_documents/publication_preflight_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（本轮独立C：当前Experiment22页和Process12页实际200dpi逐页查看与关键内容核查；不代Evidence Master或网页GPT。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A19 `PENDING`；G3-A20 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u32"></a>

## U32 GitHub完整工程与教师最小提交包分开

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页压缩包、邮箱、命名、10月5日前；第43页联系邮箱；[AGENTS.md](../../../../../../AGENTS.md) §18 GitHub与Submission Package分工；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §4/R16/13；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 原始研究/负结果/图源留GitHub；ZIP含真正必要执行闭包。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json)；[package_closure_receipt.json](../../../independent_c/package_closure_receipt.json)；[actual_zip_static_receipt.json](../../../independent_documents/actual_zip_static_receipt.json)；[isolated_archive_binding_receipt.json](../../../independent_c/isolated_archive_binding_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[package_task_receipt.json](../c_review/package_task_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A18 `BLOCKED`；G3-A20 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u33"></a>

## U33 用户工作区、依赖环境、安全和原有文件受保护

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页压缩包、邮箱、命名、10月5日前；第43页联系邮箱；[AGENTS.md](../../../../../../AGENTS.md) §18 GitHub与Submission Package分工；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §4/R16/13；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 复用.venv、旧未跟踪ZIP保持、安装与配置变化实际登记。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json)；[initial_inventory_receipt.json](../../../independent_c/initial_inventory_receipt.json)；[package_closure_receipt.json](../../../independent_c/package_closure_receipt.json)；[actual_zip_static_receipt.json](../../../independent_documents/actual_zip_static_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[package_task_receipt.json](../c_review/package_task_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A01 `PASS`；G3-A18 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u34"></a>

## U34 Notebook新内核可运行，LIVE/复算/历史分开

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 仓库与同ZIP各新内核FULL；保存真实提议重放，Provider新增0。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)（当前两Notebook各在仓库和同一ZIP解压目录新内核FULL，12/8/12/8单元；C分别读全部285分片、逐点终态和历史注册表，新增记录级调用0。）；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[package_task_receipt.json](../c_review/package_task_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A13 `PASS`；G3-A18 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u35"></a>

## U35 图表回答问题，真实、清晰、可复现和可编辑

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/4/R14；[SMART_CITIES_VISUAL_SYSTEM.md](../../../../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md) §§11–14及P2规则；[SKILL.md](../../../../../../tools/skills/publication-plots/SKILL.md) 科研制图及相关references；[p2_cloud_sorbet_colors.tex](../../../../../../templates/latex/common/p2_cloud_sorbet_colors.tex) P2颜色源；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 真实结果源生成参数/选择/全量/边界图，修布局不改数值关系。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::common_reference_metrics（L64）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::record_metrics（L153）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::summarize（L241）；[g2_metrics.py](../../../../../workflow/g2_metrics.py)::review_record（L392）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)；[result_summary.json](../../../../goal2/result_summary.json)；[result_summary.json](../../../result_summary.json)；[production_closure_receipt.json](../../../independent_c/production_closure_receipt.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-b319a6d191116aea`, `lab1-62885400114d7d2b`, `lab1-b1bbb223150ba3f1`, `lab1-20337038d9968da1`, `lab1-2eaa006465170263`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-e4873cb18864735b`, `lab1-c8644f76db1f9bfe`, `lab1-95890264cce459cd`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页20（图 10）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页10（实际规则内方法决定的路径）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。
- METRIC：coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。 预期：共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。 实际：全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[figures_current_closure.json](../../../independent_documents/figures_current_closure.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 全量共同覆盖671,899→1,172,211；显式200,470→221,149；无输出4,859→0。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。 无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前7图31targets/13sources独立闭合；数据关系未变，原生源可编辑；新Notebook图另核。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（当前7图31targets/13sources独立闭合；数据关系未变，原生源可编辑；新Notebook图另核。）；[notebook_figure_visual_receipt.json](../c_review/notebook_figure_visual_receipt.json)（当前7图31targets/13sources独立闭合；数据关系未变，原生源可编辑；新Notebook图另核。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A14 `PASS`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u36"></a>

## U36 draw.io结构源、publication-plots、固定P2及XeLaTeX

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/4/R14；[SMART_CITIES_VISUAL_SYSTEM.md](../../../../../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md) §§11–14及P2规则；[SKILL.md](../../../../../../tools/skills/publication-plots/SKILL.md) 科研制图及相关references；[p2_cloud_sorbet_colors.tex](../../../../../../templates/latex/common/p2_cloud_sorbet_colors.tex) P2颜色源；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 任务副本共享P2，结构源可编辑；已装字体不打包。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-b319a6d191116aea`, `lab1-62885400114d7d2b`, `lab1-b1bbb223150ba3f1`, `lab1-20337038d9968da1`, `lab1-2eaa006465170263`, `lab1-bd932b47abf15ad3`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-e4873cb18864735b`, `lab1-c8644f76db1f9bfe`, `lab1-95890264cce459cd`, `lab1-16c26970dd41618a`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页20（图 10）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页10（实际规则内方法决定的路径）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[figures_current_closure.json](../../../independent_documents/figures_current_closure.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）；[notebook_figure_visual_receipt.json](../c_review/notebook_figure_visual_receipt.json)（当前7图31targets/13sources独立闭合；数据关系未变，原生源可编辑；新Notebook图另核。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A14 `PASS`；G3-A15 `PASS`；G3-A16 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u37"></a>

## U37 Experiment/Process两份报告职责独立，不机械复制

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 实验报告讲方法结果，过程报告讲工作流和真实决定；互动缺项不取消报告。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)；[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`, `lab1-65870bb6cd4183c2`, `lab1-f711eb1ab5723d3f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A15 `PASS`；G3-A16 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u38"></a>

## U38 文档自然具体清楚，避免内部日志与空泛AI口吻堆砌

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 正文保留必要定义/限制，内部验收表仅作复盘资料；全文精修由B/C核。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`, `lab1-65870bb6cd4183c2`, `lab1-f711eb1ab5723d3f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（当前Experiment22页身份、构建、全文数值/来源与每页实际200dpi视觉核验完成；仅内部工程范围，新网页GPT和用户待审。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A15 `PASS`；G3-A16 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u39"></a>

## U39 Original Evidence First，真实人类贡献可追溯

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；外部待补：正式互动证据未闭合。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 真实授权/响应可索引，未提供的历史聊天不得重构成原生证据。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** 本条为文献/治理要求，不编造算法函数。
真实证据：[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1（吴博闻）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,11（互动证据仍需哪些真实输入）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[process_report_current_closure.json](../../../independent_documents/process_report_current_closure.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** Evidence Master提供原件与批准呈现spec，后续实际工程检查和Lock。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A16 `BLOCKED`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u40"></a>

## U40 Evidence Master与Research Conversation/工程职责分离

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；外部待补：正式互动证据未闭合。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 本轮A/B/C均无权选择用户anchor、高亮、因果箭头或Lock。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** 本条为文献/治理要求，不编造算法函数。
真实证据：[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1（吴博闻）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,11（互动证据仍需哪些真实输入）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[process_report_current_closure.json](../../../independent_documents/process_report_current_closure.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** Evidence Master提供原件与批准呈现spec，后续实际工程检查和Lock。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A16 `BLOCKED`；G3-A17 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u41"></a>

## U41 技术与互动两份Handoff

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §0.2/6.2/7.3；[实验课1.pptx](../../../../../实验课1.pptx) 第30/35/37页工具与核验思想；当前三角色为用户要求。详细原句/版本SHA见同名JSON。

**做法与理由：** 技术交复算；互动交候选事实与缺项，二者分别保持边界。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)；[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-65870bb6cd4183c2`, `lab1-f711eb1ab5723d3f`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1（吴博闻）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,11（互动证据仍需哪些真实输入）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（网页 GPT 二重审核）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

父要求送审输入快照时状态：G3-A17 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u42"></a>

## U42 11文件分发集与普通任务附件分开，不冒称UI已上传

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；有工程/来源证据，待用户审核。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第26页压缩包、邮箱、命名、10月5日前；第43页联系邮箱；[AGENTS.md](../../../../../../AGENTS.md) §18 GitHub与Submission Package分工；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §4/R16/13；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml；[USER_PROMPT.md](../../../USER_PROMPT.md) 原G3批准范围；只继承未被本轮覆盖的内容。详细原句/版本SHA见同名JSON。

**做法与理由：** 本轮以既有sync_sources.py --check核对EXACTLY11和active/bundle字节及manifest；身份/总账/ZIP属于任务成果，不进入固定11文件集合。 本轮实际执行既有sync_sources.py --check，只读核对固定allowlist、普通文件集合、active与bundle字节、Skill原始分发与installed effective members及内部manifest。

**可打开实现和成果：** [sync_sources.py](../../../../../../evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py)::source_rows（L65）；[sync_sources.py](../../../../../../evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py)::verify_bundle（L78）；[sync_sources.py](../../../../../../evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py)::verify_manifest（L115）；[sync_sources.py](../../../../../../evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py)::verify_skill（L41）
真实证据：[upload_bundle_check_output.txt](../upload_bundle_check_output.txt)；[SOURCE_MANIFEST.md](../../../../../../evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md)；[AGENTS.md](../../../../../../AGENTS.md)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- UPLOAD_BUNDLE：固定11文件；集合与canonical命名必须完全相等；SHA256逐项相同；身份、review指南和任务ZIP不加入集合。 预期：本轮实际执行既有sync_sources.py --check，只读核对固定allowlist、普通文件集合、active与bundle字节、Skill原始分发与installed effective members及内部manifest。 实际：本轮--check真实输出UPLOAD_BUNDLE_CONTENT: PASS; EXACTLY 11; internal manifest verified；未修改固定11文件集合。

**审核范围：** 历史内部C回执：[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json)；[initial_inventory_receipt.json](../../../independent_c/initial_inventory_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮--check真实输出UPLOAD_BUNDLE_CONTENT: PASS; EXACTLY 11; internal manifest verified；未修改固定11文件集合。 仅证明仓库Upload-Ready Bundle与active来源一致；不证明ChatGPT UI已上传或Project Settings已更新。

**剩余动作：** 本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A01 `PASS`；G3-A20 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u43"></a>

## U43 Deliverable、Understanding、Submission相互独立

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；状态已分离；理解/最终提交待用户。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 工程待审/证据待补、用户LEARNING、NOT_READY和新GPT PENDING分别记录。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)；[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`；[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1（吴博闻）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,11（互动证据仍需哪些真实输入）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（网页 GPT 二重审核）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[publication_receipt.json](../../../../goal2/c_contract/publication_receipt.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** Understanding LEARNING；Submission NOT_READY；New GPT_SECOND_REVIEW PENDING。

本轮实际C限定范围：[report_tasks_receipt.json](../c_review/report_tasks_receipt.json)（当前Process12页技术事实送审稿的工程、全文/视觉核验完成；正式互动原件/spec/Lock缺失，不能宣布正式完整。）；[package_task_receipt.json](../c_review/package_task_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)（当前116成员具名包、CRC/安全路径/当前PDF/身份/完整闭包与实际解压FULL、报告修订内容等价由C核实；仍REVIEW_ONLY/NOT_READY。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A16 `BLOCKED`；G3-A18 `BLOCKED`；G3-A20 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。

<a id="u44"></a>

## U44 当前先工程收尾，再按四板块讲解由用户审核，最后决定提交

**性质/状态：** CURRENT_USER_REQUIREMENT_INDEX；最新授权顺序已确认；后续用户审核PENDING。

**来源与授权：** 本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。 当前授权：[AUTHORIZATION.md](../AUTHORIZATION.md)。
原件定位：[AUTHORIZATION.md](../AUTHORIZATION.md) 当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态；[实验课1.pptx](../../../../../实验课1.pptx) 第5页实验一产出；第26页作业细则；[AGENTS.md](../../../../../../AGENTS.md) §§10/12/16/18；[APPROVED_PROMPT.md](../../../../goal1/APPROVED_PROMPT.md) §10/11；[实验课1.pptx](../../../../../实验课1.pptx) 物理第5页 / ppt/slides/slide5.xml；[实验课1.pptx](../../../../../实验课1.pptx) 物理第26页 / ppt/slides/slide26.xml。详细原句/版本SHA见同名JSON。

**做法与理由：** 最新用户顺序覆盖旧先讲解再收尾；本轮不代用户理解或自动发送。 源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。

**可打开实现和成果：** [reproduce.py](../../../../../goal3/reproduce.py)::recompute_historical（L84）；[reproduce.py](../../../../../goal3/reproduce.py)::recompute_production（L162）；[package.py](../../../../../goal3/package.py)::build（L327）；[package.py](../../../../../goal3/package.py)::verify_directory（L261）
真实证据：[teacher_delivery_mapping.json](../../../teacher_delivery_mapping.json)；[notebooks_task_receipt.json](../c_review/notebooks_task_receipt.json)；[notebook_runs_receipt.json](../c_review/notebook_runs_receipt.json)；[package_task_receipt.json](../c_review/package_task_receipt.json)；[package_execution_equivalence.json](../c_review/package_execution_equivalence.json)；[WORKFLOW_EVIDENCE_PLAN.md](../../../../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md)；[interaction_candidates.json](../../../interaction_candidates.json)；[INTERACTION_HANDOFF.md](../../../../../docs/goal3/INTERACTION_HANDOFF.md)。
Notebook：[作业1轨迹数据预处理_完成版.ipynb](../../../../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb) `lab1-db981efe8f4a6334`, `lab1-f734f098576e3c99`, `lab1-d035af2dc09c7e86`；[任务3_LLM辅助评估清洗_完成版.ipynb](../../../../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) `lab1-9aa8376b7bf25e5d`, `lab1-b9a7a9bb893c339f`, `lab1-1b0102fcff5af1af`, `lab1-65870bb6cd4183c2`, `lab1-f711eb1ab5723d3f`。
实际PDF：[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22（Experiment Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页1,2,3,4,5,6,7,8,9,10,11,12（Process Report）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,3（第一层：Workflow Construction）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页2,7（第二层：Experiment Decision Process）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（网页 GPT 二重审核）；[experiment1.pdf](../../../../../reports/experiment1/experiment1.pdf) 物理页2,21（如何复算与核对）；[process1.pdf](../../../../../reports/process1/process1.pdf) 物理页11（NOT_READY）。页码是文字anchor定位，不冒称视觉验收。

**对照、分母与实际结果：**
- DELIVERY：每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。 预期：源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。 实际：本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。
- EVIDENCE：证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。 预期：任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。 实际：可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。

**审核范围：** 历史内部C回执：[notebooks_complete_receipt_v2.json](../../../../goal2/c_contract/notebooks_complete_receipt_v2.json)；[figures_complete_receipt.json](../../../../goal2/c_contract/figures_complete_receipt.json)；[analysis_complete_receipt_v2.json](../../../../goal2/c_contract/analysis_complete_receipt_v2.json)；[internal_acceptance_receipt_v2.json](../../../../goal2/c_contract/internal_acceptance_receipt_v2.json)；[core_receipt_epoch02.json](../../../../goal2/c_contract/core_receipt_epoch02.json) 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。

**支持/边界：** 本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。 可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。 完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。 身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。

**剩余动作：** 按任务与要求→数据处理与评价→系统/实验/循环→正式成果与收尾讲解，最后由用户决定。

本轮实际C限定范围：[frozen_identity_receipt.json](../c_review/frozen_identity_receipt.json)（本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。）；[result_summary_equivalence.json](../c_review/result_summary_equivalence.json)（本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。）；[report_numbers_receipt.json](../c_review/report_numbers_receipt.json)（本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。）；[visual_content_receipt.json](../c_review/visual_content_receipt.json)（本轮独立C：当前Experiment22页和Process12页实际200dpi逐页查看与关键内容核查；不代Evidence Master或网页GPT。）。不代表本轮所有工程、网页GPT或用户审核通过。

父要求送审输入快照时状态：G3-A17 `PENDING`；G3-A19 `PENDING`；G3-A20 `PENDING`。观察时点 `2026-09-27T17:47:18.410070+00:00`；最终发布状态以唯一active父入口及真实CL回执为准。
