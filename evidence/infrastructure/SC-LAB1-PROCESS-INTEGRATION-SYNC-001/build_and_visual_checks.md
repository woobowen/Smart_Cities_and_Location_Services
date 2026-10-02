# Process 接管：实际构建与逐页检查

本记录由实际负责接管及构建的 `/root/process_build` 上下文编写，属于工程实施自检。独立复验由 `/root/independent_review` 另行记录于 [independent_review](independent_review/REVIEW_NOTES.md)。本轮没有重新运行实验、参数搜索或模型调用，也没有修改已验收正文、截图、箭头、图规格、结论或公共 P2 色值。

## 输入、安全检查与原件保护

| 对象 | SHA256 / 实际核验 |
|---|---|
| 批准 PDF | `45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83`，77 页 |
| 批准 ZIP | `00cb7b641b37b2a71a552fc5bef47fc551a16ea7ce88bcf139f2e68a5f1451da` |
| ZIP 内 PDF | 与单独批准 PDF 字节一致 |
| 解包工作源 | `task1/reports/process1/source/`，343 个普通文件逐成员与 ZIP 字节一致，最终构建后再次核对一致 |
| 嵌套历史 ZIP | `provenance/input_snapshot/PreTask_Accepted_Source.zip`，104 成员，SHA256 `d7382f847cae937b495f2ec64d58e7ab65dd7b4ec7de5259f5beacc90975f53b` |

正式原件位于 `reports/process-report/experiment1-revised/`，根目录用户交接原件继续保留。两个归档均实际做了 CRC、重复名、路径越界、绝对路径、反斜杠路径、链接、字体二进制和高置信真实凭据模式检查；未发现阻断项。这是明确范围的静态扫描，不是对所有图中文字作秘密不存在的绝对保证。成员、大小和哈希见 [外层 ZIP](build_checks/zip_safety_and_members.json)、[嵌套 ZIP](build_checks/nested_zip_safety_and_members.json)、[解包核对](build_checks/extraction_hash_checks.json)。

包内 `provenance/history`、`provenance/pretask_source_snapshot` 和作者检查输出继续保持历史身份。`compile.sh`、`tools/build_report.py`、`tools/make_diagrams.py` 及批准 JSON 没有改动。仓库适配仅位于 `build_process.py`、`accepted-source.json` 和局部 `fontconfig.conf`，未通过修改生成 TeX 掩盖旧生成链。

## 实际两条路线

每条路线均从批准工作源复制到新的私密隔离目录，移除主报告预置 PDF、`build/` 和 `review/`，保留必要的六幅图 PDF，再执行原始脚本。原件目录没有运行覆盖式编译。日志保留两个 XeLaTeX pass 的完整输出。

| 路线 | 实际顺序 | 结果与记录 |
|---|---|---|
| A 静态正文 | `bash compile.sh` | exit 0；两个 XeLaTeX pass 成功；[命令及环境](build_checks/route-A-final.json)、[新 PDF](build_checks/route-A-final.pdf)、[pass 1](build_checks/route-A-final_compile_stdout_1.log.txt)、[pass 2](build_checks/route-A-final_compile_stdout_2.log.txt) |
| B 全生成 | `python tools/make_diagrams.py` → `python tools/build_report.py` → `bash compile.sh` → `python tools/render_review.py` → `python tools/audit_report.py` | 五条命令均 exit 0；[命令及环境](build_checks/route-B-final.json)、[新 PDF](build_checks/route-B-final.pdf)、[pass 1](build_checks/route-B-final_compile_stdout_1.log.txt)、[pass 2](build_checks/route-B-final_compile_stdout_2.log.txt) |

实际 A、B 两个新 PDF 的 SHA256 都是：

`971f9739e43b9d13a3e6e4b3154e47968d8d40a2fd63b9cae87950cb72226c2c`

它们与批准 PDF 的 SHA256 不同，不声明二进制一致。兼容阅读入口 `task1/reports/process1/process1.pdf` 始终保持批准原 PDF 字节；工程重建件单独保存。

最终适配层再次实际执行了下列统一命令，exit 0；[完整 receipt](build_checks/adapter_final/build_receipt.json)、[控制台](build_checks/adapter_final_console.txt) 和两遍编译日志已保存：

```bash
.venv/bin/python task1/reports/build_reports.py --report process --regenerate --render --evidence-output /home/addaswsw/.local/state/codex-task-work/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/adapter-final
```

最后运行的新 PDF 与已实际目视的 B PDF 字节相同，全部 77 张 PNG 也分别字节相同，故相应目视记录可以绑定最终适配层产物；见 [逐页 SHA256 等价核对](build_checks/adapter_final_equivalence.json)。这是本机运行记录中的绝对路径，构建实现本身不依赖该个人路径；使用者可把 `--evidence-output` 指向任意新的工程证据目录。

可重复使用的仓库入口为：

```bash
.venv/bin/python task1/reports/build_reports.py --report process --render --evidence-output /tmp/sc-process-static-check
.venv/bin/python task1/reports/build_reports.py --report process --regenerate --render --evidence-output /tmp/sc-process-generated-check
```

## 全文、版面、素材及全页渲染对照

以下为最终收敛版本结果，早期失败或差异结果没有删除：

- A/B 均为 77 页，全部页面尺寸一致；`pdftotext -layout` 逐页全文包括空白完全一致。最终文本差分文件为空；[A 比较](build_checks/route_A_final_comparison.json)、[B 比较](build_checks/route_B_final_comparison.json) 保留每页结果。初始 p1、B p59 的文本空白差异仅属于被替代的环境检查结果，见 `initial_text_comparison.json`，未改写为最终通过记录。
- A/B 全部嵌入截图的像素摘要、尺寸和放置矩形一致，见 [embedded_image_comparison.json](build_checks/embedded_image_comparison.json)。没有为了复现改动原宽素材、裁片或伪报 PPI。
- B 重新生成的 `main.tex`、`chapters/pages.tex`、所有 crop、规格及 page/crop/arrow/input 来源映射，与批准源相同。六幅 draw.io、SVG 也相同；仅六幅生成 PDF 和报告/预览派生产物字节改变，见 [实际变化成员](build_checks/final_generated_member_changes.json)。
- 六幅图的单独 PDF 在同一 PyMuPDF 1.26.7、200 dpi 下逐像素相同，文本也相同；新图 PDF Producer 为 Cairo 1.18.0，批准图为 Cairo 1.18.4，见 [六图对照](build_checks/final_figure_pdf_comparison.json)。没有为追求相同 Producer 升级系统 Cairo。
- 全报告用同一 PyMuPDF 1.26.7 在 200 dpi 对照全部 77 页：71 页像素完全相同；34、41、45、59、75、77 六个技术图页存在极小像素差，最大平均 RGB 绝对差为 `0.0008643717046474971 / 255`。当前 XeTeX 的矢量嵌入/舍入是合理的环境解释，但不将它写成已证明仅为 PDF 元数据差异。六页批准/重建实际 PNG 均保存于 [render_difference_pages](build_checks/render_difference_pages/index.json)，供远程实查。A/B 本身相同说明这些差异并非 B 重新生成正文或更换图规格所致。
- 最终编译未发现 missing character、undefined command/reference/citation、Overfull 或要求重跑的未解决诊断；原日志完整保留。

全页 PNG 为本地衍生品，分别保存在私密任务目录下 `approved_render_200dpi/`、`route-A-final/render200/`、`route-B-final/review/render_200dpi/` 和 `adapter-final/render200/`。仓库保存每页结果、哈希、完整新 PDF 和六个必要差异页，而不重复上传所有相同渲染。

## 实际逐页目视范围

`/root/process_build` 实际逐张打开了 B 第 1–39 页的 200 dpi 单页 PNG，未用联系表代替；查看工具可能为屏幕显示缩小图片。检查封面双重目的与 ShareX/图片分割器原句、真实用户 UI 入口、续页、截图为主体的布局、短侧注、精确箭头、同页标题与第一组内容、字体和页脚，未见本轮新增裁切、错位、缺字、遮挡、标题孤页或箭头回退。逐页文件哈希和角色边界见 [实施者目视记录](build_checks/visual_self_check_pages_001_039.json)。

独立上下文实际查看第 40–77 页并抽查第 1、9 页，范围与逐页观察由其本人写于 [visual_observations.json](independent_review/visual_observations.json)，不是实施者代签。两者共同覆盖当前全部 77 页；独立审查并未冒称对每条 Evidence 重新 Lock。

批准原件中已有的原宽素材分辨率、部分原裁片边界和截图内历史状态均保留。例如独立审核指出 p76 源裁片底部局部行截断属于原批准裁片，不能因此声称“所有原话从无裁切”，也不能在本轮擅自重新裁剪。当前结论只覆盖工程接管没有新增视觉回退，不把整体文稿验收等同逐项 Evidence Lock。

`tools/audit_report.py` 的本次执行输出仍注明 `AUTHOR_SELF_CHECK`，实际报告 77 页、40 evidence units、134 crops、85 arrows，程序检查通过；它是原作者检查程序的真实重放，[输出](build_checks/adapter_final/upstream_author_check_replayed.json) 没有被重新命名为独立验收。原包中 `user_acceptance=PENDING_FOR_THIS_LANGUAGE_REVISION` 是当时记录；当前 `accepted-source.json` 另行登记用户在本轮提示中已验收本对 PDF/ZIP，绑定批准哈希。

## 环境修复、安装清单与保护测试

使用现有项目 `.venv`、Python 3.12.3 和用户 TeX Live 2026 的 XeTeX 0.999998。完整版本及字体选择见 [environment_checks.json](build_checks/environment_checks.json)。没有新建平行科研环境，没有安装 apt 系统包，没有更新 TeX Live 工具链，没有改启动脚本、全局认证或 TLS。

1. **报告局部 Python 依赖**：实际执行 `.venv/bin/python -m pip install --target .venv/process-report-build-deps -r task1/reports/process1/source/requirements-build.txt`。按源包精确版本安装 Pillow 12.3.0、numpy 2.3.5、PyMuPDF 1.26.7、CairoSVG 2.8.2；传递依赖为 webencodings 0.6.1、defusedxml 0.7.1、cssselect2 0.10.1、cffi 2.1.1、pycparser 3.0、cairocffi 1.7.1、tinycss2 1.5.1。适配层仅对报告子进程设置 `PYTHONPATH`。原科学环境默认 numpy 1.26.4、Pillow 10.2.0 未被升级。[安装日志](build_checks/python_dependency_install.log.txt)、[版本清单](build_checks/dependency_versions.json)。
2. **缺少的 ragged2e**：首次 A 编译实际失败并保留日志。`tlmgr install ragged2e` 因工具自身需要先更新而拒绝；没有执行 `tlmgr update --self`。官方 TDS URL 返回 404 后，从 CTAN 官方镜像下载 `ragged2e.zip`，CRC/安全检查后在私密目录用 `latex -interaction=nonstopmode ragged2e.ins` 生成，仅把 `ragged2e.sty` v3.6（2023/06/22）安装到 `.venv/texmf/tex/latex/ragged2e/`。适配层局部设置 `TEXMFHOME`，`kpsewhich` 实际找到它。源码归档 SHA256 `6ddd7c829d4bdabed187c3d0acf45f5af4f156cdfb3af3a90314a025c10209ca`；sty SHA256 `bbaa95d82bff14cd13fdead40edcdd31d7bd1e84127fe85f6b20dccff474cf4d`。[tlmgr 拒绝日志](build_checks/tex_dependency_install.log.txt)、[下载](build_checks/ragged2e_download.json)、[安装](build_checks/ragged2e_install.json)、[生成日志](build_checks/ragged2e_unpack.log.txt)。
3. **Noto Sans 用户局部字体**：系统已有 Noto Sans CJK，但没有所需拉丁 Noto Sans。通过官方 `notofonts/noto-fonts` GitHub raw 文件安装 Regular、Bold、Italic、BoldItalic、ExtraBold 到 `~/.local/share/fonts/sc-process-noto-sans/`，只对该目录运行 `fc-cache -f`。每个 URL、字节数、SHA256 见 [font_install.json](build_checks/font_install.json)。字体二进制不分发、不进入 Git。
4. **字体选择修复**：实际发现系统自动选择 CJK Black，而批准 PDF 为 Bold；拉丁粗体批准字体为 ExtraBold。先尝试 fontconfig glob 拒绝未生效，相关 `route-*-font-fixed` 记录保留为已被替代的失败适配。随后用仅构建进程启用的 `task1/reports/process1/fontconfig.conf` 按 family/style 排除冲突权重。源 `main.tex` 与生成器保持原字节；最终字体选择复现批准 PDF。适配层现在在编译前检查四个实际字体 PostScript name，防止环境变化静默换字。没有修改 `/etc/fonts` 或用户全局 fontconfig。

前述依赖用于以后重建当前已验收报告，故保留并记录位置；不因任务为一次性而无提示移除。清理需要先确认不再依赖它们或已有验证过的替代环境。

保护测试实际执行 `.venv/bin/python -m pytest -q task1/tests/test_process_report_build.py`，**8 passed**，见 [日志](build_checks/process_guard_tests.txt)。覆盖批准 hash 错误、规格变化、裁片变化、缺成员、多成员、文件软链、目录软链在任何构建命令前拒绝，并验证真实运行的替代生成器一旦恢复旧正文，在编译前被阻断；失败保留当前阅读 PDF 与原工作源。测试使用隔离的小归档夹具，不篡改真实原件。

适配层最终代码与配置 SHA256 已在 [adapter_final_equivalence.json](build_checks/adapter_final_equivalence.json) 固定；其中 `build_process.py` 为 `60cccad6f9868059d2c9c81628e49961b29bd32a9e7e061d07899562d5d7e264`。内部独立核验及网页 GPT 二重验收结论以对应独立记录为准；本记录不代签教师提交或 Evidence Lock。
