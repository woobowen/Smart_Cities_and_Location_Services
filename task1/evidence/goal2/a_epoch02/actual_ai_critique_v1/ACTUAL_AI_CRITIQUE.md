# 实际 AI 提议与构造反例

本记录引用已经独立核验的 DEVELOPMENT LIVE 响应，关联已经真实执行的 formal-02 构造反例。未读取尚在运行的正式模式、未新增模型或处理调用。它补充 actual_ai_citations，等待独立审查；不改变方法、指标或参数。

开发期148条原始提议均合法执行，0回退；70条可评价方向预测均一致，另78条不可评价。下面保留全部4条合法但出现 TRADEOFF 的建议，另按既有稳定排序引用一条一致预测和一条未承诺预测。权衡不是非法动作或幻觉，构造风险也不代表模型曾作过对应错误断言。

## AI-DEV-01 · LEGAL_PROPOSAL_TRADEOFF · 记录 7764

llm+memory+search，episode 1，round 2；[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json)。响应SHA256：`fe36cab28325d549ba8118e21e59d53363b7147f4da77b45346d36404e58db98`。

> Direction 60 alone left common maximum error unchanged. Test additional spatial splits with relaxed segment filters; existing raw breaks remain separated, while coverage and fidelity require evaluation.

执行前预测：`raw_break_crossings` / `unchanged`，参考句柄 `af61507082c6cea7b92207c5c3d95a667ff560559c14d384dc2874acc3b83b91`。实测预测状态 `NEAR_ZERO_OR_UNCHANGED`，差值 `0`；是否锁定为最终输出：False。

| 已执行读数 | 共同参考配置 | 实际提议 |
|---|---:|---:|
| 原始点分母 | 122 | 122 |
| 共同覆盖点 | 122 | 122 |
| 共同几何最大误差／工作米 | 40.214764334442535 | 69.14535092142388 |
| 本次DP完整输入点 | 91 | 105 |
| 本次DP最大误差／工作米 | 4.826419900439255 | 4.826419900439255 |
| 方向删除点 | 31 | 17 |

Legal proposal executed successfully; common geometric protection degraded, so it was not selected. Retain it as an actual tradeoff, not an illegal action, hallucination or evidence of real misclassification.

The actual candidate satisfies its own DP certificate while its common-reference geometric protection worsens. The synthetic example independently demonstrates why own-clean DP error cannot establish cross-method improvement.

冻结保护：`['COMMON_GEOMETRIC_PROTECTION_DEGRADED']`；基线已覆盖身份集合上的误差 40.214764334442535 → 69.14535092142388 工作米。候选自身DP合格不覆盖这个跨方法比较。完整参数、共同参考单位、记录/阶段hash及锁定配置见JSON。

## AI-DEV-02 · LEGAL_PROPOSAL_TRADEOFF · 记录 7764

llm+memory+search，episode 1，round 2；[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json)。响应SHA256：`fe36cab28325d549ba8118e21e59d53363b7147f4da77b45346d36404e58db98`。

> Test a stronger spatial split threshold after the direction-only trial tied protected maximum error. Preserve raw break separation; short-window coverage remains uncertain.

执行前预测：`raw_break_crossings` / `unchanged`，参考句柄 `af61507082c6cea7b92207c5c3d95a667ff560559c14d384dc2874acc3b83b91`。实测预测状态 `NEAR_ZERO_OR_UNCHANGED`，差值 `0`；是否锁定为最终输出：False。

| 已执行读数 | 共同参考配置 | 实际提议 |
|---|---:|---:|
| 原始点分母 | 122 | 122 |
| 共同覆盖点 | 122 | 111 |
| 共同几何最大误差／工作米 | 40.214764334442535 | 69.14535092142388 |
| 本次DP完整输入点 | 91 | 99 |
| 本次DP最大误差／工作米 | 4.826419900439255 | 4.826419900439255 |
| 方向删除点 | 31 | 12 |

Legal proposal executed successfully; common geometric protection degraded, so it was not selected. Retain it as an actual tradeoff, not an illegal action, hallucination or evidence of real misclassification.

The actual candidate satisfies its own DP certificate while its common-reference geometric protection worsens. The synthetic example independently demonstrates why own-clean DP error cannot establish cross-method improvement.

冻结保护：`['COMMON_COVERED_IDENTITIES_LOST', 'COMMON_GEOMETRIC_PROTECTION_DEGRADED']`；基线已覆盖身份集合上的误差 40.214764334442535 → None 工作米。候选自身DP合格不覆盖这个跨方法比较。完整参数、共同参考单位、记录/阶段hash及锁定配置见JSON。

## AI-DEV-03 · LEGAL_PROPOSAL_TRADEOFF · 记录 7764

llm+memory+search，episode 1，round 3；[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round3_call/attempt01/response.json)。响应SHA256：`9c635a83691ac1527de98b8dcf0212a57adf6b2410aa7bba07a087c06c388d82`。

> Additional spatial splits degraded protected geometry. Restore reference segmentation and test tighter DP with direction 60; removals remain 20 versus reference 31, while common error is uncertain.

执行前预测：`n_direction_removed` / `decrease`，参考句柄 `af61507082c6cea7b92207c5c3d95a667ff560559c14d384dc2874acc3b83b91`。实测预测状态 `EVALUABLE`，差值 `-11`；是否锁定为最终输出：False。

| 已执行读数 | 共同参考配置 | 实际提议 |
|---|---:|---:|
| 原始点分母 | 122 | 122 |
| 共同覆盖点 | 122 | 122 |
| 共同几何最大误差／工作米 | 40.214764334442535 | 42.54590394990599 |
| 本次DP完整输入点 | 91 | 102 |
| 本次DP最大误差／工作米 | 4.826419900439255 | 1.8959774434600742 |
| 方向删除点 | 31 | 20 |

Legal proposal executed successfully; common geometric protection degraded, so it was not selected. Retain it as an actual tradeoff, not an illegal action, hallucination or evidence of real misclassification.

The actual candidate satisfies its own DP certificate while its common-reference geometric protection worsens. The synthetic example independently demonstrates why own-clean DP error cannot establish cross-method improvement.

冻结保护：`['COMMON_GEOMETRIC_PROTECTION_DEGRADED']`；基线已覆盖身份集合上的误差 40.214764334442535 → 42.54590394990599 工作米。候选自身DP合格不覆盖这个跨方法比较。完整参数、共同参考单位、记录/阶段hash及锁定配置见JSON。

## AI-DEV-04 · LEGAL_PROPOSAL_TRADEOFF · 记录 7764

llm+search，episode 1，round 3；[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+search-e1-b2/round3_call/attempt01/response.json)。响应SHA256：`8ede213891e25566733c0627f53fbca6037e145361d321127e0238902fb9e517`。

> Direction 60 retained the reference maximum error at DP 5. Test its interaction with DP 2; direction removals remain 20 versus 31.

执行前预测：`n_direction_removed` / `decrease`，参考句柄 `af61507082c6cea7b92207c5c3d95a667ff560559c14d384dc2874acc3b83b91`。实测预测状态 `EVALUABLE`，差值 `-11`；是否锁定为最终输出：False。

| 已执行读数 | 共同参考配置 | 实际提议 |
|---|---:|---:|
| 原始点分母 | 122 | 122 |
| 共同覆盖点 | 122 | 122 |
| 共同几何最大误差／工作米 | 40.214764334442535 | 42.54590394990599 |
| 本次DP完整输入点 | 91 | 102 |
| 本次DP最大误差／工作米 | 4.826419900439255 | 1.8959774434600742 |
| 方向删除点 | 31 | 20 |

Legal proposal executed successfully; common geometric protection degraded, so it was not selected. Retain it as an actual tradeoff, not an illegal action, hallucination or evidence of real misclassification.

The actual candidate satisfies its own DP certificate while its common-reference geometric protection worsens. The synthetic example independently demonstrates why own-clean DP error cannot establish cross-method improvement.

冻结保护：`['COMMON_GEOMETRIC_PROTECTION_DEGRADED']`；基线已覆盖身份集合上的误差 40.214764334442535 → 42.54590394990599 工作米。候选自身DP合格不覆盖这个跨方法比较。完整参数、共同参考单位、记录/阶段hash及锁定配置见JSON。

## AI-DEV-05 · CORRECT_EVALUABLE_PREDICTION · 记录 10232

llm+memory+search，episode 1，round 2；[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round2_call/attempt01/response.json)。响应SHA256：`fe36cab28325d549ba8118e21e59d53363b7147f4da77b45346d36404e58db98`。

> Direction 60 improved common maximum error and removed 10 versus reference 32. Test tighter DP while preserving that verified direction stage.

执行前预测：`n_direction_removed` / `decrease`，参考句柄 `8d1cafbce7d202b9aa34d29a97406aa93309f9fa97b70cb13ce4695640699bbd`。实测预测状态 `EVALUABLE`，差值 `-22`；是否锁定为最终输出：False。

| 已执行读数 | 共同参考配置 | 实际提议 |
|---|---:|---:|
| 原始点分母 | 98 | 98 |
| 共同覆盖点 | 98 | 98 |
| 共同几何最大误差／工作米 | 5.940373318870127 | 2.5656983807839056 |
| 本次DP完整输入点 | 66 | 88 |
| 本次DP最大误差／工作米 | 4.729191523380884 | 1.7506423461456058 |
| 方向删除点 | 32 | 10 |

The pre-execution direction prediction matches this measured metric difference. Correct sign is not a claim of real cleaning accuracy or proof that this proposal should be selected.

A correct change in the number of direction deletions does not say which real points are noise. The authored normal/spike fixtures supply truth only for their own constructed inputs.

## AI-DEV-06 · UNEVALUABLE_PREDICTION · 记录 10232

llm+memory+search，episode 1，round 1；[原始 response](../../runs/g2-development-modes-02/modes/DEVELOPMENT-llm+memory+search-e1-b2/round1_call/attempt01/response.json)。响应SHA256：`6207cfd3ccfe3cee4b0cf7f12c807cf63a8f0175c9c77bcf3b1dc22c7059ce66`。

> Isolate the direction threshold's effect on protected fidelity; the card cannot establish an error change.

执行前预测：`common_max_error` / `not_predicted`，参考句柄 `8d1cafbce7d202b9aa34d29a97406aa93309f9fa97b70cb13ce4695640699bbd`。实测预测状态 `NOT_PREDICTED`，差值 `None`；是否锁定为最终输出：False。

| 已执行读数 | 共同参考配置 | 实际提议 |
|---|---:|---:|
| 原始点分母 | 98 | 98 |
| 共同覆盖点 | 98 | 98 |
| 共同几何最大误差／工作米 | 5.940373318870127 | 4.820550000705671 |
| 本次DP完整输入点 | 66 | 88 |
| 本次DP最大误差／工作米 | 4.729191523380884 | 4.820550000705671 |
| 方向删除点 | 32 | 10 |

The model did not commit an evaluable prediction here. Preserve not_predicted/null and its denominator; do not score it as either an incorrect or a correct prediction.

Uncertainty in a model prediction is distinct from zero-time/empty-output numeric undefinedness; no artificial one-to-one equivalence is asserted.

## 已执行构造风险

六组反例共19条构造处理链、25项已知答案核验；另有10条已暴露pilot处理链，均是已有正式运行，本关联工作没有新增运行。

| 反例 | 实际核验内容 | 与模型的关系 |
|---|---|---|
| CE01_DIRECTION_AMBIGUITY | normal sharp turn versus spike；3项已知答案通过 | AI-DEV-05；仅机制/解释边界关联 |
| CE02_UNDEFINED_IS_NOT_ZERO | zero displacement and same time different position；4项已知答案通过 | 无对应实际模型断言；仅机制/解释边界关联 |
| CE03_ORDER_AND_BREAK_INFORMATION | time/distance break and P removes trigger；5项已知答案通过 | 无对应实际模型断言；仅机制/解释边界关联 |
| CE04_FINITE_DISTANCE_AND_EQUALITY | finite segment versus infinite line and threshold equality；6项已知答案通过 | 无对应实际模型断言；仅机制/解释边界关联 |
| CE05_EMPTY_OUTPUT_IS_NOT_SUCCESS | delete-all scoring loophole；4项已知答案通过 | 无对应实际模型断言；仅机制/解释边界关联 |
| CE06_OWN_CLEAN_IS_NOT_COMMON_TRUTH | different clean references cannot certify overall improvement；3项已知答案通过 | AI-DEV-01, AI-DEV-02, AI-DEV-03, AI-DEV-04；仅机制/解释边界关联 |

CE01表明正常几何也可能被方向谓词删除；只有构造输入可称误删。CE02保留不可计算速度/方向的明确原因。CE03保存P提前消除断点触发信息的实际失败。CE04拒绝人为注入的无限直线捷径，验证有限线段与阈值等号。CE05空输出仍保留原始分母，误差与DP省点率是null。CE06两条自身DP误差均为0的链，共同原始误差分别为0.4472135955和0，说明阶段内证书不能证明整体更好。

这些构造结论不外推真实噪声真值；没有原始响应支持的模型错误不作归因。真实四条建议提出的是可检验假设，确定性保护发现权衡后未将其选入，体现实际建议—执行—核验流程。
