# 交付文案事实核对

本次 A 只读核对绑定 2026-09-26 21:47:11 UTC 截取的三份交付文档；字节原件保存在 `.md.source.txt`，不作为第二套活动 Markdown。结论为 **FACTUAL_CHECK_PASSED_WITH_NONBLOCKING_COMPLETENESS_NOTE**：131 项实际检查通过，没有发现数值、分母、null 比较、因果记忆收益或真实质量/最优性过度结论。

完整 [回执](receipt.json) 保存三个截取 SHA、检查值、可信输入哈希和实际检查边界。此检查没有重新计算原始轨迹，不替代独立 C 的 A01–A17 总验收，也不核实未来发布或后续文案修订。

唯一非阻断建议是补充正式阶段的负结果：467 条合法且执行的模型原始提议中，另有 2 条出现共同覆盖身份损失，均未被锁定为输出。原稿已经用 DEVELOPMENT 的真实提议解释了这种风险，但未明确写出这两个正式实例。

| 记录 | 模式与 episode | 原始提议 | 覆盖身份 | 最终锁定 |
|---|---|---|---|---|
| 3420 | llm+memory+search，e1-b2，round2 | 3420-r2-b | 127 → 111，丢失16 | 保留 reference，非工程 fallback |
| 955 | llm+memory+search，e3-b2，round3 | 955-r3-a | 100 → 99，丢失1 | 保留 reference，非工程 fallback |

[精确证据](formal_eval_tradeoff_witnesses.json) 包含两条原始提议原话、response/episode/trace/lock 路径及 SHA、丢失的原索引和锁定原因。两者在完整基线已覆盖集合上的误差为 `null`，原因为 `BASELINE_COVERED_IDENTITIES_LOST`；各自覆盖集合的较小最大误差不能视为几何改善。它们是合法探索的实测权衡，不是非法动作、幻觉或真实噪声质量错误。主线程已获建议，不需要改变冻结实验或补跑模型。

其余重点已核对：59/14配置、6/2顺序、15,721次注册处理、39表111,053行及哈希；三个单项及53/120的支持范围；四模式的72个记录—episode分母、467条提议、185条可评价预测；记忆72次检索与181个记录级回合；84/15/1次可见 CLI 调用的分账；316项测试、三 Notebook 的21代码单元和17,401次确定性复算；11图44份导出；坐标范围和已执行阈值检查。原稿明确保留未知 datum、条件化覆盖、有限搜索、无增益、危险顺序和记忆因果收益未证等限制。

三个用户 ZIP 的字节哈希均与启动记录一致。当前只有 COMPLETE 与 CLOSURE 两份未跟踪；REPAIR ZIP 已在 G1 历史提交跟踪，不能根据启动 JSON 的字段名称推断三份都未跟踪。

实际命令：

```bash
.venv/bin/python task1/evidence/goal2/a_epoch02/final_handoff_check/check_handoff.py
```

新增模型调用、候选评估、记忆写入均为0。未修改待审三份原稿、分析生成器、冻结合同、处理源码或已绑定实验产物。
