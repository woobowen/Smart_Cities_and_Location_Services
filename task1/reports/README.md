# 实验一报告工程

当前[非Process收尾](../../evidence/infrastructure/SC-LAB1-NONPROCESS-CLOSEOUT-001/REVIEW_PACKET.md)仅承接治理、验收和技术交接；[89371f6网页GPT二审](../../evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review/REVIEW_RECEIPT.md)按真实来源登记。本轮不重新编译报告、重画图或生成ZIP，下面的构建及隔离依赖说明沿用SYNC-003已验收工程。Process由用户指定的另一对话继续，原稿与既有PARTIAL限制保持。

当前 Experiment 为用户已验收的25页重构版。权威章节源在 [experiment1/chapters](experiment1/chapters/)，主入口 [Experiment_Report.tex](experiment1/Experiment_Report.tex)，兼容入口 [experiment1.tex](experiment1/experiment1.tex) 仅引用该主文件。不可变批准 PDF/ZIP 在 [canonical参考目录](../../reports/experiment-report/experiment1-reconstructed/)；[当前PDF](experiment1/experiment1.pdf) 保持批准PDF原字节。

[Process PDF](process1/process1.pdf)仍为12页技术事实送审稿，真实互动原件/spec/Lock另有未完成状态。[前期Process参考](../../reports/process-report/pre-task1/)与它分开；前期源包复现仍为[既有PARTIAL](../../evidence/infrastructure/SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md)。当前Experiment构建不生成Process，也不修改其正文、图或metadata。

在仓库根目录使用现有环境：

```bash
.venv/bin/python task1/reports/build_reports.py --render
.venv/bin/python -m task1.goal3 REPORT_BUILD --output /tmp/REVIEW_ONLY_实验一_新报告构建.zip
```

构建器逐次将当前真实源码复制到没有预置报告PDF/辅助文件的临时目录，运行源包原 `bash build.sh`（两次XeLaTeX）；核对章节/图源与批准ZIP、公共P2颜色值、姓名/学号、25页和全文。`--render`生成200dpi全页图并记录与批准版的像素差，实际目视结论另记。输出的 `rebuilt.pdf` 为本次真实编译产物；当前阅读/打包PDF维持批准原件字节，不宣称两者SHA相同。默认构建记录在 `task1/evidence/goal3/report_build/accepted/`，可用 `--evidence-output`指定本轮新目录。

REPORT_BUILD只读包中冻结依赖并执行隔离无Git依赖probe，然后生成新REVIEW_ONLY ZIP；它不执行参数/模式/全量清洗，不生成数值摘要和旧图，不调用模型。输出ZIP已存在时拒绝覆盖。旧22页生成器与旧全文/目视记录属于提交 `4483f520eabb5358d1f35cf5c33a81d3b01e47e0` 的历史；本目录遗留 `*_generated.tex` 和旧 `build_*_sources.py` 为历史素材，不是当前章节源，正常入口不再调用。

编译依赖：XeLaTeX、ctex/fontspec及源包声明的LaTeX宏包（含placeins、needspace、pdflscape等），DejaVu Serif/Sans、Noto Serif/Sans/Mono CJK SC；PDF检查需Poppler，渲染比较使用现有Python Pillow。源包含图PDF，正常编译不需Python绘图依赖、网络或模型凭据。公共颜色只从 `templates/latex/common/p2_cloud_sorbet_colors.tex` 读取；源ZIP中的颜色是受控便携副本。

SYNC-003集成时缺少placeins/needspace，已仅安装至隔离TeX树并放入 `.venv/texmf`，构建器在调用者未指定TEXMFHOME时自动使用它。复现该隔离依赖补齐步骤（只在缺包且现有TeX为用户TeX Live时执行，仓库镜像须与TeX版本匹配）：

```bash
tlmgr --usermode --usertree "$PWD/.venv/texmf" init-usertree
tlmgr --usermode --usertree "$PWD/.venv/texmf" install placeins needspace
```

直接在本目录的experiment1子目录运行源包build.sh时，用进程局部 `TEXMFHOME`指向上述树；统一Python入口已处理该路径。没有安装字体或修改全局TeX/TLS/认证配置。具体来源、版本、SHA和本轮命令在[环境变更记录](../../evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/report/environment-changes.json)。

两幅结构图在 [figures/](experiment1/figures/)中保留真实可编辑.drawio及SVG/PDF；绘图代码和冻结输入位于source/data。此次核验了归档成员、XML节点/边和编译嵌图，未重新生成十幅图，也未重跑全部实验。25页、七章、10图/17表均是这份实验一成品的事实，不是未来任务配额。项目正式写作遵循[Writing Guide](../../docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md)与[Visual System](../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)。
