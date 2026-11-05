# 图型研究与选择记录

当前已真实检索的primary sources（2026-11-05）；论文不提供本实验实测增益。

|来源|支持的具体内容|应用/局限|
|---|---|---|
|[Xu等 KDD2018](https://doi.org/10.1145/3219819.3219824)|区域价值与组合匹配连接即时/未来收益|借鉴价值地图和动态位置解释；不声称复现真实滴滴收入|
|[Lin等 KDD2018正式页](https://www.kdd.org/kdd2018/accepted-papers/view/efficient-large-scale-fleet-management-via-multi-agent-deep-reinforcement-l)|供需变化下车队管理的空间/序贯问题|本任务用tabular RL，不引入该文深度框架|
|[Matplotlib ECDF](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ecdf.html)|ECDF保留原观测，3.8起提供API|本环境3.6.3，使用等价排序+step；匹配失败质量另保留在分母|
|[Allen等 Raincloud原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6480976/)|原始点、分布与统计摘要的联合表达|KDE可能掩盖点质量/零值；本例必须并列覆盖率|
|[Matplotlib scatter+marginals](https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html)|联合关系和边缘分布的组合布局|实际输入决定是否需要边缘图，不凑复杂度|
|[Plotly官方parallel coordinates](https://plotly.com/python/parallel-coordinates-plot/)|每条解在多维轴上的同一条折线|考虑三目标投影vs平行轴；需固定归一化，不产生新总分|
|[pymoo reference directions](https://pymoo.org/misc/reference_directions.html)|真实目标单纯形与参考点数量|三维仅用于真实三个目标，不做装饰三维|

## 在线等待主图：实际两个候选

问题：短批次的较低已服务延迟是否由丢单造成？数据固定为teacher场景5个开发seed、每seed20请求。

A：all-request service ECDF+coverage，所有请求为分母，未匹配质量留在低平台。编码完整延迟与失败质量，零值保留；比条件均值多揭示覆盖损失。风险是读者将其误读普通条件CDF，轴标签和图注明确分母。成本低。

B：原始点+violin+box，底部逐组打印served/100；显示已服务分布与极端点。KDE带宽0.3为绘图选择，不用于推断；条件分布可能仍误导服务质量。成本低。

两候选均实际生成在`figures/candidates/`，同一输入、同一语义P2。最终选择须在实际查看后追加；不根据色彩偏好裁决。

V1机制图：比较空间matching small multiples+逐请求等待/行驶分解，与单独地图。前者能定位gamma作用在等待还是距离，地图线仅为接驾边、无虚构道路。案例按TBG5的最大延迟中位seed预先选择，不挑最有利实例。

后续V3 Pareto/HV/三目标、V4时空V/策略、V5成对差异与消融从实际可用结果继续生成；候选比较/检查后追加，不预填不存在的图和审查。
