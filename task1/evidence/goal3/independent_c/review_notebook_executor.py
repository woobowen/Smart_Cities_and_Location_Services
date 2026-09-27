"""C synthetic kernel isolation tests; deliberately zero trajectory processing."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import nbformat

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.goal3.execute_notebook import execute

OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT / "task1/goal3/execute_notebook.py"
    source_before = sha(source)
    target = OUT / "notebook_executor_smoke"
    target.mkdir()
    evidence, observations = [], []
    with tempfile.TemporaryDirectory(prefix="g3-c-kernel-isolation-") as directory:
        cwd = Path(directory)
        code = '''import os, json, importlib.util
from pathlib import Path
assert 'c_persistence_sentinel' not in globals()
c_persistence_sentinel = 'fresh kernel only'
assert os.environ.get('PYTHONPATH') == ''
assert os.environ.get('PYTHONNOUSERSITE') == '1'
assert importlib.util.find_spec('task1') is None, 'Original workspace leaked into an empty archive cwd'
work = Path(os.environ['SC_LAB1_RECOMPUTE_WORK'])
work.mkdir()
data = {'classification': 'SYNTHETIC_KERNEL_ENGINEERING_TEST_ZERO_TRAJECTORIES',
        'pid': os.getpid(), 'cwd': str(Path.cwd()), 'work': str(work),
        'raw_records': 0, 'fresh_sentinel': c_persistence_sentinel}
(work/'observations.json').write_text(json.dumps(data))
print('FRESH_KERNEL_ENGINEERING_TEST')
'''
        second = '''(work/'notebook_receipt.json').write_text(json.dumps({
 'status':'VERIFIED', 'new_model_call_attempts_observed':0,
 'classification':'SYNTHETIC_KERNEL_ENGINEERING_TEST_ZERO_TRAJECTORIES', 'raw_records':0}))'''
        notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(code), nbformat.v4.new_code_cell(second)])
        notebook.cells[0].execution_count = 99
        notebook.cells[0].outputs = [nbformat.v4.new_output('stream', name='stdout', text='STALE_OUTPUT_MUST_DISAPPEAR')]
        path = cwd / "SYNTHETIC_ISOLATION.ipynb"
        nbformat.write(notebook, path)
        for index in range(2):
            folder = target / f"fresh_kernel_{index+1}"
            receipt = execute(path, cwd, cwd / f"work{index+1}", folder)
            assert receipt["status"] == "VERIFIED" and receipt["executed_code_cells"] == receipt["total_code_cells"] == 2
            saved = nbformat.read(folder / path.name, as_version=4)
            assert "STALE_OUTPUT_MUST_DISAPPEAR" not in json.dumps(saved)
            assert [cell.execution_count for cell in saved.cells] == [1, 2]
            observed = json.loads((folder / "artifacts/observations.json").read_text())
            assert Path(observed["cwd"]) == cwd and Path(observed["work"]) == cwd / f"work{index+1}"
            observations.append(observed)
            evidence.append(folder / "execution_receipt.json")
        assert observations[0]["pid"] != observations[1]["pid"]
        bad = cwd / "SYNTHETIC_EXPECTED_FAILURE.ipynb"
        nbformat.write(nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(
            "raise RuntimeError('C_INTENTIONAL_ENGINEERING_FAILURE_PATH_TEST')")]), bad)
        failure_dir = target / "deliberate_synthetic_failure"
        try:
            execute(bad, cwd, cwd / "work_failure", failure_dir)
        except RuntimeError as exc:
            assert str(exc) == "NOTEBOOK_EXECUTION_FAILED_SEE_RECEIPT"
        else:
            raise AssertionError("A failed notebook was accepted")
        failed = json.loads((failure_dir / "execution_receipt.json").read_text())
        assert failed["status"] == "FAILED" and "C_INTENTIONAL_ENGINEERING_FAILURE_PATH_TEST" in failed["failure"]
        assert (failure_dir / bad.name).is_file() and (failure_dir / "failure.txt").is_file()
        evidence.append(failure_dir / "execution_receipt.json")
    assert sha(source) == source_before
    receipt = {"role_context": "/root/c_protocol", "target_id": "notebook_executor_engineering",
        "status": "VERIFIED", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "SYNTHETIC_ENGINEERING_TEST; zero trajectory recomputations; deliberate error is only a failure-handling test",
        "targets": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in [source, *evidence]],
        "checked_components": ["two genuinely separate fresh kernels with different PIDs", "old outputs/execution counts removed",
            "explicit isolated cwd and fresh work paths", "PYTHONPATH cleared/user site disabled/no original task1 import in empty cwd",
            "actual produced JSON artifacts preserved", "actual synthetic cell error retains notebook/traceback and rejects execution"],
        "unchecked_components": ["full submitted Notebook contents and complete raw recompute", "ZIP dependency closure",
            "inner receipt numerical truth; full Notebook C acceptance must independently check data scale and model tripwire"],
        "new_model_calls": 0, "trajectory_recomputations": 0, "kernel_instances": 3,
        "successful_kernel_instances": 2, "expected_failure_kernel_instances": 1,
        "source_unchanged": True, "errors": [],
        "actual_command": ".venv/bin/python task1/evidence/goal3/independent_c/review_notebook_executor.py"}
    (OUT / "notebook_executor_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "trajectory_recomputations", "kernel_instances", "errors")}))


if __name__ == "__main__":
    main()
