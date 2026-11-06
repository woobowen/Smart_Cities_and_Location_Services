# ChatGPT UI 操作交接：USER_UI_ACTION_REQUIRED

本文件是操作说明，不是第二份 active Project Settings，也不是 Project Source。正式上传目录为 `releases/chatgpt-project-sources/`，本地已核对恰好 12 项、20 条登记及 8 条 false，active 与分发字节/SHA 一致。实际 UI 是否完成只能由用户确认；此前用户报告上传过实验二 Process PDF 和源 ZIP，不据此推断当前 UI 文件名、哈希或去重结果。

1. 从批准入站包的 `PROJECT_SETTINGS_直接替换全文.txt` 取得 2026-11-06 全文，在 ChatGPT Project Settings 手动粘贴。该 TXT 只在仓库外私密保留，没有加入仓库 active 配置或 release。
2. 替换 UI 中四份规范为 release 中的 Evidence v2.9、Visual v2.8、Writing v1.4、AGENTS 2026-11-06。保留 Research v1.3 原文件、publication-plots 原包及实验一两份 PDF/配对源包，共 10 个既有参考成员。
3. 从常驻 Project Sources 移出下列五份历史/重复分发件：`Experiment_Report_P2_Exact.pdf`、`实验课1.pptx`、`作业.zip`、`任务3_LLM辅助评估清洗.ipynb`、`作业1轨迹数据预处理.ipynb`。它们的仓库权威原件与私密归档没有删除。原三项历史 false 也不加入常驻集合。
4. 确认实验二只有两份当前正式 PDF：`Experiment2_Experiment_Report.pdf`（26 页）和 `Experiment2_Process_Report.pdf`（16 页，c96c96…03e2f）。若 UI 已有 Process resend 别名或旧 8 页稿，按实际内容/SHA 核对后保留唯一正式成员；不要把 399970… 与 c96c96… 称为同一字节。
5. 任务二源 ZIP 不属于本轮 12 项。只有先确认完整安全备份仍存在后，才建议将它移出常驻 UI 成员；不要删除唯一原件。原视频、raw 帧、未选截图、私密 evidence 和 Settings TXT 均不上传到 Project Sources。
6. 按下表逐名确认 UI 最终恰好 12 项后，由用户报告实际完成情况。GitHub push、bundle check、内部检查均不能代替这一步，也不代表 GPT 外审通过。

| 规范文件名 | 版本 / 身份 | SHA-256 |
|---|---|---|
| `SMART_CITIES_RESEARCH_PROTOCOL.md` | v1.3 | `ec43f4ceab061ff6d4f1cccdec401f2f7a514aa5a5ba5963a1bcc7254c1d1b98` |
| `WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md` | v2.9 | `bec2a66770da9dc80991e84aebc67e2284310f9980671129200f706576db01fc` |
| `SMART_CITIES_REPORT_WRITING_GUIDE.md` | v1.4 | `4aef6e48c79efe87e49d2173f9975d65d8bf6716a3f2f0dd04308b2daee90f18` |
| `SMART_CITIES_VISUAL_SYSTEM.md` | v2.8 | `d109b1072cb05a5309c96e3f5aa1337d0e2a67614a1e7cbc0a62fa50253b45a8` |
| `AGENTS.md` | 2026-11-06 | `98b6b7063042b3b3e3e6b8b49d8460a514bd0ed1af0965fdb739c54d6c0694d7` |
| `publication-plots.zip` | approved original | `b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041` |
| `Experiment_Report_吴博闻_10245102410.pdf` | accepted 25-page reconstruction | `2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0` |
| `Experiment_Report_完整重构_源文件.zip` | accepted 25-page reconstruction | `6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd` |
| `Process_Report_Revised.pdf` | 2026-10-03 authorized p76 revision of prior accepted 77-page report | `dc1bb8e8e2262379b7e234550901f645ef0d6f549d6d2aef5e3985a433a1fa23` |
| `Process_Report_Revised_LaTeX_Source.zip` | 2026-10-03 authorized p76 revision of prior accepted 77-page report | `831d61baa7de160796827b60f29e1ada9f1b3809c2a87aa4acd6b98703e352ef` |
| `Experiment2_Experiment_Report.pdf` | Experiment 2 technical review, 26 pages | `7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101` |
| `Experiment2_Process_Report.pdf` | 2026-11-06 approved 16-page video-evidence PDF | `c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f` |

可核对的完整路径与字节数：[source_set_verification.json](source_set_verification.json)；[用户批准范围和未检查项](REVIEW_PACKET.md)。外审材料自身不加入 Project Sources。
