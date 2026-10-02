# 本轮工程交付回报

任务：SC-LAB1-PROCESS-INTEGRATION-SYNC-001。一次性接管与发布，不是新研究Goal。

## A. 总体结论

工程接管、输入保护、两条报告构建路线、完整项目源同步和独立内部核验已通过。发布状态在发布回执追加前保持 PENDING；不提前宣称远程已核实。用户对完整Process文稿的验收按本轮Prompt承接；网页GPT工程二审继续PENDING，逐条Evidence Lock、理解验收和教师提交不升级。

## B. Git版本与远程

Repository：https://github.com/woobowen/Smart_Cities_and_Location_Services.git ，Branch：`main`。

开始SHA：`6527945ad8e526fa606b2c09835f2e51291fa4d0`。工程内容提交与远程对象回读后，在本文件追加被审内容SHA及发布回执；包含回执的最终HEAD由对话最终回报精确给出，避免提交SHA自引用。未执行force push、reset、clean，也没有回退用户新增文件。

## C. 规范

四份原文均与用户独立基准一致；权威源和release同字节，无删段或自由改规则。release路径为 `releases/chatgpt-project-sources/<规范名称>`。

| 规范名称 | 版本 | 权威路径 | SHA256 |
|---|---|---|---|
| AGENTS.md | 2026-10-02 | `AGENTS.md` | `e1797cf00af4b55c1885d8e8753d93b0f4feadc6b1295670676e2636827a3a62` |
| SMART_CITIES_REPORT_WRITING_GUIDE.md | v1.2 | `docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md` | `d513867e76da9d5683a2b76325fa71bce8bb4387af6c2d148acb2e70fa6a5d0c` |
| SMART_CITIES_VISUAL_SYSTEM.md | v2.6 | `docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md` | `31501be77664a4d7f35ebb8d11118bdf58a18db7ce0090a125b4d87e95590b59` |
| WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md | v2.7 | `docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md` | `681ce8af7ead9b0d4abe0575ff546bc143064de42952bb5110bc350a420e4aa8` |

Research Protocol v1.2（2026-09-29修订）及 `docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md` 保持原字节，SHA256 `19f9bb4670bc3a485b064854f3d035d2a50a192386be53396851443ee5654a3f`。

## D. Process原件、工作源与复现

- 批准PDF：[Process_Report_Revised.pdf](../../../reports/process-report/experiment1-revised/Process_Report_Revised.pdf)，77页，SHA256 `45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83`。
- 批准ZIP：[Process_Report_Revised_LaTeX_Source.zip](../../../reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip)，SHA256 `00cb7b641b37b2a71a552fc5bef47fc551a16ea7ce88bcf139f2e68a5f1451da`。内部PDF配对一致；343个工作源成员逐字节相同。
- 唯一主源：[task1/reports/process1/source/main.tex](../../../task1/reports/process1/source/main.tex)；完整正文及生成规格保留原字节；当前兼容PDF仍为批准原件。
- 路线A在新的隔离目录实际执行 `bash compile.sh`，两遍XeLaTeX成功。
- 路线B实际执行 `python tools/make_diagrams.py` → `python tools/build_report.py` → `bash compile.sh` → `python tools/render_review.py` → `python tools/audit_report.py`，全部exit 0。

A/B新PDF都为 `971f9739e43b9d13a3e6e4b3154e47968d8d40a2fd63b9cae87950cb72226c2c`，与批准PDF不同。77页逐页文本含空白、尺寸、嵌图摘要和位置一致；同一渲染器200dpi比较，71页像素相同，34/41/45/59/75/77页有最多1/255的通道差，最大平均RGB差0.0008643717/255。实际逐页查看已覆盖1–77页，未发现本轮新增版面回退。批准p76已有底部局部行裁切保留，不改原件。

134个常规裁片复算PPI为73.69–146.82，按用户本轮明确APPROVED_NATIVE_WIDTH承接，不宣称达180；结尾额外裁片不冒充纳入该134项计算。整体文稿验收不等于逐条Evidence Lock。

[构建与视觉记录](build_and_visual_checks.md)含实际命令、环境、失败与修复、最终PDF和六个差异页。最终统一适配层再次真实执行 `--report process --regenerate --render`，新PDF及77张PNG与已查看B版本相同。统一 `task1.goal3 REPORT_BUILD` 也真实成功，生成[新REVIEW_ONLY验证包](../../../task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_完整双报告.zip)，116成员，只做冻结依赖probe，未执行FULL实验。

## E. Experiment与科学成果保护

独立比较6071个受保护既有文件，全部未变；Research、公共P2色值、Experiment批准PDF/ZIP、章节和图源、教师材料、starter、数据、结果、冻结合同及历史检查保持。`full_recompute/live`数值路径AST与开始版本相同。

实际改动仅在授权报告层：统一构建/打包选路、新Process验证与兼容PDF、当前Process状态字段、导航及最小模板默认值。旧审核正文仅加独立的当前入口提示，历史PENDING不重写。Experiment实际再次编译的25页PNG及比较记录与此前SYNC-003结果完全一致；继承此前已知环境字重差异，不冒称新视觉验收，也不重新开启Experiment收尾。当前阅读和打包仍用批准Experiment原PDF。

## F. release与UI

唯一结构化清单：[sources.json](../chatgpt-project-source-sync/sources.json)。`project_source=true`集合与本轮批准集合完全一致，全部真实字节匹配独立输入基准；清单总18行中的其他3行只登记非上传历史。上传成员如下：

- `AGENTS.md`
- `SMART_CITIES_RESEARCH_PROTOCOL.md`
- `SMART_CITIES_REPORT_WRITING_GUIDE.md`
- `SMART_CITIES_VISUAL_SYSTEM.md`
- `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md`
- `实验课1.pptx`
- `作业.zip`
- `作业1轨迹数据预处理.ipynb`
- `任务3_LLM辅助评估清洗.ipynb`
- `publication-plots.zip`
- `Experiment_Report_P2_Exact.pdf`
- `Experiment_Report_吴博闻_10245102410.pdf`
- `Experiment_Report_完整重构_源文件.zip`
- `Process_Report_Revised.pdf`
- `Process_Report_Revised_LaTeX_Source.zip`

[同步检查](source_sync_checks.md)记录37项隔离测试、真实plan/check只读、两次写同步幂等、失败保护和回滚。只移出授权的PreTask PDF/ZIP及Process旧模板副本，历史源均保留；新的合成模板preview保留模板身份，不加入本次Project Sources。

用户UI状态为USER_REPORTED_UPDATED。最终15项全部同用户基准，差异为空，**本次无需再次上传文件或重贴Project Settings**；Codex没有操作UI。

## G. 文件整理

根目录Process PDF/ZIP和原Experiment源ZIP保留；正式Process原件在唯一参考目录，实际工作源在source/。旧12页稿的12个原文件保留并归档到 `task1/reports/process1/history/technical-draft-12p/`；31页PreTask及其原审核记录保持原处。原模板PDF另存preview/history；原有不同hash的Skill ZIP未覆盖，批准原始Skill ZIP放入 `releases/skills/publication-plots-approved-original.zip`，不再循环读取release自身。

初始未跟踪的两个G1 HANDOFF ZIP按项目历史原件纳入Git，未混成新运行。完整初始盘点含16个release实质文件及4个Zone.Identifier；四个Windows元数据逐一私密保护后仅从release移出，无其他未知extra。6179个原文件的可恢复只读副本保留在仓库外私密目录；全页渲染、缓存、依赖和字体不提交。详情见[变更与保护](change_and_preservation.md)。

## H. 内部审查、修复与依赖

实施者：root、process_build、source_sync；独立审查上下文：independent_review，仅审阅工程与产物，不冒签报告作者或Evidence Master。最终范围与结论见[INTERNAL_REVIEW.md](INTERNAL_REVIEW.md)；独立程序复验包括输入/暂存区、归档、保护边界、全页重新渲染、嵌图、134裁片PPI、同步故障测试和导航/包检查。其实际视觉范围为40–77页、1/9页抽查、六个差异页及相关模板页；实施者查看1–39页和全12页模板，合计覆盖整份Process。

修复了缺ragged2e、Noto Sans和字体权重选择，均局部环境适配；修复同步源自引用/历史成员识别及模板残留高亮、节点重叠/标题分离，并回归。当前无材料、权限或研究定义阻碍。网页GPT二审仍未执行。

新增依赖：报告局部目录 `.venv/process-report-build-deps` 中的CairoSVG2.8.2、PyMuPDF1.26.7、Pillow12.3.0、numpy2.3.5及7项传递依赖；现有 `.venv/texmf` 增加ragged2e3.6；用户字体目录增加官方Noto Sans五款。无apt安装、无全局TeX/TLS/认证或shell配置修改，无字体二进制分发。科学环境numpy1.26.4/Pillow10.2未升级。完整版本、来源和hash在[构建记录](build_and_visual_checks.md)。这些仍为报告复现依赖，当前保留；清理前需确认替代环境或不再需要重建。

## I. 审核入口

[REVIEW_PACKET](REVIEW_PACKET.md)、[构建与视觉核验](build_and_visual_checks.md)、[来源映射](transfer_map.json)、[同步核验](source_sync_checks.md)、[独立审查记录](independent_review/REVIEW_NOTES.md)、[当前双报告导航](../../../task1/reports/README.md)。正式推送后会追加固定内容SHA的远程回读回执，最终对话提供固定提交链接。

## J. 下一步状态

等待网页GPT读取真实远程进行本轮工程二重验收（PENDING）。本轮没有发送邮件、代交作业或修改教师端；新包仅REVIEW_ONLY，未声明教师已提交。
