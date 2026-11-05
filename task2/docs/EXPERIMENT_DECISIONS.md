# 真实研究决定（按证据出现顺序追加）

## Online-01：覆盖先于条件延迟解释

前置证据：`results/online/development_v1/metrics.csv`，55实例/1045条指标。teacher 5seed：BB discard theta.5覆盖.25，recycle覆盖1。workers_first的discard所有批长覆盖0。

判断：低条件均值不能表示完整服务效果；保留discard为starter诊断，正式对照使用回收；ECDF分母用全部请求，未匹配质量保留在低平台。不是把丢单补成0延迟。

## Online-02：阈值过小的终止兜底

前置证据：同一teacher5seed，TBG gamma.5/1/2平均17%匹配发生于finalize；gamma5为7%、gamma10为2%。gamma2 mean max13.342min，gamma5为12.802min，gamma10为16.796min。

假设：小阈值使请求/司机不能在到达事件配对，末时刻集中兜底；大阈值又退化为即时局部选择。因此gamma与尾部延迟不保证单调。

针对性实验：3种到达顺序×5paired development seeds×gamma[2,3,4,5,6,8,10,15]，保持同一实例、速度、容量、终止规则。指标最大/平均/等待/接驾、finalize比例，不改TBG核心、不加入新的deadline事件。读数随后追加；局部网格是开发，不能改称独立确认。

## Online-03：局部瓶颈不保证全天瓶颈

前置证据：theta1相同输入，teacher seed13的BBmax全天最大延迟比BBsum高2.162min；55实例中另有size100 seed13和supply1.5 seed13同现象。

判断：两算法每批正确不等于全时域最优。选择首个teacher反例进行逐批同对象诊断并绘图，不以均值掩盖反例；不为消除退化擅改算法。

## Data-01：时间偏移矛盾

主线程从原始source_row复算UTC：25550教学proxy中12对UTC间隔与local不一致，6对UTC负；R独立确认12对均不满足真实UTC的10—180min窗口，inner11/validation1/test0。

决定：保留教师local-clock代理口径，不将其称为真实物理轨迹；在训练内做剔除这12对的单因素稳健性，不能静默修改原始记录/覆盖baseline。证据`evidence/research_data/OFFSET_REVIEW.md`与time_offset_anomalies.csv。

## Online-04：确认样本未重复阈值5的尾部优势

前置证据：独立合成确认seed110--114，`results/online/confirmation_v1/metrics.csv`。TBG2/TBG5均覆盖全部请求；跨实例平均延迟7.639/5.411 min，平均最大延迟13.581/15.927 min，P95为13.007/14.070 min。

判断：开发样本的尾部轻微优势没有在独立样本保持。保留gamma5减少平均等待的局部收益，同时明确尾部代价；不在确认结果上继续选阈值，也不宣称gamma5是普适改进。BBsum/BBmax在这些确认输入的全天最大延迟相同不构成一般等价，前一反例仍有效。

## 其他研究分支

进化分支：`evidence/evolution/`，由真实独立Agent执行。
RL分支：`evidence/rl/DECISIONS.md`，含beta拒单、调度空驶成本、Double公平随机流修复；最终摘要在真实结果与独立检查后统一补入，不提前承诺增益。
