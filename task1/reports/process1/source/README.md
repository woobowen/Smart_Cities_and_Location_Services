# 实验一 Process Report：完整可编辑源包

当前成品为 **77 页 A4 PDF**：`Process_Report_Revised.pdf`。包括完整 Part I 工作流构建、Part II 实验一中的交互与决策，以及整体工作流回顾。

当前版本为 **2026-10-03第76页局部修正版**。完整保留用户原始消息气泡，去掉原稿误带入的不完整GPT回复；没有修改其他76页、全文文字、实验依据或结论。当前修改与证据承接记录见 `provenance/closeout_p76/`；前次全文语言修订保持历史身份。

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
| `content/closing_evidence.json` | 第76页原始用户消息的来源、无损裁切边界与当前授权 |
| `tools/check_p76_closeout.py` | 检查全部135个裁片；给定原PDF/ZIP时验证局部差异 |
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
python tools/check_p76_closeout.py
```

所有截图和当前绘图输入均在包内。`tools/render_review.py` 生成全部200-dpi单页PNG；为控制包体大小，批量单页PNG不重复打包，可用此命令随时重建。

原始截图文字保持原样。箭头位于独立的TikZ矢量层，截图区域没有荧光圈、边框或透明蒙层。结构图的正常节点边框保留。

## 4. 当前检查与历史记录

当前检查入口：

- `provenance/closeout_p76/artifact_check.json`：原/新完整PDF的77页200-dpi比较、全部正文相同与135个无损截图裁片核对。
- `provenance/closeout_p76/clean_rebuild.json`：移除预置主PDF后的两条实际构建路线。
- `provenance/closeout_p76/evidence_inheritance_ledger.json`：40组既有互动、134个常规裁片、85条既有侧注箭头的逐项来源与验收承接，以及p76新增当前裁切检查。
- `provenance/closeout_p76/visual_review.json`：本轮实际目视p76的范围和结果。
- `provenance/closing_crop_map.json`：结尾裁片的原件、边界、显示尺寸与真实PPI。
- `provenance/artifact_audit.json`：当前原生页面、图件、常规窗口及结尾裁片的作者检查。
- `provenance/SHA256SUMS.txt`：当前源包文件校验表（不包含自身，不包含可重建缓存）。

对照前次批准原件时，在命令中显式给出原文件路径：

```bash
python tools/check_p76_closeout.py \
  --baseline-pdf /path/to/previous/Process_Report_Revised.pdf \
  --baseline-source-zip /path/to/previous/Process_Report_Revised_LaTeX_Source.zip
```

该检查要求原PDF/ZIP分别匹配已记录的旧批准SHA256，避免误把当前新版作为“原版”比较。

`provenance/language_revision/`、原 `provenance/clean_rebuild.json` 与旧历史材料记录前次制作；`provenance/history/pre_p76_closeout/`保存本次改动前相应导航、状态及裁片。不要将其旧PENDING或旧hash误读为当前结论，也不改写其历史事实。

`provenance/closeout_p76/prior_review/`保存上一轮针对GitHub固定版本的工程二重验收原件。本次修改后的检查属于作者自检；新文件的本地集成、教师ZIP的实际解压/依赖检查和GitHub最终二审按另附Codex交接任务执行。

## 5. 分发与提交

`Process_Report_Revised.pdf` 与配对源ZIP是项目源/完整工程中的报告成品。教师提交包使用这份PDF、已验收Experiment PDF、两个完成版Notebook及必要运行文件；不把整个本源包、字体、历史材料或审核日志混入教师ZIP。

本源包没有重新运行轨迹实验或调用模型，也不替代教师包的实际终检。旧截图、旧运行与前次用户认可均按其真实范围继承。
