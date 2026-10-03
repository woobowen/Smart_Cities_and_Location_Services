# 实验一 Process 接管与项目源同步：GPT 工程二重验收

审阅日期：2026-10-03  
任务：SC-LAB1-PROCESS-INTEGRATION-SYNC-001  
结论：**PASS——本轮工程接管、同步、复现与远程发布范围通过。**

本轮另登记一处已验收 Process 原稿第 76 页的截图裁切问题。该问题不是 Codex 集成引入，不撤销本轮工程验收；建议在最终提交前作局部修正。

## 1. 固定审阅版本

- 仓库：woobowen/Smart_Cities_and_Location_Services；分支 main。
- 开始版本：`6527945ad8e526fa606b2c09835f2e51291fa4d0`。
- 工程内容版本：`e1fb621aa40acc167f4ed84c0c7992a5ff0a4abe`。
- 本轮实际读取的远程 main：`9d91392289b31a4afa5c94cfd3869da9f021b4ad`。
- 从内容提交到最终提交，docs、task1、reports、releases、templates、tools 的 Git 子树均未变化；后续更新限于 evidence 中的回执、交接及验证辅助内容。

此次审阅没有修改用户 WSL、GitHub、ChatGPT 项目源或教师端。

## 2. 独立验证的方式

通过 live GitHub connector 读取固定提交的树、文件、源码与审查记录。对已挂载的批准输入独立计算 SHA256 与 Git blob/tree 指纹，并与远程对象逐项比较；随后使用已证明与远程同字节的 Process 源进行隔离构建。

这不是声称下载了远程二进制。文件/树指纹核验将本地可运行字节绑定到实际远程版本；新的 REVIEW_ONLY ZIP 未在本轮本地解压，只核查了实际远程对象、包内审核清单与有关入口。

## 3. 本轮亲自执行的结果

| 检查 | 结果 |
|---|---|
| 15 项批准输入 SHA256 与远程 Git blob | 全部一致 |
| release 完整文件集合与目录指纹 | `1b43421b57598d25cf625c8da9602c356cce2f4b`，与远程一致 |
| Process 源 ZIP CRC、安全成员与内嵌 PDF 配对 | 通过；内嵌 PDF 与批准单独 PDF 同字节 |
| 343 个源成员对应远程工作源 | 完整一致；仅 compile.sh 在 Git 中赋予可执行权限，内容未变 |
| Process 工作源目录指纹 | `f32af8ab769fcacf216a2ba24fe61926206ab381`，与远程一致 |
| 路线 A：移除预置主 PDF 后执行 compile.sh | 实际成功，77 页，两遍 XeLaTeX |
| 路线 B：make_diagrams → build_report → compile → render_review → audit_report | 实际成功；6 图、77 页、134 个常规窗口、85 个箭头、40 个互动单元 |
| 两条新构建与批准原件 | PDF 字节完全一致；77 页文本、尺寸和 200 dpi 像素对照均一致 |
| 生成内容防回退 | 被检查的 TeX、来源映射及裁片逐字节一致 |
| 新编写的同步器隔离测试 | 16 项通过、0 失败 |

本轮两条独立构建均得到：

`45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83`

它就是批准 PDF 的 SHA256。Codex 原 WSL 构建的 `971f9739…226c2c` 及六页轻微栅格差异属于其真实环境记录，保留原身份；本轮结果不改写该历史。

16 项同步测试覆盖：正常状态、plan/check 只读、重复同步幂等、动态成员、缺来源、错误 hash、未知 extra、同数量错误成员、文件与父目录链接、自引用、路径越界、缺目标恢复、异常目录、过期元数据以及第二次替换故障后的回滚。测试只写临时夹具。受测源码 Git blob 为 `6ee634db93f1860e66c26df735aa810f09c949f4`，已经核对为远程实际源码。

## 4. 科学成果与已验收文稿保护

从开始版本到最终版本，以下完整 Git 子树保持一致：

- task1/workflow、task1/results、task1/scripts；
- task1/notebooks、task1/figures、task1/作业；
- task1/reports/experiment1、tools。

因此本轮对这些范围的保护有实际远程依据。没有因 Process 集成改变既有算法、实验输出、Notebook、Experiment 正文图源或原始材料。6071 个文件是 Codex 内部逐文件审查的统计，本轮未将其冒称自己的逐文件重算计数。

四份规则的权威位置与分发副本对应批准版本；Research Protocol 保持既有 v1.2 原字节。当前 manifest 的 project_source=true 集合为批准的 15 项；PreTask 两件和旧 Process 模板保持历史身份。Skill 已解除 release 自引用。

## 5. 构建、依赖与提交包入口

实际阅读了 build_process.py、统一 build_reports.py 的主要保护与分派逻辑、goal3/__main__.py、Process 专用 fontconfig、同步器和当前报告导航。

当前阅读/打包使用批准 PDF，实际编译输出另存。REPORT_BUILD 与 FULL_RECOMPUTE / LIVE 分离，拒绝覆盖已有 ZIP，并要求 REVIEW_ONLY 文件名；因此没有把报告重建变成研究重跑。

远程存在新的 `task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_完整双报告.zip`：23,610,786 字节，Git blob `c149adbd608fc727c177ee38067d594b3d53c697`。远程包审核记录列出 116 个成员，含两个完成版 Notebook、批准的 25 页 Experiment 和 77 页 Process。其本地解压及冻结依赖 probe 属于 Codex 记录，本轮没有重新执行。

报告构建所需局部 Python、宏包和字体依赖应继续保留。不得因任务阶段结束把可复现依赖当缓存删除；本审查附件不包含字体文件。

## 6. DOC-01：第 76 页原有截图裁切

本轮实际查看第 1、3、34、59、76、77 页，并对第 76 页检查原始截图。

- 位置：Process PDF 物理第 76 页，结尾回顾截图。
- 现象：完整用户气泡下方混入 GPT 回答片段，回答左侧被截断，末行只有一部分。
- 原件：`assets/raw/o3dlGVJPTa1.png`，511×2048 像素，完整原图存在。
- 生成位置：`tools/build_report.py` 中 closing_user 裁切。
- 当前像素边界：`(186, 80, 506, 333)`。
- 归因：批准 PDF 与本轮重建均有该问题，属于原稿已有制作问题；没有证据显示是 Codex 集成造成。

建议只调整这一页的真实生成器裁切：回顾页保留完整用户消息，移除误带入的不完整 GPT 回复；确实需要 GPT 回应时另用完整、有语义边界的原文片段。不得擦改 UI 文字，也无需重新截图或重开实验。

本轮仅指出问题，**未实施修订**。后续修订应保持原批准件可追溯，形成新 PDF/源包配对并更新对应引用和文件 hash；只重新检查受影响文档与提交包。

## 7. 审查范围说明

本轮没有逐页人工重审全部 77 页，没有重新运行 Codex 原 37+19 测试、WSL 清理/快照检查或全量轨迹实验，也没有重新解压远程 116 成员 ZIP。已读取这些相应远程记录，但不将执行者记录写成本轮亲自运行。

本轮的独立工程证据是：真实远程对象与代码、两条实际干净构建、全页程序对照、16 项新隔离测试及明确列出的视觉检查。它不是对先前由 GPT 制作的文稿重新宣称一遍独立作者审核。

## 8. 当前进度与下一阶段

- 本轮工程接管/同步/发布：GPT 二重验收 PASS。
- 已有研究与 Experiment 文稿验收：保持，未重开。
- 完整 Process：已制作、用户已验收、源码集成与复现通过；登记 DOC-01 局部成稿修整项。
- Project Sources：本轮分发与用户已上传的批准输入无变化，当前无需重复上传或重贴设置。
- Evidence Lock：沿用真实既有审批范围；最后收口应关联原件、规格、检查和用户成稿验收，不补造历史 Lock。
- Understanding：承接此前真实记录，本次工程审阅不重新评定，也不要求从头学习。
- 整体 Deliverable：FINAL_REVIEW，集中处理明确的文档修整、证据状态记录及正式包终检。
- Submission：NOT_READY；当前是 REVIEW_ONLY 包，尚未执行教师提交。

建议下一阶段合并完成：**第 76 页局部修正 → 必要 Evidence/验收记录收口 → 精确的正式提交包终检**。无需新实验、全篇重写或重新同步全部规则。

教师材料规定在 10 月 5 日前，将 Notebook 与报告压缩为 ZIP 发送至 `52285903012@stu.ecnu.edu.cn`；外层建议名称 `10245102410_吴博闻_实验一.zip`。提交包须使用完成版 Notebook、两份正式 PDF 和必要复现文件，而不是整个仓库或 Project Sources 目录。正式 ZIP 必须按实际生成的那一份重新核查，发送由用户最终确认并执行。

## 9. 远程核验入口

- 仓库固定版本：https://github.com/woobowen/Smart_Cities_and_Location_Services/tree/9d91392289b31a4afa5c94cfd3869da9f021b4ad
- 本轮工程入口：`evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/REVIEW_PACKET.md`
- 内部审查：同目录 `INTERNAL_REVIEW.md`
- 来源清单：`evidence/infrastructure/chatgpt-project-source-sync/sources.json`
- 报告导航：`task1/reports/README.md`

此审查记录仅在本对话交付，尚未写入 GitHub。后续获准收尾时追加归档并绑定本次固定版本，保留旧审阅记录原样。
