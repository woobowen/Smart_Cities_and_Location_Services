# 实验一报告工程

Experiment保持已验收25页原件；Process为77页第76页授权局部修正版，承接此前全文认可，本次新文件逐页用户复核另记。本轮检查见 [REVIEW_PACKET](../../evidence/infrastructure/SC-LAB1-FINAL-SUBMISSION-CLOSEOUT-001/REVIEW_PACKET.md)；上轮工程二审PASS，本轮网页最终二审仍为PENDING。页数只用于校验这两份成品。

| 报告 | 唯一主源 | 当前阅读入口 | 不可变批准件 |
|---|---|---|---|
| Experiment | [Experiment_Report.tex](experiment1/Experiment_Report.tex) | [experiment1.pdf](experiment1/experiment1.pdf) | [PDF/ZIP](../../reports/experiment-report/experiment1-reconstructed/) |
| Process | [source/main.tex](process1/source/main.tex) | [process1.pdf](process1/process1.pdf) | [PDF/ZIP](../../reports/process-report/experiment1-revised/) |

Process 的原始 PDF/ZIP、静态正文、规格、裁片和历史来源保持批准身份；[接管说明](process1/README.md)区分不可变输入、唯一工作源和历史草稿。前期 [PreTask](../../reports/process-report/pre-task1/)继续保留，其旧 PARTIAL 仅适用于旧源包，不能推定新报告无法复现。

在仓库根目录复用现有环境，输出证据目录应为本次新目录：

```bash
# 静态 Process：原 compile.sh 两次 XeLaTeX
.venv/bin/python task1/reports/build_reports.py --report process --render --evidence-output /tmp/sc-process-static
# 完整 Process：make_diagrams → build_report → compile → render_review → audit_report → check_p76_closeout
.venv/bin/python task1/reports/build_reports.py --report process --regenerate --render --evidence-output /tmp/sc-process-full
# 兼容统一入口；默认 all，Experiment 也可单独选择
.venv/bin/python task1/reports/build_reports.py --report all --render --evidence-output /tmp/sc-both-reports
# 只生成新的工程待审包，不发送教师
.venv/bin/python -m task1.goal3 REPORT_BUILD --output /tmp/REVIEW_ONLY_实验一_双报告.zip --evidence-output /tmp/sc-package-rebuild
```

统一构建器在隔离目录移除预置主PDF与build产物，再运行实际源入口。当前阅读/打包入口保持批准PDF原字节，`rebuilt.pdf`记录本次实际编译输出；二者hash不同不能仅凭页数宣称等价。逐页文本、同渲染器200dpi像素与实际目视范围分别记录。`--regenerate`只生成报告图和页面，不执行科学实验；旧 `build_*_sources.py` 与12页稿不再进入正常报告链。

打包器校验两个阅读PDF的明确hash，拒绝旧Process混入；执行冻结依赖probe，不调用模型、不跑轨迹处理。历史 [完整双报告 REVIEW_ONLY ZIP](../submission/REVIEW_ONLY_10245102410_吴博闻_实验一_完整双报告.zip)保持旧身份。当前[正式候选ZIP](../submission/teacher-delivery/10245102410_吴博闻_实验一.zip)由独立[教师适配器](../submission/build_teacher_submission.py)生成，真实成员数、解压终检与隔离probe见本轮REVIEW_PACKET；本次没有FULL轨迹复算。

编译依赖：XeLaTeX、ctex/fontspec及源包声明的LaTeX宏包（含placeins、needspace、pdflscape等），DejaVu Serif/Sans、Noto Serif/Sans/Mono CJK SC；PDF检查需Poppler，渲染比较使用现有Python Pillow。源包含图PDF，正常编译不需Python绘图依赖、网络或模型凭据。公共颜色只从 `templates/latex/common/p2_cloud_sorbet_colors.tex` 读取；源ZIP中的颜色是受控便携副本。

SYNC-003集成时缺少placeins/needspace，已仅安装至隔离TeX树并放入 `.venv/texmf`，构建器在调用者未指定TEXMFHOME时自动使用它。此次最终收尾没有安装或升级依赖，继续保留既有环境。复现该隔离依赖补齐步骤（只在缺包且现有TeX为用户TeX Live时执行，仓库镜像须与TeX版本匹配）：

```bash
tlmgr --usermode --usertree "$PWD/.venv/texmf" init-usertree
tlmgr --usermode --usertree "$PWD/.venv/texmf" install placeins needspace
```

直接在本目录的experiment1子目录运行源包build.sh时，用进程局部 `TEXMFHOME`指向上述树；统一Python入口已处理该路径。SYNC-003当时没有安装字体或修改全局TeX/TLS/认证配置，其来源、版本、SHA和命令在[历史环境变更记录](../../evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/report/environment-changes.json)。本轮Process新增依赖见下文。

Experiment的两幅结构图在 [figures/](experiment1/figures/)中保留真实可编辑.drawio及SVG/PDF；绘图代码和冻结输入位于source/data。SYNC-003当时核验了归档成员、XML节点/边和编译嵌图，未重新生成十幅图，也未重跑全部实验。25页、七章、10图/17表均是这份实验一成品的事实，不是未来任务配额。项目正式写作遵循[Writing Guide](../../docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md)与[Visual System](../../docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md)。

2026-10-02接管时新增的Process局部依赖：在 `.venv/process-report-build-deps` 安装其 `requirements-build.txt` 的精确版本及传递依赖，未升级科学环境的numpy1.26.4/Pillow10.2.0。Noto Sans五款字体从官方notofonts源码仓库下载到用户字体目录，不随工程分发；CJK字体沿用已安装版本。`ragged2e`从CTAN官方源码归档生成sty后补入 `.venv/texmf`，未更新TeX工具链。详细来源/hash/命令见 [原依赖记录](../../evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/build_checks/)。

[报告专用fontconfig](process1/fontconfig.conf)仅由Process子进程加载，复现批准PDF实际使用的Noto Sans ExtraBold/CJK Bold字重，避免本机多字重导致版式漂移；不修改文稿或全局字体配置。需要复现时保留这些局部依赖；完整生成会生成六幅draw.io/SVG/PDF，但不运行研究代码。源包旧作者audit保留历史身份，重放结果仅作为工程程序检查。
