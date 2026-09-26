"""C-only fresh-kernel SETUP/sentinel review, not full Notebook acceptance."""
import json
import os
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from task1.scripts import build_goal2_notebooks as subject
from task1.workflow.io import write_json, digest, now

OUT = Path(__file__).resolve().parent


def main():
    code_count = 0
    for builder in (subject.parameters_notebook, subject.modes_notebook, subject.candidates_notebook):
        for index, cell in enumerate(builder()):
            if cell.cell_type == "code":
                compile(cell.source, builder.__name__ + ":cell" + str(index), "exec")
                code_count += 1
    checks = '''assert model_sentinel == {'calls': 0}
assert MODE == 'RECOMPUTE' and ENABLE_LIVE is False
assert 'pandas' not in globals()
try:
    ExperimentProvider().call('ENGINEERING_TEST_MUST_NEVER_REACH_PROVIDER', WORK/'forbidden', request_id='fixture', purpose='ENGINEERING_TEST')
except RuntimeError as error:
    assert str(error) == 'RECOMPUTE_FORBIDS_NEW_MODEL_CALLS'
else:
    raise AssertionError('provider sentinel did not reject')
assert model_sentinel == {'calls': 1}
assert not (WORK/'forbidden').exists()
shutil.rmtree(WORK)
print('C_SETUP_SENTINEL_VERIFIED; blocked_test_attempts=1; actual_model_calls=0')
'''
    notebook = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell("C independent ENGINEERING_TEST: SETUP and zero-call sentinel only; complete notebooks remain unchecked."),
        nbformat.v4.new_code_cell(subject.SETUP), nbformat.v4.new_code_cell(checks)])
    with tempfile.TemporaryDirectory(prefix="c-notebook-kernel-", dir=OUT) as temporary:
        kernel = Path(temporary) / "kernels/c-review"
        kernel.mkdir(parents=True)
        (kernel / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                                                       "display_name": "C existing environment", "language": "python"}))
        previous = os.environ.get("JUPYTER_PATH")
        os.environ["JUPYTER_PATH"] = temporary + (os.pathsep + previous if previous else "")
        try:
            NotebookClient(notebook, timeout=120, kernel_name="c-review", resources={"metadata": {"path": str(ROOT)}}).execute()
        finally:
            if previous is None:
                os.environ.pop("JUPYTER_PATH", None)
            else:
                os.environ["JUPYTER_PATH"] = previous
    notebook_path = OUT / "notebook_setup_engineering_test.ipynb"
    if notebook_path.exists():
        raise ValueError("C_REVIEW_EXISTS_NO_OVERWRITE")
    nbformat.write(notebook, notebook_path)
    target = "task1/scripts/build_goal2_notebooks.py"
    receipt = {"status": "VERIFIED", "role_context": "/root/c_contract", "issue_id": "G2-B-NOTEBOOK-001", "parent_task": "notebooks",
               "reviewed_at": now(), "targets": [{"path": target, "sha256": digest(ROOT / target)}], "source_hashes": {target: digest(ROOT / target)},
               "checked_components": ["fault_rejected", "valid_receipt_accepted", "source_epoch", "fresh_kernel_SETUP_imports", "real_provider_call_sentinel", "all_notebook_code_cells_compile"],
               "unchecked_components": ["complete three Notebook Restart Kernel Run All", "full deterministic recompute", "figures and real mode evidence cells", "entire notebooks task acceptance"],
               "compiled_code_cells": code_count, "actual_model_calls": 0, "blocked_fault_test_attempts": 1,
               "fresh_kernels": 1, "kernel_environment": "existing .venv, temporary kernel specification, no dependency installation",
               "evidence": [{"path": str(notebook_path.relative_to(ROOT)), "sha256": digest(notebook_path)},
                            {"path": str(Path(__file__).relative_to(ROOT)), "sha256": digest(Path(__file__))}],
               "limit": "This closes the missing dependency / missing active sentinel implementation defects only. Full Notebook execution remains pending."}
    write_json(OUT / "notebook_setup_closure_receipt.json", receipt, exclusive=True)
    print({key: receipt[key] for key in ("status", "compiled_code_cells", "actual_model_calls", "blocked_fault_test_attempts", "fresh_kernels")})


if __name__ == "__main__":
    main()
