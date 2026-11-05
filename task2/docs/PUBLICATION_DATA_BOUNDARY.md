# 公开发布的数据边界与复现入口

状态：**用户已明确确认没有额外数据公开许可**。按本轮最新指令，本地继续完成全部实验与验收；Git公开完整code/config/tests/scripts/figures、双报告及不泄露逐条记录的汇总，不上传原始CSV、含data的ZIP或可还原逐条签到的派生文件。这是本轮发布范围记录，不是法律结论，不禁止现有材料上的本地教学计算。此前的额外授权询问现已得到答复；若未来取得真实授权，应另加来源、时间和范围，不覆盖本次未授权发布边界。

## 已核实的获取来源

原作者 [Dingqi Yang 数据页](https://sites.google.com/site/yangdingqi/home/foursquare-dataset) 提供 [NYC/Tokyo研究数据ZIP](https://drive.google.com/file/d/1VE67jfSN-GV6fkCfuyBEQJzk_qy-SfOk/view?usp=sharing)。实际从该公开入口下载得到25,546,284字节，SHA256：

`cbe3fdab373d24b09b5fc53509c8958c77ff72b6c1a68589ce337d4f9a80235b`

来源网页和readme要求引用作者论文，但未列明确允许本仓库再次公开分发的license。原始数据继续留在本地；不把当前Foursquare API商业条款倒套到该研究数据。Google Drive插件已用于读取原作者readme与确认ZIP元数据；本地复现下载脚本只使用作者公开端点，不存连接凭证、签名下载地址或API key。

## 合法获取和重建命令

在仓库根目录运行：

```bash
.venv/bin/python task2/scripts/fetch_public_data.py \
  --compare-teacher-dir task2/teacher_materials/advanced/foursquare
```

该入口已实际从无缓存目录完成网络下载、固定hash核验、两城市TSV解析和受控CSV转换。`--compare-teacher-dir`只在已有教师CSV时做额外逐字段比对，公开clone没有该目录也能完成固定hash核验；亦可直接不传此选项。新版默认输出到 `author_original/public_conversion_exact/`，不会覆盖先前近似转换。

下载脚本拒绝原作者ZIP、TSV或转换CSV的非预期hash；保留失败下载/转换供核查，不静默接受新数据。原始教师文件永远不被覆盖。`dispatch_data.source_path`优先原教师路径，缺少时自动发现新版精确重建目录，再保留旧`public_conversion/`、`author_fetch_reproduction/`、`author_original/`兼容入口。`audit`区分真实教师提供、`AUTHOR_RECONSTRUCTED_EXACT_BYTES`与历史近似`AUTHOR_RECONSTRUCTED`；作者获取身份须验证receipt中的archive/TSV/CSV，不由目录名或相同hash自动赋予。缺/坏receipt的相同内容保持`provider_unverified`，即使hash相同也不倒写提供者；未知内容hash停止正式load。

也可显式加 `--install-converted-layout` 将**作者精确重建输入**安装到空的教师路径位置，同时写经验证的`.provenance.json`，审计仍标作者重建身份。任何一个目标已存在即停止安装，不覆盖原件。

早期近似下载回执为 `evidence/research_data/public_fetch_network_verified.json`，保留原身份。**后续新版实际无缓存网络下载**和逐字段0差回执为 `public_fetch_exact_network_verified.json`；隔离无教师文件、原教师优先、显式安装sidecar与数据全等回归为 `source_entry_exact_regression.json`。保留下载目录中的 `FETCH_RECEIPT.json` 和来源readme。

## 早期近似转换与后续字节精确重建

以下表格记录**先前Python float `.10g`转换**的真实差异，没有把历史失败改写为早已精确：

| 项目 | NYC | TKY |
|---|---|---|
| 原作者TSV行数 = 教师CSV行数 | 227428 | 573703 |
| 原TSV SHA256 | `2f39ce698e5bff6683c74bec30c436cc022c160b0f3d73c5268b55491b2445f9` | `85542c605ce708d8584637756590383a84e9bbdb71342d0d8e78858ba2a0e5c8` |
| 教师CSV SHA256 | `60a235386a5324f55c9f24fb1b06e55a38a0d53c0242435d754b38c0cc0b514a` | `849365e52e970c85819b3cc1559bb00bedbe2e37f8e274d77241d62e89ac85f2` |
| 10有效位CSV SHA256 | `7439cd16c531a3d37115febbe3c125d543d7064c66ec465f296dad948c5e7d05` | `939bc38d8cdd555d4a89ddc090921e7ad187d0e7399717b75ff5c75871d4de4f` |
| 转换后latitude不同字段数 | 11 | 31 |
| 转换后longitude不同字段数 | 32 | 311 |
| 最大纬度/经度差（度） | 约1.0e-8 / 1.0e-8 | 约1.0e-8 / 1.0e-7 |

原TSV为Latin1；早期转换为UTF8/CRLF CSV，Python浮点坐标格式化为10有效数字。八字段行序一致；用户/venue/category ID、类别文字、UTC与offset逐行一致，少量坐标末位不同。此前8小数位与“先15位再10位”的Decimal变体也未达到字节一致；这些真实尝试及失败身份保留，没有逐行补丁。

早期NYC近似输入已实际经过相同trip构造：仍为25550对，来源行对/local日期/分钟一致；最大trip_km差1.1100001e-6km、fare差2.2200002e-6，见`public_conversion_proxy_check.json`和旧`source_entry_regression.json`。这一旧范围保持原身份。

后续按用户批准继续诊断，发现正确规则是：**原十进制文本直接取10有效数字、`ROUND_HALF_UP`，UTF8、行间CRLF且末行不追加CRLF**。直接half-up在NYC全部坐标上0数值差；再按确定性CSV序列化，两城市文件字节均与teacher完全相同。`half_up_conversion_verified.json`与新版无缓存网络回执记录：NYC SHA `60a235386a5324f55c9f24fb1b06e55a38a0d53c0242435d754b38c0cc0b514a`，TKY SHA `849365e52e970c85819b3cc1559bb00bedbe2e37f8e274d77241d62e89ac85f2`。没有逐行例外或改值补丁。

隔离clone实际核验了8份DataFrame（checkins/trips及所有日期分区/司机prior）与原教师入口逐项精确相同，分区仍25550/19617/1972/21589/3961；两原教师CSV hash保持不变。公开clone因此可从作者获取后**重建相同输入字节**，同时保留作者获取来源。相同输入字节仍不自动证明跨依赖环境的随机优化/模型产物二进制相同；模型代码、环境、参数和seed仍是实验复现条件。

## 本地保留、不公开的对象

主线程应对当前文件集确认后实施精确排除；本文件不会擅自更改全局 `.gitignore`。建议范围：

- 根目录含数据的 `实验2(1).zip`、`归档.zip`；`task2/teacher_materials/` 中CSV、嵌套ZIP/RAR，以及整个 `author_original/`、`author_fetch_reproduction/`。
- `task2/results/data/*.csv`：完整check-ins和逐条proxy trips及日期分区。
- `task2/results/evolution/batches/*.npz`：从真实签到采样的逐条OD/位置批次。基础 `basic/basic_synthetic_od.npz` 是独立全合成教学数据，不属于该真实数据排除项。
- 真实代理EA的raw JSON中，`genes/pairs`与各解目标`F`绑定也不公开。独立内容检查仅用匿名membership与总收入即可构造5897个方程，对56个可服务订单的系数矩阵满秩，数值残差约1.8e-12；去掉显式坐标或ID仍能恢复逐单数值。原run不改，公开前沿/指标另做不带membership的聚合投影。DTLZ2和基础独立全合成run保留原身份。
- `task2/results/online/foursquare_proxy_v1/inputs/*.json` 及该真实代理实验的逐条matches；全合成在线场景保留其公开身份。
- `task2/results/rl/**/episode_*.npz`、`task2/results/rl/**/trace_*.json`：从真实代理池抽样/扰动的逐条模拟事件与位置。Q/V训练参数和汇总指标单独判断，不能因扩展名同为NPZ就全部排除。
- RL `value_samples_*.npz` 的逐idle状态/回报样本，以及融合static/dynamic front中逐单genes/pairs和目标绑定亦本地保留；公开分发不含这些membership的安全目标/指标投影。
- `task2/results/rl/offset_robustness_v1/filtered_inner.csv`、`filtered_validation.csv`（以实际生成目录为准）及融合实验`static_input.npz`：分别是逐条代理池和逐条司机/订单决策状态，不能因为文件不叫`episode_*`就放行。
- `evidence/research_data/time_offset_anomalies.csv`、`author_conversion_pilot.json`、`author_conversion_controlled.json`、`author_conversion_decimal.json` 含逐条来源示例；其汇总/范围说明可公开。

最初建议清单与真实hash由 `evidence/research_data/local_only_manifest.json` 计算生成，该文件只覆盖当时存在的文件，不是最终允许发布清单。最终发布由独立V-PKG对实际文件内容扫描，并登记当前exact list、理由与hash；新增逐条产物必须纳入。清单和通配模式均不替代最终Git diff和文件内容审核。

追加的实际内容分类为 `evidence/independent_package/sensitive_classification.json`；反解probe仅保留矩阵rank/误差，不写恢复出来的逐单数值，见同目录`content_probe.json`。`evidence/research_data/refresh_local_only_manifest.py`将原模式、当前命中文件与独立内容分类精确合并，输出`local_only_manifest_current.json`。早期1013、1370、1379及REPLAY后的1496文件清单均保留历史。独立stage内容检查又发现一份真实KM计时记录含41组pairs+F，按`independent_package/staged_sensitive_addendum.json`追加；**当前实际快照为1497个文件、1,831,912,940字节**。更新快照不宣称所有未列文件都可公开；最终stage和Git对象检查另有责任人。

新增计时原件为`results/evolution/km_timing/inner_hour18_batchseed2024_M2.json`，SHA256 `139dfb8a5124d990a9686d04fe1b87a7c3bca2436b5a0e2a891e5705dccc4ebe`。本地原件保持不变，公开规范指标已保留计时/求解次数和`timing_recompute_sha256`；不能因为文件名写timing就允许其中的逐单membership公开。1496快照另存`local_only_manifest_1496_previous_bc8818293d13.json`，原REPLAY hash变化与批准身份继续保留。

REPLAY取证按`evidence/rl/replay_recovery/cli_help_replay_01/replay_sensitive_classification.json`精确增加117个敏感文件：20个episode、95个trace、重放raw融合front和hash验真恢复的原融合front各1个。没有粗排整个取证目录；当前54份聚合比较/来源回执/CLI代码/模型参数等保持公开候选。原canonical `final_v1/fusion_fronts.json`仅因重放计时改变hash，从`ec45229c…e35c0f`到`484d6819…9cca1e`，按主线程明确事故披露和独立重放补验登记在`classified_file_hash_changes`及`authorized_replay_hash_changes`，不改旧分类；未解决的非预期hash变化为0。该登记不是忽略变动，也不把REPLAY冒称新独立测试。

## 可以继续发布的内容

源码、固定配置、测试与反例、全合成输入、数据来源/hash/schema/聚合统计、汇总metrics、研究决定与独立核验记录、Q/V等模型参数、原生科学图及LaTeX/PDF报告、重建脚本、外部审查索引继续制作。公开图应以聚合统计或有明确合成身份的机制展示为主，不在图表中再分发可追溯的逐条签到/用户轨迹。

本地原件、真实run、受限逐条输入与日志不删除。公开工程须明确未含哪些文件、如何从来源取得和精确复现的边界；不能以代码可下载冒称全部数据已经同步。
