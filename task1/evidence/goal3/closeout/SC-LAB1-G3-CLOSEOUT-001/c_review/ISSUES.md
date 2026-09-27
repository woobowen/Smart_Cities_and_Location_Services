# 独立 C 收尾问题与复验记录

C 上下文：`/root/c_independent`。仅写本审核目录，没有编辑报告正文、处理代码或数值结果。以下首轮观察为历史记录，表内 OPEN 为当时状态；当前状态以末尾追加复验表为准。修复由主线程/B完成，关闭依据重新读取的产物。

| ID | 对象与观察 | 影响与要求 | 当前状态 |
|---|---|---|---|
| C-01 | `task1/goal3/package.py` 新包顶层 `submission_status=NOT_SUBMITTED`，嵌套 assignment 为 `NOT_READY`；当前 Prompt 要求 Submission 为 NOT_READY。 | 统一新包的当前提交门槛状态，未发送事实另行保留；不得改旧包。 | OPEN |
| C-02 | 本轮 `citation_access_receipt.json` 已登记 Cawley 全文指定章节核读，Experiment 两处和 BibTeX 仍写本报告只读摘要。 | 将当前引用的支持范围与本轮实际核读一致绑定，历史阅读层级不可追溯升级；不称整篇全文逐行核验或复现。 | OPEN |
| C-03 | `a_diagnosis/TEACHING_DIFFERENCES.md` 多个相对链接从实际目录解析到不存在目标，如 `../../../goal1/...` 和 `../../../../../../docs/goal2/...`。 | 修复新增导航相对层级，实际 resolve 检查，不能以文件存在于别处代替链接可达。 | OPEN |
| C-04 | Process 的过程材料表含“本轮加密 native 消息”措辞。 | 无助于报告读者且引入底层实现细节；建议改为缺失的完整历史原始聊天来源，保留真实性边界。 | OPEN |

首轮冻结与身份核验：7 个启动保护文件、32 个 processing source 与数值提交及冻结哈希、132 条合同绑定、2 本 Notebook 身份与执行默认值、重复身份生成全部通过。见 `frozen_identity_receipt.json`。该检查不等于 PDF 目视、解压 FULL、用户理解或 Evidence Lock。

| C-05 | OPEN | 当前 Experiment PDF 物理页20表14末行，策略观察 22,772 与秒 1763.6 列间距不足，视觉连成连续数字；200dpi原尺寸逐页目视发现。 | B调整表格列间距/尺寸，重建报告及包，C查看新页后关闭。 |

## 已实际复验的当前状态

| ID | 当前状态 | 独立复验范围 |
|---|---|---|
| C-01 / CL-C01 | CLOSED | 源码和实际包顶层/嵌套 NOT_READY，sent_to_teacher=False；CL-C01_closure.json 绑定22项B测试与C静态包检查，主线程已按Journal恢复父任务。 |
| C-02 | CLOSED（内容源）；变页目视在最终PDF统一登记 | 已重新读取正文、结语、BibTeX和定点访问回执；明确“上一版报告”摘要层与更早研究/本轮指定段核读分开。 |
| C-03 | CLOSED | 本上下文独立解析所有教学差异表本地链接，全部目标存在；详见 issues_01_04_recheck.json。 |
| C-04 | CLOSED | 源码新措辞及Process物理第3页200dpi原尺寸实际目视一致。 |
| C-05 / CL-C02 | OPEN，B修复中 | Experiment物理第20页表14末两列需拉开，等待重建后C实际目视。 |

追加回执只关闭所述问题，不把尚未完成的Notebook/最终包/全部视觉或外部证据纳入PASS。

最终PDF复验追加：C-05 / CL-C02 **CLOSED**。最终Experiment物理20页已实际原尺寸重看，末两列清楚分离；21页引用层级措辞已实际重看。Process10–12完成首次目视。当前22+12页全部视觉覆盖，见 `visual_content_receipt.json`；新PDF哈希已绑定，旧29个不变页以同PNG字节继承本上下文真实目视。`CL-C02_closure.json`可由主线程关闭Journal并恢复父任务。
