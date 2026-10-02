# 《智慧城市与位置服务》Workflow Interaction Evidence Protocol

Version: **v2.7**\
Status: **ACTIVE / LONG-TERM RULE**\
Purpose: **Process Report · Workflow Construction · Experiment Decision Process · Human–AI Interaction Evidence**  
Revision: **2026-10-02 · Real user-UI openings / native captures / arrow-only evidence audit**  
Canonical repository path: `docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md`

本协议专门约束：真实历史恢复、原始聊天取证、Narrative规划、Evidence设计、最小必要编辑、对话精修/重构、Simulation执行、原始研究对话证据采集、截图、审核、Evidence Lock、Block/Section级LaTeX同步与最终综合图制作。

优先级：

**老师最新正式要求 / 用户最新明确要求 > 当前批准任务Prompt > Project Settings > 本协议 > 历史旧规则。**

---

本协议负责 Evidence authenticity / production 及 Process Report 叙事的真实归属；研究治理见 [Research Protocol](../research/SMART_CITIES_RESEARCH_PROTOCOL.md)，一般报告组织、论证与编辑见 [Report Writing Guide](../report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md)，视觉语法见 [Visual System](../design-system/SMART_CITIES_VISUAL_SYSTEM.md)，工程实现见 [AGENTS](../../AGENTS.md)。Process 第一人称与历史处理继续以本协议 §16.1—16.2 为准。Project Settings 由用户在 UI 维护。

本协议适用于项目每项正式研究的真实互动证据。后续Process继承共同基础并记录当前任务新增演化，按Report Writing Guide §12组织；继承不得扩大原证据的来源、适用范围或Lock状态。

## 1. 核心目标

本协议服务于 Process Report 的两个正式层次：

### Part I — Workflow Construction

回答：

> **这套Human–AI研究工作流，是怎样从用户真实提出的问题、补充、质疑、纠正和确认中一步一步形成的？**

### Part II — Experiment Decision Process

回答：

> **具体实验任务中的方法、参数、指标和结论，是怎样通过真实Human–AI互动、外部资料、数据和实验逐步形成的？**

本协议的核心目标不是重新制造一个“更漂亮”的历史，而是：

> **尽可能直接使用真实聊天与真实研究过程，只对影响正式呈现的冗长、重复、上下文断裂和后补内容进行最低必要程度的整理。**

正式Evidence应尽可能做到：

**真实聊天优先\
→ 原始截图优先\
→ 最小干预优先\
→ 版式适应证据\
→ 重构只作为最后手段。**

---

## 2. 原始聊天的两个主要编辑问题

历史聊天本身是首选Evidence，但通常存在两个实际问题。

### 2.1 问题A：GPT回复过长，截图和阅读困难

典型情况：

- 单条GPT回复很长；
- 包含大量背景解释；
- 有多个例子；
- 重复总结；
- 与当前Decision无关的支线过多；
- 一张截图无法清楚呈现。

该问题本质上首先是：

> **截图 / 版式问题**

而不是“重新写一遍对话”的理由。

优先通过：

- 多页原截图；
- 原文裁切；
- 关键段落截取；
- GPT冗余删除；
- annotation；
- caption；
- LaTeX多页布局；

解决。

### 2.2 问题B：用户有重复表达、后补内容或时间顺序不连续

典型情况：

- 同一意思反复确认；
- 连续2–3轮只补同一个点；
- 后来又回来补充前面的问题；
- 原始时间顺序真实，但正式阅读逻辑较散；
- 某个Decision被分散在多个位置。

该问题本质上首先是：

> **Narrative / Decision Unit组织问题**

而不是“把全部聊天重新写短”的理由。

优先通过：

- 去除纯重复；
- 原句最小合并；
- Decision Unit归组；
- Historical Order / Report Order分离；
- 对无新证据的后补内容做编辑性调序；

解决。

---

## 3. 最高真实性原则

所有正式Interaction Evidence都必须满足：

**真实历史\
→ 真实用户立场\
→ 真实AI建议/回应\
→ 真实证据\
→ 真实Decision。**

允许：

- 回看真实历史；
- 提取真实用户原话；
- 删除无价值重复；
- 裁切原始截图；
- 将长回复拆成多页；
- 删除GPT重复或与当前Decision无关的段落；
- 合并用户围绕同一Decision的重复表达；
- 将无新证据的后补内容归回同一Decision Unit；
- 对真实历史进行阶段性复盘；
- 现在重新确认过去已形成的规则；
- 为正式报告进行必要的编辑性调序。

禁止：

- 创造过去不存在的用户观点；
- 创造过去不存在的核心GPT建议；
- 伪造争论、否决、错误、证据或Decision；
- 把GPT提出的专业概念倒写成用户原本就知道；
- 把GPT观点写成用户原创；
- 把后来才形成的结论提前放入更早历史；
- 将依赖新证据的观点前移；
- 改变真实Decision的因果关系；
- 将当前重构聊天冒充过去原始聊天；
- 为丰富Process Report故意制造AI错误或虚假Human-in-the-loop；
- 为了截图“好看”而污染真实研究过程。

---

## 4. 三角色对话体系

本协议区分以下三个Evidence生产职责角色；这不是对每项研究/执行Multi-Agent角色数量的固定要求，具体任务的实质工作流按Research Protocol §C设计。

### 4.1 Evidence Master / Master Planning Conversation

**由用户明确指定的Evidence Master / Master Planning Conversation**是Evidence构建的负责入口，在指定范围内长期负责：

- Historical Question Inventory；
- Historical Retrieval Card；
- Original Transcript Packet；
- Turn Classification；
- Decision Unit识别；
- Narrative整理；
- Report Evidence Map；
- Historical Order / Report Order；
- Evidence ID / Tier / Section；
- 最低干预等级判断；
- 必要时A/B/C/D方案设计；
- User Verbatim核验；
- 用户/GPT双边脚本设计；
- Script Approval；
- Transcript Diff Audit；
- Screenshot Audit；
- 裁切方案；
- 多页拆分；
- annotation设计；
- caption设计；
- Evidence Lock；
- Process Report叙事；
- Block/Section-Level LaTeX Sync；
- 局部图与全局图规划；
- Part I / Part II Evidence整合；
- 内部Evidence Plan逻辑维护。

该职责在用户指定的范围内持续，由用户明确决定是否迁移。新对话仅仅读到“当前长期规划对话”不构成自动任命，也不能据此接管Evidence Master或宣布新的Lock。

### 4.2 Research Conversation

每个正式实验/任务的研究对话负责：

> **真正解决研究问题，并自然产生Original Evidence。**

它负责：

- 读老师材料；
- 网络研究；
- Source Audit；
- 方法候选；
- 用户真实质疑；
- 参数/指标讨论；
- 实验设计；
- 真实结果分析；
- Human-in-the-loop决策；
- 必要时标记Interaction Evidence Candidate。

它不负责：

- 为了截图重写真实聊天；
- A/B/C/D后期方案；
- Retrospective Reconstruction脚本；
- Evidence Tier；
- Screenshot Audit；
- Evidence Lock；
- Process Report总体Narrative。

原则：

> **Research Conversation produces evidence; Evidence Master curates evidence.**

研究正确性永远优先于截图效果。

### 4.3 Simulation Conversation

独立模拟对话只负责：

> **执行已经由Evidence Master与用户批准的双边脚本。**

它的身份是：

**Approved Script Renderer**

它仅在原始聊天经过最低干预梯度后仍无法合理使用时启用。

它不得：

- 规划Evidence；
- 修改Approved Script；
- 重新总结历史；
- 增加新候选；
- 自由扩写GPT回复；
- 改变Decision；
- 评价截图；
- 决定Evidence是否LOCK；
- 开始正式研究。

原则：

> **Simulator renders only approved retrospective evidence.**

---

## 5. 用户与Evidence Master的截图职责

### 5.1 用户职责

用户负责原生取证：

> **保存原生、完整、真实的ChatGPT Web截图。**

原则上：

- 不要求用户自行裁切；
- 不要求用户自行排版；
- 不要求用户自行制作annotation；
- 不要求用户判断最终截图应该放几页；
- 不要求用户提前为LaTeX调整截图尺寸。

用户应尽量：

- 保留完整消息边界；
- 宁可多截，不要少截；
- 关键Evidence附近保留必要上下文；
- 保存原始文件；
- 不覆盖raw截图。

用户可以自愿使用ShareX等工具进行长截图与图片分割；“不要求用户自行裁切”不是禁止提交已经分割的原生图片。收到长图和分割图时，保存两者及其对应关系；仅收到分割图时，如实记录当前可用原件，不伪造缺失的整张长图。正式取舍、裁切规格、排版与标注仍由Evidence Master负责。


### 5.2 Evidence Master职责

Evidence Master负责：

- 判断真正需要哪一段；
- 决定是否裁切；
- 决定是否拆成多页；
- 设计截图顺序；
- 设计annotation；
- 设计caption；
- 设计Contact Sheet；
- 设计LaTeX placement；
- 决定是否需要local diagram。

原则：

> **用户负责原生取证，Evidence Master负责正式呈现。**

---

### 5.3 Retrieval Screenshot / Formal Evidence Screenshot

Retrieval Screenshot 可以长滚动，用于历史检索、恢复上下文与寻找 Decision Unit。原生长截图及用户提供的分割图，只要保留真实UI、必要上下文且最终可读，可经无损裁切与分页用于正式Evidence；不因其属于长截图就要求重新模拟或另截一遍。

Formal Evidence Screenshot 以真实、可读的ChatGPT Web UI为基础；一张覆盖当前Interaction Window或其连续片段，宁可多张，不将长聊天压缩到一页。PNG preferred，保留原图宽高比和像素，不规定跨任务统一的最低宽度。按Visual System §8.7安排截图主导的版面；Evidence Master负责selection、crop、pagination、annotation、caption、LaTeX placement、audit、lock。

### 5.4 Resolution / Image Integrity

正式清晰度来自 raw 本身。记录 raw pixel size、final display size、effective PPI；裁切时同时记录 crop pixel size 与 crop bounds。有效 PPI = 实际显示区域的像素数 / 最终物理尺寸（英寸），横纵分别计算，取较小值；不能用整张 raw 的像素数除以局部 crop 的尺寸。

常规目标为 **>= 180 ppi，preferred >= 200 ppi**，同时检查最终页面中的实际可读性。新素材优先通过合理显示尺寸、无损裁切和拆页改善；未获明确原宽批准且仍无法达到适用清晰度条件时，记录 `RECAPTURE_REQUIRED`，暂停该证据的Lock并说明需要补取的具体范围。

**已批准原宽素材。**用户明确允许使用现有截图宽度，并已审核真实样页或成品效果时，可以在该素材与版式范围内记录 `APPROVED_NATIVE_WIDTH` 后继续制作。保留实际PPI、原件/裁片标识、批准来源及对应样页，不将其写成达到了更高PPI，也不反复要求用户加宽重截。后续无需因同一原宽再次请求批准；版式发生影响可读性的变化时检查受影响页面。

该批准只解决现有真实素材的显示宽度/分辨率取舍，不免除来源、原话、上下文和箭头关系的检查。关键文字确实无法辨认时先调整裁切、分页与侧注，仍无法恢复则登记具体缺项；不得猜写原句或用另一条消息替代。页面按200 dpi渲染仅用于检查，不增加截图原始细节。

禁止 low-res screenshot upscale、AI super-resolution 替代原图、generative redraw of ChatGPT UI、反复重采样后放大、fake sharpening、为塞进一页缩小到不可读。

### 5.5 Raw / Crop / Annotated

正式资产保留三层：raw、crop、annotated（可由 LaTeX/TikZ 源文件与 PDF overlay 表示）。raw 不得覆盖。

推荐：**raw PNG → lossless crop / LaTeX trim → direct embed → vector annotation**。LaTeX trim 可保留 raw 文件并以可追溯的裁切参数表达 crop 层。

禁止：raw → downsample → raster annotation → enlarge。

原始取证图、用户分割图、正式裁片与叠加层分别标识。裁片对应来源文件、顺序、像素边界和必要重叠；跨页保留连续关系。不得把旧LaTeX/PDF报告页面渲染成图后当作原始对话截图，也不得把不连续的裁片拼成一条未经标明编辑的“完整原消息”。正文整理或L2—L5的文本处理不授权改写原始UI像素；回顾/重构材料保持其明确身份。

### 5.6 每个新互动板块的真实用户UI入口

每个新的互动部分/板块，起始部分必须包含对应的真实用户消息UI截图；不能只有GPT回答，也不能用正文、引语框、人工排字或技术图来代替用户UI。标题和简短导语之后直接接这组证据，避免标题单占一页。

此要求作用于新的互动板块，而不是要求每一张续页重新贴一次用户消息。一个Decision Unit跨多页时，第一页展示用户原话及必要回应，后续页按连续关系承接。若用户消息依赖上一条GPT内容，允许在起始截图中按真实顺序一并保留前文；“用户可见”不等于把用户消息移到真实发生顺序之前。

缺少对应用户原件时，先检索已有素材、同组长图、分割图及相邻上下文；仍缺失则登记该板块缺项，不能用不相关的用户话语、报告截图或补写聊天凑齐。封面、目录及单纯综合图页不作为独立互动板块，亦不代替该板块的用户UI入口。

### 5.7 开篇的真实截图采集说明

Process Report开篇用一句话如实说明本次截图由谁采集、实际使用的工具/分割方式，以及AI在本次协作中的取证能力与制作职责。说明出现一次即可；详细来源映射保留源包，个别证据有不同来源或复盘性质时另行标明。

本次已验收Process成品的用户确认原句为：

> 文档中的所有对话截图，都是我在 ChatGPT 网页中通过sharex软件利用长截图一张一张手动截取然后再利用图片分割器功能一张张切割并提供的；在本次协作中，GPT 没有直接截取我的网页对话界面的功能。

这句保留为该成品的采集说明。未来任务按真实工具与能力填写，不强制使用ShareX，不把“本次协作中”的工具能力限定扩展为永久事实。采集说明与前言衔接按Report Writing Guide §12执行，不扩写为反复出现的制作免责声明。


---

## 6. Original Evidence 优先原则

Evidence优先级：

1. **Raw Original Evidence**
2. Original Evidence + crop / multi-page
3. Original Evidence + GPT trim
4. Minimal Consolidation
5. Decision Unit reorder
6. Retrospective Reconstruction / Current Reconfirmation

只要原始聊天本身可用，就不应模拟重写。

每项正式研究都应尽量：

> **实时保存Original Evidence，而不是事后重构。**

Simulator主要用于：

- Part I历史已经发生；
- 原聊天极端冗长；
- 同一Decision散落很远；
- 上下文无法自然拼接；
- 原始聊天无法直接形成可读Evidence。

---

## 7. Minimal Intervention Principle

对已有真实聊天，编辑程度必须保持在实现正式可读性所需的最低水平。

执行原则：

> **能通过裁切解决的问题，不通过改写解决。**

> **能通过多页解决的问题，不通过压缩解决。**

> **能通过删除冗余解决的问题，不重新创作。**

> **能通过原句拼接解决的问题，不专业化改写。**

> **只有原始证据无法合理使用时，才进入Retrospective Reconstruction。**

---

## 8. 最低干预等级 L0–L5

每条Evidence必须先判断最低可行干预等级。

### L0 — RAW ORIGINAL

直接使用真实原始聊天。

允许：

- 选择消息范围；
- 多页截图；

不改文字。

### L1 — CROP / MULTI-PAGE

仍使用原始聊天。

允许：

- 裁切与当前Decision无关的上下区域；
- 将同一原聊天拆成2–3页；
- 用caption说明上下文。

不修改聊天文字。

### L2 — GPT TRIM

用户消息保持原文。

GPT回复只做：

- 删除重复背景；
- 删除无关支线；
- 删除重复例子；
- 删除重复总结；
- 删除无关收尾。

原则：

> **以删除为主，不重新写答案。**

所有与当前Decision直接相关的实质内容原则上保留。

### L3 — MINIMAL MERGE

仅当用户2–3轮实际上只是重复或补全同一意思时使用。

要求：

- 优先直接拼接用户原句；
- 删除重复；
- 只做最小连接；
- 不加入新专业术语；
- 不改变语气；
- 不提升“专业程度”。

### L4 — REORDER WITHIN DECISION UNIT

同一Decision在不同时间点有无新证据的补充时，可在Report Order中归组。

要求：

- Historical Order必须保留；
- Report Order可以调整；
- 必须记录Reorder Reason；
- 依赖新证据的内容不得前移。

### L5 — RETROSPECTIVE RECONSTRUCTION

仅当L0–L4都无法形成可用Evidence时使用。

必须：

- 透明标注复盘性质；
- 依据真实历史；
- Verbatim-First；
- 用户/GPT双边脚本预审核；
- Transcript Diff Audit；
- Simulator逐字执行。

默认永远选择：

> **能够解决问题的最低干预等级。**

---

## 9. Terminology Ownership / 术语所有权

专业术语必须遵循真实历史中的出现顺序与提出者。

如果某个概念最初由GPT提出，例如：

- Human-in-the-loop；
- Source Audit；
- CONFIRMED / CANDIDATE / UNRESOLVED；
- Full Mirror；
- Decision Chain；

不得在重构更早用户消息时倒塞给用户。

正确模式：

### 用户
用自己的自然语言表达问题。

### GPT
将问题抽象成专业术语或正式规则。

### 用户
确认、修改或采用该术语。

例如：

用户可以说：

> “我不希望最后变成你们都做完了，然后我只说一句可以。”

而不是在更早阶段直接写：

> “用户不能成为形式性确认者。”

除非历史证据证明用户当时确实使用过该术语。

---

## 10. Verbatim-First Policy

用户侧采用：

**VERBATIM-FIRST**

只要原话可用，优先保留：

- 用户自己的词；
- 自然口语；
- 原句结构；
- 判断方式；
- 犹豫；
- 否定；
- 补充；
- 强调。

允许：

- 删除纯重复；
- 拼接同义表达；
- 调整明显影响理解的连接；
- 增加最少必要上下文。

禁止：

- 专业化润色用户语言；
- 把用户改写成GPT风格；
- 增加过去没有的观点；
- 把犹豫改成坚定；
- 把后来才知道的结论提前；
- 改变演化逻辑。

---

## 11. Historical Retrieval Card

每条Part I Evidence进入脚本设计前，应先建立：

# HISTORICAL RETRIEVAL CARD

至少包括：

- Evidence ID；
- Topic；
- 预计历史阶段；
- 可能关键词；
- 用户可能出现的原句片段；
- GPT可能出现的关键词；
- 希望找到的起止范围；
- 该段历史为什么重要。

如果Evidence Master没有可靠逐字原文，应：

> **给用户搜索关键词，让用户回原始聊天中寻找。**

不得凭最终规则反向编造对话。

---

## 12. Original Transcript Packet

找到历史后，正式建立：

# ORIGINAL TRANSCRIPT PACKET

包括：

- Original User Message 1；
- Original GPT Response 1；
- Original User Message 2；
- Original GPT Response 2；
- ……
- 必要的Neighbouring Context。

原则：

> **宁可先收集多一点原文，再做删减。**

没有Transcript Packet，不进入重度精修。

---

## 13. Turn Classification

对Transcript Packet中的每个turn进行内部分类：

### CORE
直接推动Decision。

### SUPPORT
为Decision提供重要解释。

### DUPLICATE
纯重复。

### CONTEXT
理解上下文需要，但不是决策核心。

### LATE_SUPPLEMENT
后来补充前面的同一Decision，没有新证据。

### NEW_EVIDENCE
引入新信息，并改变或推动判断。

### CORRECTION
明确修正此前观点或规则。

### FINAL_CONFIRMATION
最终确认。

Turn Classification用于决定：

- 是否删除；
- 是否裁切；
- 是否合并；
- 是否调序；
- 是否必须保持原位。

---

## 14. Decision Unit

正式Evidence的基本组织单位不是“一条消息”，而是：

> **围绕同一个Decision形成的一组真实消息。**

一个Decision Unit可能跨越：

- 多轮聊天；
- 不同时间；
- 后续无新证据的补充。

内部应记录：

- Unit ID；
- Core Question；
- Historical Turns；
- Trigger；
- User Judgment；
- GPT Response；
- Evidence；
- Final Decision；
- Later Supplement；
- New Evidence Boundary。

---

## 15. 后补内容的三类处理

### 15.1 重复补充

后来只是换一种方式重复同一意思。

处理：

- 可删除一次；
- 或最小合并。

### 15.2 完善性补充

后来补全同一Decision，但没有新证据，也没有改变结论。

处理：

- 可归入同一Decision Unit；
- Report Order可相邻；
- Historical Order必须保留。

### 15.3 证据驱动修正

后来因为：

- 新证据；
- 新实验；
- 老师新要求；
- 新错误发现；

导致Decision发生变化。

处理：

> **必须保留真实演化顺序。**

不得提前。

---

## 16. Question-Led Principle

Workflow Construction必须优先沿着：

> **用户真实提问思路**

恢复。

禁止先设计一个漂亮框架，再挑历史去证明它。

正确顺序：

**真实历史问题\
→ Historical Question Inventory\
→ Decision Unit归组\
→ 代表性筛选\
→ 必要编辑性调序\
→ Narrative Spine\
→ Report Evidence Map\
→ 最终Section归纳。**

Framework / Block只能用于编辑组织，不是历史来源。

---

## 16.1 Process Report正式叙事语言

正式 Process Report 的正文默认采用：

> **第一人称研究复盘口吻。**

目标是让老师读到：

> **“我是怎样和AI一步一步讨论、判断、修改、验证并完成研究的。”**

而不是第三方审计式描述。

默认写法：

- 用户自己的动作、发现、判断、质疑、修改、选择和确认，用 **“我”**；
- 只有确实由用户与 GPT 共同完成的动作，才使用 **“我们”**；
- AI角色直接写 **GPT**；
- 工程执行角色直接写 **Codex**；
- 不把正式正文写成“用户提出……”“本项目形成……”“系统建立……”的第三方项目说明书；
- `User / Human Judgment / Evidence Master` 等角色名可以用于图示、标签、协议定义和必要的方法说明，但不作为正文默认叙事视角；
- 技术术语应在真实问题出现后再引入。例如用户先用自然语言表达“讨论后还是不能确定就都跑一下”，正文可随后说明“GPT后来把这种情况整理为 UNRESOLVED”，不得反写成用户当时已经使用该专业术语。

正式文字采用：

- **A — 自然研究叙事**作为主体；
- **C — 真实轻口语**用于关键 Human Judgment、转折与用户原本就很自然的判断；
- **B — 简洁技术定义**用于术语、方法、状态和必要规则。

即：

> **正文自然叙事，关键判断保留人的语气，技术定义保持准确。**

允许整理真实历史形成连贯叙事，但不得改变：

- 谁提出了观点；
- 谁做出判断；
- 判断发生的先后关系；
- 原始不确定程度；
- 最终Decision的因果关系。

### 16.2 Formal Section Aggregation

内部 Evidence Unit / Block / Evidence ID 不等于正式报告章节。

正式 Process Report 应按自然研究故事聚合内容，例如：

- 任务理解与要求确认；
- Human–AI工作流构建；
- 研究与审核机制；
- Multi-Agent体系构建；
- Experiment Decision Process；
- 文档、Evidence与可视化系统；
- 整体工作流回顾。

具体章节随真实任务调整，不机械固定。

禁止把正式正文组织成：

> `Block 01 / Block 02 / Block 03 / ...`

或：

> “一条规则 = 一节 / 一页”。

多个相关 Decision Unit 应在不改变真实顺序和因果的前提下合并为一个自然叙事板块。新互动板块的用户UI入口按§5.6执行，标题与截图同页、侧注比例和箭头排版按Visual System执行。

### 16.3 报告改写与证据原文的边界

已批准的报告文风调整，可以组织真实事实、减少冗余、改进章节衔接；不能因此修改原始聊天、重写截图内的用户原话、添加过去不存在的质疑或升级历史确定程度。

正式叙述里的“我/我们”仍必须对应真实行为。用户事先批准比较、回退和停止规则后，系统按规则执行的具体选择，应准确写为授权内的系统裁决；不能补写成用户逐条判断，也不能用“人必须参与每一步”的图式制造缺失回合。

技术实验报告可以用共同输入、参考/候选、检查、实测与判断解释最终方法。它不因此成为历史Interaction Evidence，也不自动使用本协议的User anchor或术语所有权结论。报告作者自检不替代Evidence Master的来源核查与Lock。

具体正文组织和图文衔接参考Report Writing Guide；原话摘录、裁切、编辑干预和真实历史仍按本协议执行。

---

## 17. 后台完整、前台代表性

内部历史恢复应尽量完整。

正式Process Report不需要逐一展示所有历史问题。

采用：

> **后台完整恢复 → 前台代表性选择。**

正式Part I只选择：

- 真正改变工作流方向的Decision；
- 明显体现用户判断的互动；
- 对后续研究机制有解释价值的节点。

多个相关问题应合并成自然Decision Process。

禁止机械形成：

> “一个问题 = 一条Chain = 一张截图”

---

## 18. Part I / Part II 边界

### 18.1 Part I — Workflow Construction

只保留真正解释：

> **Human–AI工作流为什么会这样形成。**

典型主题：

- GPT / 用户 / Codex角色与决策权；
- 任务范围与T1–T4；
- 资料优先级与Source Audit；
- CONFIRMED / CANDIDATE / UNRESOLVED；
- 公平并行实验；
- AI建议的Human challenge与Evidence机制；
- Experiment / Process Report分工；
- Brainstorm职责；
- Interaction Evidence体系；
- 重要Visual / Diagram表达规则；
- Codex → GitHub → GPT remote audit；
- GitHub Full Mirror与Submission Package分离；
- 双重审核与Workflow Freeze。

### 18.2 Part II — Experiment Decision Process

具体任务技术问题进入Part II，例如：

- CRS；
- WGS84 / GCJ02；
- 投影；
- 95m vs 400m；
- Douglas–Peucker；
- 评价指标；
- 参数敏感性；
- LLM Agent实验；
- 其他Experiment-specific技术问题。

### 18.3 后期证据加工流程不进入正式Part I

以下属于internal production protocol：

- L0–L5；
- A/B/C/D；
- 双边脚本预锁定；
- Simulator；
- Turn Classification；
- Screenshot Audit；
- Diff Audit；
- Evidence Lock；
- WORKFLOW_EVIDENCE_PLAN；
- Block-Level LaTeX Sync；
- 后期裁切和排版流程。

老师要看的是：

> **真实Human–AI工作流。**

不是：

> **我们后来怎样加工这些截图。**

开篇依§5.7保留一句真实采集说明即可；它不要求把具体截图加工日志写成独立研究章节。

### 18.4 两份报告的技术重叠不等于叙事复制

同一个技术事实可以进入两份报告，但作用不同：Experiment Report说明方法、比较和结果为何支持取舍；Process Report说明这些问题怎样在真实互动中被发现、判断和验证。

不得为了避免重复，把Experiment Report的实际Workflow/验证方法全部删除；也不得把其移出的哈希、提交管理和普通Debug全部倒入Process Report。历史素材决定过程报告叙事，最终方法结构不能反向生成历史。

---

## 19. A/B/C/D 的新定位

A/B/C/D不再是每条Evidence一开始就生成四套“新对话”。

只有在L0–L4处理后仍存在多个合理编辑方案时，才比较A/B/C/D。

建议定义：

### A — RAW / NEAR-RAW ORIGINAL
尽量直接使用原始聊天。

### B — ORIGINAL + TRIM
用户原文不改，GPT主要删除冗余。

### C — MINIMAL CONSOLIDATION
用户重复/完善性补充做原句最小合并。

### D — RETROSPECTIVE RECONSTRUCTION
仅在原聊天确实无法直接使用时重构。

默认推荐优先级：

**A > B > C > D**

除非实际可读性证据支持更高干预。

---

## 20. GPT回复精修规则

GPT原回复默认：

**ORIGINAL-FIRST**

优先保留：

- 原长度节奏；
- 原解释结构；
- 原候选比较；
- 原不确定性；
- 原语气。

可以删除：

- 重复背景；
- 与当前Decision无关的支线；
- 过多重复例子；
- 重复总结；
- 无关收尾。

不应：

- 把长回复整体重写成“截图专用短答案”；
- 让GPT提前知道后来的Decision；
- 删除用户后续真实回应所依赖的内容。

原则：

> **所有与当前Decision直接相关的实质内容原则上保留。**

不使用机械字数压缩比例。

---

## 21. 多页优先原则

核心互动内容真实但较长时：

> **优先多页，不优先重写。**

允许：

- 2页；
- 3页；
- 更多必要页数。

页面拆分优先：

- 按自然消息边界；
- 按逻辑段落；
- 避免截断关键句；
- 保留最终确认。

版式系统应适应真实Evidence，而不是强迫真实Evidence适应单页。新互动板块首先落实§5.6的用户UI入口；续页明确承接，不机械重复用户气泡。截图主体与简短侧注的配比、标题随首图排布及箭头留白按Visual System §8.7执行。

---

## 22. 上下文依赖处理

如果原始用户消息中出现：

> “这个不太对”
> “就按这个”
> “我还是觉得前面那个更好”

等强上下文表达：

优先：

1. 连同必要上一条消息一起截图；
2. 在caption中补最少上下文；
3. 使用annotation指出讨论对象；

而不是改写用户原话。

---

## 23. 一段聊天包含多个Decision时

如果同一原始聊天同时包含多个不同Decision：

- 不强行让一张截图证明全部内容；
- 可以从同一原始聊天形成多个Evidence excerpt；
- 每个Evidence只聚焦一个Decision；
- 原始来源保持一致。

---

## 24. 用户贡献被长GPT回复淹没时

优先通过视觉表达解决：

- 保留真实用户UI入口，让用户关键句充分可见；
- 以精确箭头指出有依据的对应关系；
- 必要的Human Reasoning → Evidence → Decision局部图；
- 截图主导的页面节奏；
- 截图分段；
- 简短caption。

不得通过删掉重要GPT内容来人为制造“用户贡献”。

原则：

> **视觉问题优先用视觉系统解决，而不是用篡改对话解决。**

---

### 24.1 Phrase-level Interaction Trace / Micro Trace

Interaction Trace 是一个完整 decision interaction；Micro Trace 是其中一个具体 phrase correspondence。

基本结构：**GPT before phrase ↕ USER anchor phrase ↕ GPT after phrase**。USER anchor phrase 是视觉中心；双侧关系并非每个 anchor 都必须具备。

### 24.2 Interaction Window

正式画箭头前至少检查 previous 1–2 relevant GPT turns、current User turn、following 1–2 relevant GPT turns。必要时延伸到 GPT before → User anchor → GPT revision → User confirmation → GPT freeze；不得只看孤立句子。

Human Action 至少允许 QUESTION、CHALLENGE、CORRECTION、REJECTION、SELECTION、SUPPLEMENT、CONFIRMATION。

Trace Relation 可记录 RESPONDS_TO、CHALLENGES、CORRECTS、REJECTS、SELECTS、SUPPLEMENTS、CONFIRMS、LEADS_TO、REVISED_AS、ADOPTED_AS。

允许真实 one-to-one、one-to-many、many-to-one；每根箭头都必须有原文语义依据，时间相邻本身不构成关系。不得为了对称强行给每个 User phrase 配上下两条箭头。

### 24.3 Exact Phrase / Arrow Only / Side Note

对真实对话截图采用 **ARROW_ONLY**：只用精确矢量箭头表示对应关系，不加荧光圈、彩色框、半透明填充、下划线或圈号覆盖聊天。原生UI自带的元素保持原样；独立技术图正常使用的节点与边框不受此截图标注规则限制。

每根箭头制作前明确：它支持什么Evidence Claim、对应哪一处真实原句、关系是什么、箭头从哪里指向哪里。区分“原句之间的真实回应/修正关系”和“侧注指向原句的阅读提示”，后者不能伪装成历史因果。

仍采用最小充分的**语义范围**：只指向证明该Claim所需的原句位置，而非重新画一个最小框。箭头端点落在目标短语紧邻的留白或明确指向该短语；不能只停在消息外框、页面边缘或不相干空白。起点、终点与方向均须可解释。

箭头优先沿截图外侧、栏间和局部留白走线，不压字，避免大量交叉、任意分叉和装饰性绕线。关系过密时拆页或减少无新增信息的标注，不删去关键原话来腾空间。不为凑数量给每个用户短语强配两根箭头。

Side Note简短说明我的要求或判断、GPT的回应变化及必要后续意义；不长篇复述截图，不抢占截图的主要版面。约40—80汉字为通常参考，不是每页固定字数。具体截图/侧注比例、P2箭头颜色和页面密度统一按Visual System §8.7执行。

采用raw/crop图片直接嵌入及可编辑TikZ/PDF矢量箭头。截图、裁切规格、箭头层和正文分开维护，不能将整页报告栅格化后复用为新的Evidence原件。

### 24.4 Render-Level User UI / Phrase / Arrow Verification

annotation specification通过后，必须在实际XeLaTeX/PDF render中检查最终效果：

- 新互动板块的起始部分是否真正出现对应用户UI，续页是否明确承接；
- 原句及必要上下文是否可读，有无截断字形、缺失句尾或编辑性拼接歧义；
- 截图是否为视觉主体，侧注是否过多，标题是否与首组证据衔接；
- 是否仍存在荧光圈、框、填充或其他覆盖原话的旧标注；
- crop / scaling / placement变化后，箭头起终点是否仍对准批准短语；
- 箭头方向与关系是否准确，是否压字、交叉混乱或看似指向另一句话；
- 原图、裁片、最终显示尺寸和实际PPI是否对应，原宽例外是否有明确批准。

审核字段和结果取值由§30.H统一定义，不维护另一套Box检查表。旧版本的BOX RANGE记录按历史保留；当前箭头页不要求重新制作圈框来通过旧测试。无法支持的关系或无法辨认的关键原句，应修订或补证后再Lock。

### 24.5 Decision Authority

Evidence Master决定用户UI入口、User anchor、GPT before/after、phrase关系、箭头语义与对应位置、turn调序、Evidence入选与原文整理规格。Codex只能按批准的Evidence Plan / annotation specification实现裁切、走线与排版，不自行推断、补造关系或恢复圈框。缺少specification时暂停受影响的真实页面；模板synthetic demo不构成真实Evidence或批准关系。

### 24.6 技术核验图与Human–AI Evidence图区分

技术图可以展示真实原始输入、参考方案、候选方案、独立评价、判断条件、适用模式下的反馈与回退。这类图以代码、数据和方法关系为依据，不需要凭空添加User Observation或Human Challenge。

只有实际历史及Interaction Window支持相应人类行为时，才使用Human Reasoning → Evidence → Decision表达该段互动。箭头表达方法上的数据/控制依赖，不自动证明历史上谁回应或改变了谁。

GPT直接制作报告、图表或LaTeX不自动迁移Evidence Master职责。角色迁移须由用户明确指定；作者自检、工程检查、用户文稿认可与Evidence Lock分别记录。

---

## 25. Transcript Diff Audit

任何L2–L5精修版本在截图前，都必须进行：

# TRANSCRIPT DIFF AUDIT

### User Side

检查：

- 删除了什么；
- 合并了什么；
- 是否新增词语；
- 是否新增专业术语；
- 是否改变语气；
- 是否改变观点确定程度。

### GPT Side

检查：

- 删除了哪些段落；
- 是否改写技术内容；
- 是否改变候选；
- 是否提前知道后来的Decision；
- 是否删除后续用户回应所依赖内容。

### Sequence

检查：

- 是否调序；
- 调序内容是否只是无新证据补充；
- 是否移动了NEW_EVIDENCE；
- 是否产生hindsight bias。

输出：

- `INTERVENTION LEVEL: L0–L5`
- `HISTORICAL MEANING CHANGED: YES / NO`
- `TERMINOLOGY OWNERSHIP VIOLATION: YES / NO`
- `SEQUENCE CAUSALITY PRESERVED: YES / NO`

只有：

`HISTORICAL MEANING CHANGED: NO`\
`TERMINOLOGY OWNERSHIP VIOLATION: NO`\
`SEQUENCE CAUSALITY PRESERVED: YES`

才能进入正式截图。

---

## 26. 双边脚本预审核

只有进入L5 Retrospective Reconstruction时，用户话术和GPT回复必须在截图前完整设计并审核。

脚本状态：

`DRAFT`
→ `USER_SELECTED`
→ `REVISED`
→ `SCRIPT_APPROVED`

内部记录：

`Reconstruction Control: USER_AND_GPT_PREAPPROVED`

完整写死GPT回复不意味着模板化。

必须保持自然节奏，不允许所有Evidence都变成：

> “你说得对 → 总结三点 → 正式冻结。”

---

## 27. Simulation Conversation执行规则

Simulation Conversation只接受Evidence Master已批准脚本。

推荐：

### Step 1 — LOAD SCRIPT

用户加载完整Approved Script。

Simulation GPT只回复：

`SCRIPT LOADED`

控制块不进入正式截图。

### Step 2 — NATURAL DIALOGUE

用户按Approved User Script逐轮发送。

Simulation GPT逐字输出Approved GPT Response。

不得：

- 润色；
- 改词；
- 增删句；
- 加标题；
- 加解释；
- 新增建议；
- 一次输出多个后续GPT turn。

---

## 28. 正式Research Conversation实时证据机制

每项正式研究从开始时即优先实时保存Original Evidence；既有任务的历史起点不限制后续任务的适用范围。

推荐：

**真实研究问题\
→ GPT候选\
→ 用户真实质疑/修改\
→ 资料/数据/实验\
→ Decision\
→ 标记Interaction Evidence Candidate\
→ 用户保存原生截图\
→ 继续研究。**

Research Conversation可以轻量记录：

- Candidate ID；
- Topic；
- Trigger；
- User Verbatim；
- Evidence；
- Final Decision；
- Message Range。

但它不负责最终Evidence设计。

---

## 29. Experiment Interaction Handoff

一个研究阶段结束后，Research Conversation可以输出：

**Experiment Interaction Handoff**

每条候选包括：

- Candidate ID；
- Topic；
- Trigger；
- Original Message Range；
- User Key Verbatim；
- Evidence Used；
- Final Decision；
- Why It May Matter。

它不得：

- 决定最终Tier；
- 改写原聊天；
- 设计模拟脚本；
- 决定正式Report Order；
- 宣布Evidence LOCK。

这些由Evidence Master完成。

---

## 30. Screenshot Audit

所有正式截图必须回Evidence Master审核。

检查：

### A. Historical Fidelity
是否改变真实历史。

### B. User Authenticity
是否来自对应的真实用户UI、是否保持本人原话与语气；新互动板块的起始部分是否满足§5.6，而非只出现文字复述。

### C. GPT Fidelity
GPT回复是否符合真实角色和Decision。

### D. Decision Value
是否证明有价值Decision。

### E. Visual Usability
长度、重点、裁切与续页是否清楚；按Visual System检查截图主体、简短侧注、标题衔接、箭头准确和实际阅读体验。

### F. Provenance
标记：

- ORIGINAL
- ORIGINAL + CROP
- ORIGINAL + TRIM
- MINIMAL CONSOLIDATION
- RETROSPECTIVE RECONSTRUCTION
- CURRENT RECONFIRMATION

### G. Required Label
是否需要标注：

- 原始交互；
- 阶段性历史复盘；
- 当前重新确认。

结果只有：

- `PASS`
- `REVISE`

---

### H. User UI / Phrase / Arrow / Readability Audit

Screenshot Audit按实际对象逐项记录，取值统一为：

- `USER UI ENTRY: PASS / REVISE / CONTINUATION`
- `ANNOTATION MODE: ARROW_ONLY / NONE`
- `PHRASE MATCH: PASS / REVISE`
- `ARROW RELATION: PASS / REVISE / NOT_APPLICABLE`
- `ARROW ENDPOINT: PASS / REVISE / NOT_APPLICABLE`
- `PAGE READABILITY: PASS / REVISE`
- `SOURCE RESOLUTION: PASS / APPROVED_NATIVE_WIDTH / RECAPTURE_REQUIRED`

检查对应用户原话确在起始UI截图中；GPT before/after确为有关原句；箭头具有语义依据且端点、方向准确；没有圈框、压字和错误裁切；实际页面的截图、侧注、标题和续页可读。`CONTINUATION`只用于承接已建立用户入口的续页，并记录其起始页；不能用于没有用户UI的新板块。

没有设计箭头的Contact Sheet或未标注裁片，记录`ANNOTATION MODE: NONE`及不适用依据，不虚构关系或通过记录；若出现旧圈框/高亮则页面检查为`REVISE`。`APPROVED_NATIVE_WIDTH`须满足§5.4的明确批准、实际尺寸/PPI和可读性检查，不能作为来源或原话真实性的豁免。

任一适用项`REVISE`或`RECAPTURE_REQUIRED`均阻止该Evidence的总审核通过与Lock。符合条件的原宽批准可与其他检查一起进入Evidence Master审核，不再机械要求补截更宽原图。旧BOX RANGE/高亮检查只作为历史记录保留，当前新审查不再以圈框范围为门槛。

---

## 31. Evidence Lock

审核通过后登记：

# EVIDENCE LOCK

- Evidence ID
- Topic
- Decision Unit
- Historical Turns
- Historical Order
- Report Order
- Reordered?
- Reorder Reason
- Part
- Section
- Tier
- Provenance
- Intervention Level
- Historical Basis
- User Verbatim
- GPT Verbatim
- Final Approved Script（若适用）
- Decision Demonstrated
- User Contribution
- GPT Contribution
- Evidence / Verification
- Final Decision
- Raw Screenshot
- User UI Entry Screenshot / Opening Page
- Capture Method / Supplied Split Images / Available Parent Capture
- Crop / Split Source Mapping
- Cropped Screenshot
- Annotated Screenshot
- Suggested Caption
- Local Diagram Candidate
- Transcript Diff Audit Result
- Reconstruction Control（若适用）
- Interaction Window
- User Anchor Phrase(s)
- GPT Before Phrase(s)
- GPT After Phrase(s)
- Trace Relation(s)
- User UI / Phrase / Arrow / Readability Audit Result
- Raw Screenshot Pixel Size
- Crop Pixel Size / Bounds
- Final Display Size
- Effective PPI
- Native-Width Approval / Applicable Sample or Page（若适用）
- Annotation Medium / Mode
- Status: LOCKED

---

## 32. Evidence状态机

### Original Evidence

`IDENTIFIED`
→ `HISTORY_RETRIEVED`
→ `TRANSCRIPT_PACKET_READY`
→ `TURN_CLASSIFIED`
→ `INTERVENTION_SELECTED`
→ `RAW_CAPTURED`
→ `SCREENSHOT_REVIEWED`
→ `CROPPED / ANNOTATED`
→ `LOCKED`

### Retrospective Evidence

`IDENTIFIED`
→ `HISTORY_RETRIEVED`
→ `TRANSCRIPT_PACKET_READY`
→ `TURN_CLASSIFIED`
→ `INTERVENTION_SELECTED`
→ `OPTIONS_READY`
→ `SCRIPT_SELECTED`
→ `SCRIPT_APPROVED`
→ `DIFF_AUDITED`
→ `SIMULATED`
→ `RAW_CAPTURED`
→ `SCREENSHOT_REVIEWED`
→ `CROPPED / ANNOTATED`
→ `LOCKED`

如需修改：

`LOCKED → REOPENED`

不得静默覆盖历史版本。

---

## 33. Evidence Tier / 证据预算

### Tier 1 — Core Decision
核心转折。

可能使用：

- 1–3页或更多必要页；
- 独立截图；
- annotation；
- Local Diagram。

### Tier 2 — Supporting Decision
重要但无需长篇。

可能：

- 半页到1页；
- 单张截图；
- Contact Sheet重点单元。

### Tier 3 — Context
用于说明阶段存在。

通常：

- Contact Sheet一格；
- 简短caption；
- 不独立展开。

Tier按Decision价值确定，不按原聊天长度确定。

---

## 34. 内部任务文档

实际任务计划作为internal evidence维护：

`evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md`

或对应Part II目录中的Evidence Plan。

不进入ChatGPT Project source。

Evidence Master负责逻辑维护；需要正式写入仓库时交由Codex或用户同步。

至少记录：

- Question / Candidate ID；
- Historical Order；
- Decision Unit；
- User Verbatim；
- GPT Verbatim；
- Turn Classification；
- Decision；
- Evidence ID；
- Report Order；
- Tier；
- Intervention Level；
- Mode；
- Screenshot；
- Crop Plan；
- Annotation；
- Caption；
- Diagram；
- Status。

---

实际字段以 [WORKFLOW_EVIDENCE_PLAN](../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md) 的有效schema为准。新候选尚未取得原图或Evidence Master批准时，对应缺失字段保持未定，不制造Evidence ID、phrase或LOCK；不能因此清空已有真实有效记录。Project Sources中的参考PDF和源包也不自动构成内部Evidence Plan或逐项Lock。

## 35. LaTeX同步策略

采用：

**BLOCK / SECTION-LEVEL LATEX SYNC**

不要求每个Evidence完成后立即重排全文。

当一个自然Narrative Section的主要Evidence全部LOCK后：

**确定Section结构\
→ Evidence顺序\
→ Screenshot Placement\
→ Crop / Multi-page\
→ Annotation\
→ Captions\
→ Contact Sheet\
→ Local Diagram\
→ Block Preview\
→ 审核\
→ BLOCK LOCK。**

原则：

> **先让LaTeX版式适应真实Evidence，再考虑进一步精简Evidence。**

同步时同时检查：

- 正式正文是否使用第一人称研究复盘口吻；
- 是否把内部 Block / Evidence ID 误当成正式章节；
- 多个相关Decision是否已经聚合为自然Narrative Section；
- 新互动板块是否有真实用户UI入口，标题是否接首组证据；
- 截图主体和侧注是否符合批准版式，是否已移除旧圈框/高亮；
- 每根箭头在最终render中是否准确指向批准phrase；
- 原宽批准、实际可读性和源图/裁片映射是否仍适用。

接管已验收的局部/完整文稿时，保护对应源码、原图、批准规格与PDF版本；不得让旧模板或生成器把第一人称改回“用户”、恢复旧圈框、缩窄截图或重新按Block机械拆章。影响已锁短语、用户UI入口、箭头关系或呈现的变更需重新审核相应范围；纯外围文字调整也应核查是否改变分页与引用，不自动重开无关实验。

已验收的完整Process PDF/源包与较早的局部前期参考，按Visual System §16分别登记当前成品和历史身份；复用正文与制作方式时保留原证据来源及实际Lock范围。较早文件不覆盖新版已验收的呈现方式，也不能凭文件名推定逐项Lock。已有真实材料先查找再列缺项，不因另一个工程环境没有副本就声称全部原件不存在。

---

## 36. 图片与流程图时机

### Evidence / Section阶段可制作

- screenshot crop；
- annotation；
- Contact Sheet；
- Human Reasoning → Evidence → Decision；
- Horizontal Candidate Decision Tree；
- local Editorial Decision Board。

仅在确实提高理解时制作，不要求每条Evidence配图。

### 最后制作

正式：

**Global Workflow Evolution Map**

必须在主要Workflow Construction Evidence全部LOCK后设计。

前期只维护：

**Conceptual Evidence Map / Narrative Spine**

不提前冻结全局图。

---

## 37. Housekeeping Boundary

以下通常不成为独立正式Evidence：

- Zone.Identifier；
- cache；
- ordinary path fixes；
- routine git status；
- 临时LaTeX warning；
- meaningless shell/debug；
- build housekeeping。

除非它们真实触发Workflow Decision变化，否则只留internal evidence。

---

## 38. 正式阶段顺序

### Phase 0 — Historical Reconstruction / Narrative Planning

针对Part I：

- Historical Question Inventory；
- Decision Unit归组；
- Narrative Spine；
- Report Evidence Map。

### Phase 1 — Evidence Production

Part I：

- Historical Retrieval Card；
- Original Transcript Packet；
- Turn Classification；
- 最低干预L0–L5；
- Original Evidence优先；
- 必要时Retrospective Reconstruction；
- Screenshot；
- Audit；
- Lock。

Part II：

- Original Research Conversation优先；
- 实时保存原生截图；
- Evidence Master后续筛选、裁切、排版和Lock。

### Phase 2 — Block / Section-Level LaTeX Sync

自然Narrative Section完成后进行局部排版和视觉审核。

### Phase 3 — Synthesis Visuals

主要Workflow Evidence冻结后制作Global Workflow Evolution Map及必要综合图。

### Phase 4 — Full Process Report

整合：

- Workflow Construction；
- Experiment Decision Process；
- Contact Sheets；
- Evidence；
- 图表；
- Human-Style Review；
- 真实性审核；
- 最终视觉审核。

---

## 39. 最高执行原则

1. **真实聊天优先于重构聊天。**
2. **Raw Original优先于任何精修版本。**
3. **能裁切不改写，能多页不压缩。**
4. **长是版式问题；乱是Narrative问题，两者分开处理。**
5. **用户负责保存真实原生截图，可自愿提供长图分割件；正式裁切规格、排版、annotation和LaTeX呈现由Evidence Master负责。**
6. **Research Conversation负责产生真实Evidence。**
7. **Evidence Master负责筛选、整理、裁切、审核和Lock。**
8. **Simulation Conversation只执行必要的Approved Retrospective Script。**
9. **专业术语遵循真实Terminology Ownership。**
10. **用户原话优先，不做专业化润色。**
11. **GPT回复以Original-First为原则，精修主要做删除而非重写。**
12. **后台历史恢复尽量完整，正式报告只保留代表性Decision。**
13. **Decision Unit优先于单条消息。**
14. **Historical Order与Report Order同时保留。**
15. **允许无新证据的编辑性调序，不允许改变因果。**
16. **依赖新证据的修正必须保留真实顺序。**
17. **L0–L5选择能够解决问题的最低干预等级。**
18. **A/B/C/D只在确实存在多种编辑方案时使用。**
19. **L2–L5必须通过Transcript Diff Audit。**
20. **Part I只讲Workflow Construction，不混入具体Experiment技术问题。**
21. **Part II记录具体任务中的真实研究Decision。**
22. **后期Evidence生产协议不作为正式Workflow Construction故事。**
23. **截图必须由Evidence Master独立审核。**
24. **未LOCK不作为正式Evidence。**
25. **内部Evidence Plan不进入Project source。**
26. **LaTeX按自然Block/Section同步。**
27. **局部图随Evidence成熟制作。**
28. **Global Workflow Evolution Map最后制作。**
29. **视觉问题优先用视觉设计解决，不用篡改对话解决。**
30. **Process Report呈现真实决策演化，不制造一个更漂亮但不真实的历史。**
31. **Process Report正文默认使用“我”的第一人称研究复盘口吻，不写成第三方项目审计。**
32. **内部Evidence Unit / Block用于生产管理，正式章节按自然研究故事聚合。**
33. **每个新互动板块以真实用户UI为入口；截图标注采用纯箭头，每条对应关系均有明确Evidence Claim和最小充分原句依据。**
34. **每根箭头必须在最终render中准确指向批准原句；原句之间的真实关系与侧注阅读提示分别标明。**
