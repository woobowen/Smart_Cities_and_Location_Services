"""Derive the review ledger from existing requirement/navigation/result sources.

This script checks locators and hashes. It never executes research or grants acceptance.
The two mutable governance inputs require real immutable review snapshots. Missing
or stale snapshot bytes fail closed; advancing active state does not invalidate a
past observation or turn the snapshot into a second active authority.
"""
from __future__ import annotations
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'AGENTS.md').is_file() and (p/'task1').is_dir())
CLOSE=OUT.parent
TASK='SC-LAB1-G3-CLOSEOUT-001'
G1='task1/evidence/goal1'
G2='task1/evidence/goal2'
G3='task1/evidence/goal3'
AUTH=str((CLOSE/'AUTHORIZATION.md').relative_to(ROOT))
MAP=f'{G3}/teacher_delivery_mapping.json'
LIT='task1/docs/research/Task1_Source_Audit_2025_2026_Merged.json'
PPT='task1/实验课1.pptx'
PPT_TEXT=f'{G1}/materials/pptx_05_text_and_notes.md'
NOW=datetime.now(timezone.utc).isoformat()
SNAPSHOT_DIR=str((CLOSE/'review_input_snapshot').relative_to(ROOT))
SNAPSHOT_MANIFEST=f'{SNAPSHOT_DIR}/SNAPSHOT_MANIFEST.json'
SNAPSHOT_PURPOSE='IMMUTABLE_REVIEW_INPUT_SNAPSHOT_NOT_ACTIVE_STATE'
ACTIVE_STATE_LINKS=[f'{G3}/requirements.json',f'{G3}/goal_state.json',str((CLOSE/'ACCEPTANCE_MATRIX.json').relative_to(ROOT))]

def load_review_input_snapshot():
    manifest=json.loads((ROOT/SNAPSHOT_MANIFEST).read_text())
    if manifest.get('purpose')!=SNAPSHOT_PURPOSE:
        raise ValueError('Review snapshot manifest purpose must explicitly reject active-state authority')
    created=manifest.get('created_at')
    if not isinstance(created,str) or datetime.fromisoformat(created.replace('Z','+00:00')).tzinfo is None:
        raise ValueError('Review snapshot manifest requires a timezone-qualified created_at')
    if manifest.get('active_state_links')!=ACTIVE_STATE_LINKS:
        raise ValueError('Review snapshot active_state_links must identify the unique active requirements, goal_state and CL matrix')
    expected={active:f'{SNAPSHOT_DIR}/{Path(active).name}' for active in ACTIVE_STATE_LINKS[:2]}
    rows=manifest.get('sources',[])
    if len(rows)!=2 or {r.get('active_path') for r in rows}!=set(expected):
        raise ValueError('Review snapshot must bind exactly requirements.json and goal_state.json')
    sources={}
    for row in rows:
        active=row['active_path'];snapshot=row.get('snapshot_path')
        if snapshot!=expected[active]:
            raise ValueError(f'Unexpected review snapshot path for {active}')
        path=ROOT/snapshot
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f'Required ordinary review snapshot file missing: {snapshot}')
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if row.get('sha256')!=digest:
            raise ValueError(f'Review snapshot hash mismatch: {snapshot}')
        sources[active]={'path':snapshot,'sha256':digest,'source_active_path':active,'observed_at_utc':created,'snapshot_manifest_path':SNAPSHOT_MANIFEST,'state_semantics':SNAPSHOT_PURPOSE}
    return manifest,sources

SNAPSHOT_META,SNAPSHOT_SOURCES=load_review_input_snapshot()

def observed_path(path):return SNAPSHOT_SOURCES.get(path,{}).get('path',path)
def read(path): return json.loads((ROOT/observed_path(path)).read_text())
def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def ref(path,locator='',kind='ARTIFACT',quote=None):
    active_path=path;path=observed_path(path);p=ROOT/path
    o={'path':path,'sha256':sha(path) if p.is_file() else None,'locator':locator,'source_kind':kind,'exists':p.is_file()}
    if active_path in SNAPSHOT_SOURCES:
        o.update(SNAPSHOT_SOURCES[active_path])
    if quote is not None:o['necessary_quote']=quote
    return o
def link(path,label=None):return f'[{label or Path(path).name}]({os.path.relpath(ROOT/path,OUT)})'
def dump(path,obj):(OUT/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def line_of(path,needle):
    lines=(ROOT/path).read_text().splitlines()
    return next((i+1 for i,x in enumerate(lines) if needle in x),None)
def code(path,names):
    tree=ast.parse((ROOT/path).read_text())
    found={x.name:x.lineno for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
    return [dict(ref(path, f'{name}:L{found.get(name)}','IMPLEMENTATION'),function=name,line=found.get(name)) for name in names]

td=read(MAP);bytd={x['id']:x for x in td['entries']}
reqs={g:{x['id']:x for x in read(f'task1/evidence/goal{g}/requirements.json')['requirements']} for g in [1,2,3]}
g2=read(f'{G2}/result_summary.json');g3=read(f'{G3}/result_summary.json')
current_runs=read(f'{G3}/current_runs.json')
# Read only task-relevant original slide XML; no broad re-render or historical rewriting.
slide_numbers=[5,6,8,17,18,19,20,21,22,24,25,26,28,30,32,33,34,35,36,37,38,42]
slides={}
with zipfile.ZipFile(ROOT/PPT) as z:
    for n in slide_numbers:
        name=f'ppt/slides/slide{n}.xml';b=z.read(name);r=ET.fromstring(b)
        text='\n'.join(x.text or '' for x in r.iter() if x.tag.endswith('}t'))
        slides[n]={'physical_slide_one_based':n,'member':name,'member_sha256':hashlib.sha256(b).hexdigest(),'text':text}
dump('teacher_source_recheck.json',{'task':TASK,'role':'A','source':ref(PPT,kind='TEACHER_ORIGINAL'),'scope':'Selected original slide XML text; prior visual mathematics interpretation inherited, not re-rendered here.','slides':list(slides.values())})

def original_sources(tids):
    out=[]; seen=set()
    for tid in tids:
        ent=bytd[tid]
        for rid in ent.get('g1_requirement_ids',[]):
            for s in reqs[1][rid].get('sources',[]):
                key=(s['path'],s.get('locator',''))
                if key not in seen:
                    out.append(ref(s['path'],s.get('locator',''),s.get('source_kind','HISTORICAL_REQUIREMENT_SOURCE')));seen.add(key)
        for sr in ent.get('historical_requirement_sources',[]):
            for n in sr.get('teacher_slide_pages_one_based',[]):
                if n in slides:
                    key=(PPT,f'slide {n}')
                    if key not in seen:
                        # Store exact source separately; a short necessary phrase serves the ledger.
                        lines=[t for t in slides[n]['text'].splitlines() if t.strip()]
                        out.append(ref(PPT,f'物理第{n}页 / ppt/slides/slide{n}.xml','TEACHER_ORIGINAL',' / '.join(lines[:4])));seen.add(key)
    return out

def normal(s):return re.sub(r'\s+','',s)
pages={}
for key,path in [('E','task1/reports/experiment1/experiment1.pdf'),('P','task1/reports/process1/process1.pdf')]:
    raw=subprocess.check_output(['pdftotext','-layout',str(ROOT/path),'-']).decode('utf-8')
    arr=raw.split('\f')
    if arr and not arr[-1].strip():arr.pop()
    pages[key]={'path':path,'sha256':sha(path),'page_texts':arr,'page_count':len(arr)}

def locators(tids):
    notebooks=[];reports=[];nbseen=set();rpseen=set()
    for tid in tids:
        for n in bytd[tid].get('notebooks',[]):
            nb=read(n['path']);cells={c['id']:(i,c) for i,c in enumerate(nb['cells'])}
            for c in n['cells']:
                cid=c['cell_id'];key=(n['path'],cid)
                if key in nbseen:continue
                nbseen.add(key);current=cells.get(cid)
                if current:
                    idx,cell=current;source=''.join(cell.get('source',[])) if isinstance(cell.get('source'),list) else cell.get('source','')
                    notebooks.append({'path':n['path'],'stable_cell_id':cid,'physical_index_zero_based':idx,'cell_type':cell['cell_type'],'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'first_line':source.splitlines()[0] if source else '', 'td_id':tid,'checked':'CURRENT_CELL_SOURCE_LOCATED; execution receipt remains separate'})
                else:notebooks.append({'path':n['path'],'stable_cell_id':cid,'checked':'CELL_MISSING'})
        for r in bytd[tid].get('reports',[]):
            anchor=r['verified_text_anchor'];key=(r['report'],anchor)
            if tid=='TD-20' and anchor=='待补姓名':anchor='吴博闻';key=(r['report'],anchor)
            if tid=='TD-22' and anchor=='REVIEW_ONLY':anchor='NOT_READY';key=(r['report'],anchor)
            if key in rpseen:continue
            rpseen.add(key);p=pages[r['report']]
            physical=[i+1 for i,t in enumerate(p['page_texts']) if normal(anchor) in normal(t)]
            # Identity appears only on the cover; a report may have a TOC occurrence too.
            reports.append({'path':p['path'],'pdf_sha256':p['sha256'],'page_count':p['page_count'],'physical_pages_one_based':physical,'text_anchor':anchor,'section_or_figure':r['section_or_figure'],'historical_mapping_pages':r['pdf_pages_one_based'],'checked':'CURRENT_PDF_TEXT_ANCHOR_LOCATED_NOT_VISUAL_REVIEW' if physical else 'ANCHOR_NOT_FOUND_REQUIRES_NAVIGATION_REPAIR','td_id':tid})
    return notebooks,reports

# Evidence families are shared definitions, not separate pass/fail matrices.
GEO='task1/workflow/geometry.py'; MET='task1/workflow/g2_metrics.py'
GROUPS={
 'S': {'code':code(GEO,['split_trajectory','filter_segments']), 'evidence':[f'{G3}/result_summary.json',f'{G3}/full_filter_attribution.json',f'{G3}/independent_c/production_closure_receipt.json'], 'check':'同一原始输入与冻结R0/S0，严格>切边、严格<过滤、边右归和原始身份守恒。','metric':'分段与过滤点数；点终态分母全部1,173,410原始点；记录分母11,386。','actual':f"R0/S0均{g3['production']['summaries']['R0']['n_s_segments']:,}段；过滤{g3['production']['summaries']['R0']['n_filtered']:,} / {g3['production']['summaries']['S0']['n_filtered']:,}点。",'limit':'可恢复几何覆盖不等于恢复干净轨迹；source_crs未认证。'},
 'D': {'code':code(GEO,['direction_candidates','denoise_trajectory','recompute_features']), 'evidence':[f'{G1}/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json',f'{G2}/tables/exposed_pilot_direction.csv',f'{G3}/result_summary.json'], 'check':'教师双侧outgoing方向谓词；D2同时删除，端点/不可计算窗口保留，后续重算。','metric':'D删除与不可计算原因逐点保存；方向角单位度，几何工作米。','actual':f"全量R0/S0 D删除{g3['production']['summaries']['R0']['n_direction_removed']:,} / {g3['production']['summaries']['S0']['n_direction_removed']:,}。记录352/index105由D删除。",'limit':'删除仅是规则动作，没有真实噪声标签；D前点不属于P误差保证。'},
 'P': {'code':code(GEO,['point_segment_distance','douglas_peucker_indices']), 'evidence':[f'{G2}/counterexamples/formal-02/manifest.json',f'{G3}/result_summary.json',f'{G3}/independent_c/g3-full-production-01_categories_receipt.json'], 'check':'有限线段投影裁剪、端点重合、严格阈值、原始索引、dp=0保全；独立输入对应距离核验。','metric':'P省点率=1-N_P_out/N_P_in；误差只对完整即时P输入，不是raw真值误差。','actual':f"全量R0/S0 P删除{g3['production']['summaries']['R0']['n_dp_removed']:,} / {g3['production']['summaries']['S0']['n_dp_removed']:,}；两者即时max={g3['production']['summaries']['S0']['dp_max_error']:.9f}工作米。",'limit':'不能把5工作米预算用于被D先删的原始点或证明真实定位精度。'},
 'METRIC': {'code':code(MET,['common_reference_metrics','record_metrics','summarize','review_record']), 'evidence':[f'{G2}/result_summary.json',f'{G3}/result_summary.json',f'{G3}/independent_c/production_closure_receipt.json'], 'check':'共同raw窗口固定；保留身份、同片段夹持边、覆盖集合和不可计算原因分别检查。','metric':'coverage=共同可计算原始点/N_raw；retention=N_final/N_raw；记录统计保留有效/null分母。','actual':f"全量共同覆盖{g3['production']['summaries']['R0']['common_covered_points']:,}→{g3['production']['summaries']['S0']['common_covered_points']:,}；显式{g3['production']['summaries']['R0']['n_final']:,}→{g3['production']['summaries']['S0']['n_final']:,}；无输出{g3['production']['summaries']['R0']['n_no_output_records']:,}→{g3['production']['summaries']['S0']['n_no_output_records']:,}。",'limit':'无噪声标签，不称准确率；无获批标量目标，normalized regret不可用。'},
 'PARAM': {'code':code('task1/workflow/g2_experiments.py',['run_parameters']), 'evidence':[f'{G2}/runs/g2-development-parameters-02/manifest.json',f'{G2}/tables/parameter_records.csv',f'{G2}/tables/stable_intervals.csv',f'{G2}/c_contract/development_parameters_epoch02_receipt.json'], 'check':'规定S两5×5网格与OAT、5方向值、7DP值；同记录、参考和预登记保护。','metric':'开发120记录，59唯一配置；评估120记录，14代表配置；重复配置不算新独立样本。','actual':'C-S评估120条全部保护，53条严格改善；C-D/C-P均保留R0，无统一新赢家。','limit':'完整参数实验不是任一参数普遍最优的证明；未新增本轮调参。'},
 'ORDER': {'code':code('task1/workflow/g2_pipeline.py',['run_record']), 'evidence':[f'{G2}/runs/g2-development-orders-02/manifest.json',f'{G2}/tables/order_configurations.csv',f'{G2}/result_summary.json'], 'check':'六排列实际执行；不在S之前暗加切分；核原断点跨越、触发点、方向邻域与最终误差。','metric':'DEVELOPMENT每顺序120记录；失败按记录，跨边/窗口另按事件，不混分母。','actual':'D-S-P、D-P-S、P-S-D、P-D-S各有46/87/87/87条安全失败；S-P-D保留为权衡，最终S-D-P。','limit':'失败顺序被正确执行；拒绝是规则内研究结果，不修成胜出。'},
 'AI': {'code':code('task1/workflow/g2_modes.py',['validate_response','run_batch_episode']), 'evidence':[f'{G2}/a_epoch02/actual_ai_critique/actual_ai_critique.json',f'{G2}/counterexamples/formal-02/manifest.json',f'{G2}/tables/ai_legal_proposal_tradeoffs.csv'], 'check':'引真实response绑定参数/执行/同集合前后指标；构造已知答案与自然AI提议分开。','metric':'记录7764同122个共同覆盖点的max；6组合成例、19处理链、25已知答案检查不作为总体样本。','actual':'真实合法建议共同max 40.215→69.145工作米，自身P 4.826仍合格；后续丢11覆盖身份，null不能当误差上升。','limit':'原模型没有承诺真值准确率；不伪造用户拒绝、非法提议或自然噪声标签。'},
 'MODES': {'code':code('task1/workflow/g2_modes.py',['dispatch','run_batch_episode']), 'evidence':[f'{G2}/result_summary.json',f'{G2}/tables/mode_summary.csv',f'{G2}/tables/model_calls.csv'], 'check':'llm-only无搜索反馈/记忆；search-only Provider哨兵；其余两模式实测反馈，唯一差别记忆。','metric':'开发24记录×1episode；评估24记录×3episode=每模式72观测，非72独立记录；有效模型派发84批。','actual':'评估LLM-only 15/72、Search-only 27/72、LLM+Search 47/72、LLM+Memory+Search 47/72支持输出；search-only记录级调用0。','limit':'预算上限相同不等于实耗相同；新增记忆没有已证因果收益。'},
 'MEMORY': {'code':code('task1/workflow/g2_memory.py',['feature_vector','build_snapshot','FrozenMemory','retrieve','consumption']), 'evidence':[f'{G2}/runs/g2-demo-memory-02/memory_snapshot.json',f'{G2}/tables/memory_consumption.csv',f'{G2}/tables/memory_independent_mode_comparison.csv'], 'check':'60条DEMO构建、六特征尺度只从DEMO，完整分区/关联组排除、snapshot hash与写拒绝检查。','metric':'retrieved→eligible→delivered→model_cited→action_consistent分别统计；评估按24记录×3重复。','actual':'60条记忆含26条范围内收益、34无收益；人类知识条目0；评估带/不带记忆均47/72支持输出。','limit':'送达或动作一致不证明因果收益，独立真实调用间差异不能只归因记忆。'},
 'SELECT': {'code':code('task1/goal3/selection.py',['paired','aggregate_pairs','choose']), 'evidence':[f'{G3}/A3_DECISION.json',f'{G3}/selection_freeze.json',f'{G3}/selection_decision.json',f'{G3}/final_freeze.json',f'{G3}/release_decision.json'], 'check':'单项→组合/移除→240选择→冻结→600最终确认；共同保护全满足再判严格收益。','metric':'开发240已暴露记录，选择240，最终确认600/62,284点；全量生产不作第二次独立测试。','actual':'S0_G0开发相对S0 41条几何改善，选择3017/9311/9534退化回退S0；确认600全保护、349严格覆盖改善、+26,352覆盖。','limit':'冻结确认没有重新选择参数；不声明全局最优或新用户逐条确认。'},
 'WORKFLOW': {'code':code('task1/goal3/control.py',['submit','accept','issue','repair','close_issue','invalidate_changed','checkpoint']), 'evidence':[f'{G2}/PROCESS_RECORD.md',f'{G3}/goal_state.json',f'{G3}/independent_c/internal_acceptance_receipt.json',f'{G3}/repairs/NB01_attempt2_impact.json'], 'check':'真实A/B/C上下文、可信参考绑定、issue→repair→regression→rebuild→review→resume；普通函数仍称工具。','metric':'审核范围以具体targets/source hashes及全检/独立抽查区分；不把测试数作实验量。','actual':'历史G3有13项真实工程闭合；全量22,772轨迹原件核验，独立数学50记录/100轨迹；坐标阶段独立56记录/112轨迹。','limit':'历史内部C不替新版本报告/包验收，不替Human Understanding或Evidence Lock。'},
 'DELIVERY': {'code':code('task1/goal3/reproduce.py',['recompute_historical','recompute_production'])+code('task1/goal3/package.py',['build','verify_directory']), 'evidence':[f'{G3}/teacher_delivery_mapping.json',f'{G3}/closeout/{TASK}/c_review/notebooks_task_receipt.json',f'{G3}/closeout/{TASK}/c_review/notebook_runs_receipt.json',f'{G3}/closeout/{TASK}/c_review/package_task_receipt.json',f'{G3}/closeout/{TASK}/c_review/package_execution_equivalence.json'], 'check':'源与PDF/Notebook/ZIP绑定；当前仓库与同一ZIP独立解压新内核FULL由本轮回执判定。','metric':'每对Notebook应覆盖9720历史参数/顺序+6001历史候选+384episode+22772全量策略记录处理；新增模型0。','actual':'本轮四次新内核FULL及独立C已完成：基础12/12、系统8/8各在仓库与同一解压目录一次；当前包仅报告/manifest修订，完整运行闭包113成员逐字节等价。每次新增记录级模型调用0；这是本轮复现，不新增独立研究样本。','limit':'完整Process互动外部依赖、用户理解和新网页GPT二重审核仍独立；不发送教师。'},
 'REPORT_CURRENT': {'code':[], 'evidence':[f'{G3}/closeout/{TASK}/c_review/report_tasks_receipt.json',f'{G3}/closeout/{TASK}/c_review/visual_content_receipt.json',f'{G3}/closeout/{TASK}/c_review/report_numbers_receipt.json'], 'check':'当前Experiment正文、表图数值与来源及200dpi全部22物理页由独立C核对；修订变页重新查看。','metric':'22/22当前Experiment物理页实际视觉覆盖，回执绑定最终PDF和每页PNG；数值核对按实际源表/分母而非图页存在。','actual':'本轮Experiment全文、视觉和对应报告任务的限定内部审核已完成；C回执记录当前有效字节和核查范围。','limit':'内部C不能代替新网页GPT二重审核或用户逐项理解；不据此关闭Process真实互动证据或Submission门槛。'},
 'UPLOAD_BUNDLE': {'code':code('evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py',['source_rows','verify_bundle','verify_manifest','verify_skill']), 'evidence':[f'{G3}/closeout/{TASK}/upload_bundle_check_output.txt','evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md','AGENTS.md'], 'check':'本轮实际执行既有sync_sources.py --check，只读核对固定allowlist、普通文件集合、active与bundle字节、Skill原始分发与installed effective members及内部manifest。','metric':'固定11文件；集合与canonical命名必须完全相等；SHA256逐项相同；身份、review指南和任务ZIP不加入集合。','actual':'本轮--check真实输出UPLOAD_BUNDLE_CONTENT: PASS; EXACTLY 11; internal manifest verified；未修改固定11文件集合。','limit':'仅证明仓库Upload-Ready Bundle与active来源一致；不证明ChatGPT UI已上传或Project Settings已更新。'},
 'SOURCE': {'code':[], 'evidence':[LIT,'task1/docs/research/Task1_Literature_Review_2025_2026_Merged.md',f'{G3}/A_CANDIDATE_RATIONALE.md'], 'check':'26来源按实际访问层级、论文出版年/会议年、建议与实现/因果分开。','metric':'来源范围22论文+4官方文档；数量仅索引，不是质量指标或最低采用数量。','actual':'正式报告只引用具体转换语义与选择偏差命题；G3已读S08/S10/S17/S21/D03审计段，未复现论文算法。','limit':'正文相似不能倒推灵感；SHoTClean/TAV/PED/STR未全文核读不引用定理与性能。'},
 'EVIDENCE': {'code':[], 'evidence':['evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md',f'{G3}/interaction_candidates.json','task1/docs/goal3/INTERACTION_HANDOFF.md'], 'check':'任务限定目录真实原文/原图/spec/Lock盘点；只保留有来源候选，无spec不画高亮/因果关系。','metric':'证据条目状态与对应批准版本，缺原件/spec/Lock不以工程截图或render DPI补齐。','actual':'可用授权文本与模型response；当前Evidence Plan无登记正式Evidence，完整原图/呈现spec/Lock未闭合。','limit':'身份已由本轮用户提供，不再是外部缺项；A/B/C不能代锁或虚构用户已理解。'},
}
# Function names come from AST; use the exact real parameter runner.
if not GROUPS['PARAM']['code'][0]['line']:
    tree=ast.parse((ROOT/'task1/workflow/g2_experiments.py').read_text())
    GROUPS['PARAM']['code']=code('task1/workflow/g2_experiments.py',[x.name for x in tree.body if isinstance(x,ast.FunctionDef) and ('run' in x.name or 'grid' in x.name)])

entries=[]
def add(i,title,tids,groups,g3ids,why,status='有实现与结果证据，待用户审核',remaining='按四块复盘核查含义；当前报告/包接受本轮C与网页GPT新审。',history='',slides_needed=None):
    tids=[f'TD-{n:02}' for n in tids]
    entries.append({'id':i,'requirement':title,'td_ids':tids,'evidence_group_ids':groups,'g3_requirement_ids':[f'G3-A{n:02}' for n in g3ids],'why':why,'status':status,'remaining':remaining,'authorization_history':history,'direct_teacher_pages':slides_needed or []})
add('T1-01','异常时间/空间连接识别与分段',[2],['S'],[2,8],'先阻断异常连接，避免后续D/P跨越固定原始边界。')
add('T1-02','分段后的短距离/少点数片段处理和原因',[2,17],['S','SELECT'],[2,3,8],'保留R0过滤规则与独立原因，S0放宽过滤是经过比较的最终策略，不能取消教学实现。','批准调整实现，范围内覆盖收益已获历史证据支持')
add('T1-03','教师方向关系去噪及获批删除调度',[3],['D'],[2,10],'固定D2使邻域/删除集合唯一；保留不可计算条件。','批准补充调度，待用户审核',history='原PPT未写尽调度；G1 USER_DECISIONS D2真实答复随后批准一次标记同时删除。')
add('T1-04','有限线段 Douglas–Peucker 简化及边界',[4],['P'],[2,10],'修正无限直线/浮点反查索引等starter风险，遵守教师有限线段定义。')
add('T1-05','评价指标定义、参考与分母',[5],['METRIC'],[2,7,8],'共同原始身份约束防止候选用自身clean自证，null不变零。')
add('T1-06','指标设计逻辑和真实结果分析',[5,16,17],['METRIC','SELECT'],[7,8],'同时报告覆盖、显式存储、几何和新增覆盖边界，收益与限制分别说明。')
add('T1-07','基础Notebook空缺、处理程序与实际可运行入口',[2,3,4,12],['S','D','P','DELIVERY'],[2,13],'完成版有可调用S/D/P与原始索引，原starter保持原样；新内核复算核依赖。')
add('T1-08','AI生成内容准确性批判',[11],['AI'],[2,10],'依据实际响应与可信同集合指标，区分合法提议、执行成功与保护失败。',slides_needed=[6])
add('T1-09','至少一组明确反例、真实修改前后指标和拒绝原因',[11],['AI'],[2,10],'真实7764负结果与合成机制反例互补；不能制造人机争论。',slides_needed=[6])
add('T1-10','AI隐含假设及其失效情形',[11],['AI','METRIC'],[2,10],'用P自身误差不能保护D前raw、丢覆盖造成null、正常折返与毛刺混淆揭示假设。',slides_needed=[6])
add('T1-11','独立的数据处理评估报告',[12,17],['REPORT_CURRENT','METRIC'],[15],'独立Experiment Report完整解释定义、实验、真实结论和边界，不让README替代。','当前Experiment全文/视觉限定内部C审核完成；新网页GPT与用户待审','用户与网页GPT按四块指南继续核查；内部C通过不替代最终Deliverable或Understanding判断。')
add('T1-12','包含AI批判的实验过程报告',[11,19,20],['AI','EVIDENCE'],[16],'Part I组织工作流、Part II解释真实实验决定；有源技术正文可交审，真实互动呈现仍必需。','部分完成；互动Evidence外部待补','需要真实原件/完整消息范围、Evidence Master呈现spec及最终Lock；继续保留当前送审报告。')
add('T1-13','Notebook/报告ZIP、规定命名与教师提交条件',[22],['DELIVERY'],[18,20],'构建含运行闭包的新REVIEW_ONLY身份包；教师正式目标名与发送门槛分开。','待审包工程与隔离FULL已获本轮C限定核验；Submission NOT_READY','当前包与实际解压FULL的内容等价已核实；剩余为真实Evidence原件/spec/Lock及网页GPT/用户最终审核，未发送教学邮箱。',slides_needed=[26])
add('T2-01','分段/过滤参数实验',[6],['PARAM','S'],[2,3],'四S参数分开及两小网格验证，允许无效候选保留。')
add('T2-02','方向阈值参数实验',[6],['PARAM','D'],[2,3],'同输入改变direction，数量趋势与噪声准确率分开。','实验完成；无统一新赢家')
add('T2-03','DP容差实验',[6],['PARAM','P'],[2,3],'固定上游比较完整P输入下的误差与省点；共同预算仍5工作米。','实验完成；无统一新赢家')
add('T2-04','三步换序讨论及必要实际比较',[7],['ORDER'],[2,3],'原始断点和即时/最终参考不混淆，保留六排列真实负结果。',slides_needed=[42])
add('T2-05','基于助教系统的实际LLM辅助质量提升工作流',[8,9,13],['MODES','WORKFLOW'],[2,11,12],'继承诊断卡/工具/核验思想，按明确用户合同实现范围内可拒绝的真实工作流。','批准调整实现；方法收益按结果限定',history='教师第26页选做，本项目用户把T2转为必做；具体15/9/12等差异见教学差异表。',slides_needed=[26,28,30,33,34,35])
add('T2-06','结构性不同的四模式及真实search-only零模型调用',[9],['MODES'],[2,12],'模式的信息权限、反馈与记忆结构不同，search-only用Provider哨兵拒绝调用。',slides_needed=[37])
add('T2-07','示范记忆、留出只读、泄漏隔离及收益检验',[10],['MEMORY'],[2,6,12],'记忆从60DEMO构建，留出只读；检索消费与因果收益分开。','实验完成；记忆因果收益未获证实',slides_needed=[36,37])
add('T2-08','更实用系统的思考与本项目获批增强',[8,13,14],['WORKFLOW','SELECT'],[3,4,11],'候选/组合/回退、冻结生产、恢复机制和可复算包解决本实验问题；不新增平台。','批准增强已实现；仍待用户审核',slides_needed=[42])

urows=[
(1,'教师基础和附加任务优先',[2,6,12],['DELIVERY'],[2],'先覆盖教师要求，用户T2必做范围保留。'),
(2,'所有增强针对实验一，不脱离轨迹任务',[8,14],['WORKFLOW','SELECT'],[3,11],'不因Task3文件名开展其他课程实验。'),
(3,'研究先于实现，重要规则先确认',[1,3,15],['SOURCE','SELECT'],[3,6],'历史未知与后续批准分开，不倒写全程已有规则。'),
(4,'检索与实验相关的高质量论文，不泛查Multi-Agent',[],['SOURCE'],[3],'已归档研究围绕轨迹质量/简化/指标与选择偏差，没有本轮通用Agent检索。'),
(5,'更新2025/2026来源并与旧研究整合',[],['SOURCE'],[3],'旧22论文/4官方文档索引保留出版年/会议年和访问限制，不重开广泛搜索。'),
(6,'说明各来源与任务关联、可迁移点及风险',[],['SOURCE'],[3],'literature_use_map逐项区分支持命题、实际位置、未采用与风险。'),
(7,'少量有用文献，不强制复现、采用或数量凑数',[],['SOURCE'],[3],'正式报告仅引用真正支持命题的来源，未为凑2–4篇新增算法。'),
(8,'多候选实际尝试，以结果选择',[6,14,15],['PARAM','SELECT'],[3,5],'历史开发/选择真实比较，并非主观直接指定S0。'),
(9,'单项验证先于组合',[14],['SELECT'],[3,4],'G0单项经C核验准入后再组合；S两个过滤父项有移除对照。'),
(10,'有益保留、退化拒绝/回退',[14,15],['SELECT'],[4,5],'选择集组合三条保护失败后回退S0，不把开发获胜固化。'),
(11,'共同评选尺度与方法专项审核并存',[4,5,14],['METRIC','P','SELECT'],[5,10],'共同覆盖/几何/断点保护之外，P另审完整即时输入预算。'),
(12,'参数、方法、审核和结论有来源或实验证据',[1,5,6,15],['SOURCE','METRIC','SELECT'],[3,10],'来源、批准合同和当前真实产物分层绑定。'),
(13,'不换指标、挑样本、隐瞒失败追求漂亮结果',[5,7,15],['METRIC','ORDER','SELECT'],[4,6],'分区/指标预冻结，危险顺序、DP负结果与266工作米边界保留。'),
(14,'不要求复杂方案、论文方法、记忆机制必然获胜',[10,14,15],['MEMORY','SELECT'],[4,12],'无统一方向/DP赢家、记忆未证增益和组合退化都保留。'),
(15,'工作流涵盖研究、执行、审核、优化及交付全过程',[8,13,19],['WORKFLOW','DELIVERY'],[11,19],'父任务维护依赖、修复、重建与发布；局部回执不是结束条件。'),
(16,'Agent实际组织计算与实验，不只提出建议',[8,13],['WORKFLOW'],[11],'原生A/B/C任务与工具/控制器真实记录绑定实际run。'),
(17,'Agent宁少勿滥，不将普通函数改名冒充Agent',[8,13],['WORKFLOW'],[11],'只有三个治理职责，确定性工具和控制器不称LLM Agent。'),
(18,'角色输入输出、工具、状态、权限和交接明确',[8,13,21],['WORKFLOW'],[11,17],'TaskPlan、回执、目标哈希、拒绝及恢复由接口限定。'),
(19,'Verifier真正检查可信参考与目标产物，能拒绝错误',[5,13],['METRIC','WORKFLOW'],[10,11],'独立C读raw/合同/trace，故障注入和真实目标绑定拒绝均留证。'),
(20,'修复是工作流一部分，不能发现问题就返回',[13],['WORKFLOW'],[11,19],'历史哈希/Notebook/图形修复均回归再恢复；本轮普通问题留本任务消化。'),
(21,'对完整父Goal持续负责，不把局部任务结束当完成',[13,19],['WORKFLOW','DELIVERY'],[11,19],'三阶段G3收尾仍属父Goal，不新增Goal4或NEXT_PROMPT。'),
(22,'最小必要人工介入，批准规则后自主执行',[13,15],['WORKFLOW','SELECT'],[5,11],'已批准候选预算/保护内自动裁决；研究定义变化才升级。'),
(23,'不凭主观直接选最优，由有效比较裁决',[14,15,16],['SELECT'],[5,7],'冻结选择规则后读真实选择/确认结果；不宣称全局最优。'),
(24,'迭代有范围、预算和停止理由，不无限搜索',[14,15],['SELECT'],[3,4],'11策略定义、1新结构单项和3组合；第二删除保护因无合理定义未准入。'),
(25,'总体三个大Goal，减少反复转发；保留早期真实返工历史',[13,19],['WORKFLOW'],[1,11],'G1/G2/G3仍同实验，早期revisions与失败回执不覆盖。'),
(26,'retry/fallback/escalation/stop与恢复真实，不只画图',[13,15],['WORKFLOW','SELECT'],[4,11],'真实中断/错误分类修复与选择回退留证；未触发R0最终发布门控不说曾触发。'),
(27,'原始材料、starter、原始数据和历史有效结果保留',[1,22],['DELIVERY'],[1],'新完成版/新ZIP与旧教师文件分开；原件哈希核验。'),
(28,'尊重但核查starter、默认数值、Mock及历史演示',[2,4,8],['S','P','MODES'],[2,10],'TODO/索引/直线投影/Mock/类型统计疑点按来源核查，不盲继承。'),
(29,'不伪造运行、模型输出、截图、用户判断或决策历史',[11,19,20],['AI','EVIDENCE'],[11,16],'真实AI响应、合成反例、系统裁决和用户授权分别标记。'),
(30,'时空语义、单位、不可计算性与样本边界明确',[1,5,16,17],['METRIC','SELECT'],[6,9],'source_crs UNVERIFIED、固定条件化ENU、raw记录非独立用户，null保存原因。'),
(31,'内部审核后发布，网页GPT读取真实远程二重验收',[21],['DELIVERY'],[19,20],'本轮内部验收与新网页GPT待审分开，旧技术接受不补签新PDF/ZIP。'),
(32,'GitHub完整工程与教师最小提交包分开',[22],['DELIVERY'],[18,20],'原始研究/负结果/图源留GitHub；ZIP含真正必要执行闭包。'),
(33,'用户工作区、依赖环境、安全和原有文件受保护',[22],['DELIVERY'],[1,18],'复用.venv、旧未跟踪ZIP保持、安装与配置变化实际登记。'),
(34,'Notebook新内核可运行，LIVE/复算/历史分开',[12,22],['DELIVERY'],[13,18],'仓库与同ZIP各新内核FULL；保存真实提议重放，Provider新增0。'),
(35,'图表回答问题，真实、清晰、可复现和可编辑',[18],['DELIVERY','METRIC'],[14],'真实结果源生成参数/选择/全量/边界图，修布局不改数值关系。'),
(36,'draw.io结构源、publication-plots、固定P2及XeLaTeX',[18],['DELIVERY'],[14,15,16],'任务副本共享P2，结构源可编辑；已装字体不打包。'),
(37,'Experiment/Process两份报告职责独立，不机械复制',[12,19],['DELIVERY','EVIDENCE'],[15,16],'实验报告讲方法结果，过程报告讲工作流和真实决定；互动缺项不取消报告。'),
(38,'文档自然具体清楚，避免内部日志与空泛AI口吻堆砌',[12,19],['DELIVERY'],[15,16],'正文保留必要定义/限制，内部验收表仅作复盘资料；全文精修由B/C核。'),
(39,'Original Evidence First，真实人类贡献可追溯',[20],['EVIDENCE'],[16],'真实授权/响应可索引，未提供的历史聊天不得重构成原生证据。'),
(40,'Evidence Master与Research Conversation/工程职责分离',[20],['EVIDENCE'],[16,17],'本轮A/B/C均无权选择用户anchor、高亮、因果箭头或Lock。'),
(41,'技术与互动两份Handoff',[19,20,21],['DELIVERY','EVIDENCE'],[17],'技术交复算；互动交候选事实与缺项，二者分别保持边界。'),
(42,'11文件分发集与普通任务附件分开，不冒称UI已上传',[22],['UPLOAD_BUNDLE'],[1,20],'本轮以既有sync_sources.py --check核对EXACTLY11和active/bundle字节及manifest；身份/总账/ZIP属于任务成果，不进入固定11文件集合。'),
(43,'Deliverable、Understanding、Submission相互独立',[20,21,22],['DELIVERY','EVIDENCE'],[16,18,20],'工程待审/证据待补、用户LEARNING、NOT_READY和新GPT PENDING分别记录。'),
(44,'当前先工程收尾，再按四板块讲解由用户审核，最后决定提交',[12,19,21,22],['DELIVERY','EVIDENCE'],[17,19,20],'最新用户顺序覆盖旧先讲解再收尾；本轮不代用户理解或自动发送。'),
]
for n,title,tids,gs,gg,why in urows:
    status='有工程/来源证据，待用户审核';remaining='本轮收尾完成后由用户与网页GPT复核；新验收不继承旧版本范围。'
    if n in [39,40]:status='外部待补：正式互动证据未闭合';remaining='Evidence Master提供原件与批准呈现spec，后续实际工程检查和Lock。'
    if n==43:status='状态已分离；理解/最终提交待用户';remaining='Understanding LEARNING；Submission NOT_READY；New GPT_SECOND_REVIEW PENDING。'
    if n==44:status='最新授权顺序已确认；后续用户审核PENDING';remaining='按任务与要求→数据处理与评价→系统/实验/循环→正式成果与收尾讲解，最后由用户决定。'
    add(f'U{n:02}',title,tids,gs,gg,why,status,remaining,history='本轮用户§5.3归并索引是当前要求，不是历史逐字聊天；历史来源按相关G1/G2/G3/TD链接核对，未找到原话不补消息ID。')

for item in entries:
    tids=item['td_ids']; nb,rp=locators(tids)
    item['g1_requirement_ids']=sorted({x for tid in tids for x in bytd[tid].get('g1_requirement_ids',[])})
    item['g2_requirement_ids']=sorted({x for tid in tids for x in bytd[tid].get('g2_requirement_ids',[])})
    item['source_category']='CURRENT_USER_REQUIREMENT_INDEX' if item['id'].startswith('U') else ('TEACHER_OPTIONAL_NOW_USER_REQUIRED_T2' if item['id'].startswith('T2') else 'TEACHER_REQUIRED_T1')
    item['sources']=original_sources(tids)
    for n in item.pop('direct_teacher_pages'):
        item['sources'].append(ref(PPT,f'物理第{n}页','TEACHER_ORIGINAL',' / '.join(slides[n]['text'].splitlines()[:4])))
    item['current_authority']=ref(AUTH,'当前用户SC-LAB1-G3-CLOSEOUT-001；§1冻结范围，§5稳定复盘ID，§14/16状态','CURRENT_USER_EXCERPT_NOT_FULL_TRANSCRIPT',item['requirement'])
    item['current_authority']['quote_scope']='requirement label is the current supplied index; AUTHORIZATION.md may contain a selected excerpt only'
    item['sources'].append(ref(f'{G3}/USER_PROMPT.md','原G3批准范围；只继承未被本轮覆盖的内容','HISTORICAL_AUTHORIZED_PROMPT'))
    if item['source_category']=='CURRENT_USER_REQUIREMENT_INDEX':
        item['sources'].insert(0,dict(item['current_authority']))
    group_data=[GROUPS[g] for g in item['evidence_group_ids']]
    item['actual_approach']=' '.join(g['check'] for g in group_data)
    item['implementation']=list({(x['path'],x['function']):x for g in group_data for x in g['code']}.values())
    item['implementation_applicability']='APPLICABLE_FUNCTIONS_LOCATED' if item['implementation'] else 'DOCUMENT_OR_AUTHORITY_REQUIREMENT; no algorithm function fabricated'
    paths=list(dict.fromkeys(p for g in group_data for p in g['evidence']))
    item['evidence']=[ref(p) for p in paths]
    item['notebook_locators']=nb
    item['report_locators']=rp
    item['locator_applicability']='Mapped from TD and refreshed actual current PDF text/cell source. Empty lists on literature/governance-only items mean no fabricated notebook/report placement.'
    item['comparison_and_checks']=[{'family':gid,'expected_check':GROUPS[gid]['check'],'metric_and_denominator':GROUPS[gid]['metric'],'actual_saved_result':GROUPS[gid]['actual']} for gid in item['evidence_group_ids']]
    reviews=[]
    for gid in item['g2_requirement_ids']:
        for p in reqs[2][gid].get('review_evidence',[]):reviews.append(dict(ref(p,kind='HISTORICAL_INTERNAL_C'),scope=reqs[2][gid].get('conclusion_boundary','G2 scope only'),current_run=False))
    current_reviews=[]
    for gid in item['g3_requirement_ids']:
        parent_entry=reqs[3][gid]
        historical_entry=parent_entry.get('previous_acceptance',parent_entry)
        for p in historical_entry.get('evidence',[]):
            path=p.get('path') if isinstance(p,dict) else p
            if '/independent_' in path:reviews.append(dict(ref(path,kind='HISTORICAL_INTERNAL_C'),scope=historical_entry.get('scope','historical G3 scope only'),current_run=False,historical_as_of=parent_entry.get('historical_as_of','G3 historical receipt')))
        if 'previous_acceptance' in parent_entry:
            for p in parent_entry.get('evidence',[]):
                path=p.get('path') if isinstance(p,dict) else p
                if '/c_review/' in path:
                    receipt=read(path)
                    current_reviews.append(dict(ref(path,kind='CURRENT_CLOSEOUT_INTERNAL_C'),scope=p.get('scope',receipt.get('scope_limit','Only actual receipt scope')),current_run=True,review_status=receipt.get('status','SEE_RECEIPT'),not_new_web_gpt_review=True))
    item['reviews']=list({r['path']:r for r in reviews}.values())
    item['parent_status_at_review_input_snapshot']=[dict(ref(f'{G3}/requirements.json',f'requirements[id={gid}]','IMMUTABLE_GOVERNANCE_REVIEW_INPUT'),id=gid,status=reqs[3][gid]['status'],scope=reqs[3][gid].get('scope',''),final_state_lookup=f'{G3}/requirements.json') for gid in item['g3_requirement_ids']]
    item['current_closeout_reviews']=list({r['path']:r for r in current_reviews}.values())
    item['this_closeout_check']={'role':'A requirements/source diagnosis','scope':'All 65 stable IDs mapped; relevant original source, contract, current source-cell and current PDF text anchors checked. No numerical rerun, C acceptance or visual review claimed.','review_status':'A_DIAGNOSIS_COMPLETE_PENDING_C','current_new_C':'See closeout c_review receipts; not self-granted by this derivative ledger.'}
    item['historical_web_review']='USER_RELAYED_GPT_STAGE_ACCEPTANCE only: G1/G2 and G3 numerical/key-code scope per current user; no fabricated webpage logs, no inheritance of all new PDF/ZIP checks.'
    item['quality_supports']=' '.join(g['actual'] for g in group_data)
    item['does_not_prove']=' '.join(dict.fromkeys(g['limit'] for g in group_data))

binding={'teacher_mapping':ref(MAP),'requirements':[ref(f'task1/evidence/goal{g}/requirements.json') for g in [1,2,3]],'review_input_snapshot_manifest':ref(SNAPSHOT_MANIFEST,kind='IMMUTABLE_GOVERNANCE_REVIEW_INPUT_MANIFEST'),'review_input_snapshots':list(SNAPSHOT_SOURCES.values()),'result_summaries':[ref(f'{G2}/result_summary.json'),ref(f'{G3}/result_summary.json')],'reports':[{k:v for k,v in p.items() if k!='page_texts'} for p in pages.values()],'generation_script':ref(str(Path(__file__).relative_to(ROOT))),'generated_at_utc':NOW}
missing=[{'id':e['id'],'path':x['path']} for e in entries for x in e['evidence'] if not x['exists']]
missfunc=[x for e in entries for x in e['implementation'] if not x['line']]
missanchors=[{'id':e['id'],**x} for e in entries for x in e['report_locators'] if not x['physical_pages_one_based']]
result={'task_id':TASK,'role':'A_REQUIREMENTS_AND_SOURCE_DIAGNOSIS','derived_only':True,'not_parallel_acceptance_matrix':True,'state_authority':ACTIVE_STATE_LINKS,'instruction':'This is the four-block review entrypoint crosswalk. File existence and navigation are never a pass; method outcomes, execution scope, and external acceptance are separate. requirements/goal_state values are immutable review-input observations, not final active state; unique active requirements, goal_state and CL are path-only navigation links to avoid circular acceptance hashes.','current_identity_source':'Current user provided 吴博闻 / string 10245102410; Identity VERIFIED by actual frozen_identity_receipt in the observed parent requirements snapshot.','status_policy':{'new_GPT_SECOND_REVIEW':'PENDING','Understanding':'LEARNING','Submission':'NOT_READY','Evidence_Lock':'NOT_SELF_GRANTED'},'bindings':binding,'entry_count':len(entries),'entries':entries,'locator_checks':{'missing_evidence_paths':missing,'missing_functions':missfunc,'unlocated_current_report_anchors':missanchors},'new_record_model_calls':0,'new_research_experiments':0}
dump('MASTER_REQUIREMENTS_REVIEW.json',result)
lines=['# 实验一完整要求复盘总账','',f'任务 `{TASK}`；A 来源与要求诊断。共 {len(entries)} 个稳定复盘 ID。','',
'本文件从原 G1/G2/G3 requirements、TD 导航和真实结果派生，作为后续四块讲解的入口，不新建另一套“全部通过”状态表。原要求与审核范围保持原身份。U01–U44 是用户本轮归并索引，不是原始聊天逐字稿。历史网页 GPT 结论仅按用户转交范围登记；本轮 A 的源定位不能替代 C、PDF目视、Notebook执行或用户验收。','',
'唯一父要求入口：'+link(f'{G3}/requirements.json')+'；其中 `previous_acceptance` 原样保存 1a5e26b 历史范围，当前状态另记。本轮 CL 矩阵由主线程在 `../ACCEPTANCE_MATRIX.json` 登记；不因目录/文件存在宣称验收通过。','',
'本表中的父状态与工作流治理输入固定为送审输入快照：观察时点 `'+SNAPSHOT_META['created_at']+'`，'+link(SNAPSHOT_MANIFEST,'真实复制与哈希清单')+'。两份快照严格核验字节，缺失或不符时生成失败；快照不是第二 active source。最终发布状态查 '+link(f'{G3}/requirements.json','active requirements')+'、'+link(f'{G3}/goal_state.json','active goal_state')+' 与 CL 入口，合法后续状态推进不倒写本次观察。','',
'当前身份由用户直接给出，姓名/学号不再列外部缺项。正式互动原件/spec/Lock、新网页 GPT 审核和用户深入理解仍按各自状态登记。总账会在最终 PDF 构建后刷新实际页码和字节绑定；物理页含封面，Notebook编号从0开始。','',
'配套：'+link(str((OUT/'TEACHING_DIFFERENCES.md').relative_to(ROOT)),'七项教学差异')+' · '+link(str((OUT/'literature_use_map.md').relative_to(ROOT)),'文献使用对账')+' · '+link(str((OUT/'DIAGNOSIS.md').relative_to(ROOT)),'本轮具体工作项')+'。','',
'当前绑定：'+', '.join(f"{link(p['path'])}（{p['page_count']}页，SHA256 `{p['sha256']}`）" for p in pages.values())+'。','',
'| ID | 当前要求 | 状态 | 交叉入口 |','|---|---|---|---|']
for e in entries:lines.append(f"| [{e['id']}](#{e['id'].lower().replace('-','')}) | {e['requirement']} | {e['status']} | {'、'.join(e['td_ids']) or '来源研究'}；{'、'.join(e['g3_requirement_ids'])} |")
for e in entries:
    lines.extend(['',f"<a id=\"{e['id'].lower().replace('-','')}\"></a>",'',f"## {e['id']} {e['requirement']}",'',f"**性质/状态：** {e['source_category']}；{e['status']}。",'',f"**来源与授权：** {e['authorization_history'] or '教师要求与后续用户授权分别登记；本轮冻结方法，只收尾修复。'} 当前授权：{link(AUTH)}。"])
    src=[]
    for s in e['sources']:
        if len(src)>=6:break
        key=(s['path'],s['locator'])
        if key not in src:src.append(key)
    lines.append('原件定位：'+'；'.join(f'{link(p)} {loc}' for p,loc in src)+'。详细原句/版本SHA见同名JSON。')
    lines.extend(['',f"**做法与理由：** {e['why']} {e['actual_approach']}",'', '**可打开实现和成果：** '+('；'.join(f"{link(x['path'])}::{x['function']}（L{x['line']}）" for x in e['implementation']) or '本条为文献/治理要求，不编造算法函数。')])
    lines.append('真实证据：'+'；'.join(link(x['path']) for x in e['evidence'])+'。')
    if e['notebook_locators']:
        grouped={}
        for n in e['notebook_locators']:grouped.setdefault(n['path'],[]).append(f"`{n['stable_cell_id']}`")
        lines.append('Notebook：'+'；'.join(f'{link(p)} '+', '.join(ids) for p,ids in grouped.items())+'。')
    if e['report_locators']:
        lines.append('实际PDF：'+'；'.join(f"{link(r['path'])} 物理页{','.join(map(str,r['physical_pages_one_based'])) or '未定位'}（{r['text_anchor']}）" for r in e['report_locators'])+'。页码是文字anchor定位，不冒称视觉验收。')
    lines.extend(['','**对照、分母与实际结果：**'])
    for c in e['comparison_and_checks']:lines.append(f"- {c['family']}：{c['metric_and_denominator']} 预期：{c['expected_check']} 实际：{c['actual_saved_result']}")
    lines.extend(['','**审核范围：** 历史内部C回执：'+('；'.join(link(r['path']) for r in e['reviews'][:5]) or '本条不单凭数值C回执成立，使用来源/权限/文档证据。')+' 逐回执范围及全检/抽查见JSON；历史C不自动验收新版本。新A仅做来源与导航对账，新C和网页GPT仍需分别查看当前有效产物。','',f"**支持/边界：** {e['quality_supports']} {e['does_not_prove']}",'',f"**剩余动作：** {e['remaining']}"])
    if e['current_closeout_reviews']:
        lines.extend(['','本轮实际C限定范围：'+'；'.join(f"{link(r['path'])}（{r['scope']}）" for r in e['current_closeout_reviews'])+'。不代表本轮所有工程、网页GPT或用户审核通过。'])
    lines.extend(['','父要求送审输入快照时状态：'+'；'.join(f"{r['id']} `{r['status']}`" for r in e['parent_status_at_review_input_snapshot'])+'。观察时点 `'+SNAPSHOT_META['created_at']+'`；最终发布状态以唯一active父入口及真实CL回执为准。'])
(OUT/'MASTER_REQUIREMENTS_REVIEW.md').write_text('\n'.join(lines)+'\n')

# Literature use map keeps historical reading untouched; current citation check is additive.
lit=read(LIT);paper_rows=[]
historical_influence={'S08':'原始DP出处与定义边界；实际算法来自教师指定和获批数学合同，不称原论文复现。','S10':'选择与最终确认分开的一般风险提醒；G3 A明确读过历史审计条目。','S17':'后验检查与误差参照边界的思想借鉴；没有实现PILOT-C编码、重采样或纠正算法。','S21':'单一主要改动与依赖重建的思想借鉴；没有实现PipeLens代理/搜索系统。','D03':'有限线段/现代实现资料的定义边界；不以GEOS API调用替代当前独立实现。'}
for s in lit['sources']:
    sid=s['id'];reading=s.get('reading','');access=s.get('access','')
    if sid in ['S07','S08','S12']:level='仅题录/摘要或作者说明，未全文核读'
    elif sid in ['S13','S14','S15','S16']:level='仅题录/可见摘要/作者资料，正式全文未核读'
    elif sid.startswith('D'):level='官方文档核读（继承2026-09-24 Source Audit范围）'
    else:level='全文指定章节核读（继承Source Audit，非全篇逐式验收）'
    statuses=['已检索',level]
    if sid in historical_influence:statuses.append('思想借鉴/定义边界有候选前记录');use=historical_influence[sid];cause='G3 A_CANDIDATE_RATIONALE及a_candidate_plan明确列入已读条目；这只证明审计稿阅读/思想边界，不证明原全文阅读或算法采用。'
    else:statuses.extend(['未采用','仅事后对应（如与当前实现相似）']);use='已有合并研究卡的迁移建议保持候选身份；当前未找到把该具体论文算法准入并运行的记录。';cause='不能从当前代码/报告与论文相似倒推历史灵感；不编因果。'
    if sid in ['S03','S05','S07','S12','S13','S14','S15','S16','S19','S20','S22','D02','D04']:statuses.append('仅风险提醒/范围边界')
    if sid=='S08':statuses.append('教师指定DP已实现并试验；原论文算法未独立复现')
    item={'id':sid,'title':s['title'],'authors':s.get('authors',[]),'year':s.get('year'),'venue_or_institution':s.get('publication'),'conference_year':s.get('conference_year'),'publication_status':'官方文档' if sid.startswith('D') else '按归档Source Audit所核正式题录；作者稿与正式版阅读差别见reading/access','urls':s.get('urls',[]),'historical_reading_level':level,'historical_actual_reading':reading,'historical_access':access,'original_location':s.get('location'),'supported_proposition':s.get('support',s.get('evidence')),'task_relevance':s.get('relevance',s.get('role')),'actual_use':use,'historical_causation_boundary':cause,'status':statuses,'implementation_or_trial':'No author algorithm reproduction identified; DP required by teacher is separately implemented/tested.' if sid=='S08' else 'No author algorithm implementation/reproduction claimed.','risk_or_nonproof':s.get('limitation',s.get('boundary')),'source_audit':ref(LIT,f"sources[id={sid}]",'HISTORICAL_SOURCE_AUDIT'),'historical_evidence':[ref(f'{G3}/A_CANDIDATE_RATIONALE.md','文献边界','PRE_CANDIDATE_READING_RECORD')] if sid in historical_influence else [],'current_formal_report_citation': 'cawley2010' if sid=='S10' else None}
    if sid=='D02':
        item['current_scope_clarification']='历史Source Audit的投影待定描述仅属于2026-09-24研究阶段；当前固定条件化ENU已冻结，未采用Web Mercator，不再存在本轮投影选择待办。'
        item['risk_or_nonproof']='历史审计提示Web Mercator尺度失真、显示用途和分析距离不可混同。当前条件化ENU已冻结，未采用Web Mercator；本条仅保留排除/风险参照。'
    if sid=='S10':
        item['historical_reading_distinction']='2026-09-24合并Source Audit记载摘要、引言和选择/评估分离论证阅读；G3候选A只明确核读审计稿；收尾前正式报告的直接引文核验仅登记官方摘要/元数据。这是三个不同主体/用途的访问范围，不能互相覆盖。'
        item['current_closeout_reading']={'level':'全文指定段核读（本轮新增访问，不倒改历史）','location':'§1；§4.4、§5–5.1，印刷2094–2095/物理16–17；§5.3印刷2102/物理24；§6印刷2103/物理25','receipt':ref(str((OUT/'citation_access_receipt.json').relative_to(ROOT))), 'effect':'只加强当前引用的文本依据，不改变选择合同、样本或结论。'}
    paper_rows.append(item)
for sid,title,url,claim in [('REF-PROJ-CART','Geodetic to cartesian conversion','https://proj.org/en/stable/operations/conversions/cart.html','geodetic→ECEF数学语义，显式椭球'),('REF-PROJ-TOPO','Geocentric to topocentric conversion','https://proj.org/en/stable/operations/conversions/topocentric.html','ECEF→固定原点ENU数学语义，原点与参数单位')]:
    paper_rows.append({'id':sid,'title':title,'authors':['PROJ contributors'],'year':None,'venue_or_institution':'PROJ official documentation','publication_status':'滚动官方文档，本轮网页标PROJ9.9.0；不代表本机版本','urls':[url],'status':['官方文档核读','实现并试验：转换语义交叉核对'],'historical_reading_level':'已有报告2026-09-27访问说明','current_closeout_reading':{'level':'本轮官方操作说明定点核读','receipt':ref(str((OUT/'citation_access_receipt.json').relative_to(ROOT)))},'supported_proposition':claim,'actual_use':'Experiment §1.1转换公式与独立PROJ数值核算；task1/workflow/coordinates.py、coordinate_review.py；G3 coordinates.py。','historical_causation_boundary':'当前再次核读是引用复核，不声称本轮才发明历史工作坐标合同。','risk_or_nonproof':'公式一致不证明原始datum/CRS，不设置EPSG补充来源事实。','implementation_or_trial':'数学工作坐标及独立核验已运行；不是论文算法复现。','current_formal_report_citation':'proj-cart' if sid.endswith('CART') else 'proj-topocentric'})
litmap={'task_id':TASK,'role':'A_SOURCE_DIAGNOSIS','generated_at_utc':NOW,'historical_audit_unchanged':True,'source_binding':ref(LIT),'count_archived_sources':26,'count_current_extra_report_documents':2,'no_algorithm_minimum':True,'no_new_literature_algorithm_experiments':True,'no_broad_new_search':True,'entries':paper_rows,'interpretation':'研究过、思想借鉴、实现和实际试验分别登记；未找到因果记录即不作历史灵感主张。正式报告仅保留直接支持具体命题的引用。'}
dump('literature_use_map.json',litmap)
l=['# 文献研究、启发与实际使用对账','',
'这是内部复盘资料，不是新增论文复现计划。归档研究保留22篇论文和4项官方文档；另登记当前报告直接引用的2项PROJ转换文档。原Source Audit的2026-09-24阅读记录不改写。本轮只定点核查当前引用，访问范围见'+link(str((OUT/'citation_access_receipt.json').relative_to(ROOT)))+'。','',
'G3候选前的A记录明确读取S08/S10/S17/S21/D03审计条目，能够支持相应思想边界；不能升级为原全文已核读、具体算法已采用，或每个设计都因论文而生。其他来源若与实现相似，只能标事后对应；未采用不等于研究任务失败。没有2–4个算法必须采用的最低数。','',
'| 来源 | 实际阅读层级 | 真实使用与状态 | 历史审计风险与本轮边界 |','|---|---|---|---|']
for s in paper_rows:
    title=s['title'];year=s.get('year');venue=s.get('venue_or_institution','');names='; '.join(s.get('authors',[]));url=s.get('urls',[''])[0]
    bib=f"{s['id']} · [{title}]({url})<br>{names}<br>{year if year else '官方文档'} · {venue}"
    hist=s.get('historical_actual_reading',s.get('historical_reading_level',''))
    if s.get('historical_reading_distinction'):hist+='；'+s['historical_reading_distinction']
    if s.get('current_closeout_reading'):hist+='；本轮：'+s['current_closeout_reading']['level']
    l.append('| '+bib+' | '+hist.replace('|','/')+' | '+s['actual_use'].replace('|','/')+'<br>'+'；'.join(s['status'])+' | '+str(s.get('risk_or_nonproof','')).replace('|','/')+' |')
l.extend(['','2025/2026出版年份与会议周期以原审计题录分别记录：T-Assess/MTCSC/MLSimp刊出2024，不能改成2025新论文；PILOT-C/PED/STR刊出2025，与2026会议周期不同。2026条目保留其所核正式卷期和访问限制，不凭年份宣称顶会全文已读。详细原文段落、支持命题、因果边界、具体来源SHA及报告引用键见JSON。','',
'本轮 Cawley–Talbot 核查只支持一般选择偏差风险，不规定600条最终确认规模，不证明本项目单次分层确认统计无偏，也不要求新增嵌套交叉验证。PROJ文档只支撑转换定义，不认证原始CRS。全文PDF未存入待审包，未新增模型训练或算法实验。'])
(OUT/'literature_use_map.md').write_text('\n'.join(l)+'\n')
print(json.dumps({'entries':len(entries),'lit_entries':len(paper_rows),'pdf_pages':{k:v['page_count'] for k,v in pages.items()},'missing_paths':missing,'missing_functions':missfunc,'unlocated_anchors_count':len(missanchors)},ensure_ascii=False))
