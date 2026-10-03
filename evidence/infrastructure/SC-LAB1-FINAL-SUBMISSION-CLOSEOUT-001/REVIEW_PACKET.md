# 实验一最终收尾：网页最终二审入口

任务：SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001。起始及上轮被审远程版本：`9d91392289b31a4afa5c94cfd3869da9f021b4ad`。本文件随工程内容提交；内容SHA由后续[PUBLISH_RECEIPT](PUBLISH_RECEIPT.md)固定，避免在提交中写自己的SHA。

本轮接管第76页授权局部修正版，保留已验收Experiment和科学成果；生成正式命名教师候选，完成真实隔离终检、独立内部核验，再正常发布和回读远程字节。网页最终二审仍为PENDING，Deliverable=FINAL_REVIEW，Submission=NOT_READY，sent_to_teacher=false。没有邮件或教学平台操作。

## 1. 实际身份与证据

- GPT是p76报告修改者，源包17项检查、两渲染器p76目视及两条干净构建属于作者自检；本轮原样保留。
- Codex主线程执行保护、导入、包外适配、实际构建、同步、教师包生成/真实解压检查与发布。
- `/root/independent_review`使用独立上下文进行只读实测；[INTERNAL_REVIEW](INTERNAL_REVIEW.md)和`independent_*`记录检查范围，不能用主线程摘要代替。
- 上轮网页工程二审原件在[prior_review](prior_review/)，结论仅绑定9d91392及该轮范围。本轮新SHA、新ZIP需新的远程二审。
- [证据与验收承接](EVIDENCE_ACCEPTANCE_HANDOFF.md)绑定40组互动、134常规裁片、85箭头和p76回引；无历史Lock补签、无新用户逐页验收、无Understanding升级。

## 2. 新成品与保护

| 成品 | 字节数 | SHA256 |
|---|---:|---|
| Process PDF | 8143247 | `dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23` |
| Process源ZIP | 56878339 | `831d61baa7de160796827b60f29e1ada9f1b3809c2a87aa4acd6b98703e352ef` |
| 正式教师候选ZIP | 23599893 | `c1d0b80313f81e81a6bcd4cc02d06002c442201379ea871c4c338386bde2eb66` |

权威成品：[PDF](../../../reports/process-report/experiment1-revised/Process_Report_Revised.pdf)、[ZIP](../../../reports/process-report/experiment1-revised/Process_Report_Revised_LaTeX_Source.zip)。唯一工作源：[source/main.tex](../../../task1/reports/process1/source/main.tex)，397个普通文件与输入ZIP逐成员同字节。阅读副本与根目录/release副本保持用户新原字节。

旧批准PDF/ZIP在[history/accepted-20261002](../../../reports/process-report/experiment1-revised/history/accepted-20261002/)按指定旧hash保护；新输入、被替换文件与首次候选另存仓库外任务快照，路径见[initial_inventory](initial_inventory.json)及[import_receipt](import_receipt.json)。[science_protection_check](science_protection_check.json)检查5591个保护文件，仅两个打包/身份元数据模块作授权维护，科研实现、原始数据、只读记忆、冻结结果、Experiment源与五规范未改。

## 3. 实际构建与页面

- A：[builds/route-A/build_receipt.json](builds/route-A/build_receipt.json)，隔离副本删除预置主PDF/build/review后运行`bash compile.sh`，真实两遍XeLaTeX，退出0。
- B：[builds/route-B/build_receipt.json](builds/route-B/build_receipt.json)，通过仓库统一`build_reports.py --report process --regenerate --render`执行make_diagrams → build_report → compile.sh → render_review → audit_report → check_p76_closeout，各退出0。
- 两路线WSL产物均为77页，SHA256=`700d91c9b850feb0fa63149928e904ae37c3108ce0fe6b379221f7333416b4ad`，原生全文精确相同，无未解决编译诊断，**并非用户原PDF同字节**。阅读/教师打包始终使用上表原件。
- [同环境实证](report_environment_comparison.json)另从旧ZIP干净编译。原件旧→新与同环境构建旧→新均仅p76截图矩形变化；旧/新输入各自到WSL的六图页34/41/45/59/75/77差异逐项相同。[独立signed RGB复核](independent_build_environment_check.json)验证更强的完整像素差分一致。六图PDF容器不同，但SVG/drawio、词序/词坐标、几何及独立200-dpi像素均实际一致，未只按Producer放行。
- [独立逐页目视](independent_visual_review.json)实际查看原件全部77张200-dpi单页及WSL六图页。p76完整气泡四边、首尾行、排除残缺回复、标题/邻页承接正常；135裁片均无损，p76约60.2901 PPI承接APPROVED_NATIVE_WIDTH。
- [测试摘要](test_summary.json)：64项既有/修改后回归、12项新增回归，共76项及10个subtests通过；[12项合成checker复测](verifier_synthetic_fixture_results.json)单独登记，不能代替真实教师ZIP终检。

## 4. 教师材料与真实终检

[文件夹](../../../task1/submission/teacher-delivery/10245102410_吴博闻_实验一/) / [正式ZIP](../../../task1/submission/teacher-delivery/10245102410_吴博闻_实验一.zip)。115个声明成员加manifest=116个普通文件，集合/每成员字节均精确一致，ZIP位于文件夹外且未压入自身。包内README、requirements、两个完成版Notebook、两份独立PDF、代码/配置/原始数据/冻结依赖及离线重放依据来自真实closure。

- [真实ZIP终检](teacher_zip_final_check.json)：CRC、安全路径、重复/Windows冲突、symlink、额外成员、字体/秘密模式、精确声明集合/大小/hash、PDF25/77及指定hash、39个Python模块语法、Notebook结构/保存输出检查通过。
- [fresh解压CLI与probe](teacher_delivery_check.json)：无.git，实际`python -B -m task1.goal3.package --verify-dir .`退出0，当前ROOT=隔离根，历史/合同/A-plan/生产冻结probe退出0，输入前后hash未变，模型调用0，轨迹处理0。
- [独立真实ZIP检查](independent_teacher_zip_check.json)及[独立fresh检查](independent_teacher_fresh_validation.json)另行实测相同最终hash，没有只读主线程PASS摘要。
- 两份Notebook分别12/8代码单元，执行计数全null、保存输出0、无error，完整复算代码与基线原字节保持；本轮不宣称Run All。此前真实FULL依据见[历史独立Notebook运行记录](../../../task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/c_review/notebook_runs_receipt.json)，按绑定身份承接。
- 首次候选README错误声称保留输出，已被独立检查发现；只修说明并重建、重验，旧候选和旧检查在[attempts/teacher-candidate-01](attempts/teacher-candidate-01/)保护。其他普通适配见[engineering_fixes](engineering_fixes.md)。未降低任何硬门。

最终二审与用户确认后发送上面正式ZIP；无需再压缩ZIP，也不发送整个release或LaTeX源交接包。manifest=TEACHER_SUBMISSION_CANDIDATE、sent_to_teacher=false；网页最终审核状态留包外。

## 5. Project Sources、环境与教师细则

[source_sync_receipt](source_sync_receipt.json)逐项给出15成员集合/实际hash：只替换两件Process，其他13项metadata与字节均保持；正向同步→check→再同步→check退出0、幂等且无mtime变化。唯一清单为[sources.json](../chatgpt-project-source-sync/sources.json)，release无其他文件。[UI交接](source_sync_checks.md)：本轮未收到新两件已上传的明确报告，USER_CONFIRMATION_REQUIRED；若用户已上传当前同hash文件，无需重复上传。Project Settings未改、无需重贴。

[environment_reuse](environment_reuse.json)：系统包、语言包、字体/工具链新增均0，全局配置改动0；现有科学.venv、报告局部依赖、TeX树和fontconfig按授权保留。

已重新读取[教师PPT第26页细则](teacher_submission_instruction_slide26.txt)：10月5日前将Notebook与报告压缩为ZIP发送至52285903012@stu.ecnu.edu.cn，命名学号_姓名_实验一.zip/.ipynb/.docx/.pdf，未规定具体钟点。发送由用户在最后二审与确认后执行；本轮没有发送。

## 6. 远程验收

[PUBLISH_RECEIPT](PUBLISH_RECEIPT.md)绑定内容提交与后续仅回执提交；[remote_content_verification](remote_content_verification.json)从独立网络fetch的FETCH_HEAD实际读取报告、源ZIP、397工作源、清单/15项分发、正式教师ZIP和116文件夹成员字节。最终HEAD在CLI最终回执给出，防止SHA自引用；后续提交差异须仅限本任务发布回执。本轮网页最终二审仍待执行。
