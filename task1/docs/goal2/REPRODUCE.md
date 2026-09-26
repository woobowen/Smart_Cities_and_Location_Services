# Goal 2 工作成果复算

从仓库根目录使用既有 `.venv`。原始数据、教师 starter 与 Goal 1 冻结合同不覆盖。当前有效 run 的唯一索引为 `task1/evidence/goal2/current_runs.json`；旧 smoke、失效与失败产物不能替代该索引。

```bash
.venv/bin/python -m task1.scripts.goal2 --help
.venv/bin/python -m task1.scripts.build_goal2_notebooks --execute
```

三份工作 Notebook 位于 `task1/notebooks/goal2/`：参数与顺序、真实四模式与记忆、单项候选与反例。每份均支持新内核 Run All，默认调用 `task1.scripts.goal2.recompute`，从 raw 与已冻结真实提议重新执行相应确定性处理、指标与图。它不新增模型请求，不写记忆快照，不把重复计算计为新的独立实验。`MODE='RECOMPUTE'` 和 `ENABLE_LIVE=False` 是默认状态；新的 LIVE 调用须使用独立入口并遵循冻结预算。

可在 Python 中分别复算三个主题，输出放到新目录：

```python
from pathlib import Path
from task1.scripts.goal2 import recompute

result = recompute(topic="parameters", output_directory=Path("/tmp/sc-g2-parameters-recompute"), rebuild_figures=True)
assert result["status"] == "VERIFIED" and result["new_model_calls"] == 0
```

`topic` 还可取 `modes`、`candidates`。前者从原始数据重建真实 LIVE 已实际评价的候选及锁定选择，保持原始提议身份；后者重算单项与解析反例。数据、合同、源码或目标 hash 不一致时应停止并登记失效，不能借旧审核回执继续。

单独重新生成当前图：

```bash
.venv/bin/python -m task1.scripts.build_goal2_figures --current-runs task1/evidence/goal2/current_runs.json --output task1/figures/goal2
```

图来自已核验的当前 run，保存 SVG/PDF/300-dpi PNG 和 PDF 的 200-dpi 实际渲染。`figure_data.json` 绑定绘图读数；`figure_manifest.json` 绑定来源与输出 hash。生成器的尺寸/非空检查不替代逐张 visual inspection 或独立 C 验收。架构 `.drawio` 为可编辑 diagrams.net 原生 XML，与各导出格式使用同一节点/边规范；不依赖不存在的模型或模块。

解析反例可独立执行，输出目录必须为空以保留旧证据：

```bash
.venv/bin/python -m task1.scripts.goal2_counterexamples --output /tmp/sc-g2-counterexamples --run-id local-recompute
```

构造输入标 `SYNTHETIC_COUNTEREXAMPLE`；七条真实 pilot 是 `KNOWN_EXPOSED`，不是新留出。工作平面单位不证明源 datum 或绝对定位精度。两份正式报告尚未定稿；Goal 3 的组合与全量最终处理不由上述命令执行。
