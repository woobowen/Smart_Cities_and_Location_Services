"""Export only visible role tool metadata from this authorized root thread.

The session archive stores some message arguments as opaque encrypted strings.
Their hashes are evidence of the archived representation, not plaintext hashes.
Reasoning, unrelated threads and account history are never exported.
"""
import hashlib
import json
from pathlib import Path

from task1.workflow.io import ROOT, now, write_json

THREAD = "01a0df00-be37-7da0-a34e-aa94db790ca6"
DESTINATION = ROOT / "task1/evidence/goal2/governance_dispatches.json"
NAMES = {"spawn_agent", "followup_task", "send_message", "interrupt_agent"}


def main():
    paths = list((Path.home() / ".codex/sessions").rglob("*" + THREAD + ".jsonl"))
    if len(paths) != 1:
        raise ValueError("EXACT_CURRENT_THREAD_SOURCE_REQUIRED")
    calls, results = [], {}
    for line in paths[0].open(encoding="utf-8"):
        row = json.loads(line)
        if row.get("type") != "response_item":
            continue
        payload = row.get("payload", {})
        if payload.get("type") == "function_call" and payload.get("name") in NAMES:
            args = json.loads(payload["arguments"])
            message = args.get("message", "")
            calls.append({
                "at": row["timestamp"], "tool": payload["name"], "call_id": payload["call_id"],
                "target": args.get("target", args.get("task_name")),
                "message_archive_representation": "opaque_encrypted" if message.startswith("gAAAA") else "visible_text",
                "message_archive_sha256": hashlib.sha256(message.encode()).hexdigest(),
                "message_archive_utf8_bytes": len(message.encode()),
                "plaintext_exported": False,
            })
        elif payload.get("type") == "function_call_output":
            # Save only a result for a previously recognized role call.
            if any(call["call_id"] == payload.get("call_id") for call in calls):
                results[payload["call_id"]] = payload.get("output", "")
    for call in calls:
        output = results.get(call["call_id"])
        call["tool_result_present"] = call["call_id"] in results
        call["tool_result_sha256"] = hashlib.sha256(str(output).encode()).hexdigest() if output is not None else None
    dispatches = [call for call in calls if call["tool"] in {"spawn_agent", "followup_task"}]
    report = {
        "at": now(), "thread_id": THREAD,
        "source": "visible collaboration tool metadata in this exact authorized root thread only",
        "scope": "governance; never experiment model calls",
        "governance_role_dispatches": len(dispatches), "role_dispatches": dispatches,
        "role_messages_and_interrupts": [call for call in calls if call not in dispatches],
        "provider_request_count": "unknown", "tokens": "unavailable", "currency_cost": "unavailable",
        "limitations": [
            "Dispatches count native role task starts, not hidden model requests.",
            "Only root-visible role tools are counted; child-internal model requests are not observable.",
            "Message hashes bind the archived representation; opaque messages are not claimed to be recovered plaintext.",
            "Concrete role work is evidenced separately by A plans, B commands/artifacts and C independent receipts.",
        ],
    }
    write_json(DESTINATION, report)
    print(json.dumps({"governance_role_dispatches": len(dispatches),
                      "messages_and_interrupts": len(calls) - len(dispatches)}))


if __name__ == "__main__":
    main()
