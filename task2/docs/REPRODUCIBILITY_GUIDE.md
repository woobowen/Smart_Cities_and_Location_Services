# 复现指南

所有命令在仓库根目录执行。原始材料/结果、实验重算、图表重画、报告编译分别验收。
当前工作目录不要覆盖已审核run；完整实验重算应在独立干净副本运行。现有作者脚本和原始版本快照保留真实身份，发现REPLAY/RECOMPUTE记录时不能算新独立实验。

## 1. 环境

本轮实际沿用已有`.venv`，Python3.12.3、NumPy1.26.4、SciPy1.11.4。公开环境可按以下步骤创建；这是复现说明，不表示本轮另建了平行环境。

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r task2/requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name smartcities_dispatch --display-name 'Smart Cities project .venv'
```

已有继承system-site-packages的venv可能被系统旧`mpl_toolkits` namespace抢先固定。仅在出现已记录的Axes3D版本冲突时运行项目内修复：

```bash
.venv/bin/python -m task2.scripts.repair_project_matplotlib_namespace
```

它只在当前venv写`.pth`，不改系统配置。纯新venv通常不需要。TeX使用XeLaTeX/latexmk和Noto Serif/Sans CJK SC；字体二进制不分发。报告直接依赖ctex、fontspec、geometry、booktabs、tabularx、amsmath、titlesec、fancyhdr、caption、hyperref、microtype、placeins、etoolbox、enumitem、needspace等，按实际安装来源补齐。本轮只补placeins/needspace并按包管理器要求自更新tlmgr，未update全套TeX。

## 2. 原始数据的合法获取和SHA

作者发布页：[Foursquare dataset](https://sites.google.com/site/yangdingqi/home/foursquare-dataset)。页面指向的公开下载：[原作者ZIP](https://drive.google.com/file/d/1VE67jfSN-GV6fkCfuyBEQJzk_qy-SfOk/view?usp=sharing)。脚本确实从该渠道网络下载并校验，不在GitHub再分发数据。

```bash
.venv/bin/python task2/scripts/fetch_public_data.py
.venv/bin/python -m task2.src.dispatch_data
```

输入链的预期SHA256：

|对象|SHA256|
|---|---|
|作者ZIP|`cbe3fdab373d24b09b5fc53509c8958c77ff72b6c1a68589ce337d4f9a80235b`|
|NYC教师CSV/精确重建CSV|`60a235386a5324f55c9f24fb1b06e55a38a0d53c0242435d754b38c0cc0b514a`|
|TKY教师CSV/精确重建CSV|`849365e52e970c85819b3cc1559bb00bedbe2e37f8e274d77241d62e89ac85f2`|

重建规则是原TSV Latin1→UTF8、坐标直接Decimal10有效位ROUND_HALF_UP、原行序、行间CRLF且末行无CRLF。初期近似转换的失败/差异记录保留历史，默认已使用实测精确规则。两城市源记录数为227428/573703，NYC教师矩形代理25550，inner/validation/test为19617/1972/3961。

已有教师数据可手动保持在`task2/teacher_materials/advanced/foursquare/`（两个CSV规范文件名见脚本），匹配固定hash后优先使用。公开重建在独立目录，验证FETCH_RECEIPT和获取sidecar后标`AUTHOR_RECONSTRUCTED_EXACT_BYTES`；同字节不倒写获取者。缺失/坏receipt和未知hash受明确检查，不只凭目录名认定来源。可选`--install-converted-layout`仅安装到不存在的教师路径，并保留作者来源sidecar。

已实测独立网络获取和孤立fallback/安装/8个DataFrame逐项一致，见`evidence/research_data/public_fetch_exact_network_verified.json`和`evidence/independent_package/exact_public_data_review.json`。source_crs仍UNVERIFIED；输入字节精确不证明地理datum，也不承诺跨任意软件版本随机实验二进制相同。

## 3. 数学和最小运行检查

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q task2/tests
.venv/bin/python -m task2.scripts.audit_geometry
```

数据fixture、在线参考、HV/Spacing/编码、TD/Double/移动/取消和公开边界反例都有已知答案；正式大样本另由独立参考检查，不能用测试数代替研究效果。

## 4. 正式实验入口

在线开发/独立合成确认及针对性研究（新副本或全新输出路径）：

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m task2.scripts.run_online --output task2/results/online/recompute_development_01
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m task2.scripts.run_online --confirmation --output task2/results/online/recompute_confirmation_01
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m task2.scripts.run_online_studies threshold --output task2/results/online/recompute_threshold_01
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m task2.scripts.run_online_studies proxy --output task2/results/online/recompute_proxy_01
```

进化分阶段命令和五seed已在`results/evolution/SUMMARY.md`逐项给出。依次baseline→scale→hybrid→combination，最后执行事前冻结的confirmation；不是在看到测试结果后选参数。原始已存run受源码hash/输入数组检查，完整重算在干净副本进行。

RL参考训练：

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python task2/scripts/run_rl.py --phase baseline --run recompute_baseline_01 --data task2/results/data --episodes 300
```

后续入口为`run_rl.py --phase sensitivity`、`resume_rl_rngfix.py`、`run_rl_followup.py`、`run_reposition_cost.py`、`run_rl_component_ablation.py`、`confirm_rl_movement.py`、`run_rl_offset_robustness.py`、`run_rl_fusion.py`。各真实命令、输入与run配置见相应`evidence/rl`日志、METHOD_SPEC和FINAL_SELECTION。当前11个RL启动器及基础NSGA入口有真正`--help`和既存输出拒写；帮助在导入实验/读取数据之前退出。**历史源码快照仍保留当时行为**，不要对旧快照盲目运行`--help`。

例如，保留公开提供的冻结父模型，单项重算使用新输出（不是新训练seed）：

```bash
.venv/bin/python task2/scripts/run_rl_followup.py --phase beta --model task2/results/rl/development_v1/q_f60_s2024 --run recompute_beta_01
.venv/bin/python task2/scripts/run_rl_fusion.py --output task2/results/rl/recompute_fusion_01
.venv/bin/python task2/scripts/diagnose_rl_double.py --output task2/results/rl/recompute_double_diagnostics_01
.venv/bin/python task2/scripts/run_rl_final.py --output task2/results/rl/recompute_final_01
.venv/bin/python task2/scripts/run_basic_multiobjective.py --output task2/results/evolution/recompute_basic_01
```

`--output`改变输出根目录，输入/冻结父模型仍按各脚本明示路径读取；先查看帮助和源码顶部路径。`diagnose_rl_double`从已登记Double模型/trace读取，诊断写入新目录；既有正式绘图不会自动改读新诊断。需要自己重建父trace时先在独立工作副本运行对应训练/评估步骤。新派生结果用于与原指标核对，不无声合并进当前ACTIVE索引、旧图或已验收PDF。最终重训使用全前70%数据、固定300回合及已冻结规则，不按重算结果改选。

整套从头重算须在**独立工作副本**将已有记录结果移到仓库外的归档位置，再按原父路径依次生成：数据导出→baseline/pilot→参数与beta验证→公平Double→移动成本/组件消融/五训练seed→融合→冻结final→secondary Monte Carlo→显式当前索引/统计→投影/绘图/报告。原始路径和依赖见`review/EXPERIMENT_INDEX.md`与各脚本；需要把新诊断用于绘图时显式适配其新目录，不覆写旧run。完整29模型+115EA在全新公开clone的一次命令重跑**未另行实测**；已实际验证的是全部原研究运行、输入精确重建、两本干净Kernel、独立数学/事件/统计核验、无原数据重画及报告源包独立编译，各范围分开报告。

原`run_rl_final.py`误触REPLAY、不可恢复旧逐日runtime、当前安全CLI与覆盖保护在追加修复记录中明确；最终策略不因此重新选择。当前guard仅改CLI/输出控制，数学主体等值及结果零变化有独立回执，原run保留真正执行的旧source hash。

不把原始数据/新生成逐条结果stage到公开Git。所有原始run保留本地，并用`project_public_results.py`生成经独立逐数核对的无membership聚合投影。

## 5. 干净Kernel执行Notebook

```bash
OPENBLAS_NUM_THREADS=1 JUPYTER_PATH=.venv/share/jupyter .venv/bin/python -m task2.scripts.execute_notebooks 'task2/notebooks/作业2_运力调度_完成版.ipynb'
OPENBLAS_NUM_THREADS=1 JUPYTER_PATH=.venv/share/jupyter .venv/bin/python -m task2.scripts.execute_notebooks 'task2/notebooks/实验3_多目标与强化学习派单_完成版.ipynb'
```

交付Notebook包含真实运行输出，基础7/7、进阶10/10代码Cells。进阶实际运行五seed核心EA和300回合RL；完整扫描汇总明确从有效索引读取，读取旧run不冒称重新训练。Notebook生成器可只依赖公开teacher starter，不要求根目录数据ZIP；重生成将清空输出，只在工作副本执行。

## 6. 只用公开聚合输入重画图

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m task2.scripts.build_figures
OPENBLAS_NUM_THREADS=1 .venv/bin/python task2/scripts/build_evolution_figures.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python task2/scripts/build_rl_figures.py --final
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m task2.scripts.build_diagrams
```

公开MOO投影含F/history/共同界和预算，RL公开模型/均值/网格计数/时间计数足够精确重画，独立临时目录已验证PNG字节一致。若从新实验原始输出重建RL绘图聚合，显式加`--prepare-data`；不要用旧聚合混合新实验。正式在线主图的输入为纯合成公开原件，proxy时段图只读公开汇总指标。各图sidecar保存真实输入、绘图源码及公共P2色源hash。

## 7. 报告和源包

```bash
.venv/bin/python -m task2.scripts.generate_report_tables
.venv/bin/python -m task2.scripts.build_reports
```

后者强制从真正XeLaTeX源重编译，检查最终log/引用/字形/overfull，提取全文并逐页200dpi渲染；脚本不伪造视觉PASS，实际逐页检查另存receipt。只编译源包时也保持其中的相对目录（task2及templates颜色源）；不需要原始签到数据。字体不在包内。

2026-11-06 当前 Process 已替换为用户认可的 16 页正式 PDF，保留原生 UI、TikZ 箭头与任务源码；原 8 页交接稿及旧源包保留历史配对。只检查当前 Process 时执行：

```bash
.venv/bin/python -B task2/scripts/build_reports.py --kind process \
  --evidence-dir task2/reports/process/build/recheck
```

该分支隔离编译并保留正式 PDF；即使比较失败也不覆盖。实测编译返回 0、页数和全文一致，但 200 dpi 像素未全部相同，严格完整命令仍返回非零。环境级字重修复与残余限制见 [Process 构建说明](../reports/process/README.md)。未新增全局字体配置或安装依赖。发布到 GitHub、网页 GPT 二审、UI 实际上传、用户理解验收及教师 Submission 分开记录。
