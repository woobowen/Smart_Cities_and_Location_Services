"""Current repair diagnostics and actual call status; old failed diagrams preserved."""
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from task1.workflow.io import read_json,write_json,digest,relative
from task1.workflow.budget import REVISION,LEDGER
from task1.scripts.build_goal1_figures import palette,export_drawio_svg,render_drawio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager


def main():
    out=REVISION/'figures';out.mkdir(exist_ok=True);colors=palette()
    font_path=subprocess.check_output(['fc-match','-f','%{file}','Noto Sans CJK SC'],text=True).strip()
    font_manager.fontManager.addfont(font_path);font=font_manager.FontProperties(fname=font_path)
    plt.rcParams.update({'font.family':font.get_name(),'figure.facecolor':colors['Paper'],'axes.facecolor':colors['Paper'],
                         'text.color':colors['Ink'],'axes.labelcolor':colors['Ink'],'svg.fonttype':'none'})
    rows=read_json(REVISION/'results/profile_pilot.json')['result']['profiles']
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,field,label,color in [(axes[0],'zero_dt','零时间差',colors['C1']),(axes[1],'consecutive_duplicate_position','相邻重复位置',colors['C4'])]:
        bars=ax.bar(range(7),[r[field] for r in rows],color=color)
        ax.bar_label(bars,padding=3);ax.set_xticks(range(7),[r['record_id']+'\n边='+str(r['edges_total']) for r in rows])
        ax.set_title(label,loc='left');ax.set_ylabel('原始相邻边数');ax.set_xlabel('固定 pilot 的原始 ID / 分母')
        ax.spines[['top','right']].set_visible(False);ax.set_ylim(0,max(r[field] for r in rows)*1.15+3)
    for suffix in ('png','svg','pdf'):fig.savefig(out/('pilot_diagnostics.'+suffix),dpi=300)
    plt.close(fig)
    ledger=read_json(LEDGER);calls=list(ledger['calls'].items())
    probe=next((v['status'] for k,v in calls if v['probe']),'NOT_RUN')
    roles=read_json(REVISION/'runs/g1-repair-roles-01/manifest.json') if (REVISION/'runs/g1-repair-roles-01/manifest.json').exists() else None
    role_calls=[(k,v) for k,v in calls if not v['probe']]
    statuses=[probe]+[role_calls[i][1]['status'] if i<len(role_calls) else 'NOT_RUN' for i in range(5)]
    labels=['连通性探针','A · 初始诊断','B · 实际执行','C · 独立核查','A · 反馈后动作','C · 再次核查']
    mx=ET.Element('mxfile',host='app.diagrams.net');d=ET.SubElement(mx,'diagram',name='Repair actual state')
    model=ET.SubElement(d,'mxGraphModel',page='1',pageWidth='1400',pageHeight='840');root=ET.SubElement(model,'root')
    ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    def node(id,text,x,y,w,h,fill='Panel',size=20):
        cell=ET.SubElement(root,'mxCell',id=id,value=text,vertex='1',parent='1',style=f'fillColor={colors.get(fill,fill)};strokeColor={colors["Rule"]};fontColor={colors["Ink"]};fontSize={size};')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    node('title','Goal 1 定向修复 · 本批实际调用与处理边界',40,25,1320,65,'none',28)
    for i,(label,status) in enumerate(zip(labels,statuses)):
        textstatus='有效结构响应' if status=='VERIFIED_STRUCTURE_ONLY' else '受阻 / 已停止' if status=='BLOCKED' else '尚未调用'
        node('call'+str(i),label+'\n'+textstatus,35+i*225,145,205,120,'P1' if status=='VERIFIED_STRUCTURE_ONLY' else 'Panel',20)
        if i<5:
            cell=ET.SubElement(root,'mxCell',id='edge'+str(i),edge='1',parent='1',style=f'strokeColor={colors["C1"]};dashed={int(statuses[i+1]=="NOT_RUN")};')
            g=ET.SubElement(cell,'mxGeometry',**{'as':'geometry'});ET.SubElement(g,'mxPoint',x=str(240+i*225),y='205',**{'as':'sourcePoint'});ET.SubElement(g,'mxPoint',x=str(260+i*225),y='205',**{'as':'targetPoint'})
    node('budget',f'新批次预算\n外层预留 {ledger["model_attempts"]} / 6；串行\n工具请求 {ledger["tool_requests"]} / 12\n首次可见异常 → 终止整个进程组\n底层服务请求数：unknown',50,345,615,235)
    node('research','真实数据：7 条 / 783 点\nD1 坐标基准与距离口径未批准\nD2 去噪删除调度未批准\n完整真实处理：BLOCKED\n未处理点保留原始 ID 与索引',735,345,615,235)
    loop=roles.get('diagnostic_loop_status','NOT_COMPLETE') if roles else 'NOT_COMPLETE'
    node('footer',f'诊断闭环：{loop}；完整真实 baseline：BLOCKED。\n旧 run01/02/03 与旧预算冻结保留；本图只表示新批次。\n虚线表示没有发生的交接；构造处理测试不计入真实轨迹结果。',50,650,1300,150,'none',23)
    path=out/'repair_loop.drawio';ET.indent(mx);ET.ElementTree(mx).write(path,encoding='utf-8',xml_declaration=True)
    export_drawio_svg(path,path.with_suffix('.svg'));render_drawio(path)
    write_json(out/'manifest.json',{'code_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
               'classification':'CURRENT_REPAIR_REAL_DIAGNOSTICS_AND_ACTUAL_LIVE_STATUS','statuses':statuses,'data_sha256':digest(REVISION/'results/profile_pilot.json'),
               'ledger_sha256':digest(LEDGER),'palette':relative(ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex'),
               'files':{p.name:digest(p) for p in out.iterdir() if p.name!='manifest.json'},'baseline_before_after':'BLOCKED: no real baseline result'})


if __name__=='__main__':main()
