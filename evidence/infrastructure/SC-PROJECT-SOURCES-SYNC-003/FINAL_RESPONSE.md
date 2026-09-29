# SC-PROJECT-SOURCES-SYNC-003 · 最终交付说明

唯一审阅入口：[REVIEW_PACKET.md](REVIEW_PACKET.md)。本文件记录本次一次性治理与报告源同步，不重新评判实验一效果。

## A. 状态与已完成范围

SYNC-01—13 已完成真实实现、测试和独立 C 审核，未关闭工程 Issue 为 0。五份治理文件、已验收25页 Experiment 的原件/源码/生成器、动态分发清单、当前导航与具名审阅包已同步。SYNC-14 在此初始记录时尚待实际发布回读，不能用本地审核代替。

| 状态 | 当前结论 |
|---|---|
| REPOSITORY_SYNC | PENDING_PUBLICATION |
| UPLOAD_BUNDLE | READY，批准清单推导16个普通文件 |
| EXPERIMENT_REPORT_INTEGRATION | VERIFIED，本轮报告编译与实际验证范围 |
| PROCESS_REFERENCE_REPRODUCTION | PARTIAL，沿用既有复现限制 |
| UI_SCOPE_UPDATE | USER_ACTION_PENDING |
| GPT_SECOND_REVIEW | PENDING |
| 实验一Submission | NOT_READY |

## B. 项目规则与实验实例边界

| 项目通用规则 | 主要落点 |
|---|---|
| P1 正式研究默认交付 Experiment / Process 双报告 | Writing Guide §1 |
| P2 真实多角色职责与持续工程修复闭环 | Research §C；AGENTS工程执行与审核条款 |
| P3 Process继承真实共同基础、记录本次新增演化；Evidence Master由用户指定 | Writing Guide §12；Evidence §4.1 |
| P4 正式工作流/架构图交付可编辑draw.io及SVG/PDF | Visual §13 |

其他规范通过引用衔接，保留 W01—W22、P2、原话归属、第一人称、最小框选、箭头、PPI 和 Lock。实验一算法、参数、四模式、25页、特定图型和未知datum下的条件授权仍限定在批准任务；不成为后续实验自动输入。完整理由和diff见[范围审核](governance/SCOPE_REVIEW.md)及[逐文件变更](governance/DOCUMENT_CHANGES.md)。

## C. 输入、权威源与安全分发

7份核心输入先保存至 `received/`，全部size/SHA256匹配。5份Markdown以完整底稿导入对应active规范；Experiment PDF/ZIP原字节进入 `reports/experiment-report/experiment1-reconstructed/`；bundle由active分发。唯一成员定义为[sources.json](../chatgpt-project-source-sync/sources.json)，最终路径、角色、版本、配对和hash见[原manifest](../chatgpt-project-source-sync/SOURCE_MANIFEST.md)。

本次批准集合为16个普通文件，程序使用清单长度与集合，不写死永久数量。7个Windows下载元数据原字节、hash和mtime保留后移出bundle；没有删除有效文件。旧同步器在原路径迁移为全输入预检、拒绝未批准extra/路径异常、暂存与原子替换、失败回滚、只读`--check`、无变化不改mtime。原Skill ZIP固定hash及6个installed effective members独立核验，未重打包。

## D. 两份报告、构建与审阅包

批准 Experiment PDF SHA256 为 `2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0`；源ZIP为 `6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd`。两原件保持不变。72成员ZIP通过CRC、路径、重复成员、字体和秘密检查；可编辑章节、两幅真实draw.io及SVG/PDF导入 `task1/reports/experiment1/`，公共P2仅作必要路由适配。

`build_reports.py`及`python -m task1.goal3 REPORT_BUILD`已接入真实25页源码；干净目录移除预带PDF后实际XeLaTeX构建，正常入口连续两次构建均为25页，没有恢复旧22页稿。批准PDF与重建PDF不宣称字节/像素相同：全文相同，作者实际查看两版各25张200dpi全页，C独立干净编译并抽查6页两版；两次正常构建的全页图均与作者实际查看的重建图绑定。

当前具名包为 `task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip`，SHA256 `231ce92475fdfe7ed12fa1c7e3304c22d6fd56ce39a0b53b43fee87103334a63`。116成员逐项核验；与旧当前包及旧实际FULL执行包均112项相同，4项变化是manifest、README、报告入口文件和Experiment PDF。冻结数值源、FULL/LIVE函数身份与变化CLI的隔离回归分别验证，不笼统声称所有runtime字节不变。

新包manifest.metadata完整继承旧实际FULL包，其中旧`report_revision_date`和默认`review_package_name`属于历史身份来源；当前Experiment日期为2026-09-29，实际归档名/hash以本次回执为准。没有为元信息解释而改冻结配置或Process。

前期Process PDF/ZIP、task1 Process待审稿和合成模板保持原字节。保留[原SOURCE_ARCHIVE_BUILD=PARTIAL记录](../SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md)：31页源不能完全复现REVISED文字/标注且存在已知缺字。本次未制作新Process Evidence、未更改截图/箭头、未重新Lock，未声称图全部重画或全实验复算。

## E. 实测、独立审核与修复

- 同步器19项专项测试通过；C另做13类独立异常/回滚/动态扩展探针。
- 报告集成17项测试及10个subtests通过；真实干净编译、两次正常入口、25页两版目视和C独立构建通过。
- C对新包做CRC/116成员hash、7项隔离CLI/门禁检查及32项数值源身份验证；没有新增FULL运行。
- 起始5982项保护核验：5943原件不变、32项授权修改、7项OS元数据保留迁移，无范围外改动。当前24份Markdown的422个本地路径/anchor检查通过。
- C-001为AGENTS Revision在manifest中的标签不精确，已最小修复并由C复验关闭。缺少placeins/needspace导致首次干净编译失败，隔离补齐后真实重建通过；初期不适当的逐像素相等判据已改为明确的文字/布局比较并保留差异。C包检查脚本自身首次误假设可选字段，修正及真实失败记录均保留。

[C最终审核](c_review/C_REVIEW.md)为 `INTERNAL_C_VERIFIED_FOR_REVIEWED_ARTIFACTS`，独立于作者自检；不代表网页GPT最终验收。本轮记录级实验模型调用为0，新数值实验为0；历史结果和数值 `CODE_SHA=e12f8a27944210adb452730be92a0674dfc6b84b` 保持原身份。

新依赖仅 `.venv/texmf` 中placeins 2.2、needspace 1.3e；无系统包、Python包、字体、全局配置变更。[安装/核验记录](report/environment-changes.json)包含包元信息、sty hash与实际查找；原安装stdout未独立落盘的限制如实保留。是否保留这两个隔离TeX包由用户决定；一次性任务可以清理，本次未主动清理。

## F. 文件版本、hash与UI差异

主要新增：Writing Guide、唯一sources.json、批准Experiment canonical pair、可编辑章节/绘图源、回归测试、新审阅ZIP和本任务evidence。主要修改：五规范、原同步器/验证器/manifest、报告构建入口及当前导航。没有删除有效项目文件，详细清单见[发布扫描](publication-audit.json)。

用户后续只需替换这5个Project Sources：

| 文件 | 最终版本 |
|---|---|
| SMART_CITIES_RESEARCH_PROTOCOL.md | v1.2 |
| SMART_CITIES_REPORT_WRITING_GUIDE.md | v1.1 |
| SMART_CITIES_VISUAL_SYSTEM.md | v2.5 |
| WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md | v2.6 |
| AGENTS.md | 2026-09-29 · Project-wide P1–P4 scope / manifest-driven source distribution |

其余11项字节未变，无需重复上传。16项前后hash见[UI_SOURCE_DIFF.md](handoff/UI_SOURCE_DIFF.md)，最终hash见[manifest](../chatgpt-project-source-sync/SOURCE_MANIFEST.md)。[PROJECT_SETTINGS_SCOPE_PATCH.md](handoff/PROJECT_SETTINGS_SCOPE_PATCH.md)仅提供总适用范围/角色、正式报告、Evidence三处短补丁，是TRANSFER_COPY，不是第二份active设置。

## G. Git与发布

Repository：`https://github.com/woobowen/Smart_Cities_and_Location_Services.git`；Branch：`main`。起始本地HEAD、origin/main与实际远程均为 `4483f520eabb5358d1f35cf5c33a81d3b01e47e0`。此记录写入时尚待artifact commit、push和固定提交HTTPS字节回读；发布后在本节与独立发布记录补充真实结果，不预先宣称。

根目录原有3个用户ZIP保持原字节、原未跟踪身份：`Experiment_Report_完整重构_源文件.zip`、`SC-LAB1-G1-CLOSURE-002_HANDOFF.zip`、`SC-LAB1-G1-COMPLETE-001_HANDOFF.zip`。本次只提交授权工程与证据，不覆盖用户输入。

## H. 外部验收边界

等待网页GPT读取发布后的固定GitHub版本二审。未替用户操作ChatGPT UI、未完成新增Evidence Lock、未代发教师、未代用户确认Understanding或Submission通过；实验一Submission仍为NOT_READY。仓库工程交付与上述后续动作分开记录，不返回下一份同步Prompt。
