# Goal 2 阶段技术分析

本文件由当前有效 run 的固定哈希产物生成；不调用模型、不修改参数、不重新选择候选。它是阶段分析，不替代独立 C 全验收、网页 GPT 二重验收或用户最终研究判断。

派生状态：**DEVELOPMENT_PRESENTATION_REGRESSION_ONLY_NOT_FINAL_ANALYSIS**。原始 CRS 为 UNVERIFIED；距离和几何误差均为共同模型下的工作米。

缺少的必需输入：G2_EVAL results deliberately excluded from this regression。以下仅陈述已有的有效计算，不宣称 Goal 2 完成。

## 数据与比较口径

按原始记录分组，固定 seed=42，以原始跨度分位层、时间异常和相邻精确重复作描述性分层。低／中／高层不是标注运动真值；等额分层样本均值不代表总体均值。

| 分区 | 记录数 | 用途 |
|---|---:|---|
| PILOT_REGRESSION | 7 | 七条已暴露回归 |
| DEMO_MEMORY | 60 | 记忆构建 |
| DEVELOPMENT | 120 | 参数与选择 |
| G2_EVAL | 120 | 锁定后阶段评估 |
| G3_RESERVED | 11079 | 本轮保留，不用于选择或评测 |

共同参考固定为原始 dt=30、distance=400 的窗口，不做短段过滤。覆盖由保留原始点或同一原始窗口内的原始索引包围边定义；未覆盖误差为 null，并保留原始分母。保护比较要求基线已覆盖点身份集合不丢失，防止以易点替换难点。不同 clean 的 P 局部误差不能证明整体质量更高。

DP 省点率使用即时 P 输出／完整 P 输入；P 后续被 D/S 删除的点另计。空 P 输入不填 0。点保留、记录覆盖、全部由 S 过滤和最终无输出分别报告。长度、异常数与删点量均为描述性读数。

## 参数实验与稳定性

尚无完整参数运行可供陈述。

稳定区间仅指相邻已测试 OAT 值具有完全相同的逐记录阶段索引集合、共同覆盖集合与去向计数；不对未测试的连续区间作保证。
当前有效表中没有两个相邻取值满足这一完整一致条件；不以近似平均数制造平台区间。

各配置、分层、逐记录配对及完整可行集/Pareto 关系见 tables/parameter_*.csv、stable_intervals.csv 和 feasible_pareto.csv。C-S/C-D 比较共同覆盖及基线覆盖集合上的几何误差；C-P 在相同上游和固定 5 工作米预算内比较压缩。没有新加权质量分。

## 顺序对照

| 分区 | 顺序 | 安全失败记录 | 跨原始断点边 | D 跨断点窗口 | P 删除断点触发点 | 结论 |
|---|---|---:|---:|---:|---:|---|

S 的点数／长度过滤作用于当时输入；P 可能改变断点触发点，D 可能形成跨间断的方向窗口，P 在 D 前会改变邻域。order_failure_mechanisms.csv 保存实际索引、跨越边及邻域变化，不能仅凭顺序标签断言每条记录发生了同一种失败。安全失败的原始顺序保留为约束拒绝，不加隐藏预分段使其通过。评测只执行开发期已冻结的可行顺序。

## 四种模式、预算与记忆

同一分区的四模式共享固定 24 条记录。开发各 1 个 episode，正式评测各 3 个独立 episode；模型不能设置 seed 时记录 episode，不能声称模型完全可重复。llm-only 一次提议，搜索模式最多 20 候选、最多 3 决策回合；参考评分与 llm-only 决策之外的工作单列，批量 8 条记录的请求只计一次真实派发。

| 分区 | 模式 | 记录×episode | 原始合法/有原始提议 | 执行提议 | 回退 | 实验模型派发 | 候选评估 |
|---|---|---:|---:|---:|---:|---:|---:|
| DEVELOPMENT | llm+memory+search | 24×1 | 52/52 | 52 | 0 | 9 | 330 |
| DEVELOPMENT | llm+search | 24×1 | 72/72 | 72 | 0 | 9 | 372 |
| DEVELOPMENT | llm-only | 24×1 | 24/24 | 24 | 0 | 3 | 36 |
| DEVELOPMENT | search-only | 24×1 | 0/0 | 0 | 0 | 0 | 480 |

mode_pairwise.csv 保留同记录同 episode 的模式配对及不可比原因；mode_episode_distributions.csv 展示三次 episode 的分布。总体读数先在同一原始记录内汇总重复，再描述原始记录；重复、片段和点均不作为新增独立样本。这里只报告描述性分布，不将三次小样本胜负解释为稳定总体优势。

model_calls.csv 保存真实回执、可见 tokens、耗时与可用请求标识；底层请求数与费用不可见时保持 unknown/unavailable。治理 A/B/C 调用另由控制器记录，不能充当 search-only 的实验模型调用。resource_totals.csv 区分 manifest 原始处理/审核计数、缓存命中后 review_batch、以及记忆快照逐条准入的 review_record；三者之和只称注册 processing/verifier 调用，不是全部 Python helper 或 CPU 操作。候选锁定和治理复验属于额外治理工作，不混入模式实验调用。

当前有效模型派发 21 次；历史已失效或中断运行另有 15 次真实可见派发，其中 14 次完成、1 次中断或失败。历史成本逐项回读原始 provider receipt，并与 interrupted_model_costs.json 对照；它们不进入当前模式效果、合法率或收益统计。缺失 usage 保持 unknown，已观察 tokens 的部分和不冒充完整总成本。详见 historical_model_calls.csv 与 model_cost_scope_summary.csv。

示范记忆来自 60 条 DEMO_MEMORY，冻结哈希 `2330543c3a443532891936ac29d4080cb6e5f45c58e2976cc81c8fa67c6607d6`。有效检索记录 episode 中，24/24 有实际送达条目；17/60 个有记录的决策回合引用了有效条目，13/60 回合同时满足引用与参数一致。

上述分母分别是检索机会和实际决策回合。命中、模型引用、参数一致、与无记忆独立 episode 的建议变化分别保存；均不能单独证明记忆改善质量。评测快照前后哈希必须相同，示范条目不包含评测记录。

## 已锁定的单项候选

| 候选 | 配置 | 留出结论 | 建议 | 保护通过/记录 | 严格增益记录 |
|---|---|---|---|---:|---:|

候选参数在 G2_EVAL 前锁定，本表只应用原保护规则；没有评测后重选。保留参考配置是操作性回退，不代表参考已证最优。支持进入 Goal 3 的对象仍是单项证据；本轮不叠加 C-S/C-D/C-P，不冻结最终方法。分层退化见 candidate_by_stratum.csv，逐记录保护失败见 candidate_record_pairs.csv。两个轻量结构类别按冻结合同登记 NOT_ADMITTED_WITH_REASON。

## AI 建议与反例核验

实际 CORRECT_EVALUABLE_PREDICTION：DEVELOPMENT / llm+memory+search / episode 1 / 记录 10232 / round 2。模型原始理由："Direction 60 improved common maximum error and removed 10 versus reference 32. Test tighter DP while preserving that verified direction stage."。合法=True，执行=True；预测 n_direction_removed decrease，实际 decrease，差值 -22，预测状态 EVALUABLE；拒绝原因 None，是否成为锁定输出=False。执行前参考句柄 `8d1cafbce7d202b9aa34d29a97406aa93309f9fa97b70cb13ce4695640699bbd`。来源：[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json)；候选与参考 trace 的核验哈希在 mode_proposals.csv。这是可执行性和预测方向核对，不是真实质量验收。

实际 UNEVALUABLE_PREDICTION：DEVELOPMENT / llm+memory+search / episode 1 / 记录 10232 / round 1。模型原始理由："Isolate the direction threshold's effect on protected fidelity; the card cannot establish an error change."。合法=True，执行=True；预测 common_max_error not_predicted，实际 None，差值 不可用，预测状态 NOT_PREDICTED；拒绝原因 None，是否成为锁定输出=False。执行前参考句柄 `8d1cafbce7d202b9aa34d29a97406aa93309f9fa97b70cb13ce4695640699bbd`。来源：[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round1_call/attempt01/response.json)；候选与参考 trace 的核验哈希在 mode_proposals.csv。这是可执行性和预测方向核对，不是真实质量验收。

实际 LEGAL_PROPOSAL_TRADEOFF：DEVELOPMENT / llm+memory+search / episode 1 / 记录 7764 / round 2。模型原始理由："Direction 60 alone left common maximum error unchanged. Test additional spatial splits with relaxed segment filters; existing raw breaks remain separated, while coverage and fidelity require evaluation."。合法=True，执行=True；预测 raw_break_crossings unchanged，实际 unchanged，差值 0，预测状态 NEAR_ZERO_OR_UNCHANGED；拒绝原因 None，是否成为锁定输出=False。执行前参考句柄 `af61507082c6cea7b92207c5c3d95a667ff560559c14d384dc2874acc3b83b91`。来源：[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json)；候选与参考 trace 的核验哈希在 mode_proposals.csv。这是可执行性和预测方向核对，不是真实质量验收。

该合法建议的实际保护判定为 TRADEOFF：共同原始覆盖 122/122 → 122/122；基线已覆盖身份集合上的最大误差 40.214764 → 69.145351 工作米；原始断点跨越 0 → 0；保护失败项 ['COMMON_GEOMETRIC_PROTECTION_DEGRADED']。候选自身 DP 输入 105 点、即时输出 59 点，自身最大误差 4.8264199 工作米，超界 0 点。自身 DP 合格不代表共同原始几何更好；该案例是已执行的建议权衡，不能称为非法动作、真实误删或真实质量真值。全部此类原始提议、前置预测、参考／候选实际读数及是否锁定见 ai_legal_proposal_tradeoffs.csv，正文代表按既有稳定排序取首条，不按效果大小挑选。

未观察到以下类别，故没有对应模型引语：ILLEGAL_PROPOSAL、PREDICTION_MISMATCH、FALLBACK。

The archived teacher time-threshold explanation is checked arithmetically: 20 > 15, so dt=15 splits a 20-unit interval; this is not attributed to a current model response。

## 解释边界与复现

所有几何结果条件于固定数学椭球、h=0 和共同 ENU 平面；坐标敏感性独立产物描述扩大空间范围内的实现误差、近似差异和实际阈值变化，不能由清洗分数反选坐标模型。没有真实噪声标签，因此不报告真实误删率、检测准确率或真值恢复率。

bounded-search 是有限预算参考；没有冻结可比标量目标时，本轮不计算归一化 regret，也不称搜索为全局最优。负结果、约束拒绝与无收益是有效实验结果，与实现错误分别记录。

复算入口：`python -m task1.scripts.build_goal2_analysis --current-runs task1/evidence/goal2/current_runs.json --output-dir task1/evidence/goal2 --document task1/docs/goal2/STAGE_ANALYSIS.md`。本脚本只重建分析表；从原始数据重建确定性处理和图请使用 Goal 2 工作 Notebook 的默认 RECOMPUTE 入口，真实新调用须显式 LIVE。

输入哈希、每张表的哈希及行数均在 result_summary.json。GPT_SECOND_REVIEW=PENDING；Submission=NOT_READY。本文件不宣称最终报告定稿、Evidence Lock、用户 Understanding 通过或项目最终 PASS。
