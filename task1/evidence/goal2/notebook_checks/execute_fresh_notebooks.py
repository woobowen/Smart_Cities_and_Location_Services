"""Execute existing Goal 2 notebooks in at most two isolated OS workers.

Preparation alone never launches a kernel. --execute and frozen input hashes
are required; the existing generator/executor remain the only notebook writers.
"""
import argparse
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
EV = ROOT / "task1/evidence/goal2"
NAMES = ("01_parameters_and_orders.ipynb", "02_real_modes_and_memory.ipynb",
         "03_candidates_counterexamples_and_cases.ipynb")


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def sources(notebook):
    return [(cell["cell_type"], cell["source"]) for cell in notebook["cells"]]


def preflight(args):
    index_path = EV / "current_runs.json"
    figure_source = ROOT / "task1/scripts/build_goal2_figures.py"
    if digest(index_path) != args.expected_current_sha256:
        raise ValueError("CURRENT_RUNS_HASH_NOT_EXPECTED")
    if digest(figure_source) != args.expected_figure_generator_sha256:
        raise ValueError("FIGURE_SOURCE_HASH_NOT_EXPECTED")
    freeze = read(EV / "evaluation_freeze.json")
    contract = read(ROOT / "task1/config/goal2/contract.json")
    bindings = {"task1/evidence/goal2/current_runs.json": digest(index_path),
                "task1/evidence/goal2/evaluation_freeze.json": digest(EV / "evaluation_freeze.json"),
                "task1/config/goal2/contract.json": freeze["contract_sha256"],
                "task1/evidence/goal2/data/split_manifest.json": freeze["split_sha256"],
                "task1/evidence/goal2/candidate_lock.json": freeze["candidate_lock_sha256"],
                contract["raw_path"]: contract["raw_sha256"],
                "task1/scripts/build_goal2_figures.py": digest(figure_source),
                "task1/scripts/build_goal2_notebooks.py": digest(ROOT / "task1/scripts/build_goal2_notebooks.py"),
                freeze["memory_path"]: freeze["memory_sha256"], **freeze["processing_source_hashes"]}
    for path, sha in bindings.items():
        if digest(ROOT / path) != sha:
            raise ValueError("FROZEN_SOURCE_MISMATCH:" + path)
    index = read(index_path)
    keys = ("parameter_development", "order_development", "memory", "mode_development",
            "evaluation_parameters", "evaluation_orders", "mode_evaluation")
    for key in keys:
        path = EV / "runs" / index[key] / "manifest.json"
        manifest = read(path)
        if manifest["status"] not in ("REVIEW_PENDING", "VERIFIED"):
            raise ValueError("RUN_NOT_COMPLETE:" + key)
        bindings[str(path.relative_to(ROOT))] = digest(path)
    mode_directory = EV / "runs" / index["mode_evaluation"]
    mode_manifest = read(mode_directory / "manifest.json")
    if len(mode_manifest["mode_episodes"]) != 36:
        raise ValueError("THIRTY_SIX_EVALUATION_BATCHES_REQUIRED")
    scopes, batch_counts = defaultdict(list), Counter()
    for entry in mode_manifest["mode_episodes"]:
        path = mode_directory / entry["path"]
        if digest(path) != entry["sha256"]:
            raise ValueError("EPISODE_HASH_MISMATCH")
        episode = read(path)
        scopes[(episode["mode"], episode["episode"])].extend(episode["input_ids"])
        batch_counts[episode["mode"]] += 1
    modes = {"llm-only", "search-only", "llm+search", "llm+memory+search"}
    if set(batch_counts) != modes or set(batch_counts.values()) != {9} or set(scopes) != {(m, e) for m in modes for e in (1, 2, 3)}:
        raise ValueError("INCOMPLETE_FOUR_MODES_THREE_EPISODES")
    for scope in scopes.values():
        if len(scope) != 24 or set(scope) != set(freeze["eval_llm_ids"]):
            raise ValueError("EVALUATION_EPISODE_SCOPE_MISMATCH")
    figure_manifest_path = ROOT / "task1/figures/goal2/figure_manifest.json"
    figure_manifest = read(figure_manifest_path)
    if len(figure_manifest["figures"]) != 11 or figure_manifest["generator_sha256"] != digest(figure_source):
        raise ValueError("CURRENT_ELEVEN_FIGURES_REQUIRED")
    for path, sha in figure_manifest["source_files"].items():
        if digest(ROOT / path) != sha:
            raise ValueError("OFFICIAL_FIGURE_INPUT_CHANGED:" + path)
    for figure in figure_manifest["figures"]:
        for output in [*figure["formats"].values(), figure["pdf_render"]]:
            if digest(figure_manifest_path.parent / output["file"]) != output["sha256"]:
                raise ValueError("OFFICIAL_FIGURE_OUTPUT_CHANGED")
    bindings[str(figure_manifest_path.relative_to(ROOT))] = digest(figure_manifest_path)
    return bindings, freeze


def worker(args):
    from task1.scripts.build_goal2_notebooks import execute_notebooks
    path = Path(args.worker).resolve()
    if path.parent != ROOT / "task1/notebooks/goal2" or path.name not in NAMES:
        raise ValueError("WORKER_NOTEBOOK_NOT_REGISTERED")
    directory = Path(args.output).resolve()
    started, timer = now(), time.perf_counter()
    before = read(path)
    freeze = read(EV / "evaluation_freeze.json")
    memory_path = ROOT / freeze["memory_path"]
    memory_before = digest(memory_path)
    receipt = {"notebook": str(path.relative_to(ROOT)), "started_at": started,
               "command": sys.argv, "pid": os.getpid(), "input_notebook_sha256": digest(path),
               "memory_before_sha256": memory_before, "memory_expected_sha256": freeze["memory_sha256"],
               "temporary_root": os.environ["TMPDIR"], "status": "RUNNING"}
    print(json.dumps({"event": "NOTEBOOK_STARTED", "notebook": path.name, "at": started}), flush=True)
    try:
        assert memory_before == freeze["memory_sha256"]
        original = execute_notebooks([path])
        after = read(path)
        assert sources(before) == sources(after), "NOTEBOOK_SOURCES_CHANGED_DURING_EXECUTION"
        code = [(i, cell) for i, cell in enumerate(after["cells"]) if cell["cell_type"] == "code"]
        assert [cell["execution_count"] for _, cell in code] == list(range(1, len(code) + 1))
        errors = [output for _, cell in code for output in cell.get("outputs", []) if output["output_type"] == "error"]
        assert not errors
        sentinel_setup = [i for i, cell in code if "ExperimentProvider.call = reject_model_call" in "".join(cell["source"])]
        sentinel_asserts = [i for i, cell in code if "assert model_sentinel['calls'] == 0" in "".join(cell["source"])]
        assert len(sentinel_setup) == 1 and len(sentinel_asserts) == 1 and sentinel_setup[0] < sentinel_asserts[0]
        assert digest(memory_path) == memory_before
        receipt.update(status="VERIFIED", execution=original[0], output_notebook_sha256=digest(path),
                       source_cells_unchanged=True, executed_code_cells=len(code), cell_errors=[],
                       new_model_calls=0, model_call_proof={"kind": "successful executed zero-call assertion",
                       "sentinel_setup_cell": sentinel_setup[0], "sentinel_assertion_cell": sentinel_asserts[0]},
                       memory_after_sha256=digest(memory_path), memory_unchanged=True)
    except Exception as error:
        receipt.update(status="FAILED", error_type=type(error).__name__, error=str(error),
                       memory_after_sha256=digest(memory_path))
        traceback.print_exc()
    receipt.update(ended_at=now(), elapsed_monotonic_seconds=time.perf_counter() - timer)
    write_new(directory / "worker_receipt.json", receipt)
    print(json.dumps({"event": "NOTEBOOK_FINISHED", "notebook": path.name,
                      "status": receipt["status"], "seconds": receipt["elapsed_monotonic_seconds"]}), flush=True)
    return 0 if receipt["status"] == "VERIFIED" else 1


def parent(args):
    from task1.scripts.build_goal2_notebooks import build
    from task1.workflow.io import write_json
    bindings, freeze = preflight(args)
    output = Path(args.output).resolve()
    if not output.is_relative_to(EV) or output.exists():
        raise ValueError("NEW_GOAL2_EVIDENCE_DIRECTORY_REQUIRED")
    output.mkdir(parents=True)
    started, timer = now(), time.perf_counter()
    previous = output / "before_generation"
    previous.mkdir()
    for name in NAMES:
        path = ROOT / "task1/notebooks/goal2" / name
        if path.exists():
            shutil.copy2(path, previous / name)
    if (EV / "notebook_execution.json").exists():
        shutil.copy2(EV / "notebook_execution.json", previous / "notebook_execution.json")
    generated = build(execute=False)
    mem_available_kb = next(int(line.split()[1]) for line in Path("/proc/meminfo").read_text().splitlines()
                            if line.startswith("MemAvailable:"))
    jobs = args.jobs if mem_available_kb >= 4 * 1024 * 1024 else 1
    write_new(output / "launch_context.json", {"started_at": started, "command": sys.argv,
              "bindings": bindings, "generated": generated, "requested_jobs": args.jobs,
              "effective_jobs": jobs, "mem_available_kb": mem_available_kb,
              "isolation": "independent OS subprocesses; no threaded execute_notebooks or shared JUPYTER_PATH"})
    # Long parameter and mode recomputations launch first; the shorter candidate
    # notebook uses the next available worker. Each path has exactly one writer.
    pending = deque(NAMES)
    active, receipts = {}, []
    failed = False
    while pending or active:
        while pending and len(active) < jobs and not failed:
            name = pending.popleft()
            directory = output / Path(name).stem
            directory.mkdir()
            temporary = tempfile.mkdtemp(prefix="sc-g2-nb-worker-" + name[:2] + "-")
            environment = os.environ.copy()
            environment.update(TMPDIR=temporary, JUPYTER_RUNTIME_DIR=temporary + "/jupyter-runtime",
                               MPLCONFIGDIR=temporary + "/matplotlib")
            command = [sys.executable, str(Path(__file__).resolve()), "--execute", "--worker",
                       str(ROOT / "task1/notebooks/goal2" / name), "--output", str(directory)]
            log = (directory / "execution.log").open("x")
            process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            active[name] = (process, log, directory, command, now(), time.perf_counter())
            print(json.dumps({"event": "WORKER_DISPATCHED", "notebook": name, "pid": process.pid}), flush=True)
        for name, (process, log, directory, command, at, clock) in list(active.items()):
            exit_code = process.poll()
            if exit_code is None:
                continue
            log.close()
            dispatch = {"command": command, "started_at": at, "ended_at": now(), "exit_code": exit_code,
                        "elapsed_monotonic_seconds": time.perf_counter() - clock,
                        "log": str((directory / "execution.log").relative_to(ROOT))}
            write_new(directory / "dispatch_receipt.json", dispatch)
            path = directory / "worker_receipt.json"
            receipt = read(path) if path.exists() else {"status": "FAILED", "notebook": name,
                                                       "error": "WORKER_EXITED_WITHOUT_RECEIPT"}
            receipt["worker_receipt"] = str(path.relative_to(ROOT)) if path.exists() else None
            receipts.append(receipt)
            failed = failed or exit_code != 0 or receipt["status"] != "VERIFIED"
            print(json.dumps({"event": "WORKER_COLLECTED", "notebook": name, "status": receipt["status"]}), flush=True)
            del active[name]
        if failed and not active:
            break
        if active:
            time.sleep(.5)
    unchanged = all(digest(ROOT / path) == sha for path, sha in bindings.items())
    verified = not failed and len(receipts) == 3 and unchanged
    result = {**generated, "executed": len(receipts) == 3, "status": "VERIFIED" if verified else "FAILED",
              "started_at": started, "ended_at": now(), "elapsed_monotonic_seconds": time.perf_counter() - timer,
              "executions": [r.get("execution", {"notebook": r["notebook"], "status": r["status"]}) for r in receipts],
              "worker_receipts": receipts, "unstarted_notebooks": list(pending), "effective_parallelism": jobs,
              "frozen_inputs_and_sources_unchanged": unchanged, "new_persistent_kernels": 0,
              "new_model_calls": 0 if verified else None,
              "memory_before_sha256": freeze["memory_sha256"],
              "memory_after_sha256": digest(ROOT / freeze["memory_path"]),
              "wrapper_sha256": digest(__file__), "execution_directory": str(output.relative_to(ROOT))}
    write_new(output / "combined_receipt.json", result)
    write_json(EV / "notebook_execution.json", result)
    print(json.dumps({"status": result["status"], "notebooks": len(receipts),
                      "new_model_calls": result["new_model_calls"]}), flush=True)
    return 0 if verified else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=2)
    parser.add_argument("--expected-current-sha256")
    parser.add_argument("--expected-figure-generator-sha256")
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.execute:
        parser.error("Preparation does not execute notebooks; explicit --execute is required.")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if args.worker:
        return worker(args)
    if not args.expected_current_sha256 or not args.expected_figure_generator_sha256:
        parser.error("Execution requires frozen current-runs and figure-generator SHA256 values.")
    return parent(args)


if __name__ == "__main__":
    raise SystemExit(main())
