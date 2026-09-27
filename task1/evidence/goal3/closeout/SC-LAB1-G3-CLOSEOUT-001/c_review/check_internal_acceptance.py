"""Independent final executable-engineering check before authorized publication.

The formal Process Evidence branch remains externally blocked. This receipt
does not pre-sign publication, webpage review, user understanding or submission.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from check_review_snapshot import check_events, at

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ANCHOR = "1a5e26b43189aef64a46f8986b3cc442fa50d2c5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def main():
    packet_path = BASE / "internal_acceptance_review_submission.json"
    packet = read(packet_path)
    state_path = ROOT / "task1/evidence/goal3/goal_state.json"
    state = read(state_path)
    current = state["tasks"]["internal_acceptance"]
    assert current["status"] == "REVIEW_PENDING"
    assert packet["targets"] == current["targets"]
    assert packet["source_hashes"] == current["source_hashes"]
    for row in packet["targets"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    for path, expected in packet["source_hashes"].items():
        assert sha(ROOT / path) == expected, path
    for forbidden in ("task1/evidence/goal3/requirements.json", "task1/evidence/goal3/goal_state.json",
                      str((HERE / "internal_acceptance_receipt.json").relative_to(ROOT))):
        assert forbidden not in packet["source_hashes"]
        assert not any(t["path"] == forbidden for t in packet["targets"])

    leaves = {}
    for name in ("figures", "notebooks", "experiment_report", "process_report", "handoffs", "package"):
        row = state["tasks"][name]
        expected_status = "BLOCKED_EXTERNAL" if name == "process_report" else "VERIFIED"
        assert row["status"] == expected_status, name
        assert row["verifier"] == "/root/c_independent" and row["author"] != row["verifier"]
        receipt_path = ROOT / row["receipt"]["path"]
        assert sha(receipt_path) == row["receipt"]["sha256"]
        receipt = read(receipt_path)
        assert receipt["role_context"] == "/root/c_independent"
        part = receipt["tasks"][name]
        assert part["status"] == expected_status and part["checked_components"]
        assert part["source_hashes"] == row["source_hashes"]
        assert part["targets"] == row["targets"]
        for target in row["targets"]:
            assert sha(ROOT / target["path"]) == target["sha256"]
        for path, expected in row["source_hashes"].items():
            assert sha(ROOT / path) == expected
        if name == "process_report":
            assert len(part["external_dependencies"]) == 3
        leaves[name] = {"status": expected_status, "receipt": row["receipt"], "targets": len(row["targets"]), "sources": len(row["source_hashes"])}
    assert all(row["status"] == "VERIFIED" for row in state["issues"].values())
    tip = check_events(state["events"])
    snapshot = read(BASE / "review_input_snapshot/goal_state.json")
    snap_manifest = read(BASE / "review_input_snapshot/SNAPSHOT_MANIFEST.json")
    assert state["events"][:len(snapshot["events"])] == snapshot["events"]
    assert all(at(e["at"]) >= at(snap_manifest["created_at"]) for e in state["events"][len(snapshot["events"]):])

    frozen = read(HERE / "frozen_identity_receipt.json")
    assert frozen["numeric_code_sha"] == "e12f8a27944210adb452730be92a0674dfc6b84b"
    for field in ("protected_files", "frozen_processing_sources", "contract_bindings"):
        for row in frozen[field]:
            assert sha(ROOT / row["path"]) == row["sha256"]
    visual = read(HERE / "visual_content_receipt.json")
    assert len(visual["pages"]) == 34 and visual["actual_page_views_total"] == 36
    for page in visual["pages"]:
        assert page["actual_visual_inspection"] and page["content_read"] and page["status"] == "PASS"
        assert page["dpi"] == 200 and sha(ROOT / page["page_path"]) == page["page_sha256"]
    for report in visual["reports"]:
        assert sha(ROOT / report["pdf"]) == report["sha256"]
        text = report["text"]
        assert sha(ROOT / text["path"]) == text["sha256"]
        assert sha(ROOT / text["paginated_path"]) == text["paginated_sha256"]
    full = read(HERE / "notebook_runs_receipt.json")
    assert full["status"] == "PASS" and len(full["executions"]) == 4
    assert [r["executed_code_cells"] for r in full["executions"]] == [12, 8, 12, 8]
    equivalence = read(HERE / "package_execution_equivalence.json")
    assert equivalence["status"] == "PASS" and equivalence["identical_non_pdf_payload_count"] == 113
    assert sha(ROOT / equivalence["final_zip"]) == equivalence["final_zip_sha256"]
    assert sha(ROOT / equivalence["actual_execution_zip"]) == equivalence["actual_execution_zip_sha256"]

    matrix_path = BASE / "ACCEPTANCE_MATRIX.json"
    matrix = read(matrix_path)
    rows = {r["id"]: r for r in matrix["checks"]}
    assert set(rows) == {f"CL{i:02d}" for i in range(1, 17)}
    for ident, row in rows.items():
        expected = "BLOCKED" if ident == "CL08" else "NOT_RUN" if ident == "CL16" else "PASS"
        assert row["status"] == expected, (ident, row["status"])
        assert row["actual_scope"] and row["action"] and row["result"] and row["remaining"]
        assert row["evidence"] or ident == "CL16"
        for path in row["evidence"]:
            assert (ROOT / path).is_file(), path
    assert "仍在恢复" not in rows["CL13"]["actual_scope"]
    requirements_path = ROOT / "task1/evidence/goal3/requirements.json"
    requirements = read(requirements_path)
    for doc in (requirements, state):
        assert doc["Identity"] == "VERIFIED" and doc["Understanding"] == "LEARNING"
        assert doc["Submission"] == "NOT_READY" and doc["GPT_SECOND_REVIEW"] == "PENDING"
    assert requirements["Deliverable"] == "FINAL_REVIEW" and requirements["New_GPT_SECOND_REVIEW"] == "PENDING"
    assert requirements["Process_Evidence"] == "BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK"
    assert all(r["status"] in ("PASS", "INHERITED_NUMERIC_EVIDENCE", "BLOCKED", "PENDING") for r in requirements["requirements"])
    preflight = read(BASE / "PREFLIGHT.json")
    assert preflight["status"] == "PASS" and not preflight["findings"]
    assert not preflight["outside_task_changes"] and all(preflight["protected_files_equal_startup"].values())
    assert all(f["clean_generated_source"] for f in preflight["final_notebook_output_policy"])
    assert not preflight["new_installs"] and not preflight["persistent_environment_changes"]
    links = read(BASE / "CURRENT_LINKS.json")
    assert links["status"] == "PASS" and not links["issues"]
    whitespace = read(BASE / "WHITESPACE_CHECK.json")
    assert not whitespace["unclassified"]
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    assert branch == "main"
    changes = [p for p in subprocess.check_output(["git", "diff", "--name-only", "-z", ANCHOR], cwd=ROOT, text=True).split("\0") if p]
    assert all(p.startswith("task1/") for p in changes)
    assert not any(p.startswith(("task1/workflow/", "task1/evidence/goal1/", "task1/evidence/goal2/", "task1/evidence/goal3/runs/")) for p in changes)
    external = [
        "Authentic required historical Human-AI originals/screenshots or complete contextual source text remain unavailable in the approved task scope.",
        "Evidence Master approved selection/narrative/annotation specification and Report Order are not available for formal historical presentation.",
        "Evidence/Block Lock must be decided by Evidence Master on actual material/version after engineering; current C cannot grant it.",
    ]
    part = {"status": "BLOCKED_EXTERNAL", "engineering_checks": "PASS", "targets": packet["targets"],
            "source_hashes": packet["source_hashes"], "external_dependencies": external,
            "checked_components": [
                "All220 submitted substantive targets and258 declared sources rehashed at combined review; all six accepted leaves and their actual independent C receipts are current. No self-referential output or mutable active-governance hash was admitted as this submission input.",
                "Identity regeneration/string/cover/PDF/Notebook/package, teacher13T1+8T2 and user44U crosswalk, seven teaching differences,28 literature reading/use distinctions, complete four-block guide and both Handoffs verified in their bounded actual receipts.",
                "Frozen32 numerical sources,132 contracts/bindings and7 protected startup files remain unchanged; direct numeric-manifest checks and50-digit record352 counterexample preserved. This is not a new independent full mathematical implementation of every historic result.",
                "Current22+12 PDF physical pages actually read/viewed at200dpi in this context, with34 current page bytes and36 actual views including changed-page reinspection; seven native standalone report figures and six unique current Notebook figures also actually viewed.",
                "Four actual FULL new-kernel executions complete: repository and same extracted archive12/8 cells each; two basic runs each285 actual shards/all11386 records/1173410 points/22772 processing observations,9720 historical parameter scope; each system6001 candidate computations/384 episode choices. New record-level model calls0.",
                "Current116-member final ZIP has current report/identity/runtime closure; actual executed archive is retained, all113 nonPDF payload bytes equal and only ExperimentPDF/manifest changed. Execution evidence inheritance is explicit and is not a fifth execution.",
                "CL-C01/02/03 and ordinary content/navigation repairs are actually closed with verified targets/regression/rebuild/review/resume; interrupted attempts retain false-success prohibition and unknown SIGTERM source. C checker range assertion correction is documented as checker diagnosis, not a fictitious B defect.",
                "Current CL01–15 have actual scoped evidence;CL08 alone retains genuine external block. Safety preflight/link/whitespace checks inspected, fixed11-file bundle independently checked, no teacher transmission/new research/new installs. CL16 publication remains NOT_RUN before actual push.",
            ]}
    selected = ["frozen_identity_receipt.json", "report_numbers_receipt.json", "result_summary_equivalence.json",
                "visual_content_receipt.json", "report_tasks_receipt.json", "notebook_runs_receipt.json",
                "notebook_figure_visual_receipt.json", "notebooks_task_receipt.json", "package_receipt.json",
                "package_execution_equivalence.json", "package_task_receipt.json", "requirements_literature_receipt.json",
                "review_input_snapshot_receipt.json", "guide_interaction_receipt.json", "handoffs_task_receipt.json",
                "upload_bundle_receipt.json", "CL-C01_closure.json", "CL-C02_closure.json", "CL-C03_closure.json"]
    out = {
        "role_context": "/root/c_independent", "checked_at": datetime.now(timezone.utc).isoformat(),
        "task_id": "SC-LAB1-G3-CLOSEOUT-001", "overall": "PARTIAL_BLOCKED",
        "executable_engineering": "PASS_READY_FOR_AUTHORIZED_REVIEW_CHECKPOINT_PUBLICATION",
        "tasks": {"internal_acceptance": part}, "substantive_leaves": leaves,
        "submission": bind(packet_path), "independent_C_receipts": [bind(HERE / p) for p in selected],
        "review_program_sources": [bind(p) for p in sorted(HERE.glob("*.py"))],
        "mutable_status_observations_not_immutable_inputs": [
            {"path": str(p.relative_to(ROOT)), "observed_sha256": sha(p)} for p in
            (state_path, requirements_path, matrix_path, BASE / "PREFLIGHT.json", BASE / "CURRENT_LINKS.json", BASE / "WHITESPACE_CHECK.json")],
        "current_Journal_events_verified": len(state["events"]), "current_Journal_tip_observed": tip,
        "CL_status_at_prepublication_check": {k: v["status"] for k, v in rows.items()},
        "independent_states": {"Identity": "VERIFIED", "Closeout Engineering": "PARTIAL_BLOCKED",
            "Process Evidence": "BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK", "Deliverable": "FINAL_REVIEW",
            "Understanding": "LEARNING", "Submission": "NOT_READY", "New GPT_SECOND_REVIEW": "PENDING"},
        "new_record_model_calls": 0, "publication_verification": "NOT_RUN_REQUIRES_ACTUAL_PUSH_AND_REMOTE_READBACK",
        "scope_limit": "This is actual independent internal engineering acceptance with a precise external Process Evidence block. It is not final course PASS, user Understanding acceptance, Evidence Lock, new webpageGPT review or teacher submission. Parent is authorized to publish this accurate PARTIAL_BLOCKED review checkpoint after recording the actual action; C will check the resulting publication/status delta separately.",
    }
    output = HERE / "internal_acceptance_receipt.json"
    output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    summary = """# 独立 C 收尾审核

可自主执行的工程内容已通过独立内部审核；整体保持 **PARTIAL_BLOCKED**，唯一实质外部内容阻断是 Process Report 所需的真实互动原件、Evidence Master 呈现规格及对应 Lock。身份已解决。

- 合并核验220个实际目标、258个来源；数值源码32份、冻结绑定132项、启动保护文件7项保持一致。
- 两份报告22+12页全文与200dpi原尺寸逐页实际查看，34个当前页面对应36次实际页面查看；七幅报告原生图、六幅当前Notebook独立图也实际查看。
- 仓库与同一实际解压包的两本Notebook完成四次新内核FULL，代码单元12/8/12/8；两份基础本各285个真实新分片、全部11,386记录和1,173,410点由C实际读取核查。新增记录级模型调用0。
- 最终116成员具名待审ZIP与实际执行包的113个非PDF运行成员逐字节一致；只更新Experiment PDF与manifest，明确继承等价执行证据，没有冒称第五次执行。
- 65项要求、七项教学差异、28项文献使用索引、四块13题复盘指南和两份Handoff已按来源与实际产物复验。当前PDF页码、Notebook stable cell和源哈希已绑定。
- 包状态、引用/措辞/链接、表14间距和两次中断恢复均完成对应修复与复验。中断触发源仍unknown，失败没有记为FULL成功。C自己的过严多页anchor断言修正另有诊断记录，没有伪造B缺陷。

完整范围、来源、逐页和逐次执行证据见 [合并回执](internal_acceptance_receipt.json)。历史数学审查、当前数值直接核对、真实重算与本轮目视范围在各回执中分开，未把旧网页审核补签到新报告/ZIP。

CL01—15除CL08外按限定工程范围通过；CL08保留真实外部依赖。此回执形成时CL16尚未push，不能证明未来发布或远程一致；实际发布需单列核验。

Identity=VERIFIED；Closeout Engineering=PARTIAL_BLOCKED；Process Evidence=BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK；Deliverable=FINAL_REVIEW；Understanding=LEARNING；Submission=NOT_READY；New GPT_SECOND_REVIEW=PENDING。
"""
    (HERE / "INDEPENDENT_C_REVIEW.md").write_text(summary, encoding="utf8")
    print(json.dumps({"task": "internal_acceptance", "status": part["status"], "engineering_checks": "PASS", "targets": len(packet["targets"]), "sources": len(packet["source_hashes"]), "CL16": "NOT_RUN"}))


if __name__ == "__main__":
    main()
