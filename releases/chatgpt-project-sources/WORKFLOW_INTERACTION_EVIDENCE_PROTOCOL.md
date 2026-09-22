# 《智慧城市与位置服务》Workflow Interaction Evidence Protocol

Version: **v2.3**\
Status: **ACTIVE / LONG-TERM RULE**\
Purpose: **Process Report · Workflow Construction · Experiment Decision Process · Human–AI Interaction Evidence**

本协议专门约束：真实历史恢复、原始聊天取证、Narrative规划、Evidence设计、最小必要编辑、对话精修/重构、Simulation执行、原始研究对话证据采集、截图、审核、Evidence Lock、Block/Section级LaTeX同步与最终综合图制作。

优先级：

**老师最新正式要求 / 用户最新明确要求 > 当前批准任务Prompt > Project Settings > 本协议 > 历史旧规则。**

---

本协议负责 Evidence authenticity / production；研究治理见 [Research Protocol](../../docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md)，视觉语法见 [Visual System](../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)，工程实现见 [AGENTS](../../AGENTS.md)。Project Settings 由用户在 UI 维护。

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

本项目采用三个明确分工的对话角色。

### 4.1 Evidence Master / Master Planning Conversation

**当前长期规划对话**是唯一的Evidence构建“大脑”，长期负责：

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

即使后续Experiment 1、Experiment 2或其他正式任务完成，**Evidence构建大脑仍由该Master Planning Conversation承担**，除非用户明确迁移职责。

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

用户只负责：

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

Retrieval Screenshot 可以长滚动，用于历史检索、恢复上下文与寻找 Decision Unit，不默认直接进入正式报告。

Formal Evidence Screenshot 使用正常可读浏览比例、高清原生截图、足够宽度；一张只需覆盖当前 Interaction Window，宁可多张，不压缩成一张，PNG preferred，raw 必须保留。用户只保存原生 raw；Evidence Master 负责 selection、crop、pagination、annotation、caption、LaTeX placement、audit、lock。

### 5.4 Resolution / Image Integrity

正式清晰度来自 raw 本身。记录 raw pixel size、final display size、effective PPI；裁切时同时记录 crop pixel size 与 crop bounds。有效 PPI = 实际显示区域的像素数 / 最终物理尺寸（英寸），横纵分别计算，取较小值；不能用整张 raw 的像素数除以局部 crop 的尺寸。

原则为 **>= 180 ppi，preferred >= 200 ppi**。不足时减小显示尺寸、拆页或重新截图；仍不足则 `RECAPTURE_REQUIRED`，不得 LOCK。

禁止 low-res screenshot upscale、AI super-resolution 替代原图、generative redraw of ChatGPT UI、反复重采样后放大、fake sharpening、为塞进一页缩小到不可读。

### 5.5 Raw / Crop / Annotated

正式资产保留三层：raw、crop、annotated（可由 LaTeX/TikZ 源文件与 PDF overlay 表示）。raw 不得覆盖。

推荐：**raw PNG → lossless crop / LaTeX trim → direct embed → vector annotation**。LaTeX trim 可保留 raw 文件并以可追溯的裁切参数表达 crop 层。

禁止：raw → downsample → raster annotation → enlarge。

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

尤其从Experiment 1正式开始以后，应尽量：

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

版式系统应适应真实Evidence，而不是强迫真实Evidence适应单页。

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

- highlight用户关键句；
- annotation；
- Human Reasoning → Evidence → Decision；
- 页面节奏；
-截图分段；
- caption。

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

### 24.3 Exact Phrase Highlight / Long Arrow / Side Note

优先 phrase-level highlight、short rounded outline、underline、local translucent fill、small numbered anchor，不默认把整条 message bubble 画成大框。用户原句保持视觉中心。

每根长箭头起终点对准具体 phrase，有文本支持，优先沿留白/边缘，避免遮挡和大量交叉，太密就拆页。禁止笼统“大框 → 短箭头 → 大框”，除非整个 bubble 确实就是 Evidence 对象。

Side Note 只回答用户做了什么、GPT 后面发生了什么、必要时这一步后来为何重要；不复述截图、不重写正文，一般约 40–80 个汉字，核心页可适当更长。

正式报告推荐 raw/crop PNG 直接嵌入，配 TikZ / PDF vector highlight、anchor、number、long arrow、side note、provenance label。不得把 annotation 栅格化进低清图片后再放大。颜色与页面密度以 Visual System 第 8 节为准。

### 24.4 Decision Authority

Evidence Master 决定 highlight、圈选、User anchor、GPT before/after、phrase 关系、turn 调序、Evidence 入选与用户文本编辑。Codex 只能根据批准的 Evidence Plan / annotation specification 精确实现，不自行推断或补造关系；缺少 specification 时停止受影响真实页面。模板 synthetic demo 不构成真实 Evidence 或批准关系。

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

从Experiment 1正式研究开始，优先实时保存Original Evidence。

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
是否像用户本人。

### C. GPT Fidelity
GPT回复是否符合真实角色和Decision。

### D. Decision Value
是否证明有价值Decision。

### E. Visual Usability
长度、重点、裁切和阅读体验。

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

### H. Phrase / Arrow Audit

Screenshot Audit 必须新增逐条结果：

- `PHRASE MATCH: PASS / REVISE`
- `ARROW RELATION: PASS / REVISE`
- `ARROW ENDPOINT: PASS / REVISE`
- `SOURCE RESOLUTION: PASS / RECAPTURE`

检查 User highlight 准确、GPT before 确为被回应原句、GPT after 确为采纳/修改后原句、箭头不是仅因时间相邻、端点准确、无正文遮挡、无歧义、PPI 足够。`RECAPTURE` 阻止总审核通过；前三项任一 REVISE 同样不得 LOCK。未设计箭头的 Contact Sheet 记录“无箭头，检查不适用”的依据，不虚构关系；仍需来源及可读性检查。

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
- Phrase/Arrow Audit Result
- Raw Screenshot Pixel Size
- Final Display Size
- Effective PPI
- Annotation Medium
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

本轮字段补充以 [WORKFLOW_EVIDENCE_PLAN](../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md) 的 schema 为准；未取得原图与 Evidence Master 批准前保持空记录，不制造 Evidence ID、phrase 或 LOCK。

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
5. **用户只负责保存原生截图，裁切、排版、annotation和LaTeX由Evidence Master负责。**
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
