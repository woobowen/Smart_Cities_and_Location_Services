# 任务分配：在线匹配、多目标优化与强化学习

覆盖教师基础课件/Notebook及其两个思考点、进阶Part A/B及九道思考题、全部加分；本轮是一次性交付，研究和修复由单一连续父Goal承接。实验一成果保持原身份。

- [Experiment Report](reports/experiment/Experiment_Report.pdf) / [可编辑源](reports/experiment/main.tex)：方法、真实控制变量、结果、负例和取舍。
- [16 页正式 Process Report](reports/process/Process_Report.pdf) / [源与构建状态](reports/process/README.md)：接管用户认可的 GPT 成品，仅删除末尾来源附录及目录项；原生截图、TikZ 箭头、其余正文原样保留。旧 8 页稿另存历史，不新增 Evidence Lock。
- [基础完成版Notebook](notebooks/作业2_运力调度_完成版.ipynb)、[进阶完成版Notebook](notebooks/实验3_多目标与强化学习派单_完成版.ipynb)：实际fresh Kernel输出，教师原测试保留。
- [完整要求映射](docs/REQUIREMENT_MATRIX.md)、[方法/指标合同](docs/METHOD_AND_METRIC_SPEC.md)、[实际计划](docs/EXPERIMENT_PLAN.md)、[真实决定](docs/EXPERIMENT_DECISIONS.md)。
- [进化规范指标与结果](results/evolution/SUMMARY.md)、[RL当前有效索引](results/rl/ACTIVE_RUNS.json)、[在线结果](results/online/development_v1/metrics.csv)。
- [公开聚合前沿/收敛/成本/哈希](public_results/projection_manifest.json)：真实数据membership不公开；纯合成参考、完整代码、测试、评价器及汇总证据保留。
- [复现指南](docs/REPRODUCIBILITY_GUIDE.md)、[来源审核](docs/SOURCE_AUDIT.md)、[公开数据边界](docs/PUBLICATION_DATA_BOUNDARY.md)、[环境改动](docs/ENVIRONMENT_CHANGELOG.md)。
- [外部审查入口](review/REVIEW_INDEX.md)。内部检查、未来GPT二审、用户验收与教师提交分别记录。
- [内部交付门槛](review/DELIVERY_GATE_REVIEW.md)、[历史 26+8 页 LaTeX 源包](releases/Dispatch_Reports_LaTeX_Source.zip)、[内部审核/修复总账](docs/REVIEW_LOG.md)。47 个实现/脚本、90 项研究测试属于原研究交付的既有检查；本轮未重跑。当前 Process 编译及全文通过，但严格渲染比较仍有差异；当前规范升级及 12 项分发见[本轮外审材料](../evidence/infrastructure/SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md)。

正式研究运行包括115次完整EA和29个300回合RL模型；pilot、Notebook重算、数学测试和同输入REPLAY另列，不虚增独立样本。KM初始化有未来输入支持；调度gross改善伴随空驶成本，Double和NSGA融合保留响应/收入/接驾负权衡。

用户已明确无额外数据公开再分发许可：教师原始签到、含数据ZIP和可反解逐条数据的派生结果完整留在本地。公开下载脚本已实际从原作者取得数据，重建出与教师CSV SHA一致的两城市输入；获取者身份仍明确为作者来源重建。
