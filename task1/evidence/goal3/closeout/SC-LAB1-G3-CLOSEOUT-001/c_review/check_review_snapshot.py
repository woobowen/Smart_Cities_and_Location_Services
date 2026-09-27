"""Independently verify immutable review inputs and their event-time boundary.

The snapshots are observations. Later, valid controller events may advance the
one active state; this checker does not silently rewrite the observation or
require active bytes to remain forever equal to the observed bytes.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
CLOSEOUT = HERE.parent
SNAPSHOTS = CLOSEOUT / "review_input_snapshot"
ANCHOR = "1a5e26b43189aef64a46f8986b3cc442fa50d2c5"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def at(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None, value
    return parsed


def check_events(events):
    previous = "ROOT"
    previous_time = None
    for event in events:
        assert event["previous_hash"] == previous
        payload = {k: v for k, v in event.items() if k != "hash"}
        calculated = hashlib.sha256(json.dumps(payload, ensure_ascii=False,
            sort_keys=True, allow_nan=False, separators=(",", ":")).encode()).hexdigest()
        assert calculated == event["hash"], (event["kind"], event["at"])
        stamp = at(event["at"])
        assert previous_time is None or stamp >= previous_time
        previous, previous_time = event["hash"], stamp
    return previous


def check_snapshot():
    manifest_path = SNAPSHOTS / "SNAPSHOT_MANIFEST.json"
    manifest = read(manifest_path)
    observed = at(manifest["created_at"])
    checked_at = datetime.now(timezone.utc)
    assert observed <= checked_at
    assert manifest["purpose"] == "IMMUTABLE_REVIEW_INPUT_SNAPSHOT_NOT_ACTIVE_STATE"
    active_paths = ["task1/evidence/goal3/requirements.json", "task1/evidence/goal3/goal_state.json"]
    assert manifest["active_state_links"] == active_paths + [str((CLOSEOUT / "ACCEPTANCE_MATRIX.json").relative_to(ROOT))]
    assert len(manifest["sources"]) == 2
    assert {r["active_path"] for r in manifest["sources"]} == set(active_paths)
    copied = {}
    for row in manifest["sources"]:
        expected_path = SNAPSHOTS / Path(row["active_path"]).name
        assert row["snapshot_path"] == str(expected_path.relative_to(ROOT))
        assert expected_path.is_file() and not expected_path.is_symlink()
        assert sha(expected_path) == row["sha256"]
        copied[Path(row["active_path"]).name] = read(expected_path)

    frozen, active = copied["goal_state.json"], read(ROOT / active_paths[1])
    frozen_tip, active_tip = check_events(frozen["events"]), check_events(active["events"])
    assert active["events"][:len(frozen["events"])] == frozen["events"], "Snapshot history is not a prefix of active history"
    assert all(at(e["at"]) <= observed for e in frozen["events"])
    later = active["events"][len(frozen["events"]):]
    assert all(at(e["at"]) >= observed for e in later), "Claimed copy time crosses an omitted earlier event"
    for task, expected in {"figures": "VERIFIED", "notebooks": "VERIFIED",
            "experiment_report": "VERIFIED", "process_report": "BLOCKED_EXTERNAL", "package": "VERIFIED"}.items():
        assert frozen["tasks"][task]["status"] == expected, (task, frozen["tasks"][task]["status"])
    for issue in ("CL-C01", "CL-C02", "CL-C03"):
        assert frozen["issues"][issue]["status"] == "VERIFIED", (issue, frozen["issues"][issue]["status"])

    requirements = copied["requirements.json"]
    historical = json.loads(subprocess.check_output(["git", "show", f"{ANCHOR}:task1/evidence/goal3/requirements.json"], cwd=ROOT))
    old_by_id = {r["id"]: r for r in historical["requirements"]}
    assert {r["id"] for r in requirements["requirements"]} == set(old_by_id)
    for row in requirements["requirements"]:
        assert row["previous_acceptance"] == old_by_id[row["id"]], row["id"]
        assert at(row["status_as_of"]) <= observed
    assert at(requirements["updated_at"]) <= observed
    for state in (requirements, frozen):
        assert state["Identity"] == "VERIFIED"
        assert state["Understanding"] == "LEARNING"
        assert state["Submission"] == "NOT_READY"
        assert state["GPT_SECOND_REVIEW"] == "PENDING"
    assert requirements["New_GPT_SECOND_REVIEW"] == "PENDING"
    assert requirements["Deliverable"] == "FINAL_REVIEW"
    assert requirements["Process_Evidence"] == "BLOCKED_EXTERNAL_ORIGINALS_SPEC_LOCK"
    out = {
        "role_context": "/root/c_independent", "status": "PASS_IN_STATED_SCOPE",
        "checked_at": checked_at.isoformat(), "snapshot_observed_at": manifest["created_at"],
        "manifest": {"path": str(manifest_path.relative_to(ROOT)), "sha256": sha(manifest_path)},
        "immutable_sources": manifest["sources"],
        "snapshot_events_verified": len(frozen["events"]), "snapshot_event_tip": frozen_tip,
        "active_events_observed": len(active["events"]), "active_event_tip_observed": active_tip,
        "later_active_events_count": len(later),
        "active_observation_not_source_binding": {"path": active_paths[1], "observed_sha256": sha(ROOT / active_paths[1])},
        "historical_requirements_preserved_exactly": len(old_by_id), "historical_anchor": ANCHOR,
        "scope": "Both actual snapshot bytes, explicit non-active semantics, complete Journal hash chains, observed snapshot event prefix and true timestamp boundary, leaf acceptance before copy, all20 unchanged historical previous_acceptance objects, and separate current user/evidence/submission states.",
        "limit": "A snapshot freezes a real prior observation, not the final active state or future publication. New later events are allowed only as verifiable appended events. Final active paths remain authoritative.",
    }
    (HERE / "review_input_snapshot_receipt.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    return out


if __name__ == "__main__":
    result = check_snapshot()
    print(json.dumps({k: result[k] for k in ("status", "snapshot_observed_at", "snapshot_events_verified", "later_active_events_count")}))
