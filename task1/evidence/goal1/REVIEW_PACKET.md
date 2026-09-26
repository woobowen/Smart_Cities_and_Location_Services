# SC-LAB1-G1-FOUNDATION-001 审核入口

**Engineering status：PARTIAL_BLOCKED。Goal1未完整完成。GPT_SECOND_REVIEW：PENDING。**

本轮取得材料核实、语义/评价合同、可信平面数学工具、独立审核与权限测试、7例真实诊断、两份可复算Notebook、必要P2图和真实调用失败证据。完整真实基线因CRS/距离及去噪调度阻断；三角色仅A完成来源核查，B网络失败，C和反馈回路未发生。原CLI内部重试预算护栏失败不被108项离线PASS抵消。新LIVE已冻结。

实验一 Deliverable=IMPLEMENTING，Understanding由用户确认，Submission=NOT_READY。未进入Goal2/3，没有完整参数/顺序/四模式效果实验、论文算法批量实现、组合、全量正式处理或最终报告。

## 1. 阅读顺序与完整入口

| 内容 | 稳定入口与用途 |
|---|---|
| 任务级批准记录 | [本轮完整原文](APPROVED_PROMPT.md)；用户已授权执行/commit/push，未改长期治理/11-file upload bundle |
| 完整要求映射 | [R01–R16](REQUIREMENTS.md) / [机器表](requirements.json)，含基础/附加/用户要求、精确来源、Goal与状态 |
| 原始材料/版本/读取 | [inventory](inventory/README.md)、[SHA清单](inventory/materials.json)、[教师材料读取](materials/README.md)、[coverage](materials/reading_coverage.json)、[治理/模板](materials/governance_reading.json)、[20项发现](materials/findings.md) |
| 环境与认证/权限 | [environment](environment/README.md)、[初始Git命令](environment/initial_commands.json)、[安装汇总](environment/install_summary.json)、[read-only sandbox实际探针](environment/sandbox_probe_01571.json) |
| 合同与未决 | [数据/方法/指标/权限/改进合同](../../docs/goal1/CONTRACTS.md)、[可校验配置](../../config/goal1.json)、[pilot事前清单](../../config/pilot.json)、[数学实现说明](../../docs/goal1/geometry_notes.md) |
| 角色/控制器 | [三个角色11项职责](../../docs/goal1/ARCHITECTURE.md)、[controller](../../workflow/controller.py)、[provider](../../workflow/provider.py)、[工具白名单](../../workflow/tools.py) |
| 实现与独立核验 | [geometry](../../workflow/geometry.py)、[evaluation](../../workflow/evaluation.py)、[diagnostics](../../workflow/diagnostics.py)；工作版只调用这一套，原starter未改 |
| 现状与修复测试 | [CHECK_MATRIX](tests/CHECK_MATRIX.md)、[108项逐case](tests/case_results.json)、[实际JUnit](tests/final_bound.xml)、[独立控制器审查/反例](tests/INDEPENDENT_CONTROL_REVIEW.md)、[测试源码](../../tests/) |
| 真实模型/工具/失败 | [runs说明](runs/README.md)、[逐call摘要](runs/call_summary.json)、[run03 manifest](runs/g1-live-20260926-03/manifest.json)、[全局预算冻结](runs/budget_live.json)；run01/02失败均保留 |
| 真实7例结果/全部点去向 | [pilot_diagnostics](../../results/goal1/pilot_diagnostics.json)、[逐记录CSV](../../results/goal1/pilot_summary.csv)、[783点动作JSONL](../../results/goal1/point_actions.jsonl) |
| Notebook | [基础/审核工作版](../../notebooks/01_baseline_and_audit.ipynb)、[部分LIVE记录/真实离线复算](../../notebooks/02_agent_loop_recompute.ipynb)、[新内核日志](validation/notebooks.json) |
| 图与可编辑源 | [诊断PDF](../../figures/goal1/pilot_diagnostics.pdf)、[SVG](../../figures/goal1/pilot_diagnostics.svg)、[结构PDF](../../figures/goal1/goal1_loop.pdf)、[draw.io](../../figures/goal1/goal1_loop.drawio)、[结构SVG](../../figures/goal1/goal1_loop.svg)、[生成脚本](../../scripts/build_goal1_figures.py)、[200dpi视觉检查](figures/visual_inspection.json) |
| 真实复算与版本关系 | [replay结果](validation/replay_result.json)、[原代码恢复复算脚本](../../scripts/recompute_archived_run.py)、[code_versions](validation/code_versions.json)、[117原文件不变](validation/original_integrity.json)、[实际run版本/事件核验](validation/run_artifact_audit.json)、[全部新增文件清单](validation/task_file_manifest.json) |
| 限制/升级/Goal2草案 | [LIMITATIONS_AND_NEXT_REVIEW](LIMITATIONS_AND_NEXT_REVIEW.md)；包含问题、证据、影响、候选解释、参数/门槛/划分/预算建议，均不触发执行 |
| 第一重验收与发布 | [acceptance.json](acceptance.json)、下表、[FINAL_RESPONSE](FINAL_RESPONSE.md)、[publication](publication.json)、[安全与链接检查](validation/release_check.json) |

## 2. 实际结果和解释边界

全量仅结构盘点：11,386记录、1,173,410点、1,162,024相邻边；全部原始数组对齐且有限，42,185零dt、29,175同时间不同位置、575,278相邻重复位置、8,272个dt>30秒，负dt为0。它不是全量清洗或物理质量结论。

模型反馈前保存的开发ID为0/1/2/246/256/306/352。7例共783点、776边，时间诊断12分区；0删除、0改值。完整空间切分/过滤/去噪/简化未运行，数量为null并记录783点未处理；saving/米制误差不可用，原因U01/U02。没有独立标签，因此不报告误删率/准确率/真值恢复。

4次CLI派发中2次有完成的模型turn，1次经控制器接受并真正调用source_evidence。run03 B有9条可见重连通知及1次transport fallback，底层请求数unavailable；原预算漏计内部请求。当前LIVE已冻结。初始A交接的FEEDBACK_HANDOFF事件名不能证明C→A闭环。

数学与控制测试是CONSTRUCTED_FIXTURE/MOCK_TEST工程证据，不是自然模型失败或真实清洗结果。未把旧Notebook outputs、demo_out、ABLATION_REPORT写作本轮结果。两份工作Notebook默认RECOMPUTE，均新内核6个code cell执行通过、新模型调用0；其数值工具重新读raw计算，与保存结果一致。旧LIVE只按其已提交CODE复算实际发生的一项来源核查，不补造未发生角色。

## 3. 第一重验收

PASS均限affected_scope；完整G1仍受核心BLOCKED/FAIL约束。机器表保留每项代码、真实动作、预期、实际、证据及影响范围，与下表同组ID。

| ID | 状态 | 要求 | 实际结果 | 核心证据 |
|---|---|---|---|---|
| G1-A01 | PASS | 正确仓库、分支、工作区与用户工作保护 | 初始clean main、b25efc1与origin相同；仅新增task1任务目录，117原文件未变 | [证据](environment/initial_commands.json) |
| G1-A02 | PASS | 完整材料读取与任务对应 | 5PPT/两Notebook/69文本方法source；主PPT43页及DP GIF逐帧；三研究文件缺失不补造 | [证据](materials/reading_coverage.json) |
| G1-A03 | PASS | 原始数据与历史结果区分 | 117清单文件全部未变；两数据相同；ZIP已有104文件全同，4辅助成员未解压 | [证据](inventory/raw_integrity.json) |
| G1-A04 | PASS | 时空语义与计算权限 | CRS=UNKNOWN；distance_policy=ASSUMPTION_REQUIRING_APPROVAL；Unix秒SOURCE_DECLARED；完整链BLOCKED；时间诊断可执行 | [证据](../../config/goal1.json) |
| G1-A05 | BLOCKED | 分段和过滤正确且可追踪 | 平面fixture已通过；真实7例783点形成12时间分区、0删改；真实空间切分与长度过滤未运行 | [证据](tests/case_results.json) |
| G1-A06 | BLOCKED | 忠于明确教师去噪方法且不混字段 | 双侧循环差谓词核实、命名字段/候选诊断已测；删除调度会改变结果，正式denoise抛MethodUnresolved | [证据](materials/direction_ambiguity_fixtures.json) |
| G1-A07 | PASS | DP及索引映射正确 | 已知答案与独立oracle通过；错误超差输出拒绝 | [证据](tests/case_results.json) |
| G1-A08 | PASS | 独立评价器可测对 | 108整体case中对应正反例均pass；计数审核遗漏被独立审查发现后修复；无假accuracy | [证据](tests/case_results.json) |
| G1-A09 | BLOCKED | 三个角色实际独立调用与职责 | A成功且source_evidence执行；B路由失败；C未调。2个完成model turn但仅1个被控制器接受 | [证据](runs/call_summary.json) |
| G1-A10 | PASS | 运行控制与权限生效 | sandbox拒写；修复后离线请求/缓存/恢复/事件/状态检查pass；LIVE已硬冻结 | [证据](tests/case_results.json) |
| G1-A11 | BLOCKED | 小规模真实完整基线处理 | 7例783点完成结构/时间诊断；完整链BLOCKED、stage count=null、not_processed=783；未用合成替代 | [证据](../../config/pilot.json) |
| G1-A12 | BLOCKED | 审核反馈进入真实后续动作 | 只有A初始计划→source_evidence→B输入交接，随后失败；没有C反馈或后续A行动 | [证据](runs/g1-live-20260926-03/checkpoint.json) |
| G1-A13 | FAIL | 拒绝、回退、恢复和预算受控 | 离线修复通过；真实CLI出现9重连通知+1fallback，底层请求数unavailable，原预算只记外层进程，未满足护栏；已冻结 | [证据](tests/INDEPENDENT_CONTROL_REVIEW.md) |
| G1-A14 | PASS | LIVE/REPLAY/MOCK严格区分 | 无Mock fallback；构造恢复仅pytest隔离目录；保存真实失败；默认Notebook new_model_calls=0 | [证据](tests/case_results.json) |
| G1-A15 | PASS | Notebook及工具可复算 | 两份各6 code cells通过；旧source_evidence按旧CODE重算一致；当前数值profile/audit/recompute一致 | [证据](validation/notebooks.json) |
| G1-A16 | PASS | 必要图表可重建且忠于数据 | 7例原始诊断图与实际/未完成角色结构图已生成、视觉检查；真实前后图明确BLOCKED | [证据](../../figures/goal1/figure_manifest.json) |
| G1-A17 | PASS | Goal范围未越界 | 只读全量结构盘点、7例诊断、数学工具、工程审核与部分live；Goal2/3均未执行 | [证据](../../config/goal1.json) |
| G1-A18 | PASS | 完整安全的GitHub审核包同步 | 完整审核包已实际推送9ccbf63，git ls-remote核对一致；TLS间歇错误保留，同origin重试push成功。秘密/大文件/链接/Notebook检查通过；原文和原生导出空白例外有记录。 | [证据](publication.json) |

## 4. 可复算命令与代码绑定

```bash
.venv/bin/python -m pytest task1/tests -q
.venv/bin/python task1/scripts/recompute_archived_run.py g1-live-20260926-03
.venv/bin/python task1/scripts/build_goal1_figures.py
```

Notebook在项目venv内新内核Run All。不要重建Notebook source覆盖已有执行输出；若确需重建，先运行build_goal1_notebooks.py再执行。不要开启LIVE：最终合同与ledger都已冻结。生成图会重建同名派生结果，复核时可在独立checkout中执行。

最终诊断/Notebook/图的CODE_SHA：`ea3b20ad13c65ab01cf2c761db6b09c185855b53`。108项最终核心测试绑定`0b7914dfc65cfef39a96586713c8810d7c7fbfad`，最终代码中workflow和tests逐字节未变。run03绑定`d1444eb07035ef651a36a3e89269f004186581df`，其他失败run保留各自CODE；后续安全修复没有冒充它们的重跑。最终artifact只增加记录、Notebook输出、图、表和审核说明，未再改影响结果的核心代码。

发布以publication中的实际检查和最终会话报告的HEAD/remote为准。自身所在提交SHA无法预写入自身文件；可从GitHub当前固定提交或`git log -1 --format=%H -- task1/evidence/goal1/REVIEW_PACKET.md`定位该版本。GPT须读取真实远程树和上述文件独立审核，Codex不自授最终PASS。
