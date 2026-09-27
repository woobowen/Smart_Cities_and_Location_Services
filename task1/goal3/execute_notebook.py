"""Execute a submitted notebook in a fresh explicit kernel and preserve real evidence."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time
import traceback

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

from task1.workflow.io import digest, write_json, now


def execute(path, cwd, work, evidence):
    path, cwd, work, evidence = [Path(p).resolve() for p in (path, cwd, work, evidence)]
    if evidence.exists() or work.exists():
        raise ValueError('FRESH_NOTEBOOK_WORK_AND_EVIDENCE_DIRECTORIES_REQUIRED')
    evidence.mkdir(parents=True)
    notebook = nbformat.read(path, as_version=4)
    source_hash = digest(path)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []; cell.execution_count = None
    events = []
    start = time.perf_counter(); status = 'RUNNING'; failure = None

    def cell_done(cell, cell_index, execute_reply, **kwargs):
        event = {'at': now(), 'cell_index': cell_index,
                 'execution_count': cell.execution_count,
                 'kernel_status': execute_reply.get('content', {}).get('status')}
        events.append(event); write_json(evidence/'cells.json', events)
        print(json.dumps(event), flush=True)

    with tempfile.TemporaryDirectory(prefix='sc-lab1-kernelspec-') as temp:
        folder = Path(temp)/'sc-lab1'; folder.mkdir()
        spec = {'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                'display_name': 'Experiment 1 explicit existing Python', 'language': 'python',
                'env': {'PYTHONPATH': '', 'PYTHONNOUSERSITE': '1',
                        'SC_LAB1_RECOMPUTE_WORK': str(work)}}
        write_json(folder/'kernel.json', spec)
        manager = KernelManager(kernel_name='sc-lab1', kernel_spec_manager=KernelSpecManager(kernel_dirs=[temp]))
        client = NotebookClient(notebook, km=manager, timeout=None, allow_errors=False,
            record_timing=True, resources={'metadata': {'path': str(cwd)}}, on_cell_executed=cell_done)
        try:
            client.execute(cleanup_kc=True)
            result = json.loads((work/'notebook_receipt.json').read_text())
            if result.get('status') != 'VERIFIED' or result.get('new_model_call_attempts_observed') != 0:
                raise ValueError('NOTEBOOK_FULL_RECEIPT_NOT_VERIFIED')
            status = 'VERIFIED'
        except BaseException:
            failure = traceback.format_exc(); status = 'FAILED'
            (evidence/'failure.txt').write_text(failure)
        finally:
            executed = evidence/path.name
            nbformat.write(notebook, executed)
    preserved = []
    if work.exists():
        # Recomputed full trace hashes match the canonical production shards.
        # Preserve their manifests/receipts; avoid another identical raw/trace copy in Git.
        for p in sorted(work.rglob('*')):
            if p.is_file() and p.suffix.lower() in ('.json', '.csv', '.svg', '.pdf', '.png', '.txt'):
                rel = p.relative_to(work); dest = evidence/'artifacts'/rel
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
                preserved.append({'path': str(dest.relative_to(evidence)), 'sha256': digest(dest)})
    receipt = {'status': status, 'started_from_clean_outputs_and_new_kernel': True,
               'notebook_source_sha256': source_hash, 'executed_notebook_sha256': digest(executed),
               'python_executable': sys.executable, 'kernel_cwd': str(cwd),
               'temporary_work_directory': str(work), 'elapsed_seconds': time.perf_counter()-start,
               'executed_code_cells': len(events), 'total_code_cells': sum(c.cell_type == 'code' for c in notebook.cells),
               'preserved_artifacts': preserved, 'at': now(),
               'failure': failure, 'source_sha256': digest(__file__)}
    write_json(evidence/'execution_receipt.json', receipt)
    print(json.dumps({k: receipt[k] for k in ('status', 'executed_code_cells', 'total_code_cells', 'elapsed_seconds')}), flush=True)
    if status != 'VERIFIED':
        raise RuntimeError('NOTEBOOK_EXECUTION_FAILED_SEE_RECEIPT')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('notebook', type=Path)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args(); execute(args.notebook, args.cwd, args.work, args.evidence)
