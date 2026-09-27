"""Close the notebook plotting compatibility repair, not the FULL notebook task."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    state=read(EV/'goal_state.json');issue=state['issues']['G3-NB-01']
    assert issue['status']=='REGRESSION_PENDING' and issue['attempts']==2
    assert issue['repairer']!='/root/c_protocol'
    targets={t['path']:t['sha256'] for t in issue['repair_targets']}
    smoke_path=EV/'independent_c/NB01_attempt2_smoke_receipt.json';smoke=read(smoke_path)
    assert smoke['status']=='VERIFIED' and smoke['classification']=='REAL_PILOT_PREFIX_SMOKE_NOT_FULL'
    assert smoke['authored_code_cells']==6 and smoke['pilot_points']==108 and smoke['new_model_calls']==0
    assert smoke['shared_plot_smoke_actual_raw_evaluations']==19 and len(smoke['shared_plot_smoke_figures'])==5
    assert all(e['status']=='ok' for e in smoke['kernel_events'])
    for t in smoke['targets']:targets[t['path']]=t['sha256']
    impact_path=EV/'repairs/NB01_attempt2_impact.json';impact=read(impact_path)
    system=ROOT/'task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb'
    assert sha(system)==impact['system_notebook_bytes_unchanged']
    interrupted=EV/'notebook_verification/repository_system_full/execution_receipt.json';old=read(interrupted)
    assert old['status']=='FAILED' and old['notebook_source_sha256']==sha(system)
    assert 'KeyboardInterrupt' in old['failure']
    original_failure=EV/'notebook_verification/repository_basic_full/execution_receipt.json'
    assert read(original_failure)['status']=='FAILED'
    first_failure=EV/'independent_c/NB01_first_repair_failure_receipt.json'
    assert read(first_failure)['status']=='REJECTED'
    frozen=read(EV/'production_freeze.json')
    for name,value in frozen['processing_source_hashes'].items():assert sha(ROOT/name)==value
    for p in (smoke_path,impact_path,system,interrupted,original_failure,first_failure,Path(__file__)):
        targets[str(p.relative_to(ROOT))]=sha(p)
    for name,value in targets.items():assert sha(ROOT/name)==value,name
    receipt={'role_context':'/root/c_protocol','issue_id':'G3-NB-01','status':'VERIFIED',
        'at':datetime.now(timezone.utc).isoformat(),'targets':[{'path':p,'sha256':h} for p,h in sorted(targets.items())],
        'source_hashes':{**smoke['source_hashes'],**frozen['processing_source_hashes']},
        'checked_components':['Actual basic inline failure and first Agg-only failed C regression retained',
            'Second patch replaces only pyplot/REPL construction with direct Figure/FigureCanvasAgg; processing/metrics/frozen contract bytes unchanged',
            'Fresh kernel six actual authored code cells plus explicit C observation: pilot246 real processing, plot SVG/200dpiPNG and explicit display pass',
            'Same fresh kernel exercises shared five figure types on19 real exposed pipeline evaluations; native formats/hash/data reductions and forged summary rejection pass',
            'Shared-source dependent system FULL was explicitly interrupted and savedFAILED before repair; its unmodified Notebook source hash matches',
            'Exact parent-submitted repair targets and independent smoke artifacts checked; no model calls or new dependencies'],
        'unchecked_components':['The remaining full Notebook recomputations','Isolated ZIP full executions','Final Notebook/Package task acceptance'],
        'engineering_issue_closed':'Notebook plotting API compatibility only',
        'parent_task_must_resume_as_pending':'notebooks',
        'full_notebook_status':'NOT_YET_VERIFIED; two new full executions required',
        'processing_math_or_selection_changed':False,'new_dependencies':[],'new_model_calls':0,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_NB01_closure.py'}
    output=EV/'independent_c/G3-NB-01_closure.json'
    with output.open('x') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','issue':'G3-NB-01','targets':len(targets),'receipt_sha256':sha(output)}))


if __name__=='__main__':main()
