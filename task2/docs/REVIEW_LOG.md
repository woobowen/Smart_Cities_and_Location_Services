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

- Process已经制作正文、技术图与可交接素材；尚无本轮原生ChatGPT UI截图、Evidence Master批准的箭头/phrase规格和Lock，相关真实证据页面由外部接续。
- 数据仍无额外公开再分发授权，逐条原件与可反解派生留本地；这不减少本地研究范围。原作者公开获取及输入精确重建已经实测，跨任意环境随机实验二进制一致未宣称。
- 结果来自签到OD教学代理、条件局部坐标、模拟司机和模拟日。收入是派单接受的proxy currency；不是真实营收、真实净利润或平台效果证明。
- 远程读取核对和固定commit审核包验证属于交付一致性；网页GPT独立审查与用户最终理解验收尚待本次交付之后。
