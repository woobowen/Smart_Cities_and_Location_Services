"""Generate a complete editable XeLaTeX report from original screenshots.
No OCR, screenshot redrawing, resizing or AI sharpening is used.
"""
from pathlib import Path
import sys,json,hashlib,shutil,math,re
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
from editorial import ROOT,UNITS,EXPECTED_WIDTH
for d in ['assets/raw','assets/inherited','assets/crops','chapters','provenance','build']: (ROOT/d).mkdir(parents=True,exist_ok=True)
CHAPTERS=[]
for u in UNITS:
 if (u['part'],u['chapter']) not in CHAPTERS:CHAPTERS.append((u['part'],u['chapter']))
PAL={'I':'Rose','II':'Blue'}

def esc(s):
 for a,b in [('&',r'\&'),('%',r'\%'),('#',r'\#'),('_',r'\_'),('$',r'\$')]:s=s.replace(a,b)
 return s

def tx(x,y,w,s,size=9.3,leading=13.7,color='Ink',bold=False):
 return f'\\node[anchor=north west,inner sep=0,text width={w:.2f}mm,align=left] at ({x:.2f},{y:.2f}) {{\\color{{{color}}}\\fontsize{{{size}}}{{{leading}}}\\selectfont'+('\\bfseries ' if bold else ' ')+esc(s)+'};\n'
def chars(s):return sum(1 if ord(c)>127 else .52 for c in s)
def height(s,w,size=9.3,leading=13.7):return (math.ceil(chars(s)/(w*72/25.4/size))+0.45)*leading*25.4/72

def snap(im,y,r=8):
 arr=np.asarray(im.convert('RGB'));H,W=arr.shape[:2];y=max(0,min(H,int(y)))
 if y in (0,H):return y
 lo=max(1,y-r);hi=min(H-1,y+r);g=arr.mean(2)
 score=np.abs(np.diff(g[lo:hi+1],axis=1))>45
 val=score.sum(1)+.25*np.abs(np.arange(lo,hi+1)-y)
 return int(lo+val.argmin())

def line_anchor(im,box,y):
 """Locate glyph pixels near a visually chosen source line; reject border-only rows."""
 x0,y0,x1,y1=box;a=np.asarray(im.convert('L')).astype(float);py=float(y)
 lo=max(y0+2,int(py)-28);hi=min(y1-2,int(py)+29)
 if hi<=lo:return x1-6,py
 strengths=[]
 for yy in range(lo,hi):
  band=a[max(y0,yy-1):min(y1,yy+2),x0+3:x1-3]
  edges=(np.abs(np.diff(band,axis=1))>34).sum(axis=1)
  strengths.append(float(np.max(edges)))
 ids=np.flatnonzero(np.array(strengths)>=10)
 if len(ids):
  bands=[];beg=last=int(ids[0])
  for ix in ids[1:]:
   if ix-last>2:bands.append((lo+beg,lo+last));beg=int(ix)
   last=int(ix)
  bands.append((lo+beg,lo+last))
  gy0,gy1=min(bands,key=lambda v:abs((v[0]+v[1])/2-py));yy=(gy0+gy1)/2
 else:gy0=max(lo,int(py)-2);gy1=min(hi-1,int(py)+2);yy=py
 band=a[max(y0,int(gy0)-1):min(y1,int(gy1)+2),x0+3:x1-3]
 edges=(np.abs(np.diff(band,axis=1))>34).sum(axis=0)
 xx=np.flatnonzero(edges>=2)+x0+3;groups=[]
 if len(xx):
  beg=last=int(xx[0])
  for ix in xx:
   if ix-last>14:
    if last-beg>=9:groups.append((beg,last))
    beg=int(ix)
   last=int(ix)
  if last-beg>=9:groups.append((beg,last))
 groups=[g for g in groups if g[0]>x0+1 and g[1]<x1-3]
 if groups:
  gx0,gx1=groups[-1]
  if len(groups)>1 and gx1-gx0<16 and gx0-groups[-2][1]>38:gx0,gx1=groups[-2]
  tx=min(x1-3,gx1+5)
 else:tx=x1-6
 return tx,yy

records={};PANELS={};input_meta=[]
for u in UNITS:
 pp=[]
 for idx,p in enumerate(u['panels']):
  dest=ROOT/'assets'/p['src']
  if not dest.is_file():
   raise FileNotFoundError(f'源包缺少截图素材：{dest.relative_to(ROOT)}')
  im=Image.open(dest).convert('RGB');W,H=im.size
  if p['src'] not in records:
   records[p['src']]=dict(source=p['src'],sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),pixels=[W,H],kind='original_UI' if p['src'].startswith('raw/') else 'inherited_lossless_crop')
  box=list(p['box']);factor=1
  if p['src'].startswith('raw/'):
   grp=Path(p['src']).stem[:10];factor=W/EXPECTED_WIDTH.get(grp,W)
   box[0]=round(box[0]*factor);box[2]=round(box[2]*factor)
  box=[max(0,min(W,box[0])),max(0,min(H,box[1])),max(0,min(W,box[2])),max(0,min(H,box[3]))]
  box[1]=snap(im,box[1]);box[3]=snap(im,box[3]);assert box[2]>box[0] and box[3]>box[1],(u['id'],box)
  base=p['base']*factor if p['base'] else box[2]-box[0]
  anchor=line_anchor(im,box,p['ay']) if p['ay'] is not None and box[1]<=p['ay']<=box[3] else None
  pp.append(dict(**p,box_native=box,base_native=base,image=im,anchor_native=anchor,idx=idx))
 PANELS[u['id']]=pp
(ROOT/'provenance/input_images.json').write_text(json.dumps(list(records.values()),ensure_ascii=False,indent=2))

PREAMBLE=r'''\documentclass[10pt,a4paper]{article}
\usepackage[top=12mm,bottom=12mm,left=14mm,right=14mm]{geometry}
\usepackage{fontspec,xeCJK,xcolor,graphicx,tikz,hyperref,ragged2e}
\usetikzlibrary{calc,arrows.meta}
\setmainfont{Noto Sans}\setsansfont{Noto Sans}
\setCJKmainfont{Noto Sans CJK SC}\setCJKsansfont{Noto Sans CJK SC}
\definecolor{Paper}{HTML}{FCFAF7}\definecolor{Ink}{HTML}{2D3238}
\definecolor{Muted}{HTML}{70757A}\definecolor{Blue}{HTML}{5B9FBE}
\definecolor{Rose}{HTML}{B97589}\definecolor{Violet}{HTML}{8177A8}
\definecolor{Orange}{HTML}{D49757}\definecolor{Rule}{HTML}{DDE3E7}
\pagecolor{Paper}\color{Ink}\pagestyle{empty}
\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
\hypersetup{hidelinks,pdftitle={实验一过程报告：我与GPT的持续交互——改进工作流，完成实验一},pdfauthor={吴博闻},pdfsubject={真实Human–AI研究过程},bookmarksopen=true}
\newcommand{\PageStart}{\null\begin{tikzpicture}[remember picture,overlay]\begin{scope}[shift={(current page.north west)},x=1mm,y=-1mm]}
\newcommand{\PageEnd}{\end{scope}\end{tikzpicture}\clearpage}
\begin{document}
'''
PAGES=[];PAGE_META=[];crop_meta=[];arrow_meta=[]
def footer(number,part=''):
 return '\\draw[Rule,line width=.35pt] (14,283)--(196,283);\n'+tx(14,287,170,'智慧城市与位置服务  /  实验一过程报告'+('  /  '+part if part else ''),6.7,8.5,'Muted')+tx(185,286.5,11,str(number).zfill(2),8,9,'Muted')
def add_page(code,meta):
 number=len(PAGES)+1;PAGES.append('\\PageStart\n'+code+footer(number,meta.get('part',''))+'\\PageEnd\n');meta['pdf_page']=number;PAGE_META.append(meta)

# Opening: introduce both interaction and workflow, then explain manual capture.
cv=tx(14,19,182,'SMART CITIES & LOCATION SERVICES',8.5,11,'Rose',True)
cv+=tx(14,47,182,'实验一过程报告',28,35,'Ink',True)
cv+=tx(14,72,182,'我与 GPT 的持续交互：',18.5,25,'Ink',True)
cv+=tx(14,85,182,'改进工作流，完成实验一',18.5,25,'Ink',True)
cv+=tx(14,116,176,'本报告记录我与 GPT 通过持续讨论、质疑、修改和核验，逐步完善协作工作流并完成实验一的过程。我们从既有协作经验出发，围绕任务理解、方法比较、实验反馈和报告表达调整做法；明确的工程任务交由 Codex 实现和运行，结果再回到讨论与核验中，推动后续决定。',10.7,17)
cv+='\\draw[Blue,line width=1.1pt] (14,164)--(196,164);\n'
cv+=tx(14,181,176,'截图采集',11.5,16,'Blue',True)
cv+=tx(14,194,176,'文档中的所有对话截图，都是我在 ChatGPT 网页中通过sharex软件利用长截图一张一张手动截取然后再利用图片分割器功能一张张切割并提供的；在本次协作中，GPT 没有直接截取我的网页对话界面的功能。',10.7,17)
cv+=tx(14,258,170,'吴博闻  ·  10245102410',11,14,'Ink',True)
add_page(cv,{'type':'cover'})
# TOC reserved; filled after pagination.
add_page('',{'type':'contents'})
chapter_start={};unit_start={};chapter_counter={c:i+1 for i,c in enumerate(CHAPTERS)}

def unit_header(u,k,total):
 ch=(u['part'],u['chapter']);cno=chapter_counter[ch]
 code=tx(14,11,182,('PART I · 工作流构建' if u['part']=='I' else 'PART II · 实验一中的交互与决策')+'  /  '+u['chapter'],7.8,10,PAL[u['part']],True)
 title=u['title']+('（续）' if k else '')
 code+=tx(14,22,182,title,17.5,22.5,'Ink',True)
 titleh=height(title,182,17.5,22.5)-3.0
 y=22+titleh+3
 if not k:
  code+=tx(14,y,182,u['intro'],9.5,14.6);y+=height(u['intro'],182,9.5,14.6)+2.5
 else:
  code+=tx(14,y,182,'接前页，继续阅读这组对话。',8.2,11,'Muted');y+=9
 return code,y

for u in UNITS:
 pp=PANELS[u['id']];frame=136.5;gap=5.2
 native_height=sum((p['box_native'][3]-p['box_native'][1])/p['base_native'] for p in pp)
 overhead=len(pp)*(gap+4.2)
 _,start=unit_header(u,0,1);cap=272-start
 total=native_height*frame+overhead
 if total>cap and native_height*127.4+overhead<=cap-1:
  frame=max(127.4,min(frame,(cap-overhead-1)/native_height))
 total=native_height*frame+overhead
 n=max(1,math.ceil(total/cap));target=min(cap,total/n+1)
 # Build balanced pieces; a break is always snapped to a row gap, never resampled.
 out=[];cur=[];used=0
 for p in pp:
  x0,y0,x1,y1=p['box_native'];cursor=y0
  while cursor<y1:
   need=(y1-cursor)/p['base_native']*frame+gap+4.2
   room=(cap if len(out)>=n-1 else target)-used
   if cur and room<35:
    out.append(cur);cur=[];used=0;room=(cap if len(out)>=n-1 else target)
   if need<=room+1 or (y1-cursor)<60:
    end=y1
   else:
    maxpix=int((room-gap-4.2)*p['base_native']/frame)
    if maxpix<75 and cur:
     out.append(cur);cur=[];used=0;continue
    end=snap(p['image'],min(y1,cursor+max(75,maxpix)),12)
    if end<=cursor:end=min(y1,cursor+max(75,maxpix))
    if y1-end<60 and used+need<=cap+1:end=y1
   q=dict(p);q['piece_box']=[x0,cursor,x1,end];q['continued']=cursor>y0
   cur.append(q);used+=(end-cursor)/p['base_native']*frame+gap+4.2;cursor=end
   if cursor<y1:
    out.append(cur);cur=[];used=0
 if cur:out.append(cur)
 # Rebalance neighbouring pages and eliminate orphan strips without shrinking UI.
 def hh(items):
  return sum((q['piece_box'][3]-q['piece_box'][1])/q['base_native']*frame+gap+4.2 for q in items)
 for _ in range(6):
  changed=False;ii=0
  while ii<len(out)-1:
   A,B=out[ii],out[ii+1];ha,hb=hh(A),hh(B)
   if ha+hb<=cap-1:
    out[ii]=A+B;out.pop(ii+1);changed=True;continue
   # Move a lossless piece from the fuller side toward the shorter side.
   if abs(ha-hb)>36:
    want=abs(ha-hb)/2
    forward=ha>hb
    src=A if forward else B;dst=B if forward else A
    q=src[-1] if forward else src[0]
    x0,yy0,x1,yy1=q['piece_box'];ph=(yy1-yy0)/q['base_native']*frame
    if ph<=want+4 and len(src)>1:
     if forward:dst.insert(0,src.pop())
     else:dst.append(src.pop(0))
     changed=True
    elif ph>want+18:
     amount=max(40,int((want-4)*q['base_native']/frame))
     cut=snap(q['image'],yy1-amount if forward else yy0+amount,10)
     if yy0+30<cut<yy1-30:
      qa=dict(q);qb=dict(q)
      qa['piece_box']=[x0,yy0,x1,cut];qb['piece_box']=[x0,cut,x1,yy1];qb['continued']=True
      if forward:src[-1]=qa;dst.insert(0,qb)
      else:dst.append(qa);src[0]=qb
      changed=True
   ii+=1
  if not changed:break
 # Adjacent parts of a single original excerpt remain one image when they fit.
 def coalesce(items):
  z=[]
  for q in items:
   if z and z[-1]['src']==q['src'] and z[-1]['idx']==q['idx'] and z[-1]['piece_box'][3]==q['piece_box'][1]:
    z[-1]=dict(z[-1]);z[-1]['piece_box']=z[-1]['piece_box'][:3]+[q['piece_box'][3]]
   else:z.append(dict(q))
  return z
 out=[coalesce(v) for v in out]
 ii=0
 while ii<len(out)-1:
  combined=coalesce(out[ii]+out[ii+1])
  actual_cap=272-unit_header(u,ii,len(out))[1]
  if hh(combined)<=actual_cap-1:
   out[ii]=combined;out.pop(ii+1)
  else:ii+=1
 firstpage=len(PAGES)+1;unit_start[u['id']]=firstpage;ch=(u['part'],u['chapter'])
 if ch not in chapter_start:chapter_start[ch]=firstpage
 for k,pieces in enumerate(out):
  code,y=unit_header(u,k,len(out));pn=len(PAGES)+1
  if not k:code+=f'\\node[anchor=north west,inner sep=0] at (14,8) {{\\hypertarget{{{u["id"]}}}{{}}}};\n'
  placed=[]
  for j,q in enumerate(pieces):
   x0,y0,x1,y1=q['piece_box'];im=q['image'].crop((x0,y0,x1,y1))
   name=f'{u["id"]}_{k+1:02}_{j+1:02}.png';dest=ROOT/'assets/crops'/name;im.save(dest)
   width=(x1-x0)/q['base_native']*frame;h=(y1-y0)/q['base_native']*frame
   x=14+(frame-width if q['role'] in ('user','transfer') and width<frame else 0)
   label=q['label']+(' · 续页' if q['continued'] else '')
   code+=tx(14,y,frame,label,7.2,9.5,'Muted');y+=4.2
   code+=f'\\node[anchor=north west,inner sep=0] at ({x:.3f},{y:.3f}) {{\\includegraphics[width={width:.3f}mm]{{assets/crops/{name}}}}};\n'
   anchor=None
   if q['anchor_native'] and y0<=q['anchor_native'][1]<y1:
    xx,yy=q['anchor_native'];anchor=(x+(xx-x0)*frame/q['base_native'],y+(yy-y0)*frame/q['base_native'])
   placed.append(dict(image=name,src=q['src'],box=q['piece_box'],x=x,y=y,w=width,h=h,anchor=anchor,role=q['role'],label=label))
   crop_meta.append(dict(unit=u['id'],page=pn,image='assets/crops/'+name,source='assets/'+q['src'],box=q['piece_box'],ppi=(x1-x0)/(width/25.4),placement_mm=[x,y,width,h],role=q['role']))
   y+=h+gap
  # Sidebar notes remain narrow and secondary. One or two verified targets per page.
  notes=[]
  if u['id']=='E24' and k==0:notes=u['notes'][:]
  elif u['id']=='E24':notes=[('从样章到全篇','我确认实际样章后要求完整重构，随后审阅并验收25页实验报告。GPT再将这些表达做法整理为可复用原则。')]
  elif str(k) in u.get('continuation_notes',{}):notes=u['continuation_notes'][str(k)]
  elif len(out)==1:notes=u['notes'][:]
  elif k==0:notes=[u['notes'][0]]
  elif k==len(out)-1:notes=[u['notes'][-1]]
  else:notes=[('判断的依据',u['close'] or u['notes'][-1][1])]
  targets=[a['anchor'] for a in placed if a['anchor']]
  # Do not invent an arrow target when a continued excerpt contains no authored target.
  sy=(unit_header(u,k,len(out))[1]+6)
  for j,(title,text) in enumerate(notes):
   col='Blue' if j%2==0 else 'Violet'
   code+=tx(159.6,sy,36.4,title,9.5,13,col,True)
   th=height(title,36.4,9.5,13);code+=tx(159.6,sy+th+2,36.4,text,8.7,12.8)
   nh=th+2+height(text,36.4,8.7,12.8)
   if targets and (j==0 or len(targets)>1):
    target=targets[-1] if len(notes)==1 and k>0 else targets[0 if j==0 else -1];txx,ty=target
    startx=157.4;starty=sy+3.5
    lane=153.2+2.1*j
    code+=f'\\draw[draw={col},line width=.66pt,rounded corners=1mm,-{{Stealth[length=1.8mm,width=1.35mm]}}] ({startx:.3f},{starty:.3f}) -- ({lane:.3f},{starty:.3f}) -- ({lane:.3f},{ty:.3f}) -- ({txx:.3f},{ty:.3f});\n'
    arrow_meta.append(dict(page=pn,unit=u['id'],note=title,target_mm=[txx,ty],start_mm=[startx,starty]))
   sy+=nh+17
  if k==len(out)-1 and u['close']:
   nh=height(u['close'],36.4,8.5,12.7)+10
   if sy+nh<273:
    code+=tx(159.6,sy,36.4,'我的回看',8.9,12.5,'Rose',True)+tx(159.6,sy+7,36.4,u['close'],8.5,12.7)
  add_page(code,dict(type='evidence',unit=u['id'],part='Part '+u['part'],chapter=u['chapter'],continued=bool(k),pieces=placed,frame_mm=frame,body_end=y))
 if u['diagram']:
  did=u['diagram'];d=json.loads((ROOT/'provenance/diagrams.json').read_text())[did]
  code=tx(14,11,182,('PART I · 工作流构建' if u['part']=='I' else 'PART II · 实验一中的交互与决策')+'  /  '+u['chapter']+'  /  关系图',7.8,10,PAL[u['part']],True)
  code+=tx(14,25,182,d['title'],18,24,'Ink',True)+tx(14,43,182,d['subtitle'],9.6,15)
  code+=f'\\node[anchor=north west,inner sep=0] at (14,71) {{\\includegraphics[width=182mm]{{figures/{did}.pdf}}}};\n'
  cap_y=71+182*d['h']/d['w']+10
  code+=tx(14,cap_y,182,d['caption'],10,15.5,'Ink')
  add_page(code,dict(type='diagram',diagram=did,part='Part '+u['part'],chapter=u['chapter']))
# Retrospective closing with the original user excerpt and the complete evolution diagram.
code=tx(14,11,182,'整体工作流回顾',8,11,'Rose',True)+tx(14,25,182,'回到我最初要求的“真实完成与持续改进”',18,24,'Ink',True)
code+=tx(14,45,182,'回看这次实验，我最关心的几件事始终连在一起：依据是否清楚，任务有没有实际执行，结果怎样核验，以及发现问题后能否继续推进。下面回引我当时的要求，再看它怎样逐步落实。',9.6,15)
f=ROOT/'assets/raw/o3dlGVJPTa1.png';im=Image.open(f);box=(int(im.width*.365),80,im.width-5,333);im.crop(box).save(ROOT/'assets/crops/closing_user.png')
code+='\\node[anchor=north west,inner sep=0] at (14,74) {\\includegraphics[width=136.5mm]{assets/crops/closing_user.png}};\n'
code+=tx(159.6,78,36.4,'让反馈引出下一步',9.5,13,'Blue',True)+tx(159.6,96,36.4,'我要求体系完成任务后继续检查结果、寻找改进。后续讨论又明确了候选依据、有限预算和停止条件。',8.8,13)
code+=tx(14,207,182,'我在这次任务中不断补充和修正要求：把Multi-Agent拉回真实轨迹任务，要求先验证单项、共用评价，让普通修复留在当前Goal，并继续检查方法解释与报告表达。GPT负责研究、解释、候选和结果核查，Codex负责实现与运行；我的质疑和选择也持续影响着后续工作。',10,15.5)
code+=tx(14,245,182,'前期交接曾经反复，审核接口出现过漏洞，开发阶段有优势的组合也在新记录上退出。正是这些经历，让我们逐渐明确什么时候继续、怎样修复，以及为什么保留较简单的方案。',10,15.5)
add_page(code,dict(type='reflection',part='回顾'))
d=json.loads((ROOT/'provenance/diagrams.json').read_text())['D06'];code=tx(14,11,182,'整体工作流回顾  /  研究演化图',8,11,'Rose',True)+tx(14,25,182,d['title'],18,24,'Ink',True)+tx(14,47,182,d['subtitle'],9.6,15)
code+='\\node[anchor=north west,inner sep=0] at (14,78) {\\includegraphics[width=182mm]{figures/D06.pdf}};\n'
code+=tx(14,224,182,'这次交互让我形成了更具体的工作习惯：先把问题和依据讲清，再用可检查的结果决定下一步；实现有错就修复，有效候选没有收益就保留结论并调整方向。方案和报告都在这种往返中逐步成形。',10,15.5)
code+=tx(14,251,182,'相关材料：原始对话节选见各章；算法、指标与完整结果见配套Experiment Report；截图来源、裁切与箭头定义、构建方法和制作记录随LaTeX源包保存。',8.8,13,'Muted')
add_page(code,dict(type='diagram',diagram='D06',part='回顾'))
# Build compact real-page-number contents, no artificial section-only pages.
code=tx(14,17,182,'目录',21,27,'Ink',True)+tx(14,34,182,'先回看工作流的形成，再记录我与GPT推进实验一时的交互与决定。',10,15)
y=57
for part in ['I','II']:
 code+=tx(14,y,165,('Part I  工作流构建' if part=='I' else 'Part II  实验一中的交互与决策'),13,18,'Rose' if part=='I' else 'Blue',True);y+=14
 for ch in [c for c in CHAPTERS if c[0]==part]:
  code+=tx(20,y,160,ch[1],10.3,15)+tx(181,y,15,str(chapter_start[ch]),10.3,15,'Muted');y+=15
 y+=9
code+=tx(20,y,160,'整体工作流回顾',10.3,15)+tx(181,y,15,str(len(PAGES)-1),10.3,15,'Muted')
PAGES[1]='\\PageStart\n'+code+footer(2)+'\\PageEnd\n'
# Save authorable LaTeX by logical part and the complete compile entry.
(ROOT/'chapters/pages.tex').write_text('\n'.join(PAGES),encoding='utf8')
(ROOT/'main.tex').write_text(PREAMBLE+'\\input{chapters/pages.tex}\n\\end{document}\n',encoding='utf8')
(ROOT/'provenance/page_map.json').write_text(json.dumps(PAGE_META,ensure_ascii=False,indent=2))
(ROOT/'provenance/crop_map.json').write_text(json.dumps(crop_meta,ensure_ascii=False,indent=2))
(ROOT/'provenance/arrow_map.json').write_text(json.dumps(arrow_meta,ensure_ascii=False,indent=2))
(ROOT/'provenance/editorial_blueprint.json').write_text(json.dumps(UNITS,ensure_ascii=False,indent=2))
print('Generated',len(PAGES),'pages,',len(crop_meta),'lossless UI windows,',len(arrow_meta),'editable arrows')
# Explicit delimiter after font-selection commands keeps Unicode text out of control names.
_pg=ROOT/'chapters/pages.tex'
_pg.write_text(_pg.read_text(encoding='utf8').replace('\\selectfont','\\selectfont '),encoding='utf8')
