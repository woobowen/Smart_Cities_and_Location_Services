"""Validate the received-to-active scope edit and unchanged governed content."""

from pathlib import Path
import difflib
import hashlib
import json
import re
from urllib.parse import unquote, urlparse


HERE = Path(__file__).resolve().parent
TASK = HERE.parent
ROOT = TASK.parents[2]
FILES = {
    "SMART_CITIES_RESEARCH_PROTOCOL.md": (
        "docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md", "v1.2",
        "332741175630b1329387a0d69acf0061c6278c82bb27596f1d4629c2aa13a378",
        {"__preamble__", "A. Research Scope / Task Governance", "C. Standard Research Workflow", "G. Spatiotemporal Correctness"},
    ),
    "SMART_CITIES_REPORT_WRITING_GUIDE.md": (
        "docs/report-writing/SMART_CITIES_REPORT_WRITING_GUIDE.md", "v1.1",
        "abc729c5f7f764021ae1417dc6e8fcb1997eb3632747e46c8d0d53166642ff37",
        {"__preamble__", "1. 两份报告的读者与任务", "3. 把研究要求融入实际方法与实验", "12. Process Report写作衔接：不覆盖最新第一人称规则"},
    ),
    "SMART_CITIES_VISUAL_SYSTEM.md": (
        "docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md", "v2.5",
        "fbba109a796cff5ffe09848986a75b749248e5d609860c54eb2004b839fd9cbc",
        {"__preamble__", "1. Shared Identity", "13. Native and Reproducible Production", "16. Reference Files"},
    ),
    "WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md": (
        "docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md", "v2.6",
        "2385583504caa7c4a7708cd12602c2f692dfd6bb217e1b6ffdd3558b25a22fbd",
        {"__preamble__", "4. 三角色对话体系", "6. Original Evidence 优先原则", "28. 正式Research Conversation实时证据机制"},
    ),
    "AGENTS.md": (
        "AGENTS.md", "2026-09-29 · Project-wide P1–P4 scope / manifest-driven source distribution",
        "aec7864126d07644ab2d8a724aad7357d146b9adf000ff3e8a3a70b2b644d171",
        {"__preamble__", "2. Scope", "18. Git and GitHub"},
    ),
}
NAVIGATION = [
    "README.md", "docs/design-system/README.md",
    "templates/latex/experiment-report/README.md", "templates/latex/process-report/README.md",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sections(text):
    chunks = re.split(r"(?m)^(## [^\n]+\n)", text)
    result = {"__preamble__": chunks[0]}
    for heading, body in zip(chunks[1::2], chunks[2::2]):
        key = heading[3:].strip()
        if key in result:
            raise ValueError(f"Duplicate section: {key}")
        result[key] = heading + body
    return result


def anchors(text):
    result = set()
    counts = {}
    for heading in re.findall(r"(?m)^#{1,6} (.+)$", text):
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug if not count else f"{slug}-{count}")
    return result


def write_if_changed(path, text):
    data = text.encode("utf-8")
    if not path.exists() or path.read_bytes() != data:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    errors = []
    documents = []
    for name, (active_path, version, expected_hash, allowed_changes) in FILES.items():
        original = (TASK / "received" / name).read_bytes()
        active = (ROOT / active_path).read_bytes()
        before, after = original.decode("utf-8"), active.decode("utf-8")
        if sha(original) != expected_hash:
            errors.append(f"Received hash changed: {name}")
        if version not in after.split("Canonical repository path:")[0]:
            errors.append(f"Version/revision mismatch: {active_path}")
        old_sections, new_sections = sections(before), sections(after)
        if list(old_sections) != list(new_sections):
            errors.append(f"Original section topology changed: {active_path}")
        changed = [key for key in old_sections if old_sections[key] != new_sections.get(key)]
        unexpected = sorted(set(changed) - allowed_changes)
        if unexpected:
            errors.append(f"Unapproved changed sections in {active_path}: {unexpected}")
        diff = "".join(difflib.unified_diff(
            before.splitlines(keepends=True), after.splitlines(keepends=True),
            fromfile=f"received/{name}", tofile=active_path,
        ))
        diff_path = HERE / "input-to-active" / f"{name}.diff"
        write_if_changed(diff_path, diff)
        documents.append({
            "canonical_name": name, "active_path": active_path, "version": version,
            "received_sha256": sha(original), "active_sha256": sha(active),
            "received_size": len(original), "active_size": len(active),
            "section_count_including_preamble": len(old_sections),
            "unchanged_sections": [key for key in old_sections if key not in changed],
            "changed_sections": changed, "unexpected_changed_sections": unexpected,
            "diff": diff_path.relative_to(TASK).as_posix(),
        })

    writing_before = (TASK / "received/SMART_CITIES_REPORT_WRITING_GUIDE.md").read_text()
    writing_after = (ROOT / FILES["SMART_CITIES_REPORT_WRITING_GUIDE.md"][0]).read_text()
    old_rows = re.findall(r"(?m)^\| W\d{2} \|.*$", writing_before)
    new_rows = re.findall(r"(?m)^\| W\d{2} \|.*$", writing_after)
    w_checks = old_rows == new_rows and len(new_rows) == 22
    if not w_checks:
        errors.append("W01–W22 rows were changed or lost")

    inventory = {row["path"]: row for row in json.loads((TASK / "starting-protection-inventory.json").read_text())}
    protected = []
    for name in inventory:
        is_template = name.startswith("templates/latex/") and not name.endswith("/README.md")
        is_process_reference = name.startswith("reports/process-report/pre-task1/")
        if not (is_template or is_process_reference) or inventory[name]["type"] != "file":
            continue
        path = ROOT / name
        current_hash = sha(path.read_bytes()) if path.is_file() and not path.is_symlink() else None
        passed = current_hash == inventory[name]["sha256"]
        protected.append({"path": name, "sha256": current_hash, "unchanged": passed})
        if not passed:
            errors.append(f"Protected template/palette/Process reference changed: {name}")

    visual = (ROOT / FILES["SMART_CITIES_VISUAL_SYSTEM.md"][0]).read_text()
    palette_rows = re.findall(r"(?m)^\| ([^|]+) \| `#([0-9A-F]{6})` \|$", sections(visual)["2. Exact P2 · Cloud Sorbet Palette"])
    tex_colors = re.findall(r"\\definecolor\{[^}]+\}\{HTML\}\{([0-9A-F]{6})\}", (ROOT / "templates/latex/common/p2_cloud_sorbet_colors.tex").read_text())
    p2_exact = [value for _, value in palette_rows] == tex_colors
    if not p2_exact:
        errors.append("Visual palette differs from canonical P2 source")

    links = []
    prefix = "/woobowen/Smart_Cities_and_Location_Services/blob/main/"
    for path in [entry[0] for entry in FILES.values()] + NAVIGATION:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", (ROOT / path).read_text()):
            parsed = urlparse(target)
            if parsed.scheme:
                if parsed.netloc != "github.com" or not parsed.path.startswith(prefix):
                    continue
                destination = ROOT / unquote(parsed.path[len(prefix):])
            else:
                destination = (ROOT / Path(path).parent / unquote(parsed.path)).resolve() if parsed.path else ROOT / path
            exists = destination.exists()
            fragment = unquote(parsed.fragment)
            anchor_ok = not fragment or (exists and destination.suffix == ".md" and fragment in anchors(destination.read_text()))
            links.append({"source": path, "target": target, "exists": exists, "anchor_valid": anchor_ok})
            if not exists or not anchor_ok:
                errors.append(f"Unresolved local route: {path} -> {target}")

    result = {
        "review_type": "B_AUTHOR_VALIDATION; independent C is recorded separately",
        "command": ".venv/bin/python evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/governance/validate_governance.py",
        "status": "PASS" if not errors else "INCOMPLETE",
        "documents": documents, "w01_w22_identical": w_checks,
        "p2_values_match_common_source": p2_exact, "p2_role_count": len(palette_rows),
        "protected_template_and_process_files": protected,
        "local_links": links, "errors": errors,
        "scope_limit": "Byte/section/route validation supplements the explicit semantic review; it does not confer Evidence Lock or GPT second-review acceptance.",
    }
    write_if_changed(HERE / "document-validation.json", json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "documents": len(documents), "links": len(links), "protected_files": len(protected), "errors": errors}, ensure_ascii=False))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
