# 共同方法与指标合同

初版冻结在正式实验之前；模块细则见各Agent METHOD_SPEC。变化须记录影响、失效结果和重跑范围。

## 在线单次二部匹配

Worker与Request各只使用一次；同刻采用(arrival, request-before-worker, id)稳定顺序。时间非负，事件截至显式horizon；批次在该时刻全部到达处理完后执行。派单时刻不早于双方到达；接驾延迟=请求等待+Euclidean距离/v，完成接驾可在horizon之后。

TBG gamma定义为时间阈值；请求到达时比较distance/v≤gamma，worker到达先服务按到达顺序首个wait≥gamma的请求，否则取wait+travel<gamma的最小者。v=1时与starter原判断一致。终止时只对真实剩余双方作最小总延迟最大基数匹配，不创造司机；缺供给的请求明确未匹配。

BB在theta整数倍处理，含同刻已到达对象；最终在horizon补一次非重复批次。遵照课件回收未匹配，保留starter discard作为对照。discard对象单独记录，不悄悄在后续恢复。课件§9提瓶颈，Notebook用sum KM，因此分别标BB（Notebook最小总成本）、BBmax（最小最大成本）；并行比较，不将一个目标冒称另一个。

离线每条边的最早派单=max(a_w,a_r)，延迟C=max(a_w-a_r,0)+d/v；相同输入与单次容量下先固定k=min(n_w,n_r)，分别最小化sum C和max C。最小总成本用线性分配；瓶颈用阈值可行性匹配，二者分别小规模枚举验证。

平均/最大/p95延迟的统计单位是已匹配请求；同时给全部请求分母、匹配率、unmatched、discard。零匹配的延迟=null（非0）。实例比值=online objective/offline same objective，仅服务基数相同且offline>0时定义；offline=0且online=0标等价0成本，非0/0不填1。

## 静态进化与动态RL

目标方向统一为min；收入的负号仅用于求解，展示仍为正收入。可行边、容量、无人匹配状态必须真实。HV以共同固定的可行目标界/参考点归一化，不为各算法分别拟合；Spacing对不足2个不同点明确边界。实测时间与函数评价数均保留。

RL用签到代理池采样模拟日；训练episode、源日期、测试模拟日三者不同。收入定义、时段终止与未完成服务分开记录。动态派单和主动调度的接驾、送客、空驶均有真实时间与位置变化；忙车不可接新单。LT区域中心时间只是价值估计，不能替代实际司机物理时间。Q更新后继max只允许当时定义的可行动作并包含WAIT。
