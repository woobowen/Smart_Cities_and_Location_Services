# Goal 3 内部总验收入口

此入口不创建新研究任务，不重算方法，也不自动修改 Journal。
`prepare` 只给出实物核对和未闭合项；只有 `accept` 在当前精确提交上实际
通过，才产生可由主线程消费的 `internal_acceptance` C 回执。

## 固定判据

- 从真实 raw 重新读取记录与点数，核对批准的 raw/contract/split SHA。
  当前有效运行、冻结、C 回执、分片、图表、两报告、Handoff 和 ZIP 都按
  实际文件字节与版本核对，不以 requirements 的 PASS 代替证据。
- 全部 15 个前置任务必须真实闭合；所有工程 issue 必须经过实际 B 修复和
  独立 C 回执消费。报告与 package 仅允许 `META_DEPENDENCY`、
  `EVIDENCE_MASTER_DEPENDENCY` 导致 `BLOCKED_EXTERNAL`，且可完成的
  engineering 必须为 VERIFIED。Notebook/处理/ZIP 技术失败不属外部缺项。
- 必须有仓库 basic/system 与同一真实解压 ZIP basic/system 四次 FULL
  的独立回执。局部 smoke、启动成功、已有输入输出哈希都不能代替 FULL。
- 当前工作回归必须确为 469 个通过 testcase 节点和 10 个通过 subtests
  （suite 总计 479），且实际被测数值/辅助源码哈希仍相同。
- 数值生产 CODE 为 `e12f8a27944210adb452730be92a0674dfc6b84b`；仓库
  basic FULL 实际运行 CODE 为 `0b20be8e4142e8e62246e9357993e83951833e4f`。
  两个 commit 中 32 个数值源码逐字相同。无 `.git` 的包使用冻结的
  `FROZEN_SOURCE_BUNDLE` 身份，不冒称拥有本地 Git HEAD。
- 正式内部验收前必须完成真实独立发布预检：diff、secret scan、大文件、
  原件保护、local links。回执 `target_id` 为 `publication_preflight`，
  `checks` 对上述五项使用 `diff`、`secret_scan`、`large_files`、
  `original_protection`、`local_links` 键，并记录实际结果；只有全部 VERIFIED
  才可通过。它必须用 `candidate_manifest_path` 和 `candidate_manifest_sha256`
  绑定实际稳定待发布文件清单 `files: [{path, sha256, ...}]`。该回执必须来自
  已登记真实独立 C 上下文，并包含实际 targets/source_hashes/checked_components。

## 准备与提交

```bash
.venv/bin/python task1/evidence/goal3/independent_c/review_internal_acceptance.py \
  --mode prepare \
  --prepublication-receipt '<actual-independent-prepublication-receipt>' \
  --output task1/evidence/goal3/independent_c/internal_acceptance_ready_inputs.json
```

若仍有未完成项，输出保持 `PREPARATION_ONLY_NOT_ACCEPTANCE` 并列明阻断。
`suggested_stable_targets` 是当前实际逐字核对的稳定文件并集；
`suggested_source_hashes` 包括前置任务的全部当前源码与本独立入口。
主线程完成缺项后重新运行准备，不能使用较旧准备结果盖过新产物。

全部前置任务闭合后，主线程先将当时真实 `goal_state.json` 原字节复制为
新的 `internal_acceptance_submission_snapshot.json`，再实际
`Journal.submit('internal_acceptance', ...)`。提交对象包含上述完整稳定
targets、这份已发生状态的不可变快照和完整 source hash map。

随后 C 实际运行：

```bash
.venv/bin/python task1/evidence/goal3/independent_c/review_internal_acceptance.py \
  --mode accept \
  --snapshot task1/evidence/goal3/internal_acceptance_submission_snapshot.json \
  --prepublication-receipt '<actual-independent-prepublication-receipt>' \
  --output task1/evidence/goal3/independent_c/internal_acceptance_receipt.json
```

快照中的全部前置 task、issues 与当前 Journal 必须一致，events 必须是
当前真实事件链的前缀；不能用编辑后的摘要代替实际快照。C 不运行
Journal.accept，由主线程消费真实 C 回执并恢复父任务。

## 发布与无自引用版本记录

`goal_state.json`、`requirements.json`、`FINAL_RESPONSE.md`、
`PUBLICATION_RECORD.json`、`REVIEW_PACKET.md`、当前资源/治理索引是持续
收尾文件。它们在本次 gate 作为当前事实读取，但不与未来状态互相作为
固定 hash target；需要保存时使用上述已经发生的不可变快照。
发布预检的稳定 candidate manifest 也不能包含这些未来还要更新的字段。

内部 C 通过只允许发布明确的 `PARTIAL_BLOCKED` 审查检查点，不把缺姓名、
Evidence Master 原始材料/spec/LOCK 的两报告和包称为完全可提交。
技术/研究结论与缺项分别报告。A19 在实际内部回执被消费后更新；A20 只有
真实 push、Local/Remote 核对和固定 SHA 文件回读后才更新。

发布后的真实记录、最终 A–I 回应和导航进行独立 publication 核查；
已经发生的 ARTIFACT_SHA/远程检查可以写入文件，文件不能预先声称其自身
尚不存在的 commit SHA。最后聊天报告实际最终 HEAD，避免 Git 自引用循环。
后续收尾内容改变不倒写此前数学 CODE/报告运行身份。

网页 GPT_SECOND_REVIEW 始终 PENDING，Submission 始终 NOT_READY，
Understanding 由用户决定。本 C gate 不发送邮件、不提交平台、不作 Evidence LOCK。
