# Goal 2 反例与已暴露案例

构造反例具有解析定义和已知答案；其误删计数只适用于这些人工定义的坐标，不能外推真实轨迹准确率。

所有条目实际执行 S/D/P，并用候选之外的可信输入审核。没有新模型调用；下面是风险检验，不声称模型犯过这些错误。

## CE01_DIRECTION_AMBIGUITY

A single right-angle turn is retained here, but legitimate zigzag vertices satisfy the same deletion predicate. In the authored spike example the method deletes one normal neighbor together with the injected spike. Geometry alone is not a noise truth label.

Retain approved predicate as the teaching reference; do not claim real-data detection accuracy or alter the method from this example alone.

## CE02_UNDEFINED_IS_NOT_ZERO

Zero displacement has undefined direction; zero dt has undefined speed, including the moving same-time edge. These are explicit reasons, not fabricated zero velocities or a physical speed limit.

Keep undefined direction windows according to the approved one-pass schedule and report their denominator.

## CE03_ORDER_AND_BREAK_INFORMATION

P preserves its own geometric tolerance but can remove breakpoint trigger information. On the time fixture later S filters the two remaining singleton segments; on the distance fixture a 399-metre final edge crosses the original 401-metre break.

Keep actual unsafe order results as constraint-rejected experiments; no hidden segmentation or repair is added.

## CE04_FINITE_DISTANCE_AND_EQUALITY

The middle point projects beyond the finite endpoint, so its finite distance is sqrt(2), not the infinite-line distance 1. A separate exact-height example verifies strict recursion and dp=0 identity.

Reject the constructed infinite-line shortcut. Audit tolerance remains separate from the algorithm threshold.

## CE05_EMPTY_OUTPUT_IS_NOT_SUCCESS

An empty output contains no observed anomaly but also no covered raw points. Error and DP saving are unavailable, not perfect zeros; complete input membership remains visible.

Use coverage guards and null+reason rather than rewarding absence of output.

## CE06_OWN_CLEAN_IS_NOT_COMMON_TRUTH

Both P stages copy their own inputs exactly and report error zero; the direction=35 path has already removed a point. Its common raw-reference error is positive while direction=60 remains zero. Separate DP certificates therefore cannot establish cross-method quality.

Compare the pre-fixed raw reference and covered point identities; keep DP guarantees as stage-local facts.

## 七条已暴露 pilot

记录 0、1、2 的真实过滤分段与理由：

- 记录 0：99 原始点，0 最终点；99 点、段内 12.281263484 工作米、原因 TOO_SHORT_LENGTH。
- 记录 1：97 原始点，0 最终点；97 点、段内 23.539446104 工作米、原因 TOO_SHORT_LENGTH。
- 记录 2：99 原始点，0 最终点；99 点、段内 4.171537495 工作米、原因 TOO_SHORT_LENGTH。

按预登记距离规则选中的近阈值点为记录 306 / 原始索引 2，参考索引区间 [0, 12]，误差 4.938319812632 工作米。
方向案例保留一次标记的输入窗口和同时删除后的新邻接边。DP=2/5/10 的局部重算共享 S/D，仅解释已有 pilot；不作为未观察的评测发现或最终参数选择。

## 来源与边界

教师方向谓词和有限线段定义的来源沿用冻结合同的原件定位。本文件不引用不存在的模型原话、用户质疑、Human Approval 或 Evidence Lock。
