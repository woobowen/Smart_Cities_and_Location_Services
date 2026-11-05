# 内部交付门槛与外部状态

此表是本轮工程集成结论，逐项证据由实际执行者回执支持；不把作者重复检查称独立，不把发布称为用户理解或教师提交。Gate8的真实SHA/ZIP身份在发布后从Git对象冻结，见交付审核包根目录FIXED_COMMIT.json。

|门槛|内部结论与证据|
|---|---|
|1 教师完整性|39页PPT/59Cells完整审读，基础TODO1–5/finalize与两个思考点、PartA/B及进阶九道思考题、全部加分映射到代码/测试/实验/图/报告；[要求矩阵](../docs/REQUIREMENT_MATRIX.md)|
|2 实现正确性|在线两类离线独立参考、EA解码/HV/DTLZ、Q/Double/LT/可行动作及物理移动核验；当前47个Python实现/脚本compile、90项测试通过；[验证包](VERIFICATION_PACKET.md)|
|3 实验可信性|训练/验证/未来日期分区、train-only prior、共同可行图/归一化、不同基数实例比、原始与REPLAY身份均明确；原始数据/旧失败不覆盖；[方法](../docs/METHOD_AND_METRIC_SPEC.md)|
|4 研究循环|真实读数触发阈值诊断、EA初始化/有限组合、Double公平随机流、移动成本/移除LT、五训练seed与冻结确认；保留尾部/响应/收入/净成本负结果；预算和停止理由见[计划](../docs/EXPERIMENT_PLAN.md)、[决定](../docs/EXPERIMENT_DECISIONS.md)|
|5 Multi-Agent|四原生上下文、明确作者/独立核验交接，六类职责分时履行；[真实协作](MULTI_AGENT_EVIDENCE.md)|
|6 正式图|22数据图、实际候选比较、2原生可编辑技术图，P2/SVG/PDF/源代码/真实输入，34页200dpi实际审核覆盖；[图包](VISUALIZATION_PACKET.md)|
|7 双报告/复现|26页Experiment与8页Process交接稿，320表数字独立核对；两本fresh Kernel；原作者下载两CSV精确SHA；公开聚合重画；81成员LaTeX源包隔离编译并逐页像素等价，来源元数据变更按编译资产相等追加继承；[报告包](REPORT_PACKET.md)|
|8 发布/审核包|公开边界1497本地文件精确排除，实际staged blob语义审、最终delta及结构检查分别保存。普通commit/push后核对remote=local，再从该commit读出小型审核ZIP；固定提交身份与包SHA由post-push回执给出，不能在尚未执行时自造|

公开内容允许实质审查：完整代码、测试、评价器、run配置、非逐条汇总、科学图和双报告、真实独立核验。原始Foursquare、含data的教师ZIP、逐条proxy/episode/trace/真实membership仍完整留本地，既有公共计时/统计不随原始文件排除而遗漏。

外部尚待：网页GPT读取固定远程版本二审；用户理解/最终验收；教师正式提交。本轮原生ChatGPT用户UI截图、Evidence Master呈现规格及Lock未提供，Process仅在已授权的正文和技术素材范围交付。三者不由内部PASS代替，也不据此减少已完成的本地实验范围。
