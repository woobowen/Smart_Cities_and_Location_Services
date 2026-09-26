# A 发布前只读范围核对

状态：**保护与治理检查通过；最终文档和入口仍待生成后复核。** 本检查不重算核心数值、不替代 C 总审查，不判定 G1 已完成。

检查时间：`2026-09-26T17:09:31.853417+00:00`。当前 HEAD：`f229d9a4113bcc0dd763e1b410f1f5fb73903a62`。初始锚点来自 [workspace_initial.json](../workspace_initial.json)，为 `7e6cd4082c2cdad2452fa5a1006e99dcfb050d17`。机器结果见 [release_scope_check.json](release_scope_check.json)。

## 受保护文件

本轮初始 hash 表共有 **273项**：272项一致，改变的1项仅在获准更新的当前 requirements/acceptance/REVIEW_PACKET 三入口范围内；未授权改变0、缺失0。两个用户原有 untracked ZIP 均保持原hash且仍未跟踪。

该初始表不含教师/raw/templates/plots。为避免用不完整清单声称全保护，本次额外从**已记录初始 Git commit**取原字节逐文件比对；未更改或新造保护清单：

| 初始提交内类别 | 文件数 | 结果 |
|---|---:|---|
| plots_zip | 1 | 字节一致 |
| historical_results_figures | 11 | 字节一致 |
| teacher_materials_starter_raw | 106 | 字节一致 |
| templates | 26 | 字节一致 |
| installed_plots_skill | 6 | 字节一致 |

共150项全部字节一致，含原始教师JSON、作业ZIP、PPT、starter、模板、未触及的绘图ZIP和已安装Skill，以及旧results/figures。原始实验数据和旧失败/调用ledger未被覆盖。

## 授权治理与11文件分发

相对初始提交：AGENTS 仅新增23行、删除0行；Research Protocol 仅新增13行、删除0行。内容限于已批准持续修复/恢复和明确授权条件化分析规则；完整实际diff在JSON中单独保存。Interaction Evidence Protocol与Visual System字节未变。

实际命令：

```bash
.venv/bin/python evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py --check
```

返回码0：`UPLOAD_BUNDLE_CONTENT: PASS; EXACTLY 11; internal manifest verified`。沿用既有allowlist，11个普通文件的active/bundle字节及hash一致；publication-plots原ZIP固定hash通过，6个effective members与installed source一致。仅证明仓库 **UPLOAD BUNDLE READY**，未声明ChatGPT UI已上传。

## 当前文档

先前 `geometry_notes.md` 将当前真实处理错误写成D2/CRS未决而阻断，且称去噪总是抛MethodUnresolved；主线程已在本次检查中修正，A再次读取后确认关闭。当前技术说明区分D2已批准、source datum UNVERIFIED和授权条件化分析；54项旧测试明确为历史。

两本新Notebook的**源文本**均正确说明条件化真实处理、默认RECOMPUTE/零新模型调用、G2/G3不提前执行。A没有运行Notebook；当前保存执行计数仍为0，最终新内核运行证据待主线程生成。

requirements 曾存在逐项 current_work/blocking_ids/future_acceptance 的旧口径；主线程在本次检查期间将其迁入明确历史字段，并填写当前 native 角色、条件化链和实际证据。最终静态读取未发现此前报告的逐项矛盾，检查时的文件 hash 与当前 authority snapshot 见机器结果。其实际运行与图表证据仍须由 C 总审查核对，不能仅由字段文字证明。**不要求新 datum 审批，也不把 datum 未知判成整体 Goal 失败**。

## 最终入口定点复核

README当前示例指 `g1-complete-pilot-03`。最终有效运行正在重建，REVIEW_PACKET/acceptance尚待新产物和内部审核后更新，因此本次只记录待复核，不运行或复算该例，不借旧入口作最终结论。

发布前需定点核对：最终run与CODE_SHA/合同/输出绑定；两Notebook实际执行及图一致；requirements 引用与最终证据一致；当前唯一REVIEW_PACKET与acceptance；实际push和remote SHA。先前被拒绝/失效run应保留且标明，不覆盖成成功。

A本次仅新增这两份检查报告，未改任何待审文件、保护表、治理、合同、代码、Notebook或旧证据，未新增环境依赖。未知source datum仍限制绝对定位/真实地面精度等结论，授权内的条件化处理继续。
