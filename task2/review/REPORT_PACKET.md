# 双报告与来源包

|成品|实际文件与构建|
|---|---|
|Experiment Report|[26页PDF](../reports/experiment/Experiment_Report.pdf)、[main.tex](../reports/experiment/main.tex)及chapters；方法/对照/结果/负例/思考题/局限|
|Process Report|[8页正文与技术素材交接PDF](../reports/process/Process_Report.pdf)、[main.tex](../reports/process/main.tex)及chapters；第一人称仅用于真实用户判断，Codex自动决定不冒称Human Judgment|
|配对可编辑源包|[Dispatch_Reports_LaTeX_Source.zip](../releases/Dispatch_Reports_LaTeX_Source.zip)；[成员与SHA回执](../evidence/report_source_package.json)，包内保留相对目录、10生成表、矢量图、draw.io与公共P2|
|构建|`../scripts/generate_report_tables.py`、`build_reports.py`；`../reports/common.tex`。XeLaTeX/latexmk、Poppler、Noto CJK/DejaVu；无字体二进制分发|
|真实检查|`../evidence/report_build/build_receipt.json`记录最终PDF SHA、页数、log、200dpi渲染；`../evidence/independent_report_review/`记录独立数字/实际逐页检查；隔离源包编译另有回执|

源包范围是**报告编译**，不含原始签到。完整仓库还提供公开聚合重画与作者原数据获取后实验重算入口；三项分别验收。报告source不是复制最终PDF掩盖旧生成器，本文稿和表/图确由同一实际构建链生成。

本轮原生ChatGPT UI截图尚未收到，也没有Evidence Master批准的User anchor/GPT before-after/phrase/arrow规格。Process无假UI、无倒写原话、无自行Lock；受影响的是新的互动证据展示页和最终Evidence Lock，正文、真实技术素材、过程记录与交接已经制作。外部接续只改受影响页面，不重开无关有效实验。
