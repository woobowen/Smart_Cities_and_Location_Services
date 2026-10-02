"""Artifact checks, with boundaries: this is author-side checking, not independent review."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import fitz,json,hashlib,math,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parents[1]
doc=fitz.open(R/'build/main.pdf');pages=json.loads((R/'provenance/page_map.json').read_text());crops=json.loads((R/'provenance/crop_map.json').read_text());arrows=json.loads((R/'provenance/arrow_map.json').read_text())
checks=[]
def ck(name,passed,detail=''):
 checks.append(dict(check=name,passed=bool(passed),detail=detail))
ck('PDF pages match authored page map',len(doc)==len(pages),str(len(doc)))
ck('16 inherited workflow units + 24 Part II units',len({p.get('unit') for p in pages if p['type']=='evidence'})==40)
ck('All pages are A4 portrait',all(abs(p.rect.width-595.276)<2 and abs(p.rect.height-841.89)<2 for p in doc))
ck('No evidence image below footer',all(p.get('body_end',0)<278 for p in pages))
ck('Screenshot frame stays in approved 70–80 percent range',all(127.3<=p.get('frame_mm',136.5)<=145.7 for p in pages))
px=[]
for c in crops:
 raw=Image.open(R/c['source']).convert('RGB');cut=Image.open(R/c['image']).convert('RGB');px.append(np.array_equal(np.array(raw.crop(tuple(c['box']))),np.array(cut)))
ck('Every formal screenshot is a lossless original-pixel crop',all(px),f'{len(px)} crops')
openers=[]
for p in pages:
 if p['type']=='evidence' and not p['continued']:
  first=p['pieces'][0];im=np.array(Image.open(R/'assets/crops'/first['image']).convert('L'))
  rows=((im<60).mean(1)>.2).sum()
  openers.append(dict(unit=p['unit'],page=p['pdf_page'],role=first['role'],dark_bubble_rows=int(rows),pass_ui=bool(first['role'] in ('user','user_gpt','transfer') and rows>=8)))
ck('Each independent unit opens with real user UI / clearly identified forwarded reply',all(o['pass_ui'] for o in openers),str(openers))
coverage=[]
for a in arrows:
 p=pages[a['page']-1];x,y=a['target_mm']
 inside=any(z['x']-1<=x<=z['x']+z['w']+1 and z['y']-1<=y<=z['y']+z['h']+1 for z in p.get('pieces',[]))
 coverage.append(inside)
ck('All arrow endpoints map inside the corresponding screenshot',all(coverage),f'{len(arrows)} arrow endpoints')
tex=(R/'chapters/pages.tex').read_text();ck('No screenshot highlight/circle/filled-box overlay commands',not any(v in tex for v in ['fill opacity','draw opacity','\\fill[','\\filldraw',' circle (',' rectangle (']))
ck('Only intended cover may be a title-only page',all(p['type']!='evidence' or len(p['pieces'])>0 for p in pages))
log=(R/'build/main.log').read_text(errors='replace')
ck('No missing glyph / undefined control / overfull box',not any(t in log for t in ['Missing character:','Undefined control sequence','Overfull \\hbox','Overfull \\vbox']))
ck('All pages rendered at 200 dpi',all((R/f'review/render_200dpi/p{i+1:03}.png').exists() for i in range(len(doc))))
for id in [f'D{i:02}' for i in range(1,7)]:
 t=ET.parse(R/'figures'/f'{id}.drawio');nodes=t.findall('.//mxCell[@vertex="1"]');edges=t.findall('.//mxCell[@edge="1"]')
 ck(f'{id}: genuine editable draw.io nodes and connectors',len(nodes)>=3 and len(edges)>=2,f'{len(nodes)} nodes, {len(edges)} edges')
# Text bounding boxes check exact generated pages. Raster UI text is not rewritten or OCR'd.
strays=[]
for n,p in enumerate(doc):
 for b in p.get_text('blocks'):
  if b[6]!=0:continue
  if b[0]<20 or b[2]>577 or b[1]<0 or b[3]>837:strays.append([n+1,b[:4],b[4][:80]])
ck('Native report text remains within page',not strays,str(strays[:20]))
result=dict(role='AUTHOR_SELF_CHECK',independent_review='NOT_CLAIMED',user_acceptance='PENDING_FOR_THIS_LANGUAGE_REVISION',page_count=len(doc),evidence_units=40,crop_count=len(crops),arrow_count=len(arrows),checks=checks,all_checks_pass=all(c['passed'] for c in checks),openers=openers,source_resolution='Native pixels retained; current user explicitly accepted source width.')
(R/'provenance/artifact_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
# Fixed-size review packs make every rendered page and every arrow available for visual inspection.
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
try:cf=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
except OSError:cf=f
for batch in range(8):
 ids=list(range(batch,len(doc),8));rows=math.ceil(len(ids)/3);sheet=Image.new('RGB',(1110,rows*553),'#d9d9d9');dr=ImageDraw.Draw(sheet)
 for j,pn in enumerate(ids):
  im=Image.open(R/f'review/render_200dpi/p{pn+1:03}.png').convert('RGB');im.thumbnail((360,516));x=j%3*370;y=j//3*553;sheet.paste(im,(x,y+28));dr.text((x+4,y+4),f'PAGE {pn+1}',font=f,fill='black')
 sheet.save(R/f'review/all_pages_{batch+1}.jpg',quality=96)
for batch in range(8):
 aa=arrows[batch::8];rows=max(1,math.ceil(len(aa)/3));sheet=Image.new('RGB',(1470,rows*195),'#e3e3e3');dr=ImageDraw.Draw(sheet)
 for j,a in enumerate(aa):
  pn=a['page'];im=Image.open(R/f'review/render_200dpi/p{pn:03}.png').convert('RGB');xmm,ymm=a['target_mm'];xx=round(xmm/25.4*200);yy=round(ymm/25.4*200)
  cut=im.crop((max(0,xx-375),max(0,yy-58),min(im.width,xx+90),min(im.height,yy+65)));x=j%3*490;y=j//3*195;sheet.paste(cut,(x,y+46));dr.text((x+3,y+3),f'{a["unit"]} / p{pn}',font=f,fill='black');dr.text((x+3,y+24),a['note'],font=cf,fill='black')
 sheet.save(R/f'review/all_arrows_{batch+1}.jpg',quality=96)
print(json.dumps({k:result[k] for k in ['page_count','evidence_units','crop_count','arrow_count','all_checks_pass']},ensure_ascii=False))
for c in checks:
 if not c['passed']:print('REQUIRES REVIEW:',c)
