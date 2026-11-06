# 规范升级与 Project Sources 精简：独立初核

审查者：独立 Codex Agent `process_integration_verifier`。本次按用户新批准的 `SC-PROJECT-REFRESH-20261106` 范围执行，旧 `process_report_sync_20261106` 审查记录保留原身份。本记录不表示最终分发集合、GitHub 发布、UI 上传或 GPT 外审已经完成。

实际结果与可复查方法见 [initial_refresh_audit.json](initial_refresh_audit.json) 和 [verify_approved_refresh.py](verify_approved_refresh.py)。

## 批准包与四份权威规范

实际入站包 SHA256 为 `5012d8643f7a59208b89dc5be803b65b8701e9c55a85cb8c345767adf55dae13`；10 个成员的 CRC、路径和文件类型检查通过。四份权威规范与该包的完整文件逐字节一致，并匹配包内版本/SHA 清单：

| 权威规范 | 版本 | SHA256 |
|---|---|---|
| Workflow Interaction Evidence Protocol | v2.9 | `bec2a66770da9dc80991e84aebc67e2284310f9980671129200f706576db01fc` |
| Visual System | v2.8 | `d109b1072cb05a5309c96e3f5aa1337d0e2a67614a1e7cbc0a62fa50253b45a8` |
| Report Writing Guide | v1.4 | `4aef6e48c79efe87e49d2173f9975d65d8bf6716a3f2f0dd04308b2daee90f18` |
| AGENTS | 2026-11-06 | `98b6b7063042b3b3e3e6b8b49d8460a514bd0ed1af0965fdb739c54d6c0694d7` |

独立从基准 `b7fd9ee522905c11ddcea760470e7a5f0c1be9f0` 取得四份旧文件，核对旧版本的文件哈希及 Git blob，再计算旧→当前实际 unified diff；结果与父线程保存的 `governance.diff` 精确一致。没有发现导入时误抄、截断或自行改造。已实际读取新版 AGENTS 及四文件差异，其录屏来源、真实解码帧、时间码映射、私密证据、简短采集说明和精简来源集规则按批准全文承接。

Research Protocol v1.3 保持原 SHA256 `ec43f4ceab061ff6d4f1cccdec401f2f7a514aa5a5ba5963a1bcc7254c1d1b98`；没有为了版本一致而改写。

## 冻结成果与继承检查

通过 Git 对象差异核对，公共模板/P2、实验一目录、实验二算法实现、测试、结果、公开汇总、图表、技术图、Notebook、Experiment Report 及生成源、`common.tex` 和历史报告源包均未相对既有基准改变。

两份实验二正式 PDF 仍是：

- Process：16 页，SHA256 `c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f`。
- Experiment：26 页，SHA256 `7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101`。

Process 的 11 个 `.tex`、18 个正式引用 PNG 和原独立审核的 9 个已暂存记录仍与此前独立核验的文件哈希一致。其“PNG 与获批 PDF 内嵌图像一一对应、无隐藏 PNG metadata”的检查可按相同字节继承。本轮没有再执行实验、模型训练、报告编译、截图加工或逐页视觉重审。

同样必须继承原限制：Process 源码先前编译和全文核验通过，但严格 200 dpi 像素验证返回非零；该失败不能因本次规范刷新改为 PASS，也不授予新的 Evidence Master Lock。

## 目标集合与待完成范围

包内 `PROJECT_SOURCES_TARGET_12.json` 是批准目标，不是 active `sources.json` 的替代品。目标确认为 12 个唯一 active 名称、20 条总登记及 8 条 false。五份退出成员的权威原件必须保留；三份已 false 的旧记录保持其原身份；原 16 项中间集合中的 Process 记录应按批准名称迁移为 `Experiment2_Process_Report.pdf`，避免再追加一个重复 Process 记录。

本次核验时 active 清单仍为 19 条登记、16 条 true 的预期中间态，尚未完成目标迁移及安全同步。因此没有对当前 release 宣称 12 项通过；最终 manifest、分发目录、派生清单、index 和远程发布将由后续追加审查承接。

## 公开边界与未执行项

当时的待提交集合没有完整输入 ZIP、Project Settings TXT 全文、原视频或 raw 帧。Settings TXT 保持受保护的 TRANSFER_COPY，只供用户在 ChatGPT UI 粘贴；本次没有建立第二份 active Settings。实际源 ZIP、视频母件和未选截图不得因正式 PDF 获准发布而自动公开。

此初核未执行 ChatGPT UI 设置替换、UI 文件上传、GPT 外部二审、Evidence Lock 或远程 push/readback。目标状态仍须依据最终实际同步和固定提交回读分别确认。
