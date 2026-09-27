# SC-LAB1-G3-FINAL-001 本轮结果

本轮研究、全量生产和全部可自主完成的交付工程已通过独立总验收，产物已实际推送 `main` 并从 GitHub 回读核验。总状态为 **PARTIAL_BLOCKED**：可信姓名/学号及 Evidence Master 输入仍缺失，不能直接向教师提交，也不是实验一最终 PASS。本文记录已经发生的 ARTIFACT 发布；最终记录提交的 HEAD 由最后聊天回复给出，避免 Git 自引用。

## A. 范围与状态

本轮按用户批准的一次性范围，承接已验收 G2，完成有限候选、父项/组合/移除比较、选择、一次性最终确认及全量生产。仍属于实验一。当前 Technical 数值处理、完整交付复算和 Handoff 为 `VERIFIED`；Research 为范围内支持 S0 的覆盖改善；Reports 可用工程 `VERIFIED`、外部项 `BLOCKED_EXTERNAL`；Package 工程已独立 VERIFIED，整体仅因身份/Evidence 输入保持 BLOCKED_EXTERNAL / REVIEW_ONLY；Publication 的 ARTIFACT 已实际发布并核对远程；独立发布回执以 goal_state 中真实记录为准。`GPT_SECOND_REVIEW=PENDING`，不代替外部最终验收。

可信姓名/学号及 Evidence Master 的真实原图、呈现规格和 LOCK 未提供，登记于 [teacher_mapping.json](teacher_mapping.json)。缺项只阻断身份填写、对应互动页面、正式 Process Report 和可直接提交状态；其余必需工作继续。

## B. 最终方案

统一确定性 S-D-P，参数为 `dt=30、distance=400、min_points=2、min_length=0、direction=35、dp=5`，即 S0。教学参考 R0 的过滤参数为 `5/65`，其余相同。记录处理不调用 LLM、不搜索、不读记忆，不含逐记录回退；最终确认不支持时采用 R0 的发布门控在开集前已冻结，本轮未触发。

D 沿用一次计算完整标记、同时删除、不可计算窗口保留、下游重算的授权。P 使用有限线段距离，发布即时误差预算 5 工作米。`source_crs=UNVERIFIED`，采用固定椭球、h=0 与 ENU 工作坐标，不能把公式一致性当作源 datum 认证。

## C. 候选与实际循环

开发集 240 条已暴露记录上实际复验 R0/S0、过滤父项、方向和 P 参数；新增 1 个结构单项及 3 个组合定义，没有耗尽配额或无限搜索。S0 相对 R0 有 107 条覆盖严格改善、增加 6,704 点。时间条件方向规则 G0 单独有局部几何价值；组合 S0_G0 后来相对 S0 全部保护并有 41 条几何改善，确实曾成为开发 incumbent，移除任一父组件均有损失。

冻结短名单的 240 条选择记录中，S0 全部保护、103 条覆盖改善、增加 6,625 点；G0 和 S0_G0 在 `3017、9311、9534` 三条记录退化。独立重算确认这是 D 输出变化影响后续 DP 选点的真实权衡，因此未采用组合。没有预先指定 S0 必胜。

P2 与 S0_P2 在相同上游下分别增加 1,946/2,010 个存储点，无压缩收益且有共同几何保护失败；P10/S0_P10 分别有 173/178 条超过共同 5 工作米预算。第二种轻量删除保护因缺乏合理独立定义未准入；危险顺序没有新机制依据，未重复全面六排列。A 的[实际收敛复盘](CONVERGENCE_REVIEW.md) 与 C 覆盖检查支持停止探索，而不是要求每轮必须获胜。

## D. 最终确认

最终冻结时间为 `2026-09-27T05:23:51.350095+00:00`，冻结 SHA256 为 `d64869cc4623b3751d365d54d2cc70305a188891c41b8c6de17b58f3fadb1e6e`。冻结后对 600 条完整记录、62,284 点真实运行 R0/S0，共 1,200 次处理；没有根据最终效果调参。

S0 在 600 条记录上全部保护通过，349 条覆盖严格改善。共同覆盖 `35,868→62,220`，显式存储点 `10,991→12,114`，无输出记录 `255→0`。345 条几何可比较、255 条因参考无覆盖不可比较，未把 null 算成改善。两者即时 P 最大误差均为 `4.997131` 工作米，新增覆盖点最大几何偏差 `6.087102` 工作米。有限记录样本不代表独立用户或普遍清洗准确率。

## E. 全量结果

全部原始输入实测 **11,386 条记录、1,173,410 点**。R0/S0 共 22,772 次真实处理，每个原始点有终态；0 处理失败、0 未处理记录、0 逐记录回退、0 新增记录级模型调用。

| 全量读数 | R0 | S0 |
|---|---:|---:|
| S 过滤 | 501,511 | 1,199 |
| D 删除 | 36,056 | 39,732 |
| P 精简 | 435,373 | 911,330 |
| 显式保留 | 200,470 | 221,149 |
| 共同原始覆盖 | 671,899 | 1,172,211 |
| 无输出记录 | 4,859 | 0 |

前四项每列合计 1,173,410。11,386 条全部保护通过，6,522 条严格覆盖改善；共同覆盖增加 500,312，存储增加 20,679。这是包含所有开发分区的数据集生产描述，不是第二个独立测试。

新增覆盖的过滤原因互斥分解为：仅长度不足 492,513、仅点数不足 5,434、两者同时 2,365。最差新增覆盖点 record 352 / index 105 偏差 **266.016754 工作米**，来自原四点窗口经 D 删除该点；该局部 P 没有再删点。报告保留这一限制，不把新增覆盖说成噪声已正确识别。

全量工作坐标程序覆盖全部点、1,162,024 条原始相邻边和所有实际阶段；独立 C 又核全部点、范围和计数，并对随机/类别/极值合并的 56 条记录、112 份轨迹独立重算敏感性。未发现固定实际输入上的阈值/保留集合差异；这不等于 AEQD 整链重跑，也不证明源 CRS。

## F. 系统、修复与成本

A、B、C 由真实原生子任务和主线程承担；确定性控制器管理依赖、预算、哈希、修复、失效与恢复。A 在冻结前提出并消费真实开发证据，最终反馈不回流 A。C 从原始范围与实际分片核验，不只阅读 B 的摘要。

C01—C08 的实现/来源/缓存/审核门控问题、文档结构与参数呈现问题、REPORT_BUILD 缺打包问题均在同一 Goal 内修复。最终 Notebook 实跑又暴露绘图依赖接口不兼容：第一次修复被 C 拒绝，第二次用原生 Figure/Canvas 通过独立新内核专项核验后再跑 FULL。图例、文字容纳及真实开发反馈路径也经独立复验。失败及明确中断记录保留，不冒充研究负结果或成功运行。

最终有效源码工作测试 **469 passed + 10 subtests passed**，0 失败/跳过；JUnit suite 总数 479、实际 testcase 节点 469。测试数量不是实验量。全量数值主审覆盖全部 22,772 份处理轨迹；另一数学实现覆盖 50 条随机/类别记录、100 份轨迹，未声称所有记录都做第二次数学重算。

记录级模型调用与治理分账。本轮没有新增记录级 LIVE 或重跑历史 84 次模型调用。治理工具记录是真实可得元数据，加密正文仅保留载荷哈希，不补造对话；底层请求及费用为 unknown。没有新增系统包、语言包、工具链或持久配置。

## G. 正式交付

- [基础完成版 Notebook](../../notebooks/final/作业1轨迹数据预处理_完成版.ipynb)、[系统完成版 Notebook](../../notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb)：仓库新内核 FULL 均已独立 VERIFIED，12/12 与 8/8 单元。历史 raw 候选处理 9,720+6,001 次、384 个历史 episode 选择、22,772 次全量生产、19 条构造和 1 条已暴露 pilot；Provider attempts=0。执行版原字节已推广正式路径。
- [Experiment Report 源/PDF](../../reports/experiment1/) 与 [Process Report 源/PDF](../../reports/process1/)：21/12 页，全篇和全部 33 页 200 dpi 实际目视完成；实际 REPORT_BUILD 后另行重渲染逐页字节一致，当前源与 PDF 已精确复绑。两者工程 VERIFIED，身份及 Process 真实互动呈现仍为外部缺项。
- [七张正式图及可编辑源](../../figures/goal3/)、[图源程序](../../goal3/figures.py)：当前 31 个目标、13 个来源已独立 VERIFIED 并由控制器关闭。
- [Technical Handoff](../../docs/goal3/TECHNICAL_HANDOFF.md)、[Interaction Handoff](../../docs/goal3/INTERACTION_HANDOFF.md)、[答辩说明](../../docs/goal3/DEFENSE_NOTES.md)：互动索引保留真实触发和 NOT_AVAILABLE，不代替 Evidence Master 或用户 Understanding。[独立 Handoff 闭合](independent_documents/handoffs_current_closure.json) 核验 6 个目标、111 个来源。
- [实际 REVIEW_ONLY ZIP](../../submission/REVIEW_ONLY_实验一.zip) 已由统一入口真实生成：21,418,989 字节、113 个成员（含 manifest），SHA256 `97d5dbe2d7a5c87d09bcb21ae5798fa0b76374fabdd03f25447fb87c4f27c447`。静态闭包、CRC/全部字节、独立解压与模块边界已验；包内两个 FULL 已独立通过：基础本 12/12、2,811.70 秒，系统本 8/8、534.86 秒；新分片与正式结果一致，独立核验全部 285 分片、任务模块边界和 Provider attempts=0。不是仅以静态依赖检查替代真实运行。[包工程父任务](independent_c/package_closure_receipt.json) 已按 213 个目标、45 个来源独立闭合，只保留外部缺项。

## H. 验收与发布

[G3-A01—A20](requirements.json) 是唯一逐项登记；[REVIEW_PACKET](REVIEW_PACKET.md) 是当前入口。[全量独立闭合](independent_c/production_closure_receipt.json) 绑定 313 个实际目标、37 个源码依赖，四次 FULL、图、两报告可用工程、两个 Handoff 和包工程也已分别独立闭合。[最终内部总验收](independent_c/internal_acceptance_receipt.json) 实际核对 15 个前置任务、1,131 个目标和 222 个源码依赖，全部工程问题已关闭；随后已实际完成产物推送与远程核对。G3-A01—A14、A17、A19、A20 为 PASS；A15、A16、A18 因明确外部缺项为 BLOCKED，可完成工程分别 VERIFIED。未将缺项改成 N/A。

数值 CODE_SHA 为 `e12f8a27944210adb452730be92a0674dfc6b84b`。仓库 Notebook 实际执行代码为 `0b20be8`，32 个数值源码与正式生产相同；报告源码提交为 `cb4f211`，没有改写原数值运行身份。ARTIFACT_SHA 为 `fd559e451291b9d424682853ef0909aa5eb94b32`，已实际推送至 `https://github.com/woobowen/Smart_Cities_and_Location_Services.git` 的 `main`。发布时 Local HEAD、origin/main 与实际 Remote SHA 均为该值；固定 SHA 回读的 8 个关键文件全部 HTTP 200、哈希匹配。[发布记录](PUBLICATION_RECORD.json) 只登记已经发生的核对；最终包含本记录的 HEAD 由最后聊天回复报告。

固定产物链接：[Experiment Report](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/fd559e451291b9d424682853ef0909aa5eb94b32/task1/reports/experiment1/experiment1.pdf)、[Process Report 送审稿](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/fd559e451291b9d424682853ef0909aa5eb94b32/task1/reports/process1/process1.pdf)、[完整结果摘要](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/fd559e451291b9d424682853ef0909aa5eb94b32/task1/evidence/goal3/result_summary.json)、[审阅入口的 ARTIFACT 快照](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/fd559e451291b9d424682853ef0909aa5eb94b32/task1/evidence/goal3/REVIEW_PACKET.md)。最后一个快照保留形成时的发布待办；本目录当前 REVIEW_PACKET 和最终聊天链接指向随后真实完成的发布记录。

本轮新增/修改集中于主 README、task1/goal3 与 config/goal3、tests、docs/goal3、evidence/goal3、notebooks/final、figures/goal3、两报告工程及 submission；完整路径和内容可从提交 diff 与独立清单核查，没有删除有效文件。原有两份未跟踪 Handoff ZIP 保持未跟踪，三份既有 ZIP 字节未变；未覆盖用户未提交工作，未 force push 或改旧历史。报告源、完整结果、失败证据和原有有效工程保留在 GitHub 工程范围，教师包单独取必要闭包。

## I. 最终边界

全部可自主完成的稳定工程已通过独立总验收并实际发布。可信身份与 Evidence Master 原始材料、批准呈现规格/LOCK 仍缺失，因此总状态保持 `PARTIAL_BLOCKED`，不能称作完整可提交成果。网页 GPT 二重审核保持 PENDING，Evidence LOCK、用户 Understanding 和最终提交确认均由对应真实角色完成。

离线复算命令为 `.venv/bin/python -m task1.goal3 FULL_RECOMPUTE --output <新的结果目录>`；`LIVE` 需显式开启，本轮未新增 LIVE。本轮实际执行了 `.venv/bin/python -m task1.goal3 REPORT_BUILD`（当时目标 ZIP 不存在）以及四次新内核 Notebook；以后重建需 `REPORT_BUILD --output <新的REVIEW_ONLY_*.zip路径>`，不得覆盖已审核包。完整参数与本轮真实命令见 [README](../../README.md) 和执行回执。`git diff --cached --check` 实际返回 2，独立分类确认 167,289 条告警仅来自可解析 CSV 的 CRLF、原生 SVG、真实补丁及日志格式；原字节和[独立依据](independent_documents/staged_diff_check_receipt.json)保留，没有修改配置掩盖或重写冻结结果。
