# 独立核验与优化反馈（V/O）

执行者：原生子Agent `/root/research_data`。该Agent是共享数据入口作者；本记录的独立性限于**其他Agent制作的多目标算法/结果与主线程图表/Notebook**，不把自己的数据测试冒称独立数据审核。

## 实际参考与核验

- `verify_evolution.py`：独立请求顺序解码，不调用候选decoder作oracle；原NPZ重新算Manhattan pickup/fare、每个gene对应pair与F；独立坐标压缩盒并集重算2D/3D HV及全history；DTLZ2独立球面范数关系。最新范围110个advanced EA run、10个KM批次。
- 60个随机HV集合；30个随机3×4可选匹配图，独立穷举150个标量化最优值；全部与执行器结果一致。
- `verify_basic.py`：5个基础NSGA run从Euclidean OD重算；5个λ以独立integer MILP核验最优utility。基础收入为送客km，不是进阶模拟货币。
- `verify_canonical.py`：125条当前规范指标记录、8/10/12decimal精度，独立显式pairwise dominance和盒并集重算HV/Spacing；全部一致。被审packet另存 `metrics_input_<hash>.json`，原始文件hash逐项绑定。
- `verify_batch_provenance.py`：9个实际批次的OD/fare/source index对应各日期分区；以同seed独立从训练热点重建driver数组，字节级数值相同。5个未来测试批次9010–9014只用训练前70%driver prior。
- 旧baseline60/中间追加核验的回执按`*_previous_<hash>.json`保留，不以新审核覆盖旧范围。`result.json`与`canonical_result.json`指向最新实际检查范围。

## 真实发现、修复、复核

1. 原weighted-KM Spacing直接使用41个加权解，包含dominated点；18点unique21中4点被支配，8/23点各2。另有约1e-13的加法顺序重复。反馈后E-A单独建立统一`front_metrics.py`：所有方法round10→unique→ND→共同指标，不改变EA选择过程和历史raw。8/10/12精度独立复核一致，负结果与旧raw字段保留历史身份。
2. 混合初始化的41次KM求解原来位于EA timer外。hybrid尚未正式运行时反馈；E-A在运行前增加initialization计时、41次求解/目标和total runtime字段，共同归一化成本单列。未把旧EA-only时间改写为已测全流程时间。
3. 图表/Notebook首轮实际查看20个formal PNG，完整读三套figure builder及两Notebook全部代码。hash/发现见`figure_notebook_review_round1.json`：online colorbar裁切、Notebook尚未统一canonical、旧warning与尚未执行状态交主线程闭环。RL value-map逐条背景点已改为8×8聚合，在本轮已实际重看新图；不改V值。

## 结果驱动的研究交接

首批18点二目标结果，NSGA-II HV1.090244、III1.077092，KM1.098977。V/O据此提出：supported高收入端/初始化不足可能比单纯增加代数更重要；先按教师要求分别测试N200或G600，再单独KM初始化；只有有互补证据才组合。

E-A随后真实运行单因素：II N200的HV1.101432、G600为1.094778，III分别1.085327、1.090552；说明两个算法的预算受益不同，不能仅凭“进化代数更多”判优。之后完成KMonly、必要组合/移除与预冻结5未来批次确认；最新全部raw和指标已在上述独立程序核验。具体采用/回退的真实记录由E-A合同和研究决定文件承接，不由本记录冒充用户Human Judgment。

## 未覆盖

本审核不替代GPT远程审核、用户验收、Process截图Evidence Lock。首轮图表审核未覆盖最终PDF嵌入尺寸或全页；Notebook执行后的数字和最终页面需要后续追加检查。基础/多目标比值分别是有限在线实例比或静态标量近似比，不构成普适理论竞争保证。
