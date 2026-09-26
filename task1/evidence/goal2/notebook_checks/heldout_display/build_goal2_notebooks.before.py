"""Create three Goal 2 working notebooks with raw-data RECOMPUTE defaults."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

import nbformat as nbf
from nbclient import NotebookClient

from task1.workflow.io import ROOT, digest, now, write_json


OUT = ROOT / "task1/notebooks/goal2"
EV = ROOT / "task1/evidence/goal2"

SETUP = '''from pathlib import Path
import sys, json, tempfile, shutil
from html import escape
from IPython.display import display, Image, HTML
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'AGENTS.md').is_file() and (p/'task1').is_dir())
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from task1.workflow.io import read_json, digest, object_hash
from task1.workflow.g2_provider import ExperimentProvider
model_sentinel = {'calls': 0}
def reject_model_call(*args, **kwargs):
    model_sentinel['calls'] += 1
    raise RuntimeError('RECOMPUTE_FORBIDS_NEW_MODEL_CALLS')
ExperimentProvider.call = reject_model_call
EV = ROOT/'task1/evidence/goal2'
current = read_json(EV/'current_runs.json')
contract = read_json(ROOT/'task1/config/goal2/contract.json')
split = read_json(EV/'data/split_manifest.json')
MODE = 'RECOMPUTE'
ENABLE_LIVE = False
assert MODE == 'RECOMPUTE' and ENABLE_LIVE is False, '新的 LIVE 调用须使用独立命令并显式启用，默认 Notebook 不发起模型请求。'
WORK = Path(tempfile.mkdtemp(prefix='sc-g2-notebook-'))
def show(rows):
    rows = list(rows)
    columns = list(dict.fromkeys(key for row in rows for key in row))
    header = ''.join('<th>'+escape(str(key))+'</th>' for key in columns)
    body = ''.join('<tr>'+''.join('<td>'+escape(str(row.get(key, '')))+'</td>' for key in columns)+'</tr>' for row in rows)
    display(HTML('<table><thead><tr>'+header+'</tr></thead><tbody>'+body+'</tbody></table>'))
def figure(name):
    directory = Path(recomputed.get('figure_directory', WORK/'figures'))
    target = directory/(name+'.png')
    assert target.is_file(), f'复算图缺失: {target}'
    display(Image(filename=str(target), width=1050))
print('运行方式:', MODE, '| 新模型调用:', 0)
print('原始来源 datum:', contract['source_crs'], '| 单位: 工作米 / 原始相对秒')
print('当前固定分区:', {name:len(ids) for name,ids in split['splits'].items()})
'''


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


def recompute_cell(topic):
    return code(f'''from task1.scripts.goal2 import recompute
recomputed = recompute(topic='{topic}', output_directory=WORK, rebuild_figures=True)
assert recomputed['status'] == 'VERIFIED', recomputed
assert recomputed['new_model_calls'] == 0, recomputed
assert model_sentinel['calls'] == 0, model_sentinel
print('从 raw 和冻结提议复算:', recomputed['status'])
print('新增模型调用:', recomputed['new_model_calls'])
print('检查项数量:', len(recomputed['checks']))
show(recomputed['checks'][:20])
print('全部检查结果保存在独立复算输出，不把重复计算计为新独立实验。')
''')


def parameters_notebook():
    return [
        md("# Goal 2：参数实验与顺序比较\n\n本工作 Notebook 对应基础作业的分段、方向去噪、DP 实现空缺及三个选做参数实验，并回答处理顺序问题。结果均是 `source_crs=UNVERIFIED` 条件下的工作平面几何分析；原始记录不自动代表独立用户或完整骑行。"),
        code(SETUP),
        md("## 教师入口与实现\n\n| 教师材料 | 本轮入口 |\n|---|---|\n| 基础 Notebook cell 4：分段 | `workflow/geometry.py:split_trajectory` 与 `filter_segments` |\n| cell 6：去噪 | `denoise_trajectory`，一次标记后同时删除 |\n| cell 8：简化 | `douglas_peucker_indices`，有限线段与原始索引 |\n| cells 12–17：三组参数实验 | `g2_experiments.parameter_development` |\n| PPT 42：能否交换顺序 | 六种 S/D/P 的真实受控对照 |\n\nG2 使用单独合同与入口，G1 的七条回归合同保留。S 前不隐藏分段；每阶段重新计算邻接特征。"),
        code("from task1.workflow.g2_pipeline import REFERENCE_PARAMETERS, ORDERS\nprint('参考配置:', REFERENCE_PARAMETERS)\nprint('已登记顺序:', ORDERS)\nprint('规定参数网格:')\nshow([{'parameter':key,'values':value} for key,value in contract['parameter_grids'].items()])"),
        md("## Restart Kernel → Run All 的实际重算\n\n下面从不可变 raw 重算完整 DEVELOPMENT 参数与顺序产物，以及当前 G2_EVAL 代表配置、冻结单项和可行顺序，重新检查参数、原始身份、阶段操作、完整 P 参考和账本。保存文件只作为版本比较目标。此路径不以加载 CSV 代替实验，也不发起新的 LLM 调用。"),
        recompute_cell("parameters"),
        md("## 分段与短片段过滤\n\n分段在严格大于阈值的边右点前切开；短段过滤单独判点数和段内累计长度。`dt=15` 会切开 20 秒间隔。95 工作米是教学例值，不能解释为本数据已确认限速。图同时给出 raw 点保留与整条无输出，两者分母不同；全量逐记录结果仍在当前 run。"),
        code("parameter_run = EV/'runs'/current['parameter_development']\nparameter_rows = read_json(parameter_run/'parameter_table.json')\nshow([{'config_id':row['config_id'],**row['parameters'],**{key:row['summary'][key] for key in ('n_records','n_input','n_final','n_no_output_records','point_retention','common_coverage')}} for row in parameter_rows])\nfigure('segmentation_filter_response')\nfigure('segmentation_filter_grids')"),
        md("## 一次方向删除与 DP 的独立分母\n\n方向不可计算窗口和首尾点保持；删点后的新邻接不触发第二轮迭代。DP 省点率是 `1 − N_P_immediate_output / N_P_input`，不把上游或后续阶段损失算入。共同 raw 几何误差另外评价；各自 clean 的小误差不能证明整体更好。"),
        code("figure('direction_threshold_and_neighborhood')\nfigure('dp_error_compression')"),
        md("## 顺序是否可以交换\n\n六顺序都按实际当前索引运行。下表将工程正确与共同原始断点、覆盖保护分开；违反保护是有效负结果。P 先执行可能删去断点触发信息，D 先执行可能跨间断取方向窗口，P 先于 D 会改变 D 的邻域。是否进入阶段留出评估由冻结的保护规则和实际失败证据决定。"),
        code("order_rows = read_json(EV/'runs'/current['order_development']/'order_table.json')\nshow([{'order':row['order'],'engineering':row['engineering_status'],'research':row['research_status'],'failed_records':len(row['safety_failures']),**{key:row['summary'][key] for key in ('common_coverage','raw_break_crossings','direction_windows_across_raw_breaks','n_no_output_records')}} for row in order_rows])\nfigure('order_protection_and_neighborhoods')"),
        md("## 解释边界\n\n统计单位首先是原始记录。分层样本不代表总体均值；删点数、长度变化和计算可行性不是噪声检测准确率。三单项只形成 Goal 3 备选，本轮不组合或冻结最终方法。"),
        code("print('raw hash unchanged:', digest(ROOT/contract['raw_path']) == contract['raw_sha256'])\nprint('GPT_SECOND_REVIEW=PENDING; Submission=NOT_READY')\nshutil.rmtree(WORK)"),
    ]


def modes_notebook():
    return [
        md("# Goal 2：真实四模式、搜索预算与冻结记忆\n\n本工作 Notebook 对应 LLM 作业的四模式和示范记忆对照。生产 A/B/C 调度与被评估系统的模型调用单独计数。默认复算使用已经锁定的真实提议，身份是 RECOMPUTE，不伪装为新 LIVE。"),
        code(SETUP),
        md("## 四种决策路径\n\n| 模式 | 决策模型 | 搜索反馈 | 示范记忆 |\n|---|---|---|---|\n| llm-only | 一次真实锁定提议 | 无 | 无 |\n| search-only | 严格 0 次；不实例化 Provider | 确定性至多 20 候选 | 无 |\n| llm+search | 至多 3 回合真实决策 | 仅本 episode 已执行结果 | 无 |\n| llm+memory+search | 相同模型、回合、预算 | 同上 | 冻结 DEMO_MEMORY，只读 |\n\n一次调用至多 8 张诊断卡，调用数按实际批次算。LLM-only 的计算预算不同是结构消融的一部分，不伪称等量计算。"),
        md("## 从 raw 与已保存真实提议重建确定性执行\n\n复算重新处理开发和三次阶段评测中每个实际候选，检查原始提议合法性、预算、选择与锁定后评价；不用固定 Mock 答案。Provider 哨兵阻断任何意外模型调用，持久记忆保持原哈希。"),
        recompute_cell("modes"),
        code("mode_run = EV/'runs'/current['mode_evaluation']\nmode_manifest = read_json(mode_run/'manifest.json')\nepisodes = []\nfor entry in mode_manifest['mode_episodes']:\n    path = mode_run/entry['path']\n    assert digest(path) == entry['sha256']\n    episodes.append(read_json(path))\nmode_rows = [row for episode in episodes for row in episode['records']]\nshow([{'mode':episode['mode'],'episode':episode['episode'],'records':len(episode['input_ids']),'classification':episode['classification'],'model_dispatches':episode['resources']['experiment_model_dispatches'],'candidate_evaluations':episode['resources']['candidate_evaluations'],'elapsed_seconds':episode['elapsed_seconds']} for episode in episodes])\nassert all(episode['resources']['experiment_model_dispatches']==0 for episode in episodes if episode['mode']=='search-only')"),
        md("## 逐记录配对、失效动作与成本\n\n同一原始记录的三 episode 保留为重复决策，不能当作三个独立样本。图中描述相对该记录 reference 的有符号变化；空误差不填 0。原始非法提议和工程回退分别显示，回退不能替原始建议取得合法性分数。"),
        code("figure('four_mode_paired_results')\nfigure('four_mode_failures_and_cost')\nproposal_rows=[]\nfor row in mode_rows:\n    for proposal in row['proposal_records']:\n        proposal_rows.append({'record_id':row['record_id'],'mode':row['mode'],'episode':row['episode'],'round':proposal['round'],'legal':proposal['legal'],'executed':proposal['executed'],'rejection_reason':proposal.get('rejection_reason',proposal.get('reason')),'original':proposal.get('original')})\nshow(proposal_rows[:12])\nprint('全部原始提议条目:',len(proposal_rows),'；这里只展示前12条，完整来源保留。')"),
        md("## 检索、消费与泄漏隔离\n\nDEMO 60 条先经过确定性核验，再冻结快照。检索按父记录/同源组、分区、版本和原始诊断适用性过滤；评测不写记忆、不读取其他模式结果。检索命中、模型引用、参数与案例一致是不同级别的可观察事实，并不单独证明因果收益。"),
        code("figure('memory_coverage_and_consumption')\nmemory_rows = [row for row in mode_rows if row['mode']=='llm+memory+search']\nhashes = sorted({row['memory_snapshot_hash'] for row in memory_rows})\nassert len(hashes)==1 and hashes[0], hashes\nprint('全部正式记忆episode使用同一snapshot:',hashes[0])\nshow([{'record_id':row['record_id'],'episode':row['episode'],'round':rd['round'],**rd['memory_consumption']} for row in memory_rows for rd in row['rounds'] if 'memory_consumption' in rd][:12])"),
        md("## 真实调用与理解边界\n\n原始请求、响应、provider/session ID 和可见 tokens 在各 round 的调用目录；底层不可见请求/费用保持 unknown。实际预测只和事前绑定的 metric/reference/sign 比较。新的 LIVE 调用使用 `python -m task1.scripts.goal2 --help` 中明确的 LIVE 入口；改变本 Notebook 的显示字符串不会启动模型。"),
        code("print('本 Notebook 新模型调用:',recomputed['new_model_calls'])\nprint('先前真实正式派发:',sum(episode['resources']['experiment_model_dispatches'] for episode in episodes))\nprint('GPT_SECOND_REVIEW=PENDING; Submission=NOT_READY')\nshutil.rmtree(WORK)"),
    ]


def candidates_notebook():
    return [
        md("# Goal 2：单项候选、反例与阶段案例\n\nC-S、C-D、C-P 分别只改变一个参数组，保留开发选择和 G2_EVAL 确认的区别。没有独立真值的自然数据只支持条件化覆盖、几何与约束结论。构造反例具有明确解析答案，其误删/漏检计数不能外推到真实数据。"),
        code(SETUP),
        md("## 从 raw 复算候选确认与反例\n\n固定候选后才打开 G2_EVAL。本段重新执行对应真实数据处理与构造反例，检查保存结果一致；它是复现，不产生新的选择机会或独立实验数量。"),
        recompute_cell("candidates"),
        code("lock = read_json(EV/'candidate_lock.json')\nassert lock['source_partition']=='DEVELOPMENT' and lock['g2_eval_observed_for_selection'] is False\nshow([{'candidate':name,**row} for name,row in lock['selected_single_candidates'].items()])\nprint('额外结构候选:',lock['structural_candidates'])\nprint('仅以下冻结顺序进入阶段留出:',lock['feasible_orders'])"),
        md("## 解析构造反例\n\n正常转弯、合法 zigzag 和注入毛刺说明方向几何不是噪声真值。零位移和零时间差保留不可计算原因。有限线段反例拒绝无限直线捷径；P 先删触发点可能掩盖原始断点。整条无输出无法凭缺少异常获得好分，各自 clean 的零 DP 误差不能证明跨方法整体更好。这里检验风险，不伪造实际模型错误或用户质疑。"),
        code("counter_directory = ROOT/current['counterexamples']\nsynthetic = read_json(counter_directory/'synthetic_cases.json')\nassert synthetic['classification']=='SYNTHETIC_COUNTEREXAMPLE'\nshow([{'case':case['case_id'],'family':case['family'],'checks':len(case['known_answer_checks']),'passed':all(check['passed'] for check in case['known_answer_checks']),'interpretation':case['interpretation']} for case in synthetic['cases']])\nfigure('synthetic_metric_counterexamples')"),
        md("## 真实案例：代表样本、退化与近阈值\n\n出图前按原始跨度层中位代表、最大覆盖损失、最大共同误差、最小正 P 阈值间隔规则登记案例。图只在工作平面显示点和真实输出片段，不叠加未核实底图，不跨记录/分段连线。缺输出同样保留。"),
        code("figure('real_trajectory_cases')\npilot = read_json(counter_directory/'exposed_pilot_cases.json')\nshow([{'record_id':row['record_id'],'raw_points':row['raw_points'],'final_points':row['final_points'],'segments':[{'n':part['n_points'],'length_working_m':part['within_segment_length_working_m'],'reasons':part['filter_reasons']} for part in row['segments']]} for row in pilot['all_filtered_records_0_1_2']])\nnear=pilot['near_threshold_case']\nprint('已暴露pilot近阈值:',{key:near[key] for key in ('record_id','original_index','reference_bracketing_indices','actual_error_working_m')})\nshow([{'dp':threshold,**row} for threshold,row in near['before_after'].items()])"),
        md("## 实际生产工作流与被评估系统\n\n主线程负责父 Goal；A 安排冻结范围内实验，B 执行或修复，独立 C 从可信原始输入核验。确定性 GoalJournal 检查版本、依赖和回执。普通问题经过修复、复验、失效产物重建后恢复父任务；这些角色调用与四模式内部调用分开计数。"),
        code("figure('goal2_actual_architecture')\nstate=read_json(EV/'goal_state.json')\nshow([{'issue':key,'parent_task':row['parent_task'],'status':row['status'],'fact':row.get('fact'),'repairer':row.get('repairer'),'verifier':row.get('verifier')} for key,row in state.get('issues',{}).items()])\nprint('Notebook执行时journal状态:',state['status'])"),
        md("## 下一阶段边界\n\n本轮只保留支持、否定、权衡或证据不足的单项结果供 Goal 3 判断。组合、冻结最终方法、最终全量处理、两份正式报告定稿、Evidence Lock 和提交包均不在本工作 Notebook 执行。最终网页 GPT 二重审核不能由内部自检替代。"),
        code("print('原始数据不变:',digest(ROOT/contract['raw_path'])==contract['raw_sha256'])\nprint('本次新模型调用:',recomputed['new_model_calls'])\nprint('GPT_SECOND_REVIEW=PENDING; Submission=NOT_READY')\nshutil.rmtree(WORK)"),
    ]


def execute_notebooks(paths):
    logs = []
    with tempfile.TemporaryDirectory(prefix="sc-g2-kernelspec-") as temporary:
        kernel = Path(temporary) / "kernels/sc-g2"
        kernel.mkdir(parents=True)
        (kernel / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                                                       "display_name": "Smart Cities Goal 2 existing environment", "language": "python"}))
        previous = os.environ.get("JUPYTER_PATH")
        os.environ["JUPYTER_PATH"] = temporary + (os.pathsep + previous if previous else "")
        try:
            for path in paths:
                started = now()
                notebook = nbf.read(path, as_version=4)
                NotebookClient(notebook, timeout=3600, kernel_name="sc-g2", resources={"metadata": {"path": str(path.parent)}}).execute()
                nbf.validate(notebook)
                nbf.write(notebook, path)
                logs.append({"notebook": str(path.relative_to(ROOT)), "sha256": digest(path), "started_at": started,
                             "ended_at": now(), "new_kernel": True, "new_model_calls": 0,
                             "status": "VERIFIED", "cell_errors": []})
        finally:
            if previous is None:
                os.environ.pop("JUPYTER_PATH", None)
            else:
                os.environ["JUPYTER_PATH"] = previous
    return logs


def build(output_directory=OUT, execute=False):
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    notebooks = {"01_parameters_and_orders.ipynb": parameters_notebook(),
                 "02_real_modes_and_memory.ipynb": modes_notebook(),
                 "03_candidates_counterexamples_and_cases.ipynb": candidates_notebook()}
    paths = []
    for name, cells in notebooks.items():
        path = output_directory / name
        notebook = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                                             "language_info": {"name": "python", "version": sys.version.split()[0]},
                                                             "goal_id": "SC-LAB1-G2-EXPERIMENTS-001", "default_mode": "RECOMPUTE"})
        nbf.validate(notebook)
        nbf.write(notebook, path)
        paths.append(path)
    logs = execute_notebooks(paths) if execute else []
    result = {"generated_at": now(), "generator_sha256": digest(__file__), "executed": execute,
              "paths": [str(path.relative_to(ROOT)) for path in paths], "executions": logs,
              "new_persistent_kernels": 0, "environment": "existing .venv"}
    write_json(EV / "notebook_execution.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.execute), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
