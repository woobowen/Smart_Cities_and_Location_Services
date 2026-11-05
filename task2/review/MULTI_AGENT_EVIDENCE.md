# 真实Multi-Agent工作及边界

本轮使用原生collaboration的四个真实上下文：主线程 `/root`、子线程 `/root/research_data`、`/root/evolution`、`/root/reinforcement`。不是把普通函数改名为Agent，也没有用付费模型API模拟额外角色。用户批准的六类职责通过四上下文先后交接承担，最多四个同时活动。

|上下文|实际作者工作|独立审查工作|
|---|---|---|
|root|单一父Goal协调；在线派单、两离线参考；整体合同、Notebook整合、公共图/技术图、双报告、版本交付|作者自检不记独立；协调缺陷闭环，最终集成与远程身份核对|
|research_data|逐页PPT/逐Cell材料、数据来源/时空/分区、精确下载重建|从原genes独立计算EA和HV；基础MILP与来源追溯；320表数字与34页实际PDF检查|
|evolution|NSGA-II/III、DTLZ2、共同指标、KM初始化、真实分阶段实验与MOO图|独立实现RL事件重建、TD/LT/Double与策略核对；REPLAY及CLI专项追加复核|
|reinforcement|Q-KM/Double/移动/融合、300回合训练、控制与消融、RL图|独立在线离线参考与实际结果；数据反解风险、公开投影逐数核对、无原数据重画与源包编译|

具体交接见 [协调记录](../evidence/multi_agent/COORDINATION_LOG.md)，独立实现保存在 `../evidence/independent_*`，各运行源快照和回执绑定输入/模型/代码/产物hash。异步消息中的发现实际推动了修复：初始化成本漏记、非规范KM Spacing、Double随机流、公开membership反解、报告图注、CLI无副作用假设。

实质研究循环由真实读数触发并在同一父Goal继续：在线覆盖/阈值；EA预算→初始化→有限组合→未来输入；beta1→Double→响应代价；移动惩罚→移除LT→五训练seed→冻结确认；融合估计目标→真实动态收益/接驾权衡。每个子Agent结束仅代表其责任范围交接，父线程继续集成和修复。

未实现或未宣称的能力：最终派单程序是确定性/随机数算法，不是每笔订单调用LLM；没有真实出租车平台在线部署；没有自动扮演用户或Evidence Master；没有生成虚构聊天截图；网页GPT外部独立二审与用户理解验收在交付后发生。原生工具会话本身未被伪造成可公开完整聊天导出，仓库记录是有源产物和实际行动回执的工程handoff。
