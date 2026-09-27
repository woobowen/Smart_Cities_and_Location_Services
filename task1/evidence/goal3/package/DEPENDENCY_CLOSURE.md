# 教师包依赖闭包与构建边界

构建入口：`python -m task1.goal3.package --build task1/submission/REVIEW_ONLY_实验一.zip`。构建前以 `--check --probe` 实际核验现存依赖；缺最终冻结、正式图或报告时不会造占位内容。目标 ZIP 已存在时拒绝覆盖，由主线程保留旧包并明确更新。

`source_closure.json` 是每次实际执行的完整文件清单、源/归档双 SHA256、必需文件缺项与安全检查。`package_build_receipt.json` 仅在实际 ZIP 完成且逐成员 CRC/字节 hash 检查后产生。包中的 `PACKAGE_MANIFEST.json` 记录相同字节闭包，不声称包含自身尚未计算的 hash。正式 ZIP 的解压 FULL 复算由主线程独立执行，本构建器的静态通过不能替代该检查。

闭包由以下实际读取关系构成：

- 两份完成版 Notebook 的 raw、图、历史汇总、反例、真实 AI 建议及冻结只读 memory。
- `g2_journal.source_snapshot()` 枚举全部 `workflow/*.py` 与 `scripts/goal2.py`，因此这些源码全部保持原字节。
- `recompute_historical()` 读取精简 registry、其 binding 文件、真实 raw 与 registry 的源码/合同绑定。registry 内保留真实 `original_proposals`、`original_rounds`、记录目标 hash 与源 run/episode hash。旧 run manifests 和大 trace 只作来源链接，并不被离线计算读取，不重复纳入。
- `runtime.definitions()` 的 A plan `evidence_sha256`、`execution_gate()` 的 `contract_freeze.bindings`、各最终冻结的 `bindings`，以及 `production_freeze.processing_source_hashes` 均逐文件闭包并核对 hash。生产 CODE_SHA 取实际 production freeze，不写死历史 SHA。
- `recompute_production()` 读取当前 production manifest，从 raw 生成新的完整 trace 分片，再比较分片 hash、逐记录指标和配对汇总。原生产分片不作为计算输入。
- `offline_plots.py` 从重算循环中新产生的汇总/选择读数，以及新生产 trace 的点账本，生成新的 SVG/PDF/300 dpi PNG、画图数据与 hash。它不读取随包旧汇总或旧图作画图输入；Notebook 直接展示 WORK 中的新图，原图标为历史解释材料。
- `coordinates.registration()` 核对既有条件化坐标合同、USER_DECISIONS 与原授权补充；包内原样保留这些绑定。

唯一预先限定的内容变换是未绑定历史 `result_summary.json` 的顶层 `actual_command[0]`，从旧工作区个人绝对路径改为 `task1/scripts/build_goal2_analysis.py`。包内派生文件新增透明来源说明，清单记录原文件 SHA、变换字段和归档 SHA；原文件不改，全部其他字段与数学结果/模型提议不改。发现其他必要文件含个人绝对路径、潜在密钥或冻结 hash 失配时直接报错，不能擅自归一化绑定内容。

安全检查采用路径 allowlist/绑定闭包，拒绝路径穿越、符号链接、虚拟环境、账号目录、字体二进制、额外 ZIP，并扫描文本及 gzip JSON 的个人绝对路径和高置信密钥格式。PDF 文本由本机构建环境已有 `pdftotext` 提取后扫描；PNG 是正式图的原字节。没有安装依赖，没有复制字体或论文全文。接收者 PDF 阅读与离线运行不需要 TeX 或 `pdftotext`。

`--probe` 将计划成员复制到临时无 `.git` 目录，用当前 Python 的 `-I -B` 模式导入并核验授权、A plan、历史源码快照；生产冻结存在后还会实际检查完整生产 gate 与冻结字节代码身份。它不运行轨迹候选、不读取最终评分来选参数、不调用模型。临时目录退出后删除。专项测试的 ZIP 都是临时的 `ENGINEERING_FIXTURE`，不是教师交付包。

当前状态及缺项以 `source_closure.json` 的最近一次真实命令为准。Process Evidence 与身份缺失使教师包保持 REVIEW_ONLY / NOT_SUBMITTED；报告、Notebook 和技术工程仍继续完成。GitHub 完整工程保留全部有效历史证据，不因精简包而删除。
