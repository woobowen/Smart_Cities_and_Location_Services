# 独立 Notebook FULL 审核入口

此文件提供 C 审核命令，不是执行回执。检查器只接受已经完成并保存
`execution_receipt.json` 的真实新内核运行；RUNNING、FAILED、前缀 smoke
均不能通过。它不重新启动 Notebook，也不运行轨迹处理算法。

## 仓库 basic FULL

待 `repository_basic_full_02` 实际结束、并将执行版原字节推广至正式路径后：

```bash
.venv/bin/python task1/evidence/goal3/independent_c/review_full_notebook.py \
  --evidence task1/evidence/goal3/notebook_verification/repository_basic_full_02 \
  --input-notebook task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb \
  --source-git-ref 0b20be8e4142e8e62246e9357993e83951833e4f \
  --target-id repository_basic_full_02 \
  --output task1/evidence/goal3/independent_c/repository_basic_full_02_receipt.json
```

核查 12 个实际单元、9,720 个历史参数/顺序记录—候选配对、19 条构造
处理链、25 项历史已知答案检查、pilot 246 的 108 点演示及其真实图。
全量部分从该次 WORK 实际读取 285 个新分片，核对 11,386 个有序记录、
1,173,410 个原始点、22,772 次真实处理、每个点的终态、新图逐记录数据、
实际生产参考分片字节哈希。缓存重核数必须为 0，parent_cache 必须为空。

原 NB01 修复回执是当时源文件/前缀 smoke 的历史凭据；正式输出推广后，
本检查器另行证明 Git 源字节和全部源码单元不变，并绑定当前执行版和
canonical 哈希。旧 smoke 不覆盖新 FULL 产物，也不因输出增加而否定修复。

## 解压 ZIP 的两次 FULL

先由执行线程对真实 ZIP 安全解压到新目录，再分别在两个新的 WORK
目录中以该解压根为内核 cwd 完整执行两份 Notebook。证据保存在仓库
`notebook_verification/` 下的独立目录。不能借用仓库的原始数据或生产缓存。

以下变量只是明确传入实际目录；不推断目录，不创建或删除执行结果。

```bash
REVIEW_ROOT="$PWD"
EXTRACTED_ROOT="<actual-new-extracted-root>"
BASIC_EVIDENCE="<actual-basic-isolated-evidence-directory>"
SYSTEM_EVIDENCE="<actual-system-isolated-evidence-directory>"

.venv/bin/python task1/evidence/goal3/independent_c/review_full_notebook.py \
  --project-root "$EXTRACTED_ROOT" \
  --executor-source "$REVIEW_ROOT/task1/goal3/execute_notebook.py" \
  --evidence "$BASIC_EVIDENCE" \
  --input-notebook task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb \
  --target-id isolated_package_basic_full \
  --output task1/evidence/goal3/independent_c/isolated_package_basic_full_receipt.json

.venv/bin/python task1/evidence/goal3/independent_c/review_full_notebook.py \
  --project-root "$EXTRACTED_ROOT" \
  --executor-source "$REVIEW_ROOT/task1/goal3/execute_notebook.py" \
  --evidence "$SYSTEM_EVIDENCE" \
  --input-notebook task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb \
  --target-id isolated_package_system_full \
  --output task1/evidence/goal3/independent_c/isolated_package_system_full_receipt.json
```

外部 executor 仅启动内核和保存证据；它不是包的数值依赖。独立检查要求：

- execution receipt 的 cwd 等于实际解压根，原输入 Notebook 字节匹配，全部
  源码单元与执行版完全一致；每次 WORK 位于工程之外且初始为空。
- ZIP 所声明的原始成员字节保持不变；raw、配置、只读记忆和冻结的 32 个
  数值源码均来自解压包。G2 summary 的唯一路径元数据变换由包审核另核。
- 无 `.git` 时，生产代码身份是 `FROZEN_SOURCE_BUNDLE`，绑定已发布处理
  源码 hash，不冒称临时目录具有真实 Git HEAD。
- 额外的 `python -I -B` 只读导入检查核验所有实际导入的 `task1.*` 模块都
  位于解压根，并核对合同、生产门控和 raw hash。该检查执行 0 条轨迹，不能
  替代已经完成的两个 FULL 内核。
- Notebook 两个已登记 Provider 入口均实际拦截，attempts 为 0；不存在读取
  历史汇总代替 raw 重算的路径。隐藏底层请求和费用仍按既有口径 unknown。

外部包成员在回执中单独列为 `external_checked_files`，不会伪装成仓库同名
文件的 Journal target。最终 package 闭合仍须绑定实际 ZIP、其精确成员清单、
两次执行证据及独立 C 回执。只有 system 的回执不能关闭 notebooks 或 package。
