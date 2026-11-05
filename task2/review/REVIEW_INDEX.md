# 任务分配实验：GPT外部二审入口

审核对象是包含本文件的**固定Git提交**，仓库 `woobowen/Smart_Cities_and_Location_Services`、分支 `main`。交付ZIP根目录的 `FIXED_COMMIT.json` 给出实测local/remote SHA、ZIP生成身份与远程读取回执；使用该SHA读取所有文件，不把移动的main当作已审版本。此仓库内索引不嵌入自身commit以避免循环身份。

本提交的内部交付状态为 `READY_FOR_GPT_REVIEW`，发布动作与固定SHA/包身份须结合post-push回执核对；不代表GPT外部审核PASS或用户验收。真实未交付范围只有本轮原生UI互动证据页面及Evidence Master Lock；Process当前为正文与技术素材交接稿。原始Foursquare及可反解逐条派生按用户明确要求留本地，代码、聚合数值和实质审查证据公开。[八项门槛与外部状态](DELIVERY_GATE_REVIEW.md)分别登记。

建议顺序：

1. [要求矩阵](../docs/REQUIREMENT_MATRIX.md) → [方法与指标](../docs/METHOD_AND_METRIC_SPEC.md) → [来源](../docs/SOURCE_AUDIT.md)。先核对教师两份Notebook/PPT与任务身份。
2. [实验索引](EXPERIMENT_INDEX.md) → [结果与取舍](RESULT_SUMMARY.md)。检查开发/选择/独立确认，以及所有负结果。
3. [真实Multi-Agent记录](MULTI_AGENT_EVIDENCE.md) → [验证包](VERIFICATION_PACKET.md)。先看独立检查的执行范围，再看作者测试。
4. [可视化包](VISUALIZATION_PACKET.md) → [双报告包](REPORT_PACKET.md)。实际阅读PDF，不能只读摘要。
5. [Git与复现](GIT_AND_REPRODUCIBILITY.md)。核对固定提交、公开集合、数据下载、Notebook、聚合重画和报告源包分别验证。

重要入口：`../src/`、`../tests/`、`../scripts/`、`../public_results/projection_manifest.json`、`../results/rl/ACTIVE_RUNS.json`、`../results/evolution/SUMMARY.md`。审核者可逐数检查完整公开代码与聚合输出；原始受限记录的本地独立检查有真实hash和明确覆盖，不冒称远程提供了这些记录。

请重点质疑：同基数/同目标实例比是否正确；共同HV是否公平；Q的可行动作与跨时间折扣；忙闲/取消/移动成本；选择是否接触未来；增益是否值得额外成本；报告是否把开发、重复抽样模拟日或估计值夸大为真实业务证据。
