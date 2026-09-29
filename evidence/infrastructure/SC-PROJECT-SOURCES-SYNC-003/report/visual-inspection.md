# 25页批准版与重建版的实际视觉对照

2026-09-29。全部页面先以 `pdftoppm -r 200 -png` 渲染，再实际打开每一页完整PNG对照。使用的是 `render200/approved/` 与 `render200/clean-rebuilt/`，不是缩略图。24张竖页为1654×2339 px，物理页15横页为2339×1654 px。

| 实际观察者 | 完整检查范围 | 逐页记录 |
|---|---|---|
| `/root/report_integration` | 两版物理页1—12，共24图 | [visual-pages-01-12.md](visual-pages-01-12.md) |
| `/root/governance` | 两版物理页13—18，共12图 | [report-pages-13-18-visual.json](../governance/report-pages-13-18-visual.json) |
| `/root` | 两版物理页19—25，共14图 | [root-pages-19-25-visual.json](root-pages-19-25-visual.json) |

三份记录合并覆盖两版全部25页、50张完整页图。姓名学号、目录、七章、公式、17表、10图、四项参考文献与附录在各页可读；未发现新缺字、裁切、跨页或图文构图变化。此表是实际分工的作者/工程检查汇总，不将三人合写称为独立C。C另外真实编译与抽查的范围由其独立回执负责。

批准PDF与新编译PDF不是二进制相同，也不是逐像素相同。提取文字全字节相同；[几何与栅格比较](geometry-raster-comparison.json)显示文本bbox最大差0.242 pt（封面）、其余页不超过0.026 pt，页面RGB平均绝对差为0.041—0.405/255。上述像素指标只描述编译环境差异，不代替逐页目视，也不是新设研究评价标准。

正常REPORT_BUILD两次成功调用使用同一真实章节/图源与公共P2输入，`normal-build-1/render200`、`normal-build-2/render200` 全25张PNG逐字节等于此次已实际查看的 `clean-rebuilt` 对应页。该绑定见 [integration-verification.json](integration-verification.json)，故其视觉检查可以准确绑定到两次正常构建结果；不靠把旧22页检查改名证明新稿。当前阅读/打包PDF保留批准原件hash；真实编译产物各自保存为 `rebuilt.pdf`。
