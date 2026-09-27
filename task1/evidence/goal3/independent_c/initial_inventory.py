"""C-only raw/split takeover check; no processing or candidate-result imports."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw_path = ROOT / "task1/作业/作业/traj_dict.json"
    old_split_path = ROOT / "task1/evidence/goal2/data/split_manifest.json"
    old_diagnostics_path = ROOT / "task1/evidence/goal2/data/raw_diagnostics.json"
    raw = json.loads(raw_path.read_text())
    old_split = json.loads(old_split_path.read_text())
    groups = collections.defaultdict(list)
    for rid, record in raw.items():
        canonical = json.dumps(record, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":"), allow_nan=False)
        groups[hashlib.sha256(canonical.encode()).hexdigest()].append(rid)
    all_ids = sum(old_split["splits"].values(), [])
    observations = {
        "raw_sha256": sha(raw_path),
        "raw_records": len(raw),
        "raw_points": sum(len(record[0]) for record in raw.values()),
        "alignment_errors": sum(len(r[0]) != len(r[1]) for r in raw.values()),
        "empty_records": sum(not r[0] for r in raw.values()),
        "duplicate_groups": [ids for ids in groups.values() if len(ids) > 1],
        "inherited_split_sha256": sha(old_split_path),
        "inherited_split_counts": {k: len(v) for k, v in old_split["splits"].items()},
        "inherited_split_overlap": len(all_ids) - len(set(all_ids)),
        "inherited_split_scope_equal_raw": set(all_ids) == set(raw),
        "inherited_diagnostics_hash_matches": sha(old_diagnostics_path) == old_split["diagnostics_sha256"],
        "inherited_quantiles": old_split["quantiles"],
        "inherited_population_strata": old_split["population_strata"],
        "higher_entity_identity": "NO_INDEPENDENTLY_VERIFIED_HIGHER_ENTITY",
    }
    errors = []
    expected = {
        "raw_sha256": "c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3",
        "raw_records": 11386, "raw_points": 1173410,
        "alignment_errors": 0, "empty_records": 0,
        "inherited_split_overlap": 0,
        "inherited_split_scope_equal_raw": True,
        "inherited_diagnostics_hash_matches": True,
    }
    for key, value in expected.items():
        if observations[key] != value:
            errors.append({"field": key, "expected": value, "actual": observations[key]})
    files = [
        "AGENTS.md", "docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md",
        "task1/evidence/goal3/USER_PROMPT.md", "task1/config/goal2/contract.json",
        "task1/config/conditional_planar.json", "task1/docs/goal1/CONTRACTS.md",
        "task1/docs/goal2/CONTRACT.md", "task1/workflow/g2_data.py",
        "task1/workflow/g2_pipeline.py", "task1/workflow/g2_metrics.py",
        "task1/workflow/g2_selection.py", "task1/workflow/coordinates.py",
        "task1/evidence/goal2/c_contract/independent_numeric.py",
    ]
    receipt = {
        "reviewer": "native Codex sub-agent /root/c_protocol",
        "reviewer_role": "C; no core implementation or contract authorship",
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "VERIFIED" if not errors else "REJECTED",
        "target": "raw original and inherited Goal 2 split only",
        "command": ".venv/bin/python task1/evidence/goal3/independent_c/initial_inventory.py",
        "source_hashes": {name: sha(ROOT / name) for name in files},
        "observations": observations, "errors": errors,
        "checked": ["raw byte identity", "actual complete raw counts", "record alignment",
                    "complete raw canonical duplicate groups", "inherited split exact partition",
                    "inherited diagnostics byte binding"],
        "unchecked": ["new Goal 3 contract and split", "candidate outcomes",
                      "source datum", "independent vehicle/person identity",
                      "raw descriptor mathematical recomputation", "Goal 3 publication"],
        "method_effect_exposure": "NONE; raw structure and inherited descriptor inventory only",
        "git_head_at_review": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (OUT / "initial_inventory_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "observations": observations, "errors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()
