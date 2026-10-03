# 实验一最终收尾：独立内部只读核验

任务：SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001。独立审核上下文：`/root/independent_review`，受主线程委派，但未制作或修改被审报告、科研实现、教师包或项目源清单。审核者仅在仓库外临时目录执行只读产物检查，并在本任务目录写入自己的 `independent_*` 证据和本文件。

审核基线：`9d91392289b31a4afa5c94cfd3869da9f021b4ad`。本记录先绑定实际文件指纹；发布前尚未知本轮提交SHA，由后续发布回执绑定内容提交，审核者不填造SHA。被审适配/源/状态/README指纹见 [independent_reviewed_file_fingerprints.json](independent_reviewed_file_fingerprints.json)。

**本地目标范围独立工程核验：PASS。** 本轮远程发布/回读由主线程继续执行并另行登记；网页最终二审仍为 **PENDING**，Deliverable为FINAL_REVIEW、Submission为NOT_READY、sent_to_teacher=false。此结论不代表新的用户逐页验收、Evidence Lock、Understanding升级或教师已收到作业。

## 1. 真实输入、保护与当前映射

首次命令为 `ls -la`，确认既有科学 `.venv`、报告局部依赖和fontconfig后复用。初始main、本地HEAD、origin/main与直接远程main均为上述基线，未发现其他本地修改；初始两对根目录/release修改为本轮用户新输入。起始证据见 [independent_initial_inputs.json](independent_initial_inputs.json) 和 [independent_initial_tracked_hashes.json](independent_initial_tracked_hashes.json)。

| 本轮输入 | 字节数 | SHA256 |
|---|---:|---|
| Process PDF | 8143247 | `dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23` |
| Process源ZIP | 56878339 | `831d61baa7de160796827b60f29e1ada9f1b3809c2a87aa4acd6b98703e352ef` |
| 实际最终教师ZIP | 23599893 | `c1d0b80313f81e81a6bcd4cc02d06002c442201379ea871c4c338386bde2eb66` |

独立校验新ZIP的CRC、安全路径、重复名/Windows大小写冲突、符号链接、字体二进制和凭据文件名；397个普通成员逐一解压及原字节对照，内嵌PDF严格配对。输入PDF/ZIP在根目录、权威报告目录和release，以及工作源/当前阅读PDF的映射全部保持指定原字节。构建后的唯一工作源仍为397个文件，集合与每成员字节严格匹配输入ZIP，无额外或缺失。

旧批准PDF/ZIP已实际读取Git基线原对象并校验指定旧hash；当前history/accepted-20261002中的旧件再次核对相同hash。仓库外新输入/被替换文件快照保留，未reset/clean/覆盖研究成果。最终映射见 [independent_final_mapping_and_protection.json](independent_final_mapping_and_protection.json)。

## 2. p76、原件与逐页视觉

审核者读取真实生成器、`closing_evidence.json`及生成的`closing_crop_map.json`，核对规格实际驱动生成器：原图511×2048且原hash不变；边界 `[186,68,510,263]`，无损裁片324×195，显示宽136.5mm/右侧36.4mm，实际60.2901 PPI按既有APPROVED_NATIVE_WIDTH承接。不是手改PDF或仅修生成TeX。

独立135个裁片逐像素与各原始图整数边界切片比较均无损。40组互动规格、134常规裁片、85既有箭头、原始素材及正文保持；仅p76预定截图内容变化。对应检查见 [independent_process_programmatic.json](independent_process_programmatic.json) 和 [independent_page_comparison.json](independent_page_comparison.json)。

审核者通过图像工具**逐张实际查看了当前正式原件全部77页200-dpi单页**，另逐张实际查看6张WSL重建结构图页面，记录各单页路径/hash和实际观察，未用联系表或文本提取冒充目视。封面姓名学号、目录、原生正文、页码和尺寸正确；第76页用户气泡四边及首尾行可见，下方残缺GPT回复已排除，标题、右侧文字和相邻75/77页衔接正常，没有新增圈框、错误箭头或遮挡。既有截图原生清晰度按此前批准范围保留，未上采样或夸大PPI。目视证据见 [independent_visual_review.json](independent_visual_review.json)。

## 3. 两条真实构建与环境差异实证

读取A/B隔离构建入口、清理预置主PDF逻辑、实际两遍XeLaTeX日志、各命令日志及实际输出，而非仅取PASS摘要：

- A：`bash compile.sh`，退出0，两遍真实XeLaTeX，77页。
- B：仓库统一入口调用`python tools/make_diagrams.py` → `python tools/build_report.py` → `bash compile.sh` → `python tools/render_review.py` → `python tools/audit_report.py` → `python tools/check_p76_closeout.py`，六步全部退出0，两遍XeLaTeX，77页；预置主PDF已移除。

两条实际重建PDF同hash `700d91c9b850feb0fa63149928e904ae37c3108ce0fe6b379221f7333416b4ad`，**与用户新原PDF不同字节**。阅读及教师包始终使用用户新原PDF。源包作者检查程序重放仅记录工程程序复播，未称独立审核；独立审查来源是本上下文另行读取和计算。

审核者重新读取原始旧/新PDF、同WSL环境旧构建PDF和新A/B构建PDF，独立对77页原生全文、页面尺寸、200-dpi像素进行比较：原件旧→新、同环境旧构建→新构建均仅p76指定矩形有差异。旧输入→旧WSL与新输入→新WSL不仅差异页34/41/45/59/75/77、像素数量/bbox相同，**整张有符号RGB差分层逐页完全相等**。因此六页差异有同环境旧基准实证，未按页号或Producer猜测放行。

6幅重新导出图PDF虽容器hash不同，但独立实际核对SVG/drawio原字节、文字词序、逐词坐标、页面几何和200-dpi单独图像全部相同；6页目视显示文字/关系/箭头可读，无新增重叠。实际旧构建两遍日志也已读取。独立重算方法/结果见 [independent_check_environment.py](independent_check_environment.py) 和 [independent_build_environment_check.json](independent_build_environment_check.json)。

## 4. 真正最终教师ZIP的独立终检

被审正式文件为 `task1/submission/teacher-delivery/10245102410_吴博闻_实验一.zip`，绑定上表c1d0b803…，并非旧REVIEW_ONLY包或合成夹具。审核者在原科学`.venv`中实际执行新源包`verify_teacher_zip.py --probe --python <原科学Python>`，退出0，输出 [independent_teacher_zip_check.json](independent_teacher_zip_check.json)。CRC、安全路径、重复/大小写冲突、符号链接、字体/秘密模式、额外文件、manifest精确集合/大小/hash、PDF25/77页与指定原件hash、39个Python模块语法均通过。

另用自己的检查程序独立fresh解压同一真实ZIP，再次核对所有成员及来源hash、声明集合、大小、总字节、文件夹/ZIP严格同字节；115个manifest声明成员加manifest自身，共116个普通文件，manifest不计算自身hash，ZIP自身位于目录外。仅goal2历史result_summary的机器专有命令路径有明确变换记录，科研数值未改。

在fresh无.git目录中**实际执行**`<科学Python> -B -m task1.goal3.package --verify-dir .`，退出0且115成员VERIFIED；另实际以`-I -B`导入当前fresh根代码，确认ROOT为隔离根，执行已有`static_probe(payload)`，历史绑定/合同/A-plan/生产冻结均VERIFIED，11个注册策略，新增模型调用0、轨迹处理0。检查前后fresh成员及被保护科研文件字节不变。命令、真实输出和检查程序分别见 [independent_teacher_fresh_validation.json](independent_teacher_fresh_validation.json)、[verifier日志](independent_teacher_verify_dir.log.txt)、[probe日志](independent_teacher_static_probe.log.txt)、[independent_check_teacher.py](independent_check_teacher.py)。

两份完成版Notebook实际读取JSON及全部20个代码cell，分别25/17总cell、12/8代码cell；代码完整且未替换为starter，原字节与基线完成版一致，执行计数全部null、保存输出0、error输出0。本轮没有Run All；此前4项真实FULL运行记录的执行回执hash及当前Notebook绑定另行实际核对，按历史身份继承，见 [independent_science_extended_and_FULL_inheritance.json](independent_science_extended_and_FULL_inheritance.json)。

独立审查发现首候选README错误声称Notebook保存运行输出；主线程仅修README并重算manifest/ZIP，Notebook与科学文件保持原字节。旧候选hash f588c386…及其原检查证据保留在 [attempts/teacher-candidate-01](attempts/teacher-candidate-01/)。本结论绑定第二候选，检查器、fresh CLI/probe与文件夹逐成员检查均重新实际执行，未将首候选PASS挪用到新ZIP。

现有REVIEW_ONLY默认文件名安全门保留；教师适配器是独立显式入口，复用closure/static_probe。已审阅新增安全回归、p76缺失/变规格及旧hash失败场景和实际测试日志：76项与10个subtests通过，其中64既有/维护回归、12新增。另12项ZIP合成夹具复测属于验证器分支测试，未拿来替代真实ZIP终检。

## 5. 项目源、科学保护及真实验收身份

独立重新执行`sync_sources.py --check`退出0，从清单`project_source:true`计算并核对完整15成员精确集合；3个历史排除项的行仍保留。只两件Process更换，其他13项清单metadata、active字节与基线一致，release逐项同字节，无extra。已读取主线程正向写/check/重写/check实际回执，幂等验证通过。release不含教师ZIP、审核记录、设置或本Prompt。UI仍USER_CONFIRMATION_REQUIRED，未冒称本轮已替换；Project Settings未改。

独立比较全部6773个起始tracked普通文件的当前hash，无缺失；全部实际变化均为指定Process导入及必要报告入口、构建/打包/状态/测试维护。5,527个原始数据、只读记忆、冻结输入/结果、科研工作流、Notebook及Experiment相关保护文件逐一保持原字节，并在实际隔离检查前后再核对；另37个goal3/scripts/配置路径中34项原字节不变，只有assignment/identity/package的授权状态或打包metadata维护。五份长期规范正文/版本均未改，科研实现、参数/选择/停止规则未改，无FULL/LIVE运行，无新依赖/字体/全局配置安装。

已实际读取最终REVIEW_PACKET、EVIDENCE_ACCEPTANCE_HANDOFF、accepted-source、assignment及教师manifest。上轮GPT二审MD与原证据ZIP在本轮prior_review归档中逐字节与源包原件相等，结论只绑定9d91392。40组继承台账保留真实来源与历史身份，E09/E19明确为用户UI转交执行回报；没有无记录的历史Lock补签，也没有将本轮作者检查、工程执行、独立内部检查、上轮网页审查或未来网页二审互相混称。新PDF逐页用户复核NOT_RECORDED，Understanding仍LEARNING。

教师PPT第26页细则已实际重读：10月5日前把Notebook与报告压缩为ZIP发送至52285903012@stu.ecnu.edu.cn，按学号_姓名_实验一命名；没有具体截止钟点。正式ZIP已准备并真实终检，通过网页最终二审与用户确认后由用户发送，审核者与主线程未发邮件/平台提交。规则及历史归档hash见 [independent_inheritance_and_teacher_rules.json](independent_inheritance_and_teacher_rules.json)。

独立本地范围全部通过；允许主线程继续本轮已授权的正常commit/push及远程字节回读。远程回读回执和网页最后二审分别记录，本文件不将未来动作预记为完成。

## 6. 发布前新增远程回读辅助脚本代码审核

主线程新增包外`verify_remote.py`后，审核者进行了追加的**只读代码审核**，结论PASS，最终脚本hash、具体检查项及初始发现见 [independent_remote_helper_review.json](independent_remote_helper_review.json)。该检查未执行网络fetch或远程blob回读，尚不代表远程发布验收。

脚本每次depth=1 fetch后解析FETCH_HEAD，并以FETCH_HEAD实际读取tree/blob，避免旧浅克隆本地分支未快进的问题；`ls-tree -z`按NUL分隔并UTF-8解码，保留中文路径。Local HEAD、origin/main、直接远程main、独立FETCH_HEAD与显式expected SHA必须全部相等。项目源集合从清单true成员计算，工作源集合来自字节绑定的输入ZIP台账，教师文件夹集合来自实际远程ZIP的manifest；当前15/397/116只是被审冻结版本的实数，不是未来硬编码规则。正式ZIP本身被实际读取并要求与本地已审ZIP同字节，其CRC与全部文件夹blob/ZIP成员逐字节核对。

初版缺少实际no-alternates约束却在回执宣称无alternates，已由审核者指出并由主线程最小补齐：所有Git子进程显式清除6个对象/工作目录环境覆盖变量；fetch前验证bare和准确origin URL，拒绝非空alternates/http-alternates，fetch后再次检查；回执记录对象目录起始存在状态及实际隔离检查。追加仅影响本轮包外远程核验脚本，正式教师ZIP、报告成品及科学代码未变。本文件继续将真正发布/网络回读与未来网页最终二审留给各自后续真实记录。

## 7. 已发布内容的独立实际对象回读

工程内容提交 **`543e2c5deec7dc9d75598c7e1096b334a11a6fab`** 正常发布后，主线程完成从网络向仓库外新bare目录取得对象，并提供真实命令回执。审核者新增执行自己的只读检查，**实际从该对象库FETCH_HEAD读出551个blob**，没有只看主线程PASS摘要；550个对应主线程全部已读产物，另1个是已冻结审核的远程辅助脚本。完整结果、各blob的Git对象OID/字节数/SHA256见 [independent_remote_publication_check.json](independent_remote_publication_check.json)。本项结论PASS，范围绑定上述工程内容SHA。

审核者实际验证bare、准确origin URL、alternates/http-alternates均不存在，所有自己的Git子进程也显式清除6个对象/工作目录环境覆盖变量；独立直接执行`git ls-remote`，Local HEAD、origin/main、直接remote main及该对象库FETCH_HEAD均等于上述SHA。网络fetch由主线程真实执行，新增审核者执行范围是实际对象/远程HEAD读取及精确产物复核，未冒称自己又执行一次网络fetch。

具体blob读取采用`git cat-file --batch`，按返回二进制长度读取并逐对象重新计算Git blob SHA1与SHA256；tree读取采用`ls-tree -r -z`，按NUL解析中文路径及普通blob模式。实际读取新Process权威PDF/ZIP、根目录原件、sources.json、全部15项active/release副本，两件Process严格匹配指定新hash和大小，其他13项hash及metadata继续与固定基线一致，release精确集合无extra。

从**实际远程Process源ZIP**核对CRC及397个普通成员，并将FETCH_HEAD中唯一工作源的完整集合及每成员字节逐一与该ZIP比较，全部精确相同；两份当前阅读PDF的远程blob严格为25页Experiment批准hash及77页Process新批准hash。正式教师ZIP另从远程对象读取并存入审核者仓库外专用目录，23599893 bytes、SHA256仍为c1d0b80313f81e81a6bcd4cc02d06002c442201379ea871c4c338386bde2eb66，实际CRC通过。115个声明成员加manifest=116个ZIP普通文件；远程教师文件夹tree精确集合及全部116个blob与该ZIP成员逐文件字节/大小/hash一致，manifest总字节正确，sent_to_teacher=false。

上述全部550个主线程产物记录又与审核者自己的实际读取结果逐一相等；远程辅助脚本也匹配发布前已审hash d9b4bc0831526b9d6a7037171bd787397e7b3301f28a6f647dc16d125efbc802。工程成品与代码冻结，此后仅允许本任务发布/审核回执追加；后续最终HEAD及其相对内容提交的差异范围另行核对，当前不填造尚未知最终SHA。网页最终二审继续PENDING，教师未发送。
