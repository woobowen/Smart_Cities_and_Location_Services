"""Record closeout status without rewriting the accepted historical checkpoint.

This A checkpoint is deliberately pending for FULL/package/current aggregate C
acceptance/publication. Do not rerun it after the controller advances those states.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
TASK = "SC-LAB1-G3-CLOSEOUT-001"
CLOSE = f"task1/evidence/goal3/closeout/{TASK}"
REL = "task1/evidence/goal3/requirements.json"
ANCHOR = "1a5e26b43189aef64a46f8986b3cc442fa50d2c5"
NUMERIC_SHA = "e12f8a27944210adb452730be92a0674dfc6b84b"
NOW = datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def evidence(path, scope):
    return {"path": path, "sha256": sha(path), "scope": scope}


historical_bytes = subprocess.check_output(["git", "show", f"{ANCHOR}:{REL}"], cwd=ROOT)
historical = json.loads(historical_bytes)
current = load(REL)
assert current == historical or current.get("current_review_stage") == "A_PARENT_REFRESH_PENDING_C", "Controller state advanced; do not overwrite it."
identity = load("task1/config/assignment.json")
identity_receipt = load(f"{CLOSE}/c_review/frozen_identity_receipt.json")
equivalence = load(f"{CLOSE}/c_review/result_summary_equivalence.json")
assert identity["student_name"] == "吴博闻"
assert type(identity["student_id"]) is str and identity["student_id"] == "10245102410"
assert identity_receipt["status"] == "PASS" and all(identity_receipt["identity_checks"].values())
assert equivalence["status"] == "PASS"
assert equivalence["current_sha256"] == sha("task1/evidence/goal3/result_summary.json")
assert all(item["path"] == "/at" for item in equivalence["differences"])

frozen = evidence(f"{CLOSE}/c_review/frozen_identity_receipt.json", "本轮独立C：冻结源码/合同/原件字节、身份字符串与重复元数据生成；不证明FULL或最终交付。")
same_numbers = evidence(f"{CLOSE}/c_review/result_summary_equivalence.json", "本轮独立C：当前result_summary相对历史锚点仅/at不同；不是重新执行历史实验。")
report_numbers = evidence(f"{CLOSE}/c_review/report_numbers_receipt.json", "本轮独立C：最终确认/全量表与冻结run、记录352方向删除及有限线段偏差的指定核查；非全数值重新独立审计。")
visual = evidence(f"{CLOSE}/c_review/visual_content_receipt.json", "本轮独立C：当前Experiment22页和Process12页实际200dpi逐页查看与关键内容核查；不代Evidence Master或网页GPT。")
repo_system = evidence(f"{CLOSE}/notebooks/repository_system/execution_receipt.json", "本轮仓库system Notebook新内核8/8执行完成；其余三个有效FULL与C合并验收仍等待真实回执。")
interruptions = evidence(f"{CLOSE}/notebook_interruptions.json", "两次SIGTERM失败尝试真实保留，不计FULL成功；同源新内核重试由主线程继续。")
auth = evidence(f"{CLOSE}/AUTHORIZATION.md", "本轮用户授权节选与要求归并说明；不冒称完整历史逐字对话。")

updates = {
    "G3-A01": ("PASS", ["承接当前1a5e26b锚点；独立C比较原始材料、旧ZIP、冻结源码和合同字节。"], "当前冻结与原件保护范围独立通过；最终发布前复核仍由本轮CL01/CL15/CL16记录。", [frozen, evidence(f"{CLOSE}/startup.json", "本轮真实启动仓库/分支/远程/未跟踪文件快照。")], "当前只覆盖启动与冻结保护，不继承未来发布结果。"),
    "G3-A02": ("PENDING", ["复用原TD22项，并派生T1/T2/U共65项crosswalk；按当前PDF/Notebook刷新定位。"], "来源、实现、真实结果、差异和剩余依赖已逐条对账；本轮完整内容与导航C结论待回执。", [auth], "65项只是父requirements的解释入口，不是平行验收或单凭存在通过。"),
    "G3-A10": ("PENDING", ["冻结数学源码保持不变；新增元数据/生成链/包工程回归由本轮独立验收核对。"], "历史数学正确性只在未变源码/合同范围继承；本轮工程回归和集成结果尚未在本项汇总验收。", [frozen, same_numbers, report_numbers], "不能把历史469+10等测试计作本轮新执行。"),
    "G3-A11": ("PENDING", ["本轮真实A诊断、B编辑/构建/修复、独立C审查；主线程持续消费普通问题并恢复收尾。"], "已形成真实审查与修复回执；完整本轮循环关闭需等待FULL、包与C总验收，不预写完成。", [auth, interruptions, visual], "治理协作与实验记录级LIVE分账；不编造用户逐项判断。"),
    "G3-A13": ("PENDING", ["仓库system新内核执行完成；仓库basic与ZIP system首次SIGTERM后保留失败记录并同源新内核重试；ZIP basic继续。"], "当前仅仓库system有实际执行完成回执；不将旧四FULL或中断尝试计为本轮四FULL完成。", [repo_system, interruptions], "以本轮最终四份有效FULL及同一ZIP内容绑定/C核验为完成条件；报告字节替换可另作同依赖内容等价绑定。"),
    "G3-A14": ("PENDING", ["当前报告全页200dpi查看，表14列间距与来源访问层级修订后C复查变页。"], "当前PDF视觉/内容限定范围有C回执；图源/数据及最终交付版本闭合由本轮总验收汇总。", [visual, report_numbers], "当前视觉回执不证明Notebook FULL、Evidence Lock或新网页GPT验收。"),
    "G3-A15": ("PENDING", ["姓名/学号唯一配置与生成器同步、重复生成回归；Experiment重建22页并完成当前C逐页核查。"], "Identity VERIFIED，META外部依赖已关闭；本轮报告与最终包绑定及总验收待收齐回执。", [frozen, visual, report_numbers], "当前技术报告送审；历史21页/身份缺项已保存于previous_acceptance，不能作为当前描述。"),
    "G3-A16": ("BLOCKED", ["Process保留Part I/II、校正真实技术事实与来源；当前12页已由C逐页查看。"], "身份已解决；真实互动原件、Evidence Master批准spec及Lock仍是外部依赖，可做工程与最终包绑定继续。", [frozen, visual, auth], "不伪造聊天、用户anchor/箭头、逐次裁决或Evidence Lock；正文完整正式互动证据尚未完成。"),
    "G3-A17": ("PENDING", ["更新技术/互动Handoff与四块REVIEW_GUIDE，继续逐文件/图表/单元绑定。"], "当前交接稿待本轮C导航/内容回执；不继承历史Handoff已检查为新稿通过。", [auth], "互动候选与外部依赖分开；Understanding仍LEARNING。"),
    "G3-A18": ("BLOCKED", ["构建有身份的新REVIEW_ONLY待审包；实际解压目录运行两本FULL，并绑定后续只改报告的同依赖内容。"], "META已解决；当前包完整工程验收PENDING，Process Evidence及用户/GPT最终审核继续阻断正式提交。", [frozen, interruptions, auth], "不复用历史113成员ZIP统计为当前结果；当前名称REVIEW_ONLY_10245102410_吴博闻_实验一.zip，Submission NOT_READY。"),
    "G3-A19": ("PENDING", ["独立C已经出具冻结/身份、指定数值与当前34页视觉限定范围回执。"], "尚未形成当前全部可执行工程合并验收；完整FULL、最终包、总账/交接和发布预检仍须真实回执。", [frozen, same_numbers, report_numbers, visual], "分项C通过不自动等于当前总验收；外部Evidence只局部BLOCKED。"),
    "G3-A20": ("PENDING", ["保留历史发布记录；本轮按用户授权在实际内部验收后push并固定SHA远程回读。"], "本轮尚未据此项登记新push/远程一致；历史fd559e4发布和1a5e26b锚点保持历史身份。", [auth], "不得以旧ARTIFACT_REMOTE_VERIFIED冒充本轮新报告/包已发布。"),
}
numeric_ids = {f"G3-A{i:02d}" for i in range(3, 10)} | {"G3-A12"}
rows = []
for old in historical["requirements"]:
    rid = old["id"]
    row = {"id": rid, "requirement": old["requirement"], "review_task": TASK, "status_as_of": NOW}
    row["historical_as_of"] = ANCHOR
    row["previous_acceptance"] = copy.deepcopy(old)
    row["expected"] = "保留原Goal3要求；当前用户SC-LAB1-G3-CLOSEOUT-001仅调整收尾顺序和已授权工程范围。"
    if rid in numeric_ids:
        row.update(status="INHERITED_NUMERIC_EVIDENCE", actual_actions=["本轮冻结数学代码、候选、参数、划分与研究结论；独立C核对冻结字节及result_summary与历史锚点等价。"], measured="继承历史已登记实验结论，非本轮重开研究；当前summary仅构建时间变化。历史实际结果、分母和审核范围见previous_acceptance。", evidence=[frozen, same_numbers], scope="继承数值证据只覆盖原run及未变数学源码；不能验收本轮报告、ZIP、四FULL或网页GPT。")
        if rid in {"G3-A07", "G3-A08"}:
            row["evidence"].append(report_numbers)
        if rid == "G3-A12":
            row["current_recompute_accounting"] = "PENDING_CURRENT_FOUR_FULL_RECEIPTS; 新增记录级LIVE默认0，已完成system单份执行不代表全部四份。"
            row["evidence"].append(repo_system)
    else:
        status, actions, measured, receipts, scope = updates[rid]
        row.update(status=status, actual_actions=actions, measured=measured, evidence=receipts, scope=scope)
    row["current_closeout_matrix"] = {"path": f"{CLOSE}/ACCEPTANCE_MATRIX.json", "reference_type": "PATH_ONLY_PENDING_CONTROLLER_MATRIX", "hash_binding": "Not recorded before the actual matrix exists; avoid circular parent/crosswalk hashes."}
    if rid in {"G3-A15", "G3-A16", "G3-A18"}:
        row["identity_status"] = "VERIFIED"
        row["engineering_status"] = "PENDING_CURRENT_AGGREGATE_ACCEPTANCE"
    if rid in {"G3-A16", "G3-A18"}:
        row["external_dependencies"] = ["EVIDENCE_MASTER_DEPENDENCY"]
    rows.append(row)

result = {
    "goal_id": historical["goal_id"],
    "current_task_id": TASK,
    "sole_remaining_requirements_entry": True,
    "authority": {"historical_goal_prompt": "task1/evidence/goal3/USER_PROMPT.md §18", "current_closeout_authority": f"{CLOSE}/AUTHORIZATION.md", "meaning": "用户本轮消息优先；AUTHORIZATION是准确节选/归并索引，不伪称完整原始聊天。"},
    "inherited": historical["inherited"],
    "historical_as_of": {"git_commit": ANCHOR, "path": REL, "blob_sha256": hashlib.sha256(historical_bytes).hexdigest(), "fixed_url": f"https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/{ANCHOR}/{REL}", "scope": "完整历史状态可从固定Git原件恢复；每项previous_acceptance原样保存该条。历史新内核/视觉/包/发布PASS只适用于旧产物，不给新提交补签。"},
    "previous_acceptance_metadata": {k: copy.deepcopy(v) for k, v in historical.items() if k != "requirements"},
    "current_review_stage": "A_PARENT_REFRESH_PENDING_C",
    "status_semantics": {"PASS": "当前回执明确的限定范围已通过，不等于整体或用户验收", "INHERITED_NUMERIC_EVIDENCE": "历史数值证据加本轮冻结字节/summary等价复核，不是本轮新实验", "PENDING": "本轮最终有效回执尚未收齐，不继承旧PASS", "BLOCKED": "明确外部依赖阻断正式闭合；可执行工程继续，工程状态另记"},
    "requirements": rows,
    "derived_review_crosswalk": {"path": f"{CLOSE}/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.json", "role": "65条稳定复盘索引，仅crosswalk，不是平行父要求或验收表", "hash_binding": "PATH_ONLY_TO_AVOID_CIRCULAR_BINDING"},
    "current_acceptance_detail": {"json_path": f"{CLOSE}/ACCEPTANCE_MATRIX.json", "markdown_path": f"{CLOSE}/ACCEPTANCE_MATRIX.md", "status": "PENDING_CONTROLLER_RECORD", "hash_binding": "PATH_ONLY; 尚未生成时不制造哈希"},
    "external_dependencies": [{"id": "EVIDENCE_MASTER_DEPENDENCY", "status": "AWAITING_EVIDENCE_MASTER", "affects": ["G3-A16", "G3-A18"], "missing": ["需要入选的真实完整互动原件（已有可追溯转录候选不等于完整原件已提供）", "Evidence Master批准的入选/叙事与annotation specification", "对应真实材料及批准版本的Evidence/Block Lock"], "identity_is_not_missing": True}],
    "resolved_dependencies": [{"id": "META_DEPENDENCY", "status": "RESOLVED", "identity_status": "VERIFIED", "student_name": identity["student_name"], "student_id": identity["student_id"], "authority": "本轮用户直接提供可信身份并授权同步本作业", "actual_resolution": "唯一assignment配置、生成器及重复元数据生成、Notebook介绍由当前C回执核实", "evidence": [frozen, evidence("task1/config/assignment.json", "当前唯一任务身份源；student_id为字符串。")], "does_not_resolve": ["EVIDENCE_MASTER_DEPENDENCY", "新网页GPT验收", "用户Understanding与最终提交决定"]}],
    "Identity": "VERIFIED",
    "Closeout_Engineering": "PARTIAL_BLOCKED",
    "Process_Evidence": "BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK",
    "Deliverable": "FINAL_REVIEW",
    "Understanding": "LEARNING",
    "Submission": "NOT_READY",
    "GPT_SECOND_REVIEW": "PENDING",
    "New_GPT_SECOND_REVIEW": "PENDING",
    "updated_at": NOW,
    "goal_completion_claim": False,
    "remaining_work": "Identity已解决。完成本轮有效四FULL、最终包/导航绑定、C总验收与实际发布；外部仅需Evidence Master真实原件/spec/Lock及未来网页GPT和用户深入审核。不新增研究。",
    "overall_status": "PARTIAL_BLOCKED",
    "technical_status": "PENDING_CURRENT_CLOSEOUT_AGGREGATE_ACCEPTANCE",
    "research_status": "INHERITED_NUMERIC_EVIDENCE_WITH_CURRENT_EQUIVALENCE_CHECK",
    "reports_status": "CURRENT_CONTENT_VISUAL_SCOPE_REVIEWED; FINAL_BINDING_PENDING; PROCESS_EXTERNAL_BLOCKED",
    "package_status": "REVIEW_ONLY; CURRENT_ENGINEERING_ACCEPTANCE_PENDING",
    "publication_status": "PENDING_CURRENT_CLOSEOUT_PUBLICATION",
    "NUMERIC_CODE_SHA": NUMERIC_SHA,
    "historical_ARTIFACT_SHA": "fd559e451291b9d424682853ef0909aa5eb94b32",
    "current_record_level_model_calls_policy": "0 new LIVE; actual FULL provider counts require current execution/C receipts; governance backend usage unknown",
}
(ROOT / REL).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
saved = load(REL)
assert [r["id"] for r in saved["requirements"]] == [r["id"] for r in historical["requirements"]]
assert [r["previous_acceptance"] for r in saved["requirements"]] == historical["requirements"]
assert saved["previous_acceptance_metadata"] == {k: v for k, v in historical.items() if k != "requirements"}
assert not any(d["id"] == "META_DEPENDENCY" for d in saved["external_dependencies"])
assert not any(r["status"] == "PASS" for r in saved["requirements"] if r["id"] in {"G3-A13", "G3-A15", "G3-A18", "G3-A19", "G3-A20"})
receipt = {"role": "A_REQUIREMENTS_STATUS_REFRESH_NOT_C_ACCEPTANCE", "at": NOW, "status": "PASS_SELF_CHECK", "historical_source_commit": ANCHOR, "historical_source_sha256": hashlib.sha256(historical_bytes).hexdigest(), "updated_requirements_path": REL, "updated_requirements_sha256": sha(REL), "checks": {"20_original_ids_preserved": len(rows) == 20, "all_original_rows_exact_in_previous_acceptance": True, "all_original_metadata_exact_preserved": True, "META_resolved_only_after_real_C_identity_receipt": True, "new_FULL_reports_package_aggregate_C_publication_not_inherited_PASS": True, "summary_equivalence_receipt_matches_current_bytes": True, "CL_and_crosswalk_path_only_no_circular_hash": True}, "new_research_experiments": 0, "new_record_model_calls": 0}
(OUT / "parent_requirements_update_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": receipt["status"], "requirements": len(rows), "status_counts": {s: sum(r["status"] == s for r in rows) for s in sorted({r["status"] for r in rows})}, "requirements_sha256": receipt["updated_requirements_sha256"]}, ensure_ascii=False))
