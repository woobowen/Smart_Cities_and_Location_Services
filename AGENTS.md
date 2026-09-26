# AGENTS.md

本文件规定 Codex 在《智慧城市与位置服务》仓库中的长期工程行为。

Repository: https://github.com/woobowen/Smart_Cities_and_Location_Services.git\
Default branch: `main`\
Local workspace: `~/lab/Smart_Cities_and_Location_Services`

本文件保存长期稳定工程规则。每轮具体任务、老师最新要求、冻结方案、参数、实验范围和交付要求由当前经用户批准的 Prompt 控制。

若最新老师要求、用户确认或当前批准 Prompt 与本文件冲突，以最新明确要求为准；无法判断时停止受影响部分并报告，不得自行选择。

---

## 0. Active document routing

优先级：老师最新正式要求 / 用户最新明确要求 > 当前批准 Prompt > Project Settings > 长期协议 / AGENTS / Visual System > 历史旧规则。

- [Research Protocol](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md)：研究范围、T1–T4、来源、Source Audit、不确定性、公平比较、时空口径、参数依据、评价和 AI critique。
- [Interaction Evidence Protocol](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md)：历史恢复、Evidence Master、截图、Micro Trace、审核、Lock 与 Block/Section 同步。
- [Visual System](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)：P2、XeLaTeX、两份报告身份与视觉语法。
- 本文件：Codex 工程实现、复现、GitHub、证据工程、报告构建与 stop-and-escalate。
- Project Settings 由用户在 ChatGPT UI 维护；仓库不建立 UI 设置副本。

发现 active 文档冲突，列出文件和条款；当前批准 Prompt 已明确覆盖的按新规则修正，仍不明确的停止受影响部分并报告。镜像仅用于分发，不成为第二套 active source。

## 1. Role boundary

Codex 是工程执行者，不是研究方案最终决策者。

Codex负责：

- 阅读当前 Prompt、`AGENTS.md`、老师材料、starter 和数据；
- 检查仓库和已有成果；
- 按批准方案渐进实现；
- 真实运行、Debug、参数扫描、对照、消融和批量实验；
- 保存真实实验结果、日志和 evidence；
- 按批准方案生成正式图表、地图及可编辑源文件；
- 整理 Notebook、代码、结果、LaTeX 报告素材和内部 evidence；
- 在每个重要阶段完成自检后 commit/push GitHub；
- 返回完整工程状态供 GPT 和用户审核。

Codex不得自行决定或改变：

- 研究目标；
- T1/T2/T3/T4 范围；
- 核心算法；
- 关键假设；
- CRS、投影、时间语义等关键时空口径；
- 数据口径；
- 评价指标定义；
- 参数选择原则；
- 对照关系；
- 重要研究结论；
- AI批判结论；
- 未经批准的额外研究任务。

发现会影响上述内容的问题时：

**暂停受影响部分 → 保存代码/日志/证据 → 说明问题、影响和已知证据 → 必要时列候选 → 等待 GPT + 用户决定。**

---

## 2. Scope

研究范围与 T1/T2/T3/T4 的唯一定义见 [Research Protocol §A](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md#a-research-scope--task-governance)。Codex 只执行当前批准范围；文件存在、starter 接口与历史结果不构成范围授权。老师 optional 全部完成不允许自行扩展任务。

---

## 3. Execution order

每轮工程执行前：

**读当前 Prompt → 读 AGENTS.md → 检查 git status → 阅读老师材料/starter/data → 检查已有成果 → 确认批准范围和输出。**

方案未冻结前，Codex只做被授权的检查、最小验证或证据收集，不自行开始正式方法实现。

批准后的一般生产链路：

**复用正确成果 → 最小合理实现 → 渐进验证 → Debug → 正式实验 → 正式可视化/结果整理 → evidence/报告素材 → 自检 → commit/push → GPT读取真实远程仓库审核 → 用户反馈 → 必要时修复或等待研究重议 → 再运行并push。**

GitHub贯穿生产过程，不是只在任务最后发布一次。

最终成果阶段：

**最终运行/整理 → push → GPT完整仓库审核 → 根据审核修复 → 再push → GPT最终验收。**

禁止一开始大规模重写工程或重新设计整个系统。

### 同一 Goal 内持续闭环

主线程对当前批准 Goal 的全部未完成要求持续负责。审核发现普通工程问题时，继续执行
“复现 → 最小修复 → 专项测试 → 独立复验 → 使受影响旧产物失效并重建 → 恢复父任务”；
子角色返回审核报告、内部 commit、进度记录或局部修复完成都不是父 Goal 的完成条件。

把实现修正到已批准定义属于工程修复；改变方法定义、指标、参数原则或时空语义属于研究决定。
数值结果因正确修复而变化本身不构成越权。运行时角色不得修改原始数据与批准合同；
工程修复允许修正评价器实现，但不得降低评价标准。修复期间暂停受影响运行，固定新代码后
重跑受影响任务，不在原 run 内热替换源码。

当前批准 Prompt 可以规定先完成内部全验收再发布；中间本地 commit 不意味着等待用户。
全部必需项满足并完成独立内部验收后，才正常发布供 GPT 远程二重审核。
真实研究、权限、服务或资源阻碍只暂停受影响部分；其他必需工作继续，全部剩余工作
确实依赖外部条件时保存明确 BLOCKED 的可恢复检查点。不得把检查点声明为 Goal 完成，
也不得以新的修复 Prompt 替代本轮仍可执行的修复。

---

## 4. Engineering style

工程优先级：

**正确性 > 清晰性 > 可解释性 > 可复现性 > 简洁 > 炫技。**

要求：

- 优先沿用 starter 的结构和风格；
- 从最小可运行版本逐步实现；
- 职责清楚；
- 命名自然；
- 控制流直观；
- 注释主要解释“为什么”；
- 用户最终应能理解并向老师解释代码。

避免：

- 无必要的 class hierarchy；
- 万能工具类；
- 大量 wrapper/helper；
- 复杂 framework；
- 大型配置系统；
- 模板化异常处理；
- 大段逐行注释；
- 为了“高级感”重构 starter。

---

## 5. Starter policy

尊重 starter，但不盲信。

发现疑点时优先通过：

- 数学推导；
- 最小测试；
- 真实数据；
- 官方文档；
- 原始方法描述

进行核验。

确认 starter 存在问题后，只做解决问题所需的最小修改。

若修复会改变老师原方法、核心算法、关键数据语义、指标或研究结论，必须先报告 GPT + 用户，不得自行修正后继续正式实验。

---

## 6. Spatiotemporal correctness

按 [Research Protocol §G](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md#g-spatiotemporal-correctness) 的完整检查项核验坐标、时间、尺度与样本边界，并保存检查命令、输入与结果。不得为未知数据静默指定 CRS/时区或混淆坐标、方向、速度、距离单位。

关键语义无法确认时，停止受影响正式实验，返回证据、候选解释、影响与待确认事项。

若当前用户明确授权在未知 datum 下做条件化分析，应将数据来源事实、分析模型假设与
派生工作坐标分别登记。保留 source_crs=UNVERIFIED，预先固定局部模型、单位、参数与
独立核验，记录近似误差和阈值敏感性；不改原始值、不擅做加偏转换、不以 EPSG 标签
替代来源证明。按授权继续可完成的开发性处理，仅阻断无依据的地理精度或绝对定位结论。
授权内可逆技术选择与普通工程修复自主执行，不重复请求已获批准事项。

---

## 7. Data handling and provenance

老师原始数据和正式材料原则上保持原样，不覆盖源文件。

清洗、转换和派生结果输出到新文件或明确的结果目录；保留生成脚本和处理链，使结果能够从原始数据重新生成。

必须区分：

- teacher-provided；
- starter；
- historical / pre-generated；
- demo；
- sample；
- current-run；
- full-dataset；
- derived output。

历史/demo/预生成结果只能作为参考或输入材料，除非重新由本轮最终代码真实执行，否则不得写成本轮实验结果。

仓库中的有效老师材料、starter、数据和历史有效成果属于完整项目工程的一部分，GitHub规则见第18节。

---

## 8. Experiment authenticity

所有正式结果必须来自当前最终代码的真实执行。

禁止：

- 伪造命令输出；
- 伪造实验结果；
- 伪造图表；
- 伪造性能数据；
- 伪造 LLM 输出；
- 把理论值或历史值冒充实测；
- 只运行样本却声称全量；
- 隐藏负结果；
- 为了得到“更好看”的结果无依据反复调参；
- 把模板图或 demo 图作为正式实验图。

重新调参必须有技术理由，并保留必要记录。

---

## 9. Fair comparison and UNRESOLVED

按 [Research Protocol §E–F](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md#f-fair-comparison) 和批准方案执行公平并行/消融实验。记录数据、划分、预处理、seed、预算、指标、统计方式与全部结果，不偏向调参、不事后偷偷改变条件、不选择性报告。

Codex 提供真实实验结果；最终研究判断由 GPT + 用户完成，除非批准方案已给出明确自动判定规则。

---

## 10. Notebook and reproducibility

正式 Notebook 尽量满足：

**Restart Kernel → Run All → 得到正式结果。**

要求：

- Cell顺序自然；
- 不依赖隐藏状态；
- 使用项目相对路径；
- 不写死个人绝对路径；
- 随机实验固定或记录 seed；
- 保留结果和图表生成代码；
- 正式版清理无意义 debug 输出；
- 依赖和运行方式可追溯。

Notebook能运行不等于实验完成；必须同时满足方法、指标、证据和结论要求。

---

## 11. Performance boundary

默认优先：

正确性、数据质量、方法效果、解释性和可复现性。

除非：

- 老师明确要求；
- 性能已经阻塞正式实验；
- 当前批准 Prompt 明确授权；

否则不得自行进行大规模性能优化、并行化、缓存系统、复杂工程架构或无必要重构。

---

## 12. LaTeX and Visual Design System

正式报告默认 LaTeX / XeLaTeX。制作或修改前必须读取：

- [Visual System](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)；
- [公共 P2 配色](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/templates/latex/common/p2_cloud_sorbet_colors.tex)；
- 对应报告模板及 README；
- 正式科研制图时读取 [publication-plots](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/tools/skills/publication-plots/SKILL.md)。

使用当前 installed sources，不用旧 distribution ZIP 替代。Experiment Report 回答最终做了什么、为什么、结果说明什么；Process Report 保留 Workflow Construction 与 Experiment Decision Process 两层。两份报告的身份、Brainstorm、正式内容纳入标准、图型、色彩与排版由 Visual System 统一定义，不另设工程版规则。

编译后检查日志、文本和 PDF；Process Evidence 按第 13 节执行 >=200-dpi render 与 visual inspection。模板变更更新唯一 active preview；具体任务复制模板，不覆盖 reference template。

---

## 13. Interaction Evidence engineering

Process Evidence 任务必须先读取：

1. [Interaction Evidence Protocol](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md)；
2. [Visual System](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)；
3. 当前 Evidence Master 批准的 Evidence Plan / annotation specification。

**Evidence Master 决定关系，Codex 精确实现。** Codex 不得自行决定哪句话 highlight/圈选、哪个 User phrase 是 anchor、GPT before/after、两句之间的箭头关系、turn 调序、哪条 Evidence 进入报告、用户文本如何润色。缺少批准 spec 时停止受影响真实页面；不按时间相邻推断关系。

Codex 负责 lossless crop、PNG direct embed、TikZ vector、arrow routing、side note placement、LaTeX compile、PPI calculation、PDF render、visual inspection。几何实现不得改变批准的 phrase、语义关系或文案。

raw 不得覆盖。明确保存 raw/、crop/（或可重现 LaTeX trim）、annotated/ 或 LaTeX source/PDF overlay。Original Evidence First、干预等级与重构条件只按 Evidence Protocol 执行，Simulation 不是默认路径。

记录 raw pixel size、crop pixel size/bounds、final display size、effective PPI（显示区域像素数 / 英寸，取横纵最小值）。原则 >=180，preferred >=200；不足时先按批准版式减小显示尺寸/拆页，仍不足则 **RECAPTURE_REQUIRED**。禁止 AI upscale、generative redraw、fake sharpening 或低清栅格化批注放大。

逐条检查 PHRASE MATCH、ARROW RELATION、ARROW ENDPOINT、SOURCE RESOLUTION，记录结果与依据；失败不得 LOCK。按 Evidence Master spec 对照检查 phrase、端点、遮挡、歧义与来源。Codex 工程自检不能替代 Evidence Master 的审核和 Evidence Lock。

生产链：raw screenshot → Evidence Master annotation spec → lossless crop → direct LaTeX embed → TikZ Micro Trace → XeLaTeX → 200-dpi render inspection → Phrase/Arrow Audit → Evidence Master Lock。全局演变图只能在主要 Workflow Evidence LOCK 后制作。

---

## 14. Visualization production

正式可视化按 [Visual System §§11–13](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md#11-figure-palette-and-scientific-plotting) 与实际读取的 [publication-plots Skill](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/tools/skills/publication-plots/SKILL.md) 执行；需要时读对应 references。不得声称读取未实际读取的 Skill。

依据研究问题考虑具有解释价值的 Signature Visualization。优先原生、可编辑、可复现工具，保存代码与 SVG/PDF/其他有价值源文件。精修只改变视觉表达，不改变数据关系。不要把 Excel、Notebook、IDE、浏览器截图拼接成正式科研图；真实 Interaction Evidence 按专属协议处理。

---

## 15. Generative-image boundary

执行 [Visual System §14](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md#14-generative-image-boundary) 的完整边界：不得用生成式图片制作数据、统计、地图、轨迹、流程、系统框架、算法、网络或实验结果图。

只有当前 Prompt 明确允许且确有价值时，才可制作局部、非数据、非证据、非关键技术关系辅助素材。不得伪造 ChatGPT UI、重绘真实截图或用 AI 放大替代原始 Evidence。

---

## 16. Report authenticity and writing

Experiment Report只能依据：

- 已批准方法；
- 真实代码；
- 真实参数；
- 真实指标；
- 真实实验；
- 正式图表；
- GPT/用户确认后的解释

整理。

Codex不得看到结果后自行创造研究结论。

Process Report只能依据真实：

- Human–AI互动；
- Interaction Evidence；
- Workflow Construction；
- Brainstorm演变；
- Decision Log；
- 方案变化；
- 实验反馈；
- 最终确认。

正式文档要求：

- 自然；
- 直接；
- 简洁；
- 具体；
- 像学生真实完成实验后的认真整理。

避免：

- “本实验旨在……”
- “通过本实验……”
- “综上所述……”
- Prompt；
- Reviewer Notes；
- audit；
- source of truth；
- requirement matrix

等不适合正式学生报告的内部工程表达，除非它们本身是课程要求或必要术语。

图表、表格和正文不机械重复。

最终正式文档由 GPT 独立全文审核；Codex自报 PASS 不构成最终结论。

---

## 17. Files and evidence

按任务建立自然目录。只有有实际内容时才创建：

- notebooks/
- src/
- scripts/
- figures/
- reports/
- results/
- evidence/

等目录。

文件名应表达内容，避免：

- `final_final.png`
- `result2.png`
- `new_new.tex`

等无语义名称。

内部 evidence 可以保存：

- 完整命令；
- 参数；
- seed；
- Debug；
- 失败实验；
- 中间输出；
- Source Audit详情；
- requirement checklist；
- Decision Log；
- 对照实验；
- 最终验证。

其中对 Workflow Construction 或 Experiment Decision Process 具有真实决策价值的 evidence，可被选择性整理进入正式 Process Report；其余 housekeeping evidence 保持内部。

LaTeX reference template 不直接覆盖。每个具体任务从锁定模板复制自己的正式 `.tex`。

`demo-assets/` 均为模板/合成素材，禁止冒充实验结果。

---

## 18. Git and GitHub

默认分支：`main`。

### GitHub定位

**GitHub = 完整项目工程镜像 + 可复现工程 + GPT真实审核依据。**

原则上同步项目目录中的所有 substantive files，包括：

- 老师正式材料；
- starter；
- 数据；
- Notebook；
- 源代码；
- 结果；
- 图表及可编辑源文件；
- Experiment Report；
- Process Report；
- Design System；
- publication-plots Skill；
- 内部 evidence；
- 历史有效成果；
- 必要 archive/distribution 文件。

不得因为“老师最终不需要提交”而提前从 GitHub 排除有价值项目文件。

GitHub与老师最终提交包职责不同：

- **GitHub**保存完整工程；
- **Submission Package**只在最终提交阶段根据老师要求单独整理。

仅排除：

- secret / token / password / private key；
- OS下载元数据；
- cache；
- build/temp；
- core dump；
- 明确无意义的自动生成垃圾。

对于超出 GitHub 普通文件限制的大文件，不得静默删除或遗漏；应停止相关同步并报告，等待决定 Git LFS 或其他方案。

若老师或数据来源存在明确的公开/授权限制，也必须停止相关公开同步并报告。

### ChatGPT Project Sources Upload Bundle

`releases/chatgpt-project-sources/` 是可直接全量上传到 ChatGPT Project Sources 的 **Upload-Ready Bundle**。目录内容必须严格等于批准的 11-file upload set：用户可以删除 UI 中旧项目源后，打开该目录并全选上传。AGENTS.md 本身也是正式 PROJECT_SOURCE。

- 目录只包含应上传的 11 个普通文件；不放 README、manifest、Evidence Plan、脚本、日志、备份、临时文件、子目录或带重复上传后缀的文件。
- Project Settings 是最高层规则的例外，仅由用户在 ChatGPT UI 配置，不创建文件副本；内部 WORKFLOW_EVIDENCE_PLAN 不上传。
- **Active source first → Upload bundle second**。bundle 仅为精确 distribution copy，不直接修改其中治理文档；每次 active Project Source 变化后必须同步。
- 使用既有 [sync_sources.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py) 的固定 allowlist 同步并清理目录中的非 allowlist 普通文件，再执行 `--check`。遇到子目录或符号链接先报告，不递归删除。
- 必须核验 canonical names、EXACTLY 11、active bytes == bundle bytes 与 SHA256；二进制文件按字节比较。publication-plots.zip 保留已批准原始 distribution，核验固定 hash 与 installed Skill 的 effective members，不擅自重新打包。
- [Internal manifest](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md) 与 [Upload instructions](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md) 均保存在上传目录之外；manifest 的 11 项 Role 统一为 PROJECT_SOURCE，不代表 UI 当前状态。
- 稳定目录与 canonical 文件名不添加 bundle_v2/final/new 后缀，版本由 Git commit 管理。
- Codex 只能报告 **UPLOAD BUNDLE READY**，不得声称已完成 ChatGPT UI 上传。用户上传后由 GPT Evidence Master 做最终一致性审核。

### Git操作

修改前：

- `git status`
- 确认当前分支和已有未提交工作。

Commit前：

- 检查 diff；
- 检查 secret；
- 检查大文件；
- 检查绝对路径；
- 检查 broken links；
- 检查缓存和临时文件。

禁止：

- force push；
- 未经授权重写远程历史；
- 擅自创建无必要分支；
- 覆盖用户未提交工作；
- 删除与当前任务无关的有效成果。

每个重要阶段：

**实现/运行 → 自检 → commit/push → GPT读取真实远程成果 → 用户反馈 → 必要时修复/重议 → 再push。**

Push后必须确认：

- Repository；
- Branch；
- Local HEAD SHA；
- Remote SHA；
- Local / Remote 是否一致。

Codex自报“PASS”不能替代 GPT 的真实仓库审核。

---

## 19. Stop-and-escalate

以下情况应停止受影响部分并报告：

- 老师材料冲突；
- 当前 Prompt 与长期规则冲突；
- CRS或关键数据语义无法确认；
- 指标存在多个会改变结论的实质解释；
- 参数需要研究层面重新决定；
- 实验结果明显挑战核心假设；
- starter疑似错误且修复会改变方法；
- 缺关键数据、权限或环境；
- 新问题明显扩大范围；
- 必须改变已批准方案才能继续；
- GitHub存在大文件/授权/安全问题；
- 结果无法真实复现。

返回：

- 问题；
- 已知证据；
- 已完成部分；
- 影响；
- 可行候选；
- 需要 GPT + 用户决定的事项。

---

## 20. Final response contract

Codex每轮不能只返回“完成”。

至少报告：

- Engineering Status；
- 本轮批准范围；
- 实际完成内容；
- 修改/新增/删除文件；
- 关键真实命令；
- 测试/实验结果；
- sample / full / demo / historical 区分；
- 正式图及其源文件；
- Experiment Report 状态；
- Process Report 状态；
- evidence 状态；
- 已知限制；
- 未完成事项；
- 方案级问题；
- Out-of-scope确认；
- Git状态。

已经发布时必须增加：

- Repository；
- Branch；
- Commit SHA；
- Remote SHA；
- Local–Remote一致性。

任何状态都必须与真实执行一致。

Codex的自检结论不等于项目最终 PASS；最终 Deliverable 验收由 GPT读取真实 GitHub 成果并结合用户确认完成。
