# 《智慧城市与位置服务》项目级治理与报告源同步
# 从用户更新的 release 输入迁移到权威源、生成器、分发集合和 GitHub

Task ID：SC-PROJECT-SOURCES-SYNC-003
Repository：https://github.com/woobowen/Smart_Cities_and_Location_Services.git
Branch：main
Workspace：~/lab/Smart_Cities_and_Location_Services
用户已更新的输入目录：releases/chatgpt-project-sources/
网页 GPT 本轮实际读取的远程锚点：4483f520eabb5358d1f35cf5c33a81d3b01e47e0
其父提交：718e6d9eb69d3e47ee8929755cd3bd3c94526fab
任务性质：项目级规则、已验收报告与源文件的同步和必要集成；不是新实验，不重开实验一研究。

## 0. 直接接管执行，并持续修复到本次同步闭合

用户已经在 ChatGPT UI 更新 Project Settings 和 Project Sources，并把本轮五份 Markdown、已验收 Experiment PDF 与源 ZIP 放入/替换到本地 release 目录，但没有更新仓库其他位置。

本次需要你完成：

保护收到的 release 文件 → 核验来源 → 导入仓库权威源 → 补入最新项目通用范围确认 → 接管已验收报告及生成链 → 迁移分发脚本与显式清单 → 正向重建 bundle → 自检及真实独立 C 审核 → 同任务内修复和回归 → commit/push → 回读固定远程版本 → 返回完整结果，等待网页 GPT 二重验收。

不得只回答计划，不得只复制七个文件后停止，也不得发现一个普通工程问题就生成 NEXT_CODEX_PROMPT 让用户再开对话。子代理完成、产生一份审核意见或本地 commit 均不是父任务结束条件。

本轮只使用既有合法账户和工具。新增记录级实验模型调用为0；不重新跑参数、组合、四模式、最终确认或全量清洗。治理角色为完成当前审核而实际调用，与实验调用分账；不能伪造独立角色或错误。

正常终点：本次必需同步和集成已内部通过、实际发布并核验。真正外部阻碍仅暂停对应部分，其余继续；若最终仅剩外部阻碍，保存可恢复检查点并准确报告，不假称全部完成。

## 1. 最新用户确认：四项均为整个项目通用要求

下面四项不是待决定事项，也不是只针对实验一。将它们以简短、明确的适用范围写进各自负责文档，不重复请求用户确认，也不把全部细则重新堆进 Project Settings。

### P1. 双报告是项目级正式交付规则

本项目正式实验、课程设计及当轮安排的正式报告任务，采用独立的 Experiment Report 与 Process Report，分别解释技术方法/结果与真实研究/AI使用过程。不得因为进入实验二，就把双报告视为实验一特例而省略。

教师最新明确格式要求仍按既定优先级处理。日常概念问答、临时解释或未授权的任务，不因存在这条规则就自动生成两份报告。

### P2. 工作流与实质 Multi-Agent、持续闭环是项目通用工作方式

正式任务要有与其问题匹配的真实研究、执行、核验、反馈、优化、修复和恢复机制，不能退化为模型只提出建议、普通函数改名或事后补一张架构图。

具体角色数量、实现工具和信息合同按当前任务设计，不将实验一 A/B/C 的全部实现永久固定；但不能把用户确认的项目级工作流/Multi-Agent要求重新解释为仅实验一才需要。

各任务应有与实际职责相匹配的核验证据。四模式、记忆、特定消融、调用预算不自动变成每个未来任务的必做实验，是否采用和怎样评价由老师材料及当轮批准方案决定。

最终记录级方法可以是经实测选定的确定性程序；这与研究/执行层有实质多角色工作流并不矛盾。不要求为了形式让每条数据都调用 LLM。

### P3. Process Report继承共同基础，记录当前任务新增演化

已经真实形成的项目工作流可作为后续任务共同基础。后续报告根据独立可读性作必要介绍或引用，重点说明本次新增、修正、否定及本次 Experiment Decision Process。

不得每次从零重写相同工作流历史、机械复制31页前期材料，或制造新的争论来表现迭代。共同规则和已有证据可以继承，其实际适用范围、来源及 Lock 状态不能扩大。

Evidence Master由用户明确指定，不因新对话读到“当前长期规划对话”就自动接管该角色。

### P4. 正式结构图的 draw.io 交付是项目级要求

本项目正式工作流/体系架构图以 draw.io/diagrams.net 为主要可编辑交付，保留真实可编辑的 .drawio 及相应 SVG/PDF 导出，不只是往 draw.io 里嵌入一张整图位图。

这不要求统计图、GIS图、数学几何图全部改为 .drawio；它们使用适合且可复现的原生工具。不同类型工具的边界写清楚，不新增与当前任务无关的绘图任务。

### 通用原则与实验一实例严格分开

项目通用：真实数据、公平比较、参数依据、先单项后组合、结果驱动选择、有限迭代、工程持续修复、自然问题驱动报告、第一人称Process、P2/XeLaTeX、成品保护和独立审核。

实验一专用：S-D-P、R0/S0/G0、30秒/400工作米/35度/5工作米、600条确认、三个Goal、特定候选数/模型轮次/四模式与记忆设置、25页/七章/10图/17表、具体轨迹和结论。不得把这些数值或方法写成整个项目永久要求。

时空语义与未知坐标处理是条件性通用规则；实验一的条件化分析授权不自动证明新数据的CRS，也不自动授权未来一切未知datum分析。

## 2. 当前远程事实：防止使用过时同步脚本覆盖新文件

网页 GPT 本轮实际读到的 main 为4483f520eabb5358d1f35cf5c33a81d3b01e47e0，提交说明是同步第一人称证据规则和前期Process参考。它已经比旧718e6d9提交前进，不能 reset 回旧版本。

已检查的旧同步脚本为：

evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py

该版本仍硬编码13项，包含 len(SOURCES)==13、EXACTLY 13及删除非allowlist普通文件的逻辑。旧输入不是只存在11项；不要仅替换字符串“11”为“16”。

旧 UPLOAD_INSTRUCTIONS.md 还要求删除全部当前Project Source后上传13项。这个危险的整体替换流程需迁移为按实际差异更新，不要求用户删除当前已经正确上传的文件。

因此，在保护新输入并迁移所有清单/脚本以前，禁止对真实 release 执行旧sync的写模式，禁止rsync --delete、git clean、rm -rf或按照旧白名单清理新文件。先读取脚本，不因文件名熟悉就运行。

## 3. 先核验工作区，再将收到的 release 建立不可变快照

1. 核对pwd、git status --short、当前分支、HEAD、origin/main和实际远程。锚点不是强制回退目标；如果已前进，先读差异，保留合法新成果。
2. 本轮用户放入release的新文件属于授权输入，即使未commit也必须保护。不要stash、还原或清除它们；其他用户未提交内容亦不擅自处理。
3. 在任何会改变release或权威源的操作前，对完整release清单记录相对路径、类型、大小、SHA256；检查路径、符号链接、重复后缀和目录，遇到异常先保留。
4. 将收到的七份核心输入原字节保存到本任务内部 received/，记录其本地路径、hash和导入来源。该快照是历史接收证据，不是第二份active源，不能放回上传集合。
5. 记录起始权威文档、原始材料、冻结数值实现/结果、已验收参考、当前Process文件、模板与用户原有ZIP的保护清单。
6. 本轮允许的是“用户更新release → 一次受控导入”。导入后恢复“权威源 → 显式清单 → release”的正常单向分发；不得长期让两套文档相互覆盖。

建议内部目录：evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/。

## 4. 七份输入基准：本地实际核验，不凭文件名和截图

以下是此前网页侧确认、并在本轮交接中重新读取字节计算的输入基准，不是本次加上范围条款后的最终输出hash：

| 文件 | 大小/B | 输入 SHA256 |
|---|---:|---|
| SMART_CITIES_RESEARCH_PROTOCOL.md | 11981 | 332741175630b1329387a0d69acf0061c6278c82bb27596f1d4629c2aa13a378 |
| SMART_CITIES_REPORT_WRITING_GUIDE.md | 24040 | abc729c5f7f764021ae1417dc6e8fcb1997eb3632747e46c8d0d53166642ff37 |
| SMART_CITIES_VISUAL_SYSTEM.md | 42569 | fbba109a796cff5ffe09848986a75b749248e5d609860c54eb2004b839fd9cbc |
| WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md | 44284 | 2385583504caa7c4a7708cd12602c2f692dfd6bb217e1b6ffdd3558b25a22fbd |
| AGENTS.md | 33593 | aec7864126d07644ab2d8a724aad7357d146b9adf000ff3e8a3a70b2b644d171 |
| Experiment_Report_吴博闻_10245102410.pdf | 907540 | 2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0 |
| Experiment_Report_完整重构_源文件.zip | 3515637 | 6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd |

输入文档版本：Research v1.1；Writing Guide v1.0；Visual v2.4；Evidence v2.5；AGENTS Revision 2026-09-29 · Report production / accepted-source integration。

逐字节比较并保存机器结果。差异不能凭mtime或同名认定为更新：先保留原件、查明是否换行变化、用户合法后改或错误文件。与本Prompt可明确对应的合法新修订可在C核验后合并；研究/范围含义不明时只暂停该输入分支。不能通过覆盖本地用户文件让比较强行通过。

报告PDF与ZIP属于已经验收的不可变输入，不因为增加项目通用条款而改动或重打包。

## 5. 导入权威文档，并只补这次批准的范围澄清

导入映射：
- Research → docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md
- Writing Guide → docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md
- Visual → docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md
- Evidence → docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md
- AGENTS → 仓库根 AGENTS.md

新文件是完整底稿，不按旧仓库删减回旧文风。不得把(3)/(7)/(10)等上传后缀版本选作active。历史文件保留历史身份，修复active入口而非全局删除旧记录。

逐份作最小补充：

A. Research：说明适用整个项目，工作流/多角色及持续闭环为共同方式，具体任务重新确定方法、数据和评价；保留批准空间内自主选择、不篡改标准、不强求组合获胜。
B. Writing Guide：明确双报告的项目级正式交付范围；解释后续Process如何继承基础与记录新增演化；保留W01—W22，明确实例不构成未来实验输入。
C. Visual：保留精确P2与XeLaTeX，补正式工作流/架构图的draw.io交付边界；不改变已验收图型和页面，不把25页、三维图或某张G6变成固定配额。
D. Evidence：将歧义的“从Experiment 1开始”改为每项正式研究适用的规则，真实历史起点需要时另标；将角色入口写成用户指定的Evidence Master；保留真实原话、第一人称、最小框选、箭头、PPI、原文归属与Lock规则。
E. AGENTS：明确P1—P4是项目通用，受托任务按其规模实现真实职责；继续保护已验收文稿、集成生成器和独立审核；迁移分发规则。

各模块细则只有一个主负责文档，其他文件引用；不复制四份长篇相同段落。修订日期用真实时间，版本记录新增范围澄清。若底稿仍为上列版本且正文确有修改，可采用Research v1.2、Writing v1.1、Visual v2.5、Evidence v2.6；AGENTS更新Revision说明。若用户另有更新则按其实际版本递增，不能倒退。

保存输入→最终文档的diff和变更理由；检查链接、章节引用、优先级及“通用/条件/本任务示例”之间无冲突。不是把标题改成项目通用却留下只针对task1的强制数值。

## 6. Project Settings只交付最小UI补丁，不创建第二套active设置

ChatGPT UI中的Project Settings已经由用户更新；你不能直接修改该UI，也不能声称已刷新。

本轮四项范围澄清可能需要设置中的少量补充。提供一个 PROJECT_SETTINGS_SCOPE_PATCH.md 作为本次交付副本，包含推荐插入/替换位置、短文本及对应规则文件；通常只涉及总适用范围/角色、正式报告、Evidence三个位置。

说明四项适用于项目后续正式任务；详细写法、Agent实现和图表规则继续引用各自文档。不要另写一份庞大的Project Settings，不在仓库根/Project Sources创建第二份active设置，不复制完整规则到README。

该补丁只保存在本任务handoff目录，标明TRANSFER_COPY / USER_UI_ACTION_REQUIRED。用户后续复制不属于你已完成动作。文档更新后哪些Project Sources需要替换也要列明；当前UI匹配的是输入基准，不自动匹配本轮再次修订后的输出。

UI操作是后续用户动作，不作为完成本次仓库同步的阻塞条件。

## 7. 接管已验收的Experiment PDF与完整源包

用户已验收的是25页重构版，不是仓库此前22页旧稿，也不是合成P2模板。

建议正式参考资产目录：reports/experiment-report/experiment1-reconstructed/，保留原规范文件名PDF和ZIP。若已有同角色且明确的canonical目录，直接复用并在manifest登记，不创建两份竞争active参考。

1. 原PDF/ZIP保持输入hash不变；复制到canonical参考位置，release只从该位置分发。
2. 对ZIP检查CRC、重复成员、越界路径、符号链接、字体二进制、秘密和异常执行行为。实际基准ZIP有72个成员，根目录Experiment_Report_source/；源入口Experiment_Report.tex、README.md、build.sh；内置Experiment_Report.pdf与外部批准PDF字节相同。本地仍须重验。
3. 保留不可变源ZIP，并将可编辑内容安全导入task1报告工作目录，明确一处是当前权威章节源。路径适配只改必要构建关系，不改论文式含义、实验数字、结构、图注和已验收构图。
4. 仓库当前Experiment入口及 task1/reports/experiment1/experiment1.pdf 应切换到已验收25页版本，旧稿通过原Git提交/明确历史记录保留，不继续作当前成果。
5. 接入真正的生成器：检查 task1/reports/build_reports.py 及 python -m task1.goal3 REPORT_BUILD 调用链，不能仍由旧章节生成器重建22页工程稿，也不能只复制PDF却不接源码。
6. 修改实际调用关系/模板路由。旧生成逻辑可保留为明确legacy，但不得从正常入口无声恢复。不得为了兼容旧校验而改回旧章节或旧句子。
7. 公共P2颜色源保持不变。源包内颜色副本只作来源受控的便携副本，核对实际色值；仓库不出现两份可独立手改的色值权威。
8. 两幅既有.drawio及绘图源码保留可编辑结构；不因新范围条款重画已验收报告。

### 真正检查能否重建，不能用预带PDF伪装编译

在临时干净副本移开已有输出PDF，使用README/build.sh真实编译；保留退出码、日志、实际输出和依赖。核对姓名吴博闻、学号10245102410、页数、文字、公式、表图、引用与渲染。

批准的参考PDF/ZIP永远不覆盖。新编译PDF可以因元数据字节不同，须明确比较文字及视觉是否一致；不能宣称SHA相同。报告25页仅是本次已验收成品的回归事实，不是未来任务页数要求。

全部重建页面至少200dpi渲染并实际查看；同一内容无变化的页面可记录明确视觉对照，不用缩略图或脚本哈希冒充目视。缺字、换页或构图明显变化先修复环境/路径；需要改变已批准内容才能解决时保持原成品并仅阻断相应重建集成，返回具体差异。

至少重新验证一次正常生成链不会恢复旧稿/覆盖批准参考；第二次构建的输入与结果应可说明。源包可编译、图可重画和全实验可复算是不同结论。图重画只做本次实际能验证的范围，不凭有SVG就宣布完整绘图复现。

本轮不为报告编译再跑全量清洗或历史84次模型实验。处理、指标、数据和记忆未变时继承其真实旧run身份；数值CODE_SHA仍为对应实际计算版本，不替换为本次文档提交SHA。

## 8. 保护已经同步的Process参考，不扩大成过程报告制作任务

当前远程已有：
- reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_REVISED.pdf
- reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip

应保留其实际文件和用户批准范围。读取既有证据：
evidence/infrastructure/SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md

该记录明确：源ZIP能构建31页，但不完全重现REVISED.pdf的文字与标注几何，且构建有已记录缺字等限制；SOURCE_ARCHIVE_BUILD为PARTIAL。不能因本轮再次复制文件就改成完整复现PASS，也不能因这种既存限制删除源ZIP。

这不是本次新发现的必须重做全部Process任务：保持参考、限度和关联记录，继续治理与Experiment集成；不改其原文/截图/箭头、不重新LOCK、不把PreTask1材料当作完整实验一Process已完成。

当前task1 Process送审稿与前期参考身份分开。Experiment构建回归不得无意重生成或覆盖Process页面；需要只构建Experiment的入口可做最小适配。

模板预览也保持模板身份，不能用25页真实报告覆盖 Experiment_Report_P2_Exact.pdf，或让Process模板文件名证明真实Evidence Lock。

## 9. 本次完整分发集合：以明确16项为迁移基准，不写死永久数量

本Prompt批准保留当前远程13项，并增加写作指南、已验收Experiment PDF及源ZIP共3项。本次基准集合为以下16个规范文件名，次序不代表优先级：

1. AGENTS.md
2. SMART_CITIES_RESEARCH_PROTOCOL.md
3. SMART_CITIES_REPORT_WRITING_GUIDE.md
4. SMART_CITIES_VISUAL_SYSTEM.md
5. WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md
6. Experiment_Report_P2_Exact.pdf
7. Process_Report_P2_Locked_v1.pdf
8. WF_WorkflowConstruction_PreTask1_REVISED.pdf
9. WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip
10. Experiment_Report_吴博闻_10245102410.pdf
11. Experiment_Report_完整重构_源文件.zip
12. 实验课1.pptx
13. 作业.zip
14. 任务3_LLM辅助评估清洗.ipynb
15. 作业1轨迹数据预处理.ipynb
16. publication-plots.zip

不是“截图里七份即全部项目源”，也不是未来永远EXACTLY16。程序按唯一批准清单计算len，核查集合、路径、普通文件、规范名和字节。

来源：五份规范用§5路径；两个Experiment参考用§7登记的canonical目录；前期Process用§8路径；模板保留 templates/latex/*/preview/ 原路径；老师PPT/ZIP和两Notebook沿用旧manifest中的已核验原始路径，不重新保存或执行starter。

Skill归档沿用既有批准原件与实际安装成员。原脚本的固定SHA256为b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041，须本地验证而非复制声明。保留其原archive，禁止重打包来凑hash。原archive若仍以bundle保留目录为来源，明确标为受固定hash和installed effective members独立验证的原件例外；不得只做源与自身比较就PASS。

遇到release另有未在此集合的文件：先保留并判断类型/来源，不能默认删除。已存在且能查到更晚用户批准的成员可记录依据再纳入；没有依据的条目不擅自上传或清理，只阻断bundle集合闭合，其余同步继续。不得把内部README/manifest/脚本/日志/备份、Project Settings文本或重复上传后缀混进release。

## 10. 迁移同步脚本、manifest和上传说明

优先改既有脚本与内部清单，不另建第二套不可控同步平台。建议将结构化显式清单放在现有 evidence/infrastructure/chatgpt-project-source-sync/ 下；SOURCE_MANIFEST.md和UPLOAD_INSTRUCTIONS.md由其或同一权威定义生成。

每成员至少登记canonical_name、active_path、语义角色、适用范围、当前版本、hash、配对ID（适用时）、批准/历史范围、被替代关系。project-source身份与文件角色分开：治理规则、教师材料、starter、合成模板、真实成品、历史局部参考和源码不能全写成一个语义标签。

迁移所有硬编码11/13的正常执行、帮助、错误信息、测试、README和生成模板；保留历史日志中原有数量，不篡改旧事实。不得简单替换成硬编码16。

同步必须先验证全部输入，再原子/受控更新目标。至少具备：
- --check：只读验证，不创建/修改manifest、不重写文件、不改mtime。
- 可查看的差异计划：新增、变化、缺失、意外项和不安全项。
- 写同步：权威源到bundle，全部来源存在且安全才执行；未知extra默认报错并保持，不自动unlink。
- 无变更重复执行幂等：正文、清单、日期、哈希及目标mtime不无故波动。
- 更新退出失败时不丢原文件；有可恢复信息，不出现一半新一半旧却输出READY。

允许采用最小清晰函数和一次结构化清单，不强制复杂事务框架。安全删除确实需要时必须有具体授权列表和备份，本轮默认无删除有效文件授权。

UPLOAD_INSTRUCTIONS改成差异更新：按本轮UI差异表替换内容变化的文件、保留未变有效资料；不要再写“先删除全部Project Sources”。说明生成文件、本地同步、远程验证、bundle就绪与用户实际UI上传是五种不同状态。

## 11. 模板、导航和现有提交包按影响范围同步

更新根README/文档路由、模板README、task1当前报告链接、来源manifest及必要运行说明，使新会话能找到五份规范与25页已验收报告；已验收样例不成为未来数据、算法或结论依据。

模板保留稳定视觉组件和必要说明，只补写作指南/适用范围/真实参考链接，不嵌入实验一数值和结论，也不无理由重新生成未改变的合成preview。

修正当前报告导航与已存在的teacher_delivery_mapping/REVIEW_GUIDE中受新报告影响的页码或路径。只更新当前读者导航；旧版检查和历史页码保留其原版本身份，不伪称旧检查针对新PDF。

若现有对外当前包入口仍指向22页旧报告，使用已修复生成链生成新的REVIEW_ONLY具名包，实际核对包中Experiment与批准成品一致，Process保持真实待审身份，依赖/Notebook/数据没有被遗漏。保留旧ZIP历史，不覆盖用户任意文件，不发送教师。

纯PDF/文档替换且运行依赖、输入和Notebook字节完全不变，可用具体成员hash继承旧FULL复算证据，明确不是本轮又跑一次FULL；运行依赖确实变更才做必要的隔离回归。不能用“只同步文档”隐瞒包内容仍是旧稿。

## 12. 在本任务内完成A/B/C审核与修复，不将工作交回用户

A：核对P1—P4适用范围、来源角色、保留集合及迁移计划，发现旧约束与新输入冲突。
B：导入、最小文档修订、生成器/同步脚本适配、报告构建、测试与发布准备。
C：独立读取received基准与真实active/bundle/报告，检查内容范围、字节、删除风险、实际编译、版本和已做检查，不只认可B的PASS清单。

可使用现有真实独立子上下文完成C，不强制新增厂商或专用Provider。主线程自己写完后再看一遍只能记作者自检；不能宣称独立C。依赖确实不可用则如实报告，并继续可做项。

发现普通bug后：复现→最小修复→专项测试→C复验→重建受影响产物→恢复父任务。不得运行后只给“下次需要修复同步脚本”便停止。

范围已批准的路径适配、相对链接、scope文本和安全脚本修复无需新弹窗；方法改变、真实资料缺失、付费/权限或不可解决的参考内容不一致才局部升级。

## 13. 必须实际运行的测试与验收

至少有正反例，不用纯字符串grep代替全部验证：
- 正确源集正向同步并--check通过；各成员active/bundle字节一致。
- 重复canonical名、缺来源、错误hash、意外extra、目录/符号链接/路径越界被拒绝。
- 输入缺失或hash错误时目标不被部分覆盖；--check前后工作树和目标字节/mtime不变。
- 第二次无变更同步没有新diff；不因当前日期重写所有manifest。
- 在测试临时目录扩展一个有明确声明的dummy成员后，数量由清单计算，证明实现没有隐藏的固定16依赖；不能把dummy放进真实项目源。
- 核验规范版本/路由/P1—P4、保留Process语言/术语归属/最小框选和P2精确值，任务数值未升级为通用标准。
- 报告pair原字节不变；新生成链由真实源码编译，保护批准PDF/ZIP，连续构建不恢复旧稿。
- 同步/报告构建不得触发实验模型、参数搜索、修改raw/记忆/数值结果或Process已验收素材。
- 新包成员和当前报告对应；无秘密、字体文件和依赖缺口。

使用现有测试框架扩充必要专项测试，回归受影响构建/同步接口。无需以旧469测试总数作为目标，更不能重新运行所有数值实验来证明复制文件正确。

本任务验收矩阵：

| ID | 必需证据 |
|---|---|
| SYNC-01 | 起始工作区、实际remote、用户release快照与七份输入核验 |
| SYNC-02 | P1—P4已写成项目通用，任务实例/条件模块/历史参考清晰 |
| SYNC-03 | 五份active规范完成导入与必要范围修订，版本与路由一致 |
| SYNC-04 | UI最小补丁与Source差异清单实际生成，没有第二份active Settings |
| SYNC-05 | 批准Experiment PDF/ZIP原hash保持，canonical来源明确 |
| SYNC-06 | 实际报告源与生成器接管，真实编译/视觉比对，不恢复22页旧稿 |
| SYNC-07 | Process参考与既有PARTIAL复现结论保留，未越权修图/Lock |
| SYNC-08 | 明确本次成员集合，权威源与bundle一致，无误删有效材料 |
| SYNC-09 | 脚本无永久固定11/13/16；check只读、同步幂等、异常安全 |
| SYNC-10 | manifest、上传说明、模板与当前导航对应，旧历史未篡改 |
| SYNC-11 | 当前REVIEW_ONLY包/报告关系正确，影响范围复现证据真实 |
| SYNC-12 | raw、冻结方法/数值、记忆、Skill原件及用户文件保护成立 |
| SYNC-13 | 独立C实查完成，普通必修Issue闭合、父任务恢复 |
| SYNC-14 | 内部通过后commit/push并实际远程逐成员回读、hash/内容核对 |

每项记录具体对象、动作/命令、期望、实际结果、范围、状态和证据路径，不以其他PASS抵消阻断项。Process原归档的既有PARTIAL不等于本轮同步失败，只要未修改它且正确保留限制；Experiment新导入源的未解决构建问题则明确影响SYNC-06，不能混同。

## 14. 实际Git发布与远程核验

按本次授权可在中途本地commit固定实现，但内部C与必需同步完成以前不把未完成版本作为正常发布。不要git add .带入用户无关变更。

发布前检查diff、secret、大文件、绝对路径、引用、Notebook意外执行、重复active源和受保护文件；必要依赖只用项目/临时隔离，不改全局TLS、认证或字体配置，不把字体二进制提交。

远程前进时先比较并保留合法新工作，不force push、不reset旧SHA、不重写历史。网络暂时错误有界重试，保留失败；权限/安全限制不绕过。

push后必须通过真实远程读取证明：
- Local HEAD、origin/main和实际remote对应；
- 本次全部bundle成员的remote raw bytes与本地清单相等，关键active文件也相等；
- 报告PDF/ZIP、实际源、同步脚本、manifest、检查记录与当前入口存在；
- 固定SHA URL引用的确是本次内容，不能只比较跟踪分支缓存或树条目数量。

允许通过Git远程对象和blob实际取回大文件核验，不能用GitHub页面显示的size替代hash。注意Git换行转换/attributes会影响字节；必要适配须局部明确记录，不能改全局设置或用不同文件算hash蒙混。

避免自引用SHA：发布记录只记录已经存在的提交与回读事实；最后聊天给实际最终HEAD并明确代码/产物/发布记录提交的关系。

## 15. 输出内容与最终回复

唯一审阅入口：
evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md

最低产物包括：本Prompt、received输入清单/快照、起始保护清单、规范diff与范围说明、canonical映射/最终成员清单、测试命令与结果、报告源重建和视觉检查、包对应验证、C审核与Issue关闭、最终hash表、UI差异表、Project Settings最小补丁、FINAL_RESPONSE.md和实际发布核验。

不要额外再创建多套同义“final manifest”；原manifest继续作为分发权威，本次文件记录迁移事实与检查。

最终中文A—H：
A. 总状态、已完成范围和仍受阻部分；不是重新汇报实验一效果。
B. 四项项目通用规则具体写入哪里，哪些实验一实例仍为任务专用。
C. received→active→bundle映射与最终文件数；旧脚本如何安全迁移。
D. 已验收25页Experiment的导入、编译、原件保护、生成器与包检查；Process原件和PARTIAL限制如何保留。
E. 真实测试/构建/内部C范围，修复历史；本轮实验模型调用数、数值结果是否改变。
F. 文件、版本、hash和UI差异：需要用户替换哪些Project Sources；最小设置补丁位置；未变PDF/ZIP不要建议重复上传。
G. Repository、Branch、COMMIT/ARTIFACT/最终Remote SHA、实际回读结果和固定REVIEW_PACKET链接；保留的用户文件状态。
H. 边界：等待网页GPT真实GitHub二审；未替用户操作UI、未完成新增Evidence Lock、未代发教师、未替用户宣布Understanding或Submission通过。

状态分别记录：
- REPOSITORY_SYNC：VERIFIED/PARTIAL_BLOCKED。
- UPLOAD_BUNDLE：READY/NOT_READY（按实际集合及字节）。
- EXPERIMENT_REPORT_INTEGRATION：VERIFIED/有明确范围的限制。
- PROCESS_REFERENCE_REPRODUCTION：保留既有PARTIAL及依据，不升级。
- UI_SCOPE_UPDATE：USER_ACTION_PENDING（本轮规范内容变化时）；迁移前用户上传成功仍是原版本历史事实。
- GPT_SECOND_REVIEW：PENDING。
- 实验一Submission：NOT_READY；不得SUBMITTED。

完成后停下，把真实结果交给用户转回网页GPT。网页GPT随后会读取你发布的固定提交审查；不要提前代其写PASS，也不要返回下一份让用户再转发的同步提示词。