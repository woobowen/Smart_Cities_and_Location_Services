# 实验一报告工程

两份报告复制自锁定的 P2 XeLaTeX 模板，分别回答最终技术结果和真实过程。模板及公共配色保持原件，不使用模板的合成数据或聊天素材。

- `experiment1/experiment1.tex`：技术报告；`references.bib` 为实际核读的 3 个主来源。
- `process1/process1.tex`：Workflow Construction 与 Experiment Decision Process 两层过程报告；真实互动截图/spec/LOCK 缺失时明确为送审稿。
- `metadata.tex`：由唯一身份源 `../config/assignment.json` 经 `task1.goal3.identity` 生成；REPORT_BUILD 每次重建，学号保持字符串；封面和 PDF author 同步验证。
- `experiment1/generated.tex`、`process1/generated.tex`：G3 已核验结果与真实过程接入点，不从最终集反向选择报告结论。
- `build_history_sources.py`：从已保存 G1/G2 JSON 重建历史数值和表，既不执行新实验，也不调用模型。
- `build_goal3_sources.py`：先验证独立 C 对当前开发 A1/A2/A3、收敛与实际产物的哈希绑定，再生成两份报告的开发正文；不读取选择或 FINAL_CONFIRM 效果。数值出处保存为 `goal3_development_bindings.json`。
- `build_selection_sources.py`：从已闭合的选择裁决、完整运行与三个失败的独立数学检查生成选择正文；未读取最终确认效果。数值出处保存为 `goal3_selection_bindings.json`。
- `build_final_sources.py`：核对确认闭合回执与冻结时序，从真实确认分片重新汇总分层/缺失几何读数；生成 native 事件元数据的真实边界说明。全量分支只有在 `result_summary.json`、当前生产 C 与全部 7 张正式图绑定齐备时才执行，缺少结果不填零；数值与来源保存为 `goal3_final_bindings.json`。

从项目根目录重新生成历史表与当前已核验的 G3 正文：

```bash
.venv/bin/python task1/reports/build_history_sources.py
.venv/bin/python task1/reports/build_goal3_sources.py
.venv/bin/python task1/reports/build_selection_sources.py
.venv/bin/python task1/reports/build_final_sources.py --scope full
```

统一构建并检查日志、导出正文、200 dpi 渲染：

```bash
.venv/bin/python task1/reports/build_reports.py --render
```

也可在各报告目录分别执行：

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build experiment1.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build process1.tex
```

使用现有 TeX Live、Noto CJK/DejaVu/Fandol 字体和 BibTeX；不需要 shell escape、模型凭据或新增字体包。报告依赖公共配色 `templates/latex/common/p2_cloud_sorbet_colors.tex`、历史 G2 图 `task1/figures/goal2/`、当前 G3 图 `task1/figures/goal3/` 及各代数值与绑定输入。源码构建结果与 200 dpi 检查回执保存在 `task1/evidence/goal3/report_build/`。当前完整构建必须使用已闭合生产与 7 图的真实输入；`--scope confirmation` 仅供先前阶段的明确预览，不作为最终报告构建入口。

PDF 可编译不代表整体完成。当前正文已接入真实开发、选择、最终确认、全量生产及图表；姓名学号已按用户直接提供内容同步；真实互动 Evidence、独立全文审核和用户理解仍有各自状态，不可把待补送审稿称为正式可提交完稿。

当前200dpi逐页图复用 `report_build/render200/`，新增 `experiment1_pages.txt` / `process1_pages.txt` 以“PDF物理页 n”分隔UTF-8全文。`build_receipt.json`绑定PDF/text/page图/命令/DPI，构建器不冒称目视；实际目视结论在本次closeout的C回执。
