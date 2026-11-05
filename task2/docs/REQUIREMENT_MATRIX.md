# 教师要求与工程覆盖总账

审读者：原生子 Agent `/root/research_data`（Task R-001）。这是逐项登记与后续追踪入口，初稿状态不构成独立验收。材料的 Notebook Cell 编号从 **0** 开始；PPT 页码从 **1** 开始。`实现中/待运行/待报告` 保持真实含义，最终执行者须追加实际路径和验证结果。

## 材料全集及身份

- 基础课件：`teacher_materials/basic/实验2/实验2-任务分配（1）.pptx`，14页，首页日期20261014；原始ZIP SHA256 `19742d213c484b7bec40953bc4ca711c50859f60c600d19a60d2fa7b8955fb9d`。
- 基础starter：同目录 `作业2 运力调度.ipynb`，15 Cells，保持原件。课件p13提到 `task_assignment.ipynb`，压缩包实际文件名如上，不自行补造第二份教师starter。
- 进阶课件：`teacher_materials/advanced/实验3-任务分配(2) 多目标与强化学习派单.pptx`，25页；首页写实验二—任务分配(2)，p24与Notebook写实验3，保留编号差异。
- 进阶starter：同目录 `实验3 多目标与强化学习派单（学生版）.ipynb`，44 Cells；原始ZIP SHA256 `feb5569a3625dac74bc1044eff6af004ddf480c02a3bb17494513d7b521aa41f`。
- 两个城市CSV在进阶ZIP、基础嵌套ZIP、基础RAR中各有一份；逐字节SHA256证明各城市三份相同，见 `evidence/material_audit/archive_manifest.json`，不将重复副本视为独立样本。
- 全部PPT逐页XML文本与Notebook逐Cell文本位于 `evidence/material_audit/*_slides.md` / `*_cells.md`。PPT经LibreOffice转PDF并以120 dpi逐页渲染后，R-001已实际查看基础1–14页、进阶1–25页；转换PDF和逐页PNG位于该目录的 `ppt_render/`。

## 基础部分

| ID | 类别 | 来源 | 要求 | 实现 / 验证 / 结果 / 图与报告落点 | 当前状态 |
|---|---|---|---|---|---|
| B01 | T1 | PPT5；NB1–2 | 双边在线事件、身份唯一性、不可预知未来；速度/空间/时间单位；同刻和结束边界 | `src/online.py`；`tests/test_online.py`；`results/online/`；报告在线仿真定义 | 主线程实现与实验中，独立核验另列 |
| B02 | T1 | PPT5；NB2 | PPT N=20/T20/10km/1km-min 与NB N100/T2000/space1000分开 | `scripts/run_online.py` 场景身份；不得把NB空间数值自动称km | 主线程运行，报告待核 |
| B03 | T1 | NB4 TODO1 | 请求到达，候选司机距离阈值内分配、删除司机、记录真实delay | `src/online.py::TBGAlgorithm`；匹配trace独立复算 | 实现中 |
| B04 | T1 | NB4 TODO2 | 无可行司机则请求缓冲 | 同上；空队列/部分匹配反例 | 实现中 |
| B05 | T1 | NB4 TODO3 | 司机到达，优先FIFO超阈值请求，无距离限制 | 同上；等候≥γ边界、强制分配真实性 | 实现中 |
| B06 | T1 | NB4 TODO4 | 未超时请求中按总delay<γ找最小值 | 同上；等待与travel拆分 | 实现中 |
| B07 | T1 | NB4 TODO5 | 无匹配请求则司机缓冲 | 同上；NB文字只写TODO1–4，代码第五项也必做 | 实现中 |
| B08 | T1 | NB4 finalize | 只使用真实存在的剩余双方，记录无法完成对象 | 同上；不足司机、结束时仍缓冲测试 | 实现中 |
| B09 | T1 | PPT9–11；NB8 | BB Assignment生成、正确事件推进、保留回收与丢弃语义 | `src/online.py::BBAlgorithm`；`results/online/development_v1` | 已有初轮真实结果，待最终核验 |
| B10 | T1 | NB10 | theta=50/100/200独立比较，与NB尺度一致 | 对应notebook尺度场景与匹配率、avg/max delay | 已有初轮真实结果，待报告 |
| B11 | T1 | PPT3/13 | TBG/BB竞争比；总delay、最大delay与最大基数分开；零分母/部分匹配明确 | 独立枚举/LP参考、原始instance/matches；报告实例比值适用条件 | 独立核验中 |
| B12 | T1 | PPT13；NB13–14 | 基础NSGA-II，OD收入以送客距离表示、pickup距离、前沿、定义一致的标量化ratio | `src/evolution.py` 的basic身份实验；不可仅进阶NSGA冒充完成 | 待结果与报告 |
| B13 | T2 | NB0 | Foursquare真实签到改进仿真器，明确代理 | `src/dispatch_data.py`；`results/data/`；在线真实代理场景 | 数据已运行，场景实验待核 |
| BQ1 | T2 | PPT6 | “如果基于到达时间只受距离影响，给定上述仿真器，你将设计什么策略以实现‘成本’最小化；基于这种策略你将怎么设计算法求解？” | 报告解释最近贪心、批次sum/max目标与offline基准 | 待报告 |
| BQ2 | T2 | PPT12 | “有约束了怎么办” | 报告说明可行边、容量、半径和未匹配基数；小图反例 | 待报告 |

## 进阶Part A

| ID | 类别 | 来源 | 要求 | 工程证据落点 | 当前状态 |
|---|---|---|---|---|---|
| A01 | T1 | NB5–8；PPT5–8 | NSGA-II运行、编码解码修复、排序拥挤距离与精英保留 | `src/evolution.py`；`tests/test_evolution.py`；`results/evolution/` | E-A实现与运行中 |
| A02 | T1 | NB9–10 | NSGA-III、归一化、105个三目标参考方向、niche保留 | 同上；奇数105种群不得丢失个体 | 待独立审核 |
| A03 | T1 | NB11–15 | 同候选集合加权和+KM，二目标前沿、HV共同归一化/参考点 | `evidence/evolution/METHOD_SPEC.md`；保存fronts与history | 待运行核验 |
| A04 | T1 | NB16–17；PPT9 | 5 seeds的收敛与波动，原参考pop100/gen300/pc.9/pm1-m | 同上；不得只报最佳seed | 待运行核验 |
| A05 | T1 | NB18–20 | 三目标（收入、pickup、服务数），HV和Spacing | 三目标fronts，指标反例 | 待运行核验 |
| A06 | T1 | NB21–22 | DTLZ2，球面收敛误差、Spacing、HV与NSGA-II/III对照 | DTLZ2真实运行，不能抄PPT参考数值 | 待运行核验 |
| A07 | T1 | NB23–24 | 8/13/18/23点各批次前沿 | 共同40drivers/80orders，训练分区hotspots | 待运行核验 |
| A08 | T1 | NB25 Q3a | 种群与代数单因素扩大 | 基线先行，各自只改pop或gen，记录NFE和耗时 | 待结果驱动执行 |
| A09 | T1 | NB25 Q3b；PPT24 | 真正编码KM解到初始population的混合初始化，比较HV | decode(encode(KM))一致性、五seed对照 | 待单项后运行 |
| AQ1 | T2 | NB25 Q1 | “加权和 + KM 在本实验中表现不差，为什么？（提示：观察前沿形状是否‘凸’。）什么情况下加权和会漏掉帕累托解？” | 报告结合实际front与unsupported离散反例 | 待报告 |
| AQ2 | T2 | NB25 Q2 | “2目标时NSGA-II与NSGA-III谁更好？3目标时呢？结合‘拥挤距离’与‘参考点’的原理解释。” | 本轮实测与DTLZ2机制，不能预写新算法必胜 | 待报告 |
| AQ3 | T2 | NB25 Q3 | “前沿的高收入端，NSGA的解比KM稍差。请尝试：(a)增大代数/种群；(b)用KM的解初始化部分个体（混合策略），观察HV变化。” | A08/A09的真实正负结果 | 待报告 |
| AQ4 | T2 | NB25 Q4 | “平台运营中要从前沿上选一个方案，你会怎么选？膝点、约束法（接驾距离≤X km下收入最大）各有什么优缺点？” | 预定义约束/归一化、实际选择点，说明业务阈值是假设 | 待报告 |

## 进阶Part B

| ID | 类别 | 来源 | 要求 | 工程证据落点 | 当前状态 |
|---|---|---|---|---|---|
| R01 | T1 | NB27 | 108时间片、8×8网格、25km/h、PATIENCE2、1500模拟单 | `src/rl_dispatch.py`；仿真trace与边界测试 | E-B实现中 |
| R02 | T1 | NB31 TODO1 | Q更新、可行动作∪WAIT、gamma**delta、终止、计数与V样本平均 | 原Notebook手算单测保留；独立手算反例 | E-B作者测试已跑，待独立 |
| R03 | T1 | NB33 TODO2/3 | LT索引/机会成本；Q-KM W≤0不派；原单元测试 | `src/rl_dispatch.py`；`tests/test_rl.py` | E-B作者测试已跑，待独立 |
| R04 | T1 | NB34–37 | 300真实训练episode、曲线、TD、价值热力图 | `results/rl/`模型/curve/metrics，模拟训练日不能说真实300天 | 待正式训练与报告 |
| R05 | T1 | NB38–40 | 三策略、40/60/100车、五个测试模拟日 | 对每车队独立训练，测试冻结后进行 | 待正式实验 |
| R06 | T1 | NB41–42 | beta=0/.2/.4/.5/.6/.8/1敏感性 | 在validation扫描可选择，独立test不调参 | 待正式实验 |
| R07 | T2 | NB43 Q4 | GAMMA .8/.95、GRID、PATIENCE单因素 | 明确训练配置/计算成本，其他条件固定 | 待正式实验 |
| R08 | T2 | PPT24 | Double Q或SARSA，重点β1，过估计/拒单/价值/收入 | Double Q手算、对照训练，不能见收益才留记录 | 待正式实验 |
| R09 | T2 | NB43 Q5；PPT24 | V指导相邻区域主动调度，真实距离/时间/忙闲/后续位置 | 调度日志与成本，净收益需成本依据 | 待正式实验 |
| R10 | T2 | PPT24 | Q-KM长期边权+pickup双目标NSGA-II前沿 | 组件先行，估计目标与实现收入分开 | 待正式实验 |
| RQ1 | T2 | NB43 Q1 | “本仿真中‘KM-即时收入’反而不如‘贪心最近’，为什么？（提示：长途单把司机带到哪里？司机送完后多久才能接下一单？）” | 结果不保证同PPT，结合真实司机busy/空间再分布 | 待报告 |
| RQ2 | T2 | NB43 Q2 | “Q-KM的LT只按区域计算，同一区域内的所有司机共享同一个价值。这种近似损失了什么？换来了什么？” | 中心DELTA和真实出行dur区别，表规模和局限 | 待报告 |
| RQ3 | T2 | NB43 Q3 | “β=1时效果变差。从‘每个司机独立取max，忽略了其他司机抢单’的角度解释Q-learning的过估计；你能想到什么改进？（例如SARSA/策略评估、Double Q-learning）” | R08实际收益或负结果；max统计偏差与竞争失配不同 | 待报告 |
| RQ4 | T2 | NB43 Q4 | “尝试修改GAMMA（0.8/0.95）、网格大小GRID、PATIENCE，观察对结果的影响。” | R07，不以文字讨论替代真实运行 | 待报告 |
| RQ5 | T2 | NB43 Q5 | “（加分）让空闲司机按V主动调度到相邻高价值区域（repositioning），能否进一步提升收入？” | R09完整成本与单项/必要组合 | 待报告 |

## 项目正式要求

| ID | 类别 | 要求 | 落点 | 当前状态 |
|---|---|---|---|---|
| P01 | T2 | 独立Experiment/Process双报告，P2/XeLaTeX、真实科研解释 | `reports/` PDF、LaTeX与构建入口 | 待制作 |
| P02 | T2 | 真实多Agent职责、交接、研究/修复循环 | `evidence/multi_agent/`、各角色实际源码/记录 | 三原生Agent已真实行动，后续持续 |
| P03 | T2 | 独立验证、反例、负结果、最终总审核 | `evidence/independent_*` 与 `docs/REVIEW_LOG.md` | 进行中 |
| P04 | T2 | workflow/architecture可编辑drawio + SVG + PDF | `diagrams/` | 待制作；全局历史演变图须Evidence Lock后 |
| P05 | T2 | 科学可视化研究与候选比较，真实数据与可编辑源 | `figures/` 与可视化审查记录 | 主线程负责 |
| P06 | T2 | 正式Notebook Restart/RunAll，公开复现、固定commit审查包 | `notebooks/`、`docs/REPRODUCIBILITY_GUIDE.md`、`review/` | 待总验收 |
| P07 | T2 | Process真实UI/Evidence Master边界 | 缺当前原始截图/Plan只阻断相应证据页，正文与技术图继续；不代Lock | 外部证据待交接 |
| P08 | T2 | 数据/ZIP公开分发权限、secret、大文件及远程SHA | `docs/SOURCE_AUDIT.md`及发布检查 | 原数据license待确认，其他工程继续 |

## 本轮发现的语义风险（不得静默抹去）

1. 基础PPT9说瓶颈匹配；NB8用sum assignment。主线程保留sum/max两个明名实现与共同精确参考，不将KM-sum冒称minimax。
2. 基础PPT8图片伪码使用 `wait>γ or wait+travel≤γ`，NB4明确超时 `≥γ`优先，然后未超时严格`<γ`且选最小delay；本轮Prompt明确要求完成Notebook行为。须在方法说明保留边界差异。
3. 基础BB原starter已实现Assignment却清空未匹配双方；PPT10/11明确“未分配回收”，必须比较回收/丢弃。
4. 进阶NB6/27使用全量`ck`采样司机热点；当前数据入口强制训练内或训练70%来源，避免测试时间泄漏。
5. 进阶NB8的variation奇数population会只生成104个子代，三目标参考105时需正确处理并登记NFE；同名“105参考方向”不代表105次实际评价。
6. 进阶NB19 Spacing小于2个unique点或mean nearest distance为0时无定义，不能填零夸大均匀性。
7. 教学local-clock顺序产生25550 proxy；其中12对local gap与UTC elapsed矛盾、6对UTC负值，不能解释为真实相邻打车。保留teacher基线，并在独立开发单因素检查异常对影响，见 `evidence/research_data/time_offset_anomalies.csv`。
8. 原作者网页日期起点/原readme东京条数与实际CSV有差异，按实际文件计数，见SOURCE_AUDIT；source_crs未获证明，保持UNVERIFIED。

## 当前覆盖索引：实际产物承接初稿

此段由R-001在2026-11-05追加；以上初稿的“待运行/待报告”保留当时身份，不批量回写。这里登记当前已存在的实现、真实run与已执行核验，不代替最终PDF、外部GPT审核或用户验收。正文路径以 `reports/experiment/chapters/` 为基准；公开数据边界按用户最新明确答复另由 `docs/PUBLICATION_DATA_BOUNDARY.md` 管理。

| 要求ID | 当前实现/实际run | 已有核验与报告对应 | 本段状态 |
|---|---|---|---|
| B01–B08 | `src/online.py`；`tests/test_online.py`；两份完成版Notebook复用生产模块 | `evidence/independent_rl_on_online/verify_online.py` 从instance/matches独立复算；`02_online.tex`定义事件、同刻、strict边界与结束兜底 | 实现及原始记录独立核验已完成；PDF另审 |
| B02、B10 | `results/online/development_v1`分别有teacher与notebook尺度；Notebook实际运行theta50/100/200 | `notebooks/作业2_运力调度_完成版.ipynb` code Cell9；`01_data.tex`场景表及在线正文 | 两尺度保持独立，Notebook已执行 |
| B09、B11 | 同时保留BBsum/BBmax与discard/recycle；`results/online/{development,confirmation,threshold_diagnosis}_v1` | 独立枚举/LP/瓶颈参考；`02_online.tex`2×2 sum/max反例、同基数实例比、零分母/未匹配语义；两张在线表逐单元核数 | 实际实验与参考一致；不宣称理论竞争保证 |
| B12 | `scripts/run_basic_multiobjective.py`；`results/evolution/basic`共5个100/300合成欧氏OD run | `evidence/independent_research_on_evolution/verify_basic.py` 重加目标并以独立MILP核验5个lambda效用；`03_evolution.tex`首段与基础前沿图 | 已实际运行和独立核验，收入为送客km |
| B13 | `src/dispatch_data.py`；`scripts/run_online_studies.py`；`results/online/foursquare_proxy_v1` | 25,550代理与日期分区独立检查、训练only热点；`01_data.tex`和`02_online.tex`真实来源扩展段 | 数据与4时段代理实验已有真实结果，逐条产物本地保留 |
| BQ1–BQ2 | 最近可行/批次sum/max与共同可行边、顶点容量实现 | `02_online.tex`直接比较距离成本、全局目标和约束，并说明不强行填满无可行边；BQ1直接回答句由作者补入 | 源稿已讨论，最终排版另审 |
| A01–A04 | `src/evolution.py`；`tests/test_evolution.py`；18点二目标两算法各5seed及4时段；完整history | R-001另写decoder和2D/3D box-union HV；`front_metrics.py` round10→unique→ND统一指标，8/10/12位敏感性；`03_evolution.tex`机制与规范标尺 | 数学实现/原始run独立核验已完成 |
| A05 | 3目标40车/80单，105种群/105参考方向，各5seed，真实105子代 | 独立重解码F/服务数、HV/Spacing；`evolution_three_objective_geometry`与baseline表，正文区分相关第三目标与广铺前沿 | 已运行，未预设III必胜 |
| A06 | 教师整数DTLZ2，12变量、92/400，各5seed | 独立DTLZ公式/球面误差与规范HV/Spacing；`evolution_dtlz2_geometry`只图示seed0+解析网格，多seed指标另报 | 实验已做；球面误差的正式正文/表落点由作者补足 |
| A07 | inner小时8/13/18/23，每时段同40/80、3km/K6且5EAseed | `verify_batch_provenance.py`独立从日期池和训练only热点重建9个批次；时段前沿图与正文 | 已实际运行和输入核验 |
| A08–A09、AQ3 | 各算法N200/G300、N100/G600单项；原100/300的KMonly；有限KM+N200组合/父项；5个未来输入确认 | 115个EA run含基础5，另10个KM批次；独立原genes/pairs/F与125条规范指标；初始化41次求解/目标及timer单列 | 单项→组合/移除→冻结确认已真实闭环；未用未来重选参数 |
| AQ1 | weighted-KM真实前沿与线性权重参考 | `03_evolution.tex`区分unsupported非凸段与有限权重网格漏点；给出(0,2)/(1,1.1)/(2,0)已知答案反例 | 已有具体机制回答 |
| AQ2 | 两算法同种群/代数/候选图、5seed，派单2D/3D与DTLZ2分别比较 | 正文拥挤距离/方向关联机制；baseline表与3D/球面图；没有跨实例比较绝对HV | 已有实测及带范围解释 |
| AQ4 | `knee_point`、`constraint_choice`；各seed实际选择点 | 归一化尺度、端点敏感性和教学60km约束非活跃均在正文披露，不把非活跃阈值称实际SLA | 已实现并保留实际选择，源稿已回答 |
| R01–R03 | `src/rl_dispatch.py`及`tests/test_rl.py`，教师原始手算断言保留在完成版Notebook | `/root/evolution`独立手算Q/Double、WAIT/终止/次数、全部LT表，以及独立事件回放；正文定义区域中心DELTA与真实车程区别 | 作者测试+不同角色独立核验均已执行 |
| R04 | development每模型300实际模拟episode，曲线/TD/V模型真实保存；完成版Notebook也新训300episode | `rl_learning`、`rl_value_maps`；R-001已实际看正式图，来源背景已改8×8聚合；`04_rl.tex`不把模拟episode称真实300天 | 实际训练和源图检查完成；最终PDF另审 |
| R05 | 40/60/100各自完整重训，固定最后30%日期池各5个采样模拟日 | `results/rl/final_v1/fleet{40,60,100}`；独立trace回放与fleet表逐数核对；QKM60相对KM+2.47%、100为−3.59% | 已最终确认，无全面胜出声明 |
| R06 | beta0/.2/.4/.5/.6/.8/1在验证池成对5模拟日 | `beta_validation_v1`、`rl_beta_rejection`及Notebook；非正可行边分母不是独立拒绝订单数 | 已真实扫描并明确统计单位 |
| R07、RQ4 | gamma.8/.95、grid6/10、patience1/3分别重训300回合，固定5验证日 | 活跃数据分别在`sensitivity_v1`与修复后的`sensitivity_v2_rngfix`；sensitivity表已从各day_metrics独立核数 | 单因素已执行；patience改变等待合同明确披露 |
| R08、RQ3 | Double Q真实训练5seed×5验证日，beta1；最终模型/5日确认 | 受影响旧Double失效，更新coin与行为RNG分离；独立手算、真实策略与TD核验；收入改善但应答降低、拒单未修复，统计max偏差与竞争失配分开 | 加分实验已真实完成，负结果保留 |
| R09、RQ5 | `make_repositioner`真实四邻移动、ceil耗时、busy释放；lambda0/1/3/5单项、KM/LT边权移除及5训练seed确认 | 独立375trace回放核查位置/空驶/占用；正式成本、ablation图；冻结KM+move3在首批5日及独立新增20seed分别确认，不改参数 | 真实单项/组合/移除/成本闭环完成，不能称净利润改善 |
| R10 | QKM长期正边值+pickup双目标；静态100/300与动态40/30分别保存 | 独立125静态解/2040穷举参考、2124动态帧与所选膝点/0.6父项接驾预算；`04_rl.tex`估计目标和全天已实现收入分开 | 真实融合加分完成，不作全面优胜结论 |
| RQ1–RQ2 | greedy/KM/QKM同订单/初始司机且busy/释放可追溯 | `04_rl.tex`解释即时长途机会成本、未来位置与共享V的状态压缩代价，5.1稳健性补充时空限制 | 正文已有具体回答 |
| 时空修复证据 | 保留12个local/UTC矛盾对教学主基线；副本剔除后inner运营池少9对并重训300回合 | `OFFSET_REVIEW.md`、`offset_robustness_v1`和报告offset表；全25,550OD数学几何检查另由主线程完成 | 已有实测；不声称已证明源datum/真实出行时长 |

### 工程与交付要求的当前状态

| ID | 已存在的真实产物/核验 | 尚不能声明的范围 |
|---|---|---|
| P01 | Experiment章节01–05/附录及main已全文独立审读，8份生成表258项核数一致；报告在`reports/experiment/`，Process由主线程制作 | PDF未在本段时点完成独立≥200dpi逐页检查；不写双报告最终验收 |
| P02 | 三名原生子Agent实际职责、双向反馈与代码/实验/独立审查见`evidence/multi_agent/COORDINATION_LOG.md`、各`independent_*` | 不把普通优化函数或同作者自测冒称独立Agent |
| P03 | online由RL Agent、EA由数据Agent、RL由EA Agent交叉核验；R-001另独立读图/表/报告源，发现及真实修复保留旧身份 | 外部GPT真实远程审查和最终用户确认尚非内部检查能替代 |
| P04 | `diagrams/{dispatch_runtime_and_evaluation,research_verification_workflow}.{drawio,svg,pdf}`及同源导出脚本真实存在，XML非栅格嵌图 | 桌面draw.io未实际打开；技术图不冒充Evidence Lock后的全局历史演变图 |
| P05 | P2原生SVG/PDF/PNG、真实输入hash和三套绘图脚本；R-001逐一实际看过20个首轮正式PNG，发现的裁切/聚合/图注问题交作者闭环 | 最终嵌入尺寸与所有重导出图仍须最终PDF逐页检查 |
| P06 | 基础fresh-kernel attempt3完成7/7，进阶attempt2完成10/10，两个output hash与实际Notebook一致且无error输出，详见`evidence/independent_report_review/notebook_final_output_inspection.json` | 本Agent这是输出/回执独立核查，不冒称自己又额外执行了一次Run All；远程固定SHA审核包仍由主线程交付 |
| P07 | Process正文可从真实职责/决定/修复写起；外部原始ChatGPT UI/Evidence Plan未由R-001收到，不重绘、不代Lock | 用户UI截图页和Evidence Master验收保持真实外部依赖，不能填造截图 |
| P08 | 用户明确无额外许可，原始/可还原逐条派生本地保留；公开代码/配置/测试/脚本/图/双报告/安全汇总。公开作者fetch已真实无缓存下载、自动fallback与identity回归通过 | 最终公开exact list由独立V-PKG作内容级检查；仅匿名去ID不足以排除由pairs+F反推订单值，最终Git对象与远程SHA仍待审核 |

覆盖索引依据当前真实文件与不同角色的实际回执。`evidence/independent_report_review/`保留源稿首轮问题、数字核对和后续PDF检查；凡涉及最终成品、公开投影或新增run的变动，须另加针对性回执，不用这段承接记录自动签署新产物。

后续数据入口闭环追加：新版公开fetch于2026-11-05 11:33:19 UTC再次真实无缓存下载作者ZIP，直接Decimal10有效位half-up、UTF8/行间CRLF/末行无CRLF，重建NYC/TKY与teacher完全相同CSV字节，见`evidence/research_data/public_fetch_exact_network_verified.json`。`source_entry_exact_regression.json`进一步实际验证无教师文件的公开clone自动fallback、8份DataFrame逐项精确全等、25550代理和全部日期分区、原教师路径优先及显式安装sidecar；身份保持`AUTHOR_RECONSTRUCTED_EXACT_BYTES`，不因内容hash相同冒称教师直接提供。原CSV/正式run不变，旧近似转换和其失败回执保持历史身份。相同输入字节不自动证明跨环境随机产物bit相等。

来源独立验收追加：`/root/reinforcement`以不同上下文在隔离root实际运行已验证缓存ZIP转换，2城SHA/8份DataFrame全等和8个provider/receipt/teacher优先反例通过，见`evidence/independent_package/exact_public_data_review.json`。author目录绕过receipt的真实缺陷由该角色提出、R-001修复后复验。其检查不是第二次网络下载；不同动作和审查者保持原身份。

报告检查追加：R-001已将Experiment26页和Process8页分别以200dpi完整渲染，逐页实际打开全部34张页面；PDF及每页PNG hash和范围记录于`evidence/independent_report_review/pdf_visual_review_round1.json`。10份生成表320项核数另见`report_numbers_round2.json`。Process正文/技术素材交接稿范围通过；Experiment首轮只遗留图2黑色discard曲线方法标识需作者补图注/图例后复验。本段不代替Process真实UI Evidence Lock、外部远程二审和用户验收。

最终报告承接：作者修正discard标识、追加在线确认负结果与真实REPLAY段后，R-001独立重新200dpi渲染；Experiment仅物理6/9页、Process仅物理8页改变，余31页PNG字节等同首轮已目视页面。3个改变页已实际逐张重看，全部在声明范围通过，见`evidence/independent_report_review/PDF_FINAL_REVIEW.md`和`pdf_final_review.json`。最终Experiment SHA为`7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101`，Process为`a2c57f58d246e326d398003045cadad090db19dcab9163cae5871fd791b01de1`。g5开发尾部均值略优但确认更差的负结果已独立逐seed核对，确认平均延迟仍更低，不用测试重选参数。源ZIP的异目录独立编译另由V-PKG负责，不在此冒签。

发布边界末轮承接：用户无额外许可的明确答复保持；`local_only_manifest_current.json`现在按实际内容登记1496文件/1,831,809,449字节，包含117份逐条REPLAY取证而不粗排整个取证目录。原fusion front因REPLAY计时而变化的旧/新hash与批准原因显式追加，旧分类不改，非预期未解决变化0；当前54份聚合取证/CLI代码/来源摘要仍可作为公开候选。最终Git stage/对象与远程commit SHA由主线程及独立V-PKG核验。

外部边界仍为：本轮原始ChatGPT用户UI及Evidence Master规格/Lock未由R-001取得，不制作替代截图；公开工程真实远程GPT二审、用户理解与最终确认、教师提交分别承接。上述外部步骤不被内部数学/页面PASS替代，也不阻止已授权本地工程和许可范围内公开产物继续完成。

Stage新增内容检查承接：V-PKG发现真实`evolution/km_timing`计时原件中仍含41组pairs+F，本地保留该原件；公开规范指标已有实际runtime/计数及对应hash，不新增重复projection。依据`staged_sensitive_addendum.json`，当前私有exact list追加为1497文件/1,831,912,940字节，1496快照及REPLAY旧/新hash身份保留。最终unstage/check-ignore与Git对象审查由主线程/V-PKG继续执行。
