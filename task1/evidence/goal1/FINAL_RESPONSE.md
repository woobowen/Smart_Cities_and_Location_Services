# A. 本轮结论

Task ID：SC-LAB1-G1-FOUNDATION-001。Engineering status：**PARTIAL_BLOCKED**，不是完整Goal1完成。已提交工程基础、真实诊断和失败证据；完整真实三步链及三角色反馈仍有核心缺项。GPT second review：**PENDING**。没有执行Goal2/3。

本轮可以确认：原始材料保护、全量结构盘点、语义/方法/评价门控、平面几何与独立评价、控制器修复、7例真实诊断、离线可复算Notebook和必要图。不能确认：未知CRS下的米制清洗、未明确调度的方向去噪、完整A/B/C真实闭环或质量提升。预算内部重试问题保留FAIL，未靠改run_id继续。

实验一 Deliverable=IMPLEMENTING；Understanding由用户实际理解决定；Submission=NOT_READY。

# B. 实际材料与要求核查

完整来源在 [REQUIREMENTS.md](REQUIREMENTS.md)、[reading_coverage.json](materials/reading_coverage.json)、[governance_reading.json](materials/governance_reading.json)。读取主PPT43页文字/备注/技术图、DP GIF全部16帧、其他4份PPT、两份原Notebook全部source/execution_count/outputs及69个starter方法文本、README/使用说明/DECISIONS/ABLATION_REPORT/demo/examples。两份P2模板PDF全文与页面视觉参考已读，不当本轮结果。

主输入路径仍为 `task1/实验课1.pptx`、`task1/作业.zip`、`task1/作业/作业/作业1轨迹数据预处理.ipynb`、`任务3_LLM辅助评估清洗.ipynb` 及相邻raw/utils/douglas_peucker/traj_agent/tests。ZIP已有104个解压文件字节完全一致，另外4个辅助成员未解压，0个已有文件不一致。两份traj_dict.json逐字节相同。原始117个清单文件结束时hash均未变。

`Task1_Literature_Review_2025_2026_Merged.md`、`Task1_Source_Audit_2025_2026_Merged.json`、`Task1_Stage01_Readonly_Audit.md`未找到，未声称已读或自造替代原文。没有广泛论文检索。

教师任务和用户要求已映射R01–R16；阅读不等于任务完成。教师提交要求：10月5日前发送至52285903012@stu.ecnu.edu.cn，命名“学号_姓名_实验一”，具体时刻未说明。按本轮2026-09-26与PPT日期，该节点尚未过；本轮没有发送邮件。四人分组、开题及最终答辩的课程设计适用范围单独记录，未加作实验一额外交付。GPT＋Codex是用户选择，不称教师单独批准。

# C. 实际实现

教师starter保持原样；新增 `task1/workflow/` 为工作版共同实现。复用索引栈式DP思路，补齐有限线段距离、退化/重复/闭合/回头索引处理；分段边界与短段过滤分开；新邻接重算时间差、距离、速度与方向，字段命名避免旧注释交换。独立评价器按保留索引区间直接核验误差，避免旧“全轨迹最近段”和自报误差。未沿用默认平滑、改时间、折叠重复或旧综合目标函数。

方向去噪只落实PPT明确的双侧循环角差候选谓词；删除调度会改变结果，故正式删除函数阻断。两个构造反例、代码位置和影响见 [合同](../../docs/goal1/CONTRACTS.md)及[材料发现](materials/findings.md)。CRS/距离口径也未确认；只允许不依赖它们的结构/相对时间诊断。

A/B/C职责、独立输入/输出/工具/自主边界/交接/核验/升级等11项已配置，见 [ARCHITECTURE](../../docs/goal1/ARCHITECTURE.md)。实际A调用返回计划并执行source_evidence；B独立调用失败；C没有调用。控制器负责固定Goal/参数白名单、schema/path/hash、预算、工具执行、状态及恢复。模型没有任意shell/代码执行权限；真实read-only sandbox写探针被拒绝。工程材料核查/代码审查子代理不补算runtime C。

独立审查发现并修复缓存、恢复伪成功、失败状态升级、未完成工具事件漏检、进程组超时/中断回收、诊断字段覆盖及模式标签等问题。旧缺陷和真实反例留存。新增0重试/关闭WebSocket配置尚未真实复验；因原运行超出内部重试护栏，最终LIVE在合同和持久ledger均冻结。

# D. 实际运行与结果

最终诊断/图/Notebook CODE_SHA：`ea3b20ad13c65ab01cf2c761db6b09c185855b53`。108项核心测试绑定`0b7914dfc65cfef39a96586713c8810d7c7fbfad`，之后workflow和tests字节未变。成功A所在run03绑定`d1444eb07035ef651a36a3e89269f004186581df`；其他失败run保留各自版本。版本关系见 [code_versions](validation/code_versions.json)。

关键命令与证据：

| 命令/动作 | 真实结果/日志 |
|---|---|
| git status/branch/remote/log/fetch/HEAD | [初始命令](environment/initial_commands.json)：初始main clean，local/origin b25efc1一致 |
| 原starter pytest | 289pass/3fail/1skip；3个相对cwd失败在starter目录单独复测3pass，未改原文件；[基线日志](tests/starter_baseline.txt) |
| `.venv/bin/python -m pytest task1/tests -q` | 108pass/0fail/0skip；[JUnit](tests/final_bound.xml)、[逐case与hash](tests/case_results.json) |
| `codex exec` 真实JSONL/schema路径 | 4次CLI派发、2完成turn、1接受请求、1工具；[逐call](runs/call_summary.json) |
| `build_goal1_figures.py` | 从原始JSON重算7例并生成图/动作；[命令回执](validation/figures_command.json) |
| `recompute_archived_run.py g1-live-20260926-03` | 按旧CODE实际重跑唯一source_evidence，hash一致；[结果](validation/replay_result.json) |
| 两Notebook各独立新内核Run All | 各6个code cell成功，new_model_calls=0；[运行记录](validation/notebooks.json) |
| pdftoppm -r 200 + view_image | 两图PDF与PNG实际视觉检查，中文/数值/状态清楚；[检查记录](figures/visual_inspection.json) |

全量只读：11,386条、1,173,410点；42,185零时间差、29,175同时间不同位置、575,278相邻重复位置、8,272个>30秒间隔；0负dt。没有全量清洗或模型调用。

固定开发ID：0/1/2/246/256/306/352；共783点、776边。时间诊断12分区，122零dt、62同时间不同位置、323相邻重复位置、5个>30秒边界；0删除、0改值。完整空间分段、过滤、去噪和简化未执行：阶段数量为null、783点not_processed，saving和米制误差不可用。配置65/5/30/400/35/5仅STARTER_REFERENCE；PPT95m另列教学示例。

真实模型运行：run01旧CLI0.147.0被服务拒绝；隔离安装0.157.1后run02因本工程解析器误判禁用code host提示而失败；修复后run03 A成功，B因workspace routing discovery failed失败。B事件含9次可见重连通知和1次transport fallback；底层请求总数unavailable。没有C反馈，也没有反馈后的A动作，不以初始交接事件名称替代证据。

分类严格区分：CURRENT_RUN_REAL_DATA为实际原始诊断；CONSTRUCTED_FIXTURE/MOCK_TEST为工程挑战；REPLAY为旧CODE来源核查和当前数值复算；HISTORICAL为教师Notebook保存输出/demo/旧报告。工程正确不代表恢复真值或质量最优。

# E. 逐项验收

[acceptance.json](acceptance.json)和[REVIEW_PACKET](REVIEW_PACKET.md)保存同组ID的代码、真实动作、预期、实际、证据与影响范围。

| ID | 状态 | 要求 | 证据 |
|---|---|---|---|
| G1-A01 | PASS | 正确仓库、分支、工作区与用户工作保护 | [依据](environment/initial_commands.json) |
| G1-A02 | PASS | 完整材料读取与任务对应 | [依据](materials/reading_coverage.json) |
| G1-A03 | PASS | 原始数据与历史结果区分 | [依据](inventory/raw_integrity.json) |
| G1-A04 | PASS | 时空语义与计算权限 | [依据](../../config/goal1.json) |
| G1-A05 | BLOCKED | 分段和过滤正确且可追踪 | [依据](tests/case_results.json) |
| G1-A06 | BLOCKED | 忠于明确教师去噪方法且不混字段 | [依据](materials/direction_ambiguity_fixtures.json) |
| G1-A07 | PASS | DP及索引映射正确 | [依据](tests/case_results.json) |
| G1-A08 | PASS | 独立评价器可测对 | [依据](tests/case_results.json) |
| G1-A09 | BLOCKED | 三个角色实际独立调用与职责 | [依据](runs/call_summary.json) |
| G1-A10 | PASS | 运行控制与权限生效 | [依据](tests/case_results.json) |
| G1-A11 | BLOCKED | 小规模真实完整基线处理 | [依据](../../config/pilot.json) |
| G1-A12 | BLOCKED | 审核反馈进入真实后续动作 | [依据](runs/g1-live-20260926-03/checkpoint.json) |
| G1-A13 | FAIL | 拒绝、回退、恢复和预算受控 | [依据](tests/INDEPENDENT_CONTROL_REVIEW.md) |
| G1-A14 | PASS | LIVE/REPLAY/MOCK严格区分 | [依据](tests/case_results.json) |
| G1-A15 | PASS | Notebook及工具可复算 | [依据](validation/notebooks.json) |
| G1-A16 | PASS | 必要图表可重建且忠于数据 | [依据](../../figures/goal1/figure_manifest.json) |
| G1-A17 | PASS | Goal范围未越界 | [依据](../../config/goal1.json) |
| G1-A18 | NOT_RUN | 完整安全的GitHub审核包同步 | [依据](publication.json) |

核心A05/A06/A09/A11/A12仍BLOCKED；A13保留真实预算护栏FAIL。其他PASS不能抵消。GPT独立远程二重验收仍PENDING。

# F. 产物导航

- [REVIEW_PACKET](REVIEW_PACKET.md)、[acceptance.json](acceptance.json)、[requirements](REQUIREMENTS.md)、[合同](../../docs/goal1/CONTRACTS.md)、[未决项/下一阶段草案](LIMITATIONS_AND_NEXT_REVIEW.md)。
- `task1/workflow/`、`task1/tests/`、`task1/config/`、`task1/scripts/`：实际工作实现、独立反例及生成/复算入口。
- [基础工作Notebook](../../notebooks/01_baseline_and_audit.ipynb)、[真实调用记录/复算Notebook](../../notebooks/02_agent_loop_recompute.ipynb)。
- [逐记录CSV](../../results/goal1/pilot_summary.csv)、[逐点动作](../../results/goal1/point_actions.jsonl)、[完整诊断](../../results/goal1/pilot_diagnostics.json)、[运行回执](runs/README.md)。
- [诊断PDF](../../figures/goal1/pilot_diagnostics.pdf)、[诊断SVG](../../figures/goal1/pilot_diagnostics.svg)、[结构draw.io](../../figures/goal1/goal1_loop.drawio)、[结构SVG](../../figures/goal1/goal1_loop.svg)、[结构PDF](../../figures/goal1/goal1_loop.pdf)。

新增文件均为本任务目录；没有删除有效材料，没有改公共模板、长期治理、ChatGPT UI或11-file上传集合。Experiment Report/Process Report只保留阶段素材；未制作正式报告或虚假聊天证据/Evidence Lock。没有最终教师ZIP。

# G. 待GPT/用户审核事项

1. U01：教师材料未绑定实际JSON CRS，且两套旧距离实现不同。建议先取得可靠来源说明，再确认距离口径；影响所有真实米制处理。若最终只能用假设，需要显式批准，当前不确定性未解除。
2. U02：教师方向谓词明确，但同时/在线/迭代删除、末端/零位移策略未定。两个最小反例证明删除结果不同。请审核教学意图与单一明确调度，不把工程自主选择当教师方法。
3. U03/U04：确认工作区路由可用及严格预算后，再复验修复版provider和A/B/C闭环。建议后续最多5个串行角色调用、禁止自动重提、最多8工具请求；这是待批草案，当前LIVE仍锁住，不开启其他计费路径。
4. U05及Goal2：先补齐Goal1，再冻结单项参数范围、共同主要收益门槛/保护项、开发/最终划分及实验预算。当前没有标签，不应造准确率。候选范围与理由在LIMITATIONS文档，未执行。当前论文候选数0；没有为了凑论文额外实现算法，组合留Goal3。

普通工程缺陷已自主修复并测试；上述事项属于来源事实、研究定义或真实服务/预算条件，不能由Codex补成默认同意。

# H. Git发布与环境

Repository：`https://github.com/woobowen/Smart_Cities_and_Location_Services.git`，Branch：`main`。

CODE_SHA：`ea3b20ad13c65ab01cf2c761db6b09c185855b53`。代码里程碑真实push并核对remote一致。审核包的artifact发布状态见[publication.json](publication.json)；最终会话回复在最后push后提供ARTIFACT_SHA/Remote SHA和固定提交链接。自身文件不预写尚未生成的自身提交SHA。初始无用户未提交工作，未stash/reset/force push或创建分支。

本次新增环境：项目`.venv`中的pytest/nbformat/nbclient/ipykernel及依赖；临时目录`/tmp/sc-g1-codex-0.157.1`中的CLI0.157.1。无apt系统包、无新字体、无全局CLI/账户配置改动、无额外付费API。[完整安装日志/包清单](environment/README.md)。当前保留以便复算；用户可决定是否在验收后清理。

# I. 下一步边界

本轮阶段出口停止，等待GPT读取真实远程工程作二重验收。不能把PARTIAL_BLOCKED解释为Goal1完整通过，不自行开始Goal2/3、参数大扫描、融合、全量最终实验或报告定稿。
