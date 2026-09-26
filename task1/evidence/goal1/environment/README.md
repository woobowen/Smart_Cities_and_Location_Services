# 环境、权限与真实模型诊断

系统 Python 3.12.3。首个命令为 `ls -la`；初始 main 工作区干净，origin/main 与本地均为 `b25efc153311a967109c586edab39361326500c7`。[初始命令](initial_commands.json)保存 pwd/status/branch/脱敏 remote/log/HEAD/fetch 结果。

原目录没有现成 `.venv`、requirements 或容器执行入口。本轮创建项目 `.venv --system-site-packages`，安装 pytest、nbformat、nbclient、ipykernel 及依赖；没有系统包、字体或全局配置改动。完整新增包见 [installed_local_packages.json](installed_local_packages.json)，安装输出见 [install.txt](install.txt)，汇总见 [install_summary.json](install_summary.json)。项目依赖清单在 [requirements-goal1.txt](../../../config/requirements-goal1.txt)。

## 已实际测试的访问路径

只使用用户现有 ChatGPT 登录的 Codex CLI，模型请求为 gpt-6-astra（既有配置），没有读/复制认证文件，没有开启额外计费 API或新供应商。[provider_probe.json](provider_probe.json)保存旧版本、help、features和安全的登录状态类别。

1. 系统 CLI 0.147.0：实际 run01 被服务拒绝，提示当前模型需要更新客户端。
2. npm 官方 registry 隔离安装 `@openai/codex@0.157.1` 至 `/tmp/sc-g1-codex-0.157.1`；系统 CLI 未升级。见 [安装回执](codex_isolated_install.json)、[日志](codex_isolated_install.txt)、[实际版本](codex_01571_version.txt)。只对该子进程移除继承的 NODE_TLS_REJECT_UNAUTHORIZED 覆盖，并启用 strict SSL，未修改全局环境。
3. run02 新 CLI 返回完整结构化模型结果，但本轮解析器将主动禁用 code host 的固定提示判为失败，未派发工具。修复后保留旧失败，未追认成功。
4. run03 A成功，B因 `workspace routing discovery failed` 失败。B有9条可见 Reconnecting 通知和1条WebSocket→HTTPS fallback；底层请求数不可见，原预算计数不足。LIVE 已在合同和持久ledger冻结。

可见模型完成事件为2次（run02 A、run03 A）；被控制器接受并触发工具的是run03 A的1次。共4次CLI派发不能被写成仅4次底层网络请求。失败用量若事件未报告则 unavailable，金额不可知。

## 实际权限与修复边界

两版CLI read-only sandbox探针均拒绝向临时保护文件写入：[旧版](sandbox_probe.json)、[新版](sandbox_probe_01571.json)。角色运行在独立临时cwd；shell、code executor、apps/plugins、web、subagents等能力关闭，只返回schema JSON；工具由确定性控制器计算。角色不能修改数据、合同、审核代码或产物。

修复版恢复入口验证派发预算登记、请求hash、schema、可见完成事件、role/call/thread/usage、receipt与response的一致性，再密封文件hash；缓存复用核对既有登记，不接受自带hash伪造。超时/中断回收整个进程组。[独立审查](../tests/INDEPENDENT_CONTROL_REVIEW.md)和108项测试只证明这些离线工程边界；没有补造C调用或反馈闭环。

重试配置参考 [OpenAI Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)：request_max_retries、stream_max_retries、supports_websockets。代码添加每进程0重试/关闭WebSocket参数，但没有再次联网验证其对当前服务的实际作用；保持 LIVE BLOCKED。原官方入口 [noninteractive](https://developers.openai.com/codex/noninteractive/) 与 [multi-agent](https://developers.openai.com/codex/multi-agent/) 均已阅读，重定向分别为 [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) 与 [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。文档不能替代本机运行。

环境暂保留以便GPT复核。可清理对象为项目 `.venv` 与上述临时CLI目录；不自动删除用户账户状态或教师材料。
