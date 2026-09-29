# A：项目通用范围与来源核对

Task: SC-PROJECT-SOURCES-SYNC-003 · 2026-09-29  
Actual context: `/root/governance`，承担A范围核对与B文档导入；不是独立C。  
依据：本任务批准Prompt、逐字节保护的七份received输入、起始保护清单、仓库基线4483f520eabb5358d1f35cf5c33a81d3b01e47e0。

首个命令为`ls -la`，实际目录包含`.venv`、docs、evidence、releases、reports、task1、templates、tools以及用户根目录ZIP。随后读取`git status --short`，保留release中五规范/报告输入和用户未提交ZIP；本子任务没有执行旧sync写模式、清理、stash、reset或commit。

五份received Markdown与完整批准Prompt均已通读。读到的输入版本为Research v1.1、Writing v1.0、Visual v2.4、Evidence v2.5、AGENTS 2026-09-29 Report production / accepted-source integration。用户明确授权直接完成一次性迁移，P1—P4不是待批准方案；本次不另写长期design/implementation plan。

| 范围 | 主负责规则与本次明确的边界 |
|---|---|
| P1 双报告 | Writing §1：项目正式实验、课程设计、当轮正式报告任务使用独立双报告；老师最新格式优先，日常问答不自动生成两报告。 |
| P2 实质Multi-Agent与持续闭环 | Research §C：真实研究、执行、独立核验、反馈、优化、修复和恢复，按任务规模落实并留证据；角色、工具、合同随任务。AGENTS §3负责工程闭环。普通函数改名不构成Agent；最终记录级程序可为确定性。 |
| P3 共同基础与新增演化 | Writing §12：必要介绍或引用既有真实工作流，重点写当前新增/修正/否定及当前Experiment Decision Process；Evidence §4.1明确用户任命Evidence Master，继承不扩大来源、范围或Lock。 |
| P4 draw.io | Visual §13：正式工作流/体系架构图的主要可编辑交付为真实.drawio及SVG/PDF；位图嵌入不满足可编辑。统计、GIS、数学几何图保留适合的原生工具；没有新增绘图任务。 |
| 条件性通用规则 | Research §G：新任务仍需自己的坐标来源核验和授权，实验一条件化分析不证明新数据CRS、不概括授权未来未知datum处理。 |
| 实验一实例 | S-D-P、R0/S0/G0、30秒/400工作米/35度/5工作米、600条确认、三个Goal、候选数/轮次/四模式/记忆、25页/七章/10图/17表与具体轨迹结论仍仅属实验一。它们没有被加进通用模板或设为未来输入。 |

共同规则与特定实验机制分别处理：公平比较、参数依据、候选组合先有单项/父项依据、实测选择和有限迭代继续有效；四模式、记忆、特定消融和调用预算是否采用，由老师材料和当轮批准方案确定。不要求复杂组合获胜，也不改批准空间内的自主裁决或共同评价标准。

本次批准集合是旧远程13项保留、加Writing及已验收Experiment PDF/ZIP后的16项迁移基准；未来数量由唯一`sources.json`计算。角色核对如下，具体规范名/路径/hash以[结构化清单](../../chatgpt-project-source-sync/sources.json)为准，本文件不建立第二份分发清单。

| 来源组 | 数量（本次） | 角色与保护 |
|---|---:|---|
| 五份Markdown | 5 | 项目规范；收到的全文作为底稿，最小scope修订后成为唯一active入口。 |
| 已验收Experiment PDF/源ZIP | 2 | 实验一真实成品/配对源；原字节不可变，可编辑工作源另行接管生成器，不作模板或未来数据。 |
| 前期Process PDF/源ZIP | 2 | 局部历史参考；已有SOURCE_ARCHIVE_BUILD=PARTIAL继续保留，不宣称完整Process或新增Lock。 |
| Experiment/Process模板preview | 2 | 合成视觉参考；不被真实报告替换，不因Markdown改动重编译。 |
| 老师PPT、作业ZIP、两个Notebook | 4 | teacher-provided/starter；沿用原路径及字节，不执行、不另存Notebook。 |
| publication-plots ZIP | 1 | 保留批准原archive，固定hash和installed effective members独立核验；不重打包。 |

已实际读取基线脚本：`git show HEAD:evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py`。它确有`len(SOURCES)==13`、`EXACTLY 13`及对extra的`unlink()`；不是只有11项。基线上传说明首条实际要求“Delete all current ChatGPT Project Source files.”。received AGENTS/Visual虽已提出动态清单原则，仍用旧11项描述历史风险；当前正常规则已统一为清单计算、预验证、未知extra拒绝并保留、只读check、幂等更新和UI差异替换。原基线提交和received历史字节均保留，不改历史记录。

本子任务只改五规范、根/设计系统/模板README和任务内部文档证据。报告/脚本集成与真实独立C由其他实际上下文完成；不以本文替代其运行和审核。新增记录级实验模型调用为0；未运行清洗、调参、消融、四模式或最终确认。没有修改raw、数值结果、记忆、Process截图/箭头/Lock、P2源或模板正文/preview。
