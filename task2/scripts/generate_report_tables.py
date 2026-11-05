"""Teacher-facing tables derived from canonical metrics; no manually filled result cells."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'task2/reports/generated'
SOURCES=[]


def read_csv(rel):
    p=ROOT/rel;SOURCES.append(p);return pd.read_csv(p)


def esc(v):
    s=str(v)
    for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:s=s.replace(a,b)
    return s


def number(v,digits=3):
    return '--' if pd.isna(v) else f'{v:,.{digits}f}'


def table(name,caption,label,headers,rows,note='',columns=None):
    if columns is None:columns='Y'+'r'*(len(headers)-1)
    text=[r'\begin{table}[htbp]\centering\small',f'\\caption{{{caption}}}\\label{{{label}}}',
          f'\\begin{{tabularx}}{{\\linewidth}}{{{columns}}}\\toprule',
          ' & '.join(headers)+r'\\\midrule']
    text+=[' & '.join(str(x) for x in row)+r'\\' for row in rows]
    text += [r'\bottomrule\end{tabularx}']
    if note:text.append(r'\tabnote{'+note+'}')
    text.append(r'\end{table}')
    (OUT/(name+'.tex')).write_text('\n'.join(text)+'\n')


def online_tables():
    methods={'TBG_g2':'TBG(2)','TBG_g5':'TBG(5)','BB_recycle_t1':'BBsum(1)',
             'BBmax_recycle_t1':'BBmax(1)','BB_discard_t0.5':'discard(0.5)',
             'offline_sum':'离线sum','offline_max':'离线max'}
    for phase,caption in [('development','五个开发实例：覆盖和延迟必须一起解释。'),('confirmation','五个独立合成确认实例：不按结果重新选择阈值。')]:
        d=read_csv(f'task2/results/online/{phase}_v1/metrics.csv');d=d[d.scenario=='teacher']
        rows=[]
        for k,label in methods.items():
            q=d[d.method==k];rows.append([label,number(q.match_rate.mean(),2),number(q.avg_delay.mean()),
                    number(q.max_delay.mean()),number(q.p95_delay.mean()),number(q.ratio_max.mean())])
        table(f'online_{phase}_table',caption,f'tab:online{phase}',
              ['方法(参数)','匹配率','均值/min','最大/min','P95/min','max实例比'],rows,
              '每行对5个输入seed先逐实例算指标，再平均；P95不是把全部seed混成单条观测。部分覆盖的实例比无定义，以--表示。')


def evolution_tables():
    d=read_csv('task2/results/evolution/summary.csv')
    rows=[]
    baseline=d[(d.stage=='baseline')&((d.batch_id=='inner_hour18_batchseed2024')|(d.batch_id=='dtlz2'))]
    for (batch,obj,algo),q in baseline.groupby(['batch_id','n_obj','algorithm']):
        rows.append(['DTLZ2' if batch=='dtlz2' else f'派单{obj}D',{'nsga2':'NSGA-II','nsga3':'NSGA-III'}[algo],
              f'{q.HV.mean():.6f} $\\pm$ {q.HV.std(ddof=1):.6f}',number(q.Spacing_cv.mean()),number(q.runtime.mean())])
    text_intro='18点相同开发批次；5seed均值±样本标准差，DTLZ2独立使用92/400设置。'
    # Some run IDs use a more explicit DTLZ batch label; detect by the actual stage as well.
    if not any(r[0]=='DTLZ2' for r in rows):
        for algo,q in d[d.front_error.notna()&(d.stage=='baseline')].groupby('algorithm'):
            rows.append(['DTLZ2',{'nsga2':'NSGA-II','nsga3':'NSGA-III'}[algo],f'{q.HV.mean():.6f} $\\pm$ {q.HV.std(ddof=1):.6f}',number(q.Spacing_cv.mean()),number(q.runtime.mean())])
    table('evolution_table',text_intro,'tab:evobaseline',['问题','算法','HV','Spacing','EA秒'],rows,
          '各问题使用各自预先定义的共同标尺，HV不是百分比，也不跨不同问题比高低。',columns='Ylrrr')
    rows=[]
    labels={('baseline',100,300):'基线',('scale',200,300):'种群200',('scale',100,600):'代数600',
            ('hybrid',100,300):'KM初始',('combination',200,300):'KM+种群'}
    q=d[(d.batch_id=='inner_hour18_batchseed2024')&(d.n_obj==2)]
    for (stage,pop,gen),label in labels.items():
        for algo in ['nsga2','nsga3']:
            z=q[(q.stage==stage)&(q.pop_size==pop)&(q.n_gen==gen)&(q.algorithm==algo)]
            if len(z)!=5:raise ValueError((stage,pop,gen,algo,len(z)))
            extra=41 if stage in ['hybrid','combination'] else 0
            rows.append([{'nsga2':'II','nsga3':'III'}[algo],label,
               f'{z.HV.mean():.6f}',number(z.Spacing_cv.mean()),
               f'{int(z.n_eval.iloc[0]):,}'+(f'(+{extra})' if extra else ''),number(z.total_runtime.mean())])
    table('evolution_budget_table','18点开发输入的单项、父项和组合，每项5个进化seed。','tab:evobudget',
          ['算法','变化','HV均值','Spacing','目标评价','总秒'],rows,
          '括号为额外KM初始化目标求和次数，另有相同次数标量求解；共同归一化成本分开记录。现场并发耗时不作严格微基准。',columns='lYrrrr')
    c=d[(d.stage=='confirmation')&(d.n_obj==2)].copy()
    rows=[]
    if len(c):
        for bid,q in c.groupby('batch_id'):
            base=q[q.run_id.str.contains('teacher|baseline')]
            hybrid=q[q.run_id.str.contains('hybrid|km')]
            # Canonical run metadata also distinguishes the two confirmation stages by stage/name.
            if len(base)!=1 or len(hybrid)!=1:
                p=ROOT/'task2/public_results/evolution/metrics.json';SOURCES.append(p)
                raw=json.loads(p.read_text())['rows'];lookup={x['run_id']:x for x in raw}
                q=q.copy();q['init']=[lookup[x].get('initialization','') for x in q.run_id]
                base=q[~q['init'].str.contains('km')];hybrid=q[q['init'].str.contains('km')]
            if len(base)==1 and len(hybrid)==1:
                a,b=base.HV.iloc[0],hybrid.HV.iloc[0];rows.append([esc(bid.replace('test_hour18_batchseed','')),number(a,6),number(b,6),f'{b-a:+.6f}'])
    # Final packet run stages are explicit; use original run identity to classify teacher vs KM seeds.
    if not rows:
        p=ROOT/'task2/public_results/evolution/metrics.json';SOURCES.append(p)
        rr=json.loads(p.read_text())['rows'];by={}
        for r in rr:
            if 'test_hour18' not in r['batch_id'] or r['algorithm']!='nsga2':continue
            raw=ROOT/r['path'];SOURCES.append(raw);record=json.loads(raw.read_text())
            by.setdefault(r['batch_id'],{})['hybrid' if record.get('initialization','').startswith('km') else 'teacher']=r['metrics']['HV']
        for key,v in sorted(by.items()):
            if len(v)==2:rows.append([esc(key.replace('test_hour18_batchseed','')),number(v['teacher'],6),number(v['hybrid'],6),f"{v['hybrid']-v['teacher']:+.6f}"])
    if len(rows)!=5:raise ValueError(f'Expected five paired held-out EA inputs, found {len(rows)}')
    table('evolution_confirmation_table','冻结后的5个未来日期池独立采样输入，算法预算相同。','tab:evofuture',
          ['输入seed','Teacher-II HV','KM初始化HV','成对差'],rows,
          '未来输入seed9010--9014、进化seed10--14；每对在自身共同标尺下相减，不重新选择参数。')


def rl_tables():
    d=read_csv('task2/results/rl/SUMMARY.csv')
    rows=[]
    for fleet in [40,60,100]:
        q=d[d.run_id==f'final_fleet{fleet}']
        if not len(q):q=d[(d.run_id.str.contains('final'))&d.run_id.str.contains(f'fleet{fleet}')]
        for policy,label in [('greedy','最近'),('km','KM即时'),('qkm','Q-KM')]:
            z=q[q.policy==policy]
            if len(z)!=1:raise ValueError((fleet,policy,'final row identity mismatch',q.run_id.tolist()))
            r=z.iloc[0];rows.append([fleet,label,number(r.revenue_mean,2),number(r.answer_rate_mean,4),number(r.avg_pickup_mean,3),number(r.completed_revenue_mean,2)])
    table('rl_fleet_table','首批5个留出模拟日：车队和策略比较。','tab:rlfleet',
          ['车辆','策略','接单车费','应答率','接驾/km','期内完成车费'],rows,
          '接单收入与期内完成收入分开。车费为教学代理，非真实人民币；各车队独立重训300回合。',columns='rlrrrr')
    q=d[d.run_id.str.startswith('sensitivity')&(d.policy=='qkm')]
    rows=[]
    names={'sensitivity_gamma08':'gamma=.8','sensitivity_gamma095':'gamma=.95','sensitivity_grid6':'grid=6','sensitivity_grid10':'grid=10','sensitivity_patience1':'patience=1','sensitivity_patience3':'patience=3'}
    base=d[(d.run_id=='baseline_f60')&(d.policy=='qkm')].iloc[0]
    rows.append(['原参考',number(base.revenue_mean,2),number(base.answer_rate_mean,4),number(base.avg_pickup_mean)])
    for _,r in q.iterrows():rows.append([esc(names.get(r.run_id,r.run_id)),number(r.revenue_mean,2),number(r.answer_rate_mean,4),number(r.avg_pickup_mean)])
    table('rl_sensitivity_table','60车开发单因素；每项重新训练300回合、同5个验证模拟日。','tab:rlsensitivity',
          ['变化','接单车费','应答率','接驾/km'],rows,'每项只改变命名参数；patience变化改变等待合同，不能直接解释为相同服务约束下的质量改善。')
    q=d[(d.identity.str.startswith('final'))&d.run_id.str.contains('enhance')]
    if not len(q):
        p=ROOT/'task2/results/rl/final_v1/enhancements/day_metrics.json';SOURCES.append(p);raw=pd.DataFrame(json.loads(p.read_text()))
        q=raw.groupby('policy').agg(revenue_mean=('revenue','mean'),answer_rate_mean=('answer_rate','mean'),avg_pickup_mean=('avg_pickup','mean'),empty_km_mean=('empty_km','mean')).reset_index()
    labels={'qkm':'Q-KM参考','km':'KM父项','km_move3':'KM+调度3','qkm_move3':'Q-KM+调度3','qkm_move5':'Q-KM+调度5',
            'q_beta1':'Q(beta1)','double_beta1':'Double(beta1)','qnsga_knee':'融合膝点','qnsga_constraint':'融合约束'}
    rows=[]
    for policy,label in labels.items():
        r=q[q.policy==policy].iloc[0];rows.append([label,number(r.revenue_mean,2),number(r.answer_rate_mean,4),number(r.avg_pickup_mean),number(r.empty_km_mean,2)])
    table('rl_enhancement_table','冻结策略的首批5日留出确认，60辆车。','tab:rlenhance',
          ['策略','接单车费','应答率','接驾/km','额外调度/km'],rows,
          '额外调度距离不包含接驾；所有策略同订单/初始车。原Q、Double、融合和父项分别保留，不据此更换选择。')
    rows=[]
    for folder,label in [('final_v1/enhancements','首批'),('final_montecarlo_v1','补充')]:
        p=ROOT/'task2/results/rl'/folder/'day_metrics.json';SOURCES.append(p)
        raw=pd.DataFrame(json.loads(p.read_text())).set_index(['policy','day_seed'])
        a=raw.loc['km_move3'].sort_index();b=raw.loc['qkm'].sort_index()
        assert a.index.equals(b.index)
        gross=a.revenue-b.revenue;costed=gross-a.empty_km+b.empty_km
        n=len(gross);crit=student_t.ppf(.975,n-1)
        for scope,series in [('gross收入差',gross),('收入减额外调度成本差',costed)]:
            mu=series.mean();half=crit*series.std(ddof=1)/np.sqrt(n)
            rows.append([label,n,scope,number(mu,2),f'[{mu-half:,.2f}, {mu+half:,.2f}]'])
    table('rl_montecarlo_table','固定KM+调度3相对Q-KM：两批模拟身份保持独立。','tab:rlmc',
          ['批次','n','比较量','配对均差','描述性t95区间'],rows,
          '成本情景只扣1教学单位/km的额外reposition，没有扣接驾/载客/固定成本；不是实际利润。区间仅描述相同代理池的采样波动。',columns='lrYrr')
    rows=[]
    for run,label in [('baseline_f60','教师全代理'),('offset_robustness','剔除UTC矛盾对')]:
        r=d[(d.run_id==run)&(d.policy=='qkm')].iloc[0]
        rows.append([label,number(r.revenue_mean,2),number(r.answer_rate_mean,4),number(r.avg_pickup_mean)])
    table('offset_table','UTC矛盾对的单因素稳健性：60车/300回合、5验证模拟日。','tab:offset',
          ['训练代理池','接单车费','应答率','接驾/km'],rows,
          '原始25550教学代理保留；剔除副本不改offset、不重排原数据，验证运营池不受那1对6:00前异常影响。')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    online_tables();evolution_tables();rl_tables()
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in set(SOURCES)}
    (OUT/'sources.json').write_text(json.dumps({'actual_input_hashes':manifest,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
    print('Created',len(list(OUT.glob('*.tex'))),'numerical tables from canonical results')


if __name__=='__main__':main()
