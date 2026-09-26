# SC-LAB1-G1-REPAIR-001 完整工程回复

**A. 工程总状态**

PARTIAL_BLOCKED。本轮修复了完整profile校验、异常结束状态、来源/反馈引用及实时可见事件控制，接通有条件平面处理链，并完成三个角色的REAL_DIAGNOSTIC_LOOP。D1/D2未批准，真实完整baseline与Goal1总体仍未完成。Goal2/3未执行。修复前c2e3ffe的GPT审核为REVISE / NOT_PASS；本次新提交GPT_SECOND_REVIEW=PENDING。

原始教师材料、starter、数据、公共治理/模板及旧run01/02/03、旧预算冻结均保留；320项受保护文件逐字节一致。三份历史研究附件已按原文件名/hash导入task1/docs/research，来源见handoff_provenance.json。source_snapshot仅归档。

**B. R1-F01—F05**

| 项 | 旧问题 → 最小修复 | 实际验证与剩余限制 |
|---|---|---|
| F01 | dict预先清理错误行 → 全列表结构/字段/唯一性/数量/集合检查，合法后才重排；[diagnostics.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/diagnostics.py)、[tools.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/tools.py) | before重复/foreign VERIFIED；after两入口均REJECTED，缺失/字段错误拒绝，正常/重排通过。不授权子集 |
| F02 | 缺失时间、null item、启动/工具异常逃逸，timeout丢日志 → 可计算性分离，失败receipt/checkpoint/manifest，部分安全日志与进程组终止；[provider.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/provider.py)、[controller.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/controller.py) | 原反例、实际OS PermissionError和坏数据路径通过；超时/重试后父子进程无后续文件写入。写盘失败报告EVIDENCE_MISSING，不自动重发 |
| F03 | 固定BLOCKED入口 → 方法注册/合同核对与实际runner分离，分段→独立过滤→单次方向候选删除→DP→独立评价→点账本；[pipeline.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/pipeline.py) | 构造8点真实执行：过滤2、方向删除1、简化3、保留2，独立审核通过。真实合同与坐标适配器尚未获准注册；没有默认投影或伪造批准 |
| F04 | 非空引用/任意交集即可 → 精确来源页/片段+hash，当前run/父版本，审核call及其VERIFIED工具双引用；[sources.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/sources.py) | 未知ID、伪路径、旧审核、错版本和非审核反馈拒绝；真实C→A引用通过。contract_snapshot仅回显合同，source_check核读真实片段但不确认CRS |
| F05 | 参数看似0却未实证、结束后才看重试 → 固定CLI/native hash，版本源码核验，实时流首错停组，固定新批ledger；[budget.py](https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/880290a5dada84c711248844038daa3ee35eeefb/task1/workflow/budget.py) | 0.157.1内置openai用or_insert，三项同名覆盖无效，已移除；默认4/5重试与WebSocket true仍在。本批6次实际成功、可见重试0；底层请求unknown。异常停止路径本轮为离线实测，未遇LIVE故障来验证它 |

[修复对照](REPAIR_COMPARISON.md)、[完整源码差异](code_repair.diff)、[before/after](probe_comparison.json)、[探针适配说明](PROBE_ADAPTATION.md)。交接原探针未删改：其不存在executable路径被新增前置检查挡住；适配副本仅换为存在的sys.executable，保留原OSError/TimeoutExpired注入，未调用模型。初次开发5fail/103pass和后续155/156pass日志均保留。

C05文字提出时间分区核验，但recompute_check实际只验证profiles。本轮不扩大该工具结论：完整时间分区与重复明细由[audit_live.py](audit_live.py)独立离线核对通过，标为OFFLINE_AUDIT_OF_ACTUAL_LIVE_ARTIFACTS。三角色反馈、补诊断和profile再次复核确实发生；不把这一点等同完整清洗或真值验证。

**C. D1 / D2**

D1仍UNKNOWN：PPT第13页正文/备注为一般WGS84/GCJ02说明，没有绑定本JSON；新增历史研究材料未补足该绑定。距离/投影与适用误差未获批准。D2为GPT推荐，尚无用户真实方法确认；本轮只在平面构造样例实现一次标记同时删除、不可算保留、不迭代及删除后重算。[原文/文件hash](source_excerpts.json)、[未决记录](SEMANTICS.md)。

数据提供方问题（未代发）：这份traj_dict.json原始坐标是什么基准、是否加偏，是否有与文件对应的数据说明？取得依据后还需批准距离口径和真实方法合同。

**D. 实际命令、测试、Notebook与分类**

- `.venv/bin/python .../handoff/probes/reproduce_repository_findings.py --repo "$PWD" --output .../probes_before.json`：修复前真实复现；修复后原版与适配版分别保存。
- `.venv/bin/python task1/scripts/repair_goal1.py validate`：compileall通过；完整task1/tests **156 passed**；正确starter cwd的完整测试 **292 passed、1 skipped、252 warnings**。skip为原starter中文字体候选探测，相关glyph warnings保留，没有改starter或安装字体。[日志](validation.json)、[starter日志](starter_full.txt)。
- `repair_goal1.py diagnostics`：教师原始固定7条/783点真实离线诊断，独立profile/recompute通过；[逐记录结果](results/profile_pilot.json)、[783点去向](results/point_actions.jsonl)。
- `repair_goal1.py qualify` / `live`：先绑定已提交代码、最终离线测试与Prompt，再小探针、串行角色链；没有自动重提。
- `build_repair_figures.py`、`repair_goal1.py notebooks`：两Notebook各9code cell新内核实际运行，默认无模型调用；旧已发生source_evidence按其历史CODE做REPLAY。[Notebook记录](notebooks.json)。
- 两张图以P2和原生SVG/PDF/draw.io生成，PDF逐页200dpi渲染检查通过。[图源/导出](figures/manifest.json)、[视觉检查](figures/visual_inspection.json)。旧失败架构图不覆盖。

构造数学链/故障测试为CONSTRUCTED_FIXTURE或ENGINEERING_TEST；新6次模型为LIVE；原始7条诊断为CURRENT_RUN_REAL_DATA；旧run复算为REPLAY；研究附件与旧starter输出为HISTORICAL。没有全量正式处理、候选效果实验或额外付费API。

**E. 真实探针与角色执行**

| 指标 | 本批实际 / 上限 |
|---|---:|
| 外层预算预留 / 进程实际启动 | 6 / 6；6实际启动 |
| 连通性探针 / 角色调用 | 1 / 1；5 / 5 |
| 完成turn / 有效结构响应 | 6 / 6 |
| 工具请求 / 实际执行 | 5 / 12；5实际执行 |
| 可见JSONL重连 / fallback | 0 / 0 |
| stderr sampling retry | 0 |
| 不可观察底层请求数 | unknown |

六次调用有六个不同thread，耗时12.27、43.70、49.43、37.30、40.97、83.61秒，均低于180秒。探针成功后才进入A→B→C→A→C。真实动作是profile_pilot→duplicate_details→verify_profiles→time_boundaries→recompute_check；A04引用C03与其实际VERIFIED工具后定位5处长间隔，C05又引用这次A与工具结果。工具复算exact_match=true；[实际manifest](runs/g1-repair-roles-01/manifest.json)、[逐call/工具独立审计](live_audit.json)、[独立上下文](independent_contexts.json)。

历史外层4次、run03的9重连通知/1fallback/10sampling retry及旧FAIL完整保留，三个通知口径不相加成HTTP或账单请求数。新批模型预算已用完，不再派发。

**F. 完整真实baseline**

未执行：D1/D2未批准，生产合同/坐标适配器未登记；实际参数仍STARTER_REFERENCE，未将65/5/30/400/35/5当作已批准最优值。固定pilot为0、1、2、246、256、306、352，共783点、776边、12个时间诊断分区；122个零dt、62个同时间异位置事件、323个连续重复位置事件、5个>30秒间隔。保持0删除、0改值、783未处理；空间分段/过滤/去噪/DP真实阶段数量及米制指标为null并附原因，未填0或生成假前后图。[阻断输出](results/baseline.json)。

**G. 逐项验收**

PASS均限表述范围，不能抵消D1/D2阻断。GPT新提交二重审核为PENDING；工程自检不授予项目总体PASS。

| 项目 | 状态与范围 | 证据 |
|---|---|---|
| R1-A01 | PASS：审核基点/工作区、320项受保护文件及旧失败记录保留 | [workspace_check.json](workspace_check.json), [protected_integrity.json](protected_integrity.json) |
| R1-A02 | PASS：完整profile列表先校验；重复/多余/缺失/字段错误拒绝，合法重排通过 | [probe_comparison.json](probe_comparison.json), [tests_final.xml](tests_final.xml) |
| R1-A03 | PASS：可预期数据/事件/启动/超时/工具异常形成失败回执；永久写盘失败明确EVIDENCE_MISSING | [actual_failure_probes.json](actual_failure_probes.json), [probes_after_adapted.json](probes_after_adapted.json), [tests_final.xml](tests_final.xml) |
| R1-A04 | PASS：来源片段、文件hash、父版本、当前审核与数值回执绑定；验证范围按工具实际输出 | [source_excerpts.json](source_excerpts.json), [live_audit.json](live_audit.json), [tests_final.xml](tests_final.xml) |
| R1-A05 | PASS：构造平面完整链实际执行及独立核验；真实合同/适配器缺失仍BLOCKED | [constructed_pipeline.json](constructed_pipeline.json), [baseline.json](results/baseline.json) |
| R1-A06 | PASS：0.157.1版本/schema/官方源码及进程组停止测试；已识别并移除无效重试覆盖 | [provider_version_evidence.json](provider_version_evidence.json), [cli_schema_evidence.json](cli_schema_evidence.json), [tests_final.xml](tests_final.xml) |
| R1-A07 | PASS：1次真实小探针成功后才串行角色链；本批6派发、无可见重试；内部请求unknown | [live_qualification.json](live_qualification.json), [live_audit.json](live_audit.json), [manifest.json](runs/g1-repair-connectivity-01/manifest.json) |
| R1-A08 | PASS：三个角色5次真实调用，C→A反馈和时间补诊断发生；仅REAL_DIAGNOSTIC_LOOP | [manifest.json](runs/g1-repair-roles-01/manifest.json), [live_audit.json](live_audit.json) |
| R1-A09 | BLOCKED：D1 UNKNOWN/D2未获用户批准；未执行同pilot真实空间baseline | [SEMANTICS.md](SEMANTICS.md), [baseline.json](results/baseline.json) |
| R1-A10 | PASS：核心156pass；starter292pass/1字体skip；两Notebook各9cell新内核执行，无新模型 | [validation.json](validation.json), [starter_full.txt](starter_full.txt), [notebooks.json](notebooks.json), [visual_inspection.json](figures/visual_inspection.json) |
| R1-A11 | PASS：CODE_SHA绑定与输入/源码/结果hash；原始文件、旧run和旧ledger不变 | [live_audit.json](live_audit.json), [protected_integrity.json](protected_integrity.json), [file_manifest.json](file_manifest.json), [release_check.json](release_check.json) |
| R1-A12 | NOT_RUN：代码880290a已push；完整artifact正在提交，发布后核对 | [publication.json](publication.json) |

| 项目 | 状态与范围 | 证据 |
|---|---|---|
| G1-A01 | PASS：本轮初始main=审核基点，原材料/旧run保留 | [protected_integrity.json](protected_integrity.json) |
| G1-A02 | PASS：三研究附件原字节补齐；定点核读相关来源，非新实验 | [handoff_provenance.json](handoff_provenance.json) |
| G1-A03 | PASS：原始/构造/LIVE/历史/REPLAY区分 | [live_audit.json](live_audit.json) |
| G1-A04 | PASS：未知语义仍门控；无真实CRS或去噪方法批准 | [SEMANTICS.md](SEMANTICS.md) |
| G1-A05 | BLOCKED：构造链已跑；真实空间分段/长度过滤仍未批准 | [constructed_pipeline.json](constructed_pipeline.json) |
| G1-A06 | BLOCKED：单次同时删除候选已独立构造验证；真实采用未批准 | [SEMANTICS.md](SEMANTICS.md) |
| G1-A07 | PASS：原DP数学验证保持，构造完整链中的DP亦核验 | [tests_final.xml](tests_final.xml) |
| G1-A08 | PASS：二重审核重开后，完整profile列表和独立审核反例修复 | [probe_comparison.json](probe_comparison.json) |
| G1-A09 | PASS：五次独立上下文真实A/B/C调用；范围为诊断 | [live_audit.json](live_audit.json) |
| G1-A10 | PASS：重开后补错误结束状态/来源反馈绑定/保护测试；LIVE实际生效 | [actual_failure_probes.json](actual_failure_probes.json) |
| G1-A11 | BLOCKED：真实完整基线未执行；783点原样未处理 | [baseline.json](results/baseline.json) |
| G1-A12 | PASS：真实C03审核→A04时间边界→C05复算；非机械重复 | [live_audit.json](live_audit.json) |
| G1-A13 | PASS：本批外层预算与无重提运行已验证；停止异常路径为离线实测。旧run03 FAIL永久保留；不保证内部零重试 | [provider_version_evidence.json](provider_version_evidence.json) |
| G1-A14 | PASS：新LIVE/历史REPLAY/构造测试保持区分；没有Mock回填 | [live_audit.json](live_audit.json) |
| G1-A15 | PASS：两Notebook新内核各9codecell；旧source_evidence由历史CODE复算 | [notebooks.json](notebooks.json) |
| G1-A16 | PASS：当前原始诊断/实际调用状态图已生成与200dpi检查；无假前后图 | [visual_inspection.json](figures/visual_inspection.json) |
| G1-A17 | PASS：Goal2/3、论文筛选、扫描、融合、全量正式处理未执行 | [SEMANTICS.md](SEMANTICS.md) |
| G1-A18 | NOT_RUN：代码已push；完整修复artifact提交后核对 | [publication.json](publication.json) |

原G1-A08/A10已因本次审查重开并修复；A13保留旧FAIL历史，当前PASS仅涵盖本批外层预算、可见事件控制与已测试路径，不代表隐藏内部重试可计数或已禁用。机器表：[acceptance.json](acceptance.json)。

**H. Git与文件**

Repository：`https://github.com/woobowen/Smart_Cities_and_Location_Services.git`；Branch：`main`。
CODE_SHA：`880290a5dada84c711248844038daa3ee35eeefb`，上述最终测试、当前诊断、6次LIVE、Notebook与图绑定这个已存在提交；随后只提交artifact/文档。发布实际核对见[publication.json](publication.json)。当前已核对远程SHA：`880290a5dada84c711248844038daa3ee35eeefb`（代码阶段push后的实际ls-remote核对；完整artifact尚待发布）。最终artifact提交的自身SHA无法预写到其自身文件；以最终会话回复给出的ARTIFACT_SHA/Remote SHA和该固定提交为准，或读取承载本文件的Git commit。不得用上述代码或上一发布SHA冒充最终HEAD。

修改workflow、tests、config、任务文档、Notebook及生成入口；新增pipeline/sources/budget、历史研究原件、本次修复证据、当前结果/图/运行日志和固定新批ledger。未删除有效文件，未改公共协议/模板/上传集合/教师原件。逐文件增改/大小/hash见[file_manifest.json](file_manifest.json)，发布检查见[release_check.json](release_check.json)。原始失败日志、Git diff和Matplotlib SVG的空白按原字节保留，未为通过whitespace检查改写证据；初次检查结果也保留。Experiment Report/Process Report仅留阶段素材，未定稿，无伪造交互截图或Evidence Lock。

**I. 环境与待决定事项**

现有.venv保留；本次仅恢复临时@openai/codex@0.157.1及Linux x64平台包，无新增pip/apt/字体，无全局配置或认证迁移。安装初次继承TLS环境警告与随后启用证书校验的官方integrity/cache/安装字节核对均如实保留；模型子进程移除该覆盖。[环境/恢复说明](ENVIRONMENT.md)。环境先保留供复核；验收后如用户明确要求可清理。

待研究/用户决定仅限D1来源事实及距离合同、D2真实删除调度与方法合同、GPT对新远程成果的独立审核。普通工程故障已在本轮处理并留证。任务在此停止，不开始Goal2/3、参数扫描、策略融合或全量最终处理。
