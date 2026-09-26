# Task 1 — Stage 0 / 1 只读核查记录

核查日期：2026-09-22。状态：任务理解待用户审核；没有方法或架构冻结。
本记录不是正式实验报告，不是 Codex 实现任务，不是 Evidence Lock。

## 核查范围与边界

读取了上传的四份治理 Markdown、两份 PDF 模板、43 页教师 PPTX 的文字和备注、两个 ZIP 的内容清单，以及 ZIP 内的两个 Notebook。检查了 starter 的主要调用链、关键处理与评价代码、测试目录和历史报告。PDF 与关键教学页面进行了视觉核查。
通过 GitHub 连接读取 main 分支、Git 对象树、关键远程文件和 source manifest；已直接读取安装态 publication-plots/SKILL.md。没有把 ZIP 的存在当成已经读过安装态 Skill。
未执行 Notebook、pytest、轨迹清洗、参数搜索、LLM 请求或正式消融。数据统计仅是独立读取原始 JSON 的全量结构统计。没有修改上传原件、仓库或用户工作区。
不是全仓每一文件逐行代码验收；未检查用户本地 ~/lab/Smart_Cities_and_Location_Services 的环境、未提交改动及运行状态。无法凭 manifest 证明 ChatGPT UI 已上传了哪些文件或 UI Project Settings 全文。

## 远程快照

Repository: woobowen/Smart_Cities_and_Location_Services
Branch: main
Commit: b25efc153311a967109c586edab39361326500c7
Commit time: 2026-09-22T08:21:03Z
Commit message: docs: make project sources bundle upload-ready
实际 starter 目录：task1/作业/作业/。

## 11 项逻辑来源

本轮有 9 个顶层附件；两个 Notebook 从作业 ZIP 中找到，因此 11 项内容均可读取。不是缺失两个 Notebook。以下 SHA256 与此远程快照的 SOURCE_MANIFEST.md 对应记录一致。

| 逻辑文件 | 实际读取位置 | SHA256 |
|---|---|---|
| `SMART_CITIES_RESEARCH_PROTOCOL.md` | `SMART_CITIES_RESEARCH_PROTOCOL(2).md` | `9f94c4f73358af90e8fce1a74b9e688e9b33c2ff375a9a42fc384f6623397699` |
| `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md` | `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL(4).md` | `fa640db61ce7b1e1487083a1d6f663c75eb11ff6ee6b7b01b21f48dbcdc7b06a` |
| `SMART_CITIES_VISUAL_SYSTEM.md` | `SMART_CITIES_VISUAL_SYSTEM(7).md` | `10cd5024641f4877fa0e7d569c507c4246bc3d0574901658e490ab0f5ff70d6c` |
| `AGENTS.md` | `AGENTS(3).md` | `cbff3157e2289b58f370d422124f6799bcde255892d999afdf94410fcda7578f` |
| `Experiment_Report_P2_Exact.pdf` | `Experiment_Report_P2_Exact(7).pdf` | `6fd543f5123ba4d67985193d5658802ae820c6585dc3f509071b8b2d39b323dd` |
| `Process_Report_P2_Locked_v1.pdf` | `Process_Report_P2_Locked_v1(6).pdf` | `3903042ef7935a722d32871a9f55ba973b1262ee0fe290363b0a6c3bda09dcfa` |
| `实验课1.pptx` | `实验课1(5).pptx` | `cf5fdbdd0e116818f4bf195e8761dd55c4733443d7c360c986cf1cdfddfda075` |
| `作业.zip` | `作业(5).zip` | `818d483cf719aeb1145ea97b551b2648913559ed1fca0be220ed41eff8ba42cc` |
| `任务3_LLM辅助评估清洗.ipynb` | `作业.zip :: 作业/任务3_LLM辅助评估清洗.ipynb` | `4ecffe64024e002c0cffe7830e18b5f6ded04cd5aa9dd645d6798fc9b0715add` |
| `作业1轨迹数据预处理.ipynb` | `作业.zip :: 作业/作业1轨迹数据预处理.ipynb` | `8601d1dfecaef062fef553992cc9774d3a0eb551751c70536f5b52f1343b158a` |
| `publication-plots.zip` | `publication-plots(3).zip` | `b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041` |

## 远程对象一致性

对 ZIP 解出的对应目录重新计算 Git tree SHA，与 GitHub 返回的真实树对象逐项比较。以下六棵树一致；这使本地读取的这些目录能对应到远程快照，不只是相信 README 或旧 PASS。

| 子目录 | 本地重建及远程共同 Git tree SHA | 一致 |
|---|---|---|
| `traj_agent` | `fccca9ac2f7b9ed9aa92b563dfb9178884e545b4` | True |
| `tests` | `049ed065061b287383eae81bb39c7b85277e1174` | True |
| `utils` | `d9917a08d3882d2d30f8742e181110f11476660f` | True |
| `demo_out` | `c18e9881dc7a775e38615934e4a8614cde537e52` | True |
| `figures` | `98a507f6a1667cfd3176ba756107e2eb562e1d94` | True |

个别关键文件的 Git blob SHA 亦与远程一致：

- 作业1轨迹数据预处理.ipynb: a17e239ed5bc540762f18210e1ddbbf067e0819b
- 任务3_LLM辅助评估清洗.ipynb: 1107126898a97bee75ebe15fa05163810c5d9344
- traj_dict.json: 212f2bd50f9aec81b65192ce42a494919717a9ae

## 教师材料定位

| 页码 | 内容 | 来源性质 |
|---|---|---|
| 4–5 | 实验一预处理、评价、LLM 工作流；清洗压缩程序、评估报告、包含 AI 批判的过程报告 | 教师材料 |
| 6 | 准确性与隐含假设批判；至少一组反例；修改前后指标；拒绝建议及原因 | 明确批判要求 |
| 8 | 建议用 deepseek harness；“能不用codex、CC、KIMI CODE就不要用” | 工具使用建议；是否有后续解释待确认 |
| 18 | 时间/距离异常处切分，过滤过短或点太少的子轨迹 | 教学方法 |
| 20 | 当前至后序点方向，与前后方向差异均大时去除漂移点 | 教学方法 |
| 22–23 | Douglas–Peucker，点到端点线段距离 | 教学方法 |
| 24–25 | 12s、25km/h 推出约83m，再取95m；保留比例 | 教学参数示例；并非已验证全局最优 |
| 26 | 必做填 Notebook 与评价报告；LLM 系统和思考讨论选做；10月5日前邮件提交 | 作业细则 |
| 28–40 | 诊断卡、句柄、LLM 建议、确定性搜索核验、四层记忆、消融与未验证边界 | TA 工作流教学说明与旧结果 |
| 42 | 三种预处理步骤可否调换顺序 | 思考讨论 |

第26页邮件：52285903012@stu.ecnu.edu.cn；名称：学号_姓名_实验一.zip/.ipynb/.docx/.pdf。日期行未给具体时刻；年份由封面的2026课程背景解释。PPT 的 Trajectory_preprocessing.ipynb 与实际中文 Notebook 需记录名称对应，不能凭空声称找到另一份英文文件。

## 原始数据独立全量盘点

数据根文件与 utils/traj_dict.json 按字节一致，是同一数据的两份副本。所有统计基于未处理数据，分母和单位如下。数值时间差不需要指定时区；解释为秒采用 starter 口径，原始文件未自带时区或 CRS 元数据。

```json
{
  "scope": "Read-only full JSON inventory, not a cleaning run or experiment",
  "source": "作业(5).zip :: 作业/traj_dict.json",
  "data_sha256": "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3",
  "raw_objects": 11386,
  "point_count": 1173410,
  "value_schema": "[timestamps, [[longitude_like,latitude_like],...]]",
  "aligned_records": 11386,
  "schema_mismatch_keys": [],
  "nonfinite_keys": [],
  "point_count_per_record_quantiles": {
    "min": 20.0,
    "p25": 99.0,
    "median": 100.0,
    "p75": 106.0,
    "max": 229.0
  },
  "coordinate_min": [
    120.38636499999998,
    30.578117
  ],
  "coordinate_max": [
    121.915853,
    32.239372
  ],
  "raw_timestamp_min": 1523293200.0,
  "raw_timestamp_max": 1523294398.0,
  "intra_record_dt_count": 1162024,
  "dt_mean_raw_units": 11.497196271333467,
  "dt_quantiles_raw_units": {
    "min": 0.0,
    "p25": 10.0,
    "p50": 10.0,
    "p75": 11.0,
    "p95": 20.0,
    "p99": 29.0,
    "max": 1037.0
  },
  "nonpositive_dt_edges": 42185,
  "zero_dt_edges": 42185,
  "negative_dt_edges": 0,
  "records_with_nonpositive_dt": 5125,
  "records_with_negative_dt": 0,
  "adjacent_identical_coordinates": 575278,
  "adjacent_identical_coordinates_and_timestamp": 13010,
  "dt_most_common": [
    [
      10.0,
      595459
    ],
    [
      20.0,
      148290
    ],
    [
      11.0,
      73048
    ],
    [
      9.0,
      72340
    ],
    [
      0.0,
      42185
    ],
    [
      1.0,
      23424
    ],
    [
      21.0,
      19728
    ],
    [
      19.0,
      19662
    ],
    [
      2.0,
      17352
    ],
    [
      3.0,
      16100
    ]
  ],
  "crs": "UNVERIFIED: raw file has no CRS metadata",
  "timezone": "UNVERIFIED: raw file has no timezone metadata",
  "object_identity": "Raw keys exist; one key = one unique vehicle/person/trip is not established by file alone",
  "ground_truth": "No truth coordinate/label fields in raw [timestamps,coordinates] schema",
  "record_352_read_only_check": {
    "n_points": 170,
    "unique_timestamps": 54,
    "timestamp_min": 1523293809,
    "timestamp_max": 1523294352,
    "span_raw_units": 543,
    "zero_dt_edges": 116
  },
  "record_352_conflict": {
    "historical_claim_source": "DECISIONS.md D5; LLM notebook cell 26 (0-based)",
    "historical_claim_n_points": 170,
    "historical_claim_unique_timestamps": 4,
    "historical_claim_span_s": 3,
    "discrepancy_cause": "UNVERIFIED; no cause inferred"
  }
}
```

结构上未发现非有限数值，不等于没有缺采样、轨迹误差或时间语义问题。坐标重复不自动等于噪声，亦不能用其比例推出静止轨迹占比。11,386 是顶层 ID 记录数，不在缺少元数据时断言每条代表一次完整骑行或一名用户。

## Starter 状态与差异定位

Notebook cell 编号以下均为从 0 开始。

| 位置 | 实际读到的内容 | 对当前工作的影响 |
|---|---|---|
| 基础 Notebook cells4/6/8 | split_traj / denoise_traj / simplify_traj 均只初始化空字典并返回 | 三个作业实现空缺仍在 |
| 基础 Notebook cells12–17 | 分段、去噪、简化三组“选做”超参数实验，代码空白 | 按项目协议全部属于T2；范围不只调一个DP参数 |
| 基础 Notebook cell1 | 65m、5点、30s、400m、35°、DP5m | 仅是 starter 数值，不是本轮批准参数 |
| 基础 Notebook cell2 vs cells6/8注释 | 实际返回速度后方向，注释却写方向后速度 | 后续需要统一数据合同；不能默默互换 |
| 基础 Notebook cell2 | 经纬度转 Mercator 后调用旧DP | 不与新agent几何度量天然一致 |
| douglas_peucker.py::point2LineDistance | 垂直线返回9999999；用无限直线距离 | 旧helper不能无条件作为正确实现；尚未在本轮跑回归测试 |
| 基础 Notebook cell18 | 合成正弦噪声DP例子，保留旧图 | 不属于当前真实轨迹处理结果 |
| LLM Notebook | 33cells；代码outputs空且execution_count均null | 是待运行演示入口，不是本轮完成证据 |
| LLM Notebook cells6/21 | 显式MockProvider实例 | 只改环境变量不会把此实例变成真实API provider |
| LLM Notebook cell20 vs21 | 文字称12demo+12holdout；实际对246/256/306/209循环，没有调用两阶段runner，未开启read_only | Notebook中的消融不符合旁边文字；不能整体沿用 |
| traj_agent/verifier/ablation.py | 另有两阶段runner，检查demo/holdout重叠，holdout只读 | 不可把Notebook缺陷误说成整个包没有正确runner |
| LLM Notebook cell15 | 出图重新按默认clean运行，只取建议DP参数 | 图与提议评价路径需重新核对 |
| traj_agent/agent/loop.py::_execute | 去噪→简化；reference=cleaned；未调用分段 | 不能宣称当前Agent已统一完成三个步骤；纯DP误差不等于整体质量 |
| loop.py::run | ver.admitted为False后仍可res.ok=True；记忆记录携带admitted标志 | 工程运行成功不等于质量审核通过；记忆准入不是最终Release Gate |
| loop.py::_evaluate_and_verify / _run_search | 默认值被实际执行评分；坐标下降从默认起，另纳入建议 | default目前有基线、回退、搜索参照等不同角色 |
| loop.py::_run_search | 三个参数、5步、3轮、max_evals=60的坐标下降，另评估proposal | “搜索最优”仅指找到的最好候选，没有全局最优证明；总预算仍需核对 |
| loop.py::run / verify.py | 先夹紧提议再传核验 | 原始越界率、修正后合法率需分开记录，当前存在统计被掩盖风险 |
| core/params.py | 声称30s会切掉20s、15s能保住20s | 与dt>threshold切分判据不一致；不能引用该文字作合法参数依据 |
| core/clean.py | 默认可修正时间戳、删除重复点、平滑坐标 | 这些会改变时空语义，不能视为普通路径修复自行沿用 |
| DECISIONS.md D5 / LLM Notebook cell26 vs raw352 | 旧文档写170点/4种时间/3s；原始文件实为170点/54种时间/543单位跨度 | 原因未查明，旧案例结论不可直接继承 |

## 历史结果与真实运行边界

ABLATION_REPORT.md 明确其12+12结果基于Mock；不能用来证明真实LLM增益。demo_out/ecnu_token_report.md 则记载小规模真实API调用及两条案例，所以不能笼统说这个包从未尝试真实模型；两者都不是本轮实测，也不是正式真实LLM留出消融。
demo_out中的SQLite、预生成summary/ablation文件，figures与build_ppt相关图片、vault_stub人类笔记，均为随材料带来的历史/演示资产。两份P2 PDF是合成模板，不是已完成的作业报告。
本轮没有测试PASS、没有质量提升率、没有正式Agent贡献结论，也没有构造虚假的用户质疑或AI错误。

## 当前不冻结

不冻结CRS/坐标转换/时区、时间戳修复权限、95m或400m、预处理顺序、Agent个数、默认值角色、目标函数、regret口径、搜索预算、留出划分或结论。
下一阶段应由用户先审核任务理解，再形成集中讨论的Decision Agenda。正式代码修改与运行需在适用的方案批准之后。
