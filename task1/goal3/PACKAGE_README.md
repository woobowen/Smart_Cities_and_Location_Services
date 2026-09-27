# 实验一待审提交包

本包身份为 **吴博闻 / 10245102410**，状态为 **REVIEW_ONLY / NOT_READY**。姓名和学号来自本次用户直接提供；Process Report 的真实互动原图与 Evidence Master 呈现规格及 LOCK 仍待补齐，用户深入审核与新网页 GPT 二审也尚未完成。不得直接改名后提交。Experiment Report 与 Process Report 的当前完整性以各自正文状态说明为准。教师要求命名为“学号_姓名_实验一”，课件第 26 页规定 10 月 5 日前发送至 52285903012@stu.ecnu.edu.cn；材料没有给出具体截止时刻。本工程没有发送邮件或上传教学平台。待最终批准后的教师候选名为 `10245102410_吴博闻_实验一.zip`；本包保持 `REVIEW_ONLY_10245102410_吴博闻_实验一.zip`。报告日期为修订日期，实验日期仍按原始 run 记录。

包中的两份 Notebook 对应教师的两个 starter，PDF 可直接阅读。运行默认是从原始 JSON 与冻结规则实际重新计算，不是加载汇总表来冒充复算；历史提议按已保存内容重放，不产生新的 LIVE 模型调用。原始数据与必要模型提议在包内，不需要账号或模型凭据。

在解压目录中使用 Python 3.12 与 `requirements.txt` 所列依赖。依赖版本来自实际工程环境。可以使用已有兼容环境，也可自行创建隔离环境安装；构建器不会安装或修改系统。先核验包内文件：

```bash
python -m task1.goal3.package --verify-dir .
```

从包根目录执行完整离线复算，输出目录必须是新目录：

```bash
python -m task1.goal3 FULL_RECOMPUTE --output recompute_output
```

此入口重算 9,720 次历史参数/顺序记录处理、6,001 次历史模式候选处理及 384 个既有 record–episode 选择，并重新处理全部 11,386 条原始记录的冻结生产策略。程序从 raw 计算，比较保存的真实结果 hash、逐记录指标与分片 hash，再从本次新结果生成参数、顺序、模式、全量点去向及同案例轨迹图（SVG/PDF/300 dpi PNG），保存新画图数据和 hash。原生产大 trace 没有重复装入包；其 manifest 是对比目标，新 trace 由复算生成。受测方法的新增模型调用必须为 0，记忆保持只读。记录键不等于独立用户或完整行程，原始 source CRS 仍为 UNVERIFIED。

也可在 Jupyter 中分别 Restart Kernel → Run All：

- `task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb`：教师基础步骤、三组参数、六种顺序、AI 反例与全量生产复算。
- `task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb`：实际工作流、四模式、只读记忆、真实历史提议与模式候选复算。

两份 Notebook 的 FULL 路径默认为开启。它们使用项目相对路径和当前内核 Python；无需原工作区 `.venv`。每次运行创建新的输出目录，耗时取决于 CPU。可设环境变量 `SC_LAB1_RECOMPUTE_WORK` 指定当前工程/解压目录外的新目录；已有非空目录会被拒绝，不设则创建临时目录。Notebook 展示本次新画图，随包旧图另标历史解释材料。单独运行总入口后再运行 Notebook 会再次执行所需计算，这是明确的重复复算，不是新的独立实验。

`PACKAGE_MANIFEST.json` 保存逐文件字节数、源文件 SHA256、归档字节 SHA256、纳入理由和明确变换。历史 `result_summary.json` 中一项命令可执行路径仅在包内改为项目相对路径，并附原 hash 与精确说明；数学结果、原始提议、任何冻结绑定文件均未改写。

本包仅用于离线执行与 PDF 阅读。`REPORT_BUILD` 所需 LaTeX 源、图源、完整历史证据和 TeX 构建环境保留在 [完整 GitHub 工程](https://github.com/woobowen/Smart_Cities_and_Location_Services)。`LIVE` 也仅在完整 Git checkout 与既有授权认证中显式使用：必须提供 `--enable-live` 与新 run ID，可能有成本和随机差异；包内默认不调用 LIVE，不提供账号凭据，不静默替换模式。

未纳入：`.git`、虚拟环境、缓存、字体文件、论文全文、无关 ZIP、旧大 trace 和原生产分片。原教师材料、starter、完整结果仍在 GitHub；它们没有因精简提交包而被删除。包构建核验与隔离目录 FULL 执行属于不同检查，前者成功不等于后者已经完成，实际验收见仓库的 Goal 3 REVIEW_PACKET。
