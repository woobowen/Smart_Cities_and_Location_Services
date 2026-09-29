# 独立 C：非 Process 收尾审核

结论：**NC01–NC07 在本轮授权工程范围内通过**；作者实现未关闭 Issue 为 **0**。NC04 为“结论承接完成、原审核附件尚未入库”，来源明确为 `USER_RELAYED_PRIOR_REVIEW`。NC08 由主线程完成发布与固定远程回读，当前 C 结论不替代网页 GPT 对新提交的审核。

独立执行者：`/root/nonprocess_c`。C 未参与治理导入、清单、同步器、导航、Process 或报告作者修改；仅在本目录写审核证据，并使用唯一私有 fixture `/tmp/sc-lab1-nonprocess-independent-c-7bygwgy_`。基线为 `89371f6597f92f7dac9abf61f6f6b18e29ed76cc`。实物 hash 见 [reviewed-artifacts.json](reviewed-artifacts.json)，机器结论见 [C_FINAL_RESULT.json](C_FINAL_RESULT.json)。

起始工作区记录的status是在创建本任务received目录之后、改动既有active之前捕获；其中本任务自身未跟踪目录不是原有用户工作。C已实读作者追加的阶段说明，原命令输出未改。原有未跟踪用户文件为3个ZIP，保护清单核验均保持。

## NC01–NC07

| ID | 结论 | C 实际核验与依据 |
|---|---|---|
| NC01 | PASS | 第一个命令为 `ls -la`；读取起始工作区、21项release清单、接收与6679项保护清单。五份 received 的大小/hash均与 Prompt 相同；5个ZoneTransfer sidecar的保存字节、base64、hash和mtime与起点一致。 |
| NC02 | PASS | 全文读取 Prompt、起始AGENTS及5份完整received。独立读取Git基线，只有AGENTS变化；received→active→bundle原字节一致，旧四份active的hash和mtime均未变。新版AGENTS保留0—20节、P1—P4、第一人称及Evidence权限，只增加批准的分项收尾/验收承接规则。 |
| NC03 | PASS | 16项精确集合均为普通文件，逐项读取active/bundle并比较实际字节、hash；其他15项清单对象逐字段相同。生成metadata与实际生成器输出完全相同；C实跑真实库只读plan/check，34个目标hash/mtime不变。Skill原ZIP固定hash及6个有效成员通过。作者真实写同步/第二次幂等日志已阅读；C另以3成员fixture独立运行成功写入和幂等。 |
| NC04 | PASS_WITH_DISCLOSED_SOURCE_GAP | 实读external_review三个文件及SYNC-003 packet追加内容；被审SHA、用户转交身份、真实接收时间与未知历史审核时刻分开。旧18项测试、16项依赖恢复及25页编译/像素检查仅记历史摘要，不冒称本轮执行；不伪造缺少的原报告/ZIP。SYNC-003旧packet前文逐字不变。 |
| NC05 | PASS | 全文读当前README、技术交接、Goal3 packet与UI交接。非Process可单独关闭；Process仍为指定另一对话的必需交付，完整包REVIEW_ONLY/NOT_READY，Understanding保持LEARNING，当前新提交外审PENDING，CRS未知/无噪声真值等限制保留。345条本地/仓库Markdown链接的目标路径存在。 |
| NC06 | PASS | 独立读取保护清单中全部普通文件；6663个对象保持起始状态，11项授权工程文件变化，5项sidecar仅迁移。批准PDF和源ZIP固定hash匹配，当前PDF与批准PDF完全相同。数值/数据/Notebook/Process/Evidence/教师材料/用户文件及隔离TeX依赖未出现越界变化。 |
| NC07 | PASS | 真实独立上下文完成全文范围审读、实际字节核验及独立正反例。缺源/错hash/未知extra各自的plan/write/check均退出1且不覆盖已有目标；成功fixture的check与第二次sync保持全部文件hash/mtime和成员集合。未发现需作者修复的新Issue。 |

## 实際运行与来源区别

[independent-probes.json](independent-probes.json)记录4组独立fixture、16次同步器CLI命令的完整cwd、argv、退出码、stdout/stderr。缺源、错hash和未知extra均在已有旧目标、有效新源尚待同步的状态下测试，避免只测试空目录的弱反例。临时目录目前保留，不进入真实release。

[independent-verification.json](independent-verification.json)记录五输入、16成员、清单对象、只读真实plan/check、AST、保护、报告原件、历史保留及345个链接目标。同步器除 `instructions_text` 外的整个AST与基线相同；该函数只调整当前UI交接路由和历史适用范围，安全逻辑未改。真实库未由C调用写同步。

作者本轮19项既有同步专项测试及真实plan/write/check/第二次write/check的日志已阅读，仍归作者检查；C未将其冒称自己重新执行。C没有执行旧18项网页GPT测试、旧16项依赖恢复、报告编译、PDF渲染、ZIP重建、Notebook/FULL、模型实验或新数值实验。

C的独立验证辅助脚本有两次自身断言错误，均保留真实失败结果：
1. [attempt-1](independent-verification-attempt-1.json)：误假设起始symlink记录含target字段；实际清单只有type/size/mtime。修正为核对现有类型和lstat、记录当前target，不声称不存在的逐字target基线。
2. [attempt-2](independent-verification-attempt-2.json)：误把获准替换的旧“当前导航”前缀纳入冻结历史。独立git diff确认仅前缀更新，改为从 `Parent Goal：` 起逐字比较真实历史正文。

修正仅发生在C自己的检查脚本；最终重新执行退出0，全部检查通过。作者实现没有因这些检查工具问题发生修改，不能把它们记作作者修复或研究失败。初期过渡扫描的 `exists()` 对dangling symlink局限也已在 [INTAKE_REVIEW](INTAKE_REVIEW.md)保留。

## 核验边界

保护清单含6,678个普通文件和1个既有测试symlink。普通文件比较实际内容hash、size及mtime；symlink核对类型、size、mtime并记录当前目标，但起始清单没有目标原文，不能宣称目标字节与起点精确比较。该对象是旧同步器测试fixture，不是报告/数据/上传成员。5个 `.venv/texmf` 文件保持；C新增系统包、语言包、工具链、字体、配置均为0，未清理依赖或用户文件。

Goal3 packet历史区、TECHNICAL_HANDOFF自 `Parent Goal：` 起历史正文与Git基线逐字一致；SYNC-003 packet仅追加。旧PENDING不批量改写，新提交仍需网页GPT核查。C只检查了本地/仓库链接目标路径存在；正式网页远程字节回读属于NC08，不计入本次C检查。

报告原件保护通过不等于本轮重新编译、绘图或实验复算。用户文稿验收、旧网页二审承接、当前内部C、Evidence Lock、Understanding、UI上传及教师提交状态不互相代替。原二审报告/ZIP未入库这一来源缺口保持公开，按Prompt §5/§10不阻断本轮NC04承接。

本轮任务packet/验收矩阵/最终发布事实可在C后补充状态；这不构成对后续文本或尚未发生发布的预先通过。若治理源、同步器、清单、当前技术入口或已审历史归档实物再次改变，应按影响范围复验。
