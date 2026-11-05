# R-001 时间偏移异常审核与机制检查建议

状态：已复现，未热改共享数据或正在运行的实验。

1. 先按teacher cell3对矩形内记录按user/local排序，再按同日、local gap10–180分钟、Manhattan≥1km配对，复现 **25550** proxy trips。
2. 使用来源行号重新取两端UTC，独立计算真实elapsed。12对的UTC elapsed与local gap不同；其中6对UTC elapsed<0，全部12对的UTC gap均不满足10–180分钟。
3. 12/25550 = 0.04697%。其中11对在train_inner、1对在validation（2012-10-28），test为0。异常不仅涉及常规DST；有-240↔540的780分钟变化及-240→120等。
4. 完整差异见 `time_offset_anomalies.csv`。该文件包含原始来源行号，可回到未改CSV核验，不将签到行号视作新司机/订单真实ID。

解释：local是每条记录UTC加其offset的civil-clock值，不能假设一个用户的所有记录offset相同。按local排序可产生相对于UTC倒序的代理边。教学模型仍能作为有明确输入的仿真运行，但不能据此声称这些边是真实相邻出行或确认实际耗时。

建议的批准范围内单因素robustness：保持原teacher25550主基线及同一seed/算法/评价，另建副本仅剔除这12对，不重排序、不改offset、不静默重建整套数据。以train_inner训练/validation评价比较KM、Q-KM（固定β=.5）及已确定单项；未来test不用于选择。报告实际订单池差异与指标，不因小占比而未经实测宣称影响可忽略。若需统一纽约标准时区并重新按UTC排序构造trip，则会改变关键数据语义，应另行研究确认，本轮不擅自执行。

原始.csv、派生teacher trips和分区均未因此覆盖；当前共享数据身份仍为teacher local-clock proxy。
