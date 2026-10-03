# 实验一：轨迹数据预处理与 AI 辅助研究过程

吴博闻 · 10245102410

建议先阅读两份独立报告，再查看完成版 Notebook：

- `task1/reports/experiment1/experiment1.pdf`：25页实验报告，介绍方法、核验、比较、结果与局限。
- `task1/reports/process1/process1.pdf`：77页过程报告，记录真实工作流构建与实验决策；使用2026-10-03第76页局部修正版。
- `task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb`：基础步骤、三组参数、六种顺序、AI反例与全量生产复算。
- `task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb`：四模式、只读记忆与真实历史提议的离线复算。

两个 Notebook 提供完整复算代码，交付文件的执行计数为空、保存输出为0；此前真实FULL运行及其核验在GitHub工程记录中，本次保持Notebook原字节，没有因报告局部修改重跑实验。原始数据、冻结合同、只读记忆、保存的真实模型提议与必要代码均在本包。离线复算不需要登录或模型凭据。

## 文件核对与运行

在解压后的包根目录，使用 Python 3.12 和 `requirements.txt` 的依赖。可沿用兼容环境，或自行创建虚拟环境安装依赖。先核对文件：

```bash
python -m task1.goal3.package --verify-dir .
```

如需重新计算，从包根执行：

```bash
python -m task1.goal3 FULL_RECOMPUTE --output recompute_output
```

输出目录必须为新的目录。此入口从原始 JSON 重算9,720次历史参数/顺序记录处理、6,001次历史模式候选处理与384个既有record–episode选择，并处理全部11,386条原始记录的冻结生产策略；比较保存结果、逐记录指标和分片hash，再从重算结果生成图表。历史提议按实际保存内容重放，新增模型调用为0，记忆保持只读。记录键不代表独立用户或完整行程，source CRS仍为UNVERIFIED，结果采用固定数学工作坐标下的条件化分析。

也可在Jupyter中分别执行 Restart Kernel → Run All。两个Notebook的FULL路径默认开启，使用当前内核Python与项目相对路径。每次创建新的输出目录，耗时取决于CPU；可以设置 `SC_LAB1_RECOMPUTE_WORK` 指向新的输出目录，已有非空目录会被拒绝。不设置时使用临时目录。先运行完整入口再运行Notebook会重复计算相应任务。

`PACKAGE_MANIFEST.json`记录成员字节数、源hash、归档hash、纳入理由及明确变换。仅历史 `result_summary.json` 的一项机器专有命令路径在包内变为项目相对路径；科学结果、原始提议、冻结绑定与Notebook未改写。

完整报告LaTeX源、原生图源、历史审核及教师原材料保存在[GitHub工程](https://github.com/woobowen/Smart_Cities_and_Location_Services)。本包提供PDF阅读与离线科学复算所需内容；报告构建环境和账号凭据不随包分发。
