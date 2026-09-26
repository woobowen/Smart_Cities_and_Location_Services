# 实验一 Goal 1 · 第二轮二重验收

审核对象：`7e6cd4082c2cdad2452fa5a1006e99dcfb050d17`  
仓库：`woobowen/Smart_Cities_and_Location_Services` / `main`  
上一轮运行代码：`880290a5dada84c711248844038daa3ee35eeefb`

## 1. 裁决

**阶段成果部分认可；新增审核覆盖/可信参考问题必须修订；完整 Goal 1 仍为 PARTIAL_BLOCKED，不能进入 Goal 2。**

不是全部推倒重做。上轮完整profile列表审核漏洞已通过本次独立回归；缺失时间诊断问题也已修好。六次真实调用的可见事件支持“一次探针＋五次独立角色”的事实。C03→A04确实形成了基于数值核查的后续时间诊断。新的条件runner也不再只是固定BLOCKED占位。

但以下不能混同：
- 角色和反馈真实发生，不等于所有被请求产物都已在运行时核验。
- 构造输入上的完整处理链，不等于教师真实轨迹已经处理。
- 给定输入的数学/结构检查通过，不等于清洗质量已改善。
- 代码本身生成的检查通过，不等于另一个独立审核器能够发现所有相关错误。

## 2. 本次实际审核范围

通过GitHub连接器读取并核对main、固定提交、目录Git对象、核心实现、测试和运行记录，重点包括：
- workflow的controller、provider、budget、diagnostics、tools、pipeline、evaluation；
- 六次真实调用的visible_events、C03/A04/C05请求及live_audit；
- 当前合同、SEMANTICS、validation、tests_final和starter_full日志、Notebook执行记录；
- OpenAI Codex固定上游提交中provider合并逻辑。

从连接器读取内容恢复了diagnostics/evaluation/tools/io四个文件，并逐一核对Git blob与SHA256。四个文件均与目标提交完全一致。随后对其执行了离线构造探针，未修改用户仓库，模型调用0。

另从已提供教师ZIP读出与远程清单原始SHA256一致的JSON，独立复算七条pilot，数值吻合。没有通过任何CRS假设生成真实米制结果。

边界：没有重新发起模型调用，没有在用户环境重跑全部156/292测试，没有逐个独立重算其320项保护清单，也没有在本次逐页重渲全部PDF图。上述项目仅在实际读取到的远程记录及Git对象支持范围内认可。保存的测试日志不是GPT亲自重跑的证明；测试数也不覆盖本次新发现的反例。

## 3. 已核实进展

### 3.1 F01修复独立回归通过

本次调用真实工具接口verify_profiles和recompute_check，使用两条构造记录：

| 输入 | 两个接口实际结果 |
|---|---|
| 正常完整列表 | VERIFIED |
| 合法重排 | VERIFIED |
| 多一行重复ID | REJECTED |
| 缺失一条 | REJECTED |
| 多一行foreign ID | REJECTED |

修复后的duplicate_details能处理缺失时间：dt_raw=null、dt_reason=MISSING_OR_INVALID_TIME，同时保留可计算的位置重复信息，不删点、不改值。

代码：[tools.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/workflow/tools.py)、[diagnostics.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/workflow/diagnostics.py)。

### 3.2 真实角色链成立

实际可见事件：
`A profile_pilot → B duplicate_details → C verify_profiles → A time_boundaries → C recompute_check`。

六个thread各有完成事件和结构化结果；本批无可见重连/fallback事件。A04引用了C03和对应VERIFIED工具，基于5处长间隔请求时间边界检查。这支持真实诊断协作和后续行动，不支持“已经反复优化清洗质量”。

[C03](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/runs/g1-repair-roles-01/calls/g1-repair-roles-01-03-review/visible_events.jsonl)、[A04](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/runs/g1-repair-roles-01/calls/g1-repair-roles-01-04-research/visible_events.jsonl)、[C05](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/evidence/goal1/revisions/SC-LAB1-G1-REPAIR-001/runs/g1-repair-roles-01/calls/g1-repair-roles-01-05-review/visible_events.jsonl)。

### 3.3 数据和测试记录

七条pilot独立复算：783点、776边、122个零时间差、62个同时间异位置、323个连续重复位置、5处大于30的时间间隔、12个时间分区。原始JSON SHA256为c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3。

读取的工作测试日志为156 passed；正确cwd下的starter日志为292 passed/1 skipped/252 warnings，skip为中文字体未找到。Notebook记录为各9个code cell、新内核、模型调用0。均不自动推出完整真实baseline通过。

## 4. 两项待修订问题

### C2-F01：目标产物审核覆盖不完整

C03文字请求重复详情交叉核对；C05文字请求检查时间分区、等值不切和索引守恒。但verify_profiles/recompute_check只接收并检查previous_profiles。

控制器接受正确的反馈ID是进展，但“引用了目标产物”不是“核验了目标产物”。阶段结束后根据phase==5写VERIFIED，也不等于所有必要输出已被审核。

Codex已公开说明该限制，且另有audit_live离线补查，不能将其表述成造假。当前问题是**未来运行时关闭条件仍可能早于实际目标审核完成**。需要把现成独立检查接入明确目标的核验工具，并输出目标ID/hash、可信参考、checked/unchecked范围。旧模型消息不能修改，后补核验另存。

相关代码：[controller.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/workflow/controller.py)、[tools.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/workflow/tools.py)。

### C2-F02：baseline独立审核没有可信外部参考

`review_baseline(output)`从待审产物的segment.input重新建立inputs；分组账本的数值又从original取值，而不是实际clean/final。没有将完整输入作用域、原始值和获批参数独立传入。

本次在完全一致的evaluation.py上实际得到：

| 构造检查 | 期望 | 实际 |
|---|---|---|
| 正常4点结果 | 通过 | VERIFIED |
| 仅最终一个坐标改成999 | 拒绝 | REJECTED |
| 同时把clean和final坐标平移1000个平面单位，原input/账本不变 | 拒绝 | VERIFIED |
| 删除所有records和point_actions，stage_counts.input仍为4 | 拒绝 | VERIFIED，审核按0输入计 |
| 仅改汇总input/retained为999 | 拒绝 | VERIFIED |
| verify_baseline工具收到与当前raw记录集合不同的改值候选 | 拒绝 | VERIFIED |

这些是构造的错误产物，**不表示当前真实pilot被改过坐标**。生产runner现有原始点守恒检查可以抓到部分错误，但不能代替独立重审能力。真实baseline还没运行，正应在接入前补齐。

修复应使独立审核接收候选之外的原始数据/作用域/获批参数，检查实际数据跨阶段一致、分段和过滤规则、实际保留/删除点、DP区间误差、全部点去向及所有汇总数。不能把“理论应有的值”拼成账本后声称实际输出未改值。

代码：[evaluation.py#L246-L282](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/7e6cd4082c2cdad2452fa5a1006e99dcfb050d17/task1/workflow/evaluation.py#L246-L282)。复现：[probes/verify_round2_findings.py](probes/verify_round2_findings.py)，实际输出：[probes/results.json](probes/results.json)。

## 5. Provider与研究门控的处置

该版本上游合并逻辑对内置openai使用entry.or_insert，支持“原三个同名覆盖未生效”的判断。新的方案是外层实时观察/终止，不是关闭所有内部重试。无可见重试的成功批次不能证明隐藏请求总数或所有故障路径；当前不需要再因此建设新provider。

上游核查：[固定版本provider合并函数](https://github.com/openai/codex/blob/36650394c5b38c2990ccf2a3457165ca3e9d9726/codex-rs/model-provider-info/src/lib.rs#L678-L722)。

D1是文件级事实及距离方案缺口，D2是尚未批准的方法选择。二者不能由Codex修改状态字符串消除。GPT仍推荐D2的单次同时删除作为参考实现，但没有将其冒充用户批准或效果最优。

下一轮分两路：
- 没有D1/D2：只补两项审核、离线复核既有产物和Notebook，新增模型调用0，不重复诊断演示。
- 明确事实、距离合同与用户D2批准齐备：同一Goal1内完成七条pilot真实baseline、独立审核及有界实际处理反馈，再申请完整验收。

不要求Goal1已经有胜过其他方法的收益；Goal2阈值尚未冻结不能成为新的Goal1阻断。必须回到教师任务，不继续扩张审核平台。

## 6. 阶段状态

| 项目 | 本次判断 |
|---|---|
| F01及缺失时间诊断修复 | 独立回归通过 |
| 三角色真实调用与C→A动作 | 成立，限诊断 |
| Provider本批外层执行边界 | 认可已观察范围，内部请求仍unknown |
| 时间/重复产物运行时完整核验 | 需定向补齐 |
| baseline独立外部参考审核 | 需修订，已有实际反例 |
| D1/D2、真实完整baseline | 仍BLOCKED |
| 完整Goal1 | PARTIAL_BLOCKED / NOT_PASS |
| Goal2/3 | 不进入 |

本文件为当前GPT二重验收，不是实验最终报告或Evidence Lock。新修复提交仍须由GPT读取实际远程复核。
