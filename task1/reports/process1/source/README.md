# 实验一 Process Report：完整可编辑源包

当前成品为 **77 页 A4 PDF**：`Process_Report_Revised.pdf`。包括完整 Part I 工作流构建、Part II 实验一中的交互与决策，以及整体工作流回顾。

本轮修订覆盖封面、目录、40组互动的原生叙述、六幅结构图文字、图注和结尾。原始对话图像、裁切窗口、截图显示位置及实验参考数据沿用原稿。修改说明见根目录 `REVISION_NOTES.md`。

## 1. 直接编译完整 PDF

```bash
cd Process_Report_Revised_Source
bash compile.sh
```

脚本连续运行两次 XeLaTeX，输出根目录 `Process_Report_Revised.pdf`；中间文件写入 `build/`。主文已经完整保存在 `chapters/pages.tex`，直接编译无需 Python、网络、外部仓库、模型调用或重新运行实验。

需安装 XeLaTeX（含 fontspec、xeCJK、TikZ、hyperref、ragged2e）以及本机字体 **Noto Sans**、**Noto Sans CJK SC**。源包不分发字体文件。请保持这两种字体以复现交付稿的断行和版式。

## 2. 编辑入口与文件结构

| 位置 | 用途 |
|---|---|
| `main.tex` | 完整主文件、XeLaTeX样式与P2配色 |
| `chapters/pages.tex` | 当前完整正文、截图放置、页码、目录链接与TikZ箭头 |
| `content/evidence_units.json` | 40组互动的标题、导语、侧注、续页说明、窗口与箭头目标定义；正文编辑的主要入口 |
| `content/diagrams.json` | 六幅结构图的节点、连线、标题、文字与图注 |
| `tools/editorial.py` | 读取上述互动JSON规格的轻量入口 |
| `tools/build_report.py` | 生成全部LaTeX页面、裁片以及页码/裁切/箭头映射 |
| `tools/make_diagrams.py` | 生成六幅可编辑draw.io、SVG和PDF |
| `assets/raw/` | 用户提供的原始ChatGPT网页截图 |
| `assets/inherited/` | 从PreTask源包继承的真实UI裁片 |
| `assets/crops/` | 实际嵌入报告的无损裁切图像 |
| `figures/` | D01—D06的`.drawio`、SVG和PDF文件 |
| `provenance/accepted_experiment/` | 已冻结的实验参考材料与图形数据 |
| `provenance/language_revision/` | 本轮逐项修改、素材保留核对和逐页视觉检查记录 |
| `provenance/history/` | 历次制作/修复记录，保留历史身份，不参与当前正文构建 |
| `review/` | 全书排版与箭头检查拼版 |

## 3. 修改后重新生成

只改 `chapters/pages.tex` 可以直接编译，但再次运行生成器时会被JSON规格覆盖。需要持续保留的编辑应先写入 `content/evidence_units.json` 或 `content/diagrams.json`，再运行：

```bash
python -m pip install -r requirements-build.txt
python tools/make_diagrams.py
python tools/build_report.py
bash compile.sh
python tools/render_review.py
python tools/audit_report.py
```

所有截图和当前绘图输入均在包内。`tools/render_review.py` 生成全部200-dpi单页PNG；为控制包体大小，批量单页PNG不重复打包，可用此命令随时重建。

原始截图文字保持原样。箭头位于独立的TikZ矢量层，截图区域没有荧光圈、边框或透明蒙层。结构图的正常节点边框保留。

## 4. 本轮检查记录

- `provenance/artifact_audit.json`：77页、40组互动、134个常规证据窗口、85个箭头，以及六幅draw.io结构检查。
- `provenance/language_revision/preservation_check.json`：原始素材、冻结参考、裁切与箭头目标的前后核对。
- `provenance/language_revision/visual_review.json`：全部77页200-dpi实际阅读；修正12页后再次查看；Poppler复查封面、角色结构图和结尾。
- `provenance/language_revision/editorial_changes.json`、`diagram_changes.json`、`visual_refinement_changes.json`：逐字段修改记录。
- `provenance/clean_rebuild.json`：独立空目录内的直接编译与完整生成链复现结果。
- `provenance/FINAL_AUTHOR_REVIEW.md`：本轮制作方检查总结。
- `provenance/SHA256SUMS.txt`：交付包成员校验表。

原包中缺失但被TeX引用的结尾用户裁片已按原始截图及原裁切规格补齐，并与原PDF嵌入图像逐像素核对一致。该修复使源包可在空目录中直接编译。

以上检查由本轮制作者完成，登记为作者自检。当前交付用于用户审阅；本轮没有修改远程仓库、项目设置或教师提交状态。
