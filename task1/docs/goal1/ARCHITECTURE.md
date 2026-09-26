# 三角色与确定性控制器

本实现服务实验一 Goal1，采用一个现有访问方式：`codex exec` + 当前 ChatGPT 登录。每次 role call 都有独立的 CLI thread/context，不让一次模型输出表演三个角色。工程材料核查子代理与 runtime 角色调用分开记录，不计作三角色运行证据。

| 项目 | A 研究诊断 | B 处理实验 | C 质量核查 |
|---|---|---|---|
| Responsibility | 需求缺口/证据/后续动作 | 将批准计划变成实际工具请求 | 独立数值审核后判断支持范围与缺口 |
| Input | 需求、合同、原始诊断、反馈 | A计划、固定pilot与参数、工具回执 | 原始/派生句柄、固定合同、工具结果 |
| Output | TaskPlan/补诊断/ResearchEscalation | 工具请求、执行回执与失败 | ReviewCard摘要、问题与补查请求 |
| State | call/thread、依据、反馈ID | 请求schema、执行/受阻 | 硬检查、局限、后续请求 |
| Tools | source_evidence/profile/time_boundaries/duplicate_details/recompute | profile/time_boundaries/duplicate_details/recompute；baseline经门控 | verify_profiles/recompute/source_evidence |
| Allowed autonomy | 在白名单里选择有据补查 | 执行固定输入/合同的诊断与复算 | 挑出未证实论断/请求复核 |
| Forbidden autonomy | 猜CRS/改标准/批准新方法 | 改值/任意shell/运行时修核心代码 | 改候选/评价代码/删失败/单靠意见PASS |
| Handoff | 初始计划给B；收到C后发下一任务 | 回执给C | 真实反馈交回A；最终待研究审核 |
| Verification | 引用实际来源与反馈ID | schema、scope、hash、工具实际输出 | 与profile独立的直接计数实现、复算 |
| Escalation | 未知语义/新算法/未冻结阈值 | 依赖缺失/越界/工具失败 | 证据不足/审核异常/研究歧义 |
| Failure handling | 保留失败、阻断受影响分支 | 旧产物不覆盖，明确预算 | 拒绝错误输出但允许正确诊断通过 |

控制器为普通 Python，不是第四个 LLM。固定阶段为 A来源核查→B七例诊断→C独立核查→反馈A→A选择补查并实际执行→C复算裁决。初始阶段的工具依赖固定，反馈阶段由模型从批准的补查工具中选择，禁止改参数。每一步的实际 response 与 tool ID 会写入 `events.jsonl`、`checkpoint.json`、`manifest.json`；图由这些实现阶段和实际run生成。

## 权限与状态

模型在临时工作目录，只得到脱敏任务输入、JSON Schema和可见结果；`--ignore-user-config`仅隔离该进程工具配置，CLI认证仍复用现有登录。`--sandbox read-only`，shell/unified_exec/code_mode_host/apps/plugins/multi_agent/hooks/web等关闭，不运行模型返回的路径、代码或命令。工程主线程可改任务代码，runtime不可。没有 `eval`/shell拼接。实际sandbox探针写临时保护文件被 `Read-only file system` 拒绝。

控制器为所有请求验证完整schema、角色白名单、Goal/指标/语义版本、pilot全覆盖、反馈引用、路径和符号链接、输入/父版本/产物哈希。留出不在pilot，无读取/调参动作；SEARCH_ONLY禁止进入LLM调用。候选与审核产物都只由控制器写新文件。原始数据和批准合同前后哈希检查补充OS权限防护。

状态区分 PLANNED、DISPATCHED、RUNNING、EXECUTED、VERIFIED、QUALITY_ACCEPTED、REJECTED、NEEDS_REVIEW、BLOCKED。当前没有自动进入QUALITY_ACCEPTED的路径；退出0和有效JSON都只证明执行/格式，硬审核独立进行。

## 预算、恢复、失败

七条pilot（上限12），串行，计划最多8次模型尝试、18次工具请求，单请求180秒；所有run共享ledger。本轮外层共4次CLI派发，实际成功接入控制器1次。run03的B调用出现9条可见重连通知和1次WebSocket→HTTPS切换，底层请求总数unavailable；原计数器只数CLI进程，**未控制住内部重试**。这是真实失败，不以新的run_id清零。最终合同和持久ledger均冻结LIVE，待GPT/用户审核。

修复后的provider添加官方request/stream重试0和关闭WebSocket配置，并用独立进程组在超时或中断时杀死wrapper与其子进程。配置的真实网络行为尚未复验；只完成离线反例测试，不以此抹去本轮预算护栏失败。CLI不自动切换模型、供应商或Mock。

工具产物按请求、输入和合同哈希去重，使用独占写入；缓存必须已有登记，再核对独立保存的文件hash、父版本、输入和状态。恢复必须有预算派发登记及input_hash，并重新解析visible_events，核对receipt/response/schema/上下文，密封四个文件hash；单独预置response不能成为LIVE。中断时结果不明则阻断，不自动重发。哈希链不是签名，也不是真实性的充分证明；还须看实际命令、CLI事件、调用输出与离线复算。

Run All 默认 REPLAY/RECOMPUTE，重新读取原始JSON并执行保存决策对应的数值工具，逐对象哈希比较；new_model_calls=0。MOCK_TEST只用于测试目录，不准进入LIVE。真实模型输出的原因只是复核意见，不能替代独立硬检查。请求ID/模型快照不可见时为unavailable；不保存隐藏推理。

## 本轮实际覆盖

run01旧CLI被服务拒绝；run02新CLI返回结构化研究结果，但工程解析器误把预期禁用code host的提示当失败，未派发工具；修复后run03 A真实完成来源核查请求及tool，B网络路由失败，C未调用，feedback→A未发生。已保存失败，不回填假的角色输出。旧运行绑定其已提交CODE_SHA，后续代码修复没有冒充对旧LIVE结果的重跑；工作版Notebook从Git恢复旧源码复算仅有的一项来源核查，再明确分开当前数值工具的离线复算。
