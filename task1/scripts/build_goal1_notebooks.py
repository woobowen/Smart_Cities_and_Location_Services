"""Generate working notebooks without touching either teacher notebook."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'task1/notebooks'


def markdown(text):return nbf.v4.new_markdown_cell(text)
def code(text):return nbf.v4.new_code_cell(text)


SETUP="""from pathlib import Path
import json, sys
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'AGENTS.md').exists())
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from task1.workflow.io import DATA, CONFIG, EVIDENCE, read_json, digest
from task1.workflow.diagnostics import profile, aggregate, time_boundaries, independent_profile_review
from task1.workflow.tools import execute_tool
policy=read_json(CONFIG); pilot=read_json(ROOT/'task1/config/pilot.json')
assert digest(DATA)==policy['raw_sha256']==pilot['raw_sha256']
raw=read_json(DATA)
print('模式：RECOMPUTE；本次模型调用：0')
print('原始输入 SHA256:', digest(DATA))
print('固定开发样本:', pilot['ids'])"""


def save(name,cells):
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                                              'language_info':{'name':'python'}})
    nbf.write(nb,OUT/name)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    save('01_baseline_and_audit.ipynb',[
        markdown('# Goal 1：真实开发数据、基线门控与独立审核\n\n教师映射：`task1/作业/作业/作业1轨迹数据预处理.ipynb` → 本工作版。教师文件未修改。这里只报告本轮数据结构及明确的工程检查；真实米制三步链因 datum/距离口径与去噪删除调度未知而 **BLOCKED**。没有合成输入替代真实处理，没有方法最优结论。'),
        code(SETUP),
        markdown('## 数据口径与固定样本\nUnix 秒与 (lon,lat) 度为补充讲义声明；CRS UNKNOWN。7例属于开发暴露，无最终留出冻结。下列代码实际读取原始JSON并重算，未读旧CSV替代计算。'),
        code("rows=[profile(k,raw[k]) for k in pilot['ids']]\nsummary=aggregate(rows)\nprint(json.dumps({k:v for k,v in summary.items() if k!='dt_counts'},ensure_ascii=False,indent=2))"),
        markdown('## 三步参考链与当前阻断\n顺序来自基础 Notebook：分段/过滤→方向去噪→DP。65/5/30/400/35/5 是 STARTER_REFERENCE。完整真实链目前不会投影、删点、平滑或改时间；结构化结果保留全部输入为 not_processed。'),
        code("baseline=execute_tool('baseline',pilot['ids'],policy)\nassert baseline['status']=='BLOCKED'\nassert baseline['modified_values']==0\nassert baseline['stage_counts']['not_processed']==summary['n_points']\nprint(json.dumps(baseline,ensure_ascii=False,indent=2))"),
        markdown('## 允许的真实时间诊断\n独立于未知CRS：严格 dt>30 秒（以及负dt）标边界，右点归新片段；这不是完整的时空分段/长度过滤。零dt并不被填成0速度，不删除重复位置。'),
        code("parts=[time_boundaries(k,raw[k],30) for k in pilot['ids']]\nassert all(p['n_accounted']==p['n_input'] and p['modified']==0 and p['deleted']==0 for p in parts)\nfor p in parts: print(p['record_id'], 'input=',p['n_input'], 'time-only partitions=',len(p['partitions']), 'cuts=',len(p['cuts']))"),
        markdown('## 独立审核与已保存结果比较\n独立计数实现不调用 profile；与本轮保存的原始结构诊断逐对象比对。工程有效与质量接受分开。'),
        code("review=independent_profile_review({k:raw[k] for k in pilot['ids']},rows)\nassert review['status']=='VERIFIED'\nstored=read_json(ROOT/'task1/results/goal1/pilot_diagnostics.json')\nassert rows==stored['profiles']\nassert parts==stored['time_boundaries']\nassert digest(DATA)==policy['raw_sha256']\nprint(review)\nprint('与保存记录重算一致；真实三步处理仍 BLOCKED。')"),
        markdown('## 本轮必要图与限制\n图仅编码7条开发记录原始相邻边的诊断计数，不是清洗前后图；无CRS推断、无底图。有限线段/DP/方向关系反例属于独立测试中的 CONSTRUCTED_FIXTURE，不属于本Notebook的真实轨迹结果。'),
        code("from IPython.display import display, Image\ndisplay(Image(filename=str(ROOT/'task1/figures/goal1/pilot_diagnostics.png')))"),
    ])
    save('02_agent_loop_recompute.ipynb',[
        markdown('# Goal 1：真实角色记录与离线复算\n\n教师映射：`任务3_LLM辅助评估清洗.ipynb` → 本入口。默认不会调用模型。LIVE、REPLAY、MOCK_TEST 明确分开；工程测试不冒充自然Agent失败或真实Human–AI争论。'),
        code(SETUP),
        code("MODE='RECOMPUTE'\nRUN_ID='g1-live-20260926-03'\nENABLE_LIVE=False\nassert MODE in ('RECOMPUTE','LIVE')"),
        markdown('## 历史运行与失败边界\nrun03仅 A 研究角色成功并执行 source_evidence；B 因 workspace routing discovery failed 失败，C 未调用，反馈循环未完成。run01/02失败均保留。旧批次因内部重连预算问题冻结。本次修复批次单独授权，实际结果见末尾新增单元。不能把下方离线复算当作补齐三个真实角色。'),
        code("directory=EVIDENCE/'runs'/RUN_ID\nmanifest=read_json(directory/'manifest.json')\nprint('run',RUN_ID,'code',manifest['code_sha'],'mode',manifest['mode'],'status',manifest['status'])\nfor call in manifest['calls']:\n    reply=read_json(directory/call['response'])\n    print(call['role'],call['call_id'],call['thread_id'],reply['action'],reply['feedback_refs'])\nfor tool in manifest['tools']: print('tool',tool['tool_id'],tool['action'],tool['status'])"),
        markdown('## 按已记录代码版本复算实际动作\n控制器已在失败后修复，当前源hash与旧run不同。下面从已存在的Git CODE_SHA恢复任务源码到临时目录，校验hash，再真实重跑旧run唯一成功动作 source_evidence。不会切换当前分支，也不修改旧产物。它只能证明这一项复算一致。'),
        code("if MODE=='RECOMPUTE':\n    from task1.scripts.recompute_archived_run import recompute_archived\n    result=recompute_archived(RUN_ID)\n    assert result['new_model_calls']==0 and result['status']=='VERIFIED'\n    assert [c['action'] for c in result['checks']]==['source_evidence']\n    print(json.dumps(result,ensure_ascii=False,indent=2))\nelse:\n    assert ENABLE_LIVE, '必须显式启用LIVE'\n    assert policy['live_execution_enabled'], policy['live_stop_reason']\n    assert not directory.exists(), '新模型实验须使用新的run_id；不得重置总预算'\n    from task1.workflow.controller import Controller\n    result=Controller(RUN_ID).run()\n    print(result['status'])"),
        markdown('## 当前工程工具的真实数值复算（不是 Agent 后续动作）\n直接从固定7例原始输入重算 profile 与独立核验，再对照保存结果。该计算由Notebook发起，不伪称B/C模型完成了任务。'),
        code("numeric=execute_tool('profile_pilot',pilot['ids'],policy)\nrows=numeric['result']['profiles']\nreview=execute_tool('verify_profiles',pilot['ids'],policy,rows)\nrecheck=execute_tool('recompute_check',pilot['ids'],policy,rows)\nassert review['status']==recheck['status']=='VERIFIED'\nassert rows==read_json(ROOT/'task1/results/goal1/pilot_diagnostics.json')['profiles']\nprint(numeric['input_records'],numeric['input_points'],review['status'],recheck['result']['exact_match'])"),
        markdown('## 状态解释\nVERIFIED 仅为结构/复算有效；没有冻结质量阈值，也没有合法的真实三步全链结果，因此 QUALITY_ACCEPTED 不成立。最终 GPT second review=PENDING，Submission=NOT_READY。'),
        code("checkpoint=read_json(directory/'checkpoint.json')\nassert checkpoint['accepted_version'] is None\nprint('feedback decisions:',json.dumps(checkpoint['decisions'],ensure_ascii=False,indent=2))\nprint('raw hash unchanged:',digest(DATA)==policy['raw_sha256'])"),
    ])


def append_repair():
    for path in OUT.glob('*.ipynb'):
        nb=nbf.read(path,as_version=4)
        nb.cells.extend([
            markdown('## SC-LAB1-G1-REPAIR-001 当前修复复算\n以下为当前代码重新读取教师 JSON 的诊断；旧 run03 的 REPLAY 单独保留。构造处理链测试不代表真实数据已清洗。'),
            code("revision=EVIDENCE/'revisions/SC-LAB1-G1-REPAIR-001'\ncurrent=execute_tool('profile_pilot',pilot['ids'],policy)\nstored=read_json(revision/'results/profile_pilot.json')\nassert current==stored\nchecked=execute_tool('recompute_check',pilot['ids'],policy,current['result']['profiles'])\nassert checked['status']=='VERIFIED' and checked['result']['exact_match']\nprint('当前7条 / 783点复算一致；模型调用0；完整baseline仍BLOCKED')"),
            markdown('## 本批 LIVE 的真实边界\n只读取回执，不调用模型。有效模型响应、数值工具与完整反馈分别按实际产物计数；没有发生的角色不得补写。'),
            code("budget=read_json(EVIDENCE/'runs/budget_repair_001.json')\nprint(json.dumps(budget,ensure_ascii=False,indent=2))\nnew_run=revision/'runs/g1-repair-roles-01/manifest.json'\nprint(read_json(new_run) if new_run.exists() else '角色链NOT_RUN：连通性探针没有通过')\nassert digest(DATA)==policy['raw_sha256']"),
            code("from IPython.display import display, Image\ndisplay(Image(filename=str(revision/'figures/repair_loop.png')))"),
        ])
        nbf.write(nb,path)


if __name__=='__main__':
    main()
    append_repair()
