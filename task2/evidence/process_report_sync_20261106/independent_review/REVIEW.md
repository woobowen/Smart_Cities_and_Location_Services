# 实验二 Process Report 接管：独立内部核验

审查者：Codex 子 Agent `process_integration_verifier`，与集成执行线程使用独立执行上下文。审查基准：`b7fd9ee522905c11ddcea760470e7a5f0c1be9f0`。本记录是工程核验，不授予 Evidence Master Lock、GPT 外部二审或教师提交通过。

## 已实际核验的范围

- 私密入站 ZIP 的 SHA-256 为用户指定的 `f73432aef93abdad0c37757df03b13811ab0beb1b508f700562bb0edada1c55a`，CRC 检查通过，成员名无路径越界。正式 PDF 与该 ZIP 内 `task2/reports/process/main.pdf` 字节一致，SHA-256 为 `c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f`，Poppler 确认为 16 页。
- 11 个任务专属 `.tex` 与精确入站 ZIP 比较：9 个原字节不变；`main.tex` 和 `evidence/03_license.tex` 仅更换图片相对路径，共 3 处路径替换。已安装源码与正式 PDF 文本均不含被删除的附录标题，主文件无 `\appendix`。
- 源码实际图片引用与资产目录集合精确相等，共 18 个 PNG；其文件字节均与精确入站 ZIP 一致。独立用 `pdfimages -png` 提取正式 PDF 的全部 18 个图像，每个发布 PNG 的 RGB 像素与其中恰好一个内嵌图像一致。18 个文件均为普通文件，无符号链接；PNG 只含 IHDR/IDAT/IEND，无文本、EXIF 或尾随数据。
- 独立按基准 Git 对象逐字节核对 2,964 个冻结文件：公共模板、`common.tex`、Experiment Report、生成数据、算法实现、研究结果、科研图、技术图、Notebook、测试及其他未授权更改的脚本均无变化。此核对不执行算法、训练模型或重算实验。
- 8 页历史 PDF 与基准中的原 Process PDF 字节一致，SHA-256 为 `a2c57f58d246e326d398003045cadad090db19dcab9163cae5871fd791b01de1`；历史 README 明确标为技术交接稿，旧源包仍保持其原配对身份。

以上可追溯结果见 [integration_audit.json](integration_audit.json) 与 [asset_metadata_audit.json](asset_metadata_audit.json)。检查脚本为 [verify_integration.py](verify_integration.py)。

## 构建脚本及打包脚本

实际审阅 `build_reports.py` 与 `package_report_sources.py`，并进行 AST 语法检查和 7 个隔离合成保护测试。Process 分支的正常路径、编译失败、全文不一致、页面像素不一致均保持已认可 PDF 的字节；打包器拒绝覆盖现存输出、未引用 PNG 和缺失 PNG，拒绝发生在写入 ZIP 之前。被审脚本 SHA 及方法局限见 [script_guard_checks.json](script_guard_checks.json)。测试使用独立临时夹具和模拟子进程，不冒称真实 XeLaTeX 编译或逐页视觉检查。

Process 构建以独立临时输出目录运行 XeLaTeX，并通过本进程专用 Fontconfig 配置排除竞争的 `NotoSansCJK-Black.ttc`，使自动粗体解析使用获批 PDF 的 Bold 字重。独立最小 fontprobe 实测成功；没有修改报告、公共字体声明、系统字体或全局配置。打包器按实际 `.tex` 图片引用形成精确 PNG 集合，不扫描并发布原帧目录。

## 真实渲染差异与限制

首次原样构建的 16 页全文相同，但渲染不相同。独立将原 ZIP 的原样源码构建与安装后的路径适配构建按 200 dpi 比较，16 页均逐像素相同，证明第一次差异不是此次路径适配引入。字体列表显示获批 PDF 使用 `NotoSansCJKjp-Bold`，本机首次构建选择 `NotoSansCJKjp-Black`；实际后端分别为 xdvipdfmx 20240305 / PDF 1.5 与 20260317 / PDF 1.7。见 [render_diagnosis.json](render_diagnosis.json)。

字重环境修复后的实际回执确认 XeLaTeX 返回 0、16 页、全文相同、无检查出的字体/引用/溢出问题，正式 PDF 未被覆盖。独立重算全部 16 对 200 dpi 页面：1、6、15 页逐像素相同，其余 13 页仍有差异；第 7 页差异像素占 3.402843%，其他非零页为 0.002326%–0.204125%。见 [fontfix_render_measurements.json](fontfix_render_measurements.json)。

独立实际查看了第 7 页的两份完整 200 dpi 渲染。三组截图、侧注、矢量箭头及分页一致，残余差异主要集中于底部截图的细微栅格位置和其上来源条。该查看不等于逐像素相同，也不单凭视觉判断证明全部差异只由特定后端机制引起。独立 Agent 没有逐页实际查看其余 15 页；全页自动比较与实际查看范围分别记录。

当前严格构建验证命令会因残余像素差异返回非零。应分别报告“XeLaTeX 编译与全文核验通过”和“完整像素验证未通过”，不能将完整命令写成 PASS。此限制不改变当前正式 PDF 的用户指定 SHA 身份；本轮没有用重编译产物覆盖正式 PDF。

## 未覆盖范围

- 未取得删除附录前的完整已认可报告，未自行重建其前后差分；本次内容身份以用户指定新版 SHA 与精确源码包为准。
- 未检查原始视频；视频本轮未提供。原帧、未选 crop 和完整入站 ZIP 保持私密，不因该工程核验获得公开授权。
- 未执行 ChatGPT UI 上传、GitHub 外部 GPT 二审、Evidence Master Lock、理解验收或教师提交。
- 最终 staged 集合、Project Sources 与远程固定提交的追加核验单独承接；本记录不自动覆盖后续更改。

结论：报告字节、配对源码的最小适配、发布图片范围、冻结成果及历史身份的独立接管核验通过；当前构建环境仍存在明确记录的像素渲染复现差异。最终对外状态应由协调线程按实际发布结果报告为 `READY_FOR_GPT_REVIEW`，不得记为 GPT 外审通过。
