# 环境保留与恢复

沿用项目 .venv，未新增 pip/apt/字体/系统工具。当前依赖版本、Python 路径和 hash 见 environment.json / packages.json。

旧临时 /tmp/sc-g1-codex-0.157.1 在本轮开始时不存在，PATH 上是0.147.0。按历史记录恢复了 @openai/codex@0.157.1 及其 Linux x64 二进制包，没有升级或改全局CLI。安装日志 cli_restore.txt；运行时指定绝对路径，并同时校验 wrapper 与 native binary SHA256，不依赖PATH。保留目录不清理。

恢复命令（路径消失时使用相同版本，完成校验后再考虑经授权的新批次）：

```bash
env -u NODE_TLS_REJECT_UNAUTHORIZED npm install --prefix /tmp/sc-g1-codex-0.157.1 --ignore-scripts --no-audit --no-fund --strict-ssl=true --registry=https://registry.npmjs.org @openai/codex@0.157.1
/tmp/sc-g1-codex-0.157.1/node_modules/.bin/codex --version
/tmp/sc-g1-codex-0.157.1/node_modules/.bin/codex login status
```

本轮首次恢复命令显式 strict-ssl=true，但继承环境包含 NODE_TLS_REJECT_UNAUTHORIZED=0，日志产生警告。本轮没有设置该变量；发现后对后续子进程移除此覆盖，并通过启用证书校验的 curl 获取官方 registry integrity，独立核对 npm cache 的SHA512及已安装wrapper/native字节全部一致，见 cli_https_revalidation.json。没有以关闭TLS重试解决问题，也没有修改用户全局环境。初次urllib取源码/registry发生TLS EOF，随后使用保持证书校验的curl成功；失败不隐去。

只调用 login status 获取“Logged in using ChatGPT”，未读取、复制或上传 auth.json / token，未 logout/login，未改账户/付费API。官方当前文档用作接口背景，实际重试语义使用0.157.1 tag（commit 36650394…）源码和schema；见 provider_version_evidence.json。内置openai默认重试4/5、WebSocket true；同名provider覆盖不会生效，故已移除无效参数。首次可见错误停止不等于内部请求数精确为1或0。

旧budget_live.json与其live_stop原样保留；新授权批次使用固定budget_repair_001.json。禁止通过改run_id/base重置它。新运行结束后保留环境，等待远程审核；不进行额外环境清理。
