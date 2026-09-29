# 实验一：轨迹预处理与可核验的 AI 工作流

先看 [本次项目源同步入口](../evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md) 和 [实验一审核索引](evidence/goal3/REVIEW_PACKET.md)。历史实验收尾仍见 [原收尾回复](evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/FINAL_RESPONSE.md)。它们分别登记 Technical、Research、Reports、Package、Publication 状态。内部核验不替代网页 GPT 二重审核；提交状态不代表已发送邮件。

## 作业与报告

| 内容 | 入口 |
|---|---|
| 四板块复盘入口 | [REVIEW_GUIDE](docs/goal3/REVIEW_GUIDE.md)；用户理解审核尚未完成 |
| 完整要求与质量证据 | [MASTER_REQUIREMENTS_REVIEW](evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md) |
| 教师要求逐项定位 | [Notebook 单元与报告页码导航](evidence/goal3/teacher_delivery_mapping.md) |
| 教师基础任务完成版 | [作业1轨迹数据预处理_完成版.ipynb](notebooks/final/作业1轨迹数据预处理_完成版.ipynb) |
| 教师 LLM 系统任务完成版 | [任务3_LLM辅助评估清洗_完成版.ipynb](notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb) |
| Experiment Report | [PDF](reports/experiment1/experiment1.pdf) · [当前章节源](reports/experiment1/Experiment_Report.tex)（用户已验收25页） |
| Process Report | [PDF](reports/process1/process1.pdf) · [XeLaTeX 源](reports/process1/process1.tex) |
| 技术交接 | [Technical Handoff](docs/goal3/TECHNICAL_HANDOFF.md) |
| 互动候选索引 | [Interaction Handoff](docs/goal3/INTERACTION_HANDOFF.md)；不代替 Evidence Master 选取或 LOCK |
| 答辩说明 | [技术说明](docs/goal3/DEFENSE_NOTES.md) |
| 当前结果 | [机器摘要](evidence/goal3/result_summary.json) · [有效运行索引](evidence/goal3/current_runs.json) |
| 当前报告图与可编辑源 | [报告图源](reports/experiment1/figures/) · [绘图程序](reports/experiment1/source/)；[历史G3图](figures/goal3/)保留原身份 |

教师 PPT 和两份 starter 保持原件。历史 G2 数字、G3 开发/选择、一次最终确认、全部记录生产各保留实验身份。原始输入包含 11,386 条记录、1,173,410 点；记录键不能视为独立用户或完整行程。

## 默认离线复算

在仓库根目录运行，复用现有 Python 环境；所需版本见 [requirements-recompute.txt](goal3/requirements-recompute.txt)。完整复算实际从原始 JSON 执行处理与评价，并对照保存的真实历史提议与产物哈希。输出目录必须是新目录，避免覆盖已验收结果。

```bash
.venv/bin/python -m task1.goal3 FULL_RECOMPUTE --output /tmp/sc-lab1-full-recompute
```

该命令依次重算历史参数/顺序 9,720 个记录—候选配对、历史记忆/四模式 6,001 个候选处理及 384 个 record-episodes 的选择，再重算全部原始记录的冻结部署策略与 R0。两份完成版 Notebook 提供同样的基础步骤和可读答案，可新内核顺序运行；默认关闭 LIVE。原先有模型调用的历史 episode 在这里重放已保存的真实提议，不产生新模型建议。

`FULL_RECOMPUTE` 实际拦截两种 Provider 的新增调用并检查只读记忆哈希。没有输出的记录和不能计算的指标仍保留，`null` 不替换成零分。复算成功回执不表示噪声识别准确率已获证明。

## 报告构建与新 LIVE

```bash
.venv/bin/python -m task1.goal3 REPORT_BUILD --output /tmp/REVIEW_ONLY_实验一_重建.zip
```

此入口真实编译用户已验收的Experiment章节源，核对25页/身份/全文与200dpi页面，并将批准PDF原字节放入新REVIEW_ONLY包。Process保持12页技术事实送审稿；不会重生成数值摘要、历史图、Process或执行数值实验。包构建的隔离依赖probe验证冻结输入，输出ZIP须不存在；建议显式使用新具名路径。编译所需隔离依赖、路径与真实构建产物见 [报告工程README](reports/README.md)。

本次当前包为 [REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip](submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip)。数值实现、输入及Notebook按具体成员SHA继承旧实际FULL证据；报告命令入口变更另做隔离回归，不称本轮又执行FULL。历史旧ZIP保留。

LIVE 是另一次真实模型实验，仅在完整 Git 工程和原有合法认证下显式开启：

```bash
.venv/bin/python -m task1.goal3 LIVE --enable-live --run-id my-new-development-episode
```

它调用既有 G2 开发分区四模式入口，生成新 run，不替换已验收的 G2/G3 索引，不再打开最终确认集挑参数。真实新调用可能有成本和随机差异；费用及底层隐藏请求无法观察时保持 unknown。此命令不属于默认离线复算，也不在本轮为增加调用量而执行。

## 指标与边界

S 完成时间/距离切分和短段过滤；D 按已批准规则一次标记、同时删除并保留不可计算窗口；P 是有限线段距离的 Douglas–Peucker 简化。每阶段重算相邻特征。R0、候选与最终参数、固定原始窗口、5 工作米 P 预算和自动保护规则见 [G3 合同](config/goal3/contract.json)。

共同 raw 覆盖按原始点身份计数，与最终显式存储点数不同。比较同时检查参考已覆盖集合上的最大几何误差、已有非空记录/窗口和原始断点。没有真值，不把覆盖增加、更少删除或更小自身 DP 误差称作真实清洗质量提升。源 datum 仍是 `UNVERIFIED`；公式交叉核对不能证明绝对地理定位准确。

## 历史证据与提交边界

- [G1](evidence/goal1/REVIEW_PACKET.md)：处理合同、条件化坐标、D2 授权与真实修复。
- [G2](evidence/goal2/REVIEW_PACKET.md)：三组参数、六种顺序、四模式、记忆及可复验反例。
- [G3](evidence/goal3/REVIEW_PACKET.md)：有限候选、组合/移除、选择、确认、全量生产、复现与交付。

教师要求 `.ipynb` 与实验报告压缩为 ZIP，10 月 5 日前发送至教师材料指定邮箱；材料未规定具体截止时刻。本轮只准备待审包，未发送或提交。身份已核实为吴博闻 / 10245102410；互动证据规格或最终审核未闭合时，包保持 `REVIEW_ONLY` / `NOT_READY`。报告 LaTeX、全部真实结果、失败日志及技术图源继续在 GitHub 保存。
