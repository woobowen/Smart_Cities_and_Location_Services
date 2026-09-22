# Workflow Construction Evidence Plan

Status: **SCHEMA READY / NO EVIDENCE REGISTERED**

本文件是内部 Evidence Plan，不进入 ChatGPT Project Sources。依据 [Interaction Evidence Protocol v2.3](../../../docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md) 维护。Evidence Master 决定内容、关系、顺序、Tier 与 Lock；Codex 按批准 specification 同步工程产物。

当前没有交付真实 raw 截图与批准 annotation spec；不创建虚构 Evidence 记录，不把本轮治理同步或 synthetic template 当作已 LOCK 的真实互动。

## Record schema

每条真实 Evidence 使用以下字段；尚未知的值标记 PENDING，不能伪填 PASS/LOCKED。

| Field | Required value / rule |
|---|---|
| Evidence ID | Evidence Master 填写或批准；Codex 按证据记录。 |
| Question / Candidate ID | Evidence Master 填写或批准；Codex 按证据记录。 |
| Decision Unit | Evidence Master 填写或批准；Codex 按证据记录。 |
| Historical Turns | Evidence Master 填写或批准；Codex 按证据记录。 |
| Historical Order | Evidence Master 填写或批准；Codex 按证据记录。 |
| Report Order | Evidence Master 填写或批准；Codex 按证据记录。 |
| Reordered? / Reorder Reason | Evidence Master 填写或批准；Codex 按证据记录。 |
| Part / Section | Evidence Master 填写或批准；Codex 按证据记录。 |
| Tier | Evidence Master 填写或批准；Codex 按证据记录。 |
| Provenance | Evidence Master 填写或批准；Codex 按证据记录。 |
| Intervention Level | Evidence Master 填写或批准；Codex 按证据记录。 |
| Historical Basis | Evidence Master 填写或批准；Codex 按证据记录。 |
| User Verbatim | Evidence Master 填写或批准；Codex 按证据记录。 |
| GPT Verbatim | Evidence Master 填写或批准；Codex 按证据记录。 |
| Turn Classification | Evidence Master 填写或批准；Codex 按证据记录。 |
| Decision | Evidence Master 填写或批准；Codex 按证据记录。 |
| Evidence / Verification | Evidence Master 填写或批准；Codex 按证据记录。 |
| Final Decision | Evidence Master 填写或批准；Codex 按证据记录。 |
| Mode | Evidence Master 填写或批准；Codex 按证据记录。 |
| Raw Screenshot | Evidence Master 填写或批准；Codex 按证据记录。 |
| Raw Pixel Size | Evidence Master 填写或批准；Codex 按证据记录。 |
| Formal Screenshot Source | Evidence Master 填写或批准；Codex 按证据记录。 |
| Crop Plan | Evidence Master 填写或批准；Codex 按证据记录。 |
| Crop Pixel Size / Bounds | Evidence Master 填写或批准；Codex 按证据记录。 |
| Final Display Size | Evidence Master 填写或批准；Codex 按证据记录。 |
| Effective PPI | 显示区域像素 / 显示英寸；横纵取小值；>=180，preferred >=200。 |
| Interaction Window | Evidence Master 填写或批准；Codex 按证据记录。 |
| User Anchor Phrase(s) | Evidence Master 填写或批准；Codex 按证据记录。 |
| GPT Before Phrase(s) | Evidence Master 填写或批准；Codex 按证据记录。 |
| GPT After Phrase(s) | Evidence Master 填写或批准；Codex 按证据记录。 |
| Trace Relation(s) | 逐边记录原文 source phrase → target phrase 与语义关系；不得仅凭时间相邻。 |
| Phrase Match Audit | 记录实际检查结果与依据；Phrase/Relation/Endpoint 为 PASS / REVISE，Resolution 为 PASS / RECAPTURE；不适用须说明。 |
| Arrow Relation Audit | 记录实际检查结果与依据；Phrase/Relation/Endpoint 为 PASS / REVISE，Resolution 为 PASS / RECAPTURE；不适用须说明。 |
| Arrow Endpoint Audit | 记录实际检查结果与依据；Phrase/Relation/Endpoint 为 PASS / REVISE，Resolution 为 PASS / RECAPTURE；不适用须说明。 |
| Source Resolution Audit | 记录实际检查结果与依据；Phrase/Relation/Endpoint 为 PASS / REVISE，Resolution 为 PASS / RECAPTURE；不适用须说明。 |
| Annotation Medium | Evidence Master 填写或批准；Codex 按证据记录。 |
| Annotation | Evidence Master 填写或批准；Codex 按证据记录。 |
| Side Note | Evidence Master 填写或批准；Codex 按证据记录。 |
| Caption | Evidence Master 填写或批准；Codex 按证据记录。 |
| LaTeX Source | Evidence Master 填写或批准；Codex 按证据记录。 |
| Diagram | Evidence Master 填写或批准；Codex 按证据记录。 |
| Transcript Diff Audit Result | 记录实际检查结果与依据；Phrase/Relation/Endpoint 为 PASS / REVISE，Resolution 为 PASS / RECAPTURE；不适用须说明。 |
| Final Approved Script / Reconstruction Control (if applicable) | Evidence Master 填写或批准；Codex 按证据记录。 |
| Status | 按协议状态机推进；所有审核通过且 Evidence Master 批准后才能 LOCKED。 |

## Records

暂无。待 Evidence Master 交付真实 Evidence Plan / annotation specification 后登记。

## Production / lock gate

raw screenshot → Evidence Master annotation spec → lossless crop → direct LaTeX embed → TikZ Micro Trace → XeLaTeX → 200-dpi render inspection → Phrase/Arrow Audit → Evidence Lock。

raw 不覆盖；完整记录 Historical Order 与 Report Order。Block/Section 的主要 Evidence 全部 LOCK 后再进行局部 LaTeX 同步；Global Workflow Evolution Map 最后制作。
