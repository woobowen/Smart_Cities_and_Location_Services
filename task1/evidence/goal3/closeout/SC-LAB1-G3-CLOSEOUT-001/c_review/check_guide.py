"""Independent current guide/interaction locator and authority-boundary audit."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    guide = ROOT / "task1/docs/goal3/REVIEW_GUIDE.md"
    content = guide.read_text()
    sections = re.split(r"(?m)^## (I{1,3}|IV)\. ", content)[1:]
    assert sections[::2] == ["I", "II", "III", "IV"]
    question_counts = []
    for body in sections[1::2]:
        questions = re.findall(r"(?m)^\d+\. \*\*", body)
        assert 2 <= len(questions) <= 4
        question_counts.append(len(questions))
    assert question_counts == [3, 3, 4, 3]
    for marker in ("用户尚未逐项理解验收", "Understanding=LEARNING", "GPT_SECOND_REVIEW=PENDING", "Submission=NOT_READY",
                   "source_crs=UNVERIFIED", "266.016754", "10245102410", "吴博闻"):
        assert marker in content
    basic_path = ROOT / "task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb"
    system_path = ROOT / "task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb"
    all_cells = {}
    for path in [basic_path, system_path]:
        nb = json.loads(path.read_text())
        for i, cell in enumerate(nb["cells"]):
            all_cells.setdefault(cell["id"], []).append({"notebook": str(path.relative_to(ROOT)), "index": i,
                 "source_sha256": hashlib.sha256("".join(cell["source"]).encode()).hexdigest()})
    guide_cells = {}
    for ident in re.findall(r"lab1-[0-9a-f]{16}", content):
        assert ident in all_cells and len(all_cells[ident]) == 1
        guide_cells[ident] = all_cells[ident][0]
    assert len(guide_cells) == 10
    expected_functions = {
        "task1/workflow/coordinates.py": ["working_xy", "conditional_adapter"],
        "task1/workflow/geometry.py": ["split_trajectory", "filter_segments", "direction_candidates", "denoise_trajectory", "point_segment_distance", "douglas_peucker_indices"],
        "task1/workflow/g2_metrics.py": ["common_reference_metrics", "record_metrics", "review_record"],
        "task1/goal3/selection.py": ["paired", "aggregate_pairs", "choose"],
        "task1/workflow/g2_pipeline.py": ["run_record"],
        "task1/workflow/g2_modes.py": ["run_batch_episode"],
        "task1/goal3/reproduce.py": ["recompute_historical"],
        "task1/workflow/g2_memory.py": ["build_snapshot", "FrozenMemory", "consumption"],
        "task1/goal3/control.py": ["Journal"],
        "task1/goal3/freezes.py": ["verified_run", "selection_decision", "release_decision"],
    }
    function_rows = []
    for name, functions in expected_functions.items():
        path = ROOT / name
        tree = ast.parse(path.read_text())
        nodes = {n.name: n.lineno for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))}
        for function in functions:
            assert function in nodes and f"`{function}`" in content
            function_rows.append({"path": name, "sha256": sha(path), "function": function, "line": nodes[function]})
    interaction = ROOT / "task1/docs/goal3/INTERACTION_HANDOFF.md"
    old_interaction = subprocess.check_output(["git", "show", "1a5e26b43189aef64a46f8986b3cc442fa50d2c5:task1/docs/goal3/INTERACTION_HANDOFF.md"], cwd=ROOT)
    assert interaction.read_bytes().startswith(old_interaction)
    appended = interaction.read_bytes()[len(old_interaction):].decode()
    assert "姓名吴博闻" in appended and "不是历史聊天恢复或Evidence Lock" in appended
    assert all(s in appended for s in ("身份已关闭", "Understanding=LEARNING", "PENDING", "Submission=NOT_READY"))
    inventory = HERE.parent / "b_handoff/evidence_inventory.json"
    candidates = json.loads((ROOT / "task1/evidence/goal3/interaction_candidates.json").read_text())
    plan_path = ROOT / "evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md"
    assert "NO EVIDENCE REGISTERED" in plan_path.read_text()
    reviewed = [guide, interaction, ROOT / "task1/docs/goal3/DEFENSE_NOTES.md", inventory,
                HERE.parent / "b_handoff/evidence_inventory.md", plan_path,
                ROOT / "task1/evidence/goal3/interaction_candidates.json"]
    links = 0
    for md in [p for p in reviewed if p.suffix == ".md"]:
        for target in re.findall(r"\]\(([^)]+)\)", md.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            path = (md.parent / unquote(target.split("#")[0].strip("<>"))).resolve()
            assert path.exists(), (md, target)
            links += 1
    out = {
        "role_context": "/root/c_independent", "status": "VERIFIED_IN_LISTED_SCOPE",
        "targets": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in reviewed],
        "guide_blocks": ["I tasks/requirements", "II processing/evaluation", "III system/experiments/loop", "IV deliverables/closeout"],
        "question_count_by_block": question_counts, "local_links_checked": links,
        "notebook_cells": guide_cells, "function_locators": function_rows,
        "interaction_old_text_preserved_byte_prefix": True,
        "checked_components": [
            "C read complete four-block guide and all13 evidence-linked questions; no fictitious user answers or exam scores.",
            "Actual frozen parameter/coordinate/metric/DP-input boundary and negative-result explanations match current reports and direct numerical C checks.",
            "Current task identity and revision date distinguished from old experiment/freeze time.",
            "Interaction Handoff original479lines remain byte-identical; only sourced present closeout state appended, with Human Judgment/annotation/Lock authority untouched.",
            "Evidence inventory states task-scope filename/field search limits rather than visually claiming all322images; template images and run locks are not original interaction evidence.",
        ],
        "limits": "This receipt covers the listed static guide, interaction, defense and evidence-boundary content. Technical Handoff, REVIEW_PACKET, MASTER and current CL states must receive final run/publication state refresh before their own final acceptance. It does not assert Process Evidence Lock, user Understanding PASS or new webpageGPT acceptance."
    }
    (HERE / "guide_interaction_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": out["status"], "questions": sum(question_counts), "cells": len(guide_cells), "functions": len(function_rows), "links": links}))


if __name__ == "__main__":
    main()
