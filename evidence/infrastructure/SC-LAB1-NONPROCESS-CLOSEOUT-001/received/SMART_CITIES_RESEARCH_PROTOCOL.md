# Smart Cities Research Protocol

Version: **v1.2**\
Status: **ACTIVE / LONG-TERM RULE**\
Purpose: **Smart Cities Research Governance / Source / Uncertainty / Spatiotemporal Correctness / Experiment Evidence / AI Critique**  
Revision: **2026-09-29 · Project-wide workflow scope / conditional-analysis boundary**  
Canonical repository path: `docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md`

优先级：**老师最新正式要求 / 用户最新明确要求 > 当前批准 Prompt > Project Settings > SMART_CITIES_RESEARCH_PROTOCOL > 历史旧规则。**

本协议维护研究方法与治理；工程执行、证据生产、视觉表达分别路由到文末的对应文件。Project Settings 由用户在 ChatGPT UI 维护，不在仓库复制。发现 active documents 冲突时，明确文件及条款；当前批准 Prompt 明确覆盖的按新规则修正，其余停止受影响部分并报告，不自行择一执行。

## A. Research Scope / Task Governance

本协议适用于整个《智慧城市与位置服务》项目。后续正式实验、课程设计及批准的报告任务继承共同研究治理；各任务仍按老师材料和当轮批准方案确定方法、数据、评价与交付。既有任务的算法、阈值、样本量、Goal及报告结构仅为该任务实例，不成为未来任务的输入或永久标准。

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

实质工作流、Multi-Agent及持续闭环是项目通用工作方式。正式任务按问题和规模设置真实的研究、执行、独立核验、反馈、优化、修复与恢复职责，并保留与实际职责相匹配的证据；不能退化为模型只提建议、普通函数改名或事后补画架构图。角色数量、工具和信息合同由当轮任务设计，不永久固定实验一的A/B/C实现。

四模式、记忆、特定消融和调用预算不自动成为未来每项任务的必做实验，其采用及评价由老师材料和当轮批准方案决定。经实测选定的最终记录级方法可以是确定性程序；研究/执行层的实质多角色工作流不要求每条数据都调用LLM。

GPT 提供研究候选与审核，用户审阅、质疑、修改、否决或选择；Codex执行批准方案或用户明确批准的实验裁决规则。用户确认候选范围、指标、保护、选择/回退与停止规则后，普通授权内比较和裁决自动进行，不为每个参数重复确认；结果与正式解释仍需真实证据及范围明确的最终审核。

研究成果进入文档时，在工具与可信输入齐备且任务已授权的情况下，GPT可优先直接制作正文、原生图表与LaTeX；Codex负责接管集成及相应复现。制作分工不改变研究定义、用户决策权或独立审核的实际归属。Git与工程执行规则由AGENTS管理。

批准 Goal 内，审核发现工程缺陷后持续修复、回归、重建受影响产物并恢复父任务，
不以审核报告、局部完成或子角色结束代替 Goal 验收。实现偏离批准定义的修正属于工程修复；
改变定义、指标、关键参数原则或时空语义才需要研究决定，结果数值变化本身不自动越权。
运行时角色不能改原始数据或批准合同；评价器可以修复实现，不能降低标准。
内部进度与 commit 不代表等待用户；按当前 Prompt 完成内部总验收后发布，
真实外部阻碍保存可恢复状态并诚实说明，仍继续所有不受影响的必要工作。

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

“相同条件”指除研究干预外的可比条件，不要求顺序实验保持相同顺序，也不假称一次提议与多轮搜索计算量完全相同；不同参数域、输入可见性、反馈和实际消耗须事先说明。涉及候选组合时先保留单项及父项依据，按批准范围检查组合是否有额外价值，不以模块更多或论文更多判优。没有收益、权衡和回退均可构成有效实验结论，不为得到正结果事后放宽标准。

## G. Spatiotemporal Correctness

位置/轨迹研究必须检查：

- CRS；WGS84 / GCJ02 等坐标语义；coordinate order；conversion；projection；geographic vs planar coordinates；distance algorithm；units。
- timestamp；timezone；sampling interval；speed；direction；spatial scale；temporal scale。
- missing；duplicate；drift；jumps；temporal anomaly。
- sampling mechanism；representativeness；bias；sample vs population。

禁止无依据把经纬度直接用于米制欧氏距离、为未知数据默认指定 CRS/时区、无物理依据插值缺失轨迹、混淆方向与速度字段、混淆单位、把样本结果直接外推总体。关键语义无法确认时停止受影响正式实验，返回证据、候选解释与影响。

用户明确授权条件化分析时，允许在有依据的坐标顺序/角度单位与结构事实之上，预先固定
适合任务尺度的局部数学模型及工作坐标，独立检查实现、近似误差与阈值影响。
source_crs 仍为 UNVERIFIED；数学椭球/投影假设不是文件 datum 证明，不能按清洗分数选择。
原始值不变，产物明确标为真实数据上的条件化分析。工程正确、条件化结果有效和真实地理
语义确认分别验收；不放宽共同审核标准，也不以未知事实阻断授权内的全部处理。

本节是条件性通用规则。既有实验的条件化分析授权不自动证明新数据的CRS，也不自动授权其他任务的未知datum分析。

## H. Parameter Rationale

参数依据优先级：**物理 / 业务意义 > 数据分布 > 敏感性实验 > 原始文献 / 官方经验 > starter default > 主观经验。**

对老师/starter 参数逐项判断其性质：mandatory、teaching example、empirical initialization、value requiring validation。不得把教学示例自动当作已验证最优值，也不得擅自更改 mandatory 参数。重新调参需要技术理由与记录。

## I. Data Authenticity / Provenance

明确区分 teacher-provided、starter、historical、pre-generated、demo、sample、current-run、full-dataset、derived output。

历史/demo/预生成结果不得冒充当前实验结果，样本不得冒充总体。原始数据与材料保持原样，派生结果保存生成链。正式实测结果必须来自可追溯到对应有效代码、输入与合同的真实执行，不伪造命令、性能、图表、LLM输出或测量，不用理论值替代实测，不隐藏负结果。本轮新实验与引用的既有真实实验分别记录；纯报告修订对未受影响结果的引用按§J执行。

## J. Experiment Evaluation and Evidence Chain

代码能跑不等于实验完成。每个指标必须回答：评价什么、为什么合理、如何计算、如何解释。

重要结论尽量形成：**真实数据 → 真实代码 → 实验 → 指标/图表 → 结论。**

结论强度必须与证据一致。报告依照批准方法、真实结果与有证据的解释整理；自动裁决只在用户预先批准规则内执行，最终解释按实际审核与用户确认范围记录，不能在看到结果后无依据扩张结论。

区分任务覆盖、实现正确、评价可信、效果获支持和正式交付。候选之外的可信原始参考、明确输入范围、分母、单位、不可计算状态与实际输出是评价依据；测试数、文件数、可执行性和局部算法保证不能替代整链质量。具体指标及允许退化由批准任务决定，不用文稿润色改变数学标准。

正式报告在相应方法、参数、对照和取舍处解释核验与优化依据，让文字和图表呈现证据，而不是堆内部状态、长哈希和要求总表。完整追溯保留工程；影响结论的假设、时空不确定性、样本边界和负结果仍须在正文准确说明。纯表达/排版更新可以引用已验证且未受影响的真实运行，保持原实验身份，不必为每次改稿重新运行模型，也不得冒称新LIVE。

## K. AI / LLM Critique

AI 是研究助手，不是事实来源或最终裁决者。检查 hidden assumptions、units、coordinate semantics、missing-value assumptions、parameter rationale、counterexamples、literature/data/experiment support。

标准链：**AI proposal → Human challenge → evidence / physical rule / literature / experiment → Accept / Modify / Reject。**

禁止为了 Process Report 故意制造 AI 错误、用户质疑或虚假互动。上述Human challenge链仅描述真实发生的人类判断；用户预先批准规则后的自动核验须按真实执行主体记录，不能为凑链条补造人类动作。技术核验图与历史Human–AI Evidence分别遵循Visual System和Evidence Protocol的边界。

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
- [Visual System](../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)：P2、XeLaTeX、报告身份、Interaction Evidence Visual Grammar、正式技术可视化与参考成品。
- [Report Writing Guide](../report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md)：面向教师的正文组织、问题驱动论证、研究要求融入、自然语言、图文关系与写作审核。

本协议不重复 TikZ、截图排版或 Git 命令细节；各职责只有一个 active 规则入口。
