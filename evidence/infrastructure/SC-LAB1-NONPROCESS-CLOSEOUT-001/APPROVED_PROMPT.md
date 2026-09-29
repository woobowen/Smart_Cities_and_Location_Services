# 《智慧城市与位置服务》实验一：非Process范围收尾与项目文档同步

Task ID：SC-LAB1-NONPROCESS-CLOSEOUT-001
Repository：https://github.com/woobowen/Smart_Cities_and_Location_Services.git
Branch：main
Workspace：~/lab/Smart_Cities_and_Location_Services
用户已放置的输入：releases/chatgpt-project-sources/ 中本轮交付的五份Markdown
本Prompt编写时核实的远程：89371f6597f92f7dac9abf61f6f6b18e29ed76cc
该次工程ARTIFACT：87fc7db1ced9fd394d0cdda2113c5608205dce03
历史数值CODE_SHA：e12f8a27944210adb452730be92a0674dfc6b84b

## 0. 本次授权与完成条件

用户已明确：Process Report将在用户指定的另一个对话继续；当前对话和你只负责其他任务的收尾。现在实际完成五份项目文档从release向active源及分发清单同步、上次真实网页GPT验收归档、当前非Process技术状态与交接更新、必要回归及GitHub发布。

这是原实验一工程的范围明确收尾，不是新建Goal 4，不重新设计算法，也不替Evidence Master收尾。

直接执行：保护输入 → 核验五份文件 → 导入active源 → 更新唯一清单与分发 → 归档真实二审 → 更新当前技术导航和交接 → 内部自检及真实独立C → 修复/复验并恢复父任务 → commit/push → 实际远程核对 → 返回结果。

普通工程问题在本任务内持续处理，不只给计划、不返回NEXT_CODEX_PROMPT、不因子代理提出意见就停止。没有新错误或受影响变更，不重做已经验收的研究和成品。

本次范围全部实际完成，可记“非Process收尾工程完成/待网页GPT核查”。Process不在本次制作范围，因此它尚未完成不是本任务永远PARTIAL_BLOCKED的理由；但它仍是整体必需交付，完整实验一与教师提交不能因此改为全部PASS/READY/SUBMITTED。

真正外部阻碍只影响对应分支；完成其他可执行项后再明确报告。用户不需要重新批准已确认的分工、身份、S/D/P、坐标假设或规则范围。

## 1. 必须保护的边界

本轮不做：

- Process正文、截图、标注、caption、Evidence Plan、Micro Trace、历史恢复或Evidence Lock的制作与修改；不修前期31页Process源包与PDF的既有PARTIAL对应问题。
- 重写或重新排版用户已验收的25页Experiment Report，改变其章节、图表、正文与参考源ZIP。
- 新候选、调参、模型调用实验、顺序消融、记忆扩充、最终确认再选择或全量清洗；本轮新增实验模型调用及研究数值运行默认均为0。
- 修改原始数据、冻结配置、指标定义、历史run/失败记录、teacher/starter、公共配色或Skill原件。
- 自动邮件/平台提交、修改ChatGPT UI、代用户理解验收、清理用户ZIP或项目依赖。

五份长期Markdown是本轮明确授权的治理输入：按原字节导入/核对它们，不等于获准改变Process成品或Evidence记录。Evidence Protocol本轮文件与已验收远程v2.6一致，原则上无需改写。

现有placeins、needspace为后续报告重建所需隔离依赖，应保留；本轮不因“一次性任务”清理它们，不安装无关包，不改全局TLS/字体/认证/配置。

## 2. 起步检查：保护release，再恢复权威源单向分发

实际核对pwd、git status --short、分支、HEAD、origin/main和实际remote。上述SHA是被审基点，不是reset目标；若远程或本地前进，先读合法变更，保留用户及另一个对话的新工作。

用户只在release替换文件，active可能尚未更新。不要一启动就执行写同步将旧active覆盖新release；先读取当前同步器及清单，记录完整release成员/类型/大小/SHA256，保存五份输入不可变快照，再导入active。

本轮同步器已在原路径完成动态清单、安全拒绝、只读检查和回滚：
`evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py`
唯一清单：`evidence/infrastructure/chatgpt-project-source-sync/sources.json`

复用它们，不重建另一套同步系统。本轮是一次受控的release→active导入；之后恢复active→批准清单→release。旧目录名包含SYNC-001不表示应该恢复旧11/13项逻辑。

保存起始保护清单，至少覆盖：五份旧active及清单、原始数据与数值源/结果、当前报告及源、两份Experiment批准原件、所有Process/Evidence材料、当前提交包、用户原有未跟踪文件。记录工作树已有变更，不stash/reset/clean它们。

只从当前仓库、用户明确提供的本次交接目录/附件查找输入，不扫描无关私人目录。OS下载元数据如Zone.Identifier先保留原字节和来源；确认仅为下载元数据后，可移到任务内隔离目录并登记，不能递归清理或删除有效文件。

## 3. 五份完整输入及确切导入映射

下面是本轮交付文件的实际大小与SHA256。不要只凭文件名、mtime、版本行判断一致。

| release规范名 | 大小/B | 本轮输入SHA256 | 仓库active路径 |
|---|---:|---|---|
| SMART_CITIES_RESEARCH_PROTOCOL.md | 13264 | 19f9bb4670bc3a485b064854f3d035d2a50a192386be53396851443ee5654a3f | docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md |
| SMART_CITIES_REPORT_WRITING_GUIDE.md | 25025 | 49cb8ac101420a3262734b9ac246451fbb61b9716e8263db2dd8802bd78f5d55 | docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md |
| SMART_CITIES_VISUAL_SYSTEM.md | 43680 | 9fbbd62543da77c7cecc31f4e07a95c2570c245693a9817d17652286340d291f | docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md |
| WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md | 44829 | c3113ff2f8b6a02c95e6e1cfc9db749773fd080d212b8331eb8177557d2f8912 | docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md |
| AGENTS.md | 38260 | 24f2f2b1abe7fafce0d76e7de2baeec630aba8105b19228ef288f66284540534 | AGENTS.md |

Research v1.2、Writing v1.1、Visual v2.5、Evidence v2.6，与被审89371f6相同，不人为升版本。AGENTS本轮Revision为：
`2026-09-29 · Project-wide P1–P4 / scoped closeout and review handoff`

AGENTS在原全文上只增加“分项收尾、指定责任与验收承接”等工程细则；已确认P1—P4、完整章节、P2、第一人称和证据要求均继续保留。

差异不明时先保护两份文件并诊断；可证明的用户后续合法修订按实际范围合并并记录，不为满足上表强行覆盖新工作。改变方法或Evidence权限等未获授权差异只暂停对应文档分支。不要擅自润色其余四份规范、追加一轮新规则或修改五份之外的项目源成员。

本轮完整成员集合沿用现有批准16项：五规范、两份P2模板、前期Process PDF/ZIP、已验收Experiment PDF/ZIP、教师PPT/作业ZIP/两份starter、publication-plots.zip。不是五项上传集合，也不是永久EXACTLY16。

## 4. 文档与分发执行

先真实读取五份输入与实际AGENTS涉及条款。按§3原字节复制差异项到active，已相同文件不重写。不要使用(2)/(3)等非规范文件替代当前文件。

只更新sources.json中实际变化的条目：正常应仅AGENTS的Revision/hash及其本轮变更来源；保留其他15项各自批准范围、语义角色与hash。清单顶层可登记本次集合核验，不能伪称其余文件都是本次新创作或新批准。若出现起点以来其他合法变动按实际处理，不恢复旧文件。

随后执行现有--plan、正向sync、--check及第二次无变化sync。核对：set(actual)==set(approved)，全部普通文件，active与bundle字节相等，第二次updated为空、removed为空，--check不改载荷/元数据mtime。

SOURCE_MANIFEST.md、UPLOAD_INSTRUCTIONS.md仍由唯一清单/现有生成器产生，不手工维持第二套。当前上传说明若仍把SYNC-003差异表当成“本次”，最小调整使其指向当前交接，历史说明保留适用范围；不得取消只读、幂等和异常安全要求。

已确认P1—P4是项目级规则；实验一参数/方法/样本/Goal数/页数不成为永久标准。本轮不再调整这些研究边界。

未知extra先保留且拒绝最终bundle闭合，不能删除有效文件。批准输入不完整则不向真实bundle做部分覆盖。不要将本Prompt、Settings、审核ZIP、manifest或received目录放进release。

## 5. 归档上一轮真实网页GPT二审，不重造验收

被审提交为89371f6597f92f7dac9abf61f6f6b18e29ed76cc。此前网页GPT的实际结论为：SYNC-003在明确范围内通过；Experiment源/构建集成通过；没有发现需要重开实验一研究的新阻断问题；Process与完整提交仍未闭合。

优先读取本Prompt旁`supporting_evidence/`中的原始交付：

- GPT_SYNC003_SECOND_REVIEW.md：9468 B；SHA256 fa244757f288814f0de458b42660c68f4f6dca9e88b2d1d3fd6572f91de74c3a。
- SC_SYNC003_GPT_二重验收记录.zip：41321 B；SHA256 2e48f55bdd35b5e5e72a1bc04f891ff598d1c91f275a420a34850cca2d60f64b。
  也可读取用户明确提供的同名同hash附件。不要仅为这个名字搜遍用户磁盘。

核对后把原文件无修改保存到SYNC-003的`external_review/`子目录，登记来源为本次用户/网页GPT交接、原被审SHA和真实接收时间，不能把接收日期写成未知的历史审核时刻。审核ZIP只作证据，不默认执行内含的历史测试脚本；安全检查后按需引用其probe结果。

报告中真实范围要保留：历史18项独立同步器测试、16项依赖恢复核对、报告真实源码编译及同环境25页像素一致；没有重新取回执行全部387文件、没有重新解压执行正式ZIP、没有新增全量轨迹实验。它曾由原件/远程diff恢复字节后核验，不是用户本地完整clone。不要把这些检查改写成本轮Codex新运行。

仅复制本Prompt而未提供上述附件时，以上内容可归档为`USER_RELAYED_PRIOR_REVIEW`，注明原报告全文未导入；本Prompt的数值是已知历史审查摘要，不是新测试日志。旧结论可在其被审版本内引用，但不伪造同名原报告、旧执行日志或签字，不为此停止其他收尾。找到实际附件后再替换来源状态，保留历史接收记录。

在SYNC-003的REVIEW_PACKET.md追加“后续网页GPT验收”及链接，明确其原被审版本。不要全局替换PENDING为PASS，不改原FINAL_RESPONSE、C意见、测试回执或PUBLICATION_RECORD；旧记录继续表示当时状态。

本轮修改后的新提交仍需要网页GPT检查。`SYNC003_EXTERNAL_REVIEW=PASS_WITHIN_REVIEWED_SCOPE`与`CURRENT_CHANGE_GPT_REVIEW=PENDING`可以同时成立，不能混写成一个无范围状态。

## 6. 收尾技术状态与交接，不制作Process

只更新当前入口和技术交接，复用已有结构：

1. task1/README.md。
2. task1/evidence/goal3/REVIEW_PACKET.md的“当前状态”部分；历史正文保持原样。
3. task1/docs/goal3/TECHNICAL_HANDOFF.md的当前技术基点与交接说明。
4. 必要时根README的当前入口和报告工程README中直接受影响的导航；无变更需要不动。

明确记录：

- 技术处理、规定实验、候选比较、最终确认及全量结果保持此前范围验收，不重新评为全局最优。
- 25页Experiment的用户验收已发生，89371f6接管/构建二审已通过对应范围；原PDF/源包和生成器受保护。
- 当前非Process任务完成后可单独关闭；Process交由用户指定的另一对话，仍属于整体必需交付。
- 完整教师包仍是REVIEW_ONLY/NOT_READY，等最终Process到位再做对应合并、包核验与用户提交确认。本轮不制造删掉Process的“正式完整包”。
- 原始CRS未知、无噪声真值等技术限制保持，Process完成不会使这些限制消失。
- 用户已确认本对话的复盘及25页文稿，按真实范围登记；不要反过来写成用户从未审过这些成果，也不要据此代其新增Understanding/VIVA通过。

提供清楚的技术交接入口：冻结方法/数据/数值CODE_SHA、当前PDF与编辑源、构建/复算命令、已有验收与未覆盖范围、可供另一个对话引用的现有Interaction Handoff路径。

不修改Interaction Handoff的原话或条目，不代选截图，不新建Evidence Plan，不修其旧引用/BOX RANGE字段，不修改31页Process旧源包，不试图补齐缺失历史。前期Process源复现PARTIAL是已知的被移交事项，不改为PASS，也不把其当成本任务工程未闭合。

任务实际状态写在任务目录/本轮记录，不写回长期五规范里的实验一状态、姓名、SHA或截止时间。无需建立另一套巨型状态平台，现有入口与一个范围明确的本轮收尾记录足够。

## 7. 已验收成果和运行环境保护

至少核对以下不可变批准原件：

- reports/experiment-report/experiment1-reconstructed/Experiment_Report_吴博闻_10245102410.pdf：2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0。
- 对应Experiment_Report_完整重构_源文件.zip：6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd。
- 当前task1/reports/experiment1/experiment1.pdf应与批准PDF对应。
- 原始teacher/starter、task1/workflow、冻结配置/结果/记忆、两份完成版Notebook、Process工作目录/前期参考、现有Review ZIP与用户文件。

本轮不重新生成报告或包。只因Markdown和状态变更，不重画图、不重编25页、不重跑FULL或调用模型来凑验证次数。可核对源码/输入/输出hash及已有构建记录，写明继承范围。

如果真发现报告入口/同步最小修复导致实际代码或运行依赖改变，暂停受影响操作，保存反例并做对应回归；数学实现、指标或文章内容需要改变时仅提出证据，不借收尾授权改动。未受影响的历史数值CODE_SHA保留真实身份。

本轮不清理.venv、texmf或用户临时CLI，不安装无关依赖，不读取无关凭据。生成器正常需要的placeins/needspace保持现状。仅可清理由本轮明确创建且不再需要的私有测试目录，并记录路径和范围。

## 8. 实际工作流：作者检查、独立C与修复闭环

复用现有协作方式，不重新搭建Provider或Multi-Agent平台。
A/主线程：核对授权范围、原件、待收尾入口和历史证据；不重复研究方案。
B/执行：完成原字节导入、清单/导航更新、审核归档和专项验证。
C：真实独立上下文只读核查输入与输出、范围和证据，做适当独立探针，不只复述B总结。实际作者不能给自己标为独立C；主线程自检单独记录。

普通问题：保存→复现→修复→专项/回归→C复核→恢复父任务。没有问题就如实记无新Issue，不制造错误来展示闭环。

跨对话授权和Process原件不齐不是向用户追加任务的借口；它们本轮只登记交接。只有当前同步所需文件缺失、权限或真实冲突无法解决才局部升级。

## 9. 验证要求：充分且不重复无关实验

对实际更改的同步和治理部分运行必要测试，至少覆盖：

- 五份received hash、正确active映射、当前16项集合与所有成员字节、其他成员未改。
- 同步--plan/write/--check的成功路径，第二次幂等及check前后内容/mtime不变。
- 临时测试目录中模拟缺源、错hash、未知extra，确保拒绝且不覆盖已存在目标；不要向真实release植入测试垃圾。
- 规范链接/主要章节/版本，P1—P4与分项收尾不冲突；Evidence规则与内容未擅改。
- 原审核文件/包原字节、被审提交、历史执行范围及新提交待二审的区分。
- 修改过的当前README/REVIEW_PACKET/技术交接链接有效，没有旧“二审未发生”覆盖已归档范围，也没有整体完成的虚假声明。
- 报告PDF/源、数值、Process、用户文件及有效Review ZIP保护成立。

可使用现有同步专项测试/测试框架；报告未变不强制重跑旧17项报告测试或全部469项工程测试。报告每项实际命令、cwd、退出码、作用范围，不能把未运行说成PASS。

若测试涉及新脚本/清单回滚等异常，测试在唯一临时目录中进行，失败数据保存到本轮证据；测试本身不能覆盖原件。同步器已经具备的安全能力不应在此任务中被降级。

## 10. 本轮交付与验收矩阵

建议唯一目录：evidence/infrastructure/SC-LAB1-NONPROCESS-CLOSEOUT-001/。
仅创建有实际内容的文件：APPROVED_PROMPT、received清单/快照、实际修改清单、范围收尾状态、测试/C意见、当前REVIEW_PACKET、最终交付和发布记录。SYNC-003旧二审归档仍放其external_review中并相互链接。

| ID | 通过条件 |
|---|---|
| NC01 | 工作区与release输入已保护，五份文件来源/hash明确 |
| NC02 | active文件与批准完整底稿一致；旧四份不无故重写，AGENTS新条款完整 |
| NC03 | 唯一清单/生成manifest/上传说明与release一致，集合正确且幂等 |
| NC04 | 上次网页GPT二审按实际原件或明确转交身份归档，无伪造/历史倒写 |
| NC05 | 当前非Process范围、完成项、Process交接与整体提交状态清楚 |
| NC06 | 已验收报告、冻结研究、Process、教师材料和用户文件保持 |
| NC07 | 真实独立C及必要正反例通过；普通必修Issue闭合 |
| NC08 | 内部通过后commit/push及固定远程内容实际回读核验 |

原件附件不在工作区而使用本Prompt转交说明时，NC04注明“结论承接完成、原审核附件尚未入库”，不能宣称归档了原件；这不是伪造原件的理由。优先使用随本交接目录提供的真实附件避免此缺口。

NC01—NC08按本次范围判断；Process尚未完成不改N/A也不拖成本轮永远不完成，而是在整体依赖栏保留待办。当前提交仍需网页GPT二重核查，不能提前代其写PASS。

## 11. 发布与远程核对

只暂存本轮授权更改，避免git add .带入用户/另一个对话文件。检查diff、secret、大文件、相对链接、重复active规范及历史范围；不force push、不rewriting history、不回退已有合法新提交。

发布前核对全量保护清单或对应Git对象；文档hash变化不等于数值代码变化。可先本地commit固定实现，但不因一次commit停止父任务；内部通过后实际push main。

若远程在执行期间前进，先读差异，保护另一对话的Process工作；按影响最小合并/复核，不自动接受ours/theirs覆盖。服务暂时错误有界重试并保留，不关闭TLS、不迁移认证、不新增付费服务。

push后实际回读：五规范active与bundle、sources.json/生成manifest、当前技术入口、旧二审新增归档及本轮验收/发布文件。16项bundle均作真实远程对象/字节核对；大文件可从固定Git blob取得，不能仅看文件名/大小当成字节相等。

记录Local HEAD、origin/main、真实Remote、处理代码/文档提交身份和回读结果。文件不能事先写包含自身内容的尚未存在SHA；最终聊天报告真实最后HEAD，必要后续记录提交只追加已发生的事实。

无实际UI操作：Project Settings由用户复制本轮完整文本，五份Project Sources由用户根据其实际UI版本替换；不要再生成一份新的设置长稿或第三轮scope规则。若UI已使用本次文件，就不要求重复上传；不知道则明确USER_CONFIRMATION_REQUIRED，不宣称UI已完成。

## 12. 最终中文回复

返回完整结果，不返回下一份执行提示词：
A. 当前授权范围和完成状态，非Process部分是否可以关闭。
B. release→active→bundle的逐文件结果、清单数量及真实变更；正常只有AGENTS正文相对89371f6变化。
C. 旧网页GPT二审怎样归档、被审SHA、原件/转交范围；当前新提交仍待二审。
D. 当前README/审核入口/TECHNICAL_HANDOFF怎样更新，Process交给另一对话且其原件未动。
E. 实际测试、独立C、修复与保护结果；本轮实验模型调用/数值运行=0（以实际记录为准）。
F. 当前报告/源/包/数据及依赖是否保持；不得新称完整包已可提交。
G. Repository、Branch、CODE/ARTIFACT/最终Remote SHA、固定REVIEW_PACKET链接、实际回读及用户未跟踪文件状态。
H. 后续只剩本轮网页GPT核查、用户UI同步事实确认，以及另一对话负责的Process制作/最终包整合，不再提无依据算法任务。

状态示例必须绑定范围，不能机械填：

- SYNC003_GPT_REVIEW：PASS_WITHIN_REVIEWED_SCOPE（被审89371f6，按实际归档来源）。
- NON_PROCESS_CLOSEOUT_ENGINEERING：VERIFIED（本轮NC通过后）。
- CURRENT_CHANGE_GPT_REVIEW：PENDING。
- PROCESS_REPORT：DELEGATED_NOT_COMPLETED；不代写Evidence Lock。
- 整体Deliverable：FINAL_REVIEW；Submission：NOT_READY。
- Understanding：保留实际状态，不由本轮同步自动更新。
- UI：USER_MANAGED；只记录真实已知情况。

现在开始实际执行，在本次内完成同步、收尾与内部修复，再发布供网页GPT核查；不制作Process，不更改已验收实验报告，不重复开启研究。
