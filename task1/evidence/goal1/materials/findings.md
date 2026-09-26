# Goal 1 材料核查与影响记录

Task ID：`SC-LAB1-G1-FOUNDATION-001`。本记录来自独立的工程材料核查子任务，不是运行时研究、处理、审核三角色中的一次调用，也不构成真实 Multi-Agent 闭环证据。未修改或执行教师 Notebook，未调用原 starter 的模型或记忆入口，未把历史输出纳入本轮结果。

原文件位置、SHA256、函数位置见 [extraction_index.json](extraction_index.json) 与 [source_catalogue.md](source_catalogue.md)；全量文字、数学公式、备注及 Notebook source/count/outputs 见相应提取文件；实际阅读与图表检查边界见 [reading_coverage.json](reading_coverage.json)。本文件记录源材料事实和对 G1 的影响；实际工程处置、测试和最终状态以主审核包为准。

## 1. 数据语义：已声明的内容与未知内容

| 条目 | 来源与实际核查 | 可用状态 | 影响与 G1 处置边界 |
|---|---|---|---|
| 顶层 ID / 记录 | 补充 `build_ppt/out/轨迹数据清洗_学生讲义.pptx` 第 4 页列出真实结构样式 `"0": [[1523293209,...], [[121.472353,31.31464],...]]`，文字为“车辆 ID → 时间戳序列 + 坐标序列” | SOURCE_DECLARED；数组形状可另外结构核验 | 可按车辆记录进行开发诊断；ID 是否稳定实体 ID、单记录切取机制仍没有采集说明 |
| 坐标顺序与单位 | 同页明确 `(lon, lat)`、度；基础 Notebook Cell 2 使用该顺序 | SOURCE_DECLARED | 支持经纬度字段名，不支持擅自确认 datum 或米制计算 |
| 时间单位 | 同页明确 Unix 时间戳（秒）；Notebook Cell 1 的阈值注释使用秒 | SOURCE_DECLARED | 原始数值差、零/负时间差及重复时间诊断可独立开展；本地显示时区、采集时是否有错误时区转换仍未知 |
| CRS / 基准 | 主 PPT 13 页正文称 GPS 通常 WGS84，备注称国内采集一般 GCJ02；两者是一般说明，均没有绑定该 JSON 的来源。`utils/util.py` 的 WGS84 函数名、`core/geo.py` 的 WGS84 实现约定不是数据来源声明 | UNKNOWN；资料一般说明有不一致 | 阻止依赖确认基准的真实投影、米制长度/速度、米制分段与 DP 验收；不能把地图重合当确认，也不能声称已证明 JSON 自身声明了两个 CRS |
| 采样机制 / 运动类型 | 基础 Notebook Cell 1 用平均 10 s、20 m/s 解释 400；主 PPT 24 页用骑行 12 s、25 km/h 解释 95 m；补充讲义又叙述 20 s 的正常间隔 | 不同参考场景，非统一数据生成合同 | 不把 95/400/其他 prior 混成一组，不由历史直方图反推出固定采样机制 |
| 速度 / 方向 | 原 JSON 对应两数组；Notebook Cell 2 派生输出为 `[时间, 坐标, 速度, 方向]`，Cell 6/8 注释却写 `[时间, 坐标, 方向, 速度]` | 工程错配 VERIFIED_BY_SOURCE_INSPECTION | 新处理接口使用明确字段；零时间差速度不可计算、零位移方向不可计算；邻接变化后重算 |
| 标签 / 真值 | 两份 Notebook、README、使用说明、DECISIONS、ABLATION_REPORT、demo summaries、教师和补充 PPT 未提供点级真实异常标注或独立可靠参考轨迹 | 未发现；不能反向证明任何地方绝无标签 | 不称误删率/恢复真值/检测准确率；旧搜索“ground truth”只可解释为预算内搜索参照 |

## 2. 教师方法与初始化数值

主 PPT 全文/备注见 [pptx_05_text_and_notes.md](pptx_05_text_and_notes.md)。第 18/20/22 页单页渲染及第 23 页全部 16 帧 GIF 已实际查看，避免只读文本丢失索引关系。

- 分段：第 17–18 页在异常边 `p2→p3` 处分开，左段 `p0…p2`、右段 `p3…pn`，图中没有复制边界点；短长度与少点数片段另行过滤。第 17 页 3 s/30 s 是图解例子。基础 Notebook 对间隔/距离用严格 `>`，长度/点数过滤用严格 `<`。真实空间部分仍受 CRS 限制。
- 去噪：第 20 页明确“p3 的方向”是 `p3→p4`；若 p2 的方向与 p1 和 p3 的方向之差均超过阈值，则删除 p2 并连接 p1→p3。因此已明确的谓词是 outgoing edge direction 比较，不能替换为单个转角、曲率或 starter 后增的 drift 规则。
- 去噪未决：材料没有规定同时标记一次、每删一个点立即重算、或整轮后重算并重复。删除点集合确会不同，见下节。首尾、不可计算方向的行为也未在该页完整定义；当前 Prompt 已明确不能把零向量方向当真方位。不能从一次示意图自动批准某种重复 schedule。
- DP：第 22 页明确到起终点“线段”的距离；最大距离严格大于阈值时保留该点并分裂，否则只保留两端。第 23 页 GIF 展示递归选择/删点；它不为无限直线距离或坐标反查索引提供依据。
- 顺序：基础 Notebook Cell 10 是 `split → denoise → simplify`，只是教学参考顺序；第 42 页要求讨论换序，未证明最优。

| 参数 | 当前基础 Notebook Cell 1 原值 | 单位来源 / 限制 | 角色 |
|---|---:|---|---|
| `LIMIT_LENGTH` | 65 | Cell 1 未直接写 m；`core/params.py:115–117` 的 `min_seg_length_m` 和 `core/segment.py:62–70` 的 `min_length_m` 明确米，实际 datum 仍未知 | STARTER_REFERENCE，不能称已获批最佳值 |
| `LIMIT_POINT` | 5 | 点数，原注释“轨迹点数小于该值”过滤 | STARTER_REFERENCE |
| `LIMIT_DT` | 30 | 原注释 `3 × 平均采样间隔（10s）` | STARTER_REFERENCE，非真实固定采样结论 |
| `LIMIT_DISTANCE` | 400 | 原注释 `2 × 10s × 20m/s`，米 | STARTER_REFERENCE，不能与 95 m 混同 |
| `LIMIT_DIRECTION` | 35 | 原注释方向变化；`utils.get_angle_to_north` / `calculate_angle_diff` 使用度 | STARTER_REFERENCE；schedule 待定 |
| `DP_THRESHOLD` | 5 | 根目录 `douglas_peucker.py:6` 的 `THRESHOLD = 5 # 阈值5m` 注释及米制投影调用 | STARTER_REFERENCE；需有限线段正确实现与合法距离口径 |

PPT 第 24 页的 **95 m** 是自行车示例：约 12 s、25 km/h 给出约 83 m，再考虑图像与超速取 95 m。它不是对本 JSON 强制应用的教师全局阈值。补充讲义“30 s 会误切正常 20 s”与实际严格 `dt > threshold` 不相容，`[15,180]` 下界也不能在取 15 时保住 20 s；这些 rationale 保留为疑点，不作为正式选参依据。

## 3. 去噪 schedule 的两个最小反例

来源标记：`CONSTRUCTED_FIXTURE`；用途：`ENGINEERING_TEST / METHOD_DEFINITION_AMBIGUITY`。以下为明确的平面构造坐标，不是教师轨迹，不使用未知 CRS，也没有正式选定新算法。角度以北向为零，仅为复现教师相邻 outgoing 方位差关系；阈值为 35°，均使用正确周期角差。

| 反例 ID | 点列 / 已知初始方向 | 解读 1 | 解读 2 | 证明范围 |
|---|---|---|---|---|
| `DIRECTION-SCHEDULE-01` | `(0,0),(0,1),(0,2),(1,2),(1,3)`；`0,0,90,0` | 单次同时标记删原始 2，保留 `[0,1,3,4]` | 整轮后重算再迭代，第二轮原始 1 方向变 45°、两邻为 0°，再删 1，保留 `[0,3,4]` | 一次与迭代并不等价 |
| `DIRECTION-SCHEDULE-02` | `(0,0),(0,3),(1,3),(1,4),(2,4)`；`0,90,0,90` | 初始同时标记原始 1、2，保留 `[0,3,4]` | 左到右即时删 1 重算后，原始 2 的前邻方向约 18.435°，与自身 0°的差不再超过 35°，保留 `[0,2,3,4]` | 同时标记与即时重算并不等价 |

两例各 5 点，对初始 outgoing 方向比较提供两个可判定的内部点。真实执行的构造验证脚本和全部动作：

```bash
python3 task1/evidence/goal1/materials/direction_ambiguity_fixtures.py
```

输出：[direction_ambiguity_fixtures.json](direction_ambiguity_fixtures.json)，两个断言均为 `PASS_FOR_COUNTEREXAMPLE`；它们只证明定义差异会改变删点，不能证明任一种 schedule 对真实数据更好。建议将选择交由 GPT/用户研究审核；G1 可验证共有数学与权限阻断。

## 4. 历史审核线索逐项复核

路径根目录默认 `task1/作业/作业/`；Notebook 的 Cell 编号零起始。以下静态检查不冒充测试运行；主线程保存的现状测试日志与修复后测试另外审阅。

| ID | 源码 / 原文位置 | 实际检查与发现 | 影响 / 本轮处置建议 |
|---|---|---|---|
| M01 | 基础 Notebook Cell 4/6/8 | 三个主体均 TODO，均创建并返回空字典；不是已实现基线 | 工作版调用经过测试的新共有实现；教师源保留 |
| M02 | 基础 Notebook Cell 2/6/8；`utils/util.py:253–272` | 派生字段顺序与函数注释相反；速度 `dt==0` 返回 0；方向零位移走 `atan2(0,0)`，末值复制前一个方向 | 显式字段/可计算状态，避免假低速/假方位；邻接更新后重算 |
| M03 | 任务3 Notebook Cell 6/21/30 | 两处显式 `MockProvider()`，后文称只需环境变量/无需改代码与实例不符；所有 code execution_count 均 null，全部 outputs 为空 | LIVE 必须实际独立构造/核实合法 provider，不能把该源文件当本轮真实调用 |
| M04 | `traj_agent/agent/loop.py:464–489` | `_execute` 实际仅 `denoise_trajectory` + `simplify_trajectory`；没有调用分段 | 分段工具存在不代表主执行链调用；G1 共有链须记录阶段并守恒 |
| M05 | `traj_agent/core/anomalies.py:81–91`；上项 | `RuleParams.from_params` 映射 max_speed/max_accel/max_turn/dist_threshold，未映射 dt_threshold；主数值链也不分段 | dt 参数搜索在这条链没有对应时间分段效果（运行时间可能波动）；不继承为可信参数研究 |
| M06 | `traj_agent/core/clean.py:39–57,343–392` | 默认折叠重复点、改时间、平滑坐标，且非正时间差删除没有独立关闭项；折叠重复点保留末点 | 超出 G1 改值权限，也可能折叠停留时间；不可直接复用默认 pipeline |
| M07 | `traj_agent/core/traj.py:151–204` | loader 静默跳过结构/短记录，时间 `int()`，乱序时按时间排序 | 不适合全量原始结构盘点或保留原始值合同；直接读 JSON 并显式报告 |
| M08 | `douglas_peucker.py:10–18,28–54`；基础 Notebook Cell 2/18 | 老 DP 对竖直线返回 9999999，并用无限直线；坐标相等反查会混淆重复值索引；Cell 18 投影不裁剪，首尾相同只返回 start | 不据旧演示图证明 DP 正确；新链必须有限线段/原始索引与独立误差检查 |
| M09 | `traj_agent/core/simplify.py:douglas_peucker_indices` | 已有 indices 实现使用有限线段、首尾/退化处理，独立数值核心可以复用验证 | 不必复制整套 starter；但真实地理计算仍受语义合同限制 |
| M10 | `traj_agent/core/simplify.py:243–269` | `max_deviation_m` 对每个原点全局寻找最近简化线段；小输入直接 0 | 不等于批准的索引区间对应误差；新审核器不得用其自报值作独立证明 |
| M11 | `traj_agent/agent/loop.py:464–503`；`verifier/objective.py:107–179` | 参考是清洗后的轨迹，n_before 也为清洗后；复合目标容许 `1.5*tolerance + 1e-9`；含实测 runtime | 描述 DP 保真，不证明整体清洗质量；旧权重/松弛/适用性不是 G1 共同标准；运行时间项也不是完全确定 |
| M12 | `traj_agent/agent/loop.py:299`；`verifier/verify.py:252–269` | `res.ok=True` 表示执行到末尾；目标函数不适用且参数合规时也可 admitted=True，并称“regime 正确性” | 成功运行、当前质量、候选升级必须分开；缺少研究门槛应 PENDING_RESEARCH_REVIEW |
| M13 | `traj_agent/tools/registry.py:122–139`、render handler；`tools/store.py:153` | tool schema 是描述，call 直接传 kwargs；渲染 out_dir 来自参数；state_hash 仅 ID/n/首尾时间及首尾坐标，不能察觉内部点改动 | 不能当实际权限/完整性边界；控制器需 schema、路径和完整内容哈希校验 |
| M14 | `traj_agent/agent/provider.py:402`；`agent/prompts.py` | build_provider 无 key 可返回 Mock；旧输出解析可从自由文本提取/补救 JSON | G1 LIVE 失败必须真实失败，不能静默 Mock；严格解析和 schema 校验后才执行 |
| M15 | `traj_agent/verifier/ablation.py`；任务3 Notebook Cell 20/21 | 模块具有 use_llm=False、留出只读、不重叠保护；但 Notebook 实际仅 246/256/306/209 四条并允许写记忆，与相邻 12+12/只读文字不符 | 保留模块正确边界思想，不把示例当真实消融；G1 不执行四模式效果实验 |
| M16 | `traj_agent/verifier/ablation.py`；`verifier/verify.py` | 预算搜索最优称 ground truth；对失败 `if not r.ok: continue`；报告 proposal 而非直接采用 search best | 搜索不是全局真值，失败不能悄悄消失；search-only 效果对象需 G2 冻结，当前不沿用旧 regret |
| M17 | `traj_agent/memory/store.py:write_case`；README 架构说法 | L1 同时保存 admitted false/true，L2/retrieval 另有准入门槛，不是所有 SQLite 只写质量通过 | `memory_written` 不等于质量接受；保留负记录本身合理，需分层解释 |
| M18 | README/补充讲义/主 PPT 32 页；demo_out/summary.json | 文档出现约 63/17/20；实际保留的 200 条 demo summary 是 147/31/22（73.5/15.5/11），图显示四舍五入 74/16/11 | 历史不同描述/运行，不强凑到当前结构盘点；图中百分比和不为 100 也可能只是各项舍入 |
| M19 | 任务3 Notebook Cell 26 | “352:170 点、3 秒、4 唯一时间戳”与当前 JSON 不相符；本轮只读检查为 170 点、54 唯一值、跨度 543、116 个零差 | 旧案例叙述不能转抄；此记录已被分析，属于开发暴露 |
| M20 | `core/metrics.py` 的空输入/零长分支 | 多个空距离返回 0、零长度曲折度返回 1；可能将不可用伪成最优值 | 新结构化 metric 需 unavailable_reason；不可直接升级为准确率 |

没有为以上问题修改教师材料或 starter。本轮根目录新实现、测试、Notebook 应由主审核包说明复用/修复关系，避免材料核查报告在代码尚未验证前自行宣布修复完成。

## 5. 对历史已暴露案例的真实结构核对

为核实 Notebook 的具体旧说法，只读访问已有材料提及的 `0,246,256,306,352,209`，不作方法评分或新样本优选；未计算米制速度/距离。脚本直接读原始 JSON，不调用会排序/跳过的旧 loader：

```bash
python3 task1/evidence/goal1/materials/check_historical_cases.py
```

结果见 [historical_case_structure_check.json](historical_case_structure_check.json)。原始输入 `task1/作业/作业/traj_dict.json` 执行前后 SHA256 均为 `c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3`。

| ID | 点数 | 唯一时间值 | 时间跨度（原数值单位；来源声明秒） | 零时间差边 | 负时间差边 | 相邻重复位置边 |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 99 | 99 | 1186 | 0 | 0 | 78 |
| 246 | 108 | 107 | 1190 | 1 | 0 | 0 |
| 256 | 99 | 99 | 1173 | 0 | 0 | 7 |
| 306 | 111 | 106 | 1196 | 5 | 0 | 4 |
| 352 | 170 | 54 | 543 | 116 | 0 | 76 |
| 209 | 119 | 117 | 1192 | 2 | 0 | 0 |

分类：`CURRENT_RUN_READ_ONLY_STRUCTURE_CHECK`。这是本轮真实原始结构检查，不是正式清洗、不证明异常点真值、不替代受 CRS/schedule 阻断的完整基线真实验收。

## 6. 材料范围、缺失与后续

- 读取 5 个 PPTX（主教师 43 页、补充 16 页/15 页/14 页/14 页）；两个 14 页文件 SHA256 完全相同。全文、备注、公式逐页提取，技术图表另行视觉核查。
- 两份 Notebook 所有 source、execution_count 和输出读取；基础 Notebook 的保存输出为 HISTORICAL，Cell 18 正弦加噪示范为历史合成图。LLM Notebook 没有保存的执行输出。
- 69 个相关 starter 文本文件全量读取、散列/语法解析和函数目录；重点方法/数据/控制链进行了人工静态核查。目录读取/AST 解析不等于每分支人工审完，更不等于执行测试。
- 同名 ZIP 内外数据/源码的字节比对与全量结构盘点由主线程保存；本子任务不重复整套清单。历史测试总数不作本轮结论，实际 baseline/after 日志亦由主线程提供。
- 未发现指定的 `Task1_Literature_Review_2025_2026_Merged.md`、`Task1_Source_Audit_2025_2026_Merged.json`、`Task1_Stage01_Readonly_Audit.md`；没有访问假定的 ChatGPT sandbox 链接，没有重写冒充这些文件，没有开始广泛论文检索。
- 本材料核查不触及长期治理改写、11-file 上传集合、正式报告、真实新模型调用或 Goal 2/3 研究。

研究审核首先需要补充数据专属 datum 来源，并选定教师去噪的 schedule/端点/不可计算行为。普通 loader、索引、状态与指标不可用分支可以由 G1 工程测试独立修复；质量收益阈值、划分和候选比较仍由下一阶段合同批准。
