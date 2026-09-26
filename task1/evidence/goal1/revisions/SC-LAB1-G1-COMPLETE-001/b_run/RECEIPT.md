# B-Run：工作 Notebook 与本轮真实图回执

Engineering Status：生成、执行与本角色工程检查通过，等待 C 独立验收。本回执不关闭父 Goal，也不登记项目最终 PASS。

输入为 `current_run.json` 指向的 `g1-complete-pilot-03`。处理核心 CODE 为 `f229d9a4113bcc0dd763e1b410f1f5fb73903a62`，baseline 文件 SHA256 为 `865710aea34a316fe83088d7cf2ac1aec68c96623269bfcf06255b5db2930fd8`。所有展示均绑定同版实际 baseline；这是固定七条记录的条件化开发 pilot，不是全量、合成示例或历史结果。source CRS / datum 仍为 UNVERIFIED。

实际点去向：783 输入，30 段；309 过滤、13 方向删除、273 DP 省略、188 保留，0 未处理。DP 省点率的分母为 461 个 clean 点，值为 0.5921908893709328；不把上游删除计入 DP 收益。

## 文件与来源

- 唯一 Notebook builder：`task1/scripts/build_goal1_notebooks.py`，SHA256 `e3adbca56ad1a9179725a8cb17848ef548cbe56f4a4cdc9727be3cff70472022`。
- 图生成器：`task1/scripts/build_complete_figures.py`，SHA256 `89b1c96ef3e7821ab46857d3e9b0223839d8b768907ed0b91265c40aa3f7b7c1`。
- `task1/notebooks/01_baseline_and_audit.ipynb`：从 raw 执行 baseline，构造候选外可信参考并独立审核，展示方法、参数、逐阶段计数、DP 分母、真实图、坐标敏感性和限制。
- `task1/notebooks/02_agent_loop_recompute.ipynb`：调用 `complete_goal1.recompute_saved` 重算四目标；展示真实 A/B/C、issues/events、follow-up 与资源。历史 4+6 CLI 和本轮 native 派发分开陈述，默认不重新执行旧六次模型调用。
- `../figures/` 包含三图的 SVG/PDF/300-dpi PNG，以及各 PDF 的 200-dpi render。执行结构图另保存 `.drawio`，SVG/PDF/PNG 由同一 XML 几何和标签解析生成。`inspection/` 保存灰度检查副本。
- `figure_verification.json`、`notebook_execution.json`、`notebook_verification.json` 保存实际文件 hash、命令和检查结果；`verify_generated.py` 可重做保存产物核对。

## 实际命令与结果

在既有 `.venv` 中执行，未安装包或改变持久配置：

```text
.venv/bin/python -m task1.scripts.build_complete_figures
→ exit 0；3 图、10 个主文件，figure_manifest.json 保存输入和源 hash。

pdftoppm -r 200 -png -singlefile <每个 figure.pdf> <每个 figure_pdf_render>
→ 三次 exit 0；实际完整路径见 figure_verification.json。

.venv/bin/python -m task1.scripts.build_goal1_notebooks --execute
→ exit 0；各自新内核，各 8 个 code cells；0 新模型调用。

.venv/bin/python task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/b_run/verify_generated.py
→ exit 0；10 主图文件、9 raster、2 Notebook 核对通过，0 error outputs。

git diff --check -- task1/scripts/build_complete_figures.py task1/scripts/build_goal1_notebooks.py task1/notebooks/01_baseline_and_audit.ipynb task1/notebooks/02_agent_loop_recompute.ipynb
→ exit 0，无输出。
```

Notebook 01 新算 baseline 与保存 output hash 精确一致；九个审核组件齐全。Notebook 02 四项重算输出与已登记产物一致，独立审核通过。执行使用两个临时 kernelspec 启动的新内核，执行后恢复环境；没有调用 Provider。既有 ipykernel 的本地 TCP 提示完整保留在 `notebook_execution.json`，未产生 Notebook cell 错误。

Notebook 使用资源快照 SHA256 `299eefcbe84e38251ef5dcdb20a1b4be0be19e988934a99625cb1db696547c9a`。Notebook 02 将末尾状态明确标为“Notebook 执行时的 journal 快照”；最终总审查登记在其后，最终状态见 `task1/evidence/goal1/REVIEW_PACKET.md`。

## 实际视觉检查

已用 `view_image` 检查最终 300-dpi PNG、200-dpi PDF render 和灰度副本。初版发现 Record 2 的 offset tick 读数不直观、结构图底部文字过长；仅关闭 tick offset、缩短同义标签后重新生成和检查，未改变数据、统计、方法或核心代码。最终标题、图例、轴标签无裁切，结构框内标签和箭头路由清楚；原始轨迹仅散点，clean/final 仅连接实际处理片段，空输出不补造轨迹。灰度下类别由 hatch、线型和点符号辅助区分。

图像检查脚本对 9 个 raster 全部通过。draw.io 为 11 个 vertex、10 条 edge，33 行非空标签在 SVG 中全部可检出。最终图源、渲染文件的尺寸、hash 与视觉观察分别写入 `figure_verification.json`。

## 边界与剩余事项

源 datum 未获证明；局部模型核验不表示绝对定位、真实恢复或清洗准确率。没有 Goal 2 参数/顺序实验，没有 Goal 3 正式 Experiment / Process Report 或提交包；这些工作材料不能代替正式报告或 GPT 最终审查。没有修改原始数据、合同、workflow/config 或 core，没有 commit/push。新增系统包、语言包、字体、工具链和持久配置均为 0。剩余事项是 C 独立验收及主线程父任务登记。
