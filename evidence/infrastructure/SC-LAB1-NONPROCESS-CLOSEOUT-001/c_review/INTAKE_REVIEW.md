# C 接收与范围核验

身份：独立上下文 `nonprocess_c`；未参与作者导入、清单、导航或同步器修改。当前阶段为接收核验，**不是 NC01–07 最终意见**。

- 已先执行 `ls -la`，随后全文读取批准 Prompt、起始 active AGENTS、received 中五份完整输入。大输出显示截断处已单独重新展开全文。
- 独立核对五份输入大小 / SHA256 与 Prompt 全匹配，received 与当时 release 字节相同。
- 独立从 Git 对象 `89371f6597f92f7dac9abf61f6f6b18e29ed76cc` 取回五份 active 源，四份保持相同，只有 AGENTS 存在本轮授权差异。
- 本轮非 Process 收尾允许独立关闭；Process 仍为整体必需交付并由指定另一对话负责。作者检查 / C / 历史网页 GPT / 当前新提交外审、UI 同步和教师提交状态分别判断。
- 原二审附件尚未独立接收；Prompt §5 允许按 `USER_RELAYED_PRIOR_REVIEW` 承接结论，不允许伪造原件或新测试。最终判断待检查作者归档。
- 已全文阅读同步器及唯一清单。独立异常探针将使用唯一临时目录，实际库只作只读检查。
- 已读取起始保护清单，含 6,679 项，约 2.15 GB。一次运行中作者正在正常更新 AGENTS、清单、同步路由和迁移 OS sidecar；因此本次变化列表仅为过渡观察，不是最终保护失败。
- 该过渡观察脚本先用 `exists()` 判定，因而把既有 dangling symlink 误标为 missing。最终核验须按 `is_symlink()/lstat` 先处理，不能据此认定历史文件被删除。
- 未编译 PDF、重建 ZIP、运行数值 / 模型实验、修改 Process 原件、安装或清理任何依赖。
- 具体命令、cwd、退出码见 [command-log.json](command-log.json)。最终报告将绑定终版 hash 并重新核验保护范围。
