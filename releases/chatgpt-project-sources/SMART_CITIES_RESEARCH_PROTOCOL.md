# Smart Cities Research Protocol

Version: **v1.0**\
Status: **ACTIVE / LONG-TERM RULE**\
Purpose: **Smart Cities Research Governance / Source / Uncertainty / Spatiotemporal Correctness / Experiment Evidence / AI Critique**

优先级：**老师最新正式要求 / 用户最新明确要求 > 当前批准 Prompt > Project Settings > SMART_CITIES_RESEARCH_PROTOCOL > 历史旧规则。**

本协议维护研究方法与治理；工程执行、证据生产、视觉表达分别路由到文末的对应文件。Project Settings 由用户在 ChatGPT UI 维护，不在仓库复制。发现 active documents 冲突时，明确文件及条款；当前批准 Prompt 明确覆盖的按新规则修正，其余停止受影响部分并报告，不自行择一执行。

## A. Research Scope / Task Governance

| 层级 | 定义与执行条件 |
|---|---|
| T1 TEACHER_REQUIRED | 老师明确必做。 |
| T2 PROJECT_REQUIRED | 老师标为选做、拓展、思考讨论，本项目也必须完成。 |
| T3 CANDIDATE_ENHANCEMENT | GPT 额外提出；说明目的、收益、成本、风险，只有用户明确批准后才能执行。 |
| T4 OUT_OF_SCOPE | 当前不执行。 |

老师 optional 全部做，不等于 GPT/Codex 可以自行增加扩展。文件存在不等于当前任务范围；starter 接口、压缩包模块、历史结果不构成扩展授权。

## B. Source Priority

本轮老师正式任务/作业细则 > 老师最新补充和课堂说明 > starter notebook / code / data / template > 助教正式材料 > 理论/实验 PPT > 老师推荐资料 > 政府/标准/官方数据与文档 > 原始论文 > 权威研究机构 > 其他可信资料。

材料冲突必须显式指出，并说明对任务、方法、数据或结论的影响；不能用外部资料静默替换老师明确要求。

## C. Standard Research Workflow

老师材料 → 完整读题与范围确认 → T1/T2 / Deliverables / grading / submission → 必要网络研究 → Source Audit → starter/data 检查 → requirement checklist → spatiotemporal correctness → GPT 候选 → User review / challenge / modify / reject / select → CONFIRMED / CANDIDATE / UNRESOLVED → 必要公平实验 → 方案冻结 → Codex implementation → real execution → results → GPT audit → human interpretation → formal conclusion。

GPT 提供研究候选与审核，用户审阅、质疑、修改、否决或选择；Codex 执行批准方案。Git commit/push 的执行规则由 AGENTS 管理。

## D. Source Audit

每个关键来源至少记录：Title；Author / Institution；Publication Date；URL；Accessibility；Source Type / Authority；Exact Supported Claim。

- 尽量追溯原始来源，搜索摘要不是正式证据。
- 新闻数字尽量回到原发布；博客、论坛、知乎主要作为线索。
- 报告前复查关键来源；不可访问或未验证的支持关系明确记录。
- 无依据的内容标记为推断/未知，外部资料不得扩大任务范围。

## E. Uncertainty Governance

| 状态 | 定义与后续动作 |
|---|---|
| CONFIRMED | 老师材料、可靠来源、数据或真实实验确认。 |
| CANDIDATE | 存在多个合理解释，且会实质影响方法、参数、指标、数据口径或结论。GPT 给 2–3 个主要候选，包含依据、优势、风险、当前倾向，交 User review。 |
| UNRESOLVED | 研究和讨论后仍无法可靠决定，原则上设计公平并行/消融实验，使用统一条件和指标，以数据裁决。 |
| BLOCKED / UNVERIFIED | 仅限数据缺失、权限、环境、不可接受成本或无法获得充分证据；说明限制与受影响部分。 |

普通实现细节不要机械三选一。Codex 提供真实结果；最终研究判断由 GPT + 用户完成，除非批准方案已有明确自动判定规则。

## F. Fair Comparison

UNRESOLVED 实验原则保持 same data、same split、same preprocessing、same seed where relevant、same budget、same metric、same statistics。任何必要差异应事先说明并获得研究层面的确认。

禁止偏向性调参、看到结果后偷偷改变条件、选择性报告有利结果。

## G. Spatiotemporal Correctness

位置/轨迹研究必须检查：

- CRS；WGS84 / GCJ02 等坐标语义；coordinate order；conversion；projection；geographic vs planar coordinates；distance algorithm；units。
- timestamp；timezone；sampling interval；speed；direction；spatial scale；temporal scale。
- missing；duplicate；drift；jumps；temporal anomaly。
- sampling mechanism；representativeness；bias；sample vs population。

禁止无依据把经纬度直接用于米制欧氏距离、为未知数据默认指定 CRS/时区、无物理依据插值缺失轨迹、混淆方向与速度字段、混淆单位、把样本结果直接外推总体。关键语义无法确认时停止受影响正式实验，返回证据、候选解释与影响。

## H. Parameter Rationale

参数依据优先级：**物理 / 业务意义 > 数据分布 > 敏感性实验 > 原始文献 / 官方经验 > starter default > 主观经验。**

对老师/starter 参数逐项判断其性质：mandatory、teaching example、empirical initialization、value requiring validation。不得把教学示例自动当作已验证最优值，也不得擅自更改 mandatory 参数。重新调参需要技术理由与记录。

## I. Data Authenticity / Provenance

明确区分 teacher-provided、starter、historical、pre-generated、demo、sample、current-run、full-dataset、derived output。

历史/demo/预生成结果不得冒充当前实验结果，样本不得冒充总体。原始数据与材料保持原样，派生结果保存生成链。正式实验结果必须来自当前最终代码的真实执行，不伪造命令、性能、图表、LLM 输出或测量，不用理论值替代实测，不隐藏负结果。

## J. Experiment Evaluation and Evidence Chain

代码能跑不等于实验完成。每个指标必须回答：评价什么、为什么合理、如何计算、如何解释。

重要结论尽量形成：**真实数据 → 真实代码 → 实验 → 指标/图表 → 结论。**

结论强度必须与证据一致。报告依照批准方法、真实结果与 GPT/用户确认后的解释整理；不在看到结果后自行创造研究结论。

## K. AI / LLM Critique

AI 是研究助手，不是事实来源或最终裁决者。检查 hidden assumptions、units、coordinate semantics、missing-value assumptions、parameter rationale、counterexamples、literature/data/experiment support。

标准链：**AI proposal → Human challenge → evidence / physical rule / literature / experiment → Accept / Modify / Reject。**

禁止为了 Process Report 故意制造 AI 错误、用户质疑或虚假互动。

## L. Stop / Escalate

以下研究问题停止受影响部分并提交证据、影响及待决定事项：

- source conflict changes method；CRS/semantic ambiguity；
- metric has materially different definitions；parameter requires research-level choice；
- results challenge core assumption；starter suspected wrong and fixing changes method；
- new issue expands scope；missing evidence prevents conclusion。

工程 stop、日志保存、权限与发布处理由 AGENTS 负责；不得用未经验证的假设绕过研究决策。

## M. Cross-document References

- [AGENTS.md](../../AGENTS.md)：Codex、实现、Notebook、复现、GitHub、报告构建与工程 stop。
- [Interaction Evidence Protocol](../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md)：历史恢复、Evidence Master、截图、Micro Trace、audit、lock 与 LaTeX 同步。
- [Visual System](../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)：P2、XeLaTeX、报告身份、Interaction Evidence Visual Grammar 与正式技术可视化。

本协议不重复 TikZ、截图排版或 Git 命令细节；各职责只有一个 active 规则入口。
