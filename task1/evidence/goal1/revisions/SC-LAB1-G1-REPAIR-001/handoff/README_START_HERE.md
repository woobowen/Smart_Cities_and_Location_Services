# Goal 1 二重验收与定向修复交接包

1. 用户先阅读 `GPT_SECOND_REVIEW.md`；完整Codex任务为 `SC-LAB1-G1-REPAIR-001_CODEX_PROMPT.txt`（与MD同文）。
2. 将本包解压至本机独立目录，向Codex提供实际目录并发送完整提示词。ChatGPT的sandbox链接不能自动成为Codex本机路径。
3. `research_inputs/`是此前缺失的真实历史研究文件，可按提示词归档；不是新实验，也不是全部论文实现清单。
4. `probes/reproduce_repository_findings.py`可针对实际仓库运行，所有模型/进程调用被测试替身禁止；before/after分别保存，不覆盖旧结果。
5. `source_snapshot/`只供审核回看，是连接器获取并核对Git blob的旧代码片段集合，不是完整Git checkout，严禁直接覆盖当前工程。
6. `probes/results.json`、`provider_results.json`来自本轮GPT真实独立探针。其中被测provider函数可能生成内部LIVE_CALL_ATTEMPT标签，但外围明确ENGINEERING_TEST，实际网络、模型调用均为0，不能纳入真实模型运行统计。
7. `portable_probe_snapshot_results.json`针对非Git源码快照执行，因此checked_commit为unavailable；快照与固定提交的绑定依据为verified_blobs.json，不能把它说成完整仓库测试。
8. `figures/goal1_loop.png`为已核对远程SVG在GPT环境中的复核渲染，不是Codex原PDF的重新验证或新的正式制图。
9. 继续Goal1，不进入Goal2/3。CRS事实和去噪方法批准仍需要证据/真实确认，不能由Prompt的存在自动产生。
10. .venv和临时CLI先保留，不在本次修复前清理。

本包不含原始坐标数据全文、字体、认证文件或第三方论文全文。
