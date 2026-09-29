"""Render the user-selected G1-A form from previously verified frozen data."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE=Path(__file__).resolve().parents[1]
P={'paper':'#FCFAF7','ink':'#2D3238','muted':'#70757A','blue':'#5B9FBE','rose':'#B97589','violet':'#8177A8','rule':'#DDE3E7'}

def main():
    plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10.5,
      'axes.labelsize':11.4,'axes.unicode_minus':False,'pdf.fonttype':42,
      'svg.fonttype':'path','text.color':P['ink'],'axes.labelcolor':P['ink'],
      'xtick.color':P['muted'],'ytick.color':P['muted']})
    d=json.loads((BASE/'data/trajectory_examples.json').read_text())['352']
    xy=np.asarray(d['xy'],float);xy=xy-xy[0]
    t=(np.asarray(d['time'],float)-d['time'][0])/60.
    fig=plt.figure(figsize=(7.0,5.1),facecolor=P['paper'])
    ax=fig.add_axes([.12,.13,.77,.77],projection='3d',facecolor=P['paper'])
    for g in d['raw_segments']:
        ax.plot(xy[g,0],xy[g,1],t[g],color=P['muted'],alpha=.50,lw=1.05)
    for g in d['final_segments']:
        ax.plot(xy[g,0],xy[g,1],t[g],color=P['violet'],lw=1.8,marker='o',ms=2.7)
    bad=np.flatnonzero(np.array(d['s0_fate'])==1)
    ax.scatter(xy[bad,0],xy[bad,1],t[bad],s=26,c=P['rose'],marker='x',linewidths=1.3,depthshade=False)
    ax.set_xlabel('相对东向位置 / 工作米',labelpad=9)
    ax.set_ylabel('相对北向位置 / 工作米',labelpad=10)
    ax.set_zlabel('距首点时间 / 分钟',labelpad=7)
    ax.set_xticks([-2000,-1000,0]);ax.set_yticks([-3000,-2000,-1000,0]);ax.set_zticks([0,2,4,6,8,10])
    ax.tick_params(labelsize=9.5,pad=1)
    ax.view_init(elev=25,azim=-56)
    ax.set_box_aspect((np.ptp(xy[:,0])/np.ptp(xy[:,1]),1.0,.80))
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:
        axis.pane.fill=False;axis.pane.set_edgecolor(P['rule'])
        axis.line.set_color(P['rule']);axis._axinfo['grid'].update(color=P['rule'],linewidth=.50)
    legend=[Line2D([],[],color=P['muted'],lw=1.3,label='分段后的原始观测'),
       Line2D([],[],color=P['violet'],marker='o',lw=1.7,ms=3.5,label='最终方案的保留点'),
       Line2D([],[],color=P['rose'],marker='x',ls='',ms=5,label='方向规则删除点')]
    fig.legend(handles=legend,loc='upper center',bbox_to_anchor=(.50,.99),frameon=False,ncol=3,
       handlelength=1.35,columnspacing=1.3,fontsize=9.3)
    for ext in ['png','svg']:
        fig.savefig(BASE/'figures'/f'G1A_space_time.{ext}',dpi=300,facecolor=P['paper'])
    import cairosvg
    cairosvg.svg2pdf(url=str(BASE/'figures'/'G1A_space_time.svg'), write_to=str(BASE/'figures'/'G1A_space_time.pdf'))
    plt.close(fig)
    print('G1-A 已导出：PNG / SVG / PDF；数据与参数未改动。')

if __name__=='__main__': main()
