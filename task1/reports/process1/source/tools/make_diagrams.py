"""Generate editable draw.io, SVG and PDF from the same diagram specification."""
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import json
import cairosvg
R=Path(__file__).resolve().parents[1]
O=R/'figures';O.mkdir(exist_ok=True)
C={'ink':'#2D3238','muted':'#70757A','blue':'#5B9FBE','rose':'#B97589','violet':'#8177A8','rule':'#DDE3E7','paper':'#FCFAF7','panel':'#FFFDFC'}
D=json.loads((R/'content/diagrams.json').read_text(encoding='utf-8'))

def endpoints(a,b):
 ax=a['x']+a['w']/2;ay=a['y']+a['h']/2;bx=b['x']+b['w']/2;by=b['y']+b['h']/2
 if abs(by-ay)>100:return (ax,a['y']+a['h'] if by>ay else a['y']),(bx,b['y'] if by>ay else b['y']+b['h'])
 return (a['x']+a['w'] if bx>ax else a['x'],ay),(b['x'] if bx>ax else b['x']+b['w'],by)
for key,d in D.items():
 w,h=d['w'],d['h'];nodes={x['id']:x for x in d['nodes']}
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="100%" height="100%" fill="{C["paper"]}"/>','<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="#70757A" stroke-width="1.2"/></marker></defs>']
 mx=ET.Element('mxfile',host='app.diagrams.net');dg=ET.SubElement(mx,'diagram',name=d['title'],id=key)
 model=ET.SubElement(dg,'mxGraphModel',dx=str(w),dy=str(h),grid='1',gridSize='10',page='1',pageScale='1',pageWidth=str(w),pageHeight=str(h));root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
 for j,e in enumerate(d['edges']):
  a,b=nodes[e['a']],nodes[e['b']];(x1,y1),(x2,y2)=endpoints(a,b)
  path=f'M{x1},{y1} L{x2},{y2}'
  # A cross-row wrap gets an outer gutter rather than crossing cards.
  if key=='D06' and e['a']=='b3':path=f'M{x1},{y1} L990,155 L990,211 L165,211 L{x2},{y2}'
  svg.append(f'<path d="{path}" fill="none" stroke="{C["muted"]}" stroke-width="1.6" marker-end="url(#arrow)"/>')
  if e['label']:
   ls=e.get('label_layout')
   if ls:
    lx=(x1+x2)/2+ls.get('dx',0);ly=(y1+y2)/2+ls.get('dy',-10)
    for li,lt in enumerate(ls['lines']):
     svg.append(f'<text x="{lx}" y="{ly+li*ls["line_height"]}" text-anchor="{ls.get("anchor","middle")}" font-family="Noto Sans CJK SC" font-size="{ls["font_size"]}" fill="{C["muted"]}">{escape(lt)}</text>')
   else:
    svg.append(f'<text x="{(x1+x2)/2+8}" y="{(y1+y2)/2-10}" font-family="Noto Sans CJK SC" font-size="16" fill="{C["muted"]}">{escape(e["label"])}</text>')
  cell=ET.SubElement(root,'mxCell',id=f'e{j}',value=e['label'],edge='1',parent='1',source=e['a'],target=e['b'],style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;endFill=0;strokeColor=#70757A;fontFamily=Noto Sans CJK SC;fontSize=16;')
  geo=ET.SubElement(cell,'mxGeometry',{'relative':'1','as':'geometry'})
  if e.get('label_layout'):
   cell.set('value','\n'.join(e['label_layout']['lines']))
   cell.set('style',cell.get('style').replace('fontSize=16;','fontSize=14;')+'align=center;verticalAlign=middle;')
   ET.SubElement(geo,'mxPoint',{'x':'0','y':'-28','as':'offset'})
 for nd in d['nodes']:
  x,y,nw,nh=nd['x'],nd['y'],nd['w'],nd['h'];col=C[nd['accent']]
  svg.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="7" fill="{C["panel"]}" stroke="{col}" stroke-width="1.8"/>')
  lineh=24;first=y+(nh-(len(nd['lines'])-1)*lineh)/2+6
  for k,t in enumerate(nd['lines']):
   svg.append(f'<text x="{x+nw/2}" y="{first+k*lineh}" text-anchor="middle" font-family="Noto Sans CJK SC" font-size="{19 if k==0 else 17}" font-weight="{700 if k==0 else 400}" fill="{C["ink"]}">{escape(t)}</text>')
  style=f'rounded=1;whiteSpace=wrap;html=0;fillColor={C["panel"]};strokeColor={col};fontColor={C["ink"]};fontFamily=Noto Sans CJK SC;fontSize=17;spacing=10;'
  cell=ET.SubElement(root,'mxCell',id=nd['id'],value='\n'.join(nd['lines']),vertex='1',parent='1',style=style)
  ET.SubElement(cell,'mxGeometry',{'x':str(x),'y':str(y),'width':str(nw),'height':str(nh),'as':'geometry'})
 svg.append('</svg>');sv='\n'.join(svg);(O/(key+'.svg')).write_text(sv,encoding='utf8');ET.indent(mx);ET.ElementTree(mx).write(O/(key+'.drawio'),encoding='utf-8',xml_declaration=True)
 cairosvg.svg2pdf(bytestring=sv.encode(),write_to=str(O/(key+'.pdf')))
(R/'provenance/diagrams.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print('6 editable diagrams built')
