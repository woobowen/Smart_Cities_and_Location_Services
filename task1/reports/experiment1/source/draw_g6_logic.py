"""Native technical diagram: observed case and explicitly conditional feedback.
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
W,H=1680,980
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
f'<rect width="{W}" height="{H}" fill="{P["paper"]}"/>',
'<defs>'+''.join(f'<marker id="arrow_{k}" markerWidth="10" markerHeight="10" refX="8.5" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,5 L0,10 Z" fill="{P[k]}"/></marker>' for k in ['blue','rose','muted','violet'])+'</defs>']
mx=ET.Element('mxfile',host='app.diagrams.net',type='device')
dia=ET.SubElement(mx,'diagram',id='g6-observed-case',name='G6 建议核验与条件反馈')
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

# Editorial title, not a dashboard or synthetic conversation.
text(56,55,'参数能执行，为什么仍不采用？',35,bold=True)
text(56,93,'记录 7764：把建议和参考方案放回同一原始轨迹中比较',22,color='muted')
line('top_rule',[(56,115),(1622,115)],color='muted',width=.8,arrow=False)

# Independent raw reference: it is neither generated nor selected by the candidate.
rect('raw',56,184,270,132,stroke='blue')
text(80,222,'原始记录 7764',26,bold=True)
text(80,265,'坐标、时间与原始索引\n保持同一输入范围',22)
rect('proposal',56,420,270,144,stroke='blue')
text(80,460,'LLM 参数提议',26,bold=True)
text(80,500,'只提出候选设置\n效果交由工具实测',22)

rect('reference',405,184,310,145,stroke='muted')
text(430,222,'参考方案',26,bold=True)
text(430,260,'分段 → 方向删除 → DP',22)
text(430,299,'(30, 400, 5, 65, 35, 5)',20,color='muted')
rect('candidate',405,420,310,145,stroke='blue')
text(430,459,'候选方案',26,bold=True)
text(430,497,'同一套处理工具',22)
text(430,536,'(30, 200, 2, 0, 60, 5)',20,color='muted')

# Reference and candidate reach the same comparison, plus trusted raw comes independently.
rect('compare',800,184,824,406,stroke='violet')
text(828,224,'结果核验：局部检查与共同参考分开',26,bold=True)
line('separator',[(828,245),(1595,245)],color='muted',width=.8,arrow=False)
text(828,290,'参数能否执行',23,bold=True)
text(1125,290,'六项取值均在允许范围',22)
text(1574,290,'通过',22,color='blue',bold=True,anchor='middle')
line('r1',[(828,315),(1595,315)],color='muted',width=.6,arrow=False)
text(828,359,'DP 即时误差',23,bold=True)
text(1125,359,'4.826 ≤ 5 工作米',23)
text(1574,359,'通过',22,color='blue',bold=True,anchor='middle')
text(828,393,'仅核对进入 DP 的完整输入',20,color='muted')
line('r2',[(828,413),(1595,413)],color='muted',width=.6,arrow=False)
text(828,459,'共同原始参考',23,bold=True)
text(1125,459,'原有覆盖 122 / 122',23)
text(1574,459,'保留',22,color='blue',bold=True,anchor='middle')
text(828,513,'同一覆盖集合的\n最大几何偏差',21)
text(1125,519,'40.215 → 69.145',29,color='rose',bold=True)
text(1125,556,'增加 28.931 工作米',21,color='rose')
text(1574,516,'退化',22,color='rose',bold=True,anchor='middle')

line('raw_to_base',[(326,248),(405,248)],source='raw',target='reference')
line('raw_to_candidate',[(282,316),(282,371),(558,371),(558,420)],source='raw',target='candidate')
text(405,362,'同一原始记录',20,color='muted')
line('proposal_to_candidate',[(326,492),(405,492)],source='proposal',target='candidate')
line('base_output',[(715,260),(800,260)],source='reference',target='compare')
line('candidate_output',[(715,492),(758,492),(758,550),(800,550)],source='candidate',target='compare')
line('trusted_reference',[(190,184),(190,145),(1220,145),(1220,184)],source='raw',target='compare',color='violet')
rect('raw_ref_label',685,127,414,34,fill='paper',stroke='paper',round=0,width=0)
text(697,152,'原始参考独立提供，不由候选生成',20,color='violet')

# Explicit all-conditions decision rather than a count of passed local checks.
pts=[(1210,635),(1310,703),(1210,771),(1110,703)]
parts.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{P["panel"]}" stroke="{P["violet"]}" stroke-width="2"/>')
cell=ET.SubElement(root,'mxCell',id='decision',value='',style=f'rhombus;fillColor={P["panel"]};strokeColor={P["violet"]};strokeWidth=2;',vertex='1',parent='1')
ET.SubElement(cell,'mxGeometry',x='1110',y='635',width='200',height='136',attrib={'as':'geometry'})
text(1210,691,'全部条件',23,bold=True,anchor='middle');text(1210,724,'同时成立？',23,bold=True,anchor='middle')
line('compare_to_decision',[(1210,590),(1210,635)],color='violet',source='compare',target='decision')
rect('reject',1410,653,214,100,fill='lightrose',stroke='rose')
text(1517,694,'不采用该候选',24,color='ink',bold=True,anchor='middle')
text(1517,731,'保留当前方案',22,anchor='middle')
line('no',[(1310,703),(1410,703)],color='rose',source='decision',target='reject',width=3)
text(1356,687,'否',21,color='rose',bold=True,anchor='middle')
rect('conditional',801,653,218,100,fill='panel',stroke='muted',dashed=True)
text(910,693,'再比较是否有改善',22,color='muted',anchor='middle')
text(910,730,'才考虑替换方案',21,color='muted',anchor='middle')
line('yes',[(1110,703),(1019,703)],color='muted',dashed=True,source='decision',target='conditional')
text(1063,687,'是',21,color='muted',anchor='middle')

text(56,653,'本例揭示的问题',24,bold=True)
text(56,696,'简化步骤合格，不代表\n完整处理结果优于参考。',27,bold=True)
text(56,778,'参数顺序：时间、距离、最少点数、最短长度、方向、DP 容差。',18,color='muted')

# Only a mode-conditional mechanism, not an asserted next historical model turn.
line('feedback',[(1517,753),(1517,855),(26,855),(26,492),(56,492)],color='violet',dashed=True,source='reject',target='proposal')
rect('feedback_label',435,827,933,49,fill='paper',stroke='paper',round=0,width=0)
text(454,857,'有反馈模式：返回实测差异与拒绝原因，在剩余预算内提出下一候选',22,color='violet')
line('bottom_rule',[(56,901),(1624,901)],color='muted',width=.8,arrow=False)
text(56,938,'实线与数值：本次提议的已记录结果。虚线：条件支路或反馈机制，不代表补画了未记录的下一轮。',19,color='muted')
parts.append('</svg>')
svg='\n'.join(parts)
(OUT/'G6A_verification_logic.svg').write_text(svg,encoding='utf-8')
cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'G6A_verification_logic.png'),output_width=2520,output_height=1470)
cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(OUT/'G6A_verification_logic.pdf'))
ET.indent(mx,space='  ');ET.ElementTree(mx).write(OUT/'G6A_verification_logic.drawio',encoding='utf-8',xml_declaration=True)
(OUT/'G6A_logic_notes.md').write_text('''# G6-A 技术关系说明\n\n这是一幅技术核验案例图，不是人机互动原始证据。\n\n- 候选输入、参考输入以及核验原始参考使用同一条记录。\n- 参数合法和局部P误差合格，不能使共同几何保护自动通过。\n- 本例参数 (30,200,2,0,60,5) 和读数来自已发布报告的真实AI案例，共同原始覆盖集合为122点，不是输出保留点数。\n- 几何差值由原始精度读数相减后保留三位小数；端点分别四舍五入显示，故显示值之差可能相差0.001。\n- 灰色“是”支路只说明采用前的逻辑，不表示本例走过它；紫色虚线只表示有反馈模式的允许动作，不宣称存在某一新增真实调用。\n- 不加入没有原始证据的“用户发现—用户纠正”节点；相应人类历史判断只能由Process Report依据原件呈现。\n- `.drawio` 与SVG由同一布局脚本生成；已核验XML可解析、节点和连线存在，但未在桌面draw.io中手动打开验证。\n''',encoding='utf-8')
print('G6逻辑样图已生成：SVG / PNG / PDF / 可编辑 draw.io。')
