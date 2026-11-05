"""Execute delivered notebooks in a fresh project kernel; retain actual attempt evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import time
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('notebook',type=Path);parser.add_argument('--attempt',type=int,default=1)
    a=parser.parse_args();path=a.notebook.resolve();evidence=ROOT/'task2/evidence/notebook_execution';evidence.mkdir(parents=True,exist_ok=True)
    before=hashlib.sha256(path.read_bytes()).hexdigest()
    notebook=nbformat.read(path,as_version=4)
    start=time.perf_counter();error=None
    try:
        NotebookClient(notebook,timeout=1800,kernel_name='smartcities_dispatch',
                       resources={'metadata':{'path':str(path.parent)}}).execute()
    except Exception as exc:
        error=f'{type(exc).__name__}: {exc}'
    target=path if error is None else evidence/f'{path.stem}_attempt{a.attempt}_failed.ipynb'
    nbformat.write(notebook,target)
    record={'notebook':str(path.relative_to(ROOT)),'attempt':a.attempt,'input_sha256':before,
            'output':str(target.relative_to(ROOT)),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'kernel':'smartcities_dispatch','fresh_kernel':True,'actual_completed_code_cells':sum(c.cell_type=='code' and c.execution_count is not None for c in notebook.cells),
            'total_code_cells':sum(c.cell_type=='code' for c in notebook.cells),
            'runtime_seconds':time.perf_counter()-start,'recorded_utc':datetime.now(timezone.utc).isoformat(),
            'error':error,'status':'PASSED' if error is None else 'FAILED'}
    (evidence/f'{path.stem}_attempt{a.attempt}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print(json.dumps(record,ensure_ascii=False,indent=2),flush=True)
    if error:raise SystemExit(1)


if __name__=='__main__':main()
