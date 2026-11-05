# R-001 原材料实际审读回执

- 原始ZIP安全检查与解压：`scripts/inspect_teacher_materials.py`，实际已运行；无路径穿越/符号链接，过滤Apple元数据，19条来源/成员记录。
- 基础ZIP含nested foursquare.zip与RAR，均实际解开；RAR使用libarchive-c调用本机libarchive。原始ZIP/RAR不变。
- 基础Notebook全部15 Cells、进阶全部44 Cells已逐Cell实际读取；完整source文本已提取到同目录。
- 基础PPT全部14页、进阶全部25页XML文本已完整阅读。
- 用LibreOffice headless实际转换两份PPT为PDF；随后pdftoppm 120dpi渲染39页，使用view_image逐页实际查看全部39页。没有以联系表替代逐页查看。
- 图片内额外数学细节：基础p2容量/二元约束，p3算法值/最优值比，p8TBG伪码及边界差异，p10/11回收图；进阶p5目标/容量、p7参考方向组合数、p16Q/TD学习率、p17V、p18LT、p24正式作业细则均已核对。
- 原材料中的图表/数值是teacher pre-generated教学参考，不能成为本轮current-run结果。进阶p10–13、20–23参考图不进入本轮实测图目录。
- LibreOffice输出有非致命javaldx和PNG profile警告，转换exit0；当前完成的是源材料审读，未将此回执当作本轮正式报告200dpi视觉验收。

审读发现及逐项要求见 `docs/REQUIREMENT_MATRIX.md`。
