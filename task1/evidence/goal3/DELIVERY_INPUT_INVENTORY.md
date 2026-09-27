# Goal 3 交付输入盘点

角色：B 交付工程准备；状态：**INPUTS_CHECKED，不是最终交付验收**。机器对应表、原件哈希、15 页教师原件 XML 回读和 16 条 G1 要求映射保存在 [teacher_mapping.json](teacher_mapping.json)。本文件仅记录本轮实际读取与缺项，不把历史结果改名为 G3 实验。

## 1. 冷启动与读取边界

首条执行命令为仓库根目录的 `ls -la`。实际存在 `.venv/`、`AGENTS.md`、`docs/`、`task1/`、`templates/`、`tools/` 及根目录三份历史 Handoff ZIP。随后 `git status --short` 显示只有 `SC-LAB1-G1-CLOSURE-002_HANDOFF.zip`、`SC-LAB1-G1-COMPLETE-001_HANDOFF.zip` 两份原有 ZIP 未跟踪；REPAIR ZIP 已跟踪。本角色仅只读检查 ZIP 成员名，未修改任何历史 ZIP、教师原件或 starter。

搜索限本仓库及当前直接任务输入，没有扫描个人无关历史、账号、认证目录或完整环境。使用 `rg --files` 查找报告、截图、逐字稿、元数据和 Lock，使用 `rg` 查找姓名/学号字段；匹配结果均为提交规则或提示词要求，未发现可信学生身份值。不从 Git author、昵称或教师邮箱推断姓名/学号。

实际读取了 active AGENTS、Visual System v2.2、Interaction Evidence Protocol v2.3、当前 G3 用户原文、G1 有效授权补充、G1 当前审阅入口、G2 审阅/复算/真实过程材料与两份 starter。G1 根目录 `FINAL_RESPONSE.md` 是早期历史受阻版本；当前 G1 事实应跟随 `REVIEW_PACKET.md` 指向的 `SC-LAB1-G1-COMPLETE-001`，不能把旧 D1/D2 阻碍重新施加到 G3。

## 2. 教师原件核回

原件：[实验课1.pptx](../../实验课1.pptx)，SHA256 `cf5fdbdd0e116818f4bf195e8761dd55c4733443d7c360c986cf1cdfddfda075`。本次按 G1 已核实摘录定位，再用标准库 `zipfile` 和 `ElementTree` 实际读取原件第 1、5、6、17–26、37、42 页对应 XML 的文本 run。没有重复全面渲染 PPT；图形数学解释沿用 G1 已核验材料，文本回读不声称重新审核全部图形。

| 教师要求 | 本次原件定位 | 对最终成果的约束 |
|---|---|---|
| 实验一的清洗与压缩程序、数据处理评估报告、实验过程报告（含 AI 批判） | 第 5 页 | 两份报告是实际必需成果；README 不替代报告。 |
| AI 准确性与隐含假设批判；至少一组反例、修改前后指标、拒绝建议及理由 | 第 6 页 | 使用真实建议与反例，不能把构造机制检查包装成模型说过的话。 |
| 时间/距离分段及过短、过少片段过滤 | 第 17–18 页 | 作业需展示参考过滤实现与参数实验；最终放宽过滤不取消教学任务。 |
| 点方向取当前至后继，方向同时异于前后邻点时删除 | 第 19–20 页 | D2 的一次标记同时删除调度来自已批准用户补充，不能说成教师完整明确调度。 |
| DP 以起终点有限线段计算距离，严格大于阈值递归 | 第 21–23 页 | 有限线段、端点与原索引保护；不沿用 starter 的直线投影漏洞。 |
| 自行设计评估指标、解释设计逻辑及结果 | 第 24–26 页 | 第 24 页 95 m 是带特定骑行示例假设的教学例子，不自动覆盖 starter 的 400 工作米参考。 |
| LLM 辅助系统、思考与讨论为选做 | 第 26 页 | 当前用户已明确把 T2 纳入全部必做范围；不能在 G3 删掉四模式/换序等负结果。 |
| 四模式结构不同、search-only 零 LLM、demo/holdout 不重叠、评测只读记忆 | 第 37 页 | 复用 G2 真实调用与结果，并保留模式/成本/泄漏边界。 |
| 分段、去噪、简化能否换序 | 第 42 页 | 复用六排列真实结果和拒绝机制，不能仅保留最优顺序截图。 |

第 26 页明确：**10 月 5 日前**将 `.ipynb` 与实验报告压缩为 `.zip`，发送至 `52285903012@stu.ecnu.edu.cn`，命名 `学号_姓名_实验一`（页面列 `.zip/.ipynb/.docx/.pdf`）。封面日期为 `20260917`；提交页没有具体截止时刻，不编造 23:59。本轮不发送邮件或提交平台。

PPT 的 `Trajectory_preprocessing.ipynb` 在仓库中没有同名源文件；实际中文 [作业1轨迹数据预处理.ipynb](../../作业/作业/作业1轨迹数据预处理.ipynb) 的三项 TODO 与主函数对应这一要求。这是路径映射，不创建伪称教师提供的英文原件。

两份 starter 的当前字节哈希与 G1 摘录一致：

- 基础 Notebook：`8601d1dfecaef062fef553992cc9774d3a0eb551751c70536f5b52f1343b158a`，19 个 cell。零起始 Cell 4/6/8 是分段/去噪/简化 TODO；Cell 10 为主函数；Cell 12/14/16 对应三组参数实验，13/15/17 为待填代码。
- [任务3_LLM辅助评估清洗.ipynb](../../作业/作业/任务3_LLM辅助评估清洗.ipynb)：`4ecffe64024e002c0cffe7830e18b5f6ded04cd5aa9dd645d6798fc9b0715add`，33 个 cell。Cell 0/2/6–13 对应实际工具闭环，19–21 四模式，22–25 记忆，30–31 真实 Provider 入口。

starter 的 Mock、保存输出、regret/自身 clean 描述和“63% 静止”等断言均是历史材料，不能不经对应实验核对就写为当前事实。原件保持不变；完成版应复用已修复模块，并在教学入口展示可读答案。

## 3. 当前可复用的技术成果

- [G1 当前审阅入口](../goal1/REVIEW_PACKET.md) 已指向最终条件化 pilot 结果及真实 A/B/C；[授权补充](../goal1/revisions/SC-LAB1-G1-COMPLETE-001/AUTHORIZATION_SUPPLEMENT.md) 明确 D2 和未知 datum 下的条件化工作坐标。不能要求重复批准。
- [G2 当前审阅入口](../goal2/REVIEW_PACKET.md) 定位三组参数、六顺序、四模式、只读记忆、单项确认、反例、11 图和三份工作 Notebook；[复算说明](../../docs/goal2/REPRODUCE.md) 区分 RECOMPUTE 与 LIVE。历史 84 次有效实验模型调用不能改名成 G3 新调用。
- [真实 AI 批判](../goal2/a_epoch02/actual_ai_critique/ACTUAL_AI_CRITIQUE.md) 含已核验原文、拒绝/权衡和 [formal-02 反例](../goal2/counterexamples/formal-02/manifest.json)。可支撑技术报告；没有 Human Judgment 的记录不能伪写为用户逐次判断。
- [文献合并稿](../../docs/research/Task1_Literature_Review_2025_2026_Merged.md) 与 [Source Audit](../../docs/research/Task1_Source_Audit_2025_2026_Merged.json) 已定位并读取前言、分类和少量相关卡片；这是历史资料阅读记录，不等于本角色重新核读全部 22 篇论文。本角色未做新广泛检索。最终拟引用的少量来源应由报告作者再按具体命题核读，记录读取范围。

## 4. 身份与互动证据的真实缺口

**META_DEPENDENCY**：限定范围中没有可信正式姓名和学号。课程名、实验一身份、教师作业规范和封面日期可核实。送审稿可以用清楚的待补标记；实际 ZIP 在缺项时只能命名为 `REVIEW_ONLY`，不能声称可直接提交。

**PROCESS_EVIDENCE_DEPENDENCY**：当前 [Workflow Evidence Plan](../../../evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md) 明确写着 `SCHEMA READY / NO EVIDENCE REGISTERED`，并说明“当前没有交付真实 raw 截图与批准 annotation spec”。本次没有发现正式任务 Process Report、真实聊天 raw 截图、已批准 crop/annotation/caption 规格或 Evidence Lock。仓库中看似聊天样式的 PNG/PDF 属于模板合成素材或模板编译检查，不能采用。

存在可追溯文本事实，但范围有限：

- G1 `AUTHORIZATION_SUPPLEMENT.md` 与 `USER_DECISIONS.json` 保存直接授权文本和两条答复；可以准确引用其来源与限定含义。
- G2 `USER_PROMPT.md`、`prompt_source.json` 保存该轮用户原文及来源回执。
- 当前 G3 用户原文是当前授权；不能倒写成过去具体候选由用户逐条选定。
- G1/G2 的真实角色、工具、实验及修复记录是工程过程事实；不等于用户原话或 Human Judgment。

主线程应一次性登记姓名/学号与真实原文/截图及 Evidence Master 规格、Lock 两类输入依赖，继续全部不受影响工作。没有 spec 时不自行选句、高亮、画因果箭头或赋予 Tier/Lock。可先完成可编译的 Process Report 送审稿、两层真实事实结构和 Interaction Handoff 候选索引；该文档不能冒称正式完稿。

## 5. 模板、配色、技能与编译路线

已实际读取 installed [publication-plots Skill](../../../tools/skills/publication-plots/SKILL.md)、`references/tool-routing.md`、`references/visual-design.md`，以及已安装的 `latex-writing/SKILL.md`。P2 项目颜色优先于 plotting skill 的通用色板。技术图使用原生 Matplotlib/TikZ/draw.io 等和真实数据，保存 SVG/PDF/源代码，不生成地图或架构位图。

两份模板已读取源码、README、公共 [P2 定义](../../../templates/latex/common/p2_cloud_sorbet_colors.tex) 与 reference PDF：

| 模板 | 实际参考 PDF | 可复用工程接口 |
|---|---|---|
| [Experiment Report](../../../templates/latex/experiment-report/experiment_report_template.tex) | [5 页预览](../../../templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf) | `finding`、`noteBox`、`metric`；11 pt A4，DejaVu / Noto CJK / Fandol 等字体，统一标题、caption、页眉页脚。 |
| [Process Report](../../../templates/latex/process-report/process_report_template.tex) | [12 页预览](../../../templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf) | `contextbox`、`decisionbox`、`semantic`；复制 `components/interaction_evidence.tex` 保留工程接口，未取得 spec 前不调用真实批注。 |

本次对两个原 PDF 全部执行 `pdftoppm -r 200 -png`，退出码均 0，得到 5+12 页、每页 1654×2339 像素；已查看全部页 contact sheet，并单页细看 Experiment 第 3 页与 Process 第 5 页。模板版式、P2、中文和合成标签清楚。这个动作是参考模板阅读，**不是最终报告的全页视觉验收**。临时渲染不作为 G3 正式成果纳入仓库。

具体报告应复制到任务目录再改正文，保留模板参考原件。建议 `task1/reports/experiment1/`、`task1/reports/process1/` 使用相对路径 `../../../templates/latex/common/p2_cloud_sorbet_colors.tex`；Process 复制组件目录。两个模板当前没有 bibliography backend 设定，也没有 `minted`，新增真实 `.bib` 时明确采用一个后端即可，不需要 `-shell-escape`。

从各报告目录执行：

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build experiment_report.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build process_report.tex
```

报告正文必须完全替换模板演示文案与 `demo-assets/`；最终需要 `pdfinfo`、`pdftotext`、日志缺字/引用/溢出检查，所有报告页至少 200 dpi 渲染并逐页目视。中途预留的 G3 数值接口应明确未运行，后续由已核验结果生成，不手编数字。

## 6. 环境验证与新增项

实际执行 `latex-writing/scripts/check_latex_env.sh`，退出码 0，结果 **56 PASS / 2 WARN / 0 FAIL**。当前优先的是 Linux 用户 TeX Live 2026；XeLaTeX、latexmk 4.88、BibTeX、Biber 2.21、Poppler 工具、Noto Serif/Sans/Mono CJK、Fandol 和模板所需 TeX 包可用。

两个 WARN 为 PATH 重复和 WSL PATH 中含 Windows TeX 路径；Linux TeX 当前优先，不阻碍本任务，也未修改 PATH。`.venv` 复用现有环境，PIL 可完成渲染查看。**新增系统包、Python/npm 包、工具链、字体、持久配置修改均为 0**。本角色未运行 G3 候选、最终确认或生产；本文件不宣称这些环节已完成。

## 7. 后续可立即做与受影响闭合

可立即做：两份报告的真实 G1/G2 方法、评价、规定实验、四模式、技术批判和 G3 数值接口；完成版 Notebook 对应映射；真实技术/互动 Handoff；后续实际结果接入、全页渲染和 REVIEW_ONLY ZIP 工程。

仅受外部输入影响：真实互动 Evidence 页及完整 Process Report 闭合；可信身份与规范可提交文件名。在这些输入缺失时，最终整体状态保持 `PARTIAL_BLOCKED`，技术内容可以独立验收，教师包保持 `REVIEW_ONLY/NOT_READY`。不填网页 GPT 二重审核、Evidence Lock 或用户 Understanding 的 PASS。
