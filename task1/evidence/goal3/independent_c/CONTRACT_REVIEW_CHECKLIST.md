# Goal 3 独立 C 合同检查入口

身份：原生 Codex 子角色 `/root/c_protocol`。只读核心实现、批准合同与待审产物；独立程序仅写入本目录。这里是审核记录，不是新的研究批准。

首次命令 `ls -la` 显示已有 `.venv`、`AGENTS.md`、`task1/`、`docs/`、`templates/`、`tools/` 及原有 HANDOFF ZIP。起始 `main` HEAD 为 `6fad8420b09ba123fe0658a5cd805cb7b7b9e67b`，两份 CLOSURE/COMPLETE ZIP 原本未跟踪，均未修改。

## 合同提交时必须固定

1. 直接用户授权原文及 hash；G1/G2 验收转交身份保留 `USER_RELAYED_GPT_STAGE_ACCEPTANCE`，不得生成网页审核证据。
2. 真实 raw 路径/hash，继承 G2 split/hash，完整记录/可信关联组的原子性；新分区互斥、覆盖、完整父范围。G3 开发允许已暴露的 DEVELOPMENT 与 G2_EVAL；旧结果保持历史身份。
3. selection 的既有描述层、240 条配额与 shortage 规则；final 在剩余完整组中等概率稳定 hash 抽取 600，采用独立 salt/seed 42。不能把等额分层抽样误写为等概率 final。
4. 最多 8 单项、12 组合、深度 3、两类有限结构策略、最多 4 冻结短名单；方向/DP 交互机会实际检查。没有可信机制则说明不纳入，不能把探索上限变成配额。
5. R0/S0 的完整六参数、顺序、D 一次同时删除、固定 ENU 模型、原始时间/单位、共同 raw 窗口、指标与 binary64 余量均继承真实有效 G2 定义。
6. 每记录分别相对固定 R0 和 incumbent 检查覆盖身份集合包含、原覆盖集 max 误差不退化、非空记录/窗口不丢失、原始断点跨越为 0；null 不算几何改善。
7. P 变体另与相同上游 dp=5 的完整 P 输入比较；实际误差预算仍为 5 工作米。改变 S/D 后，各自 clean 上省点率不能证明 P 改进。
8. 保存全配对/Pareto，至少一项超固定余量的严格收益才替换；不可比保持已通过 incumbent，等价按少模块/无新增在线模型/较低已测成本/canonical ID。
9. final 打开前冻结参数、方法/部署策略、代码、模式、记忆、比较清单及失败回退 R0。不能利用 final 反馈改参数或添加未评估的逐记录回退。
10. FINAL_CONFIRM 信息边界、只读记忆、episode 隔离；治理和被测记录级调用分账。固定模式 0 新记录级模型调用不能改称已验证 LLM/记忆质量收益。
11. 全量生产必须 final 后；全量低成本字段全检、独立数学重算预登记稳定抽样及全部实际类别代表；阈值敏感性明确全检/抽查边界。
12. code/contract/split/raw/source hash 绑定、修复使依赖产物失效、新 run 重建、独立关闭、父任务恢复；文档/身份/Evidence Master 缺项只阻断对应部分。

## G2 审核器复用边界

- `review_record` / `review_batch` 的可信 raw、expected parameters/order/provenance 必须来自待审候选之外。不能从 candidate 自己的 source_record 或参数字段提取“可信”参考。
- `g2_selection.compare` 对相同上游自动走 P 专项，只按省点计收益。G3 外层须显式组织 R0、incumbent、相同上游 dp=5 三种比较，不能以一次 compare 替代组合归因。
- 处理链审核使用候选外 oracle，但同一 `record_metrics` 被生产和审核复用；独立 C 的重点数学抽查须另用独立 raw 计算（可复用原 C-only Decimal/PROJ 程序），不能仅复读 B 的 VERIFIED。
- `g2_experiments` 的源码快照覆盖 workflow；新 Goal 3 应避免无必要改变旧模块致历史回放失效。发现实际错误时按影响范围修复与失效传播，不能以保持旧 hash 阻止必要修复。

当前仅完成承接/原件范围初查。新 G3 合同、split 和所有新方法效果尚未审核。独立 C 验证不是用户批准，不是 Evidence Lock，不是实验一最终验收。
