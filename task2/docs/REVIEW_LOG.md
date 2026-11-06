# 内部审核与修复记录

本文件汇总实际检查范围；完整机器回执、原被审哈希与旧结论保留在各 evidence 目录。内部通过不等于网页GPT二审、用户验收、教师提交或Evidence Master Lock。

|检查者与对象|真实检查与发现|修复及适用范围|
|---|---|---|
|reinforcement 独立检查 root 在线实现|200小矩阵的独立瓶颈可行性/枚举、独立LP；55实例/1045结果/35190匹配逐项重算|服务基数、等待/行驶、可行时序、两类离线目标和实例比通过；见 `../evidence/independent_rl_on_online/`|
|research_data 独立检查 evolution|真实原始genes重新解码、目标和历史HV独立盒并集、150小图枚举、基础MILP、九批输入来源|发现遗漏初始化成本及KM Spacing使用非规范前沿；补计41次KM及目标求和，所有方法共同10小数去重/非支配后重新评价，保留8/10/12敏感性；见 `../evidence/independent_research_on_evolution/`|
|evolution 独立检查 reinforcement|375条原始rollout自行重建事件；完整LT与Double手算、真实edge与最优匹配核对；静态和动态融合、成对差与t区间|物理忙闲、等待/取消、接驾/送客/主动移动、收益与选择按定义执行；见 `../evidence/independent_ea_on_rl/`|
|reinforcement作者与evolution独立复核|Double分支随机更新与行为共享RNG，原比较随机流不公平|分离RNG并使旧Double无效，重新300回合训练受影响模型；Q-only数组逐项bit一致可继承，原identity保留；见 `../evidence/rl/history_rngfix/`|
|research_data / reinforcement 数据入口|原TSV转换坐标末位差异；来源身份不能由相同hash推定|Decimal直接10有效位half-up、UTF8与末行规则得到两CSV精确SHA；实际新网络下载；孤立目录验证8份DataFrame、fallback、坏receipt拒绝与teacher优先|
|reinforcement 独立公开内容审查|匿名membership与总fare能满秩反解56笔个体fare|原始结果保持本地，另产无genes/pairs/context的聚合投影；124绑定、1024816数值叶精确一致；见 `../evidence/independent_package/`|
|reinforcement 实际暂存blob追加审查|原清单漏列KM计时复算的41项真实pairs/F绑定|原件取消暂存并精确排除；清单1497项，公共规范指标已保留该计时总量/求解数/hash，不删技术证据、不重画图|
|root Notebook执行与reinforcement独立核对|旧Matplotlib与IPython backend API冲突、旧mpl_toolkits namespace冲突|仅项目venv升级Matplotlib与修复namespace；基础第三次、进阶第二次fresh Kernel执行返回0，无error输出，原教师测试保留|
|root报告作者与research_data独立全文/实际页面核对|图注样本单位、动态/静态预算、ECDF黑色discard曲线说明不足|真实LaTeX/图源修正；10表320数字独立核对；26+8页200dpi逐页检查，末轮只变3页并追加复核|
|root误触发评估与evolution独立追加检查|不解析参数的旧入口忽略`--help`，固定测试评估发生REPLAY，部分旧逐日runtime字节被覆盖|不重训、不改选择；95 trace/episode哈希相同，科学汇总/成对差/1060融合帧选择一致；旧4份day metrics完整runtime字节不可恢复，明确记录，不伪造旧文件。增加真正CLI与拒覆盖；见 `../evidence/rl/replay_recovery/`、`../evidence/independent_ea_on_rl/replay_review/`|

最新CLI、源包隔离编译、最终Git集合与PDF的具体回执由 `../review/VERIFICATION_PACKET.md` 索引。历史哈希的审核不冒称覆盖后续任何源码；只在新检查明确确认一致的科学字段上继承旧覆盖。

收尾工程回归：当前47个Python实现/脚本通过语法编译；全测试90项通过。CLI作者专项与独立复验另记，包含directfile/`-m`、无site-packages帮助、既存目录/悬空符号链接拒写与只读load_model/绘图导入；没有为验证help重跑训练或评估。保存的原始CSV、用户Prompt及日志含原CRLF/进度空格，保留真实字节；源码/文档/LaTeX的Git whitespace检查通过，不为格式检查修改历史产物hash。

## 外部边界

- 原研究交付时 Process 仅有 8 页正文与技术素材，原生 UI 当时未提供。2026-11-06 的[追加接管](../review/PROCESS_REPORT_SYNC_20261106.md)已安装用户认可的 16 页 PDF、原生截图和 TikZ 源；旧检查保留历史，不新增 Evidence Lock。
- 数据仍无额外公开再分发授权，逐条原件与可反解派生留本地；这不减少本地研究范围。原作者公开获取及输入精确重建已经实测，跨任意环境随机实验二进制一致未宣称。
- 结果来自签到OD教学代理、条件局部坐标、模拟司机和模拟日。收入是派单接受的proxy currency；不是真实营收、真实净利润或平台效果证明。
- 远程读取核对和固定commit审核包验证属于交付一致性；网页GPT独立审查与用户最终理解验收尚待本次交付之后。

## 2026-11-06 文档同步追加核验（已被新成员方案承接）

本轮没有研究运行或模型重训。集成线程核验入站 ZIP/指定 PDF SHA、安全解压及 18 个裁片的矩形逐像素复现，安装 11 个 `.tex`（仅 3 处路径适配），实际查看正式 PDF 全部 16 页 200 dpi 渲染。独立 `process_integration_verifier` 检查了冻结成果、源/PDF 嵌图对应、PNG metadata 与构建/打包保护；[完整独立范围](../evidence/process_report_sync_20261106/independent_review/REVIEW.md)。

隔离编译返回 0、16 页、全文相同，但自动字重从 Black 修复为获批 Bold 后仍有 13 页像素差异；严格完整验证未通过，失败回执保留，正式 PDF 未被覆盖。Project Sources 从 15 项仅增一份实验二 PDF 至 16 项；现有 `--plan`、写同步、`--check` 与全成员字节/SHA 检查通过。UI 上传和 GPT 外部二审分别等待实际操作。

## 2026-11-06 规范升级与 12 项成员精简

用户最新批准范围由 [SC-PROJECT-REFRESH-20261106](../../evidence/infrastructure/SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md)承接：完整替换四份规范，Research v1.3 保持原字节；五份历史/重复材料退出分发集合且权威原件保留，任务二 26 页 Experiment 和 16 页 Process 纳入唯一有效规范名。当前为 20 条登记、12 项 active、8 项 false，`--check` 与逐成员字节/SHA 检查通过，37 项现有同步器安全回归通过。旧 16 项方案、随后出现的下载元数据阻塞及原始回执保留历史身份；经用户明确授权移出的元数据和获批分发副本均在仓库外保留备份。没有新实验、训练、报告改写或再次编译；上述 Process 渲染差异继续有效。UI 操作、固定提交远程回读、GPT 外审分别登记。
