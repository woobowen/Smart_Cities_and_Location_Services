# 正式可视化及可编辑源

实际阅读publication-plots Skill、项目Visual System与P2公共颜色源后，以真实结果准备候选并比较；没有使用生成式图片制作技术或数据图。

- [整体图型研究](../docs/VISUALIZATION_RESEARCH.md)：在线ECDF/雨云/配对；EA 3D/二维投影/平行坐标；V空间小倍数/时区矩阵等。
- [EA候选与选择](../evidence/evolution/VISUAL_RESEARCH.md)、[RL候选与作者检查](../evidence/rl/VISUAL_RESEARCH_AND_AUTHOR_CHECK.md)。候选实际文件在 `../figures/candidates/`，不只是换配色。
- 正式数据图 `../figures/formal/`：在线5、EA7、RL10个图，均有PDF/SVG/高分辨率PNG及真实输入hash/脚本sidecar。ECDF保留全部请求分母；3D使用真实服务数量第三维；V图使用聚合计数而非暴露逐条签到。
- 绘图代码 `../scripts/build_figures.py`、`build_evolution_figures.py`、`build_rl_figures.py`。公开前沿/收敛、均值和网格计数足够重画；临时无原数据根目录实际复画并逐PNG验证。
- 原生技术图 `../diagrams/research_verification_workflow.{drawio,svg,pdf}`、`dispatch_runtime_and_evaluation.{drawio,svg,pdf}`。draw.io内部是真实节点、文字、边；本轮用本地几何导出脚本生产对应SVG/PDF，没有声称启动draw.io桌面应用。
- 公共颜色唯一源 `../../templates/latex/common/p2_cloud_sorbet_colors.tex`。源包只是带hash的分发副本，不建第二套可编辑色值。

解释审查核对数据/统计/单位/分母/轴/负例/图注；视觉审查在最终26+8页PDF200dpi实际页面完成，见 `../evidence/independent_report_review/`。作者图检查与独立报告检查分开记录。可交互HTML不是正式静态图的替代，本轮也未声称调用未实际使用的QGIS/Plotly/PyDeck等工具。
