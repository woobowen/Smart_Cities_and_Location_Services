"""Regenerate report figures from frozen, included numerical inputs.
No parameter fitting, method search or model calls occur in this file.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.path import Path as MPath
from matplotlib.lines import Line2D
from matplotlib import ticker
import cairosvg

B=Path(__file__).resolve().parents[1]; D=B/'data'; O=B/'figures'
P={'paper':'#FCFAF7','ink':'#2D3238','muted':'#70757A','blue':'#5B9FBE','apricot':'#D49757','rose':'#B97589','violet':'#8177A8','lightblue':'#D3EAF5','lightrose':'#E8C7D3','lightviolet':'#D7D3EA','rule':'#DDE3E7','panel':'#FFFDFC'}
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10.2,'axes.labelsize':10.5,'xtick.labelsize':9,'ytick.labelsize':9,'axes.unicode_minus':False,'text.color':P['ink'],'axes.labelcolor':P['ink'],'xtick.color':P['muted'],'ytick.color':P['muted'],'axes.edgecolor':P['rule'],'figure.facecolor':P['paper'],'axes.facecolor':P['paper'],'svg.fonttype':'path','pdf.fonttype':42})

def make(h=3.8,rect=(.11,.19,.84,.73),three=False):
 f=plt.figure(figsize=(7.0,h)); a=f.add_axes(rect,projection='3d' if three else None)
 if not three:
  a.spines[['top','right']].set_visible(False); a.grid(axis='y',color=P['rule'],lw=.55,zorder=0)
 else:
  for v in [a.xaxis,a.yaxis,a.zaxis]:
   v.pane.fill=False;v.line.set_color(P['rule']);v._axinfo['grid'].update(color=P['rule'],linewidth=.5)
 return f,a

def save(f,name):
 for ext in ['png','svg']:f.savefig(O/(name+'.'+ext),dpi=300,facecolor=P['paper'])
 cairosvg.svg2pdf(url=str(O/(name+'.svg')),write_to=str(O/(name+'.pdf')))
 plt.close(f)
 return name

def parameters():
 df=pd.read_csv(D/'parameter_grid.csv');m=df.pivot(index='min_length',columns='min_points',values='coverage_pct').sort_index()
 x,y=m.columns.to_numpy(),m.index.to_numpy();X,Y=np.meshgrid(x,y);Z=m.to_numpy()
 f,a=make(4.6,(.10,.12,.76,.78),True)
 a.plot_surface(X,Y,Z,color=P['blue'],alpha=.24,edgecolor=P['muted'],lw=.6,shade=False)
 a.scatter(X.ravel(),Y.ravel(),Z.ravel(),color=P['ink'],s=18,depthshade=False)
 a.scatter([5],[65],[m.loc[65,5]],color=P['apricot'],marker='s',s=66,depthshade=False)
 a.scatter([2],[0],[m.loc[0,2]],color=P['violet'],marker='D',s=70,depthshade=False)
 a.set_xlabel('最少点数',labelpad=8);a.set_ylabel('最短长度 / 工作米',labelpad=9);a.set_zlabel('共同覆盖率 / %',labelpad=8)
 a.set_xticks(x);a.set_yticks(y);a.set_zlim(0,105);a.set_zticks([0,25,50,75,100]);a.tick_params(pad=1)
 a.view_init(27,-57);a.set_box_aspect((1.2,1.1,.85))
 f.legend(handles=[Line2D([],[],color=P['apricot'],marker='s',ls='',label='参考：5 点、65 工作米'),Line2D([],[],color=P['violet'],marker='D',ls='',label='调整：2 点、0 工作米')],loc='upper center',bbox_to_anchor=(.5,1),frameon=False,ncol=2,fontsize=9.2)
 return save(f,'filter_parameter_surface')

def direction():
 q=pd.read_csv(D/'parameter_results.csv');v=q[(q['dt']==30)&(q.distance==400)&(q.min_points==5)&(q.min_length==65)&(q.dp==5)].sort_values('direction')
 f,a=make(3.4,(.12,.19,.83,.71));cs=[P['apricot'] if x==35 else P['blue'] for x in v.direction]
 a.bar(v.direction.astype(str),v.n_direction_removed,color=cs,width=.6,zorder=3)
 for i,n in enumerate(v.n_direction_removed):a.text(i,n+35,f'{n:,}',ha='center',fontsize=10)
 a.set_xlabel('方向阈值 / 度');a.set_ylabel('方向规则删除点数');a.set_ylim(0,max(v.n_direction_removed)*1.2)
 a.text(.98,.94,'120 条记录；11,777 个原始点\n五组共同覆盖均为 8,408 点',transform=a.transAxes,ha='right',va='top',fontsize=9.2,color=P['muted'])
 return save(f,'direction_parameter')

def dp():
 q=pd.read_csv(D/'parameter_results.csv');v=q[(q['dt']==30)&(q.distance==400)&(q.min_points==5)&(q.min_length==65)&(q.direction==35)].sort_values('dp')
 f,a=make(3.7,(.12,.2,.83,.73));a.plot(v.dp_max_error,v.dp_saving*100,c=P['blue'],lw=1,alpha=.65,zorder=2)
 for r in v.itertuples():
  c=P['rose'] if r.dp_max_error>5+1e-7 else (P['apricot'] if r.dp==5 else P['blue'])
  a.scatter(r.dp_max_error,r.dp_saving*100,s=48,c=c,marker='D' if r.dp==5 else 'o',zorder=3)
  if r.dp==0:dx,dy=7,5
  elif r.dp==.5:dx,dy=-25,4
  elif r.dp==1:dx,dy=7,-13
  elif r.dp==2:dx,dy=-22,8
  elif r.dp==5:dx,dy=7,-14
  else:dx,dy=6,-13
  a.annotate(f'ε={r.dp:g}',(r.dp_max_error,r.dp_saving*100),xytext=(dx,dy),textcoords='offset points',fontsize=9)
 a.axvline(5,color=P['apricot'],ls='--',lw=1);a.text(5.3,12,'共同预算：5',color=P['apricot'],fontsize=9)
 a.set_xlabel('完整 DP 输入的最大简化误差 / 工作米');a.set_ylabel('DP 省点率 / %');a.set_xlim(-.6,22);a.set_ylim(-5,100)
 return save(f,'dp_error_saving')

def sankey():
 M=np.loadtxt(D/'fate_transition_counts.csv',delimiter=',',skiprows=1,dtype=int);N=M.sum();L=M.sum(1);R=M.sum(0)
 assert N==1173410 and L.tolist()==[501511,36056,435373,200470] and R.tolist()==[1199,39732,911330,221149]
 f,a=make(4.5,(.01,.07,.98,.83));a.axis('off');a.set_xlim(-.02,1.02);a.set_ylim(-.02,1.03)
 scale=.72/N;gap=.07
 def pos(t):
  top=.97;rs=[]
  for n in t:rs.append((top-n*scale,top));top-=n*scale+gap
  return rs
 lp,rp=pos(L),pos(R);lc=[k[0] for k in lp];rc=[k[0] for k in rp];colors=[P['rose'],P['apricot'],P['blue'],P['violet']];names=['短段过滤','方向删除','DP 精简','显式保留']
 for i in range(4):
  for j in range(4):
   n=int(M[i,j])
   if not n:continue
   h=n*scale;l=lc[i];r=rc[j];lc[i]+=h;rc[j]+=h
   vs=[(.25,l),(.42,l),(.57,r),(.74,r),(.74,r+h),(.57,r+h),(.42,l+h),(.25,l+h),(.25,l)]
   codes=[MPath.MOVETO,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4,MPath.LINETO,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4,MPath.CLOSEPOLY]
   a.add_patch(PathPatch(MPath(vs,codes),fc=colors[j],alpha=.48 if i==0 else .23,ec='none'))
 for name,t,ps,x in [('参考设置',L,lp,.225),('过滤调整',R,rp,.74)]:
  a.text(x+.012,1.02,name,ha='center',fontsize=10.5,weight='bold')
  for i,(bot,top) in enumerate(ps):
   a.add_patch(Rectangle((x,bot),.025,top-bot,fc=colors[i],ec=colors[i],lw=.3))
   tx=x-.012 if x<.5 else x+.038
   a.text(tx,(bot+top)/2,f'{names[i]}\n{t[i]:,}',ha='right' if x<.5 else 'left',va='center',fontsize=9.8)
 a.text(.5,.62,'原先过滤 → 后续 DP 精简\n475,957 点',ha='center',va='center',fontsize=10.5,weight='bold',bbox={'fc':P['paper'],'ec':'none','alpha':.9,'pad':5})
 return save(f,'point_fate_flow')

def hist():
 q=pd.read_csv(D/'confirmation_coverage_pairs.csv');v=q.coverage_delta_pp.to_numpy();assert len(v)==600
 ct=np.r_[sum(v==0),np.histogram(v[v>0],bins=np.linspace(0,100,11))[0]];assert sum(ct)==600
 f,a=make(3.9,(.11,.26,.84,.67));x=np.arange(11)
 a.bar(x,ct,color=[P['apricot']]+[P['blue']]*10,width=.68,zorder=3)
 for i,n in enumerate(ct):a.text(i,n+4,str(n),ha='center',fontsize=9.5)
 a.set_xticks(x,['不变']+[f'{i}–{i+10}' for i in range(0,100,10)],rotation=25,ha='right')
 a.set_ylabel('原始记录数');a.set_xlabel('共同覆盖率增量 / 百分点',labelpad=8);a.set_ylim(0,max(ct)*1.18)
 return save(f,'confirmation_gain_histogram')

def selection():
 q=json.loads((D/'selection_failures.json').read_text());q.sort(key=lambda x:x['combined']-x['baseline'],reverse=True)
 f,a=make(3.0,(.18,.23,.76,.68));vs=[r['combined']-r['baseline'] for r in q]
 a.barh(range(3),vs,color=P['rose'],height=.43,zorder=3)
 a.set_yticks(range(3),[f"记录 {r['record_id']}" for r in q]);a.invert_yaxis();a.set_xlim(0,1);a.grid(False);a.grid(axis='x',color=P['rule'],lw=.55)
 for i,v in enumerate(vs):a.text(v+.02,i,f'+{v:.3f}',va='center',fontsize=11,color=P['rose'])
 a.set_xlabel('共同最大几何偏差的增加量 / 工作米')
 return save(f,'selection_geometry_increase')

def boundary():
 d=json.loads((D/'trajectory_examples.json').read_text())['352'];p=np.array(d['xy']);p=p-p[104];inds=[104,105,106,107];f,a=make(4.2,(.12,.17,.82,.76))
 a.plot(p[inds,0],p[inds,1],color=P['muted'],ls='--',marker='o',ms=4,lw=1.3,label='原始四点片段')
 out=[104,106,107];a.plot(p[out,0],p[out,1],color=P['violet'],marker='o',ms=5,lw=2,label='方向删除后；DP 未再删点')
 point=p[105];aa=p[104];bb=p[106];u=np.clip(np.dot(point-aa,bb-aa)/np.dot(bb-aa,bb-aa),0,1);foot=aa+u*(bb-aa);dist=np.linalg.norm(point-foot)
 assert abs(dist-266.01675442514176)<1e-6
 a.plot([point[0],foot[0]],[point[1],foot[1]],c=P['rose'],lw=1.5,ls=':');a.scatter([point[0]],[point[1]],c=P['rose'],marker='x',s=90,lw=1.8,zorder=5)
 for i,offset in [(104,(-12,8)),(105,(8,-5)),(106,(7,5)),(107,(7,-12))]:a.annotate(str(i),p[i],textcoords='offset points',xytext=offset,fontsize=10)
 a.annotate('点 105 的对应区间\n仅为 104—106',xy=(p[104]+p[106])/2,xytext=(-240,-15),fontsize=9.3,color=P['violet'],arrowprops={'arrowstyle':'->','color':P['violet'],'lw':.9})
 a.annotate('后续点 107 不改变\n点 105 的索引区间',xy=p[107],xytext=(185,80),fontsize=9.1,color=P['muted'],arrowprops={'arrowstyle':'->','color':P['muted'],'lw':.8})
 mid=(point+foot)/2;a.annotate(f'{dist:.3f} 工作米',mid,xytext=(5,8),textcoords='offset points',fontsize=10,color=P['rose'])
 a.set_xlabel('相对东向位置 / 工作米');a.set_ylabel('相对北向位置 / 工作米');a.set_aspect('equal',adjustable='datalim');a.margins(.22);a.legend(frameon=False,fontsize=9,loc='upper left');a.grid(color=P['rule'],lw=.55)
 return save(f,'boundary_record352')

FUNCS={'parameters':parameters,'direction':direction,'dp':dp,'sankey':sankey,'hist':hist,'selection':selection,'boundary':boundary}
def run(which=None):
 out=[]
 for k in (which or list(FUNCS)):out.append(FUNCS[k]())
 return out
if __name__=='__main__':
 import sys
 print(run(sys.argv[1:] or None))
