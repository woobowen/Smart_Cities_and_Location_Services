# Goal 1：GPT 真实远程二重验收

- 审核对象：`woobowen/Smart_Cities_and_Location_Services`
- 固定提交：`c2e3ffe2f5af92ee03dac16a2865ec7c42f576e0`
- 审核日期：2026-09-26
- 结论：**REVISE / NOT_PASS；继续 Goal 1，不进入 Goal 2/3。**
- 工程状态：**PARTIAL_BLOCKED，另有需要修复的工程缺陷。**
- 本轮 GPT 未写入远程仓库，未调用实际模型，未修改教师原始数据。

## 1. 审核方式与边界

实际通过 GitHub 连接器读取了 current main、固定提交目录、核心源码、合同、配置、测试说明与测试源、运行回执和事件、Notebook、结果与图源。不是只依据 Codex 最终回复。

已对照旧提交 `b25efc153311a967109c586edab39361326500c7` 与新提交的 Git tree/blob：AGENTS.md、公共 docs/evidence/releases/templates/tools、教师 PPT、作业 ZIP 及解压作业目录一致；新增内容位于 task1 的工作目录。此核对说明被比较提交中的原始树未变化，不证明用户机器此刻工作区仍然干净。

当前运行环境不能联网克隆整个仓库。为做独立验证，依据连接器返回内容在临时审核目录恢复 diagnostics.py、tools.py、io.py、provider.py，逐一核对 Git blob SHA 与远程完全相同，然后运行针对性工程探针。没有宣称重跑了 Codex 的全部 108 项测试。

另从已挂载的教师 ZIP 读取 SHA256 与远程合同完全一致的 JSON，独立重算结构统计和固定 pilot。模型历史只核读，没有重新发起。架构 SVG 按远程原文恢复，Git blob 校验后实际渲染检查；未取得并重验远程全部 PDF/PNG 的原始字节，因此不宣布全部图形格式重新验收通过。

### 可重查证据

- 本地独立结果：`probes/results.json`、`probes/provider_results.json`
- 执行日志：`probes/execution.log`、`probes/portable_probe_execution.log`
- 已核对源码：`source_snapshot/verified_blobs.json`
- 可在目标仓库复现的脚本：`probes/reproduce_repository_findings.py`
- 架构 SVG 与渲染：`figures/goal1_loop.svg`、`figures/goal1_loop.png`

所有新探针均为 ENGINEERING_TEST／CONSTRUCTED_FIXTURE，不是自然 Agent 运行或轨迹质量实验。

## 2. 已确认的成果

### 2.1 Git 对象一致性

| 对象 | 旧、新提交中相同的 Git 对象 |
|---|---|
| AGENTS.md | b4b4966c5102d23c21a5e597a9711e851ac81ab7 |
| docs/ | 14463453873a3bf7c3ec78d6fbcf9eca9a5c74d6 |
| templates/ | cd431d24c40514fc3e03fed28355820e228970e1 |
| tools/ | 94cc4b562c8c89cc8d84f5819fd50504a9cba249 |
| task1/作业/ | 573426f389f59bfae75f5e7cf7948aeccde485d4 |
| task1/作业.zip | 3e41b61874176f6cc02d47c989620c7ea1147307 |
| task1/实验课1.pptx | 73d98c314d062ce1d917c15f41804fb0dcee493c |

### 2.2 独立原始数据复算

原始 JSON SHA256：`c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3`。

| 项目 | GPT 独立复算 |
|---|---:|
| 记录数 | 11,386 |
| 点数 | 1,173,410 |
| 相邻边数 | 1,162,024 |
| 零时间差 | 42,185 |
| 负时间差 | 0 |
| 时间差 > 30 | 8,272 |
| 同时刻不同位置 | 29,175 |
| 连续重复位置 | 575,278 |
| 七条 pilot 点数 | 783 |
| 七条 pilot 的时间诊断分区 | 12 |

pilot `0,1,2,246,256,306,352` 点数分别为 `99,97,99,108,99,111,170`，时间诊断分区为 `1,1,1,1,1,5,2`。#352 为 170 点、54 个不同时间戳、跨度 543 原始秒，与本轮报告一致。

上述只是结构诊断，不是空间分段、去噪、简化或真值恢复效果。

### 2.3 实现与记录的积极部分

- 有限线段 DP、有序原始索引和独立几何评价器在源代码中确实存在。测试源覆盖端点、退化、重复、回头及数值定义；本次确认其实现和测试内容存在，不把它提升为真实轨迹全链通过。
- 未确认 CRS、删除调度时没有自动清洗，是遵守上一版批准边界，不应批评为“应该随便猜一个先跑”。
- LIVE、REPLAY、MOCK、构造测试与历史记录有明确区别。没有发现把缺失的 B/C 输出补造出来的证据。
- Notebook 真实代码有重新读取原始数据与重算的路径；第二份只重算历史 source_evidence，已明确不代表模型或完整闭环成功。
- 阶段架构 SVG 明确 A 成功、B 失败、C 未调用和虚线未发生。渲染后可读，没有用完成态掩盖失败。它仍只是阶段结构图，不是最终架构已验证的证明。

## 3. 新发现与核验结果

### SR-01｜审核前先去重/筛选，导致错误地通过覆盖检查（必须修复）

代码：`task1/workflow/tools.py`，`verify_profiles/recompute_check` 分支。

当前先构建：

```python
by_id = {p['record_id']: p for p in previous_profiles if p['record_id'] in subset}
selected = [by_id[k] for k in subset]
```

然后才调用独立审核。重复 ID 被覆盖，多余 ID 被过滤，原始覆盖错误被掩盖。

本轮精确源码构造探针：输入应有 1 条记录，却提供 2 行重复 profile。直接调用 independent_profile_review 返回 REJECTED/RECORD_COVERAGE；经 verify_profiles 或 recompute_check 接口却返回 VERIFIED。添加 foreign 记录也得到同样误放行，recompute_check 甚至 exact_match=true。

修复：在任何字典归一化、重排或子集处理前检查原列表结构、精确 ID 集、唯一性及覆盖；只有集合已经合法，才按 canonical 顺序比较。若未来允许子集，要有明确声明的作用域，不能静默丢行。

这不是认定已发布 pilot 有重复行；是验证器承诺存在缺口，A08 必须重开。

### SR-02｜缺失值和非正常事件会逃逸为未归一化异常（必须修复）

代码：`diagnostics.duplicate_details`、`provider.visible_events`、`CodexProvider.call` 及 controller 的异常边界。

本轮实际探针：

1. `[[None,1], [[0,0],[0,0]]]` 结构长度对齐，但 duplicate_details 直接计算 `1-None`，抛 TypeError。
2. JSONL `{"type":"item.started","item":null}` 导致 AttributeError，而不是 ProviderError/结构化协议失败。
3. 注入启动进程 OSError 后，call 目录只有 input.json，没有终止 receipt；异常不是 ProviderError。controller 只捕获 ProviderError 的这一路因此不能保证形成结束状态和清楚的失败证据。
4. 注入携带已产生可见日志的 TimeoutExpired 后，留下泛化 receipt，但部分 stdout/stderr 被丢弃。不得为了补日志保存隐藏推理或秘密；应安全提取可见部分与解析错误位置。

修复：验证输入结构与可计算性；对正常可预期的 I/O、启动、解析、工具失败统一生成事实正确的终止状态和失败回执。不能 catch 后改成成功，也不能无理由自动重提结果未知的模型请求。

### SR-03｜当前完整处理链仍未实现，并非只差解锁配置（必须补完但保留语义门控）

代码事实：
- `geometry.denoise_trajectory` 始终抛出 MethodUnresolved。
- `tools.execute_tool('baseline')` 不检查已批准后是否应运行，固定返回 BLOCKED。
- controller 的 PHASE_ACTIONS 都是诊断动作，没有处理链；提示词与结束状态也写死真实 baseline 仍 BLOCKED。

在构造策略中把 processing_status 改为 APPROVED_FOR_REAL_INPUT、blocking_ids 清空，baseline 仍返回 BLOCKED。此测试不表示真实 CRS 得到批准，只用于证实入口确实是占位实现。

修复：将“前置条件检查”和“批准后的实际执行”分开，接通已经获准的方法与工具；未知事实继续阻断。不能只把 BLOCKED 字样换为 VERIFIED，也不能把通过数据合同检查当成执行完成。

### SR-04｜证据引用和反馈关联检查仍过弱（静态发现，须补用例）

`validate_request` 只检查 evidence_refs 非空；后续反馈只要与任意既有工具/审核 ID 有交集即可。它没有核验来源路径/片段是否存在、是否来自当前版本、是否真的指向触发本轮动作的审核意见。

`source_evidence` 的主要 payload 是 policy 中已有语义说明的回显，并非重新阅读教师原文或解决来源冲突。A 的真实输出也将所列路径称为待核查来源；不应把这个工具成功写成已经核实 CRS。

修复：保持轻量，使用已核实片段/ID注册表与当前 run 的回执引用；区分 contract snapshot 与 source verification。下一轮动作要绑定触发它的真实审核/工具结果。无需为此建设通用检索平台。

### SR-05｜请求预算修复尚未通过当前版本的真实验证（原已知失败，继续保留）

实际 run03-B JSONL 有 9 条 reconnect 展示通知与 1 次 fallback；receipt.stderr 中则有两轮 1/5 至 5/5，共 10 条 sampling retry 日志。两者统计对象不同，均不能直接换算成精确 HTTP 请求数或计费次数。

当前 provider 增加了 request_max_retries=0、stream_max_retries=0、supports_websockets=false，但尚无该源码的真实调用证明；communicate() 在结束或超时后才返回，不是在发现第一条重试时立即停止。

OpenAI 官方配置说明包含这三类设置，但不证明其在用户已安装版本/实际 provider 路径中的生效范围，也不证明能覆盖 workspace routing 的所有内部行为。后续必须核对实际配置、流式可见事件、进程组终止和版本；先离线故障测试，再做小而有界的连通性探针。

不得把网络/账户路由失败归因为已证实的工作目录错误，也不要通过重登录、删认证、换 API、关 TLS 等无依据动作试到成功。

## 4. 二重验收状态

| 原验收项 | GPT 本轮结论 |
|---|---|
| A01/A03/A18 | 远程提交与原始 Git 树保持情况已核实；用户当前本地 clean 与认证状态仅有其日志，不声称远程可以直接证明本地 |
| A02/A04 | 任务和未知语义处理原则成立；缺少研究附件不等于教师材料缺失，附件可由本次交接补齐 |
| A05/A06/A11 | BLOCKED；真实完整处理链还未完成，且存在 SR-03 的代码待补部分 |
| A07 | 认可平面 DP 和相应测试的阶段成果；不扩展为真实米制轨迹已通过 |
| A08 | REVISE；独立几何检查有价值，但 profile 核验工具存在 SR-01 误放行 |
| A09/A12 | BLOCKED；A 成功、B 失败、C 未发生，尚无完整真实反馈链 |
| A10 | REVISE；原有防护仍保留，但 SR-02/SR-04 需补齐 |
| A13 | FAIL 保持；当前真实预算验证缺失，不能由离线测试冲销 |
| A14 | 已有模式分类和诚实失败报告认可；失败记录完整性按 SR-02 重验 |
| A15 | 只认可目前允许的诊断与已发生工具复算；不是三步处理成果 |
| A16 | 架构 SVG 已检查，原始图/PDF 全格式未重新取齐；不得扩大视觉验收范围 |
| A17 | 未发现本提交开始 Goal2/3 的证据；后续保持边界 |

这里的 REVISE 不是说所有现有测试失效，而是新的真实反例要求补回归测试与重新验收。

## 5. 下一步：仍属于 Goal 1 修复/补完

工程线立即进行：SR-01/SR-02 → 引用/状态绑定 → 有条件处理链接线 → 离线 provider 防护 → 受控连通性探针 → 实际三角色诊断反馈 → 若语义和方法获批，再跑同一 pilot 完整基线。

研究线不伪造事实：
- CRS：需要绑定这份 JSON 的来源证据。保持 UNKNOWN，不能为了跑通改成 VERIFIED。若资料确实没有说明，应向教师/数据提供方提出一个聚焦问题；本轮不代发邮件。
- 删除调度：GPT 当前推荐“一次计算候选、同时删除；不可计算方向保留并标记；不循环删至收敛”，因为最接近明确的候选谓词且避免扫描顺序和额外迭代引入的变化。但这是建议，不是教师已写明的事实，也不是用户已批准的新方法。本次修复可做隔离构造测试，真实采用等待明确确认。
- 距离：数据基准确认后再固定统一距离/投影及误差适用范围。不能用批准算法代替确认数据事实。

现有 .venv 与临时 CLI 先保留，记录路径、版本和可恢复安装方法；不要在修复前清理或无必要升级。

三份先前 Codex 未找到的研究文件，本次交接包提供真实副本。导入并记录 hash，不重写成新研究、不要求重复广泛检索。

## 6. 主要远程证据入口

所有下列路径都以固定提交为准：
`https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/c2e3ffe2f5af92ee03dac16a2865ec7c42f576e0/`

- task1/evidence/goal1/REVIEW_PACKET.md
- task1/evidence/goal1/tests/CHECK_MATRIX.md
- task1/evidence/goal1/tests/INDEPENDENT_CONTROL_REVIEW.md
- task1/docs/goal1/CONTRACTS.md
- task1/config/goal1.json
- task1/workflow/{geometry,evaluation,diagnostics,tools,controller,provider,io}.py
- task1/evidence/goal1/runs/call_summary.json
- task1/evidence/goal1/runs/g1-live-20260926-03/calls/g1-live-20260926-03-01-research/response.json
- task1/evidence/goal1/runs/g1-live-20260926-03/calls/g1-live-20260926-03-02-execution/{visible_events.jsonl,receipt.json}
- task1/notebooks/01_baseline_and_audit.ipynb
- task1/notebooks/02_agent_loop_recompute.ipynb
- task1/figures/goal1/{figure_manifest.json,goal1_loop.svg}

官方参考（本轮实际访问；实现时仍须核对已安装版本）：
- https://developers.openai.com/codex/config-reference/
- https://developers.openai.com/codex/noninteractive/
- https://developers.openai.com/codex/auth/

## 7. 最终判断

Codex 的 PARTIAL_BLOCKED 如实反映主要状态，值得保留。已有工作无需推倒重来，但不能进入 Goal 2：必须修复本次发现的审核与异常闭合缺口，补齐处理入口及真实角色反馈，并解决/明确隔离研究前提。下一次依然执行代码—结果绑定、自检、push、GPT 远程复核，不自报总体 PASS。
