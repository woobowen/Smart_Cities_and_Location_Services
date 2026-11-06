# Project Sources 精简与录屏规范升级：独立最终核验

审查者：独立 Codex Agent `process_integration_verifier`。批准范围：`SC-PROJECT-REFRESH-20261106`。本记录承接 [初核](INITIAL_REVIEW.md)及原 Process 接管检查，不覆盖旧回执，不授予 GPT 外审、UI 完成、Evidence Lock 或教师提交通过。

**结论：当前受审范围内部核验通过，可以按现有授权完成普通 `main` commit/push。** 提交前须纳入本审核回执；后续若更改被审内容，须核对相应新增范围。远程发布及固定对象回读尚未由本独立审查执行，不能在本记录中宣称已经完成。

完整逐文件对象、命令结果和局限见 [FINAL_REFRESH_REVIEW.json](FINAL_REFRESH_REVIEW.json)；只读核验脚本为 [verify_final_refresh.py](verify_final_refresh.py)。

## 被审对象与实际方法

审查基准：`b7fd9ee522905c11ddcea760470e7a5f0c1be9f0`。最终读取 Git index 的 **126 个变更路径**：121 个现存 blob 和 5 个删除路径；核验期间 index 对象集合保持稳定，现存暂存字节与工作树一致。该快照的路径、Git blob、文件大小和 SHA256 集合身份为：

`a016d122838b0caf0d0b77bdc2a13d354b9d1f46e3fe66154ca90eda0ab65e62`

此快照包括新远程回读工具和父线程公开审计回执，尚不包含本次随后生成的审核 Markdown、JSON 和核验脚本自身，避免自引用身份。新增审核链接或回执不自动改变受审规范/PDF 身份；协调线程仍须在提交前对最终 index 追加最小核验。

快照之后，协调线程仅在新 `REVIEW_PACKET.md` 的“同步与内部验证”追加一段审核链接及范围说明。本独立审查已核对该工作树 diff 和 6 个新增链接，内容仅汇集真实 plan/check/index/公开边界/本独立审查/远程工具入口，并准确区分整包 whitespace=2 与源/文档=0；没有修改获批规范、报告或审查结论。追加后该文件 SHA256 为 `5be9ba3130f619f5331de9e59a23b0602c58cfeed69cdf46aec5e5fc02e8ba8b`，diff SHA256 为 `bed37b5163aa60208c5b5efe0f0fc0173f8c3ee3c75c09d96062a9d59deedb36`；此项仍待协调线程随本次 3 个审核文件一起暂存，再以私密 postcheck 确认最终 delta。

独立实际运行现有同步器 `--plan`、`--check` 与 `validate_sync.py --index`，均返回 0。`--check` 输出 `UPLOAD BUNDLE READY`、file_count=12；index 验证输出 PASS、declared_members=12、writes=false。37 项安全回归为父线程此前真实运行的范围，本审查读取该回执，没有冒称重新运行。

## 规范、成员与历史保护

- 当前结构化清单 **20 条登记 / 12 条 true / 8 条 false**；12 个规范名称、权威路径及语义角色与批准 target 精确相等。目标计划未被用作 active `sources.json` 的替代品。
- 12 项权威源、分发副本、工作树、Git index 和登记 SHA 全部一致，实际 release 文件名集合精确等于批准集合，没有 unknown extra。规范名采用 `Experiment2_Experiment_Report.pdf` 和 `Experiment2_Process_Report.pdf`，未保留第二个 Process active 记录。
- 四份权威规范在 index、工作树和批准 ZIP 中逐字节相同：Evidence v2.9、Visual v2.8、Writing v1.4、AGENTS 2026-11-06。独立重新计算基准→当前 unified diff，与暂存的 `governance.diff` 精确一致；没有发现误抄、截断或自行改造。
- 五份退出条目只改变 `project_source`；其余元数据保持。五个权威原件的 index/工作树及两份私密迁出副本均逐字节一致。Git 删除集合恰好是这五个 release 副本，没有删除权威教师材料或历史报告。
- 原三份 false 条目的完整元数据保持原值；其他未受本轮修改影响的成员行保持原值。publication-plots 原发行包未重打包。
- Research v1.3、P2、公共模板、实验一、实验二算法/测试/结果/公开汇总、图表、Notebook、Experiment 源、生成源及历史源包相对基准没有变化。Process 的 11 个任务 `.tex` 和 18 个 PNG 保持此前核验的字节。

两份实验二正式 PDF 的实际页数与 index SHA 为：

| 成品 | 页数 | SHA256 |
|---|---|---|
| Experiment | 26 | `7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101` |
| Process | 16 | `c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f` |

本轮没有重新编译、运行算法、训练模型或重做截图。相同 PDF/源码继承先前真实核验：Process 编译和全文通过，但严格 200 dpi 比较仍有 **13 页像素不完全相同，完整验证命令非零**。当前 README、构建说明及新审查包准确保留该限制；没有把历史 26+8 页源包误称为当前 26+16 页配对。

## 公开边界发现与修复

独立审查发现，未提交的原 `integration.json` 含 17 个选中视频裁片的详细原帧哈希、来源时码和裁切坐标，超出新协议规定的公开边界。协调线程随后保存完整私密原字节，并将公开文件明确标为摘要；本独立审查实际读取私密备份及暂存摘要，确认：

- 私密原记录 SHA256 为 `3465d41e33a7879c00aaedf76b8de7cb921770ce8088656e8c0175940bb10db1`。
- 公开摘要 SHA256 为 `dd5d8e93c27320f5a5248bb6c661e0822e1c714e409a85eea8804a2754fc583e`。
- 公开内容相对原记录只剔除 17 组 `video_timecode`、`raw_frame_sha256`、`crop_bounds_xyxy`，共 51 个字段，并增加明确的摘要身份说明；其他检查字段和原结论保持。旧审计所登记的原记录 SHA 仍指向私密原件，没有被改造成新记录身份。

已在批准 PDF 可见的来源说明和时码按获批 PDF 原字节保留。本次没有修改 PDF、`.tex`、截图、原帧或旧独立审查结论。

进一步检查当前完整 index 与 1,497 条私密数据路径清单，交集为零。新暂存 PNG 集合恰好为原独立审查的 18 个正式引用素材，字节完全相同；其 PDF 内嵌像素对应和无额外 PNG metadata 的既有检查可按相同字节继承。对 16 个私密原帧及 1 个未选裁片的实际文件哈希进行内存比较，未在新增/修改 blob 中发现其原件字节或实际哈希引用。完整输入 ZIP、Settings TXT 全文、原视频、raw 帧和未选截图没有进入待发布集合。

高置信密钥签名及 credential 赋值候选均为零，因此没有需要凭猜测判定为真实凭证的候选。此结论属于本次新增/修改内容的静态检查，并非穷尽所有历史 Git 对象、外部账号或所有可能秘密。原视频本轮未收到，未声称独立回看视频母件。

## 导航、格式与远程工具

239 个本地 Markdown 链接解析通过。字节镜像中的相对链接按 manifest 指定的权威 `active_path` 上下文解析，没有改动已批准规范来迁就 release 相对目录。当前根 README、task2 README、Process 构建说明、审核索引、交付门槛、报告索引及同步 README 均指向新审查包；旧 16 项方案顶部明确标为历史中间记录，旧阻塞和成功回执没有冒充当前状态。

源码及文档的 whitespace 检查返回 0；整个 `git diff --cached --check` 返回 **2**。全部告警仅来自原字节的 `governance.diff`（原 Markdown hard break 与 unified-diff 上下文空格）及两份真实编译 transcript，三份均保留准确原字节。未将全局检查写成 PASS，也未为消除告警而修改规范或工具原输出。

远程回读工具 `verify_remote.py` 的被审 Git blob 为 `26b1ed3ba15dcc7a351e7cf081dbb453cbd3369d`。独立 AST/`--help` 检查通过，并实际静态审阅其逻辑：

- Git 调用限于 origin 查询、对象读取及远端 ref 查询，不执行 push、fetch、reset 或配置写入。
- 固定仓库和完整 commit SHA，使用固定提交的 GitHub HTTPS GET；Git 路径经 URL 编码，按长度、SHA256 和 Git blob 哈希匹配后才保存。
- 输出及回读根目录拒绝位于仓库内，仅向操作者控制的外部回读/回执目录写入，不改规范、报告、Git index 或远端内容。
- 覆盖 20 个登记权威源、12 个 release 文件以及该固定提交相对基准的全部新增/修改对象；失败生成 FAIL 并返回非零。

本审查只运行该工具的 `--help`，**没有执行发布后的真实网络回读**；本次不是针对恶意多租户输出路径的安全测试。协调线程应使用新建的受控外部目录运行它，绑定最终完整 local HEAD、remote SHA 和逐文件结果。

可发布结论只覆盖当前授权的文档集成、四规范升级、12 项安全同步及审查材料。发布并实际验证固定远端后才可交接为 `READY_FOR_GPT_EXTERNAL_REVIEW`；ChatGPT UI 仍为 `USER_UI_ACTION_REQUIRED`，GPT 外部二审、Evidence Lock、用户最终确认及教师提交均未由本内部检查代办或宣告通过。
