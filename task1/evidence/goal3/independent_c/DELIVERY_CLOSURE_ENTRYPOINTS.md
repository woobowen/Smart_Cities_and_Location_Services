# Notebook 与 package 独立闭合入口

此入口只合并已真实完成的独立回执、核当前字节和实际 Journal 提交，不执行 Notebook，不产生新轨迹处理或模型调用。隔离 basic 尚未完成时只能输出 `PREPARATION_ONLY_NOT_PARENT_ACCEPTANCE`；`--mode accept` 必须拒绝。

## 1. 隔离 basic 完成后的单项审核

保留实际解压根、WORK 和新内核证据。完成后由 C 运行既有入口：

```bash
.venv/bin/python task1/evidence/goal3/independent_c/review_full_notebook.py \
  --project-root /tmp/sc-lab1-g3-submission-isolated \
  --executor-source "$PWD/task1/goal3/execute_notebook.py" \
  --evidence task1/evidence/goal3/notebook_verification/isolated_basic_full_01 \
  --input-notebook task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb \
  --target-id isolated_package_basic_full \
  --output task1/evidence/goal3/independent_c/isolated_package_basic_full_receipt.json
```

必须是真实 12 个 code cells、9720 历史候选、19 构造处理、246 pilot、11386 原始记录/1173410 点、22772 实际生产处理与 285 个新分片；不能使用 smoke 或静态 ZIP 结果代替。该程序检查实际保留产物，不重跑处理算法。

## 2. Notebook 父任务

单项 C VERIFIED 后刷新精确提交集，使用新文件名保留旧准备结果：

```bash
.venv/bin/python task1/evidence/goal3/independent_c/prepare_delivery_submission.py \
  --task notebooks \
  --output task1/evidence/goal3/independent_c/notebooks_submission_ready.json
```

只有 `ready_for_actual_submission=true` 且 `blockers=[]` 才可提交。主线程将该 JSON 的 `targets` 路径与 `source_hashes` 原样传入 `Journal.submit('notebooks', paths, sources)`；不要把准备文件自身或新目标临时加进集合。C 随后运行：

```bash
.venv/bin/python task1/evidence/goal3/independent_c/prepare_delivery_submission.py \
  --task notebooks --mode accept \
  --output task1/evidence/goal3/independent_c/notebooks_closure_receipt.json
```

程序要求实际 task 为 REVIEW_PENDING，当前提交 targets/source 与重新独立合并集合完全一致。主线程再实际 `Journal.accept('notebooks', receipt_path, '/root/c_protocol')`。

## 3. package 父任务

Notebook 已实际接受后生成 package 的精确提交集；两份报告可且只能因 META_DEPENDENCY / EVIDENCE_MASTER_DEPENDENCY 为 BLOCKED_EXTERNAL，已可完成的工程必须 VERIFIED。

```bash
.venv/bin/python task1/evidence/goal3/independent_c/prepare_delivery_submission.py \
  --task package \
  --output task1/evidence/goal3/independent_c/package_submission_ready.json
```

主线程按同一规则实际 `Journal.submit('package', paths, sources)` 后，C 运行：

```bash
.venv/bin/python task1/evidence/goal3/independent_c/prepare_delivery_submission.py \
  --task package --mode accept \
  --output task1/evidence/goal3/independent_c/package_closure_receipt.json
```

预期合法终态仅是 `BLOCKED_EXTERNAL`，同时 `available_engineering_status=VERIFIED`、`package_status=REVIEW_ONLY`、`Submission=NOT_READY`。这是待审包工程闭合，不是可直接提交的正式包，也不执行邮件或教学平台提交。

## 稳定绑定规则

- 合并仓库两个 FULL、同一 ZIP 隔离两个 FULL 的独立回执及当前本地 targets/source；缺少任一 FULL 必须拒绝。
- 包内原始输入逐项对应实际 source closure 的 112 个成员、真实 ZIP 的 hash、manifest、解压和两个实际 launch。外部目录对象由独立 FULL 回执和 archive binding 明确绑定，不把仓库同名文件冒充它。
- 仓库 clean source→执行版→canonical 字节推广，以及同一 canonical→包输入→隔离执行版分别登记。处理数值源 e12、仓库 Notebook 执行时 Git 0b20、无 Git 的 FROZEN_SOURCE_BUNDLE 身份不同，32 个处理源码字节相同。
- 旧 NB01 repair/smoke 与旧 static preflight 保留原范围，不改写为当前 FULL。包构建回执中的 `NOT_RUN_BY_BUILDER` 继续是当时事实。
- `goal_state`、requirements、FINAL_RESPONSE、PUBLICATION_RECORD、REVIEW_PACKET、治理事件/资源当前索引不进入固定 targets。依赖状态以实际读取时间和不可变 C 回执观察记录；不会制造自引用关闭环。
- report 的完整页面目标由其独立父任务保留；此入口复核其当前实物哈希与 C 绑定，package 直接绑定依赖回执和实际 PDF/ZIP，不重复扩充一套页面审查。
- 最终内部总验收、实际 GitHub push 与远程回读分别执行，任何准备文件均不代表已经完成它们。
