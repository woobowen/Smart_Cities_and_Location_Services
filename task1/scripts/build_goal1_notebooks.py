"""Build the two current working notebooks; default execution never calls a model."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import tempfile

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'task1/notebooks'
REVISION = ROOT / 'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001'


def markdown(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


SETUP = """from pathlib import Path
import json, sys, html
from IPython.display import display, HTML, Image
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'AGENTS.md').is_file())
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from task1.workflow.io import DATA, CONFIG, EVIDENCE, read_json, digest, object_hash
from task1.workflow.tools import execute_tool
from task1.scripts.build_complete_figures import load_current
REVISION = EVIDENCE/'revisions/SC-LAB1-G1-COMPLETE-001'
current, manifest, saved_baseline = load_current()
policy = read_json(CONFIG)
record_ids = manifest['record_scope']
raw = read_json(DATA)
assert digest(DATA) == manifest['input_sha256'] == policy['raw_sha256']

def show_table(rows):
    if not rows:
        print('No rows')
        return
    columns = list(rows[0])
    def cell(value):
        return html.escape(json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value))
    header = ''.join('<th style="text-align:left;padding:6px">'+cell(c)+'</th>' for c in columns)
    body = ''.join('<tr>'+''.join('<td style="padding:6px;vertical-align:top">'+cell(row.get(c, ''))+'</td>' for c in columns)+'</tr>' for row in rows)
    display(HTML('<table><thead><tr>'+header+'</tr></thead><tbody>'+body+'</tbody></table>'))

print('Current run:', current['run_id'])
print('Processing CODE_SHA:', manifest['code_sha'])
print('Raw SHA256:', digest(DATA))
print('Fixed development record scope:', record_ids)
print('Default mode: RECOMPUTE; new model calls: 0')"""


def save(name, cells):
    for index, cell in enumerate(cells):
        cell['id'] = hashlib.sha256((str(index) + cell['cell_type'] + cell['source']).encode()).hexdigest()[:12]
    nb = nbf.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
        'sc_goal1': {'classification': 'WORKING_NOTEBOOK', 'default_mode': 'RECOMPUTE',
                     'current_pointer': 'task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/current_run.json',
                     'generator': 'task1/scripts/build_goal1_notebooks.py'}})
    nbf.validate(nb)
    nbf.write(nb, OUT / name)


def baseline_notebook():
    return [
        markdown('# Goal 1：条件化真实 pilot、基线与独立审核\n\n'
                 '对应教师《作业1轨迹数据预处理》Notebook 的工作版。固定使用记录 0、1、2、246、256、306、352，'
                 '从原始 JSON 重新运行获批的基础链，不改教师文件。源坐标基准仍为 **UNVERIFIED**；'
                 '局部工作坐标是明确授权的分析假设，不是源 CRS 事实或坐标偏移校正。\n\n'
                 '默认 **Restart Kernel → Run All** 只执行确定性工具及审核，新增模型调用为 0。'
                 '本文件是工作材料，正式 Experiment / Process Report 尚未定稿。'),
        code(SETUP),
        markdown('## 数据范围与坐标语义\n\n原始结构声明为 `(longitude, latitude)` 度与 Unix 秒。'
                 '没有文件绑定的 datum / offset 说明，因此不指定源 EPSG、不叠底图、不声称绝对定位精度。'
                 '固定局部 ENU 模型将原始角度映射为米制工作坐标；椭球形状和零高度是分析假设。'
                 '原始值、原始索引、适配器版本及 raw→working 关系保留在可信参考链中。'),
        code("from task1.workflow.pipeline import trusted_real_reference\n"
             "from task1.workflow.evaluation import review_baseline\n"
             "reference, contract, provenance = trusted_real_reference(raw, record_ids, policy)\n"
             "assert contract['source_crs'] == 'UNVERIFIED'\n"
             "print(json.dumps({k:contract[k] for k in ['contract_id','approval','source_crs','classification','units','adapter_version','analysis_model','limitations']}, ensure_ascii=False, indent=2))\n"
             "show_table([{'record_id':r['record_id'], 'original_points':len(r['indices']), 'raw_record_sha256':r['raw_record_sha256']} for r in reference])"),
        markdown('## 固定方法与参数\n\n顺序为分段→独立过滤→方向去噪→DP。时间/距离分段使用严格 `>`，'
                 '阈值等号不切；负时间差单独切分，右点进入新片段。过滤分别检查点数和片段累积长度。'
                 '方向规则对当前输入片段计算一次：比较本点 outgoing edge 与前后 outgoing edge 的圆周差，'
                 '两侧都严格超过阈值才标记，随后同时删除；端点及无法计算的窗口保留，并重算下游特征。'
                 'DP 使用有限线段和原始索引区间。\n\n'
                 '参数沿用 starter 参考值，未开展参数搜索；95 m 教学例子未混入 400 m 距离阈值。'),
        code("show_table([{'parameter':key, 'value':value} for key,value in contract['parameters'].items()])\n"
             "print('Order:', contract['order'])\n"
             "print('Direction schedule:', contract['method'])\n"
             "print('Approval source:', contract['approval_source'])\n"
             "print('Reference provenance:', json.dumps(provenance, ensure_ascii=False, indent=2))"),
        markdown('## 从原始输入实际重算并独立审核\n\n下面调用实际 baseline 工具。审核器接收候选之外的完整输入、'
                 '预先固定合同及 provenance，不从候选 input 或候选容差取得答案；实际 clean/final 值、'
                 '断点、过滤理由、方向决策、DP 区间和终态账本均进入核对。保存产物仅作为重算后的版本对照。'),
        code("baseline = execute_tool('baseline', record_ids, policy)\n"
             "assert baseline['status'] == 'VERIFIED', baseline.get('reason')\n"
             "audit = review_baseline(baseline, reference, contract, provenance)\n"
             "assert audit['status'] == 'VERIFIED' and not audit['unchecked_components'], audit\n"
             "assert object_hash(baseline) == manifest['artifacts']['baseline']['output_sha256']\n"
             "assert baseline['classification'] == 'CURRENT_RUN_CONDITIONAL_ANALYSIS'\n"
             "assert digest(DATA) == manifest['input_sha256']\n"
             "print('Fresh baseline:', baseline['status'], '| independent review:', audit['status'])\n"
             "print('Checked:', audit['checked_components'])\n"
             "print('Saved-current comparison: exact output hash match; new model calls: 0')"),
        markdown('## 每条记录的逐阶段去向\n\n“分段数”是片段数量，其余计数是点数。'
                 'filtered、denoised、simplified、retained 是互斥终态；简化前参考点仅指经过过滤和方向去噪后进入 DP 的 clean 点。'),
        code("stage_rows=[]\n"
             "for row in baseline['records']:\n"
             "    counts=row['stage_counts']\n"
             "    clean_points=counts['input']-counts['filtered']-counts['denoised']\n"
             "    stage_rows.append({'record':row['record_id'], 'input':counts['input'], 'segments':counts['segmented'], 'filtered':counts['filtered'], 'direction_deleted':counts['denoised'], 'DP_reference':clean_points, 'DP_omitted':counts['simplified'], 'retained':counts['retained'], 'not_processed':counts['not_processed']})\n"
             "show_table(stage_rows)\n"
             "print('Global stage counts:', baseline['stage_counts'])\n"
             "print('Complete ledger points:', len(baseline['point_actions']))\n"
             "assert len(baseline['point_actions']) == baseline['stage_counts']['input']\n"
             "assert audit['accounting']['count_conserved']"),
        markdown('## DP 的分母、误差与适用边界\n\nDP 点数节省为 `1 − N_final / N_clean`，不把上游过滤或去噪损失算成简化收益。'
                 '每个 clean 点只对其原始索引区间对应的保留线段计算误差，不能匹配轨迹中其他恰好邻近的线段。'
                 '误差阈值来自合同，数值余量为事前固定的 `64 × binary64 epsilon × max(1, 坐标尺度, tolerance)`。'),
        code("metric_rows=[]\n"
             "for row in baseline['records']:\n"
             "    segments=row['processed_segments']\n"
             "    n_clean=sum(len(s['denoise']['record']['indices']) for s in segments)\n"
             "    n_final=sum(len(s['output']['indices']) for s in segments)\n"
             "    errors=[s['independent_review']['metrics']['max_error']['value'] for s in segments if s['independent_review']['metrics']['max_error']['value'] is not None]\n"
             "    metric_rows.append({'record':row['record_id'], 'clean_reference_points':n_clean, 'final_points':n_final, 'DP_saving':1-n_final/n_clean if n_clean else None, 'max_interval_error_m':max(errors) if errors else None, 'no_output_reason':row['terminal_status'] if not n_final else None})\n"
             "show_table(metric_rows)\n"
             "total_clean=sum(r['clean_reference_points'] for r in metric_rows)\n"
             "total_final=sum(r['final_points'] for r in metric_rows)\n"
             "print('Aggregate DP saving:', 1-total_final/total_clean if total_clean else None)\n"
             "print('Quality status:', audit['quality_status'])"),
        markdown('## 本轮真实轨迹图与点终态分布\n\n原始点只画散点；clean 与 final 的线段都来自实际处理片段，不跨断点、过滤片段或记录连接。'
                 '各轨迹面板独立取轴范围，面板内 x/y 比例相同。图展示处理关系，不据此判断真实恢复或效果提升。'),
        code("figures=REVISION/'figures'\n"
             "figure_manifest=read_json(figures/'figure_manifest.json')\n"
             "assert figure_manifest['run_id']==current['run_id']\n"
             "assert figure_manifest['baseline']['sha256']==manifest['artifacts']['baseline']['sha256']\n"
             "for name in ('conditional_pilot_trajectories','point_terminal_counts'):\n"
             "    display(Image(filename=str(figures/(name+'.png')), width=1150))"),
        markdown('## 解释限制\n\n局部坐标模型的一致性核验不证明源 datum；应结合本轮 coordinate_sensitivity 产物查看近似误差及阈值影响。'
                 '无独立真值标签，因此不报告误删率、检测准确率或真实恢复准确率；几何保真也不自动证明时间保真。'
                 '七条记录属于开发 pilot，不能代表全量或最终留出。未运行 Goal 2 参数/顺序比较、未完成 Goal 3 正式报告和提交。'),
        code("followup=REVISION/'runs'/current['run_id']/'coordinate_sensitivity.json'\n"
             "if followup.exists():\n"
             "    sensitivity=read_json(followup)\n"
             "    print('Follow-up artifact:', followup.relative_to(ROOT))\n"
             "    print('SHA256:', digest(followup))\n"
             "    keys=['status','errors','source_crs','points_checked','within_record_pairs_checked','max_coordinate_crosscheck_error_m','max_model_geodesic_radius_m','max_pair_distance_relative_difference','max_pair_distance_absolute_difference_m','processing_threshold_checks','edge_400m_disagreements','segment_65m_disagreements','direction_35deg_disagreements','dp_5m_disagreements','source_datum_proven','interpretation']\n"
             "    print(json.dumps({k:sensitivity.get(k) for k in keys},ensure_ascii=False,indent=2))\n"
             "    if isinstance(sensitivity.get('dp_5m_checks'),list): show_table(sensitivity['dp_5m_checks'])\n"
             "else:\n"
             "    print('Coordinate-sensitivity follow-up: NOT_RUN; no result is inferred.')\n"
             "print('Formal reports: working material only; GPT second review: PENDING; Submission: NOT_READY')"),
    ]


def loop_notebook():
    return [
        markdown('# Goal 1：实际角色、修复返回与离线复算\n\n'
                 '对应教师《任务3_LLM辅助评估清洗》的工作入口。本轮 A、B-Run / B-Repair、C 使用主会话实际派发的原生角色任务；'
                 '确定性 Goal journal 记录职责、产物、审核和恢复。一个输出不会被重复标成多个角色。\n\n'
                 '历史 4 次初始 CLI 派发与后续 6 次修复 CLI 调用独立保留，不等于本轮 native 角色数量。'
                 '默认只读取真实记录并从 raw 重算工具，新模型调用为 0；不重跑旧六次对话。'),
        code(SETUP),
        code("MODE='RECOMPUTE'\nENABLE_LIVE=False\nLIVE_RUN_ID=None\nassert MODE in ('RECOMPUTE','LIVE')\nprint('Selected mode:',MODE)"),
        markdown('## 当前产物及目标覆盖\n\n每个审核回执绑定具体目标 ID/hash、原始参考、记录集合、合同和完整检查组件。'
                 '旧 profiles 的通过不代替新 time boundaries、duplicate details 或 baseline 的审核。'),
        code("artifact_rows=[]\n"
             "for action, artifact in manifest['artifacts'].items():\n"
             "    review_entry=manifest['reviews'].get(action)\n"
             "    review=read_json(ROOT/review_entry['path'])['result'] if review_entry else {}\n"
             "    artifact_rows.append({'action':action, 'artifact_id':artifact['artifact_id'], 'sha256':artifact['sha256'], 'review_status':review.get('status','NOT_RUN'), 'checked':review.get('checked_components',[]), 'unchecked':review.get('unchecked_components',[])})\n"
             "show_table(artifact_rows)"),
        markdown('## 从 raw 实际重算当前运行\n\n`recompute_saved` 先核对输入、合同和代码 hash，再重新执行实际工具，'
                 '由独立谓词审核新输出并比较保存产物。它不只是读取旧 CSV，也不是 snapshot 与自身比较。'
                 '源码或合同发生变化会要求重建，不能继续借旧结果完成任务。'),
        code("if MODE=='RECOMPUTE':\n"
             "    from task1.scripts.complete_goal1 import recompute_saved\n"
             "    recomputed=recompute_saved(current['run_id'])\n"
             "    assert recomputed['new_model_calls']==0 and recomputed['status']=='VERIFIED', recomputed\n"
             "    show_table([{'action':r['action'], 'fresh_output_matches':r['exact_match'], 'independent_review':r.get('independent_review',{}).get('status',r.get('status')), 'unchecked':r.get('independent_review',{}).get('unchecked_components',[])} for r in recomputed['checks']])\n"
             "else:\n"
             "    assert ENABLE_LIVE, 'LIVE 必须显式启用'\n"
             "    assert policy['live_execution_enabled'], policy['live_stop_reason']\n"
             "    assert LIVE_RUN_ID and not (EVIDENCE/'runs'/LIVE_RUN_ID).exists(), 'LIVE 使用新 run_id；不清空累计预算'\n"
             "    from task1.workflow.controller import Controller\n"
             "    live_result=Controller(LIVE_RUN_ID).run()\n"
             "    print('Controlled existing-provider run:',live_result['status'])"),
        markdown('## 真实 A / B / C 交接及资源\n\n下方读取本轮资源记录与 A 的任务交接路径。'
                 'CLI、native 派发、完成 turn、工具动作分开计数；不可观察的底层请求保持 unknown。'
                 '本 Notebook 的确定性重算不冒充新的模型回应。'),
        code("resources=read_json(REVISION/'resources.json')\n"
             "show_table([{'historical_batch':k, 'dispatches':v} for k,v in resources['historical_dispatches'].items() if k!='source'])\n"
             "show_table(resources.get('actual_native_dispatches',[]))\n"
             "print('Completed role turns:',resources.get('completed_role_turns','unknown'))\n"
             "print('This execution CLI dispatches:',resources.get('cli_dispatches','unknown'))\n"
             "print('Hidden provider requests:',resources.get('hidden_provider_requests','unknown'))\n"
             "print('Guardrails:',resources['guardrails'])\n"
             "a_path=REVISION/'a_scope/TaskPlan.json'\n"
             "a_plan=read_json(a_path)\n"
             "print('A handoff:',a_path.relative_to(ROOT),'SHA256:',digest(a_path))\n"
             "print('A artifact type:',a_plan.get('artifact_type'))"),
        markdown('## Issue → B-Repair → C → 受影响产物重建 → 父任务恢复\n\n'
                 'C2-F01/F02 来自真实外部 GPT 审核，不能称为本轮角色自行新发现。B 在同一执行中消费缺陷并修代码；'
                 'C 独立反例核验后才允许关闭，未通过则重新修复。源代码变更使受影响结果失效，父任务必须恢复并处理剩余项。'
                 '以下状态和附件来自实际 journal，不预设固定次数成功。'),
        code("state=read_json(REVISION/'goal_state.json')\n"
             "show_table([{'issue':key, 'source':row['source'], 'parent_task':row['parent_task'], 'repairer':row['repairer'], 'verifier':row.get('verifier'), 'status':row['status'], 'repair_evidence':row.get('repair_evidence',[]), 'closure_evidence':row.get('closure_evidence',[])} for key,row in state['issues'].items()])\n"
             "event_kinds={'ISSUE_OPENED','B_REPAIR_CONSUMED','REPAIR_SUBMITTED','C_REOPENED','C_VERIFIED_PARENT_RESUMED','CODE_BOUND','RUN_STARTED','TOOL_EXECUTED','FOLLOWUP_DISPATCHED','FOLLOWUP_EXECUTED','TASK_VERIFIED','GOAL_REEVALUATED'}\n"
             "show_table([{'sequence':e['sequence'], 'kind':e['kind'], 'issue_or_task':e.get('issue_id',e.get('task','')), 'run_or_operation':e.get('run_id',e.get('operation','')), 'parent_task':e.get('parent_task','')} for e in state['events'] if e['kind'] in event_kinds])"),
        markdown('## 执行结构与真实后续动作\n\n结构图表示当前实现及实际角色职责，不是 Evidence Master 的全局互动演变图。'
                 '真实处理后的 follow-up 请求、执行产物和复验均应绑定 baseline；没有结果时保持 NOT_RUN。'),
        code("figure_manifest=read_json(REVISION/'figures/figure_manifest.json')\n"
             "assert figure_manifest['run_id']==current['run_id']\n"
             "display(Image(filename=str(REVISION/'figures/goal1_execution_structure.png'),width=1200))\n"
             "run_state=state['runs'].get(current['run_id'],{})\n"
             "followup=run_state.get('followup')\n"
             "print('Actual follow-up:',json.dumps(followup,ensure_ascii=False,indent=2) if followup else 'NOT_RUN')\n"
             "if followup:\n"
             "    assert digest(ROOT/followup['path'])==followup['sha256']\n"
             "    actual_followup=read_json(ROOT/followup['path'])\n"
             "    print('Trigger:',json.dumps({k:actual_followup.get(k) for k in ['request','trigger_review','parent_artifact_id','parent_sha256','status']},ensure_ascii=False,indent=2))"),
        markdown('## 当前任务状态与解释边界\n\nVERIFIED 表示其明示范围内的工程检查成立；'
                 '它不是 QUALITY_ACCEPTED、未知真值恢复或项目最终验收。普通工程缺陷继续当前 Goal 的修复循环。'
                 '最终 GPT 远程二审仍待真实审核；不自动进入 Goal 2/3。\n\n'
                 '下方是 **Notebook 执行时的 journal 快照**；最终总审查登记在其后。'
                 '最终状态见 `task1/evidence/goal1/REVIEW_PACKET.md`，不能把执行中快照误称为最终状态。'),
        code("show_table([{'task':name,'status':row['status'],'depends_on':row['depends_on']} for name,row in state['tasks'].items()])\n"
             "print('Journal snapshot at Notebook execution:',state['status'])\n"
             "print('GPT second review:',state['gpt_second_review'])\n"
             "print('Submission:',state['submission'])\n"
             "print('Raw unchanged:',digest(DATA)==manifest['input_sha256'])\n"
             "print('Notebook mode:',MODE,'; default new model calls: 0')\n"
             "print('Final review is registered after this Notebook run; final status: task1/evidence/goal1/REVIEW_PACKET.md')"),
    ]


def execute_notebooks(paths):
    from nbclient import NotebookClient
    # A temporary kernelspec selects the existing interpreter without installing
    # or altering any persistent user/system Jupyter configuration.
    logs = []
    with tempfile.TemporaryDirectory(prefix='sc-g1-complete-kernel-') as tmp:
        kernel = Path(tmp) / 'kernels/sc-g1-complete'
        kernel.mkdir(parents=True)
        (kernel / 'kernel.json').write_text(json.dumps({'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                                                     'display_name': 'SC Goal1 current', 'language': 'python'}))
        previous = os.environ.get('JUPYTER_PATH')
        os.environ['JUPYTER_PATH'] = tmp + (os.pathsep + previous if previous else '')
        try:
            for path in paths:
                nb = nbf.read(path, as_version=4)
                client = NotebookClient(nb, timeout=240, kernel_name='sc-g1-complete',
                                        resources={'metadata': {'path': str(path.parent)}})
                client.execute()
                nbf.validate(nb)
                nbf.write(nb, path)
                logs.append({'notebook': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                             'new_kernel': True, 'new_model_calls': 0,
                             'code_cells': sum(c.cell_type == 'code' for c in nb.cells), 'status': 'VERIFIED'})
        finally:
            if previous is None:
                os.environ.pop('JUPYTER_PATH', None)
            else:
                os.environ['JUPYTER_PATH'] = previous
    return logs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Run each notebook in a fresh existing-venv kernel; no model calls by default')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    save('01_baseline_and_audit.ipynb', baseline_notebook())
    save('02_agent_loop_recompute.ipynb', loop_notebook())
    paths = [OUT / name for name in ('01_baseline_and_audit.ipynb', '02_agent_loop_recompute.ipynb')]
    result = {'generated': [str(p.relative_to(ROOT)) for p in paths], 'executed': False}
    if args.execute:
        result.update(executed=True, executions=execute_notebooks(paths))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
