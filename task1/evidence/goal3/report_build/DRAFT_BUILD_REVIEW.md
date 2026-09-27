# 两份报告的历史正文与 G3 接口

状态：**COMPILED_REVIEW_DRAFT；不是最终报告全验收**。

实际生成 Experiment Report / Process Report 的独立 XeLaTeX 工程与 PDF，完整替换模板演示正文，保留共同 P2 输入与身份。报告分别说明技术方法/评价/真实结果，以及 Workflow Construction + Experiment Decision Process。G3 仅在 `generated.tex` 中明确待接入，不填写未运行数值或预定最终赢家。姓名/学号和真实互动 Evidence 依赖仍显式待补。

## 真实来源与数值

`build_history_sources.py` 实际从四份 G1/G2 JSON 生成 23 个数值宏和四张表；`history_value_bindings.json` 绑定源哈希与生成文件。其动作不新增实验或模型调用。三项实际文献来源读取见 `SOURCE_READ_SCOPE.md` 与 HTTP 回执；只核读 JMLR 官方摘要/元数据，不声称全文复现。

## 实际构建

```bash
.venv/bin/python task1/reports/build_reports.py --render
```

调用 latexmk/XeLaTeX/BibTeX，实际生成 13 页 Experiment 与 9 页 Process 初稿；最终页数以 `build_receipt.json` 为准。所有页 `pdftoppm -r 200 -png` 真实渲染，页面哈希在回执中。`pdftotext -layout` 输出独立保存，可检查数字、引用与正文是否存在。

最终 G3 数字未接入前，本轮只记录初稿视觉检查：先查看首版 21 页联系表，再查看密集数学页、顺序/模式表、真实 AI 建议、版本表与 Process 修复/待补页。发现的章节标题孤立问题已通过本地分页约束修正；G3 接入会改变分页，因此最终必须重新逐页检查，不复用初稿视觉声明作为最终 PASS。

## 实际工程修复

- 历史数值生成器的反斜杠字符串与一个可空 comparison 字段引发实际错误。修复转义；完整原始点覆盖可严格判定同集合，其余依保存的共同集合标记。未改源数值或实验定义。
- 模板现有环境没有所请求的斜体字形。正文不用斜体强调，书目保持正体，消除字体替代警告，没有安装/合成新字体。
- 正文长哈希句出现轻微 Overfull；改为短哈希用途表。Process 认证误分类叙述也重排为清楚短句，语义未变。
- 增加分页保护时可选 `needspace.sty` 不存在；保存实际失败输出 `missing_optional_needspace.txt`，使用已有 TeX/etoolbox 的简单页剩余空间判断，不安装新包。
- 日志、正文抽取和构建回执保存于本目录；临时渲染在各报告 `build/render200/`，不作为正式数据图或互动 Evidence。

当前成功构建日志中无缺字、未定义引用、字体替代或 Overfull。少量表格 Underfull 只涉及换行间距，已在真实渲染检查其可读性。当前没有新增系统包、语言包、字体、工具链或持久配置。独立全文审核与最终 G3 内容核对尚未完成。
