"""P2 RL figures from traced experiments; report-safe scope metadata per export."""
from pathlib import Path
import argparse,json,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
TASK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TASK/'src'));sys.path.insert(0,str(TASK/'scripts'))
from build_figures import P,save as shared_save,ROOT
from run_rl import load_model,sha
from rl_dispatch import DEFAULT,region_long_term_value,sample_episode,run_episode,greedy_nearest,km_fare
CMAP=LinearSegmentedColormap.from_list('p2value',[P['Paper'],P['P1'],P['C1'],P['Ink']])


def save(fig,name,inputs,claim,selection='formal'):
    shared_save(fig,name,inputs,claim,selection)
    p=TASK/'figures'/selection/(name+'.json')
    m=json.loads(p.read_text());m['helper_script_sha256']=m['script_sha256'];m['script_sha256']=sha(__file__)
    m['figure_language']='English technical labels; teacher-facing Chinese interpretation in report'
    p.write_text(json.dumps(m,ensure_ascii=False,indent=2))


def load_rows(path):return pd.DataFrame(json.loads(Path(path).read_text()))


def prepare_aggregate_inputs():
    """Explicit raw-to-aggregate stage. Public figure replay only needs these aggregates."""
    data=TASK/'results/data';out=TASK/'figures/data';out.mkdir(parents=True,exist_ok=True)
    val=pd.read_csv(data/'trips_validation.csv');initial=pd.read_csv(data/'checkins_train_inner.csv')
    refs={}
    for name,pol in [('Nearest',greedy_nearest),('KM fare',km_fare)]:
        refs[name]=np.mean([run_episode(sample_episode(val,60,10000+k,initial),pol)[0]['revenue'] for k in range(3)])
    (out/'rl_learning_baselines.json').write_text(json.dumps(dict(statistical_unit='simulated validation day',n=3,seeds=[10000,10001,10002],revenue=refs),indent=2))
    trips=pd.read_csv(data/'trips_train_inner.csv');bg=trips.sample(min(3000,len(trips)),random_state=0)
    cols=np.clip((bg.ox.to_numpy()/DEFAULT.width*8).astype(int),0,7)
    rows=np.clip((bg.oy.to_numpy()/DEFAULT.height*8).astype(int),0,7)
    counts=np.bincount(rows*8+cols,minlength=64)
    pd.DataFrame({'zone':np.arange(64),'row':np.arange(64)//8,'column':np.arange(64)%8,'count':counts}).to_csv(out/'rl_value_origin_counts.csv',index=False)
    hist,edges=np.histogram(trips.minute/60,bins=np.linspace(6,24,109))
    pd.DataFrame({'left_hour':edges[:-1],'right_hour':edges[1:],'count':hist}).to_csv(out/'rl_training_time_counts.csv',index=False)
    (out/'rl_aggregate_provenance.json').write_text(json.dumps(dict(
        producer_sha256=sha(__file__),source_hashes={p.name:sha(p) for p in [data/'trips_validation.csv',data/'checkins_train_inner.csv',data/'trips_train_inner.csv']},
        spatial_sample_n=int(counts.sum()),spatial_sample_seed=0,grid='8x8 teacher working model',time_bins='108 bins over6:00-24:00',
        identity='aggregate counts and baseline means only; no individual coordinates or memberships'),indent=2))


def learning_and_values():
    model=TASK/'results/rl/development_v1/q_f60_s2024'
    qt,meta=load_model(model)
    with np.load(model/'model.npz') as a:curve=a['curve'];td=a['td']
    derived=TASK/'figures/data/rl_learning_baselines.json'
    refs=json.loads(derived.read_text())['revenue']
    fig,ax=plt.subplots(1,2,figsize=(8.6,3.4),layout='constrained')
    ax[0].plot(curve[:,0]+1,curve[:,1],'-o',ms=3,color=P['C3'],label='Q-KM')
    for (label,value),color,style in zip(refs.items(),[P['C1'],P['C2']],['--',':']):
        ax[0].axhline(value,color=color,ls=style,label=label)
    ax[0].set(xlabel='Actual training episode',ylabel='Accepted-fare proxy / simulated day',title='A  Same 3 validation simulations')
    ax[0].legend(frameon=False,fontsize=8,loc='lower right');ax[0].grid(axis='y',color=P['Rule'])
    ax[1].plot(np.arange(len(td))+1,td,color=P['P4'],lw=.8,label='Per episode')
    smooth=pd.Series(td).rolling(20,min_periods=1).mean()
    ax[1].plot(np.arange(len(td))+1,smooth,color=P['C4'],lw=1.5,label='20-episode rolling mean')
    ax[1].set(xlabel='Actual training episode',ylabel='Mean absolute TD error',title='B  Learning diagnostic')
    ax[1].legend(frameon=False,fontsize=8);ax[1].grid(axis='y',color=P['Rule'])
    save(fig,'rl_learning',[model/'model.npz',derived,TASK/'figures/data/rl_aggregate_provenance.json'],
         'Development: one training seed2024, 300 actual simulated episodes. Checkpoint validation n3 seeds10000–10002; raw TD plus explicitly labeled smoothing; not held-out test.')
    # A: geography-preserving small multiples. Public vectors contain cell counts only.
    aggregate=TASK/'figures/data/rl_value_origin_counts.csv'
    counts=pd.read_csv(aggregate)['count'].to_numpy()
    time_aggregate=TASK/'figures/data/rl_training_time_counts.csv'
    time_counts=pd.read_csv(time_aggregate)
    hours=[8,13,18,22];vmax=float(qt.V.max())
    fig,axs=plt.subplots(2,2,figsize=(7.2,7.0),layout='constrained')
    for ax,h in zip(axs.flat,hours):
        t=(h*60-DEFAULT.start)//DEFAULT.step_min
        im=ax.imshow(qt.V[t].reshape(8,8),origin='lower',extent=[0,DEFAULT.width,0,DEFAULT.height],cmap=CMAP,vmin=0,vmax=vmax,interpolation='nearest')
        centers=DEFAULT.centers;keep=counts>0
        ax.scatter(centers[keep,0],centers[keep,1],s=counts[keep]/counts.max()*150,
                   facecolors='none',edgecolors=P['C2'],linewidths=.7,alpha=.85)
        ax.set(xlabel='Local model x / km',ylabel='Local model y / km',title=f'{h:02d}:00',xlim=(0,DEFAULT.width),ylim=(0,DEFAULT.height))
    sizes=[25,100,500]
    handles=[axs[0,0].scatter([],[],s=n/counts.max()*150,facecolors='none',edgecolors=P['C2'],linewidths=.7,label=str(n)) for n in sizes]
    fig.legend(handles=handles,loc='outside lower center',ncol=3,frameon=False,fontsize=8,
               title='Sampled training origins per cell (n=3000; same background)',title_fontsize=8)
    fig.colorbar(im,ax=axs.ravel().tolist(),shrink=.75,label='Estimated regional V / proxy currency')
    inputs=[model/'model.npz',aggregate,time_aggregate,TASK/'figures/data/rl_aggregate_provenance.json']
    save(fig,'rl_value_maps',inputs,'Development V, one training seed; 4 real time slices, shared0–max scale. Orange circle area encodes8x8cellcounts of the same seed0sampled3000inner-training origins; circles at teaching cell centers, no individual coordinates embedded. Local teaching coordinates, source CRS unverified.','candidates')
    # B: full measured time×zone matrix, keeping spatial ID explicit rather than inventing a route.
    fig,axs=plt.subplots(2,1,figsize=(8.5,5.2),gridspec_kw={'height_ratios':[4,1]},layout='constrained')
    im=axs[0].imshow(qt.V[:-1].T,origin='lower',aspect='auto',extent=[6,24,0,64],interpolation='nearest',cmap=CMAP,vmin=0,vmax=vmax)
    axs[0].set(xlabel='Local teaching clock / hour',ylabel='Zone ID (row-major 8x8)',title='All 108 modeled steps and 64 zones')
    fig.colorbar(im,ax=axs[0],label='Estimated V / proxy currency',fraction=.04,pad=.02)
    hist=time_counts['count'].to_numpy();edges=np.r_[time_counts.left_hour.to_numpy(),time_counts.right_hour.iloc[-1]]
    axs[1].stairs(hist,edges,color=P['C1'],fill=True,alpha=.7)
    axs[1].set(xlabel='Local teaching clock / hour',ylabel='Proxy OD count',xlim=(6,24))
    save(fig,'rl_value_time_zone',inputs,'Same development V and train-origin demand; all measured time-zone cells, no interpolation. Demand is proxy count, not true taxi demand.','candidates')
    # Chosen map preserves adjacency needed to understand destination and neighboring moves.
    for extension in ['pdf','svg','png','json']:
        src=TASK/'figures/candidates'/f'rl_value_maps.{extension}'
        dst=TASK/'figures/formal'/f'rl_value_maps.{extension}';dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
    meta=json.loads((TASK/'figures/formal/rl_value_maps.json').read_text());meta['selection']='Map small multiples chosen for neighborhood adjacency; full time-zone matrix retained as complementary candidate.'
    (TASK/'figures/formal/rl_value_maps.json').write_text(json.dumps(meta,indent=2))


def beta_and_movement():
    root=TASK/'results/rl';p=root/'beta_validation_v1/day_metrics.json';d=load_rows(p)
    d['beta']=d.policy.str.replace('beta','',regex=False).astype(float)
    fig,axs=plt.subplots(1,2,figsize=(8.6,3.3),layout='constrained')
    for ax,col,label,color in [(axs[0],'revenue','Accepted fare / simulated day',P['C3']),(axs[1],'nonpositive_fraction','Nonpositive / feasible edge opportunities',P['C1'])]:
        g=d.groupby('beta')[col];mean=g.mean();sd=g.std(ddof=1)
        ax.errorbar(mean.index,mean,yerr=sd,fmt='o-',color=color,ms=4,capsize=3)
        ax.axvline(.5,color=P['Muted'],ls=':',lw=1)
        ax.set(xlabel='Long-term value coefficient beta',ylabel=label);ax.grid(axis='y',color=P['Rule'])
    save(fig,'rl_beta_rejection',[p],'Validation n5 paired simulated days, one learned V; mean±sample SD across days. Right denominator counts feasible edge opportunities, not unique rejected orders.')
    p=root/'reposition_cost_validation_v1/day_metrics.json';d=load_rows(p)
    groups=['qkm','qkm_move_cost0','qkm_move_cost1','qkm_move_cost3','qkm_move_cost5']
    labels=['No move','lambda=0','lambda=1','lambda=3','lambda=5']
    fig,axs=plt.subplots(1,2,figsize=(8.6,3.5),layout='constrained')
    for i,(name,label) in enumerate(zip(groups,labels)):
        z=d[d.policy==name];color=[P['Ink'],P['C2'],P['C1'],P['C3'],P['C4']][i]
        axs[0].scatter(z.empty_km,z.revenue,s=18,color=color,alpha=.35)
        axs[0].scatter(z.empty_km.mean(),z.revenue.mean(),s=65,color=color,marker='D',label=label)
    axs[0].set(xlabel='Actual reposition empty distance / km per day',ylabel='Accepted fare / simulated day',title='A  Gross revenue and real movement cost')
    axs[0].legend(frameon=False,fontsize=8,loc='lower right');axs[0].grid(color=P['Rule'])
    g=d.groupby('policy').diagnostic_net_revenue
    means=np.array([g.mean()[x] for x in groups]);std=np.array([g.std()[x] for x in groups])
    axs[1].errorbar(means,np.arange(5),xerr=std,fmt='o',capsize=3,color=P['C4'])
    axs[1].axvline(means[0],ls=':',color=P['Muted'])
    axs[1].set(yticks=np.arange(5),yticklabels=labels,xlabel='Fare minus reposition km\nat 1 proxy currency/km',title='B  Additional movement-cost diagnostic')
    axs[1].invert_yaxis();axs[1].grid(axis='x',color=P['Rule'])
    save(fig,'rl_reposition_cost',[p],'Validation n5 paired simulated days; diamonds=means, dots=individual days. Empty movements occupy drivers. Right subtracts reposition km only at hypothetical1currency/km; pickup is separately tracked, so this is not net profit. lambda values are decision penalties.')
    p=root/'component_ablation_v1/day_metrics.json'
    if p.exists():
        d=load_rows(p);names=['km','qkm','km_move3','qkm_move3']
        labels=['KM, no move','Q-KM, no move','KM + value move','Q-KM + value move']
        fig,axs=plt.subplots(1,3,figsize=(9.0,3.5),sharey=True,layout='constrained')
        for ax,col,label in zip(axs,['revenue','answer_rate','empty_km'],['Accepted fare / day','Response fraction','Reposition empty km / day']):
            for i,name in enumerate(names):
                z=d[d.policy==name][col]
                ax.scatter(z,np.full(len(z),i),s=12,color=P['Muted'],alpha=.3)
                ax.errorbar(z.mean(),i,xerr=z.std(ddof=1),fmt='D' if i>=2 else 'o',color=P['C1'] if i%2==0 else P['C3'],capsize=3)
            ax.set(xlabel=label,yticks=range(4),yticklabels=labels);ax.grid(axis='x',color=P['Rule'])
        axs[0].invert_yaxis()
        save(fig,'rl_movement_ablation',[p],'Validation2x2 parent/removal experiment: immediate vs LT edge weighting crossed with no movement vs same learnedV cost-aware lambda3 movement; n5 paired simulated days, individual points and mean±SD.')


def fleet(final=False):
    root=TASK/'results/rl'/('final_v1' if final else 'development_v1')
    paths=[root/(f'fleet{n}' if final else f'baseline_f{n}_s2024')/'day_metrics.json' for n in [40,60,100]]
    if not all(x.exists() for x in paths):return
    d=pd.concat([load_rows(p) for p in paths],ignore_index=True)
    fig,axs=plt.subplots(1,3,figsize=(9.0,3.4),layout='constrained')
    for ax,col,label in zip(axs,['revenue','answer_rate','avg_pickup'],['Accepted fare / day','Response fraction','Mean pickup / km']):
        for name,label2,color,marker in [('greedy','Nearest',P['C1'],'o'),('km','KM fare',P['C2'],'s'),('qkm','Q-KM',P['C3'],'D')]:
            z=d[d.policy==name];g=z.groupby('fleet')[col]
            ax.errorbar(g.mean().index,g.mean(),yerr=g.std(),fmt=marker+'-',color=color,ms=4,capsize=3,label=label2)
        ax.set(xlabel='Fleet size',ylabel=label,xticks=[40,60,100]);ax.grid(axis='y',color=P['Rule'])
    axs[0].legend(frameon=False,fontsize=8)
    save(fig,'rl_fleet_final' if final else 'rl_fleet_validation',paths,
         ('Held-out' if final else 'Development validation')+' n5 paired sampled simulated days per fleet,300 training episodes per fleet, one training seed. Mean±sample SD over simulations; not independent real operating days.')


def double_and_fusion():
    root=TASK/'results/rl';paths=[];rows=[]
    for seed in range(2024,2029):
        for name in ['q','double']:
            p=root/'double_v2_rngfix'/f'{name}_b1_s{seed}_validation/day_metrics.json'
            if p.exists():
                paths.append(p);z=load_rows(p);z['train_seed']=seed;z['learner']=name;rows.append(z)
    if len(paths)==10:
        d=pd.concat(rows);fig,axs=plt.subplots(1,3,figsize=(9.0,3.4),layout='constrained')
        for ax,col,ylabel in zip(axs,['revenue','answer_rate','nonpositive_fraction'],['Accepted fare / simulated day','Response fraction','Nonpositive / feasible edge opportunities']):
            g=d[d.policy=='beta1'].groupby(['train_seed','learner'])[col].mean().unstack()
            for seed in g.index:ax.plot([0,1],g.loc[seed,['q','double']],'-o',color=P['C4'],alpha=.55,ms=4)
            ax.set(xticks=[0,1],xticklabels=['Q-learning','Double Q'],ylabel=ylabel,title='beta=1; paired training seeds')
            ax.grid(axis='y',color=P['Rule'])
        save(fig,'rl_double_paired',paths,'Validation:5 training seeds×5 common sampled simulated days. Each line is one training-seed mean over days; separate behavior and estimator-update RNGs. No pooling of 25 dependent days as25 independent trained models.')
    public_static=TASK/'public_results/rl/static_fronts.json'
    static=public_static if public_static.exists() else root/'fusion_validation_v1/static_fronts.json'
    dyn=root/'fusion_validation_v1/dynamic/day_metrics.json'
    if static.exists() and dyn.exists():
        fronts=json.loads(static.read_text());d=load_rows(dyn)
        fig,axs=plt.subplots(1,2,figsize=(8.6,4.0),layout='constrained')
        for i,r in enumerate(fronts):
            F=np.array(r['F']);axs[0].plot(F[:,1],-F[:,0],'.',color=P['C4'],alpha=.25)
        F=np.array(fronts[0]['F']);k=fronts[0]['knee'];axs[0].scatter(F[k,1],-F[k,0],s=75,marker='*',color=P['C3'],label='Seed 0 knee')
        axs[0].set(xlabel='Batch pickup total / km',ylabel='Estimated Q-KM edge-value sum',title='A  One 18:00 validation context')
        axs[0].legend(frameon=False,fontsize=8);axs[0].grid(color=P['Rule'])
        for name,label,color,mark in [('greedy','Nearest',P['C1'],'o'),('km','KM fare',P['C2'],'s'),('qkm','Q-KM',P['C3'],'D'),('qnsga_knee','NSGA knee',P['C4'],'^'),('qnsga_constraint','NSGA constrained',P['Ink'],'v')]:
            z=d[d.policy==name];axs[1].scatter(z.avg_pickup.mean(),z.revenue.mean(),color=color,marker=mark,s=60,label=label)
        axs[1].set(xlabel='Realized average pickup / km',ylabel='Realized accepted fare / day',title='B  Full-day simulation, n=5')
        fig.legend(*axs[1].get_legend_handles_labels(),frameon=False,fontsize=8,loc='outside lower center',ncol=3)
        axs[1].grid(color=P['Rule'])
        save(fig,'rl_fusion_front_and_effect',[static,dyn],'Left:5 NSGA seeds100pop300gen on actual QKM18:00 context; estimated long-term score. Right:mean of5 validation full-day simulations,40pop30gen per dispatch; realized fare. Different quantities and compute budgets explicitly separated.')


def final_effects():
    from scipy.stats import t
    p=TASK/'results/rl/final_v1/enhancements/day_metrics.json'
    if not p.exists():return
    d=load_rows(p);reference=d[d.policy=='qkm'].set_index('day_seed')
    names=['km_move3','qkm_move3','qkm_move5','qnsga_constraint','qnsga_knee']
    labels=['KM + move, lambda3','Q-KM + move, lambda3','Q-KM + move, lambda5','NSGA constrained','NSGA knee']
    fig,axs=plt.subplots(1,2,figsize=(9.0,4.0),layout='constrained')
    for i,name in enumerate(names):
        z=d[d.policy==name].set_index('day_seed');diff=z.revenue-reference.revenue
        half=t.ppf(.975,len(diff)-1)*diff.std(ddof=1)/np.sqrt(len(diff))
        axs[0].scatter(diff,np.full(len(diff),i),color=P['Muted'],alpha=.35,s=12)
        axs[0].errorbar(diff.mean(),i,xerr=half,fmt='D',color=[P['C1'],P['C3'],P['C4'],P['Ink'],P['C2']][i],capsize=3)
    axs[0].axvline(0,ls=':',color=P['Muted']);axs[0].set(yticks=range(5),yticklabels=labels,xlabel='Paired accepted-fare change vs Q-KM',title='A  Frozen held-out comparison, n=5')
    axs[0].invert_yaxis();axs[0].grid(axis='x',color=P['Rule'])
    for name,label,color in [('km_move3','Selected KM + move3',P['C1']),('qkm_move5','Retained Q-KM + move5',P['C4'])]:
        z=d[d.policy==name].set_index('day_seed');gain=z.revenue-reference.revenue
        axs[1].scatter(z.empty_km,gain,color=color,alpha=.35,s=20)
        axs[1].scatter(z.empty_km.mean(),gain.mean(),color=color,marker='D',s=65,label=label)
    axs[1].plot([0,1100],[0,1100],':',color=P['Muted'],label='Hypothetical 1 currency/km')
    axs[1].axhline(0,color=P['Rule']);axs[1].set(xlabel='Extra reposition distance / km per day',ylabel='Paired accepted-fare change vs Q-KM',title='B  Gross gain and extra empty travel')
    axs[1].legend(frameon=False,fontsize=7.5,loc='upper left');axs[1].grid(color=P['Rule'])
    save(fig,'rl_final_tradeoffs',[p],'Held-out primary frozen n5 paired proxy simulations, one trained model. Left:individual differences and mean±descriptive pairedt95 interval; not real-date populationconfidence. Right:actual extra movement and grossfare change;1/km line is hypothetical reposition cost only, not net profit. Finaltest never changes selected policy.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true')
    p.add_argument('--prepare-data',action='store_true',help='Explicitly recompute public count/baseline aggregates from local audited raw-derived CSVs')
    args=p.parse_args()
    if args.prepare_data:prepare_aggregate_inputs()
    learning_and_values();beta_and_movement();fleet(False);double_and_fusion()
    if args.final:
        fleet(True);final_effects()
if __name__=='__main__':main()
