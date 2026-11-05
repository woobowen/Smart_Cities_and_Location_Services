# 真实实验与版本索引

所有路径相对task2。每条raw运行保存配置、seed和源/输入hash；受限输入/逐条结果留本地，公开对应聚合与hash。不要用目录glob混合失效、历史和当前run。

|分支|真实运行、输入与对照|参数/seed与结果入口|
|---|---|---|
|在线开发|`results/online/development_v1`：11场景×5成对输入×19方法，1045结果；全合成输入可公开|seed10–14；教学20×20、10km/20min/1km/min与Notebook抽象100×100尺度分开；各run `manifest.json`/metrics与 `evidence/online_development_v1.txt`|
|在线独立确认|`results/online/confirmation_v1`：相同预设配置另55输入/1045结果|seed110–114；不再按其选gamma；`reports/generated/online_confirmation_table.tex`|
|在线针对诊断|`results/online/threshold_diagnosis_v1`；三种到达顺序、5输入、8阈值及离线参考，共150指标|开发seed10–14，gamma2/3/4/5/6/8/10/15；`evidence/online_threshold_diagnosis_v1.txt`|
|在线真实代理扩展|`results/online/foursquare_proxy_v1`：训练内8/13/18/23点池，每小时5次采样、20对、10方法，共200指标|输入和matches本地；metrics/图公开。它们是历史代理抽样流，不是真实运营小时|
|基础NSGA-II|`results/evolution/basic`：单独全合成20OD/20司机教学问题，5完整EA|输入2024、EA0–4；欧氏送客km收入代理，λ0/.25/.5/1/2的exact optional KM；静态OPT/EA不混称在线理论竞争比|
|进阶EA基线|`results/evolution/runs/`中baseline阶段：60完整EA，2/3目标、低高峰、DTLZ2；共同可行图与输入先验界|开发seed0–4；2D N100/G300、3D N105/105方向/G300、DTLZ N92/G400；`results/evolution/SUMMARY.md`|
|EA结果驱动扩大|scale20、hybrid10、combination10完整EA；更大种群/更多代数→KM初始化→KM+种群组合|所有父项保留，41额外KM求解/41目标和明确计成本；预算/Spacing负权衡使最终保留teacher预算KM-only|
|EA未来确认|confirmation10完整EA，五个未见未来池输入各两方法|先冻结 `evidence/evolution/FINAL_CONFIRMATION_CONTRACT.json`；input9010–9014、EA10–14；`public_results/evolution/metrics.json`共125规范记录含10KM|
|RL基础与控制|`results/rl/ACTIVE_RUNS.json`精确登记39运行身份、36有效day表；beta/gamma/grid/patience/fleet/分布与长途诊断|29模型×300真实回合+pilot10=8710，Notebook再算另列；种子/表/模型/代码hash见ACTIVE及各训练manifest.json|
|Double修复与重复|`double_v2_rngfix`，Q/Double五训练seed、各五共同验证模拟日|2024–2028；旧共享随机流Double无效；旧Q-only精确数组等价身份保留|
|主动移动与消融|0惩罚→λ3/5成本→Q父项/KM移除LT→五训练seed确认|物理移动时间/终点/忙闲真实执行；`evidence/rl/DECISIONS.md`、`FINAL_SELECTION.json`|
|NSGA融合|静态N100/G300；逐决策N40/G30；knee与pickup≤同context QKM×.6|共同输入候选与可选匹配，估计目标≠最终实现收入；公开 `public_results/rl/`|
|RL最终留出|`final_v1`：fleet40/60/100与增强，冻结模型/规则，五个模拟日|sample50000–50004，日期池为最后30%；完整重放单独标REPLAY，未新增训练或重新选择|
|第二批冻结确认|`final_montecarlo_v1`：20个新模拟采样seed|60000–60019；同一未来日期池的新Monte Carlo，非20个真实新日期；空驶成本负结果保留|

源文件当前版本与原运行执行版本分开：`evidence/evolution/`、`evidence/rl/`中的source snapshots/manifest是真实运行身份；后加无副作用CLI保护不会倒写旧运行代码。公共投影 `public_results/projection_manifest.json` 绑定raw哈希、投影哈希与原路径；独立追加REPLAY审查承接被覆盖的runtime记录，不批量改写旧结论。

原始数据完整来源、SHA与日期边界见 [数据边界](../docs/PUBLICATION_DATA_BOUNDARY.md) 和 [复现指南](../docs/REPRODUCIBILITY_GUIDE.md)。
