# Experiment Report：完整重构版

姓名：吴博闻　学号：10245102410

主文件：`Experiment_Report.tex`；成品：`Experiment_Report.pdf`。

正文已经完整重写为七章，保留已批准样稿的表达方式。包含10幅原生图、17张表、参考文献和计算附录。这个目录是**独立的报告源文件包**，不是课程实验的全部代码仓库或教师最终提交包。

## 直接编译 PDF

在本目录执行：

```bash
bash build.sh
```

也可以在 TeX 编辑器中以 `Experiment_Report.tex` 为主文件，选择 **XeLaTeX**，编译两次。不要使用 pdfLaTeX。

需要 TeX Live（含 ctex、fontspec、pdflscape 等）以及已经安装的字体：DejaVu Serif、DejaVu Sans、Noto Serif CJK SC、Noto Sans CJK SC、Noto Sans Mono CJK SC。包内不附字体文件。

所有插图已提供 PDF，正常编译不需要运行 Python，不需要模型凭据或网络。`build.sh` 将结果写入 `build/`，然后更新根目录 `Experiment_Report.pdf`。

## 文件说明

- `chapters/`：七章正文及附录。参考文献保存在主 `.tex` 的 `thebibliography` 中，编译不依赖 BibTeX。
- `figures/`：全部图的 PDF／SVG／PNG；两幅逻辑结构图另含 `.drawio`。
- `source/`：绘图代码、共享P2颜色定义和复现入口。
- `data/`：绘图使用的冻结统计、配对表和轨迹示例；`source_manifest.json` 说明来源。
- `checks/`：本轮作者自检范围、输入核对和最终编译记录。它们不属于正式报告正文。

## 可选：重新生成图表

只有需要编辑图形时才执行：

```bash
python -m pip install -r requirements-figures.txt
python source/validate_inputs.py
python source/build_figures.py
bash build.sh
```

图表脚本使用 Matplotlib、NumPy、Pandas 和 CairoSVG；Matplotlib 绘图还需要其能够找到的 `Noto Sans CJK JP` 字体族。该名称是当前系统对Noto CJK集合的识别方式，文字为中文原文，并不改变图中文字语言。原生SVG转PDF还需要本机Cairo/fontconfig支持。若缺字体，先安装对应字体或明确修改字体设置，不能接受方框字后继续使用。

所有图表使用相对路径。重绘读取包内固定数据，不调用模型，不做新参数拟合，也不重新开展轨迹清洗实验。图表的派生统计与此前独立复算结果，不能重新标为新的独立研究实验。

## 修改与工程集成边界

数据依据仓库固定提交 `718e6d9eb69d3e47ee8929755cd3bd3c94526fab` 的已记录成果及既有数值复核材料。正文组织、措辞、构图和排版已重构；方法、比较规则与原始结果未改动。

本轮没有更新远程仓库、原报告生成器、Process Report或教师提交包。需要接入原工程时，应将本版正文设为实际构建来源，避免旧 `REPORT_BUILD` 再生成工程审计式旧稿；同时按受影响范围核查路径、数值和产物。

本轮检查是作者自检，包括全文核对、最终25页200dpi逐页查看、关键数字及引用检查、独立目录编译。不是新的模型实验、全量清洗、独立C验收或用户最终审核。
