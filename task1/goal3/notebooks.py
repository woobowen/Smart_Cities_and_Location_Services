"""Create the two teacher-mapped completion notebooks. Generation does not execute them."""
from pathlib import Path
import ast
import hashlib
import json
import textwrap

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT/'task1/notebooks/final'


def md(text, cells=()):
    cell=nbf.v4.new_markdown_cell(textwrap.dedent(text).strip())
    if cells: cell.metadata['teacher_starter_cells']=list(cells)
    return cell


def code(text):
    return nbf.v4.new_code_cell(textwrap.dedent(text).strip())


SETUP = r'''
from pathlib import Path
import contextlib, csv, gzip, hashlib, html, io, json, os, platform, re, sys, tempfile
from IPython.display import display, HTML, Image, Markdown

# 从 Notebook 所在位置或启动目录向上找项目；不依赖个人绝对路径和 ROOT/.venv。
start = Path.cwd().resolve()
ROOT = next((p for p in (start, *start.parents)
             if (p/'task1/goal3').is_dir()), None)
if ROOT is None:
    raise RuntimeError('请把 Notebook 放在完整提交包中，或从项目目录启动。')
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODE = 'FULL_RECOMPUTE'
ENABLE_LIVE = False
assert MODE == 'FULL_RECOMPUTE' and ENABLE_LIVE is False
explicit_work = os.environ.get('SC_LAB1_RECOMPUTE_WORK')
if explicit_work:
    WORK = Path(explicit_work).expanduser().resolve()
    if WORK == ROOT or ROOT in WORK.parents:
        raise RuntimeError('显式复算目录必须位于当前工程/解压包之外。')
    if WORK.exists() and (not WORK.is_dir() or any(WORK.iterdir())):
        raise RuntimeError('显式复算目录已存在且非空，拒绝覆盖。')
    WORK.mkdir(parents=True, exist_ok=True)
else:
    WORK = Path(tempfile.mkdtemp(prefix='sc-lab1-full-')).resolve()

from task1.workflow.io import digest, object_hash, read_json, write_json
from task1.workflow.io import ROOT as MODULE_ROOT
from task1.workflow.g2_provider import ExperimentProvider
from task1.workflow.provider import CodexProvider
from task1.goal3.reproduce import recompute_historical, recompute_production
assert MODULE_ROOT.resolve() == ROOT, '模块必须来自当前工程/解压包，不能借用原工作区。'

# 本内核实际拦截两个已登记 Provider 入口；出现调用立即失败，不回退到 Mock。
provider_observation = {'attempted_new_calls': 0}
def forbid_provider(*args, **kwargs):
    provider_observation['attempted_new_calls'] += 1
    raise RuntimeError('FULL_RECOMPUTE 禁止新增模型调用')
_original_experiment_call = ExperimentProvider.call
_original_governance_call = CodexProvider.call
ExperimentProvider.call = forbid_provider
CodexProvider.call = forbid_provider

G2 = ROOT/'task1/evidence/goal2'
G3 = ROOT/'task1/evidence/goal3'
stage = read_json(G2/'result_summary.json')
memory_path = ROOT/stage['memory']['snapshot_path']
memory_hash_before = digest(memory_path)
assert memory_hash_before == stage['memory']['snapshot_sha256']
raw_path = ROOT/'task1/作业/作业/traj_dict.json'
assert digest(raw_path) == stage['data']['raw_sha256']

# 只有当前生产已冻结并有真实 run 时才执行本完成版，不临时用样本替代 full。
if not (G3/'current_runs.json').is_file() or not (G3/'production_freeze.json').is_file():
    raise RuntimeError('G3 正式生产尚未登记；保持源文件待执行，不把 fast 样本冒充 full。')

def show(rows, columns=None, limit=20):
    rows = list(rows)
    if not rows:
        print('无对应行；不填造数值。')
        return
    columns = columns or list(rows[0])
    def cell(value):
        if value is None: return '不可用（见相应原因）'
        if isinstance(value, (dict,list)): value=json.dumps(value,ensure_ascii=False)
        return html.escape(str(value))
    head='<tr>'+''.join('<th>'+cell(c)+'</th>' for c in columns)+'</tr>'
    body=''.join('<tr>'+''.join('<td>'+cell(r.get(c))+'</td>' for c in columns)+'</tr>' for r in rows[:limit])
    display(HTML('<table style="border-collapse:collapse" border="1">'+head+body+'</table>'))
    if len(rows)>limit: print(f'显示前 {limit} / {len(rows)} 行；完整记录保留于来源文件。')

def figure(name, phase='goal2', width=950):
    path=ROOT/'task1/figures'/phase/(name+'.png')
    if not path.is_file(): raise FileNotFoundError('正式图不存在：'+str(path.relative_to(ROOT)))
    display(Markdown('**已归档正式图：** '+phase+' / '+name+'（历史解释材料）'))
    display(Image(filename=str(path),width=width))

def recomputed_figure(topic, name, width=950):
    directory=WORK/topic/'figures'
    manifest=read_json(directory/'figure_manifest.json')
    assert manifest['old_summary_or_figure_read_for_plotting'] is False
    entry=next(f for f in manifest['figures'] if f['name']==name)
    path=directory/entry['files']['png']['path']
    assert digest(path)==entry['files']['png']['sha256']
    assert digest(directory/'plot_data.json')==manifest['plot_data_sha256']
    display(Markdown('**本次 FULL 从 raw 重新计算并绘制：** '+name))
    display(Image(filename=str(path),width=width))

def run_logged(label, fn):
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):
        result=fn()
    (WORK/(label+'_progress.txt')).write_text(capture.getvalue(),encoding='utf8')
    assert result['status']=='VERIFIED' and result['new_model_calls']==0
    print({k:v for k,v in result.items() if k not in {'checks','selections'}})
    return result

def current_manifest(partition):
    index=read_json(G3/'current_runs.json')
    found=[]
    for run_id in index.values():
        if not isinstance(run_id,str): continue
        path=G3/'runs'/run_id/'manifest.json'
        if path.is_file():
            value=read_json(path)
            if value.get('partition')==partition: found.append((path,value))
    if len(found)!=1: raise RuntimeError('当前 run 索引没有唯一分区：'+partition)
    return found[0]

_, deployment_manifest=current_manifest('FULL_PRODUCTION')
if (deployment_manifest.get('status')!='MACHINE_VERIFIED_PENDING_C'
        or deployment_manifest['input_ids']!=deployment_manifest['completed_record_ids']):
    raise RuntimeError('当前生产尚未完整完成；不执行待验收Notebook。')

print('FULL_RECOMPUTE；Python',platform.python_version(),'; 新模型调用由实际 Provider 哨兵检查。')
print('数据：',stage['data']['raw_records'],'条 /',stage['data']['raw_points'],'点；source_crs=UNVERIFIED。')
'''

END = r'''
assert digest(memory_path)==memory_hash_before
assert digest(raw_path)==stage['data']['raw_sha256']
assert provider_observation['attempted_new_calls']==0
ExperimentProvider.call=_original_experiment_call
CodexProvider.call=_original_governance_call
receipt.update({'status':'VERIFIED','mode':MODE,'python_version':platform.python_version(),
                'new_model_call_attempts_observed':provider_observation['attempted_new_calls'],
                'memory_sha256_before':memory_hash_before,'memory_sha256_after':digest(memory_path),
                'raw_sha256_unchanged':digest(raw_path)==stage['data']['raw_sha256'],
                'historical_recompute_is_new_live':False,
                'execution_artifact_directory_name':WORK.name,
                'execution_directory_source':'SC_LAB1_RECOMPUTE_WORK' if explicit_work else 'new_temporary_directory',
                'module_root_matches_current_project':MODULE_ROOT.resolve()==ROOT})
write_json(WORK/'notebook_receipt.json',receipt)
print(json.dumps(receipt,ensure_ascii=False,indent=2))
print('本次新模型调用0；历史提议复算不作为新LIVE。网页GPT二重审核仍由外部实际审核决定。')
'''


def basic():
    return [
        md('''# 实验一 · 轨迹数据预处理完成版

对应教师 `作业1轨迹数据预处理.ipynb`。原 starter 保留；本完成版复用经过核验的同一套实现，依次展示 S 分段/过滤、D 方向删除、P 简化、三组参数、六种顺序、评价与真实 AI 批判，最后实际全量复算。

**默认 FULL_RECOMPUTE**：历史参数/顺序从 raw 重算 9,720 个记录—候选配对，再从全部 11,386 条原始记录重算冻结 R0/最终策略，并从本次新结果重新生成图与画图数据。`LIVE` 不在本 Notebook 自动开启。历史 G2 结果、最终确认样本、全量生产三者保持独立身份。可用 `SC_LAB1_RECOMPUTE_WORK` 指定工程外的新输出目录；不设置则创建临时目录，不覆盖已有非空结果。''', (0,2,10,12,14,16)),
        code(SETUP),
        md('''## 1. 数据与条件化坐标

输入原始坐标/时间不覆盖。工作坐标固定椭球 `a=6378137 m, 1/f=298.257223563`、`h=0`、ENU 中心 `(121.343555°,31.3561015°)`。数值核对不能证明源 datum；零时间差速度、零位移方向分别记为不可计算。以下只用已暴露的 pilot 记录 246 演示单条步骤，不从最终确认集挑案例。'''),
        code('''from task1.workflow.g2_data import raw_data, adapt
from task1.workflow.g2_pipeline import run_record, REFERENCE_PARAMETERS, DIRECTION_METHOD
from task1.workflow.g2_metrics import review_record
from task1.workflow.geometry import (split_trajectory, filter_segments, denoise_trajectory,
                                    douglas_peucker_indices, select_indices, recompute_features)
raw=raw_data()
pilot=adapt('246',raw['246'])
print('演示身份：已暴露 PILOT 246；原始点数',len(pilot['indices']))
print('教学参考参数',REFERENCE_PARAMETERS)
features=recompute_features(pilot,time_reliable=True)
show(features['edges'][:8],['from_index','to_index','dt','distance','speed','speed_reason','direction_degrees','direction_reason'])'''),
        md('''## 2. 完成三个基础 TODO

### S：先断边，再按完整段过滤

`dt > 阈值`、负时间差或距离 `> 阈值` 才断开；等号不切，右点属于新段。短段依据段内累计长度与点数判定，断开的边不计入长度。下面是教师 TODO 对应的可读调用入口，核心数学只有模块内一份。''',(4,5)),
        code('''def segmentation(record, dt=30, distance=400, min_points=5, min_length=65):
    split=split_trajectory(record,dt,distance,time_reliable=True)
    filtered=filter_segments(split['segments'],min_points,min_length,time_reliable=True)
    return {'boundaries':split['boundaries'],'kept':filtered['kept'],'dropped':filtered['dropped']}

segmented=segmentation(pilot)
print('原始断点:',segmented['boundaries'])
show([{'kept':keep,'original_indices':part['indices'],
       'length_work_m':part['features']['length'],
       'filter_reasons':part.get('filter_reasons',[])}
      for keep,key in [(True,'kept'),(False,'dropped')] for part in segmented[key]])'''),
        md('''### D：完整标记后同时删除

当前至后继为出边方向；与前后出边方向的圆周差都严格大于阈值才标记。一次标记、同时删除，不迭代；首尾及必要方向不可计算窗口保留并标记，下游重算特征。没有未知物理限速或“低位移就可靠”的假设。''',(6,7)),
        code('''def denoising(segment,direction=35):
    return denoise_trajectory(segment,direction,method=DIRECTION_METHOD,time_reliable=True)

denoised=[denoising(part) for part in segmented['kept']]
show([{'segment':i,'input_points':len(part['indices']),
       'deleted_indices':result['deleted_indices'],
       'remaining_points':len(result['record']['indices'])}
      for i,(part,result) in enumerate(zip(segmented['kept'],denoised))])'''),
        md('''### P：有限线段的 Douglas–Peucker

把点向有限端点线段投影，投影位置夹在 `[0,1]`；端点重合用点到端点距离。最大偏差严格超过容差时递归。`dp=0` 明确作为全部保留参考。输出沿用原始身份，不插值、不改坐标和时间。''',(8,9)),
        code('''def simplification(segment,dp=5):
    kept=douglas_peucker_indices(segment['xy'],dp,segment['indices'])
    return select_indices(segment,kept,time_reliable=True)

simplified=[simplification(result['record']) for result in denoised]
show([{'segment':i,'P_input':len(clean['record']['indices']),
       'P_output':len(final['indices']),'retained_original_indices':final['indices']}
      for i,(clean,final) in enumerate(zip(denoised,simplified))])

# 已知数学答案用于理解距离定义，非真实数据噪声标签。
from task1.workflow.geometry import point_segment_distance
print('越过端点的点到有限线段距离：',point_segment_distance((2,1),(0,0),(1,0)))'''),
        md('''## 3. 主函数、动作账本与真实前后案例

`run_record` 统一记录每阶段输入/操作/输出，原始点的终态为 filtered、denoised、simplified 或 retained。审核从独立可信 pilot 输入重构，不拿候选自己的 clean 自证。图分别画真实片段，原始断点不重连。''',(10,11)),
        code(r'''contract_hash=digest(ROOT/'task1/config/goal2/contract.json')
provenance={'source_kind':'CURRENT_NOTEBOOK_EXPOSED_PILOT','record_id':'246','not_new_independent_sample':True}
example=run_record(pilot,dict(REFERENCE_PARAMETERS),'S-D-P',contract_hash=contract_hash,provenance=provenance)
check=review_record(example,pilot,expected_parameters=dict(REFERENCE_PARAMETERS),expected_order='S-D-P',
                    contract_hash=contract_hash,trusted_provenance=provenance)
assert check['status']=='VERIFIED'
show([{k:example['metrics'][k] for k in ['n_input','n_filtered','n_direction_removed','n_dp_removed','n_final',
      'common_covered_points','common_max_error','dp_max_error','raw_break_crossings']}])
show(example['point_actions'][:12],['original_index','action','reasons'])

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
palette_text=(ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex').read_text()
palette={name:'#'+value for name,value in re.findall(r'\\definecolor\{([^}]+)\}\{HTML\}\{([0-9A-Fa-f]{6})\}',palette_text)}
raw_windows=split_trajectory(pilot,30,400,time_reliable=True)['segments']
# 原生 Figure/Canvas 文件输出不依赖 IPython 的 pyplot REPL 接口。
fig=Figure(figsize=(13,4),constrained_layout=True)
FigureCanvasAgg(fig)
axes=fig.subplots(1,3)
for ax,title,parts,color in zip(axes,['Raw fixed windows','After S-D','After S-D-P'],
        [raw_windows,example['stages'][1]['output'],example['final_segments']],[palette['Muted'],palette['C2'],palette['C1']]):
    for part in parts:
        if part['xy']:
            x,y=zip(*part['xy']);ax.plot(x,y,'.-',color=color,linewidth=1,markersize=3)
    ax.set_title(title);ax.set_xlabel('East / working m');ax.set_ylabel('North / working m')
    ax.set_aspect('equal',adjustable='datalim');ax.grid(alpha=.2)
fig.suptitle('Known-exposed pilot 246; conditional coordinates; no basemap')
fig.savefig(WORK/'pilot_steps.svg')
fig.savefig(WORK/'pilot_steps.png',dpi=200)
display(Image(filename=str(WORK/'pilot_steps.png'),width=1000))
'''),
        md('''## 4. 评价逻辑

共同 raw 窗口固定为 dt=30、distance=400（不做短段过滤）。原始点只有被显式保留，或由同一 final 片段内相邻保留索引且处在同一原始窗口夹持，才有共同误差。覆盖分母是原始点；显式保留点、共同覆盖点、P 即时输入分别统计。空输出不删除分母，误差 null 不当作零。

S/D 变化需要参考覆盖集合包含、原来非空记录/窗口不丢失、原始断点跨越0、参考已覆盖集合的最大误差非退化。P 只有相同上游完整输入且满足共同5工作米预算，才比较省点收益。没有噪声真值，不计算真实噪声准确率或主观加权分数。'''),
        md('''## 5. 三组参数与六顺序：实际从 raw 完整复算

这一单元恢复 G2 已经发生的参数/顺序实验，检查全部原始结果哈希与可信审核。参数59×120+14×120，顺序6×120+2×120，共9,720个记录—候选配对。输出不是新独立实验，也不是新的 LIVE 模型运行。''',(12,13,14,15,16,17)),
        code('''parameter_recompute=run_logged('parameters',lambda:recompute_historical('parameters',WORK/'parameters'))
assert parameter_recompute['candidate_record_recomputations']==9720
recomputed_figure('parameters','recomputed_parameters')
recomputed_figure('parameters','recomputed_orders')
show([{'parameter':k,'registered_values':v} for k,v in stage['parameters']['grid'].items()])
show(stage['single_candidates'],['candidate','dt','distance','min_points','min_length','direction','dp',
                                'n_records','strict_gain_records','common_covered_points','n_final','evaluation_status'])'''),
        md('''### 参数结果如何解释

C-S（G3称S0）只把 min_points=5→2、min_length=65→0，其余参考参数不变；G2评估120条有53条严格改善，共同覆盖8805→12162，无输出32→0。C-D、C-P仍是R0，不能说成两个新组件。新增覆盖不证明点干净；改变S/D后P省点率的变化也不证明DP变好。上方图是本次 raw 复算后新绘；以下三张已归档 G2 图保留更细的历史解释。'''),
        code("figure('segmentation_filter_grids')\nfigure('direction_threshold_and_neighborhood')\nfigure('dp_error_compression')"),
        md('''### 顺序结果与拒绝理由

六种顺序按字面执行，没有藏一个额外预分段。D先于S可能跨断点取方向邻域；P先于S可能删除断点触发点。四种危险顺序被实际拒绝。S-P-D仍有权衡，P即时误差不能冒充后续D删除后的最终保证。'''),
        code("show([r for r in stage['orders'] if r['partition']=='DEVELOPMENT'],['order','n_records','safety_failure_records','raw_break_crossings','direction_windows_across_raw_breaks','p_removed_raw_break_trigger_points','research_status'])\nfigure('order_protection_and_neighborhoods')"),
        md('''## 6. 真实 AI 批判与至少一组可复验反例

记录7764的合法建议提出额外空间分段。实际同一122点覆盖下共同最大误差40.215→69.145工作米，而自身P误差同为4.826；因此未采用。另一建议失去11个参考覆盖点，此时基线完整集合误差不可用，不能把null写成“数值变差”。完整原始引文与response哈希如下。构造标签只适用于已知答案，不迁移为真实噪声真值。'''),
        code('''ai=read_json(G2/'a_epoch02/actual_ai_critique/actual_ai_critique.json')
show([{'id':x['citation_id'],'record':x['record_id'],'original_reason':x['verbatim_model_reason'],
       'parameters':x['candidate_parameters'],'locked_output':x['proposal_became_locked_output'],
       'source_response':x['raw_response']} for x in ai['actual_ai_citations']],limit=6)
synthetic=read_json(G2/'counterexamples/formal-02/synthetic_cases.json')
show([{'case':c['case_id'],'before_after':c['before_after'],'known_answer_checks':len(c['known_answer_checks'])}
      for c in synthetic['cases']],limit=6)
# 从完整已保存构造输入重新执行19条处理链，比较真实输出；不是新独立实验。
synthetic_recomputations=0
for case in synthetic['cases']:
    for name,payload in case['executions'].items():
        expected=payload['output']
        rebuilt=run_record(expected['source_record'],expected['parameters'],expected['order'],
                           contract_hash=expected['contract_hash'],provenance=expected['provenance'])
        assert object_hash(rebuilt)==object_hash(expected),(case['case_id'],name)
        synthetic_recomputations+=1
assert synthetic_recomputations==19
print('当前内核已知答案处理链实际复算：',synthetic_recomputations)
print('完整构造与独立检查入口：task1/evidence/goal2/counterexamples/formal-02/')
figure('synthetic_metric_counterexamples')'''),
        md('''## 7. 冻结策略下全量生产：真实复算全部原始记录

最终确认在冻结规则下已经完成，本单元复算冻结生产策略与R0；若完全相同只复用一次。生产包含全部分区，其统计描述本数据集输出，不把开发使用过的记录重新当成独立测试。每条记录和每个点终态均保留；候选失败、回退和最终输出不能混为一个通过率。'''),
        code('''production_recompute=run_logged('production',lambda:recompute_production(WORK/'production'))
assert production_recompute['raw_records']==len(raw)==11386
rebuilt_production=read_json(WORK/'production'/'manifest.json')
show([{'strategy':cid,**values} for cid,values in rebuilt_production['record_metrics'].items()],
     ['strategy','n_records','n_input','n_filtered','n_direction_removed','n_dp_removed','n_final',
      'common_covered_points','n_no_output_records','raw_break_crossings','dp_max_error'])
show([{'strategy':cid,'parameters':entry['parameters'],'order':entry['order'],
       'conditional_rule':entry.get('conditional_rule')} for cid,entry in rebuilt_production['strategies'].items()])
confirm_path,confirmation=current_manifest('FINAL_CONFIRM')
print('最终确认（历史冻结执行，与全量统计分开）：',len(confirmation['input_ids']),'条。')
show([{'pair':key,**value} for key,value in confirmation['comparisons'].items()])
print('全量分片字节哈希重算一致：',production_recompute['actual_full_shard_hash_equality'])
recomputed_figure('production','recomputed_point_fates')
recomputed_figure('production','recomputed_trajectory_case')
print('以下为已核验 G3 阶段归档图；与上方本次 raw 复算重绘图分开。')
figure('development_candidates',phase='goal3')
figure('incumbent_decision_path',phase='goal3')
figure('selection_tradeoffs',phase='goal3')
figure('final_confirmation_pairs',phase='goal3')
figure('point_fates_and_coverage',phase='goal3')
figure('production_trajectory_cases',phase='goal3')'''),
        md('''## 8. 完成读数与复现边界

保存的 Notebook 输出来自本次实际 full 路径；历史模式和记忆的完整复算见另一份系统完成版。研究结论仍区分范围内支持、未证明收益、权衡和工程已验证。源datum未证实、无噪声真值、记录不等于独立用户；使用这些局限解释结果，不把它们填成已经解决。'''),
        code("receipt={'notebook':'basic','historical_record_candidate_recomputations':parameter_recompute['candidate_record_recomputations'],\n         'production_raw_records':production_recompute['raw_records'],'production_record_evaluations':production_recompute['record_evaluations'],\n         'synthetic_pipeline_recomputations':synthetic_recomputations,'known_exposed_pilot_runs':1,\n         'new_parameter_plots':parameter_recompute['raw_recomputed_plots'],'new_production_plots':production_recompute['raw_recomputed_plots']}\n"+END),
    ]


def system():
    return [
        md('''# 实验一 · LLM辅助评估清洗完成版

对应教师 `任务3_LLM辅助评估清洗.ipynb` 的工具、四模式和记忆任务。这里展示真实调用过的模型建议与评价，而非Mock；默认离线从raw复算已经发生的完整候选与记录选择，**不新增模型调用**。

系统包括治理工作流A/B/C与控制器、被测记录级四模式，两层成本分开。默认full恢复历史记忆搜索及模式合计6,001次记录—候选计算、384次原记录episode选择，并从本次新结果重新绘制模式图。最终统一/条件策略由G3真实结果冻结，不能把固定参数的全量处理继续叫逐条LLM。可用 `SC_LAB1_RECOMPUTE_WORK` 指定工程外的新输出目录；已有非空目录会被拒绝。''',(0,2,6,7,8,9,10,11,12,13,19,20,21,22,23,24,25,30,31)),
        code(SETUP),
        md('''## 1. 工具与角色的真实边界

A根据可访问开发证据提出有限TaskPlan；B在固定代码/合同下运行；C从可信原始范围独立核验；确定性控制器维护依赖、预算、回执和恢复，不是第四个模型。普通实现缺陷走修复→独立复验→失效依赖重建→恢复父任务。

被测模式只调用允许的处理、诊断、评价、检索工具。Search only的记录级LLM调用为0，治理A不能实时暗示其参数。下图是历史G2实际结构，当前G3治理与最终生产接口见本轮Technical Handoff。''',(6,7,8,9,10,11,12,13)),
        code("figure('goal2_actual_architecture')\nprint('处理入口：task1.workflow.g2_pipeline.run_record')\nprint('可信审核：task1.workflow.g2_metrics.review_record')\nprint('有限选择：task1.workflow.g2_selection.select_record')\nprint('当前生产：task1.goal3.runtime.evaluate；默认离线复算 task1.goal3.reproduce')"),
        md('''## 2. 四模式与公平预算

| 模式 | 能看到的输入 | 真实结构 |
|---|---|---|
| LLM only | 原始诊断 | 一次提议，无搜索反馈/记忆，再实际评价 |
| Search only | 原始记录+冻结配置序列 | 最多20候选，0模型调用 |
| LLM + Search | 原始诊断+本记录允许反馈 | 最多3回合，累计8/14/20候选 |
| LLM + Memory + Search | 同上+冻结DEMO只读检索 | 相同预算，不写评估记录到记忆 |

每批最多8张诊断卡，一次batch请求只计一次调用。开发同24条×1episode，G2评估同24条×3episodes，不从三次中只挑最好一次。失败、非法原提议、回退全入分母，不能通过静默clamp把非法参数改成合法。''',(19,20,21)),
        md('''## 3. 从原始输入重新执行历史候选与选择

这一步逐条重算已保存真实提议对应的处理和评价，并核对原始锁定选择；仅复用真实模型建议本身，不请求模型重答。新模型调用由两个Provider入口的实际哨兵测量为0；记忆hash前后核对。'''),
        code('''mode_recompute=run_logged('modes',lambda:recompute_historical('modes',WORK/'modes'))
assert mode_recompute['candidate_record_recomputations']==6001
assert len(mode_recompute['selections'])==384
assert all(row['selection_match'] for row in mode_recompute['selections'])
recomputed_figure('modes','recomputed_modes')
show(stage['mode_summary'],['partition','mode','original_records','episodes','record_episode_observations',
                          'protected_gain_records_episodes','candidate_evaluations','experiment_model_dispatches',
                          'fallback_records_episodes','elapsed_batch_seconds_sum'])
assert all(r['experiment_model_dispatches']==0 for r in stage['mode_summary'] if r['mode']=='search-only')
figure('four_mode_paired_results')
figure('four_mode_failures_and_cost')'''),
        md('''## 4. 原样建议、核验和拒绝

模型原话被保存，并在执行前检查参数域、预算与权限。合法建议仍可能因共同覆盖或几何保护失败而不被采用。有效开发148个原提议中70个方向预测可评价且一致，其余有不可评价原因；没有观察到非法提议/方向预测错误/回退，不能为展示批判制造事件。真实存在的4个合法权衡建议完整保留。

下面展示真实response来源和具体比较，尤其留意记录7764的同集合误差退化、失去11个原覆盖身份后null的含义，以及记录10232正确预测删除数下降的正例。'''),
        code('''ai=read_json(G2/'a_epoch02/actual_ai_critique/actual_ai_critique.json')
show([{'id':x['citation_id'],'record':x['record_id'],'reason_verbatim':x['verbatim_model_reason'],
       'parameters':x['candidate_parameters'],'legal':x['legal'],'executed':x['executed'],
       'selected':x['proposal_became_locked_output'],'raw_response':x['raw_response']}
      for x in ai['actual_ai_citations']],limit=6)
show([{'id':x['citation_id'],
       'reference_coverage':x['reference_metrics']['common_covered_points'],
       'candidate_coverage':x['candidate_metrics']['common_covered_points'],
       'reference_common_max':x['reference_metrics']['common_max_error'],
       'candidate_own_common_max':x['candidate_metrics']['common_max_error'],
       'same_common_covered_mask':(x['registered_comparison'] or {}).get('same_common_covered_point_mask'),
       'protection_readings':(x['registered_comparison'] or {}).get('registered_protection_readings')}
      for x in ai['actual_ai_citations'][:3]])
print('覆盖集合不同的两个自身最大值不作配对误差增减；真实数据无噪声真值。')'''),
        md('''## 5. 只读示范记忆：送达、引用、动作与因果分开

DEMO60条用于记忆，其中26条范围内支持、34条无新增收益。六个原始诊断特征只用DEMO缩放；描述层内最多3近邻，排除自身/关联组。评估冻结只读，工作记忆按记录episode隔离，用户知识条目实际为0。

合计96次带记忆记录观察均送达检索；241个决策回合中60次引用、49次动作一致。分母不同。评估带/不带记忆搜索各47/72支持输出，不能因此宣称因果收益或普遍等效。''',(22,23,24,25)),
        code('''print('只读记忆hash：',memory_hash_before)
show([stage['memory']],['demonstration_records','research_status_counts','read_only_policy','human_knowledge_entries','work_memory_persisted'])
with (G2/'tables/memory_consumption.csv').open(encoding='utf8',newline='') as stream:
    consumption=list(csv.DictReader(stream))
print('完整记忆消费记录行数：',len(consumption))
show(consumption,limit=8)
figure('memory_coverage_and_consumption')
assert digest(memory_path)==memory_hash_before'''),
        md('''## 6. 真正的新调用与成本

历史有效实验模型调用84次；历史失效/中断15次、工程资格1次另记。模型为既有Codex通道gpt-6-astra/medium，没有固定seed或精确snapshot。隐藏底层请求和货币费用不可见时保持unknown，不填0。

本Notebook只复算。需要新LIVE时必须创建新run、使用已授权provider和完整预算/权限/回执入口，不能把此处字符串改成LIVE就静默发请求。下面只用当前Python解释器查看CLI帮助，不调用provider。''',(30,31)),
        code('''import subprocess
help_result=subprocess.run([sys.executable,'-m','task1.scripts.goal2','--help'],cwd=ROOT,
                           text=True,capture_output=True,check=True)
print(help_result.stdout)
resources=stage['resource_accounting']
show([{'scope':'current_valid',**resources['current_valid_model_costs']},
      {'scope':'historical_superseded_or_interrupted',**resources['historical_model_costs']}],
     ['scope','visible_experiment_model_dispatches','completed_calls','interrupted_or_failed_calls',
      'provider_request_count','currency_cost','counts_as_current_effectiveness_evidence'])'''),
        md('''## 7. 当前冻结生产策略与系统选择

当前结果从生产freeze与真实run读取。统一确定性配置、简单规则或逐条搜索/模型是记录级算法身份；治理使用A/B/C不改变该身份。最终确认和生产记忆保持只读，不使用最终评分更新参数或规则。全量处理与最终确认原始记录分母不同。'''),
        code('''production_path,production=current_manifest('FULL_PRODUCTION')
show([{'strategy':cid,'parameters':value['parameters'],'order':value['order'],
       'conditional_rule':value.get('conditional_rule')} for cid,value in production['strategies'].items()])
print('全量生产原始记录:',len(production['input_ids']))
confirm_path,confirmation=current_manifest('FINAL_CONFIRM')
print('一次性最终确认原始记录:',len(confirmation['input_ids']))
show([{'pair':key,**value} for key,value in confirmation['comparisons'].items()])
figure('goal3_actual_workflow',phase='goal3')
print('实际独立核验、恢复和版本入口：task1/evidence/goal3/REVIEW_PACKET.md')'''),
        md('''## 8. 交付与真实互动边界

技术报告给方法与结果，Process Report保留Workflow Construction和Experiment Decision Process两层。缺真实截图、Evidence Master规格或Lock时文档标待补，不能用Agent互评代替人类判断。用户Understanding和网页GPT二重审核不由Notebook自动设PASS。教师包实际准备但不代发邮件。'''),
        code("receipt={'notebook':'llm_system','historical_record_candidate_recomputations':mode_recompute['candidate_record_recomputations'],\n         'recomputed_original_record_episode_selections':len(mode_recompute['selections']),\n         'new_mode_plots':mode_recompute['raw_recomputed_plots']}\n"+END),
    ]


def build():
    DEST.mkdir(parents=True,exist_ok=True)
    written=[]
    specs=[('作业1轨迹数据预处理_完成版.ipynb',basic(),'task1/作业/作业/作业1轨迹数据预处理.ipynb','8601d1dfecaef062fef553992cc9774d3a0eb551751c70536f5b52f1343b158a'),
           ('任务3_LLM辅助评估清洗_完成版.ipynb',system(),'task1/作业/作业/任务3_LLM辅助评估清洗.ipynb','4ecffe64024e002c0cffe7830e18b5f6ded04cd5aa9dd645d6798fc9b0715add')]
    for name,cells,starter,starter_hash in specs:
        nb=nbf.v4.new_notebook(cells=cells,metadata={
            'kernelspec':{'display_name':'Python 3 (project dependencies)','language':'python','name':'python3'},
            'language_info':{'name':'python','version':'3'},
            'teacher_correspondence':{'starter':starter,'starter_sha256':starter_hash,'original_untouched':True},
            'default_execution':'FULL_RECOMPUTE','new_live_enabled':False,
            'generation_does_not_execute':True})
        for i,cell in enumerate(nb.cells):
            cell['id']='lab1-'+hashlib.sha256((name+str(i)+cell.source).encode()).hexdigest()[:16]
            if cell.cell_type=='code': ast.parse(cell.source)
        nbf.validate(nb)
        path=DEST/name;nbf.write(nb,path)
        written.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'cells':len(cells),'code_cells':sum(c.cell_type=='code' for c in cells),
                        'execution_status':'NOT_RUN_PENDING_FINAL_PRODUCTION','teacher_starter':starter})
    out=ROOT/'task1/evidence/goal3/report_build/notebook_source_build.json'
    figures=['segmentation_filter_grids','direction_threshold_and_neighborhood','dp_error_compression',
             'order_protection_and_neighborhoods','synthetic_metric_counterexamples','goal2_actual_architecture',
             'four_mode_paired_results','four_mode_failures_and_cost','memory_coverage_and_consumption']
    dependencies=['task1/evidence/goal2/result_summary.json',
                  'task1/evidence/goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json',
                  'task1/evidence/goal2/counterexamples/formal-02/synthetic_cases.json',
                  'task1/evidence/goal2/tables/memory_consumption.csv',
                  'task1/evidence/goal2/runs/g2-demo-memory-02/memory_snapshot.json',
                  'templates/latex/common/p2_cloud_sorbet_colors.tex']+[f'task1/figures/goal2/{n}.png' for n in figures]
    receipt={'status':'SOURCE_VALIDATED_NOT_EXECUTED','notebooks':written,'new_model_calls':0,'new_method_runs':0,
             'explicit_display_dependencies':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in dependencies},
             'full_runtime_dependency_closure':'Requires portable registry/raw/code/freeze package; isolated ZIP execution still NOT_RUN',
             'static_checks':{'code_ast':True,'nbformat_v4':True,'new_kernel_execution':False},
             'expected_generated_dependencies':[f'task1/figures/goal3/{n}.png' for n in ['development_candidates','point_fates_and_coverage','final_confirmation_pairs','production_trajectory_cases','goal3_actual_workflow','incumbent_decision_path','selection_tradeoffs']],
             'expected_full_recomputations':{'basic_historical_parameters_orders':9720,'basic_synthetic_chains':19,
                  'basic_exposed_pilot_examples':1,'basic_production_raw_records':11386,
                  'system_historical_candidates_including_demo':6001,'system_original_record_episode_selections':384}}
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'SOURCE_VALIDATED_NOT_EXECUTED','notebooks':written},ensure_ascii=False))
    return written

if __name__=='__main__': build()
