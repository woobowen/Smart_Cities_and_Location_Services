# B：全文导入与最小修订

Date: 2026-09-29 · Author validation only; independent C remains separately recorded.

先核对五份received原字节hash，再将完整内容导入批准路径，未用旧仓库文风删减新底稿。下列版本变化只对应本次范围澄清和分发接口修订；输入→active的逐行diff位于[input-to-active/](input-to-active/)，机器结果见[document-validation.json](document-validation.json)。这些文件记录迁移事实，分发权威仍是唯一sources.json。

| 文档/版本 | 修改位置与理由 | 其余重要内容 |
|---|---|---|
| Research v1.1 → v1.2 | A明确项目范围与实例身份；C明确实质多角色、闭环和可变实现；G阻止条件化授权跨新数据自动继承。 | 保留原自主裁决、评价不降标、公平比较及组合不强求获胜的原段落。 |
| Writing v1.0 → v1.1 | §1明确项目双报告及日常问答例外；§3区分通用工作流与按任务采用的机制；§12明确继承共同基础与新增演化。 | W01—W22逐行保持；原研究真实性、第一人称、已验收成品/源码接管及未来任务不照搬实例等条款保持。 |
| Visual v2.4 → v2.5 | §1引用双报告适用范围；§13补draw.io主要可编辑交付及工具边界；§16.4改为唯一结构化清单计算成员。 | P2精确色值、XeLaTeX、已验收图型/页面、三维条件、Micro Trace、图表真实性与任务自适应均保留。 |
| Evidence v2.5 → v2.6 | 总范围与§4角色入口、§6及§28的每项正式研究实时证据规则；三类Evidence职责不固化研究Agent数量。 | 原话、术语归属、第一人称、最小框选、箭头、PPI、所有Lock和已验收Process保护条款均保留。 |
| AGENTS revision更新 | §2用短P1—P4路由表明确通用范围；§18绑定sources.json、安全同步、未知项保护、差异UI动作与独立状态。 | 全文采用received新版；已验收文稿、生成器接管、实际独立审核、同任务内修复恢复未减弱。 |

根README增加五规范、已验收25页Experiment配对源、Process局部参考及PARTIAL限度、当前报告和本次审阅入口；把原末段坐标未知表述限定为实验一。设计系统README更新活动版本、真实参考和动态分发路由，保留旧distribution的历史身份。两个模板README只补范围、写作指南、真实参考和图源交付说明；Process README把“Reproducible source archive”改为准确的“Supplied source archive with PARTIAL reproduction limit”，避免与下文限制矛盾。模板.tex、demo资产和两个preview完全未修改。

修订日期来自实际执行的`date -Iseconds`：2026-09-29T15:27:10+08:00。所有原文Markdown两空格硬换行均保留；它们是输入格式，不为消除`git diff --check`的trailing-whitespace提示而重排文风。没有安装系统包、Python包、工具链或改全局配置。

验证命令：

```bash
.venv/bin/python evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/governance/validate_governance.py
```

脚本真实比较received预期hash、版本、完整原章节拓扑和未授权变化章节，逐行比较W01—W22，核对P2表和公共TeX色值，并对模板/P2/前期Process文件核对起始保护hash。另解析九份Markdown的仓库相对链接与章节anchor。语义审查见[SCOPE_REVIEW.md](SCOPE_REVIEW.md)；精确变更diff可供独立C核读。这些自动检查不是Evidence Lock或网页GPT二审结论。

UI只提供[最小范围补丁](../handoff/PROJECT_SETTINGS_SCOPE_PATCH.md)，标为TRANSFER_COPY / USER_UI_ACTION_REQUIRED；本子任务未操作UI。五份Markdown需要替换为本轮输出，已上传且未变的PDF/ZIP不重复建议上传；完整成员差异由[UI_SOURCE_DIFF.md](../handoff/UI_SOURCE_DIFF.md)记录。
