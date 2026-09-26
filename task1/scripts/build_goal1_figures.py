"""P2 raw diagnostic figures and an editable draw.io implementation diagram.

The SVG diagram is exported by this script from its own draw.io mxGeometry,
including the same vertices/waypoints/labels. No hosted renderer or generated art.
"""
from pathlib import Path
import csv
import json
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from task1.workflow.io import DATA,CONFIG,EVIDENCE,read_json,write_json,digest,now,relative
from task1.workflow.diagnostics import profile,aggregate,time_boundaries,independent_profile_review,duplicate_details
from task1.workflow.tools import execute_tool
from task1.workflow.controller import PHASES

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch

OUT=ROOT/'task1/figures/goal1'
RESULTS=ROOT/'task1/results/goal1'
RUN_ID='g1-live-20260926-03'


def palette():
    text=(ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex').read_text()
    return {name:'#'+value for name,value in re.findall(r'\\definecolor\{(\w+)\}\{HTML\}\{([A-F0-9]+)\}',text)}


def export_drawio_svg(source,target):
    doc=ET.parse(source)
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width='1400',height='840',viewBox='0 0 1400 840')
    defs=ET.SubElement(svg,'defs');marker=ET.SubElement(defs,'marker',id='arrow',markerWidth='10',markerHeight='10',refX='9',refY='3',orient='auto',markerUnits='strokeWidth')
    ET.SubElement(marker,'path',d='M0,0 L0,6 L9,3 z',fill='#5B9FBE')
    ET.SubElement(svg,'rect',width='1400',height='840',fill='#FCFAF7')
    for cell in doc.findall('.//mxCell'):
        g=cell.find('mxGeometry')
        if g is None:continue
        style=dict(item.split('=',1) for item in cell.get('style','').split(';') if '=' in item)
        if cell.get('vertex')=='1':
            x,y,w,h=[float(g.get(k,'0')) for k in ('x','y','width','height')]
            if style.get('fillColor')!='none':
                ET.SubElement(svg,'rect',x=str(x),y=str(y),width=str(w),height=str(h),rx='6',fill=style.get('fillColor','#FFFDFC'),stroke=style.get('strokeColor','#DDE3E7'),**{'stroke-width':'2'})
            size=float(style.get('fontSize','20'));lines=cell.get('value','').split('\n')
            for i,line in enumerate(lines):
                text=ET.SubElement(svg,'text',x=str(x+18),y=str(y+30+i*(size+8)),fill=style.get('fontColor','#2D3238'),**{'font-family':'Noto Sans CJK SC, sans-serif','font-size':str(size)})
                text.text=line
        elif cell.get('edge')=='1':
            points=[g.find("mxPoint[@as='sourcePoint']"),*g.findall('Array/mxPoint'),g.find("mxPoint[@as='targetPoint']")]
            coords=' '.join(p.get('x')+','+p.get('y') for p in points)
            attrs={'points':coords,'fill':'none','stroke':style.get('strokeColor','#5B9FBE'),'stroke-width':'2.5','marker-end':'url(#arrow)'}
            if style.get('dashed')=='1':attrs['stroke-dasharray']='8 6'
            ET.SubElement(svg,'polyline',attrs)
            if cell.get('value'):
                text=ET.SubElement(svg,'text',x=g.get('labelX'),y=g.get('labelY'),fill='#2D3238',**{'font-family':'Noto Sans CJK SC, sans-serif','font-size':'18'})
                text.text=cell.get('value')
    ET.indent(svg);ET.ElementTree(svg).write(target,encoding='utf-8',xml_declaration=True)


def render_drawio(source):
    """Raster/PDF inspection exports from the exact same editable geometry."""
    fig,ax=plt.subplots(figsize=(14,8.4),dpi=100)
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    ax.set(xlim=(0,1400),ylim=(840,0),aspect='equal');ax.axis('off')
    for cell in ET.parse(source).findall('.//mxCell'):
        g=cell.find('mxGeometry')
        if g is None:continue
        style=dict(item.split('=',1) for item in cell.get('style','').split(';') if '=' in item)
        if cell.get('vertex')=='1':
            x,y,w,h=[float(g.get(k,'0')) for k in ('x','y','width','height')]
            if style.get('fillColor')!='none':
                ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=6',
                             facecolor=style['fillColor'],edgecolor=style['strokeColor'],linewidth=1.44))
            size=float(style.get('fontSize','20'))
            for i,line in enumerate(cell.get('value','').split('\n')):
                ax.text(x+18,y+30+i*(size+8),line,fontsize=size*.72,color=style['fontColor'],va='baseline')
        elif cell.get('edge')=='1':
            points=[g.find("mxPoint[@as='sourcePoint']"),*g.findall('Array/mxPoint'),g.find("mxPoint[@as='targetPoint']")]
            pairs=[(float(p.get('x')),float(p.get('y'))) for p in points]
            ax.plot(*zip(*pairs),color=style['strokeColor'],linewidth=1.8,linestyle='--' if style.get('dashed')=='1' else '-')
            ax.add_patch(FancyArrowPatch(pairs[-2],pairs[-1],arrowstyle='-|>',mutation_scale=12,
                                        color=style['strokeColor'],linewidth=0))
            if cell.get('value'):ax.text(float(g.get('labelX')),float(g.get('labelY')),cell.get('value'),fontsize=12.96,va='baseline')
    for suffix in ('png','pdf'):fig.savefig(source.with_suffix('.'+suffix),dpi=200)
    plt.close(fig)


def architecture(manifest,colors):
    mx=ET.Element('mxfile',host='app.diagrams.net');d=ET.SubElement(mx,'diagram',name='Goal1 implemented controller')
    model=ET.SubElement(d,'mxGraphModel',dx='1400',dy='840',grid='1',page='1',pageWidth='1400',pageHeight='840')
    root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    def node(id,text,x,y,w,h,fill='Panel',size=20):
        c=ET.SubElement(root,'mxCell',id=id,value=text,style=f'rounded=1;whiteSpace=wrap;html=0;fillColor={colors.get(fill,fill)};strokeColor={colors["Rule"]};fontColor={colors["Ink"]};fontSize={size};',vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    def edge(id,source,target,points,label='',label_xy=(0,0),dashed=False):
        c=ET.SubElement(root,'mxCell',id=id,source=source,target=target,value=label,edge='1',parent='1',style=f'endArrow=block;html=0;strokeColor={colors["C1"]};dashed={int(dashed)};')
        g=ET.SubElement(c,'mxGeometry',relative='1',labelX=str(label_xy[0]),labelY=str(label_xy[1]),**{'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(points[0][0]),y=str(points[0][1]),**{'as':'sourcePoint'})
        mid=ET.SubElement(g,'Array',**{'as':'points'})
        for x,y in points[1:-1]:ET.SubElement(mid,'mxPoint',x=str(x),y=str(y))
        ET.SubElement(g,'mxPoint',x=str(points[-1][0]),y=str(points[-1][1]),**{'as':'targetPoint'})
    node('title','实验一 Goal 1 · 实际角色与控制边界',50,12,1260,60,'none',28)
    node('A','A 研究诊断 · 实际返回\n来源核查计划\n独立模型上下文',70,110,330,120,'P1')
    node('B','B 处理实验 · 调用失败\nworkspace routing 失败\n未执行处理工具',535,110,330,120)
    node('C','C 质量核查 · 尚未调用\n配置已实现\n真实职责验收 BLOCKED',1000,110,330,120,'P4')
    node('controller','确定性控制器（Python，非 Agent）\nschema · 白名单 · 预算 · 哈希\ncheckpoint / 反馈交接 / 拒绝',480,370,440,130)
    node('tools','数值工具：真实 JSON 重算\n结构诊断 / 时间与重复 / 独立核验\n完整米制基线：BLOCKED',480,590,440,120)
    node('artifacts','不可覆盖的执行记录\n可见角色输出 / 工具回执\n输入、代码及产物哈希',70,590,330,120)
    node('policy','只读与研究边界\n原始值 / 合同 / 审核代码\n\nCRS、距离口径未确认\n去噪删除调度未确认\n质量收益阈值未冻结\n\n禁止自动升级质量版本',1000,370,330,340)
    edge('Arequest','A','controller',[(235,230),(235,435),(480,435)],'计划 / 补查',(265,410))
    edge('Brequest','B','controller',[(700,230),(700,370)],'未返回请求',(714,300),True)
    edge('Crequest','C','controller',[(1165,230),(1165,300),(920,300),(920,435)],'尚未发生',(966,282),True)
    edge('feedback','controller','A',[(500,370),(450,280),(400,280),(400,190)],'反馈回路尚未发生',(405,342),True)
    edge('dispatch','controller','tools',[(700,500),(700,590)],'仅 source_evidence 已执行',(720,550))
    edge('record','tools','artifacts',[(480,650),(400,650)],'',(0,0))
    edge('gate','policy','controller',[(1000,450),(920,450)],'',(0,0),True)
    roles=' → '.join(role[0] for role in PHASES)
    node('footer',f'配置阶段：{roles}；实际 A 成功、B 失败、C 未调用。虚线：未完成的角色交接。\n当前 run：{RUN_ID}；PARTIAL_BLOCKED；不能据此声称闭环完成或质量提升。',50,747,1300,85,'none',19)
    path=OUT/'goal1_loop.drawio';ET.indent(mx);ET.ElementTree(mx).write(path,encoding='utf-8',xml_declaration=True)
    export_drawio_svg(path,OUT/'goal1_loop.svg')
    render_drawio(path)


def main():
    OUT.mkdir(parents=True,exist_ok=True);RESULTS.mkdir(parents=True,exist_ok=True)
    colors=palette();policy=read_json(CONFIG);pilot=read_json(ROOT/'task1/config/pilot.json')
    assert digest(DATA)==policy['raw_sha256']==pilot['raw_sha256']
    raw=read_json(DATA);rows=[profile(k,raw[k]) for k in pilot['ids']]
    parts=[time_boundaries(k,raw[k],30) for k in pilot['ids']]
    review=independent_profile_review({k:raw[k] for k in pilot['ids']},rows)
    assert review['status']=='VERIFIED'
    data={'classification':'CURRENT_RUN_REAL_DATA_DIAGNOSTIC_RECOMPUTE','raw_sha256':digest(DATA),
          'run_id':'g1-diagnostic-final-20260926','code_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'source_hashes':{relative(p):digest(p) for p in sorted((ROOT/'task1/workflow').glob('*.py'))},
          'script_sha256':digest(Path(__file__)),'semantics_version':policy['semantics_version'],'metrics_version':policy['metrics_version'],
          'pilot':pilot,'profiles':rows,'summary':aggregate(rows),'time_boundaries':parts,
          'independent_review':review,'full_baseline_gate':execute_tool('baseline',pilot['ids'],policy),
          'created_at':now(),'command':'.venv/bin/python task1/scripts/build_goal1_figures.py'}
    write_json(RESULTS/'pilot_diagnostics.json',data)
    # Every pilot point has an explicit disposition, even when the real pipeline
    # is blocked. These are diagnostic annotations, never deletion decisions.
    with (RESULTS/'point_actions.jsonl').open('w') as f:
        for rid in pilot['ids']:
            tags={e['right_index']:e['reasons'] for e in duplicate_details(rid,raw[rid])['events']}
            cuts={e['right_index']:e['reasons'] for p in parts if p['record_id']==rid for e in p['cuts']}
            for index in range(len(raw[rid][1])):
                f.write(json.dumps({'record_id':rid,'original_index':index,'parent_version':'RAW:'+policy['raw_sha256'],
                    'classification':'CURRENT_RUN_REAL_DATA_DIAGNOSTIC','action':'PRESERVE_UNPROCESSED',
                    'changed_values':0,'deleted':False,'incoming_edge_diagnostics':tags.get(index,[])+cuts.get(index,[]),
                    'baseline_blockers':policy['method']['blocking_ids']},ensure_ascii=False)+'\n')
    csv_fields=['record_id','n_points','edges_total','zero_dt','same_time_different_position','consecutive_duplicate_position','long_gap_gt_30_source_seconds']
    with (RESULTS/'pilot_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=csv_fields);w.writeheader();w.writerows({k:r[k] for k in csv_fields} for r in rows)
    # Matplotlib sees the first face of this installed TTC as "... JP", while
    # fontconfig resolves its SC face. Register the actual file so stale caches
    # cannot silently fall back to DejaVu and drop every Chinese glyph.
    font_path=subprocess.check_output(['fc-match','-f','%{file}','Noto Sans CJK SC'],text=True).strip()
    font_manager.fontManager.addfont(font_path)
    font=font_manager.FontProperties(fname=font_path)
    plt.rcParams.update({'font.family':font.get_name(),'figure.facecolor':colors['Paper'],'axes.facecolor':colors['Paper'],
                        'text.color':colors['Ink'],'axes.labelcolor':colors['Ink'],'xtick.color':colors['Ink'],
                        'ytick.color':colors['Ink'],'axes.edgecolor':colors['Rule'],'font.size':11,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(10.8,4.6),layout='constrained')
    ids=[r['record_id'] for r in rows];x=list(range(len(rows)))
    for ax,fields,labels,cs in [
        (axes[0],['zero_dt','same_time_different_position'],['零时间差','同时间、不同位置'],['C1','C3']),
        (axes[1],['consecutive_duplicate_position','long_gap_gt_30_source_seconds'],['相邻位置相同','时间差 > 30 秒'],['C4','C2'])]:
        for j,(field,label,color) in enumerate(zip(fields,labels,cs)):
            positions=[v+(j-.5)*.34 for v in x]
            bars=ax.bar(positions,[r[field] for r in rows],width=.32,label=label,color=colors[color],hatch='//' if j==1 else None)
            ax.bar_label(bars,fontsize=8,padding=2)
        ax.set_xticks(x,[f'{r["record_id"]}\n边={r["edges_total"]}' for r in rows]);ax.set_xlabel('原始记录 ID / 相邻边分母')
        ax.set_ylabel('相邻边数');ax.spines[['top','right']].set_visible(False);ax.set_axisbelow(True)
        ax.grid(axis='y',color=colors['Rule'],linewidth=.6);ax.legend(loc='upper left',frameon=False,fontsize=10)
        ax.set_ylim(0,max(r[fields[0]] for r in rows)*1.30+8)
    axes[0].set_title('时间可计算性',loc='left',fontsize=14)
    axes[1].set_title('重复位置与时间间隔',loc='left',fontsize=14)
    for suffix in ('png','svg','pdf'):fig.savefig(OUT/('pilot_diagnostics.'+suffix),dpi=300)
    plt.close(fig)
    manifest=read_json(EVIDENCE/'runs'/RUN_ID/'manifest.json')
    architecture(manifest,colors)
    write_json(OUT/'figure_manifest.json',{'created_at':now(),'source_data_sha256':digest(DATA),'pilot_ids':pilot['ids'],
               'architecture_source_run_id':RUN_ID,'architecture_live_code_sha':manifest['code_sha'],
               'diagnostic_code_sha':data['code_sha'],'script_sha256':digest(Path(__file__)),
               'palette_source':'templates/latex/common/p2_cloud_sorbet_colors.tex',
               'palette_sha256':digest(ROOT/'templates/latex/common/p2_cloud_sorbet_colors.tex'),
               'font_family':font.get_name(),'font_file_sha256':digest(font_path),
               'artifacts':{relative(p):digest(p) for p in OUT.iterdir() if p.is_file() and p.name!='figure_manifest.json'},
               'baseline_before_after_figure':{'status':'BLOCKED','reason':'U01/U02; no real complete baseline output'},
               'diagram_export':'draw.io XML mxGeometry -> native SVG using included exporter; same nodes/waypoints/labels',
               'limitations':'diagnostic development counts only; no basemap, no measured physical cleaning quality'} )
    print('generated diagnostic PNG/SVG/PDF and architecture DRAWIO/SVG')


if __name__=='__main__':main()
