# Goal 1 独立控制器审查

审查对象是冻结代码 `d1444eb07035ef651a36a3e89269f004186581df`，不是之后修复的自动验收。审查过程中未修改 workflow 源码、未运行 live、未读取认证文件。所有新增挑战都在临时目录使用 `CONSTRUCTED_FIXTURE / ENGINEERING_TEST`，provider 方法被替身明确禁止执行；实际模型调用为 0。

初审结论：现有正向/拒绝测试通过，但新增反例暴露恢复真实性、缓存校验、拒绝状态、事件解析及子进程终止缺口。不能以原有测试全绿给这些承诺标 PASS。主线程随后停止 live 并修复；**修复后独立验证见文末**。原始反例保留，旧 live 运行不能冒充新源码完整闭环通过。

## 审查范围及已有测试

实际读取 [controller.py](../../../workflow/controller.py)、[provider.py](../../../workflow/provider.py)、[recompute.py](../../../workflow/recompute.py)、[tools.py](../../../workflow/tools.py)、[test_control.py](../../../tests/test_control.py)，并为核实依赖读取 `io.py`、`diagnostics.py`、`goal1.json`、`pilot.json`、本轮 npm Codex 的启动 wrapper 与现有 sandbox probe。

```bash
.venv/bin/python -m pytest task1/tests/test_control.py -q
```

实际输出：`29 passed in 0.29s`。这些测试确实覆盖合法诊断、schema/holdout/未知方法拒绝、原始数据/合同哈希、`read_tool()` 篡改拒绝、注入失败后的旧产物保存、同一 base 跨 run_id 预算累计、模型不可用不能成功，以及部分 JSONL 异常。它们未覆盖下面的新反例。

冻结版本文件 SHA256：

| 文件 | SHA256 |
|---|---|
| controller.py | `738e6d0bcb53e24658d8e8fd4648db609d7d7492f0f8c9e56f48b28530edc68d` |
| provider.py | `2686c7e68b38fb8370b8488e1f00649c224cefba01a4bba5a4a9f6f7b66df021` |
| recompute.py | `4c198a016adec8554602c9ad04e0446bb90866ed970789834b96c51ebbec9b56` |
| tools.py | `7504b20b7229b5a73ee835ce06b65c26273ae68b16f96c232ac347b352d85d3f` |
| test_control.py | `89f90055e43b6c6b7f20ddece8a6545c92be1c85f1ba49a9b1a818e9f50bb16c` |

## 需修复的主要发现

行号均对应上面的冻结提交。

| ID | 优先级与代码位置 | 实际证据、影响 | 最小修复方向 |
|---|---|---|---|
| CR-01 | 高；controller.py:211–235 | 已存在 `response.json` 和空 `receipt.json` 即可走恢复分支；不要求 `visible_events`、真实已派发状态或模型预算记录。隔离反例返回 `mode=LIVE / checkpoint=VERIFIED / recorded_calls=1 / model_attempts=0 / thread_id=unavailable`，工具被标 `CURRENT_RUN_REAL_DATA`。这是恢复准入漏洞，不是对真实 run03 伪造的指控。影响 G1-A13/A14 及模型证据完整性。 | 将恢复绑定已派发 call、预算、输入/合同/代码；核对 receipt 身份/状态/哈希，重新解析保存事件的当前阶段 schema，并比较响应内容；无完整证据则停止，不能自动当新 live 成功。 |
| CR-02 | 高；controller.py:146–172 | 缓存分支只核对 `request_hash` 与文件内部自带 `output_sha256`，没有复用 `read_tool()` 的文件/父版本/状态检查。篡改 `zero_dt=999`、`status=QUALITY_ACCEPTED` 并重算内部 hash 后，`dispatch()` 返回伪值且 checkpoint 变 `QUALITY_ACCEPTED`。后续单独 `read_tool()` 会拦文件哈希，但已发生错误派发回执/状态。影响 G1-A10/A13。 | 所有重用路径统一验证已登记文件哈希、父版本、输入、代码、请求身份和状态；崩溃留下的未登记产物应验证后确定性复算或停止，不能重新信任其自带 hash。 |
| CR-03 | 高；controller.py:239–247 | 注入确定性工具返回 `REJECTED` 后，工具产物保留拒绝，但 `run()` 无条件递增 phase 并把 checkpoint 写成 `VERIFIED`。实际反例 `tool_status=REJECTED / checkpoint_status=VERIFIED / phase=1`。最终没有质量准入，但阶段工程状态失真。影响 G1-A10/A12/A13。 | 状态由实测工具状态分支决定；失败应保留拒绝/受阻原因并触发相应反馈，不能无条件转 VERIFIED。 |
| CR-04 | 中高；provider.py:51–77 | `item.started`/`item.updated` 未检查工具类型。构造 `item.started(command_execution)` 加正常完成消息可通过 `parse_response()`，工具启动事件被静默丢弃。现有测试只检查 `item.completed(command_execution)`。当前 CLI 确有只读和禁工具配置；此发现是事件侧防线不完整，不证明发生过实际越权执行。影响 G1-A10/A14。 | 对 started/updated/completed 的工具事件都拦截并留可见事件；未知结构明示失败，避免“strict parser”声明超过实现。 |
| CR-05 | 高；provider.py:129–134；npm wrapper 的 `spawn`/signal forwarding | `subprocess.run(timeout=...)` 杀直接进程，不保证 npm Node wrapper 启动的原生子进程退出。wrapper 只转发 SIGINT/SIGTERM/SIGHUP，SIGKILL 无法转发。无网络构造进程：父超时 0.1 秒、实际父等待 0.101 秒，但 0.35 秒后子进程仍成功写 marker。不能将 timeout 返回当所有网络工作停止。未测试/声称真实 Codex 子进程遗留。影响 G1-A13 与停止预算。 | 使用独立进程组及组终止/回收，或可靠管理原生进程及后代；离线用父子进程 fixture 验证超时后无后续副作用。 |
| CR-06 | 高；controller.py:95–103；provider.py 的 CLI 参数 | 外层仅按一次 CLI 调用计费预算/尝试；初始配置未控制 CLI 内部 transport 重连。真实 run03-B 的可见记录含 9 条重连通知、1 条 WebSockets→HTTPS fallback、1 条最终 routing failed。不能由这些事件推算准确的 HTTP 请求数或模型完成数；但不能声称内部重试已受 2 次护栏约束。影响 G1-A13。 | 按本机版本核实可用内部重试上限，保存可见重连/transport 切换，无法确证则停用 live；不得借更换 run_id 或隐藏 fallback 复位预算。 |

CR-01/02 的攻击前提是运行产物被损坏或由测试外部修改；真正模型在只读、禁工具上下文中没有这项写权限。用户要求的故障/篡改挑战仍应覆盖这些恢复入口。这里不设计账户级或全磁盘攻击平台。

## 次级问题与可解释边界

- **CR-07 请求顺序不一致造成假拒绝。** `validate_request()` 按集合校验同一 pilot；`recompute_check` 却按请求列表顺序生成 profiles，再与旧顺序整体 hash 比较。两个合法记录 `[a,b] → [b,a]` 的构造结果为 `REJECTED / independent_errors=[] / exact_match=false`。可固定 canonical pilot 顺序，或按记录 ID 对齐比较；不要让模型列表重排成为数据错误。
- **CR-08 构造数据嵌套分类失真。** `diagnostics.time_boundaries()` 硬编码 `CURRENT_RUN_REAL_DATA_DIAGNOSTIC`。`execute_tool(...classification='MOCK_TEST')` 的外层为 MOCK_TEST，内层仍是该真实数据标签。应传递完整分类。当前反例是构造工具产物，不能放进真实运行统计。
- **CR-09 独立 profile 审核范围需明确。** `independent_profile_review()` 验证部分点数/差分/重复计数，但不检查 `invalid_timestamps / dt_counts / time_span_raw` 等字段。把这三项改成错误值，独立审核仍返回 VERIFIED。后续完整 `recompute_check` 可以发现整体差异，但最后阶段也允许只选 `verify_profiles`。应补全所承诺字段，或逐字段报告已核验/未核验，不能把局部审核称全部 profile 正确。
- **复算的结论范围。** `recompute_run()` 确实执行确定性工具，检查原始数据、合同、源文件和已登记工具 artifact 的 hash；它不调用模型。然而它未验证保存的模型事件及反馈链，只凭 manifest 的 `mode=LIVE` 接受“来自 live”的标签。其 VERIFIED 至多表示列出的工具结果重算一致，不足以独立证明三角色、真实反馈或整个源 run 成功。可与 CR-01 共用证据验证逻辑。
- **事件链。** `event()` 生成 hash 链，但恢复/复算没有验证整条事件链。该链不能被描述为已经自动验证的防篡改证据。
- **串行预算边界。** 当前 ledger 的“读—加一—原子替换”在声明的串行上下文有效，现有跨 run_id 测试是真实正例；它不实现并发锁。本 Goal 不需要扩展并发平台。

## 新挑战的实际输出

第一组通过 shell heredoc 执行 `.venv/bin/python -`；临时文件全部位于 `TemporaryDirectory`，结束后删除，未接触真实 runs。`CodexProvider.call` 被设置为一经调用即抛 `AssertionError('NETWORK_CALL_FORBIDDEN')`，实际调用计数 0。

```json
{
  "classification": "ENGINEERING_TEST",
  "input_source": "CONSTRUCTED_FIXTURE",
  "live_model_calls": 0,
  "unproven_response_recovery": {
    "checkpoint_status": "VERIFIED",
    "recorded_mode": "LIVE",
    "recorded_calls": 1,
    "thread_id": "unavailable",
    "model_attempts": 0,
    "visible_events_exist": false,
    "tool_classification": "CURRENT_RUN_REAL_DATA"
  },
  "tampered_cached_tool": {
    "dispatch_accepted": true,
    "checkpoint_status": "QUALITY_ACCEPTED",
    "returned_zero_dt": 999,
    "later_read_tool_rejected": true
  },
  "rejected_status_overwritten": {
    "tool_status": "REJECTED",
    "checkpoint_status": "VERIFIED",
    "phase": 1
  },
  "guarded_provider_invocations": 0,
  "unexpected_started_tool": {
    "parse_accepted": true,
    "saved_event_types": ["thread.started", "item.completed", "turn.completed"]
  }
}
```

进程挑战实际输出：

```json
{
  "classification": "ENGINEERING_TEST",
  "input_source": "CONSTRUCTED_PROCESS_FIXTURE",
  "model_calls": 0,
  "configured_timeout_seconds": 0.1,
  "actual_parent_wait_seconds": 0.101,
  "timeout_raised": true,
  "child_wrote_after_parent_timeout": true,
  "observation_delay_seconds": 0.35
}
```

最先一轮在父进程刚超时即检查 marker，尚未等到构造子进程的写入时刻，输出 false；这不足以证明子进程被终止。第二轮将观察延后到明确的写入时刻以后，得到上述 true。没有执行 Codex 来试验该缺口。

次级挑战实际输出：

```json
{
  "classification": "ENGINEERING_TEST",
  "live_model_calls": 0,
  "same_records_reordered": {"status": "REJECTED", "independent_errors": [], "exact_match": false},
  "fixture_time_partition": {"outer_classification": "MOCK_TEST", "nested_classification": "CURRENT_RUN_REAL_DATA_DIAGNOSTIC"},
  "unverified_profile_fields": {"audit_status": "VERIFIED", "tampered_fields": ["invalid_timestamps", "dt_counts", "time_span_raw"]}
}
```

## 可复现的主要挑战命令

以下是隔离挑战的核心可执行版本，只适用于审查对应的冻结源码；修复后预期应转为拒绝或者不再出现错误状态。它不是 live 入口，禁止移除 provider 替身。

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
from task1.workflow import controller as c, tools
from task1.workflow.io import CONFIG, read_json, write_json, digest, object_hash
from task1.workflow.provider import CodexProvider, visible_events, parse_response, response_schema

def request(action, role, call):
    return {'role':role,'call_id':call,'action':action,'record_ids':['fixture'],
            'feedback_refs':[],'evidence_refs':['CONSTRUCTED_FIXTURE'],
            'summary':'Independent review fixture','reason':'Exercise recovery boundary',
            'request_status':'PROPOSED','candidate_for_future_review':None}

with TemporaryDirectory(prefix='sc-g1-control-review-') as temp:
    root=Path(temp)
    data=root/'raw.json'
    write_json(data,{'fixture':[[0,0,10,50],[[0,0],[1,0],[1,0],[2,1]]]})
    policy=read_json(CONFIG);policy['raw_sha256']=digest(data)
    pp=root/'policy.json';write_json(pp,policy)
    pilot=root/'pilot.json';write_json(pilot,{'ids':['fixture']})
    with patch.object(c,'DATA',data),patch.object(tools,'DATA',data),patch.object(CodexProvider,'call',side_effect=AssertionError('NETWORK_CALL_FORBIDDEN')) as no_live:
        live=c.Controller('forged-response',mode='LIVE',base=root/'runs1',policy_path=pp,pilot_path=pilot)
        call='forged-response-01-research';folder=live.directory/'calls'/call
        write_json(folder/'response.json',request('source_evidence','research',call))
        write_json(folder/'receipt.json',{})
        state=live.run(provider=CodexProvider(),stop_after=1)
        print('CR-01',state['status'],read_json(live.ledger_path)['model_attempts'])

        cached=c.Controller('cache-tamper',mode='MOCK_TEST',base=root/'runs2',policy_path=pp,pilot_path=pilot)
        q=request('profile_pilot','execution','cache-call')
        cached.dispatch(q,'execution','cache-call')
        artifact=cached.directory/cached.state['tools'][0]['artifact']
        receipt=read_json(artifact)
        receipt['output']['result']['summary']['zero_dt']=999
        receipt['output']['status']='QUALITY_ACCEPTED'
        receipt['output_sha256']=object_hash(receipt['output']);write_json(artifact,receipt)
        reused=cached.dispatch(q,'execution','cache-call')
        print('CR-02',cached.state['status'],reused['output']['result']['summary']['zero_dt'])

        rejected=c.Controller('rejected-tool',mode='LIVE',base=root/'runs3',policy_path=pp,pilot_path=pilot)
        call='rejected-tool-01-research';folder=rejected.directory/'calls'/call
        write_json(folder/'response.json',request('source_evidence','research',call))
        write_json(folder/'receipt.json',{})
        real_execute=c.execute_tool
        def rejected_tool(*args,**kwargs):
            value=real_execute(*args,**kwargs);value['status']='REJECTED'
            value['engineering_fault']='CONSTRUCTED_REJECTION';return value
        with patch.object(c,'execute_tool',side_effect=rejected_tool):
            state=rejected.run(provider=CodexProvider(),stop_after=1)
        print('CR-03',state['tools'][0]['status'],state['status'])
        assert no_live.call_count==0

response=request('source_evidence','research','parser-fixture')
stream=[{'type':'thread.started','thread_id':'CONSTRUCTED_SESSION'},
        {'type':'item.started','item':{'type':'command_execution','id':'CONSTRUCTED_COMMAND'}},
        {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(response)}},
        {'type':'turn.completed','usage':{}}]
visible=visible_events('\n'.join(map(json.dumps,stream)))
print('CR-04',parse_response(visible,response_schema('research','parser-fixture',['source_evidence']),0)[0]==response)
PY
```

进程边界的无网络复现：

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess,sys,time
with TemporaryDirectory(prefix='sc-g1-timeout-review-') as temp:
    marker=Path(temp)/'child-survived.txt'
    child='import time; from pathlib import Path; time.sleep(0.3); Path('+repr(str(marker))+').write_text("CONSTRUCTED_CHILD_SURVIVED_PARENT_TIMEOUT")'
    wrapper='import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",'+repr(child)+']); time.sleep(5)'
    try:
        subprocess.run([sys.executable,'-c',wrapper],capture_output=True,text=True,timeout=.1)
    except subprocess.TimeoutExpired:
        pass
    time.sleep(.35)
    print('CR-05 child_after_parent_timeout',marker.exists())
PY
```

## 真实 run03 的只读核验

独立读取了两个可见回执；未重新调用 provider：

- [研究角色 receipt](../runs/g1-live-20260926-03/calls/g1-live-20260926-03-01-research/receipt.json)：exit 0，`VERIFIED_STRUCTURE_ONLY`；1 个 thread、1 个完成 turn、1 个可见 agent message。对应工具只有 source_evidence。该真实调用存在，不因构造恢复漏洞而否认它。
- [执行角色 receipt](../runs/g1-live-20260926-03/calls/g1-live-20260926-03-02-execution/receipt.json)：exit 1，BLOCKED；[visible_events](../runs/g1-live-20260926-03/calls/g1-live-20260926-03-02-execution/visible_events.jsonl) 保留 workspace routing discovery failed、9 条明确重连通知、1 条 transport fallback、最终失败。
- 未见三个真实角色完成、质量审核角色调用、反馈后二次工具闭环的证据。因此 G1-A09/A12 不能仅由这些已有材料标 PASS。原始数据米制处理受阻还独立影响 G1-A11。

修复是普通工程职责；CR-01 至 CR-09 不要求用户决定新的研究方法。真实模型环境恢复和重新运行许可/预算仍须遵守已批准边界，不能靠本次构造审核器挑战替代 live 验收。

## 修复后独立复查

主线程完成源码修复后，本审查线程仍保持只读，只更新本文；没有发起模型调用。

第一轮修复后，独立构造挑战还发现两项残余：保存事件中的 `item.completed(command_execution)` 可绕过恢复检查，以及 `KeyboardInterrupt` 后构造子进程仍能写入 marker。实际输出为：

```json
{
  "classification": "ENGINEERING_TEST",
  "input_source": "CONSTRUCTED_FIXTURE",
  "model_calls": 0,
  "saved_completed_tool_is_rejected": false,
  "keyboard_interrupt_propagated": true,
  "child_wrote_after_interrupt": true
}
```

该挑战在 `finally` 中终止并回收自己创建的进程组，没有留下后台任务。主线程再收紧保存事件的类型、已知 capability 消息，并让所有异常中断路径终止进程组。

第二轮修复后实际执行全套工作模块测试：

```bash
.venv/bin/python -m pytest task1/tests -q
```

实际输出：

```text
........................................................................ [ 66%]
....................................                                     [100%]
108 passed in 1.15s
```

新增 tests 不只检查文件存在：它们验证未派发响应被拒、缺失/篡改模型证据被拒、正确恢复恰执行一次且不新增模型调用、缓存自带 hash 不能取代登记 hash、REJECTED/BLOCKED 不前进、工具启动事件拒绝、超时后子进程无写入、合法换序复算通过、fixture 分类保持、预算冻结跨 run_id 生效、待审核请求不执行，以及独立 profile 多字段错误被发现。

此外，本审查线程重新执行自己的保存事件/KeyboardInterrupt 反例，实际输出：

```json
{
  "classification": "ENGINEERING_TEST",
  "input_source": "CONSTRUCTED_FIXTURE",
  "model_calls": 0,
  "saved_completed_tool_is_rejected": true,
  "saved_completed_tool_error": "UNEXPECTED_SAVED_TOOL_OR_DIAGNOSTIC",
  "keyboard_interrupt_propagated": true,
  "child_wrote_after_interrupt": false
}
```

人工中断挑战的具体机制：真实创建一个仅会在临时目录延迟写 marker 的父子进程；把首次 `Popen.communicate()` 替为等待 0.1 秒后抛 `KeyboardInterrupt`，随后恢复原 communicate 以便回收；等待超过子进程计划写入时刻后检查 marker，最后再次安全回收测试进程组。没有使用 Codex 或网络进程验证此机制。

| 发现 | 修复后检查 | 当前结论 |
|---|---|---|
| CR-01 | 需要已计数派发登记、预存 input hash、合法四文件、当前阶段 schema、已保存事件一致，再密封文件 hash；正例和多种损坏反例均运行 | 对上述构造恢复场景修复通过；不是新模型实测 |
| CR-02 | 缓存必须已登记并调用统一 `read_tool()`；篡改缓存不再返回假成功 | 离线反例已拒绝 |
| CR-03 | 非 EXECUTED/VERIFIED 结果保留原状态，不前进 phase | REJECTED/BLOCKED 两例均通过 |
| CR-04 | started/updated/completed 工具事件和未知事件拒绝；保存事件只能是合法已过滤类型 | 初始和恢复反例均拒绝 |
| CR-05 | 独立进程组、超时与 BaseException 路径终止/回收 | 超时回归及独立 KeyboardInterrupt 挑战均通过 |
| CR-06 | CLI request/stream retry 配为 0，关闭 WebSocket；policy 与 ledger 冻结 live | **只有离线护栏验证；新 transport 没有真实调用验证，保持 BLOCKED** |
| CR-07 | 按记录 ID 对齐旧 profiles 和新请求顺序 | 合法换序复算通过 |
| CR-08 | 显式传递 classification 到时间分段诊断 | 嵌套 MOCK_TEST 标签正确 |
| CR-09 | 独立计算时间/坐标无效数、位置可计算性、时间跨度、差分分布/极值和 issues | 新增字段篡改反例均拒绝 |

第二轮独立验证时的文件 hash：

| 文件 | SHA256 |
|---|---|
| controller.py | `14def81bd1c1a16adff69510e1830de9c2eac343af5ffbdcbe76b21a28e29e6a` |
| provider.py | `6c42840f03279e3b33fb119034f67cec56b7084053e500bf27e4d6985fc755f4` |
| tools.py | `1b84da796696cc17abd5bc837fd7a2e05af3eef462f453742801d9a605dc0de5` |
| diagnostics.py | `9d4541acb2880b6f36c2470bef15914f85ef83458c617bcd5d9f76ce61878786` |
| test_control.py | `f036ab50b7ba7e60740fcab2a46f0eb94fec6e2589ec5347d5fed953225c0fd4` |

仍应保留的结论边界：事件链生成不等于完整链已自动审核；`recompute_run()` 的一致性结论不能替代模型来源和反馈链审核；保存 evidence 的完整性依赖受保护控制器目录与已登记 hash，不能声称防御任意可改全目录的外部攻击者。真实 run03 只完成研究角色及 source_evidence，执行角色实际受阻；离线 108 项通过不升级 G1-A09/A11/A12，也不解除真实输入的 CRS/去噪语义限制。
