"""C verifies an already executed engineering capability call; no model calls."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from task1.workflow.g2_provider import schema
from task1.workflow.provider import parse_response, visible_events, ProviderError


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory = ROOT / "task1/evidence/goal2/provider_smoke/attempt01"
    read = lambda name: json.loads((directory / name).read_text())
    receipt, response, request = read("receipt.json"), read("response.json"), read("input.json")
    events = [json.loads(line) for line in (directory / "visible_events.jsonl").read_text().splitlines()]
    checks = []
    def check(name, condition):
        checks.append({"name": name, "passed": bool(condition)})
    check("input_binding", sha(directory / "input.json") == receipt["input_sha256"])
    check("response_binding", sha(directory / "response.json") == receipt["response_sha256"])
    check("events_binding", sha(directory / "visible_events.jsonl") == receipt["events_sha256"])
    check("registered_schema", request["schema"] == schema())
    decoded, thread, usage = parse_response(events, schema(), receipt["exit_code"])
    check("actual_visible_response", decoded == response and receipt["thread_id"] == thread and receipt["usage"] == usage)
    check("one_visible_dispatch_not_eight_or_provider_request_count", len([e for e in events if e["type"] == "thread.started"]) == 1
          and len([e for e in events if e["type"] == "turn.completed"]) == 1 and receipt["underlying_requests"] == "unknown")
    check("probe_only", receipt["purpose"] == "ENGINEERING_PROVIDER_CAPABILITY_PROBE" and response == {"records": []})
    command = receipt["command"]
    check("read_only_ephemeral", "--ephemeral" in command and "--ignore-user-config" in command
          and "--strict-config" in command and command[command.index("--sandbox") + 1] == "read-only")
    for name in ("shell_tool", "unified_exec", "code_mode_host", "apps", "plugins", "multi_agent", "hooks", "memories",
                 "shell_snapshot", "browser_use", "browser_use_external", "computer_use", "image_generation"):
        check("disabled:" + name, any(command[i:i + 2] == ["--disable", name] for i in range(len(command) - 1)))
    check("project_docs_and_web_disabled", "project_doc_max_bytes=0" in command and 'web_search="disabled"' in command)
    check("no_visible_model_tools", not any(e["type"] in ("unexpected_tool", "unexpected_event", "error", "turn.failed") for e in events))
    altered = {
        "unexpected_tool": events + [{"type": "unexpected_tool", "item_type": "command_execution"}],
        "duplicate_turn": events + [deepcopy(events[-1])],
        "missing_turn": [e for e in events if e["type"] != "turn.completed"],
        "provider_error": events + [{"type": "error", "message": "ENGINEERING_TEST"}],
    }
    for name, trace in altered.items():
        try:
            parse_response(trace, schema(), 0)
            rejected = False
        except ProviderError:
            rejected = True
        check("fault_rejected:" + name, rejected)
    converted = visible_events(json.dumps({"type": "item.completed", "item": {"id": "fixture", "type": "command_execution"}}))
    check("hidden_tool_sentinel", converted[0]["type"] == "unexpected_tool")
    report = {"role_context": "/root/c_contract", "status": "VERIFIED" if all(c["passed"] for c in checks) else "REJECTED",
              "classification": "INDEPENDENT_C_ENGINEERING_PROVIDER_REVIEW_NOT_MODE_ACCEPTANCE",
              "at_utc": datetime.now(timezone.utc).isoformat(),
              "targets": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in
                          (directory / "receipt.json", directory / "input.json", directory / "response.json", directory / "visible_events.jsonl")],
              "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in
                                (ROOT / "task1/workflow/g2_provider.py", ROOT / "task1/workflow/provider.py")},
              "checked_components": ["actual_smoke_response_and_usage", "hash_bindings", "read_only_ephemeral_cli_flags",
                                     "disabled_tools", "unexpected_tool_failure", "completed_turn_uniqueness", "counter_classification"],
              "unchecked_components": ["actual_four_mode_data_episodes", "batch_card_scope_enforcement", "candidate_budget_enforcement",
                                       "memory_eligibility_and_consumption", "feedback_causality", "hidden_provider_request_count"],
              "checks": checks, "experiment_model_dispatches_in_probe": 0, "engineering_model_dispatches_observed": 1,
              "new_model_calls_for_this_review": 0, "underlying_provider_requests": "unknown"}
    (OUT / "provider_receipt.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "checks": len(checks), "failed": [c for c in checks if not c["passed"]]}))


if __name__ == "__main__":
    main()
