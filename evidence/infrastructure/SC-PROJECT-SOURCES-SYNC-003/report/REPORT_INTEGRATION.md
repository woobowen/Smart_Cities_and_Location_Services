# Experiment 报告集成与包回归

Engineering scope: SC-PROJECT-SOURCES-SYNC-003 §7/8/11，已验收报告接管及当前导航。未新增方法、数据口径、数值实验或记录级模型调用；数值CODE_SHA继续为原真实运行身份。

批准PDF/ZIP已原字节导入 `reports/experiment-report/experiment1-reconstructed/`，SHA保持 `2a940be5…5cdd0` / `6c0d2cc5…4dcd`。完整hash、72成员CRC、路径/重复/链接/秘密/字体/执行行为检查及两幅draw.io节点/边数见 [source-archive-check.json](source-archive-check.json)。源包内PDF与批准PDF逐字节相等。主文与章节、图形、数据和绘图脚本均保留；源中唯一语义外适配是P2颜色副本改为引用公共配色。公共P2原件未变。

`task1/reports/experiment1/Experiment_Report.tex`与`chapters/`接管当前权威章节，兼容的`experiment1.tex`引用新主文件。旧22页`*_generated.tex`作为非活动历史留存，正常构建不再调用旧章节生成脚本。`task1/reports/build_reports.py`每次在临时干净目录中调用源包原build.sh；`python -m task1.goal3 REPORT_BUILD`仅调用报告编译和既有包构建/probe，不再调用Journal失效写入、summary、figure或Process生成链。新编译PDF和批准PDF分开保存；只有实际源码编译、身份/页数/全文检查通过后才把批准原字节放入当前阅读/打包位置，未用预带PDF伪装编译。

真实命令与结果：

- `bash build.sh`在源ZIP无预置报告PDF的干净提取目录首次退出1，原因placeins缺失；kpsewhich还确认needspace缺失。[失败日志](clean-build-attempt1.txt)。
- 在临时TeX树补齐placeins/needspace，使用进程局部TEXMFHOME再次运行原build.sh，退出0、25页、无缺字/溢出/未定义引用等诊断；正文提取与批准PDF逐字节一致。[clean-build-result.json](clean-build-result.json)、[环境与依赖记录](environment-changes.json)。
- 原先新增的像素全等判断错误地把轻微栅格/字体度量差视作失败；没有改批准内容，改为保存逐页差异并进行真实目视，同时增加章节/图源逐字节保护。[实际视觉检查](visual-inspection.md)。
- `.venv/bin/python -m task1.goal3 REPORT_BUILD --output /tmp/REVIEW_ONLY_SC_PROJECT_SOURCES_SYNC_003_regression.zip --evidence-output evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/report/normal-build-1`，退出0；25页、116成员、CRC/probe通过，Process不变。[第一次正常回执](normal-build-1/build_receipt.json)。
- `.venv/bin/python -m task1.goal3 REPORT_BUILD --output task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip --evidence-output evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/report/normal-build-2`，退出0；同源第二次25页、116成员。[第二次输出](normal-build-2-command.txt)、[构建回执](normal-build-2/build_receipt.json)。
- `.venv/bin/python -m pytest -q task1/tests/test_accepted_report_integration.py task1/tests/test_closeout_identity.py task1/evidence/goal3/package/test_package.py`，17 passed、10 subtests passed；包含错hash/改章节不得编译覆盖、已有ZIP保护、只触发报告/打包、FULL/live函数AST与旧真实执行包相同等正反例。[原测试输出](targeted-tests.txt)。

当前新包 `task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip` 的SHA256为 `231ce92475fdfe7ed12fa1c7e3304c22d6fd56ce39a0b53b43fee87103334a63`。其中Experiment为批准PDF原字节；Process、两Notebook、依赖声明、raw、冻结合同、记忆、数值模块保持原身份。与旧实际FULL解压输入包比较，112个成员完全相同，变化仅PACKAGE_MANIFEST、README、goal3/__main__.py与Experiment PDF。[逐成员关系](integration-verification.json)。__main__.py确实改变，不能宣称运行闭包全部字节相同；原FULL函数和LIVE函数AST未变，报告入口另做[独立隔离CLI/gate回归](../c_review/independent-package-review.json)。这不是本轮又运行FULL。

当前teacher_delivery_mapping的44个Experiment物理页锚来自新PDF，Notebook/Process原绑定不变；task1 README、reports README、REVIEW_GUIDE、TECHNICAL_HANDOFF与DEFENSE_NOTES已更新当前入口。旧22页视觉回执和旧包保留历史身份，没有改写为新稿的审核结果。

Process工作稿原字节保护；前期31页PDF/ZIP未改，既有SOURCE_ARCHIVE_BUILD=PARTIAL及文字/标注几何和缺字限制继续见[原记录](../../SMART-CITIES-GOVERNANCE-PROCESS-REFERENCE-SYNC-002/source-archive-check.md)。此次没有重画Process、产生新Lock或将前期材料宣称为完整实验一Process。两幅.drawio可编辑XML和现成图像嵌入已检查，但没有重新生成十幅图或桌面draw.io交互验证，不扩大为全图/全实验复算。

本轮仅在隔离树增加placeins/needspace；没有新增系统包、Python包、字体或全局配置。包仍REVIEW_ONLY，Submission=NOT_READY，GPT第二审核待实际远程读取；没有替用户上传UI、发给教师或签理解验收。

新包 `PACKAGE_MANIFEST.json` 的 `metadata` 完整继承旧实际FULL包的冻结身份源。其 `report_revision_date=2026-09-28` 与默认 `review_package_name` 是该旧身份配置字段，不是此次Experiment的修订日期或本ZIP实际文件名；此次Experiment封面仍为批准的2026-09-29，实际ZIP名及SHA以本轮README/build receipt为准。未为消除这个历史字段差异去修改冻结assignment、Process或重打包。
