"""Native technical diagram: experiment organization and deterministic tools.
No invented user utterances, human intervention, or new model run is represented.
Editable draw.io nodes and SVG/PDF/PNG are emitted from the same layout specification.
"""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET
import json
import cairosvg

BASE=Path(__file__).resolve().parents[1];OUT=BASE/'figures'
P={'paper':'#FCFAF7','ink':'#2D3238','muted':'#70757A','rule':'#DDE3E7',
'blue':'#5B9FBE','lightblue':'#D3EAF5','rose':'#B97589','lightrose':'#E8C7D3',
'violet':'#8177A8','lightviolet':'#D7D3EA','panel':'#FFFDFC','apricot':'#D49757'}
W,H=1240,730
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
f'<rect width="{W}" height="{H}" fill="{P["paper"]}"/>',
'<defs>'+''.join(f'<marker id="arrow_{k}" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,5 L0,10 Z" fill="{P[k]}"/></marker>' for k in ['blue','rose','muted','violet'])+'</defs>']
mx=ET.Element('mxfile',host='app.diagrams.net',type='device')
dia=ET.SubElement(mx,'diagram',id='workflow-structure',name='实验组织与处理工具')
model=ET.SubElement(dia,'mxGraphModel',dx=str(W),dy=str(H),grid='1',gridSize='10',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H))
root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
count=0

def text(x,y,s,size=24,color='ink',bold=False,anchor='start',graph=True):
    global count
    lines=s.split('\n');lh=size*1.45
    parts.append(f'<text x="{x}" y="{y}" font-family="Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{P[color]}" text-anchor="{anchor}">'+''.join(f'<tspan x="{x}" dy="{0 if i==0 else lh}">{escape(v)}</tspan>' for i,v in enumerate(lines))+'</text>')
    if graph:
        count+=1; width=max(len(v) for v in lines)*size+16
        # Editable text, transparent container; CJK width is conservatively estimated.
        cell=ET.SubElement(root,'mxCell',id=f't{count}',value='<br>'.join(escape(v) for v in lines),style=f'text;html=1;strokeColor=none;fillColor=none;align={"center" if anchor=="middle" else "left"};verticalAlign=top;whiteSpace=wrap;fontFamily=Noto Sans CJK SC;fontSize={size};fontColor={P[color]};fontStyle={1 if bold else 0};',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x-width/2 if anchor=='middle' else x),y=str(y-size),width=str(width),height=str(lh*len(lines)+8),attrib={'as':'geometry'})

def rect(id,x,y,w,h,fill='panel',stroke='rule',round=10,width=1.8,dashed=False):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{round}" fill="{P[fill]}" stroke="{P[stroke]}" stroke-width="{width}" '+('stroke-dasharray="8 6"' if dashed else '')+'/>')
    cell=ET.SubElement(root,'mxCell',id=id,value='',style=f'rounded={int(round>0)};whiteSpace=wrap;html=1;fillColor={P[fill]};strokeColor={P[stroke]};strokeWidth={width};dashed={int(dashed)};',vertex='1',parent='1')
    ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})

def line(id,pts,color='blue',width=2.5,dashed=False,arrow=True,source=None,target=None):
    path='M '+' L '.join(f'{x},{y}' for x,y in pts)
    parts.append(f'<path d="{path}" fill="none" stroke="{P[color]}" stroke-width="{width}" stroke-linejoin="round" '+('stroke-dasharray="9 7" ' if dashed else '')+(f'marker-end="url(#arrow_{color})"' if arrow else '')+'/>')
    attrs={'id':id,'value':'','style':f'edgeStyle=none;html=1;rounded=0;strokeColor={P[color]};strokeWidth={width};dashed={int(dashed)};endArrow={"block" if arrow else "none"};','edge':'1','parent':'1'}
    if source:attrs['source']=source
    if target:attrs['target']=target
    cell=ET.SubElement(root,'mxCell',**attrs);geo=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
    ET.SubElement(geo,'mxPoint',x=str(pts[0][0]),y=str(pts[0][1]),attrib={'as':'sourcePoint'})
    ET.SubElement(geo,'mxPoint',x=str(pts[-1][0]),y=str(pts[-1][1]),attrib={'as':'targetPoint'})
    if len(pts)>2:
        arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
        for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))


text(40,45,'候选由结果推进，轨迹由确定性工具处理',27,bold=True)
text(40,84,'上层组织实验；下层执行同一套处理与核验规则',20,color='muted')
rect('A',40,142,320,144,stroke='blue')
text(60,180,'A  规划与诊断',24,bold=True)
text(60,219,'提出可比较的单项或组合\n说明假设与下一步依据',21)
rect('B',460,142,320,144,stroke='blue')
text(480,180,'B  执行与整理',24,bold=True)
text(480,219,'调用处理、搜索与评价工具\n保存真实结果及点去向',21)
rect('C',880,142,320,144,stroke='violet')
text(900,180,'C  独立核验',24,bold=True)
text(900,219,'核对原始参考与实际产物\n判断可比性和采用条件',21)
line('task',[(360,214),(460,214)],source='A',target='B')
text(409,198,'任务',19,color='blue',anchor='middle')
line('outputs',[(780,214),(880,214)],source='B',target='C')
text(830,198,'结果',19,color='blue',anchor='middle')
rect('tools',410,361,440,132,stroke='blue')
text(630,400,'分段与过滤 → 方向删除 → DP',23,bold=True,anchor='middle')
text(630,445,'计算实际轨迹、指标与参数对照',21,anchor='middle')
line('invoke',[(620,286),(620,361)],source='B',target='tools')
text(639,331,'执行',19,color='blue')
rect('raw',40,361,285,132,stroke='muted')
text(62,399,'原始输入与比较规则',22,bold=True)
text(62,439,'同一数据、窗口与指标\n候选不能自行改写参考',20)
line('rawtools',[(325,428),(410,428)],source='raw',target='tools',color='muted')
line('rawC',[(175,493),(175,533),(1038,533),(1038,286)],source='raw',target='C',color='violet')
rect('rlab',535,515,284,32,stroke='paper',fill='paper',width=0)
text(550,539,'独立取得同一原始参考',19,color='violet')
line('review',[(1040,142),(1040,113),(200,113),(200,142)],source='C',target='A',color='violet')
rect('flab',475,99,300,32,stroke='paper',fill='paper',width=0)
text(490,122,'实测差异与下一步问题',19,color='violet')
rect('next',40,585,1160,100,stroke='rule')
text(62,622,'两类结果分别处理',22,bold=True)
text(315,622,'方法无收益或退化：保留负结果，不替换原方案',20)
text(315,660,'实现错误：修正、重算并复验，再恢复未完成实验',20)
text(40,720,'最终全量阶段使用选定的固定参数，不对每条记录重新调用模型或搜索。',19,color='muted')
parts.append('</svg>')
svg='\n'.join(parts)
(OUT/'workflow_structure.svg').write_text(svg,encoding='utf-8')
cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'workflow_structure.png'),output_width=2480,output_height=1460)
cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(OUT/'workflow_structure.pdf'))
ET.indent(mx,space='  ');ET.ElementTree(mx).write(OUT/'workflow_structure.drawio',encoding='utf-8',xml_declaration=True)
print('Workflow source and exports written.')
