# 独立内部工程审查

**结论：本地待发布内容的独立内部工程核验 PASS。** 本记录由实际独立上下文 `/root/independent_review` 编写。该上下文未实施生产修改，仅提交审查脚本与记录；集成由主线程和构建/同步角色实施。开始基点为 `6527945ad8e526fa606b2c09835f2e51291fa4d0`，最终实现以 [独立记录的代码 SHA256](independent_review/reviewed_implementation_sha256.json)、下述产物 SHA256 和后续发布回执绑定。本记录不宣称已经完成远程发布核验；该步骤由主线程另存真实回执。网页 GPT 本轮二审仍为 **PENDING**。

## 独立实际执行的检查

| 范围 | 本上下文实际检查与结果 |
|---|---|
| 批准输入 | 独立转录用户附录基准并重算，15 个批准输入全部匹配。最终 active/release 共 30 个路径实例及 Git 暂存区对应 30 个 blob 全部匹配；四份新版规范无字节改写，Research Protocol 保持 v1.2 / 2026-09-29。见 [输入归档检查](independent_review/initial_input_archive_audit.json)、[最终字节核验](independent_review/final_byte_protection_audit.json)、[暂存区核验](independent_review/staged_source_hashes.json)。 |
| Process 配对与工作源 | 根目录、正式原件及 ZIP 内 PDF 身份一致；343 个工作源成员与批准 ZIP 逐成员同字节。当前 `process1.pdf` 为批准全文；旧稿的 12 个文件完整保存到历史目录。批准 PDF `45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83`；ZIP `00cb7b641b37b2a71a552fc5bef47fc551a16ea7ce88bcf139f2e68a5f1451da`。 |
| 构建真实性与入口 | 读取最终 A/B 命令、环境、四份实际 XeLaTeX stdout，每份均实际输出 77 页；阅读原 compile/generator 和最终统一适配层。隔离副本移除预置主 PDF/build/review，B 执行 make_diagrams、build_report、compile、render_review、audit 五条命令，均有 exit 0。编译由构建角色执行，本上下文独立复验输出及入口，未把历史作者检查当作新独立审核。 |
| 全 77 页独立程序对照 | 使用同一 PyMuPDF 1.26.7 以 200 dpi 重新渲染批准件和新 B；A/B PDF 字节相同，SHA256 均为 `971f9739e43b9d13a3e6e4b3154e47968d8d40a2fd63b9cae87950cb72226c2c`。全部页面文本含空白、尺寸及全部嵌图像素摘要/尺寸/位置一致。保存的 77 张 B PNG 与本次独立重渲染逐像素一致。[逐页结果](independent_review/independent_pdf_comparison.json)。 |
| 最终适配层产物 | 独立读取最终适配层输出、仓库存档 PDF 和已目视 B，三份 PDF 同字节；77 张最终 adapter PNG 与 B PNG 逐文件同字节。[复验结果](independent_review/final_adapter_independent_check.json)。最终 `build_process.py` SHA256 为 `60cccad6f9868059d2c9c81628e49961b29bd32a9e7e061d07899562d5d7e264`。 |
| 实际目视 | 本上下文用 `view_image(detail="original")` 逐张打开最终 B 的 **40–77 页**，另抽查 **1、9、34 页**，共 41 页。另实际打开批准原件的 34、41、45、59、75、76、77 页，直接核对全部差异图页及 p76 原裁切边界。[逐页观察](independent_review/visual_observations.json)、[补充图哈希](independent_review/supplementary_visual_bindings.json)。构建角色实际检查 1–39 页，合并覆盖全 77 页；未声称本独立上下文目视了所有 77 页。 |
| 原宽与裁片 | 对 crop_map 中 134 个普通窗口从真实来源按批准边界独立重裁，全部像素相同；按原像素和最终毫米尺寸独立重算 PPI，全部与记录一致，范围 73.6879–146.8176。该数值范围只覆盖这 134 个映射窗口，未推广到未列入 crop_map 的结尾额外图片。[复算记录](independent_review/native_width_resolution_audit.json)。全部按用户明确的 APPROVED_NATIVE_WIDTH 范围承接，无补造 180/200 PPI 或重截要求。 |
| 同步安全 | 独立阅读并运行同步测试 **37 passed**，覆盖动态成员、同数量错误成员、缺源/坏 hash、extra、目录/多处链接、越界、自引用、真实 CLI 只读性、替换中途失败及回滚。另在真实 release 执行 `--plan`、`--check`，两次 exit 0，全部受观察来源/分发/manifest 的字节、大小、类型与 mtime 保持。[测试日志](independent_review/sync_pytest.txt)、[真实只读检查](independent_review/actual_sync_readonly.json)。实际第二次写同步由主线程执行，其幂等输出及无变化记录见 [execution](source_sync_checks/execution.json)；本审查未写真实 release。 |
| 报告与打包保护回归 | 独立运行最终三个报告测试文件，**19 passed**，覆盖兼容路由、旧包不覆盖、两 PDF 批准 hash、源成员/规格/裁片保护、错误生成器回退阻断及科学入口 AST。先前 7 项中间运行是这 19 项的子集，不重复累计测试数量。[最终测试日志](independent_review/final_report_pytest.txt)。 |
| 科学/历史保护 | 以开始 Git 树独立重算受保护文件 blob，**6071 个既有文件无变化**，含科学配置/实现/数据/结果、Experiment 源与成品、历史 evidence、旧提交包、PreTask、公共 P2、Research Protocol 等。单独检查 assignment/identity/metadata 的精确差异：仅 Process 接管状态及描述更新；姓名、学号、日期与研究状态保持。当前 Goal 3 导航新增一段有日期的接管说明，旧审核正文完整保留。[状态差异](independent_review/allowed_process_status.diff.txt)、[导航追加](independent_review/current_navigation_append.diff.txt)。 |
| Experiment 范围承接 | 独立比较本轮实际 Experiment receipt 与旧 SYNC-003 receipt：25 张 PNG hash、逐页像素比较结果及文本摘要全部相同；批准 PDF/ZIP/章节源保持。旧 WSL 字体/渲染差异原样继承，没有新差异或新 Experiment 验收主张。[核验](independent_review/experiment_inheritance_verified.json)。 |
| 工程验证包 | 独立检查新 REVIEW_ONLY ZIP 的 CRC、116 成员、安全路径、字体/常见秘密模式及包内两份 PDF hash；两份均为批准字节。ZIP SHA256 `67421e39ca147d5ac09952c5f031f7ca0ab817518c6dac907d9abcede2e0c20c`。[独立包检查](independent_review/review_package_audit.json)。没有执行 FULL_RECOMPUTE 或 LIVE。 |

主要独立命令可在仓库根复用：

```bash
.venv/bin/python -m pytest -vv -p no:cacheprovider evidence/infrastructure/chatgpt-project-source-sync/test_sync_sources.py
.venv/bin/python -m pytest -vv -p no:cacheprovider task1/tests/test_accepted_report_integration.py task1/tests/test_closeout_identity.py task1/tests/test_process_report_build.py
.venv/bin/python evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/independent_review/audit_final_state.py
.venv/bin/python evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
```

`audit_build_and_release.py` 记录本次私密隔离构建目录中的实际对照；它的历史运行路径不属于生产运行依赖。初始输入审查脚本保护已经存在的 initial 记录，不能覆盖历史初始状态。独立上下文没有安装系统包、字体或语言依赖；本轮实施角色的局部依赖及失败修复见 [build_and_visual_checks](build_and_visual_checks.md)。

## 发现、修复与独立复验

1. **模板默认行为过时。** 初查发现旧圈框/填充/编号 API、较窄截图比例和旧版文档。初步修复后，本上下文实际查看模板 4–8 页，发现 6–8 页仍嵌入旧的烘焙高亮 PNG。已向主线程报告；模板执行者改为明确 `SYNTHETIC / NOT CHAT UI` 的原生 LaTeX 占位，旧 PNG 保留。最终独立以 200 dpi 复看 **3、5、6、7、8 页**，确认箭头端点、节点排版和续页；current source 与实际 `.fls` 已无旧 PNG 引用，三项退休宏不再存在。最终 12 页 preview SHA256 为 `b53d70a8945f10d5911a1f2ea43278172d1df9987f504a97d2b4b392c3688fc0`，旧 preview、三个旧 PNG 和公共配色均独立核对保持原字节。[最终模板复验](independent_review/template_final_independent_check.json)。
2. **实际字体环境差异。** 构建角色发现并修复 Noto Sans ExtraBold/CJK Bold 的选择问题，修复仅作用于报告子进程的 fontconfig。独立全文和渲染对照已验证最终结果。六个技术图页 **34、41、45、59、75、77** 仍有微小像素差，其余 **71 页逐像素完全一致**；独立测得每个不同通道最大为 **1/255**，每页 3312–5101 个像素不同。全部六页经原件对照目视无可见文字、几何或箭头回退。环境矢量嵌入/舍入是合理解释，未证明仅为元数据差异；不把新 PDF 冒称批准原件同 hash。必要原/新差异页已保存，批准 PDF 未修改。
3. **当前 README 混入旧轮次措辞。** 发现报告 README 的“没有安装字体/此次核验两图”可能被误读为本轮。主线程已明确限定 SYNC-003/Experiment 历史范围，另写本轮 Process 依赖；本上下文实际复读修改并更新被审文档 hash。历史 evidence 未改。
4. **保护审查的范围分类。** 最初全字节保护程序将当前 Goal 3 导航的新增接管段报为变化；独立查看精确 diff 后，确认其为允许的独立当前入口追加，原审核正文无改动。原检测保存在 [初次保护输出](independent_review/protection_before_scope_review.json)，最终程序同时检查原正文完整，不通过删除旧状态制造通过。

## 保留的事实与未覆盖范围

用户对本次完整 Process 文稿的验收绑定批准 PDF/ZIP；截图的原生宽度与历史裁切继续按其批准范围保留。**p76 原截图末行局部截断也存在于批准原件**，独立原件对照和逐像素比较均确认没有新增裁切。此项是承接范围说明，不是本轮新增故障，也未因此修改文稿、补造 PPI 或索要重复素材。

归档扫描覆盖 Process、嵌套 PreTask、根 Experiment ZIP、两份原未跟踪 HANDOFF ZIP 和新工程包；没有找到所用模式的真实凭据、字体二进制或不安全成员。HANDOFF ZIP 含实质历史交接内容，应保留历史身份。模式扫描与本次实际查看范围不等于对所有截图文字作完整隐私认证。

本次原件、manifest、release 与用户报告已更新的 UI 输入无文件内容差异，可记录 **USER_REPORTED_UPDATED / 无需重复上传这些文件**；本上下文没有操作 ChatGPT UI。逐条 Evidence Lock、Understanding 与教师提交未升级；没有新增研究、模型调用或轨迹生产。上述限定范围内没有未解决的本地工程阻碍。**实际远程发布核验由主线程继续完成；网页 GPT 工程二审 PENDING，教师提交 NOT_READY / 未发送。**
