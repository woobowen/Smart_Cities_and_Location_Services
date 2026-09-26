# Notebook extraction: task1/作业/作业/任务3_LLM辅助评估清洗.ipynb
Source SHA256: 4ecffe64024e002c0cffe7830e18b5f6ded04cd5aa9dd645d6798fc9b0715add
Classification: teacher/starter source; all saved execution counts and outputs are HISTORICAL.
Notebook metadata: {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.9.6"}}

## Cell 0 (markdown), execution_count=None
Cell metadata: {}
```text
# 任务③：LLM 辅助的轨迹清洗评估工作流

本 notebook 演示一条完整闭环：

```
诊断 → 检索记忆 → LLM 提议 → 执行 → 核验 → 记忆
```

**核心设计**：LLM 只负责"选工具、提参数、说依据"；
所有数值计算在确定性代码里；**提议好不好由 regret 定量判定**，
而不是靠人去读一段解释。

只有通过核验的建议才允许写入记忆——这是整个工作流的准入闸门。

---
### 目录
1. 环境与数据
2. 单条轨迹完整闭环（逐步展示 trace）
3. 出图：清洗前后叠加 / 异常分布 / 热力图
4. 消融实验：llm-only / search-only / llm+search / llm+memory+search
5. 记忆的可解释视图
6. 切换到真实 LLM API

```
## Cell 1 (markdown), execution_count=None
Cell metadata: {}
```text
## 1. 环境与数据
```
## Cell 2 (code), execution_count=None
Cell metadata: {}
```python
import os, sys, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath("."))

# matplotlib 需要可写缓存目录
os.environ.setdefault("MPLCONFIGDIR", os.path.abspath(".mplcache"))

from traj_agent.core import traj as tm, diagnosis, params as params_mod
from traj_agent.tools.registry import ToolRegistry, attach_dataset
from traj_agent.agent.loop import TrajCleaningAgent
from traj_agent.agent import provider as prov
from traj_agent.memory.store import MemoryStore
from traj_agent.tools.playbook import vault_status

DATA = "traj_dict.json"
raw = tm.load_raw(DATA)
print(f"载入 {len(raw)} 辆车")

status = prov.provider_status()
print("\nLLM provider 配置：")
for k, v in status.items():
    print(f"  {k}: {v}")
print("\nObsidian vault：", json.dumps(vault_status(), ensure_ascii=False))

```
## Cell 3 (markdown), execution_count=None
Cell metadata: {}
```text
### 数据集的两个 regime

本项目约 63% 的车辆全程静止、37% 在真实行驶。
**对这两类用同一套阈值是不可能的** —— 这是智能体应当自动识别出的第一件事。
```
## Cell 4 (code), execution_count=None
Cell metadata: {}
```python
import collections
sample = sorted(raw.keys(), key=lambda k: (len(k), k))[:120]
cards = [diagnosis.diagnose(tm.traj_from_raw(v, *raw[v])) for v in sample]
summary = diagnosis.dataset_regime_summary(cards)
print(json.dumps(summary, ensure_ascii=False, indent=1))

```
## Cell 5 (markdown), execution_count=None
Cell metadata: {}
```text
## 2. 单条轨迹完整闭环
```
## Cell 6 (code), execution_count=None
Cell metadata: {}
```python
mem = MemoryStore(":memory:")      # 演示用内存库；生产换成 sqlite 文件路径
agent = TrajCleaningAgent(llm=prov.MockProvider(), memory=mem,
                          regret_threshold=0.05).attach_dataset(raw)

VEHICLE = "246"     # 11 km 的真实行驶轨迹
result = agent.run(VEHICLE)
print(f"ok={result.ok}  来源={result.proposal_source}  "
      f"工具调用={result.tool_calls}  LLM 轮次={result.llm_turns}")

```
## Cell 7 (markdown), execution_count=None
Cell metadata: {}
```text
### 诊断卡（这就是 LLM 看到的全部数据 —— 不含任何坐标）
```
## Cell 8 (code), execution_count=None
Cell metadata: {}
```python
print(json.dumps(result.diagnosis, ensure_ascii=False, indent=1))
```
## Cell 9 (markdown), execution_count=None
Cell metadata: {}
```text
### trace：智能体每一步做了什么

这张表就是课堂讲评的材料 —— 能看到 LLM 调了哪些工具、
每次核验算出了什么数。
```
## Cell 10 (code), execution_count=None
Cell metadata: {}
```python
for s in result.trace:
    detail = json.dumps(s.detail, ensure_ascii=False)
    print(f"[{s.index:2d}] {s.kind:6s} {s.name:22s} {detail[:110]}")
```
## Cell 11 (markdown), execution_count=None
Cell metadata: {}
```text
### 提议与核验结果

`regret` 是**可自动判分**的核心数字：
相对确定性搜索找到的最优解，这条建议丢掉了多少比例的可得收益。
```
## Cell 12 (code), execution_count=None
Cell metadata: {}
```python
d = result.to_dict(with_trace=False)
print("LLM 提议的参数：")
print(json.dumps(d["proposal_params"], ensure_ascii=False, indent=1))
print("\n它的依据：")
print(result.proposal_raw.get("rationale", ""))
print("\n它预测的效果（会被逐一比对符号）：")
print(json.dumps(result.proposal_raw.get("expected_effect", {}), ensure_ascii=False))
print("\n实测指标（对清洗后轨迹，隔离出纯 DP 误差）：")
print(json.dumps({k: v for k, v in d["measured"].items() if k != "clean_report"},
                 ensure_ascii=False, indent=1))

```
## Cell 13 (code), execution_count=None
Cell metadata: {}
```python
v = d["verification"]
print(f"提议得分   : {v['proposal_score']}")
print(f"基线得分   : {v['baseline_score']}   （物理先验默认参数）")
print(f"搜索最优   : {v['best_score']}")
print(f"regret     : {v['regret']}   口径={v['regret_basis']}")
print(f"方向准确率 : {v['direction_accuracy']}")
print(f"约束满足   : {v['constraint_ok']}   夹紧项={v['clamped_params']}")
print(f"记忆准入   : {v['admitted']}  —— {v['admit_reason']}")
```
## Cell 14 (markdown), execution_count=None
Cell metadata: {}
```text
## 3. 出图
```
## Cell 15 (code), execution_count=None
Cell metadata: {}
```python
from traj_agent.core import clean, simplify
from traj_agent.report import figures

t_raw = tm.traj_from_raw(VEHICLE, *raw[VEHICLE])
t_clean, report = clean.denoise_trajectory(t_raw)
t_simp = simplify.simplify_trajectory(t_clean, d["proposal_params"]["dp_tolerance"]).traj

print("清洗账本：")
print(json.dumps(report.to_dict(), ensure_ascii=False, indent=1))

p1 = figures.plot_clean_overlay(t_simp, reference=t_raw, out_dir="figures",
                                filename=f"notebook_overlay_{VEHICLE}.png")
p2 = figures.plot_anomaly_scatter(t_raw, out_dir="figures",
                                  filename=f"notebook_anomaly_{VEHICLE}.png")
p3 = figures.plot_heatmap(t_simp, reference=t_raw, out_dir="figures",
                          filename=f"notebook_heatmap_{VEHICLE}.png")
print("\n输出：", p1, p2, p3, sep="\n  ")

```
## Cell 16 (markdown), execution_count=None
Cell metadata: {}
```text
### 质量—压缩率曲线

这张图**同时服务任务②和任务③**：
任务②看阈值扫描的边际递减形状，
任务③它就是 verifier 计算 regret 的目标函数地形图。
```
## Cell 17 (code), execution_count=None
Cell metadata: {}
```python
from traj_agent.core import segment

reg = ToolRegistry(); attach_dataset(reg.ctx, raw)
h = reg.call("load_trajectory", vehicle_id=VEHICLE)["handle"]
hc = reg.call("clean_trajectory", handle=h)["handle"]
curve = reg.call("run_search", handle=hc, param="dp_tolerance", n=8,
                 reference_handle=hc)["curve"]
knee = reg.call("find_knee", curve_json=json.dumps(curve))["knee"]
p4 = figures.plot_quality_compression(curve, knee, out_dir="figures",
                                     filename=f"notebook_curve_{VEHICLE}.png")

print(f"{'容差':>8} {'点数':>6} {'压缩率':>8} {'最大偏差':>10} {'长度比':>8}")
for c in curve:
    print(f"{c['value']:8.1f} {c['n_points']:6d} {c['compression_ratio']:8.3f} "
          f"{c['max_deviation_m']:10.2f} {c['length_ratio']:8.4f}")
print("\nknee point：", json.dumps(knee, ensure_ascii=False))

```
## Cell 18 (code), execution_count=None
Cell metadata: {}
```python
rows = segment.sweep_split_thresholds(t_clean, [15, 30, 60, 120],
                                        [100, 200, 400, 800, 1600])
p5 = figures.plot_sensitivity_heatmap(rows, out_dir="figures",
                                     filename=f"notebook_sensitivity_{VEHICLE}.png")
p6 = figures.plot_ablation.__doc__ and None  # 占位，消融图在第 4 节出
print("敏感性热图：", p5)
```
## Cell 19 (markdown), execution_count=None
Cell metadata: {}
```text
## 4. 消融实验
```
## Cell 20 (markdown), execution_count=None
Cell metadata: {}
```text
四种模式必须**结构性不同**，否则消融表没有意义。

| 模式 | LLM | 记忆 | 搜索 |
|---|---|---|---|
| llm-only | 有 | 无 | 无 |
| search-only | **无** | 无 | 有 |
| llm+search | 有 | 无 | 有 |
| llm+memory+search | 有 | 有 | 有 |

### 两个必须避开的陷阱

**1. 信息泄漏。** 若在评测轨迹上边跑边攒记忆，agent 会把「这条轨迹自己的
上一次结果」检索回来当先验 —— 等于考试时把答案摆桌上。
故 `run_ablation` 强制两阶段：demo 集积累记忆，**留出集**只读不写（`read_only=True`），
且 `retrieve_similar(exclude_self=True)` 排除自身。
demo 与 holdout 重叠会直接抛错。

**2. regret 口径不可比。** 关闭搜索时本模式可达上限就是基线，
regret 退化为绝对口径；含搜索模式是归一化口径。
两者**不能**直接比较，代码会在 `caveats` 里标注。

下面用按 (regime, timeline) 分层挑选的 demo / holdout 两组（各 12 条，零重叠）。

```
## Cell 21 (code), execution_count=None
Cell metadata: {}
```python
from traj_agent.verifier.verify import ablation_summary

specs = [
    ("llm-only",          dict(use_llm=True,  use_memory=False, use_search=False, regret_threshold=1.0)),
    ("search-only",       dict(use_llm=False, use_memory=False, use_search=True,  regret_threshold=0.05)),
    ("llm+search",        dict(use_llm=True,  use_memory=False, use_search=True,  regret_threshold=0.05)),
    ("llm+memory+search", dict(use_llm=True,  use_memory=True,  use_search=True,  regret_threshold=1.0)),
]
VEHICLES = ["246", "256", "306", "209"]

cases, per_mode = [], {}
for mode, kw in specs:
    m = MemoryStore(":memory:") if kw["use_memory"] else None
    r0 = ToolRegistry(); attach_dataset(r0.ctx, raw)
    ag = TrajCleaningAgent(registry=r0, llm=prov.MockProvider(), memory=m,
                           mode=mode, **kw)
    per_mode[mode] = []
    for vid in VEHICLES:
        r = ag.run(vid)
        if not r.ok:
            continue
        dd = r.to_dict(with_trace=False); vv = dd["verification"]
        row = {"mode": mode, "regret": vv["regret"],
               "proposal_score": vv["proposal_score"],
               "n_evaluations": dd["tool_calls"],
               "direction_accuracy": vv["direction_accuracy"],
               "admitted": vv["admitted"]}
        cases.append(row); per_mode[mode].append(row)
    if m: m.close()
    print(f"{mode:22s} 完成 {len(per_mode[mode])} 条")

rows = ablation_summary(cases)
print()
print(f"{'模式':22s} {'n':>3} {'平均regret':>10} {'平均分':>8} {'平均调用':>8} {'方向准确':>8} {'准入率':>7}")
for r in rows:
    print(f"{r['mode']:22s} {r['n']:3d} {str(r['mean_regret']):>10} {str(r['mean_score']):>8} "
          f"{str(r['mean_evals']):>8} {str(r['mean_direction_accuracy']):>8} {str(r['admit_rate']):>7}")

p6 = figures.plot_ablation(rows, out_dir="figures", filename="notebook_ablation.png")
print("\n消融图：", p6)

```
## Cell 22 (markdown), execution_count=None
Cell metadata: {}
```text
## 5. 记忆的可解释视图
```
## Cell 23 (markdown), execution_count=None
Cell metadata: {}
```text
记忆检索用 **12 维归一化特征 + regime 硬门控**，不用 embedding。

这样做的理由：特征都有物理含义，学生能把检索到的邻居和特征值直接打出来看，
而不是面对一个黑盒向量。 `regime` 作为门控（而非一个距离维度）是因为
静止轨迹与行驶轨迹的特征分布完全不同，混在一起检索会让结果失去参考价值。
```
## Cell 24 (code), execution_count=None
Cell metadata: {}
```python
from traj_agent.memory import retrieve as retrieve_mod
from traj_agent.memory import features as feat_mod

card = diagnosis.diagnose(t_raw)
view = retrieve_mod.explain_neighbors(card, agent.memory, k=3)
print("查询轨迹的特征向量：")
print(json.dumps(view["query"]["features"], ensure_ascii=False, indent=1))
print("\n检索到的邻居：")
for nb in view["neighbors"]:
    print(f"  {nb['seg_id']:10s} 相似度={nb['similarity']:.4f} regime匹配={nb['regime_match']} "
          f"参数={nb['params']} regret={nb['regret']}")
print("\n说明：", view["note"])

```
## Cell 25 (code), execution_count=None
Cell metadata: {}
```python
# L2：从已准入案例蒸馏出的参数区间
n = agent.memory.rebuild_procedural(min_samples=1)
print(f"蒸馏出 {n} 条参数区间\n")
print(retrieve_mod.region_hint_text(retrieve_mod.prior_for(card, agent.memory)))
print("\n记忆库统计：")
print(json.dumps(agent.memory.stats(), ensure_ascii=False, indent=1))
```
## Cell 26 (markdown), execution_count=None
Cell metadata: {}
```text
### 时间轴故障的轨迹

车辆 352 的 170 个点**全部落在 3 秒内**（时间戳只有 4 个不同值），
但坐标序列长 7.6 km。这不是"116 个坏点"，而是时间轴整体故障。
智能体应当识别出来并改用纯几何规则，而不是去删 68% 的点。
```
## Cell 27 (code), execution_count=None
Cell metadata: {}
```python
r352 = agent.run("352")
d352 = r352.to_dict(with_trace=False)
print("时间轴诊断：", json.dumps(d352["diagnosis"]["timeline"], ensure_ascii=False))
print("observations：", json.dumps(d352["diagnosis"]["observations"], ensure_ascii=False, indent=1))
print("\n提议：", json.dumps(d352["proposal_params"], ensure_ascii=False))
print("依据：", r352.proposal_raw.get("rationale", ""))
print(f"\nregret={d352['verification']['regret']:.4f} 准入={d352['verification']['admitted']}")
print("理由：", d352["verification"]["admit_reason"])
```
## Cell 28 (markdown), execution_count=None
Cell metadata: {}
```text
### 静止轨迹：目标函数不适用

车辆 0 清洗后只有 21 点、总长 12.29 m，全是厘米级抖动。
此时任何容差都会让长度比崩掉 —— 但这不是"方案不好"，
而是**压缩率与保真度在这个尺度上没有物理含义**。

核验器对此显式标记 `applicable=False`，改按 regime 正确性准入，
而不是强行算一个负分或虚高的 regret。
```
## Cell 29 (code), execution_count=None
Cell metadata: {}
```python
r0 = agent.run("0")
d0 = r0.to_dict(with_trace=False)
print("regime:", d0["regime"], " 长度相关:", json.dumps(d0["diagnosis"]["space"], ensure_ascii=False))
print("proposal_objective:", json.dumps(d0["proposal_objective"], ensure_ascii=False, indent=1))
print("\n核验：", json.dumps(d0["verification"], ensure_ascii=False, indent=1))
```
## Cell 30 (markdown), execution_count=None
Cell metadata: {}
```text
## 6. 切换到真实 LLM API

当前用的是 `MockProvider`（确定性规则，无 key 可跑通全流程）。
接真实模型只需设置环境变量：

```bash
export DSH_TRAJ_LLM_API_KEY=sk-xxx
export DSH_TRAJ_LLM_BASE_URL=https://api.deepseek.com/v1   # 或任何 OpenAI 兼容端点
export DSH_TRAJ_LLM_MODEL=deepseek-chat
```

代码里**不需要改任何东西** —— `build_provider()` 会自动切成
`OpenAICompatProvider`（原生 function-calling）。
不支持 function-calling 的模型会走文本 ReAct 协议。
```
## Cell 31 (code), execution_count=None
Cell metadata: {}
```python
print(json.dumps(prov.provider_status(), ensure_ascii=False, indent=1))
print()
print("如需显式指定：")
print('  TrajCleaningAgent(llm=prov.OpenAICompatProvider(model="deepseek-chat"))')
print('  TrajCleaningAgent(llm=prov.MockProvider())   # 离线演示')

```
## Cell 32 (markdown), execution_count=None
Cell metadata: {}
```text
## 小结：这个工作流解决了什么

| 问题 | 做法 |
|---|---|
| LLM 猜参数不准 | 物理先验定区间 → LLM 提起点 → 确定性搜索精调 |
| 无法判断 LLM 建议好不好 | regret = 相对搜索最优的差距，**可自动判分** |
| 每条轨迹都调 LLM 太贵 | 记忆分层：跑少数、复用多数（L2 直接给区间） |
| 记忆被幻觉污染 | **只有核验器能写记忆**；LLM 没有写记忆的工具 |
| 上下文塞不下坐标 | 坐标永不出进程，只以句柄 + 诊断卡流动 |
| 换模型要改代码 | OpenAI 兼容协议 + 文本 ReAct 兜底 |

### 下一步（不在本 notebook 范围）
- 路网约束接入真实 OSM 数据（`road/matcher.py` 已留协议）
- 批量跑全量 11386 条并做分层抽样统计
- 用真实 LLM 复跑消融表，对比 Mock 基线的差距

```