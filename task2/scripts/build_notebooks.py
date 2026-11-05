"""Readable completed notebooks; preserve teacher originals and original Part B assertions."""
from pathlib import Path
import json
import zipfile
import nbformat as nb

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"task2/notebooks"


def md(text):return nb.v4.new_markdown_cell(text)
def code(text):return nb.v4.new_code_cell(text.strip())


BOOT='''
from pathlib import Path
import sys, os, json
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'task2/src/online.py').exists())
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
if str(ROOT/'task2/src') not in sys.path:sys.path.insert(0,str(ROOT/'task2/src'))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from task2.scripts.build_figures import P, COLORS
from matplotlib.colors import LinearSegmentedColormap
VALUE_CMAP=LinearSegmentedColormap.from_list('p2value',[P['Paper'],P['P1'],P['C1'],P['Ink']])
get_ipython().run_line_magic('matplotlib','inline')
np.set_printoptions(precision=4,suppress=True)
'''


def write(name,cells):
    n=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Smart Cities project .venv',
        'language':'python','name':'smartcities_dispatch'},'language_info':{'name':'python'},
        'source_identity':'completed working notebook; original teacher inputs preserved under teacher_materials'})
    OUT.mkdir(parents=True,exist_ok=True);nb.write(n,OUT/name)


def main():
    basic=[
md('''# 作业2：运力调度（完成版）

保留教师 Notebook 的动态环境、TBG、BB、NSGA-II 四部分。原件不变；生产实现集中在 `task2/src/online.py`，这里逐段导入、运行与核验，避免 Notebook 与脚本维护两套算法。TODO1—5、finalize 和 Assignment 生成均有实际实现与反例。

课件场景是 10×10 km、20 min、20 对象、1 km/min；原 Notebook 的100对象、1000空间单位/2000时间单位另立示例。签到是代理需求，不是真实网约车单。'''),code(BOOT),
md('''## 1. 双边在线事件与两种离线目标

每个司机/订单只匹配一次；同刻先请求后司机（各按ID），同刻到达全部处理完再开批次。延迟=等待+距离/速度。离线分别求最小总延迟与最小最大延迟；它们是两个不同问题。'''),
code('''from task2.src.online import (Worker,Request,Assignment,SimulationEnvironment,TBGAlgorithm,BBAlgorithm,
    run_simulation,offline_reference,summarize,instance_ratios,bottleneck_assignment)
from scipy.optimize import linear_sum_assignment
C=np.array([[0.,6.],[6.,10.]])
i,j=linear_sum_assignment(C);bi,bj=bottleneck_assignment(C)
assert C[i,j].sum()==10 and C[i,j].max()==10
assert C[bi,bj].max()==6
print('sum-optimum max=10; bottleneck-optimum max=6（精确反例）')
sim=SimulationEnvironment(123)
sim.generate_synthetic_data(20,20,(0,20),(0,10))
opt_sum=offline_reference(sim.workers,sim.requests,objective='sum')
opt_max=offline_reference(sim.workers,sim.requests,objective='max')'''),
md('''## 2. TBG：完成原 Cell4 的TODO1—5与finalize

请求到达时取 travel≤gamma 的最近司机；司机到达优先最早超阈值请求，否则取总延迟<gamma的最小者。gamma的单位是时间，距离要除以速度。finalize只使用真实剩余司机，不能制造供给。小gamma不会保证更低最大延迟。'''),
code('''rows=[]
for gamma in [.5,1,2,5,10,15]:
    method=TBGAlgorithm(gamma,speed=1)
    a=run_simulation(sim.workers,sim.requests,method,20)
    rows.append(dict(gamma=gamma,**summarize(a,20,20),**instance_ratios(a,opt_sum,opt_max)))
display(pd.DataFrame(rows).round(4))
assert len(run_simulation([],sim.requests,TBGAlgorithm(5),20))==0'''),
md('''## 3. BB：原 Cell8 的Assignment已给出，真正风险是丢弃队列

sum-KM是Notebook定义；课件的瓶颈版本另标BBmax。两者均保留未匹配对象再尝试。丢弃策略只作有明确身份的对照。下表同时给出覆盖率，部分匹配不计算与全服务离线最优的实例比值。'''),
code('''rows=[]
for theta in [.5,1,2,5]:
    for recycle,objective in [(True,'sum'),(True,'max'),(False,'sum')]:
        a=run_simulation(sim.workers,sim.requests,BBAlgorithm(theta,recycle=recycle,objective=objective),20)
        rows.append(dict(theta=theta,recycle=recycle,objective=objective,
            **summarize(a,20,20),**instance_ratios(a,opt_sum,opt_max)))
display(pd.DataFrame(rows).round(4))'''),
md('''### Notebook原尺度的theta=50/100/200

这里速度=1空间单位/时间单位，绝不把数值1000直接称作km。该场景独立于上一课件场景。'''),
code('''nb_sim=SimulationEnvironment(123)
nb_sim.generate_synthetic_data(100,100,(0,2000),(0,1000))
rows=[]
for theta in [50,100,200]:
    a=run_simulation(nb_sim.workers,nb_sim.requests,BBAlgorithm(theta),2000)
    rows.append(dict(theta=theta,**summarize(a,100,100)))
display(pd.DataFrame(rows).round(4))'''),
md('''## 4. 基础NSGA-II：接驾距离与送客距离

独立合成20司机/20个OD，10×10km，收入目标=欧氏送客km。没有套用进阶的5+2d车费。五seed、种群100、300代。静态多目标前沿需先给标量偏好，才有同目标的精确比较；这里是实例近似比，不是在线理论竞争保证。'''),
code('''from task2.src.evolution import DispatchProblem,run_nsga,weighted_km
rng=np.random.default_rng(2024)
drv,origin,dest=(rng.uniform(0,10,(20,2)) for _ in range(3))
pickup=np.linalg.norm(drv[:,None]-origin[None],axis=-1)
trip=np.linalg.norm(dest-origin,axis=1)
problem=DispatchProblem(dict(drv=drv,o_xy=origin,d_xy=dest,pickup=pickup,fare=trip),K=20,radius=np.sqrt(200))
basic_runs=[run_nsga(problem,pop_size=100,n_gen=300,seed=s) for s in range(5)]
fig,ax=plt.subplots(figsize=(7,4))
for s,r in enumerate(basic_runs):ax.scatter(r['F'][:,1],-r['F'][:,0],s=10,label=f'seed{s}',alpha=.6)
ax.set(xlabel='Pickup (km)',ylabel='Delivered OD distance (km)');ax.legend();plt.show()
rows=[]
for reference in weighted_km(problem,[0,.25,.5,1,2]):
    lam=reference['lam'];opt=-reference['F'][0]-lam*reference['F'][1]
    for s,r in enumerate(basic_runs):
        val=np.max(-r['F'][:,0]-lam*r['F'][:,1])
        rows.append(dict(seed=s,lam=lam,optimal_utility=opt,obtained_utility=val,
                         instance_ratio=opt/val if val>0 else np.nan))
display(pd.DataFrame(rows).round(5))'''),
md('''## 5. 真实签到代理的空间需求扩展

使用前段训练日期的签到热点和相邻签到OD起点。将来源相同小时的起点有放回采样成60min模拟流，司机到达为模拟随机数；没有把不同日期的签到拼成真实出租车运营日。当地时间口径中的12对UTC矛盾有单独稳健性记录。'''),
code('''from task2.src.dispatch_data import load_data
bundle=load_data()
display(pd.DataFrame(bundle.audit['split']).T)
rng=np.random.default_rng(10)
pool=bundle.trips_train_inner[bundle.trips_train_inner.minute//60==18]
od=pool.iloc[rng.choice(len(pool),20)]
hot=bundle.checkins_train_inner.iloc[rng.choice(len(bundle.checkins_train_inner),20)]
w=[Worker(i,(float(row.x),float(row.y)),float(rng.uniform(0,60))) for i,(_,row) in enumerate(hot.iterrows())]
r=[Request(i,(float(row.ox),float(row.oy)),float(row.minute-1080)) for i,(_,row) in enumerate(od.iterrows())]
display(pd.DataFrame([dict(method=name,**summarize(run_simulation(w,r,algo,60),20,20)) for name,algo in
    [('TBG5',TBGAlgorithm(5)),('BBsum2',BBAlgorithm(2)),('BBmax2',BBAlgorithm(2,objective='max'))]]).round(4))'''),
md('''完整55个开发实例、独立合成确认、单因素阈值、4时段代理实验及逐匹配记录分别由`run_online.py`与`run_online_studies.py`生成；本Notebook所有表和图来自当前Kernel实际执行。正式大批次结果与报告通过`docs/REPRODUCIBILITY_GUIDE.md`定位。''')]
    write('作业2_运力调度_完成版.ipynb',basic)

    tests=[]
    starter=ROOT/'task2/teacher_materials/advanced/实验3 多目标与强化学习派单（学生版）.ipynb'
    if starter.is_file():
        teacher=json.loads(starter.read_text())
    else:
        # Existing teacher ZIP is an optional local fallback, never a public dependency.
        with zipfile.ZipFile(ROOT/'归档.zip') as z:
            name=next(n for n in z.namelist() if n.endswith('.ipynb'))
            teacher=json.loads(z.read(name))
    for i in (31,33):
        src=''.join(teacher['cells'][i]['source']);tests.append(src[src.index('# 单元测试'):])
    advanced=[
md('''# 实验3：多目标与强化学习派单（完成版）

课件首页写“实验二—任务分配(2)”，作业细则和Notebook写实验3，保留来源差异。Part A对应原Cells5—25；Part B TODO对应Cells31/33。原始输入未覆盖。生产实现集中在`evolution.py`、`rl_dispatch.py`及数据入口；这里从干净Kernel实际运行核心参考实验，并重算正式汇总。

签到→相邻签到代理→采样模拟日→训练回合→测试模拟日五种身份分别说明。默认种群100/300代/5seed，RL默认300回合，不以缩小参数冒充教师实验。完整控制变量、加分与复验结果另由脚本和固定run索引追溯。'''),code(BOOT),
md('''## A.1 数据、共同可行图与评价

前70%日期用于训练，最后30%为测试；训练内后20%为验证。司机热点只从相应训练部分取得。局部坐标为教学近似km，source_crs未获独立证明。候选为3km曼哈顿半径内最近6司机。HV使用实例预先确定的统一界和reference1.1；Spacing先容差去重、非支配筛选。'''),
code('''from task2.src.dispatch_data import load_data
from task2.src.evolution import (DispatchProblem,DTLZ2,make_batch,run_nsga,weighted_km,km_initial_genes,
    knee_point,constraint_choice,das_dennis)
from front_metrics import canonical_front as unique_front, evaluate_front
def hypervolume(F,ideal,nadir):return evaluate_front(F,ideal,nadir)['HV']
def spacing(F,ideal,nadir):return evaluate_front(F,ideal,nadir)['Spacing_cv']
bundle=load_data();display(pd.DataFrame(bundle.audit['split']).T)
batch=make_batch(bundle.trips_train_inner,bundle.checkins_train_inner,hour=18,seed=2024)
problem=DispatchProblem(batch);ideal,nadir=problem.normalization()
lambdas=np.r_[0.,np.geomspace(.05,60.,40)]
km=weighted_km(problem,lambdas);kmF=unique_front(np.asarray([r['F'] for r in km]))
print('KM HV',hypervolume(kmF,ideal,nadir),'Spacing',spacing(kmF,ideal,nadir))'''),
md('''## A.2 NSGA-II/III与五seed收敛

遗传解码冲突修复保持同一候选图。保存五个seed的全部前沿；区间为seed标准差，不能只报告最好一次。'''),
code('''runs={algo:[run_nsga(problem,algo=algo,pop_size=100,n_gen=300,seed=s) for s in range(5)]
      for algo in ['nsga2','nsga3']}
fig,axs=plt.subplots(1,2,figsize=(11,4))
for c,(algo,rs) in zip(COLORS,runs.items()):
    for r in rs:axs[0].scatter(r['F'][:,1],-r['F'][:,0],s=8,color=c,alpha=.25)
    histories=np.array([[hypervolume(h['F'],ideal,nadir) for h in r['history']] for r in rs])
    x=[h['generation'] for h in rs[0]['history']]
    axs[1].plot(x,histories.mean(0),color=c,label=algo)
    axs[1].fill_between(x,histories.mean(0)-histories.std(0,ddof=1),histories.mean(0)+histories.std(0,ddof=1),color=c,alpha=.15)
axs[0].scatter(kmF[:,1],-kmF[:,0],marker='x',color=P['Ink'],s=20,label='weighted KM')
axs[0].set(xlabel='Pickup (km)',ylabel='Teaching fare');axs[0].legend()
axs[1].set(xlabel='Generation',ylabel='Common normalized HV');axs[1].legend();plt.show()
display(pd.DataFrame([dict(algorithm=a,seed=s,HV=hypervolume(r['F'],ideal,nadir),Spacing=spacing(r['F'],ideal,nadir),n_eval=r['n_eval'],seconds=r['runtime']) for a,rs in runs.items() for s,r in enumerate(rs)]))'''),
md('''## A.3 三目标与DTLZ2

第三目标是服务数；三目标105种群/105方向（原Cell19），不同于双目标100种群。DTLZ2是已知球面前沿的独立数学对照，不能用派单front形状替代。'''),
code('''p3=DispatchProblem(batch,n_obj=3);i3,n3=p3.normalization()
rows=[]
for a in ['nsga2','nsga3']:
    for s in range(5):
        r=run_nsga(p3,algo=a,pop_size=105,n_gen=300,seed=s,ref_dirs=das_dennis(3,13))
        rows.append(dict(problem='dispatch3',algorithm=a,seed=s,HV=hypervolume(r['F'],i3,n3),Spacing=spacing(r['F'],i3,n3)))
        r=run_nsga(DTLZ2(),algo=a,pop_size=92,n_gen=400,seed=s,ref_dirs=das_dennis(3,12))
        rows.append(dict(problem='DTLZ2',algorithm=a,seed=s,HV=hypervolume(r['F'],np.zeros(3),np.ones(3)),Spacing=spacing(r['F'],np.zeros(3),np.ones(3)),front_error=np.abs(np.linalg.norm(r['F'],axis=1)-1).mean()))
display(pd.DataFrame(rows))'''),
md('''## A.4 时段、单项增强与折中选择

完整5seed的8/13/18/23时段、种群/代数单项、KM初始化和经验证组合在实际run中保存。下面重算该表的当前规范指标并查看，不将读取旧run冒充新进化实验。膝点与接驾预算60km是不同偏好，不能无依据称某个业务最优。'''),
code('''summary_path=ROOT/'task2/results/evolution/summary.csv'
if not summary_path.exists():raise FileNotFoundError('Run staged evolution scripts described in the reproducibility guide first')
display(pd.read_csv(summary_path).groupby(['stage','algorithm','n_obj','pop_size','n_gen'],dropna=False)[['HV','Spacing_cv','total_objective_evals','total_runtime']].agg(['mean','std']))
front=unique_front(runs['nsga2'][0]['F'])
k=knee_point(front);c=constraint_choice(front,60.)
display(pd.DataFrame([dict(rule='knee',F=front[k]),dict(rule='pickup<=60km',F=front[c] if c is not None else None)]))
initial=km_initial_genes(problem,lambdas)
assert all(problem.decode(g)==problem.decode(problem.encode_pairs(problem.decode(g))) for g in initial)
print('KM初始基因真实编码验证',len(initial))'''),
md('''## B.1 Q-learning TODO1—3与教师原测试

Q更新只在后继真正可行动作与WAIT上取max；动作持续delta片就折扣delta次；终止状态不bootstrap。以下原始断言逐字保留，只把函数来源换成已完成模块。'''),
code('''from task2.src.rl_dispatch import (DEFAULT,Config,QTable,DoubleQTable,q_update,double_q_update,
    region_long_term_value,make_q_km,run_episode,sample_episode,train_q_km,
    greedy_nearest,km_fare,make_repositioner,T,N_ZONES,WAIT,GAMMA,DELTA)
'''+tests[0]),code(tests[1]),
md('''## B.2 真实300回合训练、学习曲线与TD

每回合采样1500代理订单构成一个模拟日。这里从inner训练，validation只用于观察；它不是300个真实运营日。初始司机来自inner签到。'''),
code('''qt,curve,td,episode_log,seconds=train_q_km(bundle.trips_train_inner,bundle.checkins_train_inner,60,
    n_episodes=300,seed=2024,validation_pool=bundle.trips_validation)
assert len(td)==300
fig,axs=plt.subplots(1,2,figsize=(11,3.5))
axs[0].plot(curve[:,0],curve[:,1],color=COLORS[0]);axs[0].set(xlabel='Actual training episode',ylabel='Validation accepted fare')
axs[1].plot(np.arange(300),td,color=COLORS[3],alpha=.7);axs[1].set(xlabel='Actual training episode',ylabel='Mean absolute TD error');plt.show()
print('300 real simulated episodes, seconds=',seconds)'''),
md('''## B.3 区域价值与beta验证

LT区域中心近似只用于价值估计，真实派单的忙时来自实际接驾+送客距离。beta曲线在验证分区计算；最终测试不参与选择。收入按教师定义在接单时确认，另记录horizon内完成与未完成服务。'''),
code('''fig,axs=plt.subplots(1,4,figsize=(12,3),layout='constrained')
for ax,h in zip(axs,[8,13,18,23]):
    t=(h*60-360)//10
    im=ax.imshow(qt.V[t].reshape(8,8),origin='lower',vmin=0,vmax=qt.V.max(),cmap=VALUE_CMAP);ax.set_title(f'{h}:00');ax.set(xlabel='Grid column',ylabel='Grid row')
fig.colorbar(im,ax=axs,label='Estimated regional value');plt.show()
LT=region_long_term_value(qt.V);rows=[]
for seed in range(50000,50005):
    ep=sample_episode(bundle.trips_validation,60,seed,bundle.checkins_train_inner)
    for beta in [0,.2,.4,.5,.6,.8,1]:
        m,_=run_episode(ep,make_q_km(LT,beta));rows.append(dict(day_seed=seed,beta=beta,**m))
display(pd.DataFrame(rows).groupby('beta')[['revenue','answer_rate','avg_pickup','nonpositive_fraction']].mean())'''),
md('''## B.4 40/60/100车、参数、Double、主动调度与NSGA融合

正式实验包含每车队300回合、gamma/grid/patience单因素、Double在beta1的五训练seed、计入空驶的相邻调度、NSGA前沿与实际模拟效果。表中每行来自可追溯day_metrics，不是教师PPT参考数值。需要重训全套时执行复现指南的分阶段脚本；不将加载表格声称为此Kernel再次训练。

Q/Double共用行为流但有独立更新coin；Double缓解统计高估不保证消除共享订单竞争。调度收入与空驶成本分开报告，不能忽略空驶而宣称净收益。融合的估计长期目标与真实模拟收入分别展示。'''),
code('''rl_root=ROOT/'task2/results/rl'
active_index=json.loads((rl_root/'ACTIVE_RUNS.json').read_text())
paths=[ROOT/'task2'/p for p in active_index['active_day_metrics']]
tables=[]
for p in paths:
    # The explicit active index excludes invalid and historical equivalent evaluations.
    raw=json.loads(p.read_text())
    if isinstance(raw,list) and raw:
        t0=pd.DataFrame(raw);t0['run']=str(p.parent.relative_to(rl_root));tables.append(t0)
if not tables:raise FileNotFoundError('Run RL experiments first; see reproducibility guide')
all_days=pd.concat(tables,ignore_index=True)
display(all_days.groupby(['run','policy'])[['revenue','answer_rate','avg_pickup','empty_km']].mean())
print('每行统计单位：一个明确run中的模拟日；不同训练seed/分区不合并为独立真实运营日。')'''),
md('''思考题的实测解释、负结果和边界见Experiment Report及要求矩阵。完整基线/单项/父项/融合/移除/独立测试在run索引中单列。这里的原TODO断言与真实300回合已从干净Kernel执行；报告和图重建入口与实验重算入口分别提供。''')]
    write('实验3_多目标与强化学习派单_完成版.ipynb',advanced)
    print('Created two completed notebooks with original TODO assertions.')


if __name__=='__main__':main()
