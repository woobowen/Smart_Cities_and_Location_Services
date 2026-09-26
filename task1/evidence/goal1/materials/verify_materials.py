"""Validate the material evidence, without running starter or processing data."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
report_path = OUT / "verification.json"
sources = json.loads((OUT / "extraction_index.json").read_text())
hash_results = []
for item in sources:
    actual = hashlib.sha256((ROOT / item["source"]).read_bytes()).hexdigest()
    hash_results.append({"source": item["source"], "expected": item["sha256"],
                         "actual": actual, "unchanged": actual == item["sha256"]})
syntax = []
for path in sorted(OUT.glob("*.py")):
    ast.parse(path.read_text(), filename=path.name)
    syntax.append({"path": path.name, "status": "PARSE_PASS_ONLY"})
parsed_json = []
for path in sorted(OUT.glob("*.json")):
    if path == report_path:
        continue
    json.loads(path.read_text())
    parsed_json.append(path.name)
links = []
for name in ("README.md", "findings.md", "requirements_sources.md"):
    for target in re.findall(r"\]\(([^)]+)\)", (OUT / name).read_text()):
        if target.startswith(("https://", "http://")):
            continue
        resolved = (OUT / target.split("#")[0]).resolve()
        exists = resolved.exists() or resolved == report_path
        links.append({"file": name, "target": target, "exists": exists})
assert all(item["unchanged"] for item in hash_results), "Supplied source changed"
assert all(item["exists"] for item in links), "Broken material link"
report = {
    "classification": "ENGINEERING_MATERIAL_EVIDENCE_CHECK",
    "command": "python3 task1/evidence/goal1/materials/verify_materials.py",
    "recorded_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "PASS_FOR_MATERIAL_CHECK_ONLY",
    "source_hash_checks": hash_results,
    "syntax_parse": syntax,
    "json_parsed": parsed_json,
    "local_document_links": links,
    "limits": "No algorithm, real-data cleaning, runtime role, or project quality acceptance asserted."
}
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
assert report_path.exists()
print(json.dumps({"status": report["status"], "source_hashes_unchanged": len(hash_results),
                  "python_parsed": len(syntax), "json_parsed": len(parsed_json),
                  "document_links": len(links)}, ensure_ascii=False))
