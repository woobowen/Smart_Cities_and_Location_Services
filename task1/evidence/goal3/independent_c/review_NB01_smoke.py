"""Independent new-kernel execution of the real repaired basic Notebook prefix.

Only the first 12 authored cells (6 code cells) are executed. A clearly identified
C-only observation cell checks actual kernel state. This is not a FULL receipt.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    source=ROOT/'task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb'
    builder=ROOT/'task1/goal3/notebooks.py'
    output=EV/'independent_c/NB01_smoke_attempt2'
    assert not output.exists(),'PRESERVE_EXISTING_SMOKE_USE_NEW_EXPLICIT_RUN'
    output.mkdir()
    source_hash=sha(source);builder_hash=sha(builder)
    full=nbformat.read(source,as_version=4);prefix=full.cells[:12]
    assert len(prefix)==12 and sum(c.cell_type=='code' for c in prefix)==6
    original_sources=[{'cell_index':i,'cell_type':c.cell_type,
        'source_sha256':hashlib.sha256(c.source.encode()).hexdigest()} for i,c in enumerate(prefix)]
    notebook=nbformat.v4.new_notebook(cells=prefix,metadata=full.metadata)
    for c in notebook.cells:
        if c.cell_type=='code':c.outputs=[];c.execution_count=None
    notebook.cells.append(nbformat.v4.new_markdown_cell(
        'C-only engineering observation below; the six preceding code cells are unchanged actual coursework cells. This prefix run is not FULL_RECOMPUTE completion.'))
    notebook.cells.append(nbformat.v4.new_code_cell(
        "assert provider_observation['attempted_new_calls'] == 0\n"
        "assert check['status']=='VERIFIED'\n"
        "assert fig.canvas.__class__.__name__=='FigureCanvasAgg'\n"
        "assert digest(memory_path)==memory_hash_before\n"
        "from task1.evidence.goal3.report_build.smoke_offline_plots import smoke as shared_plot_smoke\n"
        "with contextlib.redirect_stdout(io.StringIO()): shared_plot_smoke(WORK/'shared_offline_plots_smoke')\n"
        "assert provider_observation['attempted_new_calls'] == 0\n"
        "write_json(WORK/'independent_smoke_probe.json', {'classification':'REAL_PILOT_PREFIX_SMOKE_NOT_FULL', "
        "'record_id':pilot['record_id'], 'points':len(pilot['indices']), 'canvas':fig.canvas.__class__.__name__, "
        "'new_model_calls':provider_observation['attempted_new_calls'], 'trace_review':check['status'], "
        "'memory_unchanged':digest(memory_path)==memory_hash_before, 'actual_metrics':example['metrics']})"))
    events=[];started=time.perf_counter()
    def done(cell,cell_index,execute_reply,**kwargs):
        events.append({'cell_index':cell_index,'execution_count':cell.execution_count,
                       'status':execute_reply.get('content',{}).get('status')})
    with tempfile.TemporaryDirectory(prefix='sc-lab1-C-NB01-') as tmp:
        tmp=Path(tmp);work=tmp/'work';ks=tmp/'kernels'/'c-nb01';ks.mkdir(parents=True)
        write(ks/'kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
            'display_name':'Independent C NB01 real prefix smoke','language':'python',
            'env':{'PYTHONPATH':'','PYTHONNOUSERSITE':'1','SC_LAB1_RECOMPUTE_WORK':str(work)}})
        km=KernelManager(kernel_name='c-nb01',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(ks.parent)]))
        client=NotebookClient(notebook,km=km,timeout=180,allow_errors=False,
            resources={'metadata':{'path':str(ROOT)}},on_cell_executed=done,record_timing=True)
        try:
            client.execute(cleanup_kc=True)
        finally:
            nbformat.write(notebook,output/'basic_actual_prefix_executed.ipynb')
            write(output/'kernel_cells.json',events)
        assert len(events)==7 and all(v['status']=='ok' for v in events)
        for name in ['pilot_steps.svg','pilot_steps.png','independent_smoke_probe.json']:
            shutil.copy2(work/name,output/name)
        shutil.copytree(work/'shared_offline_plots_smoke',output/'shared_offline_plots_smoke')
    assert sha(source)==source_hash and sha(builder)==builder_hash
    assert all(hashlib.sha256(notebook.cells[r['cell_index']].source.encode()).hexdigest()==r['source_sha256'] for r in original_sources)
    probe=json.loads((output/'independent_smoke_probe.json').read_text())
    assert probe['record_id']=='246' and probe['new_model_calls']==0 and probe['trace_review']=='VERIFIED'
    with Image.open(output/'pilot_steps.png') as im:
        im.verify()
    with Image.open(output/'pilot_steps.png') as im:
        image_info={'pixels':list(im.size),'dpi':list(im.info.get('dpi',[]))}
        assert min(image_info['dpi'])>=199
    shared=output/'shared_offline_plots_smoke'
    shared_receipt=json.loads((shared/'smoke_receipt.json').read_text())
    assert shared_receipt['status']=='VERIFIED' and shared_receipt['full_notebook_execution']=='NOT_RUN'
    assert shared_receipt['new_model_calls']==0 and shared_receipt['tampered_new_summary']=='REJECTED'
    figures=[]
    for path in sorted(shared.rglob('figure_manifest.json')):
        manifest=json.loads(path.read_text())
        assert manifest['source_sha256']==sha(ROOT/'task1/goal3/offline_plots.py')
        assert manifest['old_summary_or_figure_read_for_plotting'] is False
        assert sha(path.parent/manifest['plot_data_path'])==manifest['plot_data_sha256']
        for entry in manifest['figures']:
            assert set(entry['files'])=={'svg','pdf','png'}
            for fmt,info in entry['files'].items():
                p=path.parent/info['path'];assert sha(p)==info['sha256'] and p.stat().st_size>0
                if fmt=='png':
                    with Image.open(p) as im:assert min(im.info['dpi'])>=299
            figures.append(entry['name'])
    assert len(figures)==len(set(figures))==5
    paths=[source,builder,ROOT/'task1/goal3/offline_plots.py',
        ROOT/'task1/evidence/goal3/report_build/smoke_offline_plots.py',Path(__file__),
        *sorted(p for p in output.rglob('*') if p.is_file())]
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'G3-NB-01:actual_prefix_smoke',
        'classification':'REAL_PILOT_PREFIX_SMOKE_NOT_FULL','at':datetime.now(timezone.utc).isoformat(),
        'targets':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in paths],
        'source_hashes':{'task1/goal3/notebooks.py':builder_hash,
                       'task1/goal3/offline_plots.py':sha(ROOT/'task1/goal3/offline_plots.py'),
                       str(source.relative_to(ROOT)):source_hash},
        'checked_components':['Six unchanged actual code cells from authored first12cells run in a fresh explicit existing-environment kernel',
            'Real exposed pilot246 segmentation/direction/DP and trusted external raw review passed before plot',
            'Actual Agg backend, native SVG and200dpi PNG saved, explicit Image display succeeds without inline backend',
            'Same fresh kernel executes shared offline plot smoke from real exposed inputs: five native SVG/PDF/300dpiPNG figures, true ledger and tampered summary rejection',
            'Separate C observation confirms0 provider calls and frozen memory unchanged'],
        'unchecked_components':['Remaining full Notebook historical/production recomputation cells','Entire teacher ZIP isolation','Final Notebook acceptance'],
        'authored_cells':12,'authored_code_cells':6,'additional_C_observation_code_cells':1,
        'original_cell_sources':original_sources,'kernel_events':events,'image':image_info,
        'pilot_points':probe['points'],'new_model_calls':0,'errors':[],
        'shared_plot_smoke_actual_raw_evaluations':shared_receipt['actual_raw_pipeline_evaluations'],
        'shared_plot_smoke_figures':figures,
        'elapsed_seconds':time.perf_counter()-started,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_NB01_smoke.py'}
    rp=EV/'independent_c/NB01_attempt2_smoke_receipt.json';write(rp,receipt)
    print(json.dumps({'status':'VERIFIED','scope':receipt['classification'],'authored_code_cells':6,
                      'pilot_points':probe['points'],'image':image_info,'receipt_sha256':sha(rp)}))


if __name__=='__main__':main()
