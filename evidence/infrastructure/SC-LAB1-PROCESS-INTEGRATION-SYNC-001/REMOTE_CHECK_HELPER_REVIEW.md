# 远程回读辅助脚本：独立修复复验

**结论：本次辅助脚本最小修复通过独立审查。** 审查上下文为 `/root/independent_review`，只读检查生产内容；仅新增本记录。被审工作区 `verify_remote.py` 的 SHA256 为 `4beec09ec05d31c8ec529b0f9813579f7457962801bad7034f301c3f0e2d679e`，比较基点为首轮回执提交 `4c3ff72229eca0f451384f494514310b082dc388`。本记录不覆盖先前 [INTERNAL_REVIEW](INTERNAL_REVIEW.md) 或首次 [PUBLICATION_RECEIPT](PUBLICATION_RECEIPT.json)。

原复用路径使用 `git fetch --depth=1 origin refs/heads/main:refs/heads/main`，更新隔离对象库的本地 main 时遭遇 non-fast-forward，exit 1。修复仅把复用路径改为无目标分支的 fetch，然后读取 `FETCH_HEAD`。首次 fresh clone 的实际 clone 命令保持原样，仍读取克隆生成的 `refs/heads/main`；未增加 force、fallback 或放宽校验。

本上下文实际读取完整脚本及 diff，执行 Python AST 语法解析，并逐字串比较修复前后的校验代码，确认：

- fetch 前的直接 `ls-remote`、`--expected-sha` 与独立用户输入基准读取完全未变。
- 复用对象库仍要求 origin 精确等于指定 GitHub 仓库，仍禁止本地 object alternates；网络 fetch 必须成功。
- `observed == expected_sha` 及其后全部验证代码逐字节未变：精确 manifest/release 成员集合、manifest hash 对用户基准、普通 Git blob 类型、逐文件真实字节 SHA256、LFS 指针拒绝、最后再次 `ls-remote` 均保留。
- `subprocess.run(check=True)` 与旧回执拒绝覆盖保持；任何失败均不能进入新 PASS 回执写入。

另只读检查实际隔离对象库：没有 `remote.origin.fetch` 配置（查询 exit 1、无输出）；当时本地 `refs/heads/main` 仍为工程内容提交 `e1fb621aa40acc167f4ed84c0c7992a5ff0a4abe`，`FETCH_HEAD` 已为 `4c3ff72229eca0f451384f494514310b082dc388`。这与改动的目的相符：读取本次网络获取的提交，同时保留原本地分支。

**真实 CLI 回归由主线程 `/root` 执行。** 本上下文读取 [REMOTE_CHECK_HELPER_FIX.json](REMOTE_CHECK_HELPER_FIX.json) 中完整 `actual_fixed_cli_verification`，并与私密目录实际 CLI 输出文件逐项比较，二者完全一致。回归使用 `--reuse-network-store --expected-sha 4c3ff72229eca0f451384f494514310b082dc388`，exit 0；fetch 与 `rev-parse FETCH_HEAD` 均 exit 0；直接远程前后 SHA、fetched SHA 一致。实际集合为 15 项、active/release 共 30 个路径实例。随后本上下文再将回执的每个 `(canonical_name, role, sha256)` 与独立转录的用户基准核对，精确 30/30 匹配。本上下文未声称亲自重新运行联网 CLI。

独立检查还确认：工程内容提交与首轮回执提交之间只改变四份回执/交接文档；旧 INTERNAL_REVIEW 和首次 PUBLICATION_RECEIPT 与首轮回执提交仍同字节。当前辅助脚本修复不改变报告、科学实现、来源清单或 release。下一小提交将包含验证 helper 与追加回执/审查记录，最终交接须明确这一差异范围，不能称最终 HEAD 相对工程内容仅含纯文档回执。

本审查绑定上述辅助脚本字节和已经完成的 `4c3ff72…` 实际回归；后续最终提交仍由主线程按同样门槛实际回读。网页 GPT 二审保持 **PENDING**；教师提交保持 **NOT_PERFORMED**。
